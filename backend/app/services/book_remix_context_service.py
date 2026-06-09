"""Build remix continuation context blocks for prompt injection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan
from app.models.project import Project
from app.services.source_discovery_service import source_discovery_service
from app.services.source_pattern_pack_prompt import render_source_pattern_pack_digest


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def build_remix_continuation_progress_summary(
    *,
    packages: Any,
    plan: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build a structured whole-book continuation progress summary."""
    ordered_packages = _sort_by_chapter_asc(_chapter_analysis_packages(packages))
    chapter_numbers = [_int_or_none(package.get("chapter_number")) for package in ordered_packages]
    chapter_numbers = [number for number in chapter_numbers if number is not None]

    return {
        "package_count": len(ordered_packages),
        "chapter_range": _chapter_range_payload(chapter_numbers),
        "timeline_progression": _timeline_progression_payload(ordered_packages),
        "latest_character_states": _latest_character_state_payload(ordered_packages, max_items=8),
        "emotional_progression": _emotional_progression_payload(ordered_packages, max_items=12),
        "resolved_hooks": _hook_status_summary(ordered_packages)[0],
        "open_hooks": _hook_status_summary(ordered_packages)[1],
        "completed_plan_beats": _completed_plan_beats(ordered_packages, plan=plan, max_items=12),
        "pending_plan_beats": _pending_plan_beats(plan=plan, max_items=12),
    }


def build_remix_continuation_context_block(
    *,
    project_title: str,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]] = None,
) -> str:
    """Render a stable prompt block from confirmed remix bible and current plan."""
    normalized_title = (project_title or "").strip() or "Untitled Project"
    lines: list[str] = [
        "【Remix Continuation Canon】",
        f"Project: {normalized_title}",
        "Apply these continuity constraints before writing any new outline or chapter.",
    ]

    _append_source_pattern_pack_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_context_activation_audit_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )
    _append_scene_graph_review_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_plotgrid_reveal_branch_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_acceptance_loop_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_manuscript_structure_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_inspectable_rewrite_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_production_review_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_consistency_style_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_research_multimodal_experiment_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_serialized_continuity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_story_quality_evaluation_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_reader_market_feedback_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_delivery_packaging_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_interactive_narrative_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_copy_similarity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_near_duplicate_semantic_dedup_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_text_analysis_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_stylometry_style_overfit_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_copyedit_prose_lint_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_chinese_text_processing_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_import_extraction_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_literary_event_graph_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_segmentation_summary_topic_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_eval_observability_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_long_output_reward_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_creative_writing_benchmark_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_story_generation_pipeline_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_deconstruction_memory_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_canon_graph_retrieval_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )

    world_rules = bible.get("world_rules")
    if isinstance(world_rules, dict) and world_rules:
        lines.append("")
        lines.append("World rules to preserve:")
        for key, value in list(world_rules.items())[:12]:
            lines.append(f"- {key}: {_truncate(str(value), 220)}")

    _append_dict_section(
        lines=lines,
        title="Hard constraints",
        items=bible.get("hard_constraints"),
        preferred_keys=("rule", "constraint", "content", "name"),
        max_items=12,
    )

    character_cards = _as_dict_list(bible.get("character_cards"))
    _append_dict_section(
        lines=lines,
        title="Character continuity cards",
        items=character_cards,
        preferred_keys=("name", "role", "goal", "summary", "trait", "identity"),
        max_items=12,
    )
    _append_character_update_section(lines=lines, cards=character_cards, max_items=12)

    _append_dict_section(
        lines=lines,
        title="Organizations to preserve",
        items=bible.get("organizations"),
        preferred_keys=("name", "role", "summary", "status", "relationship"),
        max_items=12,
    )

    _append_style_signature_section(
        lines=lines,
        style_signature=bible.get("style_signature"),
    )

    _append_dict_section(
        lines=lines,
        title="Conflict and emotion arcs",
        items=bible.get("conflicts"),
        preferred_keys=("name", "conflict", "summary", "status", "pressure"),
        max_items=12,
    )

    timeline = _as_dict_list(bible.get("timeline"))
    _append_dict_section(
        lines=lines,
        title="Latest machine timeline",
        items=_latest_chapter_analysis_items(timeline, max_items=10),
        preferred_keys=("event", "summary", "milestone", "impact"),
        max_items=10,
    )
    _append_dict_section(
        lines=lines,
        title="Manual timeline anchors",
        items=_manual_items(timeline, max_items=6),
        preferred_keys=("event", "milestone", "time", "date", "summary", "impact"),
        max_items=6,
    )
    if not _latest_chapter_analysis_items(timeline, max_items=1) and not _manual_items(timeline, max_items=1):
        _append_dict_section(
            lines=lines,
            title="Timeline anchors",
            items=timeline,
            preferred_keys=("event", "milestone", "time", "date", "summary", "impact"),
            max_items=12,
        )

    _append_dict_section(
        lines=lines,
        title="Story arcs to preserve",
        items=bible.get("story_arcs"),
        preferred_keys=("name", "arc", "summary", "goal"),
        max_items=12,
    )

    chapter_change_packages = _chapter_analysis_packages(bible.get("chapter_change_packages"))
    _append_whole_book_progress_section(
        lines=lines,
        packages=chapter_change_packages,
        plan=plan,
    )
    _append_chapter_change_package_section(
        lines=lines,
        packages=chapter_change_packages,
        max_items=5,
    )

    foreshadows = _as_dict_list(bible.get("foreshadows"))
    _append_dict_section(
        lines=lines,
        title="Open hooks",
        items=_status_items(foreshadows, done=False, max_items=10),
        preferred_keys=("hook", "title", "content", "summary"),
        max_items=10,
    )
    _append_dict_section(
        lines=lines,
        title="Resolved hooks",
        items=_status_items(foreshadows, done=True, max_items=8),
        preferred_keys=("hook", "title", "content", "summary"),
        max_items=8,
    )
    if not foreshadows:
        _append_dict_section(
            lines=lines,
            title="Foreshadows and unresolved hooks",
            items=foreshadows,
            preferred_keys=("hook", "title", "content", "summary"),
            max_items=12,
        )

    if plan:
        summary = str(plan.get("summary") or "").strip()
        if summary:
            lines.append("")
            lines.append(f"Current continuation strategy: {summary}")
        _append_dict_section(
            lines=lines,
            title="Stage goals",
            items=plan.get("stage_goals"),
            preferred_keys=("goal", "summary", "content", "name"),
            max_items=8,
        )

        beats = _as_dict_list(plan.get("beats"))
        _append_dict_section(
            lines=lines,
            title="Pending planned beats",
            items=_status_items(beats, done=False, max_items=8),
            preferred_keys=("beat", "summary", "content", "name"),
            max_items=8,
        )
        _append_dict_section(
            lines=lines,
            title="Done planned beats",
            items=_status_items(beats, done=True, max_items=8),
            preferred_keys=("beat", "summary", "content", "name"),
            max_items=8,
        )
        if not beats:
            _append_dict_section(
                lines=lines,
                title="Planned beats",
                items=beats,
                preferred_keys=("beat", "summary", "content", "name"),
                max_items=10,
            )

        priority_hooks = _as_dict_list(plan.get("priority_hooks"))
        _append_dict_section(
            lines=lines,
            title="Pending priority hooks",
            items=_status_items(priority_hooks, done=False, max_items=8),
            preferred_keys=("hook", "title", "content", "summary"),
            max_items=8,
        )
        _append_dict_section(
            lines=lines,
            title="Done priority hooks",
            items=_status_items(priority_hooks, done=True, max_items=8),
            preferred_keys=("hook", "title", "content", "summary"),
            max_items=8,
        )
        if not priority_hooks:
            _append_dict_section(
                lines=lines,
                title="Priority hooks",
                items=priority_hooks,
                preferred_keys=("hook", "title", "content", "summary"),
                max_items=10,
            )

        _append_dict_section(
            lines=lines,
            title="Plan guardrails",
            items=plan.get("guardrails"),
            preferred_keys=("rule", "constraint", "content", "name"),
            max_items=12,
        )

    return "\n".join(lines).strip()


def build_remix_inspired_context_block(
    *,
    project_title: str,
    style_content: str,
    source_pattern_pack: Optional[dict[str, Any]] = None,
) -> str:
    """Render a stable same-type creation context block from inspired style anchors."""
    normalized_title = (project_title or "").strip() or "Untitled Inspired Project"
    normalized_style = (style_content or "").strip()
    if not normalized_style:
        return ""
    if not _is_inspired_style_content(normalized_style):
        return ""

    lines: list[str] = [
        "【Remix Inspired Creation Context】",
        f"Project: {normalized_title}",
        "Do not treat this as continuation canon. This is same-type creation guidance.",
        "Use only source rhythm, POV behavior, pacing, scene density, and emotional temperature.",
        "Do not copy source names, organizations, event order, set pieces, or distinctive wording.",
    ]

    _append_inspired_style_section(
        lines=lines,
        title="Source style principles",
        style_content=normalized_style,
        heading="【同类型创作总原则】",
        max_items=8,
    )
    _append_inspired_style_section(
        lines=lines,
        title="Source voice samples",
        style_content=normalized_style,
        heading="【源书语气样本】",
        max_items=6,
    )
    _append_inspired_style_section(
        lines=lines,
        title="Forbidden source elements",
        style_content=normalized_style,
        heading="【源书显性元素禁用清单】",
        max_items=8,
    )

    _append_source_pattern_pack_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        title="Source-discovered inspired guidance:",
        include_inspired_guidance=True,
    )
    _append_inspired_transformation_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_serialized_continuity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_story_quality_evaluation_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_reader_market_feedback_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_interactive_narrative_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_copy_similarity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_near_duplicate_semantic_dedup_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_text_analysis_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_stylometry_style_overfit_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_copyedit_prose_lint_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_chinese_text_processing_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_import_extraction_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_literary_event_graph_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_segmentation_summary_topic_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_eval_observability_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_deconstruction_memory_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_canon_graph_retrieval_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )

    return "\n".join(lines).strip()


def _is_inspired_style_content(style_content: str) -> bool:
    lowered = style_content.lower()
    same_type_marker = (
        "\u540c\u7c7b\u578b\u521b\u4f5c" in style_content
        or "same-type creation" in lowered
        or "inspired creation" in lowered
    )
    source_marker = (
        "\u6e90\u4e66" in style_content
        or "source voice" in lowered
        or "forbidden source" in lowered
    )
    return bool(same_type_marker and source_marker)


class BookRemixContextService:
    """Owns remix-only continuation context assembly for prompts."""

    async def has_project_durable_remix_lineage(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> bool:
        """Check whether project keeps durable remix continuation lineage markers."""
        bible = await self._load_project_bible(db=db, project_id=project.id)
        return self._has_durable_remix_lineage(bible=bible)

    async def build_project_context_block(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> str:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        plan = await self._load_project_plan(db=db, project_id=project.id)
        if not self._has_confirmed_remix_lineage(bible=bible, plan=plan):
            return ""

        plan_payload = self._to_plan_payload(plan)
        if not plan_payload:
            return ""

        source_pattern_pack = await self._resolve_source_pattern_pack()
        return build_remix_continuation_context_block(
            project_title=project.title,
            bible=self._to_bible_payload(bible),
            plan=plan_payload,
            source_pattern_pack=source_pattern_pack,
        )

    async def build_project_context_preview(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Return the exact continuation context block plus readiness metadata."""
        bible = await self._load_project_bible(db=db, project_id=project.id)
        plan = await self._load_project_plan(db=db, project_id=project.id)
        reason = self._confirmed_remix_lineage_blocker(bible=bible, plan=plan)
        if reason:
            return {
                "project_id": project.id,
                "has_context": False,
                "context": "",
                "context_length": 0,
                "lineage_confirmed": False,
                "reason": reason,
            }

        plan_payload = self._to_plan_payload(plan)
        if not plan_payload:
            return {
                "project_id": project.id,
                "has_context": False,
                "context": "",
                "context_length": 0,
                "lineage_confirmed": False,
                "reason": "continuation_plan_not_confirmed",
            }

        source_pattern_pack = await self._resolve_source_pattern_pack()
        context = build_remix_continuation_context_block(
            project_title=project.title,
            bible=self._to_bible_payload(bible),
            plan=plan_payload,
            source_pattern_pack=source_pattern_pack,
        )
        return {
            "project_id": project.id,
            "has_context": bool(context),
            "context": context,
            "context_length": len(context),
            "lineage_confirmed": bool(context),
            "reason": None if context else "empty_context",
            "source_pattern_pack_loaded": bool(source_pattern_pack),
        }

    async def _resolve_source_pattern_pack(self) -> dict[str, Any]:
        return await source_discovery_service.resolve_fresh_pattern_pack(
            repo_root=PROJECT_ROOT,
        )

    async def _load_project_bible(
        self,
        *,
        db: AsyncSession,
        project_id: str,
    ) -> Optional[BookRemixBible]:
        result = await db.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def _load_project_plan(
        self,
        *,
        db: AsyncSession,
        project_id: str,
    ) -> Optional[BookRemixContinuationPlan]:
        result = await db.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project_id
            )
        )
        return result.scalar_one_or_none()

    def _to_bible_payload(self, bible: BookRemixBible) -> dict[str, Any]:
        return {
            "world_rules": bible.world_rules or {},
            "hard_constraints": bible.hard_constraints or [],
            "character_cards": bible.character_cards or [],
            "organizations": bible.organizations or [],
            "timeline": bible.timeline or [],
            "story_arcs": bible.story_arcs or [],
            "foreshadows": bible.foreshadows or [],
            "style_signature": bible.style_signature or {},
            "conflicts": bible.conflicts or [],
            "chapter_change_packages": bible.chapter_change_packages or [],
        }

    def _has_confirmed_remix_lineage(
        self,
        *,
        bible: Optional[BookRemixBible],
        plan: Optional[BookRemixContinuationPlan],
    ) -> bool:
        return self._confirmed_remix_lineage_blocker(bible=bible, plan=plan) is None

    def _confirmed_remix_lineage_blocker(
        self,
        *,
        bible: Optional[BookRemixBible],
        plan: Optional[BookRemixContinuationPlan],
    ) -> Optional[str]:
        if not bible:
            return "remix_bible_not_found"
        if not self._has_durable_remix_lineage(bible=bible):
            return "durable_remix_lineage_missing"
        if not plan:
            return "continuation_plan_not_found"

        bible_status = str(bible.generation_status or "").strip().lower()
        if bible_status != "confirmed":
            return "remix_bible_not_confirmed"

        plan_status = str(plan.status or "").strip().lower()
        if plan_status != "confirmed":
            return "continuation_plan_not_confirmed"

        linked_bible_id = str(plan.bible_id or "").strip()
        if not linked_bible_id or linked_bible_id != str(bible.id):
            return "continuation_plan_not_bound_to_current_bible"

        if plan.updated_at and bible.updated_at and plan.updated_at < bible.updated_at:
            return "continuation_plan_stale_against_bible"

        return None

    def _has_durable_remix_lineage(
        self,
        *,
        bible: Optional[BookRemixBible],
    ) -> bool:
        if not bible:
            return False
        source_task_id = str(bible.source_task_id or "").strip()
        if not source_task_id:
            return False
        return int(bible.source_chapter_count or 0) > 0

    def _to_plan_payload(
        self,
        plan: Optional[BookRemixContinuationPlan],
    ) -> Optional[dict[str, Any]]:
        if not plan:
            return None
        plan_status = str(plan.status or "").strip().lower()
        if plan_status != "confirmed":
            return None
        return {
            "summary": plan.summary or "",
            "stage_goals": plan.stage_goals or [],
            "beats": plan.beats or [],
            "priority_hooks": plan.priority_hooks or [],
            "guardrails": plan.guardrails or [],
        }


def _append_whole_book_progress_section(
    *,
    lines: list[str],
    packages: list[dict[str, Any]],
    plan: Optional[dict[str, Any]],
) -> None:
    ordered_packages = _sort_by_chapter_asc(packages)
    if not ordered_packages:
        return

    lines.append("")
    lines.append("Whole-book continuation progress:")
    chapter_numbers = [_int_or_none(package.get("chapter_number")) for package in ordered_packages]
    chapter_numbers = [number for number in chapter_numbers if number is not None]
    if chapter_numbers:
        first_chapter = chapter_numbers[0]
        last_chapter = chapter_numbers[-1]
        chapter_range = str(first_chapter) if first_chapter == last_chapter else f"{first_chapter}-{last_chapter}"
        lines.append(f"- Continuation chapters with context: {chapter_range} ({len(ordered_packages)} packages)")
    else:
        lines.append(f"- Continuation context packages: {len(ordered_packages)}")

    timeline_progression = _build_timeline_progression(ordered_packages)
    if timeline_progression:
        lines.append(f"- Timeline progression: {_truncate(timeline_progression, 360)}")

    character_states = _latest_character_states(ordered_packages, max_items=4)
    if character_states:
        lines.append(f"- Latest character states: {'; '.join(character_states)}")

    resolved_hooks, open_hooks = _hook_status_summary(ordered_packages)
    if resolved_hooks:
        lines.append(f"- Resolved hooks: {'; '.join(resolved_hooks[:5])}")
    if open_hooks:
        lines.append(f"- Open hooks: {'; '.join(open_hooks[:5])}")

    completed_beats = _completed_plan_beats(ordered_packages, plan=plan, max_items=5)
    if completed_beats:
        lines.append(f"- Completed plan beats: {'; '.join(completed_beats)}")


def _chapter_analysis_packages(packages: Any) -> list[dict[str, Any]]:
    normalized_packages = [
        package
        for package in _as_dict_list(packages)
        if _is_machine_continuation_source(package.get("source"))
    ]
    generation_guardrails = {
        key: package.get("guardrail_check")
        for package in normalized_packages
        if _string_value(package.get("source")) == "chapter_generation"
        for key in (_chapter_identity_key(package),)
        if key is not None and isinstance(package.get("guardrail_check"), dict)
    }
    analysis_keys = {
        key
        for package in normalized_packages
        if _string_value(package.get("source")) == "chapter_analysis"
        for key in (_chapter_identity_key(package),)
        if key is not None
    }
    preferred_packages: list[dict[str, Any]] = []
    for package in normalized_packages:
        key = _chapter_identity_key(package)
        source = _string_value(package.get("source"))
        if source == "chapter_generation" and key in analysis_keys:
            continue
        if source == "chapter_analysis" and key in generation_guardrails and "guardrail_check" not in package:
            package = {**package, "guardrail_check": generation_guardrails[key]}
        preferred_packages.append(package)
    return _sort_by_chapter_desc(preferred_packages)


def _chapter_identity_key(package: dict[str, Any]) -> tuple[str, int | str] | None:
    chapter_number = _int_or_none(package.get("chapter_number"))
    if chapter_number is not None:
        return ("chapter_number", chapter_number)
    chapter_id = _string_value(package.get("chapter_id"))
    if chapter_id:
        return ("chapter_id", chapter_id)
    return None


def _chapter_range_payload(chapter_numbers: list[int]) -> dict[str, int | None]:
    if not chapter_numbers:
        return {"start": None, "end": None}
    return {"start": chapter_numbers[0], "end": chapter_numbers[-1]}


def _timeline_progression_payload(packages: list[dict[str, Any]], *, max_items: int = 12) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for package in packages[-max_items:]:
        chapter_number = _int_or_none(package.get("chapter_number"))
        for item in _as_dict_list(package.get("timeline_delta")):
            event = _first_text(item, ("event", "summary", "content"))
            if not event:
                continue
            points.append({"chapter_number": chapter_number, "event": event})
            break
    return points


def _latest_character_state_payload(packages: list[dict[str, Any]], *, max_items: int) -> list[dict[str, Any]]:
    latest_by_character: dict[str, dict[str, Any]] = {}
    for package in packages:
        chapter_number = _int_or_none(package.get("chapter_number"))
        for item in _as_dict_list(package.get("character_state_changes")):
            name = _string_value(item.get("character_name") or item.get("name"))
            state_after = _string_value(item.get("state_after"))
            if not name or not state_after:
                continue
            previous = latest_by_character.get(name)
            current_chapter = chapter_number or 0
            previous_chapter = int(previous.get("chapter_number") or 0) if previous else -1
            if previous is None or current_chapter >= previous_chapter:
                latest_by_character[name] = {
                    "character_name": name,
                    "chapter_number": chapter_number,
                    "state_after": state_after,
                }

    return sorted(
        latest_by_character.values(),
        key=lambda item: int(item.get("chapter_number") or 0),
        reverse=True,
    )[:max_items]


def _emotional_progression_payload(
    packages: list[dict[str, Any]],
    *,
    max_items: int,
) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for package in packages[-max_items:]:
        emotional_arc = package.get("emotional_arc")
        if not isinstance(emotional_arc, dict):
            continue

        item: dict[str, Any] = {
            "chapter_number": _int_or_none(package.get("chapter_number")),
        }
        tone = _string_value(
            emotional_arc.get("tone")
            or emotional_arc.get("primary_emotion")
            or emotional_arc.get("emotion")
        )
        if tone:
            item["tone"] = tone
        if emotional_arc.get("intensity") is not None:
            item["intensity"] = emotional_arc.get("intensity")
        if emotional_arc.get("curve") is not None:
            item["curve"] = emotional_arc.get("curve")

        if len(item) > 1:
            points.append(item)
    return points


def _build_timeline_progression(packages: list[dict[str, Any]], *, max_items: int = 4) -> str:
    points: list[str] = []
    for package in packages[-max_items:]:
        chapter_number = package.get("chapter_number")
        for item in _as_dict_list(package.get("timeline_delta")):
            event = _first_text(item, ("event", "summary", "content"))
            if not event:
                continue
            prefix = f"Ch{chapter_number} " if chapter_number not in (None, "") else ""
            points.append(f"{prefix}{event}")
            break
    return " -> ".join(points)


def _latest_character_states(packages: list[dict[str, Any]], *, max_items: int) -> list[str]:
    latest_by_character: dict[str, tuple[int, str]] = {}
    for package in packages:
        chapter_number = _int_or_none(package.get("chapter_number")) or 0
        for item in _as_dict_list(package.get("character_state_changes")):
            name = _string_value(item.get("character_name") or item.get("name"))
            state_after = _string_value(item.get("state_after"))
            if not name or not state_after:
                continue
            previous = latest_by_character.get(name)
            if previous is None or chapter_number >= previous[0]:
                latest_by_character[name] = (chapter_number, state_after)

    ordered = sorted(latest_by_character.items(), key=lambda item: item[1][0], reverse=True)
    states: list[str] = []
    for name, (chapter_number, state_after) in ordered[:max_items]:
        chapter = f" @ Ch{chapter_number}" if chapter_number else ""
        states.append(f"{name}{chapter} -> {state_after}")
    return states


def _hook_status_summary(packages: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    resolved: list[str] = []
    opened: list[str] = []
    for package in packages:
        for item in _as_dict_list(package.get("foreshadow_changes")):
            hook = _first_text(item, ("hook", "title", "content", "summary"))
            if not hook:
                continue
            if _is_done_status(item.get("status")):
                _append_unique(resolved, hook)
            else:
                _append_unique(opened, hook)
    return resolved, opened


def _pending_plan_beats(*, plan: Optional[dict[str, Any]], max_items: int) -> list[str]:
    if not plan:
        return []
    pending: list[str] = []
    for item in _status_items(_as_dict_list(plan.get("beats")), done=False, max_items=max_items):
        beat = _first_text(item, ("beat", "summary", "content", "name"))
        if beat:
            _append_unique(pending, beat)
    return pending[:max_items]


def _completed_plan_beats(
    packages: list[dict[str, Any]],
    *,
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> list[str]:
    completed: list[str] = []
    for package in packages:
        for item in _as_dict_list(package.get("plan_progress")):
            if not _is_done_status(item.get("status")):
                continue
            beat = _first_text(item, ("beat", "summary", "content", "name"))
            if beat:
                _append_unique(completed, beat)

    if len(completed) < max_items and plan:
        for item in _status_items(_as_dict_list(plan.get("beats")), done=True, max_items=max_items):
            beat = _first_text(item, ("beat", "summary", "content", "name"))
            if beat:
                _append_unique(completed, beat)
    return completed[:max_items]


def _append_unique(items: list[str], value: str) -> None:
    normalized = value.strip().lower()
    if not normalized:
        return
    if any(existing.strip().lower() == normalized for existing in items):
        return
    items.append(value)


def _append_chapter_change_package_section(
    *,
    lines: list[str],
    packages: Any,
    max_items: int,
) -> None:
    normalized_packages = _chapter_analysis_packages(packages)[:max_items]
    if not normalized_packages:
        return

    lines.append("")
    lines.append("Recent chapter change packages:")
    for package in normalized_packages:
        chapter_label = _chapter_package_label(package)
        summary = _string_value(package.get("summary"))
        if summary:
            lines.append(f"- {chapter_label}: {_truncate(summary, 220)}")
        else:
            lines.append(f"- {chapter_label}")

        for item in _as_dict_list(package.get("timeline_delta"))[:3]:
            event = _first_text(item, ("event", "summary", "content"))
            if event:
                lines.append(f"  - timeline: {_truncate(event, 220)}")

        for item in _as_dict_list(package.get("character_state_changes"))[:3]:
            name = _string_value(item.get("character_name") or item.get("name")) or "Unknown character"
            state_after = _string_value(item.get("state_after"))
            key_event = _string_value(item.get("key_event"))
            detail = f"{name} -> {state_after}" if state_after else name
            if key_event:
                detail = f"{detail} ({key_event})"
            lines.append(f"  - character: {_truncate(detail, 220)}")

        emotional_arc = package.get("emotional_arc") if isinstance(package.get("emotional_arc"), dict) else None
        if emotional_arc:
            emotion_parts: list[str] = []
            tone = _string_value(
                emotional_arc.get("tone")
                or emotional_arc.get("primary_emotion")
                or emotional_arc.get("emotion")
            )
            if tone:
                emotion_parts.append(f"tone: {tone}")
            if emotional_arc.get("intensity") is not None:
                emotion_parts.append(f"intensity: {emotional_arc.get('intensity')}")
            if emotional_arc.get("curve") is not None:
                curve = json.dumps(emotional_arc.get("curve"), ensure_ascii=False, sort_keys=True)
                emotion_parts.append(f"curve: {curve}")
            if emotion_parts:
                lines.append(f"  - emotion: {_truncate(' | '.join(emotion_parts), 220)}")

        for item in _as_dict_list(package.get("foreshadow_changes"))[:3]:
            hook = _first_text(item, ("hook", "title", "content", "summary"))
            status = _string_value(item.get("status"))
            suffix = f" (status: {status})" if status else ""
            lines.append(f"  - hook: {_truncate(hook + suffix, 220)}")

        for item in _as_dict_list(package.get("plan_progress"))[:3]:
            beat = _first_text(item, ("beat", "summary", "content", "name"))
            status = _string_value(item.get("status"))
            suffix = f" (status: {status})" if status else ""
            lines.append(f"  - plan: {_truncate(beat + suffix, 220)}")

        guardrail_check = package.get("guardrail_check") if isinstance(package.get("guardrail_check"), dict) else None
        if guardrail_check:
            lines.append(f"  - Guardrail rewrite applied: {bool(guardrail_check.get('applied'))}")
            violations = _as_dict_list(guardrail_check.get("violations"))
            for violation in violations[:3]:
                violation_type = _string_value(violation.get("type"))
                severity = _string_value(violation.get("severity"))
                description = _first_text(violation, ("description", "detail", "message", "title"))
                parts = [part for part in (violation_type, severity, description) if part]
                if parts:
                    lines.append(f"  - guardrail: {_truncate(' | '.join(parts), 220)}")


def _append_source_pattern_pack_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    title: str = "Source-discovered continuation guidance:",
    include_inspired_guidance: bool = False,
) -> None:
    if not source_pattern_pack:
        return

    digest = render_source_pattern_pack_digest(
        source_pattern_pack,
        include_inspired_guidance=include_inspired_guidance,
    )
    if not digest or digest.startswith("(no public source pattern pack"):
        return

    lines.append("")
    lines.append(title)
    lines.extend(digest.splitlines())


def _append_context_activation_audit_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render an explicit audit of which context layers should be active."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if not pattern_names:
        return

    activated_sections = _activated_context_sections(bible=bible, plan=plan)
    if not activated_sections:
        return

    lines.append("")
    lines.append("Context activation audit:")
    for label, detail in activated_sections[:12]:
        lines.append(f"- {label}: {detail}")

    if "lorebook_context" in pattern_names:
        lines.append("- activated_lore_entries: activate by current chapter goal and keywords; do not inject unrelated lore.")
    if "context_reference" in pattern_names:
        lines.append("- context_reference_set: record section/card/chapter and reason before drafting.")
    if "world_state_tracking" in pattern_names:
        lines.append("- world_state_slices: update only changed entity, location, faction, or item state after the chapter.")
    if "author_note_layer" in pattern_names:
        lines.append("- author_note_layer: next-chapter local style reminder; expires after this chapter.")

    if pattern_names.intersection({"lorebook_context", "context_reference", "world_state_tracking"}):
        lines.append("")
        lines.append("Context budget notes:")
        lines.append("- Prioritize current beat, latest state, open hook, active character, and direct organization/faction constraints.")
        lines.append("- Leave inactive-but-relevant lore out of the prompt and mention it only in review notes.")
        lines.append("- Avoid loading full bible/history when a compact card or chapter-change package already proves the state.")

    if "memory_snapshot_versioning" in pattern_names:
        lines.append("")
        lines.append("Rollback guidance:")
        lines.append("- Create a named memory snapshot before risky rewrite, branch merge, or bulk bible update.")
        lines.append("- Rejected drafts must revert prose plus timeline, character, organization, hook, and plan-progress state.")


def _append_scene_graph_review_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render graph/workspace gates learned from static source intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "scene_level_generation",
        "content_ref_externalization",
        "review_queue_staging",
        "style_guide_layering",
        "entity_schema_custom_fields",
        "graph_healing",
        "contradiction_detection",
        "graph_branching_atomicity",
        "query_lint_contract",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Scene graph review audit:")
    if "scene_level_generation" in pattern_names:
        lines.append("- scene_generation_units: plan scene goal, cast, location, pressure, reveal, and exit hook before drafting")
    if "content_ref_externalization" in pattern_names:
        lines.append("- external_content_refs: store large scene plans, drafts, extraction payloads, and review reports as refs with integrity metadata")
    if "review_queue_staging" in pattern_names:
        lines.append("- pending_change_queue: stage AI-proposed canon/style/card/chapter changes before applying them")
    if "style_guide_layering" in pattern_names:
        lines.append("- style_layer_stack: base style guide -> scene override -> character voice notes")
    if "entity_schema_custom_fields" in pattern_names:
        lines.append("- entity_custom_fields: validate genre-specific fields before prompt injection or canon write-back")
    if "graph_healing" in pattern_names:
        lines.append("- graph_healing_review: surface duplicate entities, orphan lore, and stale edges as reviewable candidates")
    if "contradiction_detection" in pattern_names:
        lines.append("- contradiction_gate: block acceptance on timeline, relationship, location, trait, or hook conflicts")
    if "graph_branching_atomicity" in pattern_names:
        lines.append("- branch_atomicity: publish multi-slice canon updates only after branch/snapshot validation passes")
    if "query_lint_contract" in pattern_names:
        lines.append("- query_lint_contract: lint generated mutations for target entity, relationship type, required fields, and delete/update separation")


def _append_plotgrid_reveal_branch_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render plotgrid, reveal, setup/payoff, and branch gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "premature_ending_guard",
        "layered_memory_model",
        "plot_dependency_graph",
        "plotgrid_scene_matrix",
        "plotline_thread_tracking",
        "scene_status_dashboard",
        "gradual_reveal_control",
        "setup_payoff_tracking",
        "scene_type_directing",
        "alternate_timeline_branching",
        "divergence_guidance",
        "worldpkg_export",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Plotgrid reveal branch audit:")
    if "premature_ending_guard" in pattern_names:
        lines.append("- premature_ending_guard: check whether the draft falsely resolves the main conflict, skips payoff windows, or closes the book too early")
    if "layered_memory_model" in pattern_names:
        lines.append("- memory_layer_order: story bible -> character state -> plot dependency graph; do not let a lower layer override confirmed canon")
    if "plot_dependency_graph" in pattern_names:
        lines.append("- plot_dependency_graph: every payoff should trace back to an active setup, clue, promise, or unresolved hook")
    if "plotgrid_scene_matrix" in pattern_names:
        lines.append("- plotgrid_scene_matrix: map each scene against plotline, POV, location, emotion, status, and thread coverage")
    if "plotline_thread_tracking" in pattern_names:
        lines.append("- plotline_thread_tracking: keep active, paused, paid-off, and abandoned threads visible before drafting")
    if "scene_status_dashboard" in pattern_names:
        lines.append("- scene_status_dashboard: mark scene cards by planned, drafted, reviewed, accepted, or blocked state before write-back")
    if "gradual_reveal_control" in pattern_names:
        lines.append("- gradual_reveal_budget: expose world facts through action and dialogue; keep hidden-layer facts out until triggered")
    if "setup_payoff_tracking" in pattern_names:
        lines.append("- setup_payoff_ledger: record setup chapter, expected payoff window, payoff state, and dependency risk")
    if "scene_type_directing" in pattern_names:
        lines.append("- scene_type_directing: declare scene mode before drafting so pacing, dialogue ratio, camera distance, and sensory density match the scene function")
    if "alternate_timeline_branching" in pattern_names:
        lines.append("- alternate_timeline_branch: branch what-if or same-world divergence state away from faithful continuation canon")
    if "divergence_guidance" in pattern_names:
        lines.append("- divergence_guidance: name the player/new-story choice that causes branch drift and list which canon facts stay fixed")
    if "worldpkg_export" in pattern_names:
        lines.append("- worldpkg_export_boundary: exported world packages are reusable context artifacts, not automatic canon mutations")


def _append_acceptance_loop_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render context-pack, accepted-memory, critic, resume, and rewrite gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "context_pack_preview",
        "accepted_chapter_memory",
        "critic_verifier_loop",
        "collapse_prevention",
        "trend_deconstruction_pipeline",
        "anti_ai_tone_polish",
        "preference_memory",
        "interrupted_resume_flow",
        "auto_validation_rewrite",
        "top_down_story_planning",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Acceptance loop audit:")
    if "context_pack_preview" in pattern_names:
        lines.append("- context_pack_preview: list included canon facts, retrieval reasons, token budget, and omitted-but-relevant context before drafting")
    if "accepted_chapter_memory" in pattern_names:
        lines.append("- accepted_chapter_memory: drafts cannot update canon; only accepted chapters may extract memory and feed the next context pack")
    if "critic_verifier_loop" in pattern_names:
        lines.append("- critic_verifier_loop: keep writer/reviser output separate from critic/verifier findings and verification results")
    if "collapse_prevention" in pattern_names:
        lines.append("- collapse_prevention: block write-back on invalid output, causality break, state contradiction, or repeated model failure")
    if "trend_deconstruction_pipeline" in pattern_names:
        lines.append("- trend_deconstruction_pipeline: use deconstructed trope modules as transformed craft pressure, not copied source route")
    if "anti_ai_tone_polish" in pattern_names:
        lines.append("- anti_ai_tone_polish: remove explanation-heavy AI tone after continuity passes without paraphrasing source prose")
    if "preference_memory" in pattern_names:
        lines.append("- preference_memory_boundary: apply user preference to style defaults only; never override canon state")
    if "interrupted_resume_flow" in pattern_names:
        lines.append("- interrupted_resume_flow: resume from current phase, chapter, scene, last accepted artifact, and pending validation status")
    if "auto_validation_rewrite" in pattern_names:
        lines.append("- auto_validation_rewrite: validate word count, coherence, hook, style, and state write-back before bounded retry")
    if "top_down_story_planning" in pattern_names:
        lines.append("- top_down_story_planning: preserve hierarchy from book spec to act, chapter, scene, and previous-scene context")


def _append_manuscript_structure_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render mature writing-tool manuscript planning gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "plain_text_project_storage",
        "synopsis_cross_reference",
        "snowflake_premise_expansion",
        "outliner_index_cards",
        "narrative_strand_mapping",
        "character_depth_interview",
        "mindmap_visual_planning",
        "manuscript_export_formats",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Manuscript structure audit:")
    if "plain_text_project_storage" in pattern_names:
        lines.append("- plain_text_project_storage: keep chapters, notes, summaries, and analysis as stable human-readable units")
    if "synopsis_cross_reference" in pattern_names:
        lines.append("- synopsis_cross_reference: link synopsis, comments, notes, and chapter refs before drafting")
    if "snowflake_premise_expansion" in pattern_names:
        lines.append("- snowflake_premise_expansion: preserve the premise chain from sentence to paragraph to full summary")
    if "outliner_index_cards" in pattern_names:
        lines.append("- outliner_index_cards: keep chapter and scene cards reorderable without losing state evidence")
    if "narrative_strand_mapping" in pattern_names:
        lines.append("- narrative_strand_mapping: map premise, fabula, narrative strands, and setting context before accepting arc changes")
    if "character_depth_interview" in pattern_names:
        lines.append("- character_depth_interview: verify desire, fear, contradiction, social mask, and pressure before major character turns")
    if "mindmap_visual_planning" in pattern_names:
        lines.append("- mindmap_visual_planning: keep visual idea nodes separate from canon until accepted into outline or bible")
    if "manuscript_export_formats" in pattern_names:
        lines.append("- manuscript_export_formats: treat PDF/DOCX/TXT/EPUB exports as derived artifacts, not canon sources")


def _append_delivery_packaging_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render final manuscript assembly, preview, export, and metadata gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "delivery_manuscript_assembly",
        "export_format_fidelity_audit",
        "preview_toc_packaging",
        "cover_kdp_metadata_boundary",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Delivery packaging audit:")
    if "delivery_manuscript_assembly" in pattern_names:
        lines.append("- delivery_manuscript_assembly: assemble only accepted chapters; verify count, order, missing numbers, duplicates, headings, empty titles, and SHA256")
    if "export_format_fidelity_audit" in pattern_names:
        lines.append("- export_format_fidelity_audit: verify chapter order, headings, title page, TOC, page numbers, paragraph boundaries, and derived-export manifest")
    if "preview_toc_packaging" in pattern_names:
        lines.append("- preview_toc_packaging: generate preview and table-of-contents from the same accepted chapter list used by final export")
    if "cover_kdp_metadata_boundary" in pattern_names:
        lines.append("- cover_kdp_metadata_boundary: keep cover and KDP metadata as publication artifacts; never let them mutate canon or chapter text")


def _append_interactive_narrative_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render branching narrative, dialogue-node, passage-link, and choice-state gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "branching_choice_graph",
        "node_dialogue_state_machine",
        "passage_link_navigation_map",
        "choice_stats_consequence_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Interactive narrative audit:")
    if "branching_choice_graph" in pattern_names:
        lines.append("- branching_choice_graph: model choices as branch edges with source node, option intent, consequence scope, and merge/reject decision")
    if "node_dialogue_state_machine" in pattern_names:
        lines.append("- node_dialogue_state_machine: dialogue nodes declare entry conditions, speaker state, available options, commands, and exit deltas")
    if "passage_link_navigation_map" in pattern_names:
        lines.append("- passage_link_navigation_map: passage links need reachable path checks, intentional merge points, and no accidental dead ends")
    if "choice_stats_consequence_gate" in pattern_names:
        lines.append("- choice_stats_consequence_gate: every choice-stat mutation needs visible consequence, trigger record, stat delta, and payoff window")


def _append_copy_similarity_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render source-copy fingerprint, fuzzy phrase, and diff-span gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "source_text_fingerprint_gate",
        "fuzzy_phrase_similarity_gate",
        "diff_span_copy_review",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Copy similarity audit:")
    if "source_text_fingerprint_gate" in pattern_names:
        lines.append("- source_text_fingerprint_gate: compare source and draft fingerprints; review high-overlap windows before acceptance")
    if "fuzzy_phrase_similarity_gate" in pattern_names:
        lines.append("- fuzzy_phrase_similarity_gate: apply fuzzy phrase thresholds to catch paraphrased source sentences and renamed proper-noun strings")
    if "diff_span_copy_review" in pattern_names:
        lines.append("- diff_span_copy_review: inspect diff spans for copied wording, source sentence order, semantic-cleanup matches, and patch-like edits")


def _append_near_duplicate_semantic_dedup_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render MinHash/SimHash/semantic dedup independence gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "minhash_lsh_near_duplicate_gate",
        "simhash_hamming_similarity_gate",
        "semantic_duplicate_cluster_gate",
        "embedding_similarity_independence_gate",
        "corpus_leakage_dedup_review_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Near-duplicate and semantic dedup audit:")
    if "minhash_lsh_near_duplicate_gate" in pattern_names:
        lines.append("- minhash_lsh_near_duplicate_gate: compare source and draft shingles; review high-Jaccard near-duplicate windows before acceptance")
    if "simhash_hamming_similarity_gate" in pattern_names:
        lines.append("- simhash_hamming_similarity_gate: flag low-Hamming-distance windows that survive renaming, translation, or polish")
    if "semantic_duplicate_cluster_gate" in pattern_names:
        lines.append("- semantic_duplicate_cluster_gate: cluster semantic neighbors so paraphrased source scenes cannot pass as independent drafts")
    if "embedding_similarity_independence_gate" in pattern_names:
        lines.append("- embedding_similarity_independence_gate: require key passages to be closer to transformed canon/brief than to source excerpts")
    if "corpus_leakage_dedup_review_gate" in pattern_names:
        lines.append("- corpus_leakage_dedup_review_gate: keep source corpora, deconstruction notes, transformed canon, and drafts in separate leakage-auditable manifests")


def _append_text_analysis_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render character quote, readability, lexical, and motif metric gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "character_quote_attribution_map",
        "readability_pacing_metric_gate",
        "lexical_diversity_voice_audit",
        "keyphrase_motif_extraction",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Text analysis audit:")
    if "character_quote_attribution_map" in pattern_names:
        lines.append("- character_quote_attribution_map: map mentions, aliases, quotes, speakers, and quote ownership before voice or relationship review")
    if "readability_pacing_metric_gate" in pattern_names:
        lines.append("- readability_pacing_metric_gate: compare sentence-length, paragraph-density, readability, and scene-density curves before acceptance")
    if "lexical_diversity_voice_audit" in pattern_names:
        lines.append("- lexical_diversity_voice_audit: monitor lexical diversity, repeated vocabulary clusters, MTLD/HD-D drift, and speaker-specific diction")
    if "keyphrase_motif_extraction" in pattern_names:
        lines.append("- keyphrase_motif_extraction: extract keyphrases and motif terms to audit promise coverage, topic drift, and copied source-specific anchors")


def _append_stylometry_style_overfit_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render stylometry, authorship similarity, and style-overfit gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "stylometric_author_fingerprint_gate",
        "function_word_syntax_style_gate",
        "authorship_attribution_similarity_gate",
        "style_overfit_regression_gate",
        "paraphrase_independence_review_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Stylometry and style-overfit audit:")
    if "stylometric_author_fingerprint_gate" in pattern_names:
        lines.append("- stylometric_author_fingerprint_gate: version explicit style fingerprints and keep source-author profiles separate from new-story voice")
    if "function_word_syntax_style_gate" in pattern_names:
        lines.append("- function_word_syntax_style_gate: review function words, punctuation, sentence length, and syntax windows as evidence, not automatic rewrites")
    if "authorship_attribution_similarity_gate" in pattern_names:
        lines.append("- authorship_attribution_similarity_gate: treat high source-author similarity as a copy-risk signal rather than a style target")
    if "style_overfit_regression_gate" in pattern_names:
        lines.append("- style_overfit_regression_gate: run windowed regression after paraphrase, polish, and entity remap to catch source-voice leakage")
    if "paraphrase_independence_review_gate" in pattern_names:
        lines.append("- paraphrase_independence_review_gate: require independence evidence before accepting humanized, transferred, or same-type prose")


def _append_copyedit_prose_lint_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render prose lint, grammar, and diagnostic triage gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "prose_lint_style_rule_gate",
        "grammar_spelling_copyedit_gate",
        "copyedit_diagnostic_triage_queue",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Copyedit and prose lint audit:")
    if "prose_lint_style_rule_gate" in pattern_names:
        lines.append("- prose_lint_style_rule_gate: apply project-local house style rules with speaker, scene, and deliberate-voice exceptions")
    if "grammar_spelling_copyedit_gate" in pattern_names:
        lines.append("- grammar_spelling_copyedit_gate: check grammar, spelling, and copyedit blockers after canon review, while preserving dialogue/register exceptions")
    if "copyedit_diagnostic_triage_queue" in pattern_names:
        lines.append("- copyedit_diagnostic_triage_queue: classify diagnostics as accept, ignore, rewrite, or needs-author-review before chapter acceptance")


def _append_chinese_text_processing_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render Chinese segmentation, NER/alias, normalization, and correction gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "chinese_segmentation_keyword_gate",
        "chinese_ner_alias_consistency_gate",
        "chinese_text_normalization_gate",
        "chinese_error_correction_review_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Chinese text processing audit:")
    if "chinese_segmentation_keyword_gate" in pattern_names:
        lines.append("- chinese_segmentation_keyword_gate: use a project dictionary before Chinese keyword, motif, and retrieval analysis")
    if "chinese_ner_alias_consistency_gate" in pattern_names:
        lines.append("- chinese_ner_alias_consistency_gate: audit character, alias, location, organization, and title consistency before canon write-back")
    if "chinese_text_normalization_gate" in pattern_names:
        lines.append("- chinese_text_normalization_gate: normalize Simplified/Traditional, punctuation width, and variants only as review evidence unless accepted")
    if "chinese_error_correction_review_gate" in pattern_names:
        lines.append("- chinese_error_correction_review_gate: triage typo/correction suggestions while protecting names, dialect, and invented terms")


def _append_source_import_extraction_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render source-format import, PDF/OCR, partition, and provenance gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "source_format_import_manifest",
        "pdf_layout_text_extraction_gate",
        "ocr_scanned_page_import_gate",
        "document_partition_chapter_detection_gate",
        "import_provenance_checksum_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Source import extraction audit:")
    if "source_format_import_manifest" in pattern_names:
        lines.append("- source_format_import_manifest: record source format, metadata, TOC/spine order, detected chapters, and skipped sections before deconstruction")
    if "pdf_layout_text_extraction_gate" in pattern_names:
        lines.append("- pdf_layout_text_extraction_gate: review PDF page spans, text blocks, reading order, headers/footers, and extraction gaps before analysis")
    if "ocr_scanned_page_import_gate" in pattern_names:
        lines.append("- ocr_scanned_page_import_gate: route scanned-page OCR confidence gaps and low-confidence spans to manual review before canon or style extraction")
    if "document_partition_chapter_detection_gate" in pattern_names:
        lines.append("- document_partition_chapter_detection_gate: keep typed document elements and uncertain chapter headings separate until accepted")
    if "import_provenance_checksum_gate" in pattern_names:
        lines.append("- import_provenance_checksum_gate: keep original, extracted, normalized, and accepted text artifacts linked by checksum, parser version, and settings")


def _append_literary_event_graph_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render literary annotation, event graph, emotion arc, and character-network gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "literary_event_entity_annotation_gate",
        "narrative_event_evolution_graph_gate",
        "sentiment_arc_emotion_trajectory_gate",
        "cross_context_coreference_gate",
        "character_interaction_network_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Literary event graph audit:")
    if "literary_event_entity_annotation_gate" in pattern_names:
        lines.append("- literary_event_entity_annotation_gate: separate source entities, events, participant roles, and mention spans before canon or summary write-back")
    if "narrative_event_evolution_graph_gate" in pattern_names:
        lines.append("- narrative_event_evolution_graph_gate: review temporal, causal, discourse, blocker, and payoff edges before using source event chains")
    if "sentiment_arc_emotion_trajectory_gate" in pattern_names:
        lines.append("- sentiment_arc_emotion_trajectory_gate: track global and character emotion curves with turning-point reasons, not as automatic quality scores")
    if "cross_context_coreference_gate" in pattern_names:
        lines.append("- cross_context_coreference_gate: keep ambiguous cross-chapter/source mention clusters out of accepted canon until reviewed")
    if "character_interaction_network_gate" in pattern_names:
        lines.append("- character_interaction_network_gate: audit interaction frequency, centrality, relationship polarity, and timing before accepting relationship canon")


def _append_segmentation_summary_topic_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render chunking, chapter-summary, and topic-drift gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "semantic_chunk_boundary_map",
        "chapter_summary_anchor_gate",
        "topic_drift_map",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Segmentation, summary, and topic audit:")
    if "semantic_chunk_boundary_map" in pattern_names:
        lines.append("- semantic_chunk_boundary_map: split source and generated chapters at semantic boundaries with chunk id, overlap policy, boundary reason, and inclusion purpose")
    if "chapter_summary_anchor_gate" in pattern_names:
        lines.append("- chapter_summary_anchor_gate: anchor every summary to accepted chapter ids, representative sentences, canon status, and unresolved-hook evidence")
    if "topic_drift_map" in pattern_names:
        lines.append("- topic_drift_map: map topic clusters across chapters and flag off-arc drift, missing promises, or copied source topic sequence")


def _append_eval_observability_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render grounding, trace, and prompt-regression gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "context_faithfulness_eval_gate",
        "retrieval_trace_observability_gate",
        "prompt_regression_eval_suite",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Evaluation, trace, and regression audit:")
    if "context_faithfulness_eval_gate" in pattern_names:
        lines.append("- context_faithfulness_eval_gate: score generated facts against accepted canon, retrieved context, summary anchors, and grounding evidence before write-back")
    if "retrieval_trace_observability_gate" in pattern_names:
        lines.append("- retrieval_trace_observability_gate: persist query, selected chunks, omitted candidates, relevance reason, and generation spans for context review")
    if "prompt_regression_eval_suite" in pattern_names:
        lines.append("- prompt_regression_eval_suite: run golden continuation and same-type cases before prompt-pack or context-selection changes")


def _append_long_output_reward_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render plan-write, long-output, and reward-dimension gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "agentwrite_plan_write_pipeline",
        "long_output_length_quality_ruler",
        "long_context_reward_dimension_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Long output plan-write reward audit:")
    if "agentwrite_plan_write_pipeline" in pattern_names:
        lines.append("- agentwrite_plan_write_pipeline: validate plan artifacts before prose expansion and link each write stage to its plan segment")
    if "long_output_length_quality_ruler" in pattern_names:
        lines.append("- long_output_length_quality_ruler: check target length, actual length, truncation, repetition, premature ending, coherence, canon, and style together")
    if "long_context_reward_dimension_gate" in pattern_names:
        lines.append("- long_context_reward_dimension_gate: score helpfulness, logicality, faithfulness, and completeness separately; do not average away blocking failures")


def _append_creative_writing_benchmark_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render creative-writing benchmark, judge, and reader-axis gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "instance_specific_writing_criteria_gate",
        "material_grounded_query_refinement",
        "hybrid_rubric_pairwise_elo_judge",
        "judge_bias_mitigation_check",
        "plan_reflect_character_chapter_pipeline",
        "human_story_metric_panel",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Creative writing benchmark audit:")
    if "instance_specific_writing_criteria_gate" in pattern_names:
        lines.append("- instance_specific_writing_criteria_gate: attach local criteria for canon, requested beat, style target, length/format, and reader promise")
    if "material_grounded_query_refinement" in pattern_names:
        lines.append("- material_grounded_query_refinement: prune irrelevant reference material and rewrite ambiguous chapter tasks before drafting")
    if "hybrid_rubric_pairwise_elo_judge" in pattern_names:
        lines.append("- hybrid_rubric_pairwise_elo_judge: score candidates by rubric before pairwise comparison; do not let length bias decide the winner")
    if "judge_bias_mitigation_check" in pattern_names:
        lines.append("- judge_bias_mitigation_check: swap comparison order and inspect length, position, verbosity, and ornate-prose bias")
    if "plan_reflect_character_chapter_pipeline" in pattern_names:
        lines.append("- plan_reflect_character_chapter_pipeline: persist brainstorm, plan critique, and character-profile updates before chapter writing")
    if "human_story_metric_panel" in pattern_names:
        lines.append("- human_story_metric_panel: track relevance, coherence, empathy, surprise, engagement, and complexity as separate reader-facing axes")


def _append_story_generation_pipeline_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render hierarchical generation, recursive revision, persona, and event-realization gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "hierarchical_cowriting_story_scaffold",
        "human_coauthor_edit_boundary",
        "recursive_reprompt_revision_loop",
        "reranker_guided_candidate_selection",
        "character_dialogue_persona_memory",
        "event_to_sentence_realization_trace",
        "entity_memory_slotfill_grounding",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Story generation pipeline audit:")
    if "hierarchical_cowriting_story_scaffold" in pattern_names:
        lines.append("- hierarchical_cowriting_story_scaffold: validate logline, character, plot-point, location, and dialogue layers separately before prose expansion")
    if "human_coauthor_edit_boundary" in pattern_names:
        lines.append("- human_coauthor_edit_boundary: treat generated material as editable co-writing output; inspect plagiarism, toxicity, stereotype, and formulaic risks")
    if "recursive_reprompt_revision_loop" in pattern_names:
        lines.append("- recursive_reprompt_revision_loop: keep plan, draft, rewrite, and edit as separate evidence-backed stages")
    if "reranker_guided_candidate_selection" in pattern_names:
        lines.append("- reranker_guided_candidate_selection: compare candidates by relevance to plan and coherence with accepted canon before choosing")
    if "character_dialogue_persona_memory" in pattern_names:
        lines.append("- character_dialogue_persona_memory: use dialogue evidence for tone and personality without copying source lines")
    if "event_to_sentence_realization_trace" in pattern_names:
        lines.append("- event_to_sentence_realization_trace: preserve plot event, realized sentence, confidence, and rejected alternative trace")
    if "entity_memory_slotfill_grounding" in pattern_names:
        lines.append("- entity_memory_slotfill_grounding: ground names, roles, locations, and objects against entity memory before accepting prose")


def _append_source_deconstruction_memory_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render book-memory, source-deconstruction, glossary, and edit-note gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "book_memory_bank_context_lattice",
        "spec_driven_fiction_scene_tasks",
        "toc_aware_source_deconstruction",
        "two_pass_context_glossary_pipeline",
        "inline_author_edit_markup_versioning",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Source deconstruction memory audit:")
    if "book_memory_bank_context_lattice" in pattern_names:
        lines.append("- book_memory_bank_context_lattice: separate source notes, story structure, world/characters, style guide, active context, and progress updates")
    if "spec_driven_fiction_scene_tasks" in pattern_names:
        lines.append("- spec_driven_fiction_scene_tasks: derive scene tasks from the story bible/constitution and check POV, glossary, subplot, pacing, and continuity gates")
    if "toc_aware_source_deconstruction" in pattern_names:
        lines.append("- toc_aware_source_deconstruction: keep source TOC hierarchy, summaries, quotes, anecdotes, and craft notes outside accepted new-story canon")
    if "two_pass_context_glossary_pipeline" in pattern_names:
        lines.append("- two_pass_context_glossary_pipeline: run analysis before generation, then use summary, previous-summary bridge, and cumulative glossary consistently")
    if "inline_author_edit_markup_versioning" in pattern_names:
        lines.append("- inline_author_edit_markup_versioning: keep author notes and edit notes visible until processed, reviewed, and versioned")


def _append_canon_graph_retrieval_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render temporal graph, memory, GraphRAG, and schema extraction gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "temporal_canon_context_graph",
        "long_term_author_preference_memory",
        "community_graph_source_deconstruction",
        "dual_level_graph_vector_retrieval",
        "schema_guided_graph_extraction",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Canon graph retrieval audit:")
    if "temporal_canon_context_graph" in pattern_names:
        lines.append("- temporal_canon_context_graph: store canon facts as dated/provenanced episodes and resolve validity windows before context use")
    if "long_term_author_preference_memory" in pattern_names:
        lines.append("- long_term_author_preference_memory: separate author preferences, project style decisions, session goals, and transient notes")
    if "community_graph_source_deconstruction" in pattern_names:
        lines.append("- community_graph_source_deconstruction: use source entity communities as analysis evidence, not transformed-story canon")
    if "dual_level_graph_vector_retrieval" in pattern_names:
        lines.append("- dual_level_graph_vector_retrieval: combine vector similarity with graph traversal and log local/global/hybrid mode per context item")
    if "schema_guided_graph_extraction" in pattern_names:
        lines.append("- schema_guided_graph_extraction: require bounded node labels, relationship types, properties, source metadata, and confidence for graph updates")


def _append_inspectable_rewrite_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render inspectable planning, rewrite, trace, and validation gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "human_synopsis_gate",
        "retrieval_guided_span_rewrite",
        "runtime_artifact_trace",
        "schema_validated_state_delta",
        "recursive_adaptive_planning",
        "workflow_manuscript_compilation",
        "writing_session_goal_tracking",
        "inspectable_run_workspace",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Inspectable rewrite audit:")
    if "human_synopsis_gate" in pattern_names:
        lines.append("- human_synopsis_gate: accept, edit, or regenerate synopsis and chapter summaries before prose expansion")
    if "retrieval_guided_span_rewrite" in pattern_names:
        lines.append("- retrieval_guided_span_rewrite: retrieve related body spans and outline nodes; rewrite only named spans and emit outline sync delta")
    if "runtime_artifact_trace" in pattern_names:
        lines.append("- runtime_artifact_trace: persist intent, selected context, rule stack, and trace for each chapter run")
    if "schema_validated_state_delta" in pattern_names:
        lines.append("- schema_validated_state_delta: validate structured state deltas before canon mutation; reject bad deltas instead of normalizing them")
    if "recursive_adaptive_planning" in pattern_names:
        lines.append("- recursive_adaptive_planning: split work into retrieval, reasoning, planning, composition, and review subtasks; replan on contradiction")
    if "workflow_manuscript_compilation" in pattern_names:
        lines.append("- workflow_manuscript_compilation: compile only accepted ordered scenes into manuscript outputs")
    if "writing_session_goal_tracking" in pattern_names:
        lines.append("- writing_session_goal_tracking: track target and accepted word counts without letting quota override continuity gates")
    if "inspectable_run_workspace" in pattern_names:
        lines.append("- inspectable_run_workspace: expose session, storyboard, manuscript surface, current phase, pending review, and memory refs")


def _append_production_review_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render production, continuity-bridge, voice, and review gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "craft_role_pipeline",
        "frontmatter_story_schema",
        "continuity_bridge_window",
        "episode_range_rewrite_scope",
        "voice_table_polish_axis",
        "boring_opening_quality_gates",
        "beat_strand_framework",
        "anti_hallucination_plan_check",
        "backup_restore_checkpoint",
        "multi_level_review_trend",
        "editor_notes_feedback_loop",
        "genre_parameterized_worldbuilding",
        "prose_preflight_voice_calibration",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Production review audit:")
    if "craft_role_pipeline" in pattern_names:
        lines.append("- craft_role_pipeline: keep architecture, character, prose, continuity, review, edit, and export outputs separate")
    if "frontmatter_story_schema" in pattern_names:
        lines.append("- frontmatter_story_schema: store scene state, continuity questions, promises/payoffs, and chapter draft metadata as stable fields")
    if "continuity_bridge_window" in pattern_names:
        lines.append("- continuity_bridge_window: feed the next chapter from recent accepted chapters, active timeline, open hooks, character state, and editor notes")
    if "episode_range_rewrite_scope" in pattern_names:
        lines.append("- episode_range_rewrite_scope: calculate impacted chapters and re-polish gates before applying range rewrites")
    if "voice_table_polish_axis" in pattern_names:
        lines.append("- voice_table_polish_axis: check dialogue against per-character diction, sentence endings, rhythm, and nonverbal palette")
    if "boring_opening_quality_gates" in pattern_names:
        lines.append("- boring_opening_quality_gates: reject exposition-only openings, flat scene purpose, missing pressure, and weak chapter-end hooks")
    if "beat_strand_framework" in pattern_names:
        lines.append("- beat_strand_framework: track external plot, internal change, and relationship strands with convergence beats")
    if "anti_hallucination_plan_check" in pattern_names:
        lines.append("- anti_hallucination_plan_check: verify new facts against bible, plan, retrieval evidence, and accepted chapter-change packages")
    if "backup_restore_checkpoint" in pattern_names:
        lines.append("- backup_restore_checkpoint: create restore points before bulk generation, range rewrites, or destructive canon merges")
    if "multi_level_review_trend" in pattern_names:
        lines.append("- multi_level_review_trend: review scene, chapter, batch, and cross-chapter trend risks before acceptance")
    if "editor_notes_feedback_loop" in pattern_names:
        lines.append("- editor_notes_feedback_loop: carry open editor notes forward and close them only with chapter evidence")
    if "genre_parameterized_worldbuilding" in pattern_names:
        lines.append("- genre_parameterized_worldbuilding: parameterize factions, locations, conflict sources, and taboo moves by genre/subgenre")
    if "prose_preflight_voice_calibration" in pattern_names:
        lines.append("- prose_preflight_voice_calibration: use voice samples to remove generic AI tells without inventing unsupported facts")


def _append_consistency_style_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render sourcebook, semantic-retrieval, consistency, and stylometry gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "sourcebook_author_workbench",
        "semantic_long_context_search",
        "contradiction_taxonomy_checker",
        "parallel_agent_chapter_pipeline",
        "cross_chapter_redundancy_audit",
        "humanization_stylometry_levers",
        "author_control_boundary",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Consistency and style audit:")
    if "sourcebook_author_workbench" in pattern_names:
        lines.append("- sourcebook_author_workbench: sourcebook entries are author-owned canon candidates; AI suggestions need acceptance before reuse")
    if "semantic_long_context_search" in pattern_names:
        lines.append("- semantic_long_context_search: cite query, matched artifact, inclusion reason, and canon status for each long-context hit")
    if "contradiction_taxonomy_checker" in pattern_names:
        lines.append("- contradiction_taxonomy_checker: check characterization, factual detail, narrative style, timeline/plot, and world-rule conflicts")
    if "parallel_agent_chapter_pipeline" in pattern_names:
        lines.append("- parallel_agent_chapter_pipeline: isolate chapter jobs and aggregate reviews before revision cycles")
    if "cross_chapter_redundancy_audit" in pattern_names:
        lines.append("- cross_chapter_redundancy_audit: count repeated scene shapes, weak causality, flat dialogue, and over-regular prose across chapters")
    if "humanization_stylometry_levers" in pattern_names:
        lines.append("- humanization_stylometry_levers: apply burstiness, specificity, discourse variation, and AI-transition cleanup only after canon checks")
    if "author_control_boundary" in pattern_names:
        lines.append("- author_control_boundary: keep AI proposals, accepted canon, and disclosure/labeling decisions separate")


def _append_research_multimodal_experiment_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render research taxonomy, adaptation, agent-planner, and experiment gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "research_taxonomy_story_map",
        "novel_to_multimodal_pipeline",
        "entity_to_visual_asset_pipeline",
        "agentic_book_planner_pipeline",
        "rag_synopsis_spine",
        "anti_repetition_prompt_rules",
        "prompt_recipe_experiment_grid",
        "append_only_generation_review_log",
        "narrative_arc_template_control",
        "nrd_task_tree_pipeline",
        "sampling_parameter_quality_sweep",
        "story_structure_rag_planning",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Research, multimodal, and experiment audit:")
    if "research_taxonomy_story_map" in pattern_names:
        lines.append("- research_taxonomy_story_map: use method categories as coverage checks; keep indexes out of runtime prompts")
    if "novel_to_multimodal_pipeline" in pattern_names:
        lines.append("- novel_to_multimodal_pipeline: treat scripts, storyboards, and videos as derived artifacts unless accepted into canon")
    if "entity_to_visual_asset_pipeline" in pattern_names:
        lines.append("- entity_to_visual_asset_pipeline: tie visual assets to entity/card versions so stale images do not overwrite prose state")
    if "agentic_book_planner_pipeline" in pattern_names:
        lines.append("- agentic_book_planner_pipeline: separate Story Bible, Characters, Plot Threads, Chapter Outlines, Writer, Editor, and Continuity Checker artifacts")
    if "rag_synopsis_spine" in pattern_names:
        lines.append("- rag_synopsis_spine: retrieve from the full synopsis spine with query, matched chapter, inclusion reason, and canon status")
    if "anti_repetition_prompt_rules" in pattern_names:
        lines.append("- anti_repetition_prompt_rules: reject repeated phrases, repeated scene shapes, repeated causal bridges, and repeated emotional beats")
    if "prompt_recipe_experiment_grid" in pattern_names:
        lines.append("- prompt_recipe_experiment_grid: compare prompt recipes under fixed inputs, rubric review, and keep/discard decisions")
    if "append_only_generation_review_log" in pattern_names:
        lines.append("- append_only_generation_review_log: append experiment evidence instead of rewriting previous review rows")
    if "narrative_arc_template_control" in pattern_names:
        lines.append("- narrative_arc_template_control: declare genre, story style, author style, arc, and scenario blueprint before drafting")
    if "nrd_task_tree_pipeline" in pattern_names:
        lines.append("- nrd_task_tree_pipeline: track arcs -> chapters -> scenes -> revision passes with continuity reports")
    if "sampling_parameter_quality_sweep" in pattern_names:
        lines.append("- sampling_parameter_quality_sweep: promote parameter defaults only when quality, continuity, voice, and copy-risk all improve")
    if "story_structure_rag_planning" in pattern_names:
        lines.append("- story_structure_rag_planning: map Hero's Journey/Freytag or style-RAG samples to accepted story facts before prose")



def _append_serialized_continuity_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render serialized webnovel contract, snapshot, projection, and review gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "story_contract_commit_chain",
        "fact_snapshot_delta_gate",
        "projection_sync_observability",
        "foreshadowing_debt_budget",
        "reader_retention_review_gate",
        "draft_stage_revision_ladder",
        "rolling_summary_context_trim",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Serialized continuity audit:")
    if "story_contract_commit_chain" in pattern_names:
        lines.append("- story_contract_commit_chain: contracts are canon; drafts become reusable state only through accepted chapter commits")
    if "fact_snapshot_delta_gate" in pattern_names:
        lines.append("- fact_snapshot_delta_gate: validate fact snapshots, change declarations, and after-state before writing canon")
    if "projection_sync_observability" in pattern_names:
        lines.append("- projection_sync_observability: state/index/summary/memory/vector/dashboard views must trace to accepted commits")
    if "foreshadowing_debt_budget" in pattern_names:
        lines.append("- foreshadowing_debt_budget: reserve context for high-debt hooks and cite setup/payoff windows before reveal")
    if "reader_retention_review_gate" in pattern_names:
        lines.append("- reader_retention_review_gate: review consistency, OOC, rhythm, pleasure point, and next-chapter pull together")
    if "draft_stage_revision_ladder" in pattern_names:
        lines.append("- draft_stage_revision_ladder: blueprint -> key info -> task card -> Draft A/B/C -> continuity handoff")
    if "rolling_summary_context_trim" in pattern_names:
        lines.append("- rolling_summary_context_trim: selected rolling summary, character state, timeline events, and dropped context need a manifest")


def _append_story_quality_evaluation_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render story-quality benchmark, rubric, style-axis, and simulation gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "pairwise_story_comparison_ranking",
        "multidimensional_quality_rubric",
        "story_theory_beat_evaluation",
        "constraint_specificity_creativity_benchmark",
        "style_axis_diversity_fingerprint",
        "event_outline_history_compression",
        "agentic_story_world_simulation",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Story quality evaluation audit:")
    if "pairwise_story_comparison_ranking" in pattern_names:
        lines.append("- pairwise_story_comparison_ranking: compare matched chapter variants against the same brief before accepting")
    if "multidimensional_quality_rubric" in pattern_names:
        lines.append("- multidimensional_quality_rubric: score grammar, clarity, causality, scene purpose, consistency, character motive, dialogue, reader pull, and resolution")
    if "story_theory_beat_evaluation" in pattern_names:
        lines.append("- story_theory_beat_evaluation: test beat execution, preservation, bridge quality, and constrained-continuation criteria")
    if "constraint_specificity_creativity_benchmark" in pattern_names:
        lines.append("- constraint_specificity_creativity_benchmark: track required constraints, satisfaction evidence, creativity, and coherence tradeoffs")
    if "style_axis_diversity_fingerprint" in pattern_names:
        lines.append("- style_axis_diversity_fingerprint: inspect voice, rhythm, POV, pacing, tone, imagery, dialogue, experimentation, and closure axes")
    if "event_outline_history_compression" in pattern_names:
        lines.append("- event_outline_history_compression: align compressed history with the current event outline and chapter plan")
    if "agentic_story_world_simulation" in pattern_names:
        lines.append("- agentic_story_world_simulation: keep simulated character choices and social interactions as proposals until canon acceptance")


def _append_reader_market_feedback_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render reader-signal, beta-reader, market-position, and engagement gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "reader_rating_signal_model",
        "review_spoiler_sentiment_corpus",
        "beta_reader_archetype_panel",
        "comp_title_market_positioning",
        "local_reader_experience_editor",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Reader market feedback audit:")
    if "reader_rating_signal_model" in pattern_names:
        lines.append("- reader_rating_signal_model: use ratings, shelves, tags, and to-read signals as aggregate expectation metadata only")
    if "review_spoiler_sentiment_corpus" in pattern_names:
        lines.append("- review_spoiler_sentiment_corpus: cluster praise, complaints, trope requests, and spoiler-sensitive issues without verbatim review text")
    if "beta_reader_archetype_panel" in pattern_names:
        lines.append("- beta_reader_archetype_panel: collect genre-fan, casual-reader, critical-reader, and sensitivity-reader hook/confusion/turn-page notes")
    if "comp_title_market_positioning" in pattern_names:
        lines.append("- comp_title_market_positioning: calibrate promise, tone, audience, and market gap without copying comp premise or blurb beats")
    if "local_reader_experience_editor" in pattern_names:
        lines.append("- local_reader_experience_editor: audit micro-tension, curiosity thread, hook, cliffhanger, opening/ending, rhythm, and context fit")


def _append_inspired_transformation_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render same-type creation gates that keep source inspiration out of canon."""
    if not isinstance(source_pattern_pack, dict):
        return

    mapping_targets = _as_note_list(source_pattern_pack.get("inspired_mapping_targets"))
    prompt_hints = _as_note_list(source_pattern_pack.get("inspired_prompt_hints"))
    transformation_hints = _as_note_list(source_pattern_pack.get("inspired_transformation_hints"))
    copy_risk_hints = _as_note_list(source_pattern_pack.get("inspired_copy_risk_hints"))
    if not any((mapping_targets, prompt_hints, transformation_hints, copy_risk_hints)):
        return

    lines.append("")
    lines.append("Inspired transformation audit:")
    if mapping_targets:
        lines.append(f"- required_remaps: {', '.join(mapping_targets[:8])}")
    if transformation_hints:
        lines.append(f"- transformation_rule: {_truncate(transformation_hints[0], 220)}")
    lines.append("- source_canon_boundary: source facts, names, organizations, events, and set pieces remain non-canon.")
    lines.append("- context_reference_policy: source-pattern references can justify craft choices, not story facts.")
    if prompt_hints:
        lines.append(f"- style_transfer_scope: {_truncate(prompt_hints[0], 220)}")
    if copy_risk_hints:
        lines.append(f"- copy_risk_gate: {_truncate(copy_risk_hints[0], 220)}")


def _source_pattern_names(source_pattern_pack: Optional[dict[str, Any]]) -> set[str]:
    if not isinstance(source_pattern_pack, dict):
        return set()

    names: set[str] = set()
    for pattern in _as_dict_list(source_pattern_pack.get("workflow_patterns")):
        name = _string_value(pattern.get("name"))
        if name:
            names.add(name)

    hint_to_name = {
        "lorebook_context_hints": "lorebook_context",
        "context_reference_hints": "context_reference",
        "world_state_tracking_hints": "world_state_tracking",
        "memory_snapshot_versioning_hints": "memory_snapshot_versioning",
        "author_note_layer_hints": "author_note_layer",
        "local_first_workspace_hints": "local_first_novel_workspace",
        "prompt_library_hints": "prompt_library",
        "style_guide_layering_hints": "style_guide_layering",
        "review_queue_staging_hints": "review_queue_staging",
        "entity_schema_custom_fields_hints": "entity_schema_custom_fields",
        "scene_level_generation_hints": "scene_level_generation",
        "content_ref_externalization_hints": "content_ref_externalization",
        "graph_healing_hints": "graph_healing",
        "contradiction_detection_hints": "contradiction_detection",
        "graph_branching_atomicity_hints": "graph_branching_atomicity",
        "query_lint_contract_hints": "query_lint_contract",
        "premature_ending_guard_hints": "premature_ending_guard",
        "layered_memory_model_hints": "layered_memory_model",
        "plot_dependency_graph_hints": "plot_dependency_graph",
        "plotgrid_scene_matrix_hints": "plotgrid_scene_matrix",
        "plotline_thread_tracking_hints": "plotline_thread_tracking",
        "scene_status_dashboard_hints": "scene_status_dashboard",
        "gradual_reveal_control_hints": "gradual_reveal_control",
        "setup_payoff_tracking_hints": "setup_payoff_tracking",
        "scene_type_directing_hints": "scene_type_directing",
        "worldpkg_export_hints": "worldpkg_export",
        "alternate_timeline_branching_hints": "alternate_timeline_branching",
        "divergence_guidance_hints": "divergence_guidance",
        "context_pack_preview_hints": "context_pack_preview",
        "accepted_chapter_memory_hints": "accepted_chapter_memory",
        "critic_verifier_loop_hints": "critic_verifier_loop",
        "collapse_prevention_hints": "collapse_prevention",
        "trend_deconstruction_pipeline_hints": "trend_deconstruction_pipeline",
        "anti_ai_tone_polish_hints": "anti_ai_tone_polish",
        "preference_memory_hints": "preference_memory",
        "interrupted_resume_flow_hints": "interrupted_resume_flow",
        "auto_validation_rewrite_hints": "auto_validation_rewrite",
        "top_down_story_planning_hints": "top_down_story_planning",
        "plain_text_project_storage_hints": "plain_text_project_storage",
        "synopsis_cross_reference_hints": "synopsis_cross_reference",
        "snowflake_premise_expansion_hints": "snowflake_premise_expansion",
        "outliner_index_cards_hints": "outliner_index_cards",
        "narrative_strand_mapping_hints": "narrative_strand_mapping",
        "character_depth_interview_hints": "character_depth_interview",
        "mindmap_visual_planning_hints": "mindmap_visual_planning",
        "manuscript_export_formats_hints": "manuscript_export_formats",
        "human_synopsis_gate_hints": "human_synopsis_gate",
        "retrieval_guided_span_rewrite_hints": "retrieval_guided_span_rewrite",
        "runtime_artifact_trace_hints": "runtime_artifact_trace",
        "schema_validated_state_delta_hints": "schema_validated_state_delta",
        "recursive_adaptive_planning_hints": "recursive_adaptive_planning",
        "workflow_manuscript_compilation_hints": "workflow_manuscript_compilation",
        "writing_session_goal_tracking_hints": "writing_session_goal_tracking",
        "inspectable_run_workspace_hints": "inspectable_run_workspace",
        "craft_role_pipeline_hints": "craft_role_pipeline",
        "frontmatter_story_schema_hints": "frontmatter_story_schema",
        "continuity_bridge_window_hints": "continuity_bridge_window",
        "episode_range_rewrite_scope_hints": "episode_range_rewrite_scope",
        "voice_table_polish_axis_hints": "voice_table_polish_axis",
        "boring_opening_quality_gates_hints": "boring_opening_quality_gates",
        "beat_strand_framework_hints": "beat_strand_framework",
        "anti_hallucination_plan_check_hints": "anti_hallucination_plan_check",
        "backup_restore_checkpoint_hints": "backup_restore_checkpoint",
        "multi_level_review_trend_hints": "multi_level_review_trend",
        "editor_notes_feedback_loop_hints": "editor_notes_feedback_loop",
        "genre_parameterized_worldbuilding_hints": "genre_parameterized_worldbuilding",
        "prose_preflight_voice_calibration_hints": "prose_preflight_voice_calibration",
        "sourcebook_author_workbench_hints": "sourcebook_author_workbench",
        "semantic_long_context_search_hints": "semantic_long_context_search",
        "contradiction_taxonomy_checker_hints": "contradiction_taxonomy_checker",
        "parallel_agent_chapter_pipeline_hints": "parallel_agent_chapter_pipeline",
        "cross_chapter_redundancy_audit_hints": "cross_chapter_redundancy_audit",
        "humanization_stylometry_levers_hints": "humanization_stylometry_levers",
        "author_control_boundary_hints": "author_control_boundary",
        "research_taxonomy_story_map_hints": "research_taxonomy_story_map",
        "novel_to_multimodal_pipeline_hints": "novel_to_multimodal_pipeline",
        "entity_to_visual_asset_pipeline_hints": "entity_to_visual_asset_pipeline",
        "agentic_book_planner_pipeline_hints": "agentic_book_planner_pipeline",
        "rag_synopsis_spine_hints": "rag_synopsis_spine",
        "anti_repetition_prompt_rules_hints": "anti_repetition_prompt_rules",
        "prompt_recipe_experiment_grid_hints": "prompt_recipe_experiment_grid",
        "append_only_generation_review_log_hints": "append_only_generation_review_log",
        "narrative_arc_template_control_hints": "narrative_arc_template_control",
        "nrd_task_tree_pipeline_hints": "nrd_task_tree_pipeline",
        "sampling_parameter_quality_sweep_hints": "sampling_parameter_quality_sweep",
        "story_structure_rag_planning_hints": "story_structure_rag_planning",
        "story_contract_commit_chain_hints": "story_contract_commit_chain",
        "fact_snapshot_delta_gate_hints": "fact_snapshot_delta_gate",
        "projection_sync_observability_hints": "projection_sync_observability",
        "foreshadowing_debt_budget_hints": "foreshadowing_debt_budget",
        "reader_retention_review_gate_hints": "reader_retention_review_gate",
        "draft_stage_revision_ladder_hints": "draft_stage_revision_ladder",
        "rolling_summary_context_trim_hints": "rolling_summary_context_trim",
        "pairwise_story_comparison_ranking_hints": "pairwise_story_comparison_ranking",
        "multidimensional_quality_rubric_hints": "multidimensional_quality_rubric",
        "story_theory_beat_evaluation_hints": "story_theory_beat_evaluation",
        "constraint_specificity_creativity_benchmark_hints": "constraint_specificity_creativity_benchmark",
        "style_axis_diversity_fingerprint_hints": "style_axis_diversity_fingerprint",
        "event_outline_history_compression_hints": "event_outline_history_compression",
        "agentic_story_world_simulation_hints": "agentic_story_world_simulation",
        "reader_rating_signal_model_hints": "reader_rating_signal_model",
        "review_spoiler_sentiment_corpus_hints": "review_spoiler_sentiment_corpus",
        "beta_reader_archetype_panel_hints": "beta_reader_archetype_panel",
        "comp_title_market_positioning_hints": "comp_title_market_positioning",
        "local_reader_experience_editor_hints": "local_reader_experience_editor",
        "delivery_manuscript_assembly_hints": "delivery_manuscript_assembly",
        "export_format_fidelity_audit_hints": "export_format_fidelity_audit",
        "preview_toc_packaging_hints": "preview_toc_packaging",
        "cover_kdp_metadata_boundary_hints": "cover_kdp_metadata_boundary",
        "branching_choice_graph_hints": "branching_choice_graph",
        "node_dialogue_state_machine_hints": "node_dialogue_state_machine",
        "passage_link_navigation_map_hints": "passage_link_navigation_map",
        "choice_stats_consequence_gate_hints": "choice_stats_consequence_gate",
        "source_text_fingerprint_gate_hints": "source_text_fingerprint_gate",
        "fuzzy_phrase_similarity_gate_hints": "fuzzy_phrase_similarity_gate",
        "diff_span_copy_review_hints": "diff_span_copy_review",
        "minhash_lsh_near_duplicate_gate_hints": "minhash_lsh_near_duplicate_gate",
        "simhash_hamming_similarity_gate_hints": "simhash_hamming_similarity_gate",
        "semantic_duplicate_cluster_gate_hints": "semantic_duplicate_cluster_gate",
        "embedding_similarity_independence_gate_hints": "embedding_similarity_independence_gate",
        "corpus_leakage_dedup_review_gate_hints": "corpus_leakage_dedup_review_gate",
        "character_quote_attribution_map_hints": "character_quote_attribution_map",
        "readability_pacing_metric_gate_hints": "readability_pacing_metric_gate",
        "prose_lint_style_rule_gate_hints": "prose_lint_style_rule_gate",
        "grammar_spelling_copyedit_gate_hints": "grammar_spelling_copyedit_gate",
        "copyedit_diagnostic_triage_queue_hints": "copyedit_diagnostic_triage_queue",
        "lexical_diversity_voice_audit_hints": "lexical_diversity_voice_audit",
        "keyphrase_motif_extraction_hints": "keyphrase_motif_extraction",
        "chinese_segmentation_keyword_gate_hints": "chinese_segmentation_keyword_gate",
        "chinese_ner_alias_consistency_gate_hints": "chinese_ner_alias_consistency_gate",
        "chinese_text_normalization_gate_hints": "chinese_text_normalization_gate",
        "chinese_error_correction_review_gate_hints": "chinese_error_correction_review_gate",
        "source_format_import_manifest_hints": "source_format_import_manifest",
        "pdf_layout_text_extraction_gate_hints": "pdf_layout_text_extraction_gate",
        "ocr_scanned_page_import_gate_hints": "ocr_scanned_page_import_gate",
        "document_partition_chapter_detection_gate_hints": "document_partition_chapter_detection_gate",
        "import_provenance_checksum_gate_hints": "import_provenance_checksum_gate",
        "literary_event_entity_annotation_gate_hints": "literary_event_entity_annotation_gate",
        "narrative_event_evolution_graph_gate_hints": "narrative_event_evolution_graph_gate",
        "sentiment_arc_emotion_trajectory_gate_hints": "sentiment_arc_emotion_trajectory_gate",
        "cross_context_coreference_gate_hints": "cross_context_coreference_gate",
        "character_interaction_network_gate_hints": "character_interaction_network_gate",
        "semantic_chunk_boundary_map_hints": "semantic_chunk_boundary_map",
        "chapter_summary_anchor_gate_hints": "chapter_summary_anchor_gate",
        "topic_drift_map_hints": "topic_drift_map",
        "context_faithfulness_eval_gate_hints": "context_faithfulness_eval_gate",
        "retrieval_trace_observability_gate_hints": "retrieval_trace_observability_gate",
        "prompt_regression_eval_suite_hints": "prompt_regression_eval_suite",
    }
    for hint_key, pattern_name in hint_to_name.items():
        if _as_note_list(source_pattern_pack.get(hint_key)):
            names.add(pattern_name)

    return names


def _activated_context_sections(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []

    world_rules = bible.get("world_rules")
    if isinstance(world_rules, dict) and world_rules:
        sections.append(("world_rules", f"{len(world_rules)} rules"))

    for label, value, unit in (
        ("hard_constraints", bible.get("hard_constraints"), "constraints"),
        ("character_cards", bible.get("character_cards"), "cards"),
        ("organizations", bible.get("organizations"), "entries"),
        ("conflicts", bible.get("conflicts"), "arcs"),
        ("story_arcs", bible.get("story_arcs"), "arcs"),
    ):
        count = len(_as_dict_list(value))
        if count:
            sections.append((label, f"{count} {unit}"))

    timeline = _as_dict_list(bible.get("timeline"))
    latest_machine = _latest_chapter_analysis_items(timeline, max_items=1)
    if latest_machine:
        chapter = latest_machine[0].get("chapter_number") or latest_machine[0].get("last_chapter_number")
        suffix = f" through chapter {chapter}" if chapter not in (None, "") else " present"
        sections.append(("latest_machine_timeline", suffix.strip()))
    elif timeline:
        sections.append(("timeline", f"{len(timeline)} anchors"))

    chapter_change_packages = _chapter_analysis_packages(bible.get("chapter_change_packages"))
    if chapter_change_packages:
        chapter_numbers = [
            _int_or_none(package.get("chapter_number"))
            for package in _sort_by_chapter_asc(chapter_change_packages)
        ]
        chapter_numbers = [number for number in chapter_numbers if number is not None]
        if chapter_numbers:
            first_chapter = chapter_numbers[0]
            last_chapter = chapter_numbers[-1]
            chapter_range = str(first_chapter) if first_chapter == last_chapter else f"{first_chapter}-{last_chapter}"
            sections.append(("recent_change_packages", f"{len(chapter_change_packages)} packages covering chapter {chapter_range}"))
        else:
            sections.append(("recent_change_packages", f"{len(chapter_change_packages)} packages"))

    open_hooks = _status_items(_as_dict_list(bible.get("foreshadows")), done=False, max_items=99)
    if open_hooks:
        sections.append(("open_hooks", f"{len(open_hooks)} unresolved hooks"))

    if plan:
        pending_beats = _status_items(_as_dict_list(plan.get("beats")), done=False, max_items=99)
        pending_hooks = _status_items(_as_dict_list(plan.get("priority_hooks")), done=False, max_items=99)
        guardrails = _as_dict_list(plan.get("guardrails"))
        if pending_beats:
            sections.append(("pending_plan_beats", f"{len(pending_beats)} beats"))
        if pending_hooks:
            sections.append(("pending_priority_hooks", f"{len(pending_hooks)} hooks"))
        if guardrails:
            sections.append(("plan_guardrails", f"{len(guardrails)} guardrails"))

    style_signature = bible.get("style_signature")
    if isinstance(style_signature, dict) and style_signature:
        sections.append(("style_signature", f"{len(style_signature)} fields"))

    return sections


def _append_inspired_style_section(
    *,
    lines: list[str],
    title: str,
    style_content: str,
    heading: str,
    max_items: int,
) -> None:
    section = _extract_heading_section(style_content, heading=heading)
    if not section:
        return

    items: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        items.append(_truncate(line, 260))
        if len(items) >= max_items:
            break

    if not items:
        return

    lines.append("")
    lines.append(f"{title}:")
    for item in items:
        lines.append(f"- {item}")


def _extract_heading_section(style_content: str, *, heading: str) -> str:
    if heading not in style_content:
        return ""
    _, section = style_content.split(heading, 1)
    next_heading = section.find("【")
    if next_heading >= 0:
        section = section[:next_heading]
    return section.strip()


def _chapter_package_label(package: dict[str, Any]) -> str:
    chapter_number = package.get("chapter_number")
    title = _string_value(package.get("chapter_title"))
    if chapter_number not in (None, "") and title:
        return f"Chapter {chapter_number}: {title}"
    if chapter_number not in (None, ""):
        return f"Chapter {chapter_number}"
    return title or "Recent chapter"


def _append_dict_section(
    *,
    lines: list[str],
    title: str,
    items: Any,
    preferred_keys: tuple[str, ...],
    max_items: int,
) -> None:
    normalized_items = _as_dict_list(items)
    if not normalized_items:
        return

    lines.append("")
    lines.append(f"{title}:")
    for item in normalized_items[:max_items]:
        lines.append(f"- {_item_to_text(item, preferred_keys=preferred_keys)}")


def _append_character_update_section(
    *,
    lines: list[str],
    cards: list[dict[str, Any]],
    max_items: int,
) -> None:
    updates: list[dict[str, Any]] = []
    for card in cards:
        name = _string_value(card.get("name") or card.get("character_name"))
        for update in _as_dict_list(card.get("continuation_updates")):
            merged = {**update, "character_name": name}
            updates.append(merged)

    updates = _sort_by_chapter_desc(updates)[:max_items]
    if not updates:
        return

    lines.append("")
    lines.append("Latest character continuation updates:")
    for update in updates:
        label = _string_value(update.get("character_name")) or "Unknown character"
        chapter_number = update.get("chapter_number")
        if chapter_number not in (None, ""):
            label = f"{label} @ Chapter {chapter_number}"
        parts = [label]
        for key in ("state_after", "key_event", "psychological_change", "chapter_title"):
            value = _string_value(update.get(key))
            if value:
                parts.append(f"{key}: {value}")
        lines.append(f"- {_truncate(' | '.join(parts), 260)}")


def _append_style_signature_section(
    *,
    lines: list[str],
    style_signature: Any,
) -> None:
    if not isinstance(style_signature, dict) or not style_signature:
        return

    lines.append("")
    lines.append("Style signature to preserve:")
    for key, value in list(style_signature.items())[:12]:
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
        else:
            rendered = str(value)
        if rendered.strip():
            lines.append(f"- {key}: {_truncate(rendered, 220)}")


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _as_note_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    notes: list[str] = []
    for item in value:
        text = _string_value(item)
        if text:
            notes.append(text)
    return notes


def _item_to_text(item: dict[str, Any], *, preferred_keys: tuple[str, ...]) -> str:
    label = _first_text(item, preferred_keys)
    status = _string_value(item.get("status"))
    chapter = item.get("chapter_number") or item.get("last_chapter_number")
    suffix_parts = []
    if status:
        suffix_parts.append(f"status: {status}")
    if chapter not in (None, ""):
        suffix_parts.append(f"chapter: {chapter}")
    if suffix_parts:
        label = f"{label} ({', '.join(suffix_parts)})"
    return _truncate(label, 260)


def _first_text(item: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = _string_value(item.get(key))
        if value:
            return value
    compact = json.dumps(item, ensure_ascii=False, sort_keys=True)
    return compact[:240]


def _manual_items(items: list[dict[str, Any]], *, max_items: int) -> list[dict[str, Any]]:
    manual = [item for item in items if not _is_machine_continuation_source(item.get("source"))]
    return _sort_by_chapter_desc(manual)[:max_items]


def _latest_chapter_analysis_items(items: list[dict[str, Any]], *, max_items: int) -> list[dict[str, Any]]:
    machine = [item for item in items if _is_machine_continuation_source(item.get("source"))]
    return _sort_by_chapter_desc(machine)[:max_items]


def _is_machine_continuation_source(value: Any) -> bool:
    return _string_value(value) in {"chapter_analysis", "chapter_generation"}


def _status_items(items: list[dict[str, Any]], *, done: bool, max_items: int) -> list[dict[str, Any]]:
    filtered = [item for item in items if _is_done_status(item.get("status")) is done]
    return _sort_by_chapter_desc(filtered)[:max_items]


def _is_done_status(value: Any) -> bool:
    normalized = _string_value(value).strip().lower()
    return normalized in {"done", "resolved", "paid", "closed", "complete", "completed", "已完成", "已回收", "回收"}


def _sort_by_chapter_desc(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=_chapter_sort_key, reverse=True)


def _sort_by_chapter_asc(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=_chapter_sort_key)


def _chapter_sort_key(item: dict[str, Any]) -> tuple[int, int]:
    chapter = item.get("chapter_number") or item.get("last_chapter_number") or 0
    try:
        chapter_number = int(chapter)
    except (TypeError, ValueError):
        chapter_number = 0
    source_rank = 1 if _string_value(item.get("source")) == "chapter_analysis" else 0
    return chapter_number, source_rank


def _int_or_none(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _truncate(value: str, limit: int) -> str:
    text = _string_value(value)
    return text if len(text) <= limit else text[:limit].rstrip() + "..."


book_remix_context_service = BookRemixContextService()
