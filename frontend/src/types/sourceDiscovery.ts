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
  inspired_mapping_targets?: string[];
  inspired_prompt_hints?: string[];
  inspired_transformation_hints?: string[];
  inspired_copy_risk_hints?: string[];
  self_review_policy_hints?: string[];
  self_review_gate_hints?: string[];
  chapter_change_package_hints?: string[];
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
