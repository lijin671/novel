"""add batch generation task stage fields

Revision ID: d9c8b7a6f5e4
Revises: b7d4e9f1a2c3
Create Date: 2026-03-24 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d9c8b7a6f5e4"
down_revision: Union[str, None] = "b7d4e9f1a2c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "batch_generation_tasks",
        sa.Column("current_stage", sa.String(length=40), nullable=True, comment="当前执行阶段"),
    )
    op.add_column(
        "batch_generation_tasks",
        sa.Column("stage_message", sa.String(length=255), nullable=True, comment="阶段提示文案"),
    )
    op.add_column(
        "batch_generation_tasks",
        sa.Column("current_stage_progress", sa.Integer(), nullable=True, comment="当前阶段进度"),
    )


def downgrade() -> None:
    op.drop_column("batch_generation_tasks", "current_stage_progress")
    op.drop_column("batch_generation_tasks", "stage_message")
    op.drop_column("batch_generation_tasks", "current_stage")
