"""
slack_scraper.py — Slack 채널 메시지를 공지 dict 목록으로 변환하는 모듈.

제공하는 함수:
  fetch_notices(channel_id, lookback_hours) — 지정된 Slack 채널의 최근 메시지를
    읽어 public.notices 테이블 스키마와 일치하는 dict 목록으로 반환한다.

필요한 환경변수:
  SLACK_BOT_TOKEN — Slack Bot OAuth 토큰 (xoxb-...)

필터링 규칙:
  - subtype 이 있는 메시지(편집·삭제·입장 등 시스템 메시지) 제외
  - bot_id 가 있는 봇 메시지 제외
  - text 가 비어있는 메시지 제외

Cloudflare R2 업로드 없음:
  Slack 첨부파일은 인증 없이 접근 불가하므로 image_urls 는 항상 빈 리스트.
"""

from __future__ import annotations

import hashlib
import io
import logging
import os
from datetime import datetime, timedelta, timezone

import boto3
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

_MAX_IMAGE_BYTES = 10 * 1024 * 1024


def _upload_slack_files(notice_id: str, files: list[dict], token: str) -> list[str]:
    """
    Slack 첨부 이미지를 Bearer 인증으로 다운로드한 뒤 Cloudflare R2에 업로드한다.

    Slack의 url_private / url_private_download 는 Bot 토큰으로만 접근 가능하므로
    Authorization: Bearer {token} 헤더를 사용한다.

    R2 환경변수(R2_ACCOUNT_ID 등)가 미설정이면 빈 리스트를 반환하고 조용히 종료한다.

    Input:
        notice_id (str)      — R2 객체 키 경로에 사용되는 공지 ID
        files     (list)     — Slack 메시지의 files 배열
        token     (str)      — Slack Bot OAuth 토큰

    Output:
        list[str] — 업로드 성공한 R2 공개 URL 목록
    """
    account_id = os.environ.get("R2_ACCOUNT_ID", "")
    access_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    bucket_name = os.environ.get("R2_BUCKET_NAME", "")
    public_url = os.environ.get("R2_PUBLIC_URL", "").rstrip("/")

    if not all([account_id, access_key, secret_key, bucket_name, public_url]):
        return []

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    auth_headers = {"Authorization": f"Bearer {token}"}
    r2_urls: list[str] = []

    for idx, f in enumerate(files):
        mimetype = f.get("mimetype", "")
        if not mimetype.startswith("image/"):
            continue

        dl_url = f.get("url_private_download") or f.get("url_private")
        if not dl_url:
            continue

        try:
            resp = requests.get(dl_url, headers=auth_headers, timeout=15)
            if resp.status_code != 200:
                logger.warning("slack image download failed HTTP %s: %s", resp.status_code, dl_url)
                continue
            if len(resp.content) > _MAX_IMAGE_BYTES:
                logger.warning("slack image too large (%d bytes): %s", len(resp.content), dl_url)
                continue

            filename = f.get("name") or f"image_{idx}"
            object_key = f"notices/{notice_id}/{idx}_{filename}"

            s3.upload_fileobj(
                io.BytesIO(resp.content),
                bucket_name,
                object_key,
                ExtraArgs={"ContentType": mimetype},
            )
            r2_urls.append(f"{public_url}/{object_key}")
            logger.info("slack image uploaded: %s", object_key)

        except Exception as exc:
            logger.error("slack image upload error idx=%d: %s", idx, exc)

    return r2_urls



def fetch_notices(channel_id: str, lookback_hours: int = 25) -> list[dict]:
    """
    Slack 채널의 최근 메시지를 가져와 공지 dict 목록으로 반환한다.

    conversations_history API를 페이지네이션하며 호출해 lookback_hours 이내의
    모든 메시지를 수집한다. 필터링 후 각 메시지를 notices 테이블 스키마에 맞는
    dict로 변환한다.

    Input:
        channel_id     (str) — Slack 채널 ID (예: C0XXXXXXX)
        lookback_hours (int) — 조회 기간(시간). 기본값 25 (24h + 1h 버퍼)

    Output:
        list[dict] — 각 dict 는 다음 키를 포함:
            notice_id    (str)            — "slack-{channel_id}-{ts}" 형식
            title        (str)            — 첫 번째 비어있지 않은 줄, 최대 255자
            body         (str)            — 메시지 전체 텍스트
            source       (str)            — "slack" 고정
            hash         (str)            — SHA-256(text) hex digest
            url          (str)            — Slack 퍼머링크 URL
            published_at (datetime)       — UTC-aware datetime
            image_urls   (list[str])      — 항상 [] (Slack 첨부파일은 인증 필요)

    Raises:
        RuntimeError — SLACK_BOT_TOKEN 미설정 또는 Slack API 오류
    """
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise RuntimeError("SLACK_BOT_TOKEN is not set in environment")

    client = WebClient(token=token)
    oldest = (
        datetime.now(tz=timezone.utc) - timedelta(hours=lookback_hours)
    ).timestamp()

    raw_messages: list[dict] = []
    cursor: str | None = None

    while True:
        kwargs: dict = {
            "channel": channel_id,
            "oldest": str(oldest),
            "limit": 200,
        }
        if cursor:
            kwargs["cursor"] = cursor

        try:
            resp = client.conversations_history(**kwargs)
        except SlackApiError as exc:
            raise RuntimeError(
                f"Slack API error: {exc.response['error']}"
            ) from exc

        raw_messages.extend(resp.get("messages", []))

        if not resp.get("has_more"):
            break
        cursor = resp["response_metadata"]["next_cursor"]

    notices: list[dict] = []

    for msg in raw_messages:
        # 시스템 메시지(편집·삭제·채널 입장 등) 제외
        if msg.get("subtype"):
            continue
        # 봇 메시지 제외
        if msg.get("bot_id"):
            continue

        text = msg.get("text", "").strip()
        if not text:
            continue

        ts: str = msg["ts"]
        notice_id = ts.replace(".", "")

        # 첫 번째 비어있지 않은 줄 = 제목 (:mega:, :star2: 등 이모지 포함 줄)
        # 이후 줄들 = 본문
        lines = text.splitlines()
        title_idx = next(
            (i for i, line in enumerate(lines) if line.strip()), 0
        )
        title = lines[title_idx].strip()[:255]
        body_text = "\n".join(lines[title_idx + 1:]).strip()
        body = body_text if body_text else None

        hash_val = hashlib.sha256(text.encode()).hexdigest()

        # Slack 퍼머링크: ts의 점(.)을 제거해 p{timestamp} 형식으로 변환
        url = (
            f"https://ajou-international.slack.com/archives"
            f"/{channel_id}/p{ts.replace('.', '')}"
        )

        published_at = datetime.fromtimestamp(float(ts), tz=timezone.utc)

        image_urls = _upload_slack_files(notice_id, msg.get("files", []), token)

        notices.append(
            {
                "notice_id": notice_id,
                "title": title,
                "body": body,
                "source": "slack",
                "hash": hash_val,
                "url": url,
                "published_at": published_at,
                "image_urls": image_urls,
            }
        )

    return notices
