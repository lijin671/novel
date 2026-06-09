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

    return "\n".join(lines).strip()


def _is_inspired_style_content(style_content: str) -> bool:
    return bool(
        ("同类型创作" in style_content or "同类型创作总原则" in style_content)
        and (
            "【源书语气样本】" in style_content
            or "【源书显性元素禁用清单】" in style_content
        )
    )


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
