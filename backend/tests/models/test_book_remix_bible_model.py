from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import select

from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan
from app.models.project import Project


@pytest.mark.asyncio
async def test_book_remix_bible_and_plan_persistence(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    project = Project(
        user_id="user-test",
        title="Remix Project",
        description="Used for remix bible persistence test",
    )
    db_session.add(project)
    await db_session.flush()

    bible = BookRemixBible(
        project_id=project.id,
        source_task_id="task-source-001",
        generation_status="generated",
        source_chapter_count=30,
        world_rules={"power_system": "strict"},
        character_cards=[{"name": "Lin", "core_trait": "calm"}],
        organizations=[{"name": "Shadow Court", "goal": "control trade lanes"}],
        timeline=[{"order": 1, "event": "opening conflict"}],
        story_arcs=[{"name": "Arc A", "status": "active"}],
        foreshadows=[{"hook": "broken ring", "state": "open"}],
        style_signature={"narrative_pov": "third_person", "tone": "tense"},
        hard_constraints=[
            {"key": "pov", "rule": "keep core POV"},
            {"key": "timeline", "rule": "do not retcon timeline"},
        ],
        conflicts=[{"type": "internal", "parties": ["Lin"]}],
        generation_notes=["initial extraction"],
        chapter_change_packages=[{"chapter_number": 1, "summary": "opening changed"}],
    )
    db_session.add(bible)
    await db_session.flush()

    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible.id,
        status="draft",
        summary="stabilize rivalry line before expanding cast",
        stage_goals=[{"goal": "stabilize conflict line"}],
        beats=[{"chapter": 31, "focus": "foreshadow payoff"}],
        priority_hooks=[{"hook": "broken ring"}],
        guardrails=[
            {"key": "voice", "rule": "maintain original voice"},
            {"key": "world", "rule": "keep rule consistency"},
        ],
    )
    db_session.add(plan)
    await db_session.commit()

    loaded_bible = (
        await db_session.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project.id)
        )
    ).scalar_one()
    assert loaded_bible.source_task_id == "task-source-001"
    assert loaded_bible.generation_status == "generated"
    assert loaded_bible.source_chapter_count == 30
    assert loaded_bible.world_rules["power_system"] == "strict"
    assert loaded_bible.character_cards[0]["name"] == "Lin"
    assert loaded_bible.hard_constraints[1]["rule"] == "do not retcon timeline"
    assert loaded_bible.generation_notes == ["initial extraction"]
    assert loaded_bible.chapter_change_packages[0]["summary"] == "opening changed"

    loaded_plan = (
        await db_session.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project.id
            )
        )
    ).scalar_one()
    assert loaded_plan.status == "draft"
    assert loaded_plan.summary.startswith("stabilize rivalry")
    assert loaded_plan.beats[0]["chapter"] == 31
    assert loaded_plan.guardrails[0]["rule"] == "maintain original voice"

    loaded_bible.generation_status = "confirmed"
    loaded_bible.source_chapter_count = 31
    loaded_bible.generation_notes = [*loaded_bible.generation_notes, "reviewed and confirmed"]
    loaded_bible.chapter_change_packages = [
        *loaded_bible.chapter_change_packages,
        {"chapter_number": 2, "summary": "second chapter changed"},
    ]
    loaded_bible.confirmed_at = datetime.utcnow()
    loaded_bible.hard_constraints = [
        *loaded_bible.hard_constraints,
        {"key": "power_scale", "rule": "avoid abrupt power inflation"},
    ]

    loaded_plan.status = "confirmed"
    loaded_plan.summary = "phase-1 continuation locked"
    loaded_plan.guardrails = [
        *loaded_plan.guardrails,
        {"key": "clue_check", "rule": "validate unresolved clues before writing"},
    ]
    loaded_plan.confirmed_at = datetime.utcnow()

    await db_session.commit()
    await db_session.refresh(loaded_bible)
    await db_session.refresh(loaded_plan)

    assert loaded_bible.generation_status == "confirmed"
    assert loaded_bible.source_chapter_count == 31
    assert loaded_bible.confirmed_at is not None
    assert loaded_bible.generation_notes[-1] == "reviewed and confirmed"
    assert loaded_bible.chapter_change_packages[-1]["chapter_number"] == 2
    assert loaded_bible.hard_constraints[-1]["rule"] == "avoid abrupt power inflation"
    assert loaded_plan.status == "confirmed"
    assert loaded_plan.summary == "phase-1 continuation locked"
    assert loaded_plan.confirmed_at is not None
    assert loaded_plan.guardrails[-1]["rule"] == "validate unresolved clues before writing"
