"""add information menu parts

Revision ID: e4f8a7b2c901
Revises: c0043515merge
Create Date: 2026-05-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector


revision: str = "e4f8a7b2c901"
down_revision: Union[str, None] = "c0043515merge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "information_menu_parts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("menu_key", sa.String(), nullable=False),
        sa.Column("menu_title", sa.String(), nullable=False),
        sa.Column("part_key", sa.String(), nullable=False),
        sa.Column("part_title", sa.String(), nullable=False),
        sa.Column("section_title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(), nullable=True),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(dim=1536), nullable=False),
        sa.Column("embedding_model", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "menu_key in ('visa', 'topik', 'register', 'scholarship', 'life')",
            name="ck_information_menu_parts_menu_key",
        ),
        sa.CheckConstraint(
            "length(trim(content)) > 0",
            name="ck_information_menu_parts_content_not_blank",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "menu_key",
            "part_key",
            "section_title",
            name="uq_information_menu_parts_menu_part_section",
        ),
    )
    op.create_index(
        "ix_information_menu_parts_menu_part",
        "information_menu_parts",
        ["menu_key", "part_key"],
    )
    op.create_index(
        "ix_information_menu_parts_embedding_hnsw",
        "information_menu_parts",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_information_menu_parts_embedding_hnsw",
        table_name="information_menu_parts",
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.drop_index("ix_information_menu_parts_menu_part", table_name="information_menu_parts")
    op.drop_table("information_menu_parts")
