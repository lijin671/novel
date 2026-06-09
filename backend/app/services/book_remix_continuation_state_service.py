"""Incrementally sync generated chapter analysis back into remix continuation state."""

from __future__ import annotations

import re
from copy import deepcopy
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan


class BookRemixContinuationStateService:
    """Apply per-chapter analysis deltas to confirmed remix bible and plan records."""

    async def commit_generated_chapter(
        self,
        *,
        db: AsyncSession,
        project_id: str,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        chapter_content: str,
        chapter_outline: str = "",
        previous_chapter_summary: str = "",
        continuation_point: str = "",
        guardrail_meta: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Immediately persist a generated-chapter continuity checkpoint.

        后台分析仍会补全更细的分析包；这里负责在正文保存后先落一笔
        `chapter_generation`，让下一章 prompt 能立刻读到上一章的状态变化。
        """
        bible, plan = await self._load_confirmed_state(db=db, project_id=project_id)
        if not bible or not plan:
            return {"changed": False, "reason": "remix_context_not_confirmed"}

        changed_sections: list[str] = []
        guardrail_check = self._serialize_guardrail_check(guardrail_meta)

        if self._commit_generated_timeline(
            bible=bible,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            chapter_content=chapter_content,
        ):
            changed_sections.append("timeline")

        if self._commit_generated_character_cards(
            bible=bible,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            chapter_content=chapter_content,
        ):
            changed_sections.append("character_cards")

        if self._commit_generated_plan_beats(
            plan=plan,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            chapter_content=chapter_content,
            chapter_outline=chapter_outline,
        ):
            changed_sections.append("plan_beats")

        if self._commit_generated_chapter_change_package(
            bible=bible,
            plan=plan,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            chapter_content=chapter_content,
            chapter_outline=chapter_outline,
            previous_chapter_summary=previous_chapter_summary,
            continuation_point=continuation_point,
            guardrail_check=guardrail_check,
            changed_sections=[
                *changed_sections,
                *(["guardrail_check"] if guardrail_check else []),
                "chapter_change_packages",
            ],
        ):
            changed_sections.append("chapter_change_packages")

        if not changed_sections:
            return {"changed": False, "reason": "already_committed", "changed_sections": []}

        final_sections = [
            *[section for section in changed_sections if section != "chapter_change_packages"],
            "chapter_change_packages",
        ] if "chapter_change_packages" in changed_sections else changed_sections
        if guardrail_check and "chapter_change_packages" in final_sections and "guardrail_check" not in final_sections:
            insert_at = final_sections.index("chapter_change_packages")
            final_sections.insert(insert_at, "guardrail_check")
        plan.updated_at = datetime.utcnow()

        await db.commit()
        return {"changed": True, "reason": "committed", "changed_sections": final_sections}

    async def sync_chapter_analysis(
        self,
        *,
        db: AsyncSession,
        project_id: str,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        analysis_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Patch confirmed remix bible/plan from one chapter analysis result.

        The sync is intentionally narrow and idempotent. It only appends or marks
        machine-owned chapter-analysis entries, leaving user-authored/manual
        bible entries in place.
        """
        bible, plan = await self._load_confirmed_state(db=db, project_id=project_id)
        if not bible or not plan:
            return {"changed": False, "reason": "remix_context_not_confirmed"}

        changed_sections: list[str] = []

        if self._sync_timeline(
            bible=bible,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            analysis_result=analysis_result,
        ):
            changed_sections.append("timeline")

        if self._sync_foreshadows(
            bible=bible,
            plan=plan,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            analysis_result=analysis_result,
        ):
            changed_sections.append("foreshadows")

        if self._sync_character_cards(
            bible=bible,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            analysis_result=analysis_result,
        ):
            changed_sections.append("character_cards")

        if self._sync_plan_beats(
            plan=plan,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            analysis_result=analysis_result,
        ):
            changed_sections.append("plan_beats")

        if not changed_sections and self._has_synced_chapter_change_package(
            bible=bible,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        ):
            return {"changed": False, "reason": "already_synced", "changed_sections": []}

        if self._sync_chapter_change_package(
            bible=bible,
            plan=plan,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            analysis_result=analysis_result,
            changed_sections=changed_sections,
        ):
            changed_sections.append("chapter_change_packages")

        if not changed_sections:
            return {"changed": False, "reason": "already_synced", "changed_sections": []}

        final_sections = [
            *[section for section in changed_sections if section != "chapter_change_packages"],
            "chapter_change_packages",
        ] if "chapter_change_packages" in changed_sections else changed_sections
        self._sync_package_changed_sections(bible=bible, changed_sections=final_sections)
        plan.updated_at = datetime.utcnow()

        await db.commit()
        return {"changed": True, "reason": "synced", "changed_sections": final_sections}

    async def _load_confirmed_state(
        self,
        *,
        db: AsyncSession,
        project_id: str,
    ) -> tuple[Optional[BookRemixBible], Optional[BookRemixContinuationPlan]]:
        bible_result = await db.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project_id)
        )
        bible = bible_result.scalar_one_or_none()
        if not bible:
            return None, None

        plan_result = await db.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project_id
            )
        )
        plan = plan_result.scalar_one_or_none()
        if not plan:
            return bible, None

        if str(bible.generation_status or "").strip().lower() != "confirmed":
            return bible, None
        if str(plan.status or "").strip().lower() != "confirmed":
            return bible, None
        if str(plan.bible_id or "") != str(bible.id):
            return bible, None
        if plan.updated_at and bible.updated_at and plan.updated_at < bible.updated_at:
            return bible, None
        if not str(bible.source_task_id or "").strip():
            return bible, None
        if int(bible.source_chapter_count or 0) <= 0:
            return bible, None

        return bible, plan

    def _sync_timeline(
        self,
        *,
        bible: BookRemixBible,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        analysis_result: dict[str, Any],
    ) -> bool:
        timeline = self._dict_list(bible.timeline)
        event = self._build_timeline_event(
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            analysis_result=analysis_result,
        )
        if not event:
            return False

        existing_index = self._find_analysis_entry_index(
            timeline,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        )
        generated_index = self._find_entry_index(
            timeline,
            source="chapter_generation",
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        )
        if existing_index >= 0:
            timeline = self._without_generated_entries_for_chapter(
                timeline,
                chapter_id=chapter_id,
                chapter_number=chapter_number,
                keep_index=existing_index,
            )
            existing_index = self._find_analysis_entry_index(
                timeline,
                chapter_id=chapter_id,
                chapter_number=chapter_number,
            )
            if timeline[existing_index] == event:
                if timeline != self._dict_list(bible.timeline):
                    bible.timeline = timeline
                    return True
                return False
            timeline[existing_index] = event
            bible.timeline = timeline
            return True

        if generated_index >= 0:
            timeline[generated_index] = event
            timeline = self._without_generated_entries_for_chapter(
                timeline,
                chapter_id=chapter_id,
                chapter_number=chapter_number,
                keep_index=generated_index,
            )
            bible.timeline = timeline
            return True

        timeline.append(event)
        bible.timeline = timeline
        return True

    def _sync_foreshadows(
        self,
        *,
        bible: BookRemixBible,
        plan: BookRemixContinuationPlan,
        chapter_id: str,
        chapter_number: int,
        analysis_result: dict[str, Any],
    ) -> bool:
        changed = False
        bible_foreshadows = self._dict_list(bible.foreshadows)
        plan_hooks = self._dict_list(plan.priority_hooks)

        for foreshadow in self._dict_list(analysis_result.get("foreshadows")):
            hook_text = self._extract_text(
                foreshadow,
                keys=("hook", "content", "title", "summary"),
            )
            if not hook_text:
                continue

            status = self._normalize_foreshadow_status(foreshadow.get("type") or foreshadow.get("status"))
            patch = {
                "hook": hook_text,
                "status": status,
                "source": "chapter_analysis",
                "chapter_id": chapter_id,
                "chapter_number": chapter_number,
            }
            if foreshadow.get("strength") is not None:
                patch["strength"] = foreshadow.get("strength")

            index = self._find_by_text(bible_foreshadows, text=hook_text, keys=("hook", "content", "title", "summary"))
            if index >= 0:
                merged = {**bible_foreshadows[index], **patch}
                if merged != bible_foreshadows[index]:
                    bible_foreshadows[index] = merged
                    changed = True
            else:
                bible_foreshadows.append(patch)
                changed = True

            if status == "resolved":
                changed |= self._mark_matching_items_done(
                    items=plan_hooks,
                    text=hook_text,
                    chapter_id=chapter_id,
                    chapter_number=chapter_number,
                    text_keys=("hook", "title", "content", "summary"),
                )

        if changed:
            bible.foreshadows = bible_foreshadows
            plan.priority_hooks = plan_hooks
        return changed

    def _sync_character_cards(
        self,
        *,
        bible: BookRemixBible,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        analysis_result: dict[str, Any],
    ) -> bool:
        cards = self._dict_list(bible.character_cards)
        changed = False

        for state in self._dict_list(analysis_result.get("character_states")):
            name = self._extract_text(state, keys=("character_name", "name"))
            if not name:
                continue

            update = {
                "chapter_id": chapter_id,
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "state_after": self._string_or_empty(state.get("state_after")),
                "state_before": self._string_or_empty(state.get("state_before")),
                "psychological_change": self._string_or_empty(state.get("psychological_change")),
                "key_event": self._string_or_empty(state.get("key_event")),
                "source": "chapter_analysis",
            }
            update = {key: value for key, value in update.items() if value not in ("", None)}

            card_index = self._find_by_text(cards, text=name, keys=("name", "character_name"), exact=True)
            if card_index < 0:
                cards.append({"name": name, "continuation_updates": [update]})
                changed = True
                continue

            card = deepcopy(cards[card_index])
            updates = self._dict_list(card.get("continuation_updates"))
            existing_index = self._find_analysis_entry_index(
                updates,
                chapter_id=chapter_id,
                chapter_number=chapter_number,
            )
            generated_index = self._find_entry_index(
                updates,
                source="chapter_generation",
                chapter_id=chapter_id,
                chapter_number=chapter_number,
            )
            if existing_index >= 0:
                updates = self._without_generated_entries_for_chapter(
                    updates,
                    chapter_id=chapter_id,
                    chapter_number=chapter_number,
                    keep_index=existing_index,
                )
                existing_index = self._find_analysis_entry_index(
                    updates,
                    chapter_id=chapter_id,
                    chapter_number=chapter_number,
                )
                if updates[existing_index] == update:
                    card["continuation_updates"] = updates[-8:]
                    if card != cards[card_index]:
                        cards[card_index] = card
                        changed = True
                    continue
                updates[existing_index] = update
            elif generated_index >= 0:
                updates[generated_index] = update
                updates = self._without_generated_entries_for_chapter(
                    updates,
                    chapter_id=chapter_id,
                    chapter_number=chapter_number,
                    keep_index=generated_index,
                )
            else:
                updates.append(update)
            card["continuation_updates"] = updates[-8:]
            if card != cards[card_index]:
                cards[card_index] = card
                changed = True

        if changed:
            bible.character_cards = cards
        return changed

    def _sync_plan_beats(
        self,
        *,
        plan: BookRemixContinuationPlan,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        analysis_result: dict[str, Any],
    ) -> bool:
        beats = self._dict_list(plan.beats)
        if not beats:
            return False

        evidence_parts = self._analysis_texts(analysis_result)
        if not evidence_parts:
            return False
        evidence = "\n".join(evidence_parts)

        changed = False
        for index, beat in enumerate(beats):
            status = str(beat.get("status") or "").strip().lower()
            if status == "done":
                continue
            beat_text = self._extract_text(beat, keys=("beat", "summary", "content", "name"))
            if not beat_text:
                continue
            if not self._texts_overlap(beat_text, evidence):
                continue

            updated = {
                **beat,
                "status": "done",
                "last_chapter_id": chapter_id,
                "last_chapter_number": chapter_number,
                "last_chapter_title": chapter_title,
                "evidence": self._truncate(evidence, 360),
            }
            if updated != beat:
                beats[index] = updated
                changed = True

        if changed:
            plan.beats = beats
        return changed

    def _has_synced_chapter_change_package(
        self,
        *,
        bible: BookRemixBible,
        chapter_id: str,
        chapter_number: int,
    ) -> bool:
        packages = self._dict_list(bible.chapter_change_packages)
        return self._find_analysis_entry_index(
            packages,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        ) >= 0

    def _has_chapter_change_package(
        self,
        *,
        bible: BookRemixBible,
        source: str,
        chapter_id: str,
        chapter_number: int,
    ) -> bool:
        packages = self._dict_list(bible.chapter_change_packages)
        return self._find_entry_index(
            packages,
            source=source,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        ) >= 0

    def _commit_generated_timeline(
        self,
        *,
        bible: BookRemixBible,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        chapter_content: str,
    ) -> bool:
        event_text = self._chapter_content_summary(chapter_content)
        if not event_text:
            return False

        timeline = self._dict_list(bible.timeline)
        event = {
            "chapter_id": chapter_id,
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "event": self._truncate(event_text, 240),
            "summary": self._truncate(event_text, 360),
            "source": "chapter_generation",
        }
        existing_index = self._find_entry_index(
            timeline,
            source="chapter_generation",
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        )
        if existing_index >= 0:
            if timeline[existing_index] == event:
                return False
            timeline[existing_index] = event
        else:
            timeline.append(event)
        bible.timeline = timeline
        return True

    def _commit_generated_character_cards(
        self,
        *,
        bible: BookRemixBible,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        chapter_content: str,
    ) -> bool:
        cards = self._dict_list(bible.character_cards)
        summary = self._chapter_content_summary(chapter_content)
        if not cards or not summary:
            return False

        changed = False
        content = self._normalize_text(chapter_content)
        for index, card in enumerate(cards):
            name = self._extract_text(card, keys=("name", "character_name"))
            if not name:
                continue
            if self._normalize_text(name) not in content:
                continue

            updated_card = deepcopy(card)
            updates = self._dict_list(updated_card.get("continuation_updates"))
            update = {
                "chapter_id": chapter_id,
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "state_after": self._truncate(summary, 180),
                "key_event": self._truncate(summary, 180),
                "source": "chapter_generation",
            }
            existing_index = self._find_entry_index(
                updates,
                source="chapter_generation",
                chapter_id=chapter_id,
                chapter_number=chapter_number,
            )
            if existing_index >= 0:
                if updates[existing_index] == update:
                    continue
                updates[existing_index] = update
            else:
                updates.append(update)
            updated_card["continuation_updates"] = updates[-8:]
            if updated_card != card:
                cards[index] = updated_card
                changed = True

        if changed:
            bible.character_cards = cards
        return changed

    def _commit_generated_plan_beats(
        self,
        *,
        plan: BookRemixContinuationPlan,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        chapter_content: str,
        chapter_outline: str,
    ) -> bool:
        beats = self._dict_list(plan.beats)
        if not beats:
            return False

        evidence = "\n".join(
            text
            for text in (
                self._string_or_empty(chapter_outline),
                self._chapter_content_summary(chapter_content),
                self._truncate(chapter_content, 800),
            )
            if text
        )
        if not evidence:
            return False

        changed = False
        for index, beat in enumerate(beats):
            status = str(beat.get("status") or "").strip().lower()
            if status == "done":
                continue
            beat_text = self._extract_text(beat, keys=("beat", "summary", "content", "name"))
            if not beat_text or not self._texts_overlap(beat_text, evidence):
                continue

            updated = {
                **beat,
                "status": "done",
                "last_chapter_id": chapter_id,
                "last_chapter_number": chapter_number,
                "last_chapter_title": chapter_title,
                "evidence": self._truncate(evidence, 360),
            }
            if updated != beat:
                beats[index] = updated
                changed = True

        if changed:
            plan.beats = beats
        return changed

    def _commit_generated_chapter_change_package(
        self,
        *,
        bible: BookRemixBible,
        plan: BookRemixContinuationPlan,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        chapter_content: str,
        chapter_outline: str,
        previous_chapter_summary: str,
        continuation_point: str,
        guardrail_check: Optional[dict[str, Any]],
        changed_sections: list[str],
    ) -> bool:
        packages = self._dict_list(bible.chapter_change_packages)
        package = self._build_generated_chapter_change_package(
            bible=bible,
            plan=plan,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            chapter_content=chapter_content,
            chapter_outline=chapter_outline,
            previous_chapter_summary=previous_chapter_summary,
            continuation_point=continuation_point,
            guardrail_check=guardrail_check,
            changed_sections=changed_sections,
        )
        existing_index = self._find_entry_index(
            packages,
            source="chapter_generation",
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        )
        if existing_index >= 0:
            if changed_sections == ["chapter_change_packages"]:
                package["changed_sections"] = packages[existing_index].get(
                    "changed_sections",
                    changed_sections,
                )
            if packages[existing_index] == package:
                return False
            packages[existing_index] = package
        else:
            packages.append(package)
        bible.chapter_change_packages = packages
        return True

    def _sync_chapter_change_package(
        self,
        *,
        bible: BookRemixBible,
        plan: BookRemixContinuationPlan,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        analysis_result: dict[str, Any],
        changed_sections: list[str],
    ) -> bool:
        packages = self._dict_list(bible.chapter_change_packages)
        package = self._build_chapter_change_package(
            plan=plan,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            analysis_result=analysis_result,
            changed_sections=[*changed_sections, "chapter_change_packages"],
        )
        existing_index = self._find_analysis_entry_index(
            packages,
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        )
        generated_index = self._find_entry_index(
            packages,
            source="chapter_generation",
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        )
        if existing_index >= 0:
            packages = self._without_generated_package_for_chapter(
                packages,
                chapter_id=chapter_id,
                chapter_number=chapter_number,
                keep_index=existing_index,
            )
            existing_index = self._find_analysis_entry_index(
                packages,
                chapter_id=chapter_id,
                chapter_number=chapter_number,
            )
            if packages[existing_index] == package:
                if packages != self._dict_list(bible.chapter_change_packages):
                    bible.chapter_change_packages = packages
                    return True
                return False
            packages[existing_index] = package
            bible.chapter_change_packages = packages
            return True

        if generated_index >= 0:
            packages[generated_index] = package
            packages = self._without_generated_package_for_chapter(
                packages,
                chapter_id=chapter_id,
                chapter_number=chapter_number,
                keep_index=generated_index,
            )
            bible.chapter_change_packages = packages
            return True

        packages.append(package)
        bible.chapter_change_packages = packages
        return True

    def _sync_package_changed_sections(
        self,
        *,
        bible: BookRemixBible,
        changed_sections: list[str],
    ) -> None:
        packages = self._dict_list(bible.chapter_change_packages)
        if not packages:
            return
        latest = deepcopy(packages[-1])
        if latest.get("source") != "chapter_analysis":
            return
        if latest.get("changed_sections") == changed_sections:
            return
        latest["changed_sections"] = changed_sections
        packages[-1] = latest
        bible.chapter_change_packages = packages

    def _build_chapter_change_package(
        self,
        *,
        plan: BookRemixContinuationPlan,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        analysis_result: dict[str, Any],
        changed_sections: list[str],
    ) -> dict[str, Any]:
        package = {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_id": chapter_id,
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "summary": self._truncate(self._string_or_empty(analysis_result.get("summary")), 360),
            "timeline_delta": self._build_timeline_delta(analysis_result=analysis_result),
            "character_state_changes": self._build_character_state_changes(analysis_result=analysis_result),
            "foreshadow_changes": self._build_foreshadow_changes(analysis_result=analysis_result),
            "plan_progress": self._build_plan_progress(plan=plan, chapter_id=chapter_id, chapter_number=chapter_number),
            "changed_sections": changed_sections,
        }
        emotional_arc = self._build_emotional_arc(analysis_result=analysis_result)
        if emotional_arc:
            package["emotional_arc"] = emotional_arc
        return package

    def _build_generated_chapter_change_package(
        self,
        *,
        bible: BookRemixBible,
        plan: BookRemixContinuationPlan,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        chapter_content: str,
        chapter_outline: str,
        previous_chapter_summary: str,
        continuation_point: str,
        guardrail_check: Optional[dict[str, Any]],
        changed_sections: list[str],
    ) -> dict[str, Any]:
        summary = self._chapter_content_summary(chapter_content)
        package = {
            "type": "chapter_change_package",
            "source": "chapter_generation",
            "chapter_id": chapter_id,
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "summary": self._truncate(summary, 360),
            "timeline_delta": [{"event": self._truncate(summary, 240)}] if summary else [],
            "character_state_changes": self._build_generated_character_state_changes(
                bible=bible,
                chapter_id=chapter_id,
                chapter_number=chapter_number,
            ),
            "foreshadow_changes": [],
            "plan_progress": self._build_plan_progress(
                plan=plan,
                chapter_id=chapter_id,
                chapter_number=chapter_number,
            ),
            "generation_inputs": {
                key: value
                for key, value in {
                    "chapter_outline": self._truncate(chapter_outline, 360),
                    "previous_chapter_summary": self._truncate(previous_chapter_summary, 360),
                    "continuation_point": self._truncate(continuation_point, 360),
                }.items()
                if value
            },
            "changed_sections": changed_sections,
        }
        if guardrail_check:
            package["guardrail_check"] = guardrail_check
        return package

    def _serialize_guardrail_check(self, guardrail_meta: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        if not isinstance(guardrail_meta, dict):
            return None

        violations = self._serialize_guardrail_violations(guardrail_meta.get("initial_result"))
        applied = bool(guardrail_meta.get("applied"))
        attempts = self._safe_int(guardrail_meta.get("attempts"), default=0)
        initial_passed = self._guardrail_result_passed(guardrail_meta.get("initial_result"))
        final_passed = self._guardrail_result_passed(guardrail_meta.get("final_result"))

        if not applied and attempts <= 0 and not violations:
            return None

        return {
            "applied": applied,
            "attempts": attempts,
            "initial_passed": initial_passed,
            "final_passed": final_passed,
            "violations": violations,
        }

    def _serialize_guardrail_violations(self, result: Any) -> list[dict[str, Any]]:
        raw_violations = self._guardrail_result_violations(result)
        violations: list[dict[str, Any]] = []
        for violation in raw_violations:
            value = self._guardrail_violation_to_dict(violation)
            if value:
                violations.append(value)
        return violations

    @staticmethod
    def _guardrail_result_passed(result: Any) -> bool:
        if isinstance(result, dict):
            return bool(result.get("passed"))
        return bool(getattr(result, "passed", False))

    @staticmethod
    def _guardrail_result_violations(result: Any) -> list[Any]:
        if isinstance(result, dict):
            raw = result.get("violations")
        else:
            raw = getattr(result, "violations", None)
        return list(raw) if isinstance(raw, list) else []

    def _guardrail_violation_to_dict(self, violation: Any) -> dict[str, Any]:
        if isinstance(violation, dict):
            raw = violation
        else:
            raw = {
                "type": getattr(violation, "type", None),
                "severity": getattr(violation, "severity", None),
                "description": getattr(violation, "description", None),
                "context": getattr(violation, "context", None),
                "position": getattr(violation, "position", None),
            }

        serialized = {
            key: self._string_or_empty(raw.get(key))
            for key in ("type", "severity", "description", "context")
            if self._string_or_empty(raw.get(key))
        }
        if raw.get("position") is not None:
            serialized["position"] = raw.get("position")
        return serialized

    def _build_generated_character_state_changes(
        self,
        *,
        bible: BookRemixBible,
        chapter_id: str,
        chapter_number: int,
    ) -> list[dict[str, Any]]:
        changes: list[dict[str, Any]] = []
        for card in self._dict_list(bible.character_cards):
            name = self._extract_text(card, keys=("name", "character_name"))
            if not name:
                continue
            for update in self._dict_list(card.get("continuation_updates")):
                if update.get("source") != "chapter_generation":
                    continue
                if str(update.get("chapter_id") or "") != str(chapter_id) and int(update.get("chapter_number") or -1) != int(chapter_number):
                    continue
                item = {
                    "character_name": name,
                    "state_after": self._string_or_empty(update.get("state_after")),
                    "key_event": self._string_or_empty(update.get("key_event")),
                }
                changes.append({key: value for key, value in item.items() if value not in ("", None)})
        return changes[:8]

    def _build_timeline_delta(self, *, analysis_result: dict[str, Any]) -> list[dict[str, Any]]:
        deltas: list[dict[str, Any]] = []
        for plot_point in self._dict_list(analysis_result.get("plot_points")):
            event = self._extract_text(plot_point, keys=("content", "summary", "event"))
            if not event:
                continue
            item: dict[str, Any] = {"event": self._truncate(event, 240)}
            impact = self._string_or_empty(plot_point.get("impact"))
            point_type = self._string_or_empty(plot_point.get("type"))
            if impact:
                item["impact"] = self._truncate(impact, 240)
            if point_type:
                item["type"] = point_type
            importance = plot_point.get("importance")
            if importance is not None:
                item["importance"] = importance
            deltas.append(item)
        if deltas:
            return deltas[:5]

        summary = self._string_or_empty(analysis_result.get("summary"))
        return [{"event": self._truncate(summary, 240)}] if summary else []

    def _build_character_state_changes(self, *, analysis_result: dict[str, Any]) -> list[dict[str, Any]]:
        changes: list[dict[str, Any]] = []
        for state in self._dict_list(analysis_result.get("character_states")):
            name = self._extract_text(state, keys=("character_name", "name"))
            if not name:
                continue
            item = {
                "character_name": name,
                "state_before": self._string_or_empty(state.get("state_before")),
                "state_after": self._string_or_empty(state.get("state_after")),
                "psychological_change": self._string_or_empty(state.get("psychological_change")),
                "key_event": self._string_or_empty(state.get("key_event")),
            }
            changes.append({key: value for key, value in item.items() if value not in ("", None)})
        return changes[:8]

    def _build_foreshadow_changes(self, *, analysis_result: dict[str, Any]) -> list[dict[str, Any]]:
        changes: list[dict[str, Any]] = []
        for foreshadow in self._dict_list(analysis_result.get("foreshadows")):
            hook = self._extract_text(foreshadow, keys=("hook", "content", "title", "summary"))
            if not hook:
                continue
            item: dict[str, Any] = {
                "hook": hook,
                "status": self._normalize_foreshadow_status(
                    foreshadow.get("type") or foreshadow.get("status")
                ),
            }
            if foreshadow.get("strength") is not None:
                item["strength"] = foreshadow.get("strength")
            changes.append(item)
        return changes[:8]

    def _build_emotional_arc(self, *, analysis_result: dict[str, Any]) -> dict[str, Any]:
        raw = analysis_result.get("emotional_arc")
        if isinstance(raw, dict):
            source = raw
        else:
            source = {
                "tone": analysis_result.get("emotional_tone"),
                "intensity": analysis_result.get("emotional_intensity"),
                "curve": analysis_result.get("emotional_curve"),
            }

        arc: dict[str, Any] = {}
        tone = self._string_or_empty(source.get("tone") or source.get("primary_emotion") or source.get("emotion"))
        if tone:
            arc["tone"] = tone
        if source.get("intensity") is not None:
            arc["intensity"] = source.get("intensity")
        if source.get("curve") is not None:
            arc["curve"] = source.get("curve")
        secondary = source.get("secondary_emotions")
        if isinstance(secondary, list) and secondary:
            arc["secondary_emotions"] = secondary[:6]
        return arc

    def _build_plan_progress(
        self,
        *,
        plan: BookRemixContinuationPlan,
        chapter_id: str,
        chapter_number: int,
    ) -> list[dict[str, Any]]:
        progress: list[dict[str, Any]] = []
        for beat in self._dict_list(plan.beats):
            if str(beat.get("last_chapter_id") or "") != str(chapter_id) and int(beat.get("last_chapter_number") or -1) != int(chapter_number):
                continue
            beat_text = self._extract_text(beat, keys=("beat", "summary", "content", "name"))
            if not beat_text:
                continue
            progress.append({"beat": beat_text, "status": str(beat.get("status") or "")})
        return progress[:8]

    def _build_timeline_event(
        self,
        *,
        chapter_id: str,
        chapter_number: int,
        chapter_title: str,
        analysis_result: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        summary = self._string_or_empty(analysis_result.get("summary"))
        plot_points = self._dict_list(analysis_result.get("plot_points"))
        important_points = [
            self._extract_text(item, keys=("content", "summary", "event"))
            for item in plot_points
            if self._safe_float(item.get("importance"), default=0.0) >= 0.6
        ]
        important_points = [text for text in important_points if text]

        event_text = important_points[0] if important_points else summary
        if not event_text:
            return None

        event: dict[str, Any] = {
            "chapter_id": chapter_id,
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "event": self._truncate(event_text, 240),
            "source": "chapter_analysis",
        }
        if summary:
            event["summary"] = self._truncate(summary, 360)
        if important_points:
            event["key_points"] = [self._truncate(text, 180) for text in important_points[:5]]
        return event

    def _mark_matching_items_done(
        self,
        *,
        items: list[dict[str, Any]],
        text: str,
        chapter_id: str,
        chapter_number: int,
        text_keys: tuple[str, ...],
    ) -> bool:
        changed = False
        for index, item in enumerate(items):
            item_text = self._extract_text(item, keys=text_keys)
            if not item_text or not self._texts_overlap(item_text, text):
                continue
            updated = {
                **item,
                "status": "done",
                "last_chapter_id": chapter_id,
                "last_chapter_number": chapter_number,
            }
            if updated != item:
                items[index] = updated
                changed = True
        return changed

    def _analysis_texts(self, analysis_result: dict[str, Any]) -> list[str]:
        texts: list[str] = []
        summary = self._string_or_empty(analysis_result.get("summary"))
        if summary:
            texts.append(summary)
        for key in ("plot_points", "foreshadows", "hooks", "character_states"):
            for item in self._dict_list(analysis_result.get(key)):
                text = self._extract_text(
                    item,
                    keys=(
                        "content",
                        "summary",
                        "event",
                        "hook",
                        "keyword",
                        "state_after",
                        "key_event",
                    ),
                )
                if text:
                    texts.append(text)
        return texts

    def _chapter_content_summary(self, content: str) -> str:
        text = self._string_or_empty(content)
        if not text:
            return ""
        collapsed = " ".join(text.split())
        return self._truncate(collapsed, 360)

    def _find_analysis_entry_index(
        self,
        items: list[dict[str, Any]],
        *,
        chapter_id: str,
        chapter_number: int,
    ) -> int:
        return self._find_entry_index(
            items,
            source="chapter_analysis",
            chapter_id=chapter_id,
            chapter_number=chapter_number,
        )

    def _find_entry_index(
        self,
        items: list[dict[str, Any]],
        *,
        source: str,
        chapter_id: str,
        chapter_number: int,
    ) -> int:
        for index, item in enumerate(items):
            if item.get("source") != source:
                continue
            if str(item.get("chapter_id") or "") == str(chapter_id):
                return index
            if int(item.get("chapter_number") or -1) == int(chapter_number):
                return index
        return -1

    def _without_generated_package_for_chapter(
        self,
        packages: list[dict[str, Any]],
        *,
        chapter_id: str,
        chapter_number: int,
        keep_index: int,
    ) -> list[dict[str, Any]]:
        kept: list[dict[str, Any]] = []
        for index, item in enumerate(packages):
            if index == keep_index:
                kept.append(item)
                continue
            if item.get("source") != "chapter_generation":
                kept.append(item)
                continue
            if str(item.get("chapter_id") or "") == str(chapter_id):
                continue
            if int(item.get("chapter_number") or -1) == int(chapter_number):
                continue
            kept.append(item)
        return kept

    def _without_generated_entries_for_chapter(
        self,
        items: list[dict[str, Any]],
        *,
        chapter_id: str,
        chapter_number: int,
        keep_index: int,
    ) -> list[dict[str, Any]]:
        kept: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if index == keep_index:
                kept.append(item)
                continue
            if item.get("source") != "chapter_generation":
                kept.append(item)
                continue
            if str(item.get("chapter_id") or "") == str(chapter_id):
                continue
            if int(item.get("chapter_number") or -1) == int(chapter_number):
                continue
            kept.append(item)
        return kept

    def _find_by_text(
        self,
        items: list[dict[str, Any]],
        *,
        text: str,
        keys: tuple[str, ...],
        exact: bool = False,
    ) -> int:
        for index, item in enumerate(items):
            item_text = self._extract_text(item, keys=keys)
            if not item_text:
                continue
            if exact:
                if item_text.strip().lower() == text.strip().lower():
                    return index
            elif self._texts_overlap(item_text, text):
                return index
        return -1

    def _texts_overlap(self, left: str, right: str) -> bool:
        normalized_left = self._normalize_text(left)
        normalized_right = self._normalize_text(right)
        if not normalized_left or not normalized_right:
            return False
        if normalized_left in normalized_right or normalized_right in normalized_left:
            return True

        left_tokens = set(self._tokens(normalized_left))
        right_tokens = set(self._tokens(normalized_right))
        if not left_tokens or not right_tokens:
            return False
        direct_matches = left_tokens & right_tokens
        fuzzy_matches = {
            left_token
            for left_token in left_tokens
            for right_token in right_tokens
            if self._tokens_match(left_token, right_token)
        }
        return len(direct_matches | fuzzy_matches) >= min(2, len(left_tokens), len(right_tokens))

    def _normalize_text(self, value: str) -> str:
        return " ".join(str(value or "").strip().lower().split())

    def _tokens(self, value: str) -> list[str]:
        return [
            token
            for token in re.findall(r"[a-z0-9\u4e00-\u9fff]+", value.lower())
            if len(token) > 1
        ]

    def _tokens_match(self, left: str, right: str) -> bool:
        if left == right:
            return True
        if len(left) < 4 or len(right) < 4:
            return False
        return left in right or right in left

    def _extract_text(self, item: dict[str, Any], *, keys: tuple[str, ...]) -> str:
        for key in keys:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _dict_list(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [deepcopy(item) for item in value if isinstance(item, dict)]

    def _normalize_foreshadow_status(self, value: Any) -> str:
        normalized = str(value or "").strip().lower()
        if normalized in {"resolved", "done", "paid", "回收", "已回收"}:
            return "resolved"
        if normalized in {"planted", "open", "pending", "埋下", "已埋下"}:
            return "open"
        return "open"

    def _string_or_empty(self, value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    def _safe_float(self, value: Any, *, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _safe_int(self, value: Any, *, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _truncate(self, value: str, limit: int) -> str:
        text = self._string_or_empty(value)
        return text if len(text) <= limit else text[:limit].rstrip() + "..."


book_remix_continuation_state_service = BookRemixContinuationStateService()
