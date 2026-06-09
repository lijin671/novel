"""Persistent storage for remix continuation bible and plan."""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class BookRemixBible(Base):
    """Canonical persisted continuation bible per project."""

    __tablename__ = "book_remix_bibles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="Project id owning this remix bible",
    )
    source_task_id = Column(
        String(36),
        nullable=True,
        comment="Source remix task id that generated this bible",
    )
    generation_status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="Generation status: pending/running/generated/failed/confirmed",
    )
    source_chapter_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Original source chapter count used for generation",
    )
    world_rules = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="World rules extracted from source book",
    )
    character_cards = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Character cards extracted from source book",
    )
    organizations = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Organization entries extracted from source book",
    )
    timeline = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Timeline entries extracted from source book",
    )
    story_arcs = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Main/sub story arcs extracted from source book",
    )
    foreshadows = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Foreshadow and unresolved causality entries",
    )
    style_signature = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="Style signature summary",
    )
    hard_constraints = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Hard constraints for continuation",
    )
    conflicts = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Conflict and ambiguity entries",
    )
    generation_notes = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Generator notes and reviewer notes",
    )
    chapter_change_packages = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Structured per-chapter continuation change packages",
    )
    created_at = Column(DateTime, server_default=func.now(), comment="Created time")
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Updated time",
    )
    confirmed_at = Column(DateTime, nullable=True, comment="User confirmation time")

    __table_args__ = (
        UniqueConstraint("project_id", name="uq_book_remix_bibles_project_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<BookRemixBible(id={self.id}, project_id={self.project_id}, "
            f"generation_status={self.generation_status})>"
        )


class BookRemixContinuationPlan(Base):
    """Canonical persisted continuation plan per project."""

    __tablename__ = "book_remix_continuation_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="Project id owning this continuation plan",
    )
    bible_id = Column(
        String(36),
        ForeignKey("book_remix_bibles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Bound remix bible id",
    )
    status = Column(
        String(20),
        nullable=False,
        default="draft",
        comment="Plan lifecycle status",
    )
    summary = Column(
        Text,
        nullable=True,
        comment="Plan summary",
    )
    stage_goals = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Stage goals for continuation",
    )
    beats = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Continuation beats",
    )
    priority_hooks = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Priority foreshadow hooks to resolve",
    )
    guardrails = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Hard guardrails for continuation output",
    )
    created_at = Column(DateTime, server_default=func.now(), comment="Created time")
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Updated time",
    )
    confirmed_at = Column(DateTime, nullable=True, comment="User confirmation time")

    __table_args__ = (
        UniqueConstraint("project_id", name="uq_book_remix_continuation_plans_project_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<BookRemixContinuationPlan(id={self.id}, project_id={self.project_id}, "
            f"status={self.status})>"
        )
