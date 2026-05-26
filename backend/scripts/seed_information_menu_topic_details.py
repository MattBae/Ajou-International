from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.app.database import SessionLocal  # noqa: E402
from backend.app.models import InformationMenuPart  # noqa: E402
from workers.rag.src.rag.embedder import Embedder  # noqa: E402

EMBEDDING_DIMENSIONS = 1536


def load_topic_detail_rows() -> list[dict]:
    result = subprocess.run(
        ["node", "scripts/export-topic-details.js"],
        cwd=FRONTEND_DIR,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    rows = json.loads(result.stdout)
    if not rows:
        raise RuntimeError("No topic detail rows were exported.")
    return rows


def embedding_text(row: dict) -> str:
    return "\n".join(
        [
            f"주제: {row['menuTitle']}",
            f"내용: {row['content']}",
        ]
    )


def build_values(rows: list[dict]) -> list[dict]:
    embedding_model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    embedder = Embedder().get_embedding_function()
    values = []

    for index, row in enumerate(rows, start=1):
        vector = embedder.embed_query(
            text=embedding_text(row),
            output_dimensionality=EMBEDDING_DIMENSIONS,
        )
        if len(vector) != EMBEDDING_DIMENSIONS:
            raise RuntimeError(
                f"Expected {EMBEDDING_DIMENSIONS} dimensions, got {len(vector)} "
                f"for {row['menuKey']}/{row['partKey']}"
            )

        values.append(
            {
                "menu_key": row["menuKey"],
                "menu_title": row["menuTitle"].strip(),
                "part_key": row["partKey"],
                "content": row["content"].strip(),
                "source_url": row.get("sourceUrl"),
                "embedding": vector,
                "embedding_model": embedding_model,
            }
        )
        print(f"[{index}/{len(rows)}] embedded {row['menuKey']}/{row['partKey']}")

    return values


def replace_values(values: list[dict]) -> int:
    stmt = pg_insert(InformationMenuPart).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["menu_key", "part_key"],
        set_={
            "menu_title": stmt.excluded.menu_title,
            "content": stmt.excluded.content,
            "source_url": stmt.excluded.source_url,
            "embedding": stmt.excluded.embedding,
            "embedding_model": stmt.excluded.embedding_model,
        },
    )

    with SessionLocal() as db:
        db.execute(delete(InformationMenuPart))
        result = db.execute(stmt)
        db.commit()
        return int(result.rowcount or 0)


def main() -> None:
    rows = load_topic_detail_rows()
    values = build_values(rows)
    saved_count = replace_values(values)
    print(f"Replaced information menu parts with {saved_count} grouped rows.")


if __name__ == "__main__":
    main()
