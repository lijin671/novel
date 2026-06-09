from __future__ import annotations

import sys
import uuid
from datetime import datetime
from types import ModuleType, SimpleNamespace

import pytest
import pytest_asyncio
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

if "chromadb" not in sys.modules:
    chromadb_stub = ModuleType("chromadb")

    class _DummyCollection:
        def add(self, **kwargs):
            return None

        def query(self, **kwargs):
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

        def update(self, **kwargs):
            return None

        def delete(self, **kwargs):
            return None

        def get(self, **kwargs):
            return {"ids": [], "documents": [], "metadatas": []}

    class _DummyPersistentClient:
        def __init__(self, *args, **kwargs) -> None:
            self._collection = _DummyCollection()

        def get_or_create_collection(self, *args, **kwargs):
            return self._collection

        def delete_collection(self, *args, **kwargs):
            return None

    chromadb_stub.PersistentClient = _DummyPersistentClient
    sys.modules["chromadb"] = chromadb_stub

if "sentence_transformers" not in sys.modules:
    sentence_transformers_stub = ModuleType("sentence_transformers")

    class _DummySentenceTransformer:
        def __init__(self, *args, **kwargs) -> None:
            return None

        def encode(self, texts, **kwargs):
            if isinstance(texts, str):
                return [0.0]
            return [[0.0] for _ in texts]

    sentence_transformers_stub.SentenceTransformer = _DummySentenceTransformer
    sys.modules["sentence_transformers"] = sentence_transformers_stub

if "mcp" not in sys.modules:
    mcp_stub = ModuleType("mcp")

    class _DummyClientSession:
        async def initialize(self):
            return None

    mcp_stub.ClientSession = _DummyClientSession
    mcp_stub.types = SimpleNamespace()
    sys.modules["mcp"] = mcp_stub

    mcp_client_stub = ModuleType("mcp.client")
    sys.modules["mcp.client"] = mcp_client_stub

    mcp_streamable_http_stub = ModuleType("mcp.client.streamable_http")

    async def _dummy_streamablehttp_client(*args, **kwargs):
        raise RuntimeError("streamablehttp_client is stubbed in tests")

    mcp_streamable_http_stub.streamablehttp_client = _dummy_streamablehttp_client
    sys.modules["mcp.client.streamable_http"] = mcp_streamable_http_stub

    mcp_sse_stub = ModuleType("mcp.client.sse")

    async def _dummy_sse_client(*args, **kwargs):
        raise RuntimeError("sse_client is stubbed in tests")

    mcp_sse_stub.sse_client = _dummy_sse_client
    sys.modules["mcp.client.sse"] = mcp_sse_stub

from app.api.book_remix import router
import app.api.book_remix as book_remix_api_module
from app.api.settings import get_user_ai_service
from app.database import get_db
from app.models.analysis_task import AnalysisTask
from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan
from app.models.chapter import Chapter
from app.models.memory import PlotAnalysis
from app.models.outline import Outline
from app.models.project import Project
from app.models.project_default_style import ProjectDefaultStyle
from app.models.user import User
from app.models.writing_style import WritingStyle
from app.schemas.book_import import BookImportChapter, ProjectSuggestion
from app.schemas.book_remix import BookRemixCreateProjectRequest, BookRemixCreateProjectResponse
from app.services.book_remix_continuation_state_service import BookRemixContinuationStateService
from app.services.book_remix_service import book_remix_service


class StubRemixTask:
    def __init__(self) -> None:
        self.task_id = "task-inspired-source"
        self.user_id = TEST_USER_ID
        self.filename = "source-book.txt"
        self.remix_mode = "inspired"
        self.status = "completed"
        self.normalized_chapters = [
            BookImportChapter(
                title="Chapter 1",
                content="The old sect opens a forbidden gate and the heroine pays the price.",
                summary="Forbidden gate opens.",
                chapter_number=1,
            )
        ]
        self.normalized_outlines = []
        self.preview = None


TEST_USER_ID = "user-task-3"


class StubAIService:
    def __init__(self) -> None:
        self.calls = 0
        self.last_prompt = ""
        self.payload = {
            "world_rules": {"canon": "strict"},
            "character_cards": [{"name": "Lin"}],
            "organizations": [{"name": "Black Tide"}],
            "timeline": [{"chapter": 1, "event": "opening conflict"}],
            "story_arcs": [{"name": "Debt Arc", "status": "open"}],
            "foreshadows": [{"hook": "broken ring", "status": "open"}],
            "style_signature": {"pov": "third_person"},
            "hard_constraints": [{"rule": "keep core POV"}],
            "conflicts": [{"type": "timeline", "detail": "ambiguous order"}],
            "generation_notes": ["regenerated in api test"],
            "summary": "Recover old hooks before expanding cast scope.",
            "stage_goals": [{"goal": "Payoff first unresolved ledger hook"}],
            "beats": [{"beat": "Reveal the old rival in public"}],
            "priority_hooks": [{"hook": "broken ring"}],
            "guardrails": [{"rule": "No sudden new power systems"}],
        }

    async def call_with_json_retry(self, **kwargs):
        self.calls += 1
        self.last_prompt = str(kwargs.get("prompt") or "")
        return self.payload


@pytest_asyncio.fixture
async def api_context(
    create_schema,
    db_session: AsyncSession,
):
    await create_schema(
        Project.__table__,
        Outline.__table__,
        Chapter.__table__,
        PlotAnalysis.__table__,
        AnalysisTask.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
        User.__table__,
        WritingStyle.__table__,
        ProjectDefaultStyle.__table__,
    )
    db_session.add(
        User(
            user_id=TEST_USER_ID,
            username=TEST_USER_ID,
            display_name="Test User",
            linuxdo_id=TEST_USER_ID,
        )
    )
    await db_session.commit()

    app = FastAPI()
    app.include_router(router, prefix="/api")

    @app.middleware("http")
    async def inject_user_id(request: Request, call_next):
        request.state.user_id = TEST_USER_ID
        return await call_next(request)

    async def override_get_db():
        yield db_session

    stub_ai_service = StubAIService()

    async def override_user_ai_service():
        return stub_ai_service

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_ai_service] = override_user_ai_service

    original_runner = book_remix_api_module._run_batch_analysis_in_sequence

    async def noop_batch_analysis_runner(*args, **kwargs):
        return None

    book_remix_api_module._run_batch_analysis_in_sequence = noop_batch_analysis_runner

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield {
                "client": client,
                "db_session": db_session,
                "stub_ai_service": stub_ai_service,
            }
    finally:
        book_remix_api_module._run_batch_analysis_in_sequence = original_runner


async def _seed_continuation_project(db_session: AsyncSession) -> Project:
    project = Project(
        id=str(uuid.uuid4()),
        user_id=TEST_USER_ID,
        title="Remix Project",
        description=(
            "remix continuation project for bible api tests\n"
            "[鎷嗕功妯″紡] continuation\n"
            "[鎷嗕功婧愭枃浠禲 source-book\n"
            "[鎷嗕功婧愮珷鑺傛暟] 2"
        ),
        outline_mode="one-to-one",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


async def _seed_normal_project(db_session: AsyncSession) -> Project:
    project = Project(
        id=str(uuid.uuid4()),
        user_id=TEST_USER_ID,
        title="Normal Project",
        description="normal writing project",
        outline_mode="one-to-one",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


async def _register_stub_remix_task(task: StubRemixTask) -> None:
    async with book_remix_service._tasks_lock:
        book_remix_service._tasks[task.task_id] = task  # type: ignore[assignment]


async def _drop_stub_remix_task(task_id: str) -> None:
    async with book_remix_service._tasks_lock:
        book_remix_service._tasks.pop(task_id, None)


async def _seed_draft_bible(
    db_session: AsyncSession,
    *,
    project_id: str,
    generation_status: str = "generated",
) -> BookRemixBible:
    bible = BookRemixBible(
        project_id=project_id,
        source_task_id="task-source-1",
        generation_status=generation_status,
        source_chapter_count=2,
        world_rules={"power_system": "strict"},
        character_cards=[{"name": "Old"}],
        organizations=[{"name": "Guild"}],
        timeline=[{"chapter": 1, "event": "old"}],
        story_arcs=[{"name": "Old Arc"}],
        foreshadows=[{"hook": "old hook"}],
        style_signature={"pov": "first_person"},
        hard_constraints=[{"rule": "old constraint"}],
        conflicts=[{"type": "setting"}],
        generation_notes=["seeded"],
        chapter_change_packages=[{"chapter_number": 1, "summary": "seeded change"}],
    )
    db_session.add(bible)
    await db_session.commit()
    await db_session.refresh(bible)
    return bible


async def _seed_source_chapters(db_session: AsyncSession, *, project_id: str) -> None:
    chapter_1 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project_id,
        chapter_number=1,
        title="Chapter 1",
        content="Opening chapter content",
        summary="Opening summary",
        status="completed",
    )
    chapter_2 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project_id,
        chapter_number=2,
        title="Chapter 2",
        content="Second chapter content",
        summary="Second summary",
        status="completed",
    )
    db_session.add_all([chapter_1, chapter_2])
    await db_session.commit()

    return [chapter_1.id, chapter_2.id]


@pytest.mark.asyncio
async def test_create_inspired_project_persists_source_pattern_pack_guidance(monkeypatch, api_context):
    client: AsyncClient = api_context["client"]

    import app.services.book_remix_service as remix_service_module

    resolve_calls = []

    async def fake_resolve_fresh_pattern_pack(*, repo_root, force=False, **kwargs):
        resolve_calls.append({"repo_root": repo_root, "force": force, **kwargs})
        return {
            "continuation_prompt_hints": ["fresh inspired source pattern hint"],
            "style_signature_hints": ["fresh inspired style hint"],
            "self_review_policy_hints": ["fresh inspired review hint"],
            "safety_constraints": ["fresh inspired safety hint"],
        }

    monkeypatch.setattr(
        remix_service_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve_fresh_pattern_pack,
    )

    task = StubRemixTask()
    await _register_stub_remix_task(task)
    try:
        response = await client.post(
            f"/api/book-remix/tasks/{task.task_id}/create-project",
            json={
                "project_suggestion": {
                    "title": "Inspired Draft",
                    "description": "User-provided same-type direction.",
                    "theme": "urban mystery",
                    "genre": "悬疑",
                    "narrative_perspective": "第三人称",
                    "target_words": 120000,
                }
            },
        )
    finally:
        await _drop_stub_remix_task(task.task_id)

    assert response.status_code == 200
    project_id = response.json()["project_id"]
    db_session: AsyncSession = api_context["db_session"]
    project = (
        await db_session.execute(select(Project).where(Project.id == project_id))
    ).scalar_one()

    assert resolve_calls
    assert resolve_calls[0]["repo_root"] == remix_service_module.PROJECT_ROOT
    assert resolve_calls[0]["force"] is False
    assert "[\u516c\u5f00\u6765\u6e90\u6a21\u5f0f\u5305]" in project.description
    assert "fresh inspired source pattern hint" in project.description
    assert "fresh inspired style hint" in project.description
    assert "fresh inspired review hint" in project.description
    assert "fresh inspired safety hint" in project.description


@pytest.mark.asyncio
async def test_create_inspired_project_sets_default_style_from_source_voice(monkeypatch, api_context):
    client: AsyncClient = api_context["client"]

    import app.services.book_remix_service as remix_service_module

    async def fake_resolve_fresh_pattern_pack(*, repo_root, force=False, **kwargs):
        return {
            "style_signature_hints": ["preserve source cadence without copying names"],
            "style_fidelity_hints": ["match rhythm, POV behavior, and narrative temperature"],
        }

    monkeypatch.setattr(
        remix_service_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve_fresh_pattern_pack,
    )

    task = StubRemixTask()
    task.normalized_chapters = [
        BookImportChapter(
            title="Ledger Rain",
            content=(
                "Lin kept his answer short. The rain moved across the archive windows. "
                '"No one moved the ledger," she said. Lin did not smile. '
                "He only turned the brass key once."
            ),
            summary="Restrained archive pressure.",
            chapter_number=1,
        ),
        BookImportChapter(
            title="Cold Key",
            content=(
                "The corridor stayed quiet. Lin listened to the lock before he touched it. "
                '"You are late," the rival said. Lin kept the key in his palm.'
            ),
            summary="Quiet confrontation around the key.",
            chapter_number=2,
        ),
    ]
    await _register_stub_remix_task(task)
    try:
        response = await client.post(
            f"/api/book-remix/tasks/{task.task_id}/create-project",
            json={
                "project_suggestion": {
                    "title": "Inspired Draft",
                    "description": "User-provided same-type direction.",
                    "theme": "urban mystery",
                    "genre": "悬疑",
                    "narrative_perspective": "limited third person",
                    "target_words": 120000,
                }
            },
        )
    finally:
        await _drop_stub_remix_task(task.task_id)

    assert response.status_code == 200
    project_id = response.json()["project_id"]
    db_session: AsyncSession = api_context["db_session"]
    default_style = (
        await db_session.execute(
            select(WritingStyle)
            .join(ProjectDefaultStyle, ProjectDefaultStyle.style_id == WritingStyle.id)
            .where(ProjectDefaultStyle.project_id == project_id)
        )
    ).scalar_one()

    assert default_style.user_id == TEST_USER_ID
    assert default_style.style_type == "custom"
    assert default_style.name.endswith("同类创作风格")
    assert "同类型创作" in default_style.prompt_content
    assert "保留原书的叙事口吻、节奏、视角行为和情绪温度" in default_style.prompt_content
    assert "不要照搬原书人物姓名、组织名称、专有名词或具体事件顺序" in default_style.prompt_content
    assert "preserve source cadence without copying names" in default_style.prompt_content
    assert "match rhythm, POV behavior, and narrative temperature" in default_style.prompt_content


@pytest.mark.asyncio
async def test_create_inspired_project_default_style_uses_inspired_pattern_pack(monkeypatch, api_context):
    client: AsyncClient = api_context["client"]

    import app.services.book_remix_service as remix_service_module

    async def fake_resolve_fresh_pattern_pack(*, repo_root, force=False, **kwargs):
        return {
            "style_signature_hints": ["preserve source cadence without copying names"],
            "inspired_mapping_targets": ["character_remap", "organization_remap", "world_rule_remap"],
            "inspired_prompt_hints": ["Use source style only as rhythm and POV guidance."],
            "inspired_transformation_hints": ["Rename and reframe source entities before drafting."],
            "inspired_copy_risk_hints": ["Reject copied source names, events, and set-piece order."],
        }

    monkeypatch.setattr(
        remix_service_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve_fresh_pattern_pack,
    )

    task = StubRemixTask()
    task.normalized_chapters = [
        BookImportChapter(
            title="Ledger Rain",
            content="Lin kept his answer short. The rain moved across the archive windows.",
            summary="Restrained archive pressure.",
            chapter_number=1,
        )
    ]
    await _register_stub_remix_task(task)
    try:
        response = await client.post(
            f"/api/book-remix/tasks/{task.task_id}/create-project",
            json={
                "project_suggestion": {
                    "title": "Inspired Draft",
                    "description": "User-provided same-type direction.",
                    "theme": "urban mystery",
                    "genre": "悬疑",
                    "narrative_perspective": "limited third person",
                    "target_words": 120000,
                }
            },
        )
    finally:
        await _drop_stub_remix_task(task.task_id)

    assert response.status_code == 200
    project_id = response.json()["project_id"]
    db_session: AsyncSession = api_context["db_session"]
    default_style = (
        await db_session.execute(
            select(WritingStyle)
            .join(ProjectDefaultStyle, ProjectDefaultStyle.style_id == WritingStyle.id)
            .where(ProjectDefaultStyle.project_id == project_id)
        )
    ).scalar_one()

    assert "【公开来源同类创作约束】" in default_style.prompt_content
    assert "character_remap" in default_style.prompt_content
    assert "Use source style only as rhythm and POV guidance." in default_style.prompt_content
    assert "Rename and reframe source entities before drafting." in default_style.prompt_content
    assert "Reject copied source names, events, and set-piece order." in default_style.prompt_content


@pytest.mark.asyncio
async def test_create_inspired_project_style_lists_source_names_as_forbidden_copy_targets(monkeypatch, api_context):
    client: AsyncClient = api_context["client"]

    import app.services.book_remix_service as remix_service_module

    async def fake_resolve_fresh_pattern_pack(*, repo_root, force=False, **kwargs):
        return {}

    monkeypatch.setattr(
        remix_service_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve_fresh_pattern_pack,
    )

    task = StubRemixTask()
    task.task_id = "task-inspired-forbidden-source-names"
    task.normalized_chapters = [
        BookImportChapter(
            title="青岚会的雨夜",
            content=(
                "林寒说道，青岚会不会放过星火系统。"
                "沈璃看向林寒，林寒皱眉，沈璃点头。"
                "青岚会的车停在门外，星火系统再次亮起。"
            ),
            summary="林寒和沈璃被青岚会追踪，星火系统暴露。",
            chapter_number=1,
        ),
        BookImportChapter(
            title="星火系统的回声",
            content=(
                "林寒转身，沈璃低声道，青岚会已经找到星火系统。"
                "星火系统在林寒掌心重启，青岚会的人影逼近。"
            ),
            summary="星火系统重启，青岚会继续施压。",
            chapter_number=2,
        ),
    ]
    await _register_stub_remix_task(task)
    try:
        response = await client.post(
            f"/api/book-remix/tasks/{task.task_id}/create-project",
            json={
                "project_suggestion": {
                    "title": "Inspired Draft",
                    "description": "User-provided same-type direction.",
                    "theme": "urban mystery",
                    "genre": "悬疑",
                    "narrative_perspective": "第三人称",
                    "target_words": 120000,
                }
            },
        )
    finally:
        await _drop_stub_remix_task(task.task_id)

    assert response.status_code == 200
    project_id = response.json()["project_id"]
    db_session: AsyncSession = api_context["db_session"]
    default_style = (
        await db_session.execute(
            select(WritingStyle)
            .join(ProjectDefaultStyle, ProjectDefaultStyle.style_id == WritingStyle.id)
            .where(ProjectDefaultStyle.project_id == project_id)
        )
    ).scalar_one()

    assert "源书显性元素禁用清单" in default_style.prompt_content
    assert "林寒" in default_style.prompt_content
    assert "沈璃" in default_style.prompt_content
    assert "青岚会" in default_style.prompt_content
    assert "星火系统" in default_style.prompt_content
    assert "以下名称只能作为改造参考，正文不得原样沿用" in default_style.prompt_content


@pytest.mark.asyncio
async def test_create_inspired_project_response_returns_prepared_style_id(monkeypatch, api_context):
    client: AsyncClient = api_context["client"]

    import app.services.book_remix_service as remix_service_module

    async def fake_resolve_fresh_pattern_pack(*, repo_root, force=False, **kwargs):
        return {
            "style_signature_hints": ["style id response source hint"],
            "style_fidelity_hints": ["style id response fidelity hint"],
        }

    monkeypatch.setattr(
        remix_service_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve_fresh_pattern_pack,
    )

    task = StubRemixTask()
    await _register_stub_remix_task(task)
    try:
        response = await client.post(
            f"/api/book-remix/tasks/{task.task_id}/create-project",
            json={
                "project_suggestion": {
                    "title": "Inspired Draft",
                    "description": "User-provided same-type direction.",
                    "theme": "urban mystery",
                    "genre": "悬疑",
                    "narrative_perspective": "limited third person",
                    "target_words": 120000,
                }
            },
        )
    finally:
        await _drop_stub_remix_task(task.task_id)

    assert response.status_code == 200
    payload = response.json()
    assert payload["prepared_style_id"]

    db_session: AsyncSession = api_context["db_session"]
    default_style_id = (
        await db_session.execute(
            select(ProjectDefaultStyle.style_id)
            .where(ProjectDefaultStyle.project_id == payload["project_id"])
        )
    ).scalar_one()
    assert payload["prepared_style_id"] == default_style_id


def test_create_project_response_schema_exposes_prepared_style_id():
    payload = BookRemixCreateProjectResponse(
        success=True,
        project_id="project-id",
        remix_mode="inspired",
        total_chapters=1,
        total_words=100,
        prepared_style_id=42,
        message="created",
    )

    assert payload.model_dump()["prepared_style_id"] == 42


async def _seed_plot_analysis_for_chapters(
    db_session: AsyncSession,
    *,
    project_id: str,
    chapter_ids: list[str],
) -> None:
    analyses = [
        PlotAnalysis(
            project_id=project_id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            conflict_types=["person_vs_environment"],
            foreshadows=[
                {"content": "Only cash left may not survive the city", "type": "planted"},
                {"content": "Lehua card hides an opportunity and a trap", "type": "planted"},
            ],
            plot_points=[
                {"content": "Yang Cui leaves home and goes to Shanghai with little cash"},
            ],
            character_states=[
                {"character_name": "Yang Cui", "state_after": "frightened but determined"},
            ],
            analysis_report="This chapter establishes escape and survival as the main line.",
        ),
        PlotAnalysis(
            project_id=project_id,
            chapter_id=chapter_ids[1],
            plot_stage="development",
            conflict_types=["person_vs_environment", "person_vs_self"],
            foreshadows=[
                {"content": "Lehua entertainment interview may change her life", "type": "planted"},
            ],
            plot_points=[
                {"content": "After arriving at Shanghai station, she takes the Lehua business card"},
            ],
            character_states=[
                {"character_name": "Yang Cui", "state_after": "confused but holding the only chance"},
            ],
            analysis_report="This chapter moves into Shanghai survival and entertainment entry.",
        ),
    ]
    db_session.add_all(analyses)
    await db_session.commit()


async def _seed_continuation_plan(
    db_session: AsyncSession,
    *,
    project_id: str,
    bible_id: str | None = None,
    status: str = "draft",
) -> BookRemixContinuationPlan:
    plan = BookRemixContinuationPlan(
        project_id=project_id,
        bible_id=bible_id,
        status=status,
        summary="Existing continuation plan",
        stage_goals=[{"goal": "Keep arc stable"}],
        beats=[{"beat": "Baseline beat"}],
        priority_hooks=[{"hook": "old hook"}],
        guardrails=[{"rule": "Keep perspective stable"}],
    )
    if status == "confirmed":
        plan.confirmed_at = datetime.utcnow()
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)
    return plan


@pytest.mark.asyncio
async def test_get_bible_returns_editable_and_readonly_sections(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    await _seed_draft_bible(db_session, project_id=project.id)

    response = await client.get(f"/api/book-remix/projects/{project.id}/bible")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project.id
    assert payload["generation_status"] == "generated"
    assert payload["character_cards"][0]["name"] == "Old"
    assert payload["timeline"][0]["chapter"] == 1
    assert payload["story_arcs"][0]["name"] == "Old Arc"
    assert payload["foreshadows"][0]["hook"] == "old hook"
    assert payload["hard_constraints"][0]["rule"] == "old constraint"
    assert payload["world_rules"]["power_system"] == "strict"
    assert payload["organizations"][0]["name"] == "Guild"
    assert payload["style_signature"]["pov"] == "first_person"
    assert payload["conflicts"][0]["type"] == "setting"
    assert payload["generation_notes"] == ["seeded"]
    assert payload["chapter_change_packages"][0]["summary"] == "seeded change"


@pytest.mark.asyncio
async def test_get_bible_backfills_empty_core_sections_from_existing_analysis(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id)
    bible.timeline = []
    bible.foreshadows = []
    bible.hard_constraints = []
    await db_session.commit()

    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    await _seed_plot_analysis_for_chapters(
        db_session,
        project_id=project.id,
        chapter_ids=chapter_ids,
    )

    response = await client.get(f"/api/book-remix/projects/{project.id}/bible")

    assert response.status_code == 200
    payload = response.json()
    assert payload["timeline"]
    assert payload["foreshadows"]
    assert payload["hard_constraints"]
    assert any(item.get("source") in {"timeline", "foreshadows", "analysis"} for item in payload["hard_constraints"])
    assert payload["foreshadows"][0]["hook"]


@pytest.mark.asyncio
async def test_update_bible_only_mutates_editable_sections(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    await _seed_draft_bible(db_session, project_id=project.id)

    response = await client.patch(
        f"/api/book-remix/projects/{project.id}/bible",
        json={
            "character_cards": [{"name": "Lin"}],
            "timeline": [{"chapter": 2, "event": "new"}],
            "story_arcs": [{"name": "Debt Arc", "status": "open"}],
            "foreshadows": [{"hook": "broken ring", "status": "open"}],
            "hard_constraints": [{"rule": "keep core POV"}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["character_cards"][0]["name"] == "Lin"
    assert payload["timeline"][0]["chapter"] == 2
    assert payload["story_arcs"][0]["name"] == "Debt Arc"
    assert payload["foreshadows"][0]["hook"] == "broken ring"
    assert payload["hard_constraints"][0]["rule"] == "keep core POV"
    assert payload["world_rules"]["power_system"] == "strict"
    assert payload["organizations"][0]["name"] == "Guild"
    assert payload["style_signature"]["pov"] == "first_person"
    assert payload["conflicts"][0]["type"] == "setting"
    assert payload["generation_notes"] == ["seeded"]

    bible = (
        await db_session.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project.id)
        )
    ).scalar_one()
    assert bible.character_cards[0]["name"] == "Lin"
    assert bible.world_rules["power_system"] == "strict"
    assert bible.organizations[0]["name"] == "Guild"
    assert bible.style_signature["pov"] == "first_person"
    assert bible.conflicts[0]["type"] == "setting"
    assert bible.generation_notes == ["seeded"]


@pytest.mark.asyncio
async def test_update_confirmed_bible_returns_to_generated_and_clears_confirmed_at(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.confirmed_at = datetime.utcnow()
    await db_session.commit()
    await db_session.refresh(bible)

    response = await client.patch(
        f"/api/book-remix/projects/{project.id}/bible",
        json={"story_arcs": [{"name": "Debt Arc", "status": "open"}]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_status"] == "generated"
    assert payload["confirmed_at"] is None

    updated_bible = (
        await db_session.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project.id)
        )
    ).scalar_one()
    assert updated_bible.generation_status == "generated"
    assert updated_bible.confirmed_at is None


@pytest.mark.asyncio
async def test_update_bible_with_canon_changes_invalidates_confirmed_continuation_plan(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="generated")
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="confirmed",
    )

    response = await client.patch(
        f"/api/book-remix/projects/{project.id}/bible",
        json={"story_arcs": [{"name": "Debt Arc", "status": "open"}]},
    )

    assert response.status_code == 200

    persisted_plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project.id
            )
        )
    ).scalar_one()
    assert persisted_plan.status == "draft"
    assert persisted_plan.confirmed_at is None


@pytest.mark.asyncio
async def test_update_bible_rejects_readonly_section_payload(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    await _seed_draft_bible(db_session, project_id=project.id)

    response = await client.patch(
        f"/api/book-remix/projects/{project.id}/bible",
        json={"world_rules": {"new_rule": "forbidden"}},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_confirm_bible_rejects_when_no_draft_bible(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)

    response = await client.post(f"/api/book-remix/projects/{project.id}/bible/confirm")

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_confirm_bible_marks_confirmed(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    await _seed_draft_bible(db_session, project_id=project.id, generation_status="generated")

    response = await client.post(f"/api/book-remix/projects/{project.id}/bible/confirm")

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_status"] == "confirmed"
    assert payload["confirmed_at"] is not None

    bible = (
        await db_session.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project.id)
        )
    ).scalar_one()
    assert bible.generation_status == "confirmed"
    assert bible.confirmed_at is not None


@pytest.mark.asyncio
async def test_regenerate_bible_rebuilds_draft_from_source_chapters(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]
    stub_ai_service: StubAIService = api_context["stub_ai_service"]

    project = await _seed_continuation_project(db_session)
    await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    await _seed_source_chapters(db_session, project_id=project.id)

    response = await client.post(f"/api/book-remix/projects/{project.id}/bible/regenerate")

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_status"] == "generated"
    assert payload["source_chapter_count"] == 2
    assert payload["world_rules"]["canon"] == "strict"
    assert payload["character_cards"][0]["name"] == "Lin"
    assert payload["hard_constraints"][0]["rule"] == "keep core POV"
    assert payload["confirmed_at"] is None
    assert stub_ai_service.calls == 1

    bible = (
        await db_session.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project.id)
        )
    ).scalar_one()
    assert bible.generation_status == "generated"
    assert bible.source_chapter_count == 2
    assert bible.world_rules["canon"] == "strict"
    assert bible.character_cards[0]["name"] == "Lin"
    assert bible.confirmed_at is None


@pytest.mark.asyncio
async def test_regenerate_bible_invalidates_confirmed_continuation_plan(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="confirmed",
    )
    await _seed_source_chapters(db_session, project_id=project.id)

    response = await client.post(f"/api/book-remix/projects/{project.id}/bible/regenerate")

    assert response.status_code == 200

    persisted_plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project.id
            )
        )
    ).scalar_one()
    assert persisted_plan.status == "draft"
    assert persisted_plan.confirmed_at is None


@pytest.mark.asyncio
async def test_regenerate_bible_requires_existing_bible_row(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    await _seed_source_chapters(db_session, project_id=project.id)

    response = await client.post(f"/api/book-remix/projects/{project.id}/bible/regenerate")

    assert response.status_code == 409


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["running", "failed"])
async def test_confirm_bible_rejects_non_ready_generation_status(api_context, status: str):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    await _seed_draft_bible(db_session, project_id=project.id, generation_status=status)

    response = await client.post(f"/api/book-remix/projects/{project.id}/bible/confirm")

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_normal_project_cannot_regenerate_remix_bible(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_normal_project(db_session)
    await _seed_source_chapters(db_session, project_id=project.id)

    response = await client.post(f"/api/book-remix/projects/{project.id}/bible/regenerate")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_generate_continuation_plan_requires_confirmed_bible(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    await _seed_draft_bible(db_session, project_id=project.id, generation_status="generated")

    response = await client.post(
        f"/api/book-remix/projects/{project.id}/continuation-plan/generate",
        json={"user_direction": "Continue from original ending"},
    )

    assert response.status_code == 400
    assert "confirmed remix bible required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_continuation_plan_persists_plan_and_bible_binding(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]
    stub_ai_service: StubAIService = api_context["stub_ai_service"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")

    response = await client.post(
        f"/api/book-remix/projects/{project.id}/continuation-plan/generate",
        json={"user_direction": "Continue from original ending"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project.id
    assert payload["bible_id"] == bible.id
    assert payload["status"] == "draft"
    assert payload["confirmed_at"] is None
    assert payload["summary"] == "Recover old hooks before expanding cast scope."
    assert payload["stage_goals"][0]["goal"] == "Payoff first unresolved ledger hook"
    assert payload["beats"][0]["beat"] == "Reveal the old rival in public"
    assert payload["priority_hooks"][0]["hook"] == "broken ring"
    assert payload["guardrails"][0]["rule"] == "No sudden new power systems"
    assert stub_ai_service.calls == 1

    persisted_plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project.id
            )
        )
    ).scalar_one()
    assert persisted_plan.bible_id == bible.id
    assert persisted_plan.status == "draft"
    assert persisted_plan.confirmed_at is None
    assert persisted_plan.summary == "Recover old hooks before expanding cast scope."
    assert persisted_plan.stage_goals[0]["goal"] == "Payoff first unresolved ledger hook"
    assert persisted_plan.beats[0]["beat"] == "Reveal the old rival in public"
    assert persisted_plan.priority_hooks[0]["hook"] == "broken ring"
    assert persisted_plan.guardrails[0]["rule"] == "No sudden new power systems"


@pytest.mark.asyncio
async def test_generate_continuation_plan_prompt_receives_latest_pattern_pack(monkeypatch, api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]
    stub_ai_service: StubAIService = api_context["stub_ai_service"]

    import app.services.book_remix_continuation_plan_service as plan_service_module

    monkeypatch.setattr(
        plan_service_module.source_discovery_service,
        "load_latest_pattern_pack",
        lambda *, repo_root: {
            "continuation_prompt_hints": ["API 续写规划应读取来源模式提示。"],
            "style_signature_hints": ["API 续写规划应保留原书味道。"],
        },
    )

    project = await _seed_continuation_project(db_session)
    await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")

    response = await client.post(
        f"/api/book-remix/projects/{project.id}/continuation-plan/generate",
        json={"user_direction": "Continue from original ending"},
    )

    assert response.status_code == 200
    assert stub_ai_service.calls == 1
    assert "API 续写规划应读取来源模式提示" in stub_ai_service.last_prompt
    assert "API 续写规划应保留原书味道" in stub_ai_service.last_prompt


@pytest.mark.asyncio
async def test_generate_continuation_plan_coerces_string_arrays_from_ai_payload(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]
    stub_ai_service: StubAIService = api_context["stub_ai_service"]

    stub_ai_service.payload = {
        **stub_ai_service.payload,
        "summary": "Continue directly from chapter 200 and keep the fallout in play.",
        "stage_goals": ["Stabilize the immediate aftermath of the promise"],
        "beats": ["Yena tests whether Yang Cui is hiding something"],
        "priority_hooks": ["The ring is both a bond and a risk"],
        "guardrails": ["Do not erase the stairwell ending"],
    }

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")

    response = await client.post(
        f"/api/book-remix/projects/{project.id}/continuation-plan/generate",
        json={"user_direction": ""},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["stage_goals"] == [{"goal": "Stabilize the immediate aftermath of the promise"}]
    assert payload["beats"] == [{"beat": "Yena tests whether Yang Cui is hiding something"}]
    assert payload["priority_hooks"] == [{"hook": "The ring is both a bond and a risk"}]
    assert payload["guardrails"] == [{"rule": "Do not erase the stairwell ending"}]

    persisted_plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project.id
            )
        )
    ).scalar_one()
    assert persisted_plan.bible_id == bible.id
    assert persisted_plan.stage_goals == [{"goal": "Stabilize the immediate aftermath of the promise"}]
    assert persisted_plan.beats == [{"beat": "Yena tests whether Yang Cui is hiding something"}]
    assert persisted_plan.priority_hooks == [{"hook": "The ring is both a bond and a risk"}]
    assert persisted_plan.guardrails == [{"rule": "Do not erase the stairwell ending"}]


@pytest.mark.asyncio
async def test_generate_continuation_plan_backfills_summary_only_payload(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]
    stub_ai_service: StubAIService = api_context["stub_ai_service"]

    stub_ai_service.payload = {
        **stub_ai_service.payload,
        "summary": "Continue directly from chapter 200 and preserve the immediate fallout.",
        "stage_goals": [],
        "beats": [],
        "priority_hooks": [],
        "guardrails": [],
    }

    project = await _seed_continuation_project(db_session)
    await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")

    response = await client.post(
        f"/api/book-remix/projects/{project.id}/continuation-plan/generate",
        json={"user_direction": ""},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == "Continue directly from chapter 200 and preserve the immediate fallout."
    assert payload["stage_goals"]
    assert payload["beats"]
    assert payload["priority_hooks"]
    assert payload["guardrails"]


@pytest.mark.asyncio
async def test_create_continuation_project_lineage_can_feed_commit_and_context_pipeline(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    task = StubRemixTask()
    task.task_id = "task-continuation-source"
    task.remix_mode = "continuation"
    task.normalized_chapters = [
        BookImportChapter(
            title="Source Chapter 1",
            content="Inspector Lin found the first ledger clue in the rain.",
            summary="First ledger clue.",
            chapter_number=1,
        ),
        BookImportChapter(
            title="Source Chapter 2",
            content="Inspector Lin carried the old ledger state toward the city archive.",
            summary="Old ledger state reaches archive.",
            chapter_number=2,
        ),
    ]

    await _register_stub_remix_task(task)
    try:
        create_response = await client.post(
            f"/api/book-remix/tasks/{task.task_id}/create-project",
            json={
                "project_suggestion": {
                    "title": "Continuation Imported Project",
                    "description": "Continue from the imported source book.",
                    "theme": "archive mystery",
                    "genre": "mystery",
                    "narrative_perspective": "third_person",
                    "target_words": 120000,
                }
            },
        )
    finally:
        await _drop_stub_remix_task(task.task_id)

    assert create_response.status_code == 200
    project_id = create_response.json()["project_id"]

    project = (
        await db_session.execute(select(Project).where(Project.id == project_id))
    ).scalar_one()
    bible = (
        await db_session.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project_id)
        )
    ).scalar_one()

    assert "continuation" in project.description
    assert bible.source_task_id == task.task_id
    assert bible.source_chapter_count == len(task.normalized_chapters)
    assert bible.generation_status == "running"

    bible.generation_status = "generated"
    await db_session.commit()

    confirm_bible_response = await client.post(f"/api/book-remix/projects/{project_id}/bible/confirm")
    assert confirm_bible_response.status_code == 200
    assert confirm_bible_response.json()["generation_status"] == "confirmed"

    generate_plan_response = await client.post(
        f"/api/book-remix/projects/{project_id}/continuation-plan/generate",
        json={"user_direction": "Continue from the city archive without replaying source chapters."},
    )
    assert generate_plan_response.status_code == 200
    plan_id = generate_plan_response.json()["id"]

    confirm_plan_response = await client.post(
        f"/api/book-remix/projects/{project_id}/continuation-plan/confirm"
    )
    assert confirm_plan_response.status_code == 200
    assert confirm_plan_response.json()["status"] == "confirmed"

    commit_result = await BookRemixContinuationStateService().commit_generated_chapter(
        db=db_session,
        project_id=project_id,
        chapter_id="generated-chapter-3",
        chapter_number=3,
        chapter_title="Archive Continuation",
        chapter_content=(
            "PIPELINE_SENTINEL: Inspector Lin used the imported ledger state "
            "to question the archive witness."
        ),
        chapter_outline="Question the archive witness after the imported source ending.",
        previous_chapter_summary="Inspector Lin carried the old ledger state toward the city archive.",
        continuation_point="The archive door opened after the source ending.",
    )

    assert commit_result["changed"] is True
    assert "chapter_change_packages" in commit_result["changed_sections"]

    await db_session.refresh(bible)
    assert any(
        package.get("source") == "chapter_generation"
        and package.get("chapter_number") == 3
        and "PIPELINE_SENTINEL" in package.get("summary", "")
        for package in bible.chapter_change_packages
    )

    persisted_plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(BookRemixContinuationPlan.id == plan_id)
        )
    ).scalar_one()
    assert persisted_plan.status == "confirmed"
    assert persisted_plan.bible_id == bible.id

    context_response = await client.get(f"/api/book-remix/projects/{project_id}/continuation-context-preview")
    assert context_response.status_code == 200
    payload = context_response.json()
    assert payload["has_context"] is True
    assert payload["lineage_confirmed"] is True
    assert payload["reason"] is None
    assert "Remix Continuation Canon" in payload["context"]
    assert "Recent chapter change packages" in payload["context"]
    assert "Archive Continuation" in payload["context"]
    assert "PIPELINE_SENTINEL" in payload["context"]


@pytest.mark.asyncio
async def test_get_continuation_plan_backfills_legacy_summary_only_plan(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="draft",
    )

    plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project.id
            )
        )
    ).scalar_one()
    plan.summary = "Legacy thin plan"
    plan.stage_goals = []
    plan.beats = []
    plan.priority_hooks = []
    plan.guardrails = []
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/continuation-plan")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == "Legacy thin plan"
    assert payload["stage_goals"]
    assert payload["beats"]
    assert payload["priority_hooks"]
    assert payload["guardrails"]


@pytest.mark.asyncio
async def test_update_confirmed_continuation_plan_returns_to_draft(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="confirmed",
    )

    response = await client.patch(
        f"/api/book-remix/projects/{project.id}/continuation-plan",
        json={
            "summary": "Edited plan summary",
            "guardrails": [{"rule": "Do not break timeline continuity"}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "draft"
    assert payload["confirmed_at"] is None
    assert payload["summary"] == "Edited plan summary"
    assert payload["guardrails"][0]["rule"] == "Do not break timeline continuity"

    persisted_plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project.id
            )
        )
    ).scalar_one()
    assert persisted_plan.status == "draft"
    assert persisted_plan.confirmed_at is None
    assert persisted_plan.summary == "Edited plan summary"
    assert persisted_plan.guardrails[0]["rule"] == "Do not break timeline continuity"


@pytest.mark.asyncio
async def test_confirm_continuation_plan_marks_confirmed(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="draft",
    )

    response = await client.post(f"/api/book-remix/projects/{project.id}/continuation-plan/confirm")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "confirmed"
    assert payload["confirmed_at"] is not None

    persisted_plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project.id
            )
        )
    ).scalar_one()
    assert persisted_plan.status == "confirmed"
    assert persisted_plan.confirmed_at is not None


@pytest.mark.asyncio
async def test_confirm_continuation_plan_syncs_existing_source_analysis(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 2
    bible.chapter_change_packages = []
    await db_session.commit()

    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    await _seed_plot_analysis_for_chapters(
        db_session,
        project_id=project.id,
        chapter_ids=chapter_ids,
    )
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="draft",
    )

    response = await client.post(f"/api/book-remix/projects/{project.id}/continuation-plan/confirm")

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"

    await db_session.refresh(bible)
    analysis_packages = [
        package
        for package in bible.chapter_change_packages
        if package.get("source") == "chapter_analysis"
    ]
    assert [package["chapter_number"] for package in analysis_packages] == [1, 2]
    assert analysis_packages[0]["summary"] == "Yang Cui leaves home and goes to Shanghai with little cash"
    assert analysis_packages[1]["summary"] == "After arriving at Shanghai station, she takes the Lehua business card"

    coverage_response = await client.get(f"/api/book-remix/projects/{project.id}/analysis-coverage")
    assert coverage_response.status_code == 200
    coverage = coverage_response.json()
    assert coverage["fully_analyzed"] is True
    assert coverage["fully_synced"] is True
    assert coverage["missing_analysis_chapters"] == []
    assert coverage["missing_change_package_chapters"] == []
    assert coverage["continuation_risk"]["level"] == "low"
    assert coverage["continuation_risk"]["can_continue"] is True


@pytest.mark.asyncio
async def test_confirm_continuation_plan_rejects_stale_plan_after_bible_changes(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="draft",
    )

    bible_update_response = await client.patch(
        f"/api/book-remix/projects/{project.id}/bible",
        json={"story_arcs": [{"name": "Debt Arc", "status": "open"}]},
    )
    assert bible_update_response.status_code == 200

    bible_confirm_response = await client.post(f"/api/book-remix/projects/{project.id}/bible/confirm")
    assert bible_confirm_response.status_code == 200
    assert bible_confirm_response.json()["generation_status"] == "confirmed"

    response = await client.post(f"/api/book-remix/projects/{project.id}/continuation-plan/confirm")
    assert response.status_code == 409
    assert "regenerate the plan" in response.json()["detail"]

    persisted_plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project.id
            )
        )
    ).scalar_one()
    assert persisted_plan.status == "draft"
    assert persisted_plan.confirmed_at is None


@pytest.mark.asyncio
async def test_update_missing_continuation_plan_returns_404(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)

    response = await client.patch(
        f"/api/book-remix/projects/{project.id}/continuation-plan",
        json={"summary": "new summary"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_continuation_plan_rejects_extra_field_payload(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="draft",
    )

    response = await client.patch(
        f"/api/book-remix/projects/{project.id}/continuation-plan",
        json={
            "summary": "edited",
            "status": "confirmed",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_confirm_missing_continuation_plan_returns_400(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)

    response = await client.post(f"/api/book-remix/projects/{project.id}/continuation-plan/confirm")

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_missing_continuation_plan_returns_404(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)

    response = await client.get(f"/api/book-remix/projects/{project.id}/continuation-plan")

    assert response.status_code == 404



@pytest.mark.asyncio
async def test_get_continuation_context_preview_returns_actual_prompt_context(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.character_cards = [{"name": "Inspector Lin", "continuation_updates": []}]
    bible.timeline = [{"event": "Manual source ending", "source": "manual"}]
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 20,
            "summary": "Inspector Lin questioned the archive witness.",
            "timeline_delta": [{"event": "Archive witness revealed a sealed file"}],
            "character_state_changes": [
                {"character_name": "Inspector Lin", "state_after": "suspicious"}
            ],
            "foreshadow_changes": [{"hook": "Sealed file points to city hall", "status": "open"}],
            "plan_progress": [{"beat": "Question archive witness", "status": "done"}],
        }
    ]
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="confirmed",
    )
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/continuation-context-preview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project.id
    assert payload["has_context"] is True
    assert payload["lineage_confirmed"] is True
    assert payload["reason"] is None
    assert payload["context_length"] == len(payload["context"])
    assert "Remix Continuation Canon" in payload["context"]
    assert "Project: Remix Project" in payload["context"]
    assert "Whole-book continuation progress" in payload["context"]
    assert "Archive witness revealed a sealed file" in payload["context"]
    assert "Sealed file points to city hall" in payload["context"]


@pytest.mark.asyncio
async def test_get_continuation_context_preview_explains_unconfirmed_or_stale_lineage(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="draft",
    )

    response = await client.get(f"/api/book-remix/projects/{project.id}/continuation-context-preview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project.id
    assert payload["has_context"] is False
    assert payload["lineage_confirmed"] is False
    assert payload["context"] == ""
    assert payload["context_length"] == 0
    assert payload["reason"] == "continuation_plan_not_confirmed"


@pytest.mark.asyncio
async def test_get_chapter_change_packages_returns_ordered_audit_items(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="generated")
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "manual",
            "summary": "Reviewer note without chapter number",
        },
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 20,
            "chapter_title": "Archive Witness",
            "summary": "Inspector Lin questioned the archive witness.",
            "timeline_delta": [{"event": "Archive witness revealed a sealed file"}],
            "character_state_changes": [
                {"character_name": "Inspector Lin", "state_after": "suspicious"}
            ],
            "foreshadow_changes": [{"hook": "Sealed file points to city hall", "status": "open"}],
            "plan_progress": [{"beat": "Question archive witness", "status": "done"}],
            "changed_sections": ["timeline", "character_cards", "foreshadows"],
        },
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 19,
            "chapter_title": "Ledger",
            "summary": "Inspector Lin recovered the ledger.",
        },
        "ignored non-object package",
        {
            "type": "chapter_change_package",
            "source": "manual",
            "chapter_number": 18,
            "summary": "Manual chapter anchor.",
        },
    ]
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/chapter-change-packages")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project.id
    assert payload["package_count"] == 4
    assert payload["offset"] == 0
    assert payload["limit"] == 100
    assert [item["summary"] for item in payload["items"]] == [
        "Manual chapter anchor.",
        "Inspector Lin recovered the ledger.",
        "Inspector Lin questioned the archive witness.",
        "Reviewer note without chapter number",
    ]
    assert payload["items"][2]["changed_sections"] == ["timeline", "character_cards", "foreshadows"]

    filtered_response = await client.get(
        f"/api/book-remix/projects/{project.id}/chapter-change-packages"
        "?source=chapter_analysis&limit=1&offset=1"
    )

    assert filtered_response.status_code == 200
    filtered_payload = filtered_response.json()
    assert filtered_payload["package_count"] == 2
    assert filtered_payload["offset"] == 1
    assert filtered_payload["limit"] == 1
    assert len(filtered_payload["items"]) == 1
    assert filtered_payload["items"][0]["chapter_number"] == 20


@pytest.mark.asyncio
async def test_get_chapter_change_packages_returns_404_when_bible_missing(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)

    response = await client.get(f"/api/book-remix/projects/{project.id}/chapter-change-packages")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_analysis_coverage_reports_missing_analysis_and_change_packages(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 3
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 1,
            "summary": "Chapter one synced.",
        },
        {
            "type": "chapter_change_package",
            "source": "manual",
            "chapter_number": 2,
            "summary": "Manual note does not count as analysis sync.",
        },
    ]
    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    chapter_3 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Chapter 3",
        content="Third chapter content",
        summary="Third summary",
        status="completed",
    )
    db_session.add(chapter_3)
    await db_session.commit()
    await db_session.refresh(chapter_3)

    db_session.add_all([
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            analysis_report="Chapter one analyzed.",
        ),
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_3.id,
            plot_stage="development",
            analysis_report="Chapter three analyzed.",
        ),
    ])
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/analysis-coverage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project.id
    assert payload["source_chapter_count"] == 3
    assert payload["source_chapters_count"] == 3
    assert payload["analyzed_chapter_count"] == 2
    assert payload["chapter_change_package_count"] == 1
    assert payload["analysis_coverage_percent"] == 67
    assert payload["change_package_coverage_percent"] == 33
    assert payload["fully_analyzed"] is False
    assert payload["fully_synced"] is False
    assert [item["chapter_number"] for item in payload["missing_analysis_chapters"]] == [2]
    assert [item["chapter_number"] for item in payload["missing_change_package_chapters"]] == [2, 3]
    assert payload["missing_source_chapters"] == []


@pytest.mark.asyncio
async def test_get_analysis_coverage_counts_generated_packages_as_continuation_context(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 2
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 1,
            "summary": "Chapter one analysis synced.",
        },
        {
            "type": "chapter_change_package",
            "source": "chapter_generation",
            "chapter_number": 2,
            "summary": "Chapter two generated and immediately committed.",
        },
    ]
    await _seed_source_chapters(db_session, project_id=project.id)
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/analysis-coverage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["chapter_change_package_count"] == 2
    assert payload["change_package_coverage_percent"] == 100
    assert payload["fully_synced"] is True
    assert payload["missing_change_package_chapters"] == []


@pytest.mark.asyncio
async def test_get_analysis_coverage_stays_high_risk_when_generated_package_lacks_source_analysis(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 2
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 1,
            "summary": "Chapter one analysis synced.",
        },
        {
            "type": "chapter_change_package",
            "source": "chapter_generation",
            "chapter_number": 2,
            "summary": "Chapter two generated, but source analysis still missing.",
        },
    ]
    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    db_session.add(
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            analysis_report="Chapter one analyzed.",
        )
    )
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/analysis-coverage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["chapter_change_package_count"] == 2
    assert payload["missing_change_package_chapters"] == []
    assert [item["chapter_number"] for item in payload["missing_analysis_chapters"]] == [2]
    assert payload["continuation_risk"]["level"] == "high"
    assert payload["continuation_risk"]["blocking_chapter_numbers"] == [2]
    assert "analysis_missing_before_continuation" in payload["continuation_risk"]["reasons"]


@pytest.mark.asyncio
async def test_get_analysis_coverage_ignores_generated_continuation_chapters_after_source_range(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 2
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 1,
            "summary": "Chapter one analysis synced.",
        },
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 2,
            "summary": "Chapter two analysis synced.",
        },
        {
            "type": "chapter_change_package",
            "source": "chapter_generation",
            "chapter_number": 3,
            "summary": "Continuation chapter generated after source range.",
        },
    ]
    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    continuation_chapter = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Continuation Chapter 3",
        content="Generated continuation content",
        summary="Continuation summary",
        status="completed",
    )
    db_session.add_all([
        continuation_chapter,
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            analysis_report="Chapter one analyzed.",
        ),
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[1],
            plot_stage="development",
            analysis_report="Chapter two analyzed.",
        ),
    ])
    await db_session.commit()

    coverage_response = await client.get(f"/api/book-remix/projects/{project.id}/analysis-coverage")
    start_missing_response = await client.post(f"/api/book-remix/projects/{project.id}/analysis/start-missing")

    assert coverage_response.status_code == 200
    coverage = coverage_response.json()
    assert coverage["source_chapter_count"] == 2
    assert coverage["source_chapters_count"] == 2
    assert coverage["fully_analyzed"] is True
    assert coverage["fully_synced"] is True
    assert coverage["missing_analysis_chapters"] == []
    assert coverage["missing_change_package_chapters"] == []
    assert coverage["missing_source_chapters"] == []

    assert start_missing_response.status_code == 200
    start_missing = start_missing_response.json()
    assert start_missing["target_chapter_numbers"] == []
    assert start_missing["total_started"] == 0


@pytest.mark.asyncio
async def test_get_analysis_coverage_returns_action_plan_for_whole_book_gaps(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 5
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 1,
            "summary": "Chapter one already synced.",
        }
    ]
    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    chapter_3 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Chapter 3",
        content="Third chapter content",
        summary="Third summary",
        status="completed",
    )
    chapter_4 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=4,
        title="Chapter 4",
        content="",
        summary="Empty imported placeholder",
        status="draft",
    )
    db_session.add_all([
        chapter_3,
        chapter_4,
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            analysis_report="Chapter one analyzed and synced.",
        ),
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_3.id,
            plot_stage="development",
            analysis_report="Chapter three analyzed but not synced.",
        ),
        AnalysisTask(
            chapter_id=chapter_ids[1],
            user_id=TEST_USER_ID,
            project_id=project.id,
            status="running",
            progress=40,
        ),
    ])
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/analysis-coverage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["missing_source_chapters"] == [5]
    assert [item["chapter_number"] for item in payload["missing_analysis_chapters"]] == [2]
    assert [item["chapter_number"] for item in payload["missing_change_package_chapters"]] == [2, 3]
    assert payload["analysis_action_plan"] == [
        {
            "action": "restore_source_chapter",
            "chapter_numbers": [5],
            "chapter_count": 1,
            "reason": "source_chapter_row_missing",
        },
        {
            "action": "sync_existing_analysis",
            "chapter_numbers": [3],
            "chapter_count": 1,
            "reason": "plot_analysis_exists_without_change_package",
        },
        {
            "action": "wait_running_analysis",
            "chapter_numbers": [2],
            "chapter_count": 1,
            "reason": "analysis_task_already_running",
        },
        {
            "action": "fill_chapter_content",
            "chapter_numbers": [4],
            "chapter_count": 1,
            "reason": "chapter_content_empty",
        },
    ]
    assert payload["continuation_risk"]["level"] == "high"
    assert payload["continuation_risk"]["blocking_chapter_numbers"] == [2, 3, 4, 5]
    assert "source_chapter_content_empty" in payload["continuation_risk"]["reasons"]


@pytest.mark.asyncio
async def test_get_analysis_coverage_reports_continuation_risk_summary(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 4
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 1,
            "summary": "Chapter one already synced.",
        }
    ]
    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    chapter_3 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Chapter 3",
        content="Third chapter content",
        summary="Third summary",
        status="completed",
    )
    db_session.add_all([
        chapter_3,
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            analysis_report="Chapter one analyzed and synced.",
        ),
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_3.id,
            plot_stage="development",
            analysis_report="Chapter three analyzed but not synced.",
        ),
    ])
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/analysis-coverage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["continuation_risk"] == {
        "level": "high",
        "label": "\u9ad8\u98ce\u9669",
        "can_continue": False,
        "blocking_chapter_numbers": [2, 3, 4],
        "warning_chapter_numbers": [],
        "reasons": [
            "source_chapter_row_missing",
            "analysis_missing_before_continuation",
            "change_package_missing_before_continuation",
        ],
        "reason_labels": [
            "缺失源章节",
            "缺少章节拆解分析",
            "缺少续写状态写回",
        ],
        "message": (
            "\u7eed\u5199\u524d\u5b58\u5728 3 \u4e2a\u963b\u65ad\u7ae0\u8282\u3002"
            "0 \u4e2a\u7ae0\u8282\u4e0a\u4e0b\u6587\u504f\u8584\u3002"
            "\u5efa\u8bae\u5148\u8865\u9f50\u5168\u4e66\u89e3\u6790\u7f3a\u53e3\uff0c"
            "\u518d\u7eed\u5199\u4e0b\u4e00\u7ae0\u3002"
        ),
    }


@pytest.mark.asyncio
async def test_get_analysis_coverage_blocks_unsynced_existing_analysis(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 2
    bible.chapter_change_packages = []
    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    db_session.add_all([
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            analysis_report="Chapter one analyzed but not synced.",
        ),
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[1],
            plot_stage="development",
            analysis_report="Chapter two analyzed but not synced.",
        ),
    ])
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/analysis-coverage")

    assert response.status_code == 200
    payload = response.json()
    assert payload["missing_analysis_chapters"] == []
    assert [item["chapter_number"] for item in payload["missing_change_package_chapters"]] == [1, 2]
    assert payload["continuation_risk"]["level"] == "high"
    assert payload["continuation_risk"]["can_continue"] is False
    assert payload["continuation_risk"]["blocking_chapter_numbers"] == [1, 2]
    assert payload["continuation_risk"]["warning_chapter_numbers"] == []
    assert "change_package_missing_before_continuation" in payload["continuation_risk"]["reasons"]


@pytest.mark.asyncio
async def test_start_missing_analysis_creates_tasks_for_unsynced_source_chapters(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 3
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 1,
            "summary": "Chapter one synced.",
        }
    ]
    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    chapter_3 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Chapter 3",
        content="Third chapter content",
        summary="Third summary",
        status="completed",
    )
    db_session.add(chapter_3)
    db_session.add(
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            analysis_report="Chapter one analyzed and synced.",
        )
    )
    db_session.add(
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_3.id,
            plot_stage="development",
            analysis_report="Chapter three analyzed but not synced.",
        )
    )
    await db_session.commit()

    response = await client.post(f"/api/book-remix/projects/{project.id}/analysis/start-missing")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project.id
    assert payload["target_chapter_numbers"] == [2, 3]
    assert payload["total_started"] == 2
    assert set(payload["started_tasks"]) == {chapter_ids[1], chapter_3.id}

    tasks = (
        await db_session.execute(
            select(AnalysisTask).where(AnalysisTask.project_id == project.id)
        )
    ).scalars().all()
    assert sorted(task.chapter_id for task in tasks) == sorted([chapter_ids[1], chapter_3.id])


@pytest.mark.asyncio
async def test_start_missing_analysis_syncs_existing_analysis_before_queueing(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 3
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 1,
            "summary": "Chapter one synced.",
        }
    ]
    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    chapter_3 = Chapter(
        id=str(uuid.uuid4()),
        project_id=project.id,
        chapter_number=3,
        title="Chapter 3",
        content="Third chapter content",
        summary="Third summary",
        status="completed",
    )
    db_session.add(chapter_3)
    db_session.add_all([
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            analysis_report="Chapter one analyzed and synced.",
        ),
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_3.id,
            plot_stage="development",
            plot_points=[
                {"content": "Chapter three closes the source-book ledger loop.", "importance": 0.9}
            ],
            analysis_report="Chapter three analyzed but not synced.",
        ),
    ])
    await db_session.commit()
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="confirmed",
    )

    response = await client.post(f"/api/book-remix/projects/{project.id}/analysis/start-missing")

    assert response.status_code == 200
    payload = response.json()
    assert payload["target_chapter_numbers"] == [2, 3]
    assert payload["total_synced_existing"] == 1
    assert payload["synced_existing_chapters"] == [3]
    assert payload["total_started"] == 1
    assert set(payload["started_tasks"]) == {chapter_ids[1]}

    await db_session.refresh(bible)
    package_numbers = [
        package.get("chapter_number")
        for package in bible.chapter_change_packages
        if package.get("source") == "chapter_analysis"
    ]
    assert package_numbers == [1, 3]

    tasks = (
        await db_session.execute(
            select(AnalysisTask).where(AnalysisTask.project_id == project.id)
        )
    ).scalars().all()
    assert [task.chapter_id for task in tasks] == [chapter_ids[1]]


@pytest.mark.asyncio
async def test_start_missing_analysis_syncs_existing_analysis_payload_with_summary_and_emotion(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.source_chapter_count = 1
    bible.chapter_change_packages = []
    chapter_ids = await _seed_source_chapters(db_session, project_id=project.id)
    db_session.add(
        PlotAnalysis(
            project_id=project.id,
            chapter_id=chapter_ids[0],
            plot_stage="development",
            emotional_tone="tense restraint",
            emotional_intensity=0.82,
            plot_points=[
                {
                    "content": "Inspector Lin learns the archive witness lied.",
                    "importance": 0.9,
                    "impact": "The next continuation must question the witness.",
                }
            ],
            character_states=[
                {
                    "character_name": "Inspector Lin",
                    "state_after": "controlled suspicion",
                    "key_event": "Caught the witness lie",
                }
            ],
            analysis_report="Human-readable analysis should not replace the structured chapter summary.",
        )
    )
    await db_session.commit()
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="confirmed",
    )

    response = await client.post(f"/api/book-remix/projects/{project.id}/analysis/start-missing")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_synced_existing"] == 1
    assert payload["total_started"] == 0

    await db_session.refresh(bible)
    package = bible.chapter_change_packages[0]
    assert package["source"] == "chapter_analysis"
    assert package["summary"] == "Inspector Lin learns the archive witness lied."
    assert package["timeline_delta"][0]["event"] == "Inspector Lin learns the archive witness lied."
    assert package["emotional_arc"]["tone"] == "tense restraint"
    assert package["emotional_arc"]["intensity"] == 0.82
    assert package["character_state_changes"][0]["state_after"] == "controlled suspicion"


@pytest.mark.asyncio
async def test_get_continuation_progress_summary_returns_structured_whole_book_analysis(api_context):
    client: AsyncClient = api_context["client"]
    db_session: AsyncSession = api_context["db_session"]

    project = await _seed_continuation_project(db_session)
    bible = await _seed_draft_bible(db_session, project_id=project.id, generation_status="confirmed")
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 19,
            "summary": "Inspector Lin recovered the ledger.",
            "timeline_delta": [{"event": "Inspector Lin recovered ledger"}],
            "character_state_changes": [
                {"character_name": "Inspector Lin", "state_after": "decisive"}
            ],
            "foreshadow_changes": [{"hook": "Old rival returns", "status": "resolved"}],
            "plan_progress": [{"beat": "Recover ledger", "status": "done"}],
        },
        {
            "type": "chapter_change_package",
            "source": "chapter_analysis",
            "chapter_number": 20,
            "summary": "Inspector Lin questioned the archive witness.",
            "timeline_delta": [{"event": "Archive witness revealed a sealed file"}],
            "character_state_changes": [
                {"character_name": "Inspector Lin", "state_after": "suspicious"}
            ],
            "foreshadow_changes": [{"hook": "Sealed file points to city hall", "status": "open"}],
            "plan_progress": [{"beat": "Question archive witness", "status": "done"}],
        },
    ]
    await _seed_continuation_plan(
        db_session,
        project_id=project.id,
        bible_id=bible.id,
        status="confirmed",
    )
    plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(BookRemixContinuationPlan.project_id == project.id)
        )
    ).scalar_one()
    plan.beats = [
        {"beat": "Recover ledger", "status": "done", "last_chapter_number": 19},
        {"beat": "Follow city hall file", "status": "pending"},
    ]
    await db_session.commit()

    response = await client.get(f"/api/book-remix/projects/{project.id}/continuation-progress-summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project.id
    assert payload["package_count"] == 2
    assert payload["chapter_range"] == {"start": 19, "end": 20}
    assert payload["timeline_progression"][-1]["event"] == "Archive witness revealed a sealed file"
    assert payload["latest_character_states"][0]["state_after"] == "suspicious"
    assert payload["resolved_hooks"] == ["Old rival returns"]
    assert payload["open_hooks"] == ["Sealed file points to city hall"]
    assert payload["completed_plan_beats"] == ["Recover ledger", "Question archive witness"]
    assert payload["pending_plan_beats"] == ["Follow city hall file"]
