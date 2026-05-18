"""
parser.py — 공지 상세 페이지를 가져와 본문 텍스트와 이미지 URL을 추출하는 모듈.

제공하는 함수:
  fetch_body(url) — 공지 상세 페이지를 GET하여 plain-text 본문과 이미지 URL 목록을
                    튜플로 반환한다. 실패 시 (None, []) 반환.

CSS selector 탐색 순서 (아주대 게시판 마크업 기준, 우선순위 순):
  1. div.b-content-box   — 대부분의 아주대 페이지에서 사용하는 주 본문 wrapper
  2. div.view-con        — 대체 view container
  3. div.board-view-con  — 구형 board view container
  4. article             — 시맨틱 태그 fallback
  5. 텍스트 길이가 가장 긴 <div> — 최후 fallback

이미지 추출 규칙:
  - 본문 영역 요소 내부의 <img> 태그만 대상 (헤더·네비·푸터 제외)
  - src 가 없거나 빈 값이면 건너뜀
  - data: 스킴 (base64 인라인 이미지) 이면 건너뜀
  - 상대 URL 은 urljoin 으로 절대 URL 변환
  - ajou.ac.kr 도메인을 포함하지 않는 외부 URL 은 건너뜀
  - 중복 제거 (등장 순서 유지)

후처리 (본문 텍스트):
  - get_text(separator="\\n") 로 텍스트 추출 후 각 줄 strip
  - 연속 줄바꿈 3개 이상을 2개로 축소
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AjouCrawler/1.0)"}

# 연속된 줄바꿈이 3개 이상인 경우를 매칭 (전후 공백 포함)
_COLLAPSE_NEWLINES = re.compile(r"\n{3,}")

_SELECTORS = [
    "div.b-content-box",
    "div.view-con",
    "div.board-view-con",
    "article",
]


def _extract_image_urls(content_el, base_url: str) -> list[str]:
    """
    본문 DOM 요소 내부의 <img> 태그에서 절대 이미지 URL을 추출한다.

    헤더·네비게이션·푸터 영역은 content_el 범위에 포함되지 않으므로
    본문 이미지만 추출된다.

    Input:
        content_el — BeautifulSoup Tag 객체 (본문 영역 루트 요소)
        base_url   (str) — 상대 URL 을 절대 URL로 변환하는 기준 URL

    Output:
        list[str] — 절대 이미지 URL 목록 (중복 없음, 등장 순서 유지)
    """
    seen: set[str] = set()
    urls: list[str] = []

    for img in content_el.find_all("img"):
        src = img.get("src")
        if not src or not src.strip():
            continue
        src = src.strip()

        # base64 인라인 이미지 건너뜀
        if src.startswith("data:"):
            continue

        abs_src = urljoin(base_url, src)

        # 아주대 도메인 외 외부 이미지(트래킹 픽셀 등) 건너뜀
        if "ajou.ac.kr" not in abs_src:
            continue

        if abs_src not in seen:
            seen.add(abs_src)
            urls.append(abs_src)

    return urls


def fetch_body(url: str) -> tuple[str | None, list[str]]:
    """
    공지 상세 페이지를 가져와 plain-text 본문과 이미지 URL 목록을 반환한다.

    Input:
        url (str) — 공지 상세 페이지의 전체 URL

    Output:
        tuple[str | None, list[str]]:
            첫 번째 — 공백 정규화된 plain text (연속 빈 줄 최대 2개), 또는 None
            두 번째 — 본문 영역 내 절대 이미지 URL 리스트 (중복 없음, 등장 순서 유지)
                       헤더·네비·푸터 이미지는 포함하지 않음
                       추출 실패 또는 이미지 없음 시 빈 리스트

    selector 우선순위:
        div.b-content-box → div.view-con → div.board-view-con → article
        → 텍스트 길이가 가장 긴 <div> (fallback)
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            logger.warning("fetch_body: HTTP %s for %s", resp.status_code, url)
            return None, []

        soup = BeautifulSoup(resp.text, "html.parser")

        el = None
        for sel in _SELECTORS:
            el = soup.select_one(sel)
            if el:
                break

        if el is None:
            divs = soup.find_all("div")
            if divs:
                el = max(divs, key=lambda d: len(d.get_text()))

        if el is None:
            return None, []

        # 본문 영역 내부 이미지 URL 추출 (헤더·푸터 제외)
        image_urls = _extract_image_urls(el, url)

        text = el.get_text(separator="\n")
        # 각 줄의 앞뒤 공백을 개별적으로 제거
        text = "\n".join(line.strip() for line in text.splitlines())
        text = _COLLAPSE_NEWLINES.sub("\n\n", text).strip()
        return text or None, image_urls

    except Exception as exc:
        logger.error("fetch_body: exception for %s — %s", url, exc)
        return None, []
