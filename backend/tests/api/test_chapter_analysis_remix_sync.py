from __future__ import annotations

import uuid
import hashlib
from types import SimpleNamespace

import pytest
from fastapi import BackgroundTasks, HTTPException
from starlette.responses import StreamingResponse
from sqlalchemy import select

from app.api import chapters as chapters_api
from app.models.analysis_task import AnalysisTask
from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan
from app.models.batch_generation_task import BatchGenerationTask
from app.models.chapter import Chapter
from app.models.career import Career, CharacterCareer
from app.models.character import Character
from app.models.foreshadow import Foreshadow
from app.models.generation_history import GenerationHistory
from app.models.memory import PlotAnalysis, StoryMemory
from app.models.novel_workflow import ChapterWorkflowResult, NovelWorkflowTask
from app.models.outline import Outline
from app.models.project import Project
from app.models.project_default_style import ProjectDefaultStyle
from app.models.relationship import CharacterRelationship, Organization, OrganizationMember
from app.models.user import User
from app.models.writing_style import WritingStyle
from app.services.chapter_guardrails import format_guardrail_history_note


_CHAPTER_ANALYSIS_SENTINEL = chr(31456)


class StubAIService:
    async def generate_text(self, *args, **kwargs):
        return "ok"

    async def generate_text_stream(self, *args, **kwargs):
        yield "Inspector Lin recovered the ledger and carried the updated ledger state into the archive."


@pytest.mark.asyncio
async def test_analyze_chapter_background_syncs_confirmed_remix_state(
    monkeypatch,
    create_schema,
    db_session,
    async_engine,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Career.__table__,
        Character.__table__,
        CharacterCareer.__table__,
        Chapter.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        StoryMemory.__table__,
        Foreshadow.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        CharacterRelationship.__table__,
        Organization.__table__,
        OrganizationMember.__table__,
    )

    user_id = "user-remix-analysis"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Continuation Integration",
        description="chapter analysis integration",
    )
    db_session.add(project)
    await db_session.flush()

    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=19,
        title="Ledger Returns",
        content="Inspector Lin recovered ledger and faced the old rival.",
        word_count=56,
        status="completed",
    )
    db_session.add(chapter)
    await db_session.flush()

    task = AnalysisTask(
        id=str(uuid.uuid4()),
        chapter_id=chapter.id,
        user_id=user_id,
        project_id=project.id,
        status="pending",
        progress=0,
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=18,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        foreshadows=[{"hook": "Old rival returns", "status": "open"}],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "pending"}],
        priority_hooks=[{"hook": "Old rival returns", "status": "pending"}],
    )
    db_session.add_all([task, bible, plan])
    await db_session.commit()

    async def fake_get_engine(patched_user_id):
        assert patched_user_id == user_id
        return async_engine

    monkeypatch.setattr("app.database.get_engine", fake_get_engine)
    async def no_planted_foreshadows(*args, **kwargs):
        return []

    async def no_vector_memories(*args, **kwargs):
        return 0

    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "get_planted_foreshadows_for_analysis",
        no_planted_foreshadows,
    )
    monkeypatch.setattr(
        chapters_api.memory_service,
        "batch_add_memories",
        no_vector_memories,
    )

    analysis_result = {
        "summary": "Inspector Lin recovered the ledger and faced the old rival in public.",
        "plot_stage": "development",
        "conflict": {"level": 3, "types": ["person_vs_person"]},
        "emotional_arc": {"primary_emotion": "tense", "intensity": 5},
        "hooks": [],
        "foreshadows": [
            {"content": "Old rival returns", "type": "resolved", "strength": 8}
        ],
        "plot_points": [
            {"content": "Inspector Lin recovered ledger", "importance": 0.9, "type": "resolution"}
        ],
        "character_states": [
            {"character_name": "Inspector Lin", "state_after": "decisive", "key_event": "Recovered ledger"}
        ],
        "organization_states": [],
        "scenes": [],
        "pacing": "moderate",
        "scores": {"overall": 8, "pacing": 8, "engagement": 8, "coherence": 8},
        "suggestions": [],
        "dialogue_ratio": 0.1,
        "description_ratio": 0.9,
    }

    class StubAnalyzer:
        def __init__(self, ai_service):
            self.ai_service = ai_service

        async def analyze_chapter(self, **kwargs):
            return analysis_result

        def generate_analysis_summary(self, result):
            return result["summary"]

        def extract_memories_from_analysis(self, **kwargs):
            return []

    monkeypatch.setattr(chapters_api, "PlotAnalyzer", StubAnalyzer)

    success = await chapters_api.analyze_chapter_background(
        chapter_id=chapter.id,
        user_id=user_id,
        project_id=project.id,
        task_id=task.id,
        ai_service=StubAIService(),
    )

    assert success is True

    await db_session.refresh(task)
    await db_session.refresh(bible)
    await db_session.refresh(plan)

    assert task.status == "completed"
    assert any(
        item.get("source") == "chapter_analysis" and item.get("chapter_number") == 19
        for item in bible.timeline
    )


@pytest.mark.asyncio
async def test_generate_stream_blocks_high_risk_remix_continuation_without_force(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-risk-single"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Single High Risk Continuation",
        outline_mode="one-to-many",
    )
    source_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=1,
        title="Source One",
        content="Source chapter one is complete.",
        summary=f"Source chapter one is complete {_CHAPTER_ANALYSIS_SENTINEL}",
        word_count=128,
        status="completed",
    )
    target_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Continuation Three",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=2,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Continue after source canon", "status": "pending"}],
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add_all([source_chapter, target_chapter, bible])
    await db_session.flush()
    db_session.add(
        PlotAnalysis(
            project_id=project.id,
            chapter_id=source_chapter.id,
            plot_stage="development",
            analysis_report="Source chapter one analyzed.",
        )
    )
    db_session.add(plan)
    await db_session.commit()

    async def fake_get_db(_request):
        yield db_session

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)

    with pytest.raises(HTTPException) as exc_info:
        await chapters_api.generate_chapter_content_stream(
            chapter_id=target_chapter.id,
            request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
            background_tasks=BackgroundTasks(),
            generate_request=chapters_api.ChapterGenerateRequest(enable_mcp=False),
            user_ai_service=StubAIService(),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["code"] == "continuation_risk_high"
    assert exc_info.value.detail["continuation_risk"]["level"] == "high"
    assert exc_info.value.detail["continuation_risk"]["blocking_chapter_numbers"] == [1, 2]
    assert exc_info.value.detail["continuation_risk"]["label"] == "\u9ad8\u98ce\u9669"
    assert "\u7eed\u5199\u524d\u5b58\u5728" in exc_info.value.detail["continuation_risk"]["message"]
    assert "\ufffd" not in exc_info.value.detail["continuation_risk"]["message"]


@pytest.mark.asyncio


@pytest.mark.asyncio
async def test_generate_stream_blocks_when_remix_risk_check_fails_without_force(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-risk-check-failure"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Risk Check Failure",
        outline_mode="one-to-many",
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=20,
        title="Continuation",
        content="",
        word_count=0,
        status="draft",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add(chapter)
    await db_session.commit()

    async def fake_get_db(_request):
        yield db_session

    async def confirmed_lineage(*args, **kwargs):
        return True

    async def coverage_fails(*args, **kwargs):
        raise RuntimeError("coverage unavailable")

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)
    monkeypatch.setattr(chapters_api, "_has_confirmed_remix_continuation_lineage", confirmed_lineage)
    monkeypatch.setattr(chapters_api.book_remix_service, "get_analysis_coverage", coverage_fails)

    with pytest.raises(HTTPException) as exc_info:
        await chapters_api.generate_chapter_content_stream(
            chapter_id=chapter.id,
            request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
            background_tasks=BackgroundTasks(),
            generate_request=chapters_api.ChapterGenerateRequest(enable_mcp=False),
            user_ai_service=StubAIService(),
        )

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail["code"] == "continuation_risk_check_failed"


@pytest.mark.asyncio
async def test_generate_stream_force_skips_remix_risk_check_failure(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-risk-check-force"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Risk Check Force",
        outline_mode="one-to-many",
        current_words=0,
    )
    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Continuation Outline",
        content="Continue safely.",
        order_index=2,
    )
    chapter_1 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=1,
        title="Source",
        content="Source content.",
        word_count=20,
        status="completed",
    )
    chapter_2 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=2,
        title="Continuation",
        content="",
        word_count=0,
        status="draft",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add(outline)
    await db_session.flush()
    db_session.add_all([chapter_1, chapter_2])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Continue safely."
        continuation_point = "Source content."
        previous_chapter_summary = "Source summary."
        chapter_characters = ""
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_get_db(_request):
        yield db_session

    async def confirmed_lineage(*args, **kwargs):
        return True

    async def coverage_fails(*args, **kwargs):
        raise RuntimeError("coverage unavailable")

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}"

    async def no_guardrail(**kwargs):
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)
    monkeypatch.setattr(chapters_api, "_has_confirmed_remix_continuation_lineage", confirmed_lineage)
    monkeypatch.setattr(chapters_api.book_remix_service, "get_analysis_coverage", coverage_fails)
    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", no_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", lambda *args, **kwargs: None)

    response = await chapters_api.generate_chapter_content_stream(
        chapter_id=chapter_2.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        generate_request=chapters_api.ChapterGenerateRequest(
            enable_mcp=False,
            force_high_risk_continuation=True,
        ),
        user_ai_service=StubAIService(),
    )

    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)

    assert any('"type": "result"' in chunk for chunk in chunks)

@pytest.mark.asyncio
async def test_batch_generate_blocks_high_risk_remix_continuation_without_force(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-risk-batch"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch High Risk Continuation",
        outline_mode="one-to-many",
    )
    source_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=1,
        title="Source One",
        content="Source chapter one is complete.",
        summary=f"Source chapter one is complete {_CHAPTER_ANALYSIS_SENTINEL}",
        word_count=128,
        status="completed",
    )
    target_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Continuation Three",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=2,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Continue after source canon", "status": "pending"}],
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add_all([source_chapter, target_chapter, bible])
    await db_session.flush()
    db_session.add(
        PlotAnalysis(
            project_id=project.id,
            chapter_id=source_chapter.id,
            plot_stage="development",
            analysis_report="Source chapter one analyzed.",
        )
    )
    db_session.add(plan)
    await db_session.commit()

    async def no_prepare_continuation_style(*args, **kwargs):
        return None

    monkeypatch.setattr(
        chapters_api.book_remix_service,
        "prepare_project_continuation_style",
        no_prepare_continuation_style,
    )

    with pytest.raises(HTTPException) as exc_info:
        await chapters_api.batch_generate_chapters_in_order(
            project_id=project.id,
            batch_request=chapters_api.BatchGenerateRequest(
                start_chapter_number=3,
                count=1,
                target_word_count=1200,
                enable_mcp=False,
            ),
            request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
            background_tasks=BackgroundTasks(),
            db=db_session,
            user_ai_service=StubAIService(),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["code"] == "continuation_risk_high"
    assert exc_info.value.detail["continuation_risk"]["level"] == "high"
    assert exc_info.value.detail["continuation_risk"]["blocking_chapter_numbers"] == [1, 2]


@pytest.mark.asyncio
async def test_generate_stream_allows_high_risk_remix_continuation_with_force(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-risk-single-force"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Single High Risk Continuation Force",
        outline_mode="one-to-many",
    )
    source_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=1,
        title="Source One",
        content="Source chapter one is complete.",
        summary=f"Source chapter one is complete {_CHAPTER_ANALYSIS_SENTINEL}",
        word_count=128,
        status="completed",
    )
    target_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Continuation Three",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=2,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Continue after source canon", "status": "pending"}],
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add_all([source_chapter, target_chapter, bible])
    await db_session.flush()
    db_session.add(
        PlotAnalysis(
            project_id=project.id,
            chapter_id=source_chapter.id,
            plot_stage="development",
            analysis_report="Source chapter one analyzed.",
        )
    )
    db_session.add(plan)
    await db_session.commit()

    async def fake_get_db(_request):
        yield db_session

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)

    response = await chapters_api.generate_chapter_content_stream(
        chapter_id=target_chapter.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        generate_request=chapters_api.ChapterGenerateRequest(
            enable_mcp=False,
            force_high_risk_continuation=True,
        ),
        user_ai_service=StubAIService(),
    )

    assert isinstance(response, StreamingResponse)


@pytest.mark.asyncio
async def test_batch_generate_allows_high_risk_remix_continuation_with_force(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-risk-batch-force"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch High Risk Continuation Force",
        outline_mode="one-to-many",
    )
    source_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=1,
        title="Source One",
        content="Source chapter one is complete.",
        summary=f"Source chapter one is complete {_CHAPTER_ANALYSIS_SENTINEL}",
        word_count=128,
        status="completed",
    )
    target_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Continuation Three",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=2,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Continue after source canon", "status": "pending"}],
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add_all([source_chapter, target_chapter, bible])
    await db_session.flush()
    db_session.add(
        PlotAnalysis(
            project_id=project.id,
            chapter_id=source_chapter.id,
            plot_stage="development",
            analysis_report="Source chapter one analyzed.",
        )
    )
    db_session.add(plan)
    await db_session.commit()

    async def no_prepare_continuation_style(*args, **kwargs):
        return None

    monkeypatch.setattr(
        chapters_api.book_remix_service,
        "prepare_project_continuation_style",
        no_prepare_continuation_style,
    )

    response = await chapters_api.batch_generate_chapters_in_order(
        project_id=project.id,
        batch_request=chapters_api.BatchGenerateRequest(
            start_chapter_number=3,
            count=1,
            target_word_count=1200,
            enable_mcp=False,
            force_high_risk_continuation=True,
        ),
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        db=db_session,
        user_ai_service=StubAIService(),
    )

    assert isinstance(response, chapters_api.BatchGenerateResponse)
    assert response.chapters_to_generate[0]["chapter_number"] == 3


@pytest.mark.asyncio
async def test_batch_generate_prepares_remix_style_for_confirmed_lineage(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-batch-style"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Style Continuation",
        outline_mode="one-to-many",
    )
    source_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=1,
        title="Source One",
        content="Source chapter one is complete.",
        summary=f"Source chapter one is complete {_CHAPTER_ANALYSIS_SENTINEL}",
        word_count=128,
        status="completed",
    )
    target_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Continuation Three",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=1,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        chapter_change_packages=[
            {
                "type": "chapter_change_package",
                "source": "chapter_analysis",
                "chapter_number": 1,
                "summary": "Source chapter one synced.",
            }
        ],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Continue after source canon", "status": "pending"}],
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add_all([source_chapter, target_chapter, bible])
    await db_session.flush()
    db_session.add(
        PlotAnalysis(
            project_id=project.id,
            chapter_id=source_chapter.id,
            plot_stage="development",
            analysis_report="Source chapter one analyzed.",
        )
    )
    db_session.add(plan)
    await db_session.commit()

    calls = []

    async def capture_prepare_continuation_style(*, project, user_id, db):
        calls.append({"project_id": project.id, "user_id": user_id, "db": db})
        return 123

    monkeypatch.setattr(
        chapters_api.book_remix_service,
        "prepare_project_continuation_style",
        capture_prepare_continuation_style,
    )

    response = await chapters_api.batch_generate_chapters_in_order(
        project_id=project.id,
        batch_request=chapters_api.BatchGenerateRequest(
            start_chapter_number=3,
            count=1,
            target_word_count=1200,
            enable_mcp=False,
        ),
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        db=db_session,
        user_ai_service=StubAIService(),
    )

    assert isinstance(response, chapters_api.BatchGenerateResponse)
    assert calls == [{"project_id": project.id, "user_id": user_id, "db": db_session}]


@pytest.mark.asyncio
async def test_batch_generate_persists_workflow_unlimited_review_policy(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        BatchGenerationTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-batch-workflow"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Workflow Unlimited Review",
        outline_mode="one-to-many",
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=1,
        title="Opening",
        content="",
        word_count=0,
        status="draft",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add(chapter)
    await db_session.commit()

    async def no_risk_gate(*args, **kwargs):
        return None

    monkeypatch.setattr(chapters_api, "_enforce_remix_continuation_risk_gate", no_risk_gate)
    async def no_durable_remix_lineage(**kwargs):
        return False

    monkeypatch.setattr(
        chapters_api.book_remix_context_service,
        "has_project_durable_remix_lineage",
        no_durable_remix_lineage,
    )

    response = await chapters_api.batch_generate_chapters_in_order(
        project_id=project.id,
        batch_request=chapters_api.BatchGenerateRequest(
            start_chapter_number=1,
            count=1,
            target_word_count=1200,
            enable_mcp=False,
            enable_analysis=True,
            enable_workflow=True,
            workflow_auto_regenerate=True,
            workflow_max_rounds=0,
            workflow_min_score=8.6,
        ),
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        db=db_session,
        user_ai_service=StubAIService(),
    )

    task = await db_session.get(BatchGenerationTask, response.batch_id)

    assert task is not None
    assert task.enable_analysis is True
    assert task.enable_workflow is True
    assert task.workflow_auto_regenerate is True
    assert task.workflow_max_rounds == 0
    assert task.workflow_min_score == 8.6


@pytest.mark.asyncio
async def test_batch_generation_runs_novel_workflow_after_analysis_success(
    monkeypatch,
    create_schema,
    db_session,
    async_engine,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        CharacterRelationship.__table__,
        Organization.__table__,
        OrganizationMember.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        StoryMemory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
        NovelWorkflowTask.__table__,
        ChapterWorkflowResult.__table__,
    )

    user_id = "user-batch-workflow"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Workflow",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Workflow Outline",
        content="Recover the ledger and keep the archive thread open.",
        order_index=1,
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=1,
        title="Opening",
        content="",
        word_count=0,
        status="draft",
    )
    batch = BatchGenerationTask(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=user_id,
        start_chapter_number=1,
        chapter_count=1,
        chapter_ids=[chapter.id],
        target_word_count=1200,
        enable_analysis=True,
        enable_workflow=True,
        workflow_auto_regenerate=True,
        workflow_max_rounds=0,
        workflow_min_score=8.6,
        total_chapters=1,
        max_retries=0,
        status="pending",
    )
    db_session.add(outline)
    await db_session.flush()
    db_session.add_all([chapter, batch])
    batch_id = batch.id
    chapter_id = chapter.id
    await db_session.commit()

    async def fake_get_engine(patched_user_id):
        assert patched_user_id == user_id
        return async_engine

    async def fake_generate_single_chapter_for_batch(**kwargs):
        chapter_obj = kwargs["chapter"]
        chapter_obj.content = "Inspector Lin recovered the ledger and carried the updated archive state forward."
        chapter_obj.word_count = 12
        chapter_obj.status = "completed"
        await kwargs["db_session"].commit()
        return "Inspector Lin recovered the ledger."

    analysis_result = {
        "summary": "Inspector Lin recovered the ledger and locked the archive path.",
        "plot_stage": "development",
        "conflict": {"level": 3, "types": ["person_vs_person"]},
        "emotional_arc": {"primary_emotion": "tense", "intensity": 5},
        "hooks": [],
        "foreshadows": [],
        "plot_points": [
            {"content": "Inspector Lin recovered ledger", "importance": 0.9, "type": "resolution"}
        ],
        "character_states": [],
        "organization_states": [],
        "scenes": [],
        "pacing": "moderate",
        "scores": {"overall": 8.4, "pacing": 8.2, "engagement": 8.1, "coherence": 8.5},
        "suggestions": [],
        "dialogue_ratio": 0.1,
        "description_ratio": 0.9,
    }

    class StubAnalyzer:
        def __init__(self, ai_service):
            self.ai_service = ai_service

        async def analyze_chapter(self, **kwargs):
            return analysis_result

        def generate_analysis_summary(self, result):
            return result["summary"]

        def extract_memories_from_analysis(self, **kwargs):
            return []

    workflow_calls = []

    class StubWorkflowService:
        def __init__(self, ai_service):
            self.ai_service = ai_service

        async def run_chapter_workflow(self, **kwargs):
            workflow_calls.append(kwargs)
            return {"decision": "pass"}

    async def no_planted_foreshadows(*args, **kwargs):
        return []

    async def no_vector_memories(*args, **kwargs):
        return 0

    monkeypatch.setattr("app.database.get_engine", fake_get_engine)
    monkeypatch.setattr(chapters_api, "generate_single_chapter_for_batch", fake_generate_single_chapter_for_batch)
    monkeypatch.setattr(chapters_api, "PlotAnalyzer", StubAnalyzer)
    monkeypatch.setattr(chapters_api, "NovelWorkflowService", StubWorkflowService, raising=False)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "get_planted_foreshadows_for_analysis",
        no_planted_foreshadows,
    )
    monkeypatch.setattr(chapters_api.memory_service, "batch_add_memories", no_vector_memories)

    await chapters_api.execute_batch_generation_in_order(
        batch_id=batch_id,
        user_id=user_id,
        ai_service=StubAIService(),
        custom_model=None,
        enable_mcp=False,
    )

    assert len(workflow_calls) == 1
    call = workflow_calls[0]
    assert call["db"] is not None
    assert call["chapter"].id == chapter_id
    assert call["user_id"] == user_id
    assert call["source"] == "batch_generate"
    assert call["auto_regenerate"] is True
    assert call["max_rounds"] == 0
    assert call["min_score"] == 8.6
    assert call["style_id"] is None
    assert call["analysis"] is not None
    assert call["analysis"].chapter_id == chapter_id

    await db_session.refresh(batch)
    assert batch.status == "completed"
    assert batch.completed_chapters == 1


@pytest.mark.asyncio
async def test_execute_batch_generation_skips_source_pattern_pack_for_plain_project(
    monkeypatch,
    create_schema,
    db_session,
    async_engine,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        BatchGenerationTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-plain-batch-no-source-pack"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Plain Batch",
        outline_mode="one-to-many",
        current_words=0,
    )
    chapters = [
        Chapter(
            id=str(uuid.uuid4()),
            project_id=project.id,
            chapter_number=index,
            title=f"Plain Chapter {index}",
            content="",
            word_count=0,
            status="draft",
        )
        for index in (1, 2)
    ]
    batch = BatchGenerationTask(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=user_id,
        start_chapter_number=1,
        chapter_count=2,
        chapter_ids=[chapter.id for chapter in chapters],
        target_word_count=1200,
        enable_analysis=False,
        total_chapters=2,
        max_retries=0,
        status="pending",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add_all([*chapters, batch])
    batch_id = batch.id
    await db_session.commit()

    async def fake_get_engine(patched_user_id):
        assert patched_user_id == user_id
        return async_engine

    async def fail_resolve_source_pack(*args, **kwargs):
        raise AssertionError("plain batch generation must not resolve source pattern pack")

    received_packs = []

    async def fake_generate_single_chapter_for_batch(**kwargs):
        received_packs.append(kwargs.get("source_pattern_pack"))
        chapter_obj = kwargs["chapter"]
        chapter_obj.content = f"plain generated {chapter_obj.chapter_number}"
        chapter_obj.word_count = len(chapter_obj.content)
        chapter_obj.status = "completed"
        await kwargs["db_session"].commit()
        return f"plain summary {chapter_obj.chapter_number}"

    async def always_can_generate(*args, **kwargs):
        return True, "", None

    monkeypatch.setattr("app.database.get_engine", fake_get_engine)
    monkeypatch.setattr(chapters_api, "_resolve_generation_source_pattern_pack", fail_resolve_source_pack)
    monkeypatch.setattr(chapters_api, "generate_single_chapter_for_batch", fake_generate_single_chapter_for_batch)
    monkeypatch.setattr(chapters_api, "check_prerequisites", always_can_generate)

    await chapters_api.execute_batch_generation_in_order(
        batch_id=batch_id,
        user_id=user_id,
        ai_service=StubAIService(),
        custom_model=None,
        enable_mcp=False,
    )

    await db_session.refresh(batch)
    assert batch.status == "completed"
    assert received_packs == [None, None]



@pytest.mark.asyncio
async def test_execute_batch_generation_resolves_source_pattern_pack_once_per_batch(
    monkeypatch,
    create_schema,
    db_session,
    async_engine,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        BatchGenerationTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-batch-source-pack-cache"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Source Pack Cache",
        outline_mode="one-to-many",
        current_words=0,
    )
    chapters = [
        Chapter(
            id=str(uuid.uuid4()),
            project_id=project.id,
            chapter_number=index,
            title=f"Chapter {index}",
            content="",
            word_count=0,
            status="draft",
        )
        for index in (1, 2, 3)
    ]
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=3,
        generation_status="confirmed",
        character_cards=[],
        timeline=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Keep source pattern pack available", "status": "pending"}],
        priority_hooks=[],
        guardrails=[],
    )
    batch = BatchGenerationTask(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=user_id,
        start_chapter_number=1,
        chapter_count=3,
        chapter_ids=[chapter.id for chapter in chapters],
        target_word_count=1200,
        enable_analysis=False,
        total_chapters=3,
        max_retries=0,
        status="pending",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add_all([*chapters, bible, plan, batch])
    batch_id = batch.id
    await db_session.commit()

    async def fake_get_engine(patched_user_id):
        assert patched_user_id == user_id
        return async_engine

    resolve_calls = 0
    expected_pack = {"style_signature_hints": ["cache source pack"]}

    async def fake_resolve_source_pack(*args, **kwargs):
        nonlocal resolve_calls
        resolve_calls += 1
        return expected_pack

    received_packs = []

    async def fake_generate_single_chapter_for_batch(**kwargs):
        received_packs.append(kwargs.get("source_pattern_pack"))
        chapter_obj = kwargs["chapter"]
        chapter_obj.content = f"generated {chapter_obj.chapter_number}"
        chapter_obj.word_count = len(chapter_obj.content)
        chapter_obj.status = "completed"
        await kwargs["db_session"].commit()
        return f"summary {chapter_obj.chapter_number}"

    async def always_can_generate(*args, **kwargs):
        return True, "", None

    monkeypatch.setattr("app.database.get_engine", fake_get_engine)
    monkeypatch.setattr(chapters_api, "_resolve_generation_source_pattern_pack", fake_resolve_source_pack)
    monkeypatch.setattr(chapters_api, "generate_single_chapter_for_batch", fake_generate_single_chapter_for_batch)
    monkeypatch.setattr(chapters_api, "check_prerequisites", always_can_generate)

    await chapters_api.execute_batch_generation_in_order(
        batch_id=batch_id,
        user_id=user_id,
        ai_service=StubAIService(),
        custom_model=None,
        enable_mcp=False,
    )

    await db_session.refresh(batch)
    assert batch.status == "completed"
    assert resolve_calls == 1
    assert received_packs == [expected_pack, expected_pack, expected_pack]



@pytest.mark.asyncio
async def test_batch_workflow_auto_regeneration_reanalyzes_updated_chapter(
    monkeypatch,
    create_schema,
    db_session,
    async_engine,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        CharacterRelationship.__table__,
        Organization.__table__,
        OrganizationMember.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        StoryMemory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
        NovelWorkflowTask.__table__,
        ChapterWorkflowResult.__table__,
    )

    user_id = "user-batch-workflow-reanalysis"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Workflow Reanalysis",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Workflow Reanalysis Outline",
        content="Move from ledger recovery to archive witness.",
        order_index=20,
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Witness",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Question archive witness", "status": "pending"}],
    )
    batch = BatchGenerationTask(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=user_id,
        start_chapter_number=20,
        chapter_count=1,
        chapter_ids=[chapter.id],
        target_word_count=1200,
        enable_analysis=True,
        enable_workflow=True,
        workflow_auto_regenerate=True,
        workflow_max_rounds=2,
        workflow_min_score=8.6,
        total_chapters=1,
        max_retries=0,
        status="pending",
    )
    db_session.add(outline)
    await db_session.flush()
    db_session.add_all([chapter, bible, plan, batch])
    batch_id = batch.id
    chapter_id = chapter.id
    await db_session.commit()

    async def fake_get_engine(patched_user_id):
        assert patched_user_id == user_id
        return async_engine

    async def fake_generate_single_chapter_for_batch(**kwargs):
        chapter_obj = kwargs["chapter"]
        chapter_obj.content = "Inspector Lin repeats the ledger recovery instead of moving forward."
        chapter_obj.word_count = len(chapter_obj.content)
        chapter_obj.status = "completed"
        await kwargs["db_session"].commit()
        return "Inspector Lin repeats the ledger recovery."

    analysis_contents: list[str] = []

    old_analysis_result = {
        "summary": "Old analysis still follows repeated ledger recovery.",
        "plot_stage": "development",
        "conflict": {"level": 3, "types": ["person_vs_person"]},
        "emotional_arc": {"primary_emotion": "stalled", "intensity": 4},
        "hooks": [],
        "foreshadows": [],
        "plot_points": [
            {"content": "Inspector Lin repeats ledger recovery", "importance": 0.5, "type": "repetition"}
        ],
        "character_states": [
            {"character_name": "Inspector Lin", "state_after": "stalled", "key_event": "Repeated ledger"}
        ],
        "organization_states": [],
        "scenes": [],
        "pacing": "slow",
        "scores": {"overall": 6, "pacing": 6, "engagement": 6, "coherence": 6},
        "suggestions": ["Move to the archive witness."],
        "dialogue_ratio": 0.1,
        "description_ratio": 0.9,
    }
    new_analysis_result = {
        "summary": "New analysis follows the archive witness and city hall lead.",
        "plot_stage": "development",
        "conflict": {"level": 5, "types": ["person_vs_society"]},
        "emotional_arc": {"primary_emotion": "tense focus", "intensity": 7},
        "hooks": [],
        "foreshadows": [],
        "plot_points": [
            {"content": "Archive witness opens city hall lead", "importance": 0.9, "type": "revelation"}
        ],
        "character_states": [
            {"character_name": "Inspector Lin", "state_after": "focused", "key_event": "Questioned witness"}
        ],
        "organization_states": [],
        "scenes": [],
        "pacing": "moderate",
        "scores": {"overall": 8.8, "pacing": 8.6, "engagement": 8.7, "coherence": 8.9},
        "suggestions": [],
        "dialogue_ratio": 0.2,
        "description_ratio": 0.8,
    }

    class StubAnalyzer:
        def __init__(self, ai_service):
            self.ai_service = ai_service

        async def analyze_chapter(self, **kwargs):
            content = kwargs["content"]
            analysis_contents.append(content)
            if "archive witness" in content and "city hall lead" in content:
                return new_analysis_result
            return old_analysis_result

        def generate_analysis_summary(self, result):
            return result["summary"]

        def extract_memories_from_analysis(self, **kwargs):
            return []

    workflow_calls = []

    class StubWorkflowService:
        def __init__(self, ai_service):
            self.ai_service = ai_service

        async def run_chapter_workflow(self, **kwargs):
            workflow_calls.append(kwargs)
            chapter_obj = kwargs["chapter"]
            chapter_obj.content = "Inspector Lin questions the archive witness and opens a new city hall lead."
            chapter_obj.summary = chapter_obj.content
            chapter_obj.word_count = len(chapter_obj.content)
            await kwargs["db"].commit()
            return {
                "decision": "pass",
                "applied_regeneration": True,
                "chapter_updated": True,
                "analysis_stale": {
                    "stale": True,
                    "analysis_id": kwargs["analysis"].id,
                    "reason": "workflow_auto_regeneration_updated_chapter_content",
                    "reanalysis_required": True,
                },
            }

    async def no_planted_foreshadows(*args, **kwargs):
        return []

    async def no_vector_memories(*args, **kwargs):
        return 0

    monkeypatch.setattr("app.database.get_engine", fake_get_engine)
    monkeypatch.setattr(chapters_api, "generate_single_chapter_for_batch", fake_generate_single_chapter_for_batch)
    monkeypatch.setattr(chapters_api, "PlotAnalyzer", StubAnalyzer)
    monkeypatch.setattr(chapters_api, "NovelWorkflowService", StubWorkflowService, raising=False)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "get_planted_foreshadows_for_analysis",
        no_planted_foreshadows,
    )
    monkeypatch.setattr(chapters_api.memory_service, "batch_add_memories", no_vector_memories)

    await chapters_api.execute_batch_generation_in_order(
        batch_id=batch_id,
        user_id=user_id,
        ai_service=StubAIService(),
        custom_model=None,
        enable_mcp=False,
    )

    analysis = (
        await db_session.execute(select(PlotAnalysis).where(PlotAnalysis.chapter_id == chapter_id))
    ).scalar_one()
    tasks = (
        await db_session.execute(select(AnalysisTask).where(AnalysisTask.chapter_id == chapter_id))
    ).scalars().all()
    await db_session.refresh(bible)

    assert len(workflow_calls) == 1
    assert analysis_contents == [
        "Inspector Lin repeats the ledger recovery instead of moving forward.",
        "Inspector Lin questions the archive witness and opens a new city hall lead.",
    ]
    assert analysis.analysis_report == "New analysis follows the archive witness and city hall lead."
    assert analysis.plot_points == [
        {"content": "Archive witness opens city hall lead", "importance": 0.9, "type": "revelation"}
    ]
    assert [task.status for task in tasks] == ["completed", "completed"]
    packages = bible.chapter_change_packages or []
    assert [
        item.get("summary")
        for item in packages
        if item.get("source") == "chapter_analysis" and item.get("chapter_number") == 20
    ] == ["New analysis follows the archive witness and city hall lead."]


@pytest.mark.asyncio
async def test_generate_stream_does_not_block_unconfirmed_remix_continuation_state(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-risk-draft"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Draft Remix State",
        outline_mode="one-to-many",
    )
    target_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=1,
        title="Draft Continuation",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=2,
        generation_status="draft",
        character_cards=[{"name": "Inspector Lin"}],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="draft",
        beats=[{"beat": "Continue after source canon", "status": "pending"}],
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add_all([target_chapter, bible, plan])
    await db_session.commit()

    async def fake_get_db(_request):
        yield db_session

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)

    response = await chapters_api.generate_chapter_content_stream(
        chapter_id=target_chapter.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        generate_request=chapters_api.ChapterGenerateRequest(enable_mcp=False),
        user_ai_service=StubAIService(),
    )

    assert isinstance(response, StreamingResponse)


@pytest.mark.asyncio
async def test_batch_generation_commits_generated_chapter_before_analysis(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        AnalysisTask.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-batch"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Continuation",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Ledger Outline",
        content="Recover ledger.",
        order_index=19,
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=19,
        title="Ledger Returns",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=18,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "pending"}],
    )
    db_session.add(outline)
    await db_session.flush()
    db_session.add_all([chapter, bible, plan])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Recover ledger."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Lin lost the first lead."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}\n{remix_continuation_context}"

    async def no_guardrail(**kwargs):
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", no_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    await chapters_api.generate_single_chapter_for_batch(
        db_session=db_session,
        chapter=chapter,
        user_id=user_id,
        style_id=None,
        target_word_count=1200,
        ai_service=StubAIService(),
        write_lock=chapters_api.Lock(),
        enable_mcp=False,
    )

    await db_session.refresh(bible)
    await db_session.refresh(plan)

    assert any(
        item.get("source") == "chapter_generation" and item.get("chapter_number") == 19
        for item in bible.chapter_change_packages
    )
    assert any(
        item.get("source") == "chapter_generation" and item.get("chapter_number") == 19
        for item in bible.timeline
    )
    assert plan.beats[0]["status"] == "done"


@pytest.mark.asyncio
async def test_batch_generation_next_chapter_prompt_sees_previous_generated_package(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        AnalysisTask.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-batch-context"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Continuation",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline_19 = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Ledger Outline 19",
        content="Recover ledger.",
        order_index=19,
    )
    outline_20 = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Ledger Outline 20",
        content="Enter archive after the recovered ledger.",
        order_index=20,
    )
    chapter_19 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline_19.id,
        chapter_number=19,
        title="Ledger Returns",
        content="",
        word_count=0,
        status="draft",
    )
    chapter_20 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline_20.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=18,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "pending"}],
    )
    db_session.add_all([outline_19, outline_20])
    await db_session.flush()
    db_session.add_all([chapter_19, chapter_20, bible, plan])
    await db_session.commit()

    class StubContext:
        def __init__(self, chapter):
            self.chapter_outline = "Recover ledger." if chapter.chapter_number == 19 else "Enter archive after the recovered ledger."
            self.continuation_point = "Lin looked toward the archive."
            self.previous_chapter_summary = "Lin lost the first lead."
            self.chapter_characters = "Inspector Lin"
            self.chapter_careers = ""
            self.foreshadow_reminders = ""
            self.relevant_memories = ""
            self.recent_chapters_context = ""
            self.context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext(kwargs["chapter"])

    rendered_prompts = []

    async def fake_template(*args, **kwargs):
        return "CHAPTER={chapter_number}\n{chapter_outline}\n{remix_continuation_context}"

    original_format_prompt = chapters_api.PromptService.format_prompt

    def capture_format_prompt(template, **kwargs):
        prompt = original_format_prompt(template, **kwargs)
        rendered_prompts.append(prompt)
        return prompt

    async def no_guardrail(**kwargs):
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    class SequentialAIService:
        def __init__(self):
            self.calls = 0

        async def generate_text_stream(self, *args, **kwargs):
            self.calls += 1
            if self.calls == 1:
                yield "Inspector Lin recovered the ledger and carried the updated ledger state into the archive."
            else:
                yield "Inspector Lin used the updated ledger state to confront the archive witness."

    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api.PromptService, "format_prompt", capture_format_prompt)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", no_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    ai_service = SequentialAIService()
    write_lock = chapters_api.Lock()
    for chapter in (chapter_19, chapter_20):
        await chapters_api.generate_single_chapter_for_batch(
            db_session=db_session,
            chapter=chapter,
            user_id=user_id,
            style_id=None,
            target_word_count=1200,
            ai_service=ai_service,
            write_lock=write_lock,
            enable_mcp=False,
        )

    assert len(rendered_prompts) >= 2
    assert "CHAPTER=20" in rendered_prompts[1]
    assert "Chapter 19: Ledger Returns" in rendered_prompts[1]
    assert "updated ledger state" in rendered_prompts[1]


@pytest.mark.asyncio
async def test_batch_generation_guardrail_receives_remix_canon_context(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-batch-guardrail-context"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Guardrail Canon",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Continue after the ledger was recovered.",
        order_index=20,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[
            {
                "type": "chapter_change_package",
                "source": "chapter_analysis",
                "chapter_number": 19,
                "chapter_title": "Ledger Returns",
                "summary": "CANON_SENTINEL: Inspector Lin already recovered the ledger.",
                "timeline_delta": [{"event": "Inspector Lin already recovered the ledger"}],
                "plan_progress": [{"beat": "Recover ledger", "status": "done"}],
            }
        ],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "done", "last_chapter_number": 19}],
        priority_hooks=[],
        guardrails=[],
    )
    db_session.add_all([chapter, bible, plan])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Continue after the ledger was recovered."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Inspector Lin already recovered the ledger."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}\n{remix_continuation_context}"

    captured_guardrail = {}

    async def capture_guardrail(**kwargs):
        captured_guardrail.update(kwargs)
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", capture_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    await chapters_api.generate_single_chapter_for_batch(
        db_session=db_session,
        chapter=chapter,
        user_id=user_id,
        style_id=None,
        target_word_count=1200,
        ai_service=StubAIService(),
        write_lock=chapters_api.Lock(),
        enable_mcp=False,
    )

    assert "remix_continuation_context" in captured_guardrail
    assert "CANON_SENTINEL" in captured_guardrail["remix_continuation_context"]
    assert "Done planned beats" in captured_guardrail["remix_continuation_context"]


@pytest.mark.asyncio
async def test_batch_generation_guardrail_receives_source_pattern_pack(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-batch-source-pack"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Source Pack",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Continue with source pattern guidance.",
        order_index=20,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Source Pack",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "done", "last_chapter_number": 19}],
        priority_hooks=[],
        guardrails=[],
    )
    db_session.add_all([chapter, bible, plan])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Continue with source pattern guidance."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Inspector Lin already recovered the ledger."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}"

    expected_pack = {
        "style_signature_hints": ["SOURCE_PACK_SENTINEL: preserve cadence."],
        "self_review_policy_hints": ["Self-review before accepting a chapter."],
    }

    async def fake_resolve_source_pack(*args, **kwargs):
        return expected_pack

    captured_guardrail = {}

    async def capture_guardrail(**kwargs):
        captured_guardrail.update(kwargs)
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "_resolve_generation_source_pattern_pack", fake_resolve_source_pack)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", capture_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    await chapters_api.generate_single_chapter_for_batch(
        db_session=db_session,
        chapter=chapter,
        user_id=user_id,
        style_id=None,
        target_word_count=1200,
        ai_service=StubAIService(),
        write_lock=chapters_api.Lock(),
        enable_mcp=False,
    )

    assert captured_guardrail["source_pattern_pack"] == expected_pack


@pytest.mark.asyncio
async def test_generate_single_chapter_skips_source_pattern_pack_when_resolution_fails(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-source-pack-failure"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Remix Source Pack Failure",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Continue even when source-discovery guidance is unavailable.",
        order_index=20,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Failure",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Continue after source canon", "status": "pending"}],
        priority_hooks=[],
        guardrails=[],
    )
    db_session.add_all([chapter, bible, plan])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Continue even when source-discovery guidance is unavailable."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Inspector Lin already recovered the ledger."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_context_block(*args, **kwargs):
        return ""

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}"

    resolve_calls = 0

    async def fail_resolve_source_pack(*args, **kwargs):
        nonlocal resolve_calls
        resolve_calls += 1
        raise RuntimeError("source-discovery temporarily unavailable")

    captured_guardrail = {}

    async def capture_guardrail(**kwargs):
        captured_guardrail.update(kwargs)
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(
        chapters_api.book_remix_context_service,
        "build_project_context_block",
        fake_context_block,
    )
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "_resolve_generation_source_pattern_pack", fail_resolve_source_pack)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", capture_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    await chapters_api.generate_single_chapter_for_batch(
        db_session=db_session,
        chapter=chapter,
        user_id=user_id,
        style_id=None,
        target_word_count=1200,
        ai_service=StubAIService(),
        write_lock=chapters_api.Lock(),
        enable_mcp=False,
    )

    assert resolve_calls == 1
    assert captured_guardrail["source_pattern_pack"] is None


@pytest.mark.asyncio
async def test_generate_single_chapter_skips_source_pattern_pack_for_plain_project(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-plain-single-no-source-pack"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Plain Single",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Plain Outline",
        content="Continue without source-discovery guidance.",
        order_index=1,
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=1,
        title="Plain Chapter",
        content="",
        word_count=0,
        status="draft",
    )
    db_session.add(outline)
    await db_session.flush()
    db_session.add(chapter)
    await db_session.commit()

    class StubContext:
        chapter_outline = "Continue without source-discovery guidance."
        continuation_point = ""
        previous_chapter_summary = ""
        chapter_characters = ""
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}"

    async def fail_resolve_source_pack(*args, **kwargs):
        raise AssertionError("plain single batch generation must not resolve source pattern pack")

    captured_guardrail = {}

    async def capture_guardrail(**kwargs):
        captured_guardrail.update(kwargs)
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "_resolve_generation_source_pattern_pack", fail_resolve_source_pack)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", capture_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    await chapters_api.generate_single_chapter_for_batch(
        db_session=db_session,
        chapter=chapter,
        user_id=user_id,
        style_id=None,
        target_word_count=1200,
        ai_service=StubAIService(),
        write_lock=chapters_api.Lock(),
        enable_mcp=False,
    )

    assert captured_guardrail["source_pattern_pack"] is None


@pytest.mark.asyncio
async def test_generate_stream_skips_source_pattern_pack_for_plain_project(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-plain-stream-no-source-pack"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Plain Stream",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Plain Stream Outline",
        content="Generate without source-discovery guidance.",
        order_index=1,
    )
    db_session.add(outline)
    await db_session.flush()
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=1,
        title="Plain Stream Chapter",
        content="",
        word_count=0,
        status="draft",
    )
    db_session.add(chapter)
    await db_session.commit()

    class StubContext:
        chapter_outline = "Generate without source-discovery guidance."
        continuation_point = ""
        previous_chapter_summary = ""
        chapter_characters = ""
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_get_db(_request):
        yield db_session

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}"

    async def fail_resolve_source_pack(*args, **kwargs):
        raise AssertionError("plain stream generation must not resolve source pattern pack")

    captured_guardrail = {}

    async def capture_guardrail(**kwargs):
        captured_guardrail.update(kwargs)
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)
    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "_resolve_generation_source_pattern_pack", fail_resolve_source_pack)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", capture_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", lambda *args, **kwargs: None)

    response = await chapters_api.generate_chapter_content_stream(
        chapter_id=chapter.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        generate_request=chapters_api.ChapterGenerateRequest(enable_mcp=False),
        user_ai_service=StubAIService(),
    )

    assert isinstance(response, StreamingResponse)
    async for _chunk in response.body_iterator:
        pass

    assert captured_guardrail["source_pattern_pack"] is None


@pytest.mark.asyncio
async def test_generate_stream_uses_project_default_continuation_style_when_request_has_no_style(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        User.__table__,
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-stream-default-style"
    db_session.add(
        User(
            user_id=user_id,
            username=user_id,
            display_name="Stream Default Style User",
            linuxdo_id=user_id,
        )
    )
    await db_session.flush()
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Stream Default Style",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Continue after the ledger was recovered.",
        order_index=20,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        style_signature={
            "voice": "STYLE_SENTINEL: restrained clipped voice",
            "style_fidelity_hints": ["Keep source cadence."],
        },
        chapter_change_packages=[
            {
                "type": "chapter_change_package",
                "source": "chapter_analysis",
                "chapter_number": 19,
                "chapter_title": "Ledger Returns",
                "summary": "Inspector Lin already recovered the ledger.",
            }
        ],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "done", "last_chapter_number": 19}],
    )
    style = WritingStyle(
        user_id=user_id,
        name="Continuation Style",
        style_type="custom",
        prompt_content="DEFAULT_STYLE_SENTINEL: keep original clipped cadence.",
        order_index=1,
    )
    db_session.add(style)
    await db_session.flush()
    db_session.add_all([chapter, bible, plan, ProjectDefaultStyle(project_id=project.id, style_id=style.id)])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Continue after the ledger was recovered."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Inspector Lin already recovered the ledger."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_get_db(_request):
        yield db_session

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}\n{remix_continuation_context}"

    async def no_guardrail(**kwargs):
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    captured = {}

    class CapturingAIService:
        async def generate_text_stream(self, *args, **kwargs):
            captured.update(kwargs)
            yield "Inspector Lin used the ledger state to question the archive witness."

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)
    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", no_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", lambda *args, **kwargs: None)

    response = await chapters_api.generate_chapter_content_stream(
        chapter_id=chapter.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        generate_request=chapters_api.ChapterGenerateRequest(
            enable_mcp=False,
            force_high_risk_continuation=True,
        ),
        user_ai_service=CapturingAIService(),
    )

    assert isinstance(response, StreamingResponse)
    async for _chunk in response.body_iterator:
        pass

    assert "DEFAULT_STYLE_SENTINEL" in captured["prompt"]
    assert "DEFAULT_STYLE_SENTINEL" in captured["system_prompt"]
    assert "STYLE_SENTINEL" in captured["prompt"]
    assert "Style signature to preserve" in captured["prompt"]


@pytest.mark.asyncio
async def test_generate_single_chapter_uses_project_default_continuation_style_when_style_id_missing(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        User.__table__,
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-batch-default-style"
    db_session.add(
        User(
            user_id=user_id,
            username=user_id,
            display_name="Batch Default Style User",
            linuxdo_id=user_id,
        )
    )
    await db_session.flush()
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Default Style",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Continue after the ledger was recovered.",
        order_index=20,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        style_signature={
            "voice": "BATCH_STYLE_SENTINEL: restrained clipped voice",
            "style_fidelity_hints": ["Keep source cadence."],
        },
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "done", "last_chapter_number": 19}],
    )
    style = WritingStyle(
        user_id=user_id,
        name="Continuation Style",
        style_type="custom",
        prompt_content="BATCH_DEFAULT_STYLE_SENTINEL: keep original clipped cadence.",
        order_index=1,
    )
    db_session.add(style)
    await db_session.flush()
    db_session.add_all([chapter, bible, plan, ProjectDefaultStyle(project_id=project.id, style_id=style.id)])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Continue after the ledger was recovered."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Inspector Lin already recovered the ledger."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}\n{remix_continuation_context}"

    async def no_guardrail(**kwargs):
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    captured = {}

    class CapturingAIService:
        async def generate_text_stream(self, *args, **kwargs):
            captured.update(kwargs)
            yield "Inspector Lin used the ledger state to question the archive witness."

    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", no_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    await chapters_api.generate_single_chapter_for_batch(
        db_session=db_session,
        chapter=chapter,
        user_id=user_id,
        style_id=None,
        target_word_count=1200,
        ai_service=CapturingAIService(),
        write_lock=chapters_api.Lock(),
        enable_mcp=False,
    )

    assert "BATCH_DEFAULT_STYLE_SENTINEL" in captured["prompt"]
    assert "BATCH_DEFAULT_STYLE_SENTINEL" in captured["system_prompt"]
    assert "BATCH_STYLE_SENTINEL" in captured["prompt"]
    assert "Style signature to preserve" in captured["prompt"]


@pytest.mark.asyncio
async def test_generate_single_chapter_passes_inspired_style_source_excerpts_to_guardrail(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        User.__table__,
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-inspired-source-excerpt-guardrail"
    db_session.add(
        User(
            user_id=user_id,
            username=user_id,
            display_name="Inspired Source Guardrail User",
            linuxdo_id=user_id,
        )
    )
    await db_session.flush()

    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Inspired Draft",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Write an independent archive confrontation.",
        order_index=1,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=1,
        title="New Rain",
        content="",
        word_count=0,
        status="draft",
    )
    style = WritingStyle(
        user_id=user_id,
        name="Source Book-同类创作风格",
        style_type="custom",
        prompt_content=(
            "你正在基于《Source Book》做同类型创作，而不是忠实续写或照搬改名。\n"
            "【源书语气样本】\n"
            "[样本1]\n"
            "林寒把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。\n"
            "[样本2]\n"
            "沈璃站在门外，没有立刻敲门，只等楼下的脚步声逼近。\n"
            "【源书显性元素禁用清单】\n"
            "以下名称只能作为改造参考，正文不得原样沿用：\n"
            "- 林寒, 沈璃, 青岚会, 星火系统"
        ),
        order_index=1,
    )
    db_session.add(style)
    await db_session.flush()
    db_session.add_all([chapter, ProjectDefaultStyle(project_id=project.id, style_id=style.id)])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Write an independent archive confrontation."
        continuation_point = ""
        previous_chapter_summary = ""
        chapter_characters = ""
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}"

    captured_guardrail = {}

    async def capture_guardrail(**kwargs):
        captured_guardrail.update(kwargs)
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    class CapturingAIService:
        async def generate_text_stream(self, *args, **kwargs):
            yield "新主角把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"

    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", capture_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    await chapters_api.generate_single_chapter_for_batch(
        db_session=db_session,
        chapter=chapter,
        user_id=user_id,
        style_id=None,
        target_word_count=1200,
        ai_service=CapturingAIService(),
        write_lock=chapters_api.Lock(),
        enable_mcp=False,
    )

    assert "inspired_source_excerpts" in captured_guardrail
    assert captured_guardrail["inspired_source_excerpts"] == [
        "林寒把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。",
        "沈璃站在门外，没有立刻敲门，只等楼下的脚步声逼近。",
    ]
    assert captured_guardrail["forbidden_characters"] == [
        "林寒",
        "沈璃",
        "青岚会",
        "星火系统",
    ]


@pytest.mark.asyncio
async def test_batch_generation_persists_guardrail_result_in_change_package(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-batch-guardrail-visible"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Guardrail Visibility",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Continue after the ledger was recovered.",
        order_index=20,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[],
        priority_hooks=[],
        guardrails=[],
    )
    db_session.add_all([chapter, bible, plan])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Move beyond ledger recovery."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Inspector Lin already recovered the ledger."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}\n{remix_continuation_context}"

    async def guardrail_rewrites(**kwargs):
        return {
            "applied": True,
            "attempts": 1,
            "content": "Inspector Lin questioned the archive witness instead of replaying ledger recovery.",
            "initial_result": SimpleNamespace(
                passed=False,
                violations=[
                    SimpleNamespace(
                        type="canon_repetition",
                        severity="high",
                        description="repeated confirmed Canon",
                    )
                ],
            ),
            "final_result": SimpleNamespace(passed=True, violations=[]),
        }

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", guardrail_rewrites)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    await chapters_api.generate_single_chapter_for_batch(
        db_session=db_session,
        chapter=chapter,
        user_id=user_id,
        style_id=None,
        target_word_count=1200,
        ai_service=StubAIService(),
        write_lock=chapters_api.Lock(),
        enable_mcp=False,
    )

    await db_session.refresh(bible)

    package = bible.chapter_change_packages[0]
    assert package["source"] == "chapter_generation"
    assert package["guardrail_check"]["applied"] is True
    assert package["guardrail_check"]["attempts"] == 1
    assert package["guardrail_check"]["violations"][0]["type"] == "canon_repetition"
    assert "guardrail_check" in package["changed_sections"]


@pytest.mark.asyncio
async def test_execute_batch_generation_passes_readable_previous_summary_to_next_prompt(
    monkeypatch,
    create_schema,
    db_session,
    async_engine,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-batch-readable-summary"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Readable Summary",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline_19 = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Ledger Outline 19",
        content="Recover ledger.",
        order_index=19,
    )
    outline_20 = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Ledger Outline 20",
        content="Enter archive after the recovered ledger.",
        order_index=20,
    )
    db_session.add_all([outline_19, outline_20])
    await db_session.flush()

    chapter_19 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline_19.id,
        chapter_number=19,
        title="Ledger Returns",
        content="",
        word_count=0,
        status="draft",
    )
    chapter_20 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline_20.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=18,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[],
    )
    batch = BatchGenerationTask(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=user_id,
        start_chapter_number=19,
        chapter_count=2,
        chapter_ids=[chapter_19.id, chapter_20.id],
        target_word_count=1200,
        enable_analysis=False,
        total_chapters=2,
        max_retries=0,
        status="pending",
    )
    db_session.add_all([chapter_19, chapter_20, bible, plan, batch])
    batch_id = batch.id
    await db_session.commit()

    async def fake_get_engine(patched_user_id):
        assert patched_user_id == user_id
        return async_engine

    class StubContext:
        def __init__(self, chapter):
            self.chapter_outline = (
                "Recover ledger."
                if chapter.chapter_number == 19
                else "Enter archive after the recovered ledger."
            )
            self.continuation_point = "Lin looked toward the archive."
            self.previous_chapter_summary = ""
            self.chapter_characters = "Inspector Lin"
            self.chapter_careers = ""
            self.foreshadow_reminders = ""
            self.relevant_memories = ""
            self.recent_chapters_context = ""
            self.context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext(kwargs["chapter"])

    rendered_prompts = []

    async def fake_template(*args, **kwargs):
        return "CHAPTER={chapter_number}\nPREV={previous_chapter_summary}\n{chapter_outline}\n{remix_continuation_context}"

    original_format_prompt = chapters_api.PromptService.format_prompt

    def capture_format_prompt(template, **kwargs):
        prompt = original_format_prompt(template, **kwargs)
        rendered_prompts.append(prompt)
        return prompt

    async def no_guardrail(**kwargs):
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    class SequentialAIService:
        def __init__(self):
            self.calls = 0

        async def generate_text_stream(self, *args, **kwargs):
            self.calls += 1
            if self.calls == 1:
                yield "Inspector Lin recovered the ledger and carried the updated ledger state into the archive."
            else:
                yield "Inspector Lin used the updated ledger state to confront the archive witness."

    monkeypatch.setattr("app.database.get_engine", fake_get_engine)
    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api.PromptService, "format_prompt", capture_format_prompt)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", no_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )

    await chapters_api.execute_batch_generation_in_order(
        batch_id=batch_id,
        user_id=user_id,
        ai_service=SequentialAIService(),
        enable_mcp=False,
    )

    assert len(rendered_prompts) >= 2
    assert "CHAPTER=20" in rendered_prompts[1]
    expected_previous_summary = f"PREV={chr(31532)}19{chr(31456)}{chr(12298)}Ledger Returns{chr(12299)}{chr(65306)}Inspector Lin recovered the ledger"
    assert expected_previous_summary in rendered_prompts[1]
    assert "PREV=?19??Ledger Returns??" not in rendered_prompts[1]


@pytest.mark.asyncio
async def test_execute_batch_generation_with_analysis_replaces_generated_package(
    monkeypatch,
    create_schema,
    db_session,
    async_engine,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        CharacterRelationship.__table__,
        Organization.__table__,
        OrganizationMember.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        StoryMemory.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        BatchGenerationTask.__table__,
    )

    user_id = "user-remix-batch-analysis"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Batch Continuation Analysis",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Ledger Outline",
        content="Recover ledger.",
        order_index=19,
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=19,
        title="Ledger Returns",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=18,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "pending"}],
    )
    batch = BatchGenerationTask(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=user_id,
        start_chapter_number=19,
        chapter_count=1,
        chapter_ids=[chapter.id],
        target_word_count=1200,
        enable_analysis=True,
        total_chapters=1,
        max_retries=0,
        status="pending",
    )
    db_session.add(outline)
    await db_session.flush()
    db_session.add_all([chapter, bible, plan, batch])
    batch_id = batch.id
    chapter_id = chapter.id
    await db_session.commit()

    async def fake_get_engine(patched_user_id):
        assert patched_user_id == user_id
        return async_engine

    class StubContext:
        chapter_outline = "Recover ledger."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Lin lost the first lead."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}\n{remix_continuation_context}"

    async def no_guardrail(**kwargs):
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    async def no_planted_foreshadows(*args, **kwargs):
        return []

    async def no_vector_memories(*args, **kwargs):
        return 0

    analysis_result = {
        "summary": "Inspector Lin recovered the ledger and locked the archive path.",
        "plot_stage": "development",
        "conflict": {"level": 3, "types": ["person_vs_person"]},
        "emotional_arc": {"primary_emotion": "tense", "intensity": 5},
        "hooks": [],
        "foreshadows": [],
        "plot_points": [
            {"content": "Inspector Lin recovered ledger", "importance": 0.9, "type": "resolution"}
        ],
        "character_states": [
            {"character_name": "Inspector Lin", "state_after": "decisive", "key_event": "Recovered ledger"}
        ],
        "organization_states": [],
        "scenes": [],
        "pacing": "moderate",
        "scores": {"overall": 8, "pacing": 8, "engagement": 8, "coherence": 8},
        "suggestions": [],
        "dialogue_ratio": 0.1,
        "description_ratio": 0.9,
    }

    class StubAnalyzer:
        def __init__(self, ai_service):
            self.ai_service = ai_service

        async def analyze_chapter(self, **kwargs):
            return analysis_result

        def generate_analysis_summary(self, result):
            return result["summary"]

        def extract_memories_from_analysis(self, **kwargs):
            return []

    monkeypatch.setattr("app.database.get_engine", fake_get_engine)
    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", no_guardrail)
    monkeypatch.setattr(chapters_api, "PlotAnalyzer", StubAnalyzer)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "get_planted_foreshadows_for_analysis",
        no_planted_foreshadows,
    )
    monkeypatch.setattr(chapters_api.memory_service, "batch_add_memories", no_vector_memories)

    await chapters_api.execute_batch_generation_in_order(
        batch_id=batch_id,
        user_id=user_id,
        ai_service=StubAIService(),
        enable_mcp=False,
    )

    await db_session.refresh(batch)
    await db_session.refresh(chapter)
    await db_session.refresh(bible)
    await db_session.refresh(plan)

    assert batch.status == "completed"
    assert batch.completed_chapters == 1
    assert chapter.status == "completed"
    assert plan.beats[0]["status"] == "done"

    packages = bible.chapter_change_packages or []
    assert [item.get("source") for item in packages if item.get("chapter_number") == 19] == [
        "chapter_analysis"
    ]
    assert any(
        item.get("source") == "chapter_analysis" and item.get("chapter_number") == 19
        for item in bible.timeline or []
    )
    assert not any(
        item.get("source") == "chapter_generation" and item.get("chapter_number") == 19
        for item in bible.timeline or []
    )

    tasks = (
        await db_session.execute(select(AnalysisTask).where(AnalysisTask.chapter_id == chapter_id))
    ).scalars().all()
    assert len(tasks) == 1
    assert tasks[0].status == "completed"


@pytest.mark.asyncio
async def test_analyze_chapter_background_syncs_remix_state_when_optional_foreshadow_update_fails(
    monkeypatch,
    create_schema,
    db_session,
    async_engine,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Career.__table__,
        Character.__table__,
        CharacterCareer.__table__,
        Chapter.__table__,
        AnalysisTask.__table__,
        PlotAnalysis.__table__,
        StoryMemory.__table__,
        Foreshadow.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        CharacterRelationship.__table__,
        Organization.__table__,
        OrganizationMember.__table__,
    )

    user_id = "user-remix-optional-failure"
    project = Project(id=str(uuid.uuid4()), user_id=user_id, title="Optional Failure")
    db_session.add(project)
    await db_session.flush()

    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=19,
        title="Ledger Returns",
        content="Inspector Lin recovered ledger and faced the old rival.",
        word_count=56,
        status="completed",
    )
    db_session.add(chapter)
    await db_session.flush()

    task = AnalysisTask(
        id=str(uuid.uuid4()),
        chapter_id=chapter.id,
        user_id=user_id,
        project_id=project.id,
        status="pending",
        progress=0,
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=18,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        foreshadows=[{"hook": "Old rival returns", "status": "open"}],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "pending"}],
        priority_hooks=[{"hook": "Old rival returns", "status": "pending"}],
    )
    db_session.add_all([task, bible, plan])
    chapter_id = chapter.id
    task_id = task.id
    project_id = project.id
    await db_session.commit()
    db_session.expire(chapter)

    async def fake_get_engine(patched_user_id):
        assert patched_user_id == user_id
        return async_engine

    async def no_planted_foreshadows(*args, **kwargs):
        return []

    async def no_vector_memories(*args, **kwargs):
        return 0

    async def failing_foreshadow_update(*args, **kwargs):
        db = kwargs.get("db") or args[0]
        await db.rollback()
        raise RuntimeError("optional foreshadow update failed")

    monkeypatch.setattr("app.database.get_engine", fake_get_engine)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "get_planted_foreshadows_for_analysis",
        no_planted_foreshadows,
    )
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_update_from_analysis",
        failing_foreshadow_update,
    )
    monkeypatch.setattr(chapters_api.memory_service, "batch_add_memories", no_vector_memories)

    analysis_result = {
        "summary": "Inspector Lin recovered the ledger and faced the old rival in public.",
        "plot_stage": "development",
        "conflict": {"level": 3, "types": ["person_vs_person"]},
        "emotional_arc": {"primary_emotion": "tense", "intensity": 5},
        "hooks": [],
        "foreshadows": [
            {"content": "Old rival returns", "type": "resolved", "strength": 8}
        ],
        "plot_points": [
            {"content": "Inspector Lin recovered ledger", "importance": 0.9, "type": "resolution"}
        ],
        "character_states": [
            {"character_name": "Inspector Lin", "state_after": "decisive", "key_event": "Recovered ledger"}
        ],
        "organization_states": [],
        "scenes": [],
        "pacing": "moderate",
        "scores": {"overall": 8, "pacing": 8, "engagement": 8, "coherence": 8},
        "suggestions": [],
        "dialogue_ratio": 0.1,
        "description_ratio": 0.9,
    }

    class StubAnalyzer:
        def __init__(self, ai_service):
            self.ai_service = ai_service

        async def analyze_chapter(self, **kwargs):
            return analysis_result

        def generate_analysis_summary(self, result):
            return result["summary"]

        def extract_memories_from_analysis(self, **kwargs):
            return []

    monkeypatch.setattr(chapters_api, "PlotAnalyzer", StubAnalyzer)

    success = await chapters_api.analyze_chapter_background(
        chapter_id=chapter_id,
        user_id=user_id,
        project_id=project_id,
        task_id=task_id,
        ai_service=StubAIService(),
    )

    assert success is True
    await db_session.refresh(bible)
    assert any(
        item.get("source") == "chapter_analysis" and item.get("chapter_number") == 19
        for item in bible.timeline
    )



@pytest.mark.asyncio
async def test_generate_stream_guardrail_receives_remix_canon_context(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-stream-guardrail-context"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Stream Guardrail Canon",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Continue after the ledger was recovered.",
        order_index=20,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter_19 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=19,
        title="Ledger Returns",
        content="Inspector Lin already recovered the ledger.",
        word_count=48,
        status="completed",
    )
    chapter_20 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[
            {
                "type": "chapter_change_package",
                "source": "chapter_analysis",
                "chapter_number": 19,
                "chapter_title": "Ledger Returns",
                "summary": "CANON_SENTINEL: Inspector Lin already recovered the ledger.",
                "timeline_delta": [{"event": "Inspector Lin already recovered the ledger"}],
                "plan_progress": [{"beat": "Recover ledger", "status": "done"}],
            }
        ],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "done", "last_chapter_number": 19}],
        priority_hooks=[],
        guardrails=[],
    )
    db_session.add_all([outline, chapter_19, chapter_20, bible, plan])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Continue after the ledger was recovered."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Inspector Lin already recovered the ledger."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_get_db(_request):
        yield db_session

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}\n{remix_continuation_context}"

    captured_guardrail = {}

    async def capture_guardrail(**kwargs):
        captured_guardrail.update(kwargs)
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)
    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", capture_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", lambda *args, **kwargs: None)

    response = await chapters_api.generate_chapter_content_stream(
        chapter_id=chapter_20.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        generate_request=chapters_api.ChapterGenerateRequest(
            enable_mcp=False,
            force_high_risk_continuation=True,
        ),
        user_ai_service=StubAIService(),
    )

    assert isinstance(response, StreamingResponse)
    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)

    assert chunks
    assert "remix_continuation_context" in captured_guardrail
    assert "CANON_SENTINEL" in captured_guardrail["remix_continuation_context"]
    assert "Done planned beats" in captured_guardrail["remix_continuation_context"]


@pytest.mark.asyncio
async def test_generate_stream_next_chapter_prompt_sees_previous_generated_package(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-stream-next-context"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Stream Continuation",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline_19 = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Ledger Outline 19",
        content="Recover ledger.",
        order_index=19,
    )
    outline_20 = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Ledger Outline 20",
        content="Enter archive after the recovered ledger.",
        order_index=20,
    )
    db_session.add_all([outline_19, outline_20])
    await db_session.flush()

    chapter_19 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline_19.id,
        chapter_number=19,
        title="Ledger Returns",
        content="",
        word_count=0,
        status="draft",
    )
    chapter_20 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline_20.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=18,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "Recover ledger", "status": "pending"}],
        priority_hooks=[],
        guardrails=[],
    )
    db_session.add_all([chapter_19, chapter_20, bible, plan])
    await db_session.commit()

    class StubContext:
        def __init__(self, chapter):
            self.chapter_outline = (
                "Recover ledger."
                if chapter.chapter_number == 19
                else "Enter archive after the recovered ledger."
            )
            self.continuation_point = "Lin looked toward the archive."
            self.previous_chapter_summary = "Lin lost the first lead."
            self.chapter_characters = "Inspector Lin"
            self.chapter_careers = ""
            self.foreshadow_reminders = ""
            self.relevant_memories = ""
            self.recent_chapters_context = ""
            self.context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_get_db(_request):
        yield db_session

    async def fake_build_context(*args, **kwargs):
        return StubContext(kwargs["chapter"])

    rendered_prompts = []

    async def fake_template(*args, **kwargs):
        return "CHAPTER={chapter_number}\n{chapter_outline}\n{remix_continuation_context}"

    original_format_prompt = chapters_api.PromptService.format_prompt

    def capture_format_prompt(template, **kwargs):
        prompt = original_format_prompt(template, **kwargs)
        rendered_prompts.append(prompt)
        return prompt

    async def no_guardrail(**kwargs):
        return {"applied": False, "content": kwargs["generated_text"]}

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    class SequentialAIService:
        def __init__(self):
            self.calls = 0

        async def generate_text_stream(self, *args, **kwargs):
            self.calls += 1
            if self.calls == 1:
                yield "Inspector Lin recovered the ledger and carried the updated ledger state into the archive."
            else:
                yield "Inspector Lin used the updated ledger state to confront the archive witness."

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)
    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api.PromptService, "format_prompt", capture_format_prompt)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", no_guardrail)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", lambda *args, **kwargs: None)

    ai_service = SequentialAIService()
    for chapter in (chapter_19, chapter_20):
        response = await chapters_api.generate_chapter_content_stream(
            chapter_id=chapter.id,
            request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
            background_tasks=BackgroundTasks(),
            generate_request=chapters_api.ChapterGenerateRequest(
                enable_mcp=False,
                force_high_risk_continuation=True,
            ),
            user_ai_service=ai_service,
        )
        assert isinstance(response, StreamingResponse)
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        assert chunks
        assert not any('"type": "error"' in chunk for chunk in chunks)

    assert len(rendered_prompts) >= 2
    assert "CHAPTER=20" in rendered_prompts[1]
    assert "Chapter 19: Ledger Returns" in rendered_prompts[1]
    assert "updated ledger state" in rendered_prompts[1]


@pytest.mark.asyncio
async def test_generate_stream_persists_guardrail_result_in_change_package(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-stream-guardrail-visible"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Stream Guardrail Visibility",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Continue after the ledger was recovered.",
        order_index=20,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter_19 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=19,
        title="Ledger Returns",
        content="Inspector Lin already recovered the ledger.",
        word_count=48,
        status="completed",
    )
    chapter_20 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[],
        priority_hooks=[],
        guardrails=[],
    )
    db_session.add_all([outline, chapter_19, chapter_20, bible, plan])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Move beyond ledger recovery."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Inspector Lin already recovered the ledger."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_get_db(_request):
        yield db_session

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}\n{remix_continuation_context}"

    async def guardrail_rewrites(**kwargs):
        return {
            "applied": True,
            "attempts": 1,
            "content": "Inspector Lin questioned the archive witness instead of replaying ledger recovery.",
            "initial_result": SimpleNamespace(
                passed=False,
                violations=[
                    SimpleNamespace(
                        type="canon_repetition",
                        severity="high",
                        description="repeated confirmed Canon",
                    )
                ],
            ),
            "final_result": SimpleNamespace(passed=True, violations=[]),
        }

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)
    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", guardrail_rewrites)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", lambda *args, **kwargs: None)

    response = await chapters_api.generate_chapter_content_stream(
        chapter_id=chapter_20.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        generate_request=chapters_api.ChapterGenerateRequest(
            enable_mcp=False,
            force_high_risk_continuation=True,
        ),
        user_ai_service=StubAIService(),
    )

    assert isinstance(response, StreamingResponse)
    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)

    assert chunks
    refreshed_chapter = (
        await db_session.execute(select(Chapter).where(Chapter.id == chapter_20.id))
    ).scalar_one()
    refreshed_bible = (
        await db_session.execute(select(BookRemixBible).where(BookRemixBible.id == bible.id))
    ).scalar_one()

    assert refreshed_chapter.content == "Inspector Lin questioned the archive witness instead of replaying ledger recovery."
    package = refreshed_bible.chapter_change_packages[0]
    assert package["source"] == "chapter_generation"
    assert package["guardrail_check"]["applied"] is True
    assert package["guardrail_check"]["attempts"] == 1
    assert package["guardrail_check"]["violations"][0]["type"] == "canon_repetition"
    assert "guardrail_check" in package["changed_sections"]



@pytest.mark.asyncio
async def test_generate_stream_returns_guardrail_rewritten_final_content_in_result(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
        Character.__table__,
        Career.__table__,
        CharacterCareer.__table__,
        Foreshadow.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-remix-stream-final-content"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Stream Final Content",
        outline_mode="one-to-many",
        current_words=0,
    )
    db_session.add(project)
    await db_session.flush()

    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Continue after the ledger was recovered.",
        order_index=20,
    )
    db_session.add(outline)
    await db_session.flush()

    chapter_19 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=19,
        title="Ledger Returns",
        content="Inspector Lin already recovered the ledger.",
        word_count=48,
        status="completed",
    )
    chapter_20 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="",
        word_count=0,
        status="draft",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[],
        priority_hooks=[],
        guardrails=[],
    )
    db_session.add_all([chapter_19, chapter_20, bible, plan])
    await db_session.commit()

    class StubContext:
        chapter_outline = "Move beyond ledger recovery."
        continuation_point = "Lin looked toward the archive."
        previous_chapter_summary = "Inspector Lin already recovered the ledger."
        chapter_characters = "Inspector Lin"
        chapter_careers = ""
        foreshadow_reminders = ""
        relevant_memories = ""
        recent_chapters_context = ""
        context_stats = {"memory_count": 0, "total_length": 0}

    async def fake_get_db(_request):
        yield db_session

    async def fake_build_context(*args, **kwargs):
        return StubContext()

    async def fake_template(*args, **kwargs):
        return "{chapter_outline}\n{remix_continuation_context}"

    rewritten_content = "Inspector Lin questioned the archive witness instead of replaying ledger recovery."

    async def guardrail_rewrites(**kwargs):
        return {
            "applied": True,
            "attempts": 1,
            "content": rewritten_content,
        }

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(chapters_api, "get_db", fake_get_db)
    monkeypatch.setattr(chapters_api.OneToManyContextBuilder, "build", fake_build_context)
    monkeypatch.setattr(chapters_api.PromptService, "get_template", fake_template)
    monkeypatch.setattr(chapters_api, "apply_chapter_guardrail_check", guardrail_rewrites)
    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", lambda *args, **kwargs: None)

    response = await chapters_api.generate_chapter_content_stream(
        chapter_id=chapter_20.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        background_tasks=BackgroundTasks(),
        generate_request=chapters_api.ChapterGenerateRequest(
            enable_mcp=False,
            force_high_risk_continuation=True,
        ),
        user_ai_service=StubAIService(),
    )

    all_chunks = []
    result_payloads = []
    async for chunk in response.body_iterator:
        all_chunks.append(chunk)
        if "\"type\": \"result\"" in chunk:
            payload = chunk.split("data: ", 1)[1].strip()
            result_payloads.append(payload)

    full_stream = "".join(all_chunks)
    original_chunk_text = "Inspector Lin recovered the ledger and carried the updated ledger state into the archive."

    assert result_payloads
    assert any(rewritten_content in payload for payload in result_payloads)
    assert original_chunk_text not in full_stream


@pytest.mark.asyncio
async def test_get_chapter_guardrail_review_returns_latest_structured_reasons(
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
    )

    user_id = "user-review-detail"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Review Detail",
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="Draft needs human review.",
        word_count=25,
        status="review_required",
    )
    guardrail_meta = {
        "applied": True,
        "attempts": 1,
        "initial_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                    "context": "source window",
                }
            ],
        },
        "final_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                    "context": "source window",
                }
            ],
        },
    }
    history = GenerationHistory(
        project_id=project.id,
        chapter_id=chapter.id,
        prompt="generated\n" + format_guardrail_history_note(guardrail_meta),
        generated_content=chapter.content,
        model="default",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add_all([chapter, history])
    await db_session.commit()

    response = await chapters_api.get_chapter_guardrail_review(
        chapter_id=chapter.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        db=db_session,
    )

    assert response["chapter_status"] == "review_required"
    assert response["review_required"] is True
    assert response["guardrail_review"]["acceptance_status"] == "needs_manual_review"
    assert response["guardrail_review"]["manual_review_reasons"] == [
        "inspired_source_copy:high"
    ]
    assert response["guardrail_review"]["final_violations"][0]["type"] == "inspired_source_copy"


@pytest.mark.asyncio
async def test_approve_guardrail_review_resumes_downstream_sync(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-review-approve"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Review Approval",
        outline_mode="one-to-many",
        current_words=120,
    )
    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Archive Outline",
        content="Approve the reviewed archive handoff.",
        order_index=20,
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=20,
        title="Archive Aftermath",
        content="Inspector Lin approved the archive handoff after human review.",
        word_count=62,
        status="review_required",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=19,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "approve archive handoff", "status": "pending"}],
    )
    guardrail_meta = {
        "applied": True,
        "attempts": 1,
        "initial_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                }
            ],
        },
        "final_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                }
            ],
        },
    }
    history = GenerationHistory(
        project_id=project.id,
        chapter_id=chapter.id,
        prompt="generated\n" + format_guardrail_history_note(guardrail_meta),
        generated_content=chapter.content,
        model="default",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add(outline)
    await db_session.flush()
    db_session.add(chapter)
    await db_session.flush()
    db_session.add(bible)
    await db_session.flush()
    db_session.add_all([plan, history])
    await db_session.commit()

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    scheduled = []

    def capture_task(self, func, *args, **kwargs):
        scheduled.append((func, args, kwargs))

    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", capture_task)

    response = await chapters_api.approve_chapter_guardrail_review(
        chapter_id=chapter.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        approval=chapters_api.ChapterGuardrailReviewApproveRequest(
            review_note="human accepted after editing names and spans"
        ),
        background_tasks=BackgroundTasks(),
        db=db_session,
        user_ai_service=StubAIService(),
    )

    await db_session.refresh(chapter)
    await db_session.refresh(bible)

    assert chapter.status == "completed"
    assert response["chapter_status"] == "completed"
    assert response["analysis_task_id"]
    assert scheduled and scheduled[0][0] is chapters_api.analyze_chapter_background

    task = (
        await db_session.execute(
            select(AnalysisTask).where(AnalysisTask.id == response["analysis_task_id"])
        )
    ).scalar_one()
    assert task.status == "pending"

    package = bible.chapter_change_packages[0]
    assert package["source"] == "chapter_generation"
    assert package["guardrail_check"]["manual_review"]["approved"] is True
    assert package["guardrail_check"]["manual_review"]["review_note"] == (
        "human accepted after editing names and spans"
    )
    assert package["guardrail_check"]["manual_review"]["content_sha256"] == (
        hashlib.sha256(chapter.content.encode("utf-8")).hexdigest()
    )
    assert package["guardrail_check"]["manual_review"]["word_count"] == chapter.word_count
    assert package["guardrail_check"]["manual_review"]["content_length"] == len(chapter.content)


@pytest.mark.asyncio
async def test_approve_guardrail_review_requires_review_note():
    with pytest.raises(HTTPException) as exc_info:
        await chapters_api.approve_chapter_guardrail_review(
            chapter_id="chapter-note-required",
            request=SimpleNamespace(state=SimpleNamespace(user_id="user-note-required")),
            approval=chapters_api.ChapterGuardrailReviewApproveRequest(
                review_note="   "
            ),
            background_tasks=BackgroundTasks(),
            db=None,
            user_ai_service=StubAIService(),
        )

    assert exc_info.value.status_code == 400
    assert "复核说明" in exc_info.value.detail


@pytest.mark.asyncio
async def test_approve_guardrail_review_reuses_existing_unfinished_analysis_task(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-review-reuse"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Review Approval Reuse",
        outline_mode="one-to-many",
        current_words=120,
    )
    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Reuse Outline",
        content="Approve without creating duplicate analysis tasks.",
        order_index=21,
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=21,
        title="Reuse Aftermath",
        content="Inspector Lin approved the archive handoff after a second human read.",
        word_count=64,
        status="review_required",
    )
    existing_task = AnalysisTask(
        id=str(uuid.uuid4()),
        chapter_id=chapter.id,
        user_id=user_id,
        project_id=project.id,
        status="pending",
        progress=35,
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=20,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "reuse pending analysis", "status": "pending"}],
    )
    guardrail_meta = {
        "applied": True,
        "attempts": 1,
        "initial_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                }
            ],
        },
        "final_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                }
            ],
        },
    }
    history = GenerationHistory(
        project_id=project.id,
        chapter_id=chapter.id,
        prompt="generated\n" + format_guardrail_history_note(guardrail_meta),
        generated_content=chapter.content,
        model="default",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add(outline)
    await db_session.flush()
    db_session.add(chapter)
    await db_session.flush()
    db_session.add(bible)
    await db_session.flush()
    db_session.add_all([existing_task, plan, history])
    await db_session.commit()

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    scheduled = []

    def capture_task(self, func, *args, **kwargs):
        scheduled.append((func, args, kwargs))

    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", capture_task)

    response = await chapters_api.approve_chapter_guardrail_review(
        chapter_id=chapter.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        approval=chapters_api.ChapterGuardrailReviewApproveRequest(
            review_note="human accepted after checking copied spans"
        ),
        background_tasks=BackgroundTasks(),
        db=db_session,
        user_ai_service=StubAIService(),
    )

    tasks = (
        await db_session.execute(
            select(AnalysisTask).where(AnalysisTask.chapter_id == chapter.id)
        )
    ).scalars().all()

    assert response["analysis_task_id"] == existing_task.id
    assert response["analysis_task_reused"] is True
    assert response["analysis_task_status"] == "pending"
    assert response["analysis_task_progress"] == 35
    assert len(tasks) == 1
    assert scheduled == []


@pytest.mark.asyncio
async def test_approve_guardrail_review_records_reviewed_content_hash(
    monkeypatch,
    create_schema,
    db_session,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        GenerationHistory.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    user_id = "user-review-hash"
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Review Approval Hash",
        outline_mode="one-to-many",
        current_words=120,
    )
    outline = Outline(
        id=str(uuid.uuid4()),
        project_id=project.id,
        title="Hash Outline",
        content="Record immutable reviewed text facts.",
        order_index=22,
    )
    reviewed_content = (
        "Inspector Lin approved the archive handoff after verifying "
        "the copied names, set-piece order, and source-neighbor spans."
    )
    chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        outline_id=outline.id,
        chapter_number=22,
        title="Hash Aftermath",
        content=reviewed_content,
        word_count=77,
        status="review_required",
    )
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        source_task_id="source-task",
        source_chapter_count=21,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin"}],
        timeline=[],
        chapter_change_packages=[],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        beats=[{"beat": "record reviewed hash", "status": "pending"}],
    )
    guardrail_meta = {
        "applied": True,
        "attempts": 2,
        "initial_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                }
            ],
        },
        "final_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                }
            ],
        },
    }
    history = GenerationHistory(
        project_id=project.id,
        chapter_id=chapter.id,
        prompt="generated\n" + format_guardrail_history_note(guardrail_meta),
        generated_content=chapter.content,
        model="default",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add(outline)
    await db_session.flush()
    db_session.add(chapter)
    await db_session.flush()
    db_session.add(bible)
    await db_session.flush()
    db_session.add_all([plan, history])
    await db_session.commit()

    async def no_foreshadow_plant(*args, **kwargs):
        return {"planted_count": 0}

    monkeypatch.setattr(
        chapters_api.foreshadow_service,
        "auto_plant_pending_foreshadows",
        no_foreshadow_plant,
    )
    monkeypatch.setattr(BackgroundTasks, "add_task", lambda *args, **kwargs: None)

    await chapters_api.approve_chapter_guardrail_review(
        chapter_id=chapter.id,
        request=SimpleNamespace(state=SimpleNamespace(user_id=user_id)),
        approval=chapters_api.ChapterGuardrailReviewApproveRequest(
            review_note="verified copied spans were removed"
        ),
        background_tasks=BackgroundTasks(),
        db=db_session,
        user_ai_service=StubAIService(),
    )

    await db_session.refresh(bible)
    manual_review = bible.chapter_change_packages[0]["guardrail_check"]["manual_review"]

    assert manual_review["review_note"] == "verified copied spans were removed"
    assert manual_review["content_sha256"] == hashlib.sha256(
        reviewed_content.encode("utf-8")
    ).hexdigest()
    assert manual_review["content_length"] == len(reviewed_content)
    assert manual_review["word_count"] == 77
