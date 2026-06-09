"""Draft continuation bible generation service for remix projects."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from app.models.project import Project
from app.schemas.book_import import BookImportChapter
from app.services.ai_service import AIService
from app.services.source_discovery_service import source_discovery_service
from app.services.source_pattern_pack_prompt import render_source_pattern_pack_digest


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class BookRemixBibleService:
    """Generate a normalized draft bible payload for continuation projects."""

    def __init__(self, ai_service: AIService) -> None:
        self.ai_service = ai_service

    async def build_draft_payload(
        self,
        *,
        project: Project,
        source_chapters: list[BookImportChapter],
        analysis_snapshots: Optional[list[dict[str, Any]]] = None,
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Build draft bible payload with guaranteed section keys."""
        resolved_source_pattern_pack = source_pattern_pack
        if resolved_source_pattern_pack is None:
            resolved_source_pattern_pack = await source_discovery_service.resolve_fresh_pattern_pack(
                repo_root=PROJECT_ROOT,
                force=False,
            )
        prompt = self._build_prompt(
            project=project,
            source_chapters=source_chapters,
            analysis_snapshots=analysis_snapshots or [],
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
        return self._backfill_empty_sections(
            project=project,
            payload=normalized_payload,
            source_chapters=source_chapters,
            analysis_snapshots=analysis_snapshots or [],
        )

    def _build_prompt(
        self,
        *,
        project: Project,
        source_chapters: list[BookImportChapter],
        analysis_snapshots: list[dict[str, Any]],
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> str:
        sample = self._build_chapter_sample(source_chapters)
        analysis_digest = self._build_analysis_digest(analysis_snapshots)
        source_pattern_digest = self._build_source_pattern_pack_digest(source_pattern_pack)
        template = json.dumps(self._empty_payload(), ensure_ascii=False, indent=2)

        return (
            "你正在为一部“忠实续写优先”的小说二创项目生成续写圣经草稿。\n"
            "必须返回严格 JSON，不要输出解释文字。\n"
            "所有字段内容默认使用简体中文表达；不要写成英文编辑摘要。\n"
            "请使用以下顶层键，并保持每个键的类型不变：\n"
            f"{template}\n\n"
            "要求：\n"
            "- 目标是“接着原书继续写”，不是做读后感，也不是做泛化设定摘要。\n"
            "- `character_cards` 要偏人物不崩约束，写清身份、核心冲突、行为底色、后续不能写崩的点。\n"
            "- `timeline` 要写出关键时间线硬锚点，至少覆盖开篇、转折、当前局面，不要留空。\n"
            "- `foreshadows` 要写出尚未回收、后续必须承接的线索，不要留空。\n"
            "- `hard_constraints` 要写成真正约束续写的禁写项/必守项，不要留空。\n"
            "- `story_arcs` 写主线/支线的当前推进状态，而不是泛泛主题词。\n"
            "- `generation_notes` 要写成给后续续写使用的续写提示，而不是泛化写作建议。\n"
            f"- 项目标题：{project.title}\n"
            f"- 项目主题：{(project.theme or '未知')}\n"
            f"- 题材：{(project.genre or '未知')}\n"
            f"- 叙事视角：{(project.narrative_perspective or '未知')}\n\n"
            "公开来源模式包（pattern-only，只吸收工作流模式，不导入外部代码）：\n"
            f"{source_pattern_digest}\n\n"
            "原书章节摘要与正文摘录：\n"
            f"{sample}"
            f"\n\n已有章节分析摘要：\n{analysis_digest}"
        )

    def _build_chapter_sample(self, chapters: list[BookImportChapter]) -> str:
        if not chapters:
            return "(no source chapters)"

        selected = self._select_source_window(chapters)
        lines: list[str] = []
        total_chars = 0
        max_chars = 12000

        for chapter, segment in selected:
            content = self._normalize_text(chapter.content)
            summary = self._normalize_text(chapter.summary or "")
            summary_is_shallow = self._is_shallow_summary(summary=summary, content=content)
            excerpt = self._build_content_excerpt(
                content=content,
                max_chars=420 if summary_is_shallow else 260,
            )
            summary_preview = summary[:220] if summary else "(empty)"
            block = (
                f"- Chapter {chapter.chapter_number} [{segment}]: {chapter.title}\n"
                f"  summary_quality: {'shallow' if summary_is_shallow else 'usable'}\n"
                f"  summary: {summary_preview}\n"
                f"  content_excerpt: {excerpt or '(empty)'}"
            )
            if total_chars + len(block) > max_chars:
                break
            lines.append(block)
            total_chars += len(block) + 1

        return "\n".join(lines) if lines else "(no source chapters)"

    def _select_source_window(
        self,
        chapters: list[BookImportChapter],
        *,
        max_chapters: int = 12,
        head_size: int = 4,
        tail_size: int = 4,
    ) -> list[tuple[BookImportChapter, str]]:
        if len(chapters) <= max_chapters:
            return [(chapter, "full") for chapter in chapters]

        head = chapters[:head_size]
        tail = chapters[-tail_size:]
        middle_pool = chapters[head_size:-tail_size]
        middle_slots = max(0, max_chapters - len(head) - len(tail))

        middle: list[BookImportChapter] = []
        if middle_slots > 0 and middle_pool:
            indices = self._pick_even_indices(total=len(middle_pool), count=min(middle_slots, len(middle_pool)))
            middle = [middle_pool[index] for index in indices]

        ordered: list[tuple[BookImportChapter, str]] = (
            [(chapter, "head") for chapter in head]
            + [(chapter, "middle") for chapter in middle]
            + [(chapter, "tail") for chapter in tail]
        )

        deduped: list[tuple[BookImportChapter, str]] = []
        seen_numbers: set[int] = set()
        for chapter, segment in ordered:
            if chapter.chapter_number in seen_numbers:
                continue
            deduped.append((chapter, segment))
            seen_numbers.add(chapter.chapter_number)

        return deduped[:max_chapters]

    def _pick_even_indices(self, *, total: int, count: int) -> list[int]:
        if total <= 0 or count <= 0:
            return []
        if count >= total:
            return list(range(total))

        indices: list[int] = []
        for item_index in range(count):
            raw_position = int((item_index + 0.5) * total / count)
            bounded_position = max(0, min(total - 1, raw_position))
            indices.append(bounded_position)

        deduped_indices: list[int] = []
        seen: set[int] = set()
        for index in indices:
            if index in seen:
                continue
            deduped_indices.append(index)
            seen.add(index)

        cursor = 0
        while len(deduped_indices) < count and cursor < total:
            if cursor not in seen:
                deduped_indices.append(cursor)
                seen.add(cursor)
            cursor += 1

        return sorted(deduped_indices[:count])

    def _is_shallow_summary(self, *, summary: str, content: str) -> bool:
        if not summary:
            return True
        if len(summary) < 60:
            return True
        if not content:
            return False
        if content.startswith(summary) and len(summary) < 240:
            return True
        if summary in content and len(summary) <= max(80, int(len(content) * 0.18)):
            return True
        return False

    def _build_content_excerpt(self, *, content: str, max_chars: int) -> str:
        if not content:
            return ""
        if len(content) <= max_chars:
            return content

        head_chars = int(max_chars * 0.65)
        tail_chars = max(40, max_chars - head_chars - 5)
        return f"{content[:head_chars]} ... {content[-tail_chars:]}"

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _build_source_pattern_pack_digest(self, source_pattern_pack: Optional[dict[str, Any]]) -> str:
        return render_source_pattern_pack_digest(
            source_pattern_pack,
            empty_message="(no public source pattern pack; use only source text and chapter analysis.)",
        )

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "world_rules": self._as_dict(payload.get("world_rules")),
            "character_cards": self._as_dict_list(payload.get("character_cards")),
            "organizations": self._as_dict_list(payload.get("organizations")),
            "timeline": self._as_dict_list(payload.get("timeline")),
            "story_arcs": self._as_dict_list(payload.get("story_arcs")),
            "foreshadows": self._as_dict_list(payload.get("foreshadows")),
            "style_signature": self._as_dict(payload.get("style_signature")),
            "hard_constraints": self._as_dict_list(payload.get("hard_constraints")),
            "conflicts": self._as_dict_list(payload.get("conflicts")),
            "generation_notes": self._as_note_list(payload.get("generation_notes")),
            "chapter_change_packages": self._as_dict_list(payload.get("chapter_change_packages")),
        }

    @classmethod
    def backfill_missing_sections(
        cls,
        *,
        project: Project,
        payload: dict[str, Any],
        source_chapters: list[BookImportChapter],
        analysis_snapshots: Optional[list[dict[str, Any]]] = None,
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        helper = cls.__new__(cls)
        analysis_snapshots = analysis_snapshots or []

        if not payload.get("timeline"):
            payload["timeline"] = helper._build_fallback_timeline(
                source_chapters=source_chapters,
                analysis_snapshots=analysis_snapshots,
            )
        if not payload.get("foreshadows"):
            payload["foreshadows"] = helper._build_fallback_foreshadows(
                source_chapters=source_chapters,
                analysis_snapshots=analysis_snapshots,
            )
        if not payload.get("hard_constraints"):
            payload["hard_constraints"] = helper._build_fallback_hard_constraints(
                project=project,
                character_cards=helper._as_dict_list(payload.get("character_cards")),
                story_arcs=helper._as_dict_list(payload.get("story_arcs")),
                timeline=helper._as_dict_list(payload.get("timeline")),
                foreshadows=helper._as_dict_list(payload.get("foreshadows")),
                analysis_snapshots=analysis_snapshots,
            )
        if not payload.get("style_signature"):
            payload["style_signature"] = helper._build_fallback_style_signature(
                project=project,
                source_chapters=source_chapters,
                analysis_snapshots=analysis_snapshots,
                source_pattern_pack=source_pattern_pack,
            )
        return payload

    def _build_analysis_digest(self, analysis_snapshots: list[dict[str, Any]]) -> str:
        if not analysis_snapshots:
            return "（当前暂无章节分析结果，可直接依据原文摘录生成草稿）"

        lines: list[str] = []
        for snapshot in analysis_snapshots[:12]:
            chapter_number = snapshot.get("chapter_number")
            title = snapshot.get("title") or f"第{chapter_number}章"
            plot_points = self._as_dict_list(snapshot.get("plot_points"))
            foreshadows = self._as_dict_list(snapshot.get("foreshadows"))
            character_states = self._as_dict_list(snapshot.get("character_states"))
            lines.append(f"- 第{chapter_number}章《{title}》")
            if plot_points:
                lines.append(f"  - 关键情节点：{self._item_to_text(plot_points[0], preferred_keys=('content', 'summary', 'impact'))}")
            if foreshadows:
                lines.append(f"  - 伏笔线索：{self._item_to_text(foreshadows[0], preferred_keys=('content', 'hook', 'summary'))}")
            if character_states:
                lines.append(f"  - 人物状态：{self._item_to_text(character_states[0], preferred_keys=('character_name', 'state_after', 'psychological_change'))}")
        return "\n".join(lines)

    def _build_fallback_timeline(
        self,
        *,
        source_chapters: list[BookImportChapter],
        analysis_snapshots: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        seen_chapters: set[int] = set()

        for snapshot in analysis_snapshots:
            chapter_number = int(snapshot.get("chapter_number") or 0)
            if chapter_number <= 0 or chapter_number in seen_chapters:
                continue
            summary = self._normalize_text(str(snapshot.get("summary") or ""))
            plot_points = self._as_dict_list(snapshot.get("plot_points"))
            event = summary
            if plot_points:
                event = self._item_to_text(plot_points[0], preferred_keys=("content", "summary", "impact"))
            if event:
                entries.append({"chapter": chapter_number, "event": event[:160]})
                seen_chapters.add(chapter_number)
            if len(entries) >= 12:
                break

        if entries:
            return entries

        selected = self._select_source_window(source_chapters, max_chapters=10, head_size=3, tail_size=3)
        for chapter, _segment in selected:
            event = self._normalize_text(chapter.summary or "") or self._build_content_excerpt(
                content=self._normalize_text(chapter.content or ""),
                max_chars=120,
            )
            if not event:
                continue
            entries.append({"chapter": chapter.chapter_number, "event": event[:160]})

        return entries

    def _build_fallback_foreshadows(
        self,
        *,
        source_chapters: list[BookImportChapter],
        analysis_snapshots: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        hooks: list[dict[str, Any]] = []
        seen_texts: set[str] = set()

        for snapshot in analysis_snapshots:
            chapter_number = int(snapshot.get("chapter_number") or 0)
            for foreshadow in self._as_dict_list(snapshot.get("foreshadows")):
                foreshadow_type = str(foreshadow.get("type") or "").strip().lower()
                if foreshadow_type == "resolved":
                    continue
                text = self._item_to_text(foreshadow, preferred_keys=("content", "hook", "summary", "impact")).strip()
                if not text or text in seen_texts:
                    continue
                hooks.append({
                    "hook": text[:180],
                    "source_chapter": chapter_number,
                    "status": "open",
                })
                seen_texts.add(text)
                if len(hooks) >= 10:
                    return hooks

        if hooks:
            return hooks

        for chapter, segment in self._select_source_window(source_chapters, max_chapters=6, head_size=1, tail_size=3):
            summary = self._normalize_text(chapter.summary or "")
            excerpt = self._build_content_excerpt(
                content=self._normalize_text(chapter.content or ""),
                max_chars=90,
            )
            text = summary or excerpt
            if not text:
                continue
            hint = f"第{chapter.chapter_number}章（{segment}）后续需承接：{text[:120]}"
            if hint in seen_texts:
                continue
            hooks.append({
                "hook": hint,
                "source_chapter": chapter.chapter_number,
                "status": "open",
            })
            seen_texts.add(hint)
            if len(hooks) >= 6:
                break

        return hooks

    def _build_fallback_hard_constraints(
        self,
        *,
        project: Project,
        character_cards: list[dict[str, Any]],
        story_arcs: list[dict[str, Any]],
        timeline: list[dict[str, Any]],
        foreshadows: list[dict[str, Any]],
        analysis_snapshots: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        rules: list[dict[str, Any]] = []
        protagonist = character_cards[0] if character_cards else {}
        protagonist_name = str(protagonist.get("name") or "主角").strip()
        protagonist_core = (
            protagonist.get("核心冲突")
            or protagonist.get("core_conflict")
            or protagonist.get("description")
            or protagonist.get("arc")
            or ""
        )
        if protagonist_core:
            rules.append({
                "rule": f"续写必须保持{protagonist_name}当前的核心冲突与行为逻辑，不能突然写成与前文完全相反的人。",
                "source": "character_cards",
            })
        if story_arcs:
            arc_name = self._item_to_text(story_arcs[0], preferred_keys=("名称", "name", "title", "主线"))
            if arc_name:
                rules.append({
                    "rule": f"当前主线应继续承接“{arc_name}”，不要另起炉灶把原书核心矛盾抛掉。",
                    "source": "story_arcs",
                })
        if timeline:
            rules.append({
                "rule": "必须沿已发生的时间线与关键事件顺序推进，不得篡改章节先后与重大节点因果。",
                "source": "timeline",
            })
        if foreshadows:
            rules.append({
                "rule": "已列出的未回收伏笔必须在后续计划中持续承接，不能写着写着集体失忆。",
                "source": "foreshadows",
            })
        if analysis_snapshots:
            rules.append({
                "rule": "续写时应优先延续已有情绪尾音、关系张力与章节承接义务，而不是只做泛化爽点推进。",
                "source": "analysis",
            })
        if not rules:
            rules.append({
                "rule": f"续写《{project.title}》时必须优先保持原书人物、时间线与主线推进的一致性。",
                "source": "fallback",
            })
        return rules[:6]

    def _build_fallback_style_signature(
        self,
        *,
        project: Project,
        source_chapters: list[BookImportChapter],
        analysis_snapshots: list[dict[str, Any]],
        source_pattern_pack: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Build a compact style signature when the model omits one."""
        valid_chapters = [chapter for chapter in source_chapters if (chapter.content or "").strip()]
        selected = [chapter for chapter, _segment in self._select_source_window(valid_chapters, max_chapters=8, head_size=2, tail_size=3)]
        if not selected:
            selected = valid_chapters[:8]

        source_text = " ".join(
            self._normalize_text(chapter.content or "")
            for chapter in selected
            if (chapter.content or "").strip()
        )
        sentence_lengths = self._sentence_lengths(source_text)
        average_sentence_length = round(sum(sentence_lengths) / max(1, len(sentence_lengths)), 2)
        dialogue_density = self._estimate_dialogue_density(source_text)
        style_hints = self._source_pattern_hints(source_pattern_pack, "style_signature_hints")
        fidelity_hints = self._source_pattern_hints(source_pattern_pack, "style_fidelity_hints")

        return {
            "source": "fallback_source_text",
            "narrative_perspective": (project.narrative_perspective or "以原书正文已呈现视角为准"),
            "sentence_rhythm": {
                "average_sentence_length": average_sentence_length,
                "sample_count": len(sentence_lengths),
                "label": self._sentence_rhythm_label(average_sentence_length),
            },
            "dialogue_density": dialogue_density,
            "dialogue_density_label": self._dialogue_density_label(dialogue_density),
            "emotional_temperature": self._fallback_emotional_temperature(analysis_snapshots),
            "style_signature_hints": style_hints[:4],
            "style_fidelity_hints": fidelity_hints[:4],
            "continuation_requirements": [
                "Preserve original voice, cadence, POV behavior, and narrative temperature.",
                "Match sentence rhythm, dialogue density, scene density, and emotional pressure before adding new plot.",
                "Treat style fidelity as a hard continuation constraint, not a loose preference.",
            ],
        }

    def _sentence_lengths(self, text: str) -> list[int]:
        parts = re.split(r"[。！？!?；;\.]+", text or "")
        lengths = [len(re.sub(r"\s+", "", part)) for part in parts if part.strip()]
        return [length for length in lengths if length > 0][:120]

    def _estimate_dialogue_density(self, text: str) -> float:
        compact = re.sub(r"\s+", "", text or "")
        if not compact:
            return 0.0
        quote_count = sum((text or "").count(symbol) for symbol in (chr(34), chr(8220), chr(8221), chr(8216), chr(8217), chr(12302), chr(12303), chr(12300), chr(12301)))
        return round(quote_count / max(1, len(compact)), 4)

    @staticmethod
    def _sentence_rhythm_label(average_sentence_length: float) -> str:
        if average_sentence_length <= 18:
            return "short_cadence"
        if average_sentence_length <= 35:
            return "balanced_cadence"
        return "long_cadence"

    @staticmethod
    def _dialogue_density_label(dialogue_density: float) -> str:
        if dialogue_density >= 0.025:
            return "dialogue_forward"
        if dialogue_density >= 0.01:
            return "balanced_dialogue"
        return "narration_forward"

    def _fallback_emotional_temperature(self, analysis_snapshots: list[dict[str, Any]]) -> str:
        tones: list[str] = []
        intensities: list[int] = []
        for snapshot in analysis_snapshots[:12]:
            tone = str(snapshot.get("emotional_tone") or snapshot.get("tone") or "").strip()
            if tone:
                tones.append(tone)
            try:
                intensity = int(snapshot.get("emotional_intensity") or 0)
            except (TypeError, ValueError):
                intensity = 0
            if intensity > 0:
                intensities.append(intensity)
        if tones and intensities:
            avg_intensity = round(sum(intensities) / len(intensities), 2)
            return f"{'; '.join(self._unique_notes(tones, limit=4))}; average_intensity={avg_intensity}"
        if tones:
            return "; ".join(self._unique_notes(tones, limit=4))
        if intensities:
            avg_intensity = round(sum(intensities) / len(intensities), 2)
            return f"average_intensity={avg_intensity}"
        return "derived from source chapter excerpts"

    def _source_pattern_hints(self, source_pattern_pack: Optional[dict[str, Any]], key: str) -> list[str]:
        if not isinstance(source_pattern_pack, dict):
            return []
        return self._as_note_list(source_pattern_pack.get(key))

    def _unique_notes(self, values: list[str], *, limit: int) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            text = str(value).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            result.append(text)
            if len(result) >= limit:
                break
        return result


    def _backfill_empty_sections(
        self,
        *,
        project: Project,
        payload: dict[str, Any],
        source_chapters: list[BookImportChapter],
        analysis_snapshots: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not payload.get("timeline"):
            payload["timeline"] = self._build_fallback_timeline(
                source_chapters=source_chapters,
                analysis_snapshots=analysis_snapshots,
            )
        if not payload.get("foreshadows"):
            payload["foreshadows"] = self._build_fallback_foreshadows(
                source_chapters=source_chapters,
                analysis_snapshots=analysis_snapshots,
            )
        if not payload.get("hard_constraints"):
            payload["hard_constraints"] = self._build_fallback_hard_constraints(
                project=project,
                character_cards=payload.get("character_cards") or [],
                story_arcs=payload.get("story_arcs") or [],
                timeline=payload.get("timeline") or [],
                foreshadows=payload.get("foreshadows") or [],
                analysis_snapshots=analysis_snapshots,
            )
        if not payload.get("style_signature"):
            payload["style_signature"] = self._build_fallback_style_signature(
                project=project,
                source_chapters=source_chapters,
                analysis_snapshots=analysis_snapshots,
            )
        return payload

    def _build_analysis_digest(self, analysis_snapshots: list[dict[str, Any]]) -> str:
        if not analysis_snapshots:
            return "（当前暂无章节分析结果，可直接依据原文摘录生成草稿）"

        lines: list[str] = []
        for snapshot in analysis_snapshots[:12]:
            chapter_number = snapshot.get("chapter_number")
            title = snapshot.get("title") or f"第{chapter_number}章"
            plot_points = self._as_dict_list(snapshot.get("plot_points"))
            foreshadows = self._as_dict_list(snapshot.get("foreshadows"))
            character_states = self._as_dict_list(snapshot.get("character_states"))
            lines.append(f"- 第{chapter_number}章《{title}》")
            if plot_points:
                lines.append(f"  - 关键情节点：{self._item_to_text(plot_points[0], preferred_keys=('content', 'summary', 'impact'))}")
            if foreshadows:
                lines.append(f"  - 伏笔线索：{self._item_to_text(foreshadows[0], preferred_keys=('content', 'hook', 'summary'))}")
            if character_states:
                lines.append(f"  - 人物状态：{self._item_to_text(character_states[0], preferred_keys=('character_name', 'state_after', 'psychological_change'))}")
        return "\n".join(lines)

    def _build_fallback_timeline(
        self,
        *,
        source_chapters: list[BookImportChapter],
        analysis_snapshots: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        seen_chapters: set[int] = set()

        for snapshot in analysis_snapshots:
            chapter_number = int(snapshot.get("chapter_number") or 0)
            if chapter_number <= 0 or chapter_number in seen_chapters:
                continue
            summary = str(snapshot.get("summary") or "").strip()
            plot_points = self._as_dict_list(snapshot.get("plot_points"))
            event = summary
            if plot_points:
                event = self._item_to_text(plot_points[0], preferred_keys=("content", "summary", "impact"))
            if event:
                entries.append({"chapter": chapter_number, "event": event[:160]})
                seen_chapters.add(chapter_number)
            if len(entries) >= 12:
                break

        if entries:
            return entries

        selected = self._select_source_window(source_chapters, max_chapters=10, head_size=3, tail_size=3)
        for chapter, _segment in selected:
            event = self._normalize_text(chapter.summary or "") or self._build_content_excerpt(
                content=self._normalize_text(chapter.content or ""),
                max_chars=120,
            )
            if not event:
                continue
            entries.append({"chapter": chapter.chapter_number, "event": event[:160]})

        return entries

    def _build_fallback_foreshadows(
        self,
        *,
        source_chapters: list[BookImportChapter],
        analysis_snapshots: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        hooks: list[dict[str, Any]] = []
        seen_texts: set[str] = set()

        for snapshot in analysis_snapshots:
            chapter_number = int(snapshot.get("chapter_number") or 0)
            for foreshadow in self._as_dict_list(snapshot.get("foreshadows")):
                foreshadow_type = str(foreshadow.get("type") or "").strip().lower()
                if foreshadow_type == "resolved":
                    continue
                text = self._item_to_text(foreshadow, preferred_keys=("content", "hook", "summary", "impact")).strip()
                if not text or text in seen_texts:
                    continue
                hooks.append({
                    "hook": text[:180],
                    "source_chapter": chapter_number,
                    "status": "open",
                })
                seen_texts.add(text)
                if len(hooks) >= 10:
                    return hooks

        if hooks:
            return hooks

        for chapter, segment in self._select_source_window(source_chapters, max_chapters=6, head_size=1, tail_size=3):
            summary = self._normalize_text(chapter.summary or "")
            excerpt = self._build_content_excerpt(
                content=self._normalize_text(chapter.content or ""),
                max_chars=90,
            )
            text = summary or excerpt
            if not text:
                continue
            hint = f"第{chapter.chapter_number}章（{segment}）后续需承接：{text[:120]}"
            if hint in seen_texts:
                continue
            hooks.append({
                "hook": hint,
                "source_chapter": chapter.chapter_number,
                "status": "open",
            })
            seen_texts.add(hint)
            if len(hooks) >= 6:
                break

        return hooks

    def _build_fallback_hard_constraints(
        self,
        *,
        project: Project,
        character_cards: list[dict[str, Any]],
        story_arcs: list[dict[str, Any]],
        timeline: list[dict[str, Any]],
        foreshadows: list[dict[str, Any]],
        analysis_snapshots: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        rules: list[dict[str, Any]] = []
        protagonist = character_cards[0] if character_cards else {}
        protagonist_name = str(protagonist.get("name") or "主角").strip()
        protagonist_core = (
            protagonist.get("核心冲突")
            or protagonist.get("core_conflict")
            or protagonist.get("description")
            or protagonist.get("arc")
            or ""
        )
        if protagonist_core:
            rules.append({
                "rule": f"续写必须保持{protagonist_name}当前的核心冲突与行为逻辑，不能突然写成与前文完全相反的人。",
                "source": "character_cards",
            })
        if story_arcs:
            arc_name = self._item_to_text(story_arcs[0], preferred_keys=("名称", "name", "title", "主线"))
            if arc_name:
                rules.append({
                    "rule": f"当前主线应继续承接“{arc_name}”，不要另起炉灶把原书核心矛盾抛掉。",
                    "source": "story_arcs",
                })
        if timeline:
            rules.append({
                "rule": "必须沿已发生的时间线与关键事件顺序推进，不得篡改章节先后与重大节点因果。",
                "source": "timeline",
            })
        if foreshadows:
            rules.append({
                "rule": "已列出的未回收伏笔必须在后续计划中持续承接，不能写着写着集体失忆。",
                "source": "foreshadows",
            })
        if analysis_snapshots:
            rules.append({
                "rule": "续写时应优先延续已有情绪尾音、关系张力与章节承接义务，而不是只做泛化爽点推进。",
                "source": "analysis",
            })
        if not rules:
            rules.append({
                "rule": f"续写《{project.title}》时必须优先保持原书人物、时间线与主线推进的一致性。",
                "source": "fallback",
            })
        return rules[:6]

    def _as_dict(self, value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _as_dict_list(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    def _as_list(self, value: Any) -> list[Any]:
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return []

    def _as_note_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        notes: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                notes.append(text)
        return notes

    def _item_to_text(self, item: dict[str, Any], *, preferred_keys: tuple[str, ...]) -> str:
        for key in preferred_keys:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return self._normalize_text(value)
        compact = json.dumps(item, ensure_ascii=False, sort_keys=True)
        return compact[:220]

    def _item_to_text(self, item: dict[str, Any], *, preferred_keys: tuple[str, ...]) -> str:
        for key in preferred_keys:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return self._normalize_text(value)
        compact = json.dumps(item, ensure_ascii=False, sort_keys=True)
        return compact[:220]

    def _empty_payload(self) -> dict[str, Any]:
        return {
            "world_rules": {},
            "character_cards": [],
            "organizations": [],
            "timeline": [],
            "story_arcs": [],
            "foreshadows": [],
            "style_signature": {},
            "hard_constraints": [],
            "conflicts": [],
            "generation_notes": [],
            "chapter_change_packages": [],
        }
