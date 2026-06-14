from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan
from app.models.project import Project
from app.services.book_remix_context_service import (
    BookRemixContextService,
    build_remix_continuation_control_audit,
    build_remix_continuation_context_block,
    build_remix_continuation_progress_summary,
    build_remix_continuity_control_audit,
    build_remix_context_preview_audit,
    build_remix_inspired_context_block,
    build_remix_inspired_independence_audit,
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
    assert "Continuation production control contract" in block
    assert "writeback_rule" in block


def test_build_remix_continuation_context_block_renders_universal_novel_workflow_contract():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "universal_novel_mode_contract_gate"},
            {"name": "universal_portable_tool_policy_gate"},
            {"name": "portable_story_project_structure_gate"},
            {"name": "chapter_contract_scene_beat_gate"},
            {"name": "reader_promise_micro_payoff_gate"},
            {"name": "revision_order_natural_prose_gate"},
            {"name": "progress_report_continuity_writeback_gate"},
        ],
    }

    block = build_remix_continuation_context_block(
        project_title="Universal Continuation Desk",
        bible={
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "foreshadows": [{"hook": "Archive seal breaks", "status": "open"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 8,
                    "summary": "Lin locked the archive after the seal trembled.",
                }
            ],
        },
        plan={"beats": [{"beat": "Open with the seal consequence", "status": "pending"}]},
        source_pattern_pack=pattern_pack,
    )

    assert "Universal novel workflow contract:" in block
    assert "mode_selection" in block
    assert "portable_tool_policy" in block
    assert "portable_state_files" in block
    assert "chapter_contract" in block
    assert "scene_exit_state" in block
    assert "reader_micro_payoff" in block
    assert "revision_order" in block
    assert "progress_writeback" in block


def test_universal_project_memory_gate_renders_startup_status_and_boundaries():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "portable_story_project_structure_gate", "candidate_count": 1},
        ],
        "portable_story_project_structure_gate_hints": [
            "Load story bible, outline, characters, worldbuilding, continuity, progress, and last chapters only.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Universal Project Memory Desk",
        bible={
            "world_rules": {"archive_seal": "Breaking the seal costs public trust."},
            "character_cards": [
                {
                    "name": "Lin",
                    "external_want": "protect the archive",
                    "internal_need": "trust allies",
                    "wound": "failed public testimony",
                    "voice_fingerprint": "short guarded answers",
                }
            ],
            "timeline": [{"event": "The seal trembled", "chapter_number": 8}],
            "foreshadows": [{"hook": "Archive seal breaks", "status": "open"}],
            "hard_constraints": [{"rule": "Do not overwrite accepted chapters without a patch"}],
            "style_signature": {"reader_promise": "mystery pressure with earned payoff"},
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 8,
                    "summary": "Lin locked the archive after the seal trembled.",
                }
            ],
        },
        plan={
            "summary": "Continue from the seal consequence.",
            "beats": [{"beat": "Open with public trust damage", "status": "pending"}],
            "priority_hooks": [{"hook": "Archive seal breaks onstage", "status": "pending"}],
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Project Memory Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Use project-memory discipline only.\n"
            "forbidden source elements\n"
            "- Do not reuse source story bible, characters, or continuity ledger.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    assert "Universal project memory gate:" in continuation
    assert "project_file_manifest" in continuation
    assert "startup_status_packet" in continuation
    assert "story_bible_north_star" in continuation
    assert "character_engine_cards" in continuation
    assert "world_rule_cost_custody" in continuation
    assert "continuity_decision_ledger" in continuation
    assert "no_overwrite_boundary" in continuation
    assert "runtime_boundary" in continuation
    assert "Load story bible, outline, characters" in continuation
    assert "same_type_boundary" in inspired
    assert "source story bible, character sheets, world rules" in inspired


def test_universal_project_memory_gate_extends_control_audit_and_warnings():
    audit = build_remix_continuation_control_audit(
        bible={
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 2,
                    "summary": "Lin found a sealed room.",
                }
            ],
        },
        plan={"summary": "Continue with a minimal plan."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "portable_story_project_structure_gate"},
                {"name": "universal_portable_tool_policy_gate"},
            ],
        },
    )

    assert "portable_project_file_manifest" in audit["control_axes"]
    assert "startup_status_open_thread_scan" in audit["control_axes"]
    assert "story_bible_north_star" in audit["control_axes"]
    assert "character_want_need_wound_voice" in audit["control_axes"]
    assert "world_rule_cost_research_custody" in audit["control_axes"]
    assert "continuity_decision_log_writeback" in audit["control_axes"]
    assert "verify_project_memory_startup_packet" in audit["acceptance_steps"]
    assert "verify_story_bible_project_memory_axes" in audit["acceptance_steps"]
    assert "verify_no_overwrite_manuscript_patch_scope" in audit["acceptance_steps"]
    assert "portable_tool_surface_policy" in audit["control_axes"]
    assert "assumption_register_for_unavailable_search" in audit["control_axes"]
    assert "nonoverwrite_versioned_revision_lane" in audit["control_axes"]
    assert "verify_portable_tool_policy_scope" in audit["acceptance_steps"]
    assert "portable_project_memory_warnings" in audit["warnings"]
    assert "missing_story_bible_north_star" in audit["portable_project_memory_warnings"]
    assert "missing_character_engine_card" in audit["portable_project_memory_warnings"]
    assert "missing_world_rule_cost_custody" in audit["portable_project_memory_warnings"]


def test_universal_progressive_loading_and_author_intent_gates_render_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "progressive_context_loading_gate", "candidate_count": 1},
            {"name": "author_intent_confirmation_gate", "candidate_count": 1},
        ],
        "progressive_context_loading_gate_hints": [
            "Load only the minimum needed files and previous 1-2 chapters for the current mode.",
        ],
        "author_intent_confirmation_gate_hints": [
            "Preserve authorial intent and require confirmation before long-sequence drafting changes.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Universal Scope Authority Desk",
        bible={
            "context_scope": {
                "files": ["story-bible.md", "outline.md", "progress.md"],
                "chapter_window": "previous 1-2 chapters",
            },
            "author_intent": "Keep the mystery-romance promise and guarded close-third voice.",
            "content_limits": ["no off-screen archive unlock"],
            "human_confirmation_points": ["before replacing the next 5-chapter direction"],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 8,
                    "summary": "Lin left the archive sealed and the crowd suspicious.",
                }
            ],
        },
        plan={
            "summary": "Continue from the crowd consequence.",
            "selected_context_refs": ["progress.md", "continuity.md", "chapter-008-summary"],
            "user_direction": "Keep Lin morally cautious.",
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Scope Authority Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only the scoped context-loading and author-control workflow.\n"
            "forbidden source elements\n"
            "- Do not reuse source context files, author choices, or long-sequence decisions.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={},
        plan={},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Universal context scope and author-intent gate:" in block
        assert "progressive_context_loading_gate" in block
        assert "author_intent_confirmation_gate" in block
        assert "minimum needed files" in block
        assert "Preserve authorial intent" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired

    assert "progressive_reference_scope_selection" in audit["control_axes"]
    assert "author_intent_preservation_boundary" in audit["control_axes"]
    assert "human_confirmation_before_long_sequence" in audit["control_axes"]
    assert "verify_progressive_context_scope" in audit["acceptance_steps"]
    assert "verify_author_intent_confirmation" in audit["acceptance_steps"]
    assert "context_scope_authority_warnings" in audit["warnings"]
    assert "missing_progressive_context_scope" in audit["context_scope_authority_warnings"]
    assert "missing_author_intent_boundary" in audit["context_scope_authority_warnings"]
    assert "missing_long_sequence_confirmation_policy" in audit["context_scope_authority_warnings"]


def test_gc_writer_writeflow_workspace_and_review_gates_render_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "linked_chapter_workspace_state_gate", "candidate_count": 1},
            {"name": "tri_reviewer_context_rebuild_gate", "candidate_count": 1},
        ],
        "linked_chapter_workspace_state_gate_hints": [
            "Bind imported chapter list, extracted outlines, reference display, writing area, local output folder, and current cursor.",
        ],
        "tri_reviewer_context_rebuild_gate_hints": [
            "Run context init/rebuild, then review each chapter through writer, style, and continuity findings.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Writer Desk Continuation",
        bible={
            "chapter_change_packages": [
                {
                    "source": "imported_chapter_manifest",
                    "chapter_number": 12,
                    "summary": "The imported chapter list ends with a failed promise and a saved cursor.",
                }
            ],
        },
        plan={
            "summary": "Continue from the saved cursor and review before acceptance.",
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Writer Desk Same Type",
        style_content=(
            "same-type creation only learns the workspace and review-loop shape\n"
            "source voice is reference-only and forbidden source elements stay excluded"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={},
        plan={},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Serialized continuity audit:" in block
        assert "linked_chapter_workspace_state_gate" in block
        assert "tri_reviewer_context_rebuild_gate" in block
        assert "chapter-id bound" in block
        assert "previous/next 2 chapter window" in block

    assert "linked_imported_chapter_workspace" in audit["control_axes"]
    assert "current_writing_state_memory" in audit["control_axes"]
    assert "writer_style_continuity_review_loop" in audit["control_axes"]
    assert "context_rebuild_before_midstream_adoption" in audit["control_axes"]
    assert "verify_linked_chapter_workspace_state" in audit["acceptance_steps"]
    assert "verify_context_rebuild_from_existing_chapters" in audit["acceptance_steps"]
    assert "verify_tri_reviewer_resolution" in audit["acceptance_steps"]


def test_build_remix_continuation_context_block_projects_universal_next_chapter_scaffold():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "chapter_contract_scene_beat_gate"},
            {"name": "reader_promise_micro_payoff_gate"},
            {"name": "progress_report_continuity_writeback_gate"},
        ],
    }

    block = build_remix_continuation_context_block(
        project_title="Universal Chapter Desk",
        bible={
            "style_signature": {
                "pov": "close third",
                "word_count_target": "10000 Chinese characters",
            },
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "timeline": [{"event": "Archive seal already failed in public", "chapter_number": 8}],
            "hard_constraints": [{"rule": "Do not unlock the archive off-screen"}],
            "foreshadows": [{"hook": "Archive seal breaks", "status": "open", "setup_chapter": 8}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 8,
                    "summary": "Lin locked the archive after the seal trembled.",
                    "timeline_delta": [{"event": "The seal failed in public"}],
                    "character_state_changes": [
                        {
                            "character_name": "Lin",
                            "state_after": "alert but isolated",
                            "psychological_change": "trust in allies cracks",
                        }
                    ],
                    "foreshadow_changes": [{"hook": "Archive seal breaks", "status": "open"}],
                }
            ],
        },
        plan={
            "summary": "Continue the archive-seal consequence before widening the cast.",
            "beats": [
                {
                    "beat": "Open with the seal consequence",
                    "status": "pending",
                    "escalation": "crowd turns hostile before Lin can explain",
                }
            ],
            "priority_hooks": [{"hook": "Archive seal breaks onstage", "status": "pending"}],
            "guardrails": [{"rule": "No off-screen payoff"}],
        },
        source_pattern_pack=pattern_pack,
    )

    assert "Universal next chapter scaffold:" in block
    assert "mode: continue-chapter" in block
    assert "chapter_job: Open with the seal consequence" in block
    assert "pov: close third" in block
    assert "starting_status: Lin: alert but isolated" in block
    assert "opening_hook: Continue from Ch8" in block
    assert "reader_promise: serve visible promise/payoff debt: Archive seal breaks onstage" in block
    assert "scene_plan: 3-7 scene beats" in block
    assert "escalation: crowd turns hostile before Lin can explain" in block
    assert "new_hook: Archive seal breaks onstage" in block
    assert "character_change: Lin: trust in allies cracks" in block
    assert "continuity_facts: The seal failed in public" in block
    assert "word_count_target: 10000 Chinese characters" in block
    assert "forbidden_contradiction: No off-screen payoff" in block
    assert "writeback_after_acceptance" in block
    assert "chapter_contract_warnings" in block
    assert "missing_scene_beat_sheet" in block


def test_build_remix_continuation_control_audit_flags_universal_progress_report_gaps():
    audit = build_remix_continuation_control_audit(
        bible={
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "timeline": [{"event": "The archive seal trembled", "chapter_number": 9}],
            "style_signature": {"voice": "restrained"},
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 9,
                    "summary": "Lin kept the broken archive seal from the crowd.",
                    "timeline_delta": [{"event": "The seal failed in public"}],
                }
            ],
        },
        plan={
            "beats": [{"beat": "Make the public failure cost Lin leverage", "status": "pending"}],
            "guardrails": [{"rule": "Do not repair the seal off-screen"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "progress_report_continuity_writeback_gate"},
            ],
        },
    )

    assert "chapter_progress_report_completeness" in audit["control_axes"]
    assert "verify_progress_report_fields" in audit["acceptance_steps"]
    assert audit["chapter_progress_report_gap_count"] == 1
    assert audit["chapter_progress_report_gaps"] == [
        {
            "chapter": "Ch9",
            "missing_fields": [
                "character_changes",
                "hook_deltas",
                "continuity_updates",
                "next_chapter_focus",
                "word_count",
                "risks",
            ],
        }
    ]
    assert "chapter_progress_report_missing_fields" in audit["warnings"]


def test_build_remix_continuation_context_block_renders_universal_progress_report_gap_gate():
    block = build_remix_continuation_context_block(
        project_title="Progress Report Desk",
        bible={
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "timeline": [{"event": "The archive seal trembled", "chapter_number": 9}],
            "style_signature": {"voice": "restrained"},
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 9,
                    "summary": "Lin kept the broken archive seal from the crowd.",
                    "timeline_delta": [{"event": "The seal failed in public"}],
                }
            ],
        },
        plan={
            "beats": [{"beat": "Make the public failure cost Lin leverage", "status": "pending"}],
            "guardrails": [{"rule": "Do not repair the seal off-screen"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "progress_report_continuity_writeback_gate"},
            ],
        },
    )

    assert "Universal progress report completeness gate:" in block
    assert (
        "required_fields: summary, new_facts, character_changes, hook_deltas, "
        "continuity_updates, next_chapter_focus, word_count, risks"
    ) in block
    assert "chapter_progress_report_missing_fields: Ch9" in block
    assert "character_changes, hook_deltas, continuity_updates, next_chapter_focus, word_count, risks" in block


def test_universal_progress_report_fuses_narrative_time_age_trace_gate():
    source_pattern_pack = {
        "workflow_patterns": [
            {"name": "progress_report_continuity_writeback_gate"},
            {"name": "narrative_time_age_trace_gate"},
        ],
    }

    audit = build_remix_continuation_control_audit(
        bible={
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 10,
                    "summary": "Lin hid the seal failure until midnight.",
                    "new_facts": [{"fact": "The seal failed at midnight"}],
                    "character_state_changes": [{"character_name": "Lin", "state_after": "isolated"}],
                    "foreshadow_changes": [{"hook": "Archive seal breaks", "status": "open"}],
                    "continuity_updates": [{"field": "archive_status", "value": "unstable"}],
                    "next_chapter_focus": "Make the failure public.",
                    "word_count": 2400,
                    "risks": ["time pressure may compress too fast"],
                }
            ],
        },
        plan={"beats": [{"beat": "Expose the midnight failure", "status": "pending"}]},
        source_pattern_pack=source_pattern_pack,
    )

    assert "narrative_time_age_progress_writeback" in audit["control_axes"]
    assert "verify_narrative_time_age_writeback" in audit["acceptance_steps"]
    assert audit["chapter_progress_report_gaps"] == [
        {
            "chapter": "Ch10",
            "missing_fields": [
                "narrative_time",
                "duration",
                "weekday",
                "character_age_refs",
                "section_status",
                "export_included",
            ],
        }
    ]

    block = build_remix_continuation_context_block(
        project_title="Time Trace Progress Desk",
        bible={
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 10,
                    "summary": "Lin hid the seal failure until midnight.",
                    "word_count": 2400,
                }
            ],
        },
        plan={"beats": [{"beat": "Expose the midnight failure", "status": "pending"}]},
        source_pattern_pack=source_pattern_pack,
    )

    assert "required_time_trace_fields: narrative_time, duration, weekday" in block
    assert "mdnovel-style section time/status/export boundary" in block
    assert "chapter_progress_report_missing_fields: Ch10" in block
    assert "narrative_time, duration, weekday, character_age_refs, section_status, export_included" in block


def test_build_remix_inspired_context_block_renders_universal_same_type_scaffold():
    block = build_remix_inspired_context_block(
        project_title="Universal Inspired Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Keep compressed pressure and concrete sensory turns.\n"
            "forbidden source elements\n"
            "- Do not reuse source factions, titles, or scene order.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "universal_novel_mode_contract_gate"},
                {"name": "chapter_contract_scene_beat_gate"},
                {"name": "reader_promise_micro_payoff_gate"},
                {"name": "progress_report_continuity_writeback_gate"},
            ],
        },
    )

    assert "Universal novel workflow contract:" in block
    assert "same_type_creation_scaffold" in block
    assert "rebuild reader promise" in block
    assert "project-local continuity" in block


def test_build_remix_context_blocks_render_truth_file_write_next_state_gate():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "truth_file_write_next_state_update_gate"},
        ],
        "truth_file_write_next_state_update_gate_hints": [
            "Truth files, chapter summaries, current state, unresolved promises, and snapshot id should be read into a write-next work package before drafting.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Truth File Continuation Desk",
        bible={
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "foreshadows": [{"hook": "Archive seal breaks", "status": "open"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 8,
                    "summary": "Lin locked the archive after the seal trembled.",
                }
            ],
        },
        plan={"beats": [{"beat": "Open with the seal consequence", "status": "pending"}]},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Truth File Inspired Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Keep pressure without source facts.\n"
            "forbidden source elements\n"
            "- Do not reuse source truth-file names.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Truth-file write-next state gate:" in block
        assert "write_next_package" in block
        assert "candidate_revision_boundary" in block
        assert "state_update_authority" in block
        assert "snapshot_id" in block
        assert "truth_file_write_next_state_update_gate" in block


def test_build_remix_context_blocks_render_action_review_canonization_gate():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "confirmed_action_audit_recovery_gate"},
            {"name": "planner_writer_evaluator_editor_saga_gate"},
            {"name": "story_state_output_contract_gate"},
            {"name": "markdown_frontmatter_continuity_engine_gate"},
            {"name": "craft_scene_concrete_finding_revision_gate"},
            {"name": "anti_hallucination_strand_weave_review_gate"},
            {"name": "ai_flavor_template_shell_cleanup_gate"},
        ],
        "confirmed_action_audit_recovery_gate_hints": [
            "Completion must come from confirmed actions, artifacts, and unresolved critical finding review."
        ],
        "planner_writer_evaluator_editor_saga_gate_hints": [
            "Planner, writer, evaluator and editor findings stay separate until canon approval."
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Action Review Continuation Desk",
        bible={
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "foreshadows": [{"hook": "Archive seal breaks", "status": "open"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 8,
                    "summary": "Lin locked the archive after the seal trembled.",
                }
            ],
        },
        plan={"beats": [{"beat": "Open with the seal consequence", "status": "pending"}]},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Action Review Inspired Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Keep pressure without source facts.\n"
            "forbidden source elements\n"
            "- Do not reuse source audit labels as prose.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Action-review canonization gate:" in block
        assert "confirmed_action_audit_recovery_gate" in block
        assert "planner_writer_evaluator_editor_saga_gate" in block
        assert "story_state_output_contract_gate" in block
        assert "markdown_frontmatter_continuity_engine_gate" in block
        assert "concrete_revision_finding" in block
        assert "anti_hallucination_strand_weave" in block
        assert "ai_flavor_template_shell_cleanup_gate" in block


def test_build_remix_context_preview_audit_surfaces_story_foundry_production_handoff_gate():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "capture_distillation_production_gate"},
        ],
    }

    audit = build_remix_context_preview_audit(
        context="Remix Continuation Canon\nStory Foundry production handoff gate",
        bible={
            "style_signature": {"voice": "spare close third"},
            "world_rules": {"setting": "archive city"},
            "hard_constraints": [{"rule": "No off-screen canon promotion"}],
            "character_cards": [{"name": "Inspector Lin", "goal": "protect the archive"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 5,
                    "summary": "Lin questioned the witness and exposed a false timeline.",
                    "timeline_delta": [{"event": "False timeline exposed"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "publicly cornered"}
                    ],
                }
            ],
        },
        plan={
            "summary": "Revise the witness scene only after editor critique.",
            "beats": [{"beat": "Make the witness scene cost Lin public trust", "status": "pending"}],
            "guardrails": [{"rule": "No direct manuscript merge without editor log"}],
        },
        source_pattern_pack=pattern_pack,
    )

    assert "capture_distillation_production_stage_boundary" in audit["production_control_axes"]
    assert "scene_card_external_internal_spine" in audit["production_control_axes"]
    assert "draft_critique_fixspec_revision_chain" in audit["production_control_axes"]
    assert "archivist_canon_promotion_telemetry" in audit["production_control_axes"]
    assert "verify_story_foundry_production_handoff" in audit["production_acceptance_steps"]
    assert "production_handoff_warnings" in audit["production_warnings"]
    assert "missing_scene_card_external_internal_spine" in audit["production_handoff_warnings"]
    assert "missing_editor_critique" in audit["production_handoff_warnings"]
    assert "missing_fix_spec" in audit["production_handoff_warnings"]
    assert "missing_editor_log" in audit["production_handoff_warnings"]
    assert "missing_archivist_canon_promotion" in audit["production_handoff_warnings"]


def test_build_remix_continuation_context_block_renders_story_foundry_production_handoff_gate():
    block = build_remix_continuation_context_block(
        project_title="Story Foundry Desk",
        bible={
            "style_signature": {"voice": "spare close third"},
            "world_rules": {"setting": "archive city"},
            "hard_constraints": [{"rule": "No off-screen canon promotion"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 5,
                    "summary": "Lin questioned the witness and exposed a false timeline.",
                }
            ],
        },
        plan={"summary": "Draft only after the scene card and critique path are visible."},
        source_pattern_pack={
            "workflow_patterns": [{"name": "capture_distillation_production_gate"}],
            "capture_distillation_production_gate_hints": [
                "Story Foundry separates Capture, Distillation and Production artifacts."
            ],
        },
    )

    assert "Story Foundry production handoff gate:" in block
    assert "stage_boundary" in block
    assert "scene_card_spine" in block
    assert "production_chain" in block
    assert "archivist_promotion" in block
    assert "Story Foundry separates Capture, Distillation and Production artifacts." in block
    assert "production_handoff_warnings" in block


def test_build_remix_continuation_control_audit_tracks_resume_and_memory_gates():
    audit = build_remix_continuation_control_audit(
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Recover the ledger"}],
            "timeline": [
                {"event": "Ledger clue recovered", "source": "chapter_analysis", "chapter_number": 3}
            ],
            "foreshadows": [{"hook": "Old rival returns", "status": "open"}],
            "style_signature": {"voice": "spare"},
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 1,
                    "summary": "Inspector Lin found the first ledger clue.",
                },
                {
                    "source": "chapter_analysis",
                    "chapter_number": 3,
                    "summary": "Inspector Lin confirmed the ledger clue.",
                },
            ],
        },
        plan={
            "beats": [{"beat": "Confront the archive witness", "status": "pending"}],
            "priority_hooks": [{"hook": "Old rival returns", "status": "pending"}],
            "guardrails": [{"rule": "No false final confrontation"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "automatic_director_checkpoint_chain"},
                {"name": "inspectable_memory_workspace_gate"},
                {"name": "semantic_context_consistency_gate"},
                {"name": "multi_thread_knowledge_timeline_gate"},
            ]
        },
    )

    assert audit["latest_chapter_number"] == 3
    assert audit["chapter_gap_count"] == 1
    assert audit["chapter_gaps"] == ["2"]
    assert audit["character_card_count"] == 1
    assert audit["timeline_anchor_count"] == 1
    assert audit["pending_plan_beat_count"] == 1
    assert "director_stage_checkpoint" in audit["control_axes"]
    assert "editable_memory_bank_review" in audit["control_axes"]
    assert "semantic_context_match" in audit["control_axes"]
    assert "pov_knowledge_timeline" in audit["control_axes"]
    assert "stage_checkpoint_review" in audit["acceptance_steps"]
    assert audit["warnings"] == ["chapter_sequence_gaps"]


def test_build_remix_continuation_control_audit_tracks_action_review_gates():
    audit = build_remix_continuation_control_audit(
        bible={
            "character_cards": [{"name": "Inspector Lin", "goal": "Recover the ledger"}],
            "timeline": [
                {
                    "event": "Ledger clue recovered",
                    "source": "chapter_analysis",
                    "chapter_number": 3,
                }
            ],
            "foreshadows": [{"hook": "Old rival returns", "status": "open"}],
            "style_signature": {"voice": "spare"},
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 3,
                    "summary": "Inspector Lin confirmed the ledger clue.",
                },
            ],
        },
        plan={
            "beats": [{"beat": "Confront the archive witness", "status": "pending"}],
            "priority_hooks": [{"hook": "Old rival returns", "status": "pending"}],
            "guardrails": [{"rule": "No false final confrontation"}],
        },
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "confirmed_action_audit_recovery_gate"},
                {"name": "planner_writer_evaluator_editor_saga_gate"},
                {"name": "story_state_output_contract_gate"},
                {"name": "markdown_frontmatter_continuity_engine_gate"},
                {"name": "craft_scene_concrete_finding_revision_gate"},
                {"name": "anti_hallucination_strand_weave_review_gate"},
                {"name": "ai_flavor_template_shell_cleanup_gate"},
            ]
        },
    )

    assert "confirmed_action_artifact_evidence" in audit["control_axes"]
    assert "critical_finding_recovery" in audit["control_axes"]
    assert "role_separated_findings" in audit["control_axes"]
    assert "canon_promotion_decision" in audit["control_axes"]
    assert "structured_state_delta_contract" in audit["control_axes"]
    assert "frontmatter_continuity_metadata" in audit["control_axes"]
    assert "concrete_revision_finding" in audit["control_axes"]
    assert "strand_weave_hallucination_review" in audit["control_axes"]
    assert "template_shell_cleanup" in audit["control_axes"]
    assert "verify_action_artifacts" in audit["acceptance_steps"]
    assert "resolve_critical_findings" in audit["acceptance_steps"]
    assert "approve_or_reject_canon_promotion" in audit["acceptance_steps"]
    assert "final_craft_cleanup_scan" in audit["acceptance_steps"]


def test_build_remix_context_preview_audit_reports_sections_tokens_and_patterns():
    context = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={
            "world_rules": {"magic": "ledger entries must balance"},
            "character_cards": [{"name": "Inspector Lin", "goal": "Recover the ledger"}],
            "timeline": [{"event": "Warehouse fire", "source": "chapter_analysis", "chapter_number": 12}],
            "hard_constraints": [{"rule": "Do not flip protagonist alignment abruptly"}],
            "foreshadows": [{"hook": "Old rival returns", "status": "open"}],
            "style_signature": {"voice": "spare"},
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 12,
                    "summary": "Inspector Lin found the damaged ledger.",
                    "timeline_delta": [{"event": "Warehouse fire exposed the ledger clue"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "alert"}
                    ],
                    "foreshadow_changes": [{"hook": "Old rival returns", "status": "open"}],
                }
            ],
        },
        plan={
            "summary": "Resolve old ledger thread before expanding cast scope.",
            "beats": [{"beat": "Reconnect the dropped ledger line", "status": "pending"}],
            "guardrails": [{"rule": "No sudden new power systems"}],
        },
        source_pattern_pack={
            "workflow_patterns": [{"name": "context_pack_preview"}],
            "context_pack_preview_hints": ["Preview context pack before generation."],
        },
    )

    audit = build_remix_context_preview_audit(
        context=context,
        bible={
            "world_rules": {"magic": "ledger entries must balance"},
            "character_cards": [{"name": "Inspector Lin", "goal": "Recover the ledger"}],
            "timeline": [{"event": "Warehouse fire", "source": "chapter_analysis", "chapter_number": 12}],
            "hard_constraints": [{"rule": "Do not flip protagonist alignment abruptly"}],
            "foreshadows": [{"hook": "Old rival returns", "status": "open"}],
            "style_signature": {"voice": "spare"},
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 12,
                    "summary": "Inspector Lin found the damaged ledger.",
                    "timeline_delta": [{"event": "Warehouse fire exposed the ledger clue"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "alert"}
                    ],
                    "foreshadow_changes": [{"hook": "Old rival returns", "status": "open"}],
                }
            ],
        },
        plan={
            "summary": "Resolve old ledger thread before expanding cast scope.",
            "beats": [{"beat": "Reconnect the dropped ledger line", "status": "pending"}],
            "guardrails": [{"rule": "No sudden new power systems"}],
        },
        source_pattern_pack={
            "workflow_patterns": [{"name": "context_pack_preview"}],
            "context_pack_preview_hints": ["Preview context pack before generation."],
        },
    )

    assert audit["context_estimated_tokens"] > 0
    assert audit["context_budget_risk"] == "low"
    assert {"key": "world_rules", "summary": "1 rules"} in audit["activated_sections"]
    assert any(section["key"] == "pending_plan_beats" for section in audit["activated_sections"])
    assert "context_pack_preview" in audit["active_source_patterns"]
    assert any("Old rival returns" in question for question in audit["continuity_questions"])
    assert audit["promise_payoff_debts"][0]["label"] == "Old rival returns"
    assert any(item["kind"] == "character" for item in audit["scene_state_snapshot"])
    assert "checkpoint_resume_state" in audit["production_control_axes"]
    assert "review_continuity" in audit["production_acceptance_steps"]
    assert audit["production_warnings"] == []
    assert audit["genre_tracker_warnings"] == []
    assert audit["entity_arc_timeline_risks"] == []
    assert audit["canon_drift_risks"] == []
    assert audit["context_warnings"] == []


def test_build_remix_context_preview_audit_surfaces_production_gate_warnings():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "progress_report_continuity_writeback_gate"},
            {"name": "genre_inspiration_budget_library_gate"},
            {"name": "volume_antipattern_dependency_graph_gate"},
            {"name": "webnovel_genre_tracker_gate"},
            {"name": "entity_mention_arc_timeline_gate"},
        ],
    }
    bible = {
        "genre_promise": "serialized mystery pressure",
        "character_cards": [
            {"name": "Inspector Lin", "last_seen_chapter": 1},
            {"name": "Archivist Ren", "last_seen_chapter": 2},
        ],
        "timeline": [{"event": "Old case opened", "source": "chapter_analysis", "chapter_number": 1}],
        "style_signature": {"voice": "spare"},
        "foreshadows": [{"hook": "Missing seal", "status": "open", "setup_chapter": 1}],
        "story_arcs": [{"name": "Ledger conspiracy", "status": "open"}],
        "chapter_change_packages": [
            {
                "source": "chapter_analysis",
                "chapter_number": 1,
                "summary": "Inspector Lin found the first clue.",
                "timeline_delta": [{"event": "First clue found"}],
                "character_state_changes": [
                    {"character_name": "Inspector Lin", "state_after": "alert"}
                ],
            },
            {
                "source": "chapter_analysis",
                "chapter_number": 8,
                "summary": "The city archive stayed quiet.",
            },
        ],
    }

    audit = build_remix_context_preview_audit(
        context="Remix Continuation Canon\nRecent chapter change packages",
        bible=bible,
        plan={"summary": "Continue pressure without resolving the seal off-screen.", "guardrails": []},
        source_pattern_pack=pattern_pack,
    )

    assert "chapter_progress_report_completeness" in audit["production_control_axes"]
    assert "webnovel_genre_tracker_state" in audit["production_control_axes"]
    assert "entity_mention_timeline" in audit["production_control_axes"]
    assert "production_control_review_required" in audit["context_warnings"]
    assert "chapter_progress_report_missing_fields" in audit["production_warnings"]
    assert "webnovel_genre_tracker_warnings" in audit["production_warnings"]
    assert "entity_arc_timeline_risks" in audit["production_warnings"]
    assert audit["chapter_progress_report_gap_count"] == 2
    assert any("webnovel_chapter_sequence_gaps" in item for item in audit["genre_tracker_warnings"])
    assert "webnovel_open_hooks_without_rotation_plan" in audit["genre_tracker_warnings"]
    assert any("stale_character_absence_gap: Inspector Lin" in item for item in audit["entity_arc_timeline_risks"])
    assert any("active_arc_without_chapter_link: Ledger conspiracy" in item for item in audit["canon_drift_risks"])


def test_build_remix_context_preview_audit_surfaces_universal_gate_warning_buckets():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "portable_story_project_structure_gate"},
            {"name": "post_draft_review_checklist_gate"},
            {"name": "canonkit_local_canon_drift_context_pack_gate"},
            {"name": "five_question_intake_story_promise_gate"},
            {"name": "universal_export_clean_manuscript_gate"},
            {"name": "minimal_rollback_repair_scope_gate"},
            {"name": "progressive_context_loading_gate"},
            {"name": "author_intent_confirmation_gate"},
            {"name": "local_first_provider_boundary_authoring_gate"},
            {"name": "suggestion_card_nonoverwrite_revision_gate"},
            {"name": "book_view_import_export_manifest_gate"},
            {"name": "volume_rolling_spec_quality_gate"},
            {"name": "executor_agnostic_instruction_checkpoint_gate"},
        ],
    }

    audit = build_remix_context_preview_audit(
        context="Remix Continuation Canon\nUniversal novel workflow gates",
        bible={
            "character_cards": [{"name": "Inspector Lin"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 1,
                    "summary": "The archive clue was accepted.",
                }
            ],
        },
        plan={"summary": "Continue the archive pressure."},
        source_pattern_pack=pattern_pack,
    )

    for field in (
        "portable_project_memory_warnings",
        "post_draft_review_warnings",
        "canonkit_context_pack_warnings",
        "intake_export_rollback_warnings",
        "context_scope_authority_warnings",
        "local_first_authoring_warnings",
        "deterministic_volume_spec_warnings",
    ):
        assert field in audit
        assert isinstance(audit[field], list)
        assert audit[field], field

    assert "portable_project_memory_warnings" in audit["production_warnings"]
    assert "post_draft_review_warnings" in audit["production_warnings"]
    assert "canonkit_context_pack_warnings" in audit["production_warnings"]
    assert "intake_export_rollback_warnings" in audit["production_warnings"]
    assert "context_scope_authority_warnings" in audit["production_warnings"]
    assert "local_first_authoring_warnings" in audit["production_warnings"]
    assert "deterministic_volume_spec_warnings" in audit["production_warnings"]


def test_build_remix_context_preview_audit_surfaces_noveldna_originality_warning_buckets():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "source_novel_dna_fusion_boundary_gate"},
            {"name": "originality_guard_project_creation_gate"},
        ],
    }

    audit = build_remix_context_preview_audit(
        context="Remix Continuation Canon\nNovelDNA originality gates",
        bible={"chapter_change_packages": [{"chapter_number": 1, "summary": "Target opening accepted."}]},
        plan={"summary": "Continue through abstract fusion only."},
        source_pattern_pack=pattern_pack,
    )

    assert "source_novel_dna_fusion_warnings" in audit
    assert "originality_guard_warnings" in audit
    assert isinstance(audit["source_novel_dna_fusion_warnings"], list)
    assert isinstance(audit["originality_guard_warnings"], list)
    assert audit["source_novel_dna_fusion_warnings"]
    assert audit["originality_guard_warnings"]
    assert "source_novel_dna_fusion_warnings" in audit["production_warnings"]
    assert "originality_guard_warnings" in audit["production_warnings"]


def test_build_remix_context_preview_audit_surfaces_disassembly_checkpoint_coverage():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "chapter_progressive_disassembly_checkpoint_gate"},
        ],
    }
    bible = {
        "source_chapter_count": 5,
        "character_cards": [{"name": "Inspector Lin", "last_seen_chapter": 3}],
        "timeline": [{"event": "Source opening", "source": "chapter_analysis", "chapter_number": 1}],
        "style_signature": {"voice": "spare"},
        "chapter_change_packages": [
            {
                "source": "chapter_analysis",
                "chapter_number": 1,
                "summary": "Source chapter one was analyzed.",
                "timeline_delta": [{"event": "Case opened"}],
                "character_state_changes": [
                    {"character_name": "Inspector Lin", "state_after": "curious"}
                ],
            },
            {
                "source": "chapter_analysis",
                "chapter_number": 3,
                "summary": "Source chapter three exposed the archive.",
                "timeline_delta": [{"event": "Archive appeared"}],
                "character_state_changes": [
                    {"character_name": "Inspector Lin", "state_after": "alarmed"}
                ],
            },
        ],
    }

    audit = build_remix_context_preview_audit(
        context="Remix Continuation Canon\nRecent chapter change packages",
        bible=bible,
        plan={"summary": "Continue only from checkpointed analysis.", "guardrails": [{"rule": "cite source evidence"}]},
        source_pattern_pack=pattern_pack,
    )

    assert "source_chapter_analysis_coverage" in audit["production_control_axes"]
    assert "verify_disassembly_checkpoint_coverage" in audit["production_acceptance_steps"]
    assert "disassembly_checkpoint_warnings" in audit["production_warnings"]
    assert "production_control_review_required" in audit["context_warnings"]
    assert audit["source_analysis_coverage_percent"] == 40
    assert audit["missing_source_analysis_chapters"] == ["2", "4-5"]
    assert "source_analysis_coverage_incomplete" in audit["disassembly_checkpoint_warnings"]


def test_build_remix_context_preview_audit_surfaces_mode_contract_axis_gaps():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "mode_contract_generation_gate"},
        ],
    }

    audit = build_remix_context_preview_audit(
        context="Remix Continuation Canon\nCurrent continuation strategy",
        bible={
            "character_cards": [{"name": "Inspector Lin", "role": "detective"}],
            "hard_constraints": [{"rule": "Do not change POV"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 2,
                    "summary": "The archive clue was accepted.",
                    "timeline_delta": [{"event": "Archive clue accepted"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "suspicious"}
                    ],
                }
            ],
        },
        plan={
            "summary": "Continue from the archive clue.",
            "beats": [{"beat": "Question the witness", "status": "pending"}],
            "guardrails": [{"rule": "No sudden genre shift"}],
        },
        source_pattern_pack=pattern_pack,
    )

    assert "selected_output_mode_priority" in audit["production_control_axes"]
    assert "visible_creative_axis_contract" in audit["production_control_axes"]
    assert "verify_mode_contract_axes" in audit["production_acceptance_steps"]
    assert "mode_contract_warnings" in audit["production_warnings"]
    assert "missing_visible_axis: genre" in audit["mode_contract_warnings"]
    assert "missing_visible_axis: audience" in audit["mode_contract_warnings"]
    assert audit["mode_contract_axes"]["mode"] == "continue-chapter"
    assert audit["mode_contract_axes"]["characters"] == "present"


def test_build_remix_context_preview_audit_projects_universal_chapter_contract_gates():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "universal_novel_mode_contract_gate"},
            {"name": "chapter_contract_scene_beat_gate"},
            {"name": "reader_promise_micro_payoff_gate"},
            {"name": "revision_order_natural_prose_gate"},
        ],
    }

    audit = build_remix_context_preview_audit(
        context="Remix Continuation Canon\nUniversal novel workflow contract",
        bible={
            "genre": "serialized mystery",
            "target_reader": "mobile webnovel readers",
            "world_rules": {"setting": "archive city"},
            "style_signature": {"pov": "close third", "voice": "restrained"},
            "character_cards": [{"name": "Inspector Lin", "goal": "protect the archive"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 4,
                    "summary": "Lin kept the witness alive but learned nothing decisive.",
                }
            ],
        },
        plan={
            "summary": "Force the witness interview to create a visible cost.",
            "beats": [{"beat": "Question the witness under public pressure", "status": "pending"}],
            "guardrails": [{"rule": "No off-screen payoff"}],
        },
        source_pattern_pack=pattern_pack,
    )

    assert "selected_output_mode_priority" in audit["production_control_axes"]
    assert "chapter_contract_completeness" in audit["production_control_axes"]
    assert "reader_promise_micro_payoff_contract" in audit["production_control_axes"]
    assert "revision_order_natural_prose_review" in audit["production_control_axes"]
    assert "verify_chapter_contract_scene_beats" in audit["production_acceptance_steps"]
    assert "verify_reader_micro_payoff" in audit["production_acceptance_steps"]
    assert "verify_revision_order_before_line_polish" in audit["production_acceptance_steps"]
    assert audit["mode_contract_axes"]["mode"] == "continue-chapter"
    assert "chapter_contract_warnings" in audit["production_warnings"]
    assert "missing_scene_beat_sheet" in audit["chapter_contract_warnings"]
    assert "missing_starting_status" in audit["chapter_contract_warnings"]
    assert "missing_new_hook" in audit["chapter_contract_warnings"]
    assert "missing_character_change" in audit["chapter_contract_warnings"]
    assert "missing_continuity_facts" in audit["chapter_contract_warnings"]
    assert "missing_word_count_target" in audit["chapter_contract_warnings"]
    assert "latest_chapter_missing_micro_payoff_signal" in audit["chapter_contract_warnings"]


def test_build_remix_context_preview_audit_projects_universal_reader_pull_gate():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "reader_pull_fresh_reader_gate"},
        ],
    }

    audit = build_remix_context_preview_audit(
        context="Remix Continuation Canon\nUniversal fresh-reader pull gate",
        bible={
            "style_signature": {"voice": "restrained"},
            "character_cards": [{"name": "Inspector Lin"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 5,
                    "summary": "Lin left the hearing with a vague warning.",
                }
            ],
        },
        plan={
            "summary": "Continue the hearing aftermath.",
            "beats": [{"beat": "Lin returns to the archive", "status": "pending"}],
        },
        source_pattern_pack=pattern_pack,
    )

    assert "reader_pull_fresh_reader_test" in audit["production_control_axes"]
    assert "verify_reader_pull_answers" in audit["production_acceptance_steps"]
    assert "reader_pull_warnings" in audit["production_warnings"]
    assert "missing_pov_anchor" in audit["reader_pull_warnings"]
    assert "missing_current_want" in audit["reader_pull_warnings"]
    assert "missing_main_obstacle" in audit["reader_pull_warnings"]
    assert "missing_stakes_or_why_it_matters" in audit["reader_pull_warnings"]
    assert "missing_changed_exit_state" in audit["reader_pull_warnings"]
    assert "missing_next_reader_pull" in audit["reader_pull_warnings"]


def test_build_remix_continuation_context_block_renders_universal_reader_pull_gate():
    block = build_remix_continuation_context_block(
        project_title="Fresh Reader Desk",
        bible={
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 5,
                    "summary": "Lin left the hearing with a vague warning.",
                }
            ],
        },
        plan={"summary": "Continue the hearing aftermath."},
        source_pattern_pack={
            "workflow_patterns": [{"name": "reader_pull_fresh_reader_gate"}],
            "reader_pull_fresh_reader_gate_hints": [
                "A fresh reader must answer POV, want, block, stakes, change, and pull."
            ],
        },
    )

    assert "Universal reader-pull fresh-reader gate" in block
    assert "reader_pull_questions" in block
    assert "POV, want, obstacle, stakes" in block
    assert "A fresh reader must answer POV" in block
    assert "reader_pull_warnings" in block
    assert "missing_pov_anchor" in block
    assert "missing_next_reader_pull" in block


def test_build_remix_continuation_context_block_renders_mode_contract_generation_gate():
    block = build_remix_continuation_context_block(
        project_title="Mode Contract Desk",
        bible={
            "genre": "serialized mystery",
            "character_cards": [{"name": "Inspector Lin", "role": "detective"}],
            "world_rules": {"setting": "archive city"},
            "style_signature": {"pov": "close third", "voice": "restrained"},
            "hard_constraints": [{"rule": "No provider key or source material in prompt output"}],
        },
        plan={
            "summary": "Continue the archive clue with a costly witness scene.",
            "beats": [{"beat": "Question the witness", "status": "pending"}],
            "guardrails": [{"rule": "No sudden ending"}],
        },
        source_pattern_pack={
            "workflow_patterns": [{"name": "mode_contract_generation_gate"}],
            "mode_contract_generation_gate_hints": [
                "Selected-mode priority should beat incidental source-material wording."
            ],
        },
    )

    assert "Mode contract generation audit" in block
    assert "mode: continue-chapter" in block
    assert "visible_axes" in block
    assert "selected_mode_priority" in block
    assert "under_length_rewrite_boundary" in block
    assert "Selected-mode priority should beat incidental source-material wording." in block


def test_build_remix_continuation_context_block_renders_disassembly_checkpoint_gate():
    block = build_remix_continuation_context_block(
        project_title="Disassembly Desk",
        bible={
            "source_chapter_count": 4,
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 1,
                    "summary": "Opening source chapter was normalized.",
                    "timeline_delta": [{"event": "Opening source clue"}],
                    "character_state_changes": [
                        {"character_name": "Inspector Lin", "state_after": "alert"}
                    ],
                }
            ],
        },
        plan={"summary": "Do not write beyond accepted source-analysis coverage."},
        source_pattern_pack={
            "workflow_patterns": [{"name": "chapter_progressive_disassembly_checkpoint_gate"}],
            "chapter_progressive_disassembly_checkpoint_gate_hints": [
                "Keep chapter-progressive raw output separate from accepted analysis."
            ],
        },
    )

    assert "Chapter-progressive disassembly checkpoint audit" in block
    assert "coverage=25%" in block
    assert "missing_source_analysis_chapters: 2-4" in block
    assert "raw_output outside canon" in block
    assert "QA citation jumps" in block
    assert "Keep chapter-progressive raw output separate" in block


def test_build_remix_continuity_control_audit_projects_entity_timeline_risks():
    audit = build_remix_continuity_control_audit(
        bible={
            "character_cards": [{"name": "Mira", "last_seen_chapter": 1}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 9,
                    "summary": "A courier arrived without a card.",
                    "character_state_changes": [
                        {"character_name": "Courier Vale", "state_after": "watching"}
                    ],
                }
            ],
        },
        plan={"summary": "Continue the courier route."},
        source_pattern_pack={
            "workflow_patterns": [{"name": "entity_mention_arc_timeline_gate"}],
        },
    )

    assert any("stale_character_absence_gap: Mira" in risk for risk in audit["canon_drift_risks"])
    assert any("mentioned_entity_without_card: Courier Vale" in risk for risk in audit["canon_drift_risks"])


def test_build_remix_continuation_context_block_renders_continuity_control_section():
    block = build_remix_continuation_context_block(
        project_title="Continuity Desk",
        bible={
            "foreshadows": [{"hook": "Sealed letter returns", "status": "open", "setup_chapter": 3}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 10,
                    "summary": "The hero hid the sealed letter.",
                    "timeline_delta": [{"event": "The sealed letter changed hands"}],
                    "character_state_changes": [
                        {"character_name": "Hero", "state_after": "guarded"}
                    ],
                    "foreshadow_changes": [{"hook": "Sealed letter returns", "status": "open"}],
                }
            ],
        },
        plan={
            "beats": [{"beat": "Force a public choice", "status": "pending"}],
            "guardrails": [{"rule": "Do not resolve the letter off-screen"}],
        },
    )

    assert "Continuity questions and promise/payoff control" in block
    assert "Sealed letter returns" in block
    assert "scene_state/character" in block
    assert "Hero: guarded" in block
    assert "stale_open_hook" in block


def test_build_remix_context_blocks_render_story_bible_continuity_qa_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "markdown_skill_story_project_contract_gate", "candidate_count": 1},
            {"name": "canon_drift_continuity_qa_gate", "candidate_count": 1},
            {"name": "consequence_ledger_last_actions_context_gate", "candidate_count": 1},
            {"name": "project_isolated_story_bible_query_gate", "candidate_count": 1},
            {"name": "work_dna_method_transfer_eval_gate", "candidate_count": 1},
            {"name": "governed_full_reading_continuation_gate", "candidate_count": 1},
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Story Bible QA Desk",
        bible={"hard_constraints": [{"rule": "Only accepted facts enter canon"}]},
        plan={"summary": "Continue with visible continuity questions."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Story Bible QA",
        style_content="same-type creation source voice\nforbidden source elements\n",
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Story-bible continuity QA audit" in block
        assert "frontmatter, continuity questions, and promise/payoff labels" in block
        assert "canon_drift_continuity_qa_gate" in block
        assert "last actions, consequences, state mutation" in block
        assert "one project manifest" in block
        assert "abstract method axes" in block
        assert "coverage, finalized reading state, and evidence refs" in block


def test_canonkit_local_canon_drift_context_pack_gate_renders_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "canonkit_local_canon_drift_context_pack_gate", "candidate_count": 1},
        ],
        "canonkit_local_canon_drift_context_pack_gate_hints": [
            "Detect canon-drift across character cards, ages/years, missing entities, state conflicts, and asymmetric relationships before building a focused scene context pack.",
        ],
    }

    bible = {
        "current_year": 2020,
        "character_cards": [
            {"name": "Mira", "age": 17, "birth_year": 1990},
            {"name": "Vale", "role": "ally", "goal": "protect Mira"},
        ],
        "relationships": [
            {"from": "Mira", "to": "Vale", "type": "trusts"},
        ],
        "scenes": [
            {"name": "Atrium confrontation", "entities": ["Mira", "Ghost Ledger"]},
        ],
        "scene_state_conflicts": [
            {"scene": "Atrium confrontation", "issue": "Mira is both outside and inside the archive"},
        ],
        "chapter_change_packages": [
            {
                "source": "chapter_analysis",
                "chapter_number": 21,
                "summary": "Mira found the archive door open.",
            }
        ],
    }
    plan = {"summary": "Continue after the archive door opens."}

    continuation = build_remix_continuation_context_block(
        project_title="CanonKit Desk",
        bible=bible,
        plan=plan,
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired CanonKit Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only canon-drift detector categories.\n"
            "forbidden source elements\n"
            "- Do not reuse source character cards, scene records, or JSON context packs.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible=bible,
        plan=plan,
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "CanonKit local canon-drift context-pack gate:" in block
        assert "local_first_canon_system" in block
        assert "drift_detectors" in block
        assert "missing core character setup, age/year mismatch" in block
        assert "focused_scene_context_pack" in block
        assert "JSON import/export" in block
        assert "Detect canon-drift" in block
    assert "continuation_boundary" in continuation
    assert "canonkit_context_pack_warnings" in continuation
    assert "same_type_boundary" in inspired
    assert "target character cards, scene records" in inspired

    assert "local_first_canon_drift_check" in audit["control_axes"]
    assert "focused_scene_context_pack" in audit["control_axes"]
    assert "character_age_year_consistency" in audit["control_axes"]
    assert "missing_entity_reference_review" in audit["control_axes"]
    assert "relationship_symmetry_review" in audit["control_axes"]
    assert "scene_state_conflict_review" in audit["control_axes"]
    assert "verify_canonkit_drift_detectors" in audit["acceptance_steps"]
    assert "verify_focused_scene_context_pack" in audit["acceptance_steps"]
    assert "canonkit_context_pack_warnings" in audit["warnings"]
    assert "missing_focused_scene_context_pack" in audit["canonkit_context_pack_warnings"]
    assert "missing_core_character_setup: Mira" in audit["canonkit_context_pack_warnings"]
    assert "character_age_year_mismatch: Mira" in audit["canonkit_context_pack_warnings"]
    assert "missing_entity_reference: Ghost Ledger" in audit["canonkit_context_pack_warnings"]
    assert "asymmetric_relationship: Mira->Vale" in audit["canonkit_context_pack_warnings"]
    assert any(
        warning.startswith("scene_state_conflict: Atrium confrontation")
        for warning in audit["canonkit_context_pack_warnings"]
    )


def test_canonkit_local_canon_drift_context_pack_gate_passes_with_complete_surfaces():
    audit = build_remix_continuation_control_audit(
        bible={
            "current_year": 2020,
            "character_cards": [
                {"name": "Mira", "role": "lead", "goal": "protect the archive", "age": 30, "birth_year": 1990},
                {"name": "Vale", "role": "ally", "goal": "restore public trust"},
            ],
            "relationships": [
                {"from": "Mira", "to": "Vale", "type": "trusts"},
                {"from": "Vale", "to": "Mira", "type": "trusts"},
            ],
            "locations": [{"name": "Archive"}],
            "scenes": [{"name": "Archive confrontation", "entities": ["Mira", "Vale", "Archive"]}],
            "focused_scene_context_pack": {
                "scene": "Archive confrontation",
                "included_canon_facts": ["Mira and Vale trust each other"],
            },
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 22,
                    "summary": "Mira and Vale entered the archive together.",
                }
            ],
        },
        plan={"summary": "Continue from the accepted focused context pack."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "canonkit_local_canon_drift_context_pack_gate"},
            ],
        },
    )

    assert audit["canonkit_context_pack_warnings"] == []


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


def test_build_remix_continuation_context_block_renders_long_output_reward_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={"hard_constraints": [{"rule": "Preserve accepted canon"}]},
        plan={"summary": "Write the next long chapter without truncation."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "agentwrite_plan_write_pipeline", "candidate_count": 1},
                {"name": "long_output_length_quality_ruler", "candidate_count": 2},
                {"name": "long_context_reward_dimension_gate", "candidate_count": 1},
            ],
            "agentwrite_plan_write_pipeline_hints": [
                "Split ultra-long generation into a planning artifact and a writing artifact."
            ],
            "long_output_length_quality_ruler_hints": [
                "Track long-output quality and output length together."
            ],
            "long_context_reward_dimension_gate_hints": [
                "Evaluate long-context outputs on helpfulness, logicality, faithfulness, and completeness."
            ],
        },
    )

    assert "Long output plan-write reward audit" in block
    assert "agentwrite_plan_write_pipeline" in block
    assert "long_output_length_quality_ruler" in block
    assert "long_context_reward_dimension_gate" in block
    assert "do not average away blocking failures" in block
    assert "Track long-output quality and output length together." in block


def test_build_remix_continuation_context_block_renders_creative_benchmark_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={"hard_constraints": [{"rule": "Preserve accepted canon"}]},
        plan={"summary": "Review the next chapter against writing benchmark gates."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "instance_specific_writing_criteria_gate", "candidate_count": 1},
                {"name": "hybrid_rubric_pairwise_elo_judge", "candidate_count": 1},
                {"name": "judge_bias_mitigation_check", "candidate_count": 1},
                {"name": "human_story_metric_panel", "candidate_count": 1},
            ],
            "instance_specific_writing_criteria_gate_hints": [
                "Attach five local acceptance criteria to each chapter task."
            ],
            "hybrid_rubric_pairwise_elo_judge_hints": [
                "Use rubric scores before pairwise comparison; do not let length bias decide the winner."
            ],
            "human_story_metric_panel_hints": [
                "Track relevance, coherence, empathy, surprise, engagement, and complexity as separate reader-facing axes."
            ],
        },
    )

    assert "Creative writing benchmark audit" in block
    assert "instance_specific_writing_criteria_gate" in block
    assert "hybrid_rubric_pairwise_elo_judge" in block
    assert "judge_bias_mitigation_check" in block
    assert "human_story_metric_panel" in block
    assert "do not let length bias decide the winner" in block


def test_build_remix_continuation_context_block_renders_story_generation_pipeline_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={"hard_constraints": [{"rule": "Preserve accepted canon"}]},
        plan={"summary": "Continue with recursive revision and character voice evidence."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "hierarchical_cowriting_story_scaffold", "candidate_count": 1},
                {"name": "recursive_reprompt_revision_loop", "candidate_count": 1},
                {"name": "character_dialogue_persona_memory", "candidate_count": 1},
                {"name": "event_to_sentence_realization_trace", "candidate_count": 1},
                {"name": "entity_memory_slotfill_grounding", "candidate_count": 1},
            ],
            "hierarchical_cowriting_story_scaffold_hints": [
                "Preserve logline, character, plot, location, and dialogue layers as separate checks."
            ],
            "recursive_reprompt_revision_loop_hints": [
                "Run plan, draft, rewrite, and edit as separate evidence-backed stages."
            ],
            "character_dialogue_persona_memory_hints": [
                "Use dialogue evidence to preserve tone and personality without copying source lines."
            ],
        },
    )

    assert "Story generation pipeline audit" in block
    assert "hierarchical_cowriting_story_scaffold" in block
    assert "recursive_reprompt_revision_loop" in block
    assert "character_dialogue_persona_memory" in block
    assert "event_to_sentence_realization_trace" in block
    assert "entity_memory_slotfill_grounding" in block
    assert "without copying source lines" in block


def test_build_remix_continuation_context_block_renders_source_deconstruction_memory_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={"hard_constraints": [{"rule": "Preserve accepted canon"}]},
        plan={"summary": "Deconstruct the source then continue from accepted context."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "book_memory_bank_context_lattice", "candidate_count": 1},
                {"name": "spec_driven_fiction_scene_tasks", "candidate_count": 1},
                {"name": "toc_aware_source_deconstruction", "candidate_count": 1},
                {"name": "two_pass_context_glossary_pipeline", "candidate_count": 1},
                {"name": "inline_author_edit_markup_versioning", "candidate_count": 1},
            ],
            "book_memory_bank_context_lattice_hints": [
                "Separate source deconstruction, story structure, world/characters, style guide, active context, and progress."
            ],
            "toc_aware_source_deconstruction_hints": [
                "Preserve TOC hierarchy for source summaries without making it new canon."
            ],
            "two_pass_context_glossary_pipeline_hints": [
                "Analyze summary and terms before generation uses the cumulative glossary."
            ],
        },
    )

    assert "Source deconstruction memory audit" in block
    assert "book_memory_bank_context_lattice" in block
    assert "spec_driven_fiction_scene_tasks" in block
    assert "toc_aware_source_deconstruction" in block
    assert "two_pass_context_glossary_pipeline" in block
    assert "inline_author_edit_markup_versioning" in block
    assert "outside accepted new-story canon" in block


def test_build_remix_continuation_context_block_renders_canon_graph_retrieval_audit():
    block = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={"hard_constraints": [{"rule": "Preserve accepted canon"}]},
        plan={"summary": "Retrieve canon graph context before continuing."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "temporal_canon_context_graph", "candidate_count": 1},
                {"name": "long_term_author_preference_memory", "candidate_count": 1},
                {"name": "community_graph_source_deconstruction", "candidate_count": 1},
                {"name": "dual_level_graph_vector_retrieval", "candidate_count": 1},
                {"name": "schema_guided_graph_extraction", "candidate_count": 1},
            ],
            "temporal_canon_context_graph_hints": [
                "Store canon facts as temporal graph episodes with source chapter and provenance."
            ],
            "dual_level_graph_vector_retrieval_hints": [
                "Select continuation context with vector similarity and graph traversal."
            ],
            "schema_guided_graph_extraction_hints": [
                "Extract canon graphs with bounded node labels and relationship types."
            ],
        },
    )

    assert "Canon graph retrieval audit" in block
    assert "temporal_canon_context_graph" in block
    assert "long_term_author_preference_memory" in block
    assert "community_graph_source_deconstruction" in block
    assert "dual_level_graph_vector_retrieval" in block
    assert "schema_guided_graph_extraction" in block
    assert "validity windows" in block
    assert "local/global/hybrid mode" in block


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
    assert "Same-type independence contract" in block
    assert "required_difference_axes" in block
    assert "acceptance_rule" in block


def test_build_remix_inspired_independence_audit_tracks_style_boundaries_and_risk_gates():
    audit = build_remix_inspired_independence_audit(
        style_content=(
            "同类型创作 source voice\n"
            "【同类型创作总原则】\n"
            "- 只迁移叙事引擎、节奏曲线和信息控制。\n"
            "【源书语气样本】\n"
            "- He waited until the hallway went quiet.\n"
            "【源书显性元素禁用清单】\n"
            "- 原主角、原组织、原神器\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "work_dna_method_transfer_eval_gate"},
                {"name": "authorship_attribution_similarity_gate"},
                {"name": "story_import_pattern_revision_gate"},
                {"name": "governed_full_reading_continuation_gate"},
            ]
        },
    )

    assert audit["style_principle_count"] == 1
    assert audit["source_voice_sample_count"] == 1
    assert audit["forbidden_source_element_count"] == 1
    assert "narrative_engine" in audit["transfer_axes"]
    assert "motif_family" in audit["required_difference_axes"]
    assert "style_similarity_not_goal" in audit["copy_risk_checks"]
    assert "source_import_pass_boundary" in audit["copy_risk_checks"]
    assert "reading_evidence_not_new_story_canon" in audit["copy_risk_checks"]
    assert audit["warnings"] == []


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
    assert preview["context_estimated_tokens"] > 0
    assert preview["context_budget_risk"] in {"low", "medium", "high"}
    assert any(section["key"] == "character_cards" for section in preview["activated_sections"])
    assert isinstance(preview["active_source_patterns"], list)
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
                {"name": "narrative_time_age_trace_gate"},
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
    assert "narrative_time_age_trace_gate: verify section date/time, duration, weekday, character age, status, and unused/export boundary" in block
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


def test_build_remix_inspired_context_block_renders_copy_similarity_audit():
    block = build_remix_inspired_context_block(
        project_title="Copy Safe Inspired Desk",
        style_content=(
            "【同类型创作总原则】\n"
            "- 只保留题材压力和节奏。\n"
            "【源书语气样本】\n"
            "- 克制、短句、压住解释。\n"
            "【源书显性元素禁用清单】\n"
            "- 禁止复用源书角色名和场景原句。"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "source_text_fingerprint_gate"},
                {"name": "fuzzy_phrase_similarity_gate"},
                {"name": "diff_span_copy_review"},
            ],
            "source_text_fingerprint_gate_hints": ["Fingerprint source and draft text before accepting same-type prose."],
            "fuzzy_phrase_similarity_gate_hints": ["Use fuzzy phrase thresholds to catch paraphrased source sentences."],
            "diff_span_copy_review_hints": ["Review copied spans with semantic cleanup before acceptance."],
            "inspired_mapping_targets": ["fingerprint_baseline_remap", "fuzzy_phrase_threshold_remap", "diff_span_review_remap"],
            "inspired_copy_risk_hints": ["Reject copied spans, paraphrased phrases, and source sentence order."],
        },
    )

    assert "Copy similarity audit" in block
    assert "source_text_fingerprint_gate: compare source and draft fingerprints" in block
    assert "fuzzy_phrase_similarity_gate: apply fuzzy phrase thresholds" in block
    assert "diff_span_copy_review: inspect diff spans" in block
    assert "fingerprint_baseline_remap, fuzzy_phrase_threshold_remap, diff_span_review_remap" in block


def test_build_remix_continuation_context_block_renders_near_duplicate_semantic_dedup_audit():
    block = build_remix_continuation_context_block(
        project_title="Dedup Continuation Desk",
        bible={"chapter_change_packages": [{"chapter_number": 6, "summary": "The source route was transformed."}]},
        plan={"summary": "Continue only after source-leakage and near-duplicate checks pass."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "minhash_lsh_near_duplicate_gate"},
                {"name": "simhash_hamming_similarity_gate"},
                {"name": "semantic_duplicate_cluster_gate"},
                {"name": "embedding_similarity_independence_gate"},
                {"name": "corpus_leakage_dedup_review_gate"},
            ],
            "minhash_lsh_near_duplicate_gate_hints": ["Review high-Jaccard source shingles."],
            "semantic_duplicate_cluster_gate_hints": ["Cluster source and draft windows before acceptance."],
        },
    )

    assert "Near-duplicate and semantic dedup audit" in block
    assert "minhash_lsh_near_duplicate_gate: compare source and draft shingles" in block
    assert "simhash_hamming_similarity_gate: flag low-Hamming-distance windows" in block
    assert "semantic_duplicate_cluster_gate: cluster semantic neighbors" in block
    assert "embedding_similarity_independence_gate: require key passages" in block
    assert "corpus_leakage_dedup_review_gate: keep source corpora" in block
    assert "Review high-Jaccard source shingles." in block


def test_build_remix_inspired_context_block_renders_near_duplicate_semantic_dedup_audit():
    block = build_remix_inspired_context_block(
        project_title="Dedup Inspired Desk",
        style_content=(
            "same-type creation\n"
            "- Keep genre pressure, not source scene topology.\n"
            "source voice\n"
            "- Dense reversals, compressed dialogue.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "minhash_lsh_near_duplicate_gate"},
                {"name": "simhash_hamming_similarity_gate"},
                {"name": "semantic_duplicate_cluster_gate"},
                {"name": "embedding_similarity_independence_gate"},
                {"name": "corpus_leakage_dedup_review_gate"},
            ],
            "inspired_mapping_targets": [
                "minhash_lsh_threshold_remap",
                "simhash_hamming_threshold_remap",
                "semantic_cluster_independence_remap",
                "embedding_neighbor_independence_remap",
                "corpus_leakage_boundary_remap",
            ],
            "inspired_copy_risk_hints": ["Reject source-nearest semantic neighbors and long repeated sequences."],
        },
    )

    assert "Near-duplicate and semantic dedup audit" in block
    assert "minhash_lsh_near_duplicate_gate" in block
    assert "embedding_similarity_independence_gate" in block
    assert "Inspired transformation audit" in block
    assert "minhash_lsh_threshold_remap, simhash_hamming_threshold_remap" in block
    assert "Reject source-nearest semantic neighbors and long repeated sequences." in block


def test_build_remix_continuation_context_block_renders_text_analysis_audit():
    block = build_remix_continuation_context_block(
        project_title="Metric Continuation Desk",
        bible={"character_cards": [{"name": "Lin", "voice": "short guarded replies"}]},
        plan={"summary": "Keep the final confrontation readable and character-specific."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "character_quote_attribution_map"},
                {"name": "readability_pacing_metric_gate"},
                {"name": "lexical_diversity_voice_audit"},
                {"name": "keyphrase_motif_extraction"},
            ],
            "character_quote_attribution_map_hints": ["Map every quote to speaker and alias before voice review."],
            "readability_pacing_metric_gate_hints": ["Track readability and sentence-length curve by chapter."],
        },
    )

    assert "Text analysis audit" in block
    assert "character_quote_attribution_map: map mentions, aliases, quotes" in block
    assert "readability_pacing_metric_gate: compare sentence-length" in block
    assert "lexical_diversity_voice_audit: monitor lexical diversity" in block
    assert "keyphrase_motif_extraction: extract keyphrases" in block


def test_build_remix_inspired_context_block_renders_text_analysis_audit():
    block = build_remix_inspired_context_block(
        project_title="Metric Inspired Desk",
        style_content=(
            "same-type creation\n"
            "- Keep rhythm and sentence-length curve while rebuilding the cast.\n"
            "source voice\n"
            "- Short, compressed, restrained emotional release.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "character_quote_attribution_map"},
                {"name": "readability_pacing_metric_gate"},
                {"name": "lexical_diversity_voice_audit"},
                {"name": "keyphrase_motif_extraction"},
            ],
            "inspired_mapping_targets": [
                "quote_speaker_remap",
                "readability_curve_remap",
                "lexical_diversity_remap",
                "keyphrase_motif_remap",
            ],
            "inspired_copy_risk_hints": ["Reject copied speaker quote distribution and source motif keywords."],
        },
    )

    assert "Text analysis audit" in block
    assert "character_quote_attribution_map" in block
    assert "Inspired transformation audit" in block
    assert "quote_speaker_remap, readability_curve_remap, lexical_diversity_remap, keyphrase_motif_remap" in block


def test_build_remix_continuation_context_block_renders_segmentation_summary_topic_audit():
    block = build_remix_continuation_context_block(
        project_title="Segmentation Continuation Desk",
        bible={"chapter_change_packages": [{"chapter_number": 8, "summary": "The archive clue split into two leads."}]},
        plan={"summary": "Continue from the compressed archive lead."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "semantic_chunk_boundary_map"},
                {"name": "chapter_summary_anchor_gate"},
                {"name": "topic_drift_map"},
            ],
            "semantic_chunk_boundary_map_hints": ["Split source chapters at semantic boundaries before context packing."],
            "chapter_summary_anchor_gate_hints": ["Anchor summaries to accepted chapter ids."],
            "topic_drift_map_hints": ["Track topic drift against active arcs."],
        },
    )

    assert "Segmentation, summary, and topic audit" in block
    assert "semantic_chunk_boundary_map: split source and generated chapters" in block
    assert "chapter_summary_anchor_gate: anchor every summary" in block
    assert "topic_drift_map: map topic clusters" in block


def test_build_remix_inspired_context_block_renders_segmentation_summary_topic_audit():
    block = build_remix_inspired_context_block(
        project_title="Segmentation Inspired Desk",
        style_content=(
            "same-type creation\n"
            "- Keep chapter segmentation pressure while changing events.\n"
            "source voice\n"
            "- Dense clues, short summaries.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "semantic_chunk_boundary_map"},
                {"name": "chapter_summary_anchor_gate"},
                {"name": "topic_drift_map"},
            ],
            "inspired_mapping_targets": ["chunk_boundary_remap", "summary_anchor_remap", "topic_drift_remap"],
            "inspired_copy_risk_hints": ["Reject copied chunk order, summary anchors, or source topic sequence."],
        },
    )

    assert "Segmentation, summary, and topic audit" in block
    assert "semantic_chunk_boundary_map" in block
    assert "Inspired transformation audit" in block
    assert "chunk_boundary_remap, summary_anchor_remap, topic_drift_remap" in block


def test_build_remix_continuation_context_block_renders_eval_observability_audit():
    block = build_remix_continuation_context_block(
        project_title="Eval Continuation Desk",
        bible={"chapter_change_packages": [{"chapter_number": 9, "summary": "The archive clue was accepted."}]},
        plan={"summary": "Continue with grounded context evidence."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "context_faithfulness_eval_gate"},
                {"name": "retrieval_trace_observability_gate"},
                {"name": "prompt_regression_eval_suite"},
            ],
            "context_faithfulness_eval_gate_hints": ["Evaluate generated facts against accepted canon."],
            "retrieval_trace_observability_gate_hints": ["Store selected and omitted context traces."],
            "prompt_regression_eval_suite_hints": ["Keep golden prompt cases."],
        },
    )

    assert "Evaluation, trace, and regression audit" in block
    assert "context_faithfulness_eval_gate: score generated facts" in block
    assert "retrieval_trace_observability_gate: persist query" in block
    assert "prompt_regression_eval_suite: run golden continuation" in block


def test_build_remix_inspired_context_block_renders_eval_observability_audit():
    block = build_remix_inspired_context_block(
        project_title="Eval Inspired Desk",
        style_content=(
            "same-type creation\n"
            "- Keep source-level intensity while grounding facts in the new canon.\n"
            "source voice\n"
            "- Tight clue logic, no unsupported facts.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "context_faithfulness_eval_gate"},
                {"name": "retrieval_trace_observability_gate"},
                {"name": "prompt_regression_eval_suite"},
            ],
            "inspired_mapping_targets": ["faithfulness_eval_remap", "retrieval_trace_remap", "prompt_regression_remap"],
            "inspired_copy_risk_hints": ["Reject faithfulness scores that cite source analysis as transformed canon."],
        },
    )

    assert "Evaluation, trace, and regression audit" in block
    assert "context_faithfulness_eval_gate" in block
    assert "Inspired transformation audit" in block
    assert "faithfulness_eval_remap, retrieval_trace_remap, prompt_regression_remap" in block



def test_build_remix_continuation_context_block_renders_copyedit_prose_lint_audit():
    block = build_remix_continuation_context_block(
        project_title="Copyedit Continuation Desk",
        bible={"character_cards": [{"name": "Lin", "voice": "dry short replies"}]},
        plan={"summary": "Polish the accepted next chapter without flattening voice."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "prose_lint_style_rule_gate"},
                {"name": "grammar_spelling_copyedit_gate"},
                {"name": "copyedit_diagnostic_triage_queue"},
            ],
            "prose_lint_style_rule_gate_hints": ["Keep prose lint rules project-local."],
            "grammar_spelling_copyedit_gate_hints": ["Run grammar and spelling checks after canon review."],
            "copyedit_diagnostic_triage_queue_hints": ["Triage diagnostics before acceptance."],
        },
    )

    assert "Copyedit and prose lint audit" in block
    assert "prose_lint_style_rule_gate: apply project-local house style rules" in block
    assert "grammar_spelling_copyedit_gate: check grammar, spelling" in block
    assert "copyedit_diagnostic_triage_queue: classify diagnostics" in block
    assert "Keep prose lint rules project-local." in block


def test_build_remix_inspired_context_block_renders_copyedit_prose_lint_audit():
    block = build_remix_inspired_context_block(
        project_title="Copyedit Inspired Desk",
        style_content=(
            "same-type creation\n"
            "- Keep the clipped source rhythm but rebuild all facts.\n"
            "source voice\n"
            "- Short direct sentences with dry understatement.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "prose_lint_style_rule_gate"},
                {"name": "grammar_spelling_copyedit_gate"},
                {"name": "copyedit_diagnostic_triage_queue"},
            ],
            "inspired_mapping_targets": [
                "prose_lint_rule_remap",
                "grammar_copyedit_exception_remap",
                "copyedit_triage_policy_remap",
            ],
            "inspired_copy_risk_hints": ["Reject source-like lint-clean rewrites."],
        },
    )

    assert "Copyedit and prose lint audit" in block
    assert "prose_lint_style_rule_gate" in block
    assert "grammar_spelling_copyedit_gate" in block
    assert "copyedit_diagnostic_triage_queue" in block
    assert "Inspired transformation audit" in block
    assert "prose_lint_rule_remap, grammar_copyedit_exception_remap, copyedit_triage_policy_remap" in block



def test_build_remix_continuation_context_block_renders_chinese_text_processing_audit():
    block = build_remix_continuation_context_block(
        project_title="Chinese Continuation Desk",
        bible={"character_cards": [{"name": "??", "voice": "????"}]},
        plan={"summary": "???????????????????"},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "chinese_segmentation_keyword_gate"},
                {"name": "chinese_ner_alias_consistency_gate"},
                {"name": "chinese_text_normalization_gate"},
                {"name": "chinese_error_correction_review_gate"},
            ],
            "chinese_segmentation_keyword_gate_hints": ["Use Chinese segmentation with a project dictionary."],
            "chinese_ner_alias_consistency_gate_hints": ["Map aliases before canon write-back."],
        },
    )

    assert "Chinese text processing audit" in block
    assert "chinese_segmentation_keyword_gate: use a project dictionary" in block
    assert "chinese_ner_alias_consistency_gate: audit character" in block
    assert "chinese_text_normalization_gate: normalize Simplified/Traditional" in block
    assert "chinese_error_correction_review_gate: triage typo/correction" in block
    assert "Use Chinese segmentation with a project dictionary." in block


def test_build_remix_inspired_context_block_renders_chinese_text_processing_audit():
    block = build_remix_inspired_context_block(
        project_title="Chinese Inspired Desk",
        style_content=(
            "same-type creation\n"
            "- Keep compressed Chinese rhythm while replacing names and factions.\n"
            "source voice\n"
            "- ???????\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "chinese_segmentation_keyword_gate"},
                {"name": "chinese_ner_alias_consistency_gate"},
                {"name": "chinese_text_normalization_gate"},
                {"name": "chinese_error_correction_review_gate"},
            ],
            "inspired_mapping_targets": [
                "chinese_segmentation_dictionary_remap",
                "chinese_entity_alias_remap",
                "chinese_normalization_policy_remap",
                "chinese_correction_exception_remap",
            ],
            "inspired_copy_risk_hints": ["Reject copied Chinese names and motif compounds."],
        },
    )

    assert "Chinese text processing audit" in block
    assert "chinese_segmentation_keyword_gate" in block
    assert "chinese_ner_alias_consistency_gate" in block
    assert "Inspired transformation audit" in block
    assert "chinese_segmentation_dictionary_remap, chinese_entity_alias_remap" in block


def test_build_remix_continuation_context_block_renders_source_import_extraction_audit():
    block = build_remix_continuation_context_block(
        project_title="Source Import Continuation Desk",
        bible={"character_cards": [{"name": "Mara", "voice": "precise clipped notes"}]},
        plan={"summary": "Continue after importing a scanned source book."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "source_format_import_manifest"},
                {"name": "pdf_layout_text_extraction_gate"},
                {"name": "ocr_scanned_page_import_gate"},
                {"name": "document_partition_chapter_detection_gate"},
                {"name": "import_provenance_checksum_gate"},
            ],
            "source_format_import_manifest_hints": ["Record source format, metadata, TOC and spine."],
            "ocr_scanned_page_import_gate_hints": ["Route low-confidence OCR text to manual review."],
        },
    )

    assert "Source import extraction audit" in block
    assert "source_format_import_manifest: record source format" in block
    assert "pdf_layout_text_extraction_gate: review PDF page spans" in block
    assert "ocr_scanned_page_import_gate: route scanned-page OCR confidence gaps" in block
    assert "document_partition_chapter_detection_gate: keep typed document elements" in block
    assert "import_provenance_checksum_gate: keep original, extracted, normalized" in block
    assert "Record source format, metadata, TOC and spine." in block


def test_build_remix_inspired_context_block_renders_source_import_extraction_audit():
    block = build_remix_inspired_context_block(
        project_title="Source Import Inspired Desk",
        style_content=(
            "same-type creation\n"
            "- Study imported PDF pacing without keeping page order.\n"
            "source voice\n"
            "- Dense chapter openings with marginal notes.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "source_format_import_manifest"},
                {"name": "pdf_layout_text_extraction_gate"},
                {"name": "ocr_scanned_page_import_gate"},
                {"name": "document_partition_chapter_detection_gate"},
                {"name": "import_provenance_checksum_gate"},
            ],
            "inspired_mapping_targets": [
                "source_import_structure_remap",
                "pdf_layout_evidence_remap",
                "ocr_uncertainty_review_remap",
                "chapter_partition_structure_remap",
                "import_provenance_lineage_remap",
            ],
            "inspired_copy_risk_hints": ["Reject source TOC and OCR uncertainty leakage."],
        },
    )

    assert "Source import extraction audit" in block
    assert "source_format_import_manifest" in block
    assert "pdf_layout_text_extraction_gate" in block
    assert "ocr_scanned_page_import_gate" in block
    assert "Inspired transformation audit" in block
    assert "source_import_structure_remap, pdf_layout_evidence_remap" in block


def test_build_remix_continuation_context_block_renders_literary_event_graph_audit():
    block = build_remix_continuation_context_block(
        project_title="Event Graph Continuation Desk",
        bible={"character_cards": [{"name": "Ira", "voice": "observant"}]},
        plan={"summary": "Continue after deconstructing event and relationship arcs."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "literary_event_entity_annotation_gate"},
                {"name": "narrative_event_evolution_graph_gate"},
                {"name": "sentiment_arc_emotion_trajectory_gate"},
                {"name": "cross_context_coreference_gate"},
                {"name": "character_interaction_network_gate"},
            ],
            "literary_event_entity_annotation_gate_hints": ["Separate source-book literary entities and events."],
            "sentiment_arc_emotion_trajectory_gate_hints": ["Track emotion turning points with reasons."],
        },
    )

    assert "Literary event graph audit" in block
    assert "literary_event_entity_annotation_gate: separate source entities" in block
    assert "narrative_event_evolution_graph_gate: review temporal, causal" in block
    assert "sentiment_arc_emotion_trajectory_gate: track global and character emotion curves" in block
    assert "cross_context_coreference_gate: keep ambiguous cross-chapter/source mention clusters" in block
    assert "character_interaction_network_gate: audit interaction frequency" in block
    assert "Separate source-book literary entities and events." in block


def test_build_remix_inspired_context_block_renders_literary_event_graph_audit():
    block = build_remix_inspired_context_block(
        project_title="Event Graph Inspired Desk",
        style_content=(
            "same-type creation\n"
            "- Preserve only event pressure and emotion shape after remapping.\n"
            "source voice\n"
            "- Alternating intimacy and distrust.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "literary_event_entity_annotation_gate"},
                {"name": "narrative_event_evolution_graph_gate"},
                {"name": "sentiment_arc_emotion_trajectory_gate"},
                {"name": "cross_context_coreference_gate"},
                {"name": "character_interaction_network_gate"},
            ],
            "inspired_mapping_targets": [
                "literary_annotation_role_remap",
                "event_chain_causality_remap",
                "sentiment_arc_emotion_remap",
                "cross_context_coreference_remap",
                "character_network_relationship_remap",
            ],
            "inspired_copy_risk_hints": ["Reject source-like event graph and relationship topology."],
        },
    )

    assert "Literary event graph audit" in block
    assert "narrative_event_evolution_graph_gate" in block
    assert "character_interaction_network_gate" in block
    assert "Inspired transformation audit" in block
    assert "literary_annotation_role_remap, event_chain_causality_remap" in block



def test_build_remix_continuation_context_block_renders_stylometry_style_overfit_audit():
    block = build_remix_continuation_context_block(
        project_title="Stylometry Continuation Desk",
        bible={"character_cards": [{"name": "Mara", "voice": "spare, guarded"}]},
        plan={"summary": "Continue after source style fingerprint analysis."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "stylometric_author_fingerprint_gate"},
                {"name": "function_word_syntax_style_gate"},
                {"name": "authorship_attribution_similarity_gate"},
                {"name": "style_overfit_regression_gate"},
                {"name": "paraphrase_independence_review_gate"},
            ],
            "stylometric_author_fingerprint_gate_hints": ["Build explicit style fingerprints before same-type drafting."],
            "style_overfit_regression_gate_hints": ["Run regression after paraphrase and polish."],
        },
    )

    assert "Stylometry and style-overfit audit" in block
    assert "stylometric_author_fingerprint_gate: version explicit style fingerprints" in block
    assert "function_word_syntax_style_gate: review function words" in block
    assert "authorship_attribution_similarity_gate: treat high source-author similarity" in block
    assert "style_overfit_regression_gate: run windowed regression" in block
    assert "paraphrase_independence_review_gate: require independence evidence" in block
    assert "Build explicit style fingerprints before same-type drafting." in block


def test_build_remix_inspired_context_block_renders_stylometry_style_overfit_audit():
    block = build_remix_inspired_context_block(
        project_title="Stylometry Inspired Desk",
        style_content=(
            "same-type creation\n"
            "- Keep terse pressure but rebuild the cast and event chain.\n"
            "source voice\n"
            "- Low explanation, high implication.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "stylometric_author_fingerprint_gate"},
                {"name": "function_word_syntax_style_gate"},
                {"name": "authorship_attribution_similarity_gate"},
                {"name": "style_overfit_regression_gate"},
                {"name": "paraphrase_independence_review_gate"},
            ],
            "inspired_mapping_targets": [
                "stylometric_fingerprint_remap",
                "function_word_syntax_remap",
                "authorship_similarity_threshold_remap",
                "style_overfit_regression_remap",
                "paraphrase_independence_policy_remap",
            ],
            "inspired_copy_risk_hints": ["Reject source-author nearest-neighbor drafts."],
        },
    )

    assert "Stylometry and style-overfit audit" in block
    assert "authorship_attribution_similarity_gate" in block
    assert "paraphrase_independence_review_gate" in block
    assert "Inspired transformation audit" in block
    assert "stylometric_fingerprint_remap, function_word_syntax_remap" in block



def test_build_remix_context_blocks_render_trope_independence_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "trope_inventory_similarity_gate", "candidate_count": 1},
            {"name": "trope_graph_expectation_map", "candidate_count": 1},
            {"name": "trope_density_novelty_budget", "candidate_count": 1},
            {"name": "trope_source_boundary_review", "candidate_count": 1},
        ],
        "trope_inventory_similarity_gate_hints": ["Compare source and draft trope inventories."],
        "trope_source_boundary_review_hints": ["No live trope scraping in prompts."],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={"hard_constraints": [{"rule": "Preserve accepted canon"}]},
        plan={"summary": "Continue with independent trope handling."},
        source_pattern_pack=pattern_pack,
    )

    inspired = build_remix_inspired_context_block(
        project_title="Inspired Draft",
        style_content=(
            "same-type creation source voice\n"
            "source voice sample\n"
            "forbidden source elements\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Trope independence audit" in block
        assert "trope_inventory_similarity_gate" in block
        assert "trope_graph_expectation_map" in block
        assert "trope_density_novelty_budget" in block
        assert "trope_source_boundary_review" in block
        assert "no live scraping" in block.lower()


def test_build_remix_context_blocks_render_source_rights_provenance_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "source_license_detection_gate", "candidate_count": 1},
            {"name": "spdx_reuse_compliance_gate", "candidate_count": 1},
            {"name": "public_domain_corpus_boundary", "candidate_count": 1},
            {"name": "attribution_derivative_work_gate", "candidate_count": 1},
        ],
        "source_license_detection_gate_hints": ["Record license confidence before source text import."],
        "public_domain_corpus_boundary_hints": ["Keep public-domain source metadata separate."],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={"hard_constraints": [{"rule": "Preserve accepted canon"}]},
        plan={"summary": "Continue with source rights gates."},
        source_pattern_pack=pattern_pack,
    )

    inspired = build_remix_inspired_context_block(
        project_title="Inspired Draft",
        style_content=(
            "same-type creation source voice\n"
            "source voice sample\n"
            "forbidden source elements\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Source rights provenance audit" in block
        assert "source_license_detection_gate" in block
        assert "spdx_reuse_compliance_gate" in block
        assert "public_domain_corpus_boundary" in block
        assert "attribution_derivative_work_gate" in block
        assert "license confidence" in block.lower()
        assert "public-domain source metadata" in block.lower()


def test_build_remix_context_blocks_render_source_entity_redaction_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "source_entity_redaction_gate", "candidate_count": 1},
            {"name": "custom_entity_label_inventory", "candidate_count": 1},
            {"name": "placeholder_alias_consistency_map", "candidate_count": 1},
            {"name": "proper_noun_leakage_review", "candidate_count": 1},
        ],
        "source_entity_redaction_gate_hints": ["Redact source-specific names before same-type drafting."],
        "proper_noun_leakage_review_hints": ["Compare drafts against source blocklists."],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Continuation Desk",
        bible={"hard_constraints": [{"rule": "Preserve accepted canon"}]},
        plan={"summary": "Continue with entity redaction gates."},
        source_pattern_pack=pattern_pack,
    )

    inspired = build_remix_inspired_context_block(
        project_title="Inspired Draft",
        style_content=(
            "same-type creation source voice\n"
            "source voice sample\n"
            "forbidden source elements\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Source entity redaction audit" in block
        assert "source_entity_redaction_gate" in block
        assert "custom_entity_label_inventory" in block
        assert "placeholder_alias_consistency_map" in block
        assert "proper_noun_leakage_review" in block
        assert "source-specific names" in block.lower()
        assert "source blocklists" in block.lower()


def test_build_remix_context_blocks_render_ebook_quality_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "epub_structure_validation_gate", "candidate_count": 1},
            {"name": "ebook_accessibility_audit_gate", "candidate_count": 1},
            {"name": "front_back_matter_metadata_gate", "candidate_count": 1},
            {"name": "toc_navigation_consistency_gate", "candidate_count": 1},
        ],
        "epub_structure_validation_gate_hints": ["Validate EPUB structure before export."],
        "ebook_accessibility_audit_gate_hints": ["Audit accessibility metadata."],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Ebook Delivery Desk",
        bible={"hard_constraints": [{"rule": "Only accepted chapters can be exported"}]},
        plan={"summary": "Prepare EPUB quality gates."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Ebook",
        style_content=(
            "【同类型创作总原则】\n"
            "- same-type creation must rebuild package structure from transformed chapters.\n"
            "【源书显性元素禁用清单】\n"
            "- Do not reuse source chapter titles.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Ebook quality audit" in block
        assert "epub_structure_validation_gate" in block
        assert "ebook_accessibility_audit_gate" in block
        assert "front_back_matter_metadata_gate" in block
        assert "toc_navigation_consistency_gate" in block
        assert "OPF manifest" in block
        assert "accessibility metadata" in block
        assert "title page" in block
        assert "TOC/nav/NCX" in block



def test_build_remix_context_blocks_render_agentic_editorial_craft_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "agentic_editorial_pipeline_gate", "candidate_count": 1},
            {"name": "chapter_state_archive_ladder", "candidate_count": 1},
            {"name": "section_metadata_traceability_gate", "candidate_count": 1},
            {"name": "ai_prose_fingerprint_cluster_gate", "candidate_count": 1},
        ],
        "agentic_editorial_pipeline_gate_hints": ["Separate writing roles before accepting canon."],
        "ai_prose_fingerprint_cluster_gate_hints": ["Scan voice drift clusters."],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Editorial Workbench Desk",
        bible={"hard_constraints": [{"rule": "Accepted canon changes need review"}]},
        plan={"summary": "Continue with role handoffs, state archives, and section metadata."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Editorial Workbench",
        style_content=(
            "same-type creation source voice\n"
            "- Keep craft pressure only.\n"
            "forbidden source elements\n"
            "- Do not reuse source state snapshots.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Agentic editorial and craft workbench audit" in block
        assert "agentic_editorial_pipeline_gate" in block
        assert "chapter_state_archive_ladder" in block
        assert "section_metadata_traceability_gate" in block
        assert "ai_prose_fingerprint_cluster_gate" in block
        assert "author/reviewer acceptance" in block
        assert "permanent bible" in block
        assert "cast, location, item" in block
        assert "voice drift" in block


def test_build_remix_context_blocks_render_chinese_longform_control_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "author_candidate_canon_confirmation_gate", "candidate_count": 1},
            {"name": "progressive_spoiler_context_window_gate", "candidate_count": 1},
            {"name": "chapter_control_card_writeback_gate", "candidate_count": 1},
            {"name": "trace_replay_revision_workspace_gate", "candidate_count": 1},
            {"name": "relationship_graph_global_replace_gate", "candidate_count": 1},
        ],
        "author_candidate_canon_confirmation_gate_hints": ["Confirm candidates before canon."],
        "relationship_graph_global_replace_gate_hints": ["Preview global graph replacements."],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Chinese Longform Control Desk",
        bible={"hard_constraints": [{"rule": "Only confirmed candidates enter canon"}]},
        plan={"summary": "Continue with spoiler windows, chapter cards, trace replay, and graph review."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Control Workbench",
        style_content=(
            "same-type creation source voice\n"
            "- Use craft gates only.\n"
            "forbidden source elements\n"
            "- Do not reuse source relationship graph.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Chinese long-form control audit" in block
        assert "author_candidate_canon_confirmation_gate" in block
        assert "progressive_spoiler_context_window_gate" in block
        assert "chapter_control_card_writeback_gate" in block
        assert "trace_replay_revision_workspace_gate" in block
        assert "relationship_graph_global_replace_gate" in block
        assert "preview, confirm, and apply" in block
        assert "block premature spoiler leakage" in block
        assert "chapter control card" in block
        assert "downstream impact scope" in block
        assert "preview global replacements" in block


def test_build_remix_context_blocks_render_bookrun_skill_protocol_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "bookrun_audit_trail_gate", "candidate_count": 1},
            {"name": "provider_budget_smoke_gate", "candidate_count": 1},
            {"name": "sidecar_memory_profile_boundary", "candidate_count": 1},
            {"name": "outline_checkpoint_milestone_gate", "candidate_count": 1},
            {"name": "language_localization_style_profile_gate", "candidate_count": 1},
            {"name": "progressive_disclosure_skill_protocol_gate", "candidate_count": 1},
            {"name": "anti_slop_rulepack_triage_gate", "candidate_count": 1},
        ],
        "bookrun_audit_trail_gate_hints": ["Keep BookRun export audit artifacts replayable."],
        "anti_slop_rulepack_triage_gate_hints": ["Triage banned vocabulary as review tasks."],
    }

    continuation = build_remix_continuation_context_block(
        project_title="BookRun Skill Protocol Desk",
        bible={"hard_constraints": [{"rule": "Accepted chapters need replayable evidence"}]},
        plan={"summary": "Continue with BookRun, provider, sidecar, outline, style, protocol, and prose gates."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired BookRun Workbench",
        style_content=(
            "same-type creation source voice\n"
            "- Use workflow gates only.\n"
            "forbidden source elements\n"
            "- Do not reuse source memory namespaces.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "BookRun and skill protocol audit" in block
        assert "bookrun_audit_trail_gate" in block
        assert "provider_budget_smoke_gate" in block
        assert "sidecar_memory_profile_boundary" in block
        assert "outline_checkpoint_milestone_gate" in block
        assert "language_localization_style_profile_gate" in block
        assert "progressive_disclosure_skill_protocol_gate" in block
        assert "anti_slop_rulepack_triage_gate" in block
        assert "export audit manifest" in block
        assert "token/time/cost budget" in block
        assert "graph/vector memory" in block
        assert "Story Bible version" in block
        assert "localized speaker register" in block
        assert "needed protocols" in block
        assert "banned vocabulary" in block


def test_build_remix_context_blocks_render_speckit_fiction_scene_task_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "story_bible_constitution_source_gate", "candidate_count": 1},
            {"name": "scene_outline_approval_status_gate", "candidate_count": 1},
            {"name": "pov_information_asymmetry_schedule_gate", "candidate_count": 1},
            {"name": "pacing_arc_polish_pass_gate", "candidate_count": 1},
        ],
        "scene_outline_approval_status_gate_hints": ["Draft only scene outlines marked APPROVED."],
        "pacing_arc_polish_pass_gate_hints": ["Run tension scoring before polish."],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Spec Kit Fiction Desk",
        bible={
            "style_signature": {"pov": "close third"},
            "hard_constraints": [{"rule": "constitution controls voice"}],
        },
        plan={
            "summary": "Continue through approved scene outlines.",
            "scene_beats": [
                {
                    "status": "APPROVED",
                    "required_context": ["characters.md", "timeline.md"],
                    "opening_hook": "The witness refuses the obvious answer.",
                    "goal": "Force a contradiction into view.",
                    "exit_state": "New suspicion redirects the case.",
                }
            ],
            "pov_schedule": [{"chapter": "next", "pov": "Inspector Lin", "knows": "ledger location"}],
            "information_asymmetry": [{"secret": "ledger owner", "reader_knows": "partial"}],
            "guardrails": [{"rule": "polish after checklist pass"}],
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Spec Kit Workbench",
        style_content=(
            "same-type creation source voice\n"
            "- Keep only spec-driven scene task gates.\n"
            "forbidden source elements\n"
            "- Do not reuse source scene ids or POV schedule.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Spec Kit fiction scene-task audit" in block
        assert "story_bible_constitution_source_gate" in block
        assert "scene_outline_approval_status_gate" in block
        assert "pov_information_asymmetry_schedule_gate" in block
        assert "pacing_arc_polish_pass_gate" in block
        assert "constitution" in block
        assert "APPROVED" in block
        assert "information asymmetry" in block
        assert "checklist PASS" in block


def test_build_remix_continuation_control_audit_surfaces_speckit_scene_task_warnings():
    audit = build_remix_continuation_control_audit(
        bible={
            "chapter_change_packages": [
                {
                    "chapter_number": 1,
                    "summary": "The case opens.",
                    "pov": "Inspector Lin",
                    "quality_scores": {"checklist": "FAIL"},
                }
            ],
        },
        plan={"summary": "Draft from scene outlines.", "beats": [{"beat": "question witness"}]},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "story_bible_constitution_source_gate"},
                {"name": "scene_outline_approval_status_gate"},
                {"name": "pov_information_asymmetry_schedule_gate"},
                {"name": "pacing_arc_polish_pass_gate"},
            ],
        },
    )

    assert "story_bible_constitution_authority" in audit["control_axes"]
    assert "scene_outline_approval_status" in audit["control_axes"]
    assert "pov_information_asymmetry_schedule" in audit["control_axes"]
    assert "pacing_arc_polish_pass" in audit["control_axes"]
    assert "verify_scene_outline_approval" in audit["acceptance_steps"]
    assert "verify_pov_information_asymmetry" in audit["acceptance_steps"]
    assert "verify_checklist_pass_before_polish" in audit["acceptance_steps"]
    assert "spec_kit_fiction_warnings" in audit["warnings"]
    assert "missing_story_bible_constitution" in audit["spec_kit_fiction_warnings"]
    assert "missing_approved_scene_outline" in audit["spec_kit_fiction_warnings"]
    assert "missing_pov_information_asymmetry_map" in audit["spec_kit_fiction_warnings"]
    assert "missing_pacing_tension_or_checklist_pass" in audit["spec_kit_fiction_warnings"]


def test_build_remix_context_blocks_render_project_workbench_memory_diversity_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "user_modifier_project_blueprint_gate", "candidate_count": 1},
            {"name": "portable_canon_skill_runtime_gate", "candidate_count": 1},
            {"name": "staged_outline_chunk_window_gate", "candidate_count": 1},
            {"name": "wiki_canon_graph_lint_gate", "candidate_count": 1},
            {"name": "plan_draft_log_verify_loop_gate", "candidate_count": 1},
            {"name": "mcp_scene_index_revision_boundary", "candidate_count": 1},
            {"name": "verbalized_sampling_diversity_wiki_gate", "candidate_count": 1},
        ],
        "user_modifier_project_blueprint_gate_hints": ["Bind project modifiers to blueprint evidence."],
        "verbalized_sampling_diversity_wiki_gate_hints": ["File selected variants into the writer wiki."],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Project Workbench Desk",
        bible={"hard_constraints": [{"rule": "Accepted changes need indexed evidence"}]},
        plan={"summary": "Continue with blueprint, canon runtime, wiki lint, scene index, and diversity sampling."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Workbench",
        style_content=(
            "same-type creation source voice\n"
            "- Keep workbench discipline only.\n"
            "forbidden source elements\n"
            "- Do not reuse source wiki pages.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Project workbench and memory diversity audit" in block
        assert "user_modifier_project_blueprint_gate" in block
        assert "portable_canon_skill_runtime_gate" in block
        assert "staged_outline_chunk_window_gate" in block
        assert "wiki_canon_graph_lint_gate" in block
        assert "plan_draft_log_verify_loop_gate" in block
        assert "mcp_scene_index_revision_boundary" in block
        assert "verbalized_sampling_diversity_wiki_gate" in block
        assert "blueprint id" in block
        assert "frontmatter" in block
        assert "current plus adjacent context" in block
        assert "relationship graph checks" in block
        assert "foreshadowing checklists" in block
        assert "reversible diff" in block
        assert "probability-scored variants" in block


def test_build_remix_context_blocks_render_genre_arc_style_governance_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "genre_inspiration_budget_library_gate", "candidate_count": 1},
            {"name": "volume_antipattern_dependency_graph_gate", "candidate_count": 1},
            {"name": "style_dna_breakpoint_hierarchy_gate", "candidate_count": 1},
            {"name": "arc_state_foreshadowing_persistence_gate", "candidate_count": 1},
            {"name": "webnovel_genre_tracker_gate", "candidate_count": 1},
            {"name": "platform_ranking_research_boundary_gate", "candidate_count": 1},
            {"name": "entity_mention_arc_timeline_gate", "candidate_count": 1},
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Genre Arc Desk",
        bible={"hard_constraints": [{"rule": "Do not copy source chapter order"}]},
        plan={"summary": "Continue by preserving arc custody and volume dependencies."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Genre Arc Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Transfer market promise and pressure only.\n"
            "forbidden source elements\n"
            "- Do not reuse source genre bundle, volume ladder, or arc ids.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Genre, arc, and style governance audit" in block
        assert "genre_inspiration_budget_library_gate" in block
        assert "volume_antipattern_dependency_graph_gate" in block
        assert "style_dna_breakpoint_hierarchy_gate" in block
        assert "arc_state_foreshadowing_persistence_gate" in block
        assert "webnovel_genre_tracker_gate" in block
        assert "platform_ranking_research_boundary_gate" in block
        assert "entity_mention_arc_timeline_gate" in block
        assert "abstract option matrix" in block
        assert "event dependency graph" in block
        assert "style-DNA" in block
        assert "major/minor/micro arcs" in block
        assert "appearance rhythm" in block


def test_build_remix_inspired_independence_audit_expands_genre_arc_difference_axes():
    audit = build_remix_inspired_independence_audit(
        style_content=(
            "same-type creation source voice\n"
            "- Keep genre promise and emotional pressure.\n"
            "forbidden source elements\n"
            "- Do not reuse source cast, volume ladder, or payoff sequence.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "genre_inspiration_budget_library_gate"},
                {"name": "volume_antipattern_dependency_graph_gate"},
                {"name": "style_dna_breakpoint_hierarchy_gate"},
                {"name": "arc_state_foreshadowing_persistence_gate"},
                {"name": "entity_mention_arc_timeline_gate"},
            ],
        },
    )

    assert "genre_promise_matrix" in audit["transfer_axes"]
    assert "trope_option_budget" in audit["transfer_axes"]
    assert "volume_escalation_ladder" in audit["required_difference_axes"]
    assert "event_dependency_edges" in audit["required_difference_axes"]
    assert "arc_id_namespace" in audit["required_difference_axes"]
    assert "appearance_rhythm" in audit["required_difference_axes"]
    assert "source_dependency_graph_clone" in audit["copy_risk_checks"]
    assert "style_dna_overfit_review" in audit["copy_risk_checks"]


def test_book_mcp_beta_reader_file_gate_renders_continuation_context():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "slima_book_mcp_beta_reader_file_gate", "candidate_count": 1},
        ],
        "slima_book_mcp_beta_reader_file_gate_hints": [
            "AI beta reader personas review chapter files through explicit file tools.",
        ],
    }

    block = build_remix_continuation_context_block(
        project_title="Beta Reader Desk",
        bible={"hard_constraints": [{"rule": "Human accepts review notes before canon change"}]},
        plan={"summary": "Continue after beta-reader findings are reviewed."},
        source_pattern_pack=pattern_pack,
    )

    assert "Book-MCP beta reader file gate:" in block
    assert "file_scope_envelope" in block
    assert "beta_reader_feedback" in block
    assert "mutation_boundary" in block
    assert "continuation_boundary" in block
    assert "runtime_boundary" in block
    assert "AI beta reader personas" in block


def test_book_mcp_beta_reader_file_gate_renders_same_type_boundary():
    block = build_remix_inspired_context_block(
        project_title="Inspired Beta Reader Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Keep review discipline only.\n"
            "forbidden source elements\n"
            "- Do not reuse source files or reader notes.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "slima_book_mcp_beta_reader_file_gate", "candidate_count": 1},
            ],
        },
    )

    assert "Book-MCP beta reader file gate:" in block
    assert "file_scope_envelope" in block
    assert "beta_reader_feedback" in block
    assert "mutation_boundary" in block
    assert "same_type_boundary" in block
    assert "runtime_boundary" in block


def test_book_mcp_beta_reader_file_gate_extends_continuation_control_audit():
    audit = build_remix_continuation_control_audit(
        bible={"hard_constraints": [{"rule": "Review notes cannot mutate manuscripts directly"}]},
        plan={"summary": "Review beta-reader feedback before next write."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "slima_book_mcp_beta_reader_file_gate"},
            ],
        },
    )

    assert "book_file_scope_envelope" in audit["control_axes"]
    assert "beta_reader_persona_feedback_custody" in audit["control_axes"]
    assert "verify_beta_reader_feedback_review_state" in audit["acceptance_steps"]


def test_live_diagnostics_and_outline_import_gates_render_continuation_context():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "novelwriter_live_manuscript_analytics_gate", "candidate_count": 1},
            {"name": "kindling_local_outline_reference_import_gate", "candidate_count": 1},
        ],
        "novelwriter_live_manuscript_analytics_gate_hints": [
            "Surface Event Line, open plot lines, Connection Web, and Story Pulse as advisory diagnostics.",
        ],
        "kindling_local_outline_reference_import_gate_hints": [
            "Keep scene beats visible as prompts and record import/export custody.",
        ],
    }

    block = build_remix_continuation_context_block(
        project_title="Live Diagnostics Desk",
        bible={"hard_constraints": [{"rule": "Diagnostics require author acceptance"}]},
        plan={"summary": "Continue after outline and diagnostic findings are reviewed."},
        source_pattern_pack=pattern_pack,
    )

    assert "Live diagnostics and outline-import gate:" in block
    assert "live_diagnostic_layers" in block
    assert "Event Line" in block
    assert "Story Pulse" in block
    assert "visible_outline_scaffold" in block
    assert "import_export_custody" in block
    assert "reference_detection_boundary" in block
    assert "continuation_boundary" in block
    assert "runtime_boundary" in block


def test_live_diagnostics_and_outline_import_gates_render_same_type_boundary():
    block = build_remix_inspired_context_block(
        project_title="Inspired Live Diagnostics Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Keep diagnostic discipline only.\n"
            "forbidden source elements\n"
            "- Do not reuse source event-line examples or import snapshots.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "novelwriter_live_manuscript_analytics_gate", "candidate_count": 1},
                {"name": "kindling_local_outline_reference_import_gate", "candidate_count": 1},
            ],
        },
    )

    assert "Live diagnostics and outline-import gate:" in block
    assert "advisory_analysis_boundary" in block
    assert "visible_outline_scaffold" in block
    assert "same_type_boundary" in block
    assert "runtime_boundary" in block


def test_live_diagnostics_and_outline_import_gates_extend_control_audit():
    audit = build_remix_continuation_control_audit(
        bible={"hard_constraints": [{"rule": "Outline imports are proposed deltas only"}]},
        plan={"summary": "Review diagnostics and import custody before drafting."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "novelwriter_live_manuscript_analytics_gate"},
                {"name": "kindling_local_outline_reference_import_gate"},
            ],
        },
    )

    assert "live_manuscript_diagnostic_layers" in audit["control_axes"]
    assert "advisory_scene_suggestion_review" in audit["control_axes"]
    assert "visible_outline_import_export_custody" in audit["control_axes"]
    assert "verify_live_diagnostics_review_state" in audit["acceptance_steps"]
    assert "verify_outline_import_export_custody" in audit["acceptance_steps"]


def test_filetype_rag_and_project_edit_boundary_gates_render_continuation_context():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "dialogoi_filetype_rag_novel_project_gate", "candidate_count": 1},
            {"name": "scrivener_mcp_direct_project_edit_boundary_gate", "candidate_count": 1},
        ],
        "dialogoi_filetype_rag_novel_project_gate_hints": [
            "Separate project settings, manuscript content, and instruction files before RAG.",
        ],
        "scrivener_mcp_direct_project_edit_boundary_gate_hints": [
            "Direct project access needs a boundary report before any edit patch.",
        ],
    }

    block = build_remix_continuation_context_block(
        project_title="RAG Boundary Desk",
        bible={"hard_constraints": [{"rule": "Retrieval scope must be visible"}]},
        plan={"summary": "Continue after scoped retrieval and project-boundary review."},
        source_pattern_pack=pattern_pack,
    )

    assert "FileType RAG and project edit boundary gate:" in block
    assert "filetype_retrieval_scope" in block
    assert "content | settings | instructions | both" in block
    assert "hybrid_search_evidence" in block
    assert "direct_project_boundary_report" in block
    assert "accepted_patch_scope" in block
    assert "continuation_boundary" in block
    assert "runtime_boundary" in block


def test_filetype_rag_and_project_edit_boundary_gates_render_same_type_boundary():
    block = build_remix_inspired_context_block(
        project_title="Inspired RAG Boundary Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Keep retrieval discipline only.\n"
            "forbidden source elements\n"
            "- Do not reuse source manuscript chunks or project structure.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "dialogoi_filetype_rag_novel_project_gate", "candidate_count": 1},
                {"name": "scrivener_mcp_direct_project_edit_boundary_gate", "candidate_count": 1},
            ],
        },
    )

    assert "FileType RAG and project edit boundary gate:" in block
    assert "source_file_class_custody" in block
    assert "direct_project_boundary_report" in block
    assert "same_type_boundary" in block
    assert "runtime_boundary" in block


def test_filetype_rag_and_project_edit_boundary_gates_extend_control_audit():
    audit = build_remix_continuation_control_audit(
        bible={"hard_constraints": [{"rule": "Direct project edits require accepted patch scope"}]},
        plan={"summary": "Review scoped retrieval before accepting edits."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "dialogoi_filetype_rag_novel_project_gate"},
                {"name": "scrivener_mcp_direct_project_edit_boundary_gate"},
            ],
        },
    )

    assert "filetype_scoped_retrieval_evidence" in audit["control_axes"]
    assert "hybrid_search_source_file_custody" in audit["control_axes"]
    assert "direct_project_edit_boundary_report" in audit["control_axes"]
    assert "verify_filetype_retrieval_scope" in audit["acceptance_steps"]
    assert "verify_direct_project_patch_scope" in audit["acceptance_steps"]


def test_frame_setting_state_runtime_gates_render_continuation_context():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "vector_story_frame_coordinate_gate", "candidate_count": 1},
            {"name": "setting_runtime_document_architecture_gate", "candidate_count": 1},
            {"name": "inkfoundry_state_db_redteam_voice_sandbox_gate", "candidate_count": 1},
        ],
        "vector_story_frame_coordinate_gate_hints": [
            "Use VRGB-like frame coordinates as target-owned beat, tone, density, and register controls.",
        ],
        "setting_runtime_document_architecture_gate_hints": [
            "Require a session start packet for loaded, stale, and forbidden setting documents.",
        ],
        "inkfoundry_state_db_redteam_voice_sandbox_gate_hints": [
            "StateDB must outrank vector recall before drafting.",
        ],
    }

    block = build_remix_continuation_context_block(
        project_title="State Frame Desk",
        bible={"hard_constraints": [{"rule": "Accepted state outranks vector recall"}]},
        plan={"summary": "Continue with frame coordinates, session packet, and RedTeam findings."},
        source_pattern_pack=pattern_pack,
    )

    assert "Frame, setting runtime, and StateDB gate:" in block
    assert "frame_coordinate_contract" in block
    assert "tone, density, register" in block
    assert "setting_document_architecture" in block
    assert "session_start_packet" in block
    assert "state_over_vector_boundary" in block
    assert "redteam_voice_sandbox_review" in block
    assert "continuation_boundary" in block
    assert "runtime_boundary" in block


def test_frame_setting_state_runtime_gates_render_same_type_boundary():
    block = build_remix_inspired_context_block(
        project_title="Inspired State Frame Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Keep frame and state discipline only.\n"
            "forbidden source elements\n"
            "- Do not reuse source VRGB frames, setting docs, or StateDB facts.\n"
        ),
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "vector_story_frame_coordinate_gate", "candidate_count": 1},
                {"name": "setting_runtime_document_architecture_gate", "candidate_count": 1},
                {"name": "inkfoundry_state_db_redteam_voice_sandbox_gate", "candidate_count": 1},
            ],
        },
    )

    assert "Frame, setting runtime, and StateDB gate:" in block
    assert "frame_coordinate_contract" in block
    assert "setting_document_architecture" in block
    assert "state_over_vector_boundary" in block
    assert "same_type_boundary" in block
    assert "runtime_boundary" in block


def test_frame_setting_state_runtime_gates_extend_control_audit():
    audit = build_remix_continuation_control_audit(
        bible={"hard_constraints": [{"rule": "RedTeam findings are review proposals"}]},
        plan={"summary": "Check frame, setting docs, and hard state before draft."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "vector_story_frame_coordinate_gate"},
                {"name": "setting_runtime_document_architecture_gate"},
                {"name": "inkfoundry_state_db_redteam_voice_sandbox_gate"},
            ],
        },
    )

    assert "story_frame_coordinate_contract" in audit["control_axes"]
    assert "setting_document_session_packet" in audit["control_axes"]
    assert "state_db_over_vector_review" in audit["control_axes"]
    assert "redteam_voice_sandbox_findings" in audit["control_axes"]
    assert "verify_frame_coordinate_contract" in audit["acceptance_steps"]
    assert "verify_setting_document_session_packet" in audit["acceptance_steps"]
    assert "verify_state_db_redteam_voice_review" in audit["acceptance_steps"]


def test_seed_to_bible_foundation_loop_gates_render_context_blocks():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "seed_to_bible_foundation_loop_gate", "candidate_count": 1},
            {"name": "layered_story_bible_artifact_contract_gate", "candidate_count": 1},
        ],
        "seed_to_bible_foundation_loop_gate_hints": [
            "Target the weakest dimension, then keep or discard by score comparison.",
        ],
        "layered_story_bible_artifact_contract_gate_hints": [
            "Generate world, characters, voice, mystery, outline, canon, and foreshadowing in dependency order.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Foundation Loop Desk",
        bible={
            "world_rules": {"archive_magic": "Each seal has a public cost."},
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "hard_constraints": [{"rule": "Do not promote worse foundation attempts"}],
        },
        plan={"summary": "Continue after foundation score and lore score pass."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Foundation Loop Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Use foundation-loop discipline only.\n"
            "forbidden source elements\n"
            "- Do not reuse source world, character, mystery, or canon files.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Seed-to-bible foundation loop gate:" in block
        assert "foundation_score_loop" in block
        assert "weakest_dimension_repair" in block
        assert "keep_discard_restore_policy" in block
        assert "layered_story_bible_artifacts" in block
        assert "independent_eval_boundary" in block
        assert "runtime_boundary" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired
    assert "Target the weakest dimension" in continuation


def test_seed_to_bible_foundation_loop_gates_extend_control_audit():
    audit = build_remix_continuation_control_audit(
        bible={
            "hard_constraints": [{"rule": "Only accepted foundation layers can seed chapters"}],
        },
        plan={"summary": "Check foundation layers before chapter automation."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "seed_to_bible_foundation_loop_gate"},
                {"name": "layered_story_bible_artifact_contract_gate"},
            ],
        },
    )

    assert "foundation_score_loop_review" in audit["control_axes"]
    assert "weakest_dimension_regeneration_trace" in audit["control_axes"]
    assert "foundation_keep_discard_restore_decision" in audit["control_axes"]
    assert "layered_story_bible_artifact_contract" in audit["control_axes"]
    assert "story_layer_dependency_order" in audit["control_axes"]
    assert "verify_foundation_loop_score_review" in audit["acceptance_steps"]
    assert "verify_layered_story_bible_artifacts" in audit["acceptance_steps"]


def test_universal_deep_planning_revision_gates_render_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "premise_structure_hook_payoff_gate", "candidate_count": 1},
            {"name": "scene_goal_obstacle_cost_exit_gate", "candidate_count": 1},
            {"name": "revision_finding_patch_strategy_gate", "candidate_count": 1},
        ],
        "premise_structure_hook_payoff_gate_hints": [
            "Stress-test premise, reader promise, structure choice, and hook/payoff matrix before long drafting.",
        ],
        "scene_goal_obstacle_cost_exit_gate_hints": [
            "Each scene needs goal, obstacle, tactic, turn, cost, and changed exit state.",
        ],
        "revision_finding_patch_strategy_gate_hints": [
            "Lead revision with severity findings and patch the smallest failing section first.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Deep Universal Desk",
        bible={
            "style_signature": {"reader_promise": "mystery pressure with earned payoff"},
            "story_arcs": [{"name": "Archive Arc", "status": "open"}],
            "foreshadows": [{"hook": "Archive seal breaks", "status": "open"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 12,
                    "summary": "Lin caught the archive contradiction.",
                    "scene_beats": [
                        {
                            "goal": "prove the seal was forged",
                            "obstacle": "the witness retracts",
                            "tactic": "force public comparison",
                            "turn": "the seal burns",
                            "cost": "Lin loses crowd trust",
                            "exit_state": "public danger escalates",
                        }
                    ],
                    "revision_findings": [
                        {"severity": "High", "issue": "weak public cost", "patch_scope": "scene 2"}
                    ],
                }
            ],
        },
        plan={
            "summary": "Continue from the public contradiction.",
            "beats": [
                {
                    "beat": "Make the public contradiction cost Lin leverage",
                    "goal": "restore order",
                    "obstacle": "the rival weaponizes the seal",
                    "cost": "Lin loses the archive key",
                    "status": "pending",
                }
            ],
            "guardrails": [{"rule": "No instant solution"}],
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Deep Universal Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Transfer promise pressure only.\n"
            "forbidden source elements\n"
            "- Do not reuse source premise, hook/payoff matrix, scene beats, or patch notes.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={},
        plan={"summary": "Minimal plan without deep universal surfaces."},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Universal deep planning and revision gate:" in block
        assert "premise_stress_test" in block
        assert "hook_payoff_matrix" in block
        assert "scene_goal_obstacle_cost_exit" in block
        assert "revision_findings_severity" in block
        assert "least_destructive_patch_strategy" in block
        assert "Stress-test premise" in block
        assert "goal, obstacle, tactic, turn, cost" in block
        assert "severity findings" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired
    assert "source premise, hook/payoff matrix, scene beats" in inspired

    assert "premise_structure_stress_test" in audit["control_axes"]
    assert "hook_payoff_matrix_review" in audit["control_axes"]
    assert "scene_goal_obstacle_cost_exit_state" in audit["control_axes"]
    assert "revision_finding_severity_triage" in audit["control_axes"]
    assert "least_destructive_patch_scope" in audit["control_axes"]
    assert "verify_premise_structure_hook_payoff" in audit["acceptance_steps"]
    assert "verify_scene_goal_obstacle_cost_exit" in audit["acceptance_steps"]
    assert "verify_revision_findings_patch_scope" in audit["acceptance_steps"]


def test_universal_hook_integrity_and_anti_ai_texture_gates_render_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "opening_ending_hook_integrity_gate", "candidate_count": 1},
            {"name": "anti_ai_naturalness_texture_gate", "candidate_count": 1},
        ],
        "opening_ending_hook_integrity_gate_hints": [
            "Choose an opening hook type and ending hook job; reject fake cliffhangers resolved without consequence.",
        ],
        "anti_ai_naturalness_texture_gate_hints": [
            "Replace generic AI texture with concrete action, uneven rhythm, subtext, and character-specific diction.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Hook Texture Desk",
        bible={
            "style_signature": {"reader_promise": "public mystery pressure"},
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 6,
                    "summary": "Lin exposed the forged seal but lost the crowd.",
                    "opening_hook_type": "consequence from last chapter",
                    "ending_hook_job": "force a decision",
                    "new_hooks": [{"hook": "The crowd demands the archive key"}],
                    "prose_texture_review": {"status": "pass"},
                }
            ],
        },
        plan={
            "summary": "Open with the crowd demanding the key.",
            "beats": [{"beat": "Make Lin choose between truth and crowd safety"}],
            "guardrails": [{"rule": "No fake cliffhanger or generic emotion summary"}],
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Hook Texture Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only hook pressure and prose texture review axes.\n"
            "forbidden source elements\n"
            "- Do not reuse source opening hooks, ending hook jobs, or AI-text cleanup notes.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={"chapter_change_packages": [{"source": "chapter_analysis", "chapter_number": 2}]},
        plan={"summary": "Minimal plan"},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Opening/ending hook integrity gate:" in block
        assert "opening_hook_type" in block
        assert "ending_hook_job" in block
        assert "fake_cliffhanger_boundary" in block
        assert "Anti-AI naturalness texture gate:" in block
        assert "texture_review" in block
        assert "generic_ai_texture_boundary" in block
        assert "concrete action, uneven rhythm" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired
    assert "source opening hooks, ending hook jobs" in inspired

    assert "opening_hook_type_selection" in audit["control_axes"]
    assert "ending_hook_job_integrity" in audit["control_axes"]
    assert "fake_cliffhanger_integrity" in audit["control_axes"]
    assert "anti_ai_texture_naturalness_review" in audit["control_axes"]
    assert "verify_opening_ending_hook_integrity" in audit["acceptance_steps"]
    assert "verify_anti_ai_naturalness_texture" in audit["acceptance_steps"]
    assert "hook_naturalness_warnings" in audit["warnings"]
    assert "missing_opening_hook_type" in audit["hook_naturalness_warnings"]


def test_novelforge_version_safe_scene_fact_pipeline_renders_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "versioned_scene_fact_review_pipeline_gate", "candidate_count": 1},
            {"name": "novelforge_version_safe_human_review_gate", "candidate_count": 1},
        ],
        "versioned_scene_fact_review_pipeline_gate_hints": [
            "Keep scene versions, fact approval, memory chunks, reference assets, ReviewReports, and accepted exports traceable.",
        ],
        "novelforge_version_safe_human_review_gate_hints": [
            "Never overwrite accepted prose; archive drafts and promote only reviewed facts into canon.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Version Safe Desk",
        bible={
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 14,
                    "summary": "Lin accepted the revised archive scene.",
                    "fact_approval": [{"fact": "The archive key stayed with Lin", "status": "approved"}],
                    "review_reports": [{"severity": "Medium", "issue": "weak motive"}],
                    "reference_assets": [{"name": "archive floor plan", "status": "approved"}],
                }
            ],
        },
        plan={"summary": "Draft only from accepted scene and approved fact memory."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Version Safe Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only version-safe scene/fact custody.\n"
            "forbidden source elements\n"
            "- Do not reuse source scene versions, fact memories, reference assets, or ReviewReports.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={},
        plan={"summary": "Minimal version-safe plan."},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "NovelForge version-safe scene/fact pipeline gate:" in block
        assert "scene_version_lineage" in block
        assert "fact_approval_queue" in block
        assert "focused_retrieval_scope" in block
        assert "continuity_reviewreport" in block
        assert "accepted_export_readiness" in block
        assert "scene versions, fact approval, memory chunks" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired
    assert "source scene versions, fact memories" in inspired

    assert "scene_version_lineage" in audit["control_axes"]
    assert "fact_approval_queue" in audit["control_axes"]
    assert "focused_memory_reference_asset_retrieval" in audit["control_axes"]
    assert "continuity_reviewreport_findings" in audit["control_axes"]
    assert "accepted_export_readiness" in audit["control_axes"]
    assert "verify_scene_version_lineage" in audit["acceptance_steps"]
    assert "approve_fact_extraction_before_memory" in audit["acceptance_steps"]
    assert "verify_reference_asset_retrieval_scope" in audit["acceptance_steps"]
    assert "verify_continuity_reviewreport_findings" in audit["acceptance_steps"]


def test_novel_studio_graph_memory_continuity_gate_renders_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "novel_studio_graph_memory_continuity_gate", "candidate_count": 1},
            {"name": "novel_studio_accepted_chapter_writeback_gate", "candidate_count": 1},
        ],
        "novel_studio_graph_memory_continuity_gate_hints": [
            "Use character states, graph triples, timeline events, retrieved memory chunks, and continuity checks to ground the next context pack.",
        ],
        "novel_studio_accepted_chapter_writeback_gate_hints": [
            "Drafts do not update canon; only accepted chapters write summaries, character states, graph triples, timeline events, and memory chunks.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Graph Memory Desk",
        bible={
            "character_cards": [{"name": "Lin", "status": "injured", "location": "archive"}],
            "timeline": [{"event": "Lin kept the archive key", "chapter_number": 8}],
            "hard_constraints": [{"rule": "Do not revive dead characters without canon reason"}],
        },
        plan={"summary": "Continue only after graph facts and timeline conflicts are checked."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Graph Memory Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn graph-memory continuity discipline only.\n"
            "forbidden source elements\n"
            "- Do not reuse source graph triples, character states, timeline events, or memory chunks.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={},
        plan={"summary": "Plan with graph-memory review."},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Novel Studio graph-memory continuity gate:" in block
        assert "accepted_chapter_writeback" in block
        assert "graph_fact_triples" in block
        assert "character_state_versions" in block
        assert "timeline_event_order" in block
        assert "contradiction_checklist" in block
        assert "hybrid_retrieval_pack" in block
        assert "character states, graph triples, timeline events" in block
        assert "Drafts do not update canon" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired
    assert "source graph triples, character states" in inspired

    assert "accepted_chapter_writeback_surface" in audit["control_axes"]
    assert "graph_fact_triple_consistency" in audit["control_axes"]
    assert "character_state_versioning" in audit["control_axes"]
    assert "timeline_event_ordering" in audit["control_axes"]
    assert "contradiction_checklist_review" in audit["control_axes"]
    assert "hybrid_retrieval_context_pack" in audit["control_axes"]
    assert "verify_accepted_chapter_writeback" in audit["acceptance_steps"]
    assert "verify_graph_fact_triples" in audit["acceptance_steps"]
    assert "verify_character_state_timeline_conflicts" in audit["acceptance_steps"]
    assert "verify_hybrid_retrieval_pack_scope" in audit["acceptance_steps"]


def test_genre_promise_contract_matrix_gate_renders_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "genre_promise_contract_matrix_gate", "candidate_count": 1},
            {"name": "subgenre_specific_ledger_gate", "candidate_count": 1},
        ],
        "genre_promise_contract_matrix_gate_hints": [
            "Record reader pleasure, payoff speed, planted-before-payoff items, welcome tropes, tired tropes, and emotional aftertaste.",
        ],
        "subgenre_specific_ledger_gate_hints": [
            "Pick the active romance trust, mystery clue, realm-resource-cost, or threat-rule ledger before drafting.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Genre Matrix Desk",
        bible={
            "genre": "mystery romance",
            "style_signature": {"reader_promise": "fair puzzle plus slow-burn trust"},
            "genre_promise_matrix": {
                "expected_pleasure": "fair clue puzzle and emotional intimacy",
                "payoff_speed": "one clue or trust shift per chapter",
                "plant_before_payoff": ["motive clue before reveal"],
                "welcome_tropes": ["rivals to allies"],
                "tired_tropes_to_twist": ["one-sentence misunderstanding"],
                "emotional_aftertaste": "earned tenderness under danger",
            },
            "mystery_clue_ledger": [{"clue": "blue wax seal", "payoff": "archive heir proof"}],
        },
        plan={"summary": "Continue the clue interview."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Genre Matrix Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Preserve only genre pleasure timing and aftertaste.\n"
            "forbidden source elements\n"
            "- Do not reuse source trope sequence or reveal order.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={"genre": "mystery"},
        plan={"summary": "Plan without a matrix."},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Genre promise contract matrix gate:" in block
        assert "expected_reader_pleasure" in block
        assert "payoff_timing_boundary" in block
        assert "welcome_and_tired_tropes" in block
        assert "emotional_aftertaste" in block
        assert "Record reader pleasure" in block
        assert "Subgenre-specific ledger gate:" in block
        assert "active_ledger_selection" in block
        assert "ledger_debt_fields" in block
        assert "Pick the active romance trust" in block
    assert "same_type_boundary" in inspired
    assert "source trope sequence" in inspired
    assert "trust breaks" in inspired

    assert "genre_promise_contract_matrix" in audit["control_axes"]
    assert "genre_trope_twist_boundary" in audit["control_axes"]
    assert "emotional_aftertaste_target" in audit["control_axes"]
    assert "subgenre_specific_active_ledgers" in audit["control_axes"]
    assert "genre_payoff_debt_custody" in audit["control_axes"]
    assert "same_type_ledger_independence" in audit["control_axes"]
    assert "verify_genre_promise_contract_matrix" in audit["acceptance_steps"]
    assert "verify_subgenre_specific_ledgers" in audit["acceptance_steps"]
    assert "genre_promise_contract_warnings" in audit["warnings"]
    assert "missing_genre_promise_matrix" in audit["genre_promise_contract_warnings"]
    assert "subgenre_ledger_warnings" in audit["warnings"]
    assert "missing_subgenre_specific_ledger" in audit["subgenre_ledger_warnings"]


def test_distilled_novel_toolbox_platform_compliance_gate_renders_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "distilled_novel_toolbox_platform_compliance_gate", "candidate_count": 1},
            {"name": "distilled_novel_toolbox_human_polish_boundary_gate", "candidate_count": 1},
        ],
        "distilled_novel_toolbox_platform_compliance_gate_hints": [
            "Turn commercialization, platform fit, compliance, sensitive-word review, and publishing analytics into local review packet fields.",
        ],
        "distilled_novel_toolbox_human_polish_boundary_gate_hints": [
            "Use de-AI/polishing vocabulary only for human quality review; do not provide detection evasion or prompt-body imports.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Platform Compliance Desk",
        bible={
            "reader_promise": "fast webnovel revenge with emotional cost",
            "platform": "Fanqie-style short serial",
            "hard_constraints": [{"rule": "No platform policy text is canonical without current verification"}],
        },
        plan={"summary": "Draft after market fit and compliance packet review."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Platform Compliance Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn market-fit and compliance packet shape only.\n"
            "forbidden source elements\n"
            "- Do not reuse source platform claims, prompt templates, anti-detection instructions, or sample fiction.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={"reader_promise": "serial suspense"},
        plan={"summary": "Plan without platform packet."},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Distilled Novel Toolbox platform/compliance gate:" in block
        assert "market_fit_card" in block
        assert "platform_policy_verification" in block
        assert "compliance_review_packet" in block
        assert "human_polish_boundary" in block
        assert "prompt_body_import_policy" in block
        assert "example_fiction_import_policy" in block
        assert "Turn commercialization, platform fit" in block
        assert "quality review" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired
    assert "source platform claims, prompt templates" in inspired

    assert "market_fit_card" in audit["control_axes"]
    assert "platform_policy_verification" in audit["control_axes"]
    assert "compliance_review_packet" in audit["control_axes"]
    assert "human_polish_boundary" in audit["control_axes"]
    assert "prompt_body_import_policy" in audit["control_axes"]
    assert "verify_platform_policy_current" in audit["acceptance_steps"]
    assert "verify_compliance_review_packet" in audit["acceptance_steps"]
    assert "verify_no_detection_evasion_or_prompt_body_import" in audit["acceptance_steps"]


def test_universal_post_draft_review_gate_renders_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "post_draft_review_checklist_gate", "candidate_count": 1},
        ],
        "post_draft_review_checklist_gate_hints": [
            "Review outline fidelity, continuity, POV control, character voice, scene conflict, pacing, reader-pull, hook/payoff, prose naturalness, and mobile readability before accepting a chapter.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Post Draft Review Desk",
        bible={
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 15,
                    "summary": "Lin escaped the archive but left the public trust debt unresolved.",
                }
            ],
        },
        plan={"summary": "Review the accepted chapter before drafting the next one."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Post Draft Review Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only the review checklist order.\n"
            "forbidden source elements\n"
            "- Do not reuse source review notes, chapter fixes, or mobile-readability patches.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 15,
                    "summary": "Lin escaped the archive.",
                }
            ],
        },
        plan={"summary": "Review before next draft."},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Universal post-draft review gate:" in block
        assert "checklist_dimensions" in block
        assert "outline fidelity, continuity, POV control" in block
        assert "mobile_readability" in block
        assert "least_destructive_repair" in block
        assert "Review outline fidelity" in block
    assert "continuation_boundary" in continuation
    assert "post_draft_review_warnings" in continuation
    assert "same_type_boundary" in inspired
    assert "source review notes" in inspired

    assert "post_draft_review_checklist" in audit["control_axes"]
    assert "mobile_readability_review" in audit["control_axes"]
    assert "least_destructive_repair_scope" in audit["control_axes"]
    assert "verify_post_draft_review_checklist" in audit["acceptance_steps"]
    assert "verify_mobile_readability_before_acceptance" in audit["acceptance_steps"]
    assert "verify_smallest_failing_artifact_repair" in audit["acceptance_steps"]
    assert "post_draft_review_warnings" in audit["warnings"]
    assert "missing_post_draft_review_checklist" in audit["post_draft_review_warnings"]
    assert "missing_mobile_readability_review" in audit["post_draft_review_warnings"]
    assert "missing_smallest_repair_scope" in audit["post_draft_review_warnings"]


def test_universal_post_draft_review_gate_passes_with_review_surfaces():
    audit = build_remix_continuation_control_audit(
        bible={
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 16,
                    "summary": "Lin paid one trust debt and opened a larger public threat.",
                    "post_draft_review": {
                        "outline_fidelity": "pass",
                        "continuity": "pass",
                        "pov_control": "pass",
                        "character_voice": "pass",
                        "scene_conflict": "pass",
                        "pacing": "pass",
                        "reader_pull": "pass",
                        "hook_payoff": "pass",
                        "prose_naturalness": "pass",
                    },
                    "mobile_readability_review": {"status": "pass"},
                    "repair_scope": "No rewrite needed; only keep one dialogue trim candidate.",
                }
            ],
        },
        plan={"summary": "Continue from the accepted review packet."},
        source_pattern_pack={
            "workflow_patterns": [
                {"name": "post_draft_review_checklist_gate"},
            ],
        },
    )

    assert audit["post_draft_review_warnings"] == []


def test_universal_intake_export_rollback_gates_render_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "five_question_intake_story_promise_gate", "candidate_count": 1},
            {"name": "universal_export_clean_manuscript_gate", "candidate_count": 1},
            {"name": "minimal_rollback_repair_scope_gate", "candidate_count": 1},
        ],
        "five_question_intake_story_promise_gate_hints": [
            "Ask no more than five setup questions, then produce logline, reader promise, protagonist arc, opposition, world rules, ending direction, and 5-15 beats.",
        ],
        "universal_export_clean_manuscript_gate_hints": [
            "Export mode packages a clean manuscript or structured export plan from accepted chapters only.",
        ],
        "minimal_rollback_repair_scope_gate_hints": [
            "When a gate fails, repair the smallest failing artifact instead of restarting the whole project.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Universal Intake Export Desk",
        bible={
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 3,
                    "summary": "Lin exposed the false witness but left a trust debt open.",
                }
            ],
        },
        plan={"mode": "export", "summary": "Prepare accepted chapters for a clean manuscript export."},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Intake Export Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only the compact intake, export, and smallest-repair workflow.\n"
            "forbidden source elements\n"
            "- Do not reuse source questions, export text, chapter order, or repair notes.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 3,
                    "summary": "Lin exposed the false witness.",
                }
            ],
        },
        plan={"mode": "export", "summary": "Prepare accepted chapters for export."},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Universal intake, export, and rollback gate:" in block
        assert "five_question_intake" in block
        assert "clean_manuscript_export" in block
        assert "minimal_rollback_repair_scope" in block
        assert "Ask no more than five setup questions" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired

    assert "five_question_intake_packet" in audit["control_axes"]
    assert "clean_manuscript_export_scope" in audit["control_axes"]
    assert "minimal_rollback_repair_scope" in audit["control_axes"]
    assert "verify_five_question_intake_packet" in audit["acceptance_steps"]
    assert "verify_clean_export_scope" in audit["acceptance_steps"]
    assert "verify_minimal_rollback_scope" in audit["acceptance_steps"]
    assert "intake_export_rollback_warnings" in audit["warnings"]
    assert "missing_reader_promise_or_premise" in audit["intake_export_rollback_warnings"]
    assert "missing_clean_export_manifest" in audit["intake_export_rollback_warnings"]
    assert "missing_minimal_rollback_repair_scope" in audit["intake_export_rollback_warnings"]


def test_local_first_provider_and_suggestion_card_gates_render_context_and_audit():
    source_pattern_pack = {
        "patterns": [
            {"name": "local_first_provider_boundary_authoring_gate", "candidate_count": 1},
            {"name": "suggestion_card_nonoverwrite_revision_gate", "candidate_count": 1},
            {"name": "book_view_import_export_manifest_gate", "candidate_count": 1},
        ],
        "local_first_provider_boundary_authoring_gate_hints": [
            "Record whether the chapter run uses WebLLM/WebGPU, Ollama, cloud key, or no-model fallback before any prompt can leave local storage.",
        ],
        "suggestion_card_nonoverwrite_revision_gate_hints": [
            "AI edits must arrive as accept/reject suggestion cards and never overwrite accepted prose without author approval.",
        ],
        "book_view_import_export_manifest_gate_hints": [
            "Book view/export needs front matter, live pagination, import auto-split status, and EPUB/PDF/Markdown manifest evidence.",
        ],
    }

    block = build_remix_continuation_context_block(
        project_title="Incipit Fusion",
        bible={
            "provider_boundary": "Ollama local by default; cloud key disabled for this pass.",
            "offline_fallback": "No-model proofread and outline scaffold only.",
        },
        plan={
            "suggestion_cards": [{"id": "s1", "status": "pending_author_acceptance"}],
            "export_manifest": {"formats": ["Markdown"], "front_matter": ["Title Page"]},
        },
        source_pattern_pack=source_pattern_pack,
    )

    assert "Local-first authoring and suggestion-card gate:" in block
    assert "local_first_provider_boundary_authoring_gate" in block
    assert "suggestion_card_nonoverwrite_revision_gate" in block
    assert "book_view_import_export_manifest_gate" in block
    assert "WebLLM/WebGPU" in block
    assert "accept/reject" in block
    assert "auto-split" in block

    audit = build_remix_continuation_control_audit(
        bible={},
        plan={},
        source_pattern_pack=source_pattern_pack,
    )

    assert "local_first_authoring_provider_boundary" in audit["control_axes"]
    assert "suggestion_card_accept_reject_queue" in audit["control_axes"]
    assert "book_view_import_export_manifest" in audit["control_axes"]
    assert "verify_local_first_provider_boundary" in audit["acceptance_steps"]
    assert "verify_suggestion_card_acceptance_boundary" in audit["acceptance_steps"]
    assert "verify_book_view_import_export_manifest" in audit["acceptance_steps"]
    assert "local_first_authoring_warnings" in audit["warnings"]
    assert "missing_local_first_provider_boundary" in audit["local_first_authoring_warnings"]
    assert "missing_suggestion_card_acceptance_policy" in audit["local_first_authoring_warnings"]
    assert "missing_book_view_import_export_manifest" in audit["local_first_authoring_warnings"]


def test_chinese_skill_workstation_phase_quality_gate_renders_context_and_audit():
    source_pattern_pack = {
        "patterns": [
            {"name": "chinese_skill_workstation_phase_quality_gate", "candidate_count": 1},
        ],
        "chinese_skill_workstation_phase_quality_gate_hints": [
            "Model Chinese webnovel production as six visible phases and keep task_plan.md, findings.md, and progress.md ledgers.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Chinese Webnovel Workstation",
        bible={
            "accepted_canon": "Accepted chapters stop at chapter 18.",
            "quality_findings": [{"severity": "High", "issue": "weak chapter hook"}],
        },
        plan={
            "summary": "Continue from accepted canon and run quality review before delivery.",
            "delivery_manifest": {"formats": ["clean Markdown"]},
        },
        source_pattern_pack=source_pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Webnovel Workstation",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only staged workflow and quality gates.\n"
            "forbidden source elements\n"
            "- Do not reuse source originals, examples, cover prompts, or qimao materials.\n"
        ),
        source_pattern_pack=source_pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Chinese skill workstation phase-quality gate:" in block
        assert "six_phase_workflow" in block
        assert "file_backed_ledgers" in block
        assert "quality_delivery_boundary" in block
        assert "task_plan.md, findings.md, and progress.md" in block
        assert "DOCX/HTML/reader delivery" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired
    assert "rebuild premise, cast, style abstraction" in inspired

    audit = build_remix_continuation_control_audit(
        bible={},
        plan={},
        source_pattern_pack=source_pattern_pack,
    )

    assert "six_phase_chinese_webnovel_workstation" in audit["control_axes"]
    assert "file_backed_task_findings_progress" in audit["control_axes"]
    assert "quality_review_delivery_manifest" in audit["control_axes"]
    assert "verify_six_phase_creation_artifacts" in audit["acceptance_steps"]
    assert "verify_task_findings_progress_ledgers" in audit["acceptance_steps"]
    assert "verify_quality_review_before_delivery" in audit["acceptance_steps"]


def test_saga_tui_adversarial_publish_gate_renders_context_and_audit():
    source_pattern_pack = {
        "workflow_patterns": [
            {"name": "saga_tui_adversarial_publish_gate", "candidate_count": 1},
        ],
        "saga_tui_adversarial_publish_gate_hints": [
            "Use story-vault folders, split-view status cards, adversarial score gates, and publish manifests as evidence.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="SAGA Fusion Desk",
        bible={
            "style_signature": {"anti_slop_rules": ["avoid generic dialogue beats"]},
            "chapter_change_packages": [{"chapter_number": 4, "summary": "Accepted chapter reached midpoint."}],
        },
        plan={
            "summary": "Draft chapter 5 after score gate review.",
            "review_scorecards": [{"target": "POV filter words", "status": "pending"}],
        },
        source_pattern_pack=source_pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired SAGA Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only the status and score-gate workflow.\n"
            "forbidden source elements\n"
            "- Do not reuse SAGA prompt text, agent files, example books, or audiobook assets.\n"
        ),
        source_pattern_pack=source_pattern_pack,
    )

    for block in (continuation, inspired):
        assert "SAGA TUI/adversarial publishing gate:" in block
        assert "story_vault_status_card" in block
        assert "adversarial_score_gate" in block
        assert "publish_manifest_boundary" in block
        assert "split-view status cards" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired
    assert "rebuild the status card, score thresholds" in inspired

    audit = build_remix_continuation_control_audit(
        bible={},
        plan={},
        source_pattern_pack=source_pattern_pack,
    )

    assert "saga_story_vault_status_card" in audit["control_axes"]
    assert "saga_adversarial_score_retry_gate" in audit["control_axes"]
    assert "saga_publish_artifact_boundary" in audit["control_axes"]
    assert "verify_saga_story_vault_status_manifest" in audit["acceptance_steps"]
    assert "verify_saga_adversarial_score_gate_log" in audit["acceptance_steps"]
    assert "verify_saga_publish_artifact_boundary" in audit["acceptance_steps"]


def test_writeagent_four_agent_quality_loop_renders_context_and_audit():
    pattern_pack = {
        "workflow_patterns": [
            {"name": "four_agent_chapter_quality_loop_gate", "candidate_count": 1},
        ],
        "four_agent_chapter_quality_loop_gate_hints": [
            "Planner maintains bible/plans, writer drafts chapters, reviewer scores ten dimensions, polisher removes AI flavor, then planner archives accepted changes.",
            "Pass >=35 with no item <=2; modify 25-34 or any item <=2; rewrite <25 or core item <=1.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Four Agent Quality Desk",
        bible={
            "character_cards": [{"name": "Lin", "goal": "protect the archive"}],
            "timeline": [{"event": "Archive seal broke", "chapter_number": 4}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 4,
                    "summary": "Lin saw the seal break in public.",
                }
            ],
        },
        plan={"summary": "Continue after the public failure.", "beats": [{"beat": "Reviewer blocks shortcut resolution"}]},
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Four Agent Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only the visible quality loop.\n"
            "forbidden source elements\n"
            "- Do not reuse source roles as hidden authority or copy review reports.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    audit = build_remix_continuation_control_audit(
        bible={},
        plan={"summary": "Plan without score packet."},
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Four-agent chapter quality loop gate:" in block
        assert "planner_writer_reviewer_polisher_roles" in block
        assert "chapter_quality_loop" in block
        assert "ten_dimension_score_thresholds" in block
        assert "human_confirmation_points" in block
        assert "Pass >=35" in block
        assert "main-agent decision" in block
    assert "same_type_boundary" in inspired
    assert "continuation_boundary" in continuation
    assert "four_agent_role_boundary" in audit["control_axes"]
    assert "chapter_quality_score_packet" in audit["control_axes"]
    assert "human_milestone_confirmation" in audit["control_axes"]
    assert "verify_four_agent_role_boundaries" in audit["acceptance_steps"]
    assert "verify_chapter_quality_threshold_decision" in audit["acceptance_steps"]
    assert "verify_human_milestone_confirmation_points" in audit["acceptance_steps"]


def test_deterministic_volume_spec_orchestration_gates_render_context_and_audit():
    pattern_pack = {
        "volume_rolling_spec_quality_gate_hints": [
            "Model serialized webnovel work as a volume loop with L1/L2/L3/LS contracts and 5/10 chapter audits.",
        ],
        "executor_agnostic_instruction_checkpoint_gate_hints": [
            "Separate deterministic orchestration from model execution with instruction packets, checkpoints, staging, validation, and commit transactions.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Deterministic Volume Desk",
        bible={
            "volume_plan": [{"volume": 1, "promise": "Archive trial"}],
            "storyline_contracts": [{"id": "LS-archive", "status": "active"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 10,
                    "summary": "The first volume reached its deep inventory point.",
                }
            ],
        },
        plan={
            "summary": "Continue with validated staging only.",
            "volume_audit_cadence": {"sliding": 5, "deep_inventory": 10},
            "quality_tier_decision": {"tier": "human_review"},
            "instruction_packet": {"intent": "draft next chapter"},
            "checkpoint_cursor": "ch010",
            "staging_manifest": [{"path": "staging/ch011.md"}],
            "commit_transaction": {"scope": ["chapter", "state", "foreshadowing"]},
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Deterministic Volume Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only volume cadence and deterministic checkpoint workflow.\n"
            "forbidden source elements\n"
            "- Do not reuse upstream storylines, chapter-contract ids, packet templates, or staging paths.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    missing_audit = build_remix_continuation_control_audit(
        bible={},
        plan={},
        source_pattern_pack=pattern_pack,
    )
    satisfied_audit = build_remix_continuation_control_audit(
        bible={
            "volume_plan": [{"volume": 1}],
            "storyline_contracts": [{"id": "LS-1"}],
        },
        plan={
            "volume_audit_cadence": {"sliding": 5, "deep_inventory": 10},
            "quality_tier_decision": {"tier": "pass"},
            "instruction_packet": {"intent": "draft"},
            "checkpoint_cursor": "ch001",
            "staging_manifest": [{"path": "staging/ch002.md"}],
            "commit_transaction": {"scope": ["chapter"]},
        },
        source_pattern_pack=pattern_pack,
    )
    independence = build_remix_inspired_independence_audit(
        style_content=(
            "【同类型创作总原则】\n- Abstract only.\n"
            "【源书语气样本】\n- No source prose.\n"
            "【源书显性元素禁用清单】\n- No source names.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Deterministic volume spec orchestration gate:" in block
        assert "volume_spec_layers" in block
        assert "rolling_volume_audit" in block
        assert "quality_tier_decision" in block
        assert "instruction_packet_boundary" in block
        assert "checkpoint_staging_commit" in block
        assert "L1/L2/L3/LS contracts" in block
        assert "instruction packets, checkpoints, staging" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired

    assert "volume_l1_l2_l3_ls_spec_contracts" in missing_audit["control_axes"]
    assert "instruction_packet_execution_boundary" in missing_audit["control_axes"]
    assert "verify_volume_spec_contract_layers" in missing_audit["acceptance_steps"]
    assert "verify_instruction_packet_scope" in missing_audit["acceptance_steps"]
    assert "deterministic_volume_spec_warnings" in missing_audit["warnings"]
    assert "missing_volume_spec_plan" in missing_audit["deterministic_volume_spec_warnings"]
    assert "missing_instruction_packet_scope" in missing_audit["deterministic_volume_spec_warnings"]
    assert "deterministic_volume_spec_warnings" not in satisfied_audit["warnings"]
    assert satisfied_audit["deterministic_volume_spec_warnings"] == []

    assert "volume_audit_cadence" in independence["transfer_axes"]
    assert "deterministic_orchestration_shape" in independence["transfer_axes"]
    assert "volume_storyline_ids" in independence["required_difference_axes"]
    assert "instruction_packet_namespace" in independence["required_difference_axes"]
    assert "source_storyline_contract_clone" in independence["copy_risk_checks"]
    assert "source_checkpoint_staging_template_clone" in independence["copy_risk_checks"]


def test_raw_story_assimilation_gate_projects_deltas_review_and_writeback_boundaries():
    pattern_pack = {
        "raw_story_assimilation_workflow_gate_hints": [
            "Treat imported raw story as input evidence: propose Bible/Outline deltas, run diagnosis-only review, and write continuity only after finalized chapters.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Raw Story Assimilation Desk",
        bible={
            "raw_story_manifest": {"source": "legacy-notes.md", "status": "reviewed"},
            "proposed_bible_delta": [{"fact": "Archive seal has a public cost", "status": "pending"}],
            "chapter_change_packages": [
                {
                    "source": "chapter_analysis",
                    "chapter_number": 6,
                    "summary": "Accepted chapter left the seal unresolved.",
                }
            ],
        },
        plan={
            "summary": "Continue only after assimilation deltas are approved.",
            "proposed_outline_delta": [{"beat": "Make public cost visible", "status": "pending"}],
            "diagnosis_only_review": [{"issue": "raw source order would skip current consequence"}],
            "finalized_chapter_writeback_policy": "Write continuity only after accepted chapter status.",
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Raw Story Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only the raw-story assimilation workflow.\n"
            "forbidden source elements\n"
            "- Do not reuse source raw order, plot facts, chapter sequence, or Bible deltas.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    missing_audit = build_remix_continuation_control_audit(
        bible={},
        plan={},
        source_pattern_pack=pattern_pack,
    )
    satisfied_audit = build_remix_continuation_control_audit(
        bible={
            "raw_story_manifest": {"source": "legacy-notes.md"},
            "proposed_bible_delta": [{"fact": "new target fact"}],
        },
        plan={
            "proposed_outline_delta": [{"beat": "target beat"}],
            "diagnosis_only_review": [{"status": "reviewed"}],
            "finalized_chapter_writeback_policy": "accepted chapters only",
        },
        source_pattern_pack=pattern_pack,
    )
    independence = build_remix_inspired_independence_audit(
        style_content=(
            "銆愬悓绫诲瀷鍒涗綔鎬诲師鍒欍€慭n- Abstract workflow only.\n"
            "銆愭簮涔﹁姘旀牱鏈€慭n- No source prose.\n"
            "銆愭簮涔︽樉鎬у厓绱犵鐢ㄦ竻鍗曘€慭n- No source plot order.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Raw story assimilation gate:" in block
        assert "raw_story_manifest" in block
        assert "proposed_bible_outline_delta" in block
        assert "diagnosis_only_review" in block
        assert "finalized_chapter_continuity_writeback" in block
        assert "approved Bible/Outline delta" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired

    assert "raw_story_import_manifest" in missing_audit["control_axes"]
    assert "proposed_bible_outline_delta" in missing_audit["control_axes"]
    assert "diagnosis_only_assimilation_review" in missing_audit["control_axes"]
    assert "finalized_chapter_continuity_writeback" in missing_audit["control_axes"]
    assert "verify_raw_story_manifest_scope" in missing_audit["acceptance_steps"]
    assert "verify_bible_outline_delta_approval" in missing_audit["acceptance_steps"]
    assert "raw_story_assimilation_warnings" in missing_audit["warnings"]
    assert "missing_raw_story_manifest" in missing_audit["raw_story_assimilation_warnings"]
    assert "missing_bible_outline_delta_proposal" in missing_audit["raw_story_assimilation_warnings"]
    assert "raw_story_assimilation_warnings" not in satisfied_audit["warnings"]

    assert "raw_story_assimilation_sequence" in independence["transfer_axes"]
    assert "target_bible_delta_namespace" in independence["required_difference_axes"]
    assert "source_plot_order_independence" in independence["required_difference_axes"]
    assert "source_raw_order_outline_clone" in independence["copy_risk_checks"]
    assert "source_plot_fact_canon_leak" in independence["copy_risk_checks"]


def test_noveldna_originality_gates_project_source_analysis_boundary_and_project_blockers():
    pattern_pack = {
        "source_novel_dna_fusion_boundary_gate_hints": [
            "Keep SourceNovelChunk content in the source-analysis layer only; fusion design reads abstract SourceNovelAnalysis, NovelDNA, FusionBlueprint, taboo terms, and risk metadata.",
        ],
        "originality_guard_project_creation_gate_hints": [
            "Require an explicit user-triggered originality check before a fusion result can create a formal project.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="NovelDNA Fusion Desk",
        bible={
            "source_analysis_layer_manifest": {"analysis_id": "src-analysis-7", "chunk_policy": "source-only"},
            "novel_dna": {"engine": "pressure + mystery", "voice": "abstract"},
            "raw_source_marker_scan": {"status": "clean"},
            "originality_guard": {
                "check_id": "og-42",
                "rights_status": "cleared_for_transform",
                "risk_level": "low",
            },
            "chapter_change_packages": [{"chapter_number": 4, "summary": "Target canon accepted a new clue."}],
        },
        plan={
            "summary": "Continue from accepted target canon only.",
            "fusion_blueprint": {"id": "fb-9", "premise": "new target premise"},
            "writing_layer_context_policy": "Novel writing receives only accepted new-project records; no SourceNovelChunk content.",
            "taboo_direct_copy_elements": ["source scene order", "source names"],
            "forbidden_similarity_terms": ["source catchphrase"],
            "create_project_originality_recheck": {"timestamp": "2026-06-15T08:00:00Z"},
            "guardrails": [{"rule": "raw source chunks stay outside drafting context"}],
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired NovelDNA Desk",
        style_content=(
            "同类型创作总原则\n"
            "- Transfer only abstract DNA and fusion contract.\n"
            "源书语气样本\n"
            "- No source prose or chunks.\n"
            "源书显性元素禁用清单\n"
            "- No source scene summaries or raw chunk ids.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    missing_audit = build_remix_continuation_control_audit(
        bible={},
        plan={},
        source_pattern_pack=pattern_pack,
    )
    satisfied_audit = build_remix_continuation_control_audit(
        bible={
            "source_analysis_layer_manifest": {"analysis_id": "src-analysis-7"},
            "novel_dna": {"engine": "target abstract engine"},
            "raw_source_marker_scan": {"status": "clean"},
            "originality_guard": {
                "check_id": "og-42",
                "rights_status": "cleared_for_transform",
                "risk_level": "low",
            },
        },
        plan={
            "fusion_blueprint": {"id": "fb-9"},
            "writing_layer_context_policy": "exclude source chunks",
            "taboo_direct_copy_elements": ["source set piece"],
            "forbidden_similarity_terms": ["source catchphrase"],
            "create_project_originality_recheck": {"timestamp": "2026-06-15T08:00:00Z"},
        },
        source_pattern_pack=pattern_pack,
    )
    independence = build_remix_inspired_independence_audit(
        style_content=(
            "同类型创作总原则\n"
            "- Abstract NovelDNA only.\n"
            "源书语气样本\n"
            "- No source prose.\n"
            "源书显性元素禁用清单\n"
            "- No SourceNovelChunk content.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "NovelDNA fusion boundary gate:" in block
        assert "source_analysis_layer_only" in block
        assert "novel_dna_fusion_blueprint_boundary" in block
        assert "writing_layer_raw_chunk_exclusion" in block
        assert "raw_source_marker_blocker" in block
        assert "Originality guard project creation gate:" in block
        assert "explicit_originality_check" in block
        assert "create_project_originality_rerun" in block
        assert "rights_status_risk_blocker" in block
        assert "forbidden_similarity_terms" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired

    assert "source_analysis_to_novel_dna_boundary" in missing_audit["control_axes"]
    assert "fusion_blueprint_writing_layer_boundary" in missing_audit["control_axes"]
    assert "raw_source_marker_blocker" in missing_audit["control_axes"]
    assert "explicit_originality_check_gate" in missing_audit["control_axes"]
    assert "create_project_originality_recheck" in missing_audit["control_axes"]
    assert "high_risk_project_creation_block" in missing_audit["control_axes"]
    assert "verify_source_novel_chunk_exclusion" in missing_audit["acceptance_steps"]
    assert "verify_novel_dna_fusion_blueprint_boundary" in missing_audit["acceptance_steps"]
    assert "rerun_originality_guard_before_project_creation" in missing_audit["acceptance_steps"]
    assert "block_high_risk_or_unresolved_rights" in missing_audit["acceptance_steps"]
    assert "source_novel_dna_fusion_warnings" in missing_audit["warnings"]
    assert "originality_guard_warnings" in missing_audit["warnings"]
    assert "missing_source_analysis_layer_manifest" in missing_audit["source_novel_dna_fusion_warnings"]
    assert "missing_novel_dna_or_fusion_blueprint" in missing_audit["source_novel_dna_fusion_warnings"]
    assert "missing_writing_layer_chunk_exclusion_policy" in missing_audit["source_novel_dna_fusion_warnings"]
    assert "missing_raw_source_marker_scan" in missing_audit["source_novel_dna_fusion_warnings"]
    assert "missing_explicit_originality_check" in missing_audit["originality_guard_warnings"]
    assert "missing_rights_status" in missing_audit["originality_guard_warnings"]
    assert "missing_originality_risk_level" in missing_audit["originality_guard_warnings"]
    assert "missing_create_project_recheck" in missing_audit["originality_guard_warnings"]
    assert "source_novel_dna_fusion_warnings" not in satisfied_audit["warnings"]
    assert "originality_guard_warnings" not in satisfied_audit["warnings"]

    assert "novel_dna_abstraction" in independence["transfer_axes"]
    assert "fusion_blueprint_transformation_contract" in independence["transfer_axes"]
    assert "target_premise_cast_world_namespace" in independence["required_difference_axes"]
    assert "forbidden_similarity_term_remap" in independence["required_difference_axes"]
    assert "source_novel_chunk_prompt_leak" in independence["copy_risk_checks"]
    assert "source_scene_summary_clone" in independence["copy_risk_checks"]
    assert "stale_originality_check_acceptance" in independence["copy_risk_checks"]


def test_six_layer_iron_law_gate_projects_consistency_brake_and_failure_block():
    pattern_pack = {
        "six_layer_iron_law_chapter_gate_hints": [
            "Require truth file, state tracking, knowledge graph, outline anchors, reverse-brake checks, and block acceptance when a gate fails.",
        ],
    }

    continuation = build_remix_continuation_context_block(
        project_title="Iron Law Continuation Desk",
        bible={
            "truth_file": {"seal_rule": "public trust cost is canonical"},
            "state_tracking": [{"character": "Lin", "knowledge": "seal cost"}],
            "knowledge_graph": [{"subject": "seal", "relation": "costs", "object": "trust"}],
            "outline_anchors": [{"id": "A-12", "beat": "public cost before solution"}],
            "reverse_brake": [{"label": "no premature archive unlock", "status": "active"}],
            "chapter_change_packages": [{"chapter_number": 12, "summary": "Seal cost became public."}],
        },
        plan={
            "summary": "Repair any failed gate before accepting chapter 13.",
            "gate_failure_policy": "failed gate blocks chapter acceptance",
        },
        source_pattern_pack=pattern_pack,
    )
    inspired = build_remix_inspired_context_block(
        project_title="Inspired Iron Law Desk",
        style_content=(
            "same-type creation source voice\n"
            "- Learn only six-layer consistency and reverse-brake review.\n"
            "forbidden source elements\n"
            "- Do not reuse source truth-file facts, outline anchor order, or brake labels.\n"
        ),
        source_pattern_pack=pattern_pack,
    )
    missing_audit = build_remix_continuation_control_audit(
        bible={},
        plan={},
        source_pattern_pack=pattern_pack,
    )
    satisfied_audit = build_remix_continuation_control_audit(
        bible={
            "truth_file": {"target_fact": "fact"},
            "state_tracking": [{"character": "Lin"}],
            "knowledge_graph": [{"subject": "Lin"}],
            "outline_anchors": [{"id": "target-A"}],
            "reverse_brake": [{"label": "target-brake"}],
        },
        plan={"gate_failure_policy": "failed gate blocks acceptance"},
        source_pattern_pack=pattern_pack,
    )
    independence = build_remix_inspired_independence_audit(
        style_content=(
            "銆愬悓绫诲瀷鍒涗綔鎬诲師鍒欍€慭n- Abstract consistency workflow only.\n"
            "銆愭簮涔﹁姘旀牱鏈€慭n- No source prose.\n"
            "銆愭簮涔︽樉鎬у厓绱犵鐢ㄦ竻鍗曘€慭n- No source anchors.\n"
        ),
        source_pattern_pack=pattern_pack,
    )

    for block in (continuation, inspired):
        assert "Six-layer Iron Law consistency gate:" in block
        assert "truth_file_state_tracking" in block
        assert "knowledge_graph_outline_anchors" in block
        assert "reverse_brake_anti_premature_resolution" in block
        assert "failed_gate_blocks_chapter_acceptance" in block
    assert "continuation_boundary" in continuation
    assert "same_type_boundary" in inspired

    assert "six_layer_truth_state_graph" in missing_audit["control_axes"]
    assert "outline_anchor_reverse_brake" in missing_audit["control_axes"]
    assert "failed_gate_chapter_acceptance_block" in missing_audit["control_axes"]
    assert "verify_six_layer_truth_state_graph" in missing_audit["acceptance_steps"]
    assert "verify_failed_gate_blocks_acceptance" in missing_audit["acceptance_steps"]
    assert "six_layer_iron_law_warnings" in missing_audit["warnings"]
    assert "missing_truth_file_surface" in missing_audit["six_layer_iron_law_warnings"]
    assert "missing_failed_gate_block_policy" in missing_audit["six_layer_iron_law_warnings"]
    assert "six_layer_iron_law_warnings" not in satisfied_audit["warnings"]

    assert "six_layer_consistency_review_shape" in independence["transfer_axes"]
    assert "anti_premature_resolution_brake" in independence["transfer_axes"]
    assert "truth_file_fact_namespace" in independence["required_difference_axes"]
    assert "outline_anchor_order" in independence["required_difference_axes"]
    assert "source_truth_file_clone" in independence["copy_risk_checks"]
    assert "source_reverse_brake_label_clone" in independence["copy_risk_checks"]
