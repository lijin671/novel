export type MemoryRetrievalPresetKey =
  | 'balanced_default'
  | 'plot_focused'
  | 'character_focused'
  | 'longform_consistency';

export type PipelineMemoryRetrievalPresetKey =
  | 'keep_current'
  | MemoryRetrievalPresetKey;

export interface MemoryRetrievalConfigResponse {
  version: string;
  scenario_types: Record<string, string[]>;
  supported_memory_types: string[];
  default_scenario_types: Record<string, string[]>;
}

export interface MemoryRetrievalConfigUpdateRequest {
  scenario_types: Record<string, string[] | null>;
}
