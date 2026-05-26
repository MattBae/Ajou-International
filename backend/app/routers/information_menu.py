import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import InformationMenuPart

router = APIRouter(prefix="/information-menu", tags=["information-menu"])

ALLOWED_MENU_KEYS = {"visa", "topik", "register", "scholarship", "life"}
EMBEDDING_DIMENSIONS = 1536


class InformationMenuEmbeddingRow(BaseModel):
    menuKey: str
    menuTitle: str
    partKey: str
    partTitle: str
    sectionTitle: str
    content: str
    sourceUrl: Optional[str] = None
    embedding: list[float]
    embeddingModel: str


class InformationMenuEmbeddingRequest(BaseModel):
    rows: list[InformationMenuEmbeddingRow]


class InformationMenuPartRow(BaseModel):
    menuKey: str
    menuTitle: str
    partKey: str
    partTitle: str
    sectionTitle: str
    content: str
    sourceUrl: Optional[str] = None


class InformationMenuPartRequest(BaseModel):
    rows: list[InformationMenuPartRow]


@router.post("/parts")
def create_information_menu_parts_with_embeddings(
    body: InformationMenuPartRequest,
    db: Session = Depends(get_db),
):
    if not body.rows:
        raise HTTPException(status_code=422, detail="rows must not be empty")

    embedder = _embedding_function()
    embedding_model = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    rows: list[InformationMenuEmbeddingRow] = []

    for row in body.rows:
        _validate_part_row(row)
        embedding_text = _embedding_text(row)
        try:
            embedding = embedder.embed_query(
                text=embedding_text,
                output_dimensionality=EMBEDDING_DIMENSIONS,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to generate embedding for {row.menuKey}/{row.partKey}/{row.sectionTitle}: {exc}",
            ) from exc

        rows.append(
            InformationMenuEmbeddingRow(
                **row.dict(),
                embedding=embedding,
                embeddingModel=embedding_model,
            )
        )

    return _upsert_embedding_rows(rows, db)


@router.post("/embeddings")
def upsert_information_menu_embeddings(
    body: InformationMenuEmbeddingRequest,
    db: Session = Depends(get_db),
):
    if not body.rows:
        raise HTTPException(status_code=422, detail="rows must not be empty")

    return _upsert_embedding_rows(body.rows, db)


def _upsert_embedding_rows(rows: list[InformationMenuEmbeddingRow], db: Session):
    values = []
    for row in rows:
        _validate_row(row)
        values.append(
            {
                "menu_key": row.menuKey,
                "menu_title": row.menuTitle.strip(),
                "part_key": row.partKey,
                "part_title": row.partTitle.strip(),
                "section_title": row.sectionTitle.strip(),
                "content": row.content.strip(),
                "source_url": row.sourceUrl,
                "embedding": row.embedding,
                "embedding_model": row.embeddingModel.strip(),
            }
        )

    stmt = pg_insert(InformationMenuPart).values(values)
    update_columns = {
        "menu_title": stmt.excluded.menu_title,
        "part_title": stmt.excluded.part_title,
        "content": stmt.excluded.content,
        "source_url": stmt.excluded.source_url,
        "embedding": stmt.excluded.embedding,
        "embedding_model": stmt.excluded.embedding_model,
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=["menu_key", "part_key", "section_title"],
        set_=update_columns,
    )

    result = db.execute(stmt)
    db.commit()

    return {"saved": int(result.rowcount or 0)}


@router.get("/parts")
def list_information_menu_parts(db: Session = Depends(get_db)):
    rows = (
        db.query(InformationMenuPart)
        .order_by(
            InformationMenuPart.menu_key,
            InformationMenuPart.part_key,
            InformationMenuPart.section_title,
        )
        .all()
    )

    return {
        "items": [
            {
                "id": str(row.id),
                "menuKey": row.menu_key,
                "menuTitle": row.menu_title,
                "partKey": row.part_key,
                "partTitle": row.part_title,
                "sectionTitle": row.section_title,
                "content": row.content,
                "sourceUrl": row.source_url,
                "embeddingModel": row.embedding_model,
                "embeddingDimensions": len(row.embedding or []),
                "createdAt": row.created_at,
                "updatedAt": row.updated_at,
            }
            for row in rows
        ],
        "total": len(rows),
    }


def _validate_row(row: InformationMenuEmbeddingRow) -> None:
    _validate_part_row(row)

    if not row.embedding:
        raise HTTPException(
            status_code=422,
            detail=f"embedding is required for {row.menuKey}/{row.partKey}/{row.sectionTitle}",
        )

    if len(row.embedding) != EMBEDDING_DIMENSIONS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"embedding must be {EMBEDDING_DIMENSIONS} dimensions for "
                f"{row.menuKey}/{row.partKey}/{row.sectionTitle}"
            ),
        )

    if not row.embeddingModel or not row.embeddingModel.strip():
        raise HTTPException(status_code=422, detail="embeddingModel must not be empty")


def _validate_part_row(row: InformationMenuPartRow) -> None:
    if row.menuKey not in ALLOWED_MENU_KEYS:
        raise HTTPException(status_code=422, detail=f"Invalid menuKey: {row.menuKey}")

    required_text = {
        "menuTitle": row.menuTitle,
        "partKey": row.partKey,
        "partTitle": row.partTitle,
        "sectionTitle": row.sectionTitle,
        "content": row.content,
    }
    for field, value in required_text.items():
        if not value or not value.strip():
            raise HTTPException(status_code=422, detail=f"{field} must not be empty")


def _embedding_text(row: InformationMenuPartRow) -> str:
    return "\n".join(
        [
            f"메뉴: {row.menuTitle}",
            f"파트: {row.partTitle}",
            f"섹션: {row.sectionTitle}",
            f"내용: {row.content}",
            f"링크: {row.sourceUrl or ''}",
        ]
    )


def _embedding_function():
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

    try:
        from workers.rag.src.rag.embedder import Embedder
    except ModuleNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Embedding dependency is not installed on the backend.",
        ) from exc

    return Embedder().get_embedding_function()
