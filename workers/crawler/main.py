"""
main.py — Ajou 공지 크롤러의 진입점(entrypoint).

담당 역할:
  1. python-dotenv 를 통해 .env 를 로드하여 로컬 실행 시 DATABASE_URL 을 사용 가능하게 한다.
  2. sources/sources.json 을 찾고 파싱한다 — 모든 크롤 대상의 단일 원천(source of truth).
  3. 각 소스 항목에 대해 scraper.crawl_source() 를 호출한다.
  4. 소스별 및 전체 합산 insert/skip 카운트를 stdout에 출력한다.

종료 코드:
  0 — 모든 소스 처리 완료 (공지 단위 실패는 로그에 기록하며 치명적이지 않음)
  1 — sources.json 이 없거나 비어있거나 JSON 형식이 잘못된 경우

실행 방법 (workers/ 디렉터리에서):
  python -m crawler.main
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from . import scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    sources.json 을 로드하고 구조를 검증한 뒤, 모든 source_config 를 순회한다.

    각 소스에 대해:
      - scraper.crawl_source(source_config) 를 호출하여 {"inserted": n, "skipped": n} 을 받음
      - 출력: [{source_label}] Inserted: {n}, Skipped: {n}

    모든 소스 처리 후:
      - 출력: [TOTAL] Inserted: {n}, Skipped: {n}

    Input:  없음 (sources.json 을 디스크에서 읽고 DATABASE_URL 을 환경변수에서 읽음)
    Output: 없음 (부수 효과: DB 행 삽입, stdout 출력)
    """
    load_dotenv()

    sources_path = Path(__file__).parent / "sources" / "sources.json"

    if not sources_path.exists():
        print(f"ERROR: sources.json not found at {sources_path}", file=sys.stderr)
        sys.exit(1)

    try:
        sources = json.loads(sources_path.read_text(encoding="utf-8"))
        if not isinstance(sources, list) or len(sources) == 0:
            raise ValueError("sources.json must be a non-empty JSON array")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: malformed sources.json — {exc}", file=sys.stderr)
        sys.exit(1)

    total_inserted = 0
    total_skipped = 0

    for source_config in sources:
        label = source_config.get("source_label", "<unknown>")
        logger.info("Starting crawl for source: %s", label)

        result = scraper.crawl_source(source_config)
        n_inserted = result["inserted"]
        n_skipped = result["skipped"]
        total_inserted += n_inserted
        total_skipped += n_skipped

        print(f"[{label}] Inserted: {n_inserted}, Skipped: {n_skipped}")

    print(f"[TOTAL] Inserted: {total_inserted}, Skipped: {total_skipped}")


if __name__ == "__main__":
    main()
