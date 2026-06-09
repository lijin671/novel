"""小说自动化工作流数据模型"""
from sqlalchemy import Column, String, Text, Integer, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid


class NovelWorkflowTask(Base):
    """项目级自动化工作流任务"""
    __tablename__ = "novel_workflow_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True, comment="用户ID")

    chapter_ids = Column(JSON, nullable=False, comment="待处理章节ID列表")
    source = Column(String(30), default="manual", comment="触发来源: manual/batch_generate/auto_pipeline")
    auto_regenerate = Column(Boolean, default=True, comment="是否自动返工")
    max_rounds = Column(Integer, default=2, comment="单章最大返工轮次")
    min_score = Column(Float, default=7.8, comment="通过阈值")

    status = Column(String(20), default="pending", comment="任务状态: pending/running/completed/failed/cancelled")
    total_chapters = Column(Integer, default=0, comment="总章节数")
    completed_chapters = Column(Integer, default=0, comment="已完成章节数")
    current_chapter_id = Column(String(36), comment="当前处理中的章节ID")
    current_chapter_number = Column(Integer, comment="当前处理中的章节序号")
    failed_chapters = Column(JSON, default=list, comment="失败章节信息")
    result_summary = Column(JSON, default=dict, comment="结果摘要")
    error_message = Column(Text, comment="错误信息")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")

    def __repr__(self):
        return f"<NovelWorkflowTask(id={self.id}, status={self.status}, completed={self.completed_chapters}/{self.total_chapters})>"


class ChapterWorkflowResult(Base):
    """章节级自动化工作流结果"""
    __tablename__ = "chapter_workflow_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_task_id = Column(
        String(36),
        ForeignKey("novel_workflow_tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="关联的项目级工作流任务ID"
    )
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True, comment="用户ID")

    source = Column(String(30), default="manual", comment="触发来源: manual/batch_generate/auto_pipeline")
    round_index = Column(Integer, default=1, comment="当前轮次")
    status = Column(String(20), default="completed", comment="状态: completed/failed")
    decision = Column(String(20), default="pass", comment="决策: pass/revise/max_rounds_reached")

    overall_score = Column(Float, default=0.0, comment="综合评分")
    analysis_score = Column(Float, default=0.0, comment="章节分析评分")
    review_score = Column(Float, default=0.0, comment="多评审评分")
    reader_score = Column(Float, default=0.0, comment="读者模拟评分")

    reviewers = Column(JSON, default=list, comment="多评审结果")
    reader_feedback = Column(JSON, default=list, comment="读者模拟结果")
    aggregate = Column(JSON, default=dict, comment="聚合结论")
    revision_brief = Column(Text, comment="返工建议")
    applied_regeneration = Column(Boolean, default=False, comment="是否已自动返工")
    regeneration_task_id = Column(String(36), nullable=True, comment="关联返工任务ID")
    error_message = Column(Text, comment="错误信息")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    completed_at = Column(DateTime, comment="完成时间")

    def __repr__(self):
        return f"<ChapterWorkflowResult(id={self.id}, chapter_id={self.chapter_id}, round={self.round_index}, decision={self.decision})>"
