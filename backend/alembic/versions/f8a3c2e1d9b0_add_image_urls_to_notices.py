# 파일 기능: notices 테이블에 image_urls 컬럼(text[])을 추가한다.
#            크롤러가 Cloudflare R2에 업로드한 이미지 공개 URL 배열을 저장한다.
"""add image_urls to notices

Revision ID: f8a3c2e1d9b0
Revises: d7e3f1a0b4c5
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "f8a3c2e1d9b0"
down_revision: Union[str, None] = "d7e3f1a0b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # image_urls: 크롤러가 R2에 업로드한 이미지 공개 URL 목록
    # server_default="{}" 로 기존 행은 빈 배열로 채워짐
    op.add_column(
        "notices",
        sa.Column(
            "image_urls",
            postgresql.ARRAY(sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        schema="public",
    )


def downgrade() -> None:
    op.drop_column("notices", "image_urls", schema="public")
