export type BookRemixBibleGenerationStatus =
  | 'pending'
  | 'running'
  | 'generated'
  | 'failed'
  | 'confirmed';

export type BookRemixContinuationPlanStatus = 'draft' | 'confirmed';

export interface BookRemixBible {
  id: string;
  project_id: string;
  source_task_id?: string | null;
  generation_status: BookRemixBibleGenerationStatus;
  source_chapter_count: number;
  world_rules: Record<string, unknown>;
  character_cards: Array<Record<string, unknown>>;
  organizations: Array<Record<string, unknown>>;
  timeline: Array<Record<string, unknown>>;
  story_arcs: Array<Record<string, unknown>>;
  foreshadows: Array<Record<string, unknown>>;
  style_signature: Record<string, unknown>;
  hard_constraints: Array<Record<string, unknown>>;
  conflicts: Array<Record<string, unknown>>;
  generation_notes: string[];
  chapter_change_packages: Array<Record<string, unknown>>;
  confirmed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface BookRemixBibleUpdatePayload {
  character_cards?: Array<Record<string, unknown>>;
  timeline?: Array<Record<string, unknown>>;
  story_arcs?: Array<Record<string, unknown>>;
  foreshadows?: Array<Record<string, unknown>>;
  hard_constraints?: Array<Record<string, unknown>>;
}

export interface BookRemixContinuationPlan {
  id: string;
  project_id: string;
  bible_id?: string | null;
  status: BookRemixContinuationPlanStatus;
  summary?: string | null;
  stage_goals: Array<Record<string, unknown>>;
  beats: Array<Record<string, unknown>>;
  priority_hooks: Array<Record<string, unknown>>;
  guardrails: Array<Record<string, unknown>>;
  confirmed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface BookRemixContinuationPlanGeneratePayload {
  user_direction: string;
}

export interface BookRemixContinuationPlanUpdatePayload {
  summary?: string;
  stage_goals?: Array<Record<string, unknown>>;
  beats?: Array<Record<string, unknown>>;
  priority_hooks?: Array<Record<string, unknown>>;
  guardrails?: Array<Record<string, unknown>>;
}

export interface BookRemixContinuationContextPreview {
  project_id: string;
  has_context: boolean;
  context: string;
  context_length: number;
  context_estimated_tokens: number;
  context_budget_risk: 'low' | 'medium' | 'high';
  lineage_confirmed: boolean;
  reason?: string | null;
  source_pattern_pack_loaded: boolean;
  activated_sections: Array<{ key: string; summary: string }>;
  active_source_patterns: string[];
  context_warnings: string[];
  production_control_axes: string[];
  production_acceptance_steps: string[];
  production_warnings: string[];
  chapter_progress_report_gap_count: number;
  chapter_progress_report_gaps: Array<Record<string, unknown>>;
  genre_tracker_warnings: string[];
  entity_arc_timeline_risks: string[];
  source_analysis_coverage_percent: number;
  missing_source_analysis_chapters: string[];
  disassembly_checkpoint_warnings: string[];
  mode_contract_axes: Record<string, string>;
  mode_contract_warnings: string[];
  chapter_contract_warnings: string[];
  production_handoff_warnings: string[];
  reader_pull_warnings: string[];
  spec_kit_fiction_warnings: string[];
  hook_naturalness_warnings: string[];
  genre_promise_contract_warnings: string[];
  subgenre_ledger_warnings: string[];
  progress_report_continuity_writeback_gate_hints?: string[];
  continuity_questions: string[];
  promise_payoff_debts: Array<Record<string, string>>;
  scene_state_snapshot: Array<Record<string, string>>;
  canon_drift_risks: string[];
}

export interface BookRemixChapterChangePackage {
  type?: string | null;
  source?: string | null;
  chapter_id?: string | null;
  chapter_number?: number | null;
  chapter_title?: string | null;
  summary?: string | null;
  timeline_delta?: Array<Record<string, unknown>>;
  character_state_changes?: Array<Record<string, unknown>>;
  foreshadow_changes?: Array<Record<string, unknown>>;
  plan_progress?: Array<Record<string, unknown>>;
  changed_sections?: string[];
  guardrail_check?: {
    applied?: boolean;
    attempts?: number;
    initial_passed?: boolean;
    final_passed?: boolean;
    violations?: Array<{
      type?: string;
      severity?: string;
      description?: string;
      context?: string;
      position?: number;
    }>;
  } | null;
  [key: string]: unknown;
}

export interface BookRemixChapterChangePackageList {
  project_id: string;
  package_count: number;
  offset: number;
  limit: number;
  items: BookRemixChapterChangePackage[];
}

export interface BookRemixAnalysisCoverageChapter {
  chapter_id: string;
  chapter_number: number;
  chapter_title: string;
  status?: string | null;
}

export type BookRemixAnalysisCoverageAction =
  | 'restore_source_chapter'
  | 'sync_existing_analysis'
  | 'wait_running_analysis'
  | 'fill_chapter_content'
  | 'queue_analysis';

export interface BookRemixAnalysisCoverageActionPlanItem {
  action: BookRemixAnalysisCoverageAction;
  chapter_numbers: number[];
  chapter_count: number;
  reason: string;
}

export type BookRemixContinuationRiskLevel = 'low' | 'medium' | 'high';

export interface BookRemixContinuationRisk {
  level: BookRemixContinuationRiskLevel;
  label: string;
  can_continue: boolean;
  blocking_chapter_numbers: number[];
  warning_chapter_numbers: number[];
  reasons: string[];
  reason_labels: string[];
  message: string;
}

export interface BookRemixAnalysisCoverage {
  project_id: string;
  source_chapter_count: number;
  source_chapters_count: number;
  analyzed_chapter_count: number;
  chapter_change_package_count: number;
  analysis_coverage_percent: number;
  change_package_coverage_percent: number;
  fully_analyzed: boolean;
  fully_synced: boolean;
  missing_source_chapters: number[];
  missing_analysis_chapters: BookRemixAnalysisCoverageChapter[];
  missing_change_package_chapters: BookRemixAnalysisCoverageChapter[];
  analysis_action_plan: BookRemixAnalysisCoverageActionPlanItem[];
  continuation_risk?: BookRemixContinuationRisk;
}

export interface BookRemixStartMissingAnalysisResult {
  project_id: string;
  target_chapter_numbers: number[];
  total_started: number;
  total_skipped_running: number;
  total_skipped_no_content: number;
  total_synced_existing: number;
  synced_existing_chapters: number[];
  started_tasks: Record<string, Record<string, unknown>>;
}

export interface BookRemixContinuationProgressSummary {
  project_id: string;
  package_count: number;
  chapter_range: {
    start?: number | null;
    end?: number | null;
  };
  timeline_progression: Array<Record<string, unknown>>;
  latest_character_states: Array<Record<string, unknown>>;
  emotional_progression: Array<Record<string, unknown>>;
  resolved_hooks: string[];
  open_hooks: string[];
  completed_plan_beats: string[];
  pending_plan_beats: string[];
}
