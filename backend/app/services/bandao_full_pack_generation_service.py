from __future__ import annotations

import asyncio
import json
import re
import shlex
from collections.abc import Awaitable, Callable, Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.bandao_batch_queue_plan import (
    BANDAO_START_CHAPTER,
    BANDAO_TARGET_TOTAL_CHAPTERS,
    build_bandao_chapter_expansion_plan,
)
from app.services.bandao_completion_audit_service import audit_bandao_full_completion
from app.services.bandao_regression_audit_service import audit_chapter as audit_bandao_regression_chapter
from app.services.bandao_regression_audit_service import audit_pack as audit_bandao_regression_pack

BandaoChapterWriter = Callable[[int, dict[str, Any], int], str]
BandaoAsyncChapterWriter = Callable[[int, dict[str, Any], int], Awaitable[str]]
BandaoSkipHook = Callable[[int, str], None]


def _compact_word_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text or ""))


def _chapter_path(output_dir: Path, chapter_number: int) -> Path:
    return output_dir / f"chapter_{chapter_number:04d}.txt"


def _normalize_chapter_numbers(chapter_numbers: Iterable[int] | None) -> list[int]:
    if chapter_numbers is None:
        return list(range(BANDAO_START_CHAPTER, BANDAO_TARGET_TOTAL_CHAPTERS + 1))
    numbers = [int(number) for number in chapter_numbers]
    for number in numbers:
        if number < BANDAO_START_CHAPTER or number > BANDAO_TARGET_TOTAL_CHAPTERS:
            raise ValueError(f"章节号必须在 {BANDAO_START_CHAPTER}-{BANDAO_TARGET_TOTAL_CHAPTERS} 之间: {number}")
    return numbers


def build_bandao_full_pack_ai_run_command(
    *,
    user_id: str,
    output_dir: Path,
    start_chapter: int = BANDAO_START_CHAPTER,
    end_chapter: int = BANDAO_TARGET_TOTAL_CHAPTERS,
    artifact_dir: Path = Path("tmp/book-remix-test-ban-dao-20260530"),
    target_word_count: int = 10000,
    model: str | None = None,
) -> str:
    """返回可复制的半岛 AI full-pack 生成命令。"""
    parts = [
        "python",
        "-m",
        "backend.scripts.generate_bandao_full_pack",
        "--user-id",
        user_id,
        "--artifact-dir",
        str(artifact_dir),
        "--output-dir",
        str(output_dir),
        "--start-chapter",
        str(start_chapter),
        "--end-chapter",
        str(end_chapter),
        "--target-word-count",
        str(target_word_count),
    ]
    if model:
        parts.extend(["--model", model])
    return " ".join(shlex.quote(part) for part in parts)


def _calculate_generation_max_tokens(target_word_count: int) -> int:
    normalized_target = max(1, int(target_word_count or 3000))
    calculated_max_tokens = int(normalized_target * 3)
    return max(2000, min(calculated_max_tokens, 32000))


def _build_previous_chapter_bridge(previous_text: str | None) -> str:
    if not previous_text:
        return "第200章结尾：张元英与杨翠楼梯间秘密亲吻后回宿舍，崔叡娜察觉异常并背过身。"
    compact = re.sub(r"\s+", " ", previous_text).strip()
    return f"上一章生成正文片段：{compact[-1200:]}"


def _load_existing_previous_chapter_text(output_dir: Path, chapter_number: int) -> str | None:
    if chapter_number <= BANDAO_START_CHAPTER:
        return None
    path = _chapter_path(output_dir, chapter_number - 1)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _reality_anchor_dates(reality_constraints: str) -> list[str]:
    dates = re.findall(r"\b\d{4}-\d{2}(?:-\d{2})?\b", reality_constraints or "")
    return list(dict.fromkeys(dates))


def _reality_anchor_block(reality_constraints: str) -> str:
    dates = _reality_anchor_dates(reality_constraints)
    if not dates:
        return ""
    lines = "\n".join(f"- {date}" for date in dates)
    return (
        "必须自然写入以下现实时间锚点（至少出现一次，可作为日程、新闻稿、"
        "回归资料或工作人员口播出现，不要写成说明文字）：\n"
        f"{lines}"
    )


def _existing_chapter_passes_regression(
    *,
    artifact_dir: Path,
    output_dir: Path,
    chapter_number: int,
    target_word_count: int,
) -> bool:
    result = audit_bandao_regression_chapter(
        artifact_dir=artifact_dir,
        output_dir=output_dir,
        chapter_number=chapter_number,
        required_word_count=target_word_count,
    )
    return bool(result.get("passed"))


def _build_bandao_ai_prompt(
    *,
    chapter_number: int,
    plan: dict[str, Any],
    target_word_count: int,
    previous_chapter_bridge: str | None = None,
) -> str:
    focus = "、".join(str(item) for item in plan.get("character_focus") or [])
    guardrails = "\n".join(f"- {rule}" for rule in plan.get("guardrails") or [])
    stage_goals = "\n".join(f"- {goal}" for goal in plan.get("stage_goals") or plan.get("key_events") or [])
    reality_constraints = str(plan.get("reality_timeline_constraints") or "")
    reality_anchor = _reality_anchor_block(reality_constraints)
    return f"""你正在为《混在半岛的日子》做拆书续写测试。

请撰写第{chapter_number}章正文。

硬性目标：
- 目标字数：{target_word_count}字以上。
- 保持原世界观、时间线、人物关系、组织关系与情感发展。
- 保持现实向半岛娱乐圈语境，不改写真实现实团体节点。
- 只输出正文，不输出标题、大纲、解释或元信息。

上一章承接：
{previous_chapter_bridge or _build_previous_chapter_bridge(None)}

本章阶段：
{plan.get("stage_range", "")} {plan.get("stage_title", "")}

本章剧情摘要：
{plan.get("plot_summary", "")}

本章叙事目标：
{plan.get("narrative_goal", "")}

场景安排：
{plan.get("scene_plan", "")}

人物焦点：
{focus}

现实时间线约束：
{reality_constraints}

{reality_anchor}

阶段目标：
{stage_goals}

护栏：
{guardrails}

人物身份硬约束：
- Rene 是杨翠的英文名 / 艺名，同一个人。
- 不要把 Rene 写成另一个人，不要安排杨翠与 Rene 对话、聊天、约会或发生感情线。
- 必须使用第三人称叙述，主角称为“杨翠”或“Rene”；不要用第一人称“我”作为叙述视角。
- 张元英、崔叡娜、金珉周是队内成员关系与情感暗线核心，不能整章缺席。
- 固定译名：权恩菲，不写权恩非；崔叡娜，不写崔叡那；金珉周，不写金玟周；张元英，不写张员瑛。
- 禁止出现“公开恋情”或“官宣恋情”这两个词；只能用“关系曝光风险”“不能让关系曝光”等表达。

正文写法：
- 用场景、动作、对话、心理反应和日程细节推进。
- 不要用总结腔。
- 不要把上面约束逐条复述成说明文字。
- 每章只推进一个主要现实节点或关系节点。
"""


async def _call_bandao_ai_text(
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

    attempts = max(1, int(max_attempts or 1))
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = await ai_service.generate_text(**kwargs)
            if isinstance(response, dict):
                return str(response.get("content") or "").strip()
            return str(response or "").strip()
        except Exception as exc:
            last_error = exc
            if attempt >= attempts:
                break
            if retry_delay_seconds > 0:
                await asyncio.sleep(retry_delay_seconds)
    assert last_error is not None
    raise last_error


async def generate_bandao_ai_chapter_text(
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
    """???? AI ?????????

    ????????????????????? AI ???????????
    full-pack ??????
    """
    prompt = _build_bandao_ai_prompt(
        chapter_number=chapter_number,
        plan=plan,
        target_word_count=target_word_count,
        previous_chapter_bridge=previous_chapter_bridge,
    )
    return await _call_bandao_ai_text(
        ai_service=ai_service,
        prompt=prompt,
        target_word_count=target_word_count,
        model=model,
        max_attempts=max_attempts_per_segment,
        retry_delay_seconds=retry_delay_seconds,
    )


def _build_bandao_continuation_prompt(
    *,
    chapter_number: int,
    plan: dict[str, Any],
    target_word_count: int,
    current_text: str,
) -> str:
    remaining_words = max(1, target_word_count - _compact_word_count(current_text))
    current_tail = re.sub(r"\s+", " ", current_text or "").strip()[-1500:]
    focus = "、".join(str(item) for item in plan.get("character_focus") or [])
    guardrails = "\n".join(f"- {rule}" for rule in plan.get("guardrails") or [])
    return f"""继续第{chapter_number}章正文。

当前正文还没有达到目标字数，需要补写至少{remaining_words}字。

已经写出的结尾：
{current_tail}

续写要求：
- 从上面结尾自然接下去，不要重复已经写过的段落。
- 继续保持本章剧情摘要：{plan.get("plot_summary", "")}
- 继续使用这些人物焦点：{focus}
- 继续遵守现实时间线约束：{plan.get("reality_timeline_constraints", "")}
- Rene 是杨翠的英文名 / 艺名，同一个人；不要把 Rene 写成另一个人。
- 固定译名：权恩菲，不写权恩非；崔叡娜，不写崔叡那；金珉周，不写金玟周；张元英，不写张员瑛。
- 禁止出现“公开恋情”或“官宣恋情”这两个词。
- 继续遵守护栏：
{guardrails}
- 只输出补写正文，不输出标题、大纲、解释或元信息。
"""


async def _generate_bandao_ai_chapter_text_until_target(
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
    text = await generate_bandao_ai_chapter_text(
        ai_service=ai_service,
        chapter_number=chapter_number,
        plan=plan,
        target_word_count=target_word_count,
        previous_chapter_bridge=previous_chapter_bridge,
        model=model,
        max_attempts_per_segment=max_attempts_per_segment,
        retry_delay_seconds=retry_delay_seconds,
    )
    while _compact_word_count(text) < target_word_count and max_segments > 1:
        max_segments -= 1
        prompt = _build_bandao_continuation_prompt(
            chapter_number=chapter_number,
            plan=plan,
            target_word_count=target_word_count,
            current_text=text,
        )
        segment = await _call_bandao_ai_text(
            ai_service=ai_service,
            prompt=prompt,
            target_word_count=target_word_count - _compact_word_count(text),
            model=model,
            max_attempts=max_attempts_per_segment,
            retry_delay_seconds=retry_delay_seconds,
        )
        if not segment:
            break
        text = f"{text.rstrip()}\n\n{segment.strip()}"
    return text


def generate_bandao_full_pack(
    *,
    artifact_dir: Path,
    output_dir: Path,
    writer: BandaoChapterWriter,
    chapter_numbers: Iterable[int] | None = None,
    target_word_count: int = 10000,
    overwrite: bool = False,
    audit_after: bool = True,
    on_skip: BandaoSkipHook | None = None,
) -> dict[str, Any]:
    """生成《混在半岛的日子》完整续写正文包。

    writer 是可替换的正文生成函数。生产路径可接真实 AI，测试路径可接合成 writer。
    本函数负责范围、恢复、字数门禁、manifest 和完成审计。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    numbers = _normalize_chapter_numbers(chapter_numbers)

    generated: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    manifest_chapters: list[dict[str, Any]] = []

    for chapter_number in numbers:
        path = _chapter_path(output_dir, chapter_number)
        if path.exists() and not overwrite:
            existing_text = path.read_text(encoding="utf-8")
            word_count = _compact_word_count(existing_text)
            skipped.append({"chapter_number": chapter_number, "path": str(path), "word_count": word_count})
            manifest_chapters.append({"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "status": "skipped_existing"})
            if on_skip:
                on_skip(chapter_number, existing_text)
            continue

        plan = build_bandao_chapter_expansion_plan(chapter_number, artifact_dir)
        text = writer(chapter_number, plan, target_word_count)
        word_count = _compact_word_count(text)
        if word_count < target_word_count:
            failed.append(
                {
                    "chapter_number": chapter_number,
                    "path": str(path),
                    "word_count": word_count,
                    "required_word_count": target_word_count,
                    "reason": "short_generated_text",
                }
            )
            continue

        path.write_text(text, encoding="utf-8")
        entry = {"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "status": "generated"}
        generated.append(entry)
        manifest_chapters.append(entry)

    contains_full_800 = (
        len(numbers) == 800
        and numbers[0] == BANDAO_START_CHAPTER
        and numbers[-1] == BANDAO_TARGET_TOTAL_CHAPTERS
        and not failed
    )
    manifest = {
        "type": "bandao_full_continuation_pack",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "output_dir": str(output_dir),
        "target_total_chapters": BANDAO_TARGET_TOTAL_CHAPTERS,
        "start_chapter_number": BANDAO_START_CHAPTER,
        "end_chapter_number": BANDAO_TARGET_TOTAL_CHAPTERS,
        "target_word_count": target_word_count,
        "chapter_count": len(manifest_chapters),
        "generated_chapter_count": len(generated),
        "skipped_existing_chapter_count": len(skipped),
        "failed_chapter_count": len(failed),
        "contains_full_800_chapter_text": contains_full_800,
        "chapters": sorted(manifest_chapters, key=lambda item: item["chapter_number"]),
        "failed_chapters": failed,
    }
    manifest_path = output_dir / "full_pack_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    audit = None
    if audit_after:
        audit = audit_bandao_full_completion(
            continuation_dir=output_dir,
            artifact_dir=artifact_dir,
            required_word_count=target_word_count,
        )
    regression_audit = audit_bandao_regression_pack(
        artifact_dir=artifact_dir,
        output_dir=output_dir,
        start_chapter=numbers[0],
        end_chapter=numbers[-1],
        required_word_count=target_word_count,
    )

    return {
        **manifest,
        "manifest_path": manifest_path,
        "audit": audit,
        "regression_audit": regression_audit,
    }


async def generate_bandao_full_pack_async(
    *,
    artifact_dir: Path,
    output_dir: Path,
    writer: BandaoAsyncChapterWriter,
    chapter_numbers: Iterable[int] | None = None,
    target_word_count: int = 10000,
    overwrite: bool = False,
    audit_after: bool = True,
    on_skip: BandaoSkipHook | None = None,
) -> dict[str, Any]:
    """异步生成完整续写正文包，供真实 AI writer 使用。

    与同步版本保持相同 manifest / 审计语义；单章 writer 失败只记录失败章，
    不写短章或异常章，便于长任务中断后恢复。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    numbers = _normalize_chapter_numbers(chapter_numbers)

    generated: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    manifest_chapters: list[dict[str, Any]] = []

    for chapter_number in numbers:
        path = _chapter_path(output_dir, chapter_number)
        if path.exists() and not overwrite:
            existing_text = path.read_text(encoding="utf-8")
            word_count = _compact_word_count(existing_text)
            if word_count >= target_word_count and _existing_chapter_passes_regression(
                artifact_dir=artifact_dir,
                output_dir=output_dir,
                chapter_number=chapter_number,
                target_word_count=target_word_count,
            ):
                skipped.append({"chapter_number": chapter_number, "path": str(path), "word_count": word_count})
                manifest_chapters.append(
                    {"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "status": "skipped_existing"}
                )
                if on_skip:
                    on_skip(chapter_number, existing_text)
                continue

        plan = build_bandao_chapter_expansion_plan(chapter_number, artifact_dir)
        try:
            text = await writer(chapter_number, plan, target_word_count)
        except Exception as exc:
            failed.append(
                {
                    "chapter_number": chapter_number,
                    "path": str(path),
                    "word_count": 0,
                    "required_word_count": target_word_count,
                    "reason": "writer_error",
                    "error": str(exc),
                }
            )
            continue

        word_count = _compact_word_count(text)
        if word_count < target_word_count:
            failed.append(
                {
                    "chapter_number": chapter_number,
                    "path": str(path),
                    "word_count": word_count,
                    "required_word_count": target_word_count,
                    "reason": "short_generated_text",
                }
            )
            continue

        path.write_text(text, encoding="utf-8")
        entry = {"chapter_number": chapter_number, "path": str(path), "word_count": word_count, "status": "generated"}
        generated.append(entry)
        manifest_chapters.append(entry)

    contains_full_800 = (
        len(numbers) == 800
        and numbers[0] == BANDAO_START_CHAPTER
        and numbers[-1] == BANDAO_TARGET_TOTAL_CHAPTERS
        and not failed
    )
    manifest = {
        "type": "bandao_full_continuation_pack",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "output_dir": str(output_dir),
        "target_total_chapters": BANDAO_TARGET_TOTAL_CHAPTERS,
        "start_chapter_number": BANDAO_START_CHAPTER,
        "end_chapter_number": BANDAO_TARGET_TOTAL_CHAPTERS,
        "target_word_count": target_word_count,
        "chapter_count": len(manifest_chapters),
        "generated_chapter_count": len(generated),
        "skipped_existing_chapter_count": len(skipped),
        "failed_chapter_count": len(failed),
        "contains_full_800_chapter_text": contains_full_800,
        "chapters": sorted(manifest_chapters, key=lambda item: item["chapter_number"]),
        "failed_chapters": failed,
    }
    manifest_path = output_dir / "full_pack_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    audit = None
    if audit_after:
        audit = audit_bandao_full_completion(
            continuation_dir=output_dir,
            artifact_dir=artifact_dir,
            required_word_count=target_word_count,
        )
    regression_audit = audit_bandao_regression_pack(
        artifact_dir=artifact_dir,
        output_dir=output_dir,
        start_chapter=numbers[0],
        end_chapter=numbers[-1],
        required_word_count=target_word_count,
    )

    return {
        **manifest,
        "manifest_path": manifest_path,
        "audit": audit,
        "regression_audit": regression_audit,
    }


async def generate_bandao_full_pack_with_ai(
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
    """??? AIService ???? 201-1000 ????"""
    previous_text: str | None = None

    async def writer(chapter_number: int, plan: dict[str, Any], required_words: int) -> str:
        nonlocal previous_text
        if previous_text is None:
            previous_text = _load_existing_previous_chapter_text(output_dir, chapter_number)
        text = await _generate_bandao_ai_chapter_text_until_target(
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

    return await generate_bandao_full_pack_async(
        artifact_dir=artifact_dir,
        output_dir=output_dir,
        writer=writer,
        chapter_numbers=chapter_numbers,
        target_word_count=target_word_count,
        overwrite=overwrite,
        audit_after=audit_after,
        on_skip=remember_skipped,
    )
