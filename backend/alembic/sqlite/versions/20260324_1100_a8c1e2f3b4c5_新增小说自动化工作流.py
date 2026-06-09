"""新增小说自动化工作流

Revision ID: a8c1e2f3b4c5
Revises: d887fd1a30a6
Create Date: 2026-03-24 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8c1e2f3b4c5'
down_revision: Union[str, None] = 'd887fd1a30a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'novel_workflow_tasks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('chapter_ids', sa.JSON(), nullable=False),
        sa.Column('source', sa.String(length=30), nullable=True),
        sa.Column('auto_regenerate', sa.Boolean(), nullable=True),
        sa.Column('max_rounds', sa.Integer(), nullable=True),
        sa.Column('min_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('total_chapters', sa.Integer(), nullable=True),
        sa.Column('completed_chapters', sa.Integer(), nullable=True),
        sa.Column('current_chapter_id', sa.String(length=36), nullable=True),
        sa.Column('current_chapter_number', sa.Integer(), nullable=True),
        sa.Column('failed_chapters', sa.JSON(), nullable=True),
        sa.Column('result_summary', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_novel_workflow_tasks_project_id'), 'novel_workflow_tasks', ['project_id'], unique=False)
    op.create_index(op.f('ix_novel_workflow_tasks_user_id'), 'novel_workflow_tasks', ['user_id'], unique=False)

    op.create_table(
        'chapter_workflow_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('workflow_task_id', sa.String(length=36), nullable=True),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('chapter_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('source', sa.String(length=30), nullable=True),
        sa.Column('round_index', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('decision', sa.String(length=20), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('analysis_score', sa.Float(), nullable=True),
        sa.Column('review_score', sa.Float(), nullable=True),
        sa.Column('reader_score', sa.Float(), nullable=True),
        sa.Column('reviewers', sa.JSON(), nullable=True),
        sa.Column('reader_feedback', sa.JSON(), nullable=True),
        sa.Column('aggregate', sa.JSON(), nullable=True),
        sa.Column('revision_brief', sa.Text(), nullable=True),
        sa.Column('applied_regeneration', sa.Boolean(), nullable=True),
        sa.Column('regeneration_task_id', sa.String(length=36), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workflow_task_id'], ['novel_workflow_tasks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chapter_workflow_results_chapter_id'), 'chapter_workflow_results', ['chapter_id'], unique=False)
    op.create_index(op.f('ix_chapter_workflow_results_project_id'), 'chapter_workflow_results', ['project_id'], unique=False)
    op.create_index(op.f('ix_chapter_workflow_results_user_id'), 'chapter_workflow_results', ['user_id'], unique=False)
    op.create_index(op.f('ix_chapter_workflow_results_workflow_task_id'), 'chapter_workflow_results', ['workflow_task_id'], unique=False)

    with op.batch_alter_table('batch_generation_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('enable_workflow', sa.Boolean(), nullable=True, comment='是否启用自动化全流程'))
        batch_op.add_column(sa.Column('workflow_auto_regenerate', sa.Boolean(), nullable=True, comment='工作流是否自动返工'))
        batch_op.add_column(sa.Column('workflow_max_rounds', sa.Integer(), nullable=True, comment='工作流最大返工轮次'))
        batch_op.add_column(sa.Column('workflow_min_score', sa.Float(), nullable=True, comment='工作流通过阈值'))


def downgrade() -> None:
    with op.batch_alter_table('batch_generation_tasks', schema=None) as batch_op:
        batch_op.drop_column('workflow_min_score')
        batch_op.drop_column('workflow_max_rounds')
        batch_op.drop_column('workflow_auto_regenerate')
        batch_op.drop_column('enable_workflow')

    op.drop_index(op.f('ix_chapter_workflow_results_workflow_task_id'), table_name='chapter_workflow_results')
    op.drop_index(op.f('ix_chapter_workflow_results_user_id'), table_name='chapter_workflow_results')
    op.drop_index(op.f('ix_chapter_workflow_results_project_id'), table_name='chapter_workflow_results')
    op.drop_index(op.f('ix_chapter_workflow_results_chapter_id'), table_name='chapter_workflow_results')
    op.drop_table('chapter_workflow_results')

    op.drop_index(op.f('ix_novel_workflow_tasks_user_id'), table_name='novel_workflow_tasks')
    op.drop_index(op.f('ix_novel_workflow_tasks_project_id'), table_name='novel_workflow_tasks')
    op.drop_table('novel_workflow_tasks')
