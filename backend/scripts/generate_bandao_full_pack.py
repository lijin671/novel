from __future__ import annotations

import argparse
import asyncio
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import get_engine
from app.models.settings import Settings
from app.services.ai_service import create_user_ai_service
from app.services.bandao_batch_queue_plan import (
    BANDAO_START_CHAPTER,
    BANDAO_TARGET_TOTAL_CHAPTERS,
    BANDAO_TARGET_WORD_COUNT,
)
from app.services.bandao_completion_audit_service import audit_bandao_full_completion
from app.services.bandao_full_pack_generation_service import generate_bandao_full_pack_with_ai
from app.services.bandao_regression_audit_service import audit_pack as audit_bandao_regression_pack


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Bandao real AI full-pack continuation")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--artifact-dir", default="tmp/book-remix-test-ban-dao-20260530")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--start-chapter", type=int, default=BANDAO_START_CHAPTER)
    parser.add_argument("--end-chapter", type=int, default=BANDAO_TARGET_TOTAL_CHAPTERS)
    parser.add_argument("--target-word-count", type=int, default=BANDAO_TARGET_WORD_COUNT)
    parser.add_argument("--model", default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-audit", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print scope only; do not open DB or call AI")
    parser.add_argument("--audit-only", action="store_true", help="Audit output-dir only; do not open DB or call AI")
    parser.add_argument("--regression-audit-only", action="store_true", help="Run per-chapter regression audit only; do not open DB or call AI")
    parser.add_argument("--max-segments-per-chapter", type=int, default=4, help="Max AI calls per chapter including continuation segments")
    parser.add_argument("--max-attempts-per-segment", type=int, default=2, help="Retry attempts for each AI segment")
    parser.add_argument("--retry-delay-seconds", type=float, default=1.0, help="Delay before retrying failed AI segment")
    parser.add_argument("--chunk-size", type=int, default=0, help="plan-only chunk size")
    parser.add_argument("--plan-only", action="store_true", help="Print resumable commands only; do not open DB or call AI")
    parser.add_argument("--merge-txt", action="store_true", help="Merge generated chapter_*.txt files into one txt file; do not open DB or call AI")
    parser.add_argument("--merged-path", default=None, help="Output path for --merge-txt")
    parser.add_argument("--normalize-headings", action="store_true", help="Normalize chapter headings while merging chapter_*.txt")
    return parser.parse_args(argv)


def chapter_numbers_from_args(args: argparse.Namespace) -> list[int]:
    if args.start_chapter < BANDAO_START_CHAPTER:
        raise ValueError(f"start_chapter 涓嶈兘灏忎簬 {BANDAO_START_CHAPTER}")
    if args.end_chapter > BANDAO_TARGET_TOTAL_CHAPTERS:
        raise ValueError(f"end_chapter 涓嶈兘澶т簬 {BANDAO_TARGET_TOTAL_CHAPTERS}")
    if args.end_chapter < args.start_chapter:
        raise ValueError("end_chapter 涓嶈兘灏忎簬 start_chapter")
    return list(range(args.start_chapter, args.end_chapter + 1))


def build_dry_run_summary(args: argparse.Namespace) -> dict[str, Any]:
    chapter_numbers = chapter_numbers_from_args(args)
    return {
        "dry_run": True,
        "user_id": args.user_id,
        "artifact_dir": str(Path(args.artifact_dir)),
        "output_dir": str(Path(args.output_dir)),
        "start_chapter": chapter_numbers[0],
        "end_chapter": chapter_numbers[-1],
        "chapter_count": len(chapter_numbers),
        "target_word_count": args.target_word_count,
        "estimated_total_words": len(chapter_numbers) * args.target_word_count,
        "overwrite": bool(args.overwrite),
        "audit_after": not bool(args.no_audit),
        "model": args.model,
        "max_segments_per_chapter": args.max_segments_per_chapter,
        "max_attempts_per_segment": args.max_attempts_per_segment,
        "retry_delay_seconds": args.retry_delay_seconds,
        "would_call_ai": False,
    }


def build_chunked_run_commands(args: argparse.Namespace) -> list[str]:
    chapter_numbers = chapter_numbers_from_args(args)
    chunk_size = int(args.chunk_size or len(chapter_numbers) or 1)
    if chunk_size <= 0:
        raise ValueError("chunk_size ???? 0")

    commands: list[str] = []
    for index in range(0, len(chapter_numbers), chunk_size):
        chunk = chapter_numbers[index:index + chunk_size]
        parts = [
            sys.executable,
            "-m",
            "backend.scripts.generate_bandao_full_pack",
            "--user-id",
            args.user_id,
            "--artifact-dir",
            str(Path(args.artifact_dir)),
            "--output-dir",
            str(Path(args.output_dir)),
            "--start-chapter",
            str(chunk[0]),
            "--end-chapter",
            str(chunk[-1]),
            "--target-word-count",
            str(args.target_word_count),
            "--max-segments-per-chapter",
            str(args.max_segments_per_chapter),
            "--max-attempts-per-segment",
            str(args.max_attempts_per_segment),
            "--retry-delay-seconds",
            str(args.retry_delay_seconds),
        ]
        if args.model:
            parts.extend(["--model", args.model])
        if args.overwrite:
            parts.append("--overwrite")
        if args.no_audit:
            parts.append("--no-audit")
        commands.append(" ".join(shlex.quote(part) for part in parts))
    return commands


def merge_chapters_to_single_txt(
    *,
    output_dir: Path,
    merged_path: Path,
    start_chapter: int = BANDAO_START_CHAPTER,
    end_chapter: int = BANDAO_TARGET_TOTAL_CHAPTERS,
    artifact_dir: Path | None = None,
    normalize_headings: bool = False,
) -> dict[str, Any]:
    missing = [
        chapter_number
        for chapter_number in range(start_chapter, end_chapter + 1)
        if not (output_dir / f"chapter_{chapter_number:04d}.txt").exists()
    ]
    if missing:
        raise ValueError(f"缺少章节文件，无法合并: {missing[:20]}")

    title_map = _build_continuation_title_map(
        artifact_dir or Path("tmp/book-remix-test-ban-dao-20260530")
    ) if normalize_headings else {}

    parts: list[str] = []
    total_chars = 0
    for chapter_number in range(start_chapter, end_chapter + 1):
        path = output_dir / f"chapter_{chapter_number:04d}.txt"
        text = path.read_text(encoding="utf-8").strip()
        if normalize_headings:
            text = _normalize_chapter_heading(
                chapter_number=chapter_number,
                text=text,
                title_map=title_map,
            )
        total_chars += len(text)
        parts.append(text)

    merged_path.parent.mkdir(parents=True, exist_ok=True)
    merged_text = "\n\n\n".join(parts).rstrip() + "\n"
    merged_path.write_text(merged_text, encoding="utf-8")
    return {
        "path": str(merged_path),
        "chapter_count": end_chapter - start_chapter + 1,
        "start_chapter": start_chapter,
        "end_chapter": end_chapter,
        "source_text_chars": total_chars,
        "merged_chars": len(merged_text),
    }


def _build_continuation_title_map(artifact_dir: Path) -> dict[int, str]:
    titles: dict[int, str] = {}

    outline_path = artifact_dir / "chapter_201_outline.json"
    if outline_path.exists():
        outline = json.loads(outline_path.read_text(encoding="utf-8"))
        title = str(outline.get("title") or "").strip()
        if title:
            titles[BANDAO_START_CHAPTER] = title

    plan_path = artifact_dir / "continuation_plan_to_1000.json"
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        for stage in plan.get("stage_plan") or []:
            range_text = str(stage.get("range") or "")
            if "-" not in range_text:
                continue
            try:
                start_text, end_text = range_text.split("-", 1)
                start = int(start_text)
                end = int(end_text)
            except ValueError:
                continue
            stage_title = str(stage.get("title") or "续写").strip() or "续写"
            for chapter_number in range(start, end + 1):
                titles.setdefault(chapter_number, stage_title)

    return titles


_CHAPTER_HEADING_RE = re.compile(
    r"^\s*#{0,6}\s*第\s*(?P<number>\d{1,4})\s*章(?:\s*(?P<title>.*?))?\s*$"
)


def _strip_number_prefix(title: str, chapter_number: int) -> str:
    stripped = re.sub(r"^\s*#{1,6}\s*", "", title or "").strip()
    outer_prefix = re.compile(rf"^第\s*{chapter_number}\s*章\s*")
    stripped = outer_prefix.sub("", stripped).strip()
    stripped = outer_prefix.sub("", stripped).strip()
    return stripped


def _normalize_chapter_heading(
    *,
    chapter_number: int,
    text: str,
    title_map: dict[int, str],
) -> str:
    lines = (text or "").replace("\ufeff", "").strip().splitlines()
    first_content_index = next((idx for idx, line in enumerate(lines) if line.strip()), None)
    if first_content_index is None:
        return f"第{chapter_number}章 {title_map.get(chapter_number, '续写')}".rstrip()

    first_line = lines[first_content_index].strip()
    heading_match = _CHAPTER_HEADING_RE.match(first_line)
    existing_title = ""
    body_lines = lines[first_content_index:]
    if heading_match and int(heading_match.group("number")) == chapter_number:
        existing_title = str(heading_match.group("title") or "").strip()
        body_lines = lines[first_content_index + 1 :]

    body_lines = _filter_inner_chapter_heading_noise(
        body_lines,
        chapter_number=chapter_number,
    )
    fallback_title = _strip_number_prefix(title_map.get(chapter_number, ""), chapter_number)
    title = _strip_number_prefix(existing_title, chapter_number) or fallback_title
    heading = f"第{chapter_number}章 {title}".rstrip()
    body = "\n".join(body_lines).strip()
    return f"{heading}\n\n{body}".rstrip() if body else heading


def _filter_inner_chapter_heading_noise(
    lines: list[str],
    *,
    chapter_number: int,
) -> list[str]:
    filtered: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        heading_match = _CHAPTER_HEADING_RE.match(stripped)
        if heading_match:
            matched_number = int(heading_match.group("number"))
            matched_title = str(heading_match.group("title") or "").strip()
            if matched_number == chapter_number and matched_title in {"完", "完。"}:
                index += 1
                continue
            if matched_number == chapter_number and not matched_title:
                index += 1
                continue
            if matched_number > chapter_number:
                break
        filtered.append(line)
        index += 1
    return filtered


async def build_ai_service(db: AsyncSession, user_id: str) -> Any:
    settings_result = await db.execute(select(Settings).where(Settings.user_id == user_id))
    settings = settings_result.scalar_one_or_none()
    if not settings:
        raise RuntimeError(f"鏈壘鍒扮敤鎴?AI 璁剧疆: {user_id}")
    if not settings.api_key:
        raise RuntimeError(f"鐢ㄦ埛 AI 璁剧疆缂哄皯 api_key: {user_id}")

    return create_user_ai_service(
        api_provider=settings.api_provider,
        api_key=settings.api_key,
        api_base_url=settings.api_base_url or "",
        model_name=settings.llm_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        system_prompt=settings.system_prompt,
    )


async def main(args: argparse.Namespace) -> dict[str, Any]:
    if args.plan_only:
        commands = build_chunked_run_commands(args)
        summary = {
            "plan_only": True,
            "chapter_count": len(chapter_numbers_from_args(args)),
            "chunk_size": args.chunk_size,
            "command_count": len(commands),
            "commands": commands,
            "would_call_ai": False,
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return summary

    if args.audit_only:
        report = audit_bandao_full_completion(
            continuation_dir=Path(args.output_dir),
            artifact_dir=Path(args.artifact_dir),
            required_word_count=args.target_word_count,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report

    if args.regression_audit_only:
        report = audit_bandao_regression_pack(
            artifact_dir=Path(args.artifact_dir),
            output_dir=Path(args.output_dir),
            start_chapter=args.start_chapter,
            end_chapter=args.end_chapter,
            required_word_count=args.target_word_count,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report

    if args.merge_txt:
        merged_path = Path(args.merged_path) if args.merged_path else Path(args.output_dir) / "混在半岛的日子_续写201-1000.txt"
        report = {
            "merge_txt": True,
            "merged_txt": merge_chapters_to_single_txt(
                output_dir=Path(args.output_dir),
                merged_path=merged_path,
                start_chapter=args.start_chapter,
                end_chapter=args.end_chapter,
                artifact_dir=Path(args.artifact_dir),
                normalize_headings=args.normalize_headings,
            ),
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report

    if args.dry_run:
        summary = build_dry_run_summary(args)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return summary

    engine = await get_engine(args.user_id)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as db:
        ai_service = await build_ai_service(db, args.user_id)
        result = await generate_bandao_full_pack_with_ai(
            artifact_dir=Path(args.artifact_dir),
            output_dir=Path(args.output_dir),
            ai_service=ai_service,
            chapter_numbers=chapter_numbers_from_args(args),
            target_word_count=args.target_word_count,
            overwrite=args.overwrite,
            audit_after=not args.no_audit,
            model=args.model,
            max_segments_per_chapter=args.max_segments_per_chapter,
            max_attempts_per_segment=args.max_attempts_per_segment,
            retry_delay_seconds=args.retry_delay_seconds,
        )

    regression_audit = result.get("regression_audit")
    if regression_audit is None:
        regression_audit = audit_bandao_regression_pack(
            artifact_dir=Path(args.artifact_dir),
            output_dir=Path(args.output_dir),
            start_chapter=args.start_chapter,
            end_chapter=args.end_chapter,
            required_word_count=args.target_word_count,
        )
    result["regression_audit"] = regression_audit

    audit = result.get("audit") or {}
    if not regression_audit.get("passed"):
        raise RuntimeError(
            "regression audit failed: "
            f"failed_chapter_count={regression_audit.get('failed_chapter_count')}"
        )
    print(
        "bandao_full_pack "
        f"generated={result['generated_chapter_count']} "
        f"skipped={result['skipped_existing_chapter_count']} "
        f"failed={result['failed_chapter_count']} "
        f"manifest={result['manifest_path']} "
        f"audit_completed={audit.get('completed')} "
        f"regression_passed={regression_audit.get('passed')}"
    )
    return result


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
