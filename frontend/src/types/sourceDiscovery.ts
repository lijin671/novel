export interface SourceDiscoveryRunRequest {
  github_queries?: string[] | null;
  github_repository_urls?: string[] | null;
  linux_do_rss_urls?: string[] | null;
  per_github_query?: number;
  per_rss_feed?: number;
  write_to_docs?: boolean;
}

export interface SourceDiscoveryCandidate {
  source: string;
  url: string;
  title: string;
  summary: string;
  stars?: number | null;
  license: string;
  family: string;
  posture: string;
  posture_hint?: string;
  risk_flags: string[];
  trust_review?: {
    review_basis?: string;
    flags?: string[];
    posture_hint?: string;
  };
  absorbed_patterns: string[];
  updated_at: string;
  score: number;
}

export interface SourceDiscoveryWorkflowPattern {
  name: string;
  candidate_count: number;
  top_source_url: string;
  posture_hint?: string;
  risk_flags: string[];
  trust_flags?: string[];
  sources: SourceDiscoverySourceSummary[];
}

export interface SourceDiscoverySourceSummary {
  title: string;
  url: string;
  source: string;
  summary: string;
  stars?: number | null;
  license: string;
  posture: string;
  posture_hint?: string;
  risk_flags: string[];
  trust_flags?: string[];
  score: number;
}

export interface SourceDiscoveryPatternPack {
  generated_at?: string | null;
  source_candidate_count?: number;
  source_titles?: string[];
  workflow_patterns?: SourceDiscoveryWorkflowPattern[];
  whole_book_analysis_targets?: string[];
  bible_enrichment_targets?: string[];
  continuation_prompt_hints?: string[];
  continuation_state_hints?: string[];
  style_signature_hints?: string[];
  style_fidelity_hints?: string[];
  structured_generation_hints?: string[];
  card_workbench_hints?: string[];
  context_reference_hints?: string[];
  scene_asset_pipeline_hints?: string[];
  quality_score_loop_hints?: string[];
  voice_fingerprint_hints?: string[];
  anti_slop_audit_hints?: string[];
  publication_pipeline_hints?: string[];
  lorebook_context_hints?: string[];
  author_note_layer_hints?: string[];
  world_state_tracking_hints?: string[];
  memory_snapshot_versioning_hints?: string[];
  inspired_mapping_targets?: string[];
  inspired_prompt_hints?: string[];
  inspired_transformation_hints?: string[];
  inspired_copy_risk_hints?: string[];
  self_review_policy_hints?: string[];
  self_review_gate_hints?: string[];
  chapter_change_package_hints?: string[];
  bookrun_audit_trail_gate_hints?: string[];
  provider_budget_smoke_gate_hints?: string[];
  sidecar_memory_profile_boundary_hints?: string[];
  outline_checkpoint_milestone_gate_hints?: string[];
  language_localization_style_profile_gate_hints?: string[];
  progressive_disclosure_skill_protocol_gate_hints?: string[];
  anti_slop_rulepack_triage_gate_hints?: string[];
  user_modifier_project_blueprint_gate_hints?: string[];
  portable_canon_skill_runtime_gate_hints?: string[];
  staged_outline_chunk_window_gate_hints?: string[];
  wiki_canon_graph_lint_gate_hints?: string[];
  plan_draft_log_verify_loop_gate_hints?: string[];
  mcp_scene_index_revision_boundary_hints?: string[];
  verbalized_sampling_diversity_wiki_gate_hints?: string[];
  agentic_editorial_pipeline_gate_hints?: string[];
  craft_role_pipeline_hints?: string[];
  branching_choice_graph_hints?: string[];
  choice_stats_consequence_gate_hints?: string[];
  delivery_manuscript_assembly_hints?: string[];
  export_format_fidelity_audit_hints?: string[];
  character_dialogue_persona_memory_hints?: string[];
  anti_repetition_prompt_rules_hints?: string[];
  temporal_canon_context_graph_hints?: string[];
  character_interaction_network_gate_hints?: string[];
  character_quote_attribution_map_hints?: string[];
  readability_pacing_metric_gate_hints?: string[];
  lexical_diversity_voice_audit_hints?: string[];
  keyphrase_motif_extraction_hints?: string[];
  semantic_chunk_boundary_map_hints?: string[];
  chapter_summary_anchor_gate_hints?: string[];
  topic_drift_map_hints?: string[];
  context_faithfulness_eval_gate_hints?: string[];
  retrieval_trace_observability_gate_hints?: string[];
  prompt_regression_eval_suite_hints?: string[];
  plotline_thread_tracking_hints?: string[];
  rolling_summary_context_trim_hints?: string[];
  local_first_workspace_hints?: string[];
  prompt_library_hints?: string[];
  scene_level_generation_hints?: string[];
  review_queue_staging_hints?: string[];
  style_guide_layering_hints?: string[];
  entity_schema_custom_fields_hints?: string[];
  content_ref_externalization_hints?: string[];
  graph_healing_hints?: string[];
  contradiction_detection_hints?: string[];
  graph_branching_atomicity_hints?: string[];
  relationship_graph_global_replace_gate_hints?: string[];
  query_lint_contract_hints?: string[];
  premature_ending_guard_hints?: string[];
  layered_memory_model_hints?: string[];
  plot_dependency_graph_hints?: string[];
  plotgrid_scene_matrix_hints?: string[];
  scene_status_dashboard_hints?: string[];
  gradual_reveal_control_hints?: string[];
  setup_payoff_tracking_hints?: string[];
  scene_type_directing_hints?: string[];
  worldpkg_export_hints?: string[];
  alternate_timeline_branching_hints?: string[];
  divergence_guidance_hints?: string[];
  plain_text_project_storage_hints?: string[];
  synopsis_cross_reference_hints?: string[];
  snowflake_premise_expansion_hints?: string[];
  outliner_index_cards_hints?: string[];
  narrative_strand_mapping_hints?: string[];
  character_depth_interview_hints?: string[];
  mindmap_visual_planning_hints?: string[];
  manuscript_export_formats_hints?: string[];
  causal_dramatica_agent_pipeline_hints?: string[];
  capture_distillation_production_gate_hints?: string[];
  skill_orchestrated_chinese_novel_workflow_hints?: string[];
  langgraph_story_state_machine_hints?: string[];
  story_daemon_evolution_loop_hints?: string[];
  local_rag_writing_ide_gate_hints?: string[];
  canon_drift_continuity_qa_gate_hints?: string[];
  patch_replay_manuscript_state_gate_hints?: string[];
  microkernel_skill_plugin_isolation_gate_hints?: string[];
  interactive_reader_writer_loop_gate_hints?: string[];
  abstract_style_learning_skill_gate_hints?: string[];
  impromptu_thread_pool_chapter_gate_hints?: string[];
  offline_inspiration_bank_style_gate_hints?: string[];
  atelier_phase_pipeline_gate_hints?: string[];
  book_mining_genesis_automation_gate_hints?: string[];
  multi_book_autopilot_studio_gate_hints?: string[];
  longrun_commit_projection_health_gate_hints?: string[];
  fresh_context_chapter_iteration_gate_hints?: string[];
  agentwrite_plan_write_pipeline_hints?: string[];
  long_output_length_quality_ruler_hints?: string[];
  long_context_reward_dimension_gate_hints?: string[];
  instance_specific_writing_criteria_gate_hints?: string[];
  material_grounded_query_refinement_hints?: string[];
  hybrid_rubric_pairwise_elo_judge_hints?: string[];
  judge_bias_mitigation_check_hints?: string[];
  plan_reflect_character_chapter_pipeline_hints?: string[];
  human_story_metric_panel_hints?: string[];
  hierarchical_cowriting_story_scaffold_hints?: string[];
  human_coauthor_edit_boundary_hints?: string[];
  recursive_reprompt_revision_loop_hints?: string[];
  reranker_guided_candidate_selection_hints?: string[];
  event_to_sentence_realization_trace_hints?: string[];
  entity_memory_slotfill_grounding_hints?: string[];
  book_memory_bank_context_lattice_hints?: string[];
  spec_driven_fiction_scene_tasks_hints?: string[];
  toc_aware_source_deconstruction_hints?: string[];
  two_pass_context_glossary_pipeline_hints?: string[];
  inline_author_edit_markup_versioning_hints?: string[];
  chapter_split_deconstruction_export_gate_hints?: string[];
  final_prompt_preview_span_revision_gate_hints?: string[];
  project_skill_agent_loop_gate_hints?: string[];
  knowledge_document_writeback_trace_gate_hints?: string[];
  host_instruction_context_boundary_gate_hints?: string[];
  schema_review_revision_recovery_gate_hints?: string[];
  cjk_bm25_context_retrieval_gate_hints?: string[];
  dynamic_architecture_extension_gate_hints?: string[];
  anti_copy_style_rag_gate_hints?: string[];
  living_codex_editorial_workbench_gate_hints?: string[];
  agent_role_profile_workflow_gate_hints?: string[];
  long_term_author_preference_memory_hints?: string[];
  community_graph_source_deconstruction_hints?: string[];
  dual_level_graph_vector_retrieval_hints?: string[];
  schema_guided_graph_extraction_hints?: string[];
  counterfactual_story_graph_rag_gate_hints?: string[];
  chinese_segmentation_keyword_gate_hints?: string[];
  chinese_ner_alias_consistency_gate_hints?: string[];
  chinese_text_normalization_gate_hints?: string[];
  chinese_error_correction_review_gate_hints?: string[];
  literary_event_entity_annotation_gate_hints?: string[];
  narrative_event_evolution_graph_gate_hints?: string[];
  sentiment_arc_emotion_trajectory_gate_hints?: string[];
  cross_context_coreference_gate_hints?: string[];
  source_text_fingerprint_gate_hints?: string[];
  fuzzy_phrase_similarity_gate_hints?: string[];
  diff_span_copy_review_hints?: string[];
  minhash_lsh_near_duplicate_gate_hints?: string[];
  simhash_hamming_similarity_gate_hints?: string[];
  semantic_duplicate_cluster_gate_hints?: string[];
  embedding_similarity_independence_gate_hints?: string[];
  style_axis_diversity_fingerprint_hints?: string[];
  stylometric_author_fingerprint_gate_hints?: string[];
  function_word_syntax_style_gate_hints?: string[];
  authorship_attribution_similarity_gate_hints?: string[];
  style_overfit_regression_gate_hints?: string[];
  paraphrase_independence_review_gate_hints?: string[];
  ai_prose_fingerprint_cluster_gate_hints?: string[];
  trope_inventory_similarity_gate_hints?: string[];
  trope_graph_expectation_map_hints?: string[];
  trope_density_novelty_budget_hints?: string[];
  trope_source_boundary_review_hints?: string[];
  reader_retention_review_gate_hints?: string[];
  serial_reader_reward_contract_gate_hints?: string[];
  reader_rating_signal_model_hints?: string[];
  review_spoiler_sentiment_corpus_hints?: string[];
  beta_reader_archetype_panel_hints?: string[];
  comp_title_market_positioning_hints?: string[];
  local_reader_experience_editor_hints?: string[];
  manuscript_health_ai_prep_gate_hints?: string[];
  anti_statistical_center_chapter_type_gate_hints?: string[];
  prose_lint_style_rule_gate_hints?: string[];
  grammar_spelling_copyedit_gate_hints?: string[];
  copyedit_diagnostic_triage_queue_hints?: string[];
  reader_reward_channel_gate_hints?: string[];
  tri_modal_workflow_validation_gate_hints?: string[];
  scene_promise_mob_review_gate_hints?: string[];
  webnovel_genre_tracker_gate_hints?: string[];
  simulation_causal_ledger_verification_gate_hints?: string[];
  writer_git_exploration_review_gate_hints?: string[];
  narrative_qa_comprehension_gate_hints?: string[];
  chapter_summary_alignment_gate_hints?: string[];
  story_question_answer_validation_gate_hints?: string[];
  causal_why_explanation_gate_hints?: string[];
  story_commonsense_consistency_gate_hints?: string[];
  query_focused_long_summary_gate_hints?: string[];
  source_license_detection_gate_hints?: string[];
  spdx_reuse_compliance_gate_hints?: string[];
  public_domain_corpus_boundary_hints?: string[];
  attribution_derivative_work_gate_hints?: string[];
  source_entity_redaction_gate_hints?: string[];
  custom_entity_label_inventory_hints?: string[];
  placeholder_alias_consistency_map_hints?: string[];
  proper_noun_leakage_review_hints?: string[];
  source_format_import_manifest_hints?: string[];
  pdf_layout_text_extraction_gate_hints?: string[];
  ocr_scanned_page_import_gate_hints?: string[];
  document_partition_chapter_detection_gate_hints?: string[];
  import_provenance_checksum_gate_hints?: string[];
  epub_structure_validation_gate_hints?: string[];
  ebook_accessibility_audit_gate_hints?: string[];
  front_back_matter_metadata_gate_hints?: string[];
  toc_navigation_consistency_gate_hints?: string[];
  safety_constraints?: string[];
}

export interface SourceDiscoveryLedgerResponse {
  generated_at: string;
  candidate_count: number;
  candidates: SourceDiscoveryCandidate[];
  safety_notes: string[];
  fetch_errors: Array<Record<string, string>>;
  pattern_pack: SourceDiscoveryPatternPack;
  written_path?: string | null;
  written_pattern_pack_path?: string | null;
}

export interface SourceDiscoveryPatternPackArtifact {
  found: boolean;
  path?: string | null;
  generated_at?: string | null;
  source_candidate_count: number;
  workflow_pattern_count: number;
  source_titles: string[];
  pattern_pack: SourceDiscoveryPatternPack;
}

export interface SourceDiscoveryLedgerArtifact {
  found: boolean;
  path?: string | null;
  date_slug?: string | null;
  content: string;
}

export interface SourceDiscoveryRefreshPolicy {
  refresh_needed: boolean;
  reason: string;
  generated_at?: string | null;
  age_hours?: number | null;
  max_age_hours: number;
}

export interface SourceDiscoveryRefreshRequest extends SourceDiscoveryRunRequest {
  force?: boolean;
  max_age_hours?: number;
}

export interface SourceDiscoveryRefreshResponse {
  refreshed: boolean;
  refresh_policy_before: SourceDiscoveryRefreshPolicy;
  refresh_policy_after: SourceDiscoveryRefreshPolicy;
  refresh_reason: string;
  candidate_count: number;
  candidates: SourceDiscoveryCandidate[];
  fetch_errors: Array<Record<string, string>>;
  written_path?: string | null;
  written_pattern_pack_path?: string | null;
  pattern_pack: SourceDiscoveryPatternPackArtifact;
  ledger: SourceDiscoveryLedgerArtifact;
}

export interface SourceDiscoveryLatestArtifactResponse {
  pattern_pack: SourceDiscoveryPatternPackArtifact;
  ledger: SourceDiscoveryLedgerArtifact;
  refresh_policy: SourceDiscoveryRefreshPolicy;
  default_github_queries?: string[];
  default_github_repository_urls?: string[];
  default_linux_do_rss_urls?: string[];
}
