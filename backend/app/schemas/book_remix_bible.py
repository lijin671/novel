"""Schemas for remix bible and continuation plan persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


BibleGenerationStatus = Literal["pending", "running", "generated", "failed", "confirmed"]
PlanStatus = Literal["draft", "confirmed"]


class BookRemixBibleBase(BaseModel):
    """Shared fields for remix bible payloads."""

    source_task_id: Optional[str] = Field(default=None, description="Source remix task id")
    generation_status: BibleGenerationStatus = Field(
        default="pending",
        description="Generation status",
    )
    source_chapter_count: int = Field(default=0, ge=0, description="Source chapter count")
    world_rules: dict[str, Any] = Field(
        default_factory=dict,
        description="World rules extracted from source book",
    )
    character_cards: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Character cards extracted from source book",
    )
    organizations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Organizations extracted from source book",
    )
    timeline: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Timeline entries extracted from source book",
    )
    story_arcs: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Story arcs extracted from source book",
    )
    foreshadows: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Foreshadow and unresolved causality entries",
    )
    style_signature: dict[str, Any] = Field(
        default_factory=dict,
        description="Style signature summary",
    )
    hard_constraints: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Hard constraints for continuation",
    )
    conflicts: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Conflict and ambiguity entries",
    )
    generation_notes: list[str] = Field(default_factory=list, description="Generation and reviewer notes")
    chapter_change_packages: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Structured chapter-analysis change packages for continuation context",
    )
    confirmed_at: Optional[datetime] = Field(default=None, description="User confirmation time")


class BookRemixBibleCreate(BookRemixBibleBase):
    """Create payload for a remix bible."""

    project_id: str = Field(..., description="Owning project id")


class BookRemixBibleUpdate(BaseModel):
    """Partial update payload for remix bible."""

    source_task_id: Optional[str] = None
    generation_status: Optional[BibleGenerationStatus] = None
    source_chapter_count: Optional[int] = Field(default=None, ge=0)
    world_rules: Optional[dict[str, Any]] = None
    character_cards: Optional[list[dict[str, Any]]] = None
    organizations: Optional[list[dict[str, Any]]] = None
    timeline: Optional[list[dict[str, Any]]] = None
    story_arcs: Optional[list[dict[str, Any]]] = None
    foreshadows: Optional[list[dict[str, Any]]] = None
    style_signature: Optional[dict[str, Any]] = None
    hard_constraints: Optional[list[dict[str, Any]]] = None
    conflicts: Optional[list[dict[str, Any]]] = None
    generation_notes: Optional[list[str]] = None
    chapter_change_packages: Optional[list[dict[str, Any]]] = None
    confirmed_at: Optional[datetime] = None


class BookRemixBibleEditableUpdateRequest(BaseModel):
    """Editable sections exposed to bible review API."""

    character_cards: Optional[list[dict[str, Any]]] = None
    timeline: Optional[list[dict[str, Any]]] = None
    story_arcs: Optional[list[dict[str, Any]]] = None
    foreshadows: Optional[list[dict[str, Any]]] = None
    hard_constraints: Optional[list[dict[str, Any]]] = None

    model_config = ConfigDict(extra="forbid")


class BookRemixBibleResponse(BookRemixBibleBase):
    """API response model for remix bible."""

    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookRemixContinuationPlanBase(BaseModel):
    """Shared fields for continuation plan payloads."""

    status: PlanStatus = Field(default="draft", description="Continuation plan lifecycle status")
    summary: Optional[str] = Field(default=None, description="Plan summary")
    stage_goals: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Stage goals for continuation",
    )
    beats: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Continuation beats",
    )
    priority_hooks: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Priority hooks to resolve",
    )
    guardrails: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Hard guardrails for continuation output",
    )
    confirmed_at: Optional[datetime] = Field(default=None, description="User confirmation time")


class BookRemixContinuationPlanGenerateRequest(BaseModel):
    """Generate payload for continuation plan draft."""

    user_direction: str = Field(default="", description="Optional user direction before generation")

    model_config = ConfigDict(extra="forbid")


class BookRemixContinuationPlanUpdateRequest(BaseModel):
    """Editable sections exposed to continuation plan review API."""

    summary: Optional[str] = None
    stage_goals: Optional[list[dict[str, Any]]] = None
    beats: Optional[list[dict[str, Any]]] = None
    priority_hooks: Optional[list[dict[str, Any]]] = None
    guardrails: Optional[list[dict[str, Any]]] = None

    model_config = ConfigDict(extra="forbid")


class BookRemixContinuationPlanCreate(BookRemixContinuationPlanBase):
    """Create payload for continuation plan."""

    project_id: str = Field(..., description="Owning project id")
    bible_id: Optional[str] = Field(default=None, description="Bound remix bible id")


class BookRemixContinuationPlanUpdate(BaseModel):
    """Partial update payload for continuation plan."""

    bible_id: Optional[str] = None
    status: Optional[PlanStatus] = None
    summary: Optional[str] = None
    stage_goals: Optional[list[dict[str, Any]]] = None
    beats: Optional[list[dict[str, Any]]] = None
    priority_hooks: Optional[list[dict[str, Any]]] = None
    guardrails: Optional[list[dict[str, Any]]] = None
    confirmed_at: Optional[datetime] = None


class BookRemixContinuationPlanResponse(BookRemixContinuationPlanBase):
    """API response model for continuation plan."""

    id: str
    project_id: str
    bible_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
