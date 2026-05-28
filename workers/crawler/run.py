#!/usr/bin/env python3
"""
run.py — 크롤러 수동 실행 스크립트 (로컬 전용).

GitHub Actions 없이 터미널에서 직접 크롤러를 실행한다.
리포지토리 루트, workers/, workers/crawler/ 어느 위치에서 실행해도 동작한다.
환경변수는 workers/.env 또는 프로젝트 루트 .env 에서 자동으로 로드한다.

실행 예시:
  python workers/crawler/run.py                     # 모든 소스, sources.json 기본 설정
  python workers/crawler/run.py --pages 5           # 페이지 수를 5로 오버라이드
  python workers/crawler/run.py --source 일반공지    # 특정 소스만 실행
  python workers/crawler/run.py --pages 1 --dry-run # DB 쓰기 없이 크롤 결과만 출력

옵션:
  --pages  N       : 크롤할 페이지 수 (sources.json 의 pages_per_run 을 덮어씀)
  --source LABEL   : 실행할 소스의 source_label (미지정 시 모든 소스 실행)
  --dry-run        : DB에 쓰지 않고 크롤된 공지 제목과 건수만 출력 (연결 테스트용)
"""

from __future__ import annotations

# ── sys.path 설정 ──────────────────────────────────────────────────────────────
# 어느 디렉터리에서 실행하든 workers/ 가 경로에 포함되도록 설정한다.
# __file__ = workers/crawler/run.py
# parents[0] = workers/crawler/
# parents[1] = workers/
import sys
from pathlib import Path

_WORKERS_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_WORKERS_DIR))
sys.path.insert(0, str(_PROJECT_ROOT))

# ── 표준 라이브러리 및 서드파티 임포트 ────────────────────────────────────────
import argparse
import json
import logging
import os

from dotenv import load_dotenv

# .env 로드 순서: workers/.env → 프로젝트 루트 .env (먼저 찾은 값이 우선)
load_dotenv(_WORKERS_DIR / ".env")
load_dotenv(_WORKERS_DIR.parent / ".env")

# ── 크롤러 모듈 임포트 ─────────────────────────────────────────────────────────
try:
    from crawler.scraper import crawl_source
except ImportError as exc:
    print(f"ERROR: crawler.scraper 임포트 실패 — {exc}", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _load_sources(sources_path: Path) -> list[dict]:
    """
    sources.json 을 로드하고 파싱한다.

    Input:  sources_path (Path) — sources.json 의 절대 경로
    Output: list[dict] — 소스 항목 목록
    Raises: SystemExit(1) — 파일 없음 또는 형식 오류
    """
    if not sources_path.exists():
        print(f"ERROR: sources.json 을 찾을 수 없음 — {sources_path}", file=sys.stderr)
        sys.exit(1)

    try:
        sources = json.loads(sources_path.read_text(encoding="utf-8"))
        if not isinstance(sources, list) or not sources:
            raise ValueError("sources.json 은 비어있지 않은 JSON 배열이어야 함")
        return sources
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: sources.json 형식 오류 — {exc}", file=sys.stderr)
        sys.exit(1)


def _run_dry(source_config: dict) -> None:
    """
    --dry-run 모드: DB 없이 crawl_source() 를 실행하고 공지 제목과 건수만 출력한다.
    crawler.db 의 DB 함수를 mock 으로 가로채 실제 DB 접속을 방지한다.

    Input:  source_config (dict) — sources.json 의 소스 항목 하나
    Output: 없음 (stdout 출력만 수행)
    """
    from unittest.mock import MagicMock, patch

    collected_titles: list[str] = []

    def _fake_upsert(conn, notice: dict) -> str:
        title = notice.get("title", "")
        notice_id = notice.get("notice_id", "?")
        date = notice.get("published_at")
        date_str = date.strftime("%Y-%m-%d") if date else "날짜없음"
        title_preview = title[:50] + "..." if len(title) > 50 else title
        idx = len(collected_titles) + 1
        print(f"  [{idx:>3}] {date_str} | {notice_id:>7} | {title_preview}", flush=True)
        collected_titles.append(title)
        return "inserted"

    with (
        patch("crawler.db.get_connection", return_value=MagicMock()),
        patch("crawler.db.notice_exists", return_value=False),
        patch("crawler.db.upsert_notice", side_effect=_fake_upsert),
    ):
        crawl_source(source_config)

    print(f"  → dry-run 수집 건수: {len(collected_titles)}건 (DB 쓰기 없음)")


def main() -> None:
    """
    CLI 인수를 파싱하고 지정된 소스에 대해 크롤러를 실행한다.

    --dry-run 플래그가 있으면 DB 접속 없이 크롤 결과만 출력한다.
    없으면 실제 DB(Neon)에 upsert 한다.

    Input:  없음 (sys.argv 에서 인수를 파싱)
    Output: 없음 (부수 효과: DB upsert 또는 dry-run 출력, stdout 요약)
    """
    arg_parser = argparse.ArgumentParser(
        description="Ajou 공지 크롤러 수동 실행",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "예시:\n"
            "  python workers/crawler/run.py\n"
            "  python workers/crawler/run.py --pages 5\n"
            "  python workers/crawler/run.py --source 일반공지\n"
            "  python workers/crawler/run.py --pages 1 --dry-run"
        ),
    )
    arg_parser.add_argument(
        "--pages",
        type=int,
        default=None,
        metavar="N",
        help="크롤할 페이지 수 (sources.json 의 pages_per_run 을 덮어씀)",
    )
    arg_parser.add_argument(
        "--source",
        type=str,
        default=None,
        metavar="LABEL",
        help="실행할 소스의 source_label (미지정 시 모든 소스 실행)",
    )
    arg_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="DB 에 쓰지 않고 크롤 결과만 출력 (연결·파싱 검증용)",
    )
    args = arg_parser.parse_args()

    sources_path = Path(__file__).parent / "sources" / "sources.json"
    sources = _load_sources(sources_path)

    # --source 로 특정 소스만 선택
    if args.source:
        sources = [s for s in sources if s.get("source_label") == args.source]
        if not sources:
            print(
                f"ERROR: source_label='{args.source}' 을 sources.json 에서 찾을 수 없음",
                file=sys.stderr,
            )
            sys.exit(1)

    # --pages 로 pages_per_run 오버라이드
    if args.pages is not None:
        for s in sources:
            s["pages_per_run"] = args.pages

    if args.dry_run:
        print("[ dry-run 모드 — DB 쓰기 없음 ]")

    total_inserted = 0
    total_skipped = 0

    for source_config in sources:
        label = source_config.get("source_label", "<unknown>")
        pages = source_config.get("pages_per_run", "?")
        print(f"\n[{label}] 크롤 시작 (pages_per_run={pages})...")

        if args.dry_run:
            try:
                _run_dry(source_config)
            except Exception as exc:
                print(f"ERROR: [{label}] dry-run 실패 — {exc}", file=sys.stderr)
            continue

        # 실제 DB upsert 실행
        try:
            result = crawl_source(source_config)
        except Exception as exc:
            print(f"ERROR: [{label}] crawl_source() 실패 — {exc}", file=sys.stderr)
            continue

        n_inserted = result["inserted"]
        n_skipped = result["skipped"]
        total_inserted += n_inserted
        total_skipped += n_skipped
        print(f"[{label}] 완료 — Inserted: {n_inserted}, Skipped: {n_skipped}")

    if not args.dry_run:
        print(f"\n[TOTAL] Inserted: {total_inserted}, Skipped: {total_skipped}")


if __name__ == "__main__":
    main()
