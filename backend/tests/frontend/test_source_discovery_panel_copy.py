import json
import re
from pathlib import Path


def test_source_discovery_panel_surfaces_inspired_pattern_pack_fields():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    for field in (
        "continuation_prompt_hints",
        "style_signature_hints",
        "structured_generation_hints",
        "card_workbench_hints",
        "context_reference_hints",
        "scene_asset_pipeline_hints",
        "publication_pipeline_hints",
        "self_review_policy_hints",
        "inspired_mapping_targets",
        "inspired_prompt_hints",
        "inspired_transformation_hints",
        "inspired_copy_risk_hints",
        "lorebook_context_hints",
        "author_note_layer_hints",
        "world_state_tracking_hints",
        "memory_snapshot_versioning_hints",
        "quality_score_loop_hints",
        "voice_fingerprint_hints",
        "anti_slop_audit_hints",
        "bookrun_audit_trail_gate_hints",
        "provider_budget_smoke_gate_hints",
        "sidecar_memory_profile_boundary_hints",
        "outline_checkpoint_milestone_gate_hints",
        "language_localization_style_profile_gate_hints",
        "progressive_disclosure_skill_protocol_gate_hints",
        "anti_slop_rulepack_triage_gate_hints",
        "story_bible_constitution_source_gate_hints",
        "scene_outline_approval_status_gate_hints",
        "pov_information_asymmetry_schedule_gate_hints",
        "pacing_arc_polish_pass_gate_hints",
        "user_modifier_project_blueprint_gate_hints",
        "portable_canon_skill_runtime_gate_hints",
        "staged_outline_chunk_window_gate_hints",
        "wiki_canon_graph_lint_gate_hints",
        "plan_draft_log_verify_loop_gate_hints",
        "mcp_scene_index_revision_boundary_hints",
        "verbalized_sampling_diversity_wiki_gate_hints",
        "agentic_editorial_pipeline_gate_hints",
        "craft_role_pipeline_hints",
        "branching_choice_graph_hints",
        "choice_stats_consequence_gate_hints",
        "delivery_manuscript_assembly_hints",
        "export_format_fidelity_audit_hints",
        "character_dialogue_persona_memory_hints",
        "anti_repetition_prompt_rules_hints",
        "temporal_canon_context_graph_hints",
        "narrative_time_age_trace_gate_hints",
        "plotline_thread_tracking_hints",
        "rolling_summary_context_trim_hints",
        "local_first_workspace_hints",
        "prompt_library_hints",
        "scene_level_generation_hints",
        "review_queue_staging_hints",
        "style_guide_layering_hints",
        "entity_schema_custom_fields_hints",
        "content_ref_externalization_hints",
        "graph_healing_hints",
        "contradiction_detection_hints",
        "graph_branching_atomicity_hints",
        "query_lint_contract_hints",
        "premature_ending_guard_hints",
        "layered_memory_model_hints",
        "plot_dependency_graph_hints",
        "plotgrid_scene_matrix_hints",
        "scene_status_dashboard_hints",
        "gradual_reveal_control_hints",
        "setup_payoff_tracking_hints",
        "scene_type_directing_hints",
        "worldpkg_export_hints",
        "alternate_timeline_branching_hints",
        "divergence_guidance_hints",
        "plain_text_project_storage_hints",
        "synopsis_cross_reference_hints",
        "snowflake_premise_expansion_hints",
        "outliner_index_cards_hints",
        "narrative_strand_mapping_hints",
        "character_depth_interview_hints",
        "mindmap_visual_planning_hints",
        "manuscript_export_formats_hints",
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
            "agentwrite_plan_write_pipeline_hints",
            "long_output_length_quality_ruler_hints",
            "long_context_reward_dimension_gate_hints",
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
            "event_to_sentence_realization_trace_hints",
            "entity_memory_slotfill_grounding_hints",
            "book_memory_bank_context_lattice_hints",
            "ideation_worksheet_foundation_gate_hints",
            "spec_driven_fiction_scene_tasks_hints",
            "toc_aware_source_deconstruction_hints",
            "two_pass_context_glossary_pipeline_hints",
            "inline_author_edit_markup_versioning_hints",
            "long_term_author_preference_memory_hints",
            "community_graph_source_deconstruction_hints",
            "dual_level_graph_vector_retrieval_hints",
            "schema_guided_graph_extraction_hints",
            "counterfactual_story_graph_rag_gate_hints",
            "character_knowledge_timeline_gate_hints",
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
            "scheduled_agent_style_qa_workflow_gate_hints",
            "file_based_showrunner_canon_approval_gate_hints",
            "nova_local_version_memory_role_gate_hints",
            "forge_agent_mcp_eval_contract_gate_hints",
            "three_path_graph_diff_recall_gate_hints",
            "layered_parallel_audit_state_machine_gate_hints",
            "possibility_graph_dependency_replay_gate_hints",
            "craft_companion_dual_entry_arbitration_gate_hints",
            "novelwriter_live_manuscript_analytics_gate_hints",
            "lumintree_simulation_tree_category_gate_hints",
            "scrivener_mcp_project_analysis_boundary_gate_hints",
            "kindling_local_outline_reference_import_gate_hints",
            "novelengine_weighted_rag_consistency_gate_hints",
            "public_showrunner_template_release_gate_hints",
            "phase1_style_manual_reference_boundary_gate_hints",
            "six_layer_iron_law_chapter_gate_hints",
            "element_swap_deconstruction_rewrite_pipeline_gate_hints",
            "chapter_progressive_disassembly_checkpoint_gate_hints",
            "quantified_style_learning_confidence_gate_hints",
            "truth_system_chapter_settlement_gate_hints",
            "group_collaboration_conflict_vote_memory_gate_hints",
            "arboris_story_direction_workspace_gate_hints",
            "sdd_seven_step_cross_platform_skill_gate_hints",
            "langgraph_world_outline_review_memory_gate_hints",
            "xiaoshuo_local_canon_skill_studio_gate_hints",
            "director_orchestrator_trace_canonize_gate_hints",
            "book_build_export_delivery_gate_hints",
            "plot_storyline_improvement_epub_chain_gate_hints",
            "fast_structure_content_model_split_gate_hints",
            "openai_compatible_book_api_portability_gate_hints",
            "filesystem_memory_agent_loop_gate_hints",
            "desktop_review_rag_retry_gate_hints",
            "novel_core_knowledge_pack_rag_gate_hints",
            "rag_technique_catalog_context_retrieval_gate_hints",
            "agent_architecture_catalog_workflow_gate_hints",
            "canonical_packet_source_promotion_gate_hints",
            "truth_file_dual_audit_agent_pipeline_gate_hints",
            "long_consistency_reverse_rag_retry_gate_hints",
            "summary_buffer_selective_rag_memory_gate_hints",
            "genre_gene_capsule_market_boundary_gate_hints",
            "phase_acceptance_epub_delivery_gate_hints",
            "local_continuation_memory_export_gate_hints",
            "six_agent_memory_debate_consistency_gate_hints",
            "multi_phase_sensory_continuation_gate_hints",
            "agentic_backstory_verification_rag_gate_hints",
            "voiceprint_private_baseline_drift_gate_hints",
            "margin_guided_long_context_revision_gate_hints",
            "agent_style_rulebook_soft_enforcement_gate_hints",
            "private_person_place_timeline_output_gate_hints",
            "story_os_governed_studio_pipeline_gate_hints",
            "standards_file_workflow_os_gate_hints",
            "chinese_segmentation_keyword_gate_hints",
            "chinese_ner_alias_consistency_gate_hints",
            "chinese_text_normalization_gate_hints",
            "chinese_error_correction_review_gate_hints",
            "literary_event_entity_annotation_gate_hints",
            "narrative_event_evolution_graph_gate_hints",
            "sentiment_arc_emotion_trajectory_gate_hints",
            "cross_context_coreference_gate_hints",
            "character_interaction_network_gate_hints",
            "character_quote_attribution_map_hints",
            "readability_pacing_metric_gate_hints",
            "lexical_diversity_voice_audit_hints",
            "keyphrase_motif_extraction_hints",
            "semantic_chunk_boundary_map_hints",
            "chapter_summary_anchor_gate_hints",
            "topic_drift_map_hints",
            "context_faithfulness_eval_gate_hints",
            "retrieval_trace_observability_gate_hints",
            "prompt_regression_eval_suite_hints",
            "source_text_fingerprint_gate_hints",
            "fuzzy_phrase_similarity_gate_hints",
            "diff_span_copy_review_hints",
            "minhash_lsh_near_duplicate_gate_hints",
            "simhash_hamming_similarity_gate_hints",
            "semantic_duplicate_cluster_gate_hints",
            "embedding_similarity_independence_gate_hints",
            "style_axis_diversity_fingerprint_hints",
            "stylometric_author_fingerprint_gate_hints",
            "function_word_syntax_style_gate_hints",
            "authorship_attribution_similarity_gate_hints",
            "style_overfit_regression_gate_hints",
            "paraphrase_independence_review_gate_hints",
            "ai_prose_fingerprint_cluster_gate_hints",
            "trope_inventory_similarity_gate_hints",
            "trope_graph_expectation_map_hints",
            "trope_density_novelty_budget_hints",
            "trope_source_boundary_review_hints",
            "reader_retention_review_gate_hints",
            "serial_reader_reward_contract_gate_hints",
            "reader_rating_signal_model_hints",
            "review_spoiler_sentiment_corpus_hints",
            "beta_reader_archetype_panel_hints",
            "comp_title_market_positioning_hints",
            "local_reader_experience_editor_hints",
            "prose_lint_style_rule_gate_hints",
            "grammar_spelling_copyedit_gate_hints",
            "copyedit_diagnostic_triage_queue_hints",
            "eventide_feedback_first_lorebook_queue_gate_hints",
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
            "source_license_detection_gate_hints",
            "spdx_reuse_compliance_gate_hints",
            "public_domain_corpus_boundary_hints",
            "attribution_derivative_work_gate_hints",
            "source_entity_redaction_gate_hints",
            "custom_entity_label_inventory_hints",
            "placeholder_alias_consistency_map_hints",
            "proper_noun_leakage_review_hints",
            "source_format_import_manifest_hints",
            "pdf_layout_text_extraction_gate_hints",
            "ocr_scanned_page_import_gate_hints",
            "document_partition_chapter_detection_gate_hints",
            "import_provenance_checksum_gate_hints",
            "epub_structure_validation_gate_hints",
            "ebook_accessibility_audit_gate_hints",
            "front_back_matter_metadata_gate_hints",
            "toc_navigation_consistency_gate_hints",
            "longgu_engineering_harness_gate_hints",
            "prose_health_live_dashboard_gate_hints",
            "raw_story_assimilation_workflow_gate_hints",
            "style_distillation_rights_boundary_gate_hints",
            "screenplay_ast_yaml_adaptation_gate_hints",
            "fanqie_publish_dryrun_boundary_gate_hints",
            "lore_forge_knowledge_engineering_gate_hints",
            "layered_style_profile_fusion_eval_gate_hints",
            "truth_file_rag_pyramid_audit_gate_hints",
            "proposal_accept_ledger_quality_gate_hints",
            "simulated_event_log_narrative_layer_gate_hints",
            "slash_command_context_tier_state_gate_hints",
            "dual_track_epub_manifest_pipeline_gate_hints",
            "adaptive_quality_self_healing_autonomy_gate_hints",
            "open_storyline_media_style_transfer_boundary_gate_hints",
            "hierarchical_story_tree_evaluation_agent_gate_hints",
            "recurrent_plan_memory_generation_gate_hints",
            "bookend_closure_infill_gate_hints",
            "strict_requirement_planning_generation_gate_hints",
            "canon_graph_hybrid_validation_gate_hints",
            "packet_first_style_overlay_context_gate_hints",
            "lora_style_adapter_memory_bank_gate_hints",
            "browser_local_story_bible_privacy_gate_hints",
            "jingwei_layered_canon_plugin_gate_hints",
            "roleplay_branchable_save_world_gate_hints",
            "append_only_canon_pov_promise_gate_hints",
            "author_keeps_pen_diagnostic_codex_gate_hints",
            "spec_driven_state_record_publish_gate_hints",
            "desktop_langgraph_memory_observability_gate_hints",
            "story_state_output_contract_gate_hints",
            "living_document_plan_log_verify_gate_hints",
            "markdown_frontmatter_continuity_engine_gate_hints",
            "story_design_dependency_impact_gate_hints",
            "writer_critic_verify_quality_cycle_gate_hints",
            "q15_story_quality_benchmark_gate_hints",
            "local_desktop_manuscript_revision_bible_gate_hints",
            "canonkit_local_canon_drift_context_pack_gate_hints",
            "storyforge_wiki_ingest_lint_graph_gate_hints",
            "local_copilot_layered_memory_workspace_gate_hints",
            "pending_fact_canon_promotion_graph_gate_hints",
            "work_corpus_reindex_autopilot_gate_hints",
            "memoir_story_spine_consensus_grounding_gate_hints",
            "map_reduce_factual_anchor_adaptation_gate_hints",
            "platform_genre_style_stamp_gate_hints",
            "chapter_packet_promise_debt_audit_gate_hints",
            "webnovel_state_machine_knowledge_graph_gate_hints",
            "story_knowledge_layer_sot_adaptation_gate_hints",
            "writer_studio_binder_voice_rag_gate_hints",
            "copilot_webnovel_research_runner_gate_hints",
            "tinystyler_meaning_preserving_style_transfer_gate_hints",
            "stylevec_style_signal_overfit_boundary_gate_hints",
            "chapter_translation_style_context_gate_hints",
            "slima_book_mcp_beta_reader_file_gate_hints",
            "dialogoi_filetype_rag_novel_project_gate_hints",
            "scrivener_mcp_direct_project_edit_boundary_gate_hints",
            "vector_story_frame_coordinate_gate_hints",
            "setting_runtime_document_architecture_gate_hints",
            "inkfoundry_state_db_redteam_voice_sandbox_gate_hints",
            "local_snapshot_backup_export_gate_hints",
            "continuity_passport_drift_repair_gate_hints",
            "originality_report_multimetric_gate_hints",
            "semantic_stylometric_overlap_gate_hints",
            "human_oversight_quality_signal_gate_hints",
            "ai_tell_pattern_review_gate_hints",
            "naturalization_detector_disclaimer_gate_hints",
            "web_similarity_scrape_boundary_gate_hints",
            "fiction_skill_agent_workbench_gate_hints",
            "local_node_graph_lore_fix_loop_gate_hints",
            "uploaded_style_learning_api_boundary_gate_hints",
            "editorial_memory_card_graph_agent_gate_hints",
            "genre_inspiration_budget_library_gate_hints",
            "stepwise_local_book_generation_file_gate_hints",
            "radial_subplot_timeline_xray_gate_hints",
            "volume_antipattern_dependency_graph_gate_hints",
            "style_dna_breakpoint_hierarchy_gate_hints",
            "arc_state_foreshadowing_persistence_gate_hints",
            "multi_agent_vector_memory_timeline_gate_hints",
            "versioned_workspace_chapter_index_gate_hints",
            "dual_engine_reader_sandbox_rag_gate_hints",
            "intent_tool_quality_style_checkpoint_gate_hints",
            "loreweave_graph_glossary_translation_gate_hints",
            "mcp_novel_memory_gateway_tool_gate_hints",
            "goink_tool_state_autoreview_gate_hints",
            "sandbox_godmode_branch_simulation_gate_hints",
            "editorial_persona_voice_workshop_gate_hints",
            "story_factory_thousand_chapter_cache_gate_hints",
            "strand_beat_quorum_canon_gate_hints",
            "substrate_spark_canon_promotion_gate_hints",
            "codex_webnovel_plugin_parity_gate_hints",
            "external_agent_api_free_cataloging_gate_hints",
            "rights_safe_source_to_memory_pipeline_gate_hints",
            "desktop_agent_planning_reflection_gate_hints",
            "mega_chapter_genre_layered_memory_gate_hints",
            "l0_l3_memory_skeleton_volume_gate_hints",
            "recursive_scene_reflection_long_context_gate_hints",
            "markdown_ink_export_validation_gate_hints",
            "file_backed_promise_ledger_audit_gate_hints",
            "critique_revision_series_memory_gate_hints",
            "mock_first_multi_agent_continuation_gate_hints",
            "truth_file_write_next_state_update_gate_hints",
            "author_control_context_assembly_gate_hints",
            "craft_scene_concrete_finding_revision_gate_hints",
            "tutorial_case_library_curation_gate_hints",
            "anti_hallucination_strand_weave_review_gate_hints",
            "hierarchical_narrative_memory_os_gate_hints",
            "narrative_canon_version_branch_graph_gate_hints",
            "planner_writer_evaluator_editor_saga_gate_hints",
            "story_weaver_kg_bible_rag_gate_hints",
            "taleforge_memory_continuity_research_gate_hints",
            "ai_flavor_template_shell_cleanup_gate_hints",
            "robot_writers_room_human_card_flow_gate_hints",
            "spire_roleplay_character_privacy_fiction_surface_gate_hints",
            "ai_book_generator_agent_mode_local_key_export_gate_hints",
            "risuai_lorebook_prompt_order_regex_gate_hints",
            "grimodex_codex_attribution_scene_chat_gate_hints",
            "supernovel_architecture_blueprint_state_search_gate_hints",
            "screenplay_realtime_writers_room_media_boundary_gate_hints",
            "nebula_codex_character_knowledge_version_gate_hints",
            "forfiction_theia_story_extension_skill_gate_hints",
            "inkos_truthfile_api_fanfic_imitation_gate_hints",
        ):
        assert field in types_text
        assert field in panel_text

    assert "Hierarchical narrative memory OS gates" in panel_text
    assert "Narrative canon branch graph gates" in panel_text
    assert "Planner/writer/evaluator/editor saga gates" in panel_text
    assert "Story-Weaver KG / bible / RAG gates" in panel_text
    assert "TaleForge memory continuity research gates" in panel_text
    assert "Core remix kernel gates" in panel_text
    assert "Robot Writers Room human-card flow gates" in panel_text
    assert "Spire roleplay character privacy fiction-surface gates" in panel_text
    assert "AI Book Generator agent-mode local-key export gates" in panel_text
    assert "RisuAI lorebook prompt-order regex gates" in panel_text
    assert "Grimodex Codex attribution scene-chat gates" in panel_text
    assert "SuperNovel architecture blueprint state-search gates" in panel_text
    assert "Screenplay realtime writers-room media boundary gates" in panel_text
    assert "Nebula Codex character knowledge version gates" in panel_text
    assert "forFiction Theia story-extension skill gates" in panel_text
    assert "InkOS truth-file API fanfic/imitation gates" in panel_text
    assert "default_github_queries" in types_text
    assert "default_github_queries" in panel_text
    assert "default_github_repository_urls" in types_text
    assert "default_github_repository_urls" in panel_text
    assert "default_linux_do_rss_urls" in types_text
    assert "default_linux_do_rss_urls" in panel_text
    assert "repositorySeedsEdited" in panel_text
    assert "githubQueriesEdited" in panel_text
    assert "linuxDoRssUrlsEdited" in panel_text
    assert "后端默认 seed" in panel_text
    assert "GitHub Search 查询" in panel_text
    assert "Community RSS 来源" in panel_text
    assert "只按换行拆分" in panel_text
    assert "Continuation prompt hints" in panel_text
    assert "Style signature hints" in panel_text
    assert "Structured generation hints" in panel_text
    assert "Card workbench hints" in panel_text
    assert "Context reference hints" in panel_text
    assert "Scene asset pipeline hints" in panel_text
    assert "Publication pipeline hints" in panel_text
    assert "Self-review policy hints" in panel_text
    assert "Inspired mapping targets" in panel_text
    assert "Inspired copy-risk hints" in panel_text
    assert "Lorebook context hints" in panel_text
    assert "Memory snapshot versioning hints" in panel_text
    assert "BookRun / skill protocol gates" in panel_text
    assert "Project workbench / memory diversity gates" in panel_text
    assert "Provider budget smoke gates" in panel_text
    assert "Wiki canon graph lint gates" in panel_text
    assert "Authorial agents / interactive delivery gates" in panel_text
    assert "Agentic editorial pipeline gates" in panel_text
    assert "Branching choice graph gates" in panel_text
    assert "Export format fidelity audit gates" in panel_text
    assert "Voice / timeline continuity gates" in panel_text
    assert "Character dialogue persona memory gates" in panel_text
    assert "Anti-repetition prompt rule gates" in panel_text
    assert "Temporal canon context graph gates" in panel_text
    assert "Workspace / scene planning gates" in panel_text
    assert "Local-first workspace gates" in panel_text
    assert "Prompt library gates" in panel_text
    assert "Scene-level generation gates" in panel_text
    assert "Review queue staging gates" in panel_text
    assert "Style guide layering gates" in panel_text
    assert "Entity schema custom field gates" in panel_text
    assert "ContentRef externalization gates" in panel_text
    assert "Graph healing gates" in panel_text
    assert "Contradiction detection gates" in panel_text
    assert "Graph branching atomicity gates" in panel_text
    assert "Query lint contract gates" in panel_text
    assert "Plotgrid / reveal / branch gates" in panel_text
    assert "Premature ending guards" in panel_text
    assert "Layered memory model gates" in panel_text
    assert "Plot dependency graph gates" in panel_text
    assert "Plotgrid scene matrix gates" in panel_text
    assert "Scene status dashboard gates" in panel_text
    assert "Gradual reveal control gates" in panel_text
    assert "Setup / payoff tracking gates" in panel_text
    assert "Scene type directing gates" in panel_text
    assert "WorldPkg export gates" in panel_text
    assert "Alternate timeline branching gates" in panel_text
    assert "Divergence guidance gates" in panel_text
    assert "Mature manuscript planning gates" in panel_text
    assert "Plain text project storage gates" in panel_text
    assert "Synopsis cross-reference gates" in panel_text
    assert "Snowflake premise expansion gates" in panel_text
    assert "Outliner index-card gates" in panel_text
    assert "Narrative strand mapping gates" in panel_text
    assert "Character depth interview gates" in panel_text
    assert "Mindmap visual planning gates" in panel_text
    assert "Manuscript export format gates" in panel_text
    assert "Causal state-machine / skill workflow gates" in panel_text
    assert "Causal Dramatica agent pipeline gates" in panel_text
    assert "Capture distillation production gates" in panel_text
    assert "Skill-orchestrated Chinese novel workflow gates" in panel_text
    assert "LangGraph story state machine gates" in panel_text
    assert "Agent role profile workflow gates" in panel_text
    assert "Confirmed action audit recovery gates" in panel_text
    assert "Project-isolated story-bible query gates" in panel_text
    assert "Work-DNA method transfer/eval gates" in panel_text
    assert "Governed full-reading continuation gates" in panel_text
    assert "Document gamebook branching adapter gates" in panel_text
    assert "Forensic style clone/audit risk gates" in panel_text
    assert "Story import pattern/revision gates" in panel_text
    assert "Consequence ledger last-actions context gates" in panel_text
    assert "Creative writing multi-axis provider gates" in panel_text
    assert "Story daemon evolution loop gates" in panel_text
    assert "Local RAG / canon QA / patch replay gates" in panel_text
    assert "Local RAG writing IDE gates" in panel_text
    assert "Canon drift continuity QA gates" in panel_text
    assert "Patch replay manuscript state gates" in panel_text
    assert "Microkernel skill plugin isolation gates" in panel_text
    assert "Interactive reader-writer loop gates" in panel_text
    assert "Abstract style learning skill gates" in panel_text
    assert "Impromptu / offline / atelier gates" in panel_text
    assert "Impromptu thread-pool chapter gates" in panel_text
    assert "Offline inspiration-bank style gates" in panel_text
    assert "Atelier phase pipeline gates" in panel_text
    assert "Book-mining / autopilot / longrun gates" in panel_text
    assert "Book mining genesis automation gates" in panel_text
    assert "Multi-book autopilot studio gates" in panel_text
    assert "Longrun commit projection health gates" in panel_text
    assert "Fresh-context chapter iteration gates" in panel_text
    assert "Long-output planning / reward gates" in panel_text
    assert "AgentWrite plan-write pipeline gates" in panel_text
    assert "Long-output length quality ruler gates" in panel_text
    assert "Long-context reward dimension gates" in panel_text
    assert "Writing benchmark / judge gates" in panel_text
    assert "Instance-specific writing criteria gates" in panel_text
    assert "Material-grounded query refinement gates" in panel_text
    assert "Hybrid rubric pairwise Elo judge gates" in panel_text
    assert "Judge bias mitigation checks" in panel_text
    assert "Plan-reflect character chapter pipeline gates" in panel_text
    assert "Human story metric panel gates" in panel_text
    assert "Agents Room multi-step story gates" in panel_text
    assert "Judgemark literary criteria gates" in panel_text
    assert "Seven-law platform closed-loop gates" in panel_text
    assert "Vibe Noveling skill-agent Save-the-Cat gates" in panel_text
    assert "Story Bible QA POV/lore-rule gates" in panel_text
    assert "Gemini Writer context-recovery gates" in panel_text
    assert "WikiPlots corpus-boundary gates" in panel_text
    assert "Reliquery reconstructive-recall vault gates" in panel_text
    assert "Novel Studio accepted-chapter memory gates" in panel_text
    assert "NovelForge version-safe human-review gates" in panel_text
    assert "Unorthodox pipeline stage retry gates" in panel_text
    assert "WriterOS role-validator boundary gates" in panel_text
    assert "harnessNovel deconstruct-imitate gates" in panel_text
    assert "Novel rule-auditor learning-loop gates" in panel_text
    assert "Novel rewriter copyright-cost gates" in panel_text
    assert "woke_novel template-resume CLI gates" in panel_text
    assert "Nai multi-agent RAG consistency gates" in panel_text
    assert "ScriptWhisper ScriptYAML adaptation gates" in panel_text
    assert "Novel audit 11-dimension rewrite gates" in panel_text
    assert "Local continuation workstation context gates" in panel_text
    assert "P4/P5 foreshadow relationship outline gates" in panel_text
    assert "Book Writer memory-arc revision gates" in panel_text
    assert "Kindle agent pipeline compile gates" in panel_text
    assert "KDP metadata chapter export gates" in panel_text
    assert "Dual-model summary continuation session gates" in panel_text
    assert "Morpheus trace-memory revision gates" in panel_text
    assert "Novel Control chapter-card writeback gates" in panel_text
    assert "QMAI hybrid context acceptance gates" in panel_text
    assert "ReNovel tri-model aligned rewrite gates" in panel_text
    assert "AI Novel mindmap prompt-library gates" in panel_text
    assert "File-based showrunner canon approval gates" in panel_text
    assert "Nova local version-memory role gates" in panel_text
    assert "Forge Agent MCP eval contract gates" in panel_text
    assert "Three-path graph diff recall gates" in panel_text
    assert "Layered parallel audit state-machine gates" in panel_text
    assert "Possibility graph dependency replay gates" in panel_text
    assert "Craft Companion dual-entry arbitration gates" in panel_text
    assert "NovelWriter live manuscript analytics gates" in panel_text
    assert "LuminTree simulation category gates" in panel_text
    assert "Scrivener MCP project analysis boundary gates" in panel_text
    assert "Kindling local outline reference import gates" in panel_text
    assert "NovelEngine weighted RAG consistency gates" in panel_text
    assert "Chapter-progressive disassembly checkpoint gates" in panel_text
    assert "Quantified style-learning confidence gates" in panel_text
    assert "Truth-system chapter settlement gates" in panel_text
    assert "Group collaboration conflict-vote memory gates" in panel_text
    assert "Arboris story-direction workspace gates" in panel_text
    assert "SDD seven-step cross-platform skill gates" in panel_text
    assert "LangGraph world-outline-review memory gates" in panel_text
    assert "Xiaoshuo local canon skill-studio gates" in panel_text
    assert "Director-orchestrator trace canonize gates" in panel_text
    assert "Book build export delivery gates" in panel_text
    assert "Plot-storyline improvement EPUB chain gates" in panel_text
    assert "Writer Studio binder/voice/RAG gates" in panel_text
    assert "Copilot webnovel research-runner gates" in panel_text
    assert "TinyStyler meaning-preserving style transfer gates" in panel_text
    assert "stylevec style-signal overfit boundary gates" in panel_text
    assert "Chapter translation style-context gates" in panel_text
    assert "Slima book-MCP beta-reader file gates" in panel_text
    assert "Dialogoi fileType RAG novel-project gates" in panel_text
    assert "Scrivener MCP direct project-edit boundary gates" in panel_text
    assert "Vector-story frame coordinate gates" in panel_text
    assert "Setting runtime document architecture gates" in panel_text
    assert "InkFoundry StateDB RedTeam VoiceSandbox gates" in panel_text
    assert "Co-writing / recursive revision gates" in panel_text
    assert "Hierarchical co-writing story scaffold gates" in panel_text
    assert "Human coauthor edit boundaries" in panel_text
    assert "Recursive reprompt revision loop gates" in panel_text
    assert "Reranker-guided candidate selection gates" in panel_text
    assert "Event-to-sentence realization trace gates" in panel_text
    assert "Entity memory slotfill grounding gates" in panel_text
    assert "Source deconstruction / memory glossary gates" in panel_text
    assert "Book memory-bank context lattice gates" in panel_text
    assert "Spec-driven fiction scene task gates" in panel_text
    assert "TOC-aware source deconstruction gates" in panel_text
    assert "Two-pass context glossary pipeline gates" in panel_text
    assert "Inline author edit markup versioning gates" in panel_text
    assert "Graph memory / retrieval grounding gates" in panel_text
    assert "Long-term author preference memory gates" in panel_text
    assert "Community graph source deconstruction gates" in panel_text
    assert "Dual-level graph vector retrieval gates" in panel_text
    assert "Schema-guided graph extraction gates" in panel_text
    assert "Counterfactual story Graph-RAG gates" in panel_text
    assert "Living codex editorial workbench gates" in panel_text
    assert "Relationship graph global replace gates" in panel_text
    assert "Chinese text processing gates" in panel_text
    assert "Chinese segmentation / keyword gates" in panel_text
    assert "Chinese NER / alias consistency gates" in panel_text
    assert "Chinese text normalization gates" in panel_text
    assert "Chinese correction review gates" in panel_text
    assert "Narrative event / emotion graph gates" in panel_text
    assert "Literary event/entity annotation gates" in panel_text
    assert "Narrative event evolution graph gates" in panel_text
    assert "Sentiment arc / emotion trajectory gates" in panel_text
    assert "Cross-context coreference gates" in panel_text
    assert "Character interaction network gates" in panel_text
    assert "Book NLP / readability / motif gates" in panel_text
    assert "Character quote attribution maps" in panel_text
    assert "Readability pacing metric gates" in panel_text
    assert "Lexical diversity voice audits" in panel_text
    assert "Keyphrase motif extraction gates" in panel_text
    assert "Segmentation / summary / RAG eval gates" in panel_text
    assert "Semantic chunk boundary maps" in panel_text
    assert "Chapter summary anchor gates" in panel_text
    assert "Topic drift maps" in panel_text
    assert "Context faithfulness eval gates" in panel_text
    assert "Retrieval trace observability gates" in panel_text
    assert "Prompt regression eval suites" in panel_text
    assert "Copy similarity / near-duplicate gates" in panel_text
    assert "Source text fingerprint gates" in panel_text
    assert "Fuzzy phrase similarity gates" in panel_text
    assert "Diff-span copy review gates" in panel_text
    assert "MinHash / LSH near-duplicate gates" in panel_text
    assert "SimHash / Hamming similarity gates" in panel_text
    assert "Semantic duplicate cluster gates" in panel_text
    assert "Embedding similarity independence gates" in panel_text
    assert "Stylometry / style overfit gates" in panel_text
    assert "Style-axis diversity fingerprint gates" in panel_text
    assert "Stylometric author fingerprint gates" in panel_text
    assert "Function-word / syntax style gates" in panel_text
    assert "Authorship attribution similarity gates" in panel_text
    assert "Style-overfit regression gates" in panel_text
    assert "Paraphrase independence review gates" in panel_text
    assert "AI-prose fingerprint cluster gates" in panel_text
    assert "Trope / genre independence gates" in panel_text
    assert "Trope inventory similarity gates" in panel_text
    assert "Trope graph expectation map gates" in panel_text
    assert "Trope density novelty-budget gates" in panel_text
    assert "Trope source boundary review gates" in panel_text
    assert "Reader feedback / market positioning gates" in panel_text
    assert "Reader retention review gates" in panel_text
    assert "Serial reader-reward contract gates" in panel_text
    assert "Reader rating signal model gates" in panel_text
    assert "Review spoiler / sentiment corpus gates" in panel_text
    assert "Beta-reader archetype panel gates" in panel_text
    assert "Comp-title market positioning gates" in panel_text
    assert "Local reader-experience editor gates" in panel_text
    assert "Prose lint / grammar copyedit gates" in panel_text
    assert "Prose lint style rule gates" in panel_text
    assert "Grammar spelling copyedit gates" in panel_text
    assert "Copyedit diagnostic triage queue gates" in panel_text
    assert "Reader reward / tri-modal audit gates" in panel_text
    assert "Reader reward channel gates" in panel_text
    assert "Tri-modal workflow validation gates" in panel_text
    assert "Scene promise / serial simulation review gates" in panel_text
    assert "Scene promise mob-review gates" in panel_text
    assert "Webnovel genre tracker gates" in panel_text
    assert "Simulation causal-ledger verification gates" in panel_text
    assert "Writer Git exploration review gates" in panel_text
    assert "Narrative QA / summary / causality gates" in panel_text
    assert "Narrative QA comprehension gates" in panel_text
    assert "Chapter summary alignment gates" in panel_text
    assert "Story question-answer validation gates" in panel_text
    assert "Causal why-explanation gates" in panel_text
    assert "Story commonsense consistency gates" in panel_text
    assert "Query-focused long-summary gates" in panel_text
    assert "Rights / corpus admission gates" in panel_text
    assert "Source license detection gates" in panel_text
    assert "SPDX / REUSE compliance gates" in panel_text
    assert "Public-domain corpus boundaries" in panel_text
    assert "Attribution / derivative-work gates" in panel_text
    assert "Entity redaction / leakage gates" in panel_text
    assert "Source entity redaction gates" in panel_text
    assert "Custom fiction entity label inventories" in panel_text
    assert "Placeholder alias consistency maps" in panel_text
    assert "Proper-noun leakage reviews" in panel_text
    assert "Source import / chapter extraction gates" in panel_text
    assert "Source format import manifests" in panel_text
    assert "PDF layout text extraction gates" in panel_text
    assert "OCR scanned-page import gates" in panel_text
    assert "Document partition chapter detection gates" in panel_text
    assert "Import provenance checksum gates" in panel_text
    assert "EPUB structure / publication QA gates" in panel_text
    assert "EPUB structure validation gates" in panel_text
    assert "Ebook accessibility audit gates" in panel_text
    assert "Front/back matter metadata gates" in panel_text
    assert "TOC navigation consistency gates" in panel_text
    assert "Engineering harness / rights / adaptation gates" in panel_text
    assert "Longgu engineering harness gates" in panel_text
    assert "Prose health live dashboard gates" in panel_text
    assert "Raw story assimilation workflow gates" in panel_text
    assert "Style distillation rights boundaries" in panel_text
    assert "Screenplay AST / YAML adaptation gates" in panel_text
    assert "Fanqie publish dry-run boundaries" in panel_text
    assert "Packet-first style overlay gates" in panel_text
    assert "LoRA style adapter memory-bank gates" in panel_text
    assert "Browser-local story-bible privacy gates" in panel_text
    assert "Jingwei layered canon plugin gates" in panel_text
    assert "Roleplay branchable save/world gates" in panel_text
    assert "Append-only canon POV/promise gates" in panel_text
    assert "Author-keeps-pen diagnostic codex gates" in panel_text
    assert "Spec-driven state/record/publish gates" in panel_text
    assert "Desktop LangGraph memory observability gates" in panel_text
    assert "Lore Forge knowledge-engineering gates" in panel_text
    assert "Layered style profile fusion/eval gates" in panel_text
    assert "Truth File / RAG pyramid audit gates" in panel_text
    assert "Proposal ledger quality gates" in panel_text
    assert "Simulation event-log narrative gates" in panel_text
    assert "Slash-command context tier gates" in panel_text
    assert "Dual-track EPUB manifest gates" in panel_text
    assert "Adaptive quality self-healing gates" in panel_text
    assert "OpenStoryline transition boundaries" in panel_text
    assert "Hierarchical story-tree evaluation gates" in panel_text
    assert "Recurrent plan-memory generation gates" in panel_text
    assert "Bookend closure infill gates" in panel_text
    assert "Strict requirement planning gates" in panel_text
    assert "Canon graph hybrid validation gates" in panel_text
    assert "Local copilot layered-memory gates" in panel_text
    assert "Pending fact canon-promotion gates" in panel_text
    assert "Work corpus reindex autopilot gates" in panel_text
    assert "Memoir story-spine consensus gates" in panel_text
    assert "Map/reduce factual-anchor adaptation gates" in panel_text
    assert "Platform genre style-stamp gates" in panel_text
    assert "Chapter packet promise-debt gates" in panel_text
    assert "Webnovel state-machine graph gates" in panel_text
    assert "Story Knowledge Layer SOT gates" in panel_text
    assert "Local snapshot backup/export gates" in panel_text
    assert "Continuity passport drift-repair gates" in panel_text
    assert "Originality multi-metric report gates" in panel_text
    assert "Semantic stylometric overlap gates" in panel_text
    assert "Human oversight quality gates" in panel_text
    assert "AI-tell pattern review gates" in panel_text
    assert "Naturalization disclaimer gates" in panel_text
    assert "Web similarity scrape-boundary gates" in panel_text
    assert "Fiction skill-agent workbench gates" in panel_text
    assert "Local node-graph lore fix-loop gates" in panel_text
    assert "Uploaded style-learning API boundary gates" in panel_text
    assert "Editorial memory-card graph agent gates" in panel_text
    assert "RAG technique catalog retrieval gates" in panel_text
    assert "Agent architecture catalog workflow gates" in panel_text
    assert "Canonical packet source-promotion gates" in panel_text
    assert "Truth-file dual-audit agent gates" in panel_text
    assert "Long-consistency reverse-RAG retry gates" in panel_text
    assert "Summary-buffer selective RAG memory gates" in panel_text
    assert "Genre-gene capsule market-boundary gates" in panel_text


def test_source_discovery_panel_uses_compact_seed_fallback_and_backend_registry_hydration():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    panel_text = panel.read_text(encoding="utf-8")

    panel_block = panel_text.split("const DEFAULT_GITHUB_REPOSITORY_SEEDS = [", 1)[1].split("\n];", 1)[0]
    fallback_urls = re.findall(r"'(https://github.com/[^']+)'", panel_block)

    assert fallback_urls == [
        "https://github.com/voocel/ainovel-cli",
        "https://github.com/NousResearch/autonovel",
        "https://github.com/MangoLion/plotbunni",
        "https://github.com/zlx362211854/novelforge-agent",
        "https://github.com/MissingDanial/StyleMuse",
        "https://github.com/mert-ozdemirr/sherlock-counterfactual-modular-graph-rag",
        "https://github.com/booknlp/booknlp",
        "https://github.com/google-deepmind/narrativeqa",
    ]
    assert len(fallback_urls) <= 8
    assert "default_github_repository_urls" in panel_text
    assert "default_github_queries" in panel_text
    assert "default_linux_do_rss_urls" in panel_text
    assert "!repositorySeedsEdited && result.default_github_repository_urls?.length" in panel_text
    assert "!githubQueriesEdited && result.default_github_queries?.length" in panel_text
    assert "!linuxDoRssUrlsEdited && result.default_linux_do_rss_urls?.length" in panel_text
    assert "result.default_github_repository_urls.join('\\n')" in panel_text
    assert "result.default_github_queries.join('\\n')" in panel_text
    assert "result.default_linux_do_rss_urls.join('\\n')" in panel_text
    assert "parseLineItems(githubQueries)" in panel_text
    assert "GitHub Search" in panel_text
    assert "Community RSS" in panel_text


def test_source_discovery_panel_has_dynamic_fallback_for_unpinned_hint_groups():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    pattern_pack = repo_root / "backend" / "app" / "references" / "novel-source-pattern-pack-2026-06-10.json"

    panel_text = panel.read_text(encoding="utf-8")
    pack = json.loads(pattern_pack.read_text(encoding="utf-8"))
    explicitly_rendered_fields = set(re.findall(r"patternPackPayload\?\.([a-zA-Z0-9_]+)", panel_text))
    dynamic_hint_fields = [
        key
        for key, value in pack.items()
        if key.endswith("_hints")
        and isinstance(value, list)
        and value
        and key not in explicitly_rendered_fields
    ]

    assert len(dynamic_hint_fields) > 60
    assert "Additional source-discovered gates" in panel_text
    assert "collectAdditionalHintBlocks" in panel_text
    assert "key.endsWith('_hints')" in panel_text
    assert "!PINNED_HINT_KEYS.has(key)" in panel_text


def test_source_discovery_panel_surfaces_workflow_pattern_evidence():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    panel_text = panel.read_text(encoding="utf-8")

    assert "Workflow pattern evidence" in panel_text
    assert "collectWorkflowPatternEvidence" in panel_text
    assert "renderWorkflowPatternEvidence" in panel_text
    assert "WORKFLOW_PATTERN_EVIDENCE_LIMIT" in panel_text
    assert "WORKFLOW_PATTERN_SOURCE_LIMIT" in panel_text
    assert "pattern.top_source_url" in panel_text
    assert "pattern.sources" in panel_text
    assert "source.posture" in panel_text
    assert "pattern-only 静态吸收" in panel_text
    assert "不 clone、不安装、不执行" in panel_text


def test_source_discovery_panel_surfaces_universal_novel_writing_gates():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types_file = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types_file.read_text(encoding="utf-8")

    assert "Universal novel-writing skill gates" in panel_text
    assert "Universal mode-contract gates" in panel_text
    assert "Portable tool policy gates" in panel_text
    assert "Portable story project-structure gates" in panel_text
    assert "Chapter contract / scene beat gates" in panel_text
    assert "Reader promise / micro-payoff gates" in panel_text
    assert "Revision order / natural prose gates" in panel_text
    assert "Fresh-reader pull gates" in panel_text
    assert "Post-draft review checklist gates" in panel_text
    assert "Progress report / continuity write-back gates" in panel_text
    assert "Premise / hook-payoff structure gates" in panel_text
    assert "Scene goal / cost / exit-state gates" in panel_text
    assert "Scene-surface craft gates" in panel_text
    assert "Character / world-rule coherence gates" in panel_text
    assert "Story Skills deterministic continuity gates" in panel_text
    assert "Revision finding / patch strategy gates" in panel_text
    assert "Opening / ending hook integrity gates" in panel_text
    assert "Anti-AI naturalness texture gates" in panel_text
    assert "Genre promise contract matrix gates" in panel_text
    assert "Subgenre-specific ledger gates" in panel_text
    assert "Five-question intake / story promise gates" in panel_text
    assert "Clean manuscript export gates" in panel_text
    assert "Minimal rollback repair-scope gates" in panel_text
    assert "Progressive context-loading gates" in panel_text
    assert "Startup status / context recovery gates" in panel_text
    assert "Author intent / confirmation gates" in panel_text
    assert "universal_novel_mode_contract_gate_hints" in panel_text
    assert "portable_story_project_structure_gate_hints" in panel_text
    assert "chapter_contract_scene_beat_gate_hints" in panel_text
    assert "reader_promise_micro_payoff_gate_hints" in panel_text
    assert "revision_order_natural_prose_gate_hints" in panel_text
    assert "reader_pull_fresh_reader_gate_hints" in panel_text
    assert "post_draft_review_checklist_gate_hints" in panel_text
    assert "progress_report_continuity_writeback_gate_hints" in panel_text
    assert "premise_structure_hook_payoff_gate_hints" in panel_text
    assert "scene_goal_obstacle_cost_exit_gate_hints" in panel_text
    assert "universal_story_engine_scene_pressure_gate_hints" in panel_text
    assert "universal_scene_surface_craft_gate_hints" in panel_text
    assert "universal_character_world_rule_coherence_gate_hints" in panel_text
    assert "story_skills_deterministic_continuity_contract_gate_hints" in panel_text
    assert "better_writing_voice_specificity_preflight_gate_hints" in panel_text
    assert "Better Writing voice specificity preflight gates" in panel_text
    assert "revision_finding_patch_strategy_gate_hints" in panel_text
    assert "opening_ending_hook_integrity_gate_hints" in panel_text
    assert "anti_ai_naturalness_texture_gate_hints" in panel_text
    assert "genre_promise_contract_matrix_gate_hints" in panel_text
    assert "subgenre_specific_ledger_gate_hints" in panel_text
    assert "five_question_intake_story_promise_gate_hints" in panel_text
    assert "universal_export_clean_manuscript_gate_hints" in panel_text
    assert "minimal_rollback_repair_scope_gate_hints" in panel_text
    assert "progressive_context_loading_gate_hints" in panel_text
    assert "startup_status_context_recovery_gate_hints" in panel_text
    assert "author_intent_confirmation_gate_hints" in panel_text
    assert "dynamic_world_tick_info_horizon_gate_hints" in panel_text
    assert "Dynamic world tick / information horizon gates" in panel_text
    assert "universal_portable_tool_policy_gate_hints" in panel_text

    assert "universal_novel_mode_contract_gate_hints?: string[]" in types_text
    assert "universal_portable_tool_policy_gate_hints?: string[]" in types_text
    assert "portable_story_project_structure_gate_hints?: string[]" in types_text
    assert "chapter_contract_scene_beat_gate_hints?: string[]" in types_text
    assert "reader_promise_micro_payoff_gate_hints?: string[]" in types_text
    assert "revision_order_natural_prose_gate_hints?: string[]" in types_text
    assert "reader_pull_fresh_reader_gate_hints?: string[]" in types_text
    assert "post_draft_review_checklist_gate_hints?: string[]" in types_text
    assert "premise_structure_hook_payoff_gate_hints?: string[]" in types_text
    assert "scene_goal_obstacle_cost_exit_gate_hints?: string[]" in types_text
    assert "universal_story_engine_scene_pressure_gate_hints?: string[]" in types_text
    assert "universal_scene_surface_craft_gate_hints?: string[]" in types_text
    assert "universal_character_world_rule_coherence_gate_hints?: string[]" in types_text
    assert "story_skills_deterministic_continuity_contract_gate_hints?: string[]" in types_text
    assert "better_writing_voice_specificity_preflight_gate_hints?: string[]" in types_text
    assert "revision_finding_patch_strategy_gate_hints?: string[]" in types_text
    assert "opening_ending_hook_integrity_gate_hints?: string[]" in types_text
    assert "anti_ai_naturalness_texture_gate_hints?: string[]" in types_text
    assert "genre_promise_contract_matrix_gate_hints?: string[]" in types_text
    assert "subgenre_specific_ledger_gate_hints?: string[]" in types_text
    assert "five_question_intake_story_promise_gate_hints?: string[]" in types_text
    assert "universal_export_clean_manuscript_gate_hints?: string[]" in types_text
    assert "minimal_rollback_repair_scope_gate_hints?: string[]" in types_text
    assert "progressive_context_loading_gate_hints?: string[]" in types_text
    assert "startup_status_context_recovery_gate_hints?: string[]" in types_text
    assert "author_intent_confirmation_gate_hints?: string[]" in types_text
    assert "dynamic_world_tick_info_horizon_gate_hints?: string[]" in types_text


def test_source_discovery_panel_surfaces_eventide_feedback_queue_gate():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types_file = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types_file.read_text(encoding="utf-8")

    assert "Eventide feedback-first lorebook queue gates" in panel_text
    assert "eventide_feedback_first_lorebook_queue_gate_hints" in panel_text
    assert "eventide_feedback_first_lorebook_queue_gate_hints?: string[]" in types_text


def test_source_discovery_panel_surfaces_scheduled_agent_style_qa_gate():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "Scheduled agent style/QA workflow gates" in panel_text
    assert "scheduled_agent_style_qa_workflow_gate_hints" in panel_text
    assert "scheduled_agent_style_qa_workflow_gate_hints?: string[]" in types_text


def test_source_discovery_panel_surfaces_speckit_fiction_scene_task_gates():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "Spec Kit fiction scene-task gates" in panel_text
    assert "Story-bible constitution gates" in panel_text
    assert "Scene outline approval gates" in panel_text
    assert "POV information-asymmetry gates" in panel_text
    assert "Pacing arc / polish-pass gates" in panel_text
    assert "story_bible_constitution_source_gate_hints" in panel_text
    assert "scene_outline_approval_status_gate_hints" in panel_text
    assert "pov_information_asymmetry_schedule_gate_hints" in panel_text
    assert "pacing_arc_polish_pass_gate_hints" in panel_text
    assert "story_bible_constitution_source_gate_hints?: string[]" in types_text
    assert "scene_outline_approval_status_gate_hints?: string[]" in types_text
    assert "pov_information_asymmetry_schedule_gate_hints?: string[]" in types_text
    assert "pacing_arc_polish_pass_gate_hints?: string[]" in types_text


def test_source_discovery_panel_surfaces_local_first_authoring_gates():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "Local-first authoring / revision acceptance gates" in panel_text
    assert "Local-first provider boundary gates" in panel_text
    assert "Suggestion-card non-overwrite gates" in panel_text
    assert "Book view import/export manifest gates" in panel_text
    assert "local_first_provider_boundary_authoring_gate_hints" in panel_text
    assert "suggestion_card_nonoverwrite_revision_gate_hints" in panel_text
    assert "book_view_import_export_manifest_gate_hints" in panel_text
    assert "local_first_provider_boundary_authoring_gate_hints?: string[]" in types_text
    assert "suggestion_card_nonoverwrite_revision_gate_hints?: string[]" in types_text
    assert "book_view_import_export_manifest_gate_hints?: string[]" in types_text


def test_source_discovery_panel_surfaces_chinese_skill_workstation_gates():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "Chinese skill workstation phase-quality gates" in panel_text
    assert "chinese_skill_workstation_phase_quality_gate_hints" in panel_text
    assert "chinese_skill_workstation_phase_quality_gate_hints?: string[]" in types_text


def test_source_discovery_panel_surfaces_saga_tui_adversarial_gates():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "SAGA TUI/adversarial publishing gates" in panel_text
    assert "saga_tui_adversarial_publish_gate_hints" in panel_text
    assert "saga_tui_adversarial_publish_gate_hints?: string[]" in types_text


def test_source_discovery_panel_surfaces_four_agent_quality_loop_gates():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "four_agent_chapter_quality_loop_gate_hints" in panel_text
    assert "four_agent_chapter_quality_loop_gate_hints?: string[]" in types_text


def test_source_discovery_panel_surfaces_deterministic_volume_spec_gates():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "Volume rolling spec-quality gates" in panel_text
    assert "Executor-agnostic instruction checkpoint gates" in panel_text
    assert "volume_rolling_spec_quality_gate_hints" in panel_text
    assert "executor_agnostic_instruction_checkpoint_gate_hints" in panel_text
    assert "volume_rolling_spec_quality_gate_hints?: string[]" in types_text
    assert "executor_agnostic_instruction_checkpoint_gate_hints?: string[]" in types_text


def test_continuation_preview_panel_surfaces_speckit_fiction_warnings():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "Spec Kit 场景任务 gate" in panel_text
    assert "spec_kit_fiction_warnings" in panel_text
    assert "Hook / naturalness gate" in panel_text
    assert "Genre promise contract gate" in panel_text
    assert "Subgenre ledger gate" in panel_text
    assert "hook_naturalness_warnings" in panel_text
    assert "genre_promise_contract_warnings" in panel_text
    assert "subgenre_ledger_warnings" in panel_text
    assert "spec_kit_fiction_warnings: string[]" in types_text
    assert "hook_naturalness_warnings: string[]" in types_text
    assert "genre_promise_contract_warnings: string[]" in types_text
    assert "subgenre_ledger_warnings: string[]" in types_text
    assert "progress_report_continuity_writeback_gate_hints?: string[]" in types_text


def test_continuation_context_preview_panel_surfaces_raw_story_and_iron_law_warnings():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    for field in (
        "raw_story_assimilation_warnings",
        "six_layer_iron_law_warnings",
    ):
        assert field in types_text
        assert field in panel_text
    assert "Raw story assimilation gate" in panel_text
    assert "Six-layer Iron Law gate" in panel_text


def test_continuation_context_preview_panel_surfaces_noveldna_originality_warnings():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    for field in (
        "source_novel_dna_fusion_warnings",
        "originality_guard_warnings",
    ):
        assert f"{field}: string[]" in types_text
        assert field in panel_text

    assert "NovelDNA fusion boundary gate" in panel_text
    assert "Originality guard gate" in panel_text


def test_continuation_context_preview_panel_surfaces_multimetric_similarity_warnings():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    for field in (
        "originality_report_multimetric_warnings",
        "semantic_stylometric_overlap_warnings",
    ):
        assert f"{field}: string[]" in types_text
        assert field in panel_text

    assert "Multi-metric originality report gate" in panel_text
    assert "Semantic stylometric overlap gate" in panel_text


def test_continuation_context_preview_panel_surfaces_quality_safety_warning_buckets():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    for field in (
        "human_oversight_quality_warnings",
        "ai_tell_pattern_warnings",
        "naturalization_boundary_warnings",
        "web_similarity_runtime_boundary_warnings",
    ):
        assert f"{field}: string[]" in types_text
        assert field in panel_text

    assert "Human oversight quality gate" in panel_text
    assert "AI-tell pattern review gate" in panel_text
    assert "Naturalization boundary gate" in panel_text
    assert "Web similarity runtime boundary gate" in panel_text


def test_continuation_context_preview_panel_surfaces_story_engine_warning_bucket():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "story_engine_scene_pressure_warnings: string[]" in types_text
    assert "story_engine_scene_pressure_warnings" in panel_text
    assert "Story engine scene-pressure gate" in panel_text


def test_continuation_context_preview_panel_surfaces_character_world_rule_warning_bucket():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "character_world_rule_coherence_warnings: string[]" in types_text
    assert "character_world_rule_coherence_warnings" in panel_text
    assert "Character / world-rule coherence gate" in panel_text


def test_continuation_context_preview_panel_surfaces_story_skills_continuity_warning_bucket():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "story_skills_continuity_contract_warnings: string[]" in types_text
    assert "story_skills_continuity_contract_warnings" in panel_text
    assert "Story Skills deterministic continuity contract gate" in panel_text


def test_continuation_context_preview_panel_surfaces_better_writing_warning_bucket():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "better_writing_voice_preflight_warnings: string[]" in types_text
    assert "better_writing_voice_preflight_warnings" in panel_text
    assert "Better Writing voice specificity preflight gate" in panel_text



def test_continuation_context_preview_panel_surfaces_universal_gate_warning_buckets():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixContinuationContextPreviewPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "bookRemixBible.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    for field in (
        "portable_project_memory_warnings",
        "post_draft_review_warnings",
        "canonkit_context_pack_warnings",
        "intake_export_rollback_warnings",
        "context_scope_authority_warnings",
        "local_first_authoring_warnings",
        "deterministic_volume_spec_warnings",
    ):
        assert f"{field}: string[]" in types_text
        assert field in panel_text

    for label in (
        "Portable project memory gate",
        "Post-draft review gate",
        "CanonKit context pack gate",
        "Intake/export rollback gate",
        "Context scope authority gate",
        "Local-first authoring gate",
        "Deterministic volume spec gate",
    ):
        assert label in panel_text


def test_source_discovery_panel_supports_local_reference_paths():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    assert "local_reference_paths" in types_text
    assert "default_local_reference_paths" in types_text
    assert "localReferencePaths" in panel_text
    assert "D:/project/universal-novel-writing" in panel_text
    assert "local_reference_paths" in panel_text
    assert "本地静态参考" in panel_text


def test_source_discovery_panel_surfaces_pattern_pack_merge_metadata():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    for field in (
        "merged_pattern_pack_count",
        "preserved_workflow_pattern_count",
        "preserved_hint_key_count",
        "local_reference_coverage_count",
    ):
        assert f"{field}: number" in types_text
        assert field in panel_text

    assert "合并基线" in panel_text
    assert "保留旧门控" in panel_text
    assert "保留提示" in panel_text

    assert "local_reference_coverage" in types_text
    assert "localReferenceCoverage" in panel_text
    assert "????????" in panel_text
