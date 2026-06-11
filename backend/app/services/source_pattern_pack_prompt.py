"""Render source-discovery pattern packs into compact prompt guidance."""

from __future__ import annotations

from typing import Any, Optional


def render_source_pattern_pack_digest(
    source_pattern_pack: Optional[dict[str, Any]],
    *,
    empty_message: str = "(no public source pattern pack; use only local project canon.)",
    include_inspired_guidance: bool = True,
) -> str:
    """Convert the latest source-discovery pattern pack into prompt-safe bullets."""
    if not source_pattern_pack:
        return empty_message

    lines: list[str] = []
    workflow_patterns = _as_dict_list(source_pattern_pack.get("workflow_patterns"))
    if workflow_patterns:
        lines.append("- workflow_patterns:")
        for pattern in workflow_patterns[:8]:
            name = str(pattern.get("name") or "").strip()
            if not name:
                continue
            count = pattern.get("candidate_count") or 0
            top_source_url = str(pattern.get("top_source_url") or "").strip()
            posture_hint = str(pattern.get("posture_hint") or "").strip()
            risk_flags = _as_note_list(pattern.get("risk_flags"))
            trust_flags = _as_note_list(pattern.get("trust_flags"))
            posture_text = f"; posture_hint: {posture_hint}" if posture_hint else ""
            risk_text = f"; risk_flags: {', '.join(risk_flags[:5])}" if risk_flags else ""
            trust_text = f"; trust_flags: {', '.join(trust_flags[:5])}" if trust_flags else ""
            source_text = f"; top_source: {top_source_url}" if top_source_url else ""
            lines.append(f"  - {name} (candidates: {count}{source_text}{posture_text}{risk_text}{trust_text})")

    bible_targets = _as_note_list(source_pattern_pack.get("bible_enrichment_targets"))
    if bible_targets:
        lines.append("- bible_enrichment_targets: " + ", ".join(bible_targets[:12]))

    whole_book_targets = _as_note_list(source_pattern_pack.get("whole_book_analysis_targets"))
    if whole_book_targets:
        lines.append("- whole_book_analysis_targets: " + ", ".join(whole_book_targets[:14]))

    continuation_hints = _as_note_list(source_pattern_pack.get("continuation_prompt_hints"))
    if continuation_hints:
        lines.append("- continuation_prompt_hints:")
        for hint in continuation_hints[:8]:
            lines.append(f"  - {hint}")

    continuation_state_hints = _as_note_list(source_pattern_pack.get("continuation_state_hints"))
    if continuation_state_hints:
        lines.append("- continuation_state_hints:")
        for hint in continuation_state_hints[:8]:
            lines.append(f"  - {hint}")

    style_hints = _as_note_list(source_pattern_pack.get("style_signature_hints"))
    if style_hints:
        lines.append("- style_signature_hints:")
        for hint in style_hints[:6]:
            lines.append(f"  - {hint}")

    style_fidelity_hints = _as_note_list(source_pattern_pack.get("style_fidelity_hints"))
    if style_fidelity_hints:
        lines.append("- style_fidelity_hints:")
        for hint in style_fidelity_hints[:6]:
            lines.append(f"  - {hint}")

    structured_generation_hints = _as_note_list(source_pattern_pack.get("structured_generation_hints"))
    if structured_generation_hints:
        lines.append("- structured_generation_hints:")
        for hint in structured_generation_hints[:6]:
            lines.append(f"  - {hint}")

    card_workbench_hints = _as_note_list(source_pattern_pack.get("card_workbench_hints"))
    if card_workbench_hints:
        lines.append("- card_workbench_hints:")
        for hint in card_workbench_hints[:6]:
            lines.append(f"  - {hint}")

    context_reference_hints = _as_note_list(source_pattern_pack.get("context_reference_hints"))
    if context_reference_hints:
        lines.append("- context_reference_hints:")
        for hint in context_reference_hints[:6]:
            lines.append(f"  - {hint}")

    scene_asset_pipeline_hints = _as_note_list(source_pattern_pack.get("scene_asset_pipeline_hints"))
    if scene_asset_pipeline_hints:
        lines.append("- scene_asset_pipeline_hints:")
        for hint in scene_asset_pipeline_hints[:6]:
            lines.append(f"  - {hint}")

    quality_score_loop_hints = _as_note_list(source_pattern_pack.get("quality_score_loop_hints"))
    if quality_score_loop_hints:
        lines.append("- quality_score_loop_hints:")
        for hint in quality_score_loop_hints[:6]:
            lines.append(f"  - {hint}")

    voice_fingerprint_hints = _as_note_list(source_pattern_pack.get("voice_fingerprint_hints"))
    if voice_fingerprint_hints:
        lines.append("- voice_fingerprint_hints:")
        for hint in voice_fingerprint_hints[:6]:
            lines.append(f"  - {hint}")

    anti_slop_audit_hints = _as_note_list(source_pattern_pack.get("anti_slop_audit_hints"))
    if anti_slop_audit_hints:
        lines.append("- anti_slop_audit_hints:")
        for hint in anti_slop_audit_hints[:6]:
            lines.append(f"  - {hint}")

    publication_pipeline_hints = _as_note_list(source_pattern_pack.get("publication_pipeline_hints"))
    if publication_pipeline_hints:
        lines.append("- publication_pipeline_hints:")
        for hint in publication_pipeline_hints[:6]:
            lines.append(f"  - {hint}")

    lorebook_context_hints = _as_note_list(source_pattern_pack.get("lorebook_context_hints"))
    if lorebook_context_hints:
        lines.append("- lorebook_context_hints:")
        for hint in lorebook_context_hints[:6]:
            lines.append(f"  - {hint}")

    author_note_layer_hints = _as_note_list(source_pattern_pack.get("author_note_layer_hints"))
    if author_note_layer_hints:
        lines.append("- author_note_layer_hints:")
        for hint in author_note_layer_hints[:6]:
            lines.append(f"  - {hint}")

    world_state_tracking_hints = _as_note_list(source_pattern_pack.get("world_state_tracking_hints"))
    if world_state_tracking_hints:
        lines.append("- world_state_tracking_hints:")
        for hint in world_state_tracking_hints[:6]:
            lines.append(f"  - {hint}")

    memory_snapshot_versioning_hints = _as_note_list(source_pattern_pack.get("memory_snapshot_versioning_hints"))
    if memory_snapshot_versioning_hints:
        lines.append("- memory_snapshot_versioning_hints:")
        for hint in memory_snapshot_versioning_hints[:6]:
            lines.append(f"  - {hint}")

    local_first_workspace_hints = _as_note_list(source_pattern_pack.get("local_first_workspace_hints"))
    if local_first_workspace_hints:
        lines.append("- local_first_workspace_hints:")
        for hint in local_first_workspace_hints[:6]:
            lines.append(f"  - {hint}")

    prompt_library_hints = _as_note_list(source_pattern_pack.get("prompt_library_hints"))
    if prompt_library_hints:
        lines.append("- prompt_library_hints:")
        for hint in prompt_library_hints[:6]:
            lines.append(f"  - {hint}")

    mode_contract_generation_gate_hints = _as_note_list(source_pattern_pack.get("mode_contract_generation_gate_hints"))
    if mode_contract_generation_gate_hints:
        lines.append("- mode_contract_generation_gate_hints:")
        for hint in mode_contract_generation_gate_hints[:6]:
            lines.append(f"  - {hint}")

    source_study_method_bank_isolation_gate_hints = _as_note_list(source_pattern_pack.get("source_study_method_bank_isolation_gate_hints"))
    if source_study_method_bank_isolation_gate_hints:
        lines.append("- source_study_method_bank_isolation_gate_hints:")
        for hint in source_study_method_bank_isolation_gate_hints[:6]:
            lines.append(f"  - {hint}")

    style_guide_layering_hints = _as_note_list(source_pattern_pack.get("style_guide_layering_hints"))
    if style_guide_layering_hints:
        lines.append("- style_guide_layering_hints:")
        for hint in style_guide_layering_hints[:6]:
            lines.append(f"  - {hint}")

    review_queue_staging_hints = _as_note_list(source_pattern_pack.get("review_queue_staging_hints"))
    if review_queue_staging_hints:
        lines.append("- review_queue_staging_hints:")
        for hint in review_queue_staging_hints[:6]:
            lines.append(f"  - {hint}")

    entity_schema_custom_fields_hints = _as_note_list(source_pattern_pack.get("entity_schema_custom_fields_hints"))
    if entity_schema_custom_fields_hints:
        lines.append("- entity_schema_custom_fields_hints:")
        for hint in entity_schema_custom_fields_hints[:6]:
            lines.append(f"  - {hint}")

    scene_level_generation_hints = _as_note_list(source_pattern_pack.get("scene_level_generation_hints"))
    if scene_level_generation_hints:
        lines.append("- scene_level_generation_hints:")
        for hint in scene_level_generation_hints[:6]:
            lines.append(f"  - {hint}")

    content_ref_externalization_hints = _as_note_list(source_pattern_pack.get("content_ref_externalization_hints"))
    if content_ref_externalization_hints:
        lines.append("- content_ref_externalization_hints:")
        for hint in content_ref_externalization_hints[:6]:
            lines.append(f"  - {hint}")

    graph_healing_hints = _as_note_list(source_pattern_pack.get("graph_healing_hints"))
    if graph_healing_hints:
        lines.append("- graph_healing_hints:")
        for hint in graph_healing_hints[:6]:
            lines.append(f"  - {hint}")

    contradiction_detection_hints = _as_note_list(source_pattern_pack.get("contradiction_detection_hints"))
    if contradiction_detection_hints:
        lines.append("- contradiction_detection_hints:")
        for hint in contradiction_detection_hints[:6]:
            lines.append(f"  - {hint}")

    graph_branching_atomicity_hints = _as_note_list(source_pattern_pack.get("graph_branching_atomicity_hints"))
    if graph_branching_atomicity_hints:
        lines.append("- graph_branching_atomicity_hints:")
        for hint in graph_branching_atomicity_hints[:6]:
            lines.append(f"  - {hint}")

    query_lint_contract_hints = _as_note_list(source_pattern_pack.get("query_lint_contract_hints"))
    if query_lint_contract_hints:
        lines.append("- query_lint_contract_hints:")
        for hint in query_lint_contract_hints[:6]:
            lines.append(f"  - {hint}")

    for key in (
        "premature_ending_guard_hints",
        "layered_memory_model_hints",
        "plot_dependency_graph_hints",
        "plotgrid_scene_matrix_hints",
        "plotline_thread_tracking_hints",
        "scene_status_dashboard_hints",
        "gradual_reveal_control_hints",
        "setup_payoff_tracking_hints",
        "scene_type_directing_hints",
        "worldpkg_export_hints",
        "alternate_timeline_branching_hints",
        "divergence_guidance_hints",
        "context_pack_preview_hints",
        "accepted_chapter_memory_hints",
        "critic_verifier_loop_hints",
        "collapse_prevention_hints",
        "trend_deconstruction_pipeline_hints",
        "anti_ai_tone_polish_hints",
        "preference_memory_hints",
        "interrupted_resume_flow_hints",
        "auto_validation_rewrite_hints",
        "top_down_story_planning_hints",
        "plain_text_project_storage_hints",
        "synopsis_cross_reference_hints",
        "snowflake_premise_expansion_hints",
        "outliner_index_cards_hints",
        "narrative_strand_mapping_hints",
        "character_depth_interview_hints",
        "mindmap_visual_planning_hints",
        "manuscript_export_formats_hints",
        "human_synopsis_gate_hints",
        "retrieval_guided_span_rewrite_hints",
        "runtime_artifact_trace_hints",
        "schema_validated_state_delta_hints",
        "recursive_adaptive_planning_hints",
        "workflow_manuscript_compilation_hints",
        "writing_session_goal_tracking_hints",
        "inspectable_run_workspace_hints",
        "craft_role_pipeline_hints",
        "frontmatter_story_schema_hints",
        "continuity_bridge_window_hints",
        "episode_range_rewrite_scope_hints",
        "voice_table_polish_axis_hints",
        "boring_opening_quality_gates_hints",
        "beat_strand_framework_hints",
        "anti_hallucination_plan_check_hints",
        "backup_restore_checkpoint_hints",
        "multi_level_review_trend_hints",
        "editor_notes_feedback_loop_hints",
        "genre_parameterized_worldbuilding_hints",
        "prose_preflight_voice_calibration_hints",
        "sourcebook_author_workbench_hints",
        "semantic_long_context_search_hints",
        "contradiction_taxonomy_checker_hints",
        "parallel_agent_chapter_pipeline_hints",
        "cross_chapter_redundancy_audit_hints",
        "humanization_stylometry_levers_hints",
        "author_control_boundary_hints",
        "research_taxonomy_story_map_hints",
        "novel_to_multimodal_pipeline_hints",
        "entity_to_visual_asset_pipeline_hints",
        "agentic_book_planner_pipeline_hints",
        "rag_synopsis_spine_hints",
        "anti_repetition_prompt_rules_hints",
        "prompt_recipe_experiment_grid_hints",
        "append_only_generation_review_log_hints",
        "narrative_arc_template_control_hints",
        "nrd_task_tree_pipeline_hints",
        "sampling_parameter_quality_sweep_hints",
        "story_structure_rag_planning_hints",
        "story_contract_commit_chain_hints",
        "fact_snapshot_delta_gate_hints",
        "projection_sync_observability_hints",
        "foreshadowing_debt_budget_hints",
        "reader_retention_review_gate_hints",
        "serial_reader_reward_contract_gate_hints",
        "draft_stage_revision_ladder_hints",
        "rolling_summary_context_trim_hints",
        "pairwise_story_comparison_ranking_hints",
        "multidimensional_quality_rubric_hints",
        "story_theory_beat_evaluation_hints",
        "constraint_specificity_creativity_benchmark_hints",
        "style_axis_diversity_fingerprint_hints",
        "event_outline_history_compression_hints",
        "agentic_story_world_simulation_hints",
        "reader_rating_signal_model_hints",
        "review_spoiler_sentiment_corpus_hints",
        "beta_reader_archetype_panel_hints",
        "comp_title_market_positioning_hints",
        "local_reader_experience_editor_hints",
        "manuscript_health_ai_prep_gate_hints",
        "anti_statistical_center_chapter_type_gate_hints",
        "delivery_manuscript_assembly_hints",
        "export_format_fidelity_audit_hints",
        "preview_toc_packaging_hints",
        "cover_kdp_metadata_boundary_hints",
        "branching_choice_graph_hints",
        "node_dialogue_state_machine_hints",
        "passage_link_navigation_map_hints",
        "choice_stats_consequence_gate_hints",
        "source_text_fingerprint_gate_hints",
        "fuzzy_phrase_similarity_gate_hints",
        "diff_span_copy_review_hints",
        "minhash_lsh_near_duplicate_gate_hints",
        "simhash_hamming_similarity_gate_hints",
        "semantic_duplicate_cluster_gate_hints",
        "embedding_similarity_independence_gate_hints",
        "corpus_leakage_dedup_review_gate_hints",
        "character_quote_attribution_map_hints",
        "readability_pacing_metric_gate_hints",
        "prose_lint_style_rule_gate_hints",
        "grammar_spelling_copyedit_gate_hints",
        "copyedit_diagnostic_triage_queue_hints",
        "lexical_diversity_voice_audit_hints",
        "stylometric_author_fingerprint_gate_hints",
        "function_word_syntax_style_gate_hints",
        "authorship_attribution_similarity_gate_hints",
        "style_overfit_regression_gate_hints",
        "paraphrase_independence_review_gate_hints",
        "llm_style_dimension_matrix_gate_hints",
        "stylometry_feature_extraction_baseline_gate_hints",
        "local_block_manuscript_workspace_gate_hints",
        "keyphrase_motif_extraction_hints",
        "chinese_segmentation_keyword_gate_hints",
        "chinese_ner_alias_consistency_gate_hints",
        "chinese_text_normalization_gate_hints",
        "chinese_error_correction_review_gate_hints",
        "source_format_import_manifest_hints",
        "pdf_layout_text_extraction_gate_hints",
        "ocr_scanned_page_import_gate_hints",
        "document_partition_chapter_detection_gate_hints",
        "import_provenance_checksum_gate_hints",
        "epub_structure_validation_gate_hints",
        "ebook_accessibility_audit_gate_hints",
        "front_back_matter_metadata_gate_hints",
        "toc_navigation_consistency_gate_hints",
        "agentic_editorial_pipeline_gate_hints",
        "chapter_state_archive_ladder_hints",
        "section_metadata_traceability_gate_hints",
        "ai_prose_fingerprint_cluster_gate_hints",
        "author_candidate_canon_confirmation_gate_hints",
        "progressive_spoiler_context_window_gate_hints",
        "chapter_control_card_writeback_gate_hints",
        "trace_replay_revision_workspace_gate_hints",
        "relationship_graph_global_replace_gate_hints",
        "bookrun_audit_trail_gate_hints",
        "provider_budget_smoke_gate_hints",
        "sidecar_memory_profile_boundary_hints",
        "automatic_director_checkpoint_chain_hints",
        "director_stage_checkpoint_gate_hints",
        "role_asset_quality_review_gate_hints",
        "inspectable_memory_workspace_gate_hints",
        "memory_aware_chapter_workspace_hints",
        "semantic_context_consistency_gate_hints",
        "multi_thread_knowledge_timeline_gate_hints",
        "outline_checkpoint_milestone_gate_hints",
        "language_localization_style_profile_gate_hints",
        "progressive_disclosure_skill_protocol_gate_hints",
        "anti_slop_rulepack_triage_gate_hints",
        "user_modifier_project_blueprint_gate_hints",
        "portable_canon_skill_runtime_gate_hints",
        "staged_outline_chunk_window_gate_hints",
        "wiki_canon_graph_lint_gate_hints",
        "plan_draft_log_verify_loop_gate_hints",
        "mcp_scene_index_revision_boundary_hints",
        "verbalized_sampling_diversity_wiki_gate_hints",
        "literary_event_entity_annotation_gate_hints",
        "narrative_event_evolution_graph_gate_hints",
        "sentiment_arc_emotion_trajectory_gate_hints",
        "cross_context_coreference_gate_hints",
        "character_interaction_network_gate_hints",
        "semantic_chunk_boundary_map_hints",
        "chapter_summary_anchor_gate_hints",
        "topic_drift_map_hints",
        "context_faithfulness_eval_gate_hints",
        "atomic_fact_precision_gate_hints",
        "self_consistency_hallucination_gate_hints",
        "reference_claim_verification_gate_hints",
        "retrieval_trace_observability_gate_hints",
        "prompt_regression_eval_suite_hints",
        "agentwrite_plan_write_pipeline_hints",
        "long_output_length_quality_ruler_hints",
        "long_context_reward_dimension_gate_hints",
        "long_context_benchmark_task_suite_gate_hints",
        "needle_haystack_context_recall_gate_hints",
        "distributed_fact_chain_recall_gate_hints",
        "instance_specific_writing_criteria_gate_hints",
        "material_grounded_query_refinement_hints",
        "hybrid_rubric_pairwise_elo_judge_hints",
        "judge_bias_mitigation_check_hints",
        "plan_reflect_character_chapter_pipeline_hints",
        "human_story_metric_panel_hints",
        "hierarchical_cowriting_story_scaffold_hints",
        "human_coauthor_edit_boundary_hints",
        "recursive_reprompt_revision_loop_hints",
        "reranker_guided_candidate_selection_hints",
        "character_dialogue_persona_memory_hints",
        "event_to_sentence_realization_trace_hints",
        "entity_memory_slotfill_grounding_hints",
        "book_memory_bank_context_lattice_hints",
        "ideation_worksheet_foundation_gate_hints",
        "spec_driven_fiction_scene_tasks_hints",
        "toc_aware_source_deconstruction_hints",
        "two_pass_context_glossary_pipeline_hints",
        "inline_author_edit_markup_versioning_hints",
        "inline_human_machine_coauthoring_gate_hints",
        "hierarchical_orchestrator_generation_gate_hints",
        "batch_continuation_progress_queue_gate_hints",
        "homogeneity_prompt_variation_gate_hints",
        "local_author_data_boundary_gate_hints",
        "prompt_preset_variable_library_gate_hints",
        "imported_manuscript_migration_outline_gate_hints",
        "style_dna_reference_library_gate_hints",
        "anti_copy_style_rag_gate_hints",
        "draft_candidate_promotion_gate_hints",
        "privacy_preserving_local_index_gate_hints",
        "chapter_split_deconstruction_export_gate_hints",
        "final_prompt_preview_span_revision_gate_hints",
        "project_skill_agent_loop_gate_hints",
        "knowledge_document_writeback_trace_gate_hints",
        "host_instruction_context_boundary_gate_hints",
        "schema_review_revision_recovery_gate_hints",
        "cjk_bm25_context_retrieval_gate_hints",
        "dynamic_architecture_extension_gate_hints",
        "chapter_description_continuity_bridge_gate_hints",
        "selective_streaming_regeneration_gate_hints",
        "research_citation_boundary_gate_hints",
        "beta_reader_summary_context_gate_hints",
        "style_vocab_world_card_extraction_gate_hints",
        "prompt_only_decay_ceiling_gate_hints",
        "serial_platform_minimum_audit_gate_hints",
        "multi_agent_reject_retry_review_gate_hints",
        "story_bible_context_packet_branch_gate_hints",
        "memory_augmented_delta_verification_gate_hints",
        "statistical_style_benchmark_rewrite_gate_hints",
        "dashboard_task_quality_resume_gate_hints",
        "webnovel_skill_suite_release_boundary_gate_hints",
        "platform_voice_meme_emotion_gate_hints",
        "truth_file_phase_dashboard_gate_hints",
        "platform_publish_automation_boundary_gate_hints",
        "multi_work_style_imitation_mode_gate_hints",
        "prose_metric_pov_dialogue_gate_hints",
        "pov_character_thread_filter_gate_hints",
        "agent_writing_phase_polish_gate_hints",
        "hierarchical_semantic_snapshot_workspace_gate_hints",
        "rights_first_adaptation_pipeline_gate_hints",
        "local_flow_story_graph_workspace_gate_hints",
        "editor_context_prose_analysis_gate_hints",
        "living_codex_editorial_workbench_gate_hints",
        "agent_role_profile_workflow_gate_hints",
        "confirmed_action_audit_recovery_gate_hints",
        "project_isolated_story_bible_query_gate_hints",
        "work_dna_method_transfer_eval_gate_hints",
        "governed_full_reading_continuation_gate_hints",
        "document_gamebook_branching_adapter_gate_hints",
        "forensic_style_clone_audit_risk_gate_hints",
        "story_import_pattern_revision_gate_hints",
        "consequence_ledger_last_actions_context_gate_hints",
        "creative_writing_multiaxis_provider_gate_hints",
        "system_world_fate_simulation_gate_hints",
        "constraint_harness_review_worktree_gate_hints",
        "state_current_reviewer_loop_gate_hints",
        "versioned_scene_fact_review_pipeline_gate_hints",
        "offline_chapter_revision_export_gate_hints",
        "multi_agent_outline_continuity_review_gate_hints",
        "hosted_ai_sidebar_product_boundary_gate_hints",
        "creative_scaffold_prompt_sequence_gate_hints",
        "writers_room_stop_authority_gate_hints",
        "novel_to_screenplay_structure_coverage_gate_hints",
        "translation_glossary_context_qa_gate_hints",
        "desktop_translation_batch_replacement_boundary_gate_hints",
        "platform_kb_retention_strategy_gate_hints",
        "chapter_end_hook_retention_ladder_gate_hints",
        "webnovel_kb_mcp_runtime_boundary_gate_hints",
        "agent_cache_concurrency_recovery_gate_hints",
        "long_context_role_boundary_state_validation_gate_hints",
        "chapter_memory_ingestion_context_budget_gate_hints",
        "human_ai_decision_authority_gate_hints",
        "parallel_critic_tribunal_issue_gate_hints",
        "prompt_evolution_fitness_governance_gate_hints",
        "fanqie_checkpoint_compliance_audit_gate_hints",
        "outline_validator_change_declaration_gate_hints",
        "scene_deconstruction_theory_report_gate_hints",
        "platform_ranking_research_boundary_gate_hints",
        "tiered_memory_fact_retirement_gate_hints",
        "entity_mention_arc_timeline_gate_hints",
        "codex_story_skill_project_scaffold_gate_hints",
        "ai_ism_detect_edit_convergence_gate_hints",
        "markdown_skill_story_project_contract_gate_hints",
        "canon_evidence_suggestion_review_gate_hints",
        "expert_chain_alignment_creativity_gate_hints",
        "visual_story_bible_continuity_gate_hints",
        "causal_dramatica_agent_pipeline_hints",
        "capture_distillation_production_gate_hints",
        "skill_orchestrated_chinese_novel_workflow_hints",
        "langgraph_story_state_machine_hints",
        "story_daemon_evolution_loop_hints",
        "local_rag_writing_ide_gate_hints",
        "canon_drift_continuity_qa_gate_hints",
        "patch_replay_manuscript_state_gate_hints",
        "microkernel_skill_plugin_isolation_gate_hints",
        "interactive_reader_writer_loop_gate_hints",
        "abstract_style_learning_skill_gate_hints",
        "impromptu_thread_pool_chapter_gate_hints",
        "offline_inspiration_bank_style_gate_hints",
        "atelier_phase_pipeline_gate_hints",
        "book_mining_genesis_automation_gate_hints",
        "multi_book_autopilot_studio_gate_hints",
        "longrun_commit_projection_health_gate_hints",
        "fresh_context_chapter_iteration_gate_hints",
        "reader_reward_channel_gate_hints",
        "tri_modal_workflow_validation_gate_hints",
        "scene_promise_mob_review_gate_hints",
        "webnovel_genre_tracker_gate_hints",
        "simulation_causal_ledger_verification_gate_hints",
        "writer_git_exploration_review_gate_hints",
        "narrative_qa_comprehension_gate_hints",
        "chapter_summary_alignment_gate_hints",
        "story_question_answer_validation_gate_hints",
        "causal_why_explanation_gate_hints",
        "story_commonsense_consistency_gate_hints",
        "query_focused_long_summary_gate_hints",
        "temporal_canon_context_graph_hints",
        "long_term_author_preference_memory_hints",
        "community_graph_source_deconstruction_hints",
        "dual_level_graph_vector_retrieval_hints",
        "schema_guided_graph_extraction_hints",
        "counterfactual_story_graph_rag_gate_hints",
        "character_knowledge_timeline_gate_hints",
        "trope_inventory_similarity_gate_hints",
        "trope_graph_expectation_map_hints",
        "trope_density_novelty_budget_hints",
        "trope_source_boundary_review_hints",
        "source_license_detection_gate_hints",
        "spdx_reuse_compliance_gate_hints",
        "public_domain_corpus_boundary_hints",
        "attribution_derivative_work_gate_hints",
        "source_entity_redaction_gate_hints",
        "custom_entity_label_inventory_hints",
        "placeholder_alias_consistency_map_hints",
        "proper_noun_leakage_review_hints",
        "manuscript_card_board_extraction_gate_hints",
        "chapter_timeline_frontmatter_export_gate_hints",
        "manuscript_binder_scene_snapshot_gate_hints",
        "story_bible_relationship_analytics_gate_hints",
        "seed_to_bible_foundation_loop_gate_hints",
        "layered_story_bible_artifact_contract_gate_hints",
        "author_ai_project_contract_review_gate_hints",
        "manuscript_pr_editorial_workflow_gate_hints",
        "short_drama_story_bible_template_gate_hints",
        "visual_anchor_prompt_handoff_gate_hints",
        "character_continuity_dimension_schema_gate_hints",
        "short_drama_character_memory_forbidden_change_gate_hints",
        "short_drama_worldbuilding_layer_gate_hints",
        "vertical_drama_script_format_gate_hints",
        "storyboard_shot_list_prompt_gate_hints",
        "script_to_video_workflow_handoff_gate_hints",
        "short_drama_production_stage_gate_hints",
        "drama_shot_list_camera_pattern_gate_hints",
        "vertical_hook_cliffhanger_template_gate_hints",
        "storyboard_shot_pack_reuse_gate_hints",
    ):
        hints = _as_note_list(source_pattern_pack.get(key))
        if not hints:
            continue
        lines.append(f"- {key}:")
        for hint in hints[:6]:
            lines.append(f"  - {hint}")

    if include_inspired_guidance:
        inspired_mapping_targets = _as_note_list(source_pattern_pack.get("inspired_mapping_targets"))
        if inspired_mapping_targets:
            lines.append("- inspired_mapping_targets: " + ", ".join(inspired_mapping_targets[:12]))

        inspired_prompt_hints = _as_note_list(source_pattern_pack.get("inspired_prompt_hints"))
        if inspired_prompt_hints:
            lines.append("- inspired_prompt_hints:")
            for hint in inspired_prompt_hints[:6]:
                lines.append(f"  - {hint}")

        inspired_transformation_hints = _as_note_list(source_pattern_pack.get("inspired_transformation_hints"))
        if inspired_transformation_hints:
            lines.append("- inspired_transformation_hints:")
            for hint in inspired_transformation_hints[:6]:
                lines.append(f"  - {hint}")

        inspired_copy_risk_hints = _as_note_list(source_pattern_pack.get("inspired_copy_risk_hints"))
        if inspired_copy_risk_hints:
            lines.append("- inspired_copy_risk_hints:")
            for hint in inspired_copy_risk_hints[:6]:
                lines.append(f"  - {hint}")

    review_hints = _as_note_list(source_pattern_pack.get("self_review_policy_hints"))
    if review_hints:
        lines.append("- self_review_policy_hints:")
        for hint in review_hints[:6]:
            lines.append(f"  - {hint}")

    review_gate_hints = _as_note_list(source_pattern_pack.get("self_review_gate_hints"))
    if review_gate_hints:
        lines.append("- self_review_gate_hints:")
        for hint in review_gate_hints[:6]:
            lines.append(f"  - {hint}")

    chapter_change_hints = _as_note_list(source_pattern_pack.get("chapter_change_package_hints"))
    if chapter_change_hints:
        lines.append("- chapter_change_package_hints:")
        for hint in chapter_change_hints[:6]:
            lines.append(f"  - {hint}")

    safety_constraints = _as_note_list(source_pattern_pack.get("safety_constraints"))
    if safety_constraints:
        lines.append("- safety_constraints:")
        for constraint in safety_constraints[:8]:
            lines.append(f"  - {constraint}")

    source_intake_notes = _as_note_list(source_pattern_pack.get("source_intake_notes"))
    if source_intake_notes:
        lines.append("- source_intake_notes:")
        for note in source_intake_notes[:6]:
            lines.append(f"  - {note}")

    if not lines:
        return "(empty public source pattern pack; do not import external code.)"
    return "\n".join(lines)


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _as_note_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    notes: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            notes.append(text)
    return notes
