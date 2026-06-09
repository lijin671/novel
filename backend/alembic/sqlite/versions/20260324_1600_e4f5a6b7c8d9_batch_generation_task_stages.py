"""add batch generation task stage fields

Revision ID: e4f5a6b7c8d9
Revises: a8c1e2f3b4c5
Create Date: 2026-03-24 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4f5a6b7c8d9"
down_revision: Union[str, None] = "a8c1e2f3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("batch_generation_tasks", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("current_stage", sa.String(length=40), nullable=True, comment="当前执行阶段")
        )
        batch_op.add_column(
            sa.Column("stage_message", sa.String(length=255), nullable=True, comment="阶段提示文案")
        )
        batch_op.add_column(
            sa.Column("current_stage_progress", sa.Integer(), nullable=True, comment="当前阶段进度")
        )


def downgrade() -> None:
    with op.batch_alter_table("batch_generation_tasks", schema=None) as batch_op:
        batch_op.drop_column("current_stage_progress")
        batch_op.drop_column("stage_message")
        batch_op.drop_column("current_stage")
