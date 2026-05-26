from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert as pg_insert

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.app.database import SessionLocal  # noqa: E402
from backend.app.models import InformationMenuPart  # noqa: E402

SOURCE_PATH = PROJECT_ROOT / "frontend" / "app" / "data" / "informationMenuContent.ts"
EMBEDDING_DIMENSIONS = 1536
SEED_EMBEDDING_MODEL = "seed-zero-vector-1536"


def load_information_menu_parts() -> list[dict]:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"export const INFORMATION_MENU_PARTS: InformationMenuPart\[\] = (\[.*?\]);",
        source,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError(f"INFORMATION_MENU_PARTS was not found in {SOURCE_PATH}")

    literal = match.group(1)
    literal = re.sub(r"(^|[{\s,])([A-Za-z][A-Za-z0-9_]*):", r"\1'\2':", literal)
    return ast.literal_eval(literal)


def upsert_information_menu_parts(rows: list[dict]) -> int:
    values = [
        {
            "menu_key": row["menuKey"],
            "menu_title": row["menuTitle"].strip(),
            "part_key": row["partKey"],
            "part_title": row["partTitle"].strip(),
            "section_title": row["sectionTitle"].strip(),
            "content": row["content"].strip(),
            "source_url": row.get("sourceUrl"),
            "embedding": [0.0] * EMBEDDING_DIMENSIONS,
            "embedding_model": SEED_EMBEDDING_MODEL,
        }
        for row in rows
    ]

    stmt = pg_insert(InformationMenuPart).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["menu_key", "part_key", "section_title"],
        set_={
            "menu_title": stmt.excluded.menu_title,
            "part_title": stmt.excluded.part_title,
            "content": stmt.excluded.content,
            "source_url": stmt.excluded.source_url,
            "embedding": stmt.excluded.embedding,
            "embedding_model": stmt.excluded.embedding_model,
        },
    )

    with SessionLocal() as db:
        result = db.execute(stmt)
        db.commit()
        return int(result.rowcount or 0)


def main() -> None:
    rows = load_information_menu_parts()
    saved_count = upsert_information_menu_parts(rows)
    print(f"Saved {saved_count} information menu parts.")


if __name__ == "__main__":
    main()
