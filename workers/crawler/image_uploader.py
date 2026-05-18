"""
image_uploader.py — Ajou 공지 이미지를 Cloudflare R2에 업로드하는 모듈.

제공하는 함수:
  upload_images(notice_id, image_urls) — 이미지 URL 목록을 받아 각 이미지를
    다운로드하고 R2에 업로드한 뒤 공개 URL 목록을 반환한다.

필요한 환경변수:
  R2_ACCOUNT_ID        — Cloudflare 계정 ID
  R2_ACCESS_KEY_ID     — R2 액세스 키 ID
  R2_SECRET_ACCESS_KEY — R2 시크릿 액세스 키
  R2_BUCKET_NAME       — R2 버킷 이름
  R2_PUBLIC_URL        — R2 공개 도메인 (예: https://pub-xxx.r2.dev)

R2 객체 키 형식: notices/{notice_id}/{index}_{original_filename}
  예) notices/368855/0_poster.jpg

공개 URL 형식: {R2_PUBLIC_URL}/notices/{notice_id}/{index}_{filename}
  예) https://pub-xxx.r2.dev/notices/368855/0_poster.jpg

boto3 가 S3 호환 endpoint 로 Cloudflare R2에 접속한다.
모든 이미지 처리는 io.BytesIO 를 사용해 메모리 내에서만 수행하며
디스크에 임시 파일을 생성하지 않는다.
"""

from __future__ import annotations

import io
import logging
import os
import time
from urllib.parse import urlparse

import boto3
import requests

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AjouCrawler/1.0)"}

# 단일 이미지의 최대 허용 크기: 10MB
_MAX_IMAGE_BYTES = 10 * 1024 * 1024


def upload_images(notice_id: str, image_urls: list[str]) -> list[str]:
    """
    주어진 notice_id 와 이미지 URL 목록으로 R2 업로드를 수행한다.

    처리 흐름 (이미지 1건 단위):
      1. requests.get() 으로 이미지 다운로드
      2. HTTP 상태, Content-Type, 파일 크기 검증
      3. boto3 upload_fileobj() 로 R2에 업로드 (io.BytesIO, 임시 파일 없음)
      4. 공개 R2 URL 을 결과 리스트에 추가

    개별 이미지 실패 시 로그를 남기고 다음 이미지로 넘어간다.
    절대 예외를 발생시키지 않으며 항상 리스트를 반환한다.

    Input:
        notice_id  (str)       — 공지 articleNo 문자열 (R2 키 경로에 사용됨)
        image_urls (list[str]) — 공지 본문 영역에서 추출된 절대 이미지 URL 목록

    Output:
        list[str] — 업로드 성공한 이미지의 공개 R2 URL 목록
                    실패한 이미지는 결과에서 제외됨
                    image_urls 가 빈 리스트이면 빈 리스트 즉시 반환
    """
    if not image_urls:
        return []

    # S3 클라이언트를 함수 내부에서 생성 (모듈 레벨 초기화 금지)
    # 환경변수가 없는 경우 빈 문자열로 처리하고 아래에서 조기 종료
    account_id = os.environ.get("R2_ACCOUNT_ID", "")
    access_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    bucket_name = os.environ.get("R2_BUCKET_NAME", "")
    public_url = os.environ.get("R2_PUBLIC_URL", "").rstrip("/")

    if not all([account_id, access_key, secret_key, bucket_name, public_url]):
        logger.error(
            "upload_images: R2 환경변수 미설정 — notice_id=%s 이미지 업로드 건너뜀",
            notice_id,
        )
        return []

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    r2_urls: list[str] = []

    for idx, img_url in enumerate(image_urls):
        try:
            # 이미지 다운로드
            resp = requests.get(img_url, headers=_HEADERS, timeout=10)
            if resp.status_code != 200:
                logger.warning(
                    "upload_images: 다운로드 실패 HTTP %s — %s",
                    resp.status_code, img_url,
                )
                time.sleep(0.5)
                continue

            # Content-Type 검증: image/* 만 허용
            content_type = (
                resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
            )
            if not content_type.startswith("image/"):
                logger.warning(
                    "upload_images: 이미지가 아닌 Content-Type '%s' — %s",
                    content_type, img_url,
                )
                time.sleep(0.5)
                continue

            # 파일 크기 검증: 10MB 초과 시 건너뜀
            if len(resp.content) > _MAX_IMAGE_BYTES:
                logger.warning(
                    "upload_images: 파일 크기 초과 (%d bytes > 10MB) — %s",
                    len(resp.content), img_url,
                )
                time.sleep(0.5)
                continue

            # R2 객체 키 구성: 원본 파일명이 없으면 "image" 사용
            path_part = urlparse(img_url).path
            filename = path_part.split("/")[-1] or "image"
            object_key = f"notices/{notice_id}/{idx}_{filename}"

            # 메모리 내 업로드 (디스크 임시 파일 없음)
            s3.upload_fileobj(
                io.BytesIO(resp.content),
                bucket_name,
                object_key,
                ExtraArgs={"ContentType": content_type},
            )

            r2_url = f"{public_url}/{object_key}"
            r2_urls.append(r2_url)

        except Exception as exc:
            logger.error(
                "upload_images: 예외 발생 notice_id=%s idx=%d url=%s — %s",
                notice_id, idx, img_url, exc,
            )

        # 이미지 다운로드 간 rate limiting 방지
        time.sleep(0.5)

    if r2_urls:
        print(f"    → 이미지 {len(r2_urls)}장 업로드 성공", flush=True)

    return r2_urls
