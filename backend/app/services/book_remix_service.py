"""拆书二创服务：整本拆分、预览与创建分析工作台。"""

from __future__ import annotations

import asyncio
import re
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import get_engine
from app.logger import get_logger
from app.models.analysis_task import AnalysisTask
from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan
from app.models.chapter import Chapter
from app.models.memory import PlotAnalysis
from app.models.outline import Outline
from app.models.project import Project
from app.models.project_default_style import ProjectDefaultStyle
from app.models.writing_style import WritingStyle
from app.schemas.book_import import BookImportChapter, BookImportOutline, BookImportWarning, ProjectSuggestion
from app.schemas.book_remix import (
    BookRemixBibleUpdateRequest,
    BookRemixChapterPreview,
    BookRemixCreateProjectRequest,
    BookRemixDeconstructionPack,
    BookRemixInspiredSeedProfile,
    BookRemixPreviewResponse,
    BookRemixSeedMapping,
    BookRemixTaskCreateResponse,
    BookRemixTaskStatusResponse,
    RemixMode,
)
from app.schemas.book_remix_bible import BookRemixContinuationPlanUpdateRequest
from app.services.ai_service import AIService
from app.services.book_import_service import book_import_service
from app.services.book_remix_bible_service import BookRemixBibleService
from app.services.book_remix_continuation_plan_service import BookRemixContinuationPlanService
from app.services.book_remix_continuation_state_service import book_remix_continuation_state_service
from app.services.book_remix_context_service import (
    book_remix_context_service,
    build_remix_continuation_progress_summary,
)
from app.services.source_discovery_service import source_discovery_service
from app.services.source_pattern_pack_prompt import render_source_pattern_pack_digest
from app.services.txt_parser_service import txt_parser_service

REMIX_BIBLE_NON_CONTINUATION_STATUS_CODE = 409
REMIX_BIBLE_EDITABLE_FIELDS: tuple[str, ...] = (
    "character_cards",
    "timeline",
    "story_arcs",
    "foreshadows",
    "hard_constraints",
)
REMIX_CONTINUATION_PLAN_EDITABLE_FIELDS: tuple[str, ...] = (
    "summary",
    "stage_goals",
    "beats",
    "priority_hooks",
    "guardrails",
)

logger = get_logger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

CONTINUATION_WORKBENCH_PREFIX = "[拆书续写工作台]"
INSPIRED_WORKBENCH_PREFIX = "[同类创作工作台]"
REMIX_MODE_META_PREFIX = "[拆书模式]"
REMIX_SOURCE_FILE_META_PREFIX = "[拆书源文件]"
REMIX_SOURCE_CHAPTER_COUNT_META_PREFIX = "[拆书源章节数]"

ORGANIZATION_SUFFIXES = (
    "研究所", "集团", "公司", "学院", "大学", "联邦", "帝国", "王朝",
    "宗门", "宗", "门", "派", "帮", "会", "盟", "阁", "宫", "殿", "司", "局", "团", "队", "府",
)
ABILITY_SUFFIXES = (
    "系统", "异能", "血脉", "灵根", "真气", "灵气", "功法", "心法", "秘术", "术式",
    "回路", "协议", "机甲", "领域", "天赋", "命格", "芯片", "序列", "法则", "能力",
)
WORLD_SUFFIXES = (
    "大陆", "世界", "帝国", "联邦", "王朝", "星域", "星系", "界域", "位面", "秘境", "禁区",
    "都市", "古城", "之城", "之都", "港", "城", "州", "郡", "海", "岛", "山脉", "平原",
)
CHARACTER_STOPWORDS = {
    "自己", "他们", "我们", "你们", "这里", "那里", "这个", "那个", "一种", "已经", "可以", "因为",
    "如果", "只是", "还是", "不是", "没有", "然后", "现在", "突然", "瞬间", "时候", "心中", "目光",
    "声音", "脸色", "身影", "对方", "其中", "所有", "众人", "少年", "少女", "男人", "女人", "老师",
    "师父", "师兄", "师姐", "弟子", "长老", "掌门", "族长", "城主", "皇帝", "皇后",
}


@dataclass
class _BookRemixTask:
    task_id: str
    user_id: str
    filename: str
    remix_mode: RemixMode
    status: str = "pending"
    progress: int = 0
    message: Optional[str] = "任务已创建"
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    preview: Optional[BookRemixPreviewResponse] = None
    normalized_chapters: list[BookImportChapter] = field(default_factory=list)
    normalized_outlines: list[BookImportOutline] = field(default_factory=list)
    cancelled: bool = False


class BookRemixService:
    """拆书二创服务。"""

    def __init__(self) -> None:
        self._tasks: dict[str, _BookRemixTask] = {}
        self._tasks_lock = asyncio.Lock()

    async def create_task(
        self,
        *,
        user_id: str,
        filename: str,
        file_content: bytes,
        remix_mode: RemixMode,
    ) -> BookRemixTaskCreateResponse:
        task_id = str(uuid.uuid4())
        task = _BookRemixTask(
            task_id=task_id,
            user_id=user_id,
            filename=filename,
            remix_mode=remix_mode,
        )

        async with self._tasks_lock:
            self._tasks[task_id] = task

        asyncio.create_task(self._run_pipeline(task_id=task_id, file_content=file_content))
        return BookRemixTaskCreateResponse(task_id=task_id, status="pending", remix_mode=remix_mode)

    async def get_task_status(self, *, task_id: str, user_id: str) -> BookRemixTaskStatusResponse:
        task = await self._get_task(task_id=task_id, user_id=user_id)
        return self._to_status(task)

    async def get_preview(self, *, task_id: str, user_id: str) -> BookRemixPreviewResponse:
        task = await self._get_task(task_id=task_id, user_id=user_id)
        if task.status != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成，无法获取预览")
        if not task.preview:
            raise HTTPException(status_code=500, detail="预览数据不存在")
        return task.preview

    async def cancel_task(self, *, task_id: str, user_id: str) -> dict:
        task = await self._get_task(task_id=task_id, user_id=user_id)
        if task.status in {"completed", "failed", "cancelled"}:
            return {"success": True, "message": f"任务已经处于终态：{task.status}"}

        task.cancelled = True
        self._set_task_state(task, status="cancelled", progress=task.progress, message="任务已取消")
        return {"success": True, "message": "取消成功"}

    async def create_project_from_task(
        self,
        *,
        task_id: str,
        user_id: str,
        payload: BookRemixCreateProjectRequest,
        db: AsyncSession,
        user_ai_service: Optional[AIService] = None,
    ) -> dict:
        task = await self._get_task(task_id=task_id, user_id=user_id)
        if task.status != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成，无法创建项目")
        if not task.normalized_chapters:
            raise HTTPException(status_code=400, detail="拆书结果为空，无法创建项目")

        suggestion = self._build_project_suggestion(
            remix_mode=task.remix_mode,
            filename=task.filename,
            payload=payload.project_suggestion,
        )
        if task.remix_mode == "inspired":
            suggestion.description = await self._merge_inspired_source_pattern_guidance(
                suggestion.description
            )

        project_stub = SimpleNamespace(create_new_project=True, project_id=None)
        project = await book_import_service._prepare_project(
            db=db,
            user_id=user_id,
            task=project_stub,
            suggestion=suggestion,
            chapters=task.normalized_chapters,
            import_mode="append",
        )

        outline_id_map = await book_import_service._import_outlines(
            db=db,
            project_id=project.id,
            outlines=task.normalized_outlines,
            import_mode="append",
        )
        chapter_count, total_words = await book_import_service._import_chapters(
            db=db,
            project_id=project.id,
            chapters=task.normalized_chapters,
            outline_id_map=outline_id_map,
            import_mode="append",
        )

        bible_generation_started = False
        bible_generation_status: Optional[str] = None
        continuation_background_payload: Optional[dict] = None
        prepared_style_id: Optional[int] = None

        if task.remix_mode == "continuation":
            prepared_style_id = await self._apply_continuation_default_style(
                db=db,
                project_id=project.id,
                user_id=user_id,
                source_filename=task.filename,
                chapters=task.normalized_chapters,
                narrative_perspective=suggestion.narrative_perspective,
            )
            bible_generation_started, bible_generation_status = await self._prepare_continuation_bible_generation(
                db=db,
                project_id=project.id,
                source_task_id=task.task_id,
                source_chapters=task.normalized_chapters,
                user_ai_service=user_ai_service,
            )
            if bible_generation_started and user_ai_service is not None:
                continuation_background_payload = {
                    "project_context": {
                        "user_id": user_id,
                        "title": project.title,
                        "theme": project.theme,
                        "genre": project.genre,
                        "narrative_perspective": project.narrative_perspective,
                    },
                    "source_task_id": task.task_id,
                    "source_chapters": [chapter.model_copy(deep=True) for chapter in task.normalized_chapters],
                }

        if task.remix_mode == "inspired":
            prepared_style_id = await self._apply_inspired_default_style(
                db=db,
                project_id=project.id,
                user_id=user_id,
                source_filename=task.filename,
                chapters=task.normalized_chapters,
                narrative_perspective=suggestion.narrative_perspective,
            )

        project.description = self._decorate_project_description(
            description=project.description,
            remix_mode=task.remix_mode,
            source_filename=task.filename,
            source_chapter_count=len(task.normalized_chapters),
        )
        project.current_words = total_words
        project.wizard_step = 3
        project.wizard_status = "completed"
        project.status = "writing"

        await db.commit()
        await db.refresh(project)

        if continuation_background_payload and user_ai_service is not None:
            asyncio.create_task(
                self._run_continuation_bible_generation_background(
                    user_id=user_id,
                    project_id=project.id,
                    project_context=continuation_background_payload["project_context"],
                    source_task_id=continuation_background_payload["source_task_id"],
                    source_chapters=continuation_background_payload["source_chapters"],
                    user_ai_service=user_ai_service,
                )
            )

        return {
            "project_id": project.id,
            "remix_mode": task.remix_mode,
            "total_chapters": chapter_count,
            "total_words": total_words,
            "bible_generation_started": bible_generation_started,
            "bible_generation_status": bible_generation_status,
            "prepared_style_id": prepared_style_id,
        }

    async def refresh_continuation_project(
        self,
        *,
        project: Project,
        user_id: str,
        db: AsyncSession,
        replace_pending_outlines: bool,
    ) -> dict:
        if project.outline_mode != "one-to-one":
            raise HTTPException(status_code=400, detail="当前仅支持传统模式(1→1)的拆书续写项目重建")

        chapter_result = await db.execute(
            select(Chapter)
            .where(Chapter.project_id == project.id)
            .order_by(Chapter.chapter_number)
        )
        chapters = chapter_result.scalars().all()
        if not chapters:
            raise HTTPException(status_code=400, detail="当前项目没有章节，无法重建忠实续写配置")

        source_chapter_count, source_chapters = self._infer_source_chapters_from_project(
            project=project,
            chapters=chapters,
        )
        if not source_chapters:
            raise HTTPException(status_code=400, detail="未找到可用于提炼原书风格的正文章节")

        refreshed_style_id = await self._apply_continuation_default_style(
            db=db,
            project_id=project.id,
            user_id=user_id,
            source_filename=f"{self._extract_source_filename_from_description(project.description) or project.title}.txt",
            chapters=source_chapters,
            narrative_perspective=project.narrative_perspective,
        )

        deleted_chapters = 0
        deleted_outlines = 0
        if replace_pending_outlines:
            deleted_chapters, deleted_outlines = await self._cleanup_pending_continuation_outlines(
                db=db,
                project_id=project.id,
                source_chapter_count=source_chapter_count,
                chapters=chapters,
            )

        project.description = self._decorate_project_description(
            description=project.description,
            remix_mode="continuation",
            source_filename=f"{self._extract_source_filename_from_description(project.description) or project.title}.txt",
            source_chapter_count=source_chapter_count,
        )
        await db.commit()
        await db.refresh(project)

        return {
            "source_chapter_count": source_chapter_count,
            "refreshed_style_id": refreshed_style_id,
            "deleted_chapters": deleted_chapters,
            "deleted_outlines": deleted_outlines,
            "message": (
                f"已重建忠实续写风格，锁定前 {source_chapter_count} 章为原书基准，"
                f"并清理 {deleted_outlines} 条旧续写大纲、{deleted_chapters} 个空章节占位"
                if replace_pending_outlines
                else f"已重建忠实续写风格，锁定前 {source_chapter_count} 章为原书基准"
            ),
        }

    async def get_bible(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> BookRemixBible:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not bible:
            raise HTTPException(status_code=404, detail="remix bible draft not found")
        if self._needs_bible_core_backfill(bible):
            source_chapters, analysis_snapshots = await self._load_bible_backfill_inputs(
                project=project,
                db=db,
            )
            if source_chapters:
                draft_payload = BookRemixBibleService.backfill_missing_sections(
                    project=project,
                    payload={
                        "world_rules": bible.world_rules or {},
                        "character_cards": bible.character_cards or [],
                        "organizations": bible.organizations or [],
                        "timeline": bible.timeline or [],
                        "story_arcs": bible.story_arcs or [],
                        "foreshadows": bible.foreshadows or [],
                        "style_signature": bible.style_signature or {},
                        "hard_constraints": bible.hard_constraints or [],
                        "conflicts": bible.conflicts or [],
                        "generation_notes": bible.generation_notes or [],
                        "chapter_change_packages": bible.chapter_change_packages or [],
                    },
                    source_chapters=source_chapters,
                    analysis_snapshots=analysis_snapshots,
                )
                self._apply_generated_bible_payload(
                    bible=bible,
                    draft_payload=draft_payload,
                )
                await db.commit()
                await db.refresh(bible)
        return bible

    async def update_bible(
        self,
        *,
        project: Project,
        payload: BookRemixBibleUpdateRequest,
        db: AsyncSession,
    ) -> BookRemixBible:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not bible:
            raise HTTPException(status_code=404, detail="remix bible draft not found")

        update_payload = payload.model_dump(exclude_none=True)
        has_update = self._apply_editable_bible_updates(
            bible=bible,
            payload=update_payload,
        )

        if has_update and bible.generation_status == "confirmed":
            bible.generation_status = "generated"
            bible.confirmed_at = None
        if has_update:
            await self._invalidate_project_continuation_plan(
                db=db,
                project_id=project.id,
            )

        await db.commit()
        await db.refresh(bible)
        return bible

    async def confirm_bible(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> BookRemixBible:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not bible:
            raise HTTPException(status_code=400, detail="remix bible draft not found")
        if bible.generation_status not in {"generated", "confirmed"}:
            raise HTTPException(status_code=400, detail="remix bible draft is not ready for confirmation")

        bible.generation_status = "confirmed"
        bible.confirmed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(bible)
        return bible

    async def regenerate_bible(
        self,
        *,
        project: Project,
        db: AsyncSession,
        ai_service: AIService,
    ) -> BookRemixBible:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not bible:
            raise HTTPException(
                status_code=REMIX_BIBLE_NON_CONTINUATION_STATUS_CODE,
                detail="project is not a remix continuation workbench",
            )

        chapter_result = await db.execute(
            select(Chapter)
            .where(Chapter.project_id == project.id)
            .order_by(Chapter.chapter_number)
        )
        chapters = chapter_result.scalars().all()
        if not chapters:
            raise HTTPException(status_code=400, detail="project has no source chapters for bible regeneration")

        source_chapter_count, source_chapters = self._infer_source_chapters_from_project(
            project=project,
            chapters=chapters,
        )
        if not source_chapters:
            raise HTTPException(status_code=400, detail="project has no valid source chapters for bible regeneration")

        _source_chapters_for_backfill, analysis_snapshots = await self._load_bible_backfill_inputs(
            project=project,
            db=db,
        )
        draft_payload = await BookRemixBibleService(ai_service).build_draft_payload(
            project=project,
            source_chapters=source_chapters,
            analysis_snapshots=analysis_snapshots,
        )

        bible.source_chapter_count = source_chapter_count
        self._apply_generated_bible_payload(
            bible=bible,
            draft_payload=draft_payload,
        )
        await self._invalidate_project_continuation_plan(
            db=db,
            project_id=project.id,
        )

        await db.commit()
        await db.refresh(bible)
        return bible

    async def get_continuation_progress_summary(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> dict[str, object]:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not bible:
            raise HTTPException(status_code=404, detail="remix bible draft not found")
        plan = await self._load_project_continuation_plan(db=db, project_id=project.id)
        summary = build_remix_continuation_progress_summary(
            packages=bible.chapter_change_packages or [],
            plan={"beats": plan.beats or []} if plan else None,
        )
        return {"project_id": project.id, **summary}

    async def get_chapter_change_packages(
        self,
        *,
        project: Project,
        db: AsyncSession,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, object]:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not bible:
            raise HTTPException(status_code=404, detail="remix bible draft not found")

        normalized_source = (source or "").strip()
        packages = [
            package
            for package in self._sorted_chapter_change_packages(bible.chapter_change_packages or [])
            if not normalized_source or str(package.get("source") or "").strip() == normalized_source
        ]
        safe_offset = max(0, offset)
        safe_limit = min(max(1, limit), 200)
        return {
            "project_id": project.id,
            "package_count": len(packages),
            "offset": safe_offset,
            "limit": safe_limit,
            "items": packages[safe_offset : safe_offset + safe_limit],
        }

    async def get_analysis_coverage(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> dict[str, object]:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not bible:
            raise HTTPException(status_code=404, detail="remix bible draft not found")

        source_chapter_count = int(bible.source_chapter_count or 0)
        if source_chapter_count <= 0:
            source_chapter_count = self._extract_source_chapter_count_from_description(project.description) or 0

        source_chapters = await self._load_source_chapter_rows(
            project=project,
            db=db,
            source_chapter_count=source_chapter_count,
        )
        source_chapter_numbers = {int(item["chapter_number"]) for item in source_chapters}
        expected_numbers = set(range(1, source_chapter_count + 1)) if source_chapter_count > 0 else set(source_chapter_numbers)

        analyzed_numbers = await self._load_analyzed_chapter_numbers(
            db=db,
            project_id=project.id,
            source_chapter_numbers=source_chapter_numbers,
        )
        package_numbers = self._continuation_context_package_numbers(bible.chapter_change_packages or [])
        running_analysis_numbers = await self._load_running_analysis_chapter_numbers(
            db=db,
            project_id=project.id,
            source_chapter_numbers=source_chapter_numbers,
        )

        missing_source_chapters = sorted(expected_numbers - source_chapter_numbers)
        analyzable_source_chapters = [
            chapter
            for chapter in source_chapters
            if str(chapter.get("content") or "").strip()
        ]
        missing_analysis_chapters = [
            chapter
            for chapter in analyzable_source_chapters
            if int(chapter["chapter_number"]) not in analyzed_numbers
        ]
        missing_change_package_chapters = [
            chapter
            for chapter in analyzable_source_chapters
            if int(chapter["chapter_number"]) not in package_numbers
        ]
        action_plan = self._build_analysis_coverage_action_plan(
            missing_source_chapters=missing_source_chapters,
            source_chapters=source_chapters,
            analyzed_numbers=analyzed_numbers,
            package_numbers=package_numbers,
            running_analysis_numbers=running_analysis_numbers,
        )
        continuation_risk = self._build_continuation_risk_summary(
            missing_source_chapters=missing_source_chapters,
            missing_analysis_chapters=missing_analysis_chapters,
            missing_change_package_chapters=missing_change_package_chapters,
            empty_source_chapter_numbers=[
                int(chapter["chapter_number"])
                for chapter in source_chapters
                if not str(chapter.get("content") or "").strip()
            ],
        )

        source_total = len(source_chapters)
        analyzed_count = len(source_chapter_numbers & analyzed_numbers)
        package_count = len(source_chapter_numbers & package_numbers)
        return {
            "project_id": project.id,
            "source_chapter_count": source_chapter_count,
            "source_chapters_count": source_total,
            "analyzed_chapter_count": analyzed_count,
            "chapter_change_package_count": package_count,
            "analysis_coverage_percent": self._coverage_percent(analyzed_count, source_total),
            "change_package_coverage_percent": self._coverage_percent(package_count, source_total),
            "fully_analyzed": source_total > 0 and analyzed_count == source_total and not missing_source_chapters,
            "fully_synced": source_total > 0 and package_count == source_total and not missing_source_chapters,
            "missing_source_chapters": missing_source_chapters,
            "missing_analysis_chapters": missing_analysis_chapters,
            "missing_change_package_chapters": missing_change_package_chapters,
            "analysis_action_plan": action_plan,
            "continuation_risk": continuation_risk,
        }

    async def get_missing_analysis_targets(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> dict[str, object]:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not bible:
            raise HTTPException(status_code=404, detail="remix bible draft not found")

        source_chapter_count = int(bible.source_chapter_count or 0)
        if source_chapter_count <= 0:
            source_chapter_count = self._extract_source_chapter_count_from_description(project.description) or 0

        chapter_query = (
            select(Chapter)
            .where(Chapter.project_id == project.id)
            .order_by(Chapter.chapter_number)
        )
        if source_chapter_count > 0:
            chapter_query = chapter_query.where(Chapter.chapter_number <= source_chapter_count)

        chapters = (await db.execute(chapter_query)).scalars().all()
        source_chapter_numbers = {int(chapter.chapter_number) for chapter in chapters}
        analyzed_numbers = await self._load_analyzed_chapter_numbers(
            db=db,
            project_id=project.id,
            source_chapter_numbers=source_chapter_numbers,
        )
        package_numbers = self._continuation_context_package_numbers(bible.chapter_change_packages or [])
        missing_numbers = (source_chapter_numbers - analyzed_numbers) | (source_chapter_numbers - package_numbers)

        return {
            "project_id": project.id,
            "source_chapter_count": source_chapter_count,
            "target_chapter_numbers": sorted(missing_numbers),
            "chapters": [
                chapter
                for chapter in chapters
                if int(chapter.chapter_number) in missing_numbers
            ],
        }

    async def sync_existing_source_analysis_to_continuation_state(
        self,
        *,
        project: Project,
        db: AsyncSession,
        targets: Optional[dict[str, object]] = None,
    ) -> dict[str, object]:
        """Sync existing PlotAnalysis rows into confirmed remix continuation state."""
        resolved_targets = targets or await self.get_missing_analysis_targets(project=project, db=db)
        raw_chapters = resolved_targets.get("chapters") if isinstance(resolved_targets, dict) else []
        chapters = [
            chapter
            for chapter in (raw_chapters or [])
            if isinstance(chapter, Chapter)
        ]
        target_chapter_numbers = [int(chapter.chapter_number) for chapter in chapters]
        if not chapters:
            return {
                "project_id": project.id,
                "target_chapter_numbers": [],
                "total_synced_existing": 0,
                "synced_existing_chapters": [],
                "total_already_synced": 0,
                "already_synced_chapters": [],
                "chapters_requiring_analysis": [],
            }

        chapter_ids = [chapter.id for chapter in chapters]
        analysis_result = await db.execute(
            select(PlotAnalysis).where(PlotAnalysis.chapter_id.in_(chapter_ids))
        )
        analysis_map = {
            analysis.chapter_id: analysis
            for analysis in analysis_result.scalars().all()
        }

        synced_existing_chapters: list[int] = []
        already_synced_chapters: list[int] = []
        chapters_requiring_analysis: list[Chapter] = []
        for chapter in chapters:
            analysis = analysis_map.get(chapter.id)
            if not analysis:
                chapters_requiring_analysis.append(chapter)
                continue

            sync_result = await book_remix_continuation_state_service.sync_chapter_analysis(
                db=db,
                project_id=project.id,
                chapter_id=chapter.id,
                chapter_number=int(chapter.chapter_number),
                chapter_title=chapter.title or "",
                analysis_result=self._plot_analysis_to_remix_sync_payload(analysis),
            )
            if sync_result.get("changed"):
                synced_existing_chapters.append(int(chapter.chapter_number))
                continue
            if sync_result.get("reason") == "already_synced":
                already_synced_chapters.append(int(chapter.chapter_number))
                continue
            chapters_requiring_analysis.append(chapter)

        return {
            "project_id": project.id,
            "target_chapter_numbers": target_chapter_numbers,
            "total_synced_existing": len(synced_existing_chapters),
            "synced_existing_chapters": synced_existing_chapters,
            "total_already_synced": len(already_synced_chapters),
            "already_synced_chapters": already_synced_chapters,
            "chapters_requiring_analysis": chapters_requiring_analysis,
        }


    async def get_continuation_context_preview(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> dict[str, object]:
        return await book_remix_context_service.build_project_context_preview(
            project=project,
            db=db,
        )

    async def get_continuation_plan(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> BookRemixContinuationPlan:
        plan = await self._load_project_continuation_plan(db=db, project_id=project.id)
        if not plan:
            raise HTTPException(status_code=404, detail="remix continuation plan not found")
        if self._needs_continuation_plan_backfill(plan):
            bible = await self._load_project_bible(db=db, project_id=project.id)
            payload = BookRemixContinuationPlanService.backfill_missing_sections(
                bible=self._to_plan_bible_payload(bible) if bible else {},
                payload={
                    "summary": plan.summary or "",
                    "stage_goals": plan.stage_goals or [],
                    "beats": plan.beats or [],
                    "priority_hooks": plan.priority_hooks or [],
                    "guardrails": plan.guardrails or [],
                },
            )
            self._apply_continuation_plan_payload(
                plan=plan,
                payload=payload,
                reset_status=False,
            )
            await db.commit()
            await db.refresh(plan)
        return plan

    async def generate_continuation_plan(
        self,
        *,
        project: Project,
        db: AsyncSession,
        ai_service: AIService,
        user_direction: str = "",
    ) -> BookRemixContinuationPlan:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not bible or bible.generation_status != "confirmed":
            raise HTTPException(status_code=400, detail="confirmed remix bible required before plan generation")

        try:
            plan_payload = await BookRemixContinuationPlanService(ai_service).build_plan_payload(
                project_title=project.title,
                bible=self._to_plan_bible_payload(bible),
                user_direction=user_direction,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        plan = await self._load_project_continuation_plan(db=db, project_id=project.id)
        if not plan:
            plan = BookRemixContinuationPlan(project_id=project.id)
            db.add(plan)

        plan.bible_id = bible.id
        self._apply_continuation_plan_payload(
            plan=plan,
            payload=plan_payload,
            reset_status=True,
        )

        await db.commit()
        await db.refresh(plan)
        return plan

    async def update_continuation_plan(
        self,
        *,
        project: Project,
        payload: BookRemixContinuationPlanUpdateRequest,
        db: AsyncSession,
    ) -> BookRemixContinuationPlan:
        plan = await self._load_project_continuation_plan(db=db, project_id=project.id)
        if not plan:
            raise HTTPException(status_code=404, detail="remix continuation plan not found")

        update_payload = payload.model_dump(exclude_none=True)
        has_update = self._apply_editable_continuation_plan_updates(
            plan=plan,
            payload=update_payload,
        )

        if has_update and plan.status == "confirmed":
            plan.status = "draft"
            plan.confirmed_at = None

        await db.commit()
        await db.refresh(plan)
        return plan

    async def confirm_continuation_plan(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> BookRemixContinuationPlan:
        plan = await self._load_project_continuation_plan(db=db, project_id=project.id)
        if not plan:
            raise HTTPException(status_code=400, detail="remix continuation plan not found")

        bible = await self._load_project_bible(db=db, project_id=project.id)
        if not self._is_continuation_plan_current_for_bible(plan=plan, bible=bible):
            raise HTTPException(
                status_code=409,
                detail=(
                    "remix continuation plan is stale against the current bible; "
                    "regenerate the plan from the latest confirmed bible before confirmation"
                ),
            )

        plan.status = "confirmed"
        plan.confirmed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(plan)
        await self.sync_existing_source_analysis_to_continuation_state(project=project, db=db)
        await db.refresh(plan)
        return plan

    async def prepare_project_continuation_style(
        self,
        *,
        project: Project,
        user_id: str,
        db: AsyncSession,
    ) -> Optional[int]:
        """为通用续写流程提炼或刷新项目默认的忠实续写风格。"""
        chapter_result = await db.execute(
            select(Chapter)
            .where(Chapter.project_id == project.id)
            .order_by(Chapter.chapter_number)
        )
        chapters = chapter_result.scalars().all()
        if not chapters:
            return None

        _, source_chapters = self._infer_source_chapters_from_project(
            project=project,
            chapters=chapters,
        )
        if not source_chapters:
            return None

        source_filename = f"{self._extract_source_filename_from_description(project.description) or project.title}.txt"
        return await self._apply_continuation_default_style(
            db=db,
            project_id=project.id,
            user_id=user_id,
            source_filename=source_filename,
            chapters=source_chapters,
            narrative_perspective=project.narrative_perspective,
        )

    async def _run_pipeline(self, *, task_id: str, file_content: bytes) -> None:
        task = self._tasks.get(task_id)
        if not task:
            return

        try:
            self._set_task_state(task, status="running", progress=5, message="正在识别编码并读取整本 TXT")
            self._check_cancelled(task)

            text, encoding = txt_parser_service.decode_bytes(file_content)
            cleaned = txt_parser_service.clean_text(text)

            self._set_task_state(
                task,
                status="running",
                progress=12,
                message=f"文本清洗完成，当前编码：{encoding}",
            )
            self._check_cancelled(task)

            chapters_data = txt_parser_service.split_chapters(cleaned)
            if not chapters_data:
                raise ValueError("未能识别到有效章节，请检查 TXT 内容")

            self._set_task_state(
                task,
                status="running",
                progress=20,
                message=f"已识别 {len(chapters_data)} 个章节，正在构建整本预览",
            )
            preview = await self._build_preview(task=task, chapters_data=chapters_data)

            self._check_cancelled(task)
            task.preview = preview
            self._set_task_state(task, status="completed", progress=100, message="整本拆书完成，可以创建二创工作台")
        except asyncio.CancelledError:
            self._set_task_state(task, status="cancelled", progress=task.progress, message="任务已取消")
        except Exception as exc:
            logger.error("拆书二创任务失败 task_id=%s: %s", task_id, exc, exc_info=True)
            self._set_task_state(
                task,
                status="failed",
                progress=task.progress,
                message="解析失败",
                error=str(exc),
            )

    async def _build_preview(
        self,
        *,
        task: _BookRemixTask,
        chapters_data: list[dict],
    ) -> BookRemixPreviewResponse:
        default_title = self._build_default_title(task.filename, task.remix_mode)
        suggestion = ProjectSuggestion(
            title=default_title,
            description=self._build_description_prefix(task.remix_mode),
            theme=None,
            genre=None,
            narrative_perspective="第三人称",
            target_words=120000,
        )

        normalized_chapters: list[BookImportChapter] = []
        normalized_outlines: list[BookImportOutline] = []
        preview_chapters: list[BookRemixChapterPreview] = []
        warnings: list[BookImportWarning] = []
        total_words = 0
        title_seen: set[str] = set()
        total_chapter_count = len(chapters_data)

        for idx, chapter in enumerate(chapters_data, start=1):
            raw_title = (chapter.get("title") or f"第{idx}章").strip()[:200]
            title = book_import_service._strip_chapter_prefix(raw_title)[:200]
            content = (chapter.get("content") or "").strip()
            summary = book_import_service._build_summary(content, max_len=160)
            word_count = len(re.sub(r"\s+", "", content))

            if title in title_seen:
                title = f"{title}-{idx}"
            title_seen.add(title)

            normalized_chapter = BookImportChapter(
                title=title,
                content=content,
                summary=summary,
                chapter_number=idx,
                outline_title=title,
            )
            normalized_outline = BookImportOutline(
                title=title,
                content=summary,
                order_index=idx,
                structure=book_import_service._build_fallback_outline_structure(normalized_chapter),
            )

            normalized_chapters.append(normalized_chapter)
            normalized_outlines.append(normalized_outline)
            preview_chapters.append(
                BookRemixChapterPreview(
                    title=title,
                    chapter_number=idx,
                    word_count=word_count,
                    summary=summary,
                )
            )
            total_words += word_count

            if len(content) < 300:
                warnings.append(
                    BookImportWarning(
                        code="chapter_too_short",
                        message=f"第 {idx} 章《{title}》内容较短，建议确认切分结果",
                        level="warning",
                    )
                )

            if idx % max(1, total_chapter_count // 8) == 0 or idx == total_chapter_count:
                progress = 20 + int(25 * idx / max(1, total_chapter_count))
                self._set_task_state(
                    task,
                    status="running",
                    progress=progress,
                    message=f"已整理 {idx}/{total_chapter_count} 个章节",
                )

        if len(normalized_chapters) > 120:
            warnings.append(
                BookImportWarning(
                    code="large_book_detected",
                    message=(
                        f"本次识别到 {len(normalized_chapters)} 章，创建工作台后会自动按顺序启动全书分析，"
                        "请耐心等待。"
                    ),
                    level="info",
                )
            )

        if total_words > 800000:
            warnings.append(
                BookImportWarning(
                    code="large_word_count_detected",
                    message="全文字数较多，建议先完成自动分析，再开始续写或同类创作。",
                    level="info",
                )
            )

        self._set_task_state(task, status="running", progress=50, message="正在提炼作品主题与类型")
        suggestion = await book_import_service._generate_reverse_project_suggestion(
            user_id=task.user_id,
            suggestion=suggestion,
            chapters=normalized_chapters,
            task=task,  # type: ignore[arg-type]
        )
        suggestion.title = suggestion.title[:200] if suggestion.title else default_title
        suggestion.description = self._merge_description(task.remix_mode, suggestion.description)

        task.normalized_chapters = normalized_chapters
        task.normalized_outlines = normalized_outlines
        inspired_seed_profile = (
            self._build_inspired_seed_profile(normalized_chapters)
            if task.remix_mode == "inspired"
            else None
        )
        deconstruction_pack = self._build_deconstruction_pack(
            remix_mode=task.remix_mode,
            source_filename=task.filename,
            chapters=normalized_chapters,
            total_words=total_words,
            inspired_seed_profile=inspired_seed_profile,
        )

        return BookRemixPreviewResponse(
            task_id=task.task_id,
            remix_mode=task.remix_mode,
            project_suggestion=suggestion,
            detected_total_chapters=len(normalized_chapters),
            total_words=total_words,
            chapters=preview_chapters,
            warnings=warnings,
            inspired_seed_profile=inspired_seed_profile,
            deconstruction_pack=deconstruction_pack,
        )

    def _build_deconstruction_pack(
        self,
        *,
        remix_mode: RemixMode,
        source_filename: str,
        chapters: list[BookImportChapter],
        total_words: int,
        inspired_seed_profile: Optional[BookRemixInspiredSeedProfile],
    ) -> BookRemixDeconstructionPack:
        """Build a deterministic review packet before continuation or same-type drafting."""

        valid_chapters = [chapter for chapter in chapters if (chapter.content or "").strip()]
        first_chapter = valid_chapters[0] if valid_chapters else None
        last_chapter = valid_chapters[-1] if valid_chapters else None
        average_words = int(total_words / max(1, len(valid_chapters))) if valid_chapters else 0
        dialogue_density = round(self._estimate_dialogue_ratio(valid_chapters), 4) if valid_chapters else 0.0
        sampled_chapters = self._select_deconstruction_evidence_chapters(valid_chapters)
        chapter_summaries = [
            {
                "chapter": f"Ch{chapter.chapter_number}",
                "title": chapter.title,
                "summary": self._safe_summary(chapter),
            }
            for chapter in sampled_chapters
        ]

        last_summary = self._safe_summary(last_chapter) if last_chapter else ""
        first_summary = self._safe_summary(first_chapter) if first_chapter else ""
        chapter_mode = "continue-chapter" if remix_mode == "continuation" else "full-project"
        opening_hook = (
            f"Continue from Ch{last_chapter.chapter_number}: {last_summary[:120]}"
            if last_chapter
            else "Build from accepted source scope after review"
        )
        reader_promise = self._infer_reader_promise_from_chapters(valid_chapters)
        source_names = self._collect_inspired_source_names(inspired_seed_profile)
        scene_beat_sheet = self._build_deconstruction_scene_beat_sheet(
            remix_mode=remix_mode,
            last_summary=last_summary,
            reader_promise=reader_promise,
        )
        reader_pull_checklist = [
            "Who is the POV character?",
            "What do they want now?",
            "What blocks them?",
            "Why does it matter?",
            "What changed by the end?",
            "What question or desire pulls me onward?",
        ]
        hook_payoff_matrix = self._build_deconstruction_hook_payoff_matrix(
            chapters=valid_chapters,
            opening_hook=opening_hook,
        )
        progress_report_contract = {
            "required_fields": [
                "chapter",
                "summary",
                "new_facts",
                "character_changes",
                "relationship_changes",
                "organization_changes",
                "hooks_paid_off",
                "new_hooks",
                "continuity_updates",
                "next_chapter_focus",
                "risks",
            ],
            "promotion_rule": "No generated chapter is accepted until manuscript text and progress report agree.",
            "writeback_order": [
                "chapter_text",
                "chapter_progress_report",
                "continuity_ledger",
                "bible_or_plan_delta",
                "next_chapter_contract",
            ],
        }
        revision_strategy = self._build_deconstruction_revision_strategy()
        craft_surface_contract = self._build_deconstruction_craft_surface_contract(
            remix_mode=remix_mode,
        )

        same_type_boundaries = {
            "mode": remix_mode,
            "required_difference_axes": (
                [
                    "fresh_characters",
                    "fresh_organizations",
                    "fresh_world_rules",
                    "fresh_event_order",
                    "fresh_core_conflict",
                ]
                if remix_mode == "inspired"
                else ["not_applicable_for_continuation"]
            ),
            "must_replace_elements": source_names,
            "transferable_patterns": [
                "reader promise / genre pleasure",
                "chapter-level conflict density",
                "scene goal-obstacle-cost rhythm",
                "dialogue-to-narration balance",
                "hook/payoff pacing",
            ],
            "high_risk_similarity": [
                item.source_name
                for item in (inspired_seed_profile.plot_threads if inspired_seed_profile else [])
                if item.source_name
            ],
            "copy_risk_checks": [
                "protected_expression",
                "proper_name_reuse",
                "scene_order_clone",
                "dialogue_paraphrase",
                "source_entity_graph_clone",
            ],
        }

        confidence_score = 0
        if len(valid_chapters) >= 3:
            confidence_score += 1
        if total_words >= 3000:
            confidence_score += 1
        if chapter_summaries:
            confidence_score += 1
        if remix_mode == "inspired" and source_names:
            confidence_score += 1
        confidence_level = "high" if confidence_score >= 3 else "medium" if confidence_score >= 2 else "low"

        return BookRemixDeconstructionPack(
            source_scope={
                "source_filename": source_filename,
                "mode": remix_mode,
                "chapter_count": len(valid_chapters),
                "total_words": total_words,
                "average_chapter_words": average_words,
                "first_chapter": (
                    {"number": first_chapter.chapter_number, "title": first_chapter.title}
                    if first_chapter
                    else None
                ),
                "last_chapter": (
                    {"number": last_chapter.chapter_number, "title": last_chapter.title, "summary": last_summary}
                    if last_chapter
                    else None
                ),
            },
            story_promise={
                "inferred_reader_promise": reader_promise,
                "opening_situation": first_summary,
                "current_pressure": last_summary,
                "micro_payoff_policy": "Each generated chapter must change plot, relationship, knowledge, status, risk, or emotional position.",
            },
            style_fingerprint={
                "narrative_perspective": "use project suggestion unless author overrides",
                "average_chapter_words": average_words,
                "dialogue_density": dialogue_density,
                "pacing_note": self._build_language_note(avg_words=average_words, dialogue_ratio=dialogue_density),
                "prose_constraints": [
                    "preserve concrete action and sensory detail at turning points",
                    "avoid generic emotion labels and summary-like AI texture",
                    "vary sentence rhythm without copying source phrases",
                ],
            },
            continuity_ledger={
                "required_ledgers": [
                    "timeline",
                    "character_state",
                    "relationship_state",
                    "organization_state",
                    "world_rules",
                    "foreshadowing_and_payoff",
                    "unresolved_questions",
                ],
                "progress_writeback": [
                    "chapter_log",
                    "new_facts",
                    "character_changes",
                    "hooks_paid_off",
                    "new_hooks",
                    "next_chapter_focus",
                    "risks",
                ],
                "authoritative_source": "accepted imported chapters plus reviewed bible and continuation plan",
            },
            chapter_contract={
                "mode": chapter_mode,
                "chapter_job": "continue accepted causal pressure" if remix_mode == "continuation" else "create an independent same-type premise before drafting",
                "opening_hook": opening_hook,
                "main_goal": "derive from last accepted chapter pressure" if remix_mode == "continuation" else "prove a fresh premise without source-entity reuse",
                "main_obstacle": "active opposition or consequence must block the goal",
                "turning_point": "one decision, reveal, cost, or status shift changes the chapter direction",
                "required_reveal_or_payoff": "pay off or complicate at least one accepted hook",
                "ending_hook": "end on consequence, choice, danger, or reframed fact; no fake cliffhanger",
                "scene_plan": "3-7 scenes; each scene needs goal, obstacle, turn, cost, and exit state",
                "reader_pull": "first 20% must show pressure, question, desire, or consequence",
                "forbidden_shortcuts": [
                    "off-screen payoff",
                    "state reset",
                    "unearned relationship jump",
                    "new rule without cost",
                    "chapter ending with fake cliffhanger only",
                ],
            },
            craft_surface_contract=craft_surface_contract,
            scene_beat_sheet=scene_beat_sheet,
            reader_pull_checklist=reader_pull_checklist,
            hook_payoff_matrix=hook_payoff_matrix,
            progress_report_contract=progress_report_contract,
            same_type_boundaries=same_type_boundaries,
            revision_gates=[
                {
                    "name": "developmental",
                    "checks": ["visible goal", "active opposition", "escalating stakes", "earned payoff"],
                },
                {
                    "name": "character_continuity",
                    "checks": ["want/need/wound", "voice fingerprint", "relationship movement", "no OOC convenience"],
                },
                {
                    "name": "continuity",
                    "checks": ["timeline", "names", "facts", "world rules", "who knows what", "open hooks"],
                },
                {
                    "name": "anti_ai_naturalness",
                    "checks": ["concrete action", "subtext", "uneven rhythm", "specific sensory detail", "mobile-readable paragraphs"],
                },
            ],
            revision_strategy=revision_strategy,
            evidence_chapters=chapter_summaries,
            confidence={
                "level": confidence_level,
                "score": confidence_score,
                "limits": [
                    "deterministic preview only; human review still owns canon acceptance",
                    "style fingerprint is statistical and craft-level, not permission to copy expression",
                ],
            },
        )

    def _build_deconstruction_revision_strategy(self) -> dict[str, Any]:
        """Build revision order and patch policy from the local universal writing reference."""
        return {
            "ordered_passes": [
                "developmental",
                "character",
                "continuity",
                "scene",
                "line",
                "proof_format",
            ],
            "severity_scale": {
                "critical": "breaks canon, core story logic, or continuation viability",
                "high": "damages stakes, character trust, reader understanding, or major payoff",
                "medium": "weakens pacing, scene clarity, prose force, or emotional impact",
                "low": "local wording, formatting, repetition, or proof-level issue",
            },
            "patch_policy": [
                "fix structure before line polish",
                "smallest_failing_artifact",
                "patch the smallest_failing_artifact first: ledger field, contract field, scene, paragraph, or sentence",
                "do not overwrite accepted manuscript text unless the user explicitly chooses rewrite mode",
                "after repair, rerun the affected continuity, reader-pull, hook/payoff, and naturalness gate",
            ],
            "anti_ai_naturalness_fixes": [
                "concrete_action",
                "sensory_pressure",
                "character_specific_diction",
                "subtext_or_avoidance",
                "uneven_human_rhythm",
                "mobile_readable_paragraph_breaks",
            ],
        }

    def _build_deconstruction_craft_surface_contract(self, *, remix_mode: RemixMode) -> dict[str, Any]:
        """Build scene-surface craft checks from the local universal writing reference."""
        same_type_rule = (
            "Transfer only surface-craft functions; rebuild POV filter, dialogue tactic, sensory job, "
            "and show/tell allocation for the target story."
            if remix_mode == "inspired"
            else "Use accepted target canon, POV state, and current scene pressure as the only source "
            "for surface-craft choices."
        )
        return {
            "pov_filter": [
                "observations pass through desire, fear, expertise, and bias",
                "no fact enters narration if the POV cannot know or plausibly infer it",
            ],
            "show_tell_allocation": {
                "dramatize": ["turning_points", "conflict", "emotions", "choices"],
                "summarize": ["low_value_transitions", "repeated_logistics", "already_understood_context"],
            },
            "dialogue_subtext": [
                "each exchange pursues a goal, hides pain, tests loyalty, or changes status",
                "avoid as-you-know exposition and polished synopsis dialogue",
            ],
            "description_jobs": [
                "mood",
                "threat",
                "character_pressure",
                "class_or_history",
                "world_rule",
                "foreshadowing",
            ],
            "same_type_rule": same_type_rule,
        }

    def _build_deconstruction_scene_beat_sheet(
        self,
        *,
        remix_mode: RemixMode,
        last_summary: str,
        reader_promise: list[str],
    ) -> list[dict[str, Any]]:
        opening_goal = (
            "resume the last accepted causal pressure"
            if remix_mode == "continuation"
            else "establish the independent protagonist and fresh promise"
        )
        opening_obstacle = (
            last_summary[:120] or "missing prior-pressure summary; reviewer must fill before drafting"
            if remix_mode == "continuation"
            else "source resemblance risk; prove new names, rules, conflict, and event order"
        )
        return [
            {
                "scene": 1,
                "function": "opening_hook",
                "goal": opening_goal,
                "obstacle": opening_obstacle,
                "turn": "pressure becomes concrete in action or dialogue",
                "cost": "the POV loses comfort, time, leverage, or certainty",
                "exit_state": "reader can name the immediate question and stakes",
            },
            {
                "scene": 2,
                "function": "escalation",
                "goal": "pursue the chapter objective through a tactic",
                "obstacle": "opposition adapts instead of waiting",
                "turn": "new information changes the tactic",
                "cost": "relationship, status, resource, safety, or emotional position shifts",
                "exit_state": "the board is different from the opening",
            },
            {
                "scene": 3,
                "function": "payoff_and_next_hook",
                "goal": "pay off, twist, or deliberately defer one promise",
                "obstacle": ", ".join(reader_promise[:2]) if reader_promise else "reader promise must stay visible",
                "turn": "choice, reveal, consequence, or reframed fact",
                "cost": "a future obligation or unresolved risk remains",
                "exit_state": "next chapter contract has a clear start point",
            },
        ]

    def _build_deconstruction_hook_payoff_matrix(
        self,
        *,
        chapters: list[BookImportChapter],
        opening_hook: str,
        max_items: int = 6,
    ) -> dict[str, Any]:
        recent = chapters[-max_items:] if chapters else []
        seeded_threads = [
            {
                "thread": f"Ch{chapter.chapter_number}: {chapter.title}",
                "seeded_in": f"Ch{chapter.chapter_number}",
                "reader_expectation": self._safe_summary(chapter),
                "planned_payoff": "answer, complicate, or escalate before the thread goes stale",
                "status": "open",
            }
            for chapter in recent
            if self._safe_summary(chapter)
        ]
        return {
            "opening_thread": opening_hook,
            "seeded_threads": seeded_threads,
            "delay_rule": "Every carried hook needs answer, partial answer, escalation, or explicit deferral reason.",
            "same_type_rule": "For inspired mode, transfer hook function only; replace names, scene order, evidence, and payoff mechanism.",
        }

    def _select_deconstruction_evidence_chapters(
        self,
        chapters: list[BookImportChapter],
        *,
        max_items: int = 8,
    ) -> list[BookImportChapter]:
        if len(chapters) <= max_items:
            return chapters

        indexes = {0, len(chapters) - 1, len(chapters) // 2}
        step = max(1, len(chapters) // max_items)
        indexes.update(range(0, len(chapters), step))
        return [chapters[index] for index in sorted(indexes)[:max_items]]

    def _infer_reader_promise_from_chapters(self, chapters: list[BookImportChapter]) -> list[str]:
        text = self._collect_seed_sample_text(chapters).lower()
        promise_markers: list[tuple[str, tuple[str, ...]]] = [
            ("mystery / unresolved question", ("谜", "秘密", "真相", "线索", "question", "secret")),
            ("romance / relationship pressure", ("喜欢", "恋", "心动", "误会", "relationship", "love")),
            ("progression / public proof", ("升级", "突破", "证明", "出道", "晋升", "progression")),
            ("survival / danger", ("危险", "追杀", "逃", "威胁", "survival", "danger")),
            ("organization / faction conflict", ("公司", "公会", "组织", "学院", "团队", "faction")),
        ]
        matches = [
            label
            for label, markers in promise_markers
            if any(marker.lower() in text for marker in markers)
        ]
        return matches[:4] or ["reader-pull through conflict, consequence, and hook/payoff"]

    def _collect_inspired_source_names(
        self,
        inspired_seed_profile: Optional[BookRemixInspiredSeedProfile],
        *,
        max_items: int = 24,
    ) -> list[str]:
        if not inspired_seed_profile:
            return []

        names: list[str] = []
        for mappings in (
            inspired_seed_profile.characters,
            inspired_seed_profile.organizations,
            inspired_seed_profile.abilities,
            inspired_seed_profile.world_elements,
            inspired_seed_profile.plot_threads,
        ):
            for item in mappings:
                source_name = (item.source_name or "").strip()
                if source_name and source_name not in names:
                    names.append(source_name)
                if len(names) >= max_items:
                    return names
        return names

    def _build_inspired_seed_profile(
        self,
        chapters: list[BookImportChapter],
    ) -> BookRemixInspiredSeedProfile:
        sample_text = self._collect_seed_sample_text(chapters)
        organizations = self._extract_named_candidates(
            text=sample_text,
            pattern=r"([一-龥A-Za-z0-9]{2,16}(?:研究所|集团|公司|学院|大学|联邦|帝国|王朝|宗门|宗|门|派|帮|会|盟|阁|宫|殿|司|局|团|队|府))",
            min_count=2,
            max_items=8,
            rewrite_hint="为这个组织重新命名，并改写其定位、势力结构或目标。",
        )
        organization_names = {item.source_name for item in organizations}

        abilities = self._extract_named_candidates(
            text=sample_text,
            pattern=r"([一-龥A-Za-z0-9]{2,16}(?:系统|异能|血脉|灵根|真气|灵气|功法|心法|秘术|术式|回路|协议|机甲|领域|天赋|命格|芯片|序列|法则|能力))",
            min_count=2,
            max_items=8,
            rewrite_hint="替换为新的能力名词，并重写升级逻辑或使用代价。",
            excluded_names=organization_names,
        )
        ability_names = {item.source_name for item in abilities}

        world_elements = self._extract_named_candidates(
            text=sample_text,
            pattern=r"([一-龥A-Za-z0-9]{2,16}(?:大陆|世界|帝国|联邦|王朝|星域|星系|界域|位面|秘境|禁区|都市|古城|之城|之都|港|城|州|郡|海|岛|山脉|平原))",
            min_count=2,
            max_items=8,
            rewrite_hint="调整地理背景、权力格局或世界规则，不要直接沿用原设定。",
            excluded_names=organization_names | ability_names,
        )
        world_names = {item.source_name for item in world_elements}

        characters = self._extract_character_candidates(
            text=sample_text,
            max_items=8,
            excluded_names=organization_names | ability_names | world_names,
        )

        return BookRemixInspiredSeedProfile(
            characters=characters,
            organizations=organizations,
            abilities=abilities,
            world_elements=world_elements,
            plot_threads=self._extract_plot_threads(chapters),
        )

    def _collect_seed_sample_text(self, chapters: list[BookImportChapter]) -> str:
        fragments: list[str] = []
        for chapter in chapters[:60]:
            if chapter.title:
                fragments.append(chapter.title)
            if chapter.summary:
                fragments.append(chapter.summary[:200])
            if chapter.content:
                fragments.append(chapter.content[:600])
        return "\n".join(fragment for fragment in fragments if fragment)

    def _extract_named_candidates(
        self,
        *,
        text: str,
        pattern: str,
        min_count: int,
        max_items: int,
        rewrite_hint: str,
        excluded_names: Optional[set[str]] = None,
    ) -> list[BookRemixSeedMapping]:
        counter: Counter[str] = Counter()
        contexts: dict[str, str] = {}
        excluded = excluded_names or set()

        for match in re.finditer(pattern, text):
            candidate = self._normalize_candidate(match.group(1))
            if not candidate or candidate in excluded:
                continue
            if self._should_skip_seed_candidate(candidate):
                continue
            counter[candidate] += 1
            contexts.setdefault(candidate, self._short_context(match.group(0)))

        results: list[BookRemixSeedMapping] = []
        for candidate, count in counter.most_common():
            if count < min_count:
                continue
            results.append(
                BookRemixSeedMapping(
                    source_name=candidate,
                    occurrence_count=count,
                    sample_context=contexts.get(candidate),
                    rewrite_hint=rewrite_hint,
                )
            )
            if len(results) >= max_items:
                break

        return results

    def _extract_character_candidates(
        self,
        *,
        text: str,
        max_items: int,
        excluded_names: set[str],
    ) -> list[BookRemixSeedMapping]:
        counter: Counter[str] = Counter()
        contexts: dict[str, str] = {}
        patterns = [
            r"([一-龥]{2,4})(?:说道|说着|说|问道|问|答道|冷笑道|低声道|怒喝道|看向|看着|盯着|望着|来到|走进|抬头|转身|皱眉|点头)",
            r"(?:对|向|跟)([一-龥]{2,4})(?:说|问|喊|点头|走去)",
            r"([一-龥]{2,4})(?:的目光|的声音|的身影|的手指|心中一动|心头一震)",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text):
                candidate = self._normalize_candidate(match.group(1))
                if not candidate or candidate in excluded_names:
                    continue
                if not re.fullmatch(r"[一-龥]{2,4}", candidate):
                    continue
                if candidate in CHARACTER_STOPWORDS:
                    continue
                if self._looks_like_non_character(candidate):
                    continue

                counter[candidate] += 1
                contexts.setdefault(candidate, self._short_context(match.group(0)))

        results: list[BookRemixSeedMapping] = []
        for candidate, count in counter.most_common():
            if count < 2:
                continue
            results.append(
                BookRemixSeedMapping(
                    source_name=candidate,
                    occurrence_count=count,
                    sample_context=contexts.get(candidate),
                    rewrite_hint="为该人物重新命名，并改写其身份关系或核心性格抓手。",
                )
            )
            if len(results) >= max_items:
                break

        return results

    def _build_forbidden_source_name_lines(
        self,
        chapters: list[BookImportChapter],
        *,
        max_items: int = 18,
    ) -> list[str]:
        profile = self._build_inspired_seed_profile(chapters)
        names: list[str] = []
        for mappings in (
            profile.characters,
            profile.organizations,
            profile.abilities,
            profile.world_elements,
        ):
            for item in mappings:
                source_name = (item.source_name or "").strip()
                if source_name and source_name not in names:
                    names.append(source_name)

        if not names:
            return []

        return [
            "以下名称只能作为改造参考，正文不得原样沿用：",
            f"- {', '.join(names[:max_items])}",
        ]

    def _extract_plot_threads(self, chapters: list[BookImportChapter]) -> list[BookRemixSeedMapping]:
        if not chapters:
            return []

        results: list[BookRemixSeedMapping] = []
        step = max(1, len(chapters) // 6)
        seen_titles: set[str] = set()

        for index in range(0, len(chapters), step):
            chapter = chapters[index]
            title = self._normalize_candidate(chapter.title)
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            context = (chapter.summary or chapter.content[:120]).strip()[:140] or None
            results.append(
                BookRemixSeedMapping(
                    source_name=title,
                    occurrence_count=1,
                    sample_context=context,
                    rewrite_hint="改写这一段剧情的触发事件、冲突对象或结局落点。",
                )
            )
            if len(results) >= 6:
                break

        return results

    def _normalize_candidate(self, value: str) -> str:
        return re.sub(r"\s+", "", (value or "").strip("「」『』《》〈〉()（）[]【】,，。！？；：、\"'")).strip()

    def _short_context(self, value: str) -> str:
        normalized = re.sub(r"\s+", " ", value).strip()
        return normalized[:120]

    def _should_skip_seed_candidate(self, candidate: str) -> bool:
        if len(candidate) < 2 or len(candidate) > 16:
            return True
        if candidate in CHARACTER_STOPWORDS:
            return True
        if candidate.startswith(("这个", "那个", "一种", "一座", "一名", "一位", "一个")):
            return True
        return False

    def _looks_like_non_character(self, candidate: str) -> bool:
        if any(candidate.endswith(suffix) for suffix in ORGANIZATION_SUFFIXES):
            return True
        if any(candidate.endswith(suffix) for suffix in ABILITY_SUFFIXES):
            return True
        if any(candidate.endswith(suffix) for suffix in WORLD_SUFFIXES):
            return True
        return False

    def _build_default_title(self, filename: str, remix_mode: RemixMode) -> str:
        suffix = "拆书续写工作台" if remix_mode == "continuation" else "同类创作工作台"
        base_title = Path(filename).stem[:160] or "拆书二创"
        return f"{base_title} - {suffix}"[:200]

    def _build_description_prefix(self, remix_mode: RemixMode) -> str:
        if remix_mode == "continuation":
            return "基于原书整本拆分后创建的续写工作台，将自动沉淀章节分析、人物关系与剧情记忆。"
        return "基于原书整本拆分后创建的同类创作工作台，将自动沉淀人物、世界观与剧情结构画像。"

    def _merge_description(self, remix_mode: RemixMode, description: Optional[str]) -> str:
        prefix = "[拆书续写工作台] " if remix_mode == "continuation" else "[同类创作工作台] "
        normalized = (description or "").strip()
        if normalized.startswith(prefix):
            return normalized[:500]
        if not normalized:
            return f"{prefix}{self._build_description_prefix(remix_mode)}"[:500]
        return f"{prefix}{normalized}"[:500]

    async def _merge_inspired_source_pattern_guidance(self, description: Optional[str]) -> str:
        source_pattern_pack = await source_discovery_service.resolve_fresh_pattern_pack(
            repo_root=PROJECT_ROOT,
        )
        digest = render_source_pattern_pack_digest(
            source_pattern_pack,
            empty_message="",
        ).strip()
        if not digest:
            return (description or "")[:2000]

        guidance = (
            "\n\n[\u516c\u5f00\u6765\u6e90\u6a21\u5f0f\u5305]\n"
            "\u540c\u7c7b\u521b\u4f5c\u5fc5\u987b\u6d88\u8d39\u8fd9\u4e9b\u516c\u5f00\u6765\u6e90\u6c89\u6dc0\u51fa\u7684\u6d41\u7a0b\u63d0\u793a\uff1a\u65e2\u4fdd\u7559\u539f\u4e66\u5473\u9053\u3001\u4e16\u754c\u89c2/\u4eba\u7269/\u7ec4\u7ec7/\u65f6\u95f4\u7ebf/\u98ce\u683c\u7b7e\u540d\uff0c"
            "\u53c8\u907f\u514d\u7167\u642c\u539f\u4e66\u547d\u540d\u3001\u4e8b\u4ef6\u987a\u5e8f\u548c\u5916\u90e8\u9879\u76ee\u4ee3\u7801\u3002\n"
            f"{digest}"
        )
        merged = f"{(description or '').strip()}{guidance}".strip()
        return merged[:2000]

    def _build_project_suggestion(
        self,
        *,
        remix_mode: RemixMode,
        filename: str,
        payload: ProjectSuggestion,
    ) -> ProjectSuggestion:
        title = (payload.title or self._build_default_title(filename, remix_mode)).strip()[:200]
        return ProjectSuggestion(
            title=title or self._build_default_title(filename, remix_mode),
            description=self._merge_description(remix_mode, payload.description),
            theme=(payload.theme or "").strip()[:2000] or None,
            genre=(payload.genre or "").strip()[:50] or None,
            narrative_perspective=(payload.narrative_perspective or "第三人称")[:50],
            target_words=max(1000, int(payload.target_words or 120000)),
        )

    def _is_chapter_filled(self, chapter: Chapter) -> bool:
        return bool((chapter.content or "").strip())

    def _extract_source_chapter_count_from_description(self, description: Optional[str]) -> Optional[int]:
        if not description:
            return None
        match = re.search(
            rf"{re.escape(REMIX_SOURCE_CHAPTER_COUNT_META_PREFIX)}\s*(\d+)",
            description,
        )
        if not match:
            return None
        try:
            value = int(match.group(1))
        except ValueError:
            return None
        return value if value > 0 else None

    def _extract_source_filename_from_description(self, description: Optional[str]) -> Optional[str]:
        if not description:
            return None
        match = re.search(
            rf"{re.escape(REMIX_SOURCE_FILE_META_PREFIX)}\s*(.+)",
            description,
        )
        if not match:
            return None
        value = (match.group(1) or "").strip()
        return value or None

    def _strip_project_metadata(self, description: Optional[str]) -> str:
        if not description:
            return ""

        metadata_prefixes = (
            REMIX_MODE_META_PREFIX,
            REMIX_SOURCE_FILE_META_PREFIX,
            REMIX_SOURCE_CHAPTER_COUNT_META_PREFIX,
        )
        kept_lines = [
            line.rstrip()
            for line in description.splitlines()
            if line.strip() and not line.strip().startswith(metadata_prefixes)
        ]
        return "\n".join(kept_lines).strip()

    def _decorate_project_description(
        self,
        *,
        description: Optional[str],
        remix_mode: RemixMode,
        source_filename: str,
        source_chapter_count: int,
    ) -> str:
        base_description = self._strip_project_metadata(description)
        metadata_lines = [
            f"{REMIX_MODE_META_PREFIX} {remix_mode}",
            f"{REMIX_SOURCE_FILE_META_PREFIX} {Path(source_filename).stem[:160]}",
            f"{REMIX_SOURCE_CHAPTER_COUNT_META_PREFIX} {max(1, source_chapter_count)}",
        ]
        parts = [base_description] if base_description else []
        parts.extend(metadata_lines)
        return "\n".join(parts).strip()

    def _to_import_chapter(self, chapter: Chapter) -> BookImportChapter:
        return BookImportChapter(
            title=chapter.title,
            content=chapter.content or "",
            summary=chapter.summary,
            chapter_number=chapter.chapter_number,
            outline_title=chapter.title,
        )

    async def _load_project_bible(
        self,
        *,
        db: AsyncSession,
        project_id: str,
    ) -> Optional[BookRemixBible]:
        bible_result = await db.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project_id)
        )
        return bible_result.scalar_one_or_none()

    async def _load_project_continuation_plan(
        self,
        *,
        db: AsyncSession,
        project_id: str,
    ) -> Optional[BookRemixContinuationPlan]:
        plan_result = await db.execute(
            select(BookRemixContinuationPlan).where(BookRemixContinuationPlan.project_id == project_id)
        )
        return plan_result.scalar_one_or_none()

    async def _load_source_chapter_rows(
        self,
        *,
        project: Project,
        db: AsyncSession,
        source_chapter_count: int,
    ) -> list[dict[str, object]]:
        query = (
            select(Chapter.id, Chapter.chapter_number, Chapter.title, Chapter.status, Chapter.content)
            .where(Chapter.project_id == project.id)
            .order_by(Chapter.chapter_number)
        )
        if source_chapter_count > 0:
            query = query.where(Chapter.chapter_number <= source_chapter_count)

        rows = (await db.execute(query)).all()
        return [
            {
                "chapter_id": row[0],
                "chapter_number": row[1],
                "chapter_title": row[2],
                "status": row[3],
                "content": row[4],
            }
            for row in rows
        ]

    async def _load_analyzed_chapter_numbers(
        self,
        *,
        db: AsyncSession,
        project_id: str,
        source_chapter_numbers: set[int],
    ) -> set[int]:
        if not source_chapter_numbers:
            return set()

        rows = (
            await db.execute(
                select(Chapter.chapter_number)
                .join(PlotAnalysis, PlotAnalysis.chapter_id == Chapter.id)
                .where(Chapter.project_id == project_id)
                .where(Chapter.chapter_number.in_(sorted(source_chapter_numbers)))
            )
        ).all()
        return {int(row[0]) for row in rows if row[0] is not None}

    async def _load_running_analysis_chapter_numbers(
        self,
        *,
        db: AsyncSession,
        project_id: str,
        source_chapter_numbers: set[int],
    ) -> set[int]:
        if not source_chapter_numbers:
            return set()

        rows = (
            await db.execute(
                select(Chapter.chapter_number)
                .join(AnalysisTask, AnalysisTask.chapter_id == Chapter.id)
                .where(Chapter.project_id == project_id)
                .where(Chapter.chapter_number.in_(sorted(source_chapter_numbers)))
                .where(AnalysisTask.status.in_(["pending", "running"]))
            )
        ).all()
        return {int(row[0]) for row in rows if row[0] is not None}

    def _build_analysis_coverage_action_plan(
        self,
        *,
        missing_source_chapters: list[int],
        source_chapters: list[dict[str, object]],
        analyzed_numbers: set[int],
        package_numbers: set[int],
        running_analysis_numbers: set[int],
    ) -> list[dict[str, object]]:
        source_numbers = {int(chapter["chapter_number"]) for chapter in source_chapters}
        empty_content_numbers = {
            int(chapter["chapter_number"])
            for chapter in source_chapters
            if not str(chapter.get("content") or "").strip()
        }
        numbers_missing_analysis = source_numbers - analyzed_numbers
        numbers_missing_packages = source_numbers - package_numbers

        groups: list[tuple[str, set[int], str]] = [
            (
                "restore_source_chapter",
                set(missing_source_chapters),
                "source_chapter_row_missing",
            ),
            (
                "sync_existing_analysis",
                (analyzed_numbers & numbers_missing_packages) - empty_content_numbers,
                "plot_analysis_exists_without_change_package",
            ),
            (
                "wait_running_analysis",
                running_analysis_numbers & numbers_missing_analysis,
                "analysis_task_already_running",
            ),
            (
                "fill_chapter_content",
                empty_content_numbers,
                "chapter_content_empty",
            ),
            (
                "queue_analysis",
                numbers_missing_analysis - running_analysis_numbers - empty_content_numbers,
                "plot_analysis_missing",
            ),
        ]

        action_plan: list[dict[str, object]] = []
        for action, numbers, reason in groups:
            chapter_numbers = sorted(numbers)
            if not chapter_numbers:
                continue
            action_plan.append({
                "action": action,
                "chapter_numbers": chapter_numbers,
                "chapter_count": len(chapter_numbers),
                "reason": reason,
            })
        return action_plan

    def _build_continuation_risk_summary(
        self,
        *,
        missing_source_chapters: list[int],
        missing_analysis_chapters: list[dict[str, object]],
        missing_change_package_chapters: list[dict[str, object]],
        empty_source_chapter_numbers: list[int] | None = None,
    ) -> dict[str, object]:
        missing_analysis_numbers = {
            int(chapter["chapter_number"])
            for chapter in missing_analysis_chapters
        }
        missing_package_numbers = {
            int(chapter["chapter_number"])
            for chapter in missing_change_package_chapters
        }
        empty_source_numbers = set(empty_source_chapter_numbers or [])
        blocking_numbers = sorted(
            set(missing_source_chapters)
            | missing_analysis_numbers
            | missing_package_numbers
            | empty_source_numbers
        )
        warning_numbers = []

        reason_label_map = {
            "source_chapter_row_missing": "缺失源章节",
            "source_chapter_content_empty": "源章节正文为空",
            "analysis_missing_before_continuation": "缺少章节拆解分析",
            "change_package_missing_before_continuation": "缺少续写状态写回",
        }
        reasons: list[str] = []
        if missing_source_chapters:
            reasons.append("source_chapter_row_missing")
        if empty_source_numbers:
            reasons.append("source_chapter_content_empty")
        if missing_analysis_numbers:
            reasons.append("analysis_missing_before_continuation")
        if missing_package_numbers:
            reasons.append("change_package_missing_before_continuation")
        reason_labels = [reason_label_map[reason] for reason in reasons]

        if blocking_numbers:
            level = "high"
            label = "\u9ad8\u98ce\u9669"
            can_continue = False
            message = (
                f"\u7eed\u5199\u524d\u5b58\u5728 {len(blocking_numbers)} \u4e2a\u963b\u65ad\u7ae0\u8282\u3002"
                f"{len(warning_numbers)} \u4e2a\u7ae0\u8282\u4e0a\u4e0b\u6587\u504f\u8584\u3002"
                "\u5efa\u8bae\u5148\u8865\u9f50\u5168\u4e66\u89e3\u6790\u7f3a\u53e3\uff0c\u518d\u7eed\u5199\u4e0b\u4e00\u7ae0\u3002"
            )
        elif warning_numbers:
            level = "medium"
            label = "\u4e2d\u98ce\u9669"
            can_continue = True
            message = (
                f"\u7eed\u5199\u72b6\u6001\u4e2d\u6709 {len(warning_numbers)} \u4e2a\u7ae0\u8282\u672a\u5199\u56de\u53d8\u66f4\u5305\u3002"
                "\u53ef\u4ee5\u7ee7\u7eed\u751f\u6210\uff0c\u4f46\u53ef\u80fd\u7f3a\u5c11\u90e8\u5206\u89d2\u8272\u72b6\u6001\u3001\u4f0f\u7b14\u6216\u8ba1\u5212\u8fdb\u5c55\u3002"
            )
        else:
            level = "low"
            label = "\u4f4e\u98ce\u9669"
            can_continue = True
            message = "\u5168\u4e66\u89e3\u6790\u548c\u7eed\u5199\u72b6\u6001\u5199\u56de\u5df2\u8986\u76d6\u5f53\u524d\u6e90\u7ae0\u8282\u3002"

        return {
            "level": level,
            "label": label,
            "can_continue": can_continue,
            "blocking_chapter_numbers": blocking_numbers,
            "warning_chapter_numbers": warning_numbers,
            "reasons": reasons,
            "reason_labels": reason_labels,
            "message": message,
        }

    async def _invalidate_project_continuation_plan(
        self,
        *,
        db: AsyncSession,
        project_id: str,
    ) -> None:
        plan = await self._load_project_continuation_plan(db=db, project_id=project_id)
        if not plan:
            return
        plan.bible_id = None
        plan.status = "draft"
        plan.confirmed_at = None

    def _apply_editable_bible_updates(
        self,
        *,
        bible: BookRemixBible,
        payload: dict[str, object],
    ) -> bool:
        unexpected_fields = sorted(set(payload) - set(REMIX_BIBLE_EDITABLE_FIELDS))
        if unexpected_fields:
            raise HTTPException(
                status_code=400,
                detail=f"unsupported bible editable fields: {', '.join(unexpected_fields)}",
            )

        changed = False
        for field_name in REMIX_BIBLE_EDITABLE_FIELDS:
            if field_name not in payload:
                continue
            next_value = payload[field_name]
            if getattr(bible, field_name) == next_value:
                continue
            setattr(bible, field_name, next_value)
            changed = True

        return changed

    def _sorted_chapter_change_packages(
        self,
        packages: object,
    ) -> list[dict[str, object]]:
        if not isinstance(packages, list):
            return []

        normalized_packages = [
            package
            for package in packages
            if isinstance(package, dict)
        ]

        def sort_key(package: dict[str, object]) -> tuple[int, int]:
            chapter_number = self._coerce_package_chapter_number(package.get("chapter_number"))
            no_chapter_rank = 1 if chapter_number is None else 0
            return no_chapter_rank, chapter_number or 0

        return sorted(normalized_packages, key=sort_key)

    def _coerce_package_chapter_number(self, value: object) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _continuation_context_package_numbers(self, packages: object) -> set[int]:
        numbers: set[int] = set()
        for package in self._sorted_chapter_change_packages(packages):
            if str(package.get("source") or "").strip() not in {"chapter_analysis", "chapter_generation"}:
                continue
            chapter_number = self._coerce_package_chapter_number(package.get("chapter_number"))
            if chapter_number is not None:
                numbers.add(chapter_number)
        return numbers

    def _plot_analysis_to_remix_sync_payload(self, analysis: PlotAnalysis) -> dict[str, object]:
        payload = analysis.to_dict()
        payload["summary"] = self._plot_analysis_summary(analysis)
        emotional_arc: dict[str, object] = {}
        if analysis.emotional_tone:
            emotional_arc["tone"] = analysis.emotional_tone
        if analysis.emotional_intensity is not None:
            emotional_arc["intensity"] = analysis.emotional_intensity
        if analysis.emotional_curve:
            emotional_arc["curve"] = analysis.emotional_curve
        if emotional_arc:
            payload["emotional_arc"] = emotional_arc
        return payload

    def _plot_analysis_summary(self, analysis: PlotAnalysis) -> str:
        for point in analysis.plot_points or []:
            if not isinstance(point, dict):
                continue
            for key in ("content", "summary", "event"):
                value = point.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return (analysis.analysis_report or "").strip()


    def _coverage_percent(self, count: int, total: int) -> int:
        if total <= 0:
            return 0
        return round((count / total) * 100)

    def _apply_generated_bible_payload(
        self,
        *,
        bible: BookRemixBible,
        draft_payload: dict[str, object],
    ) -> None:
        bible.world_rules = draft_payload["world_rules"]
        bible.character_cards = draft_payload["character_cards"]
        bible.organizations = draft_payload["organizations"]
        bible.timeline = draft_payload["timeline"]
        bible.story_arcs = draft_payload["story_arcs"]
        bible.foreshadows = draft_payload["foreshadows"]
        bible.style_signature = draft_payload["style_signature"]
        bible.hard_constraints = draft_payload["hard_constraints"]
        bible.conflicts = draft_payload["conflicts"]
        bible.generation_notes = draft_payload["generation_notes"]
        bible.chapter_change_packages = draft_payload.get("chapter_change_packages", [])
        bible.generation_status = "generated"
        bible.confirmed_at = None

    def _needs_bible_core_backfill(self, bible: BookRemixBible) -> bool:
        return not bool(bible.timeline) or not bool(bible.foreshadows) or not bool(bible.hard_constraints)

    async def _load_bible_backfill_inputs(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> tuple[list[BookImportChapter], list[dict[str, object]]]:
        chapter_result = await db.execute(
            select(Chapter)
            .where(Chapter.project_id == project.id)
            .order_by(Chapter.chapter_number)
        )
        chapters = chapter_result.scalars().all()
        if not chapters:
            return [], []

        _source_chapter_count, source_chapters = self._infer_source_chapters_from_project(
            project=project,
            chapters=chapters,
        )
        if not source_chapters:
            return [], []

        source_numbers = {chapter.chapter_number for chapter in source_chapters}
        analysis_rows = (
            await db.execute(
                select(
                    Chapter.chapter_number,
                    Chapter.title,
                    Chapter.summary,
                    PlotAnalysis.foreshadows,
                    PlotAnalysis.plot_points,
                    PlotAnalysis.conflict_types,
                    PlotAnalysis.character_states,
                )
                .join(PlotAnalysis, PlotAnalysis.chapter_id == Chapter.id)
                .where(Chapter.project_id == project.id)
                .order_by(Chapter.chapter_number)
            )
        ).all()

        analysis_snapshots: list[dict[str, object]] = []
        for row in analysis_rows:
            chapter_number = int(row[0] or 0)
            if source_numbers and chapter_number not in source_numbers:
                continue
            analysis_snapshots.append({
                "chapter_number": chapter_number,
                "title": row[1],
                "summary": row[2],
                "foreshadows": row[3] or [],
                "plot_points": row[4] or [],
                "conflict_types": row[5] or [],
                "character_states": row[6] or [],
            })

        return source_chapters, analysis_snapshots

    def _to_plan_bible_payload(self, bible: BookRemixBible) -> dict[str, object]:
        return {
            "generation_status": bible.generation_status,
            "world_rules": bible.world_rules or {},
            "character_cards": bible.character_cards or [],
            "organizations": bible.organizations or [],
            "timeline": bible.timeline or [],
            "story_arcs": bible.story_arcs or [],
            "foreshadows": bible.foreshadows or [],
            "style_signature": bible.style_signature or {},
            "hard_constraints": bible.hard_constraints or [],
            "conflicts": bible.conflicts or [],
            "generation_notes": bible.generation_notes or [],
            "chapter_change_packages": bible.chapter_change_packages or [],
        }

    def _is_continuation_plan_current_for_bible(
        self,
        *,
        plan: BookRemixContinuationPlan,
        bible: Optional[BookRemixBible],
    ) -> bool:
        if not bible:
            return False

        bible_status = str(bible.generation_status or "").strip().lower()
        if bible_status != "confirmed":
            return False

        linked_bible_id = str(plan.bible_id or "").strip()
        if not linked_bible_id or linked_bible_id != str(bible.id):
            return False

        if plan.updated_at and bible.updated_at and plan.updated_at < bible.updated_at:
            return False

        return True

    def _apply_editable_continuation_plan_updates(
        self,
        *,
        plan: BookRemixContinuationPlan,
        payload: dict[str, object],
    ) -> bool:
        unexpected_fields = sorted(set(payload) - set(REMIX_CONTINUATION_PLAN_EDITABLE_FIELDS))
        if unexpected_fields:
            raise HTTPException(
                status_code=400,
                detail=f"unsupported continuation plan editable fields: {', '.join(unexpected_fields)}",
            )

        changed = False
        for field_name in REMIX_CONTINUATION_PLAN_EDITABLE_FIELDS:
            if field_name not in payload:
                continue
            setattr(plan, field_name, payload[field_name])
            changed = True

        return changed

    def _needs_continuation_plan_backfill(
        self,
        plan: BookRemixContinuationPlan,
    ) -> bool:
        structured_sections = (
            plan.stage_goals or [],
            plan.beats or [],
            plan.priority_hooks or [],
            plan.guardrails or [],
        )
        return any(len(section) == 0 for section in structured_sections)

    def _apply_continuation_plan_payload(
        self,
        *,
        plan: BookRemixContinuationPlan,
        payload: dict[str, object],
        reset_status: bool,
    ) -> None:
        plan.summary = str(payload.get("summary") or "").strip()
        plan.stage_goals = payload.get("stage_goals") if isinstance(payload.get("stage_goals"), list) else []
        plan.beats = payload.get("beats") if isinstance(payload.get("beats"), list) else []
        plan.priority_hooks = (
            payload.get("priority_hooks") if isinstance(payload.get("priority_hooks"), list) else []
        )
        plan.guardrails = payload.get("guardrails") if isinstance(payload.get("guardrails"), list) else []
        if reset_status:
            plan.status = "draft"
            plan.confirmed_at = None

    def _infer_source_chapters_from_project(
        self,
        *,
        project: Project,
        chapters: list[Chapter],
    ) -> tuple[int, list[BookImportChapter]]:
        sorted_chapters = sorted(chapters, key=lambda item: item.chapter_number)
        metadata_source_count = self._extract_source_chapter_count_from_description(project.description)
        if metadata_source_count:
            source_chapters = [
                self._to_import_chapter(chapter)
                for chapter in sorted_chapters
                if chapter.chapter_number <= metadata_source_count and self._is_chapter_filled(chapter)
            ]
            if source_chapters:
                return metadata_source_count, source_chapters

        leading_source_chapters: list[BookImportChapter] = []
        for chapter in sorted_chapters:
            if not self._is_chapter_filled(chapter):
                break
            leading_source_chapters.append(self._to_import_chapter(chapter))

        if leading_source_chapters:
            return leading_source_chapters[-1].chapter_number, leading_source_chapters

        fallback_source_chapters = [
            self._to_import_chapter(chapter)
            for chapter in sorted_chapters
            if self._is_chapter_filled(chapter)
        ]
        if not fallback_source_chapters:
            return 0, []
        return fallback_source_chapters[-1].chapter_number, fallback_source_chapters

    async def _cleanup_pending_continuation_outlines(
        self,
        *,
        db: AsyncSession,
        project_id: str,
        source_chapter_count: int,
        chapters: list[Chapter],
    ) -> tuple[int, int]:
        empty_generated_chapters = [
            chapter
            for chapter in chapters
            if chapter.chapter_number > source_chapter_count and not self._is_chapter_filled(chapter)
        ]
        empty_generated_numbers = {chapter.chapter_number for chapter in empty_generated_chapters}

        deleted_chapters = 0
        if empty_generated_chapters:
            deleted_chapters = len(empty_generated_chapters)
            await db.execute(
                delete(Chapter).where(Chapter.id.in_([chapter.id for chapter in empty_generated_chapters]))
            )

        deleted_outlines = 0
        if empty_generated_numbers:
            outline_result = await db.execute(
                select(Outline.id)
                .where(Outline.project_id == project_id)
                .where(Outline.order_index.in_(sorted(empty_generated_numbers)))
            )
            outline_ids = [row[0] for row in outline_result.fetchall()]
            if outline_ids:
                deleted_outlines = len(outline_ids)
                await db.execute(delete(Outline).where(Outline.id.in_(outline_ids)))

        return deleted_chapters, deleted_outlines

    async def _apply_continuation_default_style(
        self,
        *,
        db: AsyncSession,
        project_id: str,
        user_id: str,
        source_filename: str,
        chapters: list[BookImportChapter],
        narrative_perspective: Optional[str],
    ) -> Optional[int]:
        style_payload = self._build_continuation_style_payload(
            source_filename=source_filename,
            chapters=chapters,
            narrative_perspective=narrative_perspective,
        )
        if not style_payload:
            return None

        existing_default_style_result = await db.execute(
            select(WritingStyle)
            .join(ProjectDefaultStyle, ProjectDefaultStyle.style_id == WritingStyle.id)
            .where(ProjectDefaultStyle.project_id == project_id)
        )
        existing_default_style = existing_default_style_result.scalar_one_or_none()
        if (
            existing_default_style
            and existing_default_style.user_id == user_id
            and existing_default_style.style_type == "custom"
            and (existing_default_style.name or "").endswith("忠实续写风格")
        ):
            existing_default_style.name = style_payload["name"]
            existing_default_style.description = style_payload["description"]
            existing_default_style.prompt_content = style_payload["prompt_content"]
            logger.info(
                "Book remix continuation style refreshed for project=%s style_id=%s source=%s",
                project_id,
                existing_default_style.id,
                source_filename,
            )
            return existing_default_style.id

        count_result = await db.execute(
            select(func.count(WritingStyle.id)).where(WritingStyle.user_id == user_id)
        )
        next_order = (count_result.scalar_one() or 0) + 1

        style = WritingStyle(
            user_id=user_id,
            name=style_payload["name"],
            style_type="custom",
            description=style_payload["description"],
            prompt_content=style_payload["prompt_content"],
            order_index=next_order,
        )
        db.add(style)
        await db.flush()

        await db.execute(
            delete(ProjectDefaultStyle).where(ProjectDefaultStyle.project_id == project_id)
        )
        db.add(ProjectDefaultStyle(project_id=project_id, style_id=style.id))

        logger.info(
            "Book remix continuation style prepared for project=%s style_id=%s source=%s",
            project_id,
            style.id,
            source_filename,
        )
        return style.id

    async def _apply_inspired_default_style(
        self,
        *,
        db: AsyncSession,
        project_id: str,
        user_id: str,
        source_filename: str,
        chapters: list[BookImportChapter],
        narrative_perspective: Optional[str],
    ) -> Optional[int]:
        source_pattern_pack = await source_discovery_service.resolve_fresh_pattern_pack(
            repo_root=PROJECT_ROOT,
            force=False,
        )
        style_payload = self._build_inspired_style_payload(
            source_filename=source_filename,
            chapters=chapters,
            narrative_perspective=narrative_perspective,
            source_pattern_pack=source_pattern_pack,
        )
        if not style_payload:
            return None

        existing_default_style_result = await db.execute(
            select(WritingStyle)
            .join(ProjectDefaultStyle, ProjectDefaultStyle.style_id == WritingStyle.id)
            .where(ProjectDefaultStyle.project_id == project_id)
        )
        existing_default_style = existing_default_style_result.scalar_one_or_none()
        if (
            existing_default_style
            and existing_default_style.user_id == user_id
            and existing_default_style.style_type == "custom"
            and (existing_default_style.name or "").endswith("同类创作风格")
        ):
            existing_default_style.name = style_payload["name"]
            existing_default_style.description = style_payload["description"]
            existing_default_style.prompt_content = style_payload["prompt_content"]
            logger.info(
                "Book remix inspired style refreshed for project=%s style_id=%s source=%s",
                project_id,
                existing_default_style.id,
                source_filename,
            )
            return existing_default_style.id

        count_result = await db.execute(
            select(func.count(WritingStyle.id)).where(WritingStyle.user_id == user_id)
        )
        next_order = (count_result.scalar_one() or 0) + 1

        style = WritingStyle(
            user_id=user_id,
            name=style_payload["name"],
            style_type="custom",
            description=style_payload["description"],
            prompt_content=style_payload["prompt_content"],
            order_index=next_order,
        )
        db.add(style)
        await db.flush()

        await db.execute(
            delete(ProjectDefaultStyle).where(ProjectDefaultStyle.project_id == project_id)
        )
        db.add(ProjectDefaultStyle(project_id=project_id, style_id=style.id))

        logger.info(
            "Book remix inspired style prepared for project=%s style_id=%s source=%s",
            project_id,
            style.id,
            source_filename,
        )
        return style.id

    async def _prepare_continuation_bible_generation(
        self,
        *,
        db: AsyncSession,
        project_id: str,
        source_task_id: str,
        source_chapters: list[BookImportChapter],
        user_ai_service: Optional[AIService],
    ) -> tuple[bool, str]:
        bible_result = await db.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project_id)
        )
        bible = bible_result.scalar_one_or_none()
        if not bible:
            bible = BookRemixBible(project_id=project_id)
            db.add(bible)

        bible.source_task_id = source_task_id
        bible.source_chapter_count = len(source_chapters)
        if user_ai_service is None:
            bible.generation_status = "failed"
            notes = list(bible.generation_notes or [])
            notes.append("draft generation skipped: ai service unavailable")
            bible.generation_notes = notes[-20:]
            await db.flush()
            return False, bible.generation_status

        bible.generation_status = "running"
        await db.flush()
        return True, bible.generation_status

    async def _run_continuation_bible_generation_background(
        self,
        *,
        user_id: str,
        project_id: str,
        project_context: dict[str, Optional[str]],
        source_task_id: str,
        source_chapters: list[BookImportChapter],
        user_ai_service: AIService,
    ) -> None:
        try:
            draft_payload = await BookRemixBibleService(user_ai_service).build_draft_payload(
                project=Project(
                    user_id=project_context["user_id"] or user_id,
                    title=project_context["title"] or "Book Remix Project",
                    theme=project_context["theme"],
                    genre=project_context["genre"],
                    narrative_perspective=project_context["narrative_perspective"],
                ),
                source_chapters=source_chapters,
                analysis_snapshots=[],
            )
        except Exception as exc:
            logger.error(
                "Book remix bible draft generation failed project_id=%s: %s",
                project_id,
                exc,
                exc_info=True,
            )
            await self._update_continuation_bible_generation_failure(
                user_id=user_id,
                project_id=project_id,
                source_task_id=source_task_id,
                source_chapter_count=len(source_chapters),
                error_message=f"draft generation failed: {exc}",
            )
            return

        try:
            session_factory = await self._build_user_session_factory(user_id=user_id)
            async with session_factory() as session:
                bible_result = await session.execute(
                    select(BookRemixBible).where(BookRemixBible.project_id == project_id)
                )
                bible = bible_result.scalar_one_or_none()
                if not bible:
                    bible = BookRemixBible(project_id=project_id)
                    session.add(bible)

                bible.source_task_id = source_task_id
                bible.source_chapter_count = len(source_chapters)
                self._apply_generated_bible_payload(
                    bible=bible,
                    draft_payload=draft_payload,
                )
                await session.commit()
        except Exception as exc:
            logger.error(
                "Book remix bible persistence failed project_id=%s: %s",
                project_id,
                exc,
                exc_info=True,
            )
            await self._update_continuation_bible_generation_failure(
                user_id=user_id,
                project_id=project_id,
                source_task_id=source_task_id,
                source_chapter_count=len(source_chapters),
                error_message=f"draft persistence failed: {exc}",
            )

    async def _update_continuation_bible_generation_failure(
        self,
        *,
        user_id: str,
        project_id: str,
        source_task_id: str,
        source_chapter_count: int,
        error_message: str,
    ) -> None:
        try:
            session_factory = await self._build_user_session_factory(user_id=user_id)
            async with session_factory() as session:
                bible_result = await session.execute(
                    select(BookRemixBible).where(BookRemixBible.project_id == project_id)
                )
                bible = bible_result.scalar_one_or_none()
                if not bible:
                    bible = BookRemixBible(project_id=project_id)
                    session.add(bible)

                bible.source_task_id = source_task_id
                bible.source_chapter_count = source_chapter_count
                bible.generation_status = "failed"
                notes = list(bible.generation_notes or [])
                notes.append(error_message)
                bible.generation_notes = notes[-20:]
                await session.commit()
        except Exception as exc:
            logger.error(
                "Book remix bible failure status update failed project_id=%s: %s",
                project_id,
                exc,
                exc_info=True,
            )

    async def _build_user_session_factory(
        self,
        *,
        user_id: str,
    ) -> async_sessionmaker[AsyncSession]:
        engine = await get_engine(user_id)
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def _build_continuation_style_payload(
        self,
        *,
        source_filename: str,
        chapters: list[BookImportChapter],
        narrative_perspective: Optional[str],
    ) -> Optional[dict[str, str]]:
        valid_chapters = [chapter for chapter in chapters if (chapter.content or "").strip()]
        if not valid_chapters:
            return None

        source_title = Path(source_filename).stem.strip()[:80] or "原书"
        recent_chapters = valid_chapters[-6:]
        avg_words = int(
            sum(self._chapter_word_count(chapter) for chapter in recent_chapters)
            / max(1, len(recent_chapters))
        )
        dialogue_ratio = self._estimate_dialogue_ratio(recent_chapters)

        story_lines = [
            f"- 第{chapter.chapter_number}章《{chapter.title}》：{self._safe_summary(chapter)}"
            for chapter in recent_chapters[-4:]
        ]
        excerpt_lines = []
        for index, chapter in enumerate(recent_chapters[-3:], start=1):
            excerpt = self._extract_style_excerpt(chapter)
            if excerpt:
                excerpt_lines.append(f"[样本{index}]\n{excerpt}")

        prompt_lines = [
            f"你正在续写《{source_title}》，必须把自己当成同一本书的续写执笔者，而不是改编者。",
            "",
            "【续写总原则】",
            "- 严格延续原书已经形成的叙事口吻、章节节奏、人物说话习惯和冲突推进方式。",
            "- 优先承接原书末尾已经抛出的目标、矛盾、伏笔和关系变化，不要另起炉灶。",
            "- 已出现的人名、组织名、地名、能力名和设定术语保持一致，不擅自改名或重置定义。",
            "- 除非原文已经铺垫，否则不要突然升级力量体系、扩张世界规则、切换题材或替换主角核心人格。",
            "- 正文必须像原书自然往后写，不要写成总结腔、说明书腔或高密度设定堆砌。",
            "",
            "【风格锚点】",
            f"- 叙事视角：{(narrative_perspective or '以原书正文已呈现视角为准').strip()}",
            f"- 最近{len(recent_chapters)}章平均篇幅约 {avg_words} 字，单章推进保持原书的事件密度与留钩节奏。",
            f"- 语言观感：{self._build_language_note(avg_words=avg_words, dialogue_ratio=dialogue_ratio)}",
            "",
            "【最近章节走势】",
            *(story_lines or ["- 以原书最近正文推进为唯一准绳。"]),
        ]

        prompt_lines.extend(
            self._build_deconstruction_prompt_lines(
                remix_mode="continuation",
                source_filename=source_filename,
                chapters=valid_chapters,
                total_words=sum(self._chapter_word_count(chapter) for chapter in valid_chapters),
                inspired_seed_profile=None,
            )
        )

        if excerpt_lines:
            prompt_lines.extend([
                "",
                "【原文语气样本】",
                *excerpt_lines,
            ])

        prompt_lines.extend([
            "",
            "输出后续正文时，以上规则与样本优先级高于通用创作习惯。",
            "任何新剧情都必须像原书顺着写出来，而不是像另一位作者接管后重开一本书。",
        ])

        return {
            "name": f"{source_title[:60]}-忠实续写风格",
            "description": "基于导入原书末尾章节自动提炼的忠实续写风格锚点",
            "prompt_content": "\n".join(prompt_lines).strip()[:6000],
        }

    def _build_inspired_style_payload(
        self,
        *,
        source_filename: str,
        chapters: list[BookImportChapter],
        narrative_perspective: Optional[str],
        source_pattern_pack: Optional[dict],
    ) -> Optional[dict[str, str]]:
        valid_chapters = [chapter for chapter in chapters if (chapter.content or "").strip()]
        if not valid_chapters:
            return None

        source_title = Path(source_filename).stem.strip()[:80] or "原书"
        sample_chapters = valid_chapters[-6:]
        avg_words = int(
            sum(self._chapter_word_count(chapter) for chapter in sample_chapters)
            / max(1, len(sample_chapters))
        )
        dialogue_ratio = self._estimate_dialogue_ratio(sample_chapters)

        story_lines = [
            f"- 第{chapter.chapter_number}章《{chapter.title}》：{self._safe_summary(chapter)}"
            for chapter in sample_chapters[-4:]
        ]
        excerpt_lines = []
        for index, chapter in enumerate(sample_chapters[-3:], start=1):
            excerpt = self._extract_style_excerpt(chapter)
            if excerpt:
                excerpt_lines.append(f"[样本{index}]\n{excerpt}")

        pattern_lines: list[str] = []
        inspired_pattern_lines: list[str] = []
        if isinstance(source_pattern_pack, dict):
            for key in ("style_signature_hints", "style_fidelity_hints"):
                values = source_pattern_pack.get(key)
                if isinstance(values, list):
                    pattern_lines.extend(
                        f"- {str(value).strip()}"
                        for value in values
                        if str(value).strip()
                    )
            mapping_targets = source_pattern_pack.get("inspired_mapping_targets")
            if isinstance(mapping_targets, list):
                targets = [
                    str(value).strip()
                    for value in mapping_targets
                    if str(value).strip()
                ]
                if targets:
                    inspired_pattern_lines.append(
                        "- inspired_mapping_targets: " + ", ".join(targets[:12])
                    )
            for key in (
                "inspired_prompt_hints",
                "inspired_transformation_hints",
                "inspired_copy_risk_hints",
            ):
                values = source_pattern_pack.get(key)
                if isinstance(values, list):
                    inspired_pattern_lines.extend(
                        f"- {str(value).strip()}"
                        for value in values
                        if str(value).strip()
                    )

        forbidden_name_lines = self._build_forbidden_source_name_lines(valid_chapters)

        prompt_lines = [
            f"你正在基于《{source_title}》做同类型创作，而不是忠实续写或照搬改名。",
            "",
            "【同类型创作总原则】",
            "- 保留原书的叙事口吻、节奏、视角行为和情绪温度，吸收其场景密度、爽点释放方式与冲突推进手感。",
            "- 只学习写法模式、情绪曲线、信息释放节奏和人物互动质感，不复制原书事实。",
            "- 不要照搬原书人物姓名、组织名称、专有名词或具体事件顺序。",
            "- 新故事必须使用独立人物、独立组织、独立事件链和独立核心矛盾。",
            "- 正文要像同类型作者在写一本新书，不能写成拆书笔记、设定总结或模板化仿句。",
            "",
            "【风格锚点】",
            f"- 叙事视角：{(narrative_perspective or '以源书样本呈现的主导视角为参照').strip()}",
            f"- 源书样本平均篇幅约 {avg_words} 字，生成时保持相近的事件密度、段落节奏和留钩频率。",
            f"- 语言观感：{self._build_language_note(avg_words=avg_words, dialogue_ratio=dialogue_ratio)}",
            "",
            "【源书走势样本】",
            *(story_lines or ["- 以导入章节展示出的类型节奏、情绪温度和叙事密度为参照。"]),
        ]

        prompt_lines.extend(
            self._build_deconstruction_prompt_lines(
                remix_mode="inspired",
                source_filename=source_filename,
                chapters=valid_chapters,
                total_words=sum(self._chapter_word_count(chapter) for chapter in valid_chapters),
                inspired_seed_profile=self._build_inspired_seed_profile(valid_chapters),
            )
        )

        if excerpt_lines:
            prompt_lines.extend([
                "",
                "【源书语气样本】",
                *excerpt_lines,
            ])

        if forbidden_name_lines:
            prompt_lines.extend([
                "",
                "【源书显性元素禁用清单】",
                *forbidden_name_lines,
            ])

        if pattern_lines:
            prompt_lines.extend([
                "",
                "【公开来源模式包】",
                *pattern_lines[:12],
            ])

        if inspired_pattern_lines:
            prompt_lines.extend([
                "",
                "【公开来源同类创作约束】",
                *inspired_pattern_lines[:16],
            ])

        prompt_lines.extend([
            "",
            "输出正文时，优先保持类型相似度与风格签名稳定。",
            "所有相似都应落在节奏、视角、情绪温度和叙事手感上，不能落在命名、桥段顺序或专有设定上。",
        ])

        return {
            "name": f"{source_title[:60]}-同类创作风格",
            "description": "基于导入源书样本自动提炼的同类型创作风格锚点",
            "prompt_content": "\n".join(prompt_lines).strip()[:6000],
        }

    def _build_deconstruction_prompt_lines(
        self,
        *,
        remix_mode: RemixMode,
        source_filename: str,
        chapters: list[BookImportChapter],
        total_words: int,
        inspired_seed_profile: Optional[BookRemixInspiredSeedProfile],
    ) -> list[str]:
        pack = self._build_deconstruction_pack(
            remix_mode=remix_mode,
            source_filename=source_filename,
            chapters=chapters,
            total_words=total_words,
            inspired_seed_profile=inspired_seed_profile,
        )
        source_scope = pack.source_scope
        story_promise = pack.story_promise
        chapter_contract = pack.chapter_contract
        craft_surface_contract = pack.craft_surface_contract
        progress_report_contract = pack.progress_report_contract
        same_type_boundaries = pack.same_type_boundaries
        revision_strategy = pack.revision_strategy
        show_tell = craft_surface_contract.get("show_tell_allocation") if isinstance(craft_surface_contract, dict) else {}
        show_tell_dramatize = ", ".join(show_tell.get("dramatize") or []) if isinstance(show_tell, dict) else ""
        description_jobs = ", ".join(craft_surface_contract.get("description_jobs") or [])

        lines = [
            "",
            "【可审查拆书包 / deconstruction_pack】",
            f"- source_scope.chapter_count: {source_scope.get('chapter_count')}",
            f"- source_scope.average_chapter_words: {source_scope.get('average_chapter_words')}",
            f"- story_promise.reader_pull: {', '.join(story_promise.get('inferred_reader_promise') or [])}",
            f"- chapter_contract.mode: {chapter_contract.get('mode')}",
            f"- chapter_contract.opening_hook: {chapter_contract.get('opening_hook')}",
            f"- chapter_contract.reader_pull: {chapter_contract.get('reader_pull')}",
            f"- chapter_contract.main_goal: {chapter_contract.get('main_goal')}",
            f"- chapter_contract.main_obstacle: {chapter_contract.get('main_obstacle')}",
            f"- chapter_contract.turning_point: {chapter_contract.get('turning_point')}",
            "- craft_surface_contract.pov_filter: "
            + "; ".join(craft_surface_contract.get("pov_filter") or []),
            f"- craft_surface_contract.show_tell_dramatize: {show_tell_dramatize}",
            "- craft_surface_contract.dialogue_subtext: "
            + "; ".join(craft_surface_contract.get("dialogue_subtext") or []),
            f"- craft_surface_contract.description_jobs: {description_jobs}",
            "- scene_beat_sheet: every scene must declare goal, obstacle, turn, cost, and changed exit_state",
            "- reader_pull_checklist: POV, current want, obstacle, stakes, changed exit state, next pull",
            "- continuity_writeback: timeline, character_state, relationship_state, organization_state, world_rules, foreshadowing_and_payoff, unresolved_questions",
            "- hook_payoff_matrix: each carried hook needs answer, partial answer, escalation, or explicit deferral reason",
            "- progress_report_contract.required_fields: "
            + ", ".join(progress_report_contract.get("required_fields") or []),
            "- revision_strategy.ordered_passes: "
            + ", ".join(revision_strategy.get("ordered_passes") or []),
            "- revision_strategy.patch_policy: "
            + "; ".join(revision_strategy.get("patch_policy") or []),
            "- revision_gates: developmental, character_continuity, continuity, anti_ai_naturalness",
        ]

        if remix_mode == "inspired":
            lines.extend(
                [
                    "- same_type_boundaries.required_difference_axes: "
                    + ", ".join(same_type_boundaries.get("required_difference_axes") or []),
                    "- same_type_boundaries.must_replace_elements: "
                    + ", ".join(same_type_boundaries.get("must_replace_elements") or []),
                    "- same_type_boundaries.copy_risk_checks: "
                    + ", ".join(same_type_boundaries.get("copy_risk_checks") or []),
                ]
            )

        return lines

    def _chapter_word_count(self, chapter: BookImportChapter) -> int:
        return len(re.sub(r"\s+", "", chapter.content or ""))

    def _safe_summary(self, chapter: BookImportChapter) -> str:
        summary = (chapter.summary or "").strip()
        if summary:
            return summary[:140]
        fallback = re.sub(r"\s+", " ", chapter.content or "").strip()
        return fallback[:140] or "无摘要"

    def _extract_style_excerpt(self, chapter: BookImportChapter, limit: int = 220) -> str:
        content = re.sub(r"\s+", " ", chapter.content or "").strip()
        if not content:
            return ""
        return content[:limit]

    def _estimate_dialogue_ratio(self, chapters: list[BookImportChapter]) -> float:
        text = "".join(chapter.content or "" for chapter in chapters)
        total = max(1, len(re.sub(r"\s+", "", text)))
        quote_chars = sum(text.count(symbol) for symbol in ("“", "”", "\"", "‘", "’"))
        return quote_chars / total

    def _build_language_note(self, *, avg_words: int, dialogue_ratio: float) -> str:
        if avg_words < 2200:
            pacing_note = "节奏偏紧凑"
        elif avg_words < 4200:
            pacing_note = "节奏中速推进"
        else:
            pacing_note = "节奏偏展开、铺垫较足"

        if dialogue_ratio >= 0.018:
            dialogue_note = "对话与人物交锋占比较高，要靠互动推动剧情"
        elif dialogue_ratio >= 0.008:
            dialogue_note = "叙述与对话相对均衡，要保留场景推进感"
        else:
            dialogue_note = "叙述占比更高，要保留内心、氛围和动作描写的连贯质感"

        return f"{pacing_note}，{dialogue_note}。"

    async def _get_task(self, *, task_id: str, user_id: str) -> _BookRemixTask:
        async with self._tasks_lock:
            task = self._tasks.get(task_id)

        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权访问该任务")
        return task

    def _to_status(self, task: _BookRemixTask) -> BookRemixTaskStatusResponse:
        return BookRemixTaskStatusResponse(
            task_id=task.task_id,
            remix_mode=task.remix_mode,
            status=task.status,  # type: ignore[arg-type]
            progress=task.progress,
            message=task.message,
            error=task.error,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def _set_task_state(
        self,
        task: _BookRemixTask,
        *,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        if status is not None:
            task.status = status
        if progress is not None:
            task.progress = progress
        if message is not None:
            task.message = message
        task.error = error
        task.updated_at = datetime.utcnow()

    def _check_cancelled(self, task: _BookRemixTask) -> None:
        if task.cancelled:
            raise asyncio.CancelledError()


book_remix_service = BookRemixService()
