# 파일 기능: notices 테이블에서 preview 컬럼을 제거한다.
"""drop preview from notices

Revision ID: 3b1e8f4d2a9c
Revises: f8a3c2e1d9b0
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3b1e8f4d2a9c"
down_revision: Union[str, None] = "f8a3c2e1d9b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("notices", "preview", schema="public")


def downgrade() -> None:
    # preview 컬럼 복원: 기존 행은 빈 문자열로 채워짐
    op.add_column(
        "notices",
        sa.Column("preview", sa.Text(), nullable=True),
        schema="public",
    )
