import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import chromadb
from sqlalchemy import and_, case, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.database import get_engine
from app.models.analysis_task import AnalysisTask
from app.models.batch_generation_task import BatchGenerationTask
from app.models.chapter import Chapter
from app.models.foreshadow import Foreshadow
from app.models.generation_history import GenerationHistory
from app.models.memory import PlotAnalysis, StoryMemory
from app.models.novel_workflow import ChapterWorkflowResult, NovelWorkflowTask
from app.models.project import Project
from app.models.regeneration_task import RegenerationTask


def _collection_name(user_id: str, project_id: str) -> str:
    user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8]
    project_hash = hashlib.sha256(project_id.encode()).hexdigest()[:8]
    return f"u_{user_hash}_p_{project_hash}"


class VectorMemoryCleaner:
    def __init__(self, chroma_path: str = "data/chroma_db") -> None:
        self.client = chromadb.PersistentClient(path=chroma_path)

    def delete_chapter_memories(
        self,
        *,
        user_id: str,
        project_id: str,
        chapter_ids: list[str],
    ) -> dict[str, Any]:
        collection_name = _collection_name(user_id, project_id)
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception as exc:
            if "does not exist" in str(exc).lower():
                return {
                    "collection_name": collection_name,
                    "collection_missing": True,
                    "deleted_vector_count": 0,
                    "deleted_by_chapter": {},
                }
            raise

        deleted_total = 0
        deleted_by_chapter: dict[str, int] = {}

        for chapter_id in chapter_ids:
            results = collection.get(where={"chapter_id": chapter_id})
            ids = results.get("ids") or []
            if not ids:
                continue
            collection.delete(ids=ids)
            deleted_total += len(ids)
            deleted_by_chapter[chapter_id] = len(ids)

        return {
            "collection_name": collection_name,
            "collection_missing": False,
            "deleted_vector_count": deleted_total,
            "deleted_by_chapter": deleted_by_chapter,
        }


async def _load_project(
    db: AsyncSession,
    project_id: str,
) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise RuntimeError(f"未找到项目: {project_id}")
    return project


async def _load_generated_chapters(
    db: AsyncSession,
    project_id: str,
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(
            Chapter.id,
            Chapter.chapter_number,
            Chapter.title,
            Chapter.status,
            Chapter.word_count,
        )
        .join(GenerationHistory, GenerationHistory.chapter_id == Chapter.id)
        .where(Chapter.project_id == project_id)
        .group_by(
            Chapter.id,
            Chapter.chapter_number,
            Chapter.title,
            Chapter.status,
            Chapter.word_count,
        )
        .order_by(Chapter.chapter_number.asc())
    )
    rows = result.all()
    return [
        {
            "chapter_id": row.id,
            "chapter_number": int(row.chapter_number),
            "title": row.title,
            "status": row.status,
            "word_count": int(row.word_count or 0),
        }
        for row in rows
    ]


async def _count_rows(
    db: AsyncSession,
    stmt,
) -> int:
    result = await db.execute(stmt)
    value = result.scalar_one()
    return int(value or 0)


async def build_cleanup_plan(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    project = await _load_project(db, project_id)
    generated_chapters = await _load_generated_chapters(db, project_id)
    chapter_ids = [item["chapter_id"] for item in generated_chapters]
    chapter_numbers = [item["chapter_number"] for item in generated_chapters]

    plan: dict[str, Any] = {
        "project_id": project.id,
        "project_title": project.title,
        "project_user_id": project.user_id,
        "generated_chapter_count": len(generated_chapters),
        "generated_chapter_numbers": chapter_numbers,
        "generated_chapters": generated_chapters,
        "counts": {
            "generation_history": 0,
            "analysis_tasks": 0,
            "regeneration_tasks": 0,
            "plot_analysis": 0,
            "story_memories": 0,
            "story_memories_revert": 0,
            "chapter_workflow_results": 0,
            "batch_generation_tasks": 0,
            "novel_workflow_tasks": 0,
            "foreshadows_delete_analysis": 0,
            "foreshadows_reset_manual": 0,
            "foreshadows_revert_resolve": 0,
        },
    }

    if not chapter_ids:
        return plan

    plan["counts"]["generation_history"] = await _count_rows(
        db,
        select(func.count())
        .select_from(GenerationHistory)
        .where(
            and_(
                GenerationHistory.project_id == project_id,
                GenerationHistory.chapter_id.in_(chapter_ids),
            )
        ),
    )
    plan["counts"]["analysis_tasks"] = await _count_rows(
        db,
        select(func.count())
        .select_from(AnalysisTask)
        .where(AnalysisTask.chapter_id.in_(chapter_ids)),
    )
    plan["counts"]["regeneration_tasks"] = await _count_rows(
        db,
        select(func.count())
        .select_from(RegenerationTask)
        .where(RegenerationTask.chapter_id.in_(chapter_ids)),
    )
    plan["counts"]["plot_analysis"] = await _count_rows(
        db,
        select(func.count())
        .select_from(PlotAnalysis)
        .where(PlotAnalysis.chapter_id.in_(chapter_ids)),
    )
    plan["counts"]["story_memories"] = await _count_rows(
        db,
        select(func.count())
        .select_from(StoryMemory)
        .where(StoryMemory.chapter_id.in_(chapter_ids)),
    )
    plan["counts"]["story_memories_revert"] = await _count_rows(
        db,
        select(func.count())
        .select_from(StoryMemory)
        .where(
            and_(
                StoryMemory.project_id == project_id,
                StoryMemory.chapter_id.not_in(chapter_ids),
                StoryMemory.foreshadow_resolved_at.in_(chapter_ids),
                StoryMemory.is_foreshadow == 2,
            )
        ),
    )
    plan["counts"]["chapter_workflow_results"] = await _count_rows(
        db,
        select(func.count())
        .select_from(ChapterWorkflowResult)
        .where(ChapterWorkflowResult.chapter_id.in_(chapter_ids)),
    )
    plan["counts"]["batch_generation_tasks"] = await _count_rows(
        db,
        select(func.count())
        .select_from(BatchGenerationTask)
        .where(BatchGenerationTask.project_id == project_id),
    )
    plan["counts"]["novel_workflow_tasks"] = await _count_rows(
        db,
        select(func.count())
        .select_from(NovelWorkflowTask)
        .where(NovelWorkflowTask.project_id == project_id),
    )
    plan["counts"]["foreshadows_delete_analysis"] = await _count_rows(
        db,
        select(func.count())
        .select_from(Foreshadow)
        .where(
            and_(
                Foreshadow.project_id == project_id,
                Foreshadow.source_type == "analysis",
                Foreshadow.plant_chapter_id.in_(chapter_ids),
            )
        ),
    )
    plan["counts"]["foreshadows_reset_manual"] = await _count_rows(
        db,
        select(func.count())
        .select_from(Foreshadow)
        .where(
            and_(
                Foreshadow.project_id == project_id,
                Foreshadow.source_type == "manual",
                Foreshadow.plant_chapter_id.in_(chapter_ids),
            )
        ),
    )
    plan["counts"]["foreshadows_revert_resolve"] = await _count_rows(
        db,
        select(func.count())
        .select_from(Foreshadow)
        .where(
            and_(
                Foreshadow.project_id == project_id,
                Foreshadow.actual_resolve_chapter_id.in_(chapter_ids),
                Foreshadow.status.in_(["resolved", "partially_resolved"]),
            )
        ),
    )

    return plan


async def apply_cleanup(
    db: AsyncSession,
    plan: dict[str, Any],
) -> dict[str, Any]:
    project_id = plan["project_id"]
    chapter_ids = [item["chapter_id"] for item in plan["generated_chapters"]]

    if not chapter_ids:
        return {
            "project_id": project_id,
            "project_title": plan["project_title"],
            "applied": False,
            "reason": "no_generated_chapters",
        }

    await db.execute(
        delete(Foreshadow).where(
            and_(
                Foreshadow.project_id == project_id,
                Foreshadow.source_type == "analysis",
                Foreshadow.plant_chapter_id.in_(chapter_ids),
            )
        )
    )

    await db.execute(
        update(Foreshadow)
        .where(
            and_(
                Foreshadow.project_id == project_id,
                Foreshadow.source_type == "manual",
                Foreshadow.plant_chapter_id.in_(chapter_ids),
            )
        )
        .values(
            status="pending",
            plant_chapter_id=None,
            plant_chapter_number=None,
            actual_resolve_chapter_id=None,
            actual_resolve_chapter_number=None,
            target_resolve_chapter_id=None,
            target_resolve_chapter_number=None,
            planted_at=None,
            resolved_at=None,
            resolution_text=None,
            resolution_notes=None,
        )
    )

    await db.execute(
        update(Foreshadow)
        .where(
            and_(
                Foreshadow.project_id == project_id,
                Foreshadow.actual_resolve_chapter_id.in_(chapter_ids),
                Foreshadow.status.in_(["resolved", "partially_resolved"]),
            )
        )
        .values(
            status=case(
                (Foreshadow.plant_chapter_id.is_not(None), "planted"),
                else_="pending",
            ),
            actual_resolve_chapter_id=None,
            actual_resolve_chapter_number=None,
            resolved_at=None,
            resolution_text=None,
            resolution_notes=None,
        )
    )

    await db.execute(
        update(StoryMemory)
        .where(
            and_(
                StoryMemory.project_id == project_id,
                StoryMemory.chapter_id.not_in(chapter_ids),
                StoryMemory.foreshadow_resolved_at.in_(chapter_ids),
                StoryMemory.is_foreshadow == 2,
            )
        )
        .values(
            is_foreshadow=1,
            foreshadow_resolved_at=None,
        )
    )

    await db.execute(
        delete(GenerationHistory).where(
            and_(
                GenerationHistory.project_id == project_id,
                GenerationHistory.chapter_id.in_(chapter_ids),
            )
        )
    )
    await db.execute(delete(AnalysisTask).where(AnalysisTask.chapter_id.in_(chapter_ids)))
    await db.execute(delete(RegenerationTask).where(RegenerationTask.chapter_id.in_(chapter_ids)))
    await db.execute(delete(PlotAnalysis).where(PlotAnalysis.chapter_id.in_(chapter_ids)))
    await db.execute(delete(StoryMemory).where(StoryMemory.chapter_id.in_(chapter_ids)))
    await db.execute(delete(ChapterWorkflowResult).where(ChapterWorkflowResult.chapter_id.in_(chapter_ids)))
    await db.execute(delete(BatchGenerationTask).where(BatchGenerationTask.project_id == project_id))
    await db.execute(delete(NovelWorkflowTask).where(NovelWorkflowTask.project_id == project_id))

    await db.execute(
        update(Chapter)
        .where(Chapter.id.in_(chapter_ids))
        .values(
            content=None,
            summary=None,
            word_count=0,
            status="pending",
            expansion_plan=None,
        )
    )

    current_words_result = await db.execute(
        select(func.coalesce(func.sum(Chapter.word_count), 0))
        .where(Chapter.project_id == project_id)
    )
    current_words = int(current_words_result.scalar_one() or 0)

    await db.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(current_words=current_words)
    )

    await db.commit()

    return {
        "project_id": project_id,
        "project_title": plan["project_title"],
        "applied": True,
        "cleared_chapter_numbers": plan["generated_chapter_numbers"],
        "current_words": current_words,
    }


async def main(args: argparse.Namespace) -> None:
    engine = await get_engine(args.session_user_id)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    vector_cleaner = VectorMemoryCleaner(args.chroma_path)
    execution_summary: list[dict[str, Any]] = []

    async with session_factory() as db:
        for project_id in args.project_id:
            plan = await build_cleanup_plan(db, project_id)
            print(
                json.dumps(
                    {
                        "mode": "dry-run" if not args.apply else "apply",
                        "project_id": plan["project_id"],
                        "project_title": plan["project_title"],
                        "project_user_id": plan["project_user_id"],
                        "generated_chapter_count": plan["generated_chapter_count"],
                        "generated_chapter_numbers": plan["generated_chapter_numbers"],
                        "counts": plan["counts"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

            if not args.apply or not plan["generated_chapters"]:
                execution_summary.append(
                    {
                        "project_id": plan["project_id"],
                        "project_title": plan["project_title"],
                        "applied": False,
                        "reason": "dry_run" if not args.apply else "no_generated_chapters",
                    }
                )
                continue

            vector_result = vector_cleaner.delete_chapter_memories(
                user_id=plan["project_user_id"],
                project_id=plan["project_id"],
                chapter_ids=[item["chapter_id"] for item in plan["generated_chapters"]],
            )
            apply_result = await apply_cleanup(db, plan)
            apply_result["vector_cleanup"] = vector_result
            execution_summary.append(apply_result)

    print(json.dumps({"summary": execution_summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="清理项目中由 AI 续写生成的章节内容及派生数据。"
    )
    parser.add_argument(
        "--project-id",
        action="append",
        required=True,
        help="要清理的项目 ID，可重复传入多个。",
    )
    parser.add_argument(
        "--session-user-id",
        default="maintenance_cleanup",
        help="仅用于创建数据库会话的用户标识，默认 maintenance_cleanup。",
    )
    parser.add_argument(
        "--chroma-path",
        default="data/chroma_db",
        help="ChromaDB 数据目录，默认 data/chroma_db。",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="执行真正清理；不传时仅 dry-run 预览。",
    )
    asyncio.run(main(parser.parse_args()))
