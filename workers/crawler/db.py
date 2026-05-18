"""
db.py — Ajou 공지 크롤러의 데이터베이스 상호작용 계층.

세 가지 함수를 제공:
  get_connection()   — DATABASE_URL 환경변수로 psycopg2 connection을 열어 반환
  notice_exists()    — public.notices에 해당 notice_id 행이 이미 존재하면 True 반환
  upsert_notice()    — 공지 행 한 건을 삽입; "inserted" 또는 "skipped" 반환

크롤 시점에 채워지는 컬럼:
  id, notice_id, title, body, source, hash,
  is_processed (false), url, published_at, created_at (NOW()),
  image_urls (text[] — R2에 업로드된 이미지 공개 URL 배열, 없으면 빈 배열)

하위 파이프라인을 위해 NULL로 남겨두는 컬럼:
  deadline, keyword_id, embedding, eng_body
"""

from __future__ import annotations

import os

import psycopg2


def get_connection():
    """
    환경변수 DATABASE_URL을 사용하여 psycopg2 connection을 열어 반환한다.

    Input:  없음 (os.environ["DATABASE_URL"] 를 읽음)
    Output: psycopg2.extensions.connection — 즉시 사용 가능한 열린 connection
    Raises:
        RuntimeError              — DATABASE_URL 이 설정되지 않은 경우
        psycopg2.OperationalError — DB에 접속할 수 없는 경우
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set in environment")
    # psycopg2 는 SQLAlchemy 형식의 드라이버 접두사("postgresql+psycopg2://")를 인식하지 못함
    # Neon 또는 다른 곳에서 복사한 URL에 포함되어 있을 수 있으므로 제거한다
    db_url = db_url.replace("postgresql+psycopg2://", "postgresql://")
    return psycopg2.connect(db_url)


def notice_exists(conn, notice_id: str) -> bool:
    """
    주어진 notice_id 를 가진 행이 public.notices에 이미 존재하는지 확인한다.

    Input:
        conn       — 열린 psycopg2 connection (이 함수에서 닫지 않음)
        notice_id  — 아주대 공지사항 게시판의 articleNo 문자열

    Output: 행이 존재하면 True, 그렇지 않으면 False
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM public.notices WHERE notice_id = %s LIMIT 1",
            (notice_id,),
        )
        return cur.fetchone() is not None


def upsert_notice(conn, notice: dict) -> str:
    """
    ON CONFLICT (notice_id) DO NOTHING 구문으로 public.notices에 공지 행 한 건을 삽입한다.

    새 행이 실제로 작성될 때만 transaction을 commit하며, skip 시에는 commit하지 않아
    불필요한 round-trip을 방지한다.

    Input:
        conn   — 열린 psycopg2 connection (닫는 책임은 호출자에게 있음)
        notice — 다음 키를 포함하는 dict:
                   notice_id (str), title (str), body (str | None),
                   source (str), hash (str), url (str), published_at (datetime | None),
                   image_urls (list[str]) — R2 공개 URL 목록; 없으면 빈 리스트 []

    Output: rowcount == 1 이면 "inserted", rowcount == 0 이면 "skipped"
    """
    sql = """
    INSERT INTO public.notices (
        id, notice_id, title, body, source, hash,
        is_processed, deadline, url, published_at, created_at,
        keyword_id, embedding, eng_body, image_urls
    ) VALUES (
        gen_random_uuid(),
        %(notice_id)s, %(title)s, %(body)s,
        %(source)s, %(hash)s,
        false, NULL,
        %(url)s, %(published_at)s, NOW(),
        NULL, NULL, NULL, %(image_urls)s
    )
    ON CONFLICT (notice_id) DO NOTHING;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, notice)
            if cur.rowcount == 1:
                conn.commit()
                return "inserted"
            return "skipped"
    except Exception:
        # INSERT 실패 시 트랜잭션을 rollback하여 connection을 재사용 가능한 상태로 복구
        # rollback 없이 예외를 올리면 이후 모든 SQL이 "transaction is aborted" 로 연쇄 실패함
        conn.rollback()
        raise
