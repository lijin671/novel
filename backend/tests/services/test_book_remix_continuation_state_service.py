from __future__ import annotations

import uuid

import pytest

from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan
from app.models.project import Project
from app.services.book_remix_context_service import BookRemixContextService
from app.services.book_remix_continuation_state_service import (
    BookRemixContinuationStateService,
)


async def _create_confirmed_project_state(
    create_schema,
    db_session,
    *,
    source_chapter_count: int = 18,
):
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
        source_task_id="task-1",
        source_chapter_count=source_chapter_count,
        generation_status="confirmed",
        character_cards=[{"name": "Inspector Lin", "goal": "Recover the ledger"}],
        timeline=[{"event": "Warehouse fire", "source": "manual"}],
        story_arcs=[{"name": "Ledger Arc", "status": "open"}],
        foreshadows=[{"hook": "Old rival returns", "status": "open"}],
        hard_constraints=[{"rule": "Do not flip protagonist alignment abruptly"}],
    )
    plan = BookRemixContinuationPlan(
        project_id=project.id,
        bible_id=bible_id,
        status="confirmed",
        summary="Resolve old ledger thread before expanding cast scope.",
        beats=[{"beat": "Recover ledger", "status": "pending"}],
        priority_hooks=[{"hook": "Old rival returns", "status": "pending"}],
        guardrails=[{"rule": "No sudden new power systems"}],
    )
    db_session.add_all([bible, plan])
    await db_session.commit()
    await db_session.refresh(project)
    return project, bible, plan


@pytest.mark.asyncio
async def test_sync_skips_without_confirmed_bible_and_plan(create_schema, db_session):
    await create_schema(
        Project.__table__,
        BookRemixBible.__table__,
        BookRemixContinuationPlan.__table__,
    )

    project = Project(
        id=str(uuid.uuid4()),
        user_id="user-1",
        title="Draft Project",
    )
    bible = BookRemixBible(
        project_id=project.id,
        source_task_id="task-1",
        source_chapter_count=8,
        generation_status="generated",
        timeline=[],
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add(bible)
    await db_session.commit()

    result = await BookRemixContinuationStateService().sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result={"summary": "Recovered the ledger."},
    )

    await db_session.refresh(bible)
    assert result == {"changed": False, "reason": "remix_context_not_confirmed"}
    assert bible.timeline == []


@pytest.mark.asyncio
async def test_sync_updates_bible_plan_and_next_context_block(create_schema, db_session):
    project, bible, plan = await _create_confirmed_project_state(create_schema, db_session)

    result = await BookRemixContinuationStateService().sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result={
            "summary": "Inspector Lin recovered the ledger and faced the old rival in public.",
            "plot_points": [
                {
                    "content": "Inspector Lin recovered ledger from the archive.",
                    "impact": "The ledger arc can move into confrontation.",
                    "importance": 0.9,
                    "type": "resolution",
                }
            ],
            "foreshadows": [
                {
                    "content": "Old rival returns",
                    "type": "resolved",
                    "strength": 8,
                }
            ],
            "character_states": [
                {
                    "character_name": "Inspector Lin",
                    "state_before": "uncertain",
                    "state_after": "decisive",
                    "psychological_change": "Trusts the evidence trail again",
                    "key_event": "Recovered ledger",
                }
            ],
        },
    )

    await db_session.refresh(bible)
    await db_session.refresh(plan)

    assert result["changed"] is True
    assert result["changed_sections"] == [
        "timeline",
        "foreshadows",
        "character_cards",
        "plan_beats",
        "chapter_change_packages",
    ]
    assert any(
        item.get("source") == "chapter_analysis" and item.get("chapter_number") == 19
        for item in bible.timeline
    )
    assert any(
        item.get("hook") == "Old rival returns" and item.get("status") == "resolved"
        for item in bible.foreshadows
    )
    lin_card = next(item for item in bible.character_cards if item.get("name") == "Inspector Lin")
    assert lin_card["continuation_updates"][0]["state_after"] == "decisive"
    assert plan.beats[0]["status"] == "done"
    assert plan.beats[0]["last_chapter_number"] == 19
    assert plan.priority_hooks[0]["status"] == "done"

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )
    assert "Inspector Lin recovered ledger" in block
    assert "Old rival returns" in block


@pytest.mark.asyncio
async def test_sync_is_idempotent_for_same_chapter(create_schema, db_session):
    project, bible, plan = await _create_confirmed_project_state(create_schema, db_session)
    service = BookRemixContinuationStateService()
    analysis_result = {
        "summary": "Inspector Lin recovered the ledger.",
        "plot_points": [{"content": "Inspector Lin recovered ledger", "importance": 0.9}],
        "character_states": [{"character_name": "Inspector Lin", "state_after": "decisive"}],
    }

    first = await service.sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result=analysis_result,
    )
    second = await service.sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result=analysis_result,
    )

    await db_session.refresh(bible)
    await db_session.refresh(plan)

    machine_timeline = [
        item for item in bible.timeline
        if item.get("source") == "chapter_analysis" and item.get("chapter_number") == 19
    ]
    lin_card = next(item for item in bible.character_cards if item.get("name") == "Inspector Lin")

    assert first["changed"] is True
    assert second["changed"] is False
    assert len(machine_timeline) == 1
    assert len(lin_card["continuation_updates"]) == 1
    assert plan.beats[0]["status"] == "done"


@pytest.mark.asyncio
async def test_sync_preserves_manual_entries(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(create_schema, db_session)
    original_manual_timeline = list(bible.timeline)

    await BookRemixContinuationStateService().sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-20",
        chapter_number=20,
        chapter_title="Aftermath",
        analysis_result={
            "summary": "The investigation moves to the city archive.",
            "plot_points": [{"content": "Archive search begins", "importance": 0.8}],
        },
    )

    await db_session.refresh(bible)

    assert bible.timeline[0] == original_manual_timeline[0]
    assert any(
        item.get("source") == "chapter_analysis" and item.get("chapter_number") == 20
        for item in bible.timeline
    )


@pytest.mark.asyncio
async def test_sync_allows_repeated_chapters_after_machine_bible_update(create_schema, db_session):
    project, bible, plan = await _create_confirmed_project_state(create_schema, db_session)
    service = BookRemixContinuationStateService()

    first = await service.sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result={
            "summary": "Inspector Lin recovered the ledger.",
            "plot_points": [{"content": "Inspector Lin recovered ledger", "importance": 0.9}],
        },
    )
    second = await service.sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-20",
        chapter_number=20,
        chapter_title="Archive Aftermath",
        analysis_result={
            "summary": "Inspector Lin opened the city archive aftermath file.",
            "plot_points": [{"content": "Archive aftermath file opened", "importance": 0.8}],
        },
    )

    await db_session.refresh(bible)

    assert first["changed"] is True
    assert second["changed"] is True
    assert any(
        item.get("source") == "chapter_analysis" and item.get("chapter_number") == 20
        for item in bible.timeline
    )


@pytest.mark.asyncio
async def test_sync_persists_structured_chapter_change_package(create_schema, db_session):
    project, bible, plan = await _create_confirmed_project_state(create_schema, db_session)

    result = await BookRemixContinuationStateService().sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result={
            "summary": "Inspector Lin recovered the ledger and faced the old rival in public.",
            "plot_points": [
                {"content": "Inspector Lin recovered ledger", "importance": 0.9},
                {"content": "A minor crowd reaction", "importance": 0.2},
            ],
            "foreshadows": [
                {"content": "Old rival returns", "type": "resolved", "strength": 8},
                {"content": "Archive witness hesitates", "type": "open", "strength": 5},
            ],
            "character_states": [
                {
                    "character_name": "Inspector Lin",
                    "state_before": "uncertain",
                    "state_after": "decisive",
                    "psychological_change": "Trusts the evidence trail again",
                    "key_event": "Recovered ledger",
                }
            ],
        },
    )

    await db_session.refresh(bible)
    await db_session.refresh(plan)

    assert result["changed"] is True
    assert "chapter_change_packages" in result["changed_sections"]
    assert len(bible.chapter_change_packages) == 1

    package = bible.chapter_change_packages[0]
    assert package["source"] == "chapter_analysis"
    assert package["chapter_id"] == "chapter-19"
    assert package["chapter_number"] == 19
    assert package["summary"] == "Inspector Lin recovered the ledger and faced the old rival in public."
    assert package["timeline_delta"][0]["event"] == "Inspector Lin recovered ledger"
    assert package["character_state_changes"][0]["character_name"] == "Inspector Lin"
    assert package["character_state_changes"][0]["state_after"] == "decisive"
    assert package["foreshadow_changes"][0]["hook"] == "Old rival returns"
    assert package["foreshadow_changes"][0]["status"] == "resolved"
    assert package["plan_progress"][0]["beat"] == "Recover ledger"
    assert package["plan_progress"][0]["status"] == "done"
    assert package["changed_sections"] == result["changed_sections"]


@pytest.mark.asyncio
async def test_sync_chapter_change_package_is_idempotent(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(create_schema, db_session)
    service = BookRemixContinuationStateService()
    analysis_result = {
        "summary": "Inspector Lin recovered the ledger.",
        "plot_points": [{"content": "Inspector Lin recovered ledger", "importance": 0.9}],
    }

    await service.sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result=analysis_result,
    )
    second = await service.sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result=analysis_result,
    )

    await db_session.refresh(bible)

    assert second["changed"] is False
    assert len(bible.chapter_change_packages) == 1


@pytest.mark.asyncio
async def test_sync_chapter_change_package_preserves_existing_packages(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(create_schema, db_session)
    bible.chapter_change_packages = [
        {
            "type": "chapter_change_package",
            "source": "manual",
            "chapter_id": "manual-note",
            "chapter_number": 0,
            "summary": "Manual continuity checkpoint",
        }
    ]
    await db_session.commit()

    await BookRemixContinuationStateService().sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result={
            "summary": "Inspector Lin recovered the ledger.",
            "plot_points": [{"content": "Inspector Lin recovered ledger", "importance": 0.9}],
        },
    )

    await db_session.refresh(bible)

    assert bible.chapter_change_packages[0]["source"] == "manual"
    assert any(
        item.get("source") == "chapter_analysis" and item.get("chapter_number") == 19
        for item in bible.chapter_change_packages
    )


@pytest.mark.asyncio
async def test_sync_chapter_change_package_keeps_whole_continuation_history(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(
        create_schema,
        db_session,
        source_chapter_count=25,
    )
    service = BookRemixContinuationStateService()

    for chapter_number in range(1, 26):
        await service.sync_chapter_analysis(
            db=db_session,
            project_id=project.id,
            chapter_id=f"chapter-{chapter_number}",
            chapter_number=chapter_number,
            chapter_title=f"Chapter {chapter_number}",
            analysis_result={
                "summary": f"Continuation event {chapter_number}",
                "plot_points": [
                    {"content": f"Continuation timeline event {chapter_number}", "importance": 0.9}
                ],
            },
        )

    await db_session.refresh(bible)

    chapter_numbers = [
        item.get("chapter_number")
        for item in bible.chapter_change_packages
        if item.get("source") == "chapter_analysis"
    ]
    assert chapter_numbers == list(range(1, 26))

@pytest.mark.asyncio
async def test_commit_generated_chapter_creates_immediate_package_before_analysis(create_schema, db_session):
    project, bible, plan = await _create_confirmed_project_state(create_schema, db_session)

    result = await BookRemixContinuationStateService().commit_generated_chapter(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        chapter_content="Inspector Lin recovered the ledger, faced the old rival, and chose to question the archive witness next.",
        chapter_outline="Recover ledger and push the archive witness thread forward.",
        previous_chapter_summary="Inspector Lin lost the first lead.",
        continuation_point="Lin looked toward the archive.",
    )

    await db_session.refresh(bible)
    await db_session.refresh(plan)

    assert result["changed"] is True
    assert result["reason"] == "committed"
    assert result["changed_sections"] == ["timeline", "character_cards", "plan_beats", "chapter_change_packages"]

    package = bible.chapter_change_packages[0]
    assert package["source"] == "chapter_generation"
    assert package["chapter_number"] == 19
    assert package["summary"] == "Inspector Lin recovered the ledger, faced the old rival, and chose to question the archive witness next."
    assert package["timeline_delta"][0]["event"] == "Inspector Lin recovered the ledger, faced the old rival, and chose to question the archive witness next."
    assert package["plan_progress"][0]["beat"] == "Recover ledger"
    assert package["plan_progress"][0]["status"] == "done"
    assert package["character_state_changes"][0]["character_name"] == "Inspector Lin"
    assert plan.beats[0]["status"] == "done"


@pytest.mark.asyncio
async def test_commit_generated_chapter_persists_chapter_progress_report(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(create_schema, db_session)

    await BookRemixContinuationStateService().commit_generated_chapter(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        chapter_content=(
            "Inspector Lin recovered the ledger, faced the old rival, "
            "and chose to question the archive witness next."
        ),
        chapter_outline="Recover ledger and push the archive witness thread forward.",
        previous_chapter_summary="Inspector Lin lost the first lead.",
        continuation_point="Lin looked toward the archive.",
    )

    await db_session.refresh(bible)

    package = bible.chapter_change_packages[0]
    report = package["chapter_progress_report"]

    assert report["chapter"] == "Ch19: Ledger Returns"
    assert report["summary"] == package["summary"]
    assert report["new_facts"] == package["timeline_delta"]
    assert report["character_changes"] == package["character_state_changes"]
    assert report["hooks_paid_off"] == []
    assert report["new_hooks"] == []
    assert report["continuity_updates"]
    assert report["next_chapter_likely_focus"] == "Lin looked toward the archive."
    assert report["word_count"] > 0
    assert report["risks"] == ["analysis_pending: generated chapter awaits structured analysis sync"]


@pytest.mark.asyncio
async def test_sync_chapter_analysis_persists_chapter_progress_report(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(create_schema, db_session)

    await BookRemixContinuationStateService().sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result={
            "summary": "Inspector Lin verified the ledger and exposed the archive witness clue.",
            "plot_points": [
                {
                    "content": "Archive witness clue exposed",
                    "importance": 0.9,
                    "impact": "The next chapter can pressure the witness.",
                },
            ],
            "foreshadows": [
                {"content": "Old rival returns", "type": "resolved", "strength": 8},
                {"content": "Archive witness hesitates", "type": "open", "strength": 5},
            ],
            "character_states": [
                {
                    "character_name": "Inspector Lin",
                    "state_before": "uncertain",
                    "state_after": "suspicious",
                    "key_event": "Verified ledger",
                }
            ],
            "continuity_updates": [
                {"field": "ledger_status", "value": "verified"}
            ],
            "next_chapter_likely_focus": "Force the archive witness to choose a side.",
            "word_count": 2400,
            "risks": ["witness thread can flatten if resolved off-screen"],
        },
    )

    await db_session.refresh(bible)

    package = bible.chapter_change_packages[0]
    report = package["chapter_progress_report"]

    assert report == {
        "chapter": "Ch19: Ledger Returns",
        "summary": "Inspector Lin verified the ledger and exposed the archive witness clue.",
        "new_facts": package["timeline_delta"],
        "character_changes": package["character_state_changes"],
        "hooks_paid_off": [{"hook": "Old rival returns", "status": "resolved", "strength": 8}],
        "new_hooks": [{"hook": "Archive witness hesitates", "status": "open", "strength": 5}],
        "continuity_updates": [{"field": "ledger_status", "value": "verified"}],
        "next_chapter_likely_focus": "Force the archive witness to choose a side.",
        "word_count": 2400,
        "risks": ["witness thread can flatten if resolved off-screen"],
    }


@pytest.mark.asyncio
async def test_sync_chapter_analysis_replaces_generated_package_for_same_chapter(create_schema, db_session):
    project, bible, plan = await _create_confirmed_project_state(create_schema, db_session)
    service = BookRemixContinuationStateService()

    await service.commit_generated_chapter(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        chapter_content="Inspector Lin recovered the ledger and carried the updated ledger state into the archive.",
        chapter_outline="Recover ledger.",
        previous_chapter_summary="Inspector Lin lost the first lead.",
        continuation_point="Lin looked toward the archive.",
    )

    result = await service.sync_chapter_analysis(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        analysis_result={
            "summary": "Inspector Lin verified the ledger and exposed the archive witness clue.",
            "plot_points": [
                {"content": "Archive witness clue exposed", "importance": 0.9},
            ],
            "foreshadows": [
                {"content": "Archive witness hesitates", "type": "open", "strength": 5},
            ],
            "character_states": [
                {
                    "character_name": "Inspector Lin",
                    "state_after": "suspicious",
                    "key_event": "Verified ledger",
                }
            ],
        },
    )

    await db_session.refresh(bible)
    await db_session.refresh(plan)

    chapter_19_packages = [
        item
        for item in bible.chapter_change_packages
        if item.get("chapter_number") == 19
    ]
    chapter_19_timeline = [
        item
        for item in bible.timeline
        if item.get("chapter_number") == 19
    ]
    lin_card = next(item for item in bible.character_cards if item.get("name") == "Inspector Lin")
    chapter_19_updates = [
        item
        for item in lin_card.get("continuation_updates", [])
        if item.get("chapter_number") == 19
    ]

    assert result["changed"] is True
    assert len(chapter_19_packages) == 1
    assert len(chapter_19_timeline) == 1
    assert chapter_19_timeline[0]["source"] == "chapter_analysis"
    assert chapter_19_timeline[0]["event"] == "Archive witness clue exposed"
    assert len(chapter_19_updates) == 1
    assert chapter_19_updates[0]["source"] == "chapter_analysis"
    assert chapter_19_updates[0]["state_after"] == "suspicious"
    package = chapter_19_packages[0]
    assert package["source"] == "chapter_analysis"
    assert package["summary"] == "Inspector Lin verified the ledger and exposed the archive witness clue."
    assert package["timeline_delta"][0]["event"] == "Archive witness clue exposed"
    assert package["character_state_changes"][0]["state_after"] == "suspicious"
    assert package["foreshadow_changes"][0]["hook"] == "Archive witness hesitates"
    assert package["plan_progress"][0]["beat"] == "Recover ledger"
    assert package["changed_sections"] == result["changed_sections"]

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )
    assert block.count("Chapter 19: Ledger Returns") == 1



@pytest.mark.asyncio
async def test_commit_generated_chapter_is_visible_to_next_context(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(create_schema, db_session)

    await BookRemixContinuationStateService().commit_generated_chapter(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        chapter_content="Inspector Lin recovered the ledger and carried the updated ledger state into the archive.",
        chapter_outline="Recover ledger.",
        previous_chapter_summary="Inspector Lin lost the first lead.",
        continuation_point="Lin looked toward the archive.",
    )

    block = await BookRemixContextService().build_project_context_block(
        project=project,
        db=db_session,
    )

    assert "Whole-book continuation progress" in block
    assert "Recent chapter change packages" in block
    assert "Chapter 19: Ledger Returns" in block
    assert "updated ledger state" in block


@pytest.mark.asyncio
async def test_commit_generated_chapter_is_idempotent_for_same_chapter(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(create_schema, db_session)
    service = BookRemixContinuationStateService()

    first = await service.commit_generated_chapter(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        chapter_content="Inspector Lin recovered the ledger.",
        chapter_outline="Recover ledger.",
        previous_chapter_summary="Inspector Lin lost the first lead.",
        continuation_point="Lin looked toward the archive.",
    )
    second = await service.commit_generated_chapter(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        chapter_content="Inspector Lin recovered the ledger.",
        chapter_outline="Recover ledger.",
        previous_chapter_summary="Inspector Lin lost the first lead.",
        continuation_point="Lin looked toward the archive.",
    )

    await db_session.refresh(bible)

    assert first["changed"] is True
    assert second == {"changed": False, "reason": "already_committed", "changed_sections": []}
    assert len([item for item in bible.chapter_change_packages if item.get("source") == "chapter_generation"]) == 1


@pytest.mark.asyncio
async def test_commit_generated_chapter_updates_existing_package_when_content_changes(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(create_schema, db_session)
    service = BookRemixContinuationStateService()

    await service.commit_generated_chapter(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        chapter_content="Inspector Lin recovered the ledger.",
        chapter_outline="Recover ledger.",
        previous_chapter_summary="Inspector Lin lost the first lead.",
        continuation_point="Lin looked toward the archive.",
    )
    second = await service.commit_generated_chapter(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns Revised",
        chapter_content="Inspector Lin recovered the ledger, burned the false copy, and opened the city hall file.",
        chapter_outline="Recover ledger and open city hall file.",
        previous_chapter_summary="Inspector Lin lost the first lead.",
        continuation_point="Lin looked toward the archive.",
    )

    await db_session.refresh(bible)

    generation_packages = [
        item for item in bible.chapter_change_packages
        if item.get("source") == "chapter_generation"
    ]
    generation_timeline = [
        item for item in bible.timeline
        if item.get("source") == "chapter_generation"
    ]

    assert second["changed"] is True
    assert second["reason"] == "committed"
    assert len(generation_packages) == 1
    assert len(generation_timeline) == 1
    assert generation_packages[0]["chapter_title"] == "Ledger Returns Revised"
    assert "city hall file" in generation_packages[0]["summary"]
    assert "city hall file" in generation_timeline[0]["event"]


@pytest.mark.asyncio
async def test_commit_generated_chapter_records_guardrail_meta_in_change_package(create_schema, db_session):
    project, bible, _plan = await _create_confirmed_project_state(create_schema, db_session)

    result = await BookRemixContinuationStateService().commit_generated_chapter(
        db=db_session,
        project_id=project.id,
        chapter_id="chapter-19",
        chapter_number=19,
        chapter_title="Ledger Returns",
        chapter_content="Inspector Lin moves forward after the ledger is already secured.",
        chapter_outline="Move beyond ledger recovery.",
        previous_chapter_summary="Inspector Lin already recovered the ledger.",
        continuation_point="Lin looked toward the archive.",
        guardrail_meta={
            "applied": True,
            "attempts": 1,
            "initial_result": {
                "passed": False,
                "violations": [
                    {
                        "type": "canon_repetition",
                        "severity": "high",
                        "description": "repeated confirmed Canon",
                        "context": "Inspector Lin recovered the ledger again",
                    }
                ],
            },
            "final_result": {"passed": True, "violations": []},
        },
    )

    await db_session.refresh(bible)

    assert result["changed"] is True
    assert "guardrail_check" in result["changed_sections"]
    package = bible.chapter_change_packages[0]
    assert package["guardrail_check"] == {
        "applied": True,
        "attempts": 1,
        "initial_passed": False,
        "final_passed": True,
        "violations": [
            {
                "type": "canon_repetition",
                "severity": "high",
                "description": "repeated confirmed Canon",
                "context": "Inspector Lin recovered the ledger again",
            }
        ],
    }
    assert "guardrail_check" in package["changed_sections"]
