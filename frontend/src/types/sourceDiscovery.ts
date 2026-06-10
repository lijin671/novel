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
  plotline_thread_tracking_hints?: string[];
  rolling_summary_context_trim_hints?: string[];
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
}
