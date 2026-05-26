from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import select

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.app.database import SessionLocal  # noqa: E402
from backend.app.models import InformationMenuPart  # noqa: E402
from workers.rag.src.rag.embedder import Embedder  # noqa: E402

EMBEDDING_DIMENSIONS = 1536


def embedding_text(row: InformationMenuPart) -> str:
    return "\n".join(
        [
            f"주제: {row.menu_title}",
            f"내용: {row.content}",
            f"링크: {row.source_url or ''}",
        ]
    )


def main() -> None:
    embedding_model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    embedder = Embedder().get_embedding_function()

    with SessionLocal() as db:
        rows = (
            db.execute(
                select(InformationMenuPart).order_by(
                    InformationMenuPart.menu_key,
                    InformationMenuPart.part_key,
                )
            )
            .scalars()
            .all()
        )

        if not rows:
            print("No information menu parts found.")
            return

        for index, row in enumerate(rows, start=1):
            vector = embedder.embed_query(
                text=embedding_text(row),
                output_dimensionality=EMBEDDING_DIMENSIONS,
            )
            if len(vector) != EMBEDDING_DIMENSIONS:
                raise RuntimeError(
                    f"Expected {EMBEDDING_DIMENSIONS} dimensions, got {len(vector)} "
                    f"for {row.menu_key}/{row.part_key}"
                )
            row.embedding = vector
            row.embedding_model = embedding_model
            print(f"[{index}/{len(rows)}] embedded {row.menu_key}/{row.part_key}")

        db.commit()
        print(f"Updated {len(rows)} information menu embeddings.")


if __name__ == "__main__":
    main()
