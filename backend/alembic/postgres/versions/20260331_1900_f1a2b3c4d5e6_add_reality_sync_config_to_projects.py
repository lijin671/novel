"""add reality_sync_config to projects

Revision ID: f1a2b3c4d5e6
Revises: d9c8b7a6f5e4
Create Date: 2026-03-31 19:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "d9c8b7a6f5e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("reality_sync_config", sa.JSON(), nullable=True, comment="现实资料同步配置(JSON)"),
    )


def downgrade() -> None:
    op.drop_column("projects", "reality_sync_config")
