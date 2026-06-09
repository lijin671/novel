from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan
from app.models.project import Project
from app.services.book_remix_context_service import (
    BookRemixContextService,
    build_remix_continuation_context_block,
    build_remix_inspired_context_block,
    build_remix_continuation_progress_summary,
)


def test_build_remix_continuation_context_block_contains_constraints_and_plan():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Recover the ledger"}],
            "timeline": [{"event": "Warehouse fire", "impact": "Ledger disappeared"}],
            "hard_constraints": [{"rule": "Do not flip protagonist alignment abruptly"}],
            "story_arcs": [{"name": "Ledger Arc", "status": "open"}],
            "foreshadows": [{"hook": "Old rival returns", "status": "open"}],
        },
        plan={
            "summary": "Resolve old ledger thread before expanding cast scope.",
            "beats": [{"beat": "Reconnect the dropped ledger line"}],
            "priority_hooks": [{"hook": "Old rival returns in public"}],
            "guardrails": [{"rule": "No sudden new power systems"}],
        },
    )

    assert "Inspector Lin" in block
    assert "Warehouse fire" in block
    assert "Do not flip protagonist alignment abruptly" in block
    assert "Reconnect the dropped ledger line" in block
    assert "Old rival returns in public" in block


def test_build_remix_continuation_context_block_renders_source_pattern_pack_guidance():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [{"name": "Yang Cui", "goal": "survive idol pressure"}],
            "timeline": [{"event": "The promise has already happened"}],
            "hard_constraints": [{"rule": "Do not erase the original ending"}],
            "style_signature": {
                "voice": "压抑克制",
                "pacing": "短句推进后释放情绪",
            },
            "organizations": [{"name": "Starship", "role": "management pressure"}],
            "conflicts": [{"name": "公开与保密", "status": "unresolved"}],
        },
        plan={"summary": "Continue from the promise."},
        source_pattern_pack={
            "continuation_prompt_hints": ["续写前先读取世界观、时间线、人物卡、组织、情感线。"],
            "style_signature_hints": ["保留原书味道，并把风格签名作为硬约束。"],
            "self_review_policy_hints": ["不限次数自评优化必须有停止条件。"],
            "safety_constraints": ["不克隆、不安装、不执行外部项目。"],
        },
    )

    assert "Source-discovered continuation guidance" in block
    assert "续写前先读取世界观" in block
    assert "保留原书味道" in block
    assert "不限次数自评优化" in block
    assert "不克隆、不安装、不执行外部项目" in block
    assert "Style signature to preserve" in block
    assert "压抑克制" in block
    assert "Organizations to preserve" in block
    assert "Starship" in block
    assert "Conflict and emotion arcs" in block
    assert "公开与保密" in block


def test_build_remix_continuation_context_block_omits_inspired_pattern_pack_guidance():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [{"name": "Yang Cui", "goal": "survive idol pressure"}],
            "timeline": [{"event": "The promise has already happened"}],
            "hard_constraints": [{"rule": "Do not erase the original ending"}],
        },
        plan={"summary": "Continue from the promise."},
        source_pattern_pack={
            "continuation_prompt_hints": ["Keep confirmed continuation canon."],
            "inspired_prompt_hints": ["Generate an independent new story."],
            "inspired_copy_risk_hints": ["Reject copied source names."],
        },
    )

    assert "Keep confirmed continuation canon." in block
    assert "inspired_prompt_hints" not in block
    assert "Generate an independent new story." not in block
    assert "Reject copied source names." not in block


def test_build_remix_inspired_context_block_renders_style_copy_risk_and_pattern_guidance():
    block = build_remix_inspired_context_block(
        project_title="Inspired Draft",
        style_content=(
            "你正在基于《源书》做同类型创作，而不是忠实续写或照搬改名。\n"
            "【同类型创作总原则】\n"
            "- 只学习写法模式、情绪曲线、信息释放节奏和人物互动质感，不复制原书事实。\n"
            "【源书语气样本】\n"
            "[样本1]\n"
            "Lin kept his answer short. The rain moved across the archive windows.\n"
            "【源书显性元素禁用清单】\n"
            "以下名称只能作为改造参考，正文不得原样沿用：\n"
            "- 林寒, 青岚会, 星火系统\n"
        ),
        source_pattern_pack={
            "inspired_mapping_targets": ["character_remap", "organization_remap"],
            "inspired_prompt_hints": ["Use source style as rhythm and POV guidance only."],
            "inspired_transformation_hints": ["Rename and reframe source entities before drafting."],
            "inspired_copy_risk_hints": ["Reject copied source names, events, and set-piece order."],
            "safety_constraints": ["Do not import external runtime code."],
        },
    )

    assert "【Remix Inspired Creation Context】" in block
    assert "Inspired Draft" in block
    assert "Do not treat this as continuation canon" in block
    assert "Lin kept his answer short" in block
    assert "林寒" in block
    assert "青岚会" in block
    assert "星火系统" in block
    assert "inspired_prompt_hints" in block
    assert "Use source style as rhythm and POV guidance only." in block
    assert "Reject copied source names" in block
    assert "Inspired transformation audit" in block
    assert "required_remaps: character_remap, organization_remap" in block
    assert "source_canon_boundary" in block
    assert "context_reference_policy" in block
    assert "copy_risk_gate" in block


def test_build_remix_inspired_context_block_ignores_ordinary_style_content():
    block = build_remix_inspired_context_block(
        project_title="Ordinary Draft",
        style_content="保持克制短句，减少形容词，不要使用上帝视角。",
        source_pattern_pack={"inspired_prompt_hints": ["should not render"]},
    )

    assert block == ""



def test_build_remix_continuation_context_block_treats_generated_state_as_latest_machine_state():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [
                {
                    "name": "Inspector Lin",
                    "goal": "Recover the ledger",
                    "continuation_updates": [
                        {
                            "chapter_number": 19,
                            "state_after": "decisive",
                            "key_event": "Recovered ledger",
                            "source": "chapter_analysis",
                        },
                        {
                            "chapter_number": 20,
                            "chapter_title": "Archive Witness",
                            "state_after": "suspicious",
                            "key_event": "Questioned the archive witness",
                            "source": "chapter_generation",
                        },
                    ],
                }
            ],
            "timeline": [
                {
                    "event": "Inspector Lin recovered ledger",
                    "summary": "The ledger arc moved into confrontation.",
                    "chapter_number": 19,
                    "source": "chapter_analysis",
                },
                {
                    "event": "Archive witness revealed a sealed file",
                    "summary": "The next lead now points to city hall.",
                    "chapter_number": 20,
                    "source": "chapter_generation",
                },
            ],
            "foreshadows": [],
            "hard_constraints": [],
            "story_arcs": [],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_generation",
                    "chapter_number": 20,
                    "chapter_title": "Archive Witness",
                    "summary": "Inspector Lin questioned the archive witness.",
                    "timeline_delta": [{"event": "Archive witness revealed a sealed file"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "suspicious"}
                    ],
                    "plan_progress": [{"beat": "Question archive witness", "status": "done"}],
                },
            ],
        },
        plan={
            "summary": "Follow the sealed file lead next.",
            "beats": [
                {"beat": "Question archive witness", "status": "done", "last_chapter_number": 20},
                {"beat": "Follow city hall file", "status": "pending"},
            ],
            "priority_hooks": [],
            "guardrails": [],
        },
    )

    assert "Latest machine timeline" in block
    assert "Archive witness revealed a sealed file" in block
    assert "Inspector Lin @ Chapter 20" in block
    assert "state_after: suspicious" in block
    assert "Whole-book continuation progress" in block
    assert "Continuation chapters with context: 20 (1 packages)" in block
    assert "Recent chapter change packages" in block
    assert "Chapter 20: Archive Witness" in block
    assert "chapter_generation" not in block



def test_build_remix_continuation_context_block_prioritizes_active_next_chapter_state():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [
                {
                    "name": "Inspector Lin",
                    "goal": "Recover the ledger",
                    "continuation_updates": [
                        {
                            "chapter_number": 18,
                            "state_after": "uncertain",
                            "key_event": "Lost the first lead",
                            "source": "chapter_analysis",
                        },
                        {
                            "chapter_number": 19,
                            "chapter_title": "Ledger Returns",
                            "state_after": "decisive",
                            "key_event": "Recovered ledger",
                            "source": "chapter_analysis",
                        },
                    ],
                }
            ],
            "timeline": [
                {"event": "Manual prologue anchor", "source": "manual"},
                {
                    "event": "Older machine event",
                    "summary": "Chapter 18 clue failed.",
                    "chapter_number": 18,
                    "source": "chapter_analysis",
                },
                {
                    "event": "Inspector Lin recovered ledger",
                    "summary": "The ledger arc moved into confrontation.",
                    "chapter_number": 19,
                    "source": "chapter_analysis",
                },
            ],
            "foreshadows": [
                {"hook": "Old rival returns", "status": "resolved", "chapter_number": 19},
                {"hook": "Archive witness hesitates", "status": "open", "chapter_number": 20},
            ],
            "hard_constraints": [{"rule": "Do not flip protagonist alignment abruptly"}],
        },
        plan={
            "summary": "Resolve old ledger thread before expanding cast scope.",
            "beats": [
                {"beat": "Recover ledger", "status": "done", "last_chapter_number": 19},
                {"beat": "Question archive witness", "status": "pending"},
            ],
            "priority_hooks": [
                {"hook": "Old rival returns", "status": "done", "last_chapter_number": 19},
                {"hook": "Archive witness hesitates", "status": "pending"},
            ],
            "guardrails": [{"rule": "No sudden new power systems"}],
        },
    )

    assert "Latest machine timeline" in block
    assert "Inspector Lin recovered ledger" in block
    assert "Manual prologue anchor" in block
    assert "Inspector Lin @ Chapter 19" in block
    assert "state_after: decisive" in block
    assert "Done planned beats" in block
    assert "Recover ledger" in block
    assert "Pending planned beats" in block
    assert "Question archive witness" in block
    assert block.index("Pending planned beats") < block.index("Done planned beats")
    assert "Resolved hooks" in block
    assert "Open hooks" in block
    assert block.index("Open hooks") < block.index("Resolved hooks")


@pytest.mark.asyncio
async def test_build_project_context_block_returns_empty_without_confirmed_bible(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Normal Project",
        description="ordinary writing project",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )
    assert block == ""


@pytest.mark.asyncio
async def test_build_project_context_block_returns_empty_with_draft_bible(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Draft Bible Project",
        description="remix continuation project",
    )
    db_session.add(project)
    await db_session.flush()

    bible = BookRemixBible(
        project_id=project.id,
        generation_status="draft",
        hard_constraints=[{"rule": "Do not flip protagonist alignment abruptly"}],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible.id,
        status="draft",
        summary="This plan should be ignored until bible is confirmed.",
    )
    db_session.add_all([bible, plan])
    await db_session.commit()
    await db_session.refresh(project)

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )
    assert block == ""


@pytest.mark.asyncio
async def test_build_project_context_block_returns_empty_with_confirmed_bible_and_missing_plan(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Continuation Desk",
        description="remix continuation project",
    )
    db_session.add(project)
    await db_session.flush()

    bible = BookRemixBible(
        project_id=project.id,
        generation_status="confirmed",
        hard_constraints=[{"rule": "Do not flip protagonist alignment abruptly"}],
        story_arcs=[{"name": "Ledger Arc", "status": "open"}],
        foreshadows=[{"hook": "Old rival returns", "status": "open"}],
    )
    db_session.add(bible)
    await db_session.commit()
    await db_session.refresh(project)

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )
    assert block == ""


@pytest.mark.asyncio
async def test_build_project_context_block_returns_empty_with_confirmed_bible_and_draft_plan(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Continuation Desk",
        description="remix continuation project",
    )
    db_session.add(project)
    await db_session.flush()

    bible = BookRemixBible(
        project_id=project.id,
        generation_status="confirmed",
        hard_constraints=[{"rule": "Do not flip protagonist alignment abruptly"}],
        story_arcs=[{"name": "Ledger Arc", "status": "open"}],
        foreshadows=[{"hook": "Old rival returns", "status": "open"}],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible.id,
        status="draft",
        summary="Resolve old ledger thread before expanding cast scope.",
        beats=[{"beat": "Reconnect the dropped ledger line"}],
        priority_hooks=[{"hook": "Old rival returns in public"}],
        guardrails=[{"rule": "No sudden new power systems"}],
    )
    db_session.add_all([bible, plan])
    await db_session.commit()
    await db_session.refresh(project)

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )
    assert block == ""


@pytest.mark.asyncio
async def test_build_project_context_block_returns_empty_for_ordinary_project_without_remix_lineage(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Ordinary Project",
        description="ordinary writing project",
    )
    db_session.add(project)
    await db_session.flush()

    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        generation_status="confirmed",
        source_chapter_count=0,
        hard_constraints=[{"rule": "Do not flip protagonist alignment abruptly"}],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        summary="Resolve old ledger thread before expanding cast scope.",
        beats=[{"beat": "Reconnect the dropped ledger line"}],
        priority_hooks=[{"hook": "Old rival returns in public"}],
        guardrails=[{"rule": "No sudden new power systems"}],
    )
    db_session.add_all([bible, plan])
    await db_session.commit()
    await db_session.refresh(project)

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )
    assert block == ""


@pytest.mark.asyncio
async def test_has_project_durable_remix_lineage_returns_false_without_bible(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Ordinary Project",
        description="ordinary writing project",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    has_lineage = await BookRemixContextService().has_project_durable_remix_lineage(
        project=project,
        db=db_session,
    )
    assert has_lineage is False


@pytest.mark.asyncio
async def test_has_project_durable_remix_lineage_returns_true_with_source_markers(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Remix Continuation Project",
        description="remix continuation project",
    )
    db_session.add(project)
    await db_session.flush()

    bible = BookRemixBible(
        project_id=project.id,
        source_task_id="task-1",
        source_chapter_count=18,
        generation_status="generated",
    )
    db_session.add(bible)
    await db_session.commit()
    await db_session.refresh(project)

    has_lineage = await BookRemixContextService().has_project_durable_remix_lineage(
        project=project,
        db=db_session,
    )
    assert has_lineage is True


@pytest.mark.asyncio
async def test_build_project_context_block_uses_confirmed_bible_and_confirmed_plan(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Continuation Desk",
        description="remix continuation project",
    )
    db_session.add(project)
    await db_session.flush()

    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        generation_status="confirmed",
        source_task_id="task-1",
        source_chapter_count=18,
        character_cards=[{"name": "Inspector Lin", "goal": "Recover the ledger"}],
        timeline=[{"event": "Warehouse fire", "impact": "Ledger disappeared"}],
        hard_constraints=[{"rule": "Do not flip protagonist alignment abruptly"}],
        story_arcs=[{"name": "Ledger Arc", "status": "open"}],
        foreshadows=[{"hook": "Old rival returns", "status": "open"}],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        summary="Resolve old ledger thread before expanding cast scope.",
        beats=[{"beat": "Reconnect the dropped ledger line"}],
        priority_hooks=[{"hook": "Old rival returns in public"}],
        guardrails=[{"rule": "No sudden new power systems"}],
    )
    db_session.add_all([bible, plan])
    await db_session.commit()
    await db_session.refresh(project)

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )
    assert "Continuation Desk" in block
    assert "Inspector Lin" in block
    assert "Warehouse fire" in block
    assert "Do not flip protagonist alignment abruptly" in block
    assert "Reconnect the dropped ledger line" in block


@pytest.mark.asyncio
async def test_build_project_context_block_resolves_fresh_pattern_pack(monkeypatch, create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    import app.services.book_remix_context_service as context_service_module

    resolve_calls = []

    async def fake_resolve_fresh_pattern_pack(*, repo_root, force=False, **kwargs):
        resolve_calls.append({"repo_root": repo_root, "force": force, **kwargs})
        return {
            "continuation_prompt_hints": ["fresh context continuation hint"],
            "style_signature_hints": ["fresh context style hint"],
        }

    monkeypatch.setattr(
        context_service_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve_fresh_pattern_pack,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Continuation Desk",
        description="remix continuation project",
    )
    db_session.add(project)
    await db_session.flush()

    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        generation_status="confirmed",
        source_task_id="task-1",
        source_chapter_count=18,
        character_cards=[{"name": "Inspector Lin", "goal": "Recover the ledger"}],
        timeline=[{"event": "Warehouse fire", "impact": "Ledger disappeared"}],
        hard_constraints=[{"rule": "Do not flip protagonist alignment abruptly"}],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        summary="Resolve old ledger thread before expanding cast scope.",
    )
    db_session.add_all([bible, plan])
    await db_session.commit()
    await db_session.refresh(project)

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )

    assert resolve_calls
    assert resolve_calls[0]["repo_root"] == context_service_module.PROJECT_ROOT
    assert resolve_calls[0]["force"] is False
    assert "fresh context continuation hint" in block
    assert "fresh context style hint" in block


@pytest.mark.asyncio
async def test_build_project_context_preview_loads_latest_pattern_pack(monkeypatch, create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    import app.services.book_remix_context_service as context_service_module

    monkeypatch.setattr(
        context_service_module.source_discovery_service,
        "load_latest_pattern_pack",
        lambda *, repo_root: {
            "continuation_prompt_hints": ["预览应展示最新来源模式续写提示。"],
            "style_signature_hints": ["预览应展示原书味道约束。"],
        },
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Continuation Desk",
        description="remix continuation project",
    )
    db_session.add(project)
    await db_session.flush()

    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        generation_status="confirmed",
        source_task_id="task-1",
        source_chapter_count=18,
        character_cards=[{"name": "Inspector Lin", "goal": "Recover the ledger"}],
        timeline=[{"event": "Warehouse fire", "impact": "Ledger disappeared"}],
        hard_constraints=[{"rule": "Do not flip protagonist alignment abruptly"}],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        summary="Resolve old ledger thread before expanding cast scope.",
    )
    db_session.add_all([bible, plan])
    await db_session.commit()
    await db_session.refresh(project)

    preview = await BookRemixContextService().build_project_context_preview(
        project=project,
        db=db_session,
    )

    assert preview["source_pattern_pack_loaded"] is True
    assert "预览应展示最新来源模式续写提示" in preview["context"]
    assert "预览应展示原书味道约束" in preview["context"]


@pytest.mark.asyncio
async def test_build_project_context_block_ignores_stale_confirmed_plan(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Continuation Desk",
        description="remix continuation project",
    )
    db_session.add(project)
    await db_session.flush()

    base_time = datetime.utcnow()
    bible_id = str(uuid.uuid4())
    bible = BookRemixBible(
        id=bible_id,
        project_id=project.id,
        generation_status="confirmed",
        source_task_id="task-1",
        source_chapter_count=18,
        hard_constraints=[{"rule": "Do not flip protagonist alignment abruptly"}],
        story_arcs=[{"name": "Ledger Arc", "status": "open"}],
        foreshadows=[{"hook": "Old rival returns", "status": "open"}],
        created_at=base_time + timedelta(minutes=1),
        updated_at=base_time + timedelta(minutes=1),
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        summary="Resolve old ledger thread before expanding cast scope.",
        beats=[{"beat": "Reconnect the dropped ledger line"}],
        priority_hooks=[{"hook": "Old rival returns in public"}],
        guardrails=[{"rule": "No sudden new power systems"}],
        created_at=base_time,
        updated_at=base_time,
    )
    db_session.add_all([bible, plan])
    await db_session.commit()
    await db_session.refresh(project)

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )
    assert block == ""


def test_build_remix_continuation_context_block_renders_recent_change_packages_before_done_state():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Recover the ledger"}],
            "timeline": [],
            "hard_constraints": [],
            "story_arcs": [],
            "foreshadows": [],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_id": "chapter-19",
                    "chapter_number": 19,
                    "chapter_title": "Ledger Returns",
                    "summary": "Inspector Lin recovered the ledger.",
                    "timeline_delta": [
                        {"event": "Inspector Lin recovered ledger"}
                    ],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "decisive"}
                    ],
                    "foreshadow_changes": [
                        {"hook": "Old rival returns", "status": "resolved"}
                    ],
                    "plan_progress": [
                        {"beat": "Recover ledger", "status": "done"}
                    ],
                    "changed_sections": ["timeline", "plan_beats", "chapter_change_packages"],
                },
            ],
        },
        plan={
            "summary": "Resolve old ledger thread before expanding cast scope.",
            "beats": [
                {"beat": "Recover ledger", "status": "done", "last_chapter_number": 19},
                {"beat": "Question archive witness", "status": "pending"},
            ],
            "priority_hooks": [],
            "guardrails": [],
        },
    )

    assert "Recent chapter change packages" in block
    assert "Chapter 19: Ledger Returns" in block
    assert "Inspector Lin recovered the ledger" in block
    assert "timeline: Inspector Lin recovered ledger" in block
    assert "character: Inspector Lin -> decisive" in block
    assert "hook: Old rival returns (status: resolved)" in block
    assert "plan: Recover ledger (status: done)" in block
    assert block.index("Recent chapter change packages") < block.index("Pending planned beats")



def test_build_remix_continuation_context_block_summarizes_whole_book_progress_from_change_packages():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Recover the ledger"}],
            "timeline": [],
            "hard_constraints": [],
            "story_arcs": [],
            "foreshadows": [],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 19,
                    "chapter_title": "Ledger Returns",
                    "summary": "Inspector Lin recovered the ledger.",
                    "timeline_delta": [{"event": "Inspector Lin recovered ledger"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "decisive"}
                    ],
                    "foreshadow_changes": [
                        {"hook": "Old rival returns", "status": "resolved"}
                    ],
                    "plan_progress": [{"beat": "Recover ledger", "status": "done"}],
                },
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 20,
                    "chapter_title": "Archive Witness",
                    "summary": "Inspector Lin questioned the archive witness.",
                    "timeline_delta": [{"event": "Archive witness revealed a sealed file"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "suspicious"},
                        {"character_name": "Archive Witness", "state_after": "afraid"},
                    ],
                    "foreshadow_changes": [
                        {"hook": "Sealed file points to city hall", "status": "open"}
                    ],
                    "plan_progress": [{"beat": "Question archive witness", "status": "done"}],
                },
            ],
        },
        plan={
            "summary": "Resolve old ledger thread before expanding cast scope.",
            "beats": [
                {"beat": "Recover ledger", "status": "done", "last_chapter_number": 19},
                {"beat": "Question archive witness", "status": "done", "last_chapter_number": 20},
                {"beat": "Follow city hall file", "status": "pending"},
            ],
            "priority_hooks": [],
            "guardrails": [],
        },
    )

    assert "Whole-book continuation progress" in block
    assert "Continuation chapters with context: 19-20 (2 packages)" in block
    assert "Timeline progression: Ch19 Inspector Lin recovered ledger -> Ch20 Archive witness revealed a sealed file" in block
    assert "Latest character states: Inspector Lin @ Ch20 -> suspicious; Archive Witness @ Ch20 -> afraid" in block
    assert "Resolved hooks: Old rival returns" in block
    assert "Open hooks: Sealed file points to city hall" in block
    assert "Completed plan beats: Recover ledger; Question archive witness" in block
    assert block.index("Whole-book continuation progress") < block.index("Recent chapter change packages")



def test_build_remix_continuation_context_block_deduplicates_legacy_generation_and_analysis_packages():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [],
            "timeline": [],
            "hard_constraints": [],
            "story_arcs": [],
            "foreshadows": [],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_generation",
                    "chapter_number": 19,
                    "chapter_title": "Ledger Returns",
                    "summary": "Generated placeholder summary that should be hidden.",
                    "timeline_delta": [{"event": "Generated placeholder timeline"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "generated placeholder"}
                    ],
                },
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 19,
                    "chapter_title": "Ledger Returns",
                    "summary": "Analyzed ledger resolution should win.",
                    "timeline_delta": [{"event": "Analyzed ledger resolution"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "analysis wins"}
                    ],
                    "plan_progress": [{"beat": "Recover ledger", "status": "done"}],
                },
            ],
        },
        plan={
            "summary": "Continue from the analyzed state.",
            "beats": [{"beat": "Recover ledger", "status": "done", "last_chapter_number": 19}],
            "priority_hooks": [],
            "guardrails": [],
        },
    )

    assert "Continuation chapters with context: 19 (1 packages)" in block
    assert block.count("Chapter 19: Ledger Returns") == 1
    assert "Analyzed ledger resolution should win." in block
    assert "analysis wins" in block
    assert "Generated placeholder" not in block


def test_build_remix_continuation_context_block_preserves_generation_guardrail_when_analysis_wins():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [],
            "timeline": [],
            "hard_constraints": [],
            "story_arcs": [],
            "foreshadows": [],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_generation",
                    "chapter_number": 20,
                    "chapter_title": "Archive Aftermath",
                    "summary": "Generated draft repeated the ledger recovery before guardrail rewrite.",
                    "timeline_delta": [{"event": "Generated draft repeated ledger recovery"}],
                    "guardrail_check": {
                        "applied": True,
                        "attempts": 1,
                        "initial_passed": False,
                        "final_passed": True,
                        "violations": [
                            {
                                "type": "canon_repetition",
                                "severity": "high",
                                "description": "repeated confirmed Canon",
                            }
                        ],
                    },
                },
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 20,
                    "chapter_title": "Archive Aftermath",
                    "summary": "Analyzed archive witness state should remain primary.",
                    "timeline_delta": [{"event": "Archive witness revealed city hall file"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "suspicious"}
                    ],
                },
            ],
        },
        plan={
            "summary": "Continue from the analyzed state.",
            "beats": [],
            "priority_hooks": [],
            "guardrails": [],
        },
    )

    assert "Analyzed archive witness state should remain primary." in block
    assert "Generated draft repeated the ledger recovery" not in block
    assert "Guardrail rewrite applied: True" in block
    assert "canon_repetition" in block
    assert "repeated confirmed Canon" in block


def test_build_remix_continuation_context_block_renders_emotional_arc_from_change_package():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [],
            "timeline": [],
            "hard_constraints": [],
            "story_arcs": [],
            "foreshadows": [],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 21,
                    "chapter_title": "Archive Pressure",
                    "summary": "Inspector Lin keeps pressure on the witness.",
                    "timeline_delta": [{"event": "Archive witness starts to crack"}],
                    "emotional_arc": {
                        "tone": "tense restraint",
                        "intensity": 0.82,
                        "curve": {"start": 0.4, "end": 0.8},
                    },
                }
            ],
        },
        plan={
            "summary": "Continue the interrogation pressure.",
            "beats": [],
            "priority_hooks": [],
            "guardrails": [],
        },
    )

    assert "emotion: tone: tense restraint" in block
    assert "intensity: 0.82" in block
    assert "curve" in block


def test_build_remix_continuation_context_block_renders_context_activation_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "world_rules": {"magic": "Only verified city records are supernatural."},
            "character_cards": [{"name": "Inspector Lin", "goal": "Recover the ledger"}],
            "organizations": [{"name": "Archive Office", "role": "controls sealed files"}],
            "style_signature": {"voice": "tense restraint"},
            "timeline": [
                {
                    "event": "Inspector Lin recovered ledger",
                    "chapter_number": 19,
                    "source": "chapter_analysis",
                },
            ],
            "foreshadows": [
                {"hook": "Archive witness hesitates", "status": "open", "chapter_number": 20}
            ],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 20,
                    "chapter_title": "Archive Witness",
                    "summary": "Inspector Lin questioned the archive witness.",
                },
            ],
        },
        plan={
            "summary": "Follow the sealed file lead next.",
            "beats": [{"beat": "Follow city hall file", "status": "pending"}],
            "priority_hooks": [{"hook": "Archive witness hesitates", "status": "pending"}],
            "guardrails": [{"rule": "No new power system"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "lorebook_context"},
                {"name": "context_reference"},
                {"name": "world_state_tracking"},
                {"name": "memory_snapshot_versioning"},
                {"name": "author_note_layer"},
            ],
            "continuation_prompt_hints": ["Keep confirmed continuation canon."],
        },
    )

    assert "Context activation audit" in block
    assert "world_rules: 1 rules" in block
    assert "character_cards: 1 cards" in block
    assert "recent_change_packages: 1 packages" in block
    assert "activated_lore_entries: activate by current chapter goal and keywords" in block
    assert "context_reference_set: record section/card/chapter and reason" in block
    assert "world_state_slices: update only changed entity, location, faction, or item state" in block
    assert "author_note_layer: next-chapter local style reminder; expires after this chapter" in block
    assert "Context budget notes" in block
    assert "Rollback guidance" in block
    assert "snapshot before risky rewrite" in block


def test_build_remix_continuation_context_block_renders_scene_graph_review_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Track the archive witness"}],
            "organizations": [{"name": "Archive Office", "role": "controls sealed files"}],
            "timeline": [
                {
                    "event": "Inspector Lin recovered ledger",
                    "chapter_number": 19,
                    "source": "chapter_analysis",
                },
            ],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 20,
                    "chapter_title": "Archive Witness",
                    "summary": "Inspector Lin questioned the archive witness.",
                    "timeline_delta": [{"event": "Archive witness revealed a sealed file"}],
                },
            ],
            "style_signature": {"voice": "tense restraint"},
        },
        plan={
            "summary": "Follow the sealed file lead next.",
            "beats": [{"beat": "Follow city hall file", "status": "pending"}],
            "priority_hooks": [{"hook": "Archive witness hesitates", "status": "pending"}],
            "guardrails": [{"rule": "No repeated ledger recovery"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "scene_level_generation"},
                {"name": "content_ref_externalization"},
                {"name": "review_queue_staging"},
                {"name": "style_guide_layering"},
                {"name": "entity_schema_custom_fields"},
                {"name": "graph_healing"},
                {"name": "contradiction_detection"},
                {"name": "graph_branching_atomicity"},
                {"name": "query_lint_contract"},
            ],
            "scene_level_generation_hints": ["Plan chapters as ordered scene units before drafting."],
            "review_queue_staging_hints": ["Stage AI-proposed bible, card, style, and chapter changes as pending changes before applying them to canon."],
        },
    )

    assert "Scene graph review audit" in block
    assert "scene_generation_units: plan scene goal, cast, location, pressure, reveal, and exit hook before drafting" in block
    assert "external_content_refs: store large scene plans, drafts, extraction payloads, and review reports as refs with integrity metadata" in block
    assert "pending_change_queue: stage AI-proposed canon/style/card/chapter changes before applying them" in block
    assert "style_layer_stack: base style guide -> scene override -> character voice notes" in block
    assert "entity_custom_fields: validate genre-specific fields before prompt injection or canon write-back" in block
    assert "graph_healing_review: surface duplicate entities, orphan lore, and stale edges as reviewable candidates" in block
    assert "contradiction_gate: block acceptance on timeline, relationship, location, trait, or hook conflicts" in block
    assert "branch_atomicity: publish multi-slice canon updates only after branch/snapshot validation passes" in block
    assert "query_lint_contract: lint generated mutations for target entity, relationship type, required fields, and delete/update separation" in block


def test_build_remix_continuation_context_block_renders_plotgrid_reveal_and_branch_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Track the archive witness"}],
            "timeline": [
                {
                    "event": "Inspector Lin recovered ledger",
                    "chapter_number": 19,
                    "source": "chapter_analysis",
                },
            ],
            "foreshadows": [
                {"hook": "Sealed file points to city hall", "status": "open", "chapter_number": 20}
            ],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 20,
                    "chapter_title": "Archive Witness",
                    "summary": "Inspector Lin questioned the archive witness.",
                    "timeline_delta": [{"event": "Archive witness revealed a sealed file"}],
                },
            ],
            "style_signature": {"voice": "tense restraint"},
        },
        plan={
            "summary": "Follow the sealed file lead next.",
            "beats": [{"beat": "Follow city hall file", "status": "pending"}],
            "priority_hooks": [{"hook": "Sealed file points to city hall", "status": "pending"}],
            "guardrails": [{"rule": "No premature final confrontation"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "premature_ending_guard"},
                {"name": "layered_memory_model"},
                {"name": "plot_dependency_graph"},
                {"name": "plotgrid_scene_matrix"},
                {"name": "plotline_thread_tracking"},
                {"name": "scene_status_dashboard"},
                {"name": "gradual_reveal_control"},
                {"name": "setup_payoff_tracking"},
                {"name": "scene_type_directing"},
                {"name": "alternate_timeline_branching"},
                {"name": "divergence_guidance"},
                {"name": "worldpkg_export"},
            ],
            "premature_ending_guard_hints": ["Detect false resolution before accepting a continuation chapter."],
            "plotgrid_scene_matrix_hints": ["Map scenes against plotlines, themes, status, POV, emotion, and locations."],
            "setup_payoff_tracking_hints": ["Track setup/payoff pairs before final acceptance."],
        },
    )

    assert "Plotgrid reveal branch audit" in block
    assert "premature_ending_guard: check whether the draft falsely resolves the main conflict" in block
    assert "memory_layer_order: story bible -> character state -> plot dependency graph" in block
    assert "plot_dependency_graph: every payoff should trace back to an active setup" in block
    assert "plotgrid_scene_matrix: map each scene against plotline, POV, location, emotion, status, and thread coverage" in block
    assert "plotline_thread_tracking: keep active, paused, paid-off, and abandoned threads visible before drafting" in block
    assert "scene_status_dashboard: mark scene cards by planned, drafted, reviewed, accepted, or blocked state" in block
    assert "gradual_reveal_budget: expose world facts through action and dialogue" in block
    assert "setup_payoff_ledger: record setup chapter, expected payoff window, payoff state, and dependency risk" in block
    assert "scene_type_directing: declare scene mode before drafting" in block
    assert "alternate_timeline_branch: branch what-if or same-world divergence state away from faithful continuation canon" in block
    assert "divergence_guidance: name the player/new-story choice that causes branch drift" in block
    assert "worldpkg_export_boundary: exported world packages are reusable context artifacts" in block


def test_build_remix_continuation_context_block_renders_acceptance_loop_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Track the archive witness"}],
            "timeline": [
                {
                    "event": "Inspector Lin recovered ledger",
                    "chapter_number": 19,
                    "source": "chapter_analysis",
                },
            ],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 20,
                    "chapter_title": "Archive Witness",
                    "summary": "Inspector Lin questioned the archive witness.",
                    "timeline_delta": [{"event": "Archive witness revealed a sealed file"}],
                },
            ],
            "style_signature": {"voice": "tense restraint"},
        },
        plan={
            "summary": "Follow the sealed file lead next.",
            "beats": [{"beat": "Follow city hall file", "status": "pending"}],
            "priority_hooks": [{"hook": "Sealed file points to city hall", "status": "pending"}],
            "guardrails": [{"rule": "No premature final confrontation"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "context_pack_preview"},
                {"name": "accepted_chapter_memory"},
                {"name": "critic_verifier_loop"},
                {"name": "collapse_prevention"},
                {"name": "trend_deconstruction_pipeline"},
                {"name": "anti_ai_tone_polish"},
                {"name": "preference_memory"},
                {"name": "interrupted_resume_flow"},
                {"name": "auto_validation_rewrite"},
                {"name": "top_down_story_planning"},
            ],
            "context_pack_preview_hints": ["Render a context-pack preview before drafting."],
            "accepted_chapter_memory_hints": ["Only accepted chapters extract memory."],
            "critic_verifier_loop_hints": ["Separate writer/reviser output from critic/verifier feedback."],
            "auto_validation_rewrite_hints": ["Validate each chapter before accepting it."],
        },
    )

    assert "Acceptance loop audit" in block
    assert "context_pack_preview: list included canon facts, retrieval reasons, token budget, and omitted-but-relevant context before drafting" in block
    assert "accepted_chapter_memory: drafts cannot update canon; only accepted chapters may extract memory" in block
    assert "critic_verifier_loop: keep writer/reviser output separate from critic/verifier findings" in block
    assert "collapse_prevention: block write-back on invalid output, causality break, state contradiction" in block
    assert "trend_deconstruction_pipeline: use deconstructed trope modules as transformed craft pressure" in block
    assert "anti_ai_tone_polish: remove explanation-heavy AI tone after continuity passes" in block
    assert "preference_memory_boundary: apply user preference to style defaults only" in block
    assert "interrupted_resume_flow: resume from current phase, chapter, scene, last accepted artifact" in block
    assert "auto_validation_rewrite: validate word count, coherence, hook, style, and state write-back before bounded retry" in block
    assert "top_down_story_planning: preserve hierarchy from book spec to act, chapter, scene" in block


def test_build_remix_continuation_context_block_renders_manuscript_structure_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Track the archive witness"}],
            "timeline": [
                {
                    "event": "Inspector Lin recovered ledger",
                    "chapter_number": 19,
                    "source": "chapter_analysis",
                },
            ],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 20,
                    "chapter_title": "Archive Witness",
                    "summary": "Inspector Lin questioned the archive witness.",
                    "timeline_delta": [{"event": "Archive witness revealed a sealed file"}],
                },
            ],
            "style_signature": {"voice": "tense restraint"},
        },
        plan={
            "summary": "Follow the sealed file lead next.",
            "beats": [{"beat": "Follow city hall file", "status": "pending"}],
            "priority_hooks": [{"hook": "Sealed file points to city hall", "status": "pending"}],
            "guardrails": [{"rule": "No premature final confrontation"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "plain_text_project_storage"},
                {"name": "synopsis_cross_reference"},
                {"name": "snowflake_premise_expansion"},
                {"name": "outliner_index_cards"},
                {"name": "narrative_strand_mapping"},
                {"name": "character_depth_interview"},
                {"name": "mindmap_visual_planning"},
                {"name": "manuscript_export_formats"},
            ],
            "plain_text_project_storage_hints": ["Keep chapters and notes as stable text units."],
            "snowflake_premise_expansion_hints": ["Grow premise from sentence to summary."],
            "narrative_strand_mapping_hints": ["Track narrative strands separately."],
        },
    )

    assert "Manuscript structure audit" in block
    assert "plain_text_project_storage: keep chapters, notes, summaries, and analysis as stable human-readable units" in block
    assert "synopsis_cross_reference: link synopsis, comments, notes, and chapter refs before drafting" in block
    assert "snowflake_premise_expansion: preserve the premise chain from sentence to paragraph to full summary" in block
    assert "outliner_index_cards: keep chapter and scene cards reorderable without losing state evidence" in block
    assert "narrative_strand_mapping: map premise, fabula, narrative strands, and setting context before accepting arc changes" in block
    assert "character_depth_interview: verify desire, fear, contradiction, social mask, and pressure before major character turns" in block
    assert "mindmap_visual_planning: keep visual idea nodes separate from canon until accepted into outline or bible" in block
    assert "manuscript_export_formats: treat PDF/DOCX/TXT/EPUB exports as derived artifacts, not canon sources" in block


def test_build_remix_continuation_context_block_renders_inspectable_rewrite_audit():
    block = build_remix_continuation_context_block(
        project_title="Rewrite Desk",
        bible={
            "character_cards": [{"name": "Ari", "goal": "Protect the archive"}],
            "timeline": [{"event": "Ari entered the archive", "chapter_number": 7}],
        },
        plan={
            "summary": "Patch the archive chapter without drifting the whole book.",
            "beats": [{"beat": "Rewrite archive discovery", "status": "pending"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "human_synopsis_gate"},
                {"name": "retrieval_guided_span_rewrite"},
                {"name": "runtime_artifact_trace"},
                {"name": "schema_validated_state_delta"},
                {"name": "recursive_adaptive_planning"},
                {"name": "workflow_manuscript_compilation"},
                {"name": "writing_session_goal_tracking"},
                {"name": "inspectable_run_workspace"},
            ],
            "human_synopsis_gate_hints": ["Review synopsis before prose."],
            "retrieval_guided_span_rewrite_hints": ["Rewrite only named spans."],
            "runtime_artifact_trace_hints": ["Persist trace artifacts."],
        },
    )

    assert "Inspectable rewrite audit" in block
    assert "human_synopsis_gate: accept, edit, or regenerate synopsis and chapter summaries before prose expansion" in block
    assert "retrieval_guided_span_rewrite: retrieve related body spans and outline nodes; rewrite only named spans" in block
    assert "runtime_artifact_trace: persist intent, selected context, rule stack, and trace for each chapter run" in block
    assert "schema_validated_state_delta: validate structured state deltas before canon mutation" in block
    assert "recursive_adaptive_planning: split work into retrieval, reasoning, planning, composition, and review subtasks" in block
    assert "workflow_manuscript_compilation: compile only accepted ordered scenes into manuscript outputs" in block
    assert "writing_session_goal_tracking: track target and accepted word counts without letting quota override continuity gates" in block
    assert "inspectable_run_workspace: expose session, storyboard, manuscript surface, current phase, pending review, and memory refs" in block


def test_build_remix_continuation_progress_summary_deduplicates_legacy_generation_and_analysis_packages():
    summary = build_remix_continuation_progress_summary(
        packages=[
            {
                "source": "chapter_generation",
                "chapter_number": 19,
                "summary": "Generated placeholder summary that should be hidden.",
                "timeline_delta": [{"event": "Generated placeholder timeline"}],
                "character_state_changes": [
                    {"character_name": "Inspector Lin", "state_after": "generated placeholder"}
                ],
            },
            {
                "source": "chapter_analysis",
                "chapter_number": 19,
                "summary": "Analyzed ledger resolution should win.",
                "timeline_delta": [{"event": "Analyzed ledger resolution"}],
                "character_state_changes": [
                    {"character_name": "Inspector Lin", "state_after": "analysis wins"}
                ],
                "plan_progress": [{"beat": "Recover ledger", "status": "done"}],
            },
        ],
        plan={"beats": [{"beat": "Recover ledger", "status": "done", "last_chapter_number": 19}]},
    )

    assert summary["package_count"] == 1
    assert summary["chapter_range"] == {"start": 19, "end": 19}
    assert summary["timeline_progression"] == [
        {"chapter_number": 19, "event": "Analyzed ledger resolution"}
    ]
    assert summary["latest_character_states"] == [
        {"character_name": "Inspector Lin", "chapter_number": 19, "state_after": "analysis wins"}
    ]



def test_build_remix_continuation_progress_summary_returns_structured_payload():
    summary = build_remix_continuation_progress_summary(
        packages=[
            {
                "type": "chapter_change_package",
                "source": "chapter_analysis",
                "chapter_number": 19,
                "chapter_title": "Ledger Returns",
                "summary": "Inspector Lin recovered the ledger.",
                "timeline_delta": [{"event": "Inspector Lin recovered ledger"}],
                "character_state_changes": [
                    {"character_name": "Inspector Lin", "state_after": "decisive"}
                ],
                "foreshadow_changes": [
                    {"hook": "Old rival returns", "status": "resolved"}
                ],
                "plan_progress": [{"beat": "Recover ledger", "status": "done"}],
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
                "foreshadow_changes": [
                    {"hook": "Sealed file points to city hall", "status": "open"}
                ],
                "plan_progress": [{"beat": "Question archive witness", "status": "done"}],
            },
        ],
        plan={
            "beats": [
                {"beat": "Recover ledger", "status": "done", "last_chapter_number": 19},
                {"beat": "Follow city hall file", "status": "pending"},
            ]
        },
    )

    assert summary == {
        "package_count": 2,
        "chapter_range": {"start": 19, "end": 20},
        "timeline_progression": [
            {"chapter_number": 19, "event": "Inspector Lin recovered ledger"},
            {"chapter_number": 20, "event": "Archive witness revealed a sealed file"},
        ],
        "latest_character_states": [
            {"character_name": "Inspector Lin", "chapter_number": 20, "state_after": "suspicious"}
        ],
        "emotional_progression": [],
        "resolved_hooks": ["Old rival returns"],
        "open_hooks": ["Sealed file points to city hall"],
        "completed_plan_beats": ["Recover ledger", "Question archive witness"],
        "pending_plan_beats": ["Follow city hall file"],
    }


def test_build_remix_continuation_progress_summary_renders_emotional_progression():
    summary = build_remix_continuation_progress_summary(
        packages=[
            {
                "type": "chapter_change_package",
                "source": "chapter_analysis",
                "chapter_number": 19,
                "chapter_title": "Ledger Returns",
                "summary": "Inspector Lin recovered the ledger.",
                "timeline_delta": [{"event": "Inspector Lin recovered ledger"}],
                "emotional_arc": {
                    "tone": "tense restraint",
                    "intensity": 0.82,
                    "curve": {"start": 0.4, "end": 0.8},
                },
            },
        ],
        plan=None,
    )

    assert summary["emotional_progression"] == [
        {
            "chapter_number": 19,
            "tone": "tense restraint",
            "intensity": 0.82,
            "curve": {"start": 0.4, "end": 0.8},
        }
    ]



def test_build_remix_continuation_context_block_renders_production_review_audit():
    block = build_remix_continuation_context_block(
        project_title="Production Review Novel",
        bible={"world_rules": {"rule": "keep accepted canon"}},
        plan={"summary": "Continue from accepted bridge."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "craft_role_pipeline"},
                {"name": "frontmatter_story_schema"},
                {"name": "continuity_bridge_window"},
                {"name": "episode_range_rewrite_scope"},
                {"name": "voice_table_polish_axis"},
                {"name": "boring_opening_quality_gates"},
                {"name": "beat_strand_framework"},
                {"name": "anti_hallucination_plan_check"},
                {"name": "backup_restore_checkpoint"},
                {"name": "multi_level_review_trend"},
                {"name": "editor_notes_feedback_loop"},
                {"name": "genre_parameterized_worldbuilding"},
                {"name": "prose_preflight_voice_calibration"},
            ],
            "continuity_bridge_window_hints": ["Build a compact continuity bridge."],
            "voice_table_polish_axis_hints": ["Check dialogue against voice table."],
        },
    )

    assert "Production review audit:" in block
    assert "craft_role_pipeline: keep architecture, character, prose, continuity, review, edit, and export outputs separate" in block
    assert "frontmatter_story_schema: store scene state, continuity questions, promises/payoffs, and chapter draft metadata as stable fields" in block
    assert "continuity_bridge_window: feed the next chapter from recent accepted chapters" in block
    assert "episode_range_rewrite_scope: calculate impacted chapters" in block
    assert "voice_table_polish_axis: check dialogue against per-character" in block
    assert "boring_opening_quality_gates: reject exposition-only openings" in block
    assert "beat_strand_framework: track external plot, internal change, and relationship strands" in block
    assert "anti_hallucination_plan_check: verify new facts against bible" in block
    assert "backup_restore_checkpoint: create restore points" in block
    assert "multi_level_review_trend: review scene, chapter, batch" in block
    assert "editor_notes_feedback_loop: carry open editor notes forward" in block
    assert "genre_parameterized_worldbuilding: parameterize factions" in block
    assert "prose_preflight_voice_calibration: use voice samples" in block


def test_build_remix_continuation_context_block_renders_consistency_style_audit():
    block = build_remix_continuation_context_block(
        project_title="Consistency Sourcebook Novel",
        bible={"world_rules": {"rule": "keep accepted canon"}},
        plan={"summary": "Continue from accepted sourcebook state."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "sourcebook_author_workbench"},
                {"name": "semantic_long_context_search"},
                {"name": "contradiction_taxonomy_checker"},
                {"name": "parallel_agent_chapter_pipeline"},
                {"name": "cross_chapter_redundancy_audit"},
                {"name": "humanization_stylometry_levers"},
                {"name": "author_control_boundary"},
            ],
        },
    )

    assert "Consistency and style audit:" in block
    assert "sourcebook_author_workbench: sourcebook entries are author-owned canon candidates" in block
    assert "semantic_long_context_search: cite query, matched artifact" in block
    assert "contradiction_taxonomy_checker: check characterization, factual detail" in block
    assert "parallel_agent_chapter_pipeline: isolate chapter jobs" in block
    assert "cross_chapter_redundancy_audit: count repeated scene shapes" in block
    assert "humanization_stylometry_levers: apply burstiness, specificity" in block
    assert "author_control_boundary: keep AI proposals, accepted canon" in block


def test_build_remix_continuation_context_block_renders_research_multimodal_experiment_audit():
    block = build_remix_continuation_context_block(
        project_title="Research Multimodal Novel",
        bible={"world_rules": {"rule": "keep accepted canon"}},
        plan={"summary": "Continue from taxonomy and synopsis-spine state."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "research_taxonomy_story_map"},
                {"name": "novel_to_multimodal_pipeline"},
                {"name": "entity_to_visual_asset_pipeline"},
                {"name": "agentic_book_planner_pipeline"},
                {"name": "rag_synopsis_spine"},
                {"name": "anti_repetition_prompt_rules"},
                {"name": "prompt_recipe_experiment_grid"},
                {"name": "append_only_generation_review_log"},
                {"name": "narrative_arc_template_control"},
                {"name": "nrd_task_tree_pipeline"},
                {"name": "sampling_parameter_quality_sweep"},
                {"name": "story_structure_rag_planning"},
            ],
        },
    )

    assert "Research, multimodal, and experiment audit:" in block
    assert "research_taxonomy_story_map: use method categories as coverage checks" in block
    assert "novel_to_multimodal_pipeline: treat scripts, storyboards, and videos as derived artifacts" in block
    assert "entity_to_visual_asset_pipeline: tie visual assets to entity/card versions" in block
    assert "agentic_book_planner_pipeline: separate Story Bible, Characters, Plot Threads" in block
    assert "rag_synopsis_spine: retrieve from the full synopsis spine" in block
    assert "anti_repetition_prompt_rules: reject repeated phrases" in block
    assert "prompt_recipe_experiment_grid: compare prompt recipes" in block
    assert "append_only_generation_review_log: append experiment evidence" in block
    assert "narrative_arc_template_control: declare genre, story style" in block
    assert "nrd_task_tree_pipeline: track arcs -> chapters -> scenes" in block
    assert "sampling_parameter_quality_sweep: promote parameter defaults" in block
    assert "story_structure_rag_planning: map Hero's Journey/Freytag" in block



def test_build_remix_continuation_context_block_renders_serialized_continuity_audit():
    block = build_remix_continuation_context_block(
        project_title="Serialized Desk",
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Track the archive witness"}],
            "timeline": [{"event": "Inspector Lin recovered ledger", "chapter_number": 19}],
            "chapter_change_packages": [
                {
                    "type": "chapter_change_package",
                    "source": "chapter_analysis",
                    "chapter_number": 20,
                    "summary": "Inspector Lin questioned the archive witness.",
                }
            ],
        },
        plan={"summary": "Follow the sealed file lead next."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "story_contract_commit_chain"},
                {"name": "fact_snapshot_delta_gate"},
                {"name": "projection_sync_observability"},
                {"name": "foreshadowing_debt_budget"},
                {"name": "reader_retention_review_gate"},
                {"name": "draft_stage_revision_ladder"},
                {"name": "rolling_summary_context_trim"},
            ],
            "story_contract_commit_chain_hints": ["Treat contracts as canonical commit chain."],
            "fact_snapshot_delta_gate_hints": ["Validate deltas before write-back."],
            "rolling_summary_context_trim_hints": ["Track dropped context."],
        },
    )

    assert "Serialized continuity audit" in block
    assert "story_contract_commit_chain: contracts are canon" in block
    assert "fact_snapshot_delta_gate: validate fact snapshots" in block
    assert "projection_sync_observability: state/index/summary/memory/vector/dashboard views" in block
    assert "foreshadowing_debt_budget: reserve context for high-debt hooks" in block
    assert "reader_retention_review_gate: review consistency, OOC, rhythm" in block
    assert "draft_stage_revision_ladder: blueprint -> key info -> task card -> Draft A/B/C" in block
    assert "rolling_summary_context_trim: selected rolling summary" in block


def test_build_remix_continuation_context_block_renders_story_quality_eval_audit():
    block = build_remix_continuation_context_block(
        project_title="Quality Bench Desk",
        bible={
            "character_cards": [{"name": "Mira", "goal": "Choose between truth and safety"}],
            "timeline": [{"event": "Mira found the sealed map", "chapter_number": 8}],
        },
        plan={"summary": "Draft two possible next chapters and choose the stronger one."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "pairwise_story_comparison_ranking"},
                {"name": "multidimensional_quality_rubric"},
                {"name": "story_theory_beat_evaluation"},
                {"name": "constraint_specificity_creativity_benchmark"},
                {"name": "style_axis_diversity_fingerprint"},
                {"name": "event_outline_history_compression"},
                {"name": "agentic_story_world_simulation"},
            ],
            "pairwise_story_comparison_ranking_hints": ["Compare matched variants before accepting."],
            "multidimensional_quality_rubric_hints": ["Use q1-q15-style quality metrics."],
            "style_axis_diversity_fingerprint_hints": ["Track voice and rhythm axes."],
        },
    )

    assert "Story quality evaluation audit" in block
    assert "pairwise_story_comparison_ranking: compare matched chapter variants" in block
    assert "multidimensional_quality_rubric: score grammar, clarity, causality" in block
    assert "story_theory_beat_evaluation: test beat execution" in block
    assert "constraint_specificity_creativity_benchmark: track required constraints" in block
    assert "style_axis_diversity_fingerprint: inspect voice, rhythm, POV" in block
    assert "event_outline_history_compression: align compressed history" in block
    assert "agentic_story_world_simulation: keep simulated character choices" in block

def test_build_remix_continuation_context_block_renders_reader_market_feedback_audit():
    block = build_remix_continuation_context_block(
        project_title="Reader Market Desk",
        bible={
            "character_cards": [{"name": "Mira", "goal": "keep the city from panic"}],
            "timeline": [{"event": "Mira exposed the false prophet", "chapter_number": 12}],
        },
        plan={"summary": "Increase turn-page pressure without breaking canon."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "reader_rating_signal_model"},
                {"name": "review_spoiler_sentiment_corpus"},
                {"name": "beta_reader_archetype_panel"},
                {"name": "comp_title_market_positioning"},
                {"name": "local_reader_experience_editor"},
            ]
        },
    )

    assert "Reader market feedback audit" in block
    assert "reader_rating_signal_model: use ratings, shelves, tags" in block
    assert "review_spoiler_sentiment_corpus: cluster praise, complaints" in block
    assert "beta_reader_archetype_panel: collect genre-fan" in block
    assert "comp_title_market_positioning: calibrate promise" in block
    assert "local_reader_experience_editor: audit micro-tension" in block


def test_build_remix_inspired_context_block_renders_reader_market_feedback_audit():
    block = build_remix_inspired_context_block(
        project_title="Inspired Reader Fit",
        style_content=(
            "\u4f60\u6b63\u5728\u57fa\u4e8e\u300a\u6e90\u4e66\u300b\u505a\u540c\u7c7b\u578b\u521b\u4f5c\uff0c\u800c\u4e0d\u662f\u5fe0\u5b9e\u7eed\u5199\u3002\n"
            "\u3010\u540c\u7c7b\u578b\u521b\u4f5c\u603b\u539f\u5219\u3011\n"
            "- \u53ea\u5b66\u4e60\u8bfb\u8005\u671f\u5f85\u3001\u8282\u594f\u548c\u60c5\u7eea\u6ee1\u8db3\uff0c\u4e0d\u590d\u5236\u6e90\u4e66\u4e8b\u5b9e\u3002\n"
            "\u3010\u6e90\u4e66\u8bed\u6c14\u6837\u672c\u3011\n"
            "[\u6837\u672c1] The door stayed open. Nobody called it mercy.\n"
            "\u3010\u6e90\u4e66\u663e\u6027\u5143\u7d20\u7981\u7528\u6e05\u5355\u3011\n"
            "- \u6e90\u4e66\u4e3b\u89d2\u3001\u7ec4\u7ec7\u3001\u5730\u70b9\u548c\u4e8b\u4ef6\u987a\u5e8f\u90fd\u4e0d\u5f97\u6cbf\u7528\u3002\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "reader_rating_signal_model"},
                {"name": "review_spoiler_sentiment_corpus"},
                {"name": "beta_reader_archetype_panel"},
                {"name": "comp_title_market_positioning"},
                {"name": "local_reader_experience_editor"},
            ],
            "inspired_mapping_targets": ["reader_signal_remap", "comp_title_positioning_remap"],
            "inspired_prompt_hints": ["Reader signals calibrate market feel only."],
            "inspired_transformation_hints": ["Convert comp similarities into transformed differences."],
            "inspired_copy_risk_hints": ["Reject copied review wording and comp hook sequence."],
        },
    )

    assert "Reader market feedback audit" in block
    assert "reader_rating_signal_model" in block
    assert "beta_reader_archetype_panel" in block
    assert "comp_title_market_positioning" in block
    assert "Inspired transformation audit" in block
    assert "reader_signal_remap, comp_title_positioning_remap" in block


def test_build_remix_continuation_context_block_renders_delivery_packaging_audit():
    block = build_remix_continuation_context_block(
        project_title="Delivery Desk",
        bible={
            "character_cards": [{"name": "Mira", "goal": "finish the serialized archive"}],
            "timeline": [{"event": "Mira accepted the final manuscript pass", "chapter_number": 88}],
        },
        plan={"summary": "Prepare final continuous TXT and exportable manuscript package."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "delivery_manuscript_assembly"},
                {"name": "export_format_fidelity_audit"},
                {"name": "preview_toc_packaging"},
                {"name": "cover_kdp_metadata_boundary"},
            ],
            "delivery_manuscript_assembly_hints": ["Assemble only accepted chapters into the final manuscript."],
            "export_format_fidelity_audit_hints": ["Verify each export preserves chapter order."],
        },
    )

    assert "Delivery packaging audit" in block
    assert "delivery_manuscript_assembly: assemble only accepted chapters" in block
    assert "export_format_fidelity_audit: verify chapter order, headings" in block
    assert "preview_toc_packaging: generate preview and table-of-contents" in block
    assert "cover_kdp_metadata_boundary: keep cover and KDP metadata" in block


def test_build_remix_continuation_context_block_renders_interactive_narrative_audit():
    block = build_remix_continuation_context_block(
        project_title="Branch Desk",
        bible={
            "character_cards": [{"name": "Rin", "goal": "choose without breaking canon"}],
            "timeline": [{"event": "Rin accepted a branch consequence", "chapter_number": 34}],
        },
        plan={"summary": "Continue the faithful canon while tracking optional choice branches."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "branching_choice_graph"},
                {"name": "node_dialogue_state_machine"},
                {"name": "passage_link_navigation_map"},
                {"name": "choice_stats_consequence_gate"},
            ],
            "branching_choice_graph_hints": ["Track choices as branch edges, not hidden canon changes."],
            "node_dialogue_state_machine_hints": ["Dialogue nodes must declare entry state and exit deltas."],
        },
    )

    assert "Interactive narrative audit" in block
    assert "branching_choice_graph: model choices as branch edges" in block
    assert "node_dialogue_state_machine: dialogue nodes declare entry conditions" in block
    assert "passage_link_navigation_map: passage links need reachable path" in block
    assert "choice_stats_consequence_gate: every choice-stat mutation needs visible consequence" in block


def test_build_remix_inspired_context_block_renders_interactive_narrative_audit():
    block = build_remix_inspired_context_block(
        project_title="Inspired Branch Desk",
        style_content=(
            "【同类型创作总原则】\n"
            "- 保留互动分支的选择压力。\n"
            "【源书语气样本】\n"
            "- 冷静、留白、短句。\n"
            "【源书显性元素禁用清单】\n"
            "- 禁止复用源书角色名。"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "branching_choice_graph"},
                {"name": "node_dialogue_state_machine"},
                {"name": "choice_stats_consequence_gate"},
            ],
            "inspired_mapping_targets": ["choice_branch_remap", "dialogue_node_remap"],
            "inspired_copy_risk_hints": ["Reject copied choice text and branch order."],
        },
    )

    assert "Interactive narrative audit" in block
    assert "branching_choice_graph" in block
    assert "Inspired transformation audit" in block
    assert "choice_branch_remap, dialogue_node_remap" in block
