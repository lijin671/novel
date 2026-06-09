from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Awaitable, Callable, Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OriginalChapterWriter = Callable[[int, dict[str, Any], int], str]
OriginalAsyncChapterWriter = Callable[[int, dict[str, Any], int], Awaitable[str]]
OriginalSkipHook = Callable[[int, str], None]


def compact_word_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text or ""))


def chapter_path(output_dir: Path, chapter_number: int) -> Path:
    return output_dir / f"chapter_{chapter_number:04d}.txt"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_original_bible(artifact_dir: Path) -> dict[str, Any]:
    return _read_json(artifact_dir / "rainseason_bible.json")


def load_original_outline(artifact_dir: Path) -> dict[str, Any]:
    return _read_json(artifact_dir / "outline_001_1000.json")


def load_chapter_title_overrides(artifact_dir: Path) -> dict[int, str]:
    path = artifact_dir / "chapter_title_overrides_001_1000.json"
    if not path.exists():
        return {}
    data = _read_json(path)
    raw_titles = data.get("titles") if isinstance(data, dict) else None
    if not isinstance(raw_titles, dict):
        return {}
    overrides: dict[int, str] = {}
    for key, value in raw_titles.items():
        title = str(value).strip()
        if not title:
            continue
        overrides[int(key)] = title
    return overrides


def _normalize_chapter_numbers(chapter_numbers: Iterable[int] | None, outline: dict[str, Any]) -> list[int]:
    total = int(outline.get("target_total_chapters") or 1000)
    if chapter_numbers is None:
        return list(range(1, total + 1))
    numbers = [int(number) for number in chapter_numbers]
    for number in numbers:
        if number < 1 or number > total:
            raise ValueError(f"章节号必须在 1-{total} 之间: {number}")
    return numbers


def build_original_chapter_plan(chapter_number: int, artifact_dir: Path) -> dict[str, Any]:
    bible = load_original_bible(artifact_dir)
    outline = load_original_outline(artifact_dir)
    chapters = {int(item["chapter_number"]): item for item in outline.get("chapters") or []}
    if chapter_number not in chapters:
        raise ValueError(f"章节规划不存在: {chapter_number}")
    chapter = chapters[chapter_number]
    title_override = load_chapter_title_overrides(artifact_dir).get(chapter_number)
    if title_override:
        chapter = {**chapter, "title": title_override}
    return {
        **chapter,
        "project_title": str(outline.get("title") or bible.get("title") or ""),
        "target_total_chapters": int(outline.get("target_total_chapters") or 1000),
        "target_words_per_chapter": int(outline.get("target_words_per_chapter") or 10000),
        "protagonist": bible.get("protagonist") or {},
        "core_characters": bible.get("core_characters") or [],
        "relationship_design": bible.get("relationship_design") or {},
        "style_signature": bible.get("style_signature") or {},
        "hard_constraints": bible.get("hard_constraints") or [],
        "copyright_boundary": bible.get("copyright_boundary") or {},
        "world_rules": bible.get("world_rules") or [],
    }


def _build_previous_chapter_bridge(previous_text: str | None) -> str:
    if not previous_text:
        return "第0章前置：林知夏尚未抵达首尔，故事从她进入半岛练习生体系开始。"
    compact = re.sub(r"\s+", " ", previous_text).strip()
    return f"上一章生成正文片段：{compact[-1200:]}"


def _load_existing_previous_chapter_text(output_dir: Path, chapter_number: int) -> str | None:
    if chapter_number <= 1:
        return None
    path = chapter_path(output_dir, chapter_number - 1)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _calculate_generation_max_tokens(target_word_count: int) -> int:
    normalized_target = max(1, int(target_word_count or 3000))
    return max(2000, min(int(normalized_target * 3), 32000))


def _join_list(items: Iterable[Any], limit: int = 20) -> str:
    values = [str(item) for item in items if str(item).strip()]
    return "\n".join(f"- {item}" for item in values[:limit])


def _character_digest(characters: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for item in characters[:12]:
        name = str(item.get("name") or "")
        identity = str(item.get("identity") or "")
        boundary = str(item.get("role_boundary") or item.get("relationship_to_rina") or "")
        if name:
            lines.append(f"- {name}：{identity}；边界/作用：{boundary}")
    return "\n".join(lines)


def _build_original_novel_ai_prompt(
    *,
    chapter_number: int,
    plan: dict[str, Any],
    target_word_count: int,
    previous_chapter_bridge: str | None = None,
) -> str:
    protagonist = plan.get("protagonist") or {}
    style = plan.get("style_signature") or {}
    copyright_boundary = plan.get("copyright_boundary") or {}
    relationship = plan.get("relationship_design") or {}
    return f"""你正在创作原创韩娱长篇小说《{plan.get('project_title', '')}》。

请撰写第{chapter_number}章正文。

硬性目标：
- 目标字数：{target_word_count}字以上。
- 只输出正文，不输出解释、注释、审稿意见或元信息。
- 使用第三人称贴近主角视角。
- 主角是{protagonist.get('name_cn', '林知夏')} / {protagonist.get('stage_name', 'Rina')}，这是同一个人。
- 本书只吸收类型结构、事业线节奏、情绪推进方式和现实韩娱公开时间线；不得复制参考小说原文、专属剧情和独特表达。
- 真实艺人只写公开职业关系、同伴关系、舞台关系；不要编造私密恋情或负面丑闻。
- 主情感线由虚构成年人物韩书允承接，未成年阶段不写性化和恋爱推进。

上一章承接：
{previous_chapter_bridge or _build_previous_chapter_bridge(None)}

本章标题：
{plan.get('title', '')}

本章阶段：
{plan.get('stage', '')}｜{plan.get('time_window', '')}

本章摘要：
{plan.get('summary', '')}

事业节点：
{plan.get('career_beat', '')}

情感节点：
{plan.get('relationship_beat', '')}

本章冲突：
{plan.get('conflict', '')}

本章意象：
{plan.get('motif', '')}

世界规则：
{_join_list(plan.get('world_rules') or [])}

人物与边界：
{_character_digest(plan.get('core_characters') or [])}

情感线设计：
- 主线：{relationship.get('main_emotional_line', '')}
{_join_list(relationship.get('tension_rules') or [])}

文风锚点：
- 叙事视角：{style.get('narrative_pov', '')}
- 句式节奏：{style.get('sentence_rhythm', '')}
- 对话密度：{style.get('dialogue_density_target', '')}
- 情绪温度：{style.get('emotional_temperature', '')}
- 职业质感：{style.get('career_texture', '')}
- 收尾习惯：{style.get('chapter_ending_habit', '')}

合规边界：
- {copyright_boundary.get('mode', '')}
{_join_list(copyright_boundary.get('blocked') or [])}

硬约束：
{_join_list(plan.get('hard_constraints') or [])}

正文写法：
- 用场景、动作、对白、心理反应、日程细节推进，不要总结腔。
- 每章只推进一个主要现实节点或一个主要关系节点。
- 歌曲、组合、舞台资源可以架空，但不得覆盖现实团体公开节点。
- 保留温柔克制、舞台事业线、群像互动和暧昧拉扯的类型味道。
"""


async def _call_ai_text(
    *,
    ai_service: Any,
    prompt: str,
    target_word_count: int,
    model: str | None = None,
    max_attempts: int = 1,
    retry_delay_seconds: float = 0.0,
) -> str:
    kwargs: dict[str, Any] = {
        "prompt": prompt,
        "max_tokens": _calculate_generation_max_tokens(target_word_count),
        "auto_mcp": False,
        "handle_tool_calls": False,
    }
    if model:
        kwargs["model"] = model
    last_error: Exception | None = None
    for attempt in range(1, max(1, int(max_attempts or 1)) + 1):
        try:
            response = await ai_service.generate_text(**kwargs)
            if isinstance(response, dict):
                return str(response.get("content") or "").strip()
            return str(response or "").strip()
        except Exception as exc:
            last_error = exc
            if attempt >= max(1, int(max_attempts or 1)):
                break
            if retry_delay_seconds > 0:
                await asyncio.sleep(retry_delay_seconds)
    assert last_error is not None
    raise last_error


async def generate_original_ai_chapter_text(
    *,
    ai_service: Any,
    chapter_number: int,
    plan: dict[str, Any],
    target_word_count: int = 10000,
    previous_chapter_bridge: str | None = None,
    model: str | None = None,
    max_attempts_per_segment: int = 1,
    retry_delay_seconds: float = 0.0,
) -> str:
    prompt = _build_original_novel_ai_prompt(
        chapter_number=chapter_number,
        plan=plan,
        target_word_count=target_word_count,
        previous_chapter_bridge=previous_chapter_bridge,
    )
    return await _call_ai_text(
        ai_service=ai_service,
        prompt=prompt,
        target_word_count=target_word_count,
        model=model,
        max_attempts=max_attempts_per_segment,
        retry_delay_seconds=retry_delay_seconds,
    )


def _build_continuation_prompt(*, chapter_number: int, plan: dict[str, Any], target_word_count: int, current_text: str) -> str:
    remaining_words = max(1, target_word_count - compact_word_count(current_text))
    current_tail = re.sub(r"\s+", " ", current_text or "").strip()[-1500:]
    return f"""继续第{chapter_number}章正文。

当前正文还没有达到目标字数，需要补写至少{remaining_words}字。

已写出的结尾：
{current_tail}

续写要求：
- 从上面结尾自然接下去，不要重复已经写过的段落。
- 继续保持本章标题：{plan.get('title', '')}
- 继续推进本章摘要：{plan.get('summary', '')}
- 主角是林知夏 / Rina，同一个人。
- 韩书允是虚构成年人物，承接主情感线。
- 真实艺人只写公开职业关系、同伴关系、舞台关系。
- 只输出补写正文，不输出标题、大纲、解释或元信息。
"""


async def _generate_ai_chapter_until_target(
    *,
    ai_service: Any,
    chapter_number: int,
    plan: dict[str, Any],
    target_word_count: int,
    previous_chapter_bridge: str,
    model: str | None = None,
    max_segments: int = 4,
    max_attempts_per_segment: int = 1,
    retry_delay_seconds: float = 0.0,
) -> str:
    text = await generate_original_ai_chapter_text(
        ai_service=ai_service,
        chapter_number=chapter_number,
        plan=plan,
        target_word_count=target_word_count,
        previous_chapter_bridge=previous_chapter_bridge,
        model=model,
        max_attempts_per_segment=max_attempts_per_segment,
        retry_delay_seconds=retry_delay_seconds,
    )
    while compact_word_count(text) < target_word_count and max_segments > 1:
        max_segments -= 1
        segment = await _call_ai_text(
            ai_service=ai_service,
            prompt=_build_continuation_prompt(
                chapter_number=chapter_number,
                plan=plan,
                target_word_count=target_word_count,
                current_text=text,
            ),
            target_word_count=target_word_count - compact_word_count(text),
            model=model,
            max_attempts=max_attempts_per_segment,
            retry_delay_seconds=retry_delay_seconds,
        )
        if not segment:
            break
        text = f"{text.rstrip()}\n\n{segment.strip()}"
    return text


def _forbidden_terms() -> list[str]:
    return [
        "杨翠",
        "Rene",
        "公开恋情",
        "官宣恋情",
        "林知夏加入IVE",
        "Rina加入IVE",
        "林知夏成为IVE成员",
        "Rina成为IVE成员",
        "林知夏加入LE SSERAFIM",
        "Rina加入LE SSERAFIM",
        "林知夏成为LE SSERAFIM成员",
        "Rina成为LE SSERAFIM成员",
        "林知夏加入aespa",
        "Rina加入aespa",
    ]


def _required_terms_for_chapter(plan: dict[str, Any]) -> list[str]:
    terms = ["林知夏", "Rina"]
    chapter_number = int(plan.get("chapter_number") or 0)
    if 51 <= chapter_number <= 450:
        terms.append("Aurora*One")
    if chapter_number >= 451:
        terms.append("韩书允")
    return list(dict.fromkeys(terms))


def required_term_present(term: str, text: str) -> bool:
    aliases = {
        "Rina": ["Rina", "林知夏"],
        "Aurora*One": ["Aurora*One", "Aurora", "限定团", "出道组", "预备团", "企划团"],
        "韩书允": ["韩书允", "书允"],
    }.get(term, [term])
    return any(alias in text for alias in aliases)


def audit_original_chapter(*, artifact_dir: Path, output_dir: Path, chapter_number: int, required_word_count: int) -> dict[str, Any]:
    path = chapter_path(output_dir, chapter_number)
    if not path.exists():
        return {
            "chapter_number": chapter_number,
            "path": str(path),
            "passed": False,
            "reasons": ["missing_file"],
            "word_count": 0,
            "missing_terms": [],
            "forbidden_hits": [],
        }
    text = path.read_text(encoding="utf-8")
    compact = re.sub(r"\s+", "", text)
    word_count = compact_word_count(text)
    plan = build_original_chapter_plan(chapter_number, artifact_dir)
    required_terms = _required_terms_for_chapter(plan)
    missing_terms = [term for term in required_terms if not required_term_present(term, text)]
    forbidden_hits = [term for term in _forbidden_terms() if term in compact]
    reasons: list[str] = []
    if word_count < required_word_count:
        reasons.append("short_chapter")
    if missing_terms:
        reasons.append("missing_required_terms")
    if forbidden_hits:
        reasons.append("forbidden_terms")
    return {
        "chapter_number": chapter_number,
        "path": str(path),
        "passed": not reasons,
        "reasons": reasons,
        "word_count": word_count,
        "required_word_count": required_word_count,
        "required_terms": required_terms,
        "missing_terms": missing_terms,
        "forbidden_hits": forbidden_hits,
        "stage": plan.get("stage"),
    }


def audit_original_novel_pack(
    *,
    artifact_dir: Path,
    output_dir: Path,
    start_chapter: int = 1,
    end_chapter: int = 1000,
    required_word_count: int = 10000,
) -> dict[str, Any]:
    chapters = [
        audit_original_chapter(
            artifact_dir=artifact_dir,
            output_dir=output_dir,
            chapter_number=number,
            required_word_count=required_word_count,
        )
        for number in range(start_chapter, end_chapter + 1)
    ]
    failed = [item for item in chapters if not item["passed"]]
    report = {
        "type": "original_novel_pack_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "output_dir": str(output_dir),
        "start_chapter": start_chapter,
        "end_chapter": end_chapter,
        "required_word_count": required_word_count,
        "chapter_count": len(chapters),
        "passed": not failed,
        "passed_chapter_count": len(chapters) - len(failed),
        "failed_chapter_count": len(failed),
        "failed_chapters_preview": failed[:20],
        "chapters": chapters,
        "note": "机器门禁：字数、原创主角锚点、阶段锚点、禁止串入旧项目主角/禁用词。",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "original_novel_audit_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["report_path"] = str(report_path)
    return report


def generate_original_novel_full_pack(
    *,
    artifact_dir: Path,
    output_dir: Path,
    writer: OriginalChapterWriter,
    chapter_numbers: Iterable[int] | None = None,
    target_word_count: int = 10000,
    overwrite: bool = False,
    audit_after: bool = True,
    on_skip: OriginalSkipHook | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outline = load_original_outline(artifact_dir)
    numbers = _normalize_chapter_numbers(chapter_numbers, outline)
    generated: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    manifest_chapters: list[dict[str, Any]] = []
    for chapter_number in numbers:
        path = chapter_path(output_dir, chapter_number)
        if path.exists() and not overwrite:
            existing = path.read_text(encoding="utf-8")
            word_count = compact_word_count(existing)
            entry = {"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "status": "skipped_existing"}
            skipped.append(entry)
            manifest_chapters.append(entry)
            if on_skip:
                on_skip(chapter_number, existing)
            continue
        plan = build_original_chapter_plan(chapter_number, artifact_dir)
        text = writer(chapter_number, plan, target_word_count)
        word_count = compact_word_count(text)
        if word_count < target_word_count:
            failed.append({"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "required_word_count": target_word_count, "reason": "short_generated_text"})
            continue
        path.write_text(text, encoding="utf-8")
        entry = {"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "status": "generated"}
        generated.append(entry)
        manifest_chapters.append(entry)
    manifest = {
        "type": "original_novel_full_pack",
        "project_title": str(outline.get("title") or ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "output_dir": str(output_dir),
        "target_total_chapters": int(outline.get("target_total_chapters") or 1000),
        "start_chapter_number": 1,
        "end_chapter_number": int(outline.get("target_total_chapters") or 1000),
        "target_word_count": target_word_count,
        "chapter_count": len(manifest_chapters),
        "generated_chapter_count": len(generated),
        "skipped_existing_chapter_count": len(skipped),
        "failed_chapter_count": len(failed),
        "contains_full_1000_chapter_text": len(numbers) == int(outline.get("target_total_chapters") or 1000) and not failed,
        "chapters": sorted(manifest_chapters, key=lambda item: item["chapter_number"]),
        "failed_chapters": failed,
    }
    manifest_path = output_dir / "full_pack_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = None
    if audit_after:
        audit = audit_original_novel_pack(
            artifact_dir=artifact_dir,
            output_dir=output_dir,
            start_chapter=numbers[0],
            end_chapter=numbers[-1],
            required_word_count=target_word_count,
        )
    return {**manifest, "manifest_path": manifest_path, "audit": audit}


async def generate_original_novel_full_pack_async(
    *,
    artifact_dir: Path,
    output_dir: Path,
    writer: OriginalAsyncChapterWriter,
    chapter_numbers: Iterable[int] | None = None,
    target_word_count: int = 10000,
    overwrite: bool = False,
    audit_after: bool = True,
    on_skip: OriginalSkipHook | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outline = load_original_outline(artifact_dir)
    numbers = _normalize_chapter_numbers(chapter_numbers, outline)
    generated: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    manifest_chapters: list[dict[str, Any]] = []
    for chapter_number in numbers:
        path = chapter_path(output_dir, chapter_number)
        if path.exists() and not overwrite:
            existing = path.read_text(encoding="utf-8")
            word_count = compact_word_count(existing)
            entry = {"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "status": "skipped_existing"}
            skipped.append(entry)
            manifest_chapters.append(entry)
            if on_skip:
                on_skip(chapter_number, existing)
            continue
        plan = build_original_chapter_plan(chapter_number, artifact_dir)
        try:
            text = await writer(chapter_number, plan, target_word_count)
        except Exception as exc:
            failed.append({"chapter_number": chapter_number, "path": str(path), "word_count": 0, "required_word_count": target_word_count, "reason": "writer_error", "error": str(exc)})
            continue
        word_count = compact_word_count(text)
        if word_count < target_word_count:
            failed.append({"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "required_word_count": target_word_count, "reason": "short_generated_text"})
            continue
        path.write_text(text, encoding="utf-8")
        entry = {"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "status": "generated"}
        generated.append(entry)
        manifest_chapters.append(entry)
    manifest = {
        "type": "original_novel_full_pack",
        "project_title": str(outline.get("title") or ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "output_dir": str(output_dir),
        "target_total_chapters": int(outline.get("target_total_chapters") or 1000),
        "start_chapter_number": 1,
        "end_chapter_number": int(outline.get("target_total_chapters") or 1000),
        "target_word_count": target_word_count,
        "chapter_count": len(manifest_chapters),
        "generated_chapter_count": len(generated),
        "skipped_existing_chapter_count": len(skipped),
        "failed_chapter_count": len(failed),
        "contains_full_1000_chapter_text": len(numbers) == int(outline.get("target_total_chapters") or 1000) and not failed,
        "chapters": sorted(manifest_chapters, key=lambda item: item["chapter_number"]),
        "failed_chapters": failed,
    }
    manifest_path = output_dir / "full_pack_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = None
    if audit_after:
        audit = audit_original_novel_pack(
            artifact_dir=artifact_dir,
            output_dir=output_dir,
            start_chapter=numbers[0],
            end_chapter=numbers[-1],
            required_word_count=target_word_count,
        )
    return {**manifest, "manifest_path": manifest_path, "audit": audit}


async def generate_original_novel_full_pack_with_ai(
    *,
    artifact_dir: Path,
    output_dir: Path,
    ai_service: Any,
    chapter_numbers: Iterable[int] | None = None,
    target_word_count: int = 10000,
    overwrite: bool = False,
    audit_after: bool = True,
    model: str | None = None,
    max_segments_per_chapter: int = 4,
    max_attempts_per_segment: int = 1,
    retry_delay_seconds: float = 0.0,
) -> dict[str, Any]:
    previous_text: str | None = None

    async def writer(chapter_number: int, plan: dict[str, Any], required_words: int) -> str:
        nonlocal previous_text
        if previous_text is None:
            previous_text = _load_existing_previous_chapter_text(output_dir, chapter_number)
        text = await _generate_ai_chapter_until_target(
            ai_service=ai_service,
            chapter_number=chapter_number,
            plan=plan,
            target_word_count=required_words,
            previous_chapter_bridge=_build_previous_chapter_bridge(previous_text),
            model=model,
            max_segments=max_segments_per_chapter,
            max_attempts_per_segment=max_attempts_per_segment,
            retry_delay_seconds=retry_delay_seconds,
        )
        previous_text = text
        return text

    def remember_skipped(_chapter_number: int, existing_text: str) -> None:
        nonlocal previous_text
        previous_text = existing_text

    return await generate_original_novel_full_pack_async(
        artifact_dir=artifact_dir,
        output_dir=output_dir,
        writer=writer,
        chapter_numbers=chapter_numbers,
        target_word_count=target_word_count,
        overwrite=overwrite,
        audit_after=audit_after,
        on_skip=remember_skipped,
    )


_HEADING_RE = re.compile(r"^\s*#?\s*第\s*(?P<number>\d+)\s*章\s*(?P<title>[^\n\r]*)")


def _strip_heading(text: str, chapter_number: int) -> str:
    lines = text.splitlines()
    if not lines:
        return ""
    match = _HEADING_RE.match(lines[0])
    if match and int(match.group("number")) == chapter_number:
        return "\n".join(lines[1:]).lstrip()
    return text.strip()


def merge_original_chapters_to_single_txt(
    *,
    artifact_dir: Path,
    output_dir: Path,
    merged_path: Path,
    start_chapter: int = 1,
    end_chapter: int = 1000,
    normalize_headings: bool = False,
) -> dict[str, Any]:
    missing = [number for number in range(start_chapter, end_chapter + 1) if not chapter_path(output_dir, number).exists()]
    if missing:
        raise ValueError(f"缺少章节: {missing[:20]}")
    parts: list[str] = []
    for number in range(start_chapter, end_chapter + 1):
        text = chapter_path(output_dir, number).read_text(encoding="utf-8").strip()
        if normalize_headings:
            plan = build_original_chapter_plan(number, artifact_dir)
            text = f"{plan.get('title', f'第{number}章')}\n\n{_strip_heading(text, number)}".rstrip()
        parts.append(text)
    merged_path.parent.mkdir(parents=True, exist_ok=True)
    merged_path.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    return {"path": str(merged_path), "chapter_count": end_chapter - start_chapter + 1}
