from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import select

from app.models.batch_generation_task import BatchGenerationTask
from app.models.chapter import Chapter
from app.models.outline import Outline
from app.models.project import Project
from app.services.bandao_batch_queue_plan import (
    BANDAO_EXPECTED_SOURCE_SHA256,
    build_bandao_chapter_expansion_plan,
    create_bandao_continuation_queue_plan,
)


@pytest.mark.asyncio
async def test_create_bandao_continuation_queue_plan_creates_missing_draft_chapters_and_task(
    create_schema,
    db_session,
):
    await create_schema(Project.__table__, Outline.__table__, Chapter.__table__, BatchGenerationTask.__table__)
    project = Project(
        id="bandao-project",
        user_id="tester",
        title="混在半岛的日子",
        description="拆书续写测试项目",
        chapter_count=200,
        current_words=0,
    )
    db_session.add(project)
    await db_session.commit()

    for chapter_number in range(1, 201):
        db_session.add(
            Chapter(
                project_id=project.id,
                chapter_number=chapter_number,
                title=f"第 {chapter_number} 章 原书章节",
                content="原书内容",
                word_count=4,
                status="published",
            )
        )
    await db_session.commit()

    result = await create_bandao_continuation_queue_plan(
        db_session=db_session,
        project_id=project.id,
        user_id="tester",
        artifact_dir=Path("tmp/book-remix-test-ban-dao-20260530"),
        dry_run=False,
    )

    assert result["source_sha256"] == BANDAO_EXPECTED_SOURCE_SHA256
    assert result["source_chapters"] == 200
    assert result["target_total_chapters"] == 1000
    assert result["continuation_chapters_needed"] == 800
    assert result["created_missing_chapters"] == 800
    assert result["existing_continuation_chapters"] == 0
    assert result["created_continuation_outlines"] == 10
    assert result["reused_continuation_outlines"] == 0
    assert result["batch_task_id"]

    chapters = (
        await db_session.execute(
            select(Chapter).where(Chapter.project_id == project.id).order_by(Chapter.chapter_number)
        )
    ).scalars().all()
    assert len(chapters) == 1000
    assert chapters[200].chapter_number == 201
    assert chapters[200].title == "第201章 沉默的清晨"
    assert chapters[-1].chapter_number == 1000
    assert chapters[-1].status == "draft"
    assert chapters[-1].content is None

    task = (
        await db_session.execute(select(BatchGenerationTask).where(BatchGenerationTask.id == result["batch_task_id"]))
    ).scalar_one()
    assert task.status == "pending"
    assert task.start_chapter_number == 201
    assert task.chapter_count == 800
    assert task.total_chapters == 800
    assert task.target_word_count == 10000
    assert len(task.chapter_ids) == 800
    assert task.chapter_ids[0] == chapters[200].id
    assert task.chapter_ids[-1] == chapters[-1].id

    chapter_201_plan = json.loads(chapters[200].expansion_plan)
    chapter_231_plan = json.loads(chapters[230].expansion_plan)
    chapter_1000_plan = json.loads(chapters[-1].expansion_plan)
    assert chapter_201_plan["target_word_count"] == 10000
    assert chapter_201_plan["plot_summary"].startswith("承接第200章")
    assert "沉默的清晨" in chapter_201_plan["plot_summary"]
    assert "张元英" in chapter_201_plan["character_focus"]
    assert "崔叡娜" in chapter_201_plan["character_focus"]
    assert "不公开恋情" in chapter_201_plan["guardrails"]
    assert "HEART*IZ" in chapter_231_plan["plot_summary"]
    assert "2021-04-29" in chapter_1000_plan["reality_timeline_constraints"]
    assert "不加入 IVE 或 LE SSERAFIM 固定阵容" in chapter_1000_plan["guardrails"]

    outlines = (
        await db_session.execute(
            select(Outline).where(Outline.project_id == project.id).order_by(Outline.order_index)
        )
    ).scalars().all()
    assert len(outlines) == 10
    assert outlines[0].order_index == 201
    assert outlines[0].title == "第201-230章 楼梯间余波与日常修罗场"
    assert json.loads(outlines[-1].structure)["range"] == "941-1000"


@pytest.mark.asyncio
async def test_create_bandao_continuation_queue_plan_dry_run_does_not_write(
    create_schema,
    db_session,
):
    await create_schema(Project.__table__, Outline.__table__, Chapter.__table__, BatchGenerationTask.__table__)
    project = Project(
        id="bandao-dry-run-project",
        user_id="tester",
        title="混在半岛的日子",
        description="拆书续写测试项目",
        chapter_count=200,
    )
    db_session.add(project)
    await db_session.commit()

    for chapter_number in range(1, 201):
        db_session.add(
            Chapter(
                project_id=project.id,
                chapter_number=chapter_number,
                title=f"第 {chapter_number} 章 原书章节",
                content="原书内容",
                word_count=4,
                status="published",
            )
        )
    await db_session.commit()

    result = await create_bandao_continuation_queue_plan(
        db_session=db_session,
        project_id=project.id,
        user_id="tester",
        artifact_dir=Path("tmp/book-remix-test-ban-dao-20260530"),
        dry_run=True,
    )

    assert result["dry_run"] is True
    assert result["created_missing_chapters"] == 800
    assert result["created_continuation_outlines"] == 0
    assert result["reused_continuation_outlines"] == 0
    assert result["batch_task_id"] is None

    chapter_count = len((await db_session.execute(select(Chapter).where(Chapter.project_id == project.id))).scalars().all())
    task_count = len((await db_session.execute(select(BatchGenerationTask))).scalars().all())
    assert chapter_count == 200
    assert task_count == 0


@pytest.mark.asyncio
async def test_create_bandao_continuation_queue_plan_reuses_existing_pending_task_on_rerun(
    create_schema,
    db_session,
):
    await create_schema(Project.__table__, Outline.__table__, Chapter.__table__, BatchGenerationTask.__table__)
    project = Project(
        id="bandao-idempotent-project",
        user_id="tester",
        title="混在半岛的日子",
        description="拆书续写测试项目",
        chapter_count=200,
    )
    db_session.add(project)
    await db_session.commit()

    for chapter_number in range(1, 201):
        db_session.add(
            Chapter(
                project_id=project.id,
                chapter_number=chapter_number,
                title=f"第 {chapter_number} 章 原书章节",
                content="原书内容",
                word_count=4,
                status="published",
            )
        )
    await db_session.commit()

    first = await create_bandao_continuation_queue_plan(
        db_session=db_session,
        project_id=project.id,
        user_id="tester",
        artifact_dir=Path("tmp/book-remix-test-ban-dao-20260530"),
        dry_run=False,
    )
    second = await create_bandao_continuation_queue_plan(
        db_session=db_session,
        project_id=project.id,
        user_id="tester",
        artifact_dir=Path("tmp/book-remix-test-ban-dao-20260530"),
        dry_run=False,
    )

    assert second["batch_task_id"] == first["batch_task_id"]
    assert second["reused_batch_task"] is True
    assert second["created_missing_chapters"] == 0
    assert second["existing_continuation_chapters"] == 800
    assert second["created_continuation_outlines"] == 0
    assert second["reused_continuation_outlines"] == 10

    tasks = (await db_session.execute(select(BatchGenerationTask))).scalars().all()
    chapters = (await db_session.execute(select(Chapter).where(Chapter.project_id == project.id))).scalars().all()
    outlines = (await db_session.execute(select(Outline).where(Outline.project_id == project.id))).scalars().all()
    assert len(tasks) == 1
    assert len(chapters) == 1000
    assert len(outlines) == 10


@pytest.mark.asyncio
async def test_create_bandao_continuation_queue_plan_backfills_existing_draft_expansion_plans(
    create_schema,
    db_session,
):
    await create_schema(Project.__table__, Outline.__table__, Chapter.__table__, BatchGenerationTask.__table__)
    project = Project(
        id="bandao-backfill-project",
        user_id="tester",
        title="混在半岛的日子",
        description="拆书续写测试项目",
        chapter_count=1000,
    )
    db_session.add(project)
    await db_session.commit()

    for chapter_number in range(1, 201):
        db_session.add(
            Chapter(
                project_id=project.id,
                chapter_number=chapter_number,
                title=f"第 {chapter_number} 章 原书章节",
                content="原书内容",
                word_count=4,
                status="published",
            )
        )
    await db_session.commit()

    draft_chapter_ids = []
    for chapter_number in range(201, 1001):
        chapter = Chapter(
            project_id=project.id,
            chapter_number=chapter_number,
            title=f"第{chapter_number}章 旧占位",
            content=None,
            expansion_plan=None,
            word_count=0,
            status="draft",
        )
        db_session.add(chapter)
        await db_session.flush()
        draft_chapter_ids.append(chapter.id)

    old_task = BatchGenerationTask(
        project_id=project.id,
        user_id="tester",
        start_chapter_number=201,
        chapter_count=800,
        chapter_ids=draft_chapter_ids,
        target_word_count=10000,
        status="pending",
        total_chapters=800,
        completed_chapters=0,
        failed_chapters=[],
        current_stage="queued",
        current_stage_progress=0,
        current_retry_count=0,
    )
    db_session.add(old_task)
    await db_session.commit()

    result = await create_bandao_continuation_queue_plan(
        db_session=db_session,
        project_id=project.id,
        user_id="tester",
        artifact_dir=Path("tmp/book-remix-test-ban-dao-20260530"),
        dry_run=False,
    )

    assert result["reused_batch_task"] is True
    assert result["backfilled_expansion_plans"] == 800
    assert result["created_continuation_outlines"] == 10

    refreshed = (
        await db_session.execute(
            select(Chapter)
            .where(Chapter.project_id == project.id)
            .where(Chapter.chapter_number.in_([201, 1000]))
            .order_by(Chapter.chapter_number)
        )
    ).scalars().all()
    assert json.loads(refreshed[0].expansion_plan)["plot_summary"].startswith("承接第200章")
    assert "2021-04-29" in json.loads(refreshed[1].expansion_plan)["reality_timeline_constraints"]


def test_build_bandao_chapter_expansion_plan_projects_stage_and_reality_constraints():
    plan_201 = build_bandao_chapter_expansion_plan(
        201,
        artifact_dir=Path("tmp/book-remix-test-ban-dao-20260530"),
    )
    plan_381 = build_bandao_chapter_expansion_plan(
        381,
        artifact_dir=Path("tmp/book-remix-test-ban-dao-20260530"),
    )
    plan_761 = build_bandao_chapter_expansion_plan(
        761,
        artifact_dir=Path("tmp/book-remix-test-ban-dao-20260530"),
    )

    assert plan_201["target_word_count"] == 10000
    assert plan_201["stage_title"] == "楼梯间余波与日常修罗场"
    assert "沉默的清晨" in plan_201["plot_summary"]
    assert "宿舍深夜" in plan_201["scene_plan"]
    assert "张元英" in plan_201["character_focus"]
    assert "金珉周" in plan_201["character_focus"]

    assert plan_381["stage_title"] == "2019 风波与停摆"
    assert "2019-11" in plan_381["reality_timeline_constraints"]
    assert "Produce 系列投票造假争议" in plan_381["reality_timeline_constraints"]

    assert plan_761["stage_title"] == "IVE 出道与关系重排"
    assert "2021-12-01" in plan_761["reality_timeline_constraints"]
    assert "IVE" in plan_761["reality_timeline_constraints"]
    assert "不加入 IVE 或 LE SSERAFIM 固定阵容" in plan_761["guardrails"]
