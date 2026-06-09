"""批量生成任务模型。"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String
from sqlalchemy.sql import func

from app.database import Base


class BatchGenerationTask(Base):
    """章节批量生成任务。"""

    __tablename__ = "batch_generation_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=False, comment="项目ID")
    user_id = Column(String(100), nullable=False, comment="用户ID")

    # 任务配置
    start_chapter_number = Column(Integer, nullable=False, comment="起始章节序号")
    chapter_count = Column(Integer, nullable=False, comment="生成章节数量")
    chapter_ids = Column(JSON, nullable=False, comment="待生成章节ID列表")
    style_id = Column(Integer, comment="使用的写作风格ID")
    target_word_count = Column(Integer, default=3000, comment="目标字数")
    enable_analysis = Column(Boolean, default=False, comment="是否启用同步分析")
    enable_workflow = Column(Boolean, default=False, comment="是否启用自动化全流程")
    workflow_auto_regenerate = Column(Boolean, default=True, comment="工作流是否自动返工")
    workflow_max_rounds = Column(Integer, default=2, comment="工作流最大返工轮次")
    workflow_min_score = Column(Float, default=7.8, comment="工作流通过阈值")

    # 任务状态
    status = Column(
        String(20),
        default="pending",
        comment="任务状态：pending/running/completed/failed/cancelled",
    )
    total_chapters = Column(Integer, default=0, comment="总章节数")
    completed_chapters = Column(Integer, default=0, comment="已完成章节数")
    failed_chapters = Column(JSON, default=list, comment="失败章节信息列表")
    current_chapter_id = Column(String(36), comment="当前正在处理的章节ID")
    current_chapter_number = Column(Integer, comment="当前正在处理的章节序号")
    current_stage = Column(String(40), default="queued", comment="当前执行阶段")
    stage_message = Column(String(255), comment="阶段提示文案")
    current_stage_progress = Column(Integer, default=0, comment="当前阶段进度")
    current_retry_count = Column(Integer, default=0, comment="当前章节重试次数")
    max_retries = Column(Integer, default=3, comment="最大重试次数")

    # 时间记录
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")

    # 错误信息
    error_message = Column(String(500), comment="错误信息")

    def __repr__(self) -> str:
        return (
            f"<BatchGenerationTask(id={self.id}, status={self.status}, "
            f"completed={self.completed_chapters}/{self.total_chapters})>"
        )
