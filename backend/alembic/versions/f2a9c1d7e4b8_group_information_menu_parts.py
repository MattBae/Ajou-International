"""group information menu parts by menu and part

Revision ID: f2a9c1d7e4b8
Revises: e4f8a7b2c901
Create Date: 2026-05-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2a9c1d7e4b8"
down_revision: Union[str, None] = "e4f8a7b2c901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM information_menu_parts")
    op.drop_constraint(
        "uq_information_menu_parts_menu_part_section",
        "information_menu_parts",
        type_="unique",
    )
    op.drop_column("information_menu_parts", "section_title")
    op.drop_column("information_menu_parts", "part_title")
    op.create_unique_constraint(
        "uq_information_menu_parts_menu_part",
        "information_menu_parts",
        ["menu_key", "part_key"],
    )


def downgrade() -> None:
    op.execute("DELETE FROM information_menu_parts")
    op.drop_constraint(
        "uq_information_menu_parts_menu_part",
        "information_menu_parts",
        type_="unique",
    )
    op.add_column("information_menu_parts", sa.Column("part_title", sa.String(), nullable=False))
    op.add_column("information_menu_parts", sa.Column("section_title", sa.String(), nullable=False))
    op.create_unique_constraint(
        "uq_information_menu_parts_menu_part_section",
        "information_menu_parts",
        ["menu_key", "part_key", "section_title"],
    )
