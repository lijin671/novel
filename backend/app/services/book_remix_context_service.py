"""Build remix continuation context blocks for prompt injection."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book_remix_bible import BookRemixBible, BookRemixContinuationPlan
from app.models.project import Project
from app.services.source_discovery_service import source_discovery_service
from app.services.source_pattern_pack_prompt import render_source_pattern_pack_digest


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def build_remix_continuation_progress_summary(
    *,
    packages: Any,
    plan: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build a structured whole-book continuation progress summary."""
    ordered_packages = _sort_by_chapter_asc(_chapter_analysis_packages(packages))
    chapter_numbers = [_int_or_none(package.get("chapter_number")) for package in ordered_packages]
    chapter_numbers = [number for number in chapter_numbers if number is not None]

    return {
        "package_count": len(ordered_packages),
        "chapter_range": _chapter_range_payload(chapter_numbers),
        "timeline_progression": _timeline_progression_payload(ordered_packages),
        "latest_character_states": _latest_character_state_payload(ordered_packages, max_items=8),
        "emotional_progression": _emotional_progression_payload(ordered_packages, max_items=12),
        "resolved_hooks": _hook_status_summary(ordered_packages)[0],
        "open_hooks": _hook_status_summary(ordered_packages)[1],
        "completed_plan_beats": _completed_plan_beats(ordered_packages, plan=plan, max_items=12),
        "pending_plan_beats": _pending_plan_beats(plan=plan, max_items=12),
    }


def build_remix_continuation_control_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build chapter-level production control checks for continuation prompts."""
    chapter_packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    chapter_numbers = [_int_or_none(package.get("chapter_number")) for package in chapter_packages]
    chapter_numbers = [number for number in chapter_numbers if number is not None]
    chapter_gaps = _chapter_sequence_gaps(chapter_numbers)

    timeline = _as_dict_list(bible.get("timeline"))
    latest_machine_timeline = _latest_chapter_analysis_items(timeline, max_items=99)
    timeline_anchor_count = len(latest_machine_timeline) if latest_machine_timeline else len(timeline)
    timeline_chapters = [
        _chapter_value(item, ("chapter_number", "last_chapter_number"))
        for item in latest_machine_timeline
    ]
    timeline_chapters = [number for number in timeline_chapters if number is not None]
    latest_chapter_number = chapter_numbers[-1] if chapter_numbers else (max(timeline_chapters) if timeline_chapters else None)

    character_cards = _as_dict_list(bible.get("character_cards"))
    open_hooks = _status_items(_as_dict_list(bible.get("foreshadows")), done=False, max_items=99)
    pending_plan_beats = _pending_plan_beats(plan=plan, max_items=99)
    pending_priority_hooks = _status_items(
        _as_dict_list(plan.get("priority_hooks")) if plan else [],
        done=False,
        max_items=99,
    )
    plan_guardrails = _as_dict_list(plan.get("guardrails")) if plan else []
    style_signature = bible.get("style_signature")

    control_axes = [
        "checkpoint_resume_state",
        "accepted_memory_surface",
        "character_knowledge_state",
        "timeline_chronology",
        "emotional_arc_delta",
        "foreshadow_debt",
        "parallel_plot_thread_sync",
    ]
    acceptance_steps = [
        "select_context",
        "draft_chapter",
        "review_continuity",
        "repair_failures",
        "accept_chapter",
        "write_back_memory",
    ]
    pattern_names = _source_pattern_names(source_pattern_pack)

    if pattern_names.intersection(
        {
            "automatic_director_checkpoint_chain",
            "director_stage_checkpoint_gate",
            "role_asset_quality_review_gate",
        }
    ):
        control_axes.extend([
            "director_stage_checkpoint",
            "role_asset_quality_stop",
        ])
        acceptance_steps.extend([
            "stage_checkpoint_review",
            "stop_on_unstable_role_assets",
        ])
    if pattern_names.intersection(
        {
            "inspectable_memory_workspace_gate",
            "memory_aware_chapter_workspace",
            "dashboard_task_quality_resume_gate",
        }
    ):
        control_axes.extend([
            "session_artifact_trace",
            "editable_memory_bank_review",
        ])
    if pattern_names.intersection(
        {
            "semantic_context_consistency_gate",
            "semantic_long_context_search",
            "cjk_bm25_context_retrieval_gate",
        }
    ):
        control_axes.append("semantic_context_match")
    if pattern_names.intersection(
        {
            "multi_thread_knowledge_timeline_gate",
            "character_knowledge_timeline_gate",
            "pov_character_thread_filter_gate",
        }
    ):
        control_axes.extend([
            "pov_knowledge_timeline",
            "thread_convergence_chronology",
        ])
    if "confirmed_action_audit_recovery_gate" in pattern_names:
        control_axes.extend([
            "confirmed_action_artifact_evidence",
            "critical_finding_recovery",
        ])
        acceptance_steps.extend([
            "verify_action_artifacts",
            "resolve_critical_findings",
        ])
    if "planner_writer_evaluator_editor_saga_gate" in pattern_names:
        control_axes.extend([
            "role_separated_findings",
            "canon_promotion_decision",
        ])
        acceptance_steps.append("approve_or_reject_canon_promotion")
    if pattern_names.intersection(
        {
            "story_state_output_contract_gate",
            "markdown_frontmatter_continuity_engine_gate",
        }
    ):
        control_axes.extend([
            "structured_state_delta_contract",
            "frontmatter_continuity_metadata",
        ])
    if pattern_names.intersection(
        {
            "craft_scene_concrete_finding_revision_gate",
            "anti_hallucination_strand_weave_review_gate",
            "ai_flavor_template_shell_cleanup_gate",
        }
    ):
        control_axes.extend([
            "concrete_revision_finding",
            "strand_weave_hallucination_review",
            "template_shell_cleanup",
        ])
        acceptance_steps.append("final_craft_cleanup_scan")
    include_time_trace_progress = (
        "progress_report_continuity_writeback_gate" in pattern_names
        and "narrative_time_age_trace_gate" in pattern_names
    )
    progress_report_gaps = _chapter_progress_report_gaps(
        chapter_packages,
        include_time_trace=include_time_trace_progress,
    )
    if "progress_report_continuity_writeback_gate" in pattern_names:
        control_axes.append("chapter_progress_report_completeness")
        acceptance_steps.append("verify_progress_report_fields")
    if include_time_trace_progress:
        control_axes.append("narrative_time_age_progress_writeback")
        acceptance_steps.append("verify_narrative_time_age_writeback")
    if "portable_story_project_structure_gate" in pattern_names:
        control_axes.extend([
            "portable_project_file_manifest",
            "startup_status_open_thread_scan",
            "story_bible_north_star",
            "character_want_need_wound_voice",
            "world_rule_cost_research_custody",
            "continuity_decision_log_writeback",
        ])
        acceptance_steps.extend([
            "verify_project_memory_startup_packet",
            "verify_story_bible_project_memory_axes",
            "verify_no_overwrite_manuscript_patch_scope",
        ])
    if "seed_to_bible_foundation_loop_gate" in pattern_names:
        control_axes.extend([
            "foundation_score_loop_review",
            "weakest_dimension_regeneration_trace",
            "foundation_keep_discard_restore_decision",
        ])
        acceptance_steps.append("verify_foundation_loop_score_review")
    if "layered_story_bible_artifact_contract_gate" in pattern_names:
        control_axes.extend([
            "layered_story_bible_artifact_contract",
            "story_layer_dependency_order",
        ])
        acceptance_steps.append("verify_layered_story_bible_artifacts")
    if "premise_structure_hook_payoff_gate" in pattern_names:
        control_axes.extend([
            "premise_structure_stress_test",
            "hook_payoff_matrix_review",
        ])
        acceptance_steps.append("verify_premise_structure_hook_payoff")
    if "scene_goal_obstacle_cost_exit_gate" in pattern_names:
        control_axes.append("scene_goal_obstacle_cost_exit_state")
        acceptance_steps.append("verify_scene_goal_obstacle_cost_exit")
    if "revision_finding_patch_strategy_gate" in pattern_names:
        control_axes.extend([
            "revision_finding_severity_triage",
            "least_destructive_patch_scope",
        ])
        acceptance_steps.append("verify_revision_findings_patch_scope")
    if "opening_ending_hook_integrity_gate" in pattern_names:
        control_axes.extend([
            "opening_hook_type_selection",
            "ending_hook_job_integrity",
            "fake_cliffhanger_integrity",
        ])
        acceptance_steps.append("verify_opening_ending_hook_integrity")
    if "anti_ai_naturalness_texture_gate" in pattern_names:
        control_axes.append("anti_ai_texture_naturalness_review")
        acceptance_steps.append("verify_anti_ai_naturalness_texture")
    if "post_draft_review_checklist_gate" in pattern_names:
        control_axes.extend([
            "post_draft_review_checklist",
            "mobile_readability_review",
            "least_destructive_repair_scope",
        ])
        acceptance_steps.extend([
            "verify_post_draft_review_checklist",
            "verify_mobile_readability_before_acceptance",
            "verify_smallest_failing_artifact_repair",
        ])
    if "canonkit_local_canon_drift_context_pack_gate" in pattern_names:
        control_axes.extend([
            "local_first_canon_drift_check",
            "focused_scene_context_pack",
            "character_age_year_consistency",
            "missing_entity_reference_review",
            "relationship_symmetry_review",
            "scene_state_conflict_review",
        ])
        acceptance_steps.extend([
            "verify_canonkit_drift_detectors",
            "verify_focused_scene_context_pack",
        ])
    if "genre_promise_contract_matrix_gate" in pattern_names:
        control_axes.extend([
            "genre_promise_contract_matrix",
            "genre_trope_twist_boundary",
            "emotional_aftertaste_target",
        ])
        acceptance_steps.append("verify_genre_promise_contract_matrix")
    if "subgenre_specific_ledger_gate" in pattern_names:
        control_axes.extend([
            "subgenre_specific_active_ledgers",
            "genre_payoff_debt_custody",
            "same_type_ledger_independence",
        ])
        acceptance_steps.append("verify_subgenre_specific_ledgers")
    if "five_question_intake_story_promise_gate" in pattern_names:
        control_axes.append("five_question_intake_packet")
        acceptance_steps.append("verify_five_question_intake_packet")
    if "universal_export_clean_manuscript_gate" in pattern_names:
        control_axes.append("clean_manuscript_export_scope")
        acceptance_steps.append("verify_clean_export_scope")
    if "minimal_rollback_repair_scope_gate" in pattern_names:
        control_axes.append("minimal_rollback_repair_scope")
        acceptance_steps.append("verify_minimal_rollback_scope")
    if "local_first_provider_boundary_authoring_gate" in pattern_names:
        control_axes.append("local_first_authoring_provider_boundary")
        acceptance_steps.append("verify_local_first_provider_boundary")
    if "suggestion_card_nonoverwrite_revision_gate" in pattern_names:
        control_axes.append("suggestion_card_accept_reject_queue")
        acceptance_steps.append("verify_suggestion_card_acceptance_boundary")
    if "book_view_import_export_manifest_gate" in pattern_names:
        control_axes.append("book_view_import_export_manifest")
        acceptance_steps.append("verify_book_view_import_export_manifest")
    if pattern_names.intersection({
        "distilled_novel_toolbox_platform_compliance_gate",
        "distilled_novel_toolbox_human_polish_boundary_gate",
    }):
        control_axes.extend([
            "market_fit_card",
            "platform_policy_verification",
            "compliance_review_packet",
            "human_polish_boundary",
            "prompt_body_import_policy",
        ])
        acceptance_steps.extend([
            "verify_platform_policy_current",
            "verify_compliance_review_packet",
            "verify_no_detection_evasion_or_prompt_body_import",
        ])
    if pattern_names.intersection({
        "novel_studio_graph_memory_continuity_gate",
        "novel_studio_accepted_chapter_writeback_gate",
    }):
        control_axes.extend([
            "accepted_chapter_writeback_surface",
            "graph_fact_triple_consistency",
            "character_state_versioning",
            "timeline_event_ordering",
            "contradiction_checklist_review",
            "hybrid_retrieval_context_pack",
        ])
        acceptance_steps.extend([
            "verify_accepted_chapter_writeback",
            "verify_graph_fact_triples",
            "verify_character_state_timeline_conflicts",
            "verify_hybrid_retrieval_pack_scope",
        ])
    if pattern_names.intersection({
        "versioned_scene_fact_review_pipeline_gate",
        "novelforge_version_safe_human_review_gate",
    }):
        control_axes.extend([
            "scene_version_lineage",
            "fact_approval_queue",
            "focused_memory_reference_asset_retrieval",
            "continuity_reviewreport_findings",
            "accepted_export_readiness",
        ])
        acceptance_steps.extend([
            "verify_scene_version_lineage",
            "approve_fact_extraction_before_memory",
            "verify_reference_asset_retrieval_scope",
            "verify_continuity_reviewreport_findings",
        ])
    if "chapter_progressive_disassembly_checkpoint_gate" in pattern_names:
        control_axes.extend([
            "source_chapter_analysis_coverage",
            "disassembly_checkpoint_ledger",
            "qa_citation_jump_trace",
        ])
        acceptance_steps.append("verify_disassembly_checkpoint_coverage")
    if pattern_names.intersection({"mode_contract_generation_gate", "universal_novel_mode_contract_gate"}):
        control_axes.extend([
            "selected_output_mode_priority",
            "visible_creative_axis_contract",
            "under_length_rewrite_boundary",
        ])
        acceptance_steps.append("verify_mode_contract_axes")
    if "chapter_contract_scene_beat_gate" in pattern_names:
        control_axes.extend([
            "chapter_contract_completeness",
            "scene_beat_exit_state_contract",
        ])
        acceptance_steps.append("verify_chapter_contract_scene_beats")
    if "reader_promise_micro_payoff_gate" in pattern_names:
        control_axes.append("reader_promise_micro_payoff_contract")
        acceptance_steps.append("verify_reader_micro_payoff")
    if "revision_order_natural_prose_gate" in pattern_names:
        control_axes.append("revision_order_natural_prose_review")
        acceptance_steps.append("verify_revision_order_before_line_polish")
    if "reader_pull_fresh_reader_gate" in pattern_names:
        control_axes.append("reader_pull_fresh_reader_test")
        acceptance_steps.append("verify_reader_pull_answers")
    if "slima_book_mcp_beta_reader_file_gate" in pattern_names:
        control_axes.extend([
            "book_file_scope_envelope",
            "beta_reader_persona_feedback_custody",
        ])
        acceptance_steps.append("verify_beta_reader_feedback_review_state")
    if "novelwriter_live_manuscript_analytics_gate" in pattern_names:
        control_axes.extend([
            "live_manuscript_diagnostic_layers",
            "advisory_scene_suggestion_review",
        ])
        acceptance_steps.append("verify_live_diagnostics_review_state")
    if "kindling_local_outline_reference_import_gate" in pattern_names:
        control_axes.append("visible_outline_import_export_custody")
        acceptance_steps.append("verify_outline_import_export_custody")
    if "dialogoi_filetype_rag_novel_project_gate" in pattern_names:
        control_axes.extend([
            "filetype_scoped_retrieval_evidence",
            "hybrid_search_source_file_custody",
        ])
        acceptance_steps.append("verify_filetype_retrieval_scope")
    if "scrivener_mcp_direct_project_edit_boundary_gate" in pattern_names:
        control_axes.append("direct_project_edit_boundary_report")
        acceptance_steps.append("verify_direct_project_patch_scope")
    if "vector_story_frame_coordinate_gate" in pattern_names:
        control_axes.append("story_frame_coordinate_contract")
        acceptance_steps.append("verify_frame_coordinate_contract")
    if "setting_runtime_document_architecture_gate" in pattern_names:
        control_axes.append("setting_document_session_packet")
        acceptance_steps.append("verify_setting_document_session_packet")
    if "inkfoundry_state_db_redteam_voice_sandbox_gate" in pattern_names:
        control_axes.extend([
            "state_db_over_vector_review",
            "redteam_voice_sandbox_findings",
        ])
        acceptance_steps.append("verify_state_db_redteam_voice_review")
    if pattern_names.intersection({
        "story_bible_constitution_source_gate",
        "scene_outline_approval_status_gate",
        "pov_information_asymmetry_schedule_gate",
        "pacing_arc_polish_pass_gate",
    }):
        if "story_bible_constitution_source_gate" in pattern_names:
            control_axes.append("story_bible_constitution_authority")
        if "scene_outline_approval_status_gate" in pattern_names:
            control_axes.append("scene_outline_approval_status")
            acceptance_steps.append("verify_scene_outline_approval")
        if "pov_information_asymmetry_schedule_gate" in pattern_names:
            control_axes.append("pov_information_asymmetry_schedule")
            acceptance_steps.append("verify_pov_information_asymmetry")
        if "pacing_arc_polish_pass_gate" in pattern_names:
            control_axes.append("pacing_arc_polish_pass")
            acceptance_steps.append("verify_checklist_pass_before_polish")
    if "capture_distillation_production_gate" in pattern_names:
        control_axes.extend([
            "capture_distillation_production_stage_boundary",
            "scene_card_external_internal_spine",
            "draft_critique_fixspec_revision_chain",
            "archivist_canon_promotion_telemetry",
        ])
        acceptance_steps.append("verify_story_foundry_production_handoff")
    if "genre_inspiration_budget_library_gate" in pattern_names:
        control_axes.extend([
            "genre_reader_promise_matrix",
            "trope_option_budget",
        ])
        acceptance_steps.append("verify_genre_promise_independence")
    if "volume_antipattern_dependency_graph_gate" in pattern_names:
        control_axes.extend([
            "volume_escalation_ladder",
            "event_dependency_graph",
        ])
        acceptance_steps.append("verify_volume_dependency_edges")
    if "webnovel_genre_tracker_gate" in pattern_names:
        control_axes.extend([
            "webnovel_genre_tracker_state",
            "chapter_gap_tracker",
            "cliffhanger_rotation_review",
            "stale_character_review",
        ])
        acceptance_steps.append("verify_genre_tracker_warnings")
    if "entity_mention_arc_timeline_gate" in pattern_names:
        control_axes.extend([
            "entity_mention_timeline",
            "arc_entity_appearance_gap",
        ])
        acceptance_steps.append("verify_entity_arc_timeline")

    genre_tracker_warnings = (
        _webnovel_genre_tracker_warnings(bible=bible, plan=plan, max_items=8)
        if "webnovel_genre_tracker_gate" in pattern_names
        else []
    )
    entity_arc_timeline_risks = (
        _entity_mention_arc_timeline_risks(bible=bible, plan=plan, max_items=8)
        if "entity_mention_arc_timeline_gate" in pattern_names
        else []
    )
    disassembly_checkpoint_audit = (
        _chapter_progressive_disassembly_checkpoint_audit(bible=bible, max_items=8)
        if "chapter_progressive_disassembly_checkpoint_gate" in pattern_names
        else _empty_disassembly_checkpoint_audit()
    )
    mode_contract_audit = (
        _mode_contract_generation_audit(bible=bible, plan=plan, max_items=12)
        if pattern_names.intersection({"mode_contract_generation_gate", "universal_novel_mode_contract_gate"})
        else _empty_mode_contract_generation_audit()
    )
    portable_project_memory_audit = (
        _portable_project_memory_audit(bible=bible, plan=plan, max_items=12)
        if "portable_story_project_structure_gate" in pattern_names
        else _empty_portable_project_memory_audit()
    )
    chapter_contract_audit = (
        _universal_chapter_contract_audit(
            bible=bible,
            plan=plan,
            pattern_names=pattern_names,
            max_items=12,
        )
        if pattern_names.intersection(
            {
                "chapter_contract_scene_beat_gate",
                "reader_promise_micro_payoff_gate",
                "revision_order_natural_prose_gate",
            }
        )
        else _empty_universal_chapter_contract_audit()
    )
    production_handoff_audit = (
        _story_foundry_production_handoff_audit(bible=bible, plan=plan, max_items=12)
        if "capture_distillation_production_gate" in pattern_names
        else _empty_story_foundry_production_handoff_audit()
    )
    reader_pull_audit = (
        _reader_pull_fresh_reader_audit(bible=bible, max_items=12)
        if "reader_pull_fresh_reader_gate" in pattern_names
        else _empty_reader_pull_fresh_reader_audit()
    )
    spec_kit_fiction_audit = (
        _spec_kit_fiction_scene_task_audit(bible=bible, plan=plan, max_items=12)
        if pattern_names.intersection({
            "story_bible_constitution_source_gate",
            "scene_outline_approval_status_gate",
            "pov_information_asymmetry_schedule_gate",
            "pacing_arc_polish_pass_gate",
        })
        else _empty_spec_kit_fiction_scene_task_audit()
    )
    hook_naturalness_audit = (
        _universal_hook_naturalness_audit(
            bible=bible,
            plan=plan,
            pattern_names=pattern_names,
            max_items=12,
        )
        if pattern_names.intersection({
            "opening_ending_hook_integrity_gate",
            "anti_ai_naturalness_texture_gate",
        })
        else _empty_universal_hook_naturalness_audit()
    )
    post_draft_review_audit = (
        _universal_post_draft_review_audit(
            bible=bible,
            plan=plan,
            max_items=12,
        )
        if "post_draft_review_checklist_gate" in pattern_names
        else {"warnings": []}
    )
    canonkit_context_pack_audit = (
        _canonkit_local_canon_drift_context_pack_audit(
            bible=bible,
            plan=plan,
            max_items=12,
        )
        if "canonkit_local_canon_drift_context_pack_gate" in pattern_names
        else {"warnings": []}
    )
    genre_promise_contract_audit = (
        _genre_promise_contract_matrix_audit(bible=bible, plan=plan, max_items=12)
        if "genre_promise_contract_matrix_gate" in pattern_names
        else {"warnings": []}
    )
    subgenre_ledger_audit = (
        _subgenre_specific_ledger_audit(bible=bible, plan=plan, max_items=12)
        if "subgenre_specific_ledger_gate" in pattern_names
        else {"warnings": []}
    )
    intake_export_rollback_audit = (
        _universal_intake_export_rollback_audit(
            bible=bible,
            plan=plan,
            pattern_names=pattern_names,
            max_items=12,
        )
        if pattern_names.intersection(
            {
                "five_question_intake_story_promise_gate",
                "universal_export_clean_manuscript_gate",
                "minimal_rollback_repair_scope_gate",
            }
        )
        else {"warnings": []}
    )
    local_first_authoring_audit = (
        _local_first_authoring_revision_audit(
            bible=bible,
            plan=plan,
            pattern_names=pattern_names,
            max_items=12,
        )
        if pattern_names.intersection(
            {
                "local_first_provider_boundary_authoring_gate",
                "suggestion_card_nonoverwrite_revision_gate",
                "book_view_import_export_manifest_gate",
            }
        )
        else {"warnings": []}
    )
    warnings: list[str] = []
    if not chapter_packages:
        warnings.append("missing_chapter_change_packages")
    if chapter_gaps:
        warnings.append("chapter_sequence_gaps")
    if "progress_report_continuity_writeback_gate" in pattern_names and progress_report_gaps:
        warnings.append("chapter_progress_report_missing_fields")
    if genre_tracker_warnings:
        warnings.append("webnovel_genre_tracker_warnings")
    if entity_arc_timeline_risks:
        warnings.append("entity_arc_timeline_risks")
    if disassembly_checkpoint_audit["warnings"]:
        warnings.append("disassembly_checkpoint_warnings")
    if mode_contract_audit["warnings"]:
        warnings.append("mode_contract_warnings")
    if portable_project_memory_audit["warnings"]:
        warnings.append("portable_project_memory_warnings")
    if chapter_contract_audit["warnings"]:
        warnings.append("chapter_contract_warnings")
    if production_handoff_audit["warnings"]:
        warnings.append("production_handoff_warnings")
    if reader_pull_audit["warnings"]:
        warnings.append("reader_pull_warnings")
    if spec_kit_fiction_audit["warnings"]:
        warnings.append("spec_kit_fiction_warnings")
    if hook_naturalness_audit["warnings"]:
        warnings.append("hook_naturalness_warnings")
    if post_draft_review_audit["warnings"]:
        warnings.append("post_draft_review_warnings")
    if canonkit_context_pack_audit["warnings"]:
        warnings.append("canonkit_context_pack_warnings")
    if genre_promise_contract_audit["warnings"]:
        warnings.append("genre_promise_contract_warnings")
    if subgenre_ledger_audit["warnings"]:
        warnings.append("subgenre_ledger_warnings")
    if intake_export_rollback_audit["warnings"]:
        warnings.append("intake_export_rollback_warnings")
    if local_first_authoring_audit["warnings"]:
        warnings.append("local_first_authoring_warnings")
    if not character_cards:
        warnings.append("missing_character_cards")
    if not timeline_anchor_count:
        warnings.append("missing_timeline_anchors")
    if plan and not pending_plan_beats:
        warnings.append("missing_pending_plan_beats")
    if not plan:
        warnings.append("missing_continuation_plan")
    if open_hooks and not pending_plan_beats and not pending_priority_hooks:
        warnings.append("open_hooks_without_pending_plan_target")
    if not plan_guardrails:
        warnings.append("missing_plan_guardrails")
    if not isinstance(style_signature, dict) or not style_signature:
        warnings.append("missing_style_signature")

    return {
        "chapter_package_count": len(chapter_packages),
        "latest_chapter_number": latest_chapter_number,
        "chapter_gap_count": len(chapter_gaps),
        "chapter_gaps": chapter_gaps,
        "timeline_anchor_count": timeline_anchor_count,
        "character_card_count": len(character_cards),
        "open_hook_count": len(open_hooks),
        "pending_plan_beat_count": len(pending_plan_beats),
        "pending_priority_hook_count": len(pending_priority_hooks),
        "plan_guardrail_count": len(plan_guardrails),
        "has_style_signature": isinstance(style_signature, dict) and bool(style_signature),
        "chapter_progress_report_gap_count": len(progress_report_gaps),
        "chapter_progress_report_gaps": progress_report_gaps,
        "genre_tracker_warnings": genre_tracker_warnings,
        "entity_arc_timeline_risks": entity_arc_timeline_risks,
        "source_analysis_coverage_percent": disassembly_checkpoint_audit["source_analysis_coverage_percent"],
        "missing_source_analysis_chapters": disassembly_checkpoint_audit["missing_source_analysis_chapters"],
        "disassembly_checkpoint_warnings": disassembly_checkpoint_audit["warnings"],
        "mode_contract_axes": mode_contract_audit["axes"],
        "mode_contract_warnings": mode_contract_audit["warnings"],
        "portable_project_memory_warnings": portable_project_memory_audit["warnings"],
        "chapter_contract_warnings": chapter_contract_audit["warnings"],
        "production_handoff_warnings": production_handoff_audit["warnings"],
        "reader_pull_warnings": reader_pull_audit["warnings"],
        "spec_kit_fiction_warnings": spec_kit_fiction_audit["warnings"],
        "hook_naturalness_warnings": hook_naturalness_audit["warnings"],
        "post_draft_review_warnings": post_draft_review_audit["warnings"],
        "canonkit_context_pack_warnings": canonkit_context_pack_audit["warnings"],
        "genre_promise_contract_warnings": genre_promise_contract_audit["warnings"],
        "subgenre_ledger_warnings": subgenre_ledger_audit["warnings"],
        "intake_export_rollback_warnings": intake_export_rollback_audit["warnings"],
        "local_first_authoring_warnings": local_first_authoring_audit["warnings"],
        "control_axes": _dedupe_ordered(control_axes),
        "acceptance_steps": _dedupe_ordered(acceptance_steps),
        "warnings": warnings,
    }


def build_remix_continuation_context_block(
    *,
    project_title: str,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]] = None,
) -> str:
    """Render a stable prompt block from confirmed remix bible and current plan."""
    normalized_title = (project_title or "").strip() or "Untitled Project"
    lines: list[str] = [
        "【Remix Continuation Canon】",
        f"Project: {normalized_title}",
        "Apply these continuity constraints before writing any new outline or chapter.",
    ]

    _append_source_pattern_pack_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_rights_provenance_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_entity_redaction_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_context_activation_audit_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )
    _append_continuation_control_contract_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )
    _append_universal_novel_workflow_contract_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_universal_project_memory_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_seed_to_bible_foundation_loop_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_universal_deep_planning_revision_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_genre_promise_contract_matrix_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_subgenre_specific_ledger_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_universal_intake_export_rollback_gate_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_local_first_authoring_revision_gate_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_universal_hook_naturalness_gate_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_universal_post_draft_review_gate_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_novelforge_version_safe_scene_fact_pipeline_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_distilled_novel_toolbox_platform_compliance_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_novel_studio_graph_memory_continuity_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_mode_contract_generation_audit_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )
    _append_universal_next_chapter_scaffold_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )
    _append_universal_progress_report_completeness_gate_section(
        lines=lines,
        bible=bible,
        source_pattern_pack=source_pattern_pack,
    )
    _append_universal_reader_pull_fresh_reader_gate_section(
        lines=lines,
        bible=bible,
        source_pattern_pack=source_pattern_pack,
    )
    _append_book_mcp_beta_reader_file_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_live_diagnostics_outline_import_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_filetype_rag_project_edit_boundary_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_frame_setting_state_runtime_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )
    _append_speckit_fiction_scene_task_audit_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )
    _append_story_foundry_production_handoff_gate_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )
    _append_truth_file_write_next_state_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_action_review_canonization_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_scene_graph_review_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_plotgrid_reveal_branch_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_acceptance_loop_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_manuscript_structure_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_inspectable_rewrite_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_production_review_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_consistency_style_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_research_multimodal_experiment_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_serialized_continuity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_story_quality_evaluation_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_reader_market_feedback_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_trope_independence_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_genre_arc_style_governance_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_delivery_packaging_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_ebook_quality_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_agentic_editorial_craft_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_chinese_longform_control_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_bookrun_skill_protocol_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_project_workbench_memory_diversity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_interactive_narrative_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_copy_similarity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_near_duplicate_semantic_dedup_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_text_analysis_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_stylometry_style_overfit_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_copyedit_prose_lint_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_chinese_text_processing_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_import_extraction_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_literary_event_graph_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_segmentation_summary_topic_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_eval_observability_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_long_output_reward_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_creative_writing_benchmark_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_story_generation_pipeline_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_deconstruction_memory_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_chapter_progressive_disassembly_checkpoint_section(
        lines=lines,
        bible=bible,
        source_pattern_pack=source_pattern_pack,
    )
    _append_canon_graph_retrieval_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_story_bible_continuity_qa_audit_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
        mode="continuation",
    )

    world_rules = bible.get("world_rules")
    if isinstance(world_rules, dict) and world_rules:
        lines.append("")
        lines.append("World rules to preserve:")
        for key, value in list(world_rules.items())[:12]:
            lines.append(f"- {key}: {_truncate(str(value), 220)}")

    _append_dict_section(
        lines=lines,
        title="Hard constraints",
        items=bible.get("hard_constraints"),
        preferred_keys=("rule", "constraint", "content", "name"),
        max_items=12,
    )

    character_cards = _as_dict_list(bible.get("character_cards"))
    _append_dict_section(
        lines=lines,
        title="Character continuity cards",
        items=character_cards,
        preferred_keys=("name", "role", "goal", "summary", "trait", "identity"),
        max_items=12,
    )
    _append_character_update_section(lines=lines, cards=character_cards, max_items=12)

    _append_dict_section(
        lines=lines,
        title="Organizations to preserve",
        items=bible.get("organizations"),
        preferred_keys=("name", "role", "summary", "status", "relationship"),
        max_items=12,
    )

    _append_style_signature_section(
        lines=lines,
        style_signature=bible.get("style_signature"),
    )

    _append_dict_section(
        lines=lines,
        title="Conflict and emotion arcs",
        items=bible.get("conflicts"),
        preferred_keys=("name", "conflict", "summary", "status", "pressure"),
        max_items=12,
    )

    timeline = _as_dict_list(bible.get("timeline"))
    _append_dict_section(
        lines=lines,
        title="Latest machine timeline",
        items=_latest_chapter_analysis_items(timeline, max_items=10),
        preferred_keys=("event", "summary", "milestone", "impact"),
        max_items=10,
    )
    _append_dict_section(
        lines=lines,
        title="Manual timeline anchors",
        items=_manual_items(timeline, max_items=6),
        preferred_keys=("event", "milestone", "time", "date", "summary", "impact"),
        max_items=6,
    )
    if not _latest_chapter_analysis_items(timeline, max_items=1) and not _manual_items(timeline, max_items=1):
        _append_dict_section(
            lines=lines,
            title="Timeline anchors",
            items=timeline,
            preferred_keys=("event", "milestone", "time", "date", "summary", "impact"),
            max_items=12,
        )

    _append_dict_section(
        lines=lines,
        title="Story arcs to preserve",
        items=bible.get("story_arcs"),
        preferred_keys=("name", "arc", "summary", "goal"),
        max_items=12,
    )

    chapter_change_packages = _chapter_analysis_packages(bible.get("chapter_change_packages"))
    _append_whole_book_progress_section(
        lines=lines,
        packages=chapter_change_packages,
        plan=plan,
    )
    _append_chapter_change_package_section(
        lines=lines,
        packages=chapter_change_packages,
        max_items=5,
    )
    _append_continuity_question_control_section(
        lines=lines,
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )

    foreshadows = _as_dict_list(bible.get("foreshadows"))
    _append_dict_section(
        lines=lines,
        title="Open hooks",
        items=_status_items(foreshadows, done=False, max_items=10),
        preferred_keys=("hook", "title", "content", "summary"),
        max_items=10,
    )
    _append_dict_section(
        lines=lines,
        title="Resolved hooks",
        items=_status_items(foreshadows, done=True, max_items=8),
        preferred_keys=("hook", "title", "content", "summary"),
        max_items=8,
    )
    if not foreshadows:
        _append_dict_section(
            lines=lines,
            title="Foreshadows and unresolved hooks",
            items=foreshadows,
            preferred_keys=("hook", "title", "content", "summary"),
            max_items=12,
        )

    if plan:
        summary = str(plan.get("summary") or "").strip()
        if summary:
            lines.append("")
            lines.append(f"Current continuation strategy: {summary}")
        _append_dict_section(
            lines=lines,
            title="Stage goals",
            items=plan.get("stage_goals"),
            preferred_keys=("goal", "summary", "content", "name"),
            max_items=8,
        )

        beats = _as_dict_list(plan.get("beats"))
        _append_dict_section(
            lines=lines,
            title="Pending planned beats",
            items=_status_items(beats, done=False, max_items=8),
            preferred_keys=("beat", "summary", "content", "name"),
            max_items=8,
        )
        _append_dict_section(
            lines=lines,
            title="Done planned beats",
            items=_status_items(beats, done=True, max_items=8),
            preferred_keys=("beat", "summary", "content", "name"),
            max_items=8,
        )
        if not beats:
            _append_dict_section(
                lines=lines,
                title="Planned beats",
                items=beats,
                preferred_keys=("beat", "summary", "content", "name"),
                max_items=10,
            )

        priority_hooks = _as_dict_list(plan.get("priority_hooks"))
        _append_dict_section(
            lines=lines,
            title="Pending priority hooks",
            items=_status_items(priority_hooks, done=False, max_items=8),
            preferred_keys=("hook", "title", "content", "summary"),
            max_items=8,
        )
        _append_dict_section(
            lines=lines,
            title="Done priority hooks",
            items=_status_items(priority_hooks, done=True, max_items=8),
            preferred_keys=("hook", "title", "content", "summary"),
            max_items=8,
        )
        if not priority_hooks:
            _append_dict_section(
                lines=lines,
                title="Priority hooks",
                items=priority_hooks,
                preferred_keys=("hook", "title", "content", "summary"),
                max_items=10,
            )

        _append_dict_section(
            lines=lines,
            title="Plan guardrails",
            items=plan.get("guardrails"),
            preferred_keys=("rule", "constraint", "content", "name"),
            max_items=12,
        )

    return "\n".join(lines).strip()


def build_remix_context_preview_audit(
    *,
    context: str,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build inspectable prompt-context telemetry for the remix preview UI."""
    estimated_tokens = _estimate_context_tokens(context)
    budget_risk = _context_budget_risk(estimated_tokens)
    activated_sections = [
        {"key": key, "summary": summary}
        for key, summary in _activated_context_sections(bible=bible, plan=plan)
    ]
    active_source_patterns = sorted(_source_pattern_names(source_pattern_pack))[:32]
    continuity_audit = build_remix_continuity_control_audit(
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )
    production_control_audit = build_remix_continuation_control_audit(
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )

    warnings: list[str] = []
    if not context.strip():
        warnings.append("empty_context")
    if not activated_sections and context.strip():
        warnings.append("no_structured_context_sections_detected")
    if isinstance(source_pattern_pack, dict) and source_pattern_pack and not active_source_patterns:
        warnings.append("source_pattern_pack_loaded_without_active_patterns")
    if budget_risk == "medium":
        warnings.append("context_near_budget_review_recommended")
    elif budget_risk == "high":
        warnings.append("context_budget_high_trim_or_stage_required")
    if continuity_audit["canon_drift_risks"]:
        warnings.append("canon_drift_risk_review_required")
    if production_control_audit["warnings"]:
        warnings.append("production_control_review_required")

    return {
        "context_estimated_tokens": estimated_tokens,
        "context_budget_risk": budget_risk,
        "activated_sections": activated_sections,
        "active_source_patterns": active_source_patterns,
        "context_warnings": warnings,
        "production_control_axes": production_control_audit["control_axes"],
        "production_acceptance_steps": production_control_audit["acceptance_steps"],
        "production_warnings": production_control_audit["warnings"],
        "chapter_progress_report_gap_count": production_control_audit["chapter_progress_report_gap_count"],
        "chapter_progress_report_gaps": production_control_audit["chapter_progress_report_gaps"],
        "genre_tracker_warnings": production_control_audit["genre_tracker_warnings"],
        "entity_arc_timeline_risks": production_control_audit["entity_arc_timeline_risks"],
        "source_analysis_coverage_percent": production_control_audit["source_analysis_coverage_percent"],
        "missing_source_analysis_chapters": production_control_audit["missing_source_analysis_chapters"],
        "disassembly_checkpoint_warnings": production_control_audit["disassembly_checkpoint_warnings"],
        "mode_contract_axes": production_control_audit["mode_contract_axes"],
        "mode_contract_warnings": production_control_audit["mode_contract_warnings"],
        "portable_project_memory_warnings": production_control_audit["portable_project_memory_warnings"],
        "chapter_contract_warnings": production_control_audit["chapter_contract_warnings"],
        "production_handoff_warnings": production_control_audit["production_handoff_warnings"],
        "reader_pull_warnings": production_control_audit["reader_pull_warnings"],
        "spec_kit_fiction_warnings": production_control_audit["spec_kit_fiction_warnings"],
        "hook_naturalness_warnings": production_control_audit["hook_naturalness_warnings"],
        "post_draft_review_warnings": production_control_audit["post_draft_review_warnings"],
        "canonkit_context_pack_warnings": production_control_audit["canonkit_context_pack_warnings"],
        "genre_promise_contract_warnings": production_control_audit["genre_promise_contract_warnings"],
        "subgenre_ledger_warnings": production_control_audit["subgenre_ledger_warnings"],
        **continuity_audit,
    }


def build_remix_continuity_control_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build story-bible QA fields from current canon, plans, and chapter state."""
    return {
        "continuity_questions": _continuity_questions(bible=bible, plan=plan, max_items=8),
        "promise_payoff_debts": _promise_payoff_debts(bible=bible, plan=plan, max_items=8),
        "scene_state_snapshot": _scene_state_snapshot(bible=bible, plan=plan, max_items=8),
        "canon_drift_risks": _canon_drift_risks(
            bible=bible,
            plan=plan,
            source_pattern_pack=source_pattern_pack,
            max_items=8,
        ),
    }


def build_remix_inspired_context_block(
    *,
    project_title: str,
    style_content: str,
    source_pattern_pack: Optional[dict[str, Any]] = None,
) -> str:
    """Render a stable same-type creation context block from inspired style anchors."""
    normalized_title = (project_title or "").strip() or "Untitled Inspired Project"
    normalized_style = (style_content or "").strip()
    if not normalized_style:
        return ""
    if not _is_inspired_style_content(normalized_style):
        return ""

    lines: list[str] = [
        "【Remix Inspired Creation Context】",
        f"Project: {normalized_title}",
        "Do not treat this as continuation canon. This is same-type creation guidance.",
        "Use only source rhythm, POV behavior, pacing, scene density, and emotional temperature.",
        "Do not copy source names, organizations, event order, set pieces, or distinctive wording.",
    ]

    _append_inspired_style_section(
        lines=lines,
        title="Source style principles",
        style_content=normalized_style,
        heading="【同类型创作总原则】",
        max_items=8,
    )
    _append_inspired_style_section(
        lines=lines,
        title="Source voice samples",
        style_content=normalized_style,
        heading="【源书语气样本】",
        max_items=6,
    )
    _append_inspired_style_section(
        lines=lines,
        title="Forbidden source elements",
        style_content=normalized_style,
        heading="【源书显性元素禁用清单】",
        max_items=8,
    )
    _append_inspired_independence_contract_section(
        lines=lines,
        style_content=normalized_style,
        source_pattern_pack=source_pattern_pack,
    )

    _append_source_pattern_pack_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        title="Source-discovered inspired guidance:",
        include_inspired_guidance=True,
    )
    _append_source_rights_provenance_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_entity_redaction_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_inspired_transformation_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_universal_novel_workflow_contract_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_universal_project_memory_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_seed_to_bible_foundation_loop_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_universal_deep_planning_revision_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_genre_promise_contract_matrix_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_subgenre_specific_ledger_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_universal_intake_export_rollback_gate_section(
        lines=lines,
        bible={},
        plan=None,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_local_first_authoring_revision_gate_section(
        lines=lines,
        bible={},
        plan=None,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_universal_hook_naturalness_gate_section(
        lines=lines,
        bible={},
        plan=None,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_universal_post_draft_review_gate_section(
        lines=lines,
        bible={},
        plan=None,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_novelforge_version_safe_scene_fact_pipeline_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_distilled_novel_toolbox_platform_compliance_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_novel_studio_graph_memory_continuity_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_universal_same_type_creation_scaffold_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_book_mcp_beta_reader_file_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_live_diagnostics_outline_import_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_filetype_rag_project_edit_boundary_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_frame_setting_state_runtime_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )
    _append_speckit_fiction_scene_task_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_truth_file_write_next_state_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_action_review_canonization_gate_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_serialized_continuity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_story_quality_evaluation_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_reader_market_feedback_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_trope_independence_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_genre_arc_style_governance_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_interactive_narrative_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_copy_similarity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_near_duplicate_semantic_dedup_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_text_analysis_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_stylometry_style_overfit_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_copyedit_prose_lint_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_chinese_text_processing_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_import_extraction_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_ebook_quality_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_agentic_editorial_craft_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_chinese_longform_control_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_bookrun_skill_protocol_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_project_workbench_memory_diversity_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_literary_event_graph_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_segmentation_summary_topic_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_eval_observability_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_source_deconstruction_memory_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_canon_graph_retrieval_audit_section(
        lines=lines,
        source_pattern_pack=source_pattern_pack,
    )
    _append_story_bible_continuity_qa_audit_section(
        lines=lines,
        bible={},
        plan=None,
        source_pattern_pack=source_pattern_pack,
        mode="same-type",
    )

    return "\n".join(lines).strip()


def _is_inspired_style_content(style_content: str) -> bool:
    lowered = style_content.lower()
    same_type_marker = (
        "\u540c\u7c7b\u578b\u521b\u4f5c" in style_content
        or "same-type creation" in lowered
        or "inspired creation" in lowered
    )
    source_marker = (
        "\u6e90\u4e66" in style_content
        or "source voice" in lowered
        or "forbidden source" in lowered
    )
    return bool(same_type_marker and source_marker)


class BookRemixContextService:
    """Owns remix-only continuation context assembly for prompts."""

    async def has_project_durable_remix_lineage(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> bool:
        """Check whether project keeps durable remix continuation lineage markers."""
        bible = await self._load_project_bible(db=db, project_id=project.id)
        return self._has_durable_remix_lineage(bible=bible)

    async def build_project_context_block(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> str:
        bible = await self._load_project_bible(db=db, project_id=project.id)
        plan = await self._load_project_plan(db=db, project_id=project.id)
        if not self._has_confirmed_remix_lineage(bible=bible, plan=plan):
            return ""

        plan_payload = self._to_plan_payload(plan)
        if not plan_payload:
            return ""

        source_pattern_pack = await self._resolve_source_pattern_pack()
        return build_remix_continuation_context_block(
            project_title=project.title,
            bible=self._to_bible_payload(bible),
            plan=plan_payload,
            source_pattern_pack=source_pattern_pack,
        )

    async def build_project_context_preview(
        self,
        *,
        project: Project,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Return the exact continuation context block plus readiness metadata."""
        bible = await self._load_project_bible(db=db, project_id=project.id)
        plan = await self._load_project_plan(db=db, project_id=project.id)
        reason = self._confirmed_remix_lineage_blocker(bible=bible, plan=plan)
        if reason:
            return {
                "project_id": project.id,
                "has_context": False,
                "context": "",
                "context_length": 0,
                "lineage_confirmed": False,
                "reason": reason,
                **build_remix_context_preview_audit(
                    context="",
                    bible=self._to_bible_payload(bible) if bible else {},
                    plan=self._to_plan_payload(plan) if plan else None,
                    source_pattern_pack=None,
                ),
            }

        plan_payload = self._to_plan_payload(plan)
        if not plan_payload:
            return {
                "project_id": project.id,
                "has_context": False,
                "context": "",
                "context_length": 0,
                "lineage_confirmed": False,
                "reason": "continuation_plan_not_confirmed",
                **build_remix_context_preview_audit(
                    context="",
                    bible=self._to_bible_payload(bible) if bible else {},
                    plan=None,
                    source_pattern_pack=None,
                ),
            }

        source_pattern_pack = await self._resolve_source_pattern_pack()
        bible_payload = self._to_bible_payload(bible)
        context = build_remix_continuation_context_block(
            project_title=project.title,
            bible=bible_payload,
            plan=plan_payload,
            source_pattern_pack=source_pattern_pack,
        )
        return {
            "project_id": project.id,
            "has_context": bool(context),
            "context": context,
            "context_length": len(context),
            "lineage_confirmed": bool(context),
            "reason": None if context else "empty_context",
            "source_pattern_pack_loaded": bool(source_pattern_pack),
            **build_remix_context_preview_audit(
                context=context,
                bible=bible_payload,
                plan=plan_payload,
                source_pattern_pack=source_pattern_pack,
            ),
        }

    async def _resolve_source_pattern_pack(self) -> dict[str, Any]:
        return await source_discovery_service.resolve_fresh_pattern_pack(
            repo_root=PROJECT_ROOT,
        )

    async def _load_project_bible(
        self,
        *,
        db: AsyncSession,
        project_id: str,
    ) -> Optional[BookRemixBible]:
        result = await db.execute(
            select(BookRemixBible).where(BookRemixBible.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def _load_project_plan(
        self,
        *,
        db: AsyncSession,
        project_id: str,
    ) -> Optional[BookRemixContinuationPlan]:
        result = await db.execute(
            select(BookRemixContinuationPlan).where(
                BookRemixContinuationPlan.project_id == project_id
            )
        )
        return result.scalar_one_or_none()

    def _to_bible_payload(self, bible: BookRemixBible) -> dict[str, Any]:
        return {
            "world_rules": bible.world_rules or {},
            "hard_constraints": bible.hard_constraints or [],
            "character_cards": bible.character_cards or [],
            "organizations": bible.organizations or [],
            "timeline": bible.timeline or [],
            "story_arcs": bible.story_arcs or [],
            "foreshadows": bible.foreshadows or [],
            "style_signature": bible.style_signature or {},
            "conflicts": bible.conflicts or [],
            "chapter_change_packages": bible.chapter_change_packages or [],
            "source_chapter_count": int(bible.source_chapter_count or 0),
        }

    def _has_confirmed_remix_lineage(
        self,
        *,
        bible: Optional[BookRemixBible],
        plan: Optional[BookRemixContinuationPlan],
    ) -> bool:
        return self._confirmed_remix_lineage_blocker(bible=bible, plan=plan) is None

    def _confirmed_remix_lineage_blocker(
        self,
        *,
        bible: Optional[BookRemixBible],
        plan: Optional[BookRemixContinuationPlan],
    ) -> Optional[str]:
        if not bible:
            return "remix_bible_not_found"
        if not self._has_durable_remix_lineage(bible=bible):
            return "durable_remix_lineage_missing"
        if not plan:
            return "continuation_plan_not_found"

        bible_status = str(bible.generation_status or "").strip().lower()
        if bible_status != "confirmed":
            return "remix_bible_not_confirmed"

        plan_status = str(plan.status or "").strip().lower()
        if plan_status != "confirmed":
            return "continuation_plan_not_confirmed"

        linked_bible_id = str(plan.bible_id or "").strip()
        if not linked_bible_id or linked_bible_id != str(bible.id):
            return "continuation_plan_not_bound_to_current_bible"

        if plan.updated_at and bible.updated_at and plan.updated_at < bible.updated_at:
            return "continuation_plan_stale_against_bible"

        return None

    def _has_durable_remix_lineage(
        self,
        *,
        bible: Optional[BookRemixBible],
    ) -> bool:
        if not bible:
            return False
        source_task_id = str(bible.source_task_id or "").strip()
        if not source_task_id:
            return False
        return int(bible.source_chapter_count or 0) > 0

    def _to_plan_payload(
        self,
        plan: Optional[BookRemixContinuationPlan],
    ) -> Optional[dict[str, Any]]:
        if not plan:
            return None
        plan_status = str(plan.status or "").strip().lower()
        if plan_status != "confirmed":
            return None
        return {
            "summary": plan.summary or "",
            "stage_goals": plan.stage_goals or [],
            "beats": plan.beats or [],
            "priority_hooks": plan.priority_hooks or [],
            "guardrails": plan.guardrails or [],
        }


def _append_whole_book_progress_section(
    *,
    lines: list[str],
    packages: list[dict[str, Any]],
    plan: Optional[dict[str, Any]],
) -> None:
    ordered_packages = _sort_by_chapter_asc(packages)
    if not ordered_packages:
        return

    lines.append("")
    lines.append("Whole-book continuation progress:")
    chapter_numbers = [_int_or_none(package.get("chapter_number")) for package in ordered_packages]
    chapter_numbers = [number for number in chapter_numbers if number is not None]
    if chapter_numbers:
        first_chapter = chapter_numbers[0]
        last_chapter = chapter_numbers[-1]
        chapter_range = str(first_chapter) if first_chapter == last_chapter else f"{first_chapter}-{last_chapter}"
        lines.append(f"- Continuation chapters with context: {chapter_range} ({len(ordered_packages)} packages)")
    else:
        lines.append(f"- Continuation context packages: {len(ordered_packages)}")

    timeline_progression = _build_timeline_progression(ordered_packages)
    if timeline_progression:
        lines.append(f"- Timeline progression: {_truncate(timeline_progression, 360)}")

    character_states = _latest_character_states(ordered_packages, max_items=4)
    if character_states:
        lines.append(f"- Latest character states: {'; '.join(character_states)}")

    resolved_hooks, open_hooks = _hook_status_summary(ordered_packages)
    if resolved_hooks:
        lines.append(f"- Resolved hooks: {'; '.join(resolved_hooks[:5])}")
    if open_hooks:
        lines.append(f"- Open hooks: {'; '.join(open_hooks[:5])}")

    completed_beats = _completed_plan_beats(ordered_packages, plan=plan, max_items=5)
    if completed_beats:
        lines.append(f"- Completed plan beats: {'; '.join(completed_beats)}")


def _append_continuity_question_control_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]] = None,
) -> None:
    """Render current continuity questions, promise debts, and drift risks."""
    audit = build_remix_continuity_control_audit(
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )
    questions = audit["continuity_questions"]
    debts = audit["promise_payoff_debts"]
    snapshot = audit["scene_state_snapshot"]
    risks = audit["canon_drift_risks"]
    if not questions and not debts and not snapshot and not risks:
        return

    lines.append("")
    lines.append("Continuity questions and promise/payoff control:")
    for question in questions[:6]:
        lines.append(f"- question: {_truncate(question, 220)}")
    for debt in debts[:6]:
        label = _string_value(debt.get("label"))
        if not label:
            continue
        source = _string_value(debt.get("source"))
        status = _string_value(debt.get("status"))
        chapter = _string_value(debt.get("chapter"))
        suffix_parts = [part for part in (source, status, chapter) if part]
        suffix = f" ({', '.join(suffix_parts)})" if suffix_parts else ""
        lines.append(f"- debt: {_truncate(label, 220)}{suffix}")
    for item in snapshot[:5]:
        label = _string_value(item.get("label"))
        value = _string_value(item.get("value"))
        if not label and not value:
            continue
        kind = _string_value(item.get("kind")) or "state"
        chapter = _string_value(item.get("chapter"))
        chapter_suffix = f" @ {chapter}" if chapter else ""
        rendered = f"{label}: {value}" if label and value else label or value
        lines.append(f"- scene_state/{kind}{chapter_suffix}: {_truncate(rendered, 220)}")
    for risk in risks[:5]:
        lines.append(f"- canon_drift_risk: {_truncate(risk, 220)}")


def _continuity_questions(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> list[str]:
    questions: list[str] = []
    packages = _chapter_analysis_packages(bible.get("chapter_change_packages"))

    for debt in _promise_payoff_debts(bible=bible, plan=plan, max_items=max_items):
        label = _string_value(debt.get("label"))
        if label:
            _append_unique(questions, f"What setup/payoff move must remain visible for: {label}?")
        if len(questions) >= max_items:
            return questions[:max_items]

    for state in _latest_character_state_payload(packages, max_items=4):
        name = _string_value(state.get("character_name"))
        state_after = _string_value(state.get("state_after"))
        if name and state_after:
            _append_unique(questions, f"Does {name}'s next action follow the current state: {state_after}?")
        if len(questions) >= max_items:
            return questions[:max_items]

    for beat in _pending_plan_beats(plan=plan, max_items=4):
        _append_unique(questions, f"Which scene state changes are required before advancing: {beat}?")
        if len(questions) >= max_items:
            return questions[:max_items]

    if plan:
        for guardrail in _as_dict_list(plan.get("guardrails"))[:3]:
            rule = _first_text(guardrail, ("rule", "constraint", "content", "name"))
            if rule:
                _append_unique(questions, f"What evidence proves the next chapter obeys guardrail: {rule}?")
            if len(questions) >= max_items:
                return questions[:max_items]

    return questions[:max_items]


def _promise_payoff_debts(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> list[dict[str, str]]:
    debts: list[dict[str, str]] = []

    def add_debt(item: dict[str, Any], *, source: str, reason: str) -> None:
        label = _first_text(item, ("hook", "promise", "question", "title", "content", "summary", "beat", "name"))
        if not label:
            return
        payload = {
            "label": _truncate(label, 220),
            "source": source,
            "status": _string_value(item.get("status")) or reason,
        }
        chapter = _chapter_reference(item)
        if chapter:
            payload["chapter"] = chapter
        if any(existing.get("label", "").strip().lower() == payload["label"].strip().lower() for existing in debts):
            return
        debts.append(payload)

    for item in _status_items(_as_dict_list(plan.get("priority_hooks") if plan else None), done=False, max_items=max_items):
        add_debt(item, source="plan.priority_hooks", reason="pending")
        if len(debts) >= max_items:
            return debts[:max_items]

    for package in _chapter_analysis_packages(bible.get("chapter_change_packages")):
        for item in _as_dict_list(package.get("foreshadow_changes")):
            if _is_done_status(item.get("status")):
                continue
            merged = {**item}
            if package.get("chapter_number") is not None and merged.get("chapter_number") is None:
                merged["chapter_number"] = package.get("chapter_number")
            add_debt(merged, source="chapter_change_packages", reason="open")
            if len(debts) >= max_items:
                return debts[:max_items]

    for item in _status_items(_as_dict_list(bible.get("foreshadows")), done=False, max_items=max_items):
        add_debt(item, source="bible.foreshadows", reason="open")
        if len(debts) >= max_items:
            return debts[:max_items]

    return debts[:max_items]


def _scene_state_snapshot(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> list[dict[str, str]]:
    snapshot: list[dict[str, str]] = []
    packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    latest_package = packages[-1] if packages else None
    latest_chapter = _chapter_reference(latest_package or {})

    if latest_package:
        summary = _string_value(latest_package.get("summary"))
        if summary:
            snapshot.append({
                "kind": "summary",
                "label": "latest accepted chapter",
                "value": _truncate(summary, 220),
                "chapter": latest_chapter,
            })

        for item in _as_dict_list(latest_package.get("timeline_delta"))[:2]:
            event = _first_text(item, ("event", "summary", "content"))
            if event:
                snapshot.append({
                    "kind": "timeline",
                    "label": "latest event",
                    "value": _truncate(event, 220),
                    "chapter": latest_chapter,
                })

        for item in _as_dict_list(latest_package.get("character_state_changes"))[:3]:
            name = _string_value(item.get("character_name") or item.get("name")) or "Unknown character"
            state_after = _string_value(item.get("state_after"))
            key_event = _string_value(item.get("key_event"))
            value = state_after if not key_event else f"{state_after} ({key_event})"
            if value.strip():
                snapshot.append({
                    "kind": "character",
                    "label": name,
                    "value": _truncate(value, 220),
                    "chapter": latest_chapter,
                })

        emotional_arc = latest_package.get("emotional_arc")
        if isinstance(emotional_arc, dict):
            tone = _string_value(
                emotional_arc.get("tone")
                or emotional_arc.get("primary_emotion")
                or emotional_arc.get("emotion")
            )
            if tone:
                intensity = emotional_arc.get("intensity")
                value = f"{tone}; intensity={intensity}" if intensity is not None else tone
                snapshot.append({
                    "kind": "emotion",
                    "label": "latest emotional arc",
                    "value": _truncate(value, 220),
                    "chapter": latest_chapter,
                })

    for beat in _pending_plan_beats(plan=plan, max_items=3):
        snapshot.append({
            "kind": "pending_beat",
            "label": "next planned beat",
            "value": _truncate(beat, 220),
            "chapter": "",
        })
        if len(snapshot) >= max_items:
            return snapshot[:max_items]

    return snapshot[:max_items]


def _canon_drift_risks(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]] = None,
    max_items: int,
) -> list[str]:
    risks: list[str] = []
    packages = _chapter_analysis_packages(bible.get("chapter_change_packages"))
    latest_chapter = _latest_chapter_number(packages)
    open_debts = _promise_payoff_debts(bible=bible, plan=plan, max_items=99)
    pattern_names = _source_pattern_names(source_pattern_pack)

    if not packages:
        _append_unique(risks, "missing_chapter_change_packages: no accepted chapter-state evidence is available")
    if plan and not _as_dict_list(plan.get("beats")):
        _append_unique(risks, "missing_plan_beats: continuation plan has no inspectable beat list")
    if plan and not _as_dict_list(plan.get("guardrails")):
        _append_unique(risks, "missing_plan_guardrails: continuation plan has no explicit guardrails")
    if len(open_debts) > 8:
        _append_unique(risks, f"open_promise_payoff_overflow: {len(open_debts)} unresolved debts need prioritization")

    for item in _as_dict_list(bible.get("foreshadows")):
        label = _first_text(item, ("hook", "promise", "question", "title", "content", "summary", "name"))
        setup_chapter = _chapter_value(item, ("setup_chapter", "planted_chapter", "introduced_chapter", "chapter_number"))
        payoff_chapter = _chapter_value(item, ("payoff_chapter", "resolved_chapter", "closed_chapter"))
        if setup_chapter is not None and payoff_chapter is not None and payoff_chapter < setup_chapter:
            _append_unique(risks, f"payoff_before_setup: {_truncate(label, 160)}")
        if not _is_done_status(item.get("status")) and setup_chapter is not None and latest_chapter is not None:
            if latest_chapter - setup_chapter >= 6:
                _append_unique(risks, f"stale_open_hook: {_truncate(label, 160)}")
        if len(risks) >= max_items:
            return risks[:max_items]

    if "entity_mention_arc_timeline_gate" in pattern_names:
        for risk in _entity_mention_arc_timeline_risks(bible=bible, plan=plan, max_items=max_items):
            _append_unique(risks, risk)
            if len(risks) >= max_items:
                return risks[:max_items]

    return risks[:max_items]


def _webnovel_genre_tracker_warnings(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> list[str]:
    """Return structured warnings for serial-fiction genre trackers."""
    warnings: list[str] = []
    packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    chapter_numbers = [_int_or_none(package.get("chapter_number")) for package in packages]
    chapter_numbers = [number for number in chapter_numbers if number is not None]
    chapter_gaps = _chapter_sequence_gaps(chapter_numbers)
    open_hooks = _status_items(_as_dict_list(bible.get("foreshadows")), done=False, max_items=99)
    pending_beats = _pending_plan_beats(plan=plan, max_items=99)
    pending_priority_hooks = _status_items(
        _as_dict_list(plan.get("priority_hooks")) if plan else [],
        done=False,
        max_items=99,
    )

    if not _has_genre_promise_surface(bible=bible, plan=plan):
        _append_unique(warnings, "webnovel_missing_genre_promise")
    if chapter_gaps:
        _append_unique(warnings, f"webnovel_chapter_sequence_gaps: {', '.join(chapter_gaps[:4])}")
    if open_hooks and not pending_beats and not pending_priority_hooks:
        _append_unique(warnings, "webnovel_open_hooks_without_rotation_plan")
    if len(open_hooks) > 8:
        _append_unique(warnings, f"webnovel_open_hook_overflow: {len(open_hooks)}")

    latest_package = packages[-1] if packages else None
    if latest_package and not _has_latest_chapter_micro_payoff_signal(latest_package):
        _append_unique(warnings, "webnovel_latest_chapter_missing_micro_payoff_signal")
    if latest_package and not _has_latest_chapter_cliffhanger_signal(latest_package, bible=bible):
        _append_unique(warnings, "webnovel_cliffhanger_rotation_missing")

    entity_risks = _entity_mention_arc_timeline_risks(bible=bible, plan=plan, max_items=99)
    if any("stale_character_absence_gap" in risk for risk in entity_risks):
        _append_unique(warnings, "webnovel_stale_character_review_required")

    return warnings[:max_items]


def _entity_mention_arc_timeline_risks(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> list[str]:
    """Detect entity appearance gaps before canon or same-type arc reuse."""
    risks: list[str] = []
    packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    latest_chapter = _latest_chapter_number(packages)
    mentions = _entity_mentions_by_chapter(packages)
    card_names = {
        _entity_key(name): name
        for card in _as_dict_list(bible.get("character_cards"))
        for name in (_card_entity_name(card),)
        if name
    }

    for card in _as_dict_list(bible.get("character_cards")):
        name = _card_entity_name(card)
        if not name or _is_inactive_entity_status(card.get("status")):
            continue
        mention_chapters = mentions.get(_entity_key(name), [])
        card_chapter = _chapter_value(
            card,
            (
                "last_chapter_number",
                "last_seen_chapter",
                "last_seen",
                "chapter_number",
                "first_appearance",
                "introduced_chapter",
            ),
        )
        known_chapters = [chapter for chapter in mention_chapters if chapter is not None]
        if card_chapter is not None:
            known_chapters.append(card_chapter)
        if not known_chapters:
            _append_unique(risks, f"entity_without_chapter_appearance: {name}")
            if len(risks) >= max_items:
                return risks[:max_items]
            continue
        last_seen = max(known_chapters)
        if (
            latest_chapter is not None
            and latest_chapter - last_seen >= 6
            and not _plan_mentions_label(plan=plan, label=name)
        ):
            _append_unique(
                risks,
                f"stale_character_absence_gap: {name} last_seen=Ch{last_seen} latest=Ch{latest_chapter}",
            )
        if len(risks) >= max_items:
            return risks[:max_items]

    for key, chapters in mentions.items():
        if key in card_names:
            continue
        display_name = _display_entity_key(key)
        if display_name:
            latest = max(chapter for chapter in chapters if chapter is not None) if chapters else None
            suffix = f" last_seen=Ch{latest}" if latest is not None else ""
            _append_unique(risks, f"mentioned_entity_without_card: {display_name}{suffix}")
        if len(risks) >= max_items:
            return risks[:max_items]

    for arc in _as_dict_list(bible.get("story_arcs")):
        if _is_done_status(arc.get("status")):
            continue
        label = _first_text(arc, ("name", "arc", "summary", "goal"))
        if not label:
            continue
        if _chapter_value(arc, ("chapter_number", "last_chapter_number", "setup_chapter", "introduced_chapter")) is None:
            _append_unique(risks, f"active_arc_without_chapter_link: {_truncate(label, 120)}")
        if len(risks) >= max_items:
            return risks[:max_items]

    return risks[:max_items]


def _has_genre_promise_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    direct_keys = (
        "genre",
        "genres",
        "genre_promise",
        "reader_promise",
        "target_reader",
        "market_shape",
        "platform",
    )
    if any(_has_any_package_value(bible, (key,)) for key in direct_keys):
        return True
    if plan and any(_has_any_package_value(plan, (key,)) for key in direct_keys):
        return True
    review_items = _as_dict_list(bible.get("hard_constraints"))
    if plan:
        review_items.extend(_as_dict_list(plan.get("guardrails")))
    for item in review_items:
        text = _first_text(item, ("genre", "reader_promise", "rule", "summary", "content"))
        lowered = text.lower()
        if any(marker in lowered for marker in ("genre", "reader promise", "webnovel", "romance", "mystery", "xianxia", "fantasy")):
            return True
    return False


def _has_latest_chapter_micro_payoff_signal(package: dict[str, Any]) -> bool:
    return any(
        _has_any_package_value(package, keys)
        for keys in (
            ("timeline_delta", "new_facts", "fact_deltas", "facts"),
            ("character_state_changes", "character_changes", "character_state_delta"),
            ("foreshadow_changes", "hooks_paid_off", "new_hooks", "promise_payoff_changes"),
            ("plan_progress",),
            ("emotional_arc",),
        )
    )


def _has_latest_chapter_cliffhanger_signal(package: dict[str, Any], *, bible: dict[str, Any]) -> bool:
    if _has_any_package_value(
        package,
        ("new_hooks", "foreshadow_changes", "promise_payoff_changes", "next_chapter_focus", "next_focus"),
    ):
        return True
    chapter_number = _int_or_none(package.get("chapter_number"))
    if chapter_number is None:
        return False
    for item in _status_items(_as_dict_list(bible.get("foreshadows")), done=False, max_items=99):
        setup_chapter = _chapter_value(item, ("setup_chapter", "planted_chapter", "introduced_chapter", "chapter_number"))
        if setup_chapter == chapter_number:
            return True
    return False


def _entity_mentions_by_chapter(packages: list[dict[str, Any]]) -> dict[str, list[int]]:
    mentions: dict[str, list[int]] = {}
    for package in packages:
        package_chapter = _int_or_none(package.get("chapter_number"))
        for item in _as_dict_list(package.get("character_state_changes")):
            name = _first_named_value(item, ("character_name", "name", "entity", "character"))
            key = _entity_key(name)
            if key:
                mentions.setdefault(key, []).append(
                    _chapter_value(item, ("chapter_number", "last_chapter_number")) or package_chapter or 0
                )
    return mentions


def _card_entity_name(card: dict[str, Any]) -> str:
    return _first_named_value(card, ("name", "character_name", "entity", "label", "title"))


def _first_named_value(item: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = _string_value(item.get(key))
        if value:
            return value
    return ""


def _entity_key(value: str) -> str:
    return re.sub(r"\s+", " ", _string_value(value)).strip().lower()


def _display_entity_key(key: str) -> str:
    return " ".join(part.capitalize() for part in _string_value(key).split())


def _is_inactive_entity_status(value: Any) -> bool:
    normalized = _string_value(value).strip().lower()
    return normalized in {"inactive", "retired", "dead", "removed", "closed", "complete", "completed"}


def _plan_mentions_label(*, plan: Optional[dict[str, Any]], label: str) -> bool:
    if not plan:
        return False
    needle = _entity_key(label)
    if not needle:
        return False
    haystacks = [
        _string_value(plan.get("summary")),
        *[_first_text(item, ("beat", "summary", "content", "name")) for item in _as_dict_list(plan.get("beats"))],
        *[_first_text(item, ("hook", "summary", "content", "name")) for item in _as_dict_list(plan.get("priority_hooks"))],
        *[_first_text(item, ("rule", "summary", "content", "name")) for item in _as_dict_list(plan.get("guardrails"))],
    ]
    return any(needle in _entity_key(text) for text in haystacks)


def _latest_chapter_number(packages: list[dict[str, Any]]) -> Optional[int]:
    chapter_numbers = [_int_or_none(package.get("chapter_number")) for package in packages]
    chapter_numbers = [number for number in chapter_numbers if number is not None]
    return max(chapter_numbers) if chapter_numbers else None


def _chapter_reference(item: dict[str, Any]) -> str:
    chapter_number = _chapter_value(item, ("chapter_number", "last_chapter_number", "setup_chapter", "introduced_chapter"))
    return f"Ch{chapter_number}" if chapter_number is not None else ""


def _chapter_value(item: dict[str, Any], keys: tuple[str, ...]) -> Optional[int]:
    for key in keys:
        number = _int_or_none(item.get(key))
        if number is not None:
            return number
    return None


def _chapter_analysis_packages(packages: Any) -> list[dict[str, Any]]:
    normalized_packages = [
        package
        for package in _as_dict_list(packages)
        if _is_machine_continuation_source(package.get("source"))
    ]
    generation_guardrails = {
        key: package.get("guardrail_check")
        for package in normalized_packages
        if _string_value(package.get("source")) == "chapter_generation"
        for key in (_chapter_identity_key(package),)
        if key is not None and isinstance(package.get("guardrail_check"), dict)
    }
    analysis_keys = {
        key
        for package in normalized_packages
        if _string_value(package.get("source")) == "chapter_analysis"
        for key in (_chapter_identity_key(package),)
        if key is not None
    }
    preferred_packages: list[dict[str, Any]] = []
    for package in normalized_packages:
        key = _chapter_identity_key(package)
        source = _string_value(package.get("source"))
        if source == "chapter_generation" and key in analysis_keys:
            continue
        if source == "chapter_analysis" and key in generation_guardrails and "guardrail_check" not in package:
            package = {**package, "guardrail_check": generation_guardrails[key]}
        preferred_packages.append(package)
    return _sort_by_chapter_desc(preferred_packages)


def _chapter_progress_report_gaps(
    packages: list[dict[str, Any]],
    *,
    include_time_trace: bool = False,
) -> list[dict[str, Any]]:
    """Return accepted chapter-report fields that are missing from package state."""
    required_fields: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("summary", ("summary",)),
        ("new_facts", ("new_facts", "fact_deltas", "timeline_delta", "facts")),
        ("character_changes", ("character_changes", "character_state_changes")),
        (
            "hook_deltas",
            ("hooks_paid_off", "new_hooks", "foreshadow_changes", "promise_payoff_changes"),
        ),
        ("continuity_updates", ("continuity_updates", "continuity_delta", "ledger_updates")),
        ("next_chapter_focus", ("next_chapter_focus", "next_focus", "next_likely_focus")),
        ("word_count", ("word_count", "char_count", "character_count", "length")),
        ("risks", ("risks", "risk_notes", "audit_risks")),
    )
    if include_time_trace:
        required_fields += (
            ("narrative_time", ("narrative_time", "narrative_date_time", "timeline_anchor", "date_time")),
            ("duration", ("duration", "scene_duration", "elapsed_time")),
            ("weekday", ("weekday", "day_of_week")),
            ("character_age_refs", ("character_age_refs", "character_ages", "age_refs")),
            ("section_status", ("section_status", "status", "acceptance_status")),
            ("export_included", ("export_included", "included_in_export", "export_status")),
        )

    gaps: list[dict[str, Any]] = []
    for package in packages:
        missing_fields = [
            label
            for label, keys in required_fields
            if not _has_any_package_value(package, keys)
        ]
        if missing_fields:
            chapter = (
                _chapter_reference(package)
                or _string_value(package.get("chapter_id"))
                or "unknown"
            )
            gaps.append({"chapter": chapter, "missing_fields": missing_fields})
    return gaps[:8]


def _chapter_progressive_disassembly_checkpoint_audit(
    *,
    bible: dict[str, Any],
    max_items: int,
) -> dict[str, Any]:
    """Audit source-book chapter analysis coverage for拆书-driven continuation."""
    source_chapter_count = _int_or_none(bible.get("source_chapter_count")) or 0
    analysis_packages = [
        package
        for package in _as_dict_list(bible.get("chapter_change_packages"))
        if _string_value(package.get("source")) == "chapter_analysis"
    ]
    analyzed_chapters = sorted(
        {
            chapter
            for package in analysis_packages
            for chapter in (_int_or_none(package.get("chapter_number")),)
            if chapter is not None and chapter > 0
        }
    )

    if source_chapter_count > 0:
        covered_chapters = [chapter for chapter in analyzed_chapters if chapter <= source_chapter_count]
        missing_chapters = [
            chapter
            for chapter in range(1, source_chapter_count + 1)
            if chapter not in set(covered_chapters)
        ]
        coverage_percent = int(round((len(covered_chapters) / source_chapter_count) * 100))
    else:
        missing_chapters = []
        coverage_percent = 0

    warnings: list[str] = []
    if source_chapter_count <= 0:
        warnings.append("source_chapter_count_missing")
    if not analysis_packages:
        warnings.append("missing_chapter_analysis_packages")
    if source_chapter_count > 0 and missing_chapters:
        warnings.append("source_analysis_coverage_incomplete")
    if analysis_packages and not _has_disassembly_evidence_refs(analysis_packages):
        warnings.append("missing_qa_citation_jump_trace")

    return {
        "source_chapter_count": source_chapter_count,
        "source_analysis_package_count": len(analysis_packages),
        "source_analysis_coverage_percent": coverage_percent,
        "missing_source_analysis_chapters": _compress_chapter_numbers(missing_chapters)[:max_items],
        "has_qa_citation_jump_trace": _has_disassembly_evidence_refs(analysis_packages),
        "warnings": warnings[:max_items],
    }


def _mode_contract_generation_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> dict[str, Any]:
    """Audit visible creative-axis coverage before prompt assembly."""
    axes = {
        "mode": "continue-chapter" if plan else "missing",
        "theme_or_seed": _axis_status(_string_value(plan.get("summary")) if plan else ""),
        "characters": "present" if _as_dict_list(bible.get("character_cards")) else "missing",
        "genre": _axis_status(_mode_axis_value(bible, plan, ("genre", "genres", "genre_promise", "reader_promise"))),
        "worldview_or_setting": _axis_status(_mode_worldview_value(bible)),
        "audience": _axis_status(_mode_axis_value(bible, plan, ("audience", "target_reader", "platform"))),
        "era": _axis_status(_mode_axis_value(bible, plan, ("era", "period", "time_period"))),
        "ending_style": _axis_status(_mode_axis_value(bible, plan, ("ending_style", "ending_direction", "ending"))),
        "narrator_or_pov": _axis_status(_mode_narrator_or_pov_value(bible, plan)),
        "source_material_boundary": "present" if _chapter_analysis_packages(bible.get("chapter_change_packages")) else "missing",
        "supplemental_constraints": "present" if _as_dict_list(bible.get("hard_constraints")) or (plan and _as_dict_list(plan.get("guardrails"))) else "missing",
        "style_analysis": "present" if isinstance(bible.get("style_signature"), dict) and bool(bible.get("style_signature")) else "missing",
    }

    required_axes = (
        "mode",
        "theme_or_seed",
        "characters",
        "genre",
        "worldview_or_setting",
        "audience",
        "narrator_or_pov",
        "source_material_boundary",
        "supplemental_constraints",
    )
    warnings: list[str] = []
    for axis in required_axes:
        if axes.get(axis) == "missing":
            warnings.append(f"missing_visible_axis: {axis}")
    if axes["mode"] != "continue-chapter":
        warnings.append("selected_mode_missing_or_ambiguous")
    if axes["source_material_boundary"] == "present" and axes["mode"] == "continue-chapter":
        warnings.append("selected_mode_must_override_incidental_source_material")

    return {
        "axes": axes,
        "warnings": warnings[:max_items],
    }


def _empty_mode_contract_generation_audit() -> dict[str, Any]:
    return {"axes": {}, "warnings": []}


def _portable_project_memory_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> dict[str, Any]:
    """Audit durable project-memory surfaces before continuation reuse."""
    warnings: list[str] = []
    if not _has_story_bible_north_star_surface(bible=bible, plan=plan):
        warnings.append("missing_story_bible_north_star")
    if not _has_character_engine_card_surface(bible):
        warnings.append("missing_character_engine_card")
    if not _has_world_rule_cost_custody_surface(bible):
        warnings.append("missing_world_rule_cost_custody")
    if not _has_continuity_decision_ledger_surface(bible):
        warnings.append("missing_continuity_decision_ledger")
    if not _has_startup_status_packet_surface(bible=bible, plan=plan):
        warnings.append("missing_startup_status_packet")
    return {"warnings": warnings[:max_items]}


def _empty_portable_project_memory_audit() -> dict[str, Any]:
    return {"warnings": []}


def _has_story_bible_north_star_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    style_signature = bible.get("style_signature") if isinstance(bible.get("style_signature"), dict) else {}
    carriers = [bible, style_signature]
    if isinstance(plan, dict):
        carriers.append(plan)
    keys = (
        "premise",
        "one_sentence_premise",
        "reader_promise",
        "genre_promise",
        "emotional_target",
        "theme",
        "core_theme",
        "ending_direction",
        "must_preserve",
        "must_avoid",
        "genre",
        "target_reader",
        "platform",
    )
    return any(_axis_status(carrier.get(key)) == "present" for carrier in carriers for key in keys)


def _has_character_engine_card_surface(bible: dict[str, Any]) -> bool:
    want_keys = ("external_want", "want", "goal", "current_goal", "desire")
    need_keys = ("internal_need", "need", "wound", "lie", "flaw", "fear", "cost", "voice_fingerprint")
    for card in _as_dict_list(bible.get("character_cards")):
        if any(_axis_status(card.get(key)) == "present" for key in want_keys) and any(
            _axis_status(card.get(key)) == "present" for key in need_keys
        ):
            return True
    return False


def _has_world_rule_cost_custody_surface(bible: dict[str, Any]) -> bool:
    if _axis_status(bible.get("world_rules")) == "present":
        return True
    for key in ("worldbuilding", "setting", "research_notes", "locations", "factions", "organizations"):
        if _axis_status(bible.get(key)) == "present":
            return True
    return False


def _has_continuity_decision_ledger_surface(bible: dict[str, Any]) -> bool:
    for key in ("timeline", "foreshadows", "facts", "decision_log", "continuity_updates"):
        if _axis_status(bible.get(key)) == "present":
            return True
    return bool(_chapter_analysis_packages(bible.get("chapter_change_packages")))


def _has_startup_status_packet_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    has_latest_chapter = bool(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    has_progress = _axis_status(bible.get("progress")) == "present" or _axis_status(bible.get("current_status")) == "present"
    has_plan = isinstance(plan, dict) and (
        _axis_status(plan.get("summary")) == "present"
        or bool(_as_dict_list(plan.get("beats")))
        or bool(_as_dict_list(plan.get("priority_hooks")))
    )
    return bool((has_latest_chapter or has_progress) and has_plan)


def _axis_status(value: Any) -> str:
    if isinstance(value, str):
        return "present" if value.strip() else "missing"
    if isinstance(value, (list, dict)):
        return "present" if bool(value) else "missing"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "present"
    return "missing"


def _mode_axis_value(
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    keys: tuple[str, ...],
) -> Any:
    for key in keys:
        if key in bible and _axis_status(bible.get(key)) == "present":
            return bible.get(key)
        if plan and key in plan and _axis_status(plan.get(key)) == "present":
            return plan.get(key)
    return ""


def _mode_worldview_value(bible: dict[str, Any]) -> Any:
    for key in ("world_rules", "worldbuilding", "setting", "worldview", "organizations", "timeline"):
        value = bible.get(key)
        if _axis_status(value) == "present":
            return value
    return ""


def _mode_narrator_or_pov_value(bible: dict[str, Any], plan: Optional[dict[str, Any]]) -> Any:
    style_signature = bible.get("style_signature")
    if isinstance(style_signature, dict):
        for key in ("pov", "point_of_view", "narrator", "narrative_distance"):
            value = style_signature.get(key)
            if _axis_status(value) == "present":
                return value
    value = _mode_axis_value(bible, plan, ("pov", "point_of_view", "narrator"))
    if _axis_status(value) == "present":
        return value
    for item in _as_dict_list(bible.get("hard_constraints")) + (_as_dict_list(plan.get("guardrails")) if plan else []):
        text = _first_text(item, ("rule", "constraint", "content", "summary"))
        if any(marker in text.lower() for marker in ("pov", "point of view", "narrator", "视角", "叙述")):
            return text
    return ""


def _universal_chapter_contract_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    pattern_names: set[str],
    max_items: int,
) -> dict[str, Any]:
    """Audit universal chapter-contract inputs before continuation drafting."""
    warnings: list[str] = []
    packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    latest_package = packages[-1] if packages else None
    latest_summary = _string_value(latest_package.get("summary")) if latest_package else ""
    pending_beat = _first_pending_plan_beat(plan=plan)
    pending_beat_item = _first_pending_plan_item(plan=plan)
    plan_summary = _string_value(plan.get("summary")) if plan else ""
    promise_debt = _first_promise_payoff_debt_label(bible=bible, plan=plan)
    guardrail = _first_plan_guardrail(plan=plan)
    hard_constraint = _first_hard_constraint(bible=bible)
    character_goal = _first_character_goal(bible=bible)
    conflict = _first_conflict_text(bible=bible)

    if "chapter_contract_scene_beat_gate" in pattern_names:
        if not (pending_beat or plan_summary or latest_summary):
            warnings.append("missing_chapter_job_source")
        if not (latest_summary or promise_debt):
            warnings.append("missing_opening_hook_source")
        if not (character_goal or pending_beat):
            warnings.append("missing_main_goal")
        if not (conflict or guardrail or hard_constraint):
            warnings.append("missing_main_obstacle")
        if not (guardrail or hard_constraint):
            warnings.append("missing_forbidden_contradiction")
        if not _has_structured_scene_beat_sheet(plan):
            warnings.append("missing_scene_beat_sheet")
        if not _first_contract_pov(bible=bible, plan=plan, latest_package=latest_package):
            warnings.append("missing_pov_anchor")
        if not _first_starting_status(latest_package=latest_package):
            warnings.append("missing_starting_status")
        if not _first_escalation(plan=plan, pending_beat_item=pending_beat_item, conflict=conflict):
            warnings.append("missing_escalation")
        if not _first_new_hook(bible=bible, plan=plan):
            warnings.append("missing_new_hook")
        if not _first_character_change(latest_package=latest_package):
            warnings.append("missing_character_change")
        if not _first_continuity_fact(bible=bible, latest_package=latest_package):
            warnings.append("missing_continuity_facts")
        if not _first_word_count_target(bible=bible, plan=plan):
            warnings.append("missing_word_count_target")

    if "reader_promise_micro_payoff_gate" in pattern_names:
        if not (promise_debt or _has_genre_promise_surface(bible=bible, plan=plan)):
            warnings.append("missing_reader_promise_surface")
        if latest_package and not _has_latest_chapter_micro_payoff_signal(latest_package):
            warnings.append("latest_chapter_missing_micro_payoff_signal")
        if not latest_package:
            warnings.append("missing_latest_chapter_for_micro_payoff_review")

    if "revision_order_natural_prose_gate" in pattern_names:
        if not (guardrail or hard_constraint):
            warnings.append("missing_revision_acceptance_boundary")

    return {"warnings": warnings[:max_items]}


def _genre_promise_contract_matrix_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> dict[str, Any]:
    """Audit genre-promise matrix coverage before planning or same-type drafting."""
    warnings: list[str] = []
    if not _has_genre_promise_surface(bible=bible, plan=plan):
        warnings.append("missing_genre_or_reader_promise")
    if not _has_genre_promise_matrix_surface(bible=bible, plan=plan):
        warnings.append("missing_genre_promise_matrix")
    return {"warnings": warnings[:max_items]}


def _has_genre_promise_matrix_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    matrix_keys = (
        "genre_promise_matrix",
        "genre_contract_matrix",
        "reader_promise_matrix",
        "genre_contract",
        "genre_expectations",
        "genre_conventions",
        "trope_strategy",
        "market_positioning",
    )
    fields = []
    for container in (bible, plan or {}):
        for key in matrix_keys:
            value = container.get(key) if isinstance(container, dict) else None
            if isinstance(value, dict) and value:
                fields.extend(value.keys())
            elif isinstance(value, list) and value:
                return True
            elif isinstance(value, str) and value.strip():
                return True
    normalized_fields = {str(field).lower() for field in fields}
    expected_axes = (
        ("expected_pleasure", "reader_pleasure", "reader_promise", "genre_promise"),
        ("payoff_speed", "payoff_timing", "pleasure_speed", "reward_density"),
        ("plant_before_payoff", "setup_before_payoff", "clues", "setup_requirements"),
        ("welcome_tropes", "tired_tropes_to_twist", "trope_strategy", "tropes"),
        ("emotional_aftertaste", "aftertaste", "emotional_target"),
    )
    matched_axes = 0
    for axis_keys in expected_axes:
        if any(key in normalized_fields for key in axis_keys):
            matched_axes += 1
    return matched_axes >= 3


def _subgenre_specific_ledger_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> dict[str, Any]:
    """Audit whether active genre promises have concrete subgenre ledgers."""
    warnings: list[str] = []
    if not _has_genre_promise_surface(bible=bible, plan=plan):
        warnings.append("missing_genre_or_reader_promise")
    if not _has_subgenre_specific_ledger_surface(bible=bible, plan=plan):
        warnings.append("missing_subgenre_specific_ledger")
    return {"warnings": warnings[:max_items]}


def _has_subgenre_specific_ledger_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    ledger_keys = (
        "subgenre_ledgers",
        "genre_ledgers",
        "active_genre_ledgers",
        "romance_trust_ledger",
        "trust_ledger",
        "mystery_clue_ledger",
        "clue_ledger",
        "suspect_ledger",
        "realm_ledger",
        "realm_ladder",
        "cultivation_ladder",
        "resource_ledger",
        "power_level_ledger",
        "deadline_clock",
        "deadline",
        "information_asymmetry",
        "safe_place_status",
        "magic_rules",
        "magic_costs",
        "rules_and_costs",
        "technology_rules",
        "what_if_consequences",
        "threat_rules",
        "dread_ladder",
        "motif_tracker",
        "theme_motifs",
        "historical_research",
        "research_notes",
        "reputation_ledger",
        "faction_consequences",
    )
    for container in (bible, plan or {}):
        if not isinstance(container, dict):
            continue
        for key in ledger_keys:
            value = container.get(key)
            if isinstance(value, dict) and value:
                return True
            if isinstance(value, list) and value:
                return True
            if isinstance(value, str) and value.strip():
                return True
    return False


def _universal_intake_export_rollback_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    pattern_names: set[str],
    max_items: int,
) -> dict[str, Any]:
    """Audit compact intake, export cleanliness, and smallest-repair scope."""
    warnings: list[str] = []
    if "five_question_intake_story_promise_gate" in pattern_names:
        if not _has_five_question_intake_story_promise_surface(bible=bible, plan=plan):
            warnings.append("missing_reader_promise_or_premise")
    if "universal_export_clean_manuscript_gate" in pattern_names:
        if not _has_clean_export_manifest_surface(bible=bible, plan=plan):
            warnings.append("missing_clean_export_manifest")
    if "minimal_rollback_repair_scope_gate" in pattern_names:
        chapter_packages = _sort_by_chapter_asc(
            _chapter_analysis_packages(bible.get("chapter_change_packages"))
        )
        latest_package = chapter_packages[-1] if chapter_packages else {}
        if not _has_least_destructive_repair_scope_surface(
            latest_package=latest_package,
            bible=bible,
            plan=plan,
        ):
            warnings.append("missing_minimal_rollback_repair_scope")
    return {"warnings": warnings[:max_items]}


def _has_five_question_intake_story_promise_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (bible, plan) if isinstance(carrier, dict)]
    intake_keys = (
        "five_question_intake",
        "intake_packet",
        "quick_start_packet",
        "story_promise_packet",
    )
    promise_keys = (
        "logline",
        "premise",
        "one_sentence_premise",
        "reader_promise",
        "protagonist_arc",
        "central_conflict",
        "story_promise",
    )
    beat_keys = (
        "opposition",
        "world_rules",
        "ending_direction",
        "beat_outline",
        "chapter_beats",
    )
    if any(_has_any_package_value(carrier, intake_keys) for carrier in carriers):
        return True
    has_promise = any(_has_any_package_value(carrier, promise_keys) for carrier in carriers)
    has_beat_context = any(_has_any_package_value(carrier, beat_keys) for carrier in carriers)
    return bool(has_promise and has_beat_context)


def _has_clean_export_manifest_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (bible, plan) if isinstance(carrier, dict)]
    manifest_keys = (
        "clean_export_manifest",
        "export_manifest",
        "manuscript_export_manifest",
        "accepted_chapter_manifest",
        "export_chapter_range",
        "export_included_chapters",
        "accepted_chapters",
        "excluded_drafts",
        "export_output_path",
        "export_sha256",
    )
    if any(_has_any_package_value(carrier, manifest_keys) for carrier in carriers):
        return True
    for package in _chapter_analysis_packages(bible.get("chapter_change_packages")):
        if _has_any_package_value(package, manifest_keys):
            return True
    return False


def _local_first_authoring_revision_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    pattern_names: set[str],
    max_items: int,
) -> dict[str, Any]:
    """Audit provider boundary, suggestion-card review, and book-view export custody."""
    warnings: list[str] = []
    if "local_first_provider_boundary_authoring_gate" in pattern_names:
        if not _has_local_first_provider_boundary_surface(bible=bible, plan=plan):
            warnings.append("missing_local_first_provider_boundary")
    if "suggestion_card_nonoverwrite_revision_gate" in pattern_names:
        if not _has_suggestion_card_acceptance_surface(bible=bible, plan=plan):
            warnings.append("missing_suggestion_card_acceptance_policy")
    if "book_view_import_export_manifest_gate" in pattern_names:
        if not _has_book_view_import_export_manifest_surface(bible=bible, plan=plan):
            warnings.append("missing_book_view_import_export_manifest")
    return {"warnings": warnings[:max_items]}


def _has_local_first_provider_boundary_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (bible, plan) if isinstance(carrier, dict)]
    keys = (
        "provider_boundary",
        "provider_mode",
        "model_provider",
        "local_model_provider",
        "local_first_provider_boundary",
        "webllm_boundary",
        "ollama_boundary",
        "cloud_key_policy",
        "offline_fallback",
        "no_model_fallback",
        "prompt_egress_policy",
    )
    return any(_has_any_package_value(carrier, keys) for carrier in carriers)


def _has_suggestion_card_acceptance_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (bible, plan) if isinstance(carrier, dict)]
    keys = (
        "suggestion_cards",
        "revision_cards",
        "accept_reject_queue",
        "pending_suggestions",
        "revision_acceptance_policy",
        "author_acceptance_log",
        "accepted_revision_deltas",
        "rejected_revision_deltas",
    )
    return any(_has_any_package_value(carrier, keys) for carrier in carriers)


def _has_book_view_import_export_manifest_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (bible, plan) if isinstance(carrier, dict)]
    keys = (
        "book_view_manifest",
        "book_view",
        "export_manifest",
        "import_manifest",
        "front_matter",
        "frontmatter",
        "pagination_manifest",
        "live_pagination",
        "import_auto_split",
        "auto_split_status",
        "epub_export_manifest",
        "pdf_export_manifest",
        "markdown_export_manifest",
    )
    return any(_has_any_package_value(carrier, keys) for carrier in carriers)


def _spec_kit_fiction_scene_task_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> dict[str, Any]:
    """Audit Spec Kit fiction scene-task gates before continuation or polish."""
    warnings: list[str] = []

    if not _has_story_bible_constitution_surface(bible):
        warnings.append("missing_story_bible_constitution")
    if not _has_approved_scene_outline(plan):
        warnings.append("missing_approved_scene_outline")
    if not _has_pov_information_asymmetry_map(bible=bible, plan=plan):
        warnings.append("missing_pov_information_asymmetry_map")
    if not _has_pacing_tension_or_checklist_pass(bible=bible, plan=plan):
        warnings.append("missing_pacing_tension_or_checklist_pass")

    return {"warnings": warnings[:max_items]}


def _empty_spec_kit_fiction_scene_task_audit() -> dict[str, Any]:
    return {"warnings": []}


def _has_story_bible_constitution_surface(bible: dict[str, Any]) -> bool:
    if _axis_status(bible.get("constitution")) == "present":
        return True
    if _axis_status(bible.get("story_bible_constitution")) == "present":
        return True
    if _axis_status(bible.get("constitution_source")) == "present":
        return True
    return (
        _axis_status(bible.get("style_signature")) == "present"
        and _axis_status(bible.get("hard_constraints")) == "present"
    )


def _has_approved_scene_outline(plan: Optional[dict[str, Any]]) -> bool:
    if not isinstance(plan, dict):
        return False
    for key in ("scene_beats", "scene_plan", "scenes", "approved_scenes", "beats"):
        for item in _as_dict_list(plan.get(key)):
            status = _string_value(item.get("status")).lower()
            if status in {"approved", "pass", "accepted"}:
                return True
    return False


def _has_pov_information_asymmetry_map(*, bible: dict[str, Any], plan: Optional[dict[str, Any]]) -> bool:
    carriers = [bible]
    if isinstance(plan, dict):
        carriers.append(plan)
    has_pov_schedule = any(_axis_status(carrier.get("pov_schedule")) == "present" for carrier in carriers)
    has_asymmetry = any(
        _axis_status(carrier.get(key)) == "present"
        for carrier in carriers
        for key in ("information_asymmetry", "information_asymmetry_map", "secret_knowledge_map")
    )
    return has_pov_schedule and has_asymmetry


def _has_pacing_tension_or_checklist_pass(*, bible: dict[str, Any], plan: Optional[dict[str, Any]]) -> bool:
    carriers: list[dict[str, Any]] = []
    carriers.extend(_as_dict_list(bible.get("chapter_change_packages")))
    carriers.extend(_as_dict_list(bible.get("chapter_packages")))
    if isinstance(plan, dict):
        carriers.extend(_as_dict_list(plan.get("scene_beats")))
        carriers.extend(_as_dict_list(plan.get("scene_plan")))
        carriers.extend(_as_dict_list(plan.get("scenes")))
    for item in carriers:
        for key in ("pacing_score", "tension_score", "pacing", "tension"):
            value = item.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
                return True
            if isinstance(value, str) and value.strip():
                return True
        if _checklist_passes(item):
            return True
    return False


def _checklist_passes(item: dict[str, Any]) -> bool:
    for key in ("checklist_verdict", "checklist", "quality_gate", "gate_status"):
        value = _string_value(item.get(key)).lower()
        if value in {"pass", "passed", "approved", "ok"}:
            return True
    quality_scores = item.get("quality_scores")
    if isinstance(quality_scores, dict):
        for key in ("checklist", "checklist_verdict", "pacing", "tension"):
            value = quality_scores.get(key)
            if isinstance(value, str) and value.strip().lower() in {"pass", "passed", "approved", "ok"}:
                return True
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
                return True
    return False


def _empty_universal_chapter_contract_audit() -> dict[str, Any]:
    return {"warnings": []}


def _universal_hook_naturalness_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    pattern_names: set[str],
    max_items: int,
) -> dict[str, Any]:
    """Audit hook-type and prose-texture evidence before chapter acceptance."""
    warnings: list[str] = []
    packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    latest_package = packages[-1] if packages else None

    if "opening_ending_hook_integrity_gate" in pattern_names:
        if not _has_opening_hook_type_surface(latest_package=latest_package, bible=bible, plan=plan):
            warnings.append("missing_opening_hook_type")
        if not _has_ending_hook_job_surface(latest_package=latest_package, bible=bible, plan=plan):
            warnings.append("missing_ending_hook_job")
        if latest_package and not _has_latest_chapter_cliffhanger_signal(latest_package, bible=bible):
            warnings.append("missing_ending_hook_or_next_pull")
        if latest_package is None:
            warnings.append("missing_latest_chapter_for_hook_integrity")

    if "anti_ai_naturalness_texture_gate" in pattern_names:
        if not _has_naturalness_texture_review_surface(latest_package=latest_package, bible=bible, plan=plan):
            warnings.append("missing_naturalness_texture_review")

    return {"warnings": warnings[:max_items]}


def _empty_universal_hook_naturalness_audit() -> dict[str, Any]:
    return {"warnings": []}


def _canonkit_local_canon_drift_context_pack_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> dict[str, Any]:
    """Audit CanonKit-style local canon drift and focused scene context readiness."""
    warnings: list[str] = []

    if not _has_focused_scene_context_pack_surface(bible=bible, plan=plan):
        warnings.append("missing_focused_scene_context_pack")

    for warning in _missing_core_character_setup_warnings(bible=bible):
        _append_unique(warnings, warning)
        if len(warnings) >= max_items:
            return {"warnings": warnings[:max_items]}

    for warning in _character_age_year_mismatch_warnings(bible=bible):
        _append_unique(warnings, warning)
        if len(warnings) >= max_items:
            return {"warnings": warnings[:max_items]}

    for warning in _missing_entity_reference_warnings(bible=bible):
        _append_unique(warnings, warning)
        if len(warnings) >= max_items:
            return {"warnings": warnings[:max_items]}

    for warning in _asymmetric_relationship_warnings(bible=bible):
        _append_unique(warnings, warning)
        if len(warnings) >= max_items:
            return {"warnings": warnings[:max_items]}

    for warning in _scene_state_conflict_warnings(bible=bible):
        _append_unique(warnings, warning)
        if len(warnings) >= max_items:
            return {"warnings": warnings[:max_items]}

    return {"warnings": warnings[:max_items]}


def _has_focused_scene_context_pack_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    for carrier in (bible, plan):
        if isinstance(carrier, dict) and _has_any_package_value(
            carrier,
            (
                "focused_scene_context_pack",
                "scene_context_pack",
                "llm_context_pack",
                "context_pack_preview",
            ),
        ):
            return True
    return False


def _missing_core_character_setup_warnings(*, bible: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for card in _as_dict_list(bible.get("character_cards")):
        name = _card_entity_name(card)
        if not name:
            continue
        if not _has_any_package_value(card, ("role", "goal", "external_want", "want", "summary", "identity")):
            warnings.append(f"missing_core_character_setup: {_truncate(name, 120)}")
    return warnings


def _character_age_year_mismatch_warnings(*, bible: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    current_year = _int_or_none(
        bible.get("current_year")
        or bible.get("story_year")
        or bible.get("narrative_year")
    )
    if current_year is None:
        return warnings

    for card in _as_dict_list(bible.get("character_cards")):
        name = _card_entity_name(card)
        age = _int_or_none(card.get("age") or card.get("current_age"))
        birth_year = _int_or_none(card.get("birth_year") or card.get("born_year"))
        if name and age is not None and birth_year is not None and abs((current_year - birth_year) - age) > 1:
            warnings.append(f"character_age_year_mismatch: {_truncate(name, 120)}")
    return warnings


def _missing_entity_reference_warnings(*, bible: dict[str, Any]) -> list[str]:
    known_entities = _known_canon_entity_keys(bible=bible)
    warnings: list[str] = []

    for scene in _as_dict_list(bible.get("scenes")) + _as_dict_list(bible.get("scene_cards")):
        for entity in _scene_referenced_entities(scene):
            key = _entity_key(entity)
            if key and key not in known_entities:
                warnings.append(f"missing_entity_reference: {_truncate(entity, 120)}")

    for package in _as_dict_list(bible.get("chapter_change_packages")):
        for entity in _scene_referenced_entities(package):
            key = _entity_key(entity)
            if key and key not in known_entities:
                warnings.append(f"missing_entity_reference: {_truncate(entity, 120)}")

    return _dedupe_ordered(warnings)


def _known_canon_entity_keys(*, bible: dict[str, Any]) -> set[str]:
    known: set[str] = set()
    for key in ("character_cards", "locations", "organizations", "world_rules", "items", "artifacts"):
        value = bible.get(key)
        if isinstance(value, dict):
            for name in value.keys():
                entity = _entity_key(str(name))
                if entity:
                    known.add(entity)
        for item in _as_dict_list(value):
            name = _first_named_value(item, ("name", "character_name", "location", "organization", "item", "artifact", "title"))
            entity = _entity_key(name)
            if entity:
                known.add(entity)
    return known


def _scene_referenced_entities(item: dict[str, Any]) -> list[str]:
    references: list[str] = []
    for key in ("entities", "referenced_entities", "mentions", "entity_refs"):
        value = item.get(key)
        if isinstance(value, list):
            for entry in value:
                if isinstance(entry, str):
                    references.append(entry)
                elif isinstance(entry, dict):
                    name = _first_named_value(entry, ("name", "entity", "label", "title"))
                    if name:
                        references.append(name)
        elif isinstance(value, str):
            references.append(value)
    return references


def _asymmetric_relationship_warnings(*, bible: dict[str, Any]) -> list[str]:
    relationships = _as_dict_list(bible.get("relationships"))
    if not relationships:
        return []

    edges: set[tuple[str, str, str]] = set()
    for item in relationships:
        source = _entity_key(_string_value(item.get("from") or item.get("source") or item.get("a") or item.get("character")))
        target = _entity_key(_string_value(item.get("to") or item.get("target") or item.get("b") or item.get("other")))
        relation = _entity_key(_string_value(item.get("type") or item.get("relationship") or item.get("status")))
        if source and target:
            edges.add((source, target, relation))

    warnings: list[str] = []
    for source, target, relation in edges:
        reverse_exists = any(
            other_source == target and other_target == source and (not relation or other_relation == relation)
            for other_source, other_target, other_relation in edges
        )
        if not reverse_exists:
            warnings.append(f"asymmetric_relationship: {_display_entity_key(source)}->{_display_entity_key(target)}")
    return _dedupe_ordered(warnings)


def _scene_state_conflict_warnings(*, bible: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for conflict in _as_dict_list(bible.get("scene_state_conflicts")):
        scene = _first_text(conflict, ("scene", "scene_name", "name", "location"))
        issue = _first_text(conflict, ("issue", "conflict", "description", "summary"))
        label = scene or issue or "unknown"
        suffix = f": {_truncate(issue, 120)}" if issue and issue != label else ""
        warnings.append(f"scene_state_conflict: {_truncate(label, 120)}{suffix}")

    for scene in _as_dict_list(bible.get("scenes")) + _as_dict_list(bible.get("scene_cards")):
        if _has_any_package_value(scene, ("state_conflict", "conflict", "contradiction")):
            label = _first_text(scene, ("name", "scene", "title", "summary"))
            warnings.append(f"scene_state_conflict: {_truncate(label or 'unknown', 120)}")
    return _dedupe_ordered(warnings)


def _universal_post_draft_review_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> dict[str, Any]:
    """Audit whether an accepted chapter has a full post-draft review packet."""
    warnings: list[str] = []
    packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    latest_package = packages[-1] if packages else None

    if latest_package is None:
        return {"warnings": ["missing_latest_chapter_for_post_draft_review"][:max_items]}

    if not _has_post_draft_review_checklist_surface(latest_package=latest_package, bible=bible, plan=plan):
        warnings.append("missing_post_draft_review_checklist")
    if not _has_mobile_readability_review_surface(latest_package=latest_package, bible=bible, plan=plan):
        warnings.append("missing_mobile_readability_review")
    if not _has_least_destructive_repair_scope_surface(latest_package=latest_package, bible=bible, plan=plan):
        warnings.append("missing_smallest_repair_scope")

    return {"warnings": warnings[:max_items]}


def _has_post_draft_review_checklist_surface(
    *,
    latest_package: dict[str, Any],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (latest_package, bible, plan) if isinstance(carrier, dict)]
    review_keys = (
        "post_draft_review",
        "chapter_review",
        "review_checklist",
        "acceptance_checklist",
        "quality_gate",
        "quality_scores",
    )
    if any(_has_any_package_value(carrier, review_keys) for carrier in carriers):
        return True

    required_dimensions = (
        "outline_fidelity",
        "continuity",
        "pov_control",
        "character_voice",
        "scene_conflict",
        "pacing",
        "reader_pull",
        "hook_payoff",
        "prose_naturalness",
    )
    return sum(1 for key in required_dimensions if _has_any_package_value(latest_package, (key,))) >= 3


def _has_mobile_readability_review_surface(
    *,
    latest_package: dict[str, Any],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (latest_package, bible, plan) if isinstance(carrier, dict)]
    return any(
        _has_any_package_value(
            carrier,
            (
                "mobile_readability_review",
                "mobile_readability",
                "paragraph_mobile_review",
                "readability_review",
                "mobile_layout_notes",
            ),
        )
        for carrier in carriers
    )


def _has_least_destructive_repair_scope_surface(
    *,
    latest_package: dict[str, Any],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (latest_package, bible, plan) if isinstance(carrier, dict)]
    return any(
        _has_any_package_value(
            carrier,
            (
                "repair_scope",
                "patch_scope",
                "least_destructive_repair",
                "revision_scope",
                "smallest_failing_artifact",
                "fix_scope",
            ),
        )
        for carrier in carriers
    )


def _has_opening_hook_type_surface(
    *,
    latest_package: Optional[dict[str, Any]],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (latest_package, bible, plan) if isinstance(carrier, dict)]
    if any(
        _has_any_package_value(
            carrier,
            ("opening_hook_type", "opening_hook", "hook_type", "chapter_opening_hook"),
        )
        for carrier in carriers
    ):
        return True
    return bool(_first_promise_payoff_debt_label(bible=bible, plan=plan))


def _has_ending_hook_job_surface(
    *,
    latest_package: Optional[dict[str, Any]],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (latest_package, bible, plan) if isinstance(carrier, dict)]
    if any(
        _has_any_package_value(
            carrier,
            ("ending_hook_job", "ending_hook", "chapter_ending_hook", "new_hook", "new_hooks"),
        )
        for carrier in carriers
    ):
        return True
    return bool(_status_items(_as_dict_list(bible.get("foreshadows")), done=False, max_items=1))


def _has_naturalness_texture_review_surface(
    *,
    latest_package: Optional[dict[str, Any]],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    carriers = [carrier for carrier in (latest_package, bible, plan) if isinstance(carrier, dict)]
    for carrier in carriers:
        if _has_any_package_value(
            carrier,
            (
                "prose_texture_review",
                "naturalness_review",
                "anti_ai_review",
                "ai_texture_review",
                "line_edit_notes",
                "prose_polish_notes",
                "natural_prose_pass",
            ),
        ):
            return True
    style_signature = bible.get("style_signature")
    if isinstance(style_signature, dict) and _has_any_package_value(
        style_signature,
        ("naturalness_review", "anti_ai_review", "prose_texture_review"),
    ):
        return True
    return False


def _reader_pull_fresh_reader_audit(
    *,
    bible: dict[str, Any],
    max_items: int,
) -> dict[str, Any]:
    """Audit whether the latest accepted chapter answers a fresh reader's pull test."""
    warnings: list[str] = []
    packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    latest_package = packages[-1] if packages else None

    if latest_package is None:
        return {"warnings": ["missing_latest_chapter_for_reader_pull_review"][:max_items]}

    style_signature = bible.get("style_signature") if isinstance(bible.get("style_signature"), dict) else {}

    if not (
        _has_any_package_value(latest_package, ("pov", "point_of_view", "viewpoint", "narrator"))
        or _has_any_package_value(style_signature, ("pov", "point_of_view", "viewpoint", "narrator"))
    ):
        warnings.append("missing_pov_anchor")

    if not (
        _has_any_package_value(
            latest_package,
            ("current_want", "want", "desire", "goal", "main_goal", "character_goal", "objective"),
        )
        or _chapter_package_character_state_has(latest_package, ("current_goal", "goal", "want", "desire"))
        or any(_has_any_package_value(card, ("goal", "external_want", "want", "current_goal")) for card in _as_dict_list(bible.get("character_cards")))
    ):
        warnings.append("missing_current_want")

    if not (
        _has_any_package_value(
            latest_package,
            ("obstacle", "main_obstacle", "conflict", "block", "blocked_by", "friction", "opposition"),
        )
        or _chapter_package_character_state_has(latest_package, ("obstacle", "block", "conflict", "opposition"))
        or any(_has_any_package_value(item, ("conflict", "pressure", "obstacle", "opposition")) for item in _as_dict_list(bible.get("conflicts")))
    ):
        warnings.append("missing_main_obstacle")

    if not _has_any_package_value(
        latest_package,
        ("stakes", "why_it_matters", "consequence", "cost", "risk", "risks", "danger", "pressure"),
    ):
        warnings.append("missing_stakes_or_why_it_matters")

    if not _has_latest_chapter_micro_payoff_signal(latest_package):
        warnings.append("missing_changed_exit_state")

    if not _has_latest_chapter_cliffhanger_signal(latest_package, bible=bible):
        warnings.append("missing_next_reader_pull")

    return {"warnings": warnings[:max_items]}


def _empty_reader_pull_fresh_reader_audit() -> dict[str, Any]:
    return {"warnings": []}


def _chapter_package_character_state_has(package: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return any(
        _has_any_package_value(item, keys)
        for item in _as_dict_list(package.get("character_state_changes"))
    )


def _has_structured_scene_beat_sheet(plan: Optional[dict[str, Any]]) -> bool:
    if not plan:
        return False
    for key in ("scene_beats", "scene_plan", "scenes", "beat_sheet"):
        if _has_any_package_value(plan, (key,)):
            return True
    scene_markers = ("scene", "location", "obstacle", "turn", "cost", "exit_state", "goal")
    structured_count = 0
    for beat in _as_dict_list(plan.get("beats")):
        if any(_has_any_package_value(beat, (marker,)) for marker in scene_markers):
            structured_count += 1
    return structured_count >= 2


def _story_foundry_production_handoff_audit(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> dict[str, Any]:
    """Audit Story Foundry-style draft→critique→fix→merge handoff evidence."""
    warnings: list[str] = []
    packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    latest_package = packages[-1] if packages else None

    if not _has_story_foundry_scene_card_surface(bible=bible, plan=plan):
        warnings.append("missing_scene_card_external_internal_spine")
    if not _has_story_bible_voice_canon_constraints(bible):
        warnings.append("missing_story_bible_voice_canon_constraints")

    if latest_package is None:
        warnings.append("missing_latest_chapter_for_production_handoff")
    else:
        if not _has_any_package_value(
            latest_package,
            ("critique", "critique_ref", "editor_feedback", "editor_report"),
        ):
            warnings.append("missing_editor_critique")
        if not _has_any_package_value(
            latest_package,
            ("fix_spec", "fix_spec_ref", "patch_plan", "revision_plan"),
        ):
            warnings.append("missing_fix_spec")
        if not _has_any_package_value(
            latest_package,
            ("revision_ref", "agent_draft_rev", "revised_draft_ref", "revision_summary"),
        ):
            warnings.append("missing_revision_evidence")
        if not _has_any_package_value(
            latest_package,
            ("editor_log", "editor_log_ref", "canon_promotion_log", "merge_log"),
        ):
            warnings.append("missing_editor_log")
        if not _has_any_package_value(
            latest_package,
            ("archivist_approval", "canon_promoted_by", "canon_promotion_status", "approved_by"),
        ):
            warnings.append("missing_archivist_canon_promotion")

    return {"warnings": warnings[:max_items]}


def _empty_story_foundry_production_handoff_audit() -> dict[str, Any]:
    return {"warnings": []}


def _has_story_foundry_scene_card_surface(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> bool:
    for source in (bible, plan or {}):
        for key in ("scene_cards", "scene_card", "scene_beats", "scene_plan", "scenes"):
            value = source.get(key)
            if isinstance(value, dict) and _scene_card_has_spine(value):
                return True
            for item in _as_dict_list(value):
                if _scene_card_has_spine(item):
                    return True
    return False


def _scene_card_has_spine(item: dict[str, Any]) -> bool:
    external = any(
        _has_any_package_value(item, keys)
        for keys in (
            ("alpha_point", "scene_function", "purpose"),
            ("goal", "external_goal"),
            ("conflict", "obstacles", "main_obstacle"),
            ("disaster", "hook", "ending_hook", "outcome"),
        )
    )
    internal = any(
        _has_any_package_value(item, keys)
        for keys in (
            ("desire", "internal_desire"),
            ("misbelief", "wound", "vulnerability"),
            ("emotional_stakes", "emotion", "internal_shift", "realization"),
            ("reaction", "dilemma", "decision"),
        )
    )
    return external and internal


def _has_story_bible_voice_canon_constraints(bible: dict[str, Any]) -> bool:
    has_voice = _has_any_package_value(bible, ("style_signature", "voiceSpec", "voice_spec"))
    has_canon = _has_any_package_value(
        bible,
        ("world_rules", "canon", "timeline", "organizations", "character_cards"),
    )
    has_constraints = _has_any_package_value(bible, ("hard_constraints", "constraints"))
    return has_voice and has_canon and has_constraints


def _empty_disassembly_checkpoint_audit() -> dict[str, Any]:
    return {
        "source_chapter_count": 0,
        "source_analysis_package_count": 0,
        "source_analysis_coverage_percent": 0,
        "missing_source_analysis_chapters": [],
        "has_qa_citation_jump_trace": False,
        "warnings": [],
    }


def _has_disassembly_evidence_refs(packages: list[dict[str, Any]]) -> bool:
    evidence_keys = (
        "evidence_refs",
        "source_refs",
        "citation_refs",
        "qa_citations",
        "chapter_jump_refs",
        "source_chapter_refs",
    )
    for package in packages:
        if _has_any_package_value(package, evidence_keys):
            return True
        for item in _as_dict_list(package.get("qa_notes")) + _as_dict_list(package.get("citations")):
            if _has_any_package_value(item, evidence_keys + ("chapter_number", "chapter_ref", "source_ref")):
                return True
    return False


def _compress_chapter_numbers(chapter_numbers: list[int]) -> list[str]:
    if not chapter_numbers:
        return []
    ordered = sorted(set(chapter_numbers))
    ranges: list[str] = []
    start = previous = ordered[0]
    for current in ordered[1:]:
        if current == previous + 1:
            previous = current
            continue
        ranges.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = current
    ranges.append(str(start) if start == previous else f"{start}-{previous}")
    return ranges


def _chapter_identity_key(package: dict[str, Any]) -> tuple[str, int | str] | None:
    chapter_number = _int_or_none(package.get("chapter_number"))
    if chapter_number is not None:
        return ("chapter_number", chapter_number)
    chapter_id = _string_value(package.get("chapter_id"))
    if chapter_id:
        return ("chapter_id", chapter_id)
    return None


def _chapter_range_payload(chapter_numbers: list[int]) -> dict[str, int | None]:
    if not chapter_numbers:
        return {"start": None, "end": None}
    return {"start": chapter_numbers[0], "end": chapter_numbers[-1]}


def _chapter_sequence_gaps(chapter_numbers: list[int]) -> list[str]:
    ordered = sorted(set(chapter_numbers))
    gaps: list[str] = []
    for previous, current in zip(ordered, ordered[1:]):
        if current <= previous + 1:
            continue
        start = previous + 1
        end = current - 1
        gaps.append(str(start) if start == end else f"{start}-{end}")
    return gaps


def _timeline_progression_payload(packages: list[dict[str, Any]], *, max_items: int = 12) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for package in packages[-max_items:]:
        chapter_number = _int_or_none(package.get("chapter_number"))
        for item in _as_dict_list(package.get("timeline_delta")):
            event = _first_text(item, ("event", "summary", "content"))
            if not event:
                continue
            points.append({"chapter_number": chapter_number, "event": event})
            break
    return points


def _latest_character_state_payload(packages: list[dict[str, Any]], *, max_items: int) -> list[dict[str, Any]]:
    latest_by_character: dict[str, dict[str, Any]] = {}
    for package in packages:
        chapter_number = _int_or_none(package.get("chapter_number"))
        for item in _as_dict_list(package.get("character_state_changes")):
            name = _string_value(item.get("character_name") or item.get("name"))
            state_after = _string_value(item.get("state_after"))
            if not name or not state_after:
                continue
            previous = latest_by_character.get(name)
            current_chapter = chapter_number or 0
            previous_chapter = int(previous.get("chapter_number") or 0) if previous else -1
            if previous is None or current_chapter >= previous_chapter:
                latest_by_character[name] = {
                    "character_name": name,
                    "chapter_number": chapter_number,
                    "state_after": state_after,
                }

    return sorted(
        latest_by_character.values(),
        key=lambda item: int(item.get("chapter_number") or 0),
        reverse=True,
    )[:max_items]


def _emotional_progression_payload(
    packages: list[dict[str, Any]],
    *,
    max_items: int,
) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for package in packages[-max_items:]:
        emotional_arc = package.get("emotional_arc")
        if not isinstance(emotional_arc, dict):
            continue

        item: dict[str, Any] = {
            "chapter_number": _int_or_none(package.get("chapter_number")),
        }
        tone = _string_value(
            emotional_arc.get("tone")
            or emotional_arc.get("primary_emotion")
            or emotional_arc.get("emotion")
        )
        if tone:
            item["tone"] = tone
        if emotional_arc.get("intensity") is not None:
            item["intensity"] = emotional_arc.get("intensity")
        if emotional_arc.get("curve") is not None:
            item["curve"] = emotional_arc.get("curve")

        if len(item) > 1:
            points.append(item)
    return points


def _build_timeline_progression(packages: list[dict[str, Any]], *, max_items: int = 4) -> str:
    points: list[str] = []
    for package in packages[-max_items:]:
        chapter_number = package.get("chapter_number")
        for item in _as_dict_list(package.get("timeline_delta")):
            event = _first_text(item, ("event", "summary", "content"))
            if not event:
                continue
            prefix = f"Ch{chapter_number} " if chapter_number not in (None, "") else ""
            points.append(f"{prefix}{event}")
            break
    return " -> ".join(points)


def _latest_character_states(packages: list[dict[str, Any]], *, max_items: int) -> list[str]:
    latest_by_character: dict[str, tuple[int, str]] = {}
    for package in packages:
        chapter_number = _int_or_none(package.get("chapter_number")) or 0
        for item in _as_dict_list(package.get("character_state_changes")):
            name = _string_value(item.get("character_name") or item.get("name"))
            state_after = _string_value(item.get("state_after"))
            if not name or not state_after:
                continue
            previous = latest_by_character.get(name)
            if previous is None or chapter_number >= previous[0]:
                latest_by_character[name] = (chapter_number, state_after)

    ordered = sorted(latest_by_character.items(), key=lambda item: item[1][0], reverse=True)
    states: list[str] = []
    for name, (chapter_number, state_after) in ordered[:max_items]:
        chapter = f" @ Ch{chapter_number}" if chapter_number else ""
        states.append(f"{name}{chapter} -> {state_after}")
    return states


def _hook_status_summary(packages: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    resolved: list[str] = []
    opened: list[str] = []
    for package in packages:
        for item in _as_dict_list(package.get("foreshadow_changes")):
            hook = _first_text(item, ("hook", "title", "content", "summary"))
            if not hook:
                continue
            if _is_done_status(item.get("status")):
                _append_unique(resolved, hook)
            else:
                _append_unique(opened, hook)
    return resolved, opened


def _pending_plan_beats(*, plan: Optional[dict[str, Any]], max_items: int) -> list[str]:
    if not plan:
        return []
    pending: list[str] = []
    for item in _status_items(_as_dict_list(plan.get("beats")), done=False, max_items=max_items):
        beat = _first_text(item, ("beat", "summary", "content", "name"))
        if beat:
            _append_unique(pending, beat)
    return pending[:max_items]


def _completed_plan_beats(
    packages: list[dict[str, Any]],
    *,
    plan: Optional[dict[str, Any]],
    max_items: int,
) -> list[str]:
    completed: list[str] = []
    for package in packages:
        for item in _as_dict_list(package.get("plan_progress")):
            if not _is_done_status(item.get("status")):
                continue
            beat = _first_text(item, ("beat", "summary", "content", "name"))
            if beat:
                _append_unique(completed, beat)

    if len(completed) < max_items and plan:
        for item in _status_items(_as_dict_list(plan.get("beats")), done=True, max_items=max_items):
            beat = _first_text(item, ("beat", "summary", "content", "name"))
            if beat:
                _append_unique(completed, beat)
    return completed[:max_items]


def _append_unique(items: list[str], value: str) -> None:
    normalized = value.strip().lower()
    if not normalized:
        return
    if any(existing.strip().lower() == normalized for existing in items):
        return
    items.append(value)


def _append_chapter_change_package_section(
    *,
    lines: list[str],
    packages: Any,
    max_items: int,
) -> None:
    normalized_packages = _chapter_analysis_packages(packages)[:max_items]
    if not normalized_packages:
        return

    lines.append("")
    lines.append("Recent chapter change packages:")
    for package in normalized_packages:
        chapter_label = _chapter_package_label(package)
        summary = _string_value(package.get("summary"))
        if summary:
            lines.append(f"- {chapter_label}: {_truncate(summary, 220)}")
        else:
            lines.append(f"- {chapter_label}")

        for item in _as_dict_list(package.get("timeline_delta"))[:3]:
            event = _first_text(item, ("event", "summary", "content"))
            if event:
                lines.append(f"  - timeline: {_truncate(event, 220)}")

        for item in _as_dict_list(package.get("character_state_changes"))[:3]:
            name = _string_value(item.get("character_name") or item.get("name")) or "Unknown character"
            state_after = _string_value(item.get("state_after"))
            key_event = _string_value(item.get("key_event"))
            detail = f"{name} -> {state_after}" if state_after else name
            if key_event:
                detail = f"{detail} ({key_event})"
            lines.append(f"  - character: {_truncate(detail, 220)}")

        emotional_arc = package.get("emotional_arc") if isinstance(package.get("emotional_arc"), dict) else None
        if emotional_arc:
            emotion_parts: list[str] = []
            tone = _string_value(
                emotional_arc.get("tone")
                or emotional_arc.get("primary_emotion")
                or emotional_arc.get("emotion")
            )
            if tone:
                emotion_parts.append(f"tone: {tone}")
            if emotional_arc.get("intensity") is not None:
                emotion_parts.append(f"intensity: {emotional_arc.get('intensity')}")
            if emotional_arc.get("curve") is not None:
                curve = json.dumps(emotional_arc.get("curve"), ensure_ascii=False, sort_keys=True)
                emotion_parts.append(f"curve: {curve}")
            if emotion_parts:
                lines.append(f"  - emotion: {_truncate(' | '.join(emotion_parts), 220)}")

        for item in _as_dict_list(package.get("foreshadow_changes"))[:3]:
            hook = _first_text(item, ("hook", "title", "content", "summary"))
            status = _string_value(item.get("status"))
            suffix = f" (status: {status})" if status else ""
            lines.append(f"  - hook: {_truncate(hook + suffix, 220)}")

        for item in _as_dict_list(package.get("plan_progress"))[:3]:
            beat = _first_text(item, ("beat", "summary", "content", "name"))
            status = _string_value(item.get("status"))
            suffix = f" (status: {status})" if status else ""
            lines.append(f"  - plan: {_truncate(beat + suffix, 220)}")

        guardrail_check = package.get("guardrail_check") if isinstance(package.get("guardrail_check"), dict) else None
        if guardrail_check:
            lines.append(f"  - Guardrail rewrite applied: {bool(guardrail_check.get('applied'))}")
            violations = _as_dict_list(guardrail_check.get("violations"))
            for violation in violations[:3]:
                violation_type = _string_value(violation.get("type"))
                severity = _string_value(violation.get("severity"))
                description = _first_text(violation, ("description", "detail", "message", "title"))
                parts = [part for part in (violation_type, severity, description) if part]
                if parts:
                    lines.append(f"  - guardrail: {_truncate(' | '.join(parts), 220)}")


def _append_source_pattern_pack_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    title: str = "Source-discovered continuation guidance:",
    include_inspired_guidance: bool = False,
) -> None:
    if not source_pattern_pack:
        return

    digest = render_source_pattern_pack_digest(
        source_pattern_pack,
        include_inspired_guidance=include_inspired_guidance,
    )
    if not digest or digest.startswith("(no public source pattern pack"):
        return

    lines.append("")
    lines.append(title)
    lines.extend(digest.splitlines())


def _append_source_rights_provenance_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render source rights and provenance admission gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant = {
        "source_license_detection_gate",
        "spdx_reuse_compliance_gate",
        "public_domain_corpus_boundary",
        "attribution_derivative_work_gate",
    }
    if not pattern_names.intersection(relevant):
        return

    lines.append("")
    lines.append("Source rights provenance audit:")
    if "source_license_detection_gate" in pattern_names:
        lines.append("- source_license_detection_gate: block long source text until license status, detector confidence, and reviewer decision are recorded")
    if "spdx_reuse_compliance_gate" in pattern_names:
        lines.append("- spdx_reuse_compliance_gate: keep SPDX ids, copyright holders, attribution notes, and source-file provenance outside story canon")
    if "public_domain_corpus_boundary" in pattern_names:
        lines.append("- public_domain_corpus_boundary: public-domain sources still need title, author, source URL, observed date, extraction format, and jurisdiction caveat")
    if "attribution_derivative_work_gate" in pattern_names:
        lines.append("- attribution_derivative_work_gate: attribution does not replace independent plot, character, setting, event order, and phrasing checks")


def _append_source_entity_redaction_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render source entity redaction and proper-noun leakage gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant = {
        "source_entity_redaction_gate",
        "custom_entity_label_inventory",
        "placeholder_alias_consistency_map",
        "proper_noun_leakage_review",
    }
    if not pattern_names.intersection(relevant):
        return

    lines.append("")
    lines.append("Source entity redaction audit:")
    if "source_entity_redaction_gate" in pattern_names:
        lines.append("- source_entity_redaction_gate: redact source-specific names, places, factions, artifacts, powers, titles, and proper nouns before same-type drafting")
    if "custom_entity_label_inventory" in pattern_names:
        lines.append("- custom_entity_label_inventory: track fiction labels beyond PERSON/ORG/LOC, including faction, rank, artifact, power, species, title, and invented term")
    if "placeholder_alias_consistency_map" in pattern_names:
        lines.append("- placeholder_alias_consistency_map: keep stable placeholders and replacement ids across chapters; review alias collisions before context reuse")
    if "proper_noun_leakage_review" in pattern_names:
        lines.append("- proper_noun_leakage_review: compare drafts against source blocklists and approved exceptions before accepting continuation or same-type prose")


def _append_universal_novel_workflow_contract_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render portable novel-writing gates learned from static skill intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "universal_novel_mode_contract_gate",
        "portable_story_project_structure_gate",
        "chapter_contract_scene_beat_gate",
        "reader_promise_micro_payoff_gate",
        "revision_order_natural_prose_gate",
        "reader_pull_fresh_reader_gate",
        "progress_report_continuity_writeback_gate",
        "post_draft_review_checklist_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Universal novel workflow contract:")
    if "universal_novel_mode_contract_gate" in pattern_names:
        lines.append("- mode_selection: choose the smallest explicit mode before output: continue-chapter, full-project, revise, analyze, export, or quick-start")
    if "portable_story_project_structure_gate" in pattern_names:
        lines.append("- portable_state_files: keep story-bible.md, outline.md, characters.md, worldbuilding.md, continuity.md, progress.md, chapters/, notes/, and revision/ as separate state layers")
    if "chapter_contract_scene_beat_gate" in pattern_names:
        lines.append("- chapter_contract: require job, reader promise, POV, opening hook, goal, obstacle, escalation, payoff, new hook, and forbidden contradictions before prose")
        lines.append("- scene_exit_state: each scene should leave a changed plot, knowledge, relationship, risk, moral pressure, emotion, or world-rule state")
    if "reader_promise_micro_payoff_gate" in pattern_names:
        lines.append("- reader_micro_payoff: each serial chapter needs a concrete payoff or pressure turn, and wins must carry cost, debt, reaction, or board-state change")
    if "revision_order_natural_prose_gate" in pattern_names:
        lines.append("- revision_order: fix developmental, character, continuity, and scene problems before line polish or proof/format cleanup")
        lines.append("- natural_prose_pass: replace generic emotion labels with concrete action, sensory detail, subtext, character diction, and varied rhythm")
    if "reader_pull_fresh_reader_gate" in pattern_names:
        lines.append("- reader_pull_test: a fresh reader must identify POV, want, obstacle, stakes, changed exit state, and the next pull")
    if "progress_report_continuity_writeback_gate" in pattern_names:
        lines.append("- progress_writeback: after an accepted chapter, record summary, new facts, character changes, hooks paid off, new hooks, continuity updates, next focus, and risks")
    if "post_draft_review_checklist_gate" in pattern_names:
        lines.append("- post_draft_review: accept chapters only after structure, continuity, POV, voice, conflict, pacing, reader-pull, hook/payoff, naturalness, and mobile-readability review")


def _append_universal_project_memory_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render durable project-memory and file-custody gates from universal writing intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "portable_story_project_structure_gate" not in pattern_names:
        return

    hints = (
        _as_note_list(source_pattern_pack.get("portable_story_project_structure_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Universal project memory gate:")
    lines.append(
        "- project_file_manifest: keep story-bible.md, outline.md, characters.md, "
        "worldbuilding.md, continuity.md, progress.md, chapters/, notes/, and revision/ "
        "as target-owned memory surfaces"
    )
    lines.append(
        "- startup_status_packet: record loaded files, current progress, last chapter "
        "summary, top open threads/promises, and next likely action before drafting"
    )
    lines.append(
        "- story_bible_north_star: preserve premise, reader promise, emotional target, "
        "theme, ending direction, must-preserve facts, and must-avoid boundaries"
    )
    lines.append(
        "- character_engine_cards: track external want, internal need, wound/lie/flaw, "
        "cost, relationship movement, and voice fingerprint before scene prose"
    )
    lines.append(
        "- world_rule_cost_custody: rules, factions, locations, research notes, costs, "
        "limits, and uncertainty labels must be explicit before they affect canon"
    )
    lines.append(
        "- continuity_decision_ledger: update timeline, facts, foreshadowing/payoff, "
        "unresolved questions, character state, and decision log after acceptance"
    )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: source story bible, character sheets, world rules, "
            "continuity ledgers, progress files, and chapter files define workflow axes only"
        )
    else:
        lines.append(
            "- continuation_boundary: only target-owned project memory, current accepted "
            "chapter state, and approved plan deltas can influence the next chapter"
        )
    lines.append(
        "- no_overwrite_boundary: never overwrite, delete, or silently rewrite manuscript "
        "or canon files; use accepted patches, versioned files, or revision notes"
    )
    lines.append(
        "- runtime_boundary: no local skill install, script execution, provider call, "
        "browser/MCP/desktop runtime, credential read, prompt-body transplant, or "
        "out-of-scope manuscript access is authorized"
    )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 260)}")


def _append_seed_to_bible_foundation_loop_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render seed-to-bible scoring loops and layered bible artifact custody."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    has_foundation_loop = "seed_to_bible_foundation_loop_gate" in pattern_names
    has_layer_contract = "layered_story_bible_artifact_contract_gate" in pattern_names
    if not has_foundation_loop and not has_layer_contract:
        return

    foundation_hints = (
        _as_note_list(source_pattern_pack.get("seed_to_bible_foundation_loop_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    layer_hints = (
        _as_note_list(source_pattern_pack.get("layered_story_bible_artifact_contract_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Seed-to-bible foundation loop gate:")
    if has_foundation_loop:
        lines.append(
            "- foundation_score_loop: validate seed differentiator, central tension, "
            "cost/constraint, sensory hook, foundation_score, lore_score, and max-iteration stop"
        )
        lines.append(
            "- weakest_dimension_repair: identify the weakest dimension before any rewrite; "
            "regenerate only that layer or chapter brief instead of restarting the whole project"
        )
        lines.append(
            "- keep_discard_restore_policy: compare before/after scores, keep accepted "
            "improvements, discard regressions, and restore the previous accepted version"
        )
        lines.append(
            "- independent_eval_boundary: generation, judge, mechanical slop scan, "
            "cross-layer consistency check, and reader-panel findings stay separate"
        )
    if has_layer_contract:
        lines.append(
            "- layered_story_bible_artifacts: seed, world, characters, voice, mystery, "
            "outline, canon, foreshadowing, state, eval logs, and score ledger remain separate"
        )
        lines.append(
            "- dependency_order: world -> characters -> voice -> mystery -> outline -> "
            "canon -> foreshadowing before chapter-level automation"
        )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: source seed, bible layers, scores, reader-panel findings, "
            "and accepted artifacts define review axes only, never target canon"
        )
    else:
        lines.append(
            "- continuation_boundary: only target-owned accepted foundation layers and "
            "current score-review findings can seed outline or chapter continuation"
        )
    lines.append(
        "- runtime_boundary: no auto-outline CLI, uv/pip install, provider/API key, gateway, "
        "proxy transport, model call, generated bible, eval log import, or upstream prompt body is authorized"
    )
    if foundation_hints:
        lines.append(f"- foundation_source_hint: {_truncate(foundation_hints[0], 240)}")
    if layer_hints:
        lines.append(f"- layer_source_hint: {_truncate(layer_hints[0], 240)}")


def _append_universal_deep_planning_revision_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render deeper universal-novel planning, scene, and revision contracts."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    has_premise_gate = "premise_structure_hook_payoff_gate" in pattern_names
    has_scene_gate = "scene_goal_obstacle_cost_exit_gate" in pattern_names
    has_revision_gate = "revision_finding_patch_strategy_gate" in pattern_names
    if not (has_premise_gate or has_scene_gate or has_revision_gate):
        return

    premise_hints = (
        _as_note_list(source_pattern_pack.get("premise_structure_hook_payoff_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    scene_hints = (
        _as_note_list(source_pattern_pack.get("scene_goal_obstacle_cost_exit_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    revision_hints = (
        _as_note_list(source_pattern_pack.get("revision_finding_patch_strategy_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Universal deep planning and revision gate:")
    if has_premise_gate:
        lines.append(
            "- premise_stress_test: cite premise/logline, protagonist want, opposition, "
            "stakes, ending direction, and chosen structure before long drafting"
        )
        lines.append(
            "- hook_payoff_matrix: list thread, seeded-in point, reader expectation, "
            "planned payoff, maximum delay, and current status"
        )
    if has_scene_gate:
        lines.append(
            "- scene_goal_obstacle_cost_exit: each scene needs POV, goal, obstacle, "
            "tactic, turn, cost, and changed exit state"
        )
        lines.append(
            "- scene_exit_change_rule: exit must change plot, knowledge, relationship, "
            "risk, moral pressure, emotion, or world-rule understanding"
        )
    if has_revision_gate:
        lines.append(
            "- revision_findings_severity: lead review with Critical/High/Medium/Low "
            "findings before line-level polish"
        )
        lines.append(
            "- least_destructive_patch_strategy: repair only the failing paragraph, "
            "scene, ledger field, or chapter contract unless structural scope is proven"
        )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: rebuild premise/logline, cast, hook-payoff ids, "
            "scene goals, costs, and patch notes inside target canon; never reuse the "
            "source premise, hook/payoff matrix, scene beats, or revision findings"
        )
    else:
        lines.append(
            "- continuation_boundary: use only target-owned accepted premise, arc, "
            "hook/payoff, scene, and revision artifacts as continuation authority"
        )
    lines.append(
        "- runtime_boundary: no source prompt bodies, manuscript imports, provider calls, "
        "browser/MCP runtime, or upstream patch notes may be promoted without target review"
    )
    for label, hints in (
        ("premise_source_hint", premise_hints),
        ("scene_source_hint", scene_hints),
        ("revision_source_hint", revision_hints),
    ):
        if hints:
            lines.append(f"- {label}: {_truncate(hints[0], 240)}")


def _append_genre_promise_contract_matrix_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render genre-promise matrix gates from universal genre-pattern intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "genre_promise_contract_matrix_gate" not in pattern_names:
        return

    hints = (
        _as_note_list(source_pattern_pack.get("genre_promise_contract_matrix_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Genre promise contract matrix gate:")
    lines.append(
        "- expected_reader_pleasure: name what the reader came for before outlining: "
        "mystery, romance, progression, justice, fear, wonder, comedy, literary resonance, or another concrete promise"
    )
    lines.append(
        "- payoff_timing_boundary: record how quickly that pleasure appears and what must be planted before each payoff"
    )
    lines.append(
        "- welcome_and_tired_tropes: list welcome tropes, tired tropes that need a twist, and taboo moves for this subgenre"
    )
    lines.append(
        "- emotional_aftertaste: state the intended aftertaste so hooks, scene costs, and line polish serve the same reader contract"
    )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: source genre promise, trope timing, and emotional aftertaste are craft axes only; "
            "do not reuse source trope sequence, reveal order, scene objects, names, or payoff mechanics"
        )
    else:
        lines.append(
            "- continuation_boundary: genre promise choices must follow accepted canon, open hooks, character state, and current payoff debt"
        )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 260)}")


def _append_subgenre_specific_ledger_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render subgenre-specific ledger gates from universal genre-pattern intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "subgenre_specific_ledger_gate" not in pattern_names:
        return

    hints = (
        _as_note_list(source_pattern_pack.get("subgenre_specific_ledger_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Subgenre-specific ledger gate:")
    lines.append(
        "- active_ledger_selection: choose only the ledgers the current genre promise needs, such as trust, clue/suspect, realm-resource-cost, deadline/asymmetry, magic-rule-cost, what-if consequence, threat-rule, research, or motif ledgers"
    )
    lines.append(
        "- ledger_debt_fields: each selected ledger names what is tracked, who knows it, where it was planted, payoff/cost owed, max safe delay, and contradiction risk"
    )
    lines.append(
        "- acceptance_boundary: a chapter or plan passes only when its payoffs, reveals, trust moves, upgrades, threats, or motifs update the selected ledger"
    )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: transfer the ledger category and discipline only; rebuild all clues, suspects, trust breaks, realms, rules, deadlines, threats, motifs, and consequences"
        )
    else:
        lines.append(
            "- continuation_boundary: selected ledgers must extend accepted canon and current open debts, not create a parallel unsupported genre system"
        )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 260)}")


def _append_universal_intake_export_rollback_gate_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render compact intake, export, and rollback gates from universal writing intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "five_question_intake_story_promise_gate",
        "universal_export_clean_manuscript_gate",
        "minimal_rollback_repair_scope_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    five_question_hints = (
        _as_note_list(source_pattern_pack.get("five_question_intake_story_promise_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    export_hints = (
        _as_note_list(source_pattern_pack.get("universal_export_clean_manuscript_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    rollback_hints = (
        _as_note_list(source_pattern_pack.get("minimal_rollback_repair_scope_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    audit = _universal_intake_export_rollback_audit(
        bible=bible,
        plan=plan,
        pattern_names=pattern_names,
        max_items=12,
    )

    lines.append("")
    lines.append("Universal intake, export, and rollback gate:")
    if "five_question_intake_story_promise_gate" in pattern_names:
        lines.append(
            "- five_question_intake: ask at most five setup questions before producing "
            "logline, reader promise, protagonist arc, opposition, world rules, ending "
            "direction, and 5-15 beats"
        )
    if "universal_export_clean_manuscript_gate" in pattern_names:
        lines.append(
            "- clean_manuscript_export: export mode packages only accepted chapters into "
            "a clean manuscript or structured export plan; drafts, review notes, and prompt "
            "residue stay out"
        )
    if "minimal_rollback_repair_scope_gate" in pattern_names:
        lines.append(
            "- minimal_rollback_repair_scope: when a gate fails, repair the smallest "
            "failing artifact before broad regeneration"
        )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: source intake shape, export checklist, and rollback "
            "discipline are workflow axes only; rebuild the target premise, beats, export "
            "manifest, and repair notes independently"
        )
    else:
        lines.append(
            "- continuation_boundary: intake, export, and rollback decisions must follow "
            "target-owned canon, accepted chapters, current plan, and explicit export scope"
        )
    lines.append(
        "- runtime_boundary: static intake authorizes no provider call, source manuscript "
        "body import, installer, export tool execution, or broad overwrite"
    )
    for label, hints in (
        ("five_question_source_hint", five_question_hints),
        ("clean_export_source_hint", export_hints),
        ("rollback_source_hint", rollback_hints),
    ):
        if hints:
            lines.append(f"- {label}: {_truncate(hints[0], 260)}")
    if audit["warnings"] and mode != "same-type":
        lines.append(f"- intake_export_rollback_warnings: {', '.join(audit['warnings'])}")


def _append_local_first_authoring_revision_gate_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render local-first provider, suggestion-card, and book-view manifest gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "local_first_provider_boundary_authoring_gate",
        "suggestion_card_nonoverwrite_revision_gate",
        "book_view_import_export_manifest_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    provider_hints = (
        _as_note_list(source_pattern_pack.get("local_first_provider_boundary_authoring_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    suggestion_hints = (
        _as_note_list(source_pattern_pack.get("suggestion_card_nonoverwrite_revision_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    book_view_hints = (
        _as_note_list(source_pattern_pack.get("book_view_import_export_manifest_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    audit = _local_first_authoring_revision_audit(
        bible=bible,
        plan=plan,
        pattern_names=pattern_names,
        max_items=12,
    )

    lines.append("")
    lines.append("Local-first authoring and suggestion-card gate:")
    if "local_first_provider_boundary_authoring_gate" in pattern_names:
        lines.append(
            "- local_first_provider_boundary_authoring_gate: record whether this run uses "
            "WebLLM/WebGPU, Ollama, cloud-key provider, or no-model fallback before any prompt leaves local storage"
        )
    if "suggestion_card_nonoverwrite_revision_gate" in pattern_names:
        lines.append(
            "- suggestion_card_nonoverwrite_revision_gate: AI edits stay as accept/reject "
            "cards and never overwrite accepted prose without author approval"
        )
    if "book_view_import_export_manifest_gate" in pattern_names:
        lines.append(
            "- book_view_import_export_manifest_gate: book view/export needs front matter, "
            "live pagination, import auto-split status, and EPUB/PDF/Markdown manifest evidence"
        )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: provider posture, suggestion-card workflow, and book-view manifest are transferable control patterns; source app UI, storage, examples, and code stay excluded"
        )
    else:
        lines.append(
            "- continuation_boundary: local-first provider mode, accepted suggestion cards, and export manifest must reference the target project state only"
        )
    lines.append(
        "- runtime_boundary: no browser storage read, package install, WebLLM/Ollama/cloud call, import parser execution, or export build is authorized by static intake"
    )
    for label, hints in (
        ("provider_boundary_source_hint", provider_hints),
        ("suggestion_card_source_hint", suggestion_hints),
        ("book_view_source_hint", book_view_hints),
    ):
        if hints:
            lines.append(f"- {label}: {_truncate(hints[0], 260)}")
    if audit["warnings"] and mode != "same-type":
        lines.append(f"- local_first_authoring_warnings: {', '.join(audit['warnings'])}")


def _append_universal_hook_naturalness_gate_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render chapter hook integrity and anti-AI texture gates from universal intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    has_hook_gate = "opening_ending_hook_integrity_gate" in pattern_names
    has_texture_gate = "anti_ai_naturalness_texture_gate" in pattern_names
    if not has_hook_gate and not has_texture_gate:
        return

    hook_hints = (
        _as_note_list(source_pattern_pack.get("opening_ending_hook_integrity_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    texture_hints = (
        _as_note_list(source_pattern_pack.get("anti_ai_naturalness_texture_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    audit = _universal_hook_naturalness_audit(
        bible=bible,
        plan=plan,
        pattern_names=pattern_names,
        max_items=12,
    )

    if has_hook_gate:
        lines.append("")
        lines.append("Opening/ending hook integrity gate:")
        lines.append(
            "- opening_hook_type: choose a visible hook type before prose: danger, "
            "question, almost-within-reach promise, contradiction, unexpected action, "
            "meaningful sensory image, prior-choice consequence, conflict dialogue, "
            "public pressure, or quiet image before disruption"
        )
        lines.append(
            "- bad_opening_boundary: generic weather, waking up, mirror description, "
            "and lore exposition are rejected unless they carry immediate conflict or subtext"
        )
        lines.append(
            "- ending_hook_job: ending must reveal danger, reframe fact, force decision, "
            "show cost, collide desires, pay one thread while opening another, or end on a changed image"
        )
        lines.append(
            "- fake_cliffhanger_boundary: do not accept a cliffhanger that resolves instantly "
            "without cost, state change, or payoff debt movement"
        )
        if mode == "same-type":
            lines.append(
                "- same_type_boundary: source opening hooks, ending hook jobs, and hook pressure define craft axes only; "
                "the target story needs independent hook content and consequences"
            )
        else:
            lines.append(
                "- continuation_boundary: hook choices must follow the target's last accepted "
                "physical/emotional state and open promise debts"
            )
        if hook_hints:
            lines.append(f"- hook_source_hint: {_truncate(hook_hints[0], 240)}")

    if has_texture_gate:
        lines.append("")
        lines.append("Anti-AI naturalness texture gate:")
        lines.append(
            "- texture_review: scan for balanced essay rhythm, generic emotion labels, "
            "over-neat moral summaries, repetitive transition words, polished summary dialogue, "
            "and same-length paragraphs before accepting prose"
        )
        lines.append(
            "- naturalness_repair: replace generic AI texture with concrete action, uneven rhythm, "
            "subtext, silence/avoidance, sensory pressure, and character-specific diction"
        )
        lines.append(
            "- generic_ai_texture_boundary: naturalization is a manuscript-quality review, "
            "not an AI-detector bypass claim and not permission to imitate source phrasing"
        )
        if mode == "same-type":
            lines.append(
                "- same_type_boundary: source cleanup notes may define review criteria only; "
                "target prose must remain independent in phrasing, imagery, and scene order"
            )
        else:
            lines.append(
                "- continuation_boundary: texture repair preserves accepted facts, sequence, "
                "POV, and continuity while changing only expression where needed"
            )
        if texture_hints:
            lines.append(f"- texture_source_hint: {_truncate(texture_hints[0], 240)}")

    if audit["warnings"] and mode != "same-type":
        lines.append(f"- hook_naturalness_warnings: {', '.join(audit['warnings'])}")


def _append_universal_post_draft_review_gate_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render post-draft checklist and smallest-repair gates from universal intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "post_draft_review_checklist_gate" not in pattern_names:
        return

    hints = (
        _as_note_list(source_pattern_pack.get("post_draft_review_checklist_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    audit = _universal_post_draft_review_audit(
        bible=bible,
        plan=plan,
        max_items=12,
    )

    lines.append("")
    lines.append("Universal post-draft review gate:")
    lines.append(
        "- checklist_dimensions: review outline fidelity, continuity, POV control, "
        "character voice, scene conflict, pacing, reader-pull, hook/payoff, prose "
        "naturalness, and mobile readability before accepting a chapter"
    )
    lines.append(
        "- mobile_readability: check paragraph length, turn placement, dialogue spacing, "
        "chapter title/header clarity, and whether the first screen carries reader pull"
    )
    lines.append(
        "- least_destructive_repair: if a dimension fails, repair the smallest failing "
        "artifact: paragraph, scene, ledger field, chapter contract, or review note"
    )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: source review notes, chapter fixes, and readability "
            "patches define review axes only; target findings must be produced from "
            "target-owned drafts"
        )
    else:
        lines.append(
            "- continuation_boundary: post-draft review must evaluate the latest accepted "
            "target chapter and cannot import source review notes as canon"
        )
    lines.append(
        "- runtime_boundary: this is a local review contract; no provider call, external "
        "editor, source manuscript import, or detector service is authorized by static intake"
    )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 260)}")
    if audit["warnings"] and mode != "same-type":
        lines.append(f"- post_draft_review_warnings: {', '.join(audit['warnings'])}")


def _append_novelforge_version_safe_scene_fact_pipeline_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render version-safe scene/fact custody gates from NovelForge-style intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "versioned_scene_fact_review_pipeline_gate",
        "novelforge_version_safe_human_review_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    version_hints: list[str] = []
    review_hints: list[str] = []
    if isinstance(source_pattern_pack, dict):
        version_hints = _as_note_list(
            source_pattern_pack.get("versioned_scene_fact_review_pipeline_gate_hints")
        )
        review_hints = _as_note_list(
            source_pattern_pack.get("novelforge_version_safe_human_review_gate_hints")
        )

    lines.append("")
    lines.append("NovelForge version-safe scene/fact pipeline gate:")
    lines.append(
        "- scene_version_lineage: keep draft, archived, revised, and accepted scene states traceable; "
        "do not overwrite accepted prose without a new reviewable version"
    )
    lines.append(
        "- fact_approval_queue: extracted facts stay pending until reviewed; only approved facts may update canon, "
        "memory chunks, summaries, or continuity state"
    )
    lines.append(
        "- focused_retrieval_scope: assemble only the facts, memory chunks, reference assets, state, and scene versions "
        "needed for the next decision"
    )
    lines.append(
        "- continuity_reviewreport: review contradictions, missing motive, stale references, and source-boundary risks "
        "before accepting the scene or chapter"
    )
    lines.append(
        "- accepted_export_readiness: only accepted scenes/chapters can move into manuscript merge, Markdown/DOCX export, "
        "or downstream continuity memory"
    )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: absorb the custody workflow only; do not reuse source scene versions, fact memories, "
            "reference assets, ReviewReports, prose, prompts, names, or plot order"
        )
    else:
        lines.append(
            "- continuation_boundary: version lineage and fact approval extend the target book's accepted canon only; "
            "drafts remain non-canon until reviewed"
        )
    if version_hints:
        lines.append(f"- version_pipeline_source_hint: {_truncate(version_hints[0], 260)}")
    if review_hints:
        lines.append(f"- human_review_source_hint: {_truncate(review_hints[0], 260)}")


def _append_distilled_novel_toolbox_platform_compliance_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render platform/compliance and human-polish boundaries from Distilled Novel Toolbox intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "distilled_novel_toolbox_platform_compliance_gate",
        "distilled_novel_toolbox_human_polish_boundary_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    platform_hints: list[str] = []
    polish_hints: list[str] = []
    if isinstance(source_pattern_pack, dict):
        platform_hints = _as_note_list(
            source_pattern_pack.get("distilled_novel_toolbox_platform_compliance_gate_hints")
        )
        polish_hints = _as_note_list(
            source_pattern_pack.get("distilled_novel_toolbox_human_polish_boundary_gate_hints")
        )

    lines.append("")
    lines.append("Distilled Novel Toolbox platform/compliance gate:")
    lines.append(
        "- market_fit_card: record target platform, reader promise, format, update cadence, "
        "commercial intent, and local evidence as planning metadata only"
    )
    lines.append(
        "- platform_policy_verification: platform rules, sensitive-word claims, and legal notes "
        "must be checked against current authoritative sources before use"
    )
    lines.append(
        "- compliance_review_packet: keep compliance issue, affected scene/chapter, severity, "
        "reviewer, decision, evidence date, and rewrite action visible before publishing claims"
    )
    lines.append(
        "- human_polish_boundary: use anti-AI/de-AI vocabulary only for human quality review: "
        "reduce generic texture, improve specificity, preserve author voice, and avoid evasion services"
    )
    lines.append(
        "- prompt_body_import_policy: upstream prompt templates, skill bodies, detection bypass instructions, "
        "and platform-policy bodies stay excluded from default context"
    )
    lines.append(
        "- example_fiction_import_policy: upstream sample fiction and generated outputs are not style memory, "
        "training corpus, or same-type source prose"
    )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: transfer only the review packet shape; do not reuse source platform claims, "
            "prompt templates, anti-detection instructions, sample fiction, module text, or commercial recipes"
        )
    else:
        lines.append(
            "- continuation_boundary: market fit, compliance, and polish reviews can constrain the target manuscript, "
            "but cannot override accepted canon or current verified policy"
        )
    if platform_hints:
        lines.append(f"- platform_compliance_source_hint: {_truncate(platform_hints[0], 260)}")
    if polish_hints:
        lines.append(f"- human_polish_source_hint: {_truncate(polish_hints[0], 260)}")


def _append_novel_studio_graph_memory_continuity_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render graph-memory and accepted-chapter writeback gates from Novel Studio AI intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "novel_studio_graph_memory_continuity_gate",
        "novel_studio_accepted_chapter_writeback_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    graph_hints: list[str] = []
    writeback_hints: list[str] = []
    if isinstance(source_pattern_pack, dict):
        graph_hints = _as_note_list(
            source_pattern_pack.get("novel_studio_graph_memory_continuity_gate_hints")
        )
        writeback_hints = _as_note_list(
            source_pattern_pack.get("novel_studio_accepted_chapter_writeback_gate_hints")
        )

    lines.append("")
    lines.append("Novel Studio graph-memory continuity gate:")
    lines.append(
        "- accepted_chapter_writeback: drafts stay temporary; only accepted chapters may update "
        "summaries, character states, graph triples, timeline events, and memory chunks"
    )
    lines.append(
        "- graph_fact_triples: record subject, relation, object, chapter/source, canon status, "
        "and contradiction risk before a fact enters retrieval memory"
    )
    lines.append(
        "- character_state_versions: track location, injury/status, knowledge, relationship, "
        "items, and public reputation by accepted chapter"
    )
    lines.append(
        "- timeline_event_order: verify recent accepted summaries and timeline events before "
        "moving characters, resurrecting characters, changing ownership, or paying hooks"
    )
    lines.append(
        "- contradiction_checklist: check dead-character conflicts, impossible locations, item ownership drift, "
        "relationship resets, and style-rule drift before canon promotion"
    )
    lines.append(
        "- hybrid_retrieval_pack: build the next context pack from story bible, outline, recent summaries, "
        "active character states, graph facts, retrieved memory chunks, and timeline events"
    )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: copy only the graph-memory discipline; rebuild all source graph triples, "
            "character states, timeline events, memory chunks, names, locations, and chapter summaries"
        )
    else:
        lines.append(
            "- continuation_boundary: graph facts and character states must extend the target book's accepted "
            "canon and cannot promote draft-only events"
        )
    if graph_hints:
        lines.append(f"- graph_memory_source_hint: {_truncate(graph_hints[0], 260)}")
    if writeback_hints:
        lines.append(f"- accepted_writeback_source_hint: {_truncate(writeback_hints[0], 260)}")


def _append_mode_contract_generation_audit_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render visible creative axes from mode-contract sources."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if not pattern_names.intersection({"mode_contract_generation_gate", "universal_novel_mode_contract_gate"}):
        return

    audit = _mode_contract_generation_audit(bible=bible, plan=plan, max_items=12)
    axes = audit["axes"]
    hints = []
    if source_pattern_pack:
        hints.extend(_as_note_list(source_pattern_pack.get("mode_contract_generation_gate_hints")))
        hints.extend(_as_note_list(source_pattern_pack.get("universal_novel_mode_contract_gate_hints")))

    lines.append("")
    lines.append("Mode contract generation audit:")
    lines.append(f"- mode: {axes.get('mode', 'missing')}")
    visible_axes = [
        f"{key}={value}"
        for key, value in axes.items()
        if key != "mode"
    ]
    lines.append(f"- visible_axes: {', '.join(visible_axes[:12])}")
    lines.append(
        "- selected_mode_priority: selected output mode wins over incidental words "
        "inside source material, notes, or style-analysis snippets"
    )
    lines.append(
        "- under_length_rewrite_boundary: repair short or generic drafts from the "
        "same accepted axes; do not add source-specific facts, names, or plot order"
    )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 260)}")
    if audit["warnings"]:
        lines.append(f"- mode_contract_warnings: {', '.join(audit['warnings'])}")


def _append_universal_next_chapter_scaffold_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Project universal chapter-contract gates into the concrete next step."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "chapter_contract_scene_beat_gate",
        "reader_promise_micro_payoff_gate",
        "progress_report_continuity_writeback_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    contract = _build_universal_next_chapter_contract(bible=bible, plan=plan)

    lines.append("")
    lines.append("Universal next chapter scaffold:")
    lines.append("- mode: continue-chapter")
    lines.append(f"- chapter_job: {contract['chapter_job']}")
    if contract["pov"]:
        lines.append(f"- pov: {contract['pov']}")
    if contract["starting_status"]:
        lines.append(f"- starting_status: {contract['starting_status']}")
    lines.append(f"- reader_promise: {contract['reader_promise']}")
    lines.append(f"- opening_hook: {contract['opening_hook']}")
    lines.append("- scene_plan: 3-7 scene beats; each beat needs goal, obstacle, turn, cost, and changed exit state")
    if contract["main_goal"]:
        lines.append(f"- main_goal: {contract['main_goal']}")
    if contract["main_obstacle"]:
        lines.append(f"- main_obstacle: {contract['main_obstacle']}")
    if contract["escalation"]:
        lines.append(f"- escalation: {contract['escalation']}")
    if contract["required_payoff"]:
        lines.append(f"- required_payoff: {contract['required_payoff']}")
    if contract["new_hook"]:
        lines.append(f"- new_hook: {contract['new_hook']}")
    if contract["character_change"]:
        lines.append(f"- character_change: {contract['character_change']}")
    if contract["continuity_facts"]:
        lines.append(f"- continuity_facts: {contract['continuity_facts']}")
    if contract["forbidden_contradiction"]:
        lines.append(f"- forbidden_contradiction: {contract['forbidden_contradiction']}")
    if contract["word_count_target"]:
        lines.append(f"- word_count_target: {contract['word_count_target']}")
    lines.append("- writeback_after_acceptance: summary, new facts, character changes, hooks paid off, new hooks, continuity updates, next focus, and risks")
    audit = _universal_chapter_contract_audit(
        bible=bible,
        plan=plan,
        pattern_names=pattern_names,
        max_items=12,
    )
    if audit["warnings"]:
        lines.append(f"- chapter_contract_warnings: {', '.join(audit['warnings'])}")


def _append_universal_progress_report_completeness_gate_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render concrete chapter progress-report gaps before canon writeback."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "progress_report_continuity_writeback_gate" not in pattern_names:
        return

    chapter_packages = _sort_by_chapter_asc(
        _chapter_analysis_packages(bible.get("chapter_change_packages"))
    )
    include_time_trace = "narrative_time_age_trace_gate" in pattern_names
    report_gaps = _chapter_progress_report_gaps(
        chapter_packages,
        include_time_trace=include_time_trace,
    )

    lines.append("")
    lines.append("Universal progress report completeness gate:")
    lines.append(
        "- required_fields: summary, new_facts, character_changes, hook_deltas, "
        "continuity_updates, next_chapter_focus, word_count, risks"
    )
    lines.append(
        "- writeback_scope: accepted chapter reports must separate manuscript summary, "
        "canon facts, character state, hook/payoff movement, continuity ledger updates, "
        "next focus, measurable length, and unresolved risks"
    )
    if include_time_trace:
        lines.append(
            "- required_time_trace_fields: narrative_time, duration, weekday, "
            "character_age_refs, section_status, export_included"
        )
        lines.append(
            "- time_trace_writeback_scope: universal progress reports must also carry "
            "the mdnovel-style section time/status/export boundary before canon reuse"
        )
    if not report_gaps:
        lines.append("- chapter_progress_report_missing_fields: none")
        return

    for gap in report_gaps[:5]:
        missing = ", ".join(gap["missing_fields"])
        lines.append(f"- chapter_progress_report_missing_fields: {gap['chapter']} -> {missing}")


def _append_universal_reader_pull_fresh_reader_gate_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render fresh-reader pull-test requirements from the universal writing skill."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "reader_pull_fresh_reader_gate" not in pattern_names:
        return

    hints = (
        _as_note_list(source_pattern_pack.get("reader_pull_fresh_reader_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    audit = _reader_pull_fresh_reader_audit(bible=bible, max_items=12)

    lines.append("")
    lines.append("Universal reader-pull fresh-reader gate:")
    lines.append(
        "- reader_pull_questions: after each accepted chapter, a fresh reader must answer "
        "POV, want, obstacle, stakes, what changed, and what pulls onward"
    )
    lines.append(
        "- acceptance_boundary: fluent prose is not enough if the chapter does not change "
        "plot, knowledge, relationship, risk, moral pressure, emotion, or world-rule state"
    )
    lines.append(
        "- same_type_boundary: source resemblance must never count as reader pull; the "
        "target chapter needs its own pressure, reward, and next question"
    )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 240)}")
    if audit["warnings"]:
        lines.append(f"- reader_pull_warnings: {', '.join(audit['warnings'])}")


def _append_speckit_fiction_scene_task_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    bible: Optional[dict[str, Any]] = None,
    plan: Optional[dict[str, Any]] = None,
) -> None:
    """Render Spec Kit fiction scene task gates learned from static intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "story_bible_constitution_source_gate",
        "scene_outline_approval_status_gate",
        "pov_information_asymmetry_schedule_gate",
        "pacing_arc_polish_pass_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    hints: list[str] = []
    if isinstance(source_pattern_pack, dict):
        for key in (
            "story_bible_constitution_source_gate_hints",
            "scene_outline_approval_status_gate_hints",
            "pov_information_asymmetry_schedule_gate_hints",
            "pacing_arc_polish_pass_gate_hints",
        ):
            hints.extend(_as_note_list(source_pattern_pack.get(key)))

    audit = _spec_kit_fiction_scene_task_audit(
        bible=bible or {},
        plan=plan,
        max_items=12,
    ) if bible is not None or plan is not None else _empty_spec_kit_fiction_scene_task_audit()

    lines.append("")
    lines.append("Spec Kit fiction scene-task audit:")
    if "story_bible_constitution_source_gate" in pattern_names:
        lines.append("- story_bible_constitution_source_gate: constitution/story bible controls source-of-truth voice, tense, audience, hard rules, and accepted canon")
    if "scene_outline_approval_status_gate" in pattern_names:
        lines.append("- scene_outline_approval_status_gate: draft only scene outlines marked APPROVED; SKIP/TODO outlines stay out of prose context")
    if "pov_information_asymmetry_schedule_gate" in pattern_names:
        lines.append("- pov_information_asymmetry_schedule_gate: maintain POV schedule and information asymmetry map before drafting multi-POV scenes")
    if "pacing_arc_polish_pass_gate" in pattern_names:
        lines.append("- pacing_arc_polish_pass_gate: require pacing/tension evidence and checklist PASS before polish or export")
    lines.append("- same_type_boundary: rebuild scene ids, POV timing, secrets, and checklist criteria for the target project; do not reuse source task rows")
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 260)}")
    if audit["warnings"]:
        lines.append(f"- spec_kit_fiction_warnings: {', '.join(audit['warnings'])}")


def _append_story_foundry_production_handoff_gate_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render Story Foundry-style production stage handoff gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "capture_distillation_production_gate" not in pattern_names:
        return

    hints = (
        _as_note_list(source_pattern_pack.get("capture_distillation_production_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    audit = _story_foundry_production_handoff_audit(
        bible=bible,
        plan=plan,
        max_items=12,
    )

    lines.append("")
    lines.append("Story Foundry production handoff gate:")
    lines.append(
        "- stage_boundary: keep Capture notes, Distillation outlines/scene cards, "
        "and Production drafts/revisions as separate artifacts"
    )
    lines.append(
        "- scene_card_spine: scene cards need alpha point, goal, obstacles, "
        "disaster/hook, internal desire/misbelief, emotional stakes, and aftermath"
    )
    lines.append(
        "- production_chain: draft -> critique -> numbered fix_spec -> revised draft "
        "-> editor_log -> canon promotion"
    )
    lines.append(
        "- archivist_promotion: only accepted/approved artifacts update manuscript, "
        "story bible, index, changelog, or reusable canon state"
    )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 240)}")
    if audit["warnings"]:
        lines.append(f"- production_handoff_warnings: {', '.join(audit['warnings'])}")


def _append_universal_same_type_creation_scaffold_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render same-type drafting gates learned from the portable skill."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "universal_novel_mode_contract_gate",
        "chapter_contract_scene_beat_gate",
        "reader_promise_micro_payoff_gate",
        "progress_report_continuity_writeback_gate",
        "post_draft_review_checklist_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Universal same-type creation scaffold:")
    lines.append(
        "- same_type_creation_scaffold: rebuild reader promise, protagonist want/need, "
        "opposition, chapter contract, hook/payoff ledger, and project-local continuity "
        "before drafting independent prose"
    )
    lines.append(
        "- source_boundary: transfer workflow shape and craft pressure only; do not reuse "
        "source event order, proper nouns, set pieces, or distinctive phrasing"
    )
    lines.append(
        "- target_writeback: record transformed outline decisions, new hooks/payoffs, "
        "continuity updates, and copy-risk findings as target-owned artifacts"
    )


def _append_book_mcp_beta_reader_file_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render book-file and beta-reader custody learned from Slima MCP intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "slima_book_mcp_beta_reader_file_gate" not in pattern_names:
        return

    hints = (
        _as_note_list(source_pattern_pack.get("slima_book_mcp_beta_reader_file_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Book-MCP beta reader file gate:")
    lines.append(
        "- file_scope_envelope: book_id, file_path, chapter_scope, allowed read/search "
        "scope, and forbidden write/delete/append scope must be explicit before review"
    )
    lines.append(
        "- beta_reader_feedback: store persona, reader lens, finding, severity, affected "
        "chapter/span, suggested action, and accepted/dismissed state as review notes"
    )
    lines.append(
        "- mutation_boundary: beta-reader notes and file search results are advisory; "
        "they cannot mutate canon, progress, manuscript, or export files without human acceptance"
    )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: source beta-reader feedback may define review axes only; "
            "the target story needs fresh personas, target-owned files, and independent findings"
        )
    else:
        lines.append(
            "- continuation_boundary: only feedback scoped to the current owned chapter/file "
            "can influence the next revision task"
        )
    lines.append(
        "- runtime_boundary: no npx install, hosted/remote MCP, OAuth login, token read, "
        "Cloudflare worker, live file tool, or hidden book mutation is authorized from static intake"
    )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 240)}")


def _append_live_diagnostics_outline_import_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render live manuscript diagnostics and visible outline/import custody."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    has_live_diagnostics = "novelwriter_live_manuscript_analytics_gate" in pattern_names
    has_outline_import = "kindling_local_outline_reference_import_gate" in pattern_names
    if not has_live_diagnostics and not has_outline_import:
        return

    novelwriter_hints = (
        _as_note_list(source_pattern_pack.get("novelwriter_live_manuscript_analytics_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    kindling_hints = (
        _as_note_list(source_pattern_pack.get("kindling_local_outline_reference_import_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Live diagnostics and outline-import gate:")
    if has_live_diagnostics:
        lines.append(
            "- live_diagnostic_layers: keep Event Line, open plot lines, Connection Web, "
            "Story Pulse, plot-hole findings, and scene suggestions as named review layers"
        )
        lines.append(
            "- advisory_analysis_boundary: live mood, remarks, Echo Chamber reader reactions, "
            "summaries, and inline suggestions cannot change canon or prose without acceptance"
        )
    if has_outline_import:
        lines.append(
            "- visible_outline_scaffold: scene beats may stay visible as expandable drafting "
            "prompts, but outline prompts remain separate from accepted prose"
        )
        lines.append(
            "- import_export_custody: record source tool/format, import snapshot, parser status, "
            "sync/reimport preview, export target, and rejected deltas before remapping structure"
        )
        lines.append(
            "- reference_detection_boundary: detected characters, locations, items, tags, and "
            "custom fields are metadata proposals, not automatic canon entities"
        )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: source diagnostics, import examples, outline cards, and "
            "reference labels define review axes only; the target story needs fresh diagnostic state"
        )
    else:
        lines.append(
            "- continuation_boundary: only diagnostics and outline deltas tied to the current "
            "owned chapter/scene can influence the next revision task"
        )
    lines.append(
        "- runtime_boundary: no npm/Tauri runtime, provider call, AI side panel, PDF export, "
        "SQLite project, parser execution, import/export action, or manuscript data access is authorized"
    )
    if novelwriter_hints:
        lines.append(f"- novelwriter_source_hint: {_truncate(novelwriter_hints[0], 240)}")
    if kindling_hints:
        lines.append(f"- kindling_source_hint: {_truncate(kindling_hints[0], 240)}")


def _append_filetype_rag_project_edit_boundary_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render fileType-scoped RAG and direct project edit custody."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    has_filetype_rag = "dialogoi_filetype_rag_novel_project_gate" in pattern_names
    has_project_edit = "scrivener_mcp_direct_project_edit_boundary_gate" in pattern_names
    if not has_filetype_rag and not has_project_edit:
        return

    dialogoi_hints = (
        _as_note_list(source_pattern_pack.get("dialogoi_filetype_rag_novel_project_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    scrivener_hints = (
        _as_note_list(source_pattern_pack.get("scrivener_mcp_direct_project_edit_boundary_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("FileType RAG and project edit boundary gate:")
    if has_filetype_rag:
        lines.append(
            "- filetype_retrieval_scope: every retrieval request must declare one scope: "
            "content | settings | instructions | both"
        )
        lines.append(
            "- hybrid_search_evidence: combine regex/full-text matches and semantic RAG "
            "only when chunk overlap, source file class, and missing-index fallback are recorded"
        )
        lines.append(
            "- source_file_class_custody: settings, manuscript content, and instruction files "
            "remain separate evidence classes before they can influence continuation context"
        )
    if has_project_edit:
        lines.append(
            "- direct_project_boundary_report: open/read/analyze/search findings are review "
            "inputs tied to document ids, structure, pacing, RTF parsing, and word-count evidence"
        )
        lines.append(
            "- accepted_patch_scope: edit/write/reorder operations need a human-accepted patch "
            "envelope before any project, canon, synopsis, or manuscript mutation"
        )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: source RAG chunks, settings files, Scrivener binders, and "
            "document structure examples cannot become target canon or target outline order"
        )
    else:
        lines.append(
            "- continuation_boundary: only retrieval/project-boundary findings scoped to the "
            "current owned chapter, scene, or accepted bible section can affect the next task"
        )
    lines.append(
        "- runtime_boundary: no MCP launch, Docker/Qdrant, model download, npm script, "
        "file watcher, .scriv project access, RTF read, postinstall hook, Neo4j/Redis/OpenAI "
        "runtime, or live manuscript edit is authorized"
    )
    if dialogoi_hints:
        lines.append(f"- dialogoi_source_hint: {_truncate(dialogoi_hints[0], 240)}")
    if scrivener_hints:
        lines.append(f"- scrivener_source_hint: {_truncate(scrivener_hints[0], 240)}")


def _append_frame_setting_state_runtime_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render frame-coordinate, setting-document, and hard-state review gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    has_frame = "vector_story_frame_coordinate_gate" in pattern_names
    has_setting_docs = "setting_runtime_document_architecture_gate" in pattern_names
    has_state_review = "inkfoundry_state_db_redteam_voice_sandbox_gate" in pattern_names
    if not has_frame and not has_setting_docs and not has_state_review:
        return

    frame_hints = (
        _as_note_list(source_pattern_pack.get("vector_story_frame_coordinate_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    setting_hints = (
        _as_note_list(source_pattern_pack.get("setting_runtime_document_architecture_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    state_hints = (
        _as_note_list(source_pattern_pack.get("inkfoundry_state_db_redteam_voice_sandbox_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Frame, setting runtime, and StateDB gate:")
    if has_frame:
        lines.append(
            "- frame_coordinate_contract: each target-owned frame declares story beat, "
            "tone, density, register, target length, and diff/review status before prose"
        )
    if has_setting_docs:
        lines.append(
            "- setting_document_architecture: separate story bible, voice bible, project "
            "instructions, tracked items, opening scenario, theory-of-mind notes, and anti-patterns"
        )
        lines.append(
            "- session_start_packet: list loaded documents, stale documents, closed/forbidden "
            "jobs, relevant current files, and handoff snapshot before resumed continuation"
        )
    if has_state_review:
        lines.append(
            "- state_over_vector_boundary: accepted hard state, locks, snapshots, version ids, "
            "dead/alive facts, and continuity records outrank contradictory vector recall"
        )
        lines.append(
            "- redteam_voice_sandbox_review: RedTeam plot attacks and VoiceSandbox character "
            "constraints produce review findings, not hidden generation authority"
        )
    if mode == "same-type":
        lines.append(
            "- same_type_boundary: source VRGB frames, setting documents, StateDB facts, "
            "voice profiles, and RedTeam findings can define target review axes only"
        )
    else:
        lines.append(
            "- continuation_boundary: only target-owned frame coordinates, accepted setting "
            "documents, and current state-review findings can influence the next chapter task"
        )
    lines.append(
        "- runtime_boundary: no generation engine, provider call, environment variable, shell "
        "script, campaign prompt body, MCP/filesystem runtime, ChromaDB, daemon scheduler, "
        "import/export artifact, or generated manuscript is authorized"
    )
    if frame_hints:
        lines.append(f"- frame_source_hint: {_truncate(frame_hints[0], 240)}")
    if setting_hints:
        lines.append(f"- setting_source_hint: {_truncate(setting_hints[0], 240)}")
    if state_hints:
        lines.append(f"- state_source_hint: {_truncate(state_hints[0], 240)}")


def _append_truth_file_write_next_state_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render write-next/state-update gates from truth-file workflow sources."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "truth_file_write_next_state_update_gate" not in pattern_names:
        return

    hints = (
        _as_note_list(source_pattern_pack.get("truth_file_write_next_state_update_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Truth-file write-next state gate:")
    lines.append(
        "- truth_file_write_next_state_update_gate: build every continuation task from "
        "truth files, chapter summaries, current state, unresolved promises, and snapshot_id"
    )
    lines.append(
        "- write_next_package: record selected authority files, latest accepted chapter, "
        "open hook/payoff debt, planned beat, and blocking assumptions before drafting"
    )
    lines.append(
        "- candidate_revision_boundary: revise changes the candidate draft only; it must not "
        "silently mutate long-term bible, timeline, character, hook, or plan state"
    )
    lines.append(
        "- state_update_authority: accepted chapters alone can trigger state-update, and every "
        "delta needs source chapter id, reviewer status, and rollback/snapshot_id evidence"
    )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 220)}")


def _append_action_review_canonization_gate_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render artifact-backed action, review, and canon-promotion gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    action_review_patterns = {
        "confirmed_action_audit_recovery_gate",
        "planner_writer_evaluator_editor_saga_gate",
        "story_state_output_contract_gate",
        "markdown_frontmatter_continuity_engine_gate",
        "craft_scene_concrete_finding_revision_gate",
        "anti_hallucination_strand_weave_review_gate",
        "ai_flavor_template_shell_cleanup_gate",
    }
    active_patterns = pattern_names.intersection(action_review_patterns)
    if not active_patterns:
        return

    confirmed_hints = (
        _as_note_list(source_pattern_pack.get("confirmed_action_audit_recovery_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    saga_hints = (
        _as_note_list(source_pattern_pack.get("planner_writer_evaluator_editor_saga_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )

    lines.append("")
    lines.append("Action-review canonization gate:")
    if "confirmed_action_audit_recovery_gate" in active_patterns:
        lines.append(
            "- confirmed_action_audit_recovery_gate: generation, rewrite, state writeback, "
            "and completion claims require confirmed action ids, artifact evidence, and "
            "unresolved critical finding review"
        )
    if "planner_writer_evaluator_editor_saga_gate" in active_patterns:
        lines.append(
            "- planner_writer_evaluator_editor_saga_gate: keep planner, writer, evaluator, "
            "and editor findings separate until an explicit canon-promotion decision"
        )
    if "story_state_output_contract_gate" in active_patterns:
        lines.append(
            "- story_state_output_contract_gate: prose output and state-update blocks stay "
            "separate; proposed deltas need reviewer status before memory writeback"
        )
    if "markdown_frontmatter_continuity_engine_gate" in active_patterns:
        lines.append(
            "- markdown_frontmatter_continuity_engine_gate: chapter/scene metadata must track "
            "pov, timeline, mentions, promises, payoffs, and canon status before reuse"
        )
    if "craft_scene_concrete_finding_revision_gate" in active_patterns:
        lines.append(
            "- concrete_revision_finding: every revision request names the concrete finding, "
            "narrative function, protected style-bearing material, and acceptance criterion"
        )
    if "anti_hallucination_strand_weave_review_gate" in active_patterns:
        lines.append(
            "- anti_hallucination_strand_weave: outline is law, setting is physics, invented "
            "facts are flagged, and quest/fire/constellation strands are reviewed before prose"
        )
    if "ai_flavor_template_shell_cleanup_gate" in active_patterns:
        lines.append(
            "- ai_flavor_template_shell_cleanup_gate: final cleanup rejects template sentence "
            "shells, assistant-roadmap wording, fake engagement endings, and paragraph homology"
        )
    if confirmed_hints:
        lines.append(f"- confirmed_action_source_hint: {_truncate(confirmed_hints[0], 220)}")
    if saga_hints:
        lines.append(f"- saga_source_hint: {_truncate(saga_hints[0], 220)}")


def _build_universal_next_chapter_contract(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> dict[str, str]:
    """Build a compact concrete chapter contract from current canon state."""
    packages = _sort_by_chapter_asc(_chapter_analysis_packages(bible.get("chapter_change_packages")))
    latest_package = packages[-1] if packages else None
    latest_chapter = _chapter_reference(latest_package or {})
    latest_summary = _string_value(latest_package.get("summary")) if latest_package else ""

    pending_beat = _first_pending_plan_beat(plan=plan)
    pending_beat_item = _first_pending_plan_item(plan=plan)
    plan_summary = _string_value(plan.get("summary")) if plan else ""
    promise_debt = _first_promise_payoff_debt_label(bible=bible, plan=plan)
    guardrail = _first_plan_guardrail(plan=plan)
    hard_constraint = _first_hard_constraint(bible=bible)
    character_goal = _first_character_goal(bible=bible)
    conflict = _first_conflict_text(bible=bible)
    pov = _first_contract_pov(bible=bible, plan=plan, latest_package=latest_package)
    starting_status = _first_starting_status(latest_package=latest_package)
    escalation = _first_escalation(plan=plan, pending_beat_item=pending_beat_item, conflict=conflict)
    new_hook = _first_new_hook(bible=bible, plan=plan)
    character_change = _first_character_change(latest_package=latest_package)
    continuity_fact = _first_continuity_fact(bible=bible, latest_package=latest_package)
    word_count_target = _first_word_count_target(bible=bible, plan=plan)

    if pending_beat:
        chapter_job = pending_beat
    elif plan_summary:
        chapter_job = plan_summary
    elif latest_summary:
        chapter_job = f"Continue from accepted state: {latest_summary}"
    else:
        chapter_job = "Continue accepted canon while preserving visible conflict and payoff debt"

    if promise_debt:
        reader_promise = f"serve visible promise/payoff debt: {promise_debt}"
    else:
        reader_promise = "name the reader promise before prose and make the first scene serve it"

    if latest_chapter and latest_summary:
        opening_hook = f"Continue from {latest_chapter}: {latest_summary}"
    elif promise_debt:
        opening_hook = f"Open on consequence or pressure from: {promise_debt}"
    else:
        opening_hook = "Open with consequence, conflict, or a concrete unanswered question"

    return {
        "chapter_job": _truncate(chapter_job, 220),
        "pov": _truncate(pov, 220),
        "starting_status": _truncate(starting_status, 220),
        "reader_promise": _truncate(reader_promise, 220),
        "opening_hook": _truncate(opening_hook, 220),
        "main_goal": _truncate(character_goal or pending_beat, 220),
        "main_obstacle": _truncate(conflict or guardrail or hard_constraint, 220),
        "escalation": _truncate(escalation, 220),
        "required_payoff": _truncate(promise_debt, 220),
        "new_hook": _truncate(new_hook, 220),
        "character_change": _truncate(character_change, 220),
        "continuity_facts": _truncate(continuity_fact, 220),
        "forbidden_contradiction": _truncate(guardrail or hard_constraint, 220),
        "word_count_target": _truncate(word_count_target, 220),
    }


def _first_pending_plan_beat(*, plan: Optional[dict[str, Any]]) -> str:
    beats = _pending_plan_beats(plan=plan, max_items=1)
    return beats[0] if beats else ""


def _first_pending_plan_item(*, plan: Optional[dict[str, Any]]) -> dict[str, Any]:
    if not plan:
        return {}
    for item in _as_dict_list(plan.get("beats")):
        if not _is_done_status(item.get("status")):
            return item
    beats = _as_dict_list(plan.get("beats"))
    return beats[0] if beats else {}


def _first_promise_payoff_debt_label(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> str:
    debts = _promise_payoff_debts(bible=bible, plan=plan, max_items=1)
    return _string_value(debts[0].get("label")) if debts else ""


def _first_contract_pov(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    latest_package: Optional[dict[str, Any]],
) -> str:
    carriers = [carrier for carrier in (latest_package, plan, bible) if isinstance(carrier, dict)]
    for carrier in carriers:
        text = _direct_first_text(
            carrier,
            ("pov", "point_of_view", "viewpoint", "narrator", "narrative_distance"),
        )
        if text:
            return text

    style_signature = bible.get("style_signature")
    if isinstance(style_signature, dict):
        text = _direct_first_text(
            style_signature,
            ("pov", "point_of_view", "viewpoint", "narrator", "narrative_distance"),
        )
        if text:
            return text
    return ""


def _first_starting_status(*, latest_package: Optional[dict[str, Any]]) -> str:
    if not latest_package:
        return ""

    direct = _direct_first_text(
        latest_package,
        ("starting_status", "starting_emotion", "starting_emotional_state", "status_before"),
    )
    if direct:
        return direct

    for item in _as_dict_list(latest_package.get("character_state_changes")):
        state = _direct_first_text(
            item,
            ("state_after", "status_after", "current_state", "emotional_state", "relationship_state"),
        )
        if state:
            name = _string_value(item.get("character_name") or item.get("name"))
            return f"{name}: {state}" if name else state
    return ""


def _first_escalation(
    *,
    plan: Optional[dict[str, Any]],
    pending_beat_item: dict[str, Any],
    conflict: str,
) -> str:
    text = _direct_first_text(
        pending_beat_item,
        ("escalation", "pressure", "turn", "cost", "stakes", "risk"),
    )
    if text:
        return text
    if plan:
        text = _direct_first_text(plan, ("escalation", "pressure", "turn", "stakes", "risk"))
        if text:
            return text
    return conflict


def _first_new_hook(*, bible: dict[str, Any], plan: Optional[dict[str, Any]]) -> str:
    if plan:
        for item in _as_dict_list(plan.get("priority_hooks")):
            if not _is_done_status(item.get("status")):
                text = _first_text(item, ("hook", "thread", "question", "promise", "name"))
                if text:
                    return text
    for item in _status_items(_as_dict_list(bible.get("foreshadows")), done=False, max_items=1):
        text = _first_text(item, ("hook", "thread", "question", "promise", "name"))
        if text:
            return text
    return ""


def _first_character_change(*, latest_package: Optional[dict[str, Any]]) -> str:
    if not latest_package:
        return ""

    direct = _direct_first_text(
        latest_package,
        ("character_change", "character_movement", "relationship_change", "emotional_shift"),
    )
    if direct:
        return direct

    for item in _as_dict_list(latest_package.get("character_state_changes")):
        change = _direct_first_text(
            item,
            ("psychological_change", "relationship_change", "state_delta", "change", "state_after", "key_event"),
        )
        if change:
            name = _string_value(item.get("character_name") or item.get("name"))
            return f"{name}: {change}" if name else change
    return ""


def _first_continuity_fact(
    *,
    bible: dict[str, Any],
    latest_package: Optional[dict[str, Any]],
) -> str:
    if latest_package:
        for key in ("timeline_delta", "new_facts", "continuity_updates"):
            for item in _as_dict_list(latest_package.get(key)):
                text = _first_text(item, ("event", "fact", "update", "content", "summary", "consequence"))
                if text:
                    return text
        direct = _direct_first_text(latest_package, ("continuity_fact", "new_fact", "continuity_update"))
        if direct:
            return direct

    timeline = _sort_by_chapter_desc(_as_dict_list(bible.get("timeline")))
    for item in timeline:
        text = _first_text(item, ("event", "fact", "summary", "consequence", "impact"))
        if text:
            return text
    return ""


def _first_word_count_target(*, bible: dict[str, Any], plan: Optional[dict[str, Any]]) -> str:
    keys = (
        "word_count_target",
        "target_word_count",
        "chapter_word_count",
        "length_target",
        "chapter_length",
    )
    for carrier in (plan, bible):
        if isinstance(carrier, dict):
            text = _direct_first_text(carrier, keys)
            if text:
                return text
    style_signature = bible.get("style_signature")
    if isinstance(style_signature, dict):
        text = _direct_first_text(style_signature, keys)
        if text:
            return text
    return ""


def _first_plan_guardrail(*, plan: Optional[dict[str, Any]]) -> str:
    if not plan:
        return ""
    for item in _as_dict_list(plan.get("guardrails")):
        text = _first_text(item, ("rule", "constraint", "content", "name"))
        if text:
            return text
    return ""


def _first_hard_constraint(*, bible: dict[str, Any]) -> str:
    for item in _as_dict_list(bible.get("hard_constraints")):
        text = _first_text(item, ("rule", "constraint", "content", "name"))
        if text:
            return text
    return ""


def _first_character_goal(*, bible: dict[str, Any]) -> str:
    for item in _as_dict_list(bible.get("character_cards")):
        name = _string_value(item.get("name") or item.get("character_name"))
        goal = _string_value(item.get("goal") or item.get("external_want") or item.get("want"))
        if name and goal:
            return f"{name}: {goal}"
        if goal:
            return goal
    return ""


def _first_conflict_text(*, bible: dict[str, Any]) -> str:
    for item in _as_dict_list(bible.get("conflicts")):
        text = _first_text(item, ("conflict", "pressure", "summary", "name", "status"))
        if text:
            return text
    return ""


def _append_context_activation_audit_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render an explicit audit of which context layers should be active."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if not pattern_names:
        return

    activated_sections = _activated_context_sections(bible=bible, plan=plan)
    if not activated_sections:
        return

    lines.append("")
    lines.append("Context activation audit:")
    for label, detail in activated_sections[:12]:
        lines.append(f"- {label}: {detail}")

    if "lorebook_context" in pattern_names:
        lines.append("- activated_lore_entries: activate by current chapter goal and keywords; do not inject unrelated lore.")
    if "context_reference" in pattern_names:
        lines.append("- context_reference_set: record section/card/chapter and reason before drafting.")
    if "world_state_tracking" in pattern_names:
        lines.append("- world_state_slices: update only changed entity, location, faction, or item state after the chapter.")
    if "author_note_layer" in pattern_names:
        lines.append("- author_note_layer: next-chapter local style reminder; expires after this chapter.")

    if pattern_names.intersection({"lorebook_context", "context_reference", "world_state_tracking"}):
        lines.append("")
        lines.append("Context budget notes:")
        lines.append("- Prioritize current beat, latest state, open hook, active character, and direct organization/faction constraints.")
        lines.append("- Leave inactive-but-relevant lore out of the prompt and mention it only in review notes.")
        lines.append("- Avoid loading full bible/history when a compact card or chapter-change package already proves the state.")

    if "memory_snapshot_versioning" in pattern_names:
        lines.append("")
        lines.append("Rollback guidance:")
        lines.append("- Create a named memory snapshot before risky rewrite, branch merge, or bulk bible update.")
        lines.append("- Rejected drafts must revert prose plus timeline, character, organization, hook, and plan-progress state.")


def _append_continuation_control_contract_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    audit = build_remix_continuation_control_audit(
        bible=bible,
        plan=plan,
        source_pattern_pack=source_pattern_pack,
    )

    latest = audit["latest_chapter_number"] if audit["latest_chapter_number"] is not None else "none"
    gap_summary = ",".join(audit["chapter_gaps"][:5]) if audit["chapter_gaps"] else "none"
    lines.append("")
    lines.append("Continuation production control contract:")
    lines.append(
        "- state_snapshot: "
        f"latest_chapter={latest}, "
        f"change_packages={audit['chapter_package_count']}, "
        f"timeline_anchors={audit['timeline_anchor_count']}, "
        f"character_cards={audit['character_card_count']}, "
        f"open_hooks={audit['open_hook_count']}, "
        f"pending_beats={audit['pending_plan_beat_count']}, "
        f"chapter_gaps={gap_summary}"
    )
    lines.append(f"- control_axes: {', '.join(audit['control_axes'][:12])}")
    lines.append(f"- acceptance_steps: {', '.join(audit['acceptance_steps'][:10])}")
    if audit["warnings"]:
        lines.append(f"- production_warnings: {', '.join(audit['warnings'][:10])}")
    lines.append("- writeback_rule: only accepted chapters may update bible, timeline, character state, hooks, or plan progress")


def _append_scene_graph_review_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render graph/workspace gates learned from static source intake."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "scene_level_generation",
        "content_ref_externalization",
        "review_queue_staging",
        "style_guide_layering",
        "entity_schema_custom_fields",
        "graph_healing",
        "contradiction_detection",
        "graph_branching_atomicity",
        "query_lint_contract",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Scene graph review audit:")
    if "scene_level_generation" in pattern_names:
        lines.append("- scene_generation_units: plan scene goal, cast, location, pressure, reveal, and exit hook before drafting")
    if "content_ref_externalization" in pattern_names:
        lines.append("- external_content_refs: store large scene plans, drafts, extraction payloads, and review reports as refs with integrity metadata")
    if "review_queue_staging" in pattern_names:
        lines.append("- pending_change_queue: stage AI-proposed canon/style/card/chapter changes before applying them")
    if "style_guide_layering" in pattern_names:
        lines.append("- style_layer_stack: base style guide -> scene override -> character voice notes")
    if "entity_schema_custom_fields" in pattern_names:
        lines.append("- entity_custom_fields: validate genre-specific fields before prompt injection or canon write-back")
    if "graph_healing" in pattern_names:
        lines.append("- graph_healing_review: surface duplicate entities, orphan lore, and stale edges as reviewable candidates")
    if "contradiction_detection" in pattern_names:
        lines.append("- contradiction_gate: block acceptance on timeline, relationship, location, trait, or hook conflicts")
    if "graph_branching_atomicity" in pattern_names:
        lines.append("- branch_atomicity: publish multi-slice canon updates only after branch/snapshot validation passes")
    if "query_lint_contract" in pattern_names:
        lines.append("- query_lint_contract: lint generated mutations for target entity, relationship type, required fields, and delete/update separation")


def _append_plotgrid_reveal_branch_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render plotgrid, reveal, setup/payoff, and branch gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "premature_ending_guard",
        "layered_memory_model",
        "plot_dependency_graph",
        "plotgrid_scene_matrix",
        "plotline_thread_tracking",
        "narrative_time_age_trace_gate",
        "scene_status_dashboard",
        "gradual_reveal_control",
        "setup_payoff_tracking",
        "scene_type_directing",
        "alternate_timeline_branching",
        "divergence_guidance",
        "worldpkg_export",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Plotgrid reveal branch audit:")
    if "premature_ending_guard" in pattern_names:
        lines.append("- premature_ending_guard: check whether the draft falsely resolves the main conflict, skips payoff windows, or closes the book too early")
    if "layered_memory_model" in pattern_names:
        lines.append("- memory_layer_order: story bible -> character state -> plot dependency graph; do not let a lower layer override confirmed canon")
    if "plot_dependency_graph" in pattern_names:
        lines.append("- plot_dependency_graph: every payoff should trace back to an active setup, clue, promise, or unresolved hook")
    if "plotgrid_scene_matrix" in pattern_names:
        lines.append("- plotgrid_scene_matrix: map each scene against plotline, POV, location, emotion, status, and thread coverage")
    if "plotline_thread_tracking" in pattern_names:
        lines.append("- plotline_thread_tracking: keep active, paused, paid-off, and abandoned threads visible before drafting")
    if "narrative_time_age_trace_gate" in pattern_names:
        lines.append("- narrative_time_age_trace_gate: verify section date/time, duration, weekday, character age, status, and unused/export boundary before acceptance")
    if "scene_status_dashboard" in pattern_names:
        lines.append("- scene_status_dashboard: mark scene cards by planned, drafted, reviewed, accepted, or blocked state before write-back")
    if "gradual_reveal_control" in pattern_names:
        lines.append("- gradual_reveal_budget: expose world facts through action and dialogue; keep hidden-layer facts out until triggered")
    if "setup_payoff_tracking" in pattern_names:
        lines.append("- setup_payoff_ledger: record setup chapter, expected payoff window, payoff state, and dependency risk")
    if "scene_type_directing" in pattern_names:
        lines.append("- scene_type_directing: declare scene mode before drafting so pacing, dialogue ratio, camera distance, and sensory density match the scene function")
    if "alternate_timeline_branching" in pattern_names:
        lines.append("- alternate_timeline_branch: branch what-if or same-world divergence state away from faithful continuation canon")
    if "divergence_guidance" in pattern_names:
        lines.append("- divergence_guidance: name the player/new-story choice that causes branch drift and list which canon facts stay fixed")
    if "worldpkg_export" in pattern_names:
        lines.append("- worldpkg_export_boundary: exported world packages are reusable context artifacts, not automatic canon mutations")


def _append_acceptance_loop_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render context-pack, accepted-memory, critic, resume, and rewrite gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "context_pack_preview",
        "accepted_chapter_memory",
        "critic_verifier_loop",
        "collapse_prevention",
        "trend_deconstruction_pipeline",
        "anti_ai_tone_polish",
        "preference_memory",
        "interrupted_resume_flow",
        "auto_validation_rewrite",
        "top_down_story_planning",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Acceptance loop audit:")
    if "context_pack_preview" in pattern_names:
        lines.append("- context_pack_preview: list included canon facts, retrieval reasons, token budget, and omitted-but-relevant context before drafting")
    if "accepted_chapter_memory" in pattern_names:
        lines.append("- accepted_chapter_memory: drafts cannot update canon; only accepted chapters may extract memory and feed the next context pack")
    if "critic_verifier_loop" in pattern_names:
        lines.append("- critic_verifier_loop: keep writer/reviser output separate from critic/verifier findings and verification results")
    if "collapse_prevention" in pattern_names:
        lines.append("- collapse_prevention: block write-back on invalid output, causality break, state contradiction, or repeated model failure")
    if "trend_deconstruction_pipeline" in pattern_names:
        lines.append("- trend_deconstruction_pipeline: use deconstructed trope modules as transformed craft pressure, not copied source route")
    if "anti_ai_tone_polish" in pattern_names:
        lines.append("- anti_ai_tone_polish: remove explanation-heavy AI tone after continuity passes without paraphrasing source prose")
    if "preference_memory" in pattern_names:
        lines.append("- preference_memory_boundary: apply user preference to style defaults only; never override canon state")
    if "interrupted_resume_flow" in pattern_names:
        lines.append("- interrupted_resume_flow: resume from current phase, chapter, scene, last accepted artifact, and pending validation status")
    if "auto_validation_rewrite" in pattern_names:
        lines.append("- auto_validation_rewrite: validate word count, coherence, hook, style, and state write-back before bounded retry")
    if "top_down_story_planning" in pattern_names:
        lines.append("- top_down_story_planning: preserve hierarchy from book spec to act, chapter, scene, and previous-scene context")


def _append_manuscript_structure_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render mature writing-tool manuscript planning gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "plain_text_project_storage",
        "synopsis_cross_reference",
        "snowflake_premise_expansion",
        "outliner_index_cards",
        "narrative_strand_mapping",
        "character_depth_interview",
        "mindmap_visual_planning",
        "manuscript_export_formats",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Manuscript structure audit:")
    if "plain_text_project_storage" in pattern_names:
        lines.append("- plain_text_project_storage: keep chapters, notes, summaries, and analysis as stable human-readable units")
    if "synopsis_cross_reference" in pattern_names:
        lines.append("- synopsis_cross_reference: link synopsis, comments, notes, and chapter refs before drafting")
    if "snowflake_premise_expansion" in pattern_names:
        lines.append("- snowflake_premise_expansion: preserve the premise chain from sentence to paragraph to full summary")
    if "outliner_index_cards" in pattern_names:
        lines.append("- outliner_index_cards: keep chapter and scene cards reorderable without losing state evidence")
    if "narrative_strand_mapping" in pattern_names:
        lines.append("- narrative_strand_mapping: map premise, fabula, narrative strands, and setting context before accepting arc changes")
    if "character_depth_interview" in pattern_names:
        lines.append("- character_depth_interview: verify desire, fear, contradiction, social mask, and pressure before major character turns")
    if "mindmap_visual_planning" in pattern_names:
        lines.append("- mindmap_visual_planning: keep visual idea nodes separate from canon until accepted into outline or bible")
    if "manuscript_export_formats" in pattern_names:
        lines.append("- manuscript_export_formats: treat PDF/DOCX/TXT/EPUB exports as derived artifacts, not canon sources")


def _append_delivery_packaging_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render final manuscript assembly, preview, export, and metadata gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "delivery_manuscript_assembly",
        "export_format_fidelity_audit",
        "preview_toc_packaging",
        "cover_kdp_metadata_boundary",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Delivery packaging audit:")
    if "delivery_manuscript_assembly" in pattern_names:
        lines.append("- delivery_manuscript_assembly: assemble only accepted chapters; verify count, order, missing numbers, duplicates, headings, empty titles, and SHA256")
    if "export_format_fidelity_audit" in pattern_names:
        lines.append("- export_format_fidelity_audit: verify chapter order, headings, title page, TOC, page numbers, paragraph boundaries, and derived-export manifest")
    if "preview_toc_packaging" in pattern_names:
        lines.append("- preview_toc_packaging: generate preview and table-of-contents from the same accepted chapter list used by final export")
    if "cover_kdp_metadata_boundary" in pattern_names:
        lines.append("- cover_kdp_metadata_boundary: keep cover and KDP metadata as publication artifacts; never let them mutate canon or chapter text")


def _append_ebook_quality_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render EPUB structure, accessibility, metadata, and navigation gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "epub_structure_validation_gate",
        "ebook_accessibility_audit_gate",
        "front_back_matter_metadata_gate",
        "toc_navigation_consistency_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Ebook quality audit:")
    if "epub_structure_validation_gate" in pattern_names:
        lines.append("- epub_structure_validation_gate: verify container, OPF manifest, spine, nav document, media types, and validation report before final EPUB export")
    if "ebook_accessibility_audit_gate" in pattern_names:
        lines.append("- ebook_accessibility_audit_gate: review accessibility metadata, landmarks, heading levels, reading order, alt text, language, and hazards")
    if "front_back_matter_metadata_gate" in pattern_names:
        lines.append("- front_back_matter_metadata_gate: keep title page, copyright, dedication, endnotes, afterword, colophon, identifiers, and publication metadata in delivery artifacts")
    if "toc_navigation_consistency_gate" in pattern_names:
        lines.append("- toc_navigation_consistency_gate: compare accepted chapter headings, TOC/nav/NCX entries, spine order, landmarks, and preview navigation")


def _append_agentic_editorial_craft_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render agentic editorial, state archive, section metadata, and prose fingerprint gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "agentic_editorial_pipeline_gate",
        "chapter_state_archive_ladder",
        "section_metadata_traceability_gate",
        "ai_prose_fingerprint_cluster_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Agentic editorial and craft workbench audit:")
    if "agentic_editorial_pipeline_gate" in pattern_names:
        lines.append("- agentic_editorial_pipeline_gate: separate planner, architect, writer, reviewer, copy-editor, and compiler roles; canon changes require author/reviewer acceptance")
    if "chapter_state_archive_ladder" in pattern_names:
        lines.append("- chapter_state_archive_ladder: keep permanent bible separate from transient chapter state; archive every accepted chapter state and current pointer")
    if "section_metadata_traceability_gate" in pattern_names:
        lines.append("- section_metadata_traceability_gate: attach cast, location, item, plotline, beat, pacing, status, and evidence metadata to every section")
    if "ai_prose_fingerprint_cluster_gate" in pattern_names:
        lines.append("- ai_prose_fingerprint_cluster_gate: review machine-prose fingerprints, severity clusters, voice drift, overused punctuation, hedging, and show-then-tell patterns")


def _append_chinese_longform_control_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render Chinese long-form canon-control, spoiler-window, writeback, trace, and graph gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "author_candidate_canon_confirmation_gate",
        "progressive_spoiler_context_window_gate",
        "chapter_control_card_writeback_gate",
        "trace_replay_revision_workspace_gate",
        "relationship_graph_global_replace_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Chinese long-form control audit:")
    if "author_candidate_canon_confirmation_gate" in pattern_names:
        lines.append("- author_candidate_canon_confirmation_gate: keep AI suggestions and source-derived ideas as candidates until preview, confirm, and apply are recorded")
    if "progressive_spoiler_context_window_gate" in pattern_names:
        lines.append("- progressive_spoiler_context_window_gate: select outline/RAG/future context by current story stage and block premature spoiler leakage")
    if "chapter_control_card_writeback_gate" in pattern_names:
        lines.append("- chapter_control_card_writeback_gate: require a chapter control card before drafting and write back accepted event, relationship, foreshadow, world-rule, and next-pressure deltas")
    if "trace_replay_revision_workspace_gate" in pattern_names:
        lines.append("- trace_replay_revision_workspace_gate: preserve blueprint, selected context, rewrite direction, reviewer findings, and downstream impact scope for each revision")
    if "relationship_graph_global_replace_gate" in pattern_names:
        lines.append("- relationship_graph_global_replace_gate: regenerate relationship graph and preview global replacements across bible, outline, chapters, memory, and graph before acceptance")


def _append_bookrun_skill_protocol_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render BookRun, provider, sidecar, outline, localization, protocol, and anti-slop gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "bookrun_audit_trail_gate",
        "provider_budget_smoke_gate",
        "sidecar_memory_profile_boundary",
        "outline_checkpoint_milestone_gate",
        "language_localization_style_profile_gate",
        "progressive_disclosure_skill_protocol_gate",
        "anti_slop_rulepack_triage_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("BookRun and skill protocol audit:")
    if "bookrun_audit_trail_gate" in pattern_names:
        lines.append("- bookrun_audit_trail_gate: keep blueprint, Judge/Repair findings, retry count, accepted chapter, and export audit manifest tied to one replayable run")
    if "provider_budget_smoke_gate" in pattern_names:
        lines.append("- provider_budget_smoke_gate: record provider profile, token/time/cost budget, dry-run vs real smoke status, and stop condition before long generation")
    if "sidecar_memory_profile_boundary" in pattern_names:
        lines.append("- sidecar_memory_profile_boundary: separate UI/API orchestration, sidecar analysis, graph/vector memory, queues, cache, and provider writes by namespace and profile")
    if "outline_checkpoint_milestone_gate" in pattern_names:
        lines.append("- outline_checkpoint_milestone_gate: verify Story Bible version, chapter sequence, checkpoint rollback target, and narrative milestone coverage before drafting")
    if "language_localization_style_profile_gate" in pattern_names:
        lines.append("- language_localization_style_profile_gate: enforce language-specific units, honorifics, punctuation, glossary, dialect limits, and localized speaker register")
    if "progressive_disclosure_skill_protocol_gate" in pattern_names:
        lines.append("- progressive_disclosure_skill_protocol_gate: route to only needed protocols and bind required knowledge-base files before generation or review")
    if "anti_slop_rulepack_triage_gate" in pattern_names:
        lines.append("- anti_slop_rulepack_triage_gate: triage banned vocabulary, inflated copulas, vague attribution, marketing cadence, and repeated AI-prose structure as review tasks")


def _append_project_workbench_memory_diversity_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render project-blueprint, canon runtime, staged outline, wiki, scene-index, and diversity gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "user_modifier_project_blueprint_gate",
        "portable_canon_skill_runtime_gate",
        "staged_outline_chunk_window_gate",
        "wiki_canon_graph_lint_gate",
        "plan_draft_log_verify_loop_gate",
        "mcp_scene_index_revision_boundary",
        "verbalized_sampling_diversity_wiki_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Project workbench and memory diversity audit:")
    if "user_modifier_project_blueprint_gate" in pattern_names:
        lines.append("- user_modifier_project_blueprint_gate: bind project modifiers, initial plan, chapter plan, prose, review, revision, timing log, and exported state to one blueprint id")
    if "portable_canon_skill_runtime_gate" in pattern_names:
        lines.append("- portable_canon_skill_runtime_gate: separate story assets, frontmatter, canon JSON, skill/rule layer, workflow state, checkpoints, artifacts, and export outputs")
    if "staged_outline_chunk_window_gate" in pattern_names:
        lines.append("- staged_outline_chunk_window_gate: plan long outlines in setup/part chunks, keep current plus adjacent context detailed, and record chapter-range refinement windows")
    if "wiki_canon_graph_lint_gate" in pattern_names:
        lines.append("- wiki_canon_graph_lint_gate: run story-bible wiki health, canon lint, continuity query, timeline contradiction, setup/payoff, and relationship graph checks")
    if "plan_draft_log_verify_loop_gate" in pattern_names:
        lines.append("- plan_draft_log_verify_loop_gate: after each chapter, update scene logs, continuity records, glossary, thread tracking, foreshadowing checklists, and wrap/resume state")
    if "mcp_scene_index_revision_boundary" in pattern_names:
        lines.append("- mcp_scene_index_revision_boundary: require scene ids, metadata-first context, edit scope, human confirmation, reversible diff, git/history evidence, and review bundle")
    if "verbalized_sampling_diversity_wiki_gate" in pattern_names:
        lines.append("- verbalized_sampling_diversity_wiki_gate: sample multiple probability-scored variants, reject source-like clusters, and auto-file accepted ideas into the project writer wiki")


def _append_interactive_narrative_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render branching narrative, dialogue-node, passage-link, and choice-state gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "branching_choice_graph",
        "node_dialogue_state_machine",
        "passage_link_navigation_map",
        "choice_stats_consequence_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Interactive narrative audit:")
    if "branching_choice_graph" in pattern_names:
        lines.append("- branching_choice_graph: model choices as branch edges with source node, option intent, consequence scope, and merge/reject decision")
    if "node_dialogue_state_machine" in pattern_names:
        lines.append("- node_dialogue_state_machine: dialogue nodes declare entry conditions, speaker state, available options, commands, and exit deltas")
    if "passage_link_navigation_map" in pattern_names:
        lines.append("- passage_link_navigation_map: passage links need reachable path checks, intentional merge points, and no accidental dead ends")
    if "choice_stats_consequence_gate" in pattern_names:
        lines.append("- choice_stats_consequence_gate: every choice-stat mutation needs visible consequence, trigger record, stat delta, and payoff window")


def _append_copy_similarity_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render source-copy fingerprint, fuzzy phrase, and diff-span gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "source_text_fingerprint_gate",
        "fuzzy_phrase_similarity_gate",
        "diff_span_copy_review",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Copy similarity audit:")
    if "source_text_fingerprint_gate" in pattern_names:
        lines.append("- source_text_fingerprint_gate: compare source and draft fingerprints; review high-overlap windows before acceptance")
    if "fuzzy_phrase_similarity_gate" in pattern_names:
        lines.append("- fuzzy_phrase_similarity_gate: apply fuzzy phrase thresholds to catch paraphrased source sentences and renamed proper-noun strings")
    if "diff_span_copy_review" in pattern_names:
        lines.append("- diff_span_copy_review: inspect diff spans for copied wording, source sentence order, semantic-cleanup matches, and patch-like edits")


def _append_near_duplicate_semantic_dedup_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render MinHash/SimHash/semantic dedup independence gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "minhash_lsh_near_duplicate_gate",
        "simhash_hamming_similarity_gate",
        "semantic_duplicate_cluster_gate",
        "embedding_similarity_independence_gate",
        "corpus_leakage_dedup_review_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Near-duplicate and semantic dedup audit:")
    if "minhash_lsh_near_duplicate_gate" in pattern_names:
        lines.append("- minhash_lsh_near_duplicate_gate: compare source and draft shingles; review high-Jaccard near-duplicate windows before acceptance")
    if "simhash_hamming_similarity_gate" in pattern_names:
        lines.append("- simhash_hamming_similarity_gate: flag low-Hamming-distance windows that survive renaming, translation, or polish")
    if "semantic_duplicate_cluster_gate" in pattern_names:
        lines.append("- semantic_duplicate_cluster_gate: cluster semantic neighbors so paraphrased source scenes cannot pass as independent drafts")
    if "embedding_similarity_independence_gate" in pattern_names:
        lines.append("- embedding_similarity_independence_gate: require key passages to be closer to transformed canon/brief than to source excerpts")
    if "corpus_leakage_dedup_review_gate" in pattern_names:
        lines.append("- corpus_leakage_dedup_review_gate: keep source corpora, deconstruction notes, transformed canon, and drafts in separate leakage-auditable manifests")


def _append_text_analysis_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render character quote, readability, lexical, and motif metric gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "character_quote_attribution_map",
        "readability_pacing_metric_gate",
        "lexical_diversity_voice_audit",
        "keyphrase_motif_extraction",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Text analysis audit:")
    if "character_quote_attribution_map" in pattern_names:
        lines.append("- character_quote_attribution_map: map mentions, aliases, quotes, speakers, and quote ownership before voice or relationship review")
    if "readability_pacing_metric_gate" in pattern_names:
        lines.append("- readability_pacing_metric_gate: compare sentence-length, paragraph-density, readability, and scene-density curves before acceptance")
    if "lexical_diversity_voice_audit" in pattern_names:
        lines.append("- lexical_diversity_voice_audit: monitor lexical diversity, repeated vocabulary clusters, MTLD/HD-D drift, and speaker-specific diction")
    if "keyphrase_motif_extraction" in pattern_names:
        lines.append("- keyphrase_motif_extraction: extract keyphrases and motif terms to audit promise coverage, topic drift, and copied source-specific anchors")


def _append_stylometry_style_overfit_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render stylometry, authorship similarity, and style-overfit gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "stylometric_author_fingerprint_gate",
        "function_word_syntax_style_gate",
        "authorship_attribution_similarity_gate",
        "style_overfit_regression_gate",
        "paraphrase_independence_review_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Stylometry and style-overfit audit:")
    if "stylometric_author_fingerprint_gate" in pattern_names:
        lines.append("- stylometric_author_fingerprint_gate: version explicit style fingerprints and keep source-author profiles separate from new-story voice")
    if "function_word_syntax_style_gate" in pattern_names:
        lines.append("- function_word_syntax_style_gate: review function words, punctuation, sentence length, and syntax windows as evidence, not automatic rewrites")
    if "authorship_attribution_similarity_gate" in pattern_names:
        lines.append("- authorship_attribution_similarity_gate: treat high source-author similarity as a copy-risk signal rather than a style target")
    if "style_overfit_regression_gate" in pattern_names:
        lines.append("- style_overfit_regression_gate: run windowed regression after paraphrase, polish, and entity remap to catch source-voice leakage")
    if "paraphrase_independence_review_gate" in pattern_names:
        lines.append("- paraphrase_independence_review_gate: require independence evidence before accepting humanized, transferred, or same-type prose")


def _append_copyedit_prose_lint_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render prose lint, grammar, and diagnostic triage gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "prose_lint_style_rule_gate",
        "grammar_spelling_copyedit_gate",
        "copyedit_diagnostic_triage_queue",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Copyedit and prose lint audit:")
    if "prose_lint_style_rule_gate" in pattern_names:
        lines.append("- prose_lint_style_rule_gate: apply project-local house style rules with speaker, scene, and deliberate-voice exceptions")
    if "grammar_spelling_copyedit_gate" in pattern_names:
        lines.append("- grammar_spelling_copyedit_gate: check grammar, spelling, and copyedit blockers after canon review, while preserving dialogue/register exceptions")
    if "copyedit_diagnostic_triage_queue" in pattern_names:
        lines.append("- copyedit_diagnostic_triage_queue: classify diagnostics as accept, ignore, rewrite, or needs-author-review before chapter acceptance")


def _append_chinese_text_processing_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render Chinese segmentation, NER/alias, normalization, and correction gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "chinese_segmentation_keyword_gate",
        "chinese_ner_alias_consistency_gate",
        "chinese_text_normalization_gate",
        "chinese_error_correction_review_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Chinese text processing audit:")
    if "chinese_segmentation_keyword_gate" in pattern_names:
        lines.append("- chinese_segmentation_keyword_gate: use a project dictionary before Chinese keyword, motif, and retrieval analysis")
    if "chinese_ner_alias_consistency_gate" in pattern_names:
        lines.append("- chinese_ner_alias_consistency_gate: audit character, alias, location, organization, and title consistency before canon write-back")
    if "chinese_text_normalization_gate" in pattern_names:
        lines.append("- chinese_text_normalization_gate: normalize Simplified/Traditional, punctuation width, and variants only as review evidence unless accepted")
    if "chinese_error_correction_review_gate" in pattern_names:
        lines.append("- chinese_error_correction_review_gate: triage typo/correction suggestions while protecting names, dialect, and invented terms")


def _append_source_import_extraction_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render source-format import, PDF/OCR, partition, and provenance gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "source_format_import_manifest",
        "pdf_layout_text_extraction_gate",
        "ocr_scanned_page_import_gate",
        "document_partition_chapter_detection_gate",
        "import_provenance_checksum_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Source import extraction audit:")
    if "source_format_import_manifest" in pattern_names:
        lines.append("- source_format_import_manifest: record source format, metadata, TOC/spine order, detected chapters, and skipped sections before deconstruction")
    if "pdf_layout_text_extraction_gate" in pattern_names:
        lines.append("- pdf_layout_text_extraction_gate: review PDF page spans, text blocks, reading order, headers/footers, and extraction gaps before analysis")
    if "ocr_scanned_page_import_gate" in pattern_names:
        lines.append("- ocr_scanned_page_import_gate: route scanned-page OCR confidence gaps and low-confidence spans to manual review before canon or style extraction")
    if "document_partition_chapter_detection_gate" in pattern_names:
        lines.append("- document_partition_chapter_detection_gate: keep typed document elements and uncertain chapter headings separate until accepted")
    if "import_provenance_checksum_gate" in pattern_names:
        lines.append("- import_provenance_checksum_gate: keep original, extracted, normalized, and accepted text artifacts linked by checksum, parser version, and settings")


def _append_literary_event_graph_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render literary annotation, event graph, emotion arc, and character-network gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "literary_event_entity_annotation_gate",
        "narrative_event_evolution_graph_gate",
        "sentiment_arc_emotion_trajectory_gate",
        "cross_context_coreference_gate",
        "character_interaction_network_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Literary event graph audit:")
    if "literary_event_entity_annotation_gate" in pattern_names:
        lines.append("- literary_event_entity_annotation_gate: separate source entities, events, participant roles, and mention spans before canon or summary write-back")
    if "narrative_event_evolution_graph_gate" in pattern_names:
        lines.append("- narrative_event_evolution_graph_gate: review temporal, causal, discourse, blocker, and payoff edges before using source event chains")
    if "sentiment_arc_emotion_trajectory_gate" in pattern_names:
        lines.append("- sentiment_arc_emotion_trajectory_gate: track global and character emotion curves with turning-point reasons, not as automatic quality scores")
    if "cross_context_coreference_gate" in pattern_names:
        lines.append("- cross_context_coreference_gate: keep ambiguous cross-chapter/source mention clusters out of accepted canon until reviewed")
    if "character_interaction_network_gate" in pattern_names:
        lines.append("- character_interaction_network_gate: audit interaction frequency, centrality, relationship polarity, and timing before accepting relationship canon")


def _append_segmentation_summary_topic_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render chunking, chapter-summary, and topic-drift gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "semantic_chunk_boundary_map",
        "chapter_summary_anchor_gate",
        "topic_drift_map",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Segmentation, summary, and topic audit:")
    if "semantic_chunk_boundary_map" in pattern_names:
        lines.append("- semantic_chunk_boundary_map: split source and generated chapters at semantic boundaries with chunk id, overlap policy, boundary reason, and inclusion purpose")
    if "chapter_summary_anchor_gate" in pattern_names:
        lines.append("- chapter_summary_anchor_gate: anchor every summary to accepted chapter ids, representative sentences, canon status, and unresolved-hook evidence")
    if "topic_drift_map" in pattern_names:
        lines.append("- topic_drift_map: map topic clusters across chapters and flag off-arc drift, missing promises, or copied source topic sequence")


def _append_eval_observability_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render grounding, trace, and prompt-regression gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "context_faithfulness_eval_gate",
        "retrieval_trace_observability_gate",
        "prompt_regression_eval_suite",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Evaluation, trace, and regression audit:")
    if "context_faithfulness_eval_gate" in pattern_names:
        lines.append("- context_faithfulness_eval_gate: score generated facts against accepted canon, retrieved context, summary anchors, and grounding evidence before write-back")
    if "retrieval_trace_observability_gate" in pattern_names:
        lines.append("- retrieval_trace_observability_gate: persist query, selected chunks, omitted candidates, relevance reason, and generation spans for context review")
    if "prompt_regression_eval_suite" in pattern_names:
        lines.append("- prompt_regression_eval_suite: run golden continuation and same-type cases before prompt-pack or context-selection changes")


def _append_long_output_reward_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render plan-write, long-output, and reward-dimension gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "agentwrite_plan_write_pipeline",
        "long_output_length_quality_ruler",
        "long_context_reward_dimension_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Long output plan-write reward audit:")
    if "agentwrite_plan_write_pipeline" in pattern_names:
        lines.append("- agentwrite_plan_write_pipeline: validate plan artifacts before prose expansion and link each write stage to its plan segment")
    if "long_output_length_quality_ruler" in pattern_names:
        lines.append("- long_output_length_quality_ruler: check target length, actual length, truncation, repetition, premature ending, coherence, canon, and style together")
    if "long_context_reward_dimension_gate" in pattern_names:
        lines.append("- long_context_reward_dimension_gate: score helpfulness, logicality, faithfulness, and completeness separately; do not average away blocking failures")


def _append_creative_writing_benchmark_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render creative-writing benchmark, judge, and reader-axis gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "instance_specific_writing_criteria_gate",
        "material_grounded_query_refinement",
        "hybrid_rubric_pairwise_elo_judge",
        "judge_bias_mitigation_check",
        "plan_reflect_character_chapter_pipeline",
        "human_story_metric_panel",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Creative writing benchmark audit:")
    if "instance_specific_writing_criteria_gate" in pattern_names:
        lines.append("- instance_specific_writing_criteria_gate: attach local criteria for canon, requested beat, style target, length/format, and reader promise")
    if "material_grounded_query_refinement" in pattern_names:
        lines.append("- material_grounded_query_refinement: prune irrelevant reference material and rewrite ambiguous chapter tasks before drafting")
    if "hybrid_rubric_pairwise_elo_judge" in pattern_names:
        lines.append("- hybrid_rubric_pairwise_elo_judge: score candidates by rubric before pairwise comparison; do not let length bias decide the winner")
    if "judge_bias_mitigation_check" in pattern_names:
        lines.append("- judge_bias_mitigation_check: swap comparison order and inspect length, position, verbosity, and ornate-prose bias")
    if "plan_reflect_character_chapter_pipeline" in pattern_names:
        lines.append("- plan_reflect_character_chapter_pipeline: persist brainstorm, plan critique, and character-profile updates before chapter writing")
    if "human_story_metric_panel" in pattern_names:
        lines.append("- human_story_metric_panel: track relevance, coherence, empathy, surprise, engagement, and complexity as separate reader-facing axes")


def _append_story_generation_pipeline_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render hierarchical generation, recursive revision, persona, and event-realization gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "hierarchical_cowriting_story_scaffold",
        "human_coauthor_edit_boundary",
        "recursive_reprompt_revision_loop",
        "reranker_guided_candidate_selection",
        "character_dialogue_persona_memory",
        "event_to_sentence_realization_trace",
        "entity_memory_slotfill_grounding",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Story generation pipeline audit:")
    if "hierarchical_cowriting_story_scaffold" in pattern_names:
        lines.append("- hierarchical_cowriting_story_scaffold: validate logline, character, plot-point, location, and dialogue layers separately before prose expansion")
    if "human_coauthor_edit_boundary" in pattern_names:
        lines.append("- human_coauthor_edit_boundary: treat generated material as editable co-writing output; inspect plagiarism, toxicity, stereotype, and formulaic risks")
    if "recursive_reprompt_revision_loop" in pattern_names:
        lines.append("- recursive_reprompt_revision_loop: keep plan, draft, rewrite, and edit as separate evidence-backed stages")
    if "reranker_guided_candidate_selection" in pattern_names:
        lines.append("- reranker_guided_candidate_selection: compare candidates by relevance to plan and coherence with accepted canon before choosing")
    if "character_dialogue_persona_memory" in pattern_names:
        lines.append("- character_dialogue_persona_memory: use dialogue evidence for tone and personality without copying source lines")
    if "event_to_sentence_realization_trace" in pattern_names:
        lines.append("- event_to_sentence_realization_trace: preserve plot event, realized sentence, confidence, and rejected alternative trace")
    if "entity_memory_slotfill_grounding" in pattern_names:
        lines.append("- entity_memory_slotfill_grounding: ground names, roles, locations, and objects against entity memory before accepting prose")


def _append_source_deconstruction_memory_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render book-memory, source-deconstruction, glossary, and edit-note gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "book_memory_bank_context_lattice",
        "spec_driven_fiction_scene_tasks",
        "toc_aware_source_deconstruction",
        "two_pass_context_glossary_pipeline",
        "inline_author_edit_markup_versioning",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Source deconstruction memory audit:")
    if "book_memory_bank_context_lattice" in pattern_names:
        lines.append("- book_memory_bank_context_lattice: separate source notes, story structure, world/characters, style guide, active context, and progress updates")
    if "spec_driven_fiction_scene_tasks" in pattern_names:
        lines.append("- spec_driven_fiction_scene_tasks: derive scene tasks from the story bible/constitution and check POV, glossary, subplot, pacing, and continuity gates")
    if "toc_aware_source_deconstruction" in pattern_names:
        lines.append("- toc_aware_source_deconstruction: keep source TOC hierarchy, summaries, quotes, anecdotes, and craft notes outside accepted new-story canon")
    if "two_pass_context_glossary_pipeline" in pattern_names:
        lines.append("- two_pass_context_glossary_pipeline: run analysis before generation, then use summary, previous-summary bridge, and cumulative glossary consistently")
    if "inline_author_edit_markup_versioning" in pattern_names:
        lines.append("- inline_author_edit_markup_versioning: keep author notes and edit notes visible until processed, reviewed, and versioned")


def _append_chapter_progressive_disassembly_checkpoint_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render source-analysis coverage before continuation uses拆书 state."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    if "chapter_progressive_disassembly_checkpoint_gate" not in pattern_names:
        return

    audit = _chapter_progressive_disassembly_checkpoint_audit(bible=bible, max_items=8)
    hints = _as_note_list(source_pattern_pack.get("chapter_progressive_disassembly_checkpoint_gate_hints")) if source_pattern_pack else []

    lines.append("")
    lines.append("Chapter-progressive disassembly checkpoint audit:")
    lines.append(
        "- source_analysis_coverage: "
        f"source_chapters={audit['source_chapter_count']}, "
        f"analysis_packages={audit['source_analysis_package_count']}, "
        f"coverage={audit['source_analysis_coverage_percent']}%"
    )
    if audit["missing_source_analysis_chapters"]:
        lines.append(
            "- missing_source_analysis_chapters: "
            f"{', '.join(audit['missing_source_analysis_chapters'])}"
        )
    lines.append(
        "- checkpoint_rule: normalize source chapters, keep raw_output outside canon, "
        "and checkpoint accepted JSON/Markdown analysis before continuation"
    )
    lines.append(
        "- qa_citation_jump_trace: QA citation jumps are required before full-scope "
        "continuation, source claims, or same-type transformation"
    )
    if hints:
        lines.append(f"- source_hint: {_truncate(hints[0], 260)}")
    if audit["warnings"]:
        lines.append(f"- disassembly_checkpoint_warnings: {', '.join(audit['warnings'])}")


def _append_canon_graph_retrieval_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render temporal graph, memory, GraphRAG, and schema extraction gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "temporal_canon_context_graph",
        "long_term_author_preference_memory",
        "community_graph_source_deconstruction",
        "dual_level_graph_vector_retrieval",
        "schema_guided_graph_extraction",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Canon graph retrieval audit:")
    if "temporal_canon_context_graph" in pattern_names:
        lines.append("- temporal_canon_context_graph: store canon facts as dated/provenanced episodes and resolve validity windows before context use")
    if "long_term_author_preference_memory" in pattern_names:
        lines.append("- long_term_author_preference_memory: separate author preferences, project style decisions, session goals, and transient notes")
    if "community_graph_source_deconstruction" in pattern_names:
        lines.append("- community_graph_source_deconstruction: use source entity communities as analysis evidence, not transformed-story canon")
    if "dual_level_graph_vector_retrieval" in pattern_names:
        lines.append("- dual_level_graph_vector_retrieval: combine vector similarity with graph traversal and log local/global/hybrid mode per context item")
    if "schema_guided_graph_extraction" in pattern_names:
        lines.append("- schema_guided_graph_extraction: require bounded node labels, relationship types, properties, source metadata, and confidence for graph updates")


def _append_story_bible_continuity_qa_audit_section(
    *,
    lines: list[str],
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
    source_pattern_pack: Optional[dict[str, Any]],
    mode: str,
) -> None:
    """Render story-bible QA, canon drift, and consequence-ledger gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "markdown_skill_story_project_contract_gate",
        "canon_evidence_suggestion_review_gate",
        "expert_chain_alignment_creativity_gate",
        "visual_story_bible_continuity_gate",
        "story_daemon_evolution_loop",
        "local_rag_writing_ide_gate",
        "canon_drift_continuity_qa_gate",
        "longrun_commit_projection_health_gate",
        "fresh_context_chapter_iteration_gate",
        "narrative_qa_comprehension_gate",
        "chapter_summary_alignment_gate",
        "story_question_answer_validation_gate",
        "causal_why_explanation_gate",
        "story_commonsense_consistency_gate",
        "query_focused_long_summary_gate",
        "temporal_canon_context_graph",
        "chapter_memory_ingestion_context_budget_gate",
        "human_ai_decision_authority_gate",
        "parallel_critic_tribunal_issue_gate",
        "project_isolated_story_bible_query_gate",
        "work_dna_method_transfer_eval_gate",
        "governed_full_reading_continuation_gate",
        "story_import_pattern_revision_gate",
        "consequence_ledger_last_actions_context_gate",
        "canonkit_local_canon_drift_context_pack_gate",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    canonkit_hints = (
        _as_note_list(source_pattern_pack.get("canonkit_local_canon_drift_context_pack_gate_hints"))
        if isinstance(source_pattern_pack, dict)
        else []
    )
    canonkit_audit = (
        _canonkit_local_canon_drift_context_pack_audit(
            bible=bible,
            plan=plan,
            max_items=12,
        )
        if "canonkit_local_canon_drift_context_pack_gate" in pattern_names
        else {"warnings": []}
    )

    lines.append("")
    lines.append("Story-bible continuity QA audit:")
    if "markdown_skill_story_project_contract_gate" in pattern_names:
        lines.append("- markdown_skill_story_project_contract_gate: treat frontmatter, continuity questions, and promise/payoff labels as checkable state, not prose to copy")
    if "canon_evidence_suggestion_review_gate" in pattern_names:
        lines.append("- canon_evidence_suggestion_review_gate: canon fixes need evidence refs plus author/reviewer acceptance before writeback")
    if "canon_drift_continuity_qa_gate" in pattern_names:
        lines.append("- canon_drift_continuity_qa_gate: ask drift questions for characters, objects, scene facts, and relationship timing before draft promotion")
    if "canonkit_local_canon_drift_context_pack_gate" in pattern_names:
        lines.append("")
        lines.append("CanonKit local canon-drift context-pack gate:")
        lines.append(
            "- local_first_canon_system: treat character cards, locations, rules, "
            "scenes, and accepted state as the local source of truth before drafting"
        )
        lines.append(
            "- drift_detectors: detect missing core character setup, age/year mismatch, "
            "missing entity references, state conflicts, and asymmetric relationships"
        )
        lines.append(
            "- focused_scene_context_pack: build a scene-scoped context pack from "
            "accepted canon only, with included facts, omitted-but-relevant notes, "
            "and current-scene reason"
        )
        lines.append(
            "- JSON import/export boundary: external JSON, browser persistence, demo "
            "state, and local project storage stay runtime-deferred during static intake"
        )
        if mode == "same-type":
            lines.append(
                "- same_type_boundary: transfer detector categories only; rebuild target "
                "character cards, scene records, JSON context packs, and canon facts independently"
            )
        else:
            lines.append(
                "- continuation_boundary: drift checks and focused context packs must use "
                "target-owned accepted bible, plan, scene, and chapter packages"
            )
        if canonkit_hints:
            lines.append(f"- source_hint: {_truncate(canonkit_hints[0], 260)}")
        if canonkit_audit["warnings"] and mode != "same-type":
            lines.append(f"- canonkit_context_pack_warnings: {', '.join(canonkit_audit['warnings'])}")
    if "consequence_ledger_last_actions_context_gate" in pattern_names:
        lines.append("- consequence_ledger_last_actions_context_gate: keep last actions, consequences, state mutation, and compression freshness visible as short-term context")
    if "story_import_pattern_revision_gate" in pattern_names:
        lines.append("- story_import_pattern_revision_gate: separate source import passes, abstract pattern extraction, alternates, and accepted manuscript revisions")
    if "project_isolated_story_bible_query_gate" in pattern_names:
        lines.append("- project_isolated_story_bible_query_gate: bind story-bible query answers to one project manifest and require confirmation before canon use")
    if "work_dna_method_transfer_eval_gate" in pattern_names:
        lines.append("- work_dna_method_transfer_eval_gate: transfer only abstract method axes and require difference axes plus copy-risk review")
    if "governed_full_reading_continuation_gate" in pattern_names:
        lines.append("- governed_full_reading_continuation_gate: full-book continuation needs coverage, finalized reading state, and evidence refs")
    if "longrun_commit_projection_health_gate" in pattern_names:
        lines.append("- longrun_commit_projection_health_gate: draft from accepted chapter commits and reject stale read-model projections")
    if "fresh_context_chapter_iteration_gate" in pattern_names:
        lines.append("- fresh_context_chapter_iteration_gate: resume from the next incomplete chapter using fresh context and explicit progress state")
    if "narrative_qa_comprehension_gate" in pattern_names or "story_question_answer_validation_gate" in pattern_names:
        lines.append("- narrative_qa_comprehension_gate: validate why/what/known-by-whom answers against transformed-story evidence only")
    if "chapter_summary_alignment_gate" in pattern_names:
        lines.append("- chapter_summary_alignment_gate: keep chapter summaries aligned with accepted causal order and current plan")
    if "story_commonsense_consistency_gate" in pattern_names or "causal_why_explanation_gate" in pattern_names:
        lines.append("- story_commonsense_consistency_gate: test motives, belief states, and causal why-explanations before accepting a scene")
    if "chapter_memory_ingestion_context_budget_gate" in pattern_names:
        lines.append("- chapter_memory_ingestion_context_budget_gate: separate source chapter memory, transformed canon, retrieval hits, and prompt budget cuts")
    if "human_ai_decision_authority_gate" in pattern_names:
        lines.append("- human_ai_decision_authority_gate: AI suggestions stay candidates until a visible human/author decision promotes them")
    if "parallel_critic_tribunal_issue_gate" in pattern_names:
        lines.append("- parallel_critic_tribunal_issue_gate: critic votes must surface unresolved continuity, copy-risk, and arc-ledger issues")
    if "query_focused_long_summary_gate" in pattern_names:
        lines.append("- query_focused_long_summary_gate: summarize only the question-relevant accepted facts and preserve omitted-context notes")


def _append_inspectable_rewrite_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render inspectable planning, rewrite, trace, and validation gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "human_synopsis_gate",
        "retrieval_guided_span_rewrite",
        "runtime_artifact_trace",
        "schema_validated_state_delta",
        "recursive_adaptive_planning",
        "workflow_manuscript_compilation",
        "writing_session_goal_tracking",
        "inspectable_run_workspace",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Inspectable rewrite audit:")
    if "human_synopsis_gate" in pattern_names:
        lines.append("- human_synopsis_gate: accept, edit, or regenerate synopsis and chapter summaries before prose expansion")
    if "retrieval_guided_span_rewrite" in pattern_names:
        lines.append("- retrieval_guided_span_rewrite: retrieve related body spans and outline nodes; rewrite only named spans and emit outline sync delta")
    if "runtime_artifact_trace" in pattern_names:
        lines.append("- runtime_artifact_trace: persist intent, selected context, rule stack, and trace for each chapter run")
    if "schema_validated_state_delta" in pattern_names:
        lines.append("- schema_validated_state_delta: validate structured state deltas before canon mutation; reject bad deltas instead of normalizing them")
    if "recursive_adaptive_planning" in pattern_names:
        lines.append("- recursive_adaptive_planning: split work into retrieval, reasoning, planning, composition, and review subtasks; replan on contradiction")
    if "workflow_manuscript_compilation" in pattern_names:
        lines.append("- workflow_manuscript_compilation: compile only accepted ordered scenes into manuscript outputs")
    if "writing_session_goal_tracking" in pattern_names:
        lines.append("- writing_session_goal_tracking: track target and accepted word counts without letting quota override continuity gates")
    if "inspectable_run_workspace" in pattern_names:
        lines.append("- inspectable_run_workspace: expose session, storyboard, manuscript surface, current phase, pending review, and memory refs")


def _append_production_review_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render production, continuity-bridge, voice, and review gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "craft_role_pipeline",
        "frontmatter_story_schema",
        "continuity_bridge_window",
        "episode_range_rewrite_scope",
        "voice_table_polish_axis",
        "boring_opening_quality_gates",
        "beat_strand_framework",
        "anti_hallucination_plan_check",
        "backup_restore_checkpoint",
        "multi_level_review_trend",
        "editor_notes_feedback_loop",
        "genre_parameterized_worldbuilding",
        "prose_preflight_voice_calibration",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Production review audit:")
    if "craft_role_pipeline" in pattern_names:
        lines.append("- craft_role_pipeline: keep architecture, character, prose, continuity, review, edit, and export outputs separate")
    if "frontmatter_story_schema" in pattern_names:
        lines.append("- frontmatter_story_schema: store scene state, continuity questions, promises/payoffs, and chapter draft metadata as stable fields")
    if "continuity_bridge_window" in pattern_names:
        lines.append("- continuity_bridge_window: feed the next chapter from recent accepted chapters, active timeline, open hooks, character state, and editor notes")
    if "episode_range_rewrite_scope" in pattern_names:
        lines.append("- episode_range_rewrite_scope: calculate impacted chapters and re-polish gates before applying range rewrites")
    if "voice_table_polish_axis" in pattern_names:
        lines.append("- voice_table_polish_axis: check dialogue against per-character diction, sentence endings, rhythm, and nonverbal palette")
    if "boring_opening_quality_gates" in pattern_names:
        lines.append("- boring_opening_quality_gates: reject exposition-only openings, flat scene purpose, missing pressure, and weak chapter-end hooks")
    if "beat_strand_framework" in pattern_names:
        lines.append("- beat_strand_framework: track external plot, internal change, and relationship strands with convergence beats")
    if "anti_hallucination_plan_check" in pattern_names:
        lines.append("- anti_hallucination_plan_check: verify new facts against bible, plan, retrieval evidence, and accepted chapter-change packages")
    if "backup_restore_checkpoint" in pattern_names:
        lines.append("- backup_restore_checkpoint: create restore points before bulk generation, range rewrites, or destructive canon merges")
    if "multi_level_review_trend" in pattern_names:
        lines.append("- multi_level_review_trend: review scene, chapter, batch, and cross-chapter trend risks before acceptance")
    if "editor_notes_feedback_loop" in pattern_names:
        lines.append("- editor_notes_feedback_loop: carry open editor notes forward and close them only with chapter evidence")
    if "genre_parameterized_worldbuilding" in pattern_names:
        lines.append("- genre_parameterized_worldbuilding: parameterize factions, locations, conflict sources, and taboo moves by genre/subgenre")
    if "prose_preflight_voice_calibration" in pattern_names:
        lines.append("- prose_preflight_voice_calibration: use voice samples to remove generic AI tells without inventing unsupported facts")


def _append_consistency_style_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render sourcebook, semantic-retrieval, consistency, and stylometry gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "sourcebook_author_workbench",
        "semantic_long_context_search",
        "contradiction_taxonomy_checker",
        "parallel_agent_chapter_pipeline",
        "cross_chapter_redundancy_audit",
        "humanization_stylometry_levers",
        "author_control_boundary",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Consistency and style audit:")
    if "sourcebook_author_workbench" in pattern_names:
        lines.append("- sourcebook_author_workbench: sourcebook entries are author-owned canon candidates; AI suggestions need acceptance before reuse")
    if "semantic_long_context_search" in pattern_names:
        lines.append("- semantic_long_context_search: cite query, matched artifact, inclusion reason, and canon status for each long-context hit")
    if "contradiction_taxonomy_checker" in pattern_names:
        lines.append("- contradiction_taxonomy_checker: check characterization, factual detail, narrative style, timeline/plot, and world-rule conflicts")
    if "parallel_agent_chapter_pipeline" in pattern_names:
        lines.append("- parallel_agent_chapter_pipeline: isolate chapter jobs and aggregate reviews before revision cycles")
    if "cross_chapter_redundancy_audit" in pattern_names:
        lines.append("- cross_chapter_redundancy_audit: count repeated scene shapes, weak causality, flat dialogue, and over-regular prose across chapters")
    if "humanization_stylometry_levers" in pattern_names:
        lines.append("- humanization_stylometry_levers: apply burstiness, specificity, discourse variation, and AI-transition cleanup only after canon checks")
    if "author_control_boundary" in pattern_names:
        lines.append("- author_control_boundary: keep AI proposals, accepted canon, and disclosure/labeling decisions separate")


def _append_research_multimodal_experiment_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render research taxonomy, adaptation, agent-planner, and experiment gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "research_taxonomy_story_map",
        "novel_to_multimodal_pipeline",
        "entity_to_visual_asset_pipeline",
        "agentic_book_planner_pipeline",
        "rag_synopsis_spine",
        "anti_repetition_prompt_rules",
        "prompt_recipe_experiment_grid",
        "append_only_generation_review_log",
        "narrative_arc_template_control",
        "nrd_task_tree_pipeline",
        "sampling_parameter_quality_sweep",
        "story_structure_rag_planning",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Research, multimodal, and experiment audit:")
    if "research_taxonomy_story_map" in pattern_names:
        lines.append("- research_taxonomy_story_map: use method categories as coverage checks; keep indexes out of runtime prompts")
    if "novel_to_multimodal_pipeline" in pattern_names:
        lines.append("- novel_to_multimodal_pipeline: treat scripts, storyboards, and videos as derived artifacts unless accepted into canon")
    if "entity_to_visual_asset_pipeline" in pattern_names:
        lines.append("- entity_to_visual_asset_pipeline: tie visual assets to entity/card versions so stale images do not overwrite prose state")
    if "agentic_book_planner_pipeline" in pattern_names:
        lines.append("- agentic_book_planner_pipeline: separate Story Bible, Characters, Plot Threads, Chapter Outlines, Writer, Editor, and Continuity Checker artifacts")
    if "rag_synopsis_spine" in pattern_names:
        lines.append("- rag_synopsis_spine: retrieve from the full synopsis spine with query, matched chapter, inclusion reason, and canon status")
    if "anti_repetition_prompt_rules" in pattern_names:
        lines.append("- anti_repetition_prompt_rules: reject repeated phrases, repeated scene shapes, repeated causal bridges, and repeated emotional beats")
    if "prompt_recipe_experiment_grid" in pattern_names:
        lines.append("- prompt_recipe_experiment_grid: compare prompt recipes under fixed inputs, rubric review, and keep/discard decisions")
    if "append_only_generation_review_log" in pattern_names:
        lines.append("- append_only_generation_review_log: append experiment evidence instead of rewriting previous review rows")
    if "narrative_arc_template_control" in pattern_names:
        lines.append("- narrative_arc_template_control: declare genre, story style, author style, arc, and scenario blueprint before drafting")
    if "nrd_task_tree_pipeline" in pattern_names:
        lines.append("- nrd_task_tree_pipeline: track arcs -> chapters -> scenes -> revision passes with continuity reports")
    if "sampling_parameter_quality_sweep" in pattern_names:
        lines.append("- sampling_parameter_quality_sweep: promote parameter defaults only when quality, continuity, voice, and copy-risk all improve")
    if "story_structure_rag_planning" in pattern_names:
        lines.append("- story_structure_rag_planning: map Hero's Journey/Freytag or style-RAG samples to accepted story facts before prose")



def _append_serialized_continuity_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render serialized webnovel contract, snapshot, projection, and review gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "story_contract_commit_chain",
        "fact_snapshot_delta_gate",
        "projection_sync_observability",
        "foreshadowing_debt_budget",
        "reader_retention_review_gate",
        "draft_stage_revision_ladder",
        "rolling_summary_context_trim",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Serialized continuity audit:")
    if "story_contract_commit_chain" in pattern_names:
        lines.append("- story_contract_commit_chain: contracts are canon; drafts become reusable state only through accepted chapter commits")
    if "fact_snapshot_delta_gate" in pattern_names:
        lines.append("- fact_snapshot_delta_gate: validate fact snapshots, change declarations, and after-state before writing canon")
    if "projection_sync_observability" in pattern_names:
        lines.append("- projection_sync_observability: state/index/summary/memory/vector/dashboard views must trace to accepted commits")
    if "foreshadowing_debt_budget" in pattern_names:
        lines.append("- foreshadowing_debt_budget: reserve context for high-debt hooks and cite setup/payoff windows before reveal")
    if "reader_retention_review_gate" in pattern_names:
        lines.append("- reader_retention_review_gate: review consistency, OOC, rhythm, pleasure point, and next-chapter pull together")
    if "draft_stage_revision_ladder" in pattern_names:
        lines.append("- draft_stage_revision_ladder: blueprint -> key info -> task card -> Draft A/B/C -> continuity handoff")
    if "rolling_summary_context_trim" in pattern_names:
        lines.append("- rolling_summary_context_trim: selected rolling summary, character state, timeline events, and dropped context need a manifest")


def _append_story_quality_evaluation_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render story-quality benchmark, rubric, style-axis, and simulation gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "pairwise_story_comparison_ranking",
        "multidimensional_quality_rubric",
        "story_theory_beat_evaluation",
        "constraint_specificity_creativity_benchmark",
        "style_axis_diversity_fingerprint",
        "event_outline_history_compression",
        "agentic_story_world_simulation",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Story quality evaluation audit:")
    if "pairwise_story_comparison_ranking" in pattern_names:
        lines.append("- pairwise_story_comparison_ranking: compare matched chapter variants against the same brief before accepting")
    if "multidimensional_quality_rubric" in pattern_names:
        lines.append("- multidimensional_quality_rubric: score grammar, clarity, causality, scene purpose, consistency, character motive, dialogue, reader pull, and resolution")
    if "story_theory_beat_evaluation" in pattern_names:
        lines.append("- story_theory_beat_evaluation: test beat execution, preservation, bridge quality, and constrained-continuation criteria")
    if "constraint_specificity_creativity_benchmark" in pattern_names:
        lines.append("- constraint_specificity_creativity_benchmark: track required constraints, satisfaction evidence, creativity, and coherence tradeoffs")
    if "style_axis_diversity_fingerprint" in pattern_names:
        lines.append("- style_axis_diversity_fingerprint: inspect voice, rhythm, POV, pacing, tone, imagery, dialogue, experimentation, and closure axes")
    if "event_outline_history_compression" in pattern_names:
        lines.append("- event_outline_history_compression: align compressed history with the current event outline and chapter plan")
    if "agentic_story_world_simulation" in pattern_names:
        lines.append("- agentic_story_world_simulation: keep simulated character choices and social interactions as proposals until canon acceptance")


def _append_reader_market_feedback_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render reader-signal, beta-reader, market-position, and engagement gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant_patterns = {
        "reader_rating_signal_model",
        "review_spoiler_sentiment_corpus",
        "beta_reader_archetype_panel",
        "comp_title_market_positioning",
        "local_reader_experience_editor",
    }
    if not pattern_names.intersection(relevant_patterns):
        return

    lines.append("")
    lines.append("Reader market feedback audit:")
    if "reader_rating_signal_model" in pattern_names:
        lines.append("- reader_rating_signal_model: use ratings, shelves, tags, and to-read signals as aggregate expectation metadata only")
    if "review_spoiler_sentiment_corpus" in pattern_names:
        lines.append("- review_spoiler_sentiment_corpus: cluster praise, complaints, trope requests, and spoiler-sensitive issues without verbatim review text")
    if "beta_reader_archetype_panel" in pattern_names:
        lines.append("- beta_reader_archetype_panel: collect genre-fan, casual-reader, critical-reader, and sensitivity-reader hook/confusion/turn-page notes")
    if "comp_title_market_positioning" in pattern_names:
        lines.append("- comp_title_market_positioning: calibrate promise, tone, audience, and market gap without copying comp premise or blurb beats")
    if "local_reader_experience_editor" in pattern_names:
        lines.append("- local_reader_experience_editor: audit micro-tension, curiosity thread, hook, cliffhanger, opening/ending, rhythm, and context fit")


def _append_trope_independence_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render trope-level independence gates for continuation and same-type creation."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant = {
        "trope_inventory_similarity_gate",
        "trope_graph_expectation_map",
        "trope_density_novelty_budget",
        "trope_source_boundary_review",
    }
    if not pattern_names.intersection(relevant):
        return

    lines.append("")
    lines.append("Trope independence audit:")
    if "trope_inventory_similarity_gate" in pattern_names:
        lines.append("- trope_inventory_similarity_gate: compare source and draft trope inventories; allow genre overlap only after cast, setting, stakes, causal order, and payoff differ")
    if "trope_graph_expectation_map" in pattern_names:
        lines.append("- trope_graph_expectation_map: use trope co-occurrence as expectation options, not as a copied plot route or rare adjacency chain")
    if "trope_density_novelty_budget" in pattern_names:
        lines.append("- trope_density_novelty_budget: track trope density and require a local twist, inversion, shifted cost, or new consequence for saturated clusters")
    if "trope_source_boundary_review" in pattern_names:
        lines.append("- trope_source_boundary_review: trope sources stay metadata-only by default; no live scraping, parser runtime, copied page prose, or mass mirroring in prompts")


def _append_genre_arc_style_governance_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render genre, volume, style-DNA, arc, platform, and entity-timeline gates."""
    pattern_names = _source_pattern_names(source_pattern_pack)
    relevant = {
        "genre_inspiration_budget_library_gate",
        "volume_antipattern_dependency_graph_gate",
        "style_dna_breakpoint_hierarchy_gate",
        "arc_state_foreshadowing_persistence_gate",
        "webnovel_genre_tracker_gate",
        "platform_ranking_research_boundary_gate",
        "entity_mention_arc_timeline_gate",
    }
    if not pattern_names.intersection(relevant):
        return

    lines.append("")
    lines.append("Genre, arc, and style governance audit:")
    if "genre_inspiration_budget_library_gate" in pattern_names:
        lines.append(
            "- genre_inspiration_budget_library_gate: convert genre mix, trope "
            "inspiration, format, quality level, target length, chapter count, and "
            "cost estimate into an abstract option matrix, not a copied premise bundle"
        )
    if "volume_antipattern_dependency_graph_gate" in pattern_names:
        lines.append(
            "- volume_antipattern_dependency_graph_gate: validate volume plan, chapter "
            "rhythm, anti-pattern scan, character-arc enforcement, and event dependency "
            "graph before writer execution"
        )
    if "style_dna_breakpoint_hierarchy_gate" in pattern_names:
        lines.append(
            "- style_dna_breakpoint_hierarchy_gate: keep style-DNA analysis, hierarchy "
            "generation, review dimensions, repair rounds, and breakpoint state as "
            "review artifacts instead of canon facts"
        )
    if "arc_state_foreshadowing_persistence_gate" in pattern_names:
        lines.append(
            "- arc_state_foreshadowing_persistence_gate: maintain major/minor/micro "
            "arcs, character entry/exit state, relationship logs, and foreshadowing "
            "ledgers across chapters"
        )
    if "webnovel_genre_tracker_gate" in pattern_names:
        lines.append(
            "- webnovel_genre_tracker_gate: apply genre-specific trackers for timeline, "
            "foreshadowing, LitRPG stats, romance stages, cliffhanger rotation, stale "
            "characters, and chapter gaps"
        )
    if "platform_ranking_research_boundary_gate" in pattern_names:
        lines.append(
            "- platform_ranking_research_boundary_gate: use platform ranking and category "
            "research only as reader-promise pressure; never import titles, proprietary "
            "tags, chapter text, or paid/free platform details as story canon"
        )
    if "entity_mention_arc_timeline_gate" in pattern_names:
        lines.append(
            "- entity_mention_arc_timeline_gate: link entities to chapter appearances, "
            "flag absence gaps and unsupported returns, and rebuild appearance rhythm "
            "for same-type creation on new entities"
        )


def build_remix_inspired_independence_audit(
    *,
    style_content: str,
    source_pattern_pack: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build same-type creation independence checks from style/source anchors."""
    style_principles = _heading_items(
        style_content,
        heading="\u3010\u540c\u7c7b\u578b\u521b\u4f5c\u603b\u539f\u5219\u3011",
        max_items=12,
    )
    source_voice_samples = _heading_items(
        style_content,
        heading="\u3010\u6e90\u4e66\u8bed\u6c14\u6837\u672c\u3011",
        max_items=12,
    )
    forbidden_source_elements = _heading_items(
        style_content,
        heading="\u3010\u6e90\u4e66\u663e\u6027\u5143\u7d20\u7981\u7528\u6e05\u5355\u3011",
        max_items=16,
    )
    pattern_names = _source_pattern_names(source_pattern_pack)

    transfer_axes = [
        "pov_behavior",
        "pacing_curve",
        "scene_density",
        "dialogue_pressure",
        "emotional_temperature",
    ]
    required_difference_axes = [
        "cast_identity",
        "organization_map",
        "world_rules",
        "conflict_object",
        "event_order",
        "reveal_payoff_sequence",
    ]
    copy_risk_checks = [
        "forbidden_name_scan",
        "source_scene_order_scan",
        "distinctive_wording_scan",
        "set_piece_remap_scan",
    ]

    if pattern_names.intersection(
        {
            "stylometric_author_fingerprint_gate",
            "authorship_attribution_similarity_gate",
            "paraphrase_independence_review_gate",
        }
    ):
        copy_risk_checks.extend([
            "style_similarity_not_goal",
            "authorship_nearest_neighbor_review",
        ])
    if "work_dna_method_transfer_eval_gate" in pattern_names:
        transfer_axes.extend([
            "narrative_engine",
            "scene_architecture",
            "information_control",
            "character_grammar",
        ])
        required_difference_axes.extend([
            "motif_family",
            "theme_answer",
        ])
    if "story_import_pattern_revision_gate" in pattern_names:
        copy_risk_checks.extend([
            "source_import_pass_boundary",
            "alternate_draft_not_canon",
        ])
    if "governed_full_reading_continuation_gate" in pattern_names:
        copy_risk_checks.append("reading_evidence_not_new_story_canon")
    if "genre_inspiration_budget_library_gate" in pattern_names:
        transfer_axes.extend([
            "genre_promise_matrix",
            "trope_option_budget",
        ])
        required_difference_axes.extend([
            "premise_bundle",
            "chapter_order",
            "budget_lineage",
        ])
        copy_risk_checks.append("inspiration_library_canon_leakage")
    if "volume_antipattern_dependency_graph_gate" in pattern_names:
        required_difference_axes.extend([
            "volume_escalation_ladder",
            "event_dependency_edges",
            "character_arc_checkpoints",
        ])
        copy_risk_checks.append("source_dependency_graph_clone")
    if "style_dna_breakpoint_hierarchy_gate" in pattern_names:
        transfer_axes.append("style_pressure_axes")
        copy_risk_checks.append("style_dna_overfit_review")
    if "arc_state_foreshadowing_persistence_gate" in pattern_names:
        required_difference_axes.extend([
            "arc_id_namespace",
            "foreshadowing_id_namespace",
            "relationship_state_route",
        ])
        copy_risk_checks.append("source_arc_state_persistence_leak")
    if "entity_mention_arc_timeline_gate" in pattern_names:
        required_difference_axes.extend([
            "appearance_rhythm",
            "entity_absence_gaps",
        ])
        copy_risk_checks.append("source_entity_timeline_clone")
    if "premise_structure_hook_payoff_gate" in pattern_names:
        transfer_axes.extend([
            "reader_promise_shape",
            "hook_payoff_timing",
            "structure_pressure_curve",
        ])
        required_difference_axes.extend([
            "premise_logline",
            "inciting_disruption",
            "stakes_consequence",
            "hook_payoff_thread_ids",
        ])
        copy_risk_checks.append("source_hook_payoff_matrix_clone")
    if "scene_goal_obstacle_cost_exit_gate" in pattern_names:
        transfer_axes.extend([
            "scene_engine_pattern",
            "micro_tension_density",
        ])
        required_difference_axes.extend([
            "scene_goal_sequence",
            "obstacle_tactics",
            "cost_pattern",
            "exit_state_route",
        ])
        copy_risk_checks.append("source_scene_beat_clone")
    if "revision_finding_patch_strategy_gate" in pattern_names:
        transfer_axes.append("revision_triage_discipline")
        required_difference_axes.append("patch_scope_ids")
        copy_risk_checks.append("source_revision_note_canon_leak")

    warnings: list[str] = []
    if not style_principles:
        warnings.append("missing_same_type_style_principles")
    if not source_voice_samples:
        warnings.append("missing_source_voice_samples")
    if not forbidden_source_elements:
        warnings.append("missing_forbidden_source_elements")
    voice_sample_tokens = sum(_estimate_context_tokens(item) for item in source_voice_samples)
    if voice_sample_tokens >= 1200:
        warnings.append("source_voice_samples_over_budget")

    return {
        "style_principle_count": len(style_principles),
        "source_voice_sample_count": len(source_voice_samples),
        "forbidden_source_element_count": len(forbidden_source_elements),
        "source_voice_estimated_tokens": voice_sample_tokens,
        "transfer_axes": _dedupe_ordered(transfer_axes),
        "required_difference_axes": _dedupe_ordered(required_difference_axes),
        "copy_risk_checks": _dedupe_ordered(copy_risk_checks),
        "warnings": warnings,
    }


def _append_inspired_independence_contract_section(
    *,
    lines: list[str],
    style_content: str,
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    audit = build_remix_inspired_independence_audit(
        style_content=style_content,
        source_pattern_pack=source_pattern_pack,
    )

    lines.append("")
    lines.append("Same-type independence contract:")
    lines.append(
        "- source_boundary_snapshot: "
        f"style_principles={audit['style_principle_count']}, "
        f"voice_samples={audit['source_voice_sample_count']}, "
        f"forbidden_elements={audit['forbidden_source_element_count']}, "
        f"voice_sample_tokens={audit['source_voice_estimated_tokens']}"
    )
    lines.append(f"- transferable_axes: {', '.join(audit['transfer_axes'][:10])}")
    lines.append(f"- required_difference_axes: {', '.join(audit['required_difference_axes'][:10])}")
    lines.append(f"- copy_risk_checks: {', '.join(audit['copy_risk_checks'][:10])}")
    if audit["warnings"]:
        lines.append(f"- independence_warnings: {', '.join(audit['warnings'])}")
    lines.append("- acceptance_rule: improve genre fit without maximizing source-author similarity or preserving source plot meaning")


def _append_inspired_transformation_audit_section(
    *,
    lines: list[str],
    source_pattern_pack: Optional[dict[str, Any]],
) -> None:
    """Render same-type creation gates that keep source inspiration out of canon."""
    if not isinstance(source_pattern_pack, dict):
        return

    mapping_targets = _as_note_list(source_pattern_pack.get("inspired_mapping_targets"))
    prompt_hints = _as_note_list(source_pattern_pack.get("inspired_prompt_hints"))
    transformation_hints = _as_note_list(source_pattern_pack.get("inspired_transformation_hints"))
    copy_risk_hints = _as_note_list(source_pattern_pack.get("inspired_copy_risk_hints"))
    if not any((mapping_targets, prompt_hints, transformation_hints, copy_risk_hints)):
        return

    lines.append("")
    lines.append("Inspired transformation audit:")
    if mapping_targets:
        lines.append(f"- required_remaps: {', '.join(mapping_targets[:8])}")
    if transformation_hints:
        lines.append(f"- transformation_rule: {_truncate(transformation_hints[0], 220)}")
    lines.append("- source_canon_boundary: source facts, names, organizations, events, and set pieces remain non-canon.")
    lines.append("- context_reference_policy: source-pattern references can justify craft choices, not story facts.")
    if prompt_hints:
        lines.append(f"- style_transfer_scope: {_truncate(prompt_hints[0], 220)}")
    if copy_risk_hints:
        lines.append(f"- copy_risk_gate: {_truncate(copy_risk_hints[0], 220)}")


def _source_pattern_names(source_pattern_pack: Optional[dict[str, Any]]) -> set[str]:
    if not isinstance(source_pattern_pack, dict):
        return set()

    names: set[str] = set()
    for pattern in _as_dict_list(source_pattern_pack.get("workflow_patterns")):
        name = _string_value(pattern.get("name"))
        if name:
            names.add(name)
    for pattern in _as_dict_list(source_pattern_pack.get("patterns")):
        name = _string_value(pattern.get("name"))
        if name:
            names.add(name)

    hint_to_name = {
        "lorebook_context_hints": "lorebook_context",
        "context_reference_hints": "context_reference",
        "world_state_tracking_hints": "world_state_tracking",
        "memory_snapshot_versioning_hints": "memory_snapshot_versioning",
        "author_note_layer_hints": "author_note_layer",
        "local_first_workspace_hints": "local_first_novel_workspace",
        "prompt_library_hints": "prompt_library",
        "story_bible_constitution_source_gate_hints": "story_bible_constitution_source_gate",
        "scene_outline_approval_status_gate_hints": "scene_outline_approval_status_gate",
        "pov_information_asymmetry_schedule_gate_hints": "pov_information_asymmetry_schedule_gate",
        "pacing_arc_polish_pass_gate_hints": "pacing_arc_polish_pass_gate",
        "style_guide_layering_hints": "style_guide_layering",
        "review_queue_staging_hints": "review_queue_staging",
        "entity_schema_custom_fields_hints": "entity_schema_custom_fields",
        "scene_level_generation_hints": "scene_level_generation",
        "content_ref_externalization_hints": "content_ref_externalization",
        "graph_healing_hints": "graph_healing",
        "contradiction_detection_hints": "contradiction_detection",
        "graph_branching_atomicity_hints": "graph_branching_atomicity",
        "query_lint_contract_hints": "query_lint_contract",
        "premature_ending_guard_hints": "premature_ending_guard",
        "layered_memory_model_hints": "layered_memory_model",
        "plot_dependency_graph_hints": "plot_dependency_graph",
        "plotgrid_scene_matrix_hints": "plotgrid_scene_matrix",
        "plotline_thread_tracking_hints": "plotline_thread_tracking",
        "narrative_time_age_trace_gate_hints": "narrative_time_age_trace_gate",
        "scene_status_dashboard_hints": "scene_status_dashboard",
        "gradual_reveal_control_hints": "gradual_reveal_control",
        "setup_payoff_tracking_hints": "setup_payoff_tracking",
        "scene_type_directing_hints": "scene_type_directing",
        "worldpkg_export_hints": "worldpkg_export",
        "alternate_timeline_branching_hints": "alternate_timeline_branching",
        "divergence_guidance_hints": "divergence_guidance",
        "context_pack_preview_hints": "context_pack_preview",
        "accepted_chapter_memory_hints": "accepted_chapter_memory",
        "critic_verifier_loop_hints": "critic_verifier_loop",
        "collapse_prevention_hints": "collapse_prevention",
        "trend_deconstruction_pipeline_hints": "trend_deconstruction_pipeline",
        "anti_ai_tone_polish_hints": "anti_ai_tone_polish",
        "preference_memory_hints": "preference_memory",
        "interrupted_resume_flow_hints": "interrupted_resume_flow",
        "auto_validation_rewrite_hints": "auto_validation_rewrite",
        "top_down_story_planning_hints": "top_down_story_planning",
        "plain_text_project_storage_hints": "plain_text_project_storage",
        "synopsis_cross_reference_hints": "synopsis_cross_reference",
        "snowflake_premise_expansion_hints": "snowflake_premise_expansion",
        "outliner_index_cards_hints": "outliner_index_cards",
        "narrative_strand_mapping_hints": "narrative_strand_mapping",
        "character_depth_interview_hints": "character_depth_interview",
        "mindmap_visual_planning_hints": "mindmap_visual_planning",
        "manuscript_export_formats_hints": "manuscript_export_formats",
        "human_synopsis_gate_hints": "human_synopsis_gate",
        "retrieval_guided_span_rewrite_hints": "retrieval_guided_span_rewrite",
        "runtime_artifact_trace_hints": "runtime_artifact_trace",
        "schema_validated_state_delta_hints": "schema_validated_state_delta",
        "recursive_adaptive_planning_hints": "recursive_adaptive_planning",
        "workflow_manuscript_compilation_hints": "workflow_manuscript_compilation",
        "writing_session_goal_tracking_hints": "writing_session_goal_tracking",
        "inspectable_run_workspace_hints": "inspectable_run_workspace",
        "craft_role_pipeline_hints": "craft_role_pipeline",
        "frontmatter_story_schema_hints": "frontmatter_story_schema",
        "continuity_bridge_window_hints": "continuity_bridge_window",
        "episode_range_rewrite_scope_hints": "episode_range_rewrite_scope",
        "voice_table_polish_axis_hints": "voice_table_polish_axis",
        "boring_opening_quality_gates_hints": "boring_opening_quality_gates",
        "beat_strand_framework_hints": "beat_strand_framework",
        "anti_hallucination_plan_check_hints": "anti_hallucination_plan_check",
        "backup_restore_checkpoint_hints": "backup_restore_checkpoint",
        "multi_level_review_trend_hints": "multi_level_review_trend",
        "editor_notes_feedback_loop_hints": "editor_notes_feedback_loop",
        "genre_parameterized_worldbuilding_hints": "genre_parameterized_worldbuilding",
        "prose_preflight_voice_calibration_hints": "prose_preflight_voice_calibration",
        "sourcebook_author_workbench_hints": "sourcebook_author_workbench",
        "semantic_long_context_search_hints": "semantic_long_context_search",
        "contradiction_taxonomy_checker_hints": "contradiction_taxonomy_checker",
        "parallel_agent_chapter_pipeline_hints": "parallel_agent_chapter_pipeline",
        "cross_chapter_redundancy_audit_hints": "cross_chapter_redundancy_audit",
        "humanization_stylometry_levers_hints": "humanization_stylometry_levers",
        "author_control_boundary_hints": "author_control_boundary",
        "research_taxonomy_story_map_hints": "research_taxonomy_story_map",
        "novel_to_multimodal_pipeline_hints": "novel_to_multimodal_pipeline",
        "entity_to_visual_asset_pipeline_hints": "entity_to_visual_asset_pipeline",
        "agentic_book_planner_pipeline_hints": "agentic_book_planner_pipeline",
        "rag_synopsis_spine_hints": "rag_synopsis_spine",
        "anti_repetition_prompt_rules_hints": "anti_repetition_prompt_rules",
        "prompt_recipe_experiment_grid_hints": "prompt_recipe_experiment_grid",
        "append_only_generation_review_log_hints": "append_only_generation_review_log",
        "narrative_arc_template_control_hints": "narrative_arc_template_control",
        "nrd_task_tree_pipeline_hints": "nrd_task_tree_pipeline",
        "sampling_parameter_quality_sweep_hints": "sampling_parameter_quality_sweep",
        "story_structure_rag_planning_hints": "story_structure_rag_planning",
        "story_contract_commit_chain_hints": "story_contract_commit_chain",
        "fact_snapshot_delta_gate_hints": "fact_snapshot_delta_gate",
        "projection_sync_observability_hints": "projection_sync_observability",
        "foreshadowing_debt_budget_hints": "foreshadowing_debt_budget",
        "reader_retention_review_gate_hints": "reader_retention_review_gate",
        "draft_stage_revision_ladder_hints": "draft_stage_revision_ladder",
        "rolling_summary_context_trim_hints": "rolling_summary_context_trim",
        "pairwise_story_comparison_ranking_hints": "pairwise_story_comparison_ranking",
        "multidimensional_quality_rubric_hints": "multidimensional_quality_rubric",
        "story_theory_beat_evaluation_hints": "story_theory_beat_evaluation",
        "constraint_specificity_creativity_benchmark_hints": "constraint_specificity_creativity_benchmark",
        "style_axis_diversity_fingerprint_hints": "style_axis_diversity_fingerprint",
        "event_outline_history_compression_hints": "event_outline_history_compression",
        "agentic_story_world_simulation_hints": "agentic_story_world_simulation",
        "reader_rating_signal_model_hints": "reader_rating_signal_model",
        "review_spoiler_sentiment_corpus_hints": "review_spoiler_sentiment_corpus",
        "beta_reader_archetype_panel_hints": "beta_reader_archetype_panel",
        "comp_title_market_positioning_hints": "comp_title_market_positioning",
        "local_reader_experience_editor_hints": "local_reader_experience_editor",
        "delivery_manuscript_assembly_hints": "delivery_manuscript_assembly",
        "export_format_fidelity_audit_hints": "export_format_fidelity_audit",
        "preview_toc_packaging_hints": "preview_toc_packaging",
        "cover_kdp_metadata_boundary_hints": "cover_kdp_metadata_boundary",
        "branching_choice_graph_hints": "branching_choice_graph",
        "node_dialogue_state_machine_hints": "node_dialogue_state_machine",
        "passage_link_navigation_map_hints": "passage_link_navigation_map",
        "choice_stats_consequence_gate_hints": "choice_stats_consequence_gate",
        "source_text_fingerprint_gate_hints": "source_text_fingerprint_gate",
        "fuzzy_phrase_similarity_gate_hints": "fuzzy_phrase_similarity_gate",
        "diff_span_copy_review_hints": "diff_span_copy_review",
        "minhash_lsh_near_duplicate_gate_hints": "minhash_lsh_near_duplicate_gate",
        "simhash_hamming_similarity_gate_hints": "simhash_hamming_similarity_gate",
        "semantic_duplicate_cluster_gate_hints": "semantic_duplicate_cluster_gate",
        "embedding_similarity_independence_gate_hints": "embedding_similarity_independence_gate",
        "corpus_leakage_dedup_review_gate_hints": "corpus_leakage_dedup_review_gate",
        "character_quote_attribution_map_hints": "character_quote_attribution_map",
        "readability_pacing_metric_gate_hints": "readability_pacing_metric_gate",
        "prose_lint_style_rule_gate_hints": "prose_lint_style_rule_gate",
        "grammar_spelling_copyedit_gate_hints": "grammar_spelling_copyedit_gate",
        "copyedit_diagnostic_triage_queue_hints": "copyedit_diagnostic_triage_queue",
        "lexical_diversity_voice_audit_hints": "lexical_diversity_voice_audit",
        "keyphrase_motif_extraction_hints": "keyphrase_motif_extraction",
        "chinese_segmentation_keyword_gate_hints": "chinese_segmentation_keyword_gate",
        "chinese_ner_alias_consistency_gate_hints": "chinese_ner_alias_consistency_gate",
        "chinese_text_normalization_gate_hints": "chinese_text_normalization_gate",
        "chinese_error_correction_review_gate_hints": "chinese_error_correction_review_gate",
        "source_format_import_manifest_hints": "source_format_import_manifest",
        "pdf_layout_text_extraction_gate_hints": "pdf_layout_text_extraction_gate",
        "ocr_scanned_page_import_gate_hints": "ocr_scanned_page_import_gate",
        "document_partition_chapter_detection_gate_hints": "document_partition_chapter_detection_gate",
        "import_provenance_checksum_gate_hints": "import_provenance_checksum_gate",
        "agentic_editorial_pipeline_gate_hints": "agentic_editorial_pipeline_gate",
        "chapter_state_archive_ladder_hints": "chapter_state_archive_ladder",
        "section_metadata_traceability_gate_hints": "section_metadata_traceability_gate",
        "ai_prose_fingerprint_cluster_gate_hints": "ai_prose_fingerprint_cluster_gate",
        "author_candidate_canon_confirmation_gate_hints": "author_candidate_canon_confirmation_gate",
        "progressive_spoiler_context_window_gate_hints": "progressive_spoiler_context_window_gate",
        "chapter_control_card_writeback_gate_hints": "chapter_control_card_writeback_gate",
        "trace_replay_revision_workspace_gate_hints": "trace_replay_revision_workspace_gate",
        "relationship_graph_global_replace_gate_hints": "relationship_graph_global_replace_gate",
        "bookrun_audit_trail_gate_hints": "bookrun_audit_trail_gate",
        "provider_budget_smoke_gate_hints": "provider_budget_smoke_gate",
        "sidecar_memory_profile_boundary_hints": "sidecar_memory_profile_boundary",
        "automatic_director_checkpoint_chain_hints": "automatic_director_checkpoint_chain",
        "director_stage_checkpoint_gate_hints": "director_stage_checkpoint_gate",
        "role_asset_quality_review_gate_hints": "role_asset_quality_review_gate",
        "inspectable_memory_workspace_gate_hints": "inspectable_memory_workspace_gate",
        "memory_aware_chapter_workspace_hints": "memory_aware_chapter_workspace",
        "semantic_context_consistency_gate_hints": "semantic_context_consistency_gate",
        "multi_thread_knowledge_timeline_gate_hints": "multi_thread_knowledge_timeline_gate",
        "outline_checkpoint_milestone_gate_hints": "outline_checkpoint_milestone_gate",
        "language_localization_style_profile_gate_hints": "language_localization_style_profile_gate",
        "progressive_disclosure_skill_protocol_gate_hints": "progressive_disclosure_skill_protocol_gate",
        "anti_slop_rulepack_triage_gate_hints": "anti_slop_rulepack_triage_gate",
        "user_modifier_project_blueprint_gate_hints": "user_modifier_project_blueprint_gate",
        "portable_canon_skill_runtime_gate_hints": "portable_canon_skill_runtime_gate",
        "staged_outline_chunk_window_gate_hints": "staged_outline_chunk_window_gate",
        "wiki_canon_graph_lint_gate_hints": "wiki_canon_graph_lint_gate",
        "plan_draft_log_verify_loop_gate_hints": "plan_draft_log_verify_loop_gate",
        "mcp_scene_index_revision_boundary_hints": "mcp_scene_index_revision_boundary",
        "verbalized_sampling_diversity_wiki_gate_hints": "verbalized_sampling_diversity_wiki_gate",
        "epub_structure_validation_gate_hints": "epub_structure_validation_gate",
        "ebook_accessibility_audit_gate_hints": "ebook_accessibility_audit_gate",
        "front_back_matter_metadata_gate_hints": "front_back_matter_metadata_gate",
        "toc_navigation_consistency_gate_hints": "toc_navigation_consistency_gate",
        "literary_event_entity_annotation_gate_hints": "literary_event_entity_annotation_gate",
        "narrative_event_evolution_graph_gate_hints": "narrative_event_evolution_graph_gate",
        "sentiment_arc_emotion_trajectory_gate_hints": "sentiment_arc_emotion_trajectory_gate",
        "cross_context_coreference_gate_hints": "cross_context_coreference_gate",
        "character_interaction_network_gate_hints": "character_interaction_network_gate",
        "semantic_chunk_boundary_map_hints": "semantic_chunk_boundary_map",
        "chapter_summary_anchor_gate_hints": "chapter_summary_anchor_gate",
        "topic_drift_map_hints": "topic_drift_map",
        "context_faithfulness_eval_gate_hints": "context_faithfulness_eval_gate",
        "retrieval_trace_observability_gate_hints": "retrieval_trace_observability_gate",
        "prompt_regression_eval_suite_hints": "prompt_regression_eval_suite",
        "trope_inventory_similarity_gate_hints": "trope_inventory_similarity_gate",
        "trope_graph_expectation_map_hints": "trope_graph_expectation_map",
        "trope_density_novelty_budget_hints": "trope_density_novelty_budget",
        "trope_source_boundary_review_hints": "trope_source_boundary_review",
        "source_license_detection_gate_hints": "source_license_detection_gate",
        "spdx_reuse_compliance_gate_hints": "spdx_reuse_compliance_gate",
        "public_domain_corpus_boundary_hints": "public_domain_corpus_boundary",
        "attribution_derivative_work_gate_hints": "attribution_derivative_work_gate",
        "source_entity_redaction_gate_hints": "source_entity_redaction_gate",
        "custom_entity_label_inventory_hints": "custom_entity_label_inventory",
        "placeholder_alias_consistency_map_hints": "placeholder_alias_consistency_map",
        "proper_noun_leakage_review_hints": "proper_noun_leakage_review",
        "truth_file_write_next_state_update_gate_hints": "truth_file_write_next_state_update_gate",
        "universal_novel_mode_contract_gate_hints": "universal_novel_mode_contract_gate",
        "portable_story_project_structure_gate_hints": "portable_story_project_structure_gate",
        "chapter_contract_scene_beat_gate_hints": "chapter_contract_scene_beat_gate",
        "reader_promise_micro_payoff_gate_hints": "reader_promise_micro_payoff_gate",
        "revision_order_natural_prose_gate_hints": "revision_order_natural_prose_gate",
        "reader_pull_fresh_reader_gate_hints": "reader_pull_fresh_reader_gate",
        "progress_report_continuity_writeback_gate_hints": "progress_report_continuity_writeback_gate",
        "post_draft_review_checklist_gate_hints": "post_draft_review_checklist_gate",
        "canonkit_local_canon_drift_context_pack_gate_hints": "canonkit_local_canon_drift_context_pack_gate",
        "genre_promise_contract_matrix_gate_hints": "genre_promise_contract_matrix_gate",
        "subgenre_specific_ledger_gate_hints": "subgenre_specific_ledger_gate",
        "five_question_intake_story_promise_gate_hints": "five_question_intake_story_promise_gate",
        "universal_export_clean_manuscript_gate_hints": "universal_export_clean_manuscript_gate",
        "minimal_rollback_repair_scope_gate_hints": "minimal_rollback_repair_scope_gate",
        "local_first_provider_boundary_authoring_gate_hints": "local_first_provider_boundary_authoring_gate",
        "suggestion_card_nonoverwrite_revision_gate_hints": "suggestion_card_nonoverwrite_revision_gate",
        "book_view_import_export_manifest_gate_hints": "book_view_import_export_manifest_gate",
        "versioned_scene_fact_review_pipeline_gate_hints": "versioned_scene_fact_review_pipeline_gate",
        "novelforge_version_safe_human_review_gate_hints": "novelforge_version_safe_human_review_gate",
        "distilled_novel_toolbox_platform_compliance_gate_hints": "distilled_novel_toolbox_platform_compliance_gate",
        "distilled_novel_toolbox_human_polish_boundary_gate_hints": "distilled_novel_toolbox_human_polish_boundary_gate",
        "novel_studio_graph_memory_continuity_gate_hints": "novel_studio_graph_memory_continuity_gate",
        "novel_studio_accepted_chapter_writeback_gate_hints": "novel_studio_accepted_chapter_writeback_gate",
        "seed_to_bible_foundation_loop_gate_hints": "seed_to_bible_foundation_loop_gate",
        "layered_story_bible_artifact_contract_gate_hints": "layered_story_bible_artifact_contract_gate",
        "premise_structure_hook_payoff_gate_hints": "premise_structure_hook_payoff_gate",
        "scene_goal_obstacle_cost_exit_gate_hints": "scene_goal_obstacle_cost_exit_gate",
        "revision_finding_patch_strategy_gate_hints": "revision_finding_patch_strategy_gate",
    }
    for hint_key, pattern_name in hint_to_name.items():
        if _as_note_list(source_pattern_pack.get(hint_key)):
            names.add(pattern_name)

    return names


def _activated_context_sections(
    *,
    bible: dict[str, Any],
    plan: Optional[dict[str, Any]],
) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []

    world_rules = bible.get("world_rules")
    if isinstance(world_rules, dict) and world_rules:
        sections.append(("world_rules", f"{len(world_rules)} rules"))

    for label, value, unit in (
        ("hard_constraints", bible.get("hard_constraints"), "constraints"),
        ("character_cards", bible.get("character_cards"), "cards"),
        ("organizations", bible.get("organizations"), "entries"),
        ("conflicts", bible.get("conflicts"), "arcs"),
        ("story_arcs", bible.get("story_arcs"), "arcs"),
    ):
        count = len(_as_dict_list(value))
        if count:
            sections.append((label, f"{count} {unit}"))

    timeline = _as_dict_list(bible.get("timeline"))
    latest_machine = _latest_chapter_analysis_items(timeline, max_items=1)
    if latest_machine:
        chapter = latest_machine[0].get("chapter_number") or latest_machine[0].get("last_chapter_number")
        suffix = f" through chapter {chapter}" if chapter not in (None, "") else " present"
        sections.append(("latest_machine_timeline", suffix.strip()))
    elif timeline:
        sections.append(("timeline", f"{len(timeline)} anchors"))

    chapter_change_packages = _chapter_analysis_packages(bible.get("chapter_change_packages"))
    if chapter_change_packages:
        chapter_numbers = [
            _int_or_none(package.get("chapter_number"))
            for package in _sort_by_chapter_asc(chapter_change_packages)
        ]
        chapter_numbers = [number for number in chapter_numbers if number is not None]
        if chapter_numbers:
            first_chapter = chapter_numbers[0]
            last_chapter = chapter_numbers[-1]
            chapter_range = str(first_chapter) if first_chapter == last_chapter else f"{first_chapter}-{last_chapter}"
            sections.append(("recent_change_packages", f"{len(chapter_change_packages)} packages covering chapter {chapter_range}"))
        else:
            sections.append(("recent_change_packages", f"{len(chapter_change_packages)} packages"))

    open_hooks = _status_items(_as_dict_list(bible.get("foreshadows")), done=False, max_items=99)
    if open_hooks:
        sections.append(("open_hooks", f"{len(open_hooks)} unresolved hooks"))

    if plan:
        pending_beats = _status_items(_as_dict_list(plan.get("beats")), done=False, max_items=99)
        pending_hooks = _status_items(_as_dict_list(plan.get("priority_hooks")), done=False, max_items=99)
        guardrails = _as_dict_list(plan.get("guardrails"))
        if pending_beats:
            sections.append(("pending_plan_beats", f"{len(pending_beats)} beats"))
        if pending_hooks:
            sections.append(("pending_priority_hooks", f"{len(pending_hooks)} hooks"))
        if guardrails:
            sections.append(("plan_guardrails", f"{len(guardrails)} guardrails"))

    style_signature = bible.get("style_signature")
    if isinstance(style_signature, dict) and style_signature:
        sections.append(("style_signature", f"{len(style_signature)} fields"))

    return sections


def _append_inspired_style_section(
    *,
    lines: list[str],
    title: str,
    style_content: str,
    heading: str,
    max_items: int,
) -> None:
    section = _extract_heading_section(style_content, heading=heading)
    if not section:
        return

    items: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        items.append(_truncate(line, 260))
        if len(items) >= max_items:
            break

    if not items:
        return

    lines.append("")
    lines.append(f"{title}:")
    for item in items:
        lines.append(f"- {item}")


def _heading_items(style_content: str, *, heading: str, max_items: int) -> list[str]:
    section = _extract_heading_section(style_content, heading=heading)
    if not section:
        return []

    items: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        items.append(_truncate(line, 260))
        if len(items) >= max_items:
            break
    return items


def _extract_heading_section(style_content: str, *, heading: str) -> str:
    if heading not in style_content:
        return ""
    _, section = style_content.split(heading, 1)
    next_heading = section.find("【")
    if next_heading >= 0:
        section = section[:next_heading]
    return section.strip()


def _chapter_package_label(package: dict[str, Any]) -> str:
    chapter_number = package.get("chapter_number")
    title = _string_value(package.get("chapter_title"))
    if chapter_number not in (None, "") and title:
        return f"Chapter {chapter_number}: {title}"
    if chapter_number not in (None, ""):
        return f"Chapter {chapter_number}"
    return title or "Recent chapter"


def _append_dict_section(
    *,
    lines: list[str],
    title: str,
    items: Any,
    preferred_keys: tuple[str, ...],
    max_items: int,
) -> None:
    normalized_items = _as_dict_list(items)
    if not normalized_items:
        return

    lines.append("")
    lines.append(f"{title}:")
    for item in normalized_items[:max_items]:
        lines.append(f"- {_item_to_text(item, preferred_keys=preferred_keys)}")


def _append_character_update_section(
    *,
    lines: list[str],
    cards: list[dict[str, Any]],
    max_items: int,
) -> None:
    updates: list[dict[str, Any]] = []
    for card in cards:
        name = _string_value(card.get("name") or card.get("character_name"))
        for update in _as_dict_list(card.get("continuation_updates")):
            merged = {**update, "character_name": name}
            updates.append(merged)

    updates = _sort_by_chapter_desc(updates)[:max_items]
    if not updates:
        return

    lines.append("")
    lines.append("Latest character continuation updates:")
    for update in updates:
        label = _string_value(update.get("character_name")) or "Unknown character"
        chapter_number = update.get("chapter_number")
        if chapter_number not in (None, ""):
            label = f"{label} @ Chapter {chapter_number}"
        parts = [label]
        for key in ("state_after", "key_event", "psychological_change", "chapter_title"):
            value = _string_value(update.get(key))
            if value:
                parts.append(f"{key}: {value}")
        lines.append(f"- {_truncate(' | '.join(parts), 260)}")


def _append_style_signature_section(
    *,
    lines: list[str],
    style_signature: Any,
) -> None:
    if not isinstance(style_signature, dict) or not style_signature:
        return

    lines.append("")
    lines.append("Style signature to preserve:")
    for key, value in list(style_signature.items())[:12]:
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
        else:
            rendered = str(value)
        if rendered.strip():
            lines.append(f"- {key}: {_truncate(rendered, 220)}")


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _as_note_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    notes: list[str] = []
    for item in value:
        text = _string_value(item)
        if text:
            notes.append(text)
    return notes


def _has_any_package_value(package: dict[str, Any], keys: tuple[str, ...]) -> bool:
    for key in keys:
        value = package.get(key)
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, (list, dict)) and bool(value):
            return True
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
    return False


def _dedupe_ordered(items: list[str]) -> list[str]:
    deduped: list[str] = []
    for item in items:
        _append_unique(deduped, item)
    return deduped


def _item_to_text(item: dict[str, Any], *, preferred_keys: tuple[str, ...]) -> str:
    label = _first_text(item, preferred_keys)
    status = _string_value(item.get("status"))
    chapter = item.get("chapter_number") or item.get("last_chapter_number")
    suffix_parts = []
    if status:
        suffix_parts.append(f"status: {status}")
    if chapter not in (None, ""):
        suffix_parts.append(f"chapter: {chapter}")
    if suffix_parts:
        label = f"{label} ({', '.join(suffix_parts)})"
    return _truncate(label, 260)


def _first_text(item: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = _string_value(item.get(key))
        if value:
            return value
    compact = json.dumps(item, ensure_ascii=False, sort_keys=True)
    return compact[:240]


def _direct_first_text(item: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)
    return ""


def _manual_items(items: list[dict[str, Any]], *, max_items: int) -> list[dict[str, Any]]:
    manual = [item for item in items if not _is_machine_continuation_source(item.get("source"))]
    return _sort_by_chapter_desc(manual)[:max_items]


def _latest_chapter_analysis_items(items: list[dict[str, Any]], *, max_items: int) -> list[dict[str, Any]]:
    machine = [item for item in items if _is_machine_continuation_source(item.get("source"))]
    return _sort_by_chapter_desc(machine)[:max_items]


def _is_machine_continuation_source(value: Any) -> bool:
    return _string_value(value) in {"chapter_analysis", "chapter_generation"}


def _status_items(items: list[dict[str, Any]], *, done: bool, max_items: int) -> list[dict[str, Any]]:
    filtered = [item for item in items if _is_done_status(item.get("status")) is done]
    return _sort_by_chapter_desc(filtered)[:max_items]


def _is_done_status(value: Any) -> bool:
    normalized = _string_value(value).strip().lower()
    return normalized in {"done", "resolved", "paid", "closed", "complete", "completed", "已完成", "已回收", "回收"}


def _sort_by_chapter_desc(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=_chapter_sort_key, reverse=True)


def _sort_by_chapter_asc(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=_chapter_sort_key)


def _chapter_sort_key(item: dict[str, Any]) -> tuple[int, int]:
    chapter = item.get("chapter_number") or item.get("last_chapter_number") or 0
    try:
        chapter_number = int(chapter)
    except (TypeError, ValueError):
        chapter_number = 0
    source_rank = 1 if _string_value(item.get("source")) == "chapter_analysis" else 0
    return chapter_number, source_rank


def _int_or_none(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _truncate(value: str, limit: int) -> str:
    text = _string_value(value)
    return text if len(text) <= limit else text[:limit].rstrip() + "..."


def _estimate_context_tokens(text: str) -> int:
    """Estimate mixed Chinese/English prompt tokens without provider calls."""
    compact = re.sub(r"\s+", "", text or "")
    if not compact:
        return 0

    ascii_word_count = len(re.findall(r"[A-Za-z0-9_]+", text or ""))
    cjk_char_count = len(re.findall(r"[\u4e00-\u9fff]", text or ""))
    other_char_count = max(0, len(compact) - cjk_char_count)
    return max(1, ascii_word_count + ((cjk_char_count + 1) // 2) + ((other_char_count + 3) // 4))


def _context_budget_risk(estimated_tokens: int) -> str:
    if estimated_tokens >= 12000:
        return "high"
    if estimated_tokens >= 6000:
        return "medium"
    return "low"


book_remix_context_service = BookRemixContextService()
