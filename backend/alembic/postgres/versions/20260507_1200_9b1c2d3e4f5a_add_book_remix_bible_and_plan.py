"""add persistent remix bible and continuation plan tables

Revision ID: 9b1c2d3e4f5a
Revises: f1a2b3c4d5e6
Create Date: 2026-05-07 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b1c2d3e4f5a"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "book_remix_bibles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column(
            "source_task_id",
            sa.String(length=36),
            nullable=True,
            comment="Source remix task id that generated this bible",
        ),
        sa.Column(
            "generation_status",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'pending'"),
            comment="Generation status: pending/running/generated/failed/confirmed",
        ),
        sa.Column(
            "source_chapter_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="Original source chapter count used for generation",
        ),
        sa.Column("world_rules", sa.JSON(), nullable=False, comment="World rules extracted from source book"),
        sa.Column("character_cards", sa.JSON(), nullable=False, comment="Character cards extracted from source book"),
        sa.Column("organizations", sa.JSON(), nullable=False, comment="Organization entries extracted from source book"),
        sa.Column("timeline", sa.JSON(), nullable=False, comment="Timeline entries extracted from source book"),
        sa.Column("story_arcs", sa.JSON(), nullable=False, comment="Main/sub story arcs extracted from source book"),
        sa.Column(
            "foreshadows",
            sa.JSON(),
            nullable=False,
            comment="Foreshadow and unresolved causality entries",
        ),
        sa.Column("style_signature", sa.JSON(), nullable=False, comment="Style signature summary"),
        sa.Column("hard_constraints", sa.JSON(), nullable=False, comment="Hard constraints for continuation"),
        sa.Column("conflicts", sa.JSON(), nullable=False, comment="Conflict and ambiguity entries"),
        sa.Column(
            "generation_notes",
            sa.JSON(),
            nullable=False,
            comment="Generator notes and reviewer notes",
        ),
        sa.Column(
            "chapter_change_packages",
            sa.JSON(),
            nullable=False,
            comment="Structured per-chapter continuation change packages",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True, comment="User confirmation time"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", name="uq_book_remix_bibles_project_id"),
    )

    op.create_table(
        "book_remix_continuation_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("bible_id", sa.String(length=36), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'draft'"),
            comment="Plan lifecycle status",
        ),
        sa.Column("summary", sa.Text(), nullable=True, comment="Plan summary"),
        sa.Column("stage_goals", sa.JSON(), nullable=False, comment="Stage goals for continuation"),
        sa.Column("beats", sa.JSON(), nullable=False, comment="Continuation beats"),
        sa.Column("priority_hooks", sa.JSON(), nullable=False, comment="Priority hooks to resolve"),
        sa.Column("guardrails", sa.JSON(), nullable=False, comment="Hard guardrails for continuation output"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True, comment="User confirmation time"),
        sa.ForeignKeyConstraint(["bible_id"], ["book_remix_bibles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", name="uq_book_remix_continuation_plans_project_id"),
    )
    op.create_index(
        op.f("ix_book_remix_continuation_plans_bible_id"),
        "book_remix_continuation_plans",
        ["bible_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_book_remix_continuation_plans_bible_id"),
        table_name="book_remix_continuation_plans",
    )
    op.drop_table("book_remix_continuation_plans")
    op.drop_table("book_remix_bibles")
