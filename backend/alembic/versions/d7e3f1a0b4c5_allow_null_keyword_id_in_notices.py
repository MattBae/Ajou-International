# 파일 기능: notices.keyword_id 컬럼의 NOT NULL 제약을 제거하여 NULL 허용으로 변경한다.
"""allow null keyword_id in notices

Revision ID: d7e3f1a0b4c5
Revises: 6f4a2d1c9e11
Create Date: 2026-04-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7e3f1a0b4c5"
down_revision: Union[str, None] = "a8b9c0d1e2f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # notices.keyword_id 의 NOT NULL 제약을 제거하여 NULL 허용
    op.alter_column("notices", "keyword_id", existing_type=sa.BigInteger(), nullable=True)


def downgrade() -> None:
    # NULL 값이 존재하면 SET NOT NULL 이 실패할 수 있음에 주의
    op.alter_column("notices", "keyword_id", existing_type=sa.BigInteger(), nullable=False)
