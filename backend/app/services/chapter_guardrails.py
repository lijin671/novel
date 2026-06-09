"""章节生成后的轻量护栏检查服务"""

from dataclasses import dataclass, field
from difflib import SequenceMatcher
import re
from typing import List, Optional, Sequence

from app.services.source_pattern_pack_prompt import render_source_pattern_pack_digest


@dataclass
class ChapterGuardrailViolation:
    """单条护栏违规记录"""

    type: str
    severity: str
    description: str
    position: Optional[int] = None
    context: Optional[str] = None


@dataclass
class ChapterGuardrailResult:
    """护栏检查结果"""

    passed: bool = True
    violations: List[ChapterGuardrailViolation] = field(default_factory=list)

    def add_violation(self, violation: ChapterGuardrailViolation) -> None:
        self.violations.append(violation)
        self.passed = False


class ChapterGuardrails:
    """针对章节生成结果做轻量一致性检查。"""

    OMNISCIENT_CUES = [
        r"与此同时",
        r"另一边",
        r"此时某地",
        r"殊不知",
        r"他并不知道",
        r"她并不知道",
        r"他们并不知道",
        r"在他不知道的地方",
        r"在她不知道的地方",
        r"远在.*的.*正在",
        r"而此刻.*却",
    ]

    INTRO_INDICATORS = [
        r"看见",
        r"看到",
        r"注意到",
        r"发现",
        r"出现",
        r"走来",
        r"走进",
        r"站着",
        r"坐着",
        r"一个.*人",
        r"一位",
        r"陌生",
        r"不认识",
        r"第一次见",
        r"从未见过",
        r"身穿",
        r"穿着",
        r"面容",
        r"身材",
        r"气质",
    ]

    META_PATTERNS = [
        r"^\s*第[0-9一二三四五六七八九十百千]+章",
        r"^\s*章节[0-9一二三四五六七八九十百千]+",
        r"^\s*【?本章",
    ]

    RECAP_CUES = [
        r"接上回",
        r"书接上文",
        r"上一章说到",
        r"上回说到",
    ]

    def __init__(self) -> None:
        self._omniscient_pattern = re.compile("|".join(self.OMNISCIENT_CUES), re.IGNORECASE)
        self._intro_pattern = re.compile("|".join(self.INTRO_INDICATORS), re.IGNORECASE)
        self._meta_pattern = re.compile("|".join(self.META_PATTERNS), re.IGNORECASE)
        self._recap_pattern = re.compile("|".join(self.RECAP_CUES), re.IGNORECASE)

    def check(
        self,
        generated_text: str,
        *,
        chapter_title: Optional[str] = None,
        continuation_point: Optional[str] = None,
        previous_chapter_summary: Optional[str] = None,
        remix_continuation_context: Optional[str] = None,
        inspired_source_excerpts: Optional[Sequence[str]] = None,
        forbidden_characters: Optional[Sequence[str]] = None,
        allowed_new_characters: Optional[Sequence[str]] = None,
    ) -> ChapterGuardrailResult:
        """执行护栏检查。"""
        result = ChapterGuardrailResult()
        text = (generated_text or "").strip()

        if not text:
            result.add_violation(
                ChapterGuardrailViolation(
                    type="empty_output",
                    severity="high",
                    description="章节内容为空",
                )
            )
            return result

        self._check_meta_output(text, chapter_title, result)
        self._check_recap_cues(text, result)
        self._check_omniscient_cues(text, result)
        self._check_repetitive_opening(text, continuation_point, previous_chapter_summary, result)
        self._check_canon_repetition(text, remix_continuation_context, result)
        self._check_inspired_source_copy(text, inspired_source_excerpts, result)

        if forbidden_characters:
            self._check_forbidden_names(text, forbidden_characters, result)
        if allowed_new_characters:
            self._check_character_introduction(text, allowed_new_characters, result)

        return result

    def format_violations_for_prompt(self, result: ChapterGuardrailResult) -> str:
        """将违规列表格式化成可直接喂给修复提示词的文本。"""
        if result.passed:
            return "未检测到违规。"

        lines = ["检测到以下违规，请只修复这些问题："]
        for idx, violation in enumerate(result.violations, start=1):
            lines.append(f"{idx}. [{violation.severity.upper()}] {violation.description}")
            if violation.context:
                lines.append(f"   上下文：{violation.context}")
        return "\n".join(lines)

    def _check_meta_output(
        self,
        text: str,
        chapter_title: Optional[str],
        result: ChapterGuardrailResult,
    ) -> None:
        match = self._meta_pattern.search(text[:80])
        if match:
            result.add_violation(
                ChapterGuardrailViolation(
                    type="meta_output",
                    severity="medium",
                    description=f"开头出现了章节元信息「{match.group()}」",
                    position=match.start(),
                    context=self._extract_context(text, match.start()),
                )
            )

        if chapter_title:
            title = chapter_title.strip()
            title_pos = text[:120].find(title)
            if title and len(title) >= 2 and title_pos >= 0:
                result.add_violation(
                    ChapterGuardrailViolation(
                        type="meta_output",
                        severity="medium",
                        description=f"开头出现了章节标题「{title}」",
                        position=title_pos,
                        context=self._extract_context(text, title_pos),
                    )
                )

    def _check_recap_cues(self, text: str, result: ChapterGuardrailResult) -> None:
        for match in self._recap_pattern.finditer(text[:200]):
            result.add_violation(
                ChapterGuardrailViolation(
                    type="recap_cue",
                    severity="medium",
                    description=f"出现承接套话「{match.group()}」",
                    position=match.start(),
                    context=self._extract_context(text, match.start()),
                )
            )

    def _check_omniscient_cues(self, text: str, result: ChapterGuardrailResult) -> None:
        for match in self._omniscient_pattern.finditer(text):
            result.add_violation(
                ChapterGuardrailViolation(
                    type="omniscient_cue",
                    severity="medium",
                    description=f"出现全知视角提示词「{match.group()}」",
                    position=match.start(),
                    context=self._extract_context(text, match.start()),
                )
            )

    def _check_forbidden_names(
        self,
        text: str,
        forbidden_characters: Sequence[str],
        result: ChapterGuardrailResult,
    ) -> None:
        seen = set()
        separator = r"[\s\-_·•.,，、;；:：!?！？。()（）\[\]【】《》\"'“”‘’]*"
        for raw_name in sorted(set(forbidden_characters), key=len, reverse=True):
            name = (raw_name or "").strip()
            if len(name) < 2:
                continue
            pattern = re.compile(separator.join(re.escape(char) for char in name))
            match = pattern.search(text)
            if not match or name in seen:
                continue
            seen.add(name)
            result.add_violation(
                ChapterGuardrailViolation(
                    type="forbidden_name",
                    severity="high",
                    description=f"出现了当前章节不应正式点名的角色/组织「{name}」",
                    position=match.start(),
                    context=self._extract_context(text, match.start()),
                )
            )

    def _check_character_introduction(
        self,
        text: str,
        allowed_new_characters: Sequence[str],
        result: ChapterGuardrailResult,
    ) -> None:
        for raw_name in allowed_new_characters:
            name = (raw_name or "").strip()
            if len(name) < 2:
                continue
            match = re.search(re.escape(name), text)
            if not match:
                continue
            intro_range = max(0, match.start() - 120)
            intro_text = text[intro_range:match.start()]
            if self._intro_pattern.search(intro_text):
                continue
            result.add_violation(
                ChapterGuardrailViolation(
                    type="sudden_familiarity",
                    severity="medium",
                    description=f"新角色「{name}」首次出现前缺少观察和介绍过程",
                    position=match.start(),
                    context=self._extract_context(text, match.start()),
                )
            )

    def _check_repetitive_opening(
        self,
        text: str,
        continuation_point: Optional[str],
        previous_chapter_summary: Optional[str],
        result: ChapterGuardrailResult,
    ) -> None:
        opening = self._normalize_text(text[:180])
        if len(opening) < 24:
            return

        for source_name, anchor in (
            ("衔接锚点", continuation_point),
            ("上一章摘要", previous_chapter_summary),
        ):
            normalized_anchor = self._normalize_text((anchor or "")[:180])
            if len(normalized_anchor) < 24:
                continue

            ratio = SequenceMatcher(None, opening[:120], normalized_anchor[:120]).ratio()
            if ratio >= 0.72 or opening[:40] == normalized_anchor[:40]:
                result.add_violation(
                    ChapterGuardrailViolation(
                        type="repetitive_opening",
                        severity="medium",
                        description=f"开篇与{source_name}重复度过高，像是在复述上一章内容",
                        position=0,
                        context=text[:120],
                    )
                )
                return

    def _check_canon_repetition(
        self,
        text: str,
        remix_continuation_context: Optional[str],
        result: ChapterGuardrailResult,
    ) -> None:
        canon_context = remix_continuation_context or ""
        if not canon_context.strip():
            return

        repeated_terms = self._canon_done_terms(canon_context)
        if not repeated_terms:
            return

        normalized_text = self._normalize_text(text)
        for term in repeated_terms:
            normalized_term = self._normalize_text(term)
            if len(normalized_term) < 4:
                continue
            if normalized_term not in normalized_text and self._max_window_similarity(normalized_term, normalized_text) < 0.66:
                continue

            result.add_violation(
                ChapterGuardrailViolation(
                    type="canon_repetition",
                    severity="high",
                    description=(
                        f"生成内容疑似重复书写已确认 Canon 中的完成项「{term}」，"
                        "应从该状态之后继续推进，不能回退或重演。"
                    ),
                    position=text.find(term) if term in text else None,
                    context=self._extract_context(text, max(0, text.find(term))) if term in text else text[:120],
                )
            )
            return

    def _check_inspired_source_copy(
        self,
        text: str,
        inspired_source_excerpts: Optional[Sequence[str]],
        result: ChapterGuardrailResult,
    ) -> None:
        if not inspired_source_excerpts:
            return

        normalized_text = self._normalize_text(text)
        if len(normalized_text) < 16:
            return

        for excerpt in inspired_source_excerpts:
            normalized_excerpt = self._normalize_text(excerpt or "")
            if len(normalized_excerpt) < 16:
                continue

            if self._contains_distinctive_substring_copy(normalized_excerpt, normalized_text):
                similarity = 1.0
            elif normalized_excerpt in normalized_text:
                similarity = 1.0
            else:
                similarity = self._max_window_similarity(normalized_excerpt, normalized_text)

            if similarity < 0.82:
                continue

            result.add_violation(
                ChapterGuardrailViolation(
                    type="inspired_source_copy",
                    severity="high",
                    description=(
                        "同类创作草稿疑似照搬源书片段，必须改写为独立表达，"
                        "只保留类型节奏、视角行为和情绪温度。"
                    ),
                    context=(excerpt or "")[:120],
                )
            )
            return

    @staticmethod
    def _contains_distinctive_substring_copy(source_text: str, generated_text: str) -> bool:
        min_span = 16
        if len(source_text) < min_span or len(generated_text) < min_span:
            return False

        for start in range(0, len(source_text) - min_span + 1):
            window = source_text[start:start + min_span]
            if len(set(window)) < 6:
                continue
            if window in generated_text:
                return True
        return False

    def _canon_done_terms(self, remix_continuation_context: str) -> list[str]:
        terms: list[str] = []
        for raw_line in remix_continuation_context.splitlines():
            line = raw_line.strip(" -•	")
            if not line:
                continue
            lower_line = line.lower()
            if not any(marker in lower_line for marker in ("done", "resolved", "已经", "已")):
                continue
            if lower_line.endswith(":"):
                continue
            for term in self._split_canon_line_terms(line):
                cleaned = term.strip(' ：:;；,.，。()（）[]【】《》"')
                if len(self._normalize_text(cleaned)) >= 4 and cleaned not in terms:
                    terms.append(cleaned)
        return terms[:16]

    @staticmethod
    def _max_window_similarity(needle: str, haystack: str) -> float:
        if not needle or not haystack:
            return 0.0
        if len(haystack) <= len(needle):
            return SequenceMatcher(None, needle, haystack).ratio()

        window_size = len(needle)
        step = max(1, window_size // 4)
        best = 0.0
        for start in range(0, len(haystack) - window_size + 1, step):
            window = haystack[start:start + window_size]
            best = max(best, SequenceMatcher(None, needle, window).ratio())
            if best >= 0.66:
                return best
        tail = haystack[-window_size:]
        return max(best, SequenceMatcher(None, needle, tail).ratio())

    @staticmethod
    def _split_canon_line_terms(line: str) -> list[str]:
        cleaned = re.sub(r"^(chapter|ch)\s*\d+\s*[:：-]?\s*", "", line, flags=re.IGNORECASE)
        cleaned = re.sub(r"^第[0-9一二三四五六七八九十百千]+章[《\w\W]*?[》:：]\s*", "", cleaned)
        for separator in (":", "："):
            if separator in cleaned:
                left, right = cleaned.split(separator, 1)
                if any(marker in right.lower() for marker in ("done", "resolved", "已经", "已")) or len(right.strip()) >= 6:
                    cleaned = right
                else:
                    cleaned = left
                break
        cleaned = re.sub(r"\b(status\s*)?[:：]?\s*(done|resolved)\b", "", cleaned, flags=re.IGNORECASE)
        parts = re.split(r"[;；。\n]", cleaned)
        return [part.strip() for part in parts if part.strip()]

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = re.sub(r"\s+", "", text or "")
        return re.sub(r"[，。！？、；：“”‘’\"'《》【】（）()…—\-·,.!?:;]", "", text)

    @staticmethod
    def _extract_context(text: str, pos: int, window: int = 50) -> str:
        start = max(0, pos - window)
        end = min(len(text), pos + window)
        return f"...{text[start:end]}..."


def _format_forbidden_source_names_for_prompt(
    forbidden_characters: Optional[Sequence[str]],
) -> str:
    """把同类创作禁用源书名称格式化为修复提示词中的硬约束。"""
    names: list[str] = []
    for raw_name in forbidden_characters or []:
        name = (raw_name or "").strip()
        if len(name) < 2 or name in names:
            continue
        names.append(name)
        if len(names) >= 24:
            break

    if not names:
        return "暂无源书显性元素禁用清单。"

    return "\n".join(
        [
            "这些源书显性名称不得原样沿用；修复时必须替换为独立人物、组织、能力或设定名称：",
            *(f"- {name}" for name in names),
        ]
    )


async def apply_chapter_guardrail_check(
    *,
    generated_text: str,
    ai_service,
    chapter_number: int,
    chapter_title: str,
    chapter_outline: str,
    target_word_count: int,
    chapter_director_plan: str = "",
    previous_chapter_summary: str = "",
    continuation_point: str = "",
    remix_continuation_context: str = "",
    inspired_source_excerpts: Optional[Sequence[str]] = None,
    source_pattern_pack: Optional[dict] = None,
    forbidden_characters: Optional[Sequence[str]] = None,
    allowed_new_characters: Optional[Sequence[str]] = None,
    max_rewrites: int = 1,
) -> dict:
    """执行生成后 check；失败时只触发一次最小修复。"""
    guardrails = ChapterGuardrails()
    initial_result = guardrails.check(
        generated_text,
        chapter_title=chapter_title,
        continuation_point=continuation_point,
        previous_chapter_summary=previous_chapter_summary,
        remix_continuation_context=remix_continuation_context,
        inspired_source_excerpts=inspired_source_excerpts,
        forbidden_characters=forbidden_characters,
        allowed_new_characters=allowed_new_characters,
    )
    if initial_result.passed:
        return {
            "content": generated_text,
            "applied": False,
            "attempts": 0,
            "initial_result": initial_result,
            "final_result": initial_result,
        }

    content = generated_text
    final_result = initial_result
    attempts = 0

    from app.services.prompt_service import PromptService

    for attempt in range(1, max_rewrites + 1):
        violations_text = guardrails.format_violations_for_prompt(final_result)
        source_pattern_constraints = render_source_pattern_pack_digest(
            source_pattern_pack,
            empty_message="暂无公开来源模式约束",
        )
        forbidden_source_names = _format_forbidden_source_names_for_prompt(forbidden_characters)
        template = await PromptService.get_template_with_fallback("CHAPTER_GUARDRAILS_REWRITE")
        prompt = PromptService.format_prompt(
            template,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            chapter_outline=chapter_outline or "暂无章节规划",
            target_word_count=target_word_count,
            chapter_director_plan=chapter_director_plan or "{}",
            previous_chapter_summary=previous_chapter_summary or "暂无上一章摘要",
            continuation_point=continuation_point or "暂无衔接锚点",
            remix_continuation_context=remix_continuation_context or "暂无已确认 Canon 续写状态",
            source_pattern_constraints=source_pattern_constraints,
            forbidden_source_names=forbidden_source_names,
            violations_text=violations_text,
            original_content=content,
        )
        response = await ai_service.generate_text(
            prompt=prompt,
            temperature=0.25,
            auto_mcp=False,
            handle_tool_calls=False,
        )
        repaired = ""
        if isinstance(response, dict):
            repaired = str(response.get("content") or "").strip()
        else:
            repaired = str(response or "").strip()
        if not repaired:
            break

        attempts = attempt
        content = repaired
        final_result = guardrails.check(
            content,
            chapter_title=chapter_title,
            continuation_point=continuation_point,
            previous_chapter_summary=previous_chapter_summary,
            remix_continuation_context=remix_continuation_context,
            inspired_source_excerpts=inspired_source_excerpts,
            forbidden_characters=forbidden_characters,
            allowed_new_characters=allowed_new_characters,
        )
        if final_result.passed:
            break

    return {
        "content": content,
        "applied": attempts > 0 and content != generated_text,
        "attempts": attempts,
        "initial_result": initial_result,
        "final_result": final_result,
    }
