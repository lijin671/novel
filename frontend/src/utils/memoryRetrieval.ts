import type {
  MemoryRetrievalConfigResponse,
  MemoryRetrievalPresetKey,
  PipelineMemoryRetrievalPresetKey,
} from '../types/memoryRetrieval';

export interface MemoryRetrievalPresetDefinition {
  key: MemoryRetrievalPresetKey;
  title: string;
  description: string;
  scenarioTypes?: Record<string, string[]>;
}

export interface PipelineMemoryRetrievalOption {
  value: PipelineMemoryRetrievalPresetKey;
  label: string;
  description: string;
}

export const MEMORY_RETRIEVAL_PRESETS: MemoryRetrievalPresetDefinition[] = [
  {
    key: 'balanced_default',
    title: '\u5747\u8861\u9ed8\u8ba4',
    description: '\u4f7f\u7528\u540e\u7aef\u9ed8\u8ba4\u767d\u540d\u5355\uff0c\u9002\u5408\u5927\u591a\u6570\u9879\u76ee\u3002',
  },
  {
    key: 'plot_focused',
    title: '\u805a\u7126\u5267\u60c5',
    description: '\u6536\u7f29\u53ec\u56de\u5230\u60c5\u8282\u63a8\u8fdb\u3001\u4f0f\u7b14\u548c\u7ae0\u8282\u627f\u63a5\u76f8\u5173\u8bb0\u5fc6\u3002',
    scenarioTypes: {
      chapter_generation: ['chapter_summary', 'foreshadow', 'plot_point'],
      character_context: ['character_event', 'chapter_summary'],
      plot_context: ['plot_point', 'foreshadow', 'hook'],
    },
  },
  {
    key: 'character_focused',
    title: '\u5f3a\u89d2\u8272\u6001',
    description: '\u5f3a\u5316\u89d2\u8272\u4e8b\u4ef6\u3001\u72b6\u6001\u53d8\u5316\u548c\u4eba\u7269\u6267\u884c\u903b\u8f91\u7684\u53ec\u56de\u3002',
    scenarioTypes: {
      chapter_generation: ['chapter_summary', 'character_event', 'plot_point'],
      character_context: ['character_event', 'chapter_summary', 'plot_point'],
      plot_context: ['chapter_summary', 'plot_point', 'character_event'],
    },
  },
  {
    key: 'longform_consistency',
    title: '\u957f\u7bc7\u4e00\u81f4\u6027',
    description: '\u5f3a\u5316\u7ae0\u8282\u627f\u63a5\u3001\u4f0f\u7b14\u72b6\u6001\u3001\u89d2\u8272\u4e8b\u4ef6\u4e0e\u60c5\u8282\u95ed\u73af\uff0c\u9002\u5408\u957f\u7bc7\u7eed\u5199\u3002',
    scenarioTypes: {
      chapter_generation: ['chapter_summary', 'foreshadow', 'hook', 'plot_point', 'character_event'],
      character_context: ['character_event', 'chapter_summary', 'plot_point', 'foreshadow'],
      plot_context: ['plot_point', 'hook', 'foreshadow', 'chapter_summary', 'character_event'],
    },
  },
];

export const PIPELINE_MEMORY_RETRIEVAL_OPTIONS: PipelineMemoryRetrievalOption[] = [
  {
    value: 'keep_current',
    label: '\u4fdd\u6301\u5f53\u524d\u8bbe\u7f6e',
    description: '\u4e0d\u6539\u5f53\u524d\u8d26\u53f7\u7684\u8bb0\u5fc6\u68c0\u7d22\u767d\u540d\u5355\u3002',
  },
  ...MEMORY_RETRIEVAL_PRESETS.map((preset) => ({
    value: preset.key,
    label: preset.title,
    description: preset.description,
  })),
];

export const getMemoryRetrievalPresetTitle = (
  presetKey: MemoryRetrievalPresetKey | PipelineMemoryRetrievalPresetKey
) => {
  if (presetKey === 'keep_current') {
    return '\u4fdd\u6301\u5f53\u524d\u8bbe\u7f6e';
  }
  return (
    MEMORY_RETRIEVAL_PRESETS.find((preset) => preset.key === presetKey)?.title ||
    presetKey
  );
};

export const normalizeMemoryTypes = (values: string[], supportedTypes: string[]) => {
  const orderMap = new Map(supportedTypes.map((type, index) => [type, index]));
  const filteredValues = values.filter((value) => supportedTypes.includes(value));
  return Array.from(new Set(filteredValues)).sort((left, right) => {
    const leftOrder = orderMap.get(left) ?? Number.MAX_SAFE_INTEGER;
    const rightOrder = orderMap.get(right) ?? Number.MAX_SAFE_INTEGER;
    if (leftOrder !== rightOrder) {
      return leftOrder - rightOrder;
    }
    return left.localeCompare(right, 'zh-CN');
  });
};

export const normalizeScenarioTypes = (
  scenarioTypes: Record<string, string[]>,
  supportedTypes: string[]
) => {
  const normalizedEntries: Array<[string, string[]]> = Object.entries(scenarioTypes).map(
    ([scenario, values]) => [
      scenario,
      normalizeMemoryTypes(values || [], supportedTypes),
    ]
  );
  normalizedEntries.sort(([left], [right]) => left.localeCompare(right, 'zh-CN'));
  return Object.fromEntries(normalizedEntries) as Record<string, string[]>;
};

export const normalizeScenarioTypesForKeys = (
  scenarioTypes: Record<string, string[]>,
  supportedTypes: string[],
  scenarioKeys: string[]
) => {
  const completedScenarioTypes = scenarioKeys.reduce<Record<string, string[]>>(
    (accumulator, scenario) => {
      accumulator[scenario] = scenarioTypes[scenario] || [];
      return accumulator;
    },
    {}
  );
  return normalizeScenarioTypes(completedScenarioTypes, supportedTypes);
};

export const buildMemoryRetrievalPresetScenarioTypes = (
  presetKey: MemoryRetrievalPresetKey,
  config: MemoryRetrievalConfigResponse
) => {
  const scenarioKeys = Array.from(
    new Set([
      ...Object.keys(config.default_scenario_types),
      ...Object.keys(config.scenario_types),
    ])
  );
  const defaultScenarioTypes = normalizeScenarioTypesForKeys(
    config.default_scenario_types,
    config.supported_memory_types,
    scenarioKeys
  );
  const preset = MEMORY_RETRIEVAL_PRESETS.find((item) => item.key === presetKey);

  if (!preset?.scenarioTypes) {
    return defaultScenarioTypes;
  }

  const mergedScenarioTypes = Object.entries(preset.scenarioTypes).reduce<Record<string, string[]>>(
    (accumulator, [scenario, values]) => {
      accumulator[scenario] = normalizeMemoryTypes(values, config.supported_memory_types);
      return accumulator;
    },
    { ...defaultScenarioTypes }
  );

  return normalizeScenarioTypesForKeys(
    mergedScenarioTypes,
    config.supported_memory_types,
    scenarioKeys
  );
};
