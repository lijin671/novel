import type { BookRemixBibleGenerationStatus } from './bookRemixBible';

export type BookRemixMode = 'continuation' | 'inspired';
export type BookRemixTaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type BookRemixWarningLevel = 'info' | 'warning' | 'error';

export interface BookRemixWarning {
  code: string;
  message: string;
  level: BookRemixWarningLevel;
}

export interface BookRemixProjectSuggestion {
  title: string;
  description?: string;
  theme?: string;
  genre?: string;
  narrative_perspective: string;
  target_words: number;
}

export interface BookRemixTask {
  task_id: string;
  remix_mode: BookRemixMode;
  status: BookRemixTaskStatus;
  progress: number;
  message?: string;
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface BookRemixChapterPreview {
  title: string;
  chapter_number: number;
  word_count: number;
  summary?: string;
}

export interface BookRemixSeedMapping {
  source_name: string;
  occurrence_count: number;
  sample_context?: string;
  suggested_target?: string;
  rewrite_hint?: string;
}

export interface BookRemixInspiredSeedProfile {
  characters: BookRemixSeedMapping[];
  organizations: BookRemixSeedMapping[];
  abilities: BookRemixSeedMapping[];
  world_elements: BookRemixSeedMapping[];
  plot_threads: BookRemixSeedMapping[];
}

export interface BookRemixPreview {
  task_id: string;
  remix_mode: BookRemixMode;
  project_suggestion: BookRemixProjectSuggestion;
  detected_total_chapters: number;
  total_words: number;
  chapters: BookRemixChapterPreview[];
  warnings: BookRemixWarning[];
  inspired_seed_profile?: BookRemixInspiredSeedProfile | null;
}

export interface BookRemixCreateProjectPayload {
  project_suggestion: BookRemixProjectSuggestion;
}

export interface BookRemixRefreshContinuationPayload {
  replace_pending_outlines?: boolean;
}

export interface BookRemixRefreshContinuationResult {
  success: boolean;
  project_id: string;
  source_chapter_count: number;
  refreshed_style_id?: number | null;
  deleted_outlines: number;
  deleted_chapters: number;
  message: string;
}

export interface BookRemixCreateProjectResult {
  success: boolean;
  project_id: string;
  remix_mode: BookRemixMode;
  total_chapters: number;
  total_words: number;
  bible_generation_started: boolean;
  bible_generation_status?: BookRemixBibleGenerationStatus | null;
  prepared_style_id?: number | null;
  analysis_started: boolean;
  analysis_task_count: number;
  message: string;
}
