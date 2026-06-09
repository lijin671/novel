from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database import get_engine
from app.models.settings import Settings
from app.services.ai_service import create_user_ai_service
from app.services.original_novel_full_pack_generation_service import (
    audit_original_novel_pack,
    generate_original_novel_full_pack,
    generate_original_novel_full_pack_with_ai,
    merge_original_chapters_to_single_txt,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate original novel full-pack chapters")
    parser.add_argument("--user-id", default=os.getenv("MUMU_DEFAULT_USER_ID", "local-admin"))
    parser.add_argument("--artifact-dir", default="tmp/bandao-original-rainseason-20260601")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--start-chapter", type=int, default=1)
    parser.add_argument("--end-chapter", type=int, default=1000)
    parser.add_argument("--target-word-count", type=int, default=10000)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-segments-per-chapter", type=int, default=8)
    parser.add_argument("--max-attempts-per-segment", type=int, default=3)
    parser.add_argument("--retry-delay-seconds", type=float, default=1.0)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--merge-txt", action="store_true")
    parser.add_argument("--merged-path", default=None)
    parser.add_argument("--normalize-headings", action="store_true")
    parser.add_argument("--synthetic", action="store_true", help="Use deterministic local writer for pipeline validation; not final literary output")
    return parser.parse_args(argv)


def chapter_numbers_from_args(args: argparse.Namespace) -> list[int]:
    if args.start_chapter < 1:
        raise ValueError("start_chapter 不能小于 1")
    if args.end_chapter > 1000:
        raise ValueError("end_chapter 不能大于 1000")
    if args.end_chapter < args.start_chapter:
        raise ValueError("end_chapter 不能小于 start_chapter")
    return list(range(args.start_chapter, args.end_chapter + 1))


def build_dry_run_summary(args: argparse.Namespace) -> dict[str, Any]:
    numbers = chapter_numbers_from_args(args)
    return {
        "dry_run": True,
        "artifact_dir": str(Path(args.artifact_dir)),
        "output_dir": str(Path(args.output_dir)),
        "start_chapter": numbers[0],
        "end_chapter": numbers[-1],
        "chapter_count": len(numbers),
        "target_word_count": args.target_word_count,
        "estimated_total_words": len(numbers) * args.target_word_count,
        "max_segments_per_chapter": args.max_segments_per_chapter,
    }


async def build_ai_service(db, user_id: str, *, model: str | None = None):
    result = await db.execute(select(Settings).where(Settings.user_id == user_id))
    settings = result.scalar_one_or_none()
    if settings is None:
        raise RuntimeError(f"未找到用户 AI 设置，无法生成正文: {user_id}")
    service = create_user_ai_service(
        api_provider=settings.api_provider,
        api_key=settings.api_key,
        api_base_url=settings.api_base_url,
        model_name=model or settings.llm_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        system_prompt=settings.system_prompt,
    )
    return service


def _synthetic_writer(chapter_number: int, plan: dict[str, Any], target_word_count: int) -> str:
    title = str(plan.get("title") or f"第{chapter_number}章")
    base = [
        title,
        "",
        f"林知夏 Rina 在{plan.get('time_window')}的{plan.get('stage')}阶段继续往前走。",
        f"本章围绕{plan.get('career_beat')}、{plan.get('relationship_beat')}和{plan.get('conflict')}推进。",
        "韩书允把录音室里的灯调暗，Aurora*One 的日程表贴在门边，雨声像一段还没命名的前奏。",
    ]
    body = "\n\n".join(base)
    filler = (
        "练习室的镜子、后台通道、耳返里的节拍和便利店的灯光，"
        "把事业线与情感线慢慢接在一起。林知夏没有急着回答，"
        "只把下一版 demo 保存下来，再把今天的犹豫写进雨声里。"
    )
    while len("".join(body.split())) < target_word_count:
        body += "\n\n" + filler
    return body


async def main(args: argparse.Namespace | None = None) -> dict[str, Any]:
    args = args or parse_args()
    artifact_dir = Path(args.artifact_dir)
    output_dir = Path(args.output_dir)
    numbers = chapter_numbers_from_args(args)

    if args.dry_run:
        result = build_dry_run_summary(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    if args.merge_txt:
        merged_path = Path(args.merged_path) if args.merged_path else output_dir / "半岛：雨季未命名_001-1000.txt"
        result = {
            "merged_txt": merge_original_chapters_to_single_txt(
                artifact_dir=artifact_dir,
                output_dir=output_dir,
                merged_path=merged_path,
                start_chapter=numbers[0],
                end_chapter=numbers[-1],
                normalize_headings=args.normalize_headings,
            )
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    if args.audit_only:
        result = audit_original_novel_pack(
            artifact_dir=artifact_dir,
            output_dir=output_dir,
            start_chapter=numbers[0],
            end_chapter=numbers[-1],
            required_word_count=args.target_word_count,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    if args.synthetic:
        result = generate_original_novel_full_pack(
            artifact_dir=artifact_dir,
            output_dir=output_dir,
            writer=_synthetic_writer,
            chapter_numbers=numbers,
            target_word_count=args.target_word_count,
            overwrite=args.overwrite,
            audit_after=True,
        )
        print(
            f"generated={result['generated_chapter_count']} skipped={result['skipped_existing_chapter_count']} "
            f"failed={result['failed_chapter_count']} audit_passed={result['audit']['passed'] if result.get('audit') else None}"
        )
        return result

    engine = await get_engine(args.user_id)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        ai_service = await build_ai_service(db, args.user_id, model=args.model)
        result = await generate_original_novel_full_pack_with_ai(
            artifact_dir=artifact_dir,
            output_dir=output_dir,
            ai_service=ai_service,
            chapter_numbers=numbers,
            target_word_count=args.target_word_count,
            overwrite=args.overwrite,
            audit_after=True,
            model=args.model,
            max_segments_per_chapter=args.max_segments_per_chapter,
            max_attempts_per_segment=args.max_attempts_per_segment,
            retry_delay_seconds=args.retry_delay_seconds,
        )
    print(
        f"generated={result['generated_chapter_count']} skipped={result['skipped_existing_chapter_count']} "
        f"failed={result['failed_chapter_count']} audit_passed={result['audit']['passed'] if result.get('audit') else None}"
    )
    return result


if __name__ == "__main__":
    asyncio.run(main())
