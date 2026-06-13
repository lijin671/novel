"""拆书二创相关 Schema。"""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.book_import import BookImportWarning, ProjectSuggestion
from app.schemas.book_remix_bible import (
    BibleGenerationStatus,
    BookRemixBibleEditableUpdateRequest,
    BookRemixBibleResponse,
)


RemixMode = Literal["continuation", "inspired"]
TaskStatus = Literal["pending", "running", "completed", "failed", "cancelled"]


class BookRemixChapterPreview(BaseModel):
    """拆书二创章节预览。"""

    title: str = Field(..., description="章节标题")
    chapter_number: int = Field(..., ge=1, description="章节序号")
    word_count: int = Field(default=0, ge=0, description="章节字数")
    summary: Optional[str] = Field(default=None, description="章节摘要")


class BookRemixSeedMapping(BaseModel):
    """同类创作模式的启发式映射草案。"""

    source_name: str = Field(..., description="原始元素名")
    occurrence_count: int = Field(default=1, ge=1, description="出现次数")
    sample_context: Optional[str] = Field(default=None, description="示例上下文")
    suggested_target: Optional[str] = Field(default=None, description="建议替换名")
    rewrite_hint: Optional[str] = Field(default=None, description="改写提示")


class BookRemixInspiredSeedProfile(BaseModel):
    """同类创作模式的变体映射草案。"""

    characters: list[BookRemixSeedMapping] = Field(default_factory=list)
    organizations: list[BookRemixSeedMapping] = Field(default_factory=list)
    abilities: list[BookRemixSeedMapping] = Field(default_factory=list)
    world_elements: list[BookRemixSeedMapping] = Field(default_factory=list)
    plot_threads: list[BookRemixSeedMapping] = Field(default_factory=list)


class BookRemixTaskCreateResponse(BaseModel):
    """创建任务响应。"""

    task_id: str
    status: TaskStatus
    remix_mode: RemixMode


class BookRemixTaskStatusResponse(BaseModel):
    """任务状态响应。"""

    task_id: str
    remix_mode: RemixMode
    status: TaskStatus
    progress: int = Field(..., ge=0, le=100)
    message: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BookRemixPreviewResponse(BaseModel):
    """任务预览响应。"""

    task_id: str
    remix_mode: RemixMode
    project_suggestion: ProjectSuggestion
    detected_total_chapters: int = Field(default=0, description="识别到的总章节数")
    total_words: int = Field(default=0, description="识别到的总字数")
    chapters: list[BookRemixChapterPreview]
    warnings: list[BookImportWarning] = Field(default_factory=list)
    inspired_seed_profile: Optional[BookRemixInspiredSeedProfile] = Field(
        default=None,
        description="同类创作模式的启发式变体映射草案",
    )


class BookRemixCreateProjectRequest(BaseModel):
    """创建拆书二创项目请求。"""

    project_suggestion: ProjectSuggestion


class BookRemixRefreshContinuationRequest(BaseModel):
    """刷新已有续写工作台的忠实续写配置。"""

    replace_pending_outlines: bool = Field(
        default=True,
        description="是否删除尚未写正文的旧续写大纲与空章节后重新生成",
    )


class BookRemixRefreshContinuationResponse(BaseModel):
    """刷新已有续写工作台的响应。"""

    success: bool
    project_id: str
    source_chapter_count: int
    refreshed_style_id: Optional[int] = None
    deleted_outlines: int = 0
    deleted_chapters: int = 0
    message: str




class BookRemixContinuationContextPreviewResponse(BaseModel):
    """Preview of the exact remix continuation prompt context."""

    project_id: str
    has_context: bool = False
    context: str = ""
    context_length: int = 0
    context_estimated_tokens: int = 0
    context_budget_risk: Literal["low", "medium", "high"] = "low"
    lineage_confirmed: bool = False
    reason: Optional[str] = None
    source_pattern_pack_loaded: bool = False
    activated_sections: list[dict[str, str]] = Field(default_factory=list)
    active_source_patterns: list[str] = Field(default_factory=list)
    context_warnings: list[str] = Field(default_factory=list)
    production_control_axes: list[str] = Field(default_factory=list)
    production_acceptance_steps: list[str] = Field(default_factory=list)
    production_warnings: list[str] = Field(default_factory=list)
    chapter_progress_report_gap_count: int = 0
    chapter_progress_report_gaps: list[dict[str, Any]] = Field(default_factory=list)
    genre_tracker_warnings: list[str] = Field(default_factory=list)
    entity_arc_timeline_risks: list[str] = Field(default_factory=list)
    source_analysis_coverage_percent: int = 0
    missing_source_analysis_chapters: list[str] = Field(default_factory=list)
    disassembly_checkpoint_warnings: list[str] = Field(default_factory=list)
    mode_contract_axes: dict[str, str] = Field(default_factory=dict)
    mode_contract_warnings: list[str] = Field(default_factory=list)
    chapter_contract_warnings: list[str] = Field(default_factory=list)
    continuity_questions: list[str] = Field(default_factory=list)
    promise_payoff_debts: list[dict[str, str]] = Field(default_factory=list)
    scene_state_snapshot: list[dict[str, str]] = Field(default_factory=list)
    canon_drift_risks: list[str] = Field(default_factory=list)


class BookRemixChapterChangePackageListResponse(BaseModel):
    """Auditable per-chapter continuation change packages."""

    project_id: str
    package_count: int = 0
    offset: int = 0
    limit: int = 100
    items: list[dict[str, Any]] = Field(default_factory=list)


class BookRemixAnalysisCoverageResponse(BaseModel):
    """Coverage and gap report for source-book chapter analysis sync."""

    project_id: str
    source_chapter_count: int = 0
    source_chapters_count: int = 0
    analyzed_chapter_count: int = 0
    chapter_change_package_count: int = 0
    analysis_coverage_percent: int = 0
    change_package_coverage_percent: int = 0
    fully_analyzed: bool = False
    fully_synced: bool = False
    missing_source_chapters: list[int] = Field(default_factory=list)
    missing_analysis_chapters: list[dict[str, Any]] = Field(default_factory=list)
    missing_change_package_chapters: list[dict[str, Any]] = Field(default_factory=list)
    analysis_action_plan: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Actionable next steps grouped by source-book analysis gap type",
    )
    continuation_risk: dict[str, Any] = Field(
        default_factory=dict,
        description="Risk summary for starting continuation before whole-book analysis gaps are closed",
    )


class BookRemixStartMissingAnalysisResponse(BaseModel):
    """Start analysis tasks for missing or unsynced source chapters."""

    project_id: str
    target_chapter_numbers: list[int] = Field(default_factory=list)
    total_started: int = 0
    total_skipped_running: int = 0
    total_skipped_no_content: int = 0
    total_synced_existing: int = 0
    synced_existing_chapters: list[int] = Field(default_factory=list)
    started_tasks: dict[str, dict[str, Any]] = Field(default_factory=dict)


class BookRemixContinuationProgressSummaryResponse(BaseModel):
    """Structured whole-book continuation analysis summary."""

    project_id: str
    package_count: int = 0
    chapter_range: dict[str, Optional[int]] = Field(default_factory=dict)
    timeline_progression: list[dict[str, object]] = Field(default_factory=list)
    latest_character_states: list[dict[str, object]] = Field(default_factory=list)
    emotional_progression: list[dict[str, object]] = Field(default_factory=list)
    resolved_hooks: list[str] = Field(default_factory=list)
    open_hooks: list[str] = Field(default_factory=list)
    completed_plan_beats: list[str] = Field(default_factory=list)
    pending_plan_beats: list[str] = Field(default_factory=list)


class BookRemixBibleReadResponse(BookRemixBibleResponse):
    """Bible review response payload."""


class BookRemixBibleUpdateRequest(BookRemixBibleEditableUpdateRequest):
    """Bible review update payload with editable sections only."""


class BookRemixCreateProjectResponse(BaseModel):
    """创建拆书二创项目响应。"""

    success: bool
    project_id: str
    remix_mode: RemixMode
    total_chapters: int
    total_words: int
    bible_generation_started: bool = False
    bible_generation_status: Optional[BibleGenerationStatus] = None
    prepared_style_id: Optional[int] = None
    analysis_started: bool = False
    analysis_task_count: int = 0
    message: str
