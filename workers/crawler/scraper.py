"""
scraper.py — 단일 공지 소스에 대한 핵심 크롤 파이프라인 모듈.

제공하는 함수:
  crawl_source(source_config) — 페이지네이션된 목록 페이지를 가져오고, 공지 메타데이터를 추출하며,
                                 필요 시 상세 본문을 가져와 DB에 upsert한다.

페이지네이션:
  offset = 0, 10, 20, ..., (pages_per_run - 1) * 10
  sources.json 의 base URL에 &article.offset={offset}&articleLimit=10 을 추가하여 사용.

공지 단위 처리 흐름:
  1. 목록 페이지 행에서 notice_id, title, published_at 을 추출한다.
  2. 정규 detail URL과 SHA-256 hash를 생성한다.
  3. notice_id 가 DB에 이미 있으면 본문 fetch를 건너뛰고, 없으면 본문 fetch + 1초 sleep.
  4. db.upsert_notice() 로 upsert하고 inserted/skipped 카운트를 누적한다.

connection 생명주기:
  crawl_source() 시작 시 psycopg2 connection 하나를 열고 finally 블록에서 닫으므로,
  단일 소스는 페이지·공지 수에 무관하게 connection을 정확히 하나만 사용한다.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from . import db
from . import image_uploader
from . import parser

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AjouCrawler/1.0)"}

# 정규 상세 페이지 링크를 생성할 때 사용하는 base URL
_DETAIL_BASE = "https://www.ajou.ac.kr/kr/ajou/notice.do"


def _extract_notice_id(href: str) -> str | None:
    """
    앵커 href에서 articleNo 쿼리 파라미터를 파싱한다.

    Input:
        href (str) — <a> 태그의 raw href 속성값 (상대 URL 또는 절대 URL)

    Output:
        str  — articleNo 값이 존재하고 비어있지 않으면 해당 값
        None — articleNo 가 없거나 빈 문자열인 경우
    """
    qs = parse_qs(urlparse(href).query)
    values = qs.get("articleNo")
    if values:
        return values[0].strip() or None
    return None


def _parse_list_page(html: str) -> list[dict]:
    """
    목록 페이지 HTML 한 장에서 공지 메타데이터 행들을 추출한다.

    아주대 게시판 표준 구조를 대상으로 한다: table > tbody > tr,
    제목 <a> 태그의 href에 articleNo가 포함되고, 마지막 <td>에 게시일이 있다.

    Input:
        html (str) — 페이지네이션된 목록 페이지의 전체 HTML

    Output:
        list[dict] — 각 dict 는 다음 키를 포함:
            notice_id    (str)            — articleNo 문자열
            title        (str)            — 공백 제거된 전체 제목
            published_at (datetime|None)  — "YYYY-MM-DD"를 파싱한 UTC-aware datetime,
                                            날짜를 추출할 수 없으면 None
    notice_id 가 None 이거나 빈 문자열인 행은 조용히 제거된다.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tbody tr")
    items: list[dict] = []

    for row in rows:
        a = row.select_one("a")
        if not a:
            continue

        title = a.get_text(strip=True)
        href = (a.get("href") or "").strip()
        if not title or not href:
            continue

        notice_id = _extract_notice_id(href)
        if not notice_id:
            continue

        # 게시일은 각 행의 마지막 <td>에 일관되게 위치한다
        tds = row.select("td")
        date_text = tds[-1].get_text(strip=True) if tds else ""
        m = re.search(r"\d{4}-\d{2}-\d{2}", date_text)
        published_at: datetime | None = None
        if m:
            try:
                published_at = datetime.strptime(m.group(0), "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                pass

        items.append(
            {
                "notice_id": notice_id,
                "title": title,
                "published_at": published_at,
            }
        )

    return items


def crawl_source(source_config: dict) -> dict:
    """
    sources.json 의 소스 항목 하나에 대해 전체 크롤 파이프라인을 실행한다.

    소스 실행 전체에 걸쳐 DB connection 하나를 열고 finally 블록에서 닫는다.
    각 페이지 요청은 독립적이며, 실패한 페이지는 로그에 기록 후 skip되고 실행을 중단하지 않는다.
    각 공지는 개별 try/except로 감싸져 있어 하나의 불량 행이 나머지를 중단시킬 수 없다.

    Input:
        source_config (dict) — sources.json 의 항목 하나, 다음 키를 포함해야 함:
            url           (str) — base 목록 페이지 URL (offset 파라미터 없음)
            source_label  (str) — DB `source` 컬럼에 그대로 저장될 값
            pages_per_run (int) — 페이지네이션할 목록 페이지 수

    Output:
        dict — {"inserted": int, "skipped": int}
            inserted: DB에 새로 작성된 행 수
            skipped:  이미 존재하던 행 수 (ON CONFLICT DO NOTHING)
    """
    base_url: str = source_config["url"]
    source_label: str = source_config["source_label"]
    pages_per_run: int = int(source_config["pages_per_run"])

    inserted = 0
    skipped = 0
    notice_counter = 0

    conn = db.get_connection()
    try:
        for page_idx in range(pages_per_run):
            offset = page_idx * 10
            page_url = f"{base_url}&article.offset={offset}&articleLimit=10"

            try:
                resp = requests.get(page_url, headers=_HEADERS, timeout=10)
                resp.encoding = "utf-8"
            except Exception as exc:
                logger.error(
                    "crawl_source: request failed page_idx=%d url=%s — %s",
                    page_idx, page_url, exc,
                )
                continue

            if resp.status_code != 200:
                logger.error(
                    "crawl_source: HTTP %s page_idx=%d url=%s",
                    resp.status_code, page_idx, page_url,
                )
                continue

            rows = _parse_list_page(resp.text)
            logger.info(
                "crawl_source: page %d/%d — %d rows found",
                page_idx + 1, pages_per_run, len(rows),
            )

            for row in rows:
                notice_id: str = row["notice_id"]
                title: str = row["title"]
                published_at: datetime | None = row["published_at"]

                notice_counter += 1
                date_str = published_at.strftime("%Y-%m-%d") if published_at else "날짜없음"
                title_preview = title[:40] + "..." if len(title) > 40 else title
                print(f"[{notice_counter}] {date_str} | {notice_id} | {title_preview}", flush=True)

                try:
                    detail_url = (
                        f"{_DETAIL_BASE}?mode=view"
                        f"&articleNo={notice_id}"
                        f"&article.offset=0&articleLimit=10"
                    )

                    # notice_id + title + UTC ISO timestamp 에 대한 SHA-256 해시
                    pub_iso = published_at.isoformat() if published_at else ""
                    notice_hash = hashlib.sha256(
                        f"{notice_id}{title}{pub_iso}".encode("utf-8")
                    ).hexdigest()

                    # 새로운 공지일 때만 상세 본문과 이미지를 fetch하여 불필요한 HTTP 요청을 방지
                    if db.notice_exists(conn, notice_id):
                        body = None
                        r2_urls: list[str] = []
                        print("    → 이미지 스킵 (공지 중복)", flush=True)
                    else:
                        body, image_urls = parser.fetch_body(detail_url)
                        if not image_urls:
                            print("    → 이미지 없음 (스킵)", flush=True)
                        r2_urls = image_uploader.upload_images(notice_id, image_urls)
                        time.sleep(1.0)

                    notice_dict = {
                        "notice_id": notice_id,
                        "title": title,
                        "body": body,
                        "source": source_label,
                        "hash": notice_hash,
                        "url": detail_url,
                        "published_at": published_at,
                        "image_urls": r2_urls,
                    }

                    result = db.upsert_notice(conn, notice_dict)
                    if result == "inserted":
                        inserted += 1
                        print(f"    → DB 저장 성공: {notice_id} | {title_preview}", flush=True)
                    else:
                        skipped += 1

                except Exception as exc:
                    logger.error(
                        "crawl_source: failed notice_id=%s — %s", notice_id, exc
                    )

    finally:
        conn.close()

    return {"inserted": inserted, "skipped": skipped}
