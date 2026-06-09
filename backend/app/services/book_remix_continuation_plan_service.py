"""Draft continuation plan generation service for remix projects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.ai_service import AIService
from app.services.source_discovery_service import source_discovery_service
from app.services.source_pattern_pack_prompt import render_source_pattern_pack_digest


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class BookRemixContinuationPlanService:
    """Generate a normalized continuation plan payload from a confirmed bible."""

    def __init__(self, ai_service: AIService) -> None:
        self.ai_service = ai_service

    async def build_plan_payload(
        self,
        *,
        project_title: str,
        bible: dict[str, Any],
        user_direction: str = "",
        source_pattern_pack: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        generation_status = str((bible or {}).get("generation_status") or "").strip().lower()
        if generation_status != "confirmed":
            raise ValueError("confirmed bible is required before continuation plan generation")

        resolved_source_pattern_pack = source_pattern_pack
        if resolved_source_pattern_pack is None:
            resolved_source_pattern_pack = await source_discovery_service.resolve_fresh_pattern_pack(
                repo_root=PROJECT_ROOT,
                force=False,
            )

        prompt = self._build_prompt(
            project_title=project_title,
            bible=bible,
            user_direction=user_direction,
            source_pattern_pack=resolved_source_pattern_pack,
        )
        raw_payload = await self.ai_service.call_with_json_retry(
            prompt=prompt,
            max_retries=3,
            expected_type="object",
            auto_mcp=False,
        )
        payload = raw_payload if isinstance(raw_payload, dict) else {}
        normalized_payload = self._normalize_payload(payload)
        return self.backfill_missing_sections(
            bible=bible,
            payload=normalized_payload,
        )

    def _build_prompt(
        self,
        *,
        project_title: str,
        bible: dict[str, Any],
        user_direction: str,
        source_pattern_pack: dict[str, Any] | None = None,
    ) -> str:
        template = json.dumps(self._empty_payload(), ensure_ascii=False, indent=2)
        character_cards = json.dumps(self._as_dict_list(bible.get("character_cards")), ensure_ascii=False, indent=2)
        organizations = json.dumps(self._as_dict_list(bible.get("organizations")), ensure_ascii=False, indent=2)
        timeline = json.dumps(self._as_dict_list(bible.get("timeline")), ensure_ascii=False, indent=2)
        story_arcs = json.dumps(self._as_dict_list(bible.get("story_arcs")), ensure_ascii=False, indent=2)
        foreshadows = json.dumps(self._as_dict_list(bible.get("foreshadows")), ensure_ascii=False, indent=2)
        hard_constraints = json.dumps(self._as_dict_list(bible.get("hard_constraints")), ensure_ascii=False, indent=2)
        world_rules = json.dumps(self._as_dict(bible.get("world_rules")), ensure_ascii=False, indent=2)
        style_signature = json.dumps(self._as_dict(bible.get("style_signature")), ensure_ascii=False, indent=2)
        conflicts = json.dumps(self._as_dict_list(bible.get("conflicts")), ensure_ascii=False, indent=2)
        generation_notes = json.dumps(self._as_note_list(bible.get("generation_notes")), ensure_ascii=False, indent=2)
        chapter_change_packages = json.dumps(
            self._as_dict_list(bible.get("chapter_change_packages"))[:8],
            ensure_ascii=False,
            indent=2,
        )
        source_pattern_digest = render_source_pattern_pack_digest(source_pattern_pack)
        direction = user_direction.strip() or "(none)"

        return (
            "You are preparing a continuation plan for a fiction remix project.\n"
            "Return strict JSON only.\n"
            "Use exactly these top-level keys and preserve each key type:\n"
            f"{template}\n\n"
            "Planning requirements:\n"
            "- summary: concise continuation strategy (1-3 sentences).\n"
            "- stage_goals: milestone goals for the next continuation stages.\n"
            "- beats: concrete story beats with sequence hints.\n"
            "- priority_hooks: unresolved hooks that must be paid off soon.\n"
            "- guardrails: strict continuity rules to avoid canon breaks.\n"
            f"- Project title: {project_title}\n"
            f"- User direction: {direction}\n\n"
            "Public source pattern pack (pattern-only; absorb workflow guidance, do not import external code):\n"
            f"{source_pattern_digest}\n\n"
            "Confirmed bible digest:\n"
            f"- world_rules: {world_rules}\n"
            f"- character_cards: {character_cards}\n"
            f"- organizations: {organizations}\n"
            f"- timeline: {timeline}\n"
            f"- story_arcs: {story_arcs}\n"
            f"- foreshadows: {foreshadows}\n"
            f"- style_signature: {style_signature}\n"
            f"- hard_constraints: {hard_constraints}\n"
            f"- conflicts: {conflicts}\n"
            f"- generation_notes: {generation_notes}\n"
            f"- recent_chapter_change_packages: {chapter_change_packages}\n"
        )

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        summary = payload.get("summary")
        if isinstance(summary, str):
            normalized_summary = summary.strip()
        elif summary is None:
            normalized_summary = ""
        else:
            normalized_summary = str(summary).strip()

        return {
            "summary": normalized_summary,
            "stage_goals": self._normalize_item_list(payload.get("stage_goals"), primary_key="goal"),
            "beats": self._normalize_item_list(payload.get("beats"), primary_key="beat"),
            "priority_hooks": self._normalize_item_list(payload.get("priority_hooks"), primary_key="hook"),
            "guardrails": self._normalize_item_list(payload.get("guardrails"), primary_key="rule"),
        }

    @classmethod
    def backfill_missing_sections(
        cls,
        *,
        bible: dict[str, Any],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        helper = cls.__new__(cls)
        normalized = {
            "summary": str(payload.get("summary") or "").strip(),
            "stage_goals": helper._as_dict_list(payload.get("stage_goals")),
            "beats": helper._as_dict_list(payload.get("beats")),
            "priority_hooks": helper._as_dict_list(payload.get("priority_hooks")),
            "guardrails": helper._as_dict_list(payload.get("guardrails")),
        }

        if not normalized["stage_goals"]:
            normalized["stage_goals"] = helper._build_fallback_stage_goals(bible=bible)
        if not normalized["beats"]:
            normalized["beats"] = helper._build_fallback_beats(bible=bible)
        if not normalized["priority_hooks"]:
            normalized["priority_hooks"] = helper._build_fallback_priority_hooks(bible=bible)
        if not normalized["guardrails"]:
            normalized["guardrails"] = helper._build_fallback_guardrails(bible=bible)

        return normalized

    def _normalize_item_list(
        self,
        value: Any,
        *,
        primary_key: str,
    ) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []

        normalized_items: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                normalized_items.append(item)
                continue

            if isinstance(item, str):
                text = item.strip()
                if text:
                    normalized_items.append({primary_key: text})

        return normalized_items

    def _as_dict_list(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    def _as_dict(self, value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _as_note_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        notes: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                notes.append(text)
        return notes

    def _build_fallback_stage_goals(self, *, bible: dict[str, Any]) -> list[dict[str, Any]]:
        goals: list[dict[str, Any]] = []
        timeline = self._as_dict_list(bible.get("timeline"))
        story_arcs = self._as_dict_list(bible.get("story_arcs"))
        foreshadows = self._as_dict_list(bible.get("foreshadows"))
        character_cards = self._as_dict_list(bible.get("character_cards"))

        if timeline:
            anchor = self._item_to_text(timeline[-1], preferred_keys=("event", "milestone", "summary", "impact"))
            if anchor:
                goals.append({"goal": f"Directly continue the fallout of: {anchor}"})

        for arc in story_arcs[:2]:
            arc_name = self._item_to_text(arc, preferred_keys=("name", "title", "arc", "summary"))
            if arc_name:
                goals.append({"goal": f"Keep advancing the active arc: {arc_name}"})

        for hook in foreshadows[:2]:
            hook_text = self._item_to_text(hook, preferred_keys=("hook", "title", "content", "summary"))
            if hook_text:
                goals.append({"goal": f"Pay visible attention to unresolved hook: {hook_text}"})

        if character_cards:
            protagonist = character_cards[0]
            name = str(protagonist.get("name") or "The protagonist").strip()
            conflict = self._item_to_text(
                protagonist,
                preferred_keys=("core_conflict", "核心冲突", "arc", "description", "summary"),
            )
            if conflict:
                goals.append({"goal": f"Keep {name}'s core pressure active: {conflict}"})

        return self._dedupe_dict_items(goals, primary_key="goal", max_items=6)

    def _build_fallback_beats(self, *, bible: dict[str, Any]) -> list[dict[str, Any]]:
        beats: list[dict[str, Any]] = []
        timeline = self._as_dict_list(bible.get("timeline"))
        foreshadows = self._as_dict_list(bible.get("foreshadows"))
        story_arcs = self._as_dict_list(bible.get("story_arcs"))

        if timeline:
            anchor = self._item_to_text(timeline[-1], preferred_keys=("event", "milestone", "summary", "impact"))
            if anchor:
                beats.append({"beat": f"Open by acknowledging the latest continuity anchor: {anchor}"})

        for hook in foreshadows[:3]:
            hook_text = self._item_to_text(hook, preferred_keys=("hook", "title", "content", "summary"))
            if hook_text:
                beats.append({"beat": f"Give an on-page reaction or consequence for unresolved hook: {hook_text}"})

        for arc in story_arcs[:2]:
            arc_name = self._item_to_text(arc, preferred_keys=("name", "title", "arc", "summary"))
            if arc_name:
                beats.append({"beat": f"Move the current arc one step forward: {arc_name}"})

        if len(beats) < 3 and timeline:
            beats.append({"beat": "Keep the next scene grounded in the same time, place, and relationship state as the source ending"})

        return self._dedupe_dict_items(beats, primary_key="beat", max_items=8)

    def _build_fallback_priority_hooks(self, *, bible: dict[str, Any]) -> list[dict[str, Any]]:
        hooks: list[dict[str, Any]] = []
        foreshadows = self._as_dict_list(bible.get("foreshadows"))
        timeline = self._as_dict_list(bible.get("timeline"))
        story_arcs = self._as_dict_list(bible.get("story_arcs"))

        for hook in foreshadows[:6]:
            hook_text = self._item_to_text(hook, preferred_keys=("hook", "title", "content", "summary"))
            if hook_text:
                hooks.append({"hook": hook_text})

        if not hooks and timeline:
            anchor = self._item_to_text(timeline[-1], preferred_keys=("event", "milestone", "summary", "impact"))
            if anchor:
                hooks.append({"hook": f"Preserve the immediate consequence of: {anchor}"})

        if len(hooks) < 3:
            for arc in story_arcs[:2]:
                arc_name = self._item_to_text(arc, preferred_keys=("name", "title", "arc", "summary"))
                if arc_name:
                    hooks.append({"hook": f"Do not drop arc continuity: {arc_name}"})

        return self._dedupe_dict_items(hooks, primary_key="hook", max_items=6)

    def _build_fallback_guardrails(self, *, bible: dict[str, Any]) -> list[dict[str, Any]]:
        rules: list[dict[str, Any]] = []
        hard_constraints = self._as_dict_list(bible.get("hard_constraints"))
        timeline = self._as_dict_list(bible.get("timeline"))
        story_arcs = self._as_dict_list(bible.get("story_arcs"))
        character_cards = self._as_dict_list(bible.get("character_cards"))

        for item in hard_constraints[:8]:
            rule_text = self._item_to_text(item, preferred_keys=("rule", "constraint", "content", "summary"))
            if rule_text:
                rules.append({"rule": rule_text})

        if timeline:
            rules.append({"rule": "Continue along the established event order; do not reset or skip already happened story facts."})

        if story_arcs:
            arc_name = self._item_to_text(story_arcs[0], preferred_keys=("name", "title", "arc", "summary"))
            if arc_name:
                rules.append({"rule": f"Do not abandon the active story line without paying it off first: {arc_name}"})

        if character_cards:
            protagonist = character_cards[0]
            name = str(protagonist.get("name") or "The protagonist").strip()
            rules.append({"rule": f"Keep {name}'s established behavior logic and emotional pressure consistent with prior chapters."})

        return self._dedupe_dict_items(rules, primary_key="rule", max_items=10)

    def _dedupe_dict_items(
        self,
        items: list[dict[str, Any]],
        *,
        primary_key: str,
        max_items: int,
    ) -> list[dict[str, Any]]:
        deduped: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in items:
            text = str(item.get(primary_key) or "").strip()
            if not text or text in seen:
                continue
            deduped.append({primary_key: text})
            seen.add(text)
            if len(deduped) >= max_items:
                break
        return deduped

    def _item_to_text(self, item: dict[str, Any], *, preferred_keys: tuple[str, ...]) -> str:
        for key in preferred_keys:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        compact = json.dumps(item, ensure_ascii=False, sort_keys=True)
        return compact[:220]

    def _empty_payload(self) -> dict[str, Any]:
        return {
            "summary": "",
            "stage_goals": [],
            "beats": [],
            "priority_hooks": [],
            "guardrails": [],
        }
