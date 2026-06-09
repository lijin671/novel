"""拆书二创 API。"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common import verify_project_access
from app.api.chapters import _run_batch_analysis_in_sequence
from app.api.settings import get_user_ai_service
from app.database import get_db
from app.logger import get_logger
from app.models.analysis_task import AnalysisTask
from app.models.chapter import Chapter
from app.schemas.book_remix import (
    BookRemixBibleReadResponse,
    BookRemixBibleUpdateRequest,
    BookRemixAnalysisCoverageResponse,
    BookRemixChapterChangePackageListResponse,
    BookRemixContinuationContextPreviewResponse,
    BookRemixContinuationProgressSummaryResponse,
    BookRemixCreateProjectRequest,
    BookRemixCreateProjectResponse,
    BookRemixPreviewResponse,
    BookRemixRefreshContinuationRequest,
    BookRemixRefreshContinuationResponse,
    BookRemixStartMissingAnalysisResponse,
    BookRemixTaskCreateResponse,
    BookRemixTaskStatusResponse,
)
from app.schemas.book_remix_bible import (
    BookRemixContinuationPlanGenerateRequest,
    BookRemixContinuationPlanResponse,
    BookRemixContinuationPlanUpdateRequest,
)
from app.services.ai_service import AIService
from app.services.book_remix_service import book_remix_service

router = APIRouter(prefix="/book-remix", tags=["拆书二创"])
logger = get_logger(__name__)

MAX_TXT_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/tasks", response_model=BookRemixTaskCreateResponse, summary="创建拆书二创任务")
async def create_book_remix_task(
    request: Request,
    file: UploadFile = File(..., description="TXT 文件"),
    remix_mode: str = Form(default="continuation", description="二创模式：continuation/inspired"),
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="仅支持 .txt 文件")

    if remix_mode not in {"continuation", "inspired"}:
        raise HTTPException(status_code=400, detail="remix_mode 仅支持 continuation 或 inspired")

    content = await file.read()
    if len(content) > MAX_TXT_SIZE:
        raise HTTPException(status_code=413, detail="文件大小超过 50MB 限制")

    return await book_remix_service.create_task(
        user_id=user_id,
        filename=file.filename,
        file_content=content,
        remix_mode=remix_mode,
    )


@router.get("/tasks/{task_id}", response_model=BookRemixTaskStatusResponse, summary="查询拆书二创任务状态")
async def get_book_remix_task_status(task_id: str, request: Request):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    return await book_remix_service.get_task_status(task_id=task_id, user_id=user_id)


@router.get("/tasks/{task_id}/preview", response_model=BookRemixPreviewResponse, summary="获取拆书二创预览")
async def get_book_remix_preview(task_id: str, request: Request):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    return await book_remix_service.get_preview(task_id=task_id, user_id=user_id)


@router.delete("/tasks/{task_id}", summary="取消拆书二创任务")
async def cancel_book_remix_task(task_id: str, request: Request):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    return await book_remix_service.cancel_task(task_id=task_id, user_id=user_id)


@router.post(
    "/tasks/{task_id}/create-project",
    response_model=BookRemixCreateProjectResponse,
    summary="创建拆书二创工作台项目",
)
async def create_book_remix_project(
    task_id: str,
    payload: BookRemixCreateProjectRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_ai_service: AIService = Depends(get_user_ai_service),
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    result = await book_remix_service.create_project_from_task(
        task_id=task_id,
        user_id=user_id,
        payload=payload,
        db=db,
        user_ai_service=user_ai_service,
    )

    analysis_started = False
    analysis_task_count = 0
    analysis_message = "已创建拆书二创工作台项目"

    try:
        chapter_result = await db.execute(
            select(Chapter)
            .where(Chapter.project_id == result["project_id"])
            .order_by(Chapter.chapter_number)
        )
        chapters = [
            chapter
            for chapter in chapter_result.scalars().all()
            if chapter.content and chapter.content.strip()
        ]

        if chapters:
            analysis_pairs: list[tuple[Chapter, AnalysisTask]] = []
            for chapter in chapters:
                analysis_task = AnalysisTask(
                    chapter_id=chapter.id,
                    user_id=user_id,
                    project_id=result["project_id"],
                    status="pending",
                    progress=0,
                )
                db.add(analysis_task)
                analysis_pairs.append((chapter, analysis_task))

            await db.flush()
            await db.commit()

            tasks_queue = [
                {
                    "chapter_id": chapter.id,
                    "chapter_number": chapter.chapter_number,
                    "task_id": analysis_task.id,
                }
                for chapter, analysis_task in analysis_pairs
            ]

            asyncio.create_task(
                _run_batch_analysis_in_sequence(
                    tasks_queue=tasks_queue,
                    user_id=user_id,
                    project_id=result["project_id"],
                    ai_service=user_ai_service,
                )
            )
            analysis_started = True
            analysis_task_count = len(tasks_queue)
            analysis_message = f"已创建拆书二创工作台项目，并启动 {analysis_task_count} 个章节分析任务"
    except Exception as exc:
        await db.rollback()
        logger.error(
            "拆书二创项目自动启动章节分析失败 project_id=%s: %s",
            result["project_id"],
            exc,
            exc_info=True,
        )
        analysis_message = "已创建拆书二创工作台项目，但自动章节分析启动失败，请稍后手动触发"

    return BookRemixCreateProjectResponse(
        success=True,
        project_id=result["project_id"],
        remix_mode=result["remix_mode"],
        total_chapters=result["total_chapters"],
        total_words=result["total_words"],
        bible_generation_started=result.get("bible_generation_started", False),
        bible_generation_status=result.get("bible_generation_status"),
        prepared_style_id=result.get("prepared_style_id"),
        analysis_started=analysis_started,
        analysis_task_count=analysis_task_count,
        message=analysis_message,
    )


@router.post(
    "/projects/{project_id}/refresh-continuation",
    response_model=BookRemixRefreshContinuationResponse,
    summary="刷新已有拆书续写项目的忠实续写配置",
)
async def refresh_book_remix_continuation_project(
    project_id: str,
    payload: BookRemixRefreshContinuationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    project = await verify_project_access(project_id, user_id, db)
    result = await book_remix_service.refresh_continuation_project(
        project=project,
        user_id=user_id,
        db=db,
        replace_pending_outlines=payload.replace_pending_outlines,
    )

    return BookRemixRefreshContinuationResponse(
        success=True,
        project_id=project_id,
        source_chapter_count=result["source_chapter_count"],
        refreshed_style_id=result.get("refreshed_style_id"),
        deleted_outlines=result.get("deleted_outlines", 0),
        deleted_chapters=result.get("deleted_chapters", 0),
        message=result["message"],
    )


@router.get(
    "/projects/{project_id}/bible",
    response_model=BookRemixBibleReadResponse,
    summary="鑾峰彇鎷嗕功缁啓鍦ｇ粡鑽夌",
)
async def get_book_remix_bible(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.get_bible(project=project, db=db)


@router.patch(
    "/projects/{project_id}/bible",
    response_model=BookRemixBibleReadResponse,
    summary="鏇存柊鎷嗕功缁啓鍦ｇ粡鍙紪杈戝尯鍧?",
)
async def update_book_remix_bible(
    project_id: str,
    payload: BookRemixBibleUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.update_bible(
        project=project,
        payload=payload,
        db=db,
    )


@router.post(
    "/projects/{project_id}/bible/confirm",
    response_model=BookRemixBibleReadResponse,
    summary="纭鎷嗕功缁啓鍦ｇ粡鑽夌",
)
async def confirm_book_remix_bible(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.confirm_bible(project=project, db=db)


@router.post(
    "/projects/{project_id}/bible/regenerate",
    response_model=BookRemixBibleReadResponse,
    summary="閲嶇敓鎷嗕功缁啓鍦ｇ粡鑽夌",
)
async def regenerate_book_remix_bible(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_ai_service: AIService = Depends(get_user_ai_service),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.regenerate_bible(
        project=project,
        db=db,
        ai_service=user_ai_service,
    )


@router.get(
    "/projects/{project_id}/continuation-progress-summary",
    response_model=BookRemixContinuationProgressSummaryResponse,
    summary="????????????",
)
async def get_book_remix_continuation_progress_summary(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.get_continuation_progress_summary(project=project, db=db)


@router.get(
    "/projects/{project_id}/chapter-change-packages",
    response_model=BookRemixChapterChangePackageListResponse,
    summary="List remix continuation chapter change packages",
)
async def get_book_remix_chapter_change_packages(
    project_id: str,
    request: Request,
    source: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.get_chapter_change_packages(
        project=project,
        db=db,
        source=source,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/projects/{project_id}/analysis-coverage",
    response_model=BookRemixAnalysisCoverageResponse,
    summary="Report remix source chapter analysis and sync coverage",
)
async def get_book_remix_analysis_coverage(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.get_analysis_coverage(project=project, db=db)


@router.post(
    "/projects/{project_id}/analysis/start-missing",
    response_model=BookRemixStartMissingAnalysisResponse,
    summary="Start remix source chapter analysis for missing coverage gaps",
)
async def start_book_remix_missing_analysis(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_ai_service: AIService = Depends(get_user_ai_service),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)

    targets = await book_remix_service.get_missing_analysis_targets(project=project, db=db)
    chapters = targets["chapters"]
    target_chapter_numbers = [int(chapter.chapter_number) for chapter in chapters]
    if not chapters:
        return {
            "project_id": project_id,
            "target_chapter_numbers": [],
            "total_started": 0,
            "total_skipped_running": 0,
            "total_skipped_no_content": 0,
            "total_synced_existing": 0,
            "synced_existing_chapters": [],
            "started_tasks": {},
        }

    sync_existing_result = await book_remix_service.sync_existing_source_analysis_to_continuation_state(
        project=project,
        db=db,
        targets=targets,
    )
    synced_existing_chapters = list(sync_existing_result["synced_existing_chapters"])
    chapters_requiring_analysis = list(sync_existing_result["chapters_requiring_analysis"])

    if not chapters_requiring_analysis:
        return {
            "project_id": project_id,
            "target_chapter_numbers": target_chapter_numbers,
            "total_started": 0,
            "total_skipped_running": 0,
            "total_skipped_no_content": 0,
            "total_synced_existing": len(synced_existing_chapters),
            "synced_existing_chapters": synced_existing_chapters,
            "started_tasks": {},
        }

    chapter_ids = [chapter.id for chapter in chapters_requiring_analysis]
    tasks_result = await db.execute(
        select(AnalysisTask)
        .where(AnalysisTask.chapter_id.in_(chapter_ids))
        .order_by(AnalysisTask.chapter_id, AnalysisTask.created_at.desc())
    )
    all_tasks = tasks_result.scalars().all()
    latest_task_map: dict[str, AnalysisTask] = {}
    for task in all_tasks:
        if task.chapter_id not in latest_task_map:
            latest_task_map[task.chapter_id] = task

    total_skipped_running = 0
    total_skipped_no_content = 0
    started_tasks: dict[str, dict] = {}
    tasks_to_start: list[tuple[Chapter, AnalysisTask]] = []
    for chapter in chapters_requiring_analysis:
        if not chapter.content or not chapter.content.strip():
            total_skipped_no_content += 1
            continue
        latest_task = latest_task_map.get(chapter.id)
        if latest_task and latest_task.status in {"pending", "running"}:
            total_skipped_running += 1
            continue
        analysis_task = AnalysisTask(
            chapter_id=chapter.id,
            user_id=user_id,
            project_id=project_id,
            status="pending",
            progress=0,
        )
        db.add(analysis_task)
        tasks_to_start.append((chapter, analysis_task))

    if tasks_to_start:
        await db.flush()
        for chapter, analysis_task in tasks_to_start:
            started_tasks[chapter.id] = {
                "chapter_id": chapter.id,
                "task_id": analysis_task.id,
                "status": analysis_task.status,
                "progress": analysis_task.progress,
                "message": "analysis queued",
                "error_message": None,
                "auto_recovered": False,
            }
        await db.commit()

        tasks_queue = [
            {
                "chapter_id": chapter.id,
                "chapter_number": chapter.chapter_number,
                "task_id": analysis_task.id,
            }
            for chapter, analysis_task in tasks_to_start
        ]
        asyncio.create_task(
            _run_batch_analysis_in_sequence(
                tasks_queue=tasks_queue,
                user_id=user_id,
                project_id=project_id,
                ai_service=user_ai_service,
            )
        )

    return {
        "project_id": project_id,
        "target_chapter_numbers": target_chapter_numbers,
        "total_started": len(tasks_to_start),
        "total_skipped_running": total_skipped_running,
        "total_skipped_no_content": total_skipped_no_content,
        "total_synced_existing": len(synced_existing_chapters),
        "synced_existing_chapters": synced_existing_chapters,
        "started_tasks": started_tasks,
    }


@router.get(
    "/projects/{project_id}/continuation-context-preview",
    response_model=BookRemixContinuationContextPreviewResponse,
    summary="Preview remix continuation prompt context",
)
async def get_book_remix_continuation_context_preview(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.get_continuation_context_preview(project=project, db=db)


@router.get(
    "/projects/{project_id}/continuation-plan",
    response_model=BookRemixContinuationPlanResponse,
    summary="获取当前拆书续写规划",
)
async def get_book_remix_continuation_plan(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.get_continuation_plan(project=project, db=db)


@router.post(
    "/projects/{project_id}/continuation-plan/generate",
    response_model=BookRemixContinuationPlanResponse,
    summary="基于确认版圣经生成续写规划",
)
async def generate_book_remix_continuation_plan(
    project_id: str,
    payload: BookRemixContinuationPlanGenerateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_ai_service: AIService = Depends(get_user_ai_service),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.generate_continuation_plan(
        project=project,
        db=db,
        ai_service=user_ai_service,
        user_direction=payload.user_direction,
    )


@router.patch(
    "/projects/{project_id}/continuation-plan",
    response_model=BookRemixContinuationPlanResponse,
    summary="更新续写规划可编辑内容",
)
async def update_book_remix_continuation_plan(
    project_id: str,
    payload: BookRemixContinuationPlanUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.update_continuation_plan(
        project=project,
        payload=payload,
        db=db,
    )


@router.post(
    "/projects/{project_id}/continuation-plan/confirm",
    response_model=BookRemixContinuationPlanResponse,
    summary="确认当前续写规划",
)
async def confirm_book_remix_continuation_plan(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = getattr(request.state, "user_id", None)
    project = await verify_project_access(project_id, user_id, db)
    return await book_remix_service.confirm_continuation_plan(project=project, db=db)
