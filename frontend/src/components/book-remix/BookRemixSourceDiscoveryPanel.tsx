import { Alert, Button, Card, Empty, Input, List, Space, Tag, Typography, message } from 'antd';
import { ReloadOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { useEffect, useState } from 'react';
import { sourceDiscoveryApi } from '../../services/api';
import type {
  SourceDiscoveryLatestArtifactResponse,
  SourceDiscoveryPatternPack,
  SourceDiscoveryWorkflowPattern,
} from '../../types/sourceDiscovery';

const { Paragraph, Text } = Typography;
const { TextArea } = Input;

const DEFAULT_GITHUB_REPOSITORY_SEEDS = [
  'https://github.com/voocel/ainovel-cli',
  'https://github.com/NousResearch/autonovel',
  'https://github.com/MangoLion/plotbunni',
  'https://github.com/zlx362211854/novelforge-agent',
  'https://github.com/MissingDanial/StyleMuse',
  'https://github.com/mert-ozdemirr/sherlock-counterfactual-modular-graph-rag',
  'https://github.com/booknlp/booknlp',
  'https://github.com/google-deepmind/narrativeqa',
];

const ADDITIONAL_HINT_GROUP_LIMIT = 24;
const WORKFLOW_PATTERN_EVIDENCE_LIMIT = 12;
const WORKFLOW_PATTERN_SOURCE_LIMIT = 3;
const PINNED_HINT_KEYS = new Set([
  'whole_book_analysis_targets',
  'continuation_prompt_hints',
  'style_signature_hints',
  'structured_generation_hints',
  'card_workbench_hints',
  'context_reference_hints',
  'scene_asset_pipeline_hints',
  'publication_pipeline_hints',
  'self_review_policy_hints',
  'continuation_state_hints',
  'style_fidelity_hints',
  'lorebook_context_hints',
  'author_note_layer_hints',
  'world_state_tracking_hints',
  'memory_snapshot_versioning_hints',
  'quality_score_loop_hints',
  'voice_fingerprint_hints',
  'anti_slop_audit_hints',
  'inspired_mapping_targets',
  'inspired_prompt_hints',
  'inspired_transformation_hints',
  'inspired_copy_risk_hints',
  'originality_report_multimetric_gate_hints',
  'semantic_stylometric_overlap_gate_hints',
  'human_oversight_quality_signal_gate_hints',
  'ai_tell_pattern_review_gate_hints',
  'naturalization_detector_disclaimer_gate_hints',
  'web_similarity_scrape_boundary_gate_hints',
  'fiction_skill_agent_workbench_gate_hints',
  'local_node_graph_lore_fix_loop_gate_hints',
  'uploaded_style_learning_api_boundary_gate_hints',
  'editorial_memory_card_graph_agent_gate_hints',
  'genre_inspiration_budget_library_gate_hints',
  'stepwise_local_book_generation_file_gate_hints',
  'radial_subplot_timeline_xray_gate_hints',
  'volume_antipattern_dependency_graph_gate_hints',
  'style_dna_breakpoint_hierarchy_gate_hints',
  'arc_state_foreshadowing_persistence_gate_hints',
  'multi_agent_vector_memory_timeline_gate_hints',
  'versioned_workspace_chapter_index_gate_hints',
  'dual_engine_reader_sandbox_rag_gate_hints',
  'intent_tool_quality_style_checkpoint_gate_hints',
  'loreweave_graph_glossary_translation_gate_hints',
  'mcp_novel_memory_gateway_tool_gate_hints',
  'goink_tool_state_autoreview_gate_hints',
  'sandbox_godmode_branch_simulation_gate_hints',
  'editorial_persona_voice_workshop_gate_hints',
  'story_factory_thousand_chapter_cache_gate_hints',
  'strand_beat_quorum_canon_gate_hints',
  'substrate_spark_canon_promotion_gate_hints',
  'codex_webnovel_plugin_parity_gate_hints',
  'external_agent_api_free_cataloging_gate_hints',
  'rights_safe_source_to_memory_pipeline_gate_hints',
  'desktop_agent_planning_reflection_gate_hints',
  'mega_chapter_genre_layered_memory_gate_hints',
  'l0_l3_memory_skeleton_volume_gate_hints',
  'recursive_scene_reflection_long_context_gate_hints',
  'markdown_ink_export_validation_gate_hints',
  'file_backed_promise_ledger_audit_gate_hints',
  'critique_revision_series_memory_gate_hints',
  'mock_first_multi_agent_continuation_gate_hints',
  'truth_file_write_next_state_update_gate_hints',
  'author_control_context_assembly_gate_hints',
  'craft_scene_concrete_finding_revision_gate_hints',
  'tutorial_case_library_curation_gate_hints',
  'anti_hallucination_strand_weave_review_gate_hints',
  'hierarchical_narrative_memory_os_gate_hints',
  'narrative_canon_version_branch_graph_gate_hints',
  'planner_writer_evaluator_editor_saga_gate_hints',
  'story_weaver_kg_bible_rag_gate_hints',
  'taleforge_memory_continuity_research_gate_hints',
  'ai_flavor_template_shell_cleanup_gate_hints',
  'self_review_gate_hints',
  'chapter_change_package_hints',
  'bookrun_audit_trail_gate_hints',
  'provider_budget_smoke_gate_hints',
  'sidecar_memory_profile_boundary_hints',
  'outline_checkpoint_milestone_gate_hints',
  'language_localization_style_profile_gate_hints',
  'progressive_disclosure_skill_protocol_gate_hints',
  'anti_slop_rulepack_triage_gate_hints',
  'user_modifier_project_blueprint_gate_hints',
  'portable_canon_skill_runtime_gate_hints',
  'staged_outline_chunk_window_gate_hints',
  'wiki_canon_graph_lint_gate_hints',
  'plan_draft_log_verify_loop_gate_hints',
  'mcp_scene_index_revision_boundary_hints',
  'verbalized_sampling_diversity_wiki_gate_hints',
  'agentic_editorial_pipeline_gate_hints',
  'craft_role_pipeline_hints',
  'branching_choice_graph_hints',
  'choice_stats_consequence_gate_hints',
  'delivery_manuscript_assembly_hints',
  'export_format_fidelity_audit_hints',
  'character_dialogue_persona_memory_hints',
  'anti_repetition_prompt_rules_hints',
  'temporal_canon_context_graph_hints',
  'narrative_time_age_trace_gate_hints',
  'plotline_thread_tracking_hints',
  'rolling_summary_context_trim_hints',
  'local_first_workspace_hints',
  'prompt_library_hints',
  'scene_level_generation_hints',
  'review_queue_staging_hints',
  'style_guide_layering_hints',
  'entity_schema_custom_fields_hints',
  'content_ref_externalization_hints',
  'graph_healing_hints',
  'contradiction_detection_hints',
  'graph_branching_atomicity_hints',
  'relationship_graph_global_replace_gate_hints',
  'query_lint_contract_hints',
  'premature_ending_guard_hints',
  'layered_memory_model_hints',
  'plot_dependency_graph_hints',
  'plotgrid_scene_matrix_hints',
  'scene_status_dashboard_hints',
  'gradual_reveal_control_hints',
  'setup_payoff_tracking_hints',
  'scene_type_directing_hints',
  'worldpkg_export_hints',
  'alternate_timeline_branching_hints',
  'divergence_guidance_hints',
  'plain_text_project_storage_hints',
  'synopsis_cross_reference_hints',
  'snowflake_premise_expansion_hints',
  'outliner_index_cards_hints',
  'narrative_strand_mapping_hints',
  'character_depth_interview_hints',
  'mindmap_visual_planning_hints',
  'manuscript_export_formats_hints',
  'causal_dramatica_agent_pipeline_hints',
  'capture_distillation_production_gate_hints',
  'skill_orchestrated_chinese_novel_workflow_hints',
  'langgraph_story_state_machine_hints',
  'story_daemon_evolution_loop_hints',
  'local_rag_writing_ide_gate_hints',
  'canon_drift_continuity_qa_gate_hints',
  'patch_replay_manuscript_state_gate_hints',
  'microkernel_skill_plugin_isolation_gate_hints',
  'interactive_reader_writer_loop_gate_hints',
  'abstract_style_learning_skill_gate_hints',
  'impromptu_thread_pool_chapter_gate_hints',
  'offline_inspiration_bank_style_gate_hints',
  'atelier_phase_pipeline_gate_hints',
  'book_mining_genesis_automation_gate_hints',
  'multi_book_autopilot_studio_gate_hints',
  'longrun_commit_projection_health_gate_hints',
  'fresh_context_chapter_iteration_gate_hints',
  'agentwrite_plan_write_pipeline_hints',
  'long_output_length_quality_ruler_hints',
  'long_context_reward_dimension_gate_hints',
  'instance_specific_writing_criteria_gate_hints',
  'material_grounded_query_refinement_hints',
  'hybrid_rubric_pairwise_elo_judge_hints',
  'judge_bias_mitigation_check_hints',
  'plan_reflect_character_chapter_pipeline_hints',
  'human_story_metric_panel_hints',
  'hierarchical_cowriting_story_scaffold_hints',
  'human_coauthor_edit_boundary_hints',
  'recursive_reprompt_revision_loop_hints',
  'reranker_guided_candidate_selection_hints',
  'event_to_sentence_realization_trace_hints',
  'entity_memory_slotfill_grounding_hints',
  'book_memory_bank_context_lattice_hints',
  'ideation_worksheet_foundation_gate_hints',
  'spec_driven_fiction_scene_tasks_hints',
  'toc_aware_source_deconstruction_hints',
  'two_pass_context_glossary_pipeline_hints',
  'inline_author_edit_markup_versioning_hints',
  'chapter_split_deconstruction_export_gate_hints',
  'final_prompt_preview_span_revision_gate_hints',
  'project_skill_agent_loop_gate_hints',
  'knowledge_document_writeback_trace_gate_hints',
  'host_instruction_context_boundary_gate_hints',
  'schema_review_revision_recovery_gate_hints',
  'cjk_bm25_context_retrieval_gate_hints',
  'dynamic_architecture_extension_gate_hints',
  'anti_copy_style_rag_gate_hints',
  'living_codex_editorial_workbench_gate_hints',
  'agent_role_profile_workflow_gate_hints',
  'confirmed_action_audit_recovery_gate_hints',
  'project_isolated_story_bible_query_gate_hints',
  'work_dna_method_transfer_eval_gate_hints',
  'governed_full_reading_continuation_gate_hints',
  'document_gamebook_branching_adapter_gate_hints',
  'forensic_style_clone_audit_risk_gate_hints',
  'story_import_pattern_revision_gate_hints',
  'consequence_ledger_last_actions_context_gate_hints',
  'creative_writing_multiaxis_provider_gate_hints',
  'system_world_fate_simulation_gate_hints',
  'constraint_harness_review_worktree_gate_hints',
  'state_current_reviewer_loop_gate_hints',
  'versioned_scene_fact_review_pipeline_gate_hints',
  'long_term_author_preference_memory_hints',
  'community_graph_source_deconstruction_hints',
  'dual_level_graph_vector_retrieval_hints',
  'schema_guided_graph_extraction_hints',
  'counterfactual_story_graph_rag_gate_hints',
  'character_knowledge_timeline_gate_hints',
  'chinese_segmentation_keyword_gate_hints',
  'chinese_ner_alias_consistency_gate_hints',
  'chinese_text_normalization_gate_hints',
  'chinese_error_correction_review_gate_hints',
  'literary_event_entity_annotation_gate_hints',
  'narrative_event_evolution_graph_gate_hints',
  'sentiment_arc_emotion_trajectory_gate_hints',
  'cross_context_coreference_gate_hints',
  'character_interaction_network_gate_hints',
  'character_quote_attribution_map_hints',
  'readability_pacing_metric_gate_hints',
  'lexical_diversity_voice_audit_hints',
  'keyphrase_motif_extraction_hints',
  'semantic_chunk_boundary_map_hints',
  'chapter_summary_anchor_gate_hints',
  'topic_drift_map_hints',
  'context_faithfulness_eval_gate_hints',
  'retrieval_trace_observability_gate_hints',
  'prompt_regression_eval_suite_hints',
  'source_text_fingerprint_gate_hints',
  'fuzzy_phrase_similarity_gate_hints',
  'diff_span_copy_review_hints',
  'minhash_lsh_near_duplicate_gate_hints',
  'simhash_hamming_similarity_gate_hints',
  'semantic_duplicate_cluster_gate_hints',
  'embedding_similarity_independence_gate_hints',
  'style_axis_diversity_fingerprint_hints',
  'stylometric_author_fingerprint_gate_hints',
  'function_word_syntax_style_gate_hints',
  'authorship_attribution_similarity_gate_hints',
  'style_overfit_regression_gate_hints',
  'paraphrase_independence_review_gate_hints',
  'ai_prose_fingerprint_cluster_gate_hints',
  'trope_inventory_similarity_gate_hints',
  'trope_graph_expectation_map_hints',
  'trope_density_novelty_budget_hints',
  'trope_source_boundary_review_hints',
  'reader_retention_review_gate_hints',
  'serial_reader_reward_contract_gate_hints',
  'reader_rating_signal_model_hints',
  'review_spoiler_sentiment_corpus_hints',
  'beta_reader_archetype_panel_hints',
  'comp_title_market_positioning_hints',
  'local_reader_experience_editor_hints',
  'manuscript_health_ai_prep_gate_hints',
  'anti_statistical_center_chapter_type_gate_hints',
  'prose_lint_style_rule_gate_hints',
  'grammar_spelling_copyedit_gate_hints',
  'copyedit_diagnostic_triage_queue_hints',
  'reader_reward_channel_gate_hints',
  'tri_modal_workflow_validation_gate_hints',
  'scene_promise_mob_review_gate_hints',
  'webnovel_genre_tracker_gate_hints',
  'simulation_causal_ledger_verification_gate_hints',
  'writer_git_exploration_review_gate_hints',
  'narrative_qa_comprehension_gate_hints',
  'chapter_summary_alignment_gate_hints',
  'story_question_answer_validation_gate_hints',
  'causal_why_explanation_gate_hints',
  'story_commonsense_consistency_gate_hints',
  'query_focused_long_summary_gate_hints',
  'source_license_detection_gate_hints',
  'spdx_reuse_compliance_gate_hints',
  'public_domain_corpus_boundary_hints',
  'attribution_derivative_work_gate_hints',
  'source_entity_redaction_gate_hints',
  'custom_entity_label_inventory_hints',
  'placeholder_alias_consistency_map_hints',
  'proper_noun_leakage_review_hints',
  'source_format_import_manifest_hints',
  'pdf_layout_text_extraction_gate_hints',
  'ocr_scanned_page_import_gate_hints',
  'document_partition_chapter_detection_gate_hints',
  'import_provenance_checksum_gate_hints',
  'epub_structure_validation_gate_hints',
  'ebook_accessibility_audit_gate_hints',
  'front_back_matter_metadata_gate_hints',
  'toc_navigation_consistency_gate_hints',
  'longgu_engineering_harness_gate_hints',
  'prose_health_live_dashboard_gate_hints',
  'raw_story_assimilation_workflow_gate_hints',
  'style_distillation_rights_boundary_gate_hints',
  'screenplay_ast_yaml_adaptation_gate_hints',
  'fanqie_publish_dryrun_boundary_gate_hints',
  'lore_forge_knowledge_engineering_gate_hints',
  'layered_style_profile_fusion_eval_gate_hints',
  'truth_file_rag_pyramid_audit_gate_hints',
  'proposal_accept_ledger_quality_gate_hints',
  'simulated_event_log_narrative_layer_gate_hints',
  'slash_command_context_tier_state_gate_hints',
  'dual_track_epub_manifest_pipeline_gate_hints',
  'adaptive_quality_self_healing_autonomy_gate_hints',
  'open_storyline_media_style_transfer_boundary_gate_hints',
  'hierarchical_story_tree_evaluation_agent_gate_hints',
  'recurrent_plan_memory_generation_gate_hints',
  'bookend_closure_infill_gate_hints',
  'strict_requirement_planning_generation_gate_hints',
  'canon_graph_hybrid_validation_gate_hints',
  'packet_first_style_overlay_context_gate_hints',
  'lora_style_adapter_memory_bank_gate_hints',
  'browser_local_story_bible_privacy_gate_hints',
  'jingwei_layered_canon_plugin_gate_hints',
  'roleplay_branchable_save_world_gate_hints',
  'append_only_canon_pov_promise_gate_hints',
  'author_keeps_pen_diagnostic_codex_gate_hints',
  'spec_driven_state_record_publish_gate_hints',
  'desktop_langgraph_memory_observability_gate_hints',
  'story_state_output_contract_gate_hints',
  'living_document_plan_log_verify_gate_hints',
  'markdown_frontmatter_continuity_engine_gate_hints',
  'story_design_dependency_impact_gate_hints',
  'universal_novel_mode_contract_gate_hints',
  'portable_story_project_structure_gate_hints',
  'chapter_contract_scene_beat_gate_hints',
  'reader_promise_micro_payoff_gate_hints',
  'revision_order_natural_prose_gate_hints',
  'reader_pull_fresh_reader_gate_hints',
  'progress_report_continuity_writeback_gate_hints',
  'premise_structure_hook_payoff_gate_hints',
  'scene_goal_obstacle_cost_exit_gate_hints',
  'revision_finding_patch_strategy_gate_hints',
  'opening_ending_hook_integrity_gate_hints',
  'anti_ai_naturalness_texture_gate_hints',
  'genre_promise_contract_matrix_gate_hints',
  'subgenre_specific_ledger_gate_hints',
  'five_question_intake_story_promise_gate_hints',
  'universal_export_clean_manuscript_gate_hints',
  'minimal_rollback_repair_scope_gate_hints',
  'story_bible_constitution_source_gate_hints',
  'scene_outline_approval_status_gate_hints',
  'pov_information_asymmetry_schedule_gate_hints',
  'pacing_arc_polish_pass_gate_hints',
  'writer_critic_verify_quality_cycle_gate_hints',
  'q15_story_quality_benchmark_gate_hints',
  'local_desktop_manuscript_revision_bible_gate_hints',
  'canonkit_local_canon_drift_context_pack_gate_hints',
  'storyforge_wiki_ingest_lint_graph_gate_hints',
  'agents_room_multistep_story_collaboration_gate_hints',
  'judgemark_literary_criteria_calibration_gate_hints',
  'seven_law_platform_closed_loop_gate_hints',
  'vibe_noveling_skill_agent_save_cat_gate_hints',
  'story_bible_qa_pov_lore_rule_gate_hints',
  'gemini_writer_context_recovery_gate_hints',
  'wikiplots_plot_corpus_boundary_gate_hints',
  'reliquery_reconstructive_recall_vault_gate_hints',
  'novel_studio_accepted_chapter_memory_gate_hints',
  'novelforge_version_safe_human_review_gate_hints',
  'unorthodox_pipeline_stage_retry_gate_hints',
  'writeros_role_validator_boundary_gate_hints',
  'harnessnovel_deconstruct_imitate_gate_hints',
  'novel_rule_auditor_learning_loop_gate_hints',
  'novel_rewriter_copyright_cost_gate_hints',
  'woke_novel_template_resume_cli_gate_hints',
  'nai_multi_agent_rag_consistency_gate_hints',
  'scriptwhisper_scriptyaml_adaptation_gate_hints',
  'novel_audit_11_dimension_rewrite_gate_hints',
  'local_continuation_workstation_context_export_gate_hints',
  'p4_p5_foreshadow_relationship_outline_gate_hints',
  'book_writer_memory_arc_revision_gate_hints',
  'kindle_agent_pipeline_compile_gate_hints',
  'kdp_metadata_chapter_export_gate_hints',
  'dual_model_summary_continuation_session_gate_hints',
  'morpheus_trace_memory_revision_gate_hints',
  'novel_control_chapter_card_writeback_gate_hints',
  'qmai_hybrid_context_memory_acceptance_gate_hints',
  'renovel_tri_model_aligned_rewrite_gate_hints',
  'ai_novel_mindmap_prompt_library_gate_hints',
  'file_based_showrunner_canon_approval_gate_hints',
  'nova_local_version_memory_role_gate_hints',
  'forge_agent_mcp_eval_contract_gate_hints',
  'three_path_graph_diff_recall_gate_hints',
  'layered_parallel_audit_state_machine_gate_hints',
  'possibility_graph_dependency_replay_gate_hints',
  'craft_companion_dual_entry_arbitration_gate_hints',
  'novelwriter_live_manuscript_analytics_gate_hints',
  'lumintree_simulation_tree_category_gate_hints',
  'scrivener_mcp_project_analysis_boundary_gate_hints',
  'kindling_local_outline_reference_import_gate_hints',
  'novelengine_weighted_rag_consistency_gate_hints',
  'public_showrunner_template_release_gate_hints',
  'phase1_style_manual_reference_boundary_gate_hints',
  'six_layer_iron_law_chapter_gate_hints',
  'element_swap_deconstruction_rewrite_pipeline_gate_hints',
  'chapter_progressive_disassembly_checkpoint_gate_hints',
  'quantified_style_learning_confidence_gate_hints',
  'truth_system_chapter_settlement_gate_hints',
  'group_collaboration_conflict_vote_memory_gate_hints',
  'arboris_story_direction_workspace_gate_hints',
  'sdd_seven_step_cross_platform_skill_gate_hints',
  'langgraph_world_outline_review_memory_gate_hints',
  'xiaoshuo_local_canon_skill_studio_gate_hints',
  'director_orchestrator_trace_canonize_gate_hints',
  'book_build_export_delivery_gate_hints',
  'plot_storyline_improvement_epub_chain_gate_hints',
  'fast_structure_content_model_split_gate_hints',
  'openai_compatible_book_api_portability_gate_hints',
  'filesystem_memory_agent_loop_gate_hints',
  'desktop_review_rag_retry_gate_hints',
  'novel_core_knowledge_pack_rag_gate_hints',
  'rag_technique_catalog_context_retrieval_gate_hints',
  'agent_architecture_catalog_workflow_gate_hints',
  'canonical_packet_source_promotion_gate_hints',
  'truth_file_dual_audit_agent_pipeline_gate_hints',
  'long_consistency_reverse_rag_retry_gate_hints',
  'summary_buffer_selective_rag_memory_gate_hints',
  'genre_gene_capsule_market_boundary_gate_hints',
  'phase_acceptance_epub_delivery_gate_hints',
  'local_continuation_memory_export_gate_hints',
  'six_agent_memory_debate_consistency_gate_hints',
  'multi_phase_sensory_continuation_gate_hints',
  'agentic_backstory_verification_rag_gate_hints',
  'voiceprint_private_baseline_drift_gate_hints',
  'margin_guided_long_context_revision_gate_hints',
  'agent_style_rulebook_soft_enforcement_gate_hints',
  'private_person_place_timeline_output_gate_hints',
  'story_os_governed_studio_pipeline_gate_hints',
  'standards_file_workflow_os_gate_hints',
  'obsidian_galley_scene_compile_gate_hints',
  'obsidian_storyteller_world_timeline_gate_hints',
  'obsidian_novelsmith_scene_version_graph_gate_hints',
  'obsidian_draft_bench_scene_history_compile_gate_hints',
  'obsidian_textflow_context_flow_guard_gate_hints',
  'deeplore_lore_retrieval_gap_graph_gate_hints',
  'writer_studio_binder_voice_rag_gate_hints',
  'copilot_webnovel_research_runner_gate_hints',
  'tinystyler_meaning_preserving_style_transfer_gate_hints',
  'stylevec_style_signal_overfit_boundary_gate_hints',
  'chapter_translation_style_context_gate_hints',
  'slima_book_mcp_beta_reader_file_gate_hints',
  'dialogoi_filetype_rag_novel_project_gate_hints',
  'scrivener_mcp_direct_project_edit_boundary_gate_hints',
  'vector_story_frame_coordinate_gate_hints',
  'setting_runtime_document_architecture_gate_hints',
  'inkfoundry_state_db_redteam_voice_sandbox_gate_hints',
  'robot_writers_room_human_card_flow_gate_hints',
  'spire_roleplay_character_privacy_fiction_surface_gate_hints',
  'ai_book_generator_agent_mode_local_key_export_gate_hints',
  'risuai_lorebook_prompt_order_regex_gate_hints',
  'grimodex_codex_attribution_scene_chat_gate_hints',
  'supernovel_architecture_blueprint_state_search_gate_hints',
  'screenplay_realtime_writers_room_media_boundary_gate_hints',
  'nebula_codex_character_knowledge_version_gate_hints',
  'forfiction_theia_story_extension_skill_gate_hints',
  'inkos_truthfile_api_fanfic_imitation_gate_hints',
  'local_copilot_layered_memory_workspace_gate_hints',
  'pending_fact_canon_promotion_graph_gate_hints',
  'work_corpus_reindex_autopilot_gate_hints',
  'memoir_story_spine_consensus_grounding_gate_hints',
  'map_reduce_factual_anchor_adaptation_gate_hints',
]);

function parseSeedUrls(value: string): string[] {
  return value
    .split(/[\n,]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseLineItems(value: string): string[] {
  return value
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function BookRemixSourceDiscoveryPanel() {
  const [value, setValue] = useState<SourceDiscoveryLatestArtifactResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [repositorySeeds, setRepositorySeeds] = useState(DEFAULT_GITHUB_REPOSITORY_SEEDS.join('\n'));
  const [repositorySeedsEdited, setRepositorySeedsEdited] = useState(false);
  const [githubQueries, setGithubQueries] = useState('');
  const [githubQueriesEdited, setGithubQueriesEdited] = useState(false);
  const [linuxDoRssUrls, setLinuxDoRssUrls] = useState('');
  const [linuxDoRssUrlsEdited, setLinuxDoRssUrlsEdited] = useState(false);

  const loadLatest = async () => {
    setLoading(true);
    try {
      const result = await sourceDiscoveryApi.getLatest();
      setValue(result);
      if (!githubQueriesEdited && result.default_github_queries?.length) {
        setGithubQueries(result.default_github_queries.join('\n'));
      }
      if (!repositorySeedsEdited && result.default_github_repository_urls?.length) {
        setRepositorySeeds(result.default_github_repository_urls.join('\n'));
      }
      if (!linuxDoRssUrlsEdited && result.default_linux_do_rss_urls?.length) {
        setLinuxDoRssUrls(result.default_linux_do_rss_urls.join('\n'));
      }
    } finally {
      setLoading(false);
    }
  };

  const runDiscovery = async () => {
    setRunning(true);
    try {
      await sourceDiscoveryApi.runLedger({
        write_to_docs: true,
        github_queries: githubQueriesEdited || githubQueries.trim() ? parseLineItems(githubQueries) : undefined,
        github_repository_urls: parseSeedUrls(repositorySeeds),
        linux_do_rss_urls: linuxDoRssUrlsEdited || linuxDoRssUrls.trim() ? parseSeedUrls(linuxDoRssUrls) : undefined,
      });
      await loadLatest();
      message.success('\u6765\u6e90\u53d1\u73b0\u5df2\u5237\u65b0\uff0c\u65b0\u7684\u6a21\u5f0f\u5305\u4f1a\u88ab\u540e\u7eed Bible / \u7eed\u5199\u8ba1\u5212\u8bfb\u53d6');
    } finally {
      setRunning(false);
    }
  };

  const refreshIfNeeded = async () => {
    setRefreshing(true);
    try {
      const result = await sourceDiscoveryApi.refresh({
        github_queries: githubQueriesEdited || githubQueries.trim() ? parseLineItems(githubQueries) : undefined,
        github_repository_urls: parseSeedUrls(repositorySeeds),
        linux_do_rss_urls: linuxDoRssUrlsEdited || linuxDoRssUrls.trim() ? parseSeedUrls(linuxDoRssUrls) : undefined,
      });
      await loadLatest();
      if (result.refreshed) {
        message.success('\u6765\u6e90\u53d1\u73b0\u5df2\u6309\u65b0\u9c9c\u5ea6\u5237\u65b0');
      } else {
        message.info('\u6765\u6e90\u6a21\u5f0f\u5305\u4ecd\u7136\u65b0\u9c9c\uff0c\u65e0\u9700\u5237\u65b0');
      }
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadLatest();
  }, []);

  const patternPack = value?.pattern_pack;
  const patternPackPayload = patternPack?.pattern_pack;
  const ledger = value?.ledger;
  const refreshPolicy = value?.refresh_policy;
  const found = Boolean(patternPack?.found);
  const refreshNeeded = Boolean(refreshPolicy?.refresh_needed);
  const refreshReasonText: Record<string, string> = {
    pattern_pack_missing: '\u6a21\u5f0f\u5305\u7f3a\u5931',
    pattern_pack_stale: '\u6a21\u5f0f\u5305\u5df2\u8fc7\u671f',
    pattern_pack_fresh: '\u6a21\u5f0f\u5305\u65b0\u9c9c',
    pattern_pack_invalid_timestamp: '\u751f\u6210\u65f6\u95f4\u5f02\u5e38',
  };
  const trustReviewPatterns = (patternPackPayload?.workflow_patterns || [])
    .filter((pattern) => pattern.posture_hint === 'defer-trust-review' || Boolean(pattern.trust_flags?.length));
  const additionalHintBlocks = collectAdditionalHintBlocks(patternPackPayload);
  const workflowPatternEvidence = collectWorkflowPatternEvidence(patternPackPayload?.workflow_patterns);

  return (
    <Card
      title={'Step 0.5 \u00b7 \u6765\u6e90\u53d1\u73b0\u72b6\u6001'}
      extra={(
        <Space wrap>
          <Button icon={<ReloadOutlined />} loading={loading} onClick={() => void loadLatest()}>
            {'\u5237\u65b0\u72b6\u6001'}
          </Button>
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            loading={running}
            onClick={() => void runDiscovery()}
          >
            {'\u5237\u65b0\u6765\u6e90\u53d1\u73b0'}
          </Button>
          <Button
            icon={<ReloadOutlined />}
            loading={refreshing}
            disabled={running}
            onClick={() => void refreshIfNeeded()}
          >
            {'\u6309\u65b0\u9c9c\u5ea6\u5237\u65b0'}
          </Button>
        </Space>
      )}
    >
      {value ? (
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Alert
            type={!found || refreshNeeded ? 'warning' : 'success'}
            showIcon
            message={found ? '\u5df2\u52a0\u8f7d\u516c\u5f00\u6765\u6e90\u6a21\u5f0f\u5305' : '\u5c1a\u672a\u53d1\u73b0\u6301\u4e45\u5316\u6765\u6e90\u6a21\u5f0f\u5305'}
            description={'\u7cfb\u7edf\u53ea\u91c7\u96c6 GitHub / Linux.do \u7684\u516c\u5f00\u5143\u6570\u636e\u548c\u6a21\u5f0f\u6458\u8981\uff0c\u4e0d\u514b\u9686\u3001\u4e0d\u5b89\u88c5\u3001\u4e0d\u6267\u884c\u5916\u90e8\u9879\u76ee\u3002'}
          />

          <Card size="small" title="GitHub \u4ed3\u5e93\u79cd\u5b50">
            <Space direction="vertical" size={8} style={{ width: '100%' }}>
              <Text type="secondary">
                {'\u6bcf\u884c\u6216\u9017\u53f7\u5206\u9694\u4e00\u4e2a\u516c\u5f00 GitHub \u4ed3\u5e93 URL\u3002\u53ea\u8bfb\u53d6\u516c\u5f00\u5143\u6570\u636e\uff0c\u4e0d clone\u3001\u4e0d\u5b89\u88c5\u3001\u4e0d\u6267\u884c\u3002'}
              </Text>
              <TextArea
                rows={3}
                value={repositorySeeds}
                onChange={(event) => {
                  setRepositorySeedsEdited(true);
                  setRepositorySeeds(event.target.value);
                }}
                placeholder="https://github.com/voocel/ainovel-cli"
              />
              <Text type="secondary">
                {`后端默认 seed：${value?.default_github_repository_urls?.length ?? DEFAULT_GITHUB_REPOSITORY_SEEDS.length} 个；手动编辑后本次页面会保留你的输入。`}
              </Text>
            </Space>
          </Card>

          <Card size="small" title="GitHub Search 查询">
            <Space direction="vertical" size={8} style={{ width: '100%' }}>
              <Text type="secondary">
                {'每行一个 GitHub Search 查询。查询内含 in:name,description,readme 这类逗号语法，所以这里只按换行拆分。'}
              </Text>
              <TextArea
                rows={4}
                value={githubQueries}
                onChange={(event) => {
                  setGithubQueriesEdited(true);
                  setGithubQueries(event.target.value);
                }}
                placeholder={'("ai novel" OR "novel writing") in:name,description,readme'}
              />
              <Text type="secondary">
                {`后端默认查询：${value?.default_github_queries?.length ?? 0} 个；清空后刷新会跳过 GitHub Search，只保留显式仓库。`}
              </Text>
            </Space>
          </Card>

          <Card size="small" title="Community RSS 来源">
            <Space direction="vertical" size={8} style={{ width: '100%' }}>
              <Text type="secondary">
                {'每行或逗号分隔一个公开 RSS URL。只读公开摘要，不绕过登录、403、429、WAF 或 CAPTCHA。'}
              </Text>
              <TextArea
                rows={2}
                value={linuxDoRssUrls}
                onChange={(event) => {
                  setLinuxDoRssUrlsEdited(true);
                  setLinuxDoRssUrls(event.target.value);
                }}
                placeholder="https://linux.do/latest.rss"
              />
              <Text type="secondary">
                {`后端默认 RSS：${value?.default_linux_do_rss_urls?.length ?? 0} 个；手动编辑后本次页面会保留你的输入。`}
              </Text>
            </Space>
          </Card>

          <Space wrap>
            <Text type="secondary">{'\u5019\u9009\u6765\u6e90\uff1a'}</Text>
            <Tag color="blue">{patternPack?.source_candidate_count ?? 0}</Tag>
            <Text type="secondary">{'\u5de5\u4f5c\u6d41\u6a21\u5f0f\uff1a'}</Text>
            <Tag color="geekblue">{patternPack?.workflow_pattern_count ?? 0}</Tag>
            <Text type="secondary">{'Ledger \u65e5\u671f\uff1a'}</Text>
            <Tag color={ledger?.date_slug ? 'purple' : 'default'}>{ledger?.date_slug || '\u6682\u65e0'}</Tag>
            <Text type="secondary">{'\u6765\u6e90\u65b0\u9c9c\u5ea6\uff1a'}</Text>
            <Tag color={!found || refreshNeeded ? 'orange' : 'green'}>
              {refreshReasonText[refreshPolicy?.reason || ''] || '\u672a\u77e5'}
            </Tag>
            {typeof refreshPolicy?.age_hours === 'number' ? (
              <Tag color="cyan">{refreshPolicy.age_hours}h / {refreshPolicy.max_age_hours}h</Tag>
            ) : null}
          </Space>

          {patternPack?.source_titles?.length ? (
            <List
              size="small"
              header={<Text strong>{'\u5df2\u5438\u6536\u6765\u6e90'}</Text>}
              dataSource={patternPack.source_titles.slice(0, 8)}
              renderItem={(title) => <List.Item>{title}</List.Item>}
            />
          ) : (
            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="\u6682\u65e0\u6765\u6e90\u6807\u9898" />
          )}

          {trustReviewPatterns.length ? (
            <Card size="small" title="\u6765\u6e90\u53ef\u4fe1\u5ea6\u590d\u6838">
              <List
                size="small"
                dataSource={trustReviewPatterns.slice(0, 6)}
                renderItem={renderTrustReviewPattern}
              />
            </Card>
          ) : null}

          {workflowPatternEvidence.length ? (
            <Card size="small" title="Workflow pattern evidence">
              <Text type="secondary">
                {'证据只用于 pattern-only 静态吸收：不 clone、不安装、不执行，不把外部代码、长 README 或提示词直接导入运行时。'}
              </Text>
              <List
                size="small"
                dataSource={workflowPatternEvidence}
                renderItem={renderWorkflowPatternEvidence}
              />
            </Card>
          ) : null}

          <Space direction="vertical" size={12} style={{ width: '100%' }}>
            {renderHintGroup('Core remix kernel gates', [
              ['Continuation prompt hints', patternPackPayload?.continuation_prompt_hints],
              ['Style signature hints', patternPackPayload?.style_signature_hints],
              ['Structured generation hints', patternPackPayload?.structured_generation_hints],
              ['Card workbench hints', patternPackPayload?.card_workbench_hints],
              ['Context reference hints', patternPackPayload?.context_reference_hints],
              ['Scene asset pipeline hints', patternPackPayload?.scene_asset_pipeline_hints],
              ['Publication pipeline hints', patternPackPayload?.publication_pipeline_hints],
              ['Self-review policy hints', patternPackPayload?.self_review_policy_hints],
            ])}
            {renderHintGroup('Universal novel-writing skill gates', [
              ['Universal mode-contract gates', patternPackPayload?.universal_novel_mode_contract_gate_hints],
              ['Portable story project-structure gates', patternPackPayload?.portable_story_project_structure_gate_hints],
              ['Chapter contract / scene beat gates', patternPackPayload?.chapter_contract_scene_beat_gate_hints],
              ['Reader promise / micro-payoff gates', patternPackPayload?.reader_promise_micro_payoff_gate_hints],
              ['Revision order / natural prose gates', patternPackPayload?.revision_order_natural_prose_gate_hints],
              ['Fresh-reader pull gates', patternPackPayload?.reader_pull_fresh_reader_gate_hints],
              ['Progress report / continuity write-back gates', patternPackPayload?.progress_report_continuity_writeback_gate_hints],
              ['Premise / hook-payoff structure gates', patternPackPayload?.premise_structure_hook_payoff_gate_hints],
              ['Scene goal / cost / exit-state gates', patternPackPayload?.scene_goal_obstacle_cost_exit_gate_hints],
              ['Revision finding / patch strategy gates', patternPackPayload?.revision_finding_patch_strategy_gate_hints],
              ['Opening / ending hook integrity gates', patternPackPayload?.opening_ending_hook_integrity_gate_hints],
              ['Anti-AI naturalness texture gates', patternPackPayload?.anti_ai_naturalness_texture_gate_hints],
              ['Genre promise contract matrix gates', patternPackPayload?.genre_promise_contract_matrix_gate_hints],
              ['Subgenre-specific ledger gates', patternPackPayload?.subgenre_specific_ledger_gate_hints],
              ['Five-question intake / story promise gates', patternPackPayload?.five_question_intake_story_promise_gate_hints],
              ['Clean manuscript export gates', patternPackPayload?.universal_export_clean_manuscript_gate_hints],
              ['Minimal rollback repair-scope gates', patternPackPayload?.minimal_rollback_repair_scope_gate_hints],
            ])}
            {renderHintGroup('Spec Kit fiction scene-task gates', [
              ['Story-bible constitution gates', patternPackPayload?.story_bible_constitution_source_gate_hints],
              ['Scene outline approval gates', patternPackPayload?.scene_outline_approval_status_gate_hints],
              ['POV information-asymmetry gates', patternPackPayload?.pov_information_asymmetry_schedule_gate_hints],
              ['Pacing arc / polish-pass gates', patternPackPayload?.pacing_arc_polish_pass_gate_hints],
            ])}
            {renderHintBlock('Whole-book analysis targets', patternPackPayload?.whole_book_analysis_targets)}
            {renderHintBlock('Continuation state hints', patternPackPayload?.continuation_state_hints)}
            {renderHintBlock('Style fidelity hints', patternPackPayload?.style_fidelity_hints)}
            {renderHintBlock('Lorebook context hints', patternPackPayload?.lorebook_context_hints)}
            {renderHintBlock('Author-note layer hints', patternPackPayload?.author_note_layer_hints)}
            {renderHintBlock('World-state tracking hints', patternPackPayload?.world_state_tracking_hints)}
            {renderHintBlock('Memory snapshot versioning hints', patternPackPayload?.memory_snapshot_versioning_hints)}
            {renderHintBlock('Quality score loop hints', patternPackPayload?.quality_score_loop_hints)}
            {renderHintBlock('Voice fingerprint hints', patternPackPayload?.voice_fingerprint_hints)}
            {renderHintBlock('Anti-slop audit hints', patternPackPayload?.anti_slop_audit_hints)}
            {renderHintBlock('Inspired mapping targets', patternPackPayload?.inspired_mapping_targets)}
            {renderHintBlock('Inspired prompt hints', patternPackPayload?.inspired_prompt_hints)}
            {renderHintBlock('Inspired transformation hints', patternPackPayload?.inspired_transformation_hints)}
            {renderHintBlock('Inspired copy-risk hints', patternPackPayload?.inspired_copy_risk_hints)}
            {renderHintBlock('Self-review gates', patternPackPayload?.self_review_gate_hints)}
            {renderHintBlock('Chapter change package hints', patternPackPayload?.chapter_change_package_hints)}
            {renderHintGroup('BookRun / skill protocol gates', [
              ['BookRun audit trail gates', patternPackPayload?.bookrun_audit_trail_gate_hints],
              ['Provider budget smoke gates', patternPackPayload?.provider_budget_smoke_gate_hints],
              ['Sidecar memory profile boundaries', patternPackPayload?.sidecar_memory_profile_boundary_hints],
              ['Outline checkpoint milestone gates', patternPackPayload?.outline_checkpoint_milestone_gate_hints],
              ['Language localization style profile gates', patternPackPayload?.language_localization_style_profile_gate_hints],
              ['Progressive disclosure skill protocol gates', patternPackPayload?.progressive_disclosure_skill_protocol_gate_hints],
              ['Anti-slop rulepack triage gates', patternPackPayload?.anti_slop_rulepack_triage_gate_hints],
            ])}
            {renderHintGroup('Project workbench / memory diversity gates', [
              ['User modifier project blueprint gates', patternPackPayload?.user_modifier_project_blueprint_gate_hints],
              ['Portable canon skill runtime gates', patternPackPayload?.portable_canon_skill_runtime_gate_hints],
              ['Staged outline chunk window gates', patternPackPayload?.staged_outline_chunk_window_gate_hints],
              ['Wiki canon graph lint gates', patternPackPayload?.wiki_canon_graph_lint_gate_hints],
              ['Plan draft log verify loop gates', patternPackPayload?.plan_draft_log_verify_loop_gate_hints],
              ['MCP scene index revision boundaries', patternPackPayload?.mcp_scene_index_revision_boundary_hints],
              ['Verbalized sampling diversity wiki gates', patternPackPayload?.verbalized_sampling_diversity_wiki_gate_hints],
            ])}
            {renderHintGroup('Authorial agents / interactive delivery gates', [
              ['Agentic editorial pipeline gates', patternPackPayload?.agentic_editorial_pipeline_gate_hints],
              ['Craft role pipeline gates', patternPackPayload?.craft_role_pipeline_hints],
              ['Branching choice graph gates', patternPackPayload?.branching_choice_graph_hints],
              ['Choice stats consequence gates', patternPackPayload?.choice_stats_consequence_gate_hints],
              ['Delivery manuscript assembly gates', patternPackPayload?.delivery_manuscript_assembly_hints],
              ['Export format fidelity audit gates', patternPackPayload?.export_format_fidelity_audit_hints],
            ])}
            {renderHintGroup('Voice / timeline continuity gates', [
              ['Character dialogue persona memory gates', patternPackPayload?.character_dialogue_persona_memory_hints],
              ['Anti-repetition prompt rule gates', patternPackPayload?.anti_repetition_prompt_rules_hints],
              ['Temporal canon context graph gates', patternPackPayload?.temporal_canon_context_graph_hints],
              ['Narrative time / age trace gates', patternPackPayload?.narrative_time_age_trace_gate_hints],
              ['Plotline thread tracking gates', patternPackPayload?.plotline_thread_tracking_hints],
              ['Rolling summary context trim gates', patternPackPayload?.rolling_summary_context_trim_hints],
            ])}
            {renderHintGroup('Workspace / scene planning gates', [
              ['Local-first workspace gates', patternPackPayload?.local_first_workspace_hints],
              ['Prompt library gates', patternPackPayload?.prompt_library_hints],
              ['Scene-level generation gates', patternPackPayload?.scene_level_generation_hints],
              ['Review queue staging gates', patternPackPayload?.review_queue_staging_hints],
              ['Style guide layering gates', patternPackPayload?.style_guide_layering_hints],
              ['Entity schema custom field gates', patternPackPayload?.entity_schema_custom_fields_hints],
              ['ContentRef externalization gates', patternPackPayload?.content_ref_externalization_hints],
              ['Graph healing gates', patternPackPayload?.graph_healing_hints],
              ['Contradiction detection gates', patternPackPayload?.contradiction_detection_hints],
              ['Graph branching atomicity gates', patternPackPayload?.graph_branching_atomicity_hints],
              ['Query lint contract gates', patternPackPayload?.query_lint_contract_hints],
            ])}
            {renderHintGroup('Plotgrid / reveal / branch gates', [
              ['Premature ending guards', patternPackPayload?.premature_ending_guard_hints],
              ['Layered memory model gates', patternPackPayload?.layered_memory_model_hints],
              ['Plot dependency graph gates', patternPackPayload?.plot_dependency_graph_hints],
              ['Plotgrid scene matrix gates', patternPackPayload?.plotgrid_scene_matrix_hints],
              ['Scene status dashboard gates', patternPackPayload?.scene_status_dashboard_hints],
              ['Gradual reveal control gates', patternPackPayload?.gradual_reveal_control_hints],
              ['Setup / payoff tracking gates', patternPackPayload?.setup_payoff_tracking_hints],
              ['Scene type directing gates', patternPackPayload?.scene_type_directing_hints],
              ['WorldPkg export gates', patternPackPayload?.worldpkg_export_hints],
              ['Alternate timeline branching gates', patternPackPayload?.alternate_timeline_branching_hints],
              ['Divergence guidance gates', patternPackPayload?.divergence_guidance_hints],
            ])}
            {renderHintGroup('Mature manuscript planning gates', [
              ['Plain text project storage gates', patternPackPayload?.plain_text_project_storage_hints],
              ['Synopsis cross-reference gates', patternPackPayload?.synopsis_cross_reference_hints],
              ['Snowflake premise expansion gates', patternPackPayload?.snowflake_premise_expansion_hints],
              ['Outliner index-card gates', patternPackPayload?.outliner_index_cards_hints],
              ['Narrative strand mapping gates', patternPackPayload?.narrative_strand_mapping_hints],
              ['Character depth interview gates', patternPackPayload?.character_depth_interview_hints],
              ['Mindmap visual planning gates', patternPackPayload?.mindmap_visual_planning_hints],
              ['Manuscript export format gates', patternPackPayload?.manuscript_export_formats_hints],
            ])}
            {renderHintGroup('Causal state-machine / skill workflow gates', [
              ['Causal Dramatica agent pipeline gates', patternPackPayload?.causal_dramatica_agent_pipeline_hints],
              ['Capture distillation production gates', patternPackPayload?.capture_distillation_production_gate_hints],
              ['Skill-orchestrated Chinese novel workflow gates', patternPackPayload?.skill_orchestrated_chinese_novel_workflow_hints],
              ['LangGraph story state machine gates', patternPackPayload?.langgraph_story_state_machine_hints],
              ['Agent role profile workflow gates', patternPackPayload?.agent_role_profile_workflow_gate_hints],
              ['Confirmed action audit recovery gates', patternPackPayload?.confirmed_action_audit_recovery_gate_hints],
              ['Project-isolated story-bible query gates', patternPackPayload?.project_isolated_story_bible_query_gate_hints],
              ['Work-DNA method transfer/eval gates', patternPackPayload?.work_dna_method_transfer_eval_gate_hints],
              ['Governed full-reading continuation gates', patternPackPayload?.governed_full_reading_continuation_gate_hints],
              ['Document gamebook branching adapter gates', patternPackPayload?.document_gamebook_branching_adapter_gate_hints],
              ['Forensic style clone/audit risk gates', patternPackPayload?.forensic_style_clone_audit_risk_gate_hints],
              ['Story import pattern/revision gates', patternPackPayload?.story_import_pattern_revision_gate_hints],
              ['Consequence ledger last-actions context gates', patternPackPayload?.consequence_ledger_last_actions_context_gate_hints],
              ['Creative writing multi-axis provider gates', patternPackPayload?.creative_writing_multiaxis_provider_gate_hints],
              ['System / World / Fate simulation gates', patternPackPayload?.system_world_fate_simulation_gate_hints],
              ['Constraint harness reviewer/worktree gates', patternPackPayload?.constraint_harness_review_worktree_gate_hints],
              ['State/current reviewer loop gates', patternPackPayload?.state_current_reviewer_loop_gate_hints],
              ['Versioned scene fact/review pipeline gates', patternPackPayload?.versioned_scene_fact_review_pipeline_gate_hints],
              ['Story daemon evolution loop gates', patternPackPayload?.story_daemon_evolution_loop_hints],
            ])}
            {renderHintGroup('Local RAG / canon QA / patch replay gates', [
              ['Local RAG writing IDE gates', patternPackPayload?.local_rag_writing_ide_gate_hints],
              ['Canon drift continuity QA gates', patternPackPayload?.canon_drift_continuity_qa_gate_hints],
              ['Patch replay manuscript state gates', patternPackPayload?.patch_replay_manuscript_state_gate_hints],
              ['Microkernel skill plugin isolation gates', patternPackPayload?.microkernel_skill_plugin_isolation_gate_hints],
              ['Interactive reader-writer loop gates', patternPackPayload?.interactive_reader_writer_loop_gate_hints],
              ['Abstract style learning skill gates', patternPackPayload?.abstract_style_learning_skill_gate_hints],
              ['Living codex editorial workbench gates', patternPackPayload?.living_codex_editorial_workbench_gate_hints],
            ])}
            {renderHintGroup('Impromptu / offline / atelier gates', [
              ['Impromptu thread-pool chapter gates', patternPackPayload?.impromptu_thread_pool_chapter_gate_hints],
              ['Offline inspiration-bank style gates', patternPackPayload?.offline_inspiration_bank_style_gate_hints],
              ['Atelier phase pipeline gates', patternPackPayload?.atelier_phase_pipeline_gate_hints],
            ])}
            {renderHintGroup('Book-mining / autopilot / longrun gates', [
              ['Book mining genesis automation gates', patternPackPayload?.book_mining_genesis_automation_gate_hints],
              ['Multi-book autopilot studio gates', patternPackPayload?.multi_book_autopilot_studio_gate_hints],
              ['Longrun commit projection health gates', patternPackPayload?.longrun_commit_projection_health_gate_hints],
              ['Fresh-context chapter iteration gates', patternPackPayload?.fresh_context_chapter_iteration_gate_hints],
            ])}
            {renderHintGroup('Long-output planning / reward gates', [
              ['AgentWrite plan-write pipeline gates', patternPackPayload?.agentwrite_plan_write_pipeline_hints],
              ['Long-output length quality ruler gates', patternPackPayload?.long_output_length_quality_ruler_hints],
              ['Long-context reward dimension gates', patternPackPayload?.long_context_reward_dimension_gate_hints],
            ])}
            {renderHintGroup('Writing benchmark / judge gates', [
              ['Instance-specific writing criteria gates', patternPackPayload?.instance_specific_writing_criteria_gate_hints],
              ['Material-grounded query refinement gates', patternPackPayload?.material_grounded_query_refinement_hints],
              ['Hybrid rubric pairwise Elo judge gates', patternPackPayload?.hybrid_rubric_pairwise_elo_judge_hints],
              ['Judge bias mitigation checks', patternPackPayload?.judge_bias_mitigation_check_hints],
              ['Plan-reflect character chapter pipeline gates', patternPackPayload?.plan_reflect_character_chapter_pipeline_hints],
              ['Human story metric panel gates', patternPackPayload?.human_story_metric_panel_hints],
              ['Agents Room multi-step story gates', patternPackPayload?.agents_room_multistep_story_collaboration_gate_hints],
              ['Judgemark literary criteria gates', patternPackPayload?.judgemark_literary_criteria_calibration_gate_hints],
              ['Seven-law platform closed-loop gates', patternPackPayload?.seven_law_platform_closed_loop_gate_hints],
              ['Vibe Noveling skill-agent Save-the-Cat gates', patternPackPayload?.vibe_noveling_skill_agent_save_cat_gate_hints],
              ['Story Bible QA POV/lore-rule gates', patternPackPayload?.story_bible_qa_pov_lore_rule_gate_hints],
              ['Gemini Writer context-recovery gates', patternPackPayload?.gemini_writer_context_recovery_gate_hints],
              ['WikiPlots corpus-boundary gates', patternPackPayload?.wikiplots_plot_corpus_boundary_gate_hints],
              ['Reliquery reconstructive-recall vault gates', patternPackPayload?.reliquery_reconstructive_recall_vault_gate_hints],
              ['Novel Studio accepted-chapter memory gates', patternPackPayload?.novel_studio_accepted_chapter_memory_gate_hints],
              ['NovelForge version-safe human-review gates', patternPackPayload?.novelforge_version_safe_human_review_gate_hints],
              ['Unorthodox pipeline stage retry gates', patternPackPayload?.unorthodox_pipeline_stage_retry_gate_hints],
              ['WriterOS role-validator boundary gates', patternPackPayload?.writeros_role_validator_boundary_gate_hints],
              ['harnessNovel deconstruct-imitate gates', patternPackPayload?.harnessnovel_deconstruct_imitate_gate_hints],
              ['Novel rule-auditor learning-loop gates', patternPackPayload?.novel_rule_auditor_learning_loop_gate_hints],
              ['Novel rewriter copyright-cost gates', patternPackPayload?.novel_rewriter_copyright_cost_gate_hints],
              ['woke_novel template-resume CLI gates', patternPackPayload?.woke_novel_template_resume_cli_gate_hints],
              ['Nai multi-agent RAG consistency gates', patternPackPayload?.nai_multi_agent_rag_consistency_gate_hints],
              ['ScriptWhisper ScriptYAML adaptation gates', patternPackPayload?.scriptwhisper_scriptyaml_adaptation_gate_hints],
              ['Novel audit 11-dimension rewrite gates', patternPackPayload?.novel_audit_11_dimension_rewrite_gate_hints],
              ['Local continuation workstation context gates', patternPackPayload?.local_continuation_workstation_context_export_gate_hints],
              ['P4/P5 foreshadow relationship outline gates', patternPackPayload?.p4_p5_foreshadow_relationship_outline_gate_hints],
              ['Book Writer memory-arc revision gates', patternPackPayload?.book_writer_memory_arc_revision_gate_hints],
              ['Kindle agent pipeline compile gates', patternPackPayload?.kindle_agent_pipeline_compile_gate_hints],
              ['KDP metadata chapter export gates', patternPackPayload?.kdp_metadata_chapter_export_gate_hints],
              ['Dual-model summary continuation session gates', patternPackPayload?.dual_model_summary_continuation_session_gate_hints],
              ['Morpheus trace-memory revision gates', patternPackPayload?.morpheus_trace_memory_revision_gate_hints],
              ['Novel Control chapter-card writeback gates', patternPackPayload?.novel_control_chapter_card_writeback_gate_hints],
              ['QMAI hybrid context acceptance gates', patternPackPayload?.qmai_hybrid_context_memory_acceptance_gate_hints],
              ['ReNovel tri-model aligned rewrite gates', patternPackPayload?.renovel_tri_model_aligned_rewrite_gate_hints],
              ['AI Novel mindmap prompt-library gates', patternPackPayload?.ai_novel_mindmap_prompt_library_gate_hints],
              ['File-based showrunner canon approval gates', patternPackPayload?.file_based_showrunner_canon_approval_gate_hints],
              ['Nova local version-memory role gates', patternPackPayload?.nova_local_version_memory_role_gate_hints],
              ['Forge Agent MCP eval contract gates', patternPackPayload?.forge_agent_mcp_eval_contract_gate_hints],
              ['Three-path graph diff recall gates', patternPackPayload?.three_path_graph_diff_recall_gate_hints],
              ['Layered parallel audit state-machine gates', patternPackPayload?.layered_parallel_audit_state_machine_gate_hints],
              ['Possibility graph dependency replay gates', patternPackPayload?.possibility_graph_dependency_replay_gate_hints],
              ['Craft Companion dual-entry arbitration gates', patternPackPayload?.craft_companion_dual_entry_arbitration_gate_hints],
              ['NovelWriter live manuscript analytics gates', patternPackPayload?.novelwriter_live_manuscript_analytics_gate_hints],
              ['LuminTree simulation category gates', patternPackPayload?.lumintree_simulation_tree_category_gate_hints],
              ['Scrivener MCP project analysis boundary gates', patternPackPayload?.scrivener_mcp_project_analysis_boundary_gate_hints],
              ['Kindling local outline reference import gates', patternPackPayload?.kindling_local_outline_reference_import_gate_hints],
              ['NovelEngine weighted RAG consistency gates', patternPackPayload?.novelengine_weighted_rag_consistency_gate_hints],
              ['Public showrunner template release gates', patternPackPayload?.public_showrunner_template_release_gate_hints],
              ['Phase-1 style manual reference boundary gates', patternPackPayload?.phase1_style_manual_reference_boundary_gate_hints],
              ['Six-layer Iron Law chapter gates', patternPackPayload?.six_layer_iron_law_chapter_gate_hints],
              ['Element-swap deconstruction rewrite gates', patternPackPayload?.element_swap_deconstruction_rewrite_pipeline_gate_hints],
              ['Chapter-progressive disassembly checkpoint gates', patternPackPayload?.chapter_progressive_disassembly_checkpoint_gate_hints],
              ['Quantified style-learning confidence gates', patternPackPayload?.quantified_style_learning_confidence_gate_hints],
              ['Truth-system chapter settlement gates', patternPackPayload?.truth_system_chapter_settlement_gate_hints],
              ['Group collaboration conflict-vote memory gates', patternPackPayload?.group_collaboration_conflict_vote_memory_gate_hints],
              ['Arboris story-direction workspace gates', patternPackPayload?.arboris_story_direction_workspace_gate_hints],
              ['SDD seven-step cross-platform skill gates', patternPackPayload?.sdd_seven_step_cross_platform_skill_gate_hints],
              ['LangGraph world-outline-review memory gates', patternPackPayload?.langgraph_world_outline_review_memory_gate_hints],
              ['Xiaoshuo local canon skill-studio gates', patternPackPayload?.xiaoshuo_local_canon_skill_studio_gate_hints],
              ['Director-orchestrator trace canonize gates', patternPackPayload?.director_orchestrator_trace_canonize_gate_hints],
              ['Book build export delivery gates', patternPackPayload?.book_build_export_delivery_gate_hints],
              ['Plot-storyline improvement EPUB chain gates', patternPackPayload?.plot_storyline_improvement_epub_chain_gate_hints],
              ['Fast structure/content model split gates', patternPackPayload?.fast_structure_content_model_split_gate_hints],
              ['OpenAI-compatible book API portability gates', patternPackPayload?.openai_compatible_book_api_portability_gate_hints],
              ['Filesystem memory agent-loop gates', patternPackPayload?.filesystem_memory_agent_loop_gate_hints],
              ['Desktop review RAG retry gates', patternPackPayload?.desktop_review_rag_retry_gate_hints],
              ['Novel-core knowledge-pack RAG gates', patternPackPayload?.novel_core_knowledge_pack_rag_gate_hints],
              ['Agent architecture catalog workflow gates', patternPackPayload?.agent_architecture_catalog_workflow_gate_hints],
              ['Canonical packet source-promotion gates', patternPackPayload?.canonical_packet_source_promotion_gate_hints],
              ['Truth-file dual-audit agent gates', patternPackPayload?.truth_file_dual_audit_agent_pipeline_gate_hints],
              ['Long-consistency reverse-RAG retry gates', patternPackPayload?.long_consistency_reverse_rag_retry_gate_hints],
              ['Summary-buffer selective RAG memory gates', patternPackPayload?.summary_buffer_selective_rag_memory_gate_hints],
              ['Genre-gene capsule market-boundary gates', patternPackPayload?.genre_gene_capsule_market_boundary_gate_hints],
              ['Phase acceptance EPUB delivery gates', patternPackPayload?.phase_acceptance_epub_delivery_gate_hints],
              ['Local continuation memory export gates', patternPackPayload?.local_continuation_memory_export_gate_hints],
              ['Six-agent memory debate consistency gates', patternPackPayload?.six_agent_memory_debate_consistency_gate_hints],
              ['Multi-phase sensory continuation gates', patternPackPayload?.multi_phase_sensory_continuation_gate_hints],
              ['Agentic backstory verification RAG gates', patternPackPayload?.agentic_backstory_verification_rag_gate_hints],
              ['Voiceprint private baseline drift gates', patternPackPayload?.voiceprint_private_baseline_drift_gate_hints],
              ['Margin-guided long-context revision gates', patternPackPayload?.margin_guided_long_context_revision_gate_hints],
              ['Agent Style rulebook soft-enforcement gates', patternPackPayload?.agent_style_rulebook_soft_enforcement_gate_hints],
              ['Person/place/timeline output gates', patternPackPayload?.private_person_place_timeline_output_gate_hints],
              ['Story OS governed studio pipeline gates', patternPackPayload?.story_os_governed_studio_pipeline_gate_hints],
              ['Standards-file workflow OS gates', patternPackPayload?.standards_file_workflow_os_gate_hints],
              ['Obsidian galley scene compile gates', patternPackPayload?.obsidian_galley_scene_compile_gate_hints],
              ['Obsidian storyteller timeline/world gates', patternPackPayload?.obsidian_storyteller_world_timeline_gate_hints],
              ['Obsidian NovelSmith scene version graph gates', patternPackPayload?.obsidian_novelsmith_scene_version_graph_gate_hints],
              ['Obsidian Draft Bench history compile gates', patternPackPayload?.obsidian_draft_bench_scene_history_compile_gate_hints],
              ['Obsidian textFlow context flow gates', patternPackPayload?.obsidian_textflow_context_flow_guard_gate_hints],
              ['DeepLore retrieval gap graph gates', patternPackPayload?.deeplore_lore_retrieval_gap_graph_gate_hints],
              ['Writer Studio binder/voice/RAG gates', patternPackPayload?.writer_studio_binder_voice_rag_gate_hints],
              ['Copilot webnovel research-runner gates', patternPackPayload?.copilot_webnovel_research_runner_gate_hints],
              ['TinyStyler meaning-preserving style transfer gates', patternPackPayload?.tinystyler_meaning_preserving_style_transfer_gate_hints],
              ['stylevec style-signal overfit boundary gates', patternPackPayload?.stylevec_style_signal_overfit_boundary_gate_hints],
              ['Chapter translation style-context gates', patternPackPayload?.chapter_translation_style_context_gate_hints],
              ['Slima book-MCP beta-reader file gates', patternPackPayload?.slima_book_mcp_beta_reader_file_gate_hints],
              ['Dialogoi fileType RAG novel-project gates', patternPackPayload?.dialogoi_filetype_rag_novel_project_gate_hints],
              ['Scrivener MCP direct project-edit boundary gates', patternPackPayload?.scrivener_mcp_direct_project_edit_boundary_gate_hints],
              ['Vector-story frame coordinate gates', patternPackPayload?.vector_story_frame_coordinate_gate_hints],
              ['Setting runtime document architecture gates', patternPackPayload?.setting_runtime_document_architecture_gate_hints],
              ['InkFoundry StateDB RedTeam VoiceSandbox gates', patternPackPayload?.inkfoundry_state_db_redteam_voice_sandbox_gate_hints],
              ['Robot Writers Room human-card flow gates', patternPackPayload?.robot_writers_room_human_card_flow_gate_hints],
              ['Spire roleplay character privacy fiction-surface gates', patternPackPayload?.spire_roleplay_character_privacy_fiction_surface_gate_hints],
              ['AI Book Generator agent-mode local-key export gates', patternPackPayload?.ai_book_generator_agent_mode_local_key_export_gate_hints],
              ['RisuAI lorebook prompt-order regex gates', patternPackPayload?.risuai_lorebook_prompt_order_regex_gate_hints],
              ['Grimodex Codex attribution scene-chat gates', patternPackPayload?.grimodex_codex_attribution_scene_chat_gate_hints],
              ['SuperNovel architecture blueprint state-search gates', patternPackPayload?.supernovel_architecture_blueprint_state_search_gate_hints],
              ['Screenplay realtime writers-room media boundary gates', patternPackPayload?.screenplay_realtime_writers_room_media_boundary_gate_hints],
              ['Nebula Codex character knowledge version gates', patternPackPayload?.nebula_codex_character_knowledge_version_gate_hints],
              ['forFiction Theia story-extension skill gates', patternPackPayload?.forfiction_theia_story_extension_skill_gate_hints],
              ['InkOS truth-file API fanfic/imitation gates', patternPackPayload?.inkos_truthfile_api_fanfic_imitation_gate_hints],
            ])}
            {renderHintGroup('Co-writing / recursive revision gates', [
              ['Hierarchical co-writing story scaffold gates', patternPackPayload?.hierarchical_cowriting_story_scaffold_hints],
              ['Human coauthor edit boundaries', patternPackPayload?.human_coauthor_edit_boundary_hints],
              ['Recursive reprompt revision loop gates', patternPackPayload?.recursive_reprompt_revision_loop_hints],
              ['Reranker-guided candidate selection gates', patternPackPayload?.reranker_guided_candidate_selection_hints],
              ['Event-to-sentence realization trace gates', patternPackPayload?.event_to_sentence_realization_trace_hints],
              ['Entity memory slotfill grounding gates', patternPackPayload?.entity_memory_slotfill_grounding_hints],
            ])}
            {renderHintGroup('Source deconstruction / memory glossary gates', [
              ['Book memory-bank context lattice gates', patternPackPayload?.book_memory_bank_context_lattice_hints],
              ['Spec-driven fiction scene task gates', patternPackPayload?.spec_driven_fiction_scene_tasks_hints],
              ['TOC-aware source deconstruction gates', patternPackPayload?.toc_aware_source_deconstruction_hints],
              ['Two-pass context glossary pipeline gates', patternPackPayload?.two_pass_context_glossary_pipeline_hints],
              ['Inline author edit markup versioning gates', patternPackPayload?.inline_author_edit_markup_versioning_hints],
              ['Chapter split deconstruction export gates', patternPackPayload?.chapter_split_deconstruction_export_gate_hints],
              ['Final-prompt preview span revision gates', patternPackPayload?.final_prompt_preview_span_revision_gate_hints],
              ['Project skill agent-loop gates', patternPackPayload?.project_skill_agent_loop_gate_hints],
              ['Knowledge document writeback trace gates', patternPackPayload?.knowledge_document_writeback_trace_gate_hints],
              ['Host instruction/context boundary gates', patternPackPayload?.host_instruction_context_boundary_gate_hints],
              ['Schema review/revision recovery gates', patternPackPayload?.schema_review_revision_recovery_gate_hints],
              ['Dynamic architecture extension gates', patternPackPayload?.dynamic_architecture_extension_gate_hints],
              ['Anti-copy style RAG gates', patternPackPayload?.anti_copy_style_rag_gate_hints],
            ])}
            {renderHintGroup('Graph memory / retrieval grounding gates', [
              ['Temporal canon context graph gates', patternPackPayload?.temporal_canon_context_graph_hints],
              ['Long-term author preference memory gates', patternPackPayload?.long_term_author_preference_memory_hints],
              ['Community graph source deconstruction gates', patternPackPayload?.community_graph_source_deconstruction_hints],
              ['Dual-level graph vector retrieval gates', patternPackPayload?.dual_level_graph_vector_retrieval_hints],
              ['RAG technique catalog retrieval gates', patternPackPayload?.rag_technique_catalog_context_retrieval_gate_hints],
              ['CJK BM25 context retrieval gates', patternPackPayload?.cjk_bm25_context_retrieval_gate_hints],
              ['Schema-guided graph extraction gates', patternPackPayload?.schema_guided_graph_extraction_hints],
              ['Counterfactual story Graph-RAG gates', patternPackPayload?.counterfactual_story_graph_rag_gate_hints],
              ['Relationship graph global replace gates', patternPackPayload?.relationship_graph_global_replace_gate_hints],
            ])}
            {renderHintGroup('Chinese text processing gates', [
              ['Chinese segmentation / keyword gates', patternPackPayload?.chinese_segmentation_keyword_gate_hints],
              ['Chinese NER / alias consistency gates', patternPackPayload?.chinese_ner_alias_consistency_gate_hints],
              ['Chinese text normalization gates', patternPackPayload?.chinese_text_normalization_gate_hints],
              ['Chinese correction review gates', patternPackPayload?.chinese_error_correction_review_gate_hints],
            ])}
            {renderHintGroup('Narrative event / emotion graph gates', [
              ['Literary event/entity annotation gates', patternPackPayload?.literary_event_entity_annotation_gate_hints],
              ['Narrative event evolution graph gates', patternPackPayload?.narrative_event_evolution_graph_gate_hints],
              ['Sentiment arc / emotion trajectory gates', patternPackPayload?.sentiment_arc_emotion_trajectory_gate_hints],
              ['Cross-context coreference gates', patternPackPayload?.cross_context_coreference_gate_hints],
              ['Character interaction network gates', patternPackPayload?.character_interaction_network_gate_hints],
            ])}
            {renderHintGroup('Book NLP / readability / motif gates', [
              ['Character quote attribution maps', patternPackPayload?.character_quote_attribution_map_hints],
              ['Readability pacing metric gates', patternPackPayload?.readability_pacing_metric_gate_hints],
              ['Lexical diversity voice audits', patternPackPayload?.lexical_diversity_voice_audit_hints],
              ['Keyphrase motif extraction gates', patternPackPayload?.keyphrase_motif_extraction_hints],
            ])}
            {renderHintGroup('Segmentation / summary / RAG eval gates', [
              ['Semantic chunk boundary maps', patternPackPayload?.semantic_chunk_boundary_map_hints],
              ['Chapter summary anchor gates', patternPackPayload?.chapter_summary_anchor_gate_hints],
              ['Topic drift maps', patternPackPayload?.topic_drift_map_hints],
              ['Context faithfulness eval gates', patternPackPayload?.context_faithfulness_eval_gate_hints],
              ['Retrieval trace observability gates', patternPackPayload?.retrieval_trace_observability_gate_hints],
              ['Prompt regression eval suites', patternPackPayload?.prompt_regression_eval_suite_hints],
            ])}
            {renderHintGroup('Copy similarity / near-duplicate gates', [
              ['Source text fingerprint gates', patternPackPayload?.source_text_fingerprint_gate_hints],
              ['Fuzzy phrase similarity gates', patternPackPayload?.fuzzy_phrase_similarity_gate_hints],
              ['Diff-span copy review gates', patternPackPayload?.diff_span_copy_review_hints],
              ['MinHash / LSH near-duplicate gates', patternPackPayload?.minhash_lsh_near_duplicate_gate_hints],
              ['SimHash / Hamming similarity gates', patternPackPayload?.simhash_hamming_similarity_gate_hints],
              ['Semantic duplicate cluster gates', patternPackPayload?.semantic_duplicate_cluster_gate_hints],
              ['Embedding similarity independence gates', patternPackPayload?.embedding_similarity_independence_gate_hints],
            ])}
            {renderHintGroup('Stylometry / style overfit gates', [
              ['Style-axis diversity fingerprint gates', patternPackPayload?.style_axis_diversity_fingerprint_hints],
              ['Stylometric author fingerprint gates', patternPackPayload?.stylometric_author_fingerprint_gate_hints],
              ['Function-word / syntax style gates', patternPackPayload?.function_word_syntax_style_gate_hints],
              ['Authorship attribution similarity gates', patternPackPayload?.authorship_attribution_similarity_gate_hints],
              ['Style-overfit regression gates', patternPackPayload?.style_overfit_regression_gate_hints],
              ['Paraphrase independence review gates', patternPackPayload?.paraphrase_independence_review_gate_hints],
              ['AI-prose fingerprint cluster gates', patternPackPayload?.ai_prose_fingerprint_cluster_gate_hints],
            ])}
            {renderHintGroup('Trope / genre independence gates', [
              ['Trope inventory similarity gates', patternPackPayload?.trope_inventory_similarity_gate_hints],
              ['Trope graph expectation map gates', patternPackPayload?.trope_graph_expectation_map_hints],
              ['Trope density novelty-budget gates', patternPackPayload?.trope_density_novelty_budget_hints],
              ['Trope source boundary review gates', patternPackPayload?.trope_source_boundary_review_hints],
            ])}
            {renderHintGroup('Reader feedback / market positioning gates', [
              ['Reader retention review gates', patternPackPayload?.reader_retention_review_gate_hints],
              ['Serial reader-reward contract gates', patternPackPayload?.serial_reader_reward_contract_gate_hints],
              ['Reader rating signal model gates', patternPackPayload?.reader_rating_signal_model_hints],
              ['Review spoiler / sentiment corpus gates', patternPackPayload?.review_spoiler_sentiment_corpus_hints],
              ['Beta-reader archetype panel gates', patternPackPayload?.beta_reader_archetype_panel_hints],
              ['Comp-title market positioning gates', patternPackPayload?.comp_title_market_positioning_hints],
              ['Local reader-experience editor gates', patternPackPayload?.local_reader_experience_editor_hints],
              ['Manuscript health / AI prep gates', patternPackPayload?.manuscript_health_ai_prep_gate_hints],
              ['Chapter type / anti-statistical-center gates', patternPackPayload?.anti_statistical_center_chapter_type_gate_hints],
            ])}
            {renderHintGroup('Prose lint / grammar copyedit gates', [
              ['Prose lint style rule gates', patternPackPayload?.prose_lint_style_rule_gate_hints],
              ['Grammar spelling copyedit gates', patternPackPayload?.grammar_spelling_copyedit_gate_hints],
              ['Copyedit diagnostic triage queue gates', patternPackPayload?.copyedit_diagnostic_triage_queue_hints],
            ])}
            {renderHintGroup('Reader reward / tri-modal audit gates', [
              ['Reader reward channel gates', patternPackPayload?.reader_reward_channel_gate_hints],
              ['Tri-modal workflow validation gates', patternPackPayload?.tri_modal_workflow_validation_gate_hints],
            ])}
            {renderHintGroup('Scene promise / serial simulation review gates', [
              ['Scene promise mob-review gates', patternPackPayload?.scene_promise_mob_review_gate_hints],
              ['Webnovel genre tracker gates', patternPackPayload?.webnovel_genre_tracker_gate_hints],
              ['Simulation causal-ledger verification gates', patternPackPayload?.simulation_causal_ledger_verification_gate_hints],
              ['Writer Git exploration review gates', patternPackPayload?.writer_git_exploration_review_gate_hints],
            ])}
            {renderHintGroup('Narrative QA / summary / causality gates', [
              ['Narrative QA comprehension gates', patternPackPayload?.narrative_qa_comprehension_gate_hints],
              ['Chapter summary alignment gates', patternPackPayload?.chapter_summary_alignment_gate_hints],
              ['Story question-answer validation gates', patternPackPayload?.story_question_answer_validation_gate_hints],
              ['Causal why-explanation gates', patternPackPayload?.causal_why_explanation_gate_hints],
              ['Story commonsense consistency gates', patternPackPayload?.story_commonsense_consistency_gate_hints],
              ['Query-focused long-summary gates', patternPackPayload?.query_focused_long_summary_gate_hints],
            ])}
            {renderHintGroup('Rights / corpus admission gates', [
              ['Source license detection gates', patternPackPayload?.source_license_detection_gate_hints],
              ['SPDX / REUSE compliance gates', patternPackPayload?.spdx_reuse_compliance_gate_hints],
              ['Public-domain corpus boundaries', patternPackPayload?.public_domain_corpus_boundary_hints],
              ['Attribution / derivative-work gates', patternPackPayload?.attribution_derivative_work_gate_hints],
            ])}
            {renderHintGroup('Entity redaction / leakage gates', [
              ['Source entity redaction gates', patternPackPayload?.source_entity_redaction_gate_hints],
              ['Custom fiction entity label inventories', patternPackPayload?.custom_entity_label_inventory_hints],
              ['Placeholder alias consistency maps', patternPackPayload?.placeholder_alias_consistency_map_hints],
              ['Proper-noun leakage reviews', patternPackPayload?.proper_noun_leakage_review_hints],
            ])}
            {renderHintGroup('Source import / chapter extraction gates', [
              ['Source format import manifests', patternPackPayload?.source_format_import_manifest_hints],
              ['PDF layout text extraction gates', patternPackPayload?.pdf_layout_text_extraction_gate_hints],
              ['OCR scanned-page import gates', patternPackPayload?.ocr_scanned_page_import_gate_hints],
              ['Document partition chapter detection gates', patternPackPayload?.document_partition_chapter_detection_gate_hints],
              ['Import provenance checksum gates', patternPackPayload?.import_provenance_checksum_gate_hints],
            ])}
            {renderHintGroup('EPUB structure / publication QA gates', [
              ['EPUB structure validation gates', patternPackPayload?.epub_structure_validation_gate_hints],
              ['Ebook accessibility audit gates', patternPackPayload?.ebook_accessibility_audit_gate_hints],
              ['Front/back matter metadata gates', patternPackPayload?.front_back_matter_metadata_gate_hints],
              ['TOC navigation consistency gates', patternPackPayload?.toc_navigation_consistency_gate_hints],
            ])}
            {renderHintGroup('Engineering harness / rights / adaptation gates', [
              ['Longgu engineering harness gates', patternPackPayload?.longgu_engineering_harness_gate_hints],
              ['Prose health live dashboard gates', patternPackPayload?.prose_health_live_dashboard_gate_hints],
              ['Raw story assimilation workflow gates', patternPackPayload?.raw_story_assimilation_workflow_gate_hints],
              ['Style distillation rights boundaries', patternPackPayload?.style_distillation_rights_boundary_gate_hints],
              ['Screenplay AST / YAML adaptation gates', patternPackPayload?.screenplay_ast_yaml_adaptation_gate_hints],
              ['Fanqie publish dry-run boundaries', patternPackPayload?.fanqie_publish_dryrun_boundary_gate_hints],
              ['Packet-first style overlay gates', patternPackPayload?.packet_first_style_overlay_context_gate_hints],
              ['LoRA style adapter memory-bank gates', patternPackPayload?.lora_style_adapter_memory_bank_gate_hints],
              ['Browser-local story-bible privacy gates', patternPackPayload?.browser_local_story_bible_privacy_gate_hints],
              ['Jingwei layered canon plugin gates', patternPackPayload?.jingwei_layered_canon_plugin_gate_hints],
              ['Roleplay branchable save/world gates', patternPackPayload?.roleplay_branchable_save_world_gate_hints],
              ['Append-only canon POV/promise gates', patternPackPayload?.append_only_canon_pov_promise_gate_hints],
              ['Author-keeps-pen diagnostic codex gates', patternPackPayload?.author_keeps_pen_diagnostic_codex_gate_hints],
              ['Spec-driven state/record/publish gates', patternPackPayload?.spec_driven_state_record_publish_gate_hints],
              ['Desktop LangGraph memory observability gates', patternPackPayload?.desktop_langgraph_memory_observability_gate_hints],
              ['StoryState output contract gates', patternPackPayload?.story_state_output_contract_gate_hints],
              ['Living document plan/log/verify gates', patternPackPayload?.living_document_plan_log_verify_gate_hints],
              ['Markdown frontmatter continuity engine gates', patternPackPayload?.markdown_frontmatter_continuity_engine_gate_hints],
              ['Story design dependency impact gates', patternPackPayload?.story_design_dependency_impact_gate_hints],
              ['Writer/critic verify quality-cycle gates', patternPackPayload?.writer_critic_verify_quality_cycle_gate_hints],
              ['Q15 story quality benchmark gates', patternPackPayload?.q15_story_quality_benchmark_gate_hints],
              ['Local desktop manuscript revision/bible gates', patternPackPayload?.local_desktop_manuscript_revision_bible_gate_hints],
              ['CanonKit local canon-drift context-pack gates', patternPackPayload?.canonkit_local_canon_drift_context_pack_gate_hints],
              ['Storyforge wiki ingest/lint/graph gates', patternPackPayload?.storyforge_wiki_ingest_lint_graph_gate_hints],
              ['Lore Forge knowledge-engineering gates', patternPackPayload?.lore_forge_knowledge_engineering_gate_hints],
              ['Layered style profile fusion/eval gates', patternPackPayload?.layered_style_profile_fusion_eval_gate_hints],
              ['Truth File / RAG pyramid audit gates', patternPackPayload?.truth_file_rag_pyramid_audit_gate_hints],
              ['Proposal ledger quality gates', patternPackPayload?.proposal_accept_ledger_quality_gate_hints],
              ['Simulation event-log narrative gates', patternPackPayload?.simulated_event_log_narrative_layer_gate_hints],
              ['Slash-command context tier gates', patternPackPayload?.slash_command_context_tier_state_gate_hints],
              ['Dual-track EPUB manifest gates', patternPackPayload?.dual_track_epub_manifest_pipeline_gate_hints],
              ['Adaptive quality self-healing gates', patternPackPayload?.adaptive_quality_self_healing_autonomy_gate_hints],
              ['OpenStoryline transition boundaries', patternPackPayload?.open_storyline_media_style_transfer_boundary_gate_hints],
              ['Hierarchical story-tree evaluation gates', patternPackPayload?.hierarchical_story_tree_evaluation_agent_gate_hints],
              ['Recurrent plan-memory generation gates', patternPackPayload?.recurrent_plan_memory_generation_gate_hints],
              ['Bookend closure infill gates', patternPackPayload?.bookend_closure_infill_gate_hints],
              ['Strict requirement planning gates', patternPackPayload?.strict_requirement_planning_generation_gate_hints],
              ['Canon graph hybrid validation gates', patternPackPayload?.canon_graph_hybrid_validation_gate_hints],
              ['Local copilot layered-memory gates', patternPackPayload?.local_copilot_layered_memory_workspace_gate_hints],
              ['Pending fact canon-promotion gates', patternPackPayload?.pending_fact_canon_promotion_graph_gate_hints],
              ['Work corpus reindex autopilot gates', patternPackPayload?.work_corpus_reindex_autopilot_gate_hints],
              ['Memoir story-spine consensus gates', patternPackPayload?.memoir_story_spine_consensus_grounding_gate_hints],
              ['Map/reduce factual-anchor adaptation gates', patternPackPayload?.map_reduce_factual_anchor_adaptation_gate_hints],
              ['Platform genre style-stamp gates', patternPackPayload?.platform_genre_style_stamp_gate_hints],
              ['Chapter packet promise-debt gates', patternPackPayload?.chapter_packet_promise_debt_audit_gate_hints],
              ['Webnovel state-machine graph gates', patternPackPayload?.webnovel_state_machine_knowledge_graph_gate_hints],
              ['Story Knowledge Layer SOT gates', patternPackPayload?.story_knowledge_layer_sot_adaptation_gate_hints],
              ['Local snapshot backup/export gates', patternPackPayload?.local_snapshot_backup_export_gate_hints],
              ['Continuity passport drift-repair gates', patternPackPayload?.continuity_passport_drift_repair_gate_hints],
              ['Originality multi-metric report gates', patternPackPayload?.originality_report_multimetric_gate_hints],
              ['Semantic stylometric overlap gates', patternPackPayload?.semantic_stylometric_overlap_gate_hints],
              ['Human oversight quality gates', patternPackPayload?.human_oversight_quality_signal_gate_hints],
              ['AI-tell pattern review gates', patternPackPayload?.ai_tell_pattern_review_gate_hints],
              ['Naturalization disclaimer gates', patternPackPayload?.naturalization_detector_disclaimer_gate_hints],
              ['Web similarity scrape-boundary gates', patternPackPayload?.web_similarity_scrape_boundary_gate_hints],
              ['Fiction skill-agent workbench gates', patternPackPayload?.fiction_skill_agent_workbench_gate_hints],
              ['Local node-graph lore fix-loop gates', patternPackPayload?.local_node_graph_lore_fix_loop_gate_hints],
              ['Uploaded style-learning API boundary gates', patternPackPayload?.uploaded_style_learning_api_boundary_gate_hints],
              ['Editorial memory-card graph agent gates', patternPackPayload?.editorial_memory_card_graph_agent_gate_hints],
              ['Genre inspiration budget library gates', patternPackPayload?.genre_inspiration_budget_library_gate_hints],
              ['Stepwise local book-generation file gates', patternPackPayload?.stepwise_local_book_generation_file_gate_hints],
              ['Radial subplot timeline X-ray gates', patternPackPayload?.radial_subplot_timeline_xray_gate_hints],
              ['Volume anti-pattern dependency graph gates', patternPackPayload?.volume_antipattern_dependency_graph_gate_hints],
              ['Style DNA breakpoint hierarchy gates', patternPackPayload?.style_dna_breakpoint_hierarchy_gate_hints],
              ['Arc-state foreshadowing persistence gates', patternPackPayload?.arc_state_foreshadowing_persistence_gate_hints],
              ['Multi-agent vector memory timeline gates', patternPackPayload?.multi_agent_vector_memory_timeline_gate_hints],
              ['Versioned workspace chapter-index gates', patternPackPayload?.versioned_workspace_chapter_index_gate_hints],
              ['Dual-engine reader-sandbox RAG gates', patternPackPayload?.dual_engine_reader_sandbox_rag_gate_hints],
              ['Intent-tool quality style checkpoint gates', patternPackPayload?.intent_tool_quality_style_checkpoint_gate_hints],
              ['LoreWeave graph glossary translation gates', patternPackPayload?.loreweave_graph_glossary_translation_gate_hints],
              ['MCP novel memory gateway tool gates', patternPackPayload?.mcp_novel_memory_gateway_tool_gate_hints],
              ['Goink tool-state auto-review gates', patternPackPayload?.goink_tool_state_autoreview_gate_hints],
              ['Sandbox godmode branch simulation gates', patternPackPayload?.sandbox_godmode_branch_simulation_gate_hints],
              ['Editorial persona voice workshop gates', patternPackPayload?.editorial_persona_voice_workshop_gate_hints],
              ['Story factory thousand-chapter cache gates', patternPackPayload?.story_factory_thousand_chapter_cache_gate_hints],
              ['Strand-beat quorum canon gates', patternPackPayload?.strand_beat_quorum_canon_gate_hints],
              ['Substrate spark canon-promotion gates', patternPackPayload?.substrate_spark_canon_promotion_gate_hints],
              ['Codex webnovel plugin parity gates', patternPackPayload?.codex_webnovel_plugin_parity_gate_hints],
              ['External-agent API-free cataloging gates', patternPackPayload?.external_agent_api_free_cataloging_gate_hints],
              ['Rights-safe source-to-memory pipeline gates', patternPackPayload?.rights_safe_source_to_memory_pipeline_gate_hints],
              ['Desktop-agent planning reflection gates', patternPackPayload?.desktop_agent_planning_reflection_gate_hints],
              ['Mega-chapter genre layered-memory gates', patternPackPayload?.mega_chapter_genre_layered_memory_gate_hints],
              ['L0-L3 memory skeleton volume gates', patternPackPayload?.l0_l3_memory_skeleton_volume_gate_hints],
              ['Recursive scene reflection long-context gates', patternPackPayload?.recursive_scene_reflection_long_context_gate_hints],
              ['Markdown Ink export validation gates', patternPackPayload?.markdown_ink_export_validation_gate_hints],
              ['File-backed promise ledger audit gates', patternPackPayload?.file_backed_promise_ledger_audit_gate_hints],
              ['Critique-revision series-memory gates', patternPackPayload?.critique_revision_series_memory_gate_hints],
              ['Mock-first multi-agent continuation gates', patternPackPayload?.mock_first_multi_agent_continuation_gate_hints],
              ['Truth-file write-next state-update gates', patternPackPayload?.truth_file_write_next_state_update_gate_hints],
              ['Author-control context assembly gates', patternPackPayload?.author_control_context_assembly_gate_hints],
              ['Craft-scene concrete-finding revision gates', patternPackPayload?.craft_scene_concrete_finding_revision_gate_hints],
              ['Tutorial case-library curation gates', patternPackPayload?.tutorial_case_library_curation_gate_hints],
              ['Anti-hallucination strand-weave review gates', patternPackPayload?.anti_hallucination_strand_weave_review_gate_hints],
              ['Hierarchical narrative memory OS gates', patternPackPayload?.hierarchical_narrative_memory_os_gate_hints],
              ['Narrative canon branch graph gates', patternPackPayload?.narrative_canon_version_branch_graph_gate_hints],
              ['Planner/writer/evaluator/editor saga gates', patternPackPayload?.planner_writer_evaluator_editor_saga_gate_hints],
              ['Story-Weaver KG / bible / RAG gates', patternPackPayload?.story_weaver_kg_bible_rag_gate_hints],
              ['TaleForge memory continuity research gates', patternPackPayload?.taleforge_memory_continuity_research_gate_hints],
              ['AI-flavor template-shell cleanup gates', patternPackPayload?.ai_flavor_template_shell_cleanup_gate_hints],
            ])}
            {renderHintGroup('Additional source-discovered gates', additionalHintBlocks)}
          </Space>

          {ledger?.content ? (
            <Paragraph
              copyable={{ text: ledger.content }}
              style={{
                whiteSpace: 'pre-wrap',
                maxHeight: 180,
                overflow: 'auto',
                padding: 12,
                border: '1px solid var(--color-border)',
                borderRadius: 8,
                background: 'var(--color-fill-quaternary)',
                marginBottom: 0,
              }}
            >
              {ledger.content.slice(0, 1600)}
              {ledger.content.length > 1600 ? '\n\n......' : ''}
            </Paragraph>
          ) : null}
        </Space>
      ) : (
        <Empty description="\u6b63\u5728\u8bfb\u53d6\u6765\u6e90\u53d1\u73b0\u72b6\u6001" />
      )}
    </Card>
  );
}

function renderHintBlock(title: string, items?: string[]) {
  if (!items?.length) {
    return null;
  }

  return (
    <Card size="small" title={title}>
      <List
        size="small"
        dataSource={items.slice(0, 5)}
        renderItem={(item) => <List.Item>{item}</List.Item>}
      />
    </Card>
  );
}

function renderHintGroup(title: string, blocks: Array<[string, string[] | undefined]>) {
  const visibleBlocks = blocks.filter(([, items]) => Boolean(items?.length));
  if (!visibleBlocks.length) {
    return null;
  }

  return (
    <Card size="small" title={title}>
      <Space direction="vertical" size={12} style={{ width: '100%' }}>
        {visibleBlocks.map(([blockTitle, items]) => renderHintBlock(blockTitle, items))}
      </Space>
    </Card>
  );
}

function collectAdditionalHintBlocks(patternPack?: SourceDiscoveryPatternPack | null): Array<[string, string[]]> {
  if (!patternPack) {
    return [];
  }

  const payload = patternPack as Record<string, unknown>;
  return Object.keys(payload)
    .filter((key) => key.endsWith('_hints') && !PINNED_HINT_KEYS.has(key))
    .sort()
    .map((key): [string, string[]] | null => {
      const value = payload[key];
      const items = Array.isArray(value)
        ? value.filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
        : [];
      if (!items.length) {
        return null;
      }
      return [formatHintTitle(key), items.slice(0, 3)];
    })
    .filter((block): block is [string, string[]] => Boolean(block))
    .slice(0, ADDITIONAL_HINT_GROUP_LIMIT);
}

function formatHintTitle(key: string) {
  const base = key.replace(/_hints$/, '').replace(/_/g, ' ');
  return base.replace(/\b\w/g, (char) => char.toUpperCase());
}

function collectWorkflowPatternEvidence(patterns?: SourceDiscoveryWorkflowPattern[]) {
  return [...(patterns || [])]
    .filter((pattern) => pattern.name && pattern.candidate_count > 0)
    .sort((left, right) => right.candidate_count - left.candidate_count || left.name.localeCompare(right.name))
    .slice(0, WORKFLOW_PATTERN_EVIDENCE_LIMIT);
}

function renderWorkflowPatternEvidence(pattern: SourceDiscoveryWorkflowPattern) {
  const sources = pattern.sources || [];
  const flags = [...(pattern.trust_flags || []), ...(pattern.risk_flags || [])];

  return (
    <List.Item>
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        <Space wrap>
          <Text strong>{pattern.name}</Text>
          <Tag color="blue">{'candidates'} {pattern.candidate_count}</Tag>
          {pattern.posture_hint ? <Tag color="purple">{pattern.posture_hint}</Tag> : null}
          {flags.slice(0, 4).map((flag) => (
            <Tag key={`pattern-evidence-${pattern.name}-${flag}`} color="volcano">{flag}</Tag>
          ))}
        </Space>
        {pattern.top_source_url ? (
          <Text type="secondary" copyable={{ text: pattern.top_source_url }}>
            {pattern.top_source_url}
          </Text>
        ) : null}
        {sources.length ? (
          <Space direction="vertical" size={2}>
            {sources.slice(0, WORKFLOW_PATTERN_SOURCE_LIMIT).map((source) => (
              <Text key={`${pattern.name}-${source.url}`} type="secondary">
                {source.title} · {source.posture} · score {source.score}
              </Text>
            ))}
          </Space>
        ) : null}
      </Space>
    </List.Item>
  );
}

function renderTrustReviewPattern(pattern: SourceDiscoveryWorkflowPattern) {
  const trustFlags = pattern.trust_flags || [];
  const riskFlags = pattern.risk_flags || [];
  const needsReview = pattern.posture_hint === 'defer-trust-review';

  return (
    <List.Item>
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        <Space wrap>
          <Text strong>{pattern.name}</Text>
          <Tag color={needsReview ? 'orange' : 'green'}>
            {needsReview ? '\u6682\u7f13\u5438\u6536\uff0c\u5148\u590d\u6838' : '\u5143\u6570\u636e\u521d\u7b5b'}
          </Tag>
          <Tag color="blue">{'\u5019\u9009'} {pattern.candidate_count}</Tag>
        </Space>
        <Space wrap>
          {trustFlags.length ? trustFlags.slice(0, 5).map((flag) => (
            <Tag key={`trust-${pattern.name}-${flag}`} color="volcano">{flag}</Tag>
          )) : <Tag color="green">trust_flags:none</Tag>}
          {riskFlags.slice(0, 4).map((flag) => (
            <Tag key={`risk-${pattern.name}-${flag}`} color="red">risk:{flag}</Tag>
          ))}
        </Space>
        {pattern.top_source_url ? (
          <Text type="secondary" copyable={{ text: pattern.top_source_url }}>
            {pattern.top_source_url}
          </Text>
        ) : null}
      </Space>
    </List.Item>
  );
}
