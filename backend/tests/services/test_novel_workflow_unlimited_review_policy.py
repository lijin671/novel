from __future__ import annotations

import pytest

from app.models.chapter import Chapter
from app.models.memory import PlotAnalysis
from app.services.novel_workflow_service import NovelWorkflowService
import app.services.novel_workflow_service as novel_workflow_module


class StubAIService:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    async def call_with_json_retry(self, **kwargs):
        self.prompts.append(kwargs["prompt"])
        return {}


def test_resolve_review_round_policy_caps_unlimited_request_with_stop_condition():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]

    policy = service.resolve_review_round_policy(
        requested_max_rounds=0,
        min_score=7.8,
    )

    assert policy == {
        "requested_max_rounds": 0,
        "effective_max_rounds": 12,
        "unlimited_requested": True,
        "min_score": 7.8,
        "stop_conditions": [
            "overall_score >= 7.8",
            "no high/critical issues",
            "style_fidelity_score >= 7.4",
            "no high/critical style drift",
            "reader_score >= 7.4",
            "round_index >= 12",
        ],
    }


def test_resolve_review_round_policy_clamps_manual_rounds_to_safe_window():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]

    low_policy = service.resolve_review_round_policy(requested_max_rounds=-3, min_score=11)
    high_policy = service.resolve_review_round_policy(requested_max_rounds=99, min_score=3)

    assert low_policy["effective_max_rounds"] == 12
    assert low_policy["unlimited_requested"] is True
    assert low_policy["min_score"] == 9.5
    assert high_policy["effective_max_rounds"] == 12
    assert high_policy["unlimited_requested"] is False
    assert high_policy["min_score"] == 5.0


def test_aggregate_feedback_revises_on_high_style_drift_even_when_scores_pass():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]

    reviewers = service._normalize_reviewers([
        {
            "role": "style reviewer",
            "overall_score": 9.1,
            "pacing_score": 9.0,
            "engagement_score": 9.0,
            "coherence_score": 9.0,
            "verdict": "pass",
            "strengths": ["plot moves forward"],
            "issues": [],
            "must_fix": [],
            "style_fidelity_score": 4.0,
            "style_drift_issues": [
                {
                    "severity": "high",
                    "title": "original voice drift",
                    "detail": "The continuation loses the source book's restrained voice.",
                    "advice": "Restore the original voice, cadence, and narrative temperature.",
                }
            ],
        }
    ])
    readers = [
        {
            "persona": "reader",
            "immersion_score": 9.0,
            "continue_score": 9.0,
            "favorite_points": [],
            "drop_risks": [],
            "expectations": [],
        }
    ]

    aggregate = service._aggregate_feedback(
        analysis=None,
        reviewers=reviewers,
        readers=readers,
        min_score=7.8,
    )

    assert aggregate["decision"] == "revise"
    assert aggregate["style_fidelity"]["score"] == 4.0
    assert aggregate["style_fidelity"]["min_score"] == 4.0
    assert aggregate["style_fidelity"]["has_blocking_drift"] is True
    assert aggregate["style_drift_issues"][0]["title"] == "original voice drift"
    assert "original voice drift" in aggregate["top_issues"]


def test_aggregate_feedback_revises_on_low_style_fidelity_without_drift_issue():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]

    reviewers = service._normalize_reviewers([
        {
            "role": "style reviewer",
            "overall_score": 9.2,
            "pacing_score": 9.0,
            "engagement_score": 9.0,
            "coherence_score": 9.0,
            "verdict": "pass",
            "strengths": [],
            "issues": [],
            "must_fix": [],
            "style_fidelity_score": 6.0,
            "style_drift_issues": [],
        },
        {
            "role": "plot reviewer",
            "overall_score": 9.4,
            "pacing_score": 9.0,
            "engagement_score": 9.0,
            "coherence_score": 9.0,
            "verdict": "pass",
            "strengths": [],
            "issues": [],
            "must_fix": [],
            "style_fidelity_score": 9.5,
            "style_drift_issues": [],
        },
    ])
    readers = [
        {
            "persona": "reader",
            "immersion_score": 9.0,
            "continue_score": 9.0,
            "favorite_points": [],
            "drop_risks": [],
            "expectations": [],
        }
    ]

    aggregate = service._aggregate_feedback(
        analysis=None,
        reviewers=reviewers,
        readers=readers,
        min_score=7.8,
    )

    assert aggregate["decision"] == "revise"
    assert aggregate["style_fidelity"]["score"] > aggregate["style_fidelity"]["floor"]
    assert aggregate["style_fidelity"]["min_score"] == 6.0
    assert aggregate["style_fidelity"]["has_low_score"] is True


def test_aggregate_feedback_keeps_legacy_reviewer_without_style_fields_passing():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]

    reviewers = service._normalize_reviewers([
        {
            "role": "legacy reviewer",
            "overall_score": 9.0,
            "pacing_score": 9.0,
            "engagement_score": 9.0,
            "coherence_score": 9.0,
            "verdict": "pass",
            "strengths": [],
            "issues": [],
            "must_fix": [],
        }
    ])
    readers = [
        {
            "persona": "reader",
            "immersion_score": 9.0,
            "continue_score": 9.0,
            "favorite_points": [],
            "drop_risks": [],
            "expectations": [],
        }
    ]

    aggregate = service._aggregate_feedback(
        analysis=None,
        reviewers=reviewers,
        readers=readers,
        min_score=7.8,
    )

    assert aggregate["decision"] == "pass"
    assert aggregate["style_fidelity"] == {
        "score": 0.0,
        "min_score": 0.0,
        "floor": 7.4,
        "has_low_score": False,
        "has_blocking_drift": False,
    }
    assert aggregate["style_drift_issues"] == []


def test_build_revision_brief_includes_style_drift_repair_requirements():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-style-drift",
        project_id="project-style-drift",
        chapter_number=12,
        title="Borrowed Voice",
        content="A continuation chapter with wrong style.",
        word_count=42,
        status="completed",
    )
    aggregate = {
        "high_risk_issues": [],
        "top_issues": [],
        "reader_risks": [],
        "style_drift_issues": [
            {
                "severity": "high",
                "title": "cadence drift",
                "detail": "Sentence rhythm is too modern and clipped.",
                "advice": "Match the source cadence and emotional pressure.",
            }
        ],
    }

    brief = service._build_revision_brief(
        chapter=chapter,
        analysis=None,
        aggregate=aggregate,
    )

    assert "Style fidelity repair" in brief
    assert "cadence drift" in brief
    assert "Match the source cadence and emotional pressure" in brief
    assert "original voice" in brief
    assert "narrative temperature" in brief


@pytest.mark.asyncio
async def test_review_panel_prompt_requires_style_fidelity_schema_and_checks():
    ai_service = StubAIService()
    service = NovelWorkflowService(ai_service)  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-style-prompt",
        project_id="project-style-prompt",
        chapter_number=5,
        title="Style Gate",
        content="The continuation must keep the old book flavor.",
        summary="Style gate sample.",
        word_count=52,
        status="completed",
    )
    source_pattern_pack = {
        "style_fidelity_hints": [
            "Preserve the original voice, cadence, and narrative temperature."
        ],
        "style_signature_hints": [
            "Match sentence rhythm, POV behavior, scene density, and emotional pressure."
        ],
    }

    await service._run_review_panel(
        chapter=chapter,
        analysis=None,
        source_pattern_pack=source_pattern_pack,
    )

    prompt = ai_service.prompts[0]
    assert "style_fidelity_score" in prompt
    assert "style_drift_issues" in prompt
    assert "original voice" in prompt
    assert "cadence" in prompt
    assert "narrative temperature" in prompt
    assert "style drift" in prompt
    assert "style_fidelity_hints" in prompt


@pytest.mark.asyncio
async def test_reader_panel_prompt_projects_universal_reader_pull_schema():
    ai_service = StubAIService()
    service = NovelWorkflowService(ai_service)  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-reader-pull-prompt",
        project_id="project-reader-pull-prompt",
        chapter_number=7,
        title="Reader Pull",
        content="The witness refuses to name the saboteur, but the bell starts ringing.",
        summary="The witness scene reaches a decision point.",
        word_count=88,
        status="completed",
    )
    source_pattern_pack = {
        "workflow_patterns": [
            {"name": "reader_pull_fresh_reader_gate", "candidate_count": 1},
        ],
        "reader_pull_fresh_reader_gate_hints": [
            "A fresh reader must be able to answer POV, want, obstacle, stakes, changed state, and pull-forward question."
        ],
    }

    await service._run_reader_panel(
        chapter=chapter,
        analysis=None,
        source_pattern_pack=source_pattern_pack,
    )

    prompt = ai_service.prompts[0]
    assert "Public source pattern constraints" in prompt
    assert "reader_pull_fresh_reader_gate" in prompt
    assert "reader_pull_answers" in prompt
    assert "pov_character" in prompt
    assert "current_want" in prompt
    assert "obstacle" in prompt
    assert "stakes" in prompt
    assert "changed_state" in prompt
    assert "pull_forward" in prompt


@pytest.mark.asyncio
async def test_reader_panel_prompt_projects_universal_post_draft_review_schema():
    ai_service = StubAIService()
    service = NovelWorkflowService(ai_service)  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-post-draft-review-prompt",
        project_id="project-post-draft-review-prompt",
        chapter_number=8,
        title="Post Draft Review",
        content="The hearing scene is fluent, but the acceptance packet still needs review evidence.",
        summary="A post-draft review prompt sample.",
        word_count=96,
        status="completed",
    )
    source_pattern_pack = {
        "workflow_patterns": [
            {"name": "post_draft_review_checklist_gate", "candidate_count": 1},
        ],
        "post_draft_review_checklist_gate_hints": [
            "Accept chapters only after structure, continuity, POV, voice, conflict, pacing, reader-pull, hook/payoff, naturalness, and mobile readability review."
        ],
    }

    await service._run_reader_panel(
        chapter=chapter,
        analysis=None,
        source_pattern_pack=source_pattern_pack,
    )

    prompt = ai_service.prompts[0]
    assert "post_draft_review_checklist_gate" in prompt
    assert "post_draft_review_packet" in prompt
    assert "mobile_readability_review" in prompt
    assert "least_destructive_repair_scope" in prompt
    assert "structure" in prompt
    assert "naturalness" in prompt
    assert "mobile readability" in prompt


@pytest.mark.asyncio
async def test_reader_panel_prompt_projects_novelwriter_live_diagnostics_schema():
    ai_service = StubAIService()
    service = NovelWorkflowService(ai_service)  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-live-diagnostics-prompt",
        project_id="project-live-diagnostics-prompt",
        chapter_number=9,
        title="Live Diagnostics",
        content="The archive bell rings while Lin sees two old alliances fracture.",
        summary="A diagnostic prompt sample.",
        word_count=91,
        status="completed",
    )
    source_pattern_pack = {
        "workflow_patterns": [
            {"name": "novelwriter_live_manuscript_analytics_gate", "candidate_count": 1},
        ],
        "novelwriter_live_manuscript_analytics_gate_hints": [
            "Surface Event Line, open plot lines, Connection Web, Story Pulse, and inline suggestions as advisory diagnostics."
        ],
    }

    await service._run_reader_panel(
        chapter=chapter,
        analysis=None,
        source_pattern_pack=source_pattern_pack,
    )

    prompt = ai_service.prompts[0]
    assert "novelwriter_live_manuscript_analytics_gate" in prompt
    assert "live_diagnostics" in prompt
    assert "Event Line" in prompt
    assert "open plot lines" in prompt
    assert "Connection Web" in prompt
    assert "Story Pulse" in prompt
    assert "inline_suggestions" in prompt
    assert "advisory diagnostics" in prompt


@pytest.mark.asyncio
async def test_reader_panel_prompt_projects_hook_payoff_schema():
    ai_service = StubAIService()
    service = NovelWorkflowService(ai_service)  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-hook-payoff-prompt",
        project_id="project-hook-payoff-prompt",
        chapter_number=12,
        title="Hook Payoff",
        content="The witness speaks, but the bell interrupts before the council can close the case.",
        summary="A hook and payoff prompt sample.",
        word_count=94,
        status="completed",
    )
    source_pattern_pack = {
        "workflow_patterns": [
            {"name": "premise_structure_hook_payoff_gate", "candidate_count": 1},
            {"name": "opening_ending_hook_integrity_gate", "candidate_count": 1},
        ],
        "premise_structure_hook_payoff_gate_hints": [
            "Maintain a hook/payoff matrix with reader promise, planned payoff, and current status."
        ],
        "opening_ending_hook_integrity_gate_hints": [
            "Opening hook and ending hook job must be visible on the page."
        ],
    }

    await service._run_reader_panel(
        chapter=chapter,
        analysis=None,
        source_pattern_pack=source_pattern_pack,
    )

    prompt = ai_service.prompts[0]
    assert "hook_payoff_answers" in prompt
    assert "opening_hook_type" in prompt
    assert "reader_promise" in prompt
    assert "ending_hook_job" in prompt
    assert "micro_payoff" in prompt
    assert "required_payoff" in prompt
    assert "Hook/payoff integrity gate" in prompt
    assert "fake cliffhanger" in prompt


@pytest.mark.asyncio
async def test_reader_panel_prompt_projects_chapter_contract_scene_beat_schema():
    ai_service = StubAIService()
    service = NovelWorkflowService(ai_service)  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-contract-scene-beat-prompt",
        project_id="project-contract-scene-beat-prompt",
        chapter_number=16,
        title="Scene Contract",
        content=(
            "Lin enters the archive hearing with one goal, but each witness turns "
            "the public proof into a higher-cost choice."
        ),
        summary="A chapter contract and scene beat prompt sample.",
        word_count=121,
        status="completed",
    )
    source_pattern_pack = {
        "workflow_patterns": [
            {"name": "chapter_contract_scene_beat_gate", "candidate_count": 1},
        ],
        "chapter_contract_scene_beat_gate_hints": [
            "Before drafting, define chapter goal, opening hook, main obstacle, turning point, emotional shift, payoff, ending hook, and 3-7 scene beats with exit states."
        ],
    }

    await service._run_reader_panel(
        chapter=chapter,
        analysis=None,
        source_pattern_pack=source_pattern_pack,
    )

    prompt = ai_service.prompts[0]
    assert "chapter_contract_answers" in prompt
    assert "scene_beats" in prompt
    assert "chapter_goal" in prompt
    assert "main_obstacle" in prompt
    assert "turning_point" in prompt
    assert "emotional_shift" in prompt
    assert "revealed_information" in prompt
    assert "continuity_changes" in prompt
    assert "exit_state" in prompt
    assert "Chapter contract and scene-beat gate" in prompt
    assert "3-7 visible scene beats" in prompt


def test_aggregate_feedback_revises_when_required_reader_pull_answers_are_missing():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    reviewers = service._normalize_reviewers([
        {
            "role": "editor",
            "overall_score": 9.0,
            "pacing_score": 9.0,
            "engagement_score": 9.0,
            "coherence_score": 9.0,
            "style_fidelity_score": 9.0,
            "verdict": "pass",
            "strengths": [],
            "issues": [],
            "style_drift_issues": [],
            "must_fix": [],
        }
    ])
    readers = service._normalize_readers([
        {
            "persona": "fresh reader",
            "immersion_score": 9.0,
            "continue_score": 9.0,
            "favorite_points": [],
            "drop_risks": [],
            "expectations": [],
            "reader_pull_answers": {
                "pov_character": "Lin",
                "current_want": "",
            },
        }
    ])

    aggregate = service._aggregate_feedback(
        analysis=None,
        reviewers=reviewers,
        readers=readers,
        min_score=7.8,
        source_pattern_pack={
            "workflow_patterns": [{"name": "reader_pull_fresh_reader_gate"}],
        },
    )

    assert aggregate["decision"] == "revise"
    assert aggregate["reader_pull"]["required"] is True
    assert aggregate["reader_pull"]["blocking"] is True
    assert aggregate["reader_pull"]["missing_count"] > 0
    assert "reader_pull_missing" in aggregate["top_issues"]


def test_aggregate_feedback_revises_when_required_live_diagnostics_are_missing():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    reviewers = service._normalize_reviewers([
        {
            "role": "editor",
            "overall_score": 9.0,
            "pacing_score": 9.0,
            "engagement_score": 9.0,
            "coherence_score": 9.0,
            "style_fidelity_score": 9.0,
            "verdict": "pass",
            "strengths": [],
            "issues": [],
            "style_drift_issues": [],
            "must_fix": [],
        }
    ])
    readers = service._normalize_readers([
        {
            "persona": "fresh reader",
            "immersion_score": 9.0,
            "continue_score": 9.0,
            "favorite_points": [],
            "drop_risks": [],
            "expectations": [],
            "live_diagnostics": {},
        }
    ])

    aggregate = service._aggregate_feedback(
        analysis=None,
        reviewers=reviewers,
        readers=readers,
        min_score=7.8,
        source_pattern_pack={
            "workflow_patterns": [{"name": "novelwriter_live_manuscript_analytics_gate"}],
        },
    )

    assert aggregate["decision"] == "revise"
    assert aggregate["live_diagnostics"]["required"] is True
    assert aggregate["live_diagnostics"]["blocking"] is True
    assert aggregate["live_diagnostics"]["advisory_only"] is True
    assert aggregate["live_diagnostics"]["missing_count"] > 0
    assert "event_line|open_plot_lines|story_pulse" in {
        item["field"] for item in aggregate["live_diagnostics"]["missing"]
    }
    assert "live_diagnostics_missing" in aggregate["top_issues"]


def test_aggregate_feedback_revises_when_required_hook_payoff_answers_are_missing():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    reviewers = service._normalize_reviewers([
        {
            "role": "editor",
            "overall_score": 9.0,
            "pacing_score": 9.0,
            "engagement_score": 9.0,
            "coherence_score": 9.0,
            "style_fidelity_score": 9.0,
            "verdict": "pass",
            "strengths": [],
            "issues": [],
            "style_drift_issues": [],
            "must_fix": [],
        }
    ])
    readers = service._normalize_readers([
        {
            "persona": "fresh reader",
            "immersion_score": 9.0,
            "continue_score": 9.0,
            "favorite_points": [],
            "drop_risks": [],
            "expectations": [],
            "reader_pull_answers": {
                "pov_character": "Lin",
                "current_want": "keep the witness alive",
                "obstacle": "the council isolates the witness",
                "stakes": "the archive case collapses if the witness breaks",
                "changed_state": "the public hearing turns hostile",
                "pull_forward": "who broke the archive seal?",
            },
            "hook_payoff_answers": {
                "opening_hook_type": "prior-choice consequence",
                "reader_promise": "public mystery pressure",
            },
        }
    ])

    aggregate = service._aggregate_feedback(
        analysis=None,
        reviewers=reviewers,
        readers=readers,
        min_score=7.8,
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "premise_structure_hook_payoff_gate"},
                {"name": "opening_ending_hook_integrity_gate"},
            ],
        },
    )

    assert aggregate["decision"] == "revise"
    assert aggregate["hook_payoff"]["required"] is True
    assert aggregate["hook_payoff"]["blocking"] is True
    assert aggregate["hook_payoff"]["missing_count"] > 0
    assert {"ending_hook_job", "micro_payoff", "required_payoff"} <= {
        item["field"] for item in aggregate["hook_payoff"]["missing"]
    }
    assert "hook_payoff_missing" in aggregate["top_issues"]


def test_aggregate_feedback_revises_when_required_chapter_contract_scene_beats_are_missing():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    reviewers = service._normalize_reviewers([
        {
            "role": "editor",
            "overall_score": 9.0,
            "pacing_score": 9.0,
            "engagement_score": 9.0,
            "coherence_score": 9.0,
            "style_fidelity_score": 9.0,
            "verdict": "pass",
            "strengths": [],
            "issues": [],
            "style_drift_issues": [],
            "must_fix": [],
        }
    ])
    readers = service._normalize_readers([
        {
            "persona": "fresh reader",
            "immersion_score": 9.0,
            "continue_score": 9.0,
            "favorite_points": [],
            "drop_risks": [],
            "expectations": [],
            "chapter_contract_answers": {
                "chapter_goal": "force the witness to speak",
                "opening_hook": "the witness arrives under guard",
                "main_obstacle": "the council controls the hearing",
            },
            "scene_beats": [
                {
                    "goal": "open the sealed file",
                    "obstacle": "the clerk refuses",
                    "outcome": "Lin gains partial access",
                    "exit_state": "the room turns hostile",
                }
            ],
        }
    ])

    aggregate = service._aggregate_feedback(
        analysis=None,
        reviewers=reviewers,
        readers=readers,
        min_score=7.8,
        source_pattern_pack={
            "workflow_patterns": [{"name": "chapter_contract_scene_beat_gate"}],
        },
    )

    assert aggregate["decision"] == "revise"
    assert aggregate["chapter_contract"]["required"] is True
    assert aggregate["chapter_contract"]["blocking"] is True
    assert aggregate["chapter_contract"]["missing_count"] > 0
    assert {
        "turning_point",
        "emotional_shift",
        "revealed_information",
        "payoff",
        "ending_hook",
        "continuity_changes",
        "scene_beats[3-7]",
    } <= {item["field"] for item in aggregate["chapter_contract"]["missing"]}
    assert "chapter_contract_scene_beat_missing" in aggregate["top_issues"]


def test_aggregate_feedback_revises_when_required_post_draft_review_evidence_is_missing():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    reviewers = service._normalize_reviewers([
        {
            "role": "editor",
            "overall_score": 9.0,
            "pacing_score": 9.0,
            "engagement_score": 9.0,
            "coherence_score": 9.0,
            "style_fidelity_score": 9.0,
            "verdict": "pass",
            "strengths": [],
            "issues": [],
            "style_drift_issues": [],
            "must_fix": [],
        }
    ])
    readers = service._normalize_readers([
        {
            "persona": "fresh reader",
            "immersion_score": 9.0,
            "continue_score": 9.0,
            "favorite_points": [],
            "drop_risks": [],
            "expectations": [],
        }
    ])

    aggregate = service._aggregate_feedback(
        analysis=None,
        reviewers=reviewers,
        readers=readers,
        min_score=7.8,
        source_pattern_pack={
            "workflow_patterns": [{"name": "post_draft_review_checklist_gate"}],
        },
    )

    assert aggregate["decision"] == "revise"
    assert aggregate["post_draft_review"]["required"] is True
    assert aggregate["post_draft_review"]["blocking"] is True
    assert {
        "post_draft_review_packet",
        "mobile_readability_review",
        "least_destructive_repair_scope",
    } <= {item["field"] for item in aggregate["post_draft_review"]["missing"]}
    assert "post_draft_review_missing" in aggregate["top_issues"]


def test_build_revision_brief_includes_reader_pull_repair_requirements():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-reader-pull-repair",
        project_id="project-reader-pull-repair",
        chapter_number=8,
        title="Missing Pull",
        content="A fluent chapter that does not clarify why the reader should continue.",
        word_count=76,
        status="completed",
    )
    aggregate = {
        "high_risk_issues": [],
        "top_issues": ["reader_pull_missing"],
        "reader_risks": [],
        "style_drift_issues": [],
        "reader_pull": {
            "required": True,
            "blocking": True,
            "missing_count": 2,
            "missing": [
                {"persona": "fresh reader", "field": "stakes"},
                {"persona": "fresh reader", "field": "pull_forward"},
            ],
        },
    }

    brief = service._build_revision_brief(
        chapter=chapter,
        analysis=None,
        aggregate=aggregate,
    )

    assert "Reader-pull repair" in brief
    assert "POV" in brief
    assert "stakes" in brief
    assert "pull-forward" in brief


def test_build_revision_brief_includes_post_draft_review_repair_requirements():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-post-draft-review-repair",
        project_id="project-post-draft-review-repair",
        chapter_number=12,
        title="Missing Review Packet",
        content="A fluent chapter that has not proven it passed the acceptance review.",
        word_count=84,
        status="completed",
    )
    aggregate = {
        "high_risk_issues": [],
        "top_issues": ["post_draft_review_missing"],
        "reader_risks": [],
        "style_drift_issues": [],
        "post_draft_review": {
            "required": True,
            "blocking": True,
            "missing_count": 2,
            "missing": [
                {"persona": "fresh reader", "field": "mobile_readability_review"},
                {"persona": "fresh reader", "field": "least_destructive_repair_scope"},
            ],
        },
    }

    brief = service._build_revision_brief(
        chapter=chapter,
        analysis=None,
        aggregate=aggregate,
    )

    assert "Post-draft review repair" in brief
    assert "structure, continuity, POV, voice, conflict, pacing" in brief
    assert "mobile readability" in brief
    assert "least destructive repair" in brief


def test_build_revision_brief_includes_live_diagnostics_repair_requirements():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-live-diagnostics-repair",
        project_id="project-live-diagnostics-repair",
        chapter_number=10,
        title="Missing Diagnostics",
        content="A fluent chapter with no visible event line or story pulse.",
        word_count=69,
        status="completed",
    )
    aggregate = {
        "high_risk_issues": [],
        "top_issues": ["live_diagnostics_missing"],
        "reader_risks": [],
        "style_drift_issues": [],
        "live_diagnostics": {
            "required": True,
            "blocking": True,
            "missing_count": 1,
            "missing": [
                {"persona": "fresh reader", "field": "event_line|open_plot_lines|story_pulse"},
            ],
        },
    }

    brief = service._build_revision_brief(
        chapter=chapter,
        analysis=None,
        aggregate=aggregate,
    )

    assert "Live-diagnostics repair" in brief
    assert "Event Line" in brief
    assert "open plot lines" in brief
    assert "Story Pulse" in brief
    assert "advisory diagnostics" in brief
    assert "accepted canon" in brief


def test_build_revision_brief_includes_hook_payoff_repair_requirements():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-hook-payoff-repair",
        project_id="project-hook-payoff-repair",
        chapter_number=11,
        title="Missing Payoff",
        content="A fluent chapter with no earned ending hook or payoff.",
        word_count=81,
        status="completed",
    )
    aggregate = {
        "high_risk_issues": [],
        "top_issues": ["hook_payoff_missing"],
        "reader_risks": [],
        "style_drift_issues": [],
        "hook_payoff": {
            "required": True,
            "blocking": True,
            "missing_count": 3,
            "missing": [
                {"persona": "fresh reader", "field": "ending_hook_job"},
                {"persona": "fresh reader", "field": "micro_payoff"},
                {"persona": "fresh reader", "field": "required_payoff"},
            ],
        },
    }

    brief = service._build_revision_brief(
        chapter=chapter,
        analysis=None,
        aggregate=aggregate,
    )

    assert "Hook/payoff repair" in brief
    assert "opening hook" in brief
    assert "reader promise" in brief
    assert "ending hook job" in brief
    assert "micro payoff" in brief
    assert "required payoff" in brief


def test_build_revision_brief_includes_chapter_contract_scene_beat_repair_requirements():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-contract-scene-beat-repair",
        project_id="project-contract-scene-beat-repair",
        chapter_number=17,
        title="Missing Scene Contract",
        content="A fluent chapter whose scenes do not expose goals, costs, or exit states.",
        word_count=93,
        status="completed",
    )
    aggregate = {
        "high_risk_issues": [],
        "top_issues": ["chapter_contract_scene_beat_missing"],
        "reader_risks": [],
        "style_drift_issues": [],
        "chapter_contract": {
            "required": True,
            "blocking": True,
            "missing_count": 3,
            "missing": [
                {"persona": "fresh reader", "field": "turning_point"},
                {"persona": "fresh reader", "field": "scene_beats[3-7]"},
                {"persona": "fresh reader", "field": "scene_beats[1].exit_state"},
            ],
        },
    }

    brief = service._build_revision_brief(
        chapter=chapter,
        analysis=None,
        aggregate=aggregate,
    )

    assert "Chapter contract / scene-beat repair" in brief
    assert "chapter goal" in brief
    assert "main obstacle" in brief
    assert "turning point" in brief
    assert "3-7 visible scene beats" in brief
    assert "exit state" in brief


@pytest.mark.asyncio
async def test_mark_existing_analysis_stale_after_auto_regeneration_updates_result_and_record():
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-analysis-stale",
        project_id="project-analysis-stale",
        chapter_number=8,
        title="Archive Rewrite",
        content="New regenerated archive witness scene.",
        word_count=37,
        status="completed",
    )

    class ExistingAnalysis:
        id = "analysis-old"
        analysis_report = "Old ledger recovery analysis."
        suggestions = ["旧正文分析建议"]
        overall_quality_score = 5.0
        pacing_score = 5.0
        engagement_score = 5.0
        coherence_score = 5.0
        plot_points = [{"content": "Old repeated ledger recovery"}]
        foreshadows = [{"content": "Old clue"}]
        character_states = [{"character_name": "Lin", "state_after": "old"}]

    class WorkflowRecord:
        aggregate = {"regeneration": {"applied": True}}

    existing_analysis = ExistingAnalysis()
    workflow_record = WorkflowRecord()

    stale_meta = await service._mark_analysis_stale_after_auto_regeneration(
        chapter=chapter,
        analysis=existing_analysis,  # type: ignore[arg-type]
        workflow_record=workflow_record,  # type: ignore[arg-type]
        regeneration_meta={"applied": True, "task_id": "regen-8"},
    )

    assert stale_meta == {
        "stale": True,
        "analysis_id": "analysis-old",
        "reason": "workflow_auto_regeneration_updated_chapter_content",
        "reanalysis_required": True,
    }
    assert existing_analysis.analysis_report == (
        "Stale after workflow auto regeneration; reanalysis required for updated chapter content."
    )
    assert existing_analysis.suggestions == [
        "Chapter content was auto-regenerated after this analysis. Re-run chapter analysis before using this PlotAnalysis as final continuity evidence."
    ]
    assert existing_analysis.overall_quality_score == 0
    assert existing_analysis.pacing_score == 0
    assert existing_analysis.engagement_score == 0
    assert existing_analysis.coherence_score == 0
    assert existing_analysis.plot_points == []
    assert existing_analysis.foreshadows == []
    assert existing_analysis.character_states == []
    assert workflow_record.aggregate["analysis_stale"] == stale_meta


@pytest.mark.asyncio
async def test_review_panel_prompt_includes_source_pattern_pack_self_review_hints():
    ai_service = StubAIService()
    service = NovelWorkflowService(ai_service)  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-source-hints",
        project_id="project-1",
        chapter_number=3,
        title="第三章",
        content="林在档案馆门口停住，意识到旧组织仍在暗处观察他。",
        summary="林发现组织线索。",
        word_count=26,
        status="completed",
    )
    source_pattern_pack = {
        "workflow_patterns": [{"name": "self_review", "candidate_count": 2}],
        "self_review_policy_hints": [
            "自评必须检查同类创作是否同时满足去重和风格保真。",
            "每轮自评优先修复设定冲突、人物跑偏和承接断裂。",
        ],
        "continuation_prompt_hints": ["续写评审要检查上一章状态是否被继承。"],
        "safety_constraints": ["只吸收公开来源模式，不导入外部代码。"],
    }

    await service._run_review_panel(
        chapter=chapter,
        analysis=None,
        source_pattern_pack=source_pattern_pack,
    )

    prompt = ai_service.prompts[0]
    assert "Public source pattern constraints" in prompt
    assert "self_review_policy_hints" in prompt
    assert "去重和风格保真" in prompt
    assert "承接断裂" in prompt
    assert "只吸收公开来源模式" in prompt


@pytest.mark.asyncio
async def test_run_chapter_workflow_resolves_fresh_pattern_pack_for_review_panel(monkeypatch):
    resolve_calls: list[dict] = []

    async def fake_resolve(**kwargs):
        resolve_calls.append(kwargs)
        return {"self_review_policy_hints": ["fresh workflow review hint"]}

    monkeypatch.setattr(
        novel_workflow_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve,
    )

    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-fresh-pattern",
        project_id="project-1",
        chapter_number=2,
        title="Second",
        content="The protagonist follows the previous chapter state instead of resetting.",
        word_count=72,
        status="completed",
    )
    captured_pattern_packs: list[dict] = []

    async def fake_review_panel(chapter, analysis, **kwargs):
        captured_pattern_packs.append(kwargs["source_pattern_pack"])
        return [
            {
                "role": "editor",
                "overall_score": 9.0,
                "pacing_score": 9.0,
                "engagement_score": 9.0,
                "coherence_score": 9.0,
                "verdict": "pass",
                "strengths": [],
                "issues": [],
                "must_fix": [],
            }
        ]

    async def fake_reader_panel(chapter, analysis):
        return [
            {
                "persona": "reader",
                "immersion_score": 9.0,
                "continue_score": 9.0,
                "favorite_points": [],
                "drop_risks": [],
                "expectations": [],
            }
        ]

    monkeypatch.setattr(service, "_run_review_panel", fake_review_panel)
    monkeypatch.setattr(service, "_run_reader_panel", fake_reader_panel)

    class StubDB:
        def __init__(self) -> None:
            self.records = []

        def add(self, record) -> None:
            self.records.append(record)

        async def commit(self) -> None:
            return None

        async def refresh(self, record) -> None:
            if not getattr(record, "id", None):
                record.id = "workflow-result-fresh-pattern"

    result = await service.run_chapter_workflow(
        db=StubDB(),  # type: ignore[arg-type]
        chapter=chapter,
        user_id="user-1",
        max_rounds=1,
        min_score=7.8,
        auto_regenerate=False,
    )

    assert result["decision"] == "pass"
    assert resolve_calls
    assert resolve_calls[0]["repo_root"] == novel_workflow_module.PROJECT_ROOT
    assert resolve_calls[0]["force"] is False
    assert captured_pattern_packs == [{"self_review_policy_hints": ["fresh workflow review hint"]}]


@pytest.mark.asyncio
async def test_run_chapter_workflow_uses_unlimited_policy_without_infinite_loop(monkeypatch):
    async def fake_resolve(**kwargs):
        return {}

    monkeypatch.setattr(
        novel_workflow_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve,
    )
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-1",
        project_id="project-1",
        chapter_number=1,
        title="第一章",
        content="林推开门，确认账册已经被人调包。",
        word_count=18,
        status="completed",
    )
    rounds: list[int] = []

    async def fake_review_panel(chapter, analysis, **kwargs):
        return [
            {
                "role": "剧情总编",
                "overall_score": 9.0,
                "pacing_score": 9.0,
                "engagement_score": 9.0,
                "coherence_score": 9.0,
                "verdict": "pass",
                "strengths": [],
                "issues": [],
                "must_fix": [],
            }
        ]

    async def fake_reader_panel(chapter, analysis):
        rounds.append(len(rounds) + 1)
        return [
            {
                "persona": "追更读者",
                "immersion_score": 9.0,
                "continue_score": 9.0,
                "favorite_points": [],
                "drop_risks": [],
                "expectations": [],
            }
        ]

    monkeypatch.setattr(service, "_run_review_panel", fake_review_panel)
    monkeypatch.setattr(service, "_run_reader_panel", fake_reader_panel)

    class StubDB:
        def __init__(self) -> None:
            self.records = []

        def add(self, record) -> None:
            self.records.append(record)

        async def commit(self) -> None:
            return None

        async def refresh(self, record) -> None:
            if not getattr(record, "id", None):
                record.id = "workflow-result-1"

    result = await service.run_chapter_workflow(
        db=StubDB(),  # type: ignore[arg-type]
        chapter=chapter,
        user_id="user-1",
        max_rounds=0,
        min_score=7.8,
        auto_regenerate=True,
    )

    assert rounds == [1]
    assert result["decision"] == "pass"
    assert result["round_policy"]["unlimited_requested"] is True
    assert result["round_policy"]["effective_max_rounds"] == 12



@pytest.mark.asyncio
async def test_run_chapter_workflow_commits_auto_regeneration_to_remix_continuation_state(monkeypatch):
    async def fake_resolve(**kwargs):
        return {}

    monkeypatch.setattr(
        novel_workflow_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve,
    )
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-workflow-remix-sync",
        project_id="project-remix-sync",
        chapter_number=20,
        title="Archive Aftermath",
        content="Inspector Lin repeats the ledger recovery instead of moving forward.",
        summary="Repeated ledger recovery.",
        word_count=64,
        status="completed",
    )
    review_rounds = {"count": 0}

    async def fake_review_panel(chapter, analysis, **kwargs):
        review_rounds["count"] += 1
        score = 5.0 if review_rounds["count"] == 1 else 9.0
        verdict = "revise" if review_rounds["count"] == 1 else "pass"
        issues = [
            {
                "severity": "high",
                "title": "repeated canon",
                "detail": "ledger recovery is replayed",
                "advice": "move to the archive witness",
            }
        ] if verdict == "revise" else []
        return [
            {
                "role": "????",
                "overall_score": score,
                "pacing_score": score,
                "engagement_score": score,
                "coherence_score": score,
                "verdict": verdict,
                "strengths": [],
                "issues": issues,
                "must_fix": [],
            }
        ]

    async def fake_reader_panel(chapter, analysis):
        score = 5.0 if review_rounds["count"] == 1 else 9.0
        return [
            {
                "persona": "????",
                "immersion_score": score,
                "continue_score": score,
                "favorite_points": [],
                "drop_risks": ["???????"] if score < 8 else [],
                "expectations": [],
            }
        ]

    async def fake_auto_regenerate_chapter(**kwargs):
        regenerated = "Inspector Lin questions the archive witness and keeps the recovered ledger as past canon."
        kwargs["chapter"].content = regenerated
        kwargs["chapter"].summary = regenerated
        kwargs["chapter"].word_count = len(regenerated)
        return {
            "applied": True,
            "task_id": "regen-workflow-20",
            "word_count": len(regenerated),
            "style_id": None,
        }

    commit_calls: list[dict] = []

    async def fake_commit_generated_chapter(**kwargs):
        commit_calls.append(kwargs)
        return {"changed": True, "reason": "committed", "changed_sections": ["chapter_change_packages"]}

    monkeypatch.setattr(service, "_run_review_panel", fake_review_panel)
    monkeypatch.setattr(service, "_run_reader_panel", fake_reader_panel)
    monkeypatch.setattr(service, "_auto_regenerate_chapter", fake_auto_regenerate_chapter)
    monkeypatch.setattr(
        novel_workflow_module.book_remix_continuation_state_service,
        "commit_generated_chapter",
        fake_commit_generated_chapter,
    )

    class StubDB:
        def __init__(self) -> None:
            self.records = []

        def add(self, record) -> None:
            self.records.append(record)

        async def commit(self) -> None:
            return None

        async def refresh(self, record) -> None:
            if not getattr(record, "id", None):
                record.id = f"workflow-result-{len(self.records)}"

    result = await service.run_chapter_workflow(
        db=StubDB(),  # type: ignore[arg-type]
        chapter=chapter,
        user_id="user-1",
        max_rounds=2,
        min_score=8.0,
        auto_regenerate=True,
    )

    assert result["decision"] == "pass"
    assert result["applied_regeneration"] is True
    assert result["chapter_updated"] is True
    assert len(commit_calls) == 1
    assert commit_calls[0]["project_id"] == "project-remix-sync"
    assert commit_calls[0]["chapter_id"] == "chapter-workflow-remix-sync"
    assert commit_calls[0]["chapter_number"] == 20
    assert commit_calls[0]["chapter_title"] == "Archive Aftermath"
    assert "archive witness" in commit_calls[0]["chapter_content"]
    assert "repeats the ledger recovery" not in commit_calls[0]["chapter_content"]
    assert commit_calls[0]["continuation_point"] == "workflow_auto_regeneration"


@pytest.mark.asyncio
async def test_run_chapter_workflow_marks_existing_analysis_stale_after_auto_regeneration(monkeypatch):
    async def fake_resolve(**kwargs):
        return {}

    monkeypatch.setattr(
        novel_workflow_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve,
    )
    service = NovelWorkflowService(StubAIService())  # type: ignore[arg-type]
    chapter = Chapter(
        id="chapter-workflow-stale-analysis",
        project_id="project-remix-sync",
        chapter_number=21,
        title="Archive Witness",
        content="Inspector Lin repeats the ledger recovery instead of moving forward.",
        summary="Repeated ledger recovery.",
        word_count=64,
        status="completed",
    )
    analysis = PlotAnalysis(
        id="analysis-before-regeneration",
        project_id=chapter.project_id,
        chapter_id=chapter.id,
        plot_stage="development",
        overall_quality_score=5.0,
        pacing_score=5.0,
        engagement_score=5.0,
        coherence_score=5.0,
        plot_points=[{"content": "Old repeated ledger recovery"}],
        analysis_report="Old repeated ledger recovery analysis.",
        suggestions=["旧正文需要推进"],
    )
    review_rounds = {"count": 0}

    async def fake_review_panel(chapter, analysis, **kwargs):
        review_rounds["count"] += 1
        score = 5.0 if review_rounds["count"] == 1 else 9.0
        verdict = "revise" if review_rounds["count"] == 1 else "pass"
        return [
            {
                "role": "reviewer",
                "overall_score": score,
                "pacing_score": score,
                "engagement_score": score,
                "coherence_score": score,
                "verdict": verdict,
                "strengths": [],
                "issues": [
                    {"severity": "high", "title": "old analysis conflict", "detail": "", "advice": ""}
                ] if verdict == "revise" else [],
                "must_fix": [],
            }
        ]

    async def fake_reader_panel(chapter, analysis):
        score = 5.0 if review_rounds["count"] == 1 else 9.0
        return [
            {
                "persona": "reader",
                "immersion_score": score,
                "continue_score": score,
                "favorite_points": [],
                "drop_risks": ["repeated"] if score < 8 else [],
                "expectations": [],
            }
        ]

    async def fake_auto_regenerate_chapter(**kwargs):
        regenerated = "Inspector Lin questions the archive witness and opens a new city hall lead."
        kwargs["chapter"].content = regenerated
        kwargs["chapter"].summary = regenerated
        kwargs["chapter"].word_count = len(regenerated)
        return {
            "applied": True,
            "task_id": "regen-workflow-21",
            "word_count": len(regenerated),
            "style_id": None,
        }

    async def fake_commit_generated_chapter(**kwargs):
        return {"changed": True, "reason": "committed", "changed_sections": ["chapter_change_packages"]}

    monkeypatch.setattr(service, "_run_review_panel", fake_review_panel)
    monkeypatch.setattr(service, "_run_reader_panel", fake_reader_panel)
    monkeypatch.setattr(service, "_auto_regenerate_chapter", fake_auto_regenerate_chapter)
    monkeypatch.setattr(
        novel_workflow_module.book_remix_continuation_state_service,
        "commit_generated_chapter",
        fake_commit_generated_chapter,
    )

    class StubDB:
        def __init__(self) -> None:
            self.records = []

        def add(self, record) -> None:
            self.records.append(record)

        async def commit(self) -> None:
            return None

        async def refresh(self, record) -> None:
            if not getattr(record, "id", None):
                record.id = f"workflow-result-{len(self.records)}"

    result = await service.run_chapter_workflow(
        db=StubDB(),  # type: ignore[arg-type]
        chapter=chapter,
        user_id="user-1",
        analysis=analysis,
        max_rounds=2,
        min_score=8.0,
        auto_regenerate=True,
    )

    assert result["analysis_stale"] == {
        "stale": True,
        "analysis_id": "analysis-before-regeneration",
        "reason": "workflow_auto_regeneration_updated_chapter_content",
        "reanalysis_required": True,
    }
    assert analysis.analysis_report == (
        "Stale after workflow auto regeneration; reanalysis required for updated chapter content."
    )
    assert "Re-run chapter analysis" in analysis.suggestions[0]
    assert analysis.overall_quality_score == 0
    assert analysis.plot_points == []
