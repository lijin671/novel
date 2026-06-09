import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Col,
  Empty,
  Input,
  InputNumber,
  List,
  Modal,
  Progress,
  Radio,
  Row,
  Select,
  Space,
  Spin,
  Steps,
  Tag,
  Typography,
  Upload,
  message,
} from 'antd';
import type { UploadFile } from 'antd/es/upload/interface';
import {
  CopyOutlined,
  InboxOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  RobotOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import BookRemixAnalysisCoveragePanel from '../components/book-remix/BookRemixAnalysisCoveragePanel';
import BookRemixBibleReview from '../components/book-remix/BookRemixBibleReview';
import BookRemixChapterChangePackageAuditPanel from '../components/book-remix/BookRemixChapterChangePackageAuditPanel';
import BookRemixContinuationPlanPanel from '../components/book-remix/BookRemixContinuationPlanPanel';
import BookRemixContinuationContextPreviewPanel from '../components/book-remix/BookRemixContinuationContextPreviewPanel';
import BookRemixContinuationProgressSummaryPanel from '../components/book-remix/BookRemixContinuationProgressSummaryPanel';
import BookRemixSourceDiscoveryPanel from '../components/book-remix/BookRemixSourceDiscoveryPanel';
import { bookRemixApi, chapterApi, outlineApi, projectApi, writingStyleApi } from '../services/api';
import type { GenerateOutlineResponse } from '../types';
import type {
  BookRemixInspiredSeedProfile,
  BookRemixMode,
  BookRemixPreview,
  BookRemixSeedMapping,
  BookRemixTask,
} from '../types/bookRemix';
import type {
  BookRemixBible,
  BookRemixBibleUpdatePayload,
  BookRemixAnalysisCoverage,
  BookRemixChapterChangePackageList,
  BookRemixContinuationPlan,
  BookRemixContinuationPlanUpdatePayload,
  BookRemixContinuationContextPreview,
  BookRemixContinuationProgressSummary,
  BookRemixStartMissingAnalysisResult,
} from '../types/bookRemixBible';

const { Text, Paragraph } = Typography;
const { Dragger } = Upload;
const { TextArea } = Input;

type InspiredRemixStrength = 'light' | 'medium' | 'strong';
type InspiredSeedGroupKey = keyof BookRemixInspiredSeedProfile;

const MODE_META: Record<BookRemixMode, { title: string; description: string; tag: string }> = {
  continuation: {
    title: '续写模式',
    description: '创建分析工作台后，继续沿着原书结尾向后生成新的剧情和章节骨架。',
    tag: '拆书续写',
  },
  inspired: {
    title: '同类创作模式',
    description: '创建分析工作台后，派生一个独立新项目，保留题材气质和爽点，生成全新的故事骨架。',
    tag: '同类创作',
  },
};

const INSPIRED_STRENGTH_OPTIONS: Array<{ value: InspiredRemixStrength; label: string }> = [
  { value: 'light', label: '轻变体' },
  { value: 'medium', label: '中变体' },
  { value: 'strong', label: '强变体' },
];

const INSPIRED_STRENGTH_GUIDE: Record<
  InspiredRemixStrength,
  {
    label: string;
    summary: string;
    instruction: string;
  }
> = {
  light: {
    label: '轻变体',
    summary: '保留题材气质和主线爽点，但替换主要名字、组织称呼与部分关键桥段。',
    instruction: '整体仍保留同类题材氛围，但必须替换主要人物、组织名称和若干关键事件包装。',
  },
  medium: {
    label: '中变体',
    summary: '保留题材优势，重排主要矛盾、升级路径和关键剧情节点。',
    instruction: '需要重构主要矛盾推进方式，调整关键桥段顺序，并替换核心设定名词。',
  },
  strong: {
    label: '强变体',
    summary: '只保留题材气质与爽点结构，人物关系、世界规则和冲突链全部重做。',
    instruction: '只能保留题材气质和爽点类型，人物关系、能力规则、组织格局与剧情升级链都要形成独立新故事。',
  },
};

function formatWordCount(count: number): string {
  if (count < 10000) return `${count}`;
  if (count < 1000000) return `${(count / 10000).toFixed(1).replace(/\.0$/, '')}W`;
  return `${(count / 1000000).toFixed(1).replace(/\.0$/, '')}M`;
}

function isNotFoundError(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;
  const maybeError = error as { response?: { status?: number } };
  return maybeError.response?.status === 404;
}

const BIBLE_EDITABLE_FIELDS: Array<keyof BookRemixBibleUpdatePayload> = [
  'character_cards',
  'timeline',
  'story_arcs',
  'foreshadows',
  'hard_constraints',
];

function toStableSemanticJson(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => toStableSemanticJson(item));
  }

  if (value && typeof value === 'object') {
    return Object.entries(value as Record<string, unknown>)
      .sort(([leftKey], [rightKey]) => leftKey.localeCompare(rightKey))
      .reduce<Record<string, unknown>>((accumulator, [key, nextValue]) => {
        accumulator[key] = toStableSemanticJson(nextValue);
        return accumulator;
      }, {});
  }

  return value;
}

function toStableEditableBiblePayload(
  payload: BookRemixBibleUpdatePayload,
): BookRemixBibleUpdatePayload {
  return BIBLE_EDITABLE_FIELDS.reduce<BookRemixBibleUpdatePayload>((snapshot, fieldName) => {
    snapshot[fieldName] = toStableSemanticJson(payload[fieldName] ?? []) as Array<Record<string, unknown>>;
    return snapshot;
  }, {});
}

function toEditableBiblePayload(bible: BookRemixBible): BookRemixBibleUpdatePayload {
  return {
    character_cards: bible.character_cards,
    timeline: bible.timeline,
    story_arcs: bible.story_arcs,
    foreshadows: bible.foreshadows,
    hard_constraints: bible.hard_constraints,
  };
}

function hasEditableBibleSemanticChange(
  previousPayload: BookRemixBibleUpdatePayload,
  nextBible: BookRemixBible,
): boolean {
  const previousStable = JSON.stringify(toStableEditableBiblePayload(previousPayload));
  const nextStable = JSON.stringify(
    toStableEditableBiblePayload(toEditableBiblePayload(nextBible)),
  );
  return previousStable !== nextStable;
}

function buildInspiredProjectTitle(sourceTitle: string): string {
  const normalized = (sourceTitle || '拆书二创工作台')
    .trim()
    .replace(/\s*-\s*同类创作工作台$/u, '')
    .replace(/\s*-\s*续写工作台$/u, '')
    .replace(/\s*-\s*拆书二创工作台$/u, '')
    .trim();

  return `${normalized || '拆书二创'} - 新创作稿`;
}

function buildInspiredStrategySummary(options: {
  strength: InspiredRemixStrength;
  concept: string;
  characterDirection: string;
  abilityDirection: string;
  worldDirection: string;
  plotDirection: string;
  forbiddenElements: string;
}): string[] {
  const guide = INSPIRED_STRENGTH_GUIDE[options.strength];
  const lines = [`改造强度：${guide.label}。${guide.summary}`];

  if (options.concept.trim()) {
    lines.push(`新故事方向：${options.concept.trim()}`);
  }
  if (options.characterDirection.trim()) {
    lines.push(`人物与组织改造：${options.characterDirection.trim()}`);
  }
  if (options.abilityDirection.trim()) {
    lines.push(`能力体系改造：${options.abilityDirection.trim()}`);
  }
  if (options.worldDirection.trim()) {
    lines.push(`世界观改造：${options.worldDirection.trim()}`);
  }
  if (options.plotDirection.trim()) {
    lines.push(`剧情细节改造：${options.plotDirection.trim()}`);
  }
  if (options.forbiddenElements.trim()) {
    lines.push(`禁用元素：${options.forbiddenElements.trim()}`);
  }

  return lines;
}

function buildInspiredRequirements(options: {
  strength: InspiredRemixStrength;
  concept: string;
  characterDirection: string;
  abilityDirection: string;
  worldDirection: string;
  plotDirection: string;
  forbiddenElements: string;
  mappingLines?: string[];
  customRequirements: string;
}): string {
  const guide = INSPIRED_STRENGTH_GUIDE[options.strength];
  const lines = [
    '请创作一个全新的同类型故事，不要沿用原书人物姓名、组织名称和具体事件顺序。',
    '保留题材气质、节奏优势和核心爽点，但必须形成独立新故事。',
    guide.instruction,
    '主角、核心配角、主要组织、核心能力名词都必须完成重新命名与重设计。',
  ];

  if (options.concept.trim()) {
    lines.push(`新故事方向：${options.concept.trim()}`);
  }
  if (options.characterDirection.trim()) {
    lines.push(`人物与组织改造要求：${options.characterDirection.trim()}`);
  }
  if (options.abilityDirection.trim()) {
    lines.push(`能力体系改造要求：${options.abilityDirection.trim()}`);
  }
  if (options.worldDirection.trim()) {
    lines.push(`世界观改造要求：${options.worldDirection.trim()}`);
  }
  if (options.plotDirection.trim()) {
    lines.push(`剧情细节改造要求：${options.plotDirection.trim()}`);
  }
  if (options.forbiddenElements.trim()) {
    lines.push(`明确禁止沿用这些元素：${options.forbiddenElements.trim()}`);
  }
  if (options.mappingLines?.length) {
    lines.push('请优先遵循以下显式映射改造：');
    options.mappingLines.forEach((line) => lines.push(`- ${line}`));
  }
  if (options.customRequirements.trim()) {
    lines.push(options.customRequirements.trim());
  }

  return lines.join('\n');
}

function cloneInspiredSeedProfile(
  profile?: BookRemixInspiredSeedProfile | null,
): BookRemixInspiredSeedProfile {
  return {
    characters: (profile?.characters || []).map((item) => ({ ...item })),
    organizations: (profile?.organizations || []).map((item) => ({ ...item })),
    abilities: (profile?.abilities || []).map((item) => ({ ...item })),
    world_elements: (profile?.world_elements || []).map((item) => ({ ...item })),
    plot_threads: (profile?.plot_threads || []).map((item) => ({ ...item })),
  };
}

function createEmptySeedMapping(defaultHint = ''): BookRemixSeedMapping {
  return {
    source_name: '',
    occurrence_count: 1,
    sample_context: '',
    suggested_target: '',
    rewrite_hint: defaultHint,
  };
}

function buildSeedMappingLines(
  label: string,
  mappings: BookRemixSeedMapping[],
  limit = 6,
): string[] {
  return mappings
    .filter((item) => item.source_name.trim())
    .slice(0, limit)
    .map((item) => {
      const source = item.source_name.trim();
      const target = item.suggested_target?.trim();
      const hint = item.rewrite_hint?.trim();

      if (target && hint) return `${label}：${source} -> ${target}（${hint}）`;
      if (target) return `${label}：${source} -> ${target}`;
      if (hint) return `${label}：${source}（${hint}）`;
      return `${label}：${source}`;
    });
}

function normalizePipelineChapters(
  chapters?: Array<{ id: string; chapter_number: number; title: string }> | null,
): PipelineChapter[] {
  if (!chapters?.length) {
    return [];
  }

  return chapters
    .filter((chapter) => chapter?.id && Number.isFinite(chapter.chapter_number))
    .map((chapter) => ({
      id: chapter.id,
      chapter_number: chapter.chapter_number,
      title: chapter.title,
    }))
    .sort((left, right) => left.chapter_number - right.chapter_number);
}

function buildChapterRange(chapters: PipelineChapter[], limit?: number) {
  const normalized = normalizePipelineChapters(chapters);
  const selected = normalized.slice(0, Math.max(1, limit || normalized.length));

  if (!selected.length) {
    throw new Error('未找到可生成正文的章节');
  }

  const start = selected[0].chapter_number;
  selected.forEach((chapter, index) => {
    const expected = start + index;
    if (chapter.chapter_number !== expected) {
      throw new Error('当前仅支持连续章节的首批正文批量生成');
    }
  });

  return {
    start,
    count: selected.length,
    chapters: selected,
  };
}

type PipelineChapter = {
  id: string;
  chapter_number: number;
  title: string;
};

const EMPTY_INSPIRED_SEED_PROFILE: BookRemixInspiredSeedProfile = {
  characters: [],
  organizations: [],
  abilities: [],
  world_elements: [],
  plot_threads: [],
};

type StarterPackError = Error & {
  draftProjectId?: string;
  targetPage?: 'outline' | 'chapters';
};

type InspiredPackResult = {
  projectId: string;
  targetPage: 'outline' | 'chapters';
  startedContentCount: number;
};

interface BookRemixProps {
  initialContinuationProjectId?: string | null;
}

export default function BookRemix({ initialContinuationProjectId = null }: BookRemixProps) {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<BookRemixMode>('continuation');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<BookRemixTask | null>(null);
  const [preview, setPreview] = useState<BookRemixPreview | null>(null);
  const [creatingTask, setCreatingTask] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [creatingProject, setCreatingProject] = useState(false);

  const [autoCreateInspiredPack, setAutoCreateInspiredPack] = useState(true);
  const [inspiredProjectTitle, setInspiredProjectTitle] = useState('');
  const [inspiredChapterCount, setInspiredChapterCount] = useState(12);
  const [inspiredRemixStrength, setInspiredRemixStrength] = useState<InspiredRemixStrength>('strong');
  const [inspiredConcept, setInspiredConcept] = useState('');
  const [inspiredCharacterDirection, setInspiredCharacterDirection] = useState('');
  const [inspiredAbilityDirection, setInspiredAbilityDirection] = useState('');
  const [inspiredWorldDirection, setInspiredWorldDirection] = useState('');
  const [inspiredPlotDirection, setInspiredPlotDirection] = useState('');
  const [inspiredForbiddenElements, setInspiredForbiddenElements] = useState('');
  const [inspiredRequirements, setInspiredRequirements] = useState('');
  const [autoGenerateInspiredContent, setAutoGenerateInspiredContent] = useState(true);
  const [inspiredInitialContentCount, setInspiredInitialContentCount] = useState(3);
  const [inspiredChapterTargetWordCount, setInspiredChapterTargetWordCount] = useState(2600);
  const [inspiredEnableChapterAnalysis, setInspiredEnableChapterAnalysis] = useState(true);
  const [inspiredSeedProfile, setInspiredSeedProfile] = useState<BookRemixInspiredSeedProfile>(EMPTY_INSPIRED_SEED_PROFILE);

  const [continuationWorkbenchProjectId, setContinuationWorkbenchProjectId] = useState<string | null>(null);
  const [bibleDraft, setBibleDraft] = useState<BookRemixBible | null>(null);
  const [continuationPlan, setContinuationPlan] = useState<BookRemixContinuationPlan | null>(null);
  const [analysisCoverage, setAnalysisCoverage] = useState<BookRemixAnalysisCoverage | null>(null);
  const [continuationProgressSummary, setContinuationProgressSummary] = useState<BookRemixContinuationProgressSummary | null>(null);
  const [chapterChangePackages, setChapterChangePackages] = useState<BookRemixChapterChangePackageList | null>(null);
  const [continuationContextPreview, setContinuationContextPreview] = useState<BookRemixContinuationContextPreview | null>(null);
  const [lastStartMissingResult, setLastStartMissingResult] = useState<BookRemixStartMissingAnalysisResult | null>(null);
  const [continuationPlanInvalidated, setContinuationPlanInvalidated] = useState(false);
  const [loadingBibleDraft, setLoadingBibleDraft] = useState(false);
  const [savingBibleDraft, setSavingBibleDraft] = useState(false);
  const [confirmingBibleDraft, setConfirmingBibleDraft] = useState(false);
  const [regeneratingBibleDraft, setRegeneratingBibleDraft] = useState(false);
  const [loadingContinuationPlan, setLoadingContinuationPlan] = useState(false);
  const [loadingAnalysisCoverage, setLoadingAnalysisCoverage] = useState(false);
  const [loadingContinuationProgressSummary, setLoadingContinuationProgressSummary] = useState(false);
  const [loadingChapterChangePackages, setLoadingChapterChangePackages] = useState(false);
  const [loadingContinuationContextPreview, setLoadingContinuationContextPreview] = useState(false);
  const [startingMissingAnalysis, setStartingMissingAnalysis] = useState(false);
  const [generatingContinuationPlan, setGeneratingContinuationPlan] = useState(false);
  const [savingContinuationPlan, setSavingContinuationPlan] = useState(false);
  const [confirmingContinuationPlan, setConfirmingContinuationPlan] = useState(false);

  const [starterPackVisible, setStarterPackVisible] = useState(false);
  const [starterPackTitle, setStarterPackTitle] = useState('正在准备起步包');
  const [starterPackProgress, setStarterPackProgress] = useState(0);
  const [starterPackMessage, setStarterPackMessage] = useState('正在准备自动化起步包...');

  useEffect(() => {
    if (!initialContinuationProjectId) return;
    setMode('continuation');
    setContinuationWorkbenchProjectId((current) => (
      current === initialContinuationProjectId ? current : initialContinuationProjectId
    ));
  }, [initialContinuationProjectId]);

  const isTaskTerminal = useMemo(
    () => Boolean(taskStatus && ['completed', 'failed', 'cancelled'].includes(taskStatus.status)),
    [taskStatus],
  );

  const currentStep = useMemo(() => {
    if (continuationWorkbenchProjectId) return 3;
    if (!taskId) return 0;
    if (creatingProject) return 3;
    if (preview) return 2;
    return 1;
  }, [continuationWorkbenchProjectId, creatingProject, preview, taskId]);

  const visibleChapters = useMemo(() => preview?.chapters.slice(0, 40) ?? [], [preview]);
  const isContinuationPlanOutdated = useMemo(() => {
    if (!continuationPlan) return false;
    if (continuationPlanInvalidated) return true;
    if (!bibleDraft) return false;
    if (continuationPlan.bible_id !== bibleDraft.id) return true;

    const bibleUpdatedAt = Date.parse(bibleDraft.updated_at);
    const planUpdatedAt = Date.parse(continuationPlan.updated_at);
    if (!Number.isFinite(bibleUpdatedAt) || !Number.isFinite(planUpdatedAt)) return false;

    return planUpdatedAt < bibleUpdatedAt;
  }, [bibleDraft, continuationPlan, continuationPlanInvalidated]);

  const createButtonText = useMemo(() => {
    if (preview?.remix_mode === 'continuation') {
      return '创建项目并进入 Bible/Plan 工作台';
    }
    if (preview?.remix_mode === 'inspired' && autoCreateInspiredPack) {
      return '创建工作台并派生同类创作项目';
    }
    return '创建二创工作台项目';
  }, [
    autoCreateInspiredPack,
    preview?.remix_mode,
  ]);

  const inspiredStrategySummary = useMemo(
    () => buildInspiredStrategySummary({
      strength: inspiredRemixStrength,
      concept: inspiredConcept,
      characterDirection: inspiredCharacterDirection,
      abilityDirection: inspiredAbilityDirection,
      worldDirection: inspiredWorldDirection,
      plotDirection: inspiredPlotDirection,
      forbiddenElements: inspiredForbiddenElements,
    }),
    [
      inspiredAbilityDirection,
      inspiredCharacterDirection,
      inspiredConcept,
      inspiredForbiddenElements,
      inspiredPlotDirection,
      inspiredRemixStrength,
      inspiredWorldDirection,
    ],
  );

  const inspiredMappingSummary = useMemo(
    () => [
      ...buildSeedMappingLines('人物映射', inspiredSeedProfile.characters, 4),
      ...buildSeedMappingLines('组织映射', inspiredSeedProfile.organizations, 3),
      ...buildSeedMappingLines('能力映射', inspiredSeedProfile.abilities, 3),
      ...buildSeedMappingLines('世界观映射', inspiredSeedProfile.world_elements, 3),
      ...buildSeedMappingLines('剧情改写', inspiredSeedProfile.plot_threads, 3),
    ],
    [inspiredSeedProfile],
  );

  useEffect(() => {
    if (!taskId || isTaskTerminal) return;

    const timer = window.setInterval(async () => {
      try {
        const status = await bookRemixApi.getTaskStatus(taskId);
        setTaskStatus(status);
      } catch (error) {
        console.error('轮询拆书二创任务失败:', error);
        if (isNotFoundError(error)) {
          resetTaskState();
          message.warning('拆书二创任务已失效，请重新上传 TXT');
        }
      }
    }, 1500);

    return () => window.clearInterval(timer);
  }, [isTaskTerminal, taskId]);

  useEffect(() => {
    const fetchPreview = async () => {
      if (!taskId || !taskStatus) return;
      if (taskStatus.status !== 'completed' || preview) return;

      try {
        setLoadingPreview(true);
        const data = await bookRemixApi.getPreview(taskId);
        setPreview(data);
      } catch (error) {
        console.error('获取拆书二创预览失败:', error);
        message.error('获取预览失败');
      } finally {
        setLoadingPreview(false);
      }
    };

    fetchPreview();
  }, [preview, taskId, taskStatus]);

  useEffect(() => {
    if (!preview || preview.remix_mode !== 'inspired') return;
    setInspiredProjectTitle(buildInspiredProjectTitle(preview.project_suggestion.title));
    setInspiredConcept(preview.project_suggestion.theme || preview.project_suggestion.description || '');
  }, [preview]);

  useEffect(() => {
    if (!preview || preview.remix_mode !== 'inspired') {
      setInspiredSeedProfile(EMPTY_INSPIRED_SEED_PROFILE);
      return;
    }

    setInspiredSeedProfile(cloneInspiredSeedProfile(preview.inspired_seed_profile));
  }, [preview?.task_id, preview?.remix_mode, preview?.inspired_seed_profile]);

  useEffect(() => {
    if (!continuationWorkbenchProjectId) return;
    void loadBibleDraft(continuationWorkbenchProjectId);
    void loadContinuationPlan(continuationWorkbenchProjectId);
    void loadAnalysisCoverage(continuationWorkbenchProjectId);
    void loadContinuationProgressSummary(continuationWorkbenchProjectId);
    void loadChapterChangePackages(continuationWorkbenchProjectId);
    void loadContinuationContextPreview(continuationWorkbenchProjectId);
    // 只在工作台项目切换时加载一次，避免 load* 函数身份变化导致重复请求。
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [continuationWorkbenchProjectId]);

  useEffect(() => {
    if (!continuationWorkbenchProjectId) return;
    if (!bibleDraft || !['pending', 'running'].includes(bibleDraft.generation_status)) return;

    const timer = window.setInterval(() => {
      void loadBibleDraft(continuationWorkbenchProjectId);
    }, 3000);

    return () => window.clearInterval(timer);
  }, [bibleDraft?.generation_status, continuationWorkbenchProjectId]);

  const openStarterPackModal = (title: string, initialMessage: string) => {
    setStarterPackTitle(title);
    setStarterPackMessage(initialMessage);
    setStarterPackProgress(0);
    setStarterPackVisible(true);
  };

  const closeStarterPackModal = () => {
    setStarterPackVisible(false);
    setStarterPackTitle('正在准备起步包');
    setStarterPackProgress(0);
    setStarterPackMessage('正在准备自动化起步包...');
  };

  const resetTaskState = () => {
    setTaskId(null);
    setTaskStatus(null);
    setPreview(null);
    setLoadingPreview(false);
    setCreatingProject(false);
    setAutoCreateInspiredPack(true);
    setInspiredProjectTitle('');
    setInspiredChapterCount(12);
    setInspiredRemixStrength('strong');
    setInspiredConcept('');
    setInspiredCharacterDirection('');
    setInspiredAbilityDirection('');
    setInspiredWorldDirection('');
    setInspiredPlotDirection('');
    setInspiredForbiddenElements('');
    setInspiredRequirements('');
    setAutoGenerateInspiredContent(true);
    setInspiredInitialContentCount(3);
    setInspiredChapterTargetWordCount(2600);
    setInspiredEnableChapterAnalysis(true);
    setInspiredSeedProfile(EMPTY_INSPIRED_SEED_PROFILE);
    setContinuationWorkbenchProjectId(null);
    setBibleDraft(null);
    setContinuationPlan(null);
    setAnalysisCoverage(null);
    setContinuationProgressSummary(null);
    setChapterChangePackages(null);
    setContinuationContextPreview(null);
    setLastStartMissingResult(null);
    setContinuationPlanInvalidated(false);
    setLoadingBibleDraft(false);
    setSavingBibleDraft(false);
    setConfirmingBibleDraft(false);
    setRegeneratingBibleDraft(false);
    setLoadingContinuationPlan(false);
    setLoadingAnalysisCoverage(false);
    setLoadingContinuationProgressSummary(false);
    setLoadingChapterChangePackages(false);
    setLoadingContinuationContextPreview(false);
    setStartingMissingAnalysis(false);
    setGeneratingContinuationPlan(false);
    setSavingContinuationPlan(false);
    setConfirmingContinuationPlan(false);
    closeStarterPackModal();
  };

  const loadBibleDraft = async (projectId?: string) => {
    const targetProjectId = projectId || continuationWorkbenchProjectId;
    if (!targetProjectId) return;

    try {
      setLoadingBibleDraft(true);
      const result = await bookRemixApi.getBible(targetProjectId);
      setBibleDraft(result);
    } catch (error) {
      if (isNotFoundError(error)) {
        setBibleDraft(null);
        return;
      }
      console.error('加载 Bible 草稿失败:', error);
    } finally {
      setLoadingBibleDraft(false);
    }
  };

  const loadContinuationPlan = async (projectId?: string) => {
    const targetProjectId = projectId || continuationWorkbenchProjectId;
    if (!targetProjectId) return;

    try {
      setLoadingContinuationPlan(true);
      const result = await bookRemixApi.getContinuationPlan(targetProjectId);
      setContinuationPlan(result);
    } catch (error) {
      if (isNotFoundError(error)) {
        setContinuationPlan(null);
        setContinuationPlanInvalidated(false);
        return;
      }
      console.error('加载续写计划失败:', error);
    } finally {
      setLoadingContinuationPlan(false);
    }
  };

  const loadContinuationProgressSummary = async (projectId?: string) => {
    const targetProjectId = projectId || continuationWorkbenchProjectId;
    if (!targetProjectId) return;

    try {
      setLoadingContinuationProgressSummary(true);
      const result = await bookRemixApi.getContinuationProgressSummary(targetProjectId);
      setContinuationProgressSummary(result);
    } catch (error) {
      if (isNotFoundError(error)) {
        setContinuationProgressSummary(null);
        return;
      }
      console.error('加载全书续写进度失败:', error);
    } finally {
      setLoadingContinuationProgressSummary(false);
    }
  };

  const loadAnalysisCoverage = async (projectId?: string) => {
    const targetProjectId = projectId || continuationWorkbenchProjectId;
    if (!targetProjectId) return;

    try {
      setLoadingAnalysisCoverage(true);
      const result = await bookRemixApi.getAnalysisCoverage(targetProjectId);
      setAnalysisCoverage(result);
    } catch (error) {
      if (isNotFoundError(error)) {
        setAnalysisCoverage(null);
        return;
      }
      console.error('加载分析覆盖率失败:', error);
    } finally {
      setLoadingAnalysisCoverage(false);
    }
  };

  const loadChapterChangePackages = async (projectId?: string) => {
    const targetProjectId = projectId || continuationWorkbenchProjectId;
    if (!targetProjectId) return;

    try {
      setLoadingChapterChangePackages(true);
      const result = await bookRemixApi.getChapterChangePackages(targetProjectId);
      setChapterChangePackages(result);
    } catch (error) {
      if (isNotFoundError(error)) {
        setChapterChangePackages(null);
        return;
      }
      console.error('加载章节变更包失败:', error);
    } finally {
      setLoadingChapterChangePackages(false);
    }
  };

  const loadContinuationContextPreview = async (projectId?: string) => {
    const targetProjectId = projectId || continuationWorkbenchProjectId;
    if (!targetProjectId) return;

    try {
      setLoadingContinuationContextPreview(true);
      const result = await bookRemixApi.getContinuationContextPreview(targetProjectId);
      setContinuationContextPreview(result);
    } catch (error) {
      if (isNotFoundError(error)) {
        setContinuationContextPreview(null);
        return;
      }
      console.error('加载续写上下文预览失败:', error);
    } finally {
      setLoadingContinuationContextPreview(false);
    }
  };

  const startMissingAnalysis = async () => {
    if (!continuationWorkbenchProjectId) return;

    try {
      setStartingMissingAnalysis(true);
      const result = await bookRemixApi.startMissingAnalysis(continuationWorkbenchProjectId);
      setLastStartMissingResult(result);
      if (result.total_started > 0) {
        const syncedText = result.total_synced_existing > 0
          ? `，并写回 ${result.total_synced_existing} 个已有分析`
          : '';
        message.success(`已创建 ${result.total_started} 个缺口分析任务${syncedText}`);
      } else if (result.total_synced_existing > 0) {
        message.success(`已写回 ${result.total_synced_existing} 个已有章节分析`);
      } else if (result.total_skipped_running > 0) {
        message.info('缺口章节已有分析任务在排队或运行中');
      } else {
        message.info('没有可补跑的缺口章节');
      }

      await Promise.all([
        loadAnalysisCoverage(continuationWorkbenchProjectId),
        loadContinuationProgressSummary(continuationWorkbenchProjectId),
        loadChapterChangePackages(continuationWorkbenchProjectId),
        loadContinuationContextPreview(continuationWorkbenchProjectId),
      ]);
    } finally {
      setStartingMissingAnalysis(false);
    }
  };

  const saveBibleDraft = async (payload: BookRemixBibleUpdatePayload) => {
    if (!continuationWorkbenchProjectId) return;
    const previousEditablePayload = bibleDraft
      ? toEditableBiblePayload(bibleDraft)
      : null;
    try {
      setSavingBibleDraft(true);
      const result = await bookRemixApi.updateBible(continuationWorkbenchProjectId, payload);
      setBibleDraft(result);
      if (
        continuationPlan
        && previousEditablePayload
        && hasEditableBibleSemanticChange(previousEditablePayload, result)
      ) {
        setContinuationPlanInvalidated(true);
      }
      await loadContinuationContextPreview(continuationWorkbenchProjectId);
    } finally {
      setSavingBibleDraft(false);
    }
  };

  const confirmBibleDraft = async () => {
    if (!continuationWorkbenchProjectId) return;
    try {
      setConfirmingBibleDraft(true);
      const result = await bookRemixApi.confirmBible(continuationWorkbenchProjectId);
      setBibleDraft(result);
      message.success('Bible 已确认');
      await loadContinuationPlan(continuationWorkbenchProjectId);
      await loadAnalysisCoverage(continuationWorkbenchProjectId);
      await loadContinuationProgressSummary(continuationWorkbenchProjectId);
      await loadChapterChangePackages(continuationWorkbenchProjectId);
      await loadContinuationContextPreview(continuationWorkbenchProjectId);
    } finally {
      setConfirmingBibleDraft(false);
    }
  };

  const regenerateBibleDraft = async () => {
    if (!continuationWorkbenchProjectId) return;
    try {
      setRegeneratingBibleDraft(true);
      const result = await bookRemixApi.regenerateBible(continuationWorkbenchProjectId);
      setBibleDraft(result);
      if (continuationPlan) {
        setContinuationPlanInvalidated(true);
      }
      message.success('Bible regenerated');
      await loadAnalysisCoverage(continuationWorkbenchProjectId);
      await loadContinuationProgressSummary(continuationWorkbenchProjectId);
      await loadChapterChangePackages(continuationWorkbenchProjectId);
      await loadContinuationContextPreview(continuationWorkbenchProjectId);
    } finally {
      setRegeneratingBibleDraft(false);
    }
  };

  const generateContinuationPlanDraft = async (userDirection: string) => {
    if (!continuationWorkbenchProjectId) return;
    try {
      setGeneratingContinuationPlan(true);
      const result = await bookRemixApi.generateContinuationPlan(continuationWorkbenchProjectId, {
        user_direction: userDirection,
      });
      setContinuationPlan(result);
      setContinuationPlanInvalidated(false);
      await loadContinuationContextPreview(continuationWorkbenchProjectId);
    } finally {
      setGeneratingContinuationPlan(false);
    }
  };

  const saveContinuationPlanDraft = async (payload: BookRemixContinuationPlanUpdatePayload) => {
    if (!continuationWorkbenchProjectId) return;
    try {
      setSavingContinuationPlan(true);
      const result = await bookRemixApi.updateContinuationPlan(continuationWorkbenchProjectId, payload);
      setContinuationPlan(result);
      await loadContinuationContextPreview(continuationWorkbenchProjectId);
    } finally {
      setSavingContinuationPlan(false);
    }
  };

  const confirmContinuationPlanDraft = async () => {
    if (!continuationWorkbenchProjectId) return;
    try {
      setConfirmingContinuationPlan(true);
      const result = await bookRemixApi.confirmContinuationPlan(continuationWorkbenchProjectId);
      setContinuationPlan(result);
      message.success('续写计划已确认');
      await loadContinuationContextPreview(continuationWorkbenchProjectId);
    } finally {
      setConfirmingContinuationPlan(false);
    }
  };

  const updateSuggestion = (patch: Partial<BookRemixPreview['project_suggestion']>) => {
    setPreview((prev) => (
      prev
        ? {
            ...prev,
            project_suggestion: {
              ...prev.project_suggestion,
              ...patch,
            },
          }
        : prev
    ));
  };

  const handleSuggestionTitleChange = (nextTitle: string) => {
    const previousTitle = preview?.project_suggestion.title || '';
    updateSuggestion({ title: nextTitle });

    if (preview?.remix_mode !== 'inspired') return;

    const previousDerivedTitle = buildInspiredProjectTitle(previousTitle);
    setInspiredProjectTitle((current) => {
      if (!current || current === previousDerivedTitle) {
        return buildInspiredProjectTitle(nextTitle);
      }
      return current;
    });
  };

  const updateInspiredSeedMapping = (
    group: InspiredSeedGroupKey,
    index: number,
    patch: Partial<BookRemixSeedMapping>,
  ) => {
    setInspiredSeedProfile((prev) => ({
      ...prev,
      [group]: prev[group].map((item, itemIndex) => (
        itemIndex === index
          ? { ...item, ...patch }
          : item
      )),
    }));
  };

  const addInspiredSeedMapping = (group: InspiredSeedGroupKey, defaultHint: string) => {
    setInspiredSeedProfile((prev) => ({
      ...prev,
      [group]: [...prev[group], createEmptySeedMapping(defaultHint)],
    }));
  };

  const removeInspiredSeedMapping = (group: InspiredSeedGroupKey, index: number) => {
    setInspiredSeedProfile((prev) => ({
      ...prev,
      [group]: prev[group].filter((_, itemIndex) => itemIndex !== index),
    }));
  };

  const renderInspiredSeedEditor = (
    group: InspiredSeedGroupKey,
    title: string,
    defaultHint: string,
  ) => (
    <Card
      size="small"
      title={title}
      extra={(
        <Button size="small" onClick={() => addInspiredSeedMapping(group, defaultHint)}>
          新增一条
        </Button>
      )}
    >
      <Space direction="vertical" size={12} style={{ width: '100%' }}>
        {inspiredSeedProfile[group].length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂未识别到草案，可手动补充" />
        ) : (
          inspiredSeedProfile[group].map((item, index) => (
            <Card
              key={`${group}-${index}-${item.source_name || 'empty'}`}
              size="small"
              styles={{ body: { padding: 12 } }}
            >
              <Space direction="vertical" size={10} style={{ width: '100%' }}>
                <Row gutter={[12, 12]}>
                  <Col xs={24} md={10}>
                    <Text>原元素</Text>
                    <Input
                      value={item.source_name}
                      onChange={(event) => updateInspiredSeedMapping(group, index, { source_name: event.target.value })}
                      placeholder="原书中的人物名 / 组织名 / 设定名"
                    />
                  </Col>
                  <Col xs={24} md={10}>
                    <Text>新元素</Text>
                    <Input
                      value={item.suggested_target ?? ''}
                      onChange={(event) => updateInspiredSeedMapping(group, index, { suggested_target: event.target.value })}
                      placeholder="准备替换成的新名字或新设定"
                    />
                  </Col>
                  <Col xs={24} md={4}>
                    <Text>出现次数</Text>
                    <Input value={`${item.occurrence_count || 1}`} disabled />
                  </Col>
                </Row>
                <Row gutter={[12, 12]}>
                  <Col xs={24} md={20}>
                    <Text>改造说明</Text>
                    <Input
                      value={item.rewrite_hint ?? ''}
                      onChange={(event) => updateInspiredSeedMapping(group, index, { rewrite_hint: event.target.value })}
                      placeholder={defaultHint}
                    />
                  </Col>
                  <Col xs={24} md={4}>
                    <Text>操作</Text>
                    <Button danger block onClick={() => removeInspiredSeedMapping(group, index)}>
                      删除
                    </Button>
                  </Col>
                </Row>
                {item.sample_context && (
                  <Alert
                    type="info"
                    showIcon
                    message="识别样例"
                    description={item.sample_context}
                  />
                )}
              </Space>
            </Card>
          ))
        )}
      </Space>
    </Card>
  );

  const startTask = async () => {
    if (!file) {
      message.warning('请先选择 TXT 文件');
      return;
    }

    try {
      setCreatingTask(true);
      resetTaskState();

      const response = await bookRemixApi.createTask({
        file,
        remixMode: mode,
      });

      setTaskId(response.task_id);
      setTaskStatus({
        task_id: response.task_id,
        remix_mode: response.remix_mode,
        status: response.status,
        progress: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      message.success('拆书二创任务已创建');
    } catch (error) {
      console.error('创建拆书二创任务失败:', error);
      message.error('创建任务失败');
    } finally {
      setCreatingTask(false);
    }
  };

  const refreshStatus = async () => {
    if (!taskId) return;
    try {
      const status = await bookRemixApi.getTaskStatus(taskId);
      setTaskStatus(status);
    } catch (error) {
      console.error('刷新拆书二创任务状态失败:', error);
    }
  };

  const cancelTask = async () => {
    if (!taskId) return;
    try {
      await bookRemixApi.cancelTask(taskId);
      await refreshStatus();
      message.success('任务已取消');
    } catch (error) {
      console.error('取消拆书二创任务失败:', error);
      message.error('取消任务失败');
    }
  };

  const createInspiredDraftProject = async (
    workbenchProjectId: string,
    preparedStyleId?: number | null,
  ): Promise<string> => {
    if (!preview) {
      throw new Error('缺少项目预览数据');
    }

    const projectTitle = inspiredProjectTitle.trim() || buildInspiredProjectTitle(preview.project_suggestion.title);
    const projectTheme = (
      inspiredConcept.trim()
      || preview.project_suggestion.theme
      || preview.project_suggestion.description
      || '基于原书题材气质创作一个独立新故事'
    ).trim();

    const strategySummary = buildInspiredStrategySummary({
      strength: inspiredRemixStrength,
      concept: inspiredConcept,
      characterDirection: inspiredCharacterDirection,
      abilityDirection: inspiredAbilityDirection,
      worldDirection: inspiredWorldDirection,
      plotDirection: inspiredPlotDirection,
      forbiddenElements: inspiredForbiddenElements,
    });
    const mappingSummary = [
      ...buildSeedMappingLines('人物映射', inspiredSeedProfile.characters),
      ...buildSeedMappingLines('组织映射', inspiredSeedProfile.organizations),
      ...buildSeedMappingLines('能力映射', inspiredSeedProfile.abilities),
      ...buildSeedMappingLines('世界观映射', inspiredSeedProfile.world_elements),
      ...buildSeedMappingLines('剧情改写', inspiredSeedProfile.plot_threads),
    ];

    const projectDescription = [
      `[同类创作稿] 来源工作台：${preview.project_suggestion.title}`,
      `关联工作台 ID：${workbenchProjectId}`,
      '[同类创作策略]',
      ...strategySummary.map((line) => `- ${line}`),
      ...(mappingSummary.length > 0 ? ['[显式改造映射]', ...mappingSummary.map((line) => `- ${line}`)] : []),
      preview.project_suggestion.description?.trim() || '',
    ]
      .filter(Boolean)
      .join('\n');

    const createdProject = await projectApi.createProject({
      title: projectTitle,
      description: projectDescription,
      theme: projectTheme,
      genre: preview.project_suggestion.genre,
      target_words: preview.project_suggestion.target_words,
      outline_mode: 'one-to-one',
      wizard_status: 'completed',
      wizard_step: 3,
    });

    await projectApi.updateProject(createdProject.id, {
      description: projectDescription,
      narrative_perspective: preview.project_suggestion.narrative_perspective,
    });

    if (preparedStyleId) {
      await writingStyleApi.setDefaultStyle(preparedStyleId, createdProject.id);
    }

    return createdProject.id;
  };

  const loadPipelineChapters = async (
    projectId: string,
    outlineResult?: GenerateOutlineResponse | null,
  ) => {
    const fromResult = normalizePipelineChapters(outlineResult?.chapters || []);
    if (fromResult.length > 0) {
      return fromResult;
    }

    const existingChapters = await chapterApi.getChapters(projectId);
    return normalizePipelineChapters(
      existingChapters
        .filter((chapter) => !chapter.content || !chapter.content.trim())
        .map((chapter) => ({
          id: chapter.id,
          chapter_number: chapter.chapter_number,
          title: chapter.title,
        })),
    );
  };

  const startInspiredContentGeneration = async (
    projectId: string,
    outlineResult?: GenerateOutlineResponse | null,
  ) => {
    const pendingChapters = await loadPipelineChapters(projectId, outlineResult);
    const range = buildChapterRange(pendingChapters, inspiredInitialContentCount);

    setStarterPackProgress((prev) => Math.max(prev, 92));
    setStarterPackMessage(`故事骨架已完成，正在启动前 ${range.count} 章正文生成...`);

    await chapterApi.batchGenerate(projectId, {
      start_chapter_number: range.start,
      count: range.count,
      target_word_count: inspiredChapterTargetWordCount,
      enable_analysis: inspiredEnableChapterAnalysis,
      enable_mcp: true,
      max_retries: 3,
    });

    setStarterPackProgress(100);
    setStarterPackMessage(`已启动前 ${range.count} 章正文生成，正在跳转章节页...`);

    return range.count;
  };

  const runInspiredPack = async (
    workbenchProjectId: string,
    preparedStyleId?: number | null,
  ): Promise<InspiredPackResult> => {
    if (!preview) {
      throw new Error('缺少项目预览数据');
    }

    const projectTheme = (
      inspiredConcept.trim()
      || preview.project_suggestion.theme
      || preview.project_suggestion.description
      || '保留题材气质与核心爽点，但形成独立新故事'
    ).trim();

    openStarterPackModal('正在派生同类创作项目', '正在创建独立创作项目...');
    setStarterPackProgress(10);

    const draftProjectId = await createInspiredDraftProject(workbenchProjectId, preparedStyleId);
    setStarterPackProgress(25);
    setStarterPackMessage('独立创作项目已创建，正在生成新故事骨架...');

    try {
      const outlineResult = await outlineApi.generateOutlineStream(
        {
          project_id: draftProjectId,
          genre: preview.project_suggestion.genre || undefined,
          theme: projectTheme,
          chapter_count: inspiredChapterCount,
          narrative_perspective: preview.project_suggestion.narrative_perspective || '第三人称',
          target_words: preview.project_suggestion.target_words || 100000,
          requirements: buildInspiredRequirements({
            strength: inspiredRemixStrength,
            concept: inspiredConcept,
            characterDirection: inspiredCharacterDirection,
            abilityDirection: inspiredAbilityDirection,
            worldDirection: inspiredWorldDirection,
            plotDirection: inspiredPlotDirection,
            forbiddenElements: inspiredForbiddenElements,
            mappingLines: inspiredMappingSummary,
            customRequirements: inspiredRequirements,
          }),
          mode: 'new',
        },
        {
          onProgress: (progressMessage, progress) => {
            setStarterPackMessage(progressMessage || '正在生成同类创作故事骨架...');
            setStarterPackProgress(Math.max(progress ?? 0, 25));
          },
        },
      );

      if (autoGenerateInspiredContent) {
        try {
          const startedContentCount = await startInspiredContentGeneration(draftProjectId, outlineResult);
          return {
            projectId: draftProjectId,
            targetPage: 'chapters',
            startedContentCount,
          };
        } catch (error) {
          const wrappedError: StarterPackError = error instanceof Error ? error : new Error('首批正文启动失败');
          wrappedError.draftProjectId = draftProjectId;
          wrappedError.targetPage = 'chapters';
          throw wrappedError;
        }
      }

      setStarterPackProgress(100);
      setStarterPackMessage('同类创作故事骨架已生成，正在跳转大纲页...');

      return {
        projectId: draftProjectId,
        targetPage: 'outline',
        startedContentCount: 0,
      };
    } catch (error) {
      const wrappedError: StarterPackError = error instanceof Error ? error : new Error('同类创作起步包生成失败');
      wrappedError.draftProjectId = draftProjectId;
      wrappedError.targetPage = wrappedError.targetPage || 'outline';
      throw wrappedError;
    }
  };

  const createProject = async () => {
    if (!taskId || !preview) return;

    try {
      setCreatingProject(true);
      const result = await bookRemixApi.createProject(taskId, {
        project_suggestion: preview.project_suggestion,
      });

      message.success(result.message);

      if (preview.remix_mode === 'continuation') {
        setContinuationWorkbenchProjectId(result.project_id);
        setBibleDraft(null);
        setContinuationPlan(null);
        setAnalysisCoverage(null);
        setContinuationProgressSummary(null);
        setChapterChangePackages(null);
        setContinuationContextPreview(null);
        setLastStartMissingResult(null);
        if (result.bible_generation_started && ['pending', 'running'].includes(result.bible_generation_status || '')) {
          message.info('Bible 草稿正在后台生成，页面会自动刷新状态。');
        }
        message.success('项目已创建：请先审校并确认 Bible，再生成并确认续写计划。');
        return;
      }

      if (preview.remix_mode === 'inspired' && autoCreateInspiredPack) {
        let inspiredResult: InspiredPackResult | null = null;

        try {
          inspiredResult = await runInspiredPack(result.project_id, result.prepared_style_id);
          closeStarterPackModal();
          if (inspiredResult.targetPage === 'chapters') {
            message.success(`同类创作项目已生成，已启动前 ${inspiredResult.startedContentCount} 章正文生成`);
            navigate(`/project/${inspiredResult.projectId}/chapters`);
            return;
          }

          message.success(`同类创作项目已生成，已创建 ${inspiredChapterCount} 章新故事骨架`);
          navigate(`/project/${inspiredResult.projectId}/outline`);
          return;
        } catch (error) {
          console.error('自动派生同类创作项目失败:', error);
          closeStarterPackModal();

          const maybeDraftProjectId = inspiredResult?.projectId || (error as StarterPackError).draftProjectId || '';
          if (maybeDraftProjectId) {
            const targetPage = (error as StarterPackError).targetPage || 'outline';
            if (targetPage === 'chapters') {
              message.warning('同类创作项目已创建，故事骨架已就绪，但首批正文启动失败，请进入章节页继续处理');
              navigate(`/project/${maybeDraftProjectId}/chapters`);
              return;
            }

            message.warning('同类创作项目已创建，但故事骨架生成失败，请进入大纲页继续调整');
            navigate(`/project/${maybeDraftProjectId}/outline`);
            return;
          }

          message.warning('工作台已创建，但派生同类创作项目失败，请稍后重试');
          navigate(`/project/${result.project_id}/chapter-analysis`);
          return;
        }
      }

      navigate(`/project/${result.project_id}/chapter-analysis`);
    } catch (error) {
      console.error('创建拆书二创工作台项目失败:', error);
      message.error('创建拆书二创工作台项目失败');
    } finally {
      setCreatingProject(false);
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 60 }}>
      <Alert
        type="info"
        showIcon
        icon={<RobotOutlined />}
        style={{ marginBottom: 16 }}
        message="拆书二创工作台"
        description="这个入口不会改动原有拆书导入功能。当前版本会按整本 TXT 分章，创建独立工作台，并自动启动全书章节分析，为后续的续写或同类创作做准备。"
      />

      <Card style={{ marginBottom: 16 }}>
        <Steps
          current={currentStep}
          items={[
            { title: '上传整本与选择模式' },
            { title: '整本解析' },
            { title: '确认工作台配置' },
            { title: 'Bible / 续写计划工作台' },
          ]}
        />
      </Card>

      {currentStep === 0 && (
        <Card title="上传完整 TXT 并选择二创模式" style={{ marginBottom: 16 }}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Radio.Group
              value={mode}
              onChange={(event) => setMode(event.target.value as BookRemixMode)}
              optionType="button"
              buttonStyle="solid"
            >
              <Radio.Button value="continuation">续写模式</Radio.Button>
              <Radio.Button value="inspired">同类创作模式</Radio.Button>
            </Radio.Group>

            <Card size="small" style={{ background: 'var(--color-bg-container)' }}>
              <Space direction="vertical" size={6}>
                <Tag color="blue">{MODE_META[mode].tag}</Tag>
                <Text strong>{MODE_META[mode].title}</Text>
                <Paragraph style={{ marginBottom: 0, color: 'var(--color-text-secondary)' }}>
                  {MODE_META[mode].description}
                </Paragraph>
              </Space>
            </Card>

            <Dragger
              accept=".txt"
              multiple={false}
              beforeUpload={(selectedFile) => {
                setFile(selectedFile);
                return false;
              }}
              onRemove={() => setFile(null)}
              fileList={
                file
                  ? [{ uid: 'selected-remix-txt', name: file.name, status: 'done' } as UploadFile]
                  : []
              }
              style={{ padding: '8px 0' }}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽完整 TXT 文件到此区域</p>
              <p className="ant-upload-hint">
                建议上传整本小说原文，系统会自动分章并启动后续分析。
              </p>
            </Dragger>

            <Space>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                loading={creatingTask}
                onClick={startTask}
              >
                开始整本解析
              </Button>
              {file && <Tag color="blue">{file.name}</Tag>}
            </Space>
          </Space>
        </Card>
      )}

      {currentStep === 1 && (
        <Card title="整本解析任务状态" style={{ marginBottom: 16 }}>
          {!taskId ? (
            <Empty description="尚未创建任务" />
          ) : (
            <div style={{ textAlign: 'center', padding: '24px 0' }}>
              <Progress
                type="circle"
                percent={taskStatus?.progress || 0}
                status={
                  taskStatus?.status === 'failed'
                    ? 'exception'
                    : taskStatus?.status === 'completed'
                      ? 'success'
                      : 'active'
                }
              />

              <div style={{ marginTop: 24 }}>
                <Text strong style={{ fontSize: 16 }}>
                  {taskStatus?.status === 'pending' && '等待调度中...'}
                  {taskStatus?.status === 'running' && '正在解析整本 TXT...'}
                  {taskStatus?.status === 'completed' && '解析完成，正在准备预览...'}
                  {taskStatus?.status === 'failed' && '解析失败'}
                  {taskStatus?.status === 'cancelled' && '任务已取消'}
                </Text>
                {taskStatus?.message && (
                  <div style={{ marginTop: 8 }}>
                    <Text type="secondary">{taskStatus.message}</Text>
                  </div>
                )}
              </div>

              {taskStatus?.error && (
                <Alert
                  type="error"
                  message={taskStatus.error}
                  showIcon
                  style={{ marginTop: 16, textAlign: 'left' }}
                />
              )}

              <Space style={{ marginTop: 24 }}>
                <Button icon={<ReloadOutlined />} onClick={refreshStatus}>
                  刷新状态
                </Button>
                {taskStatus && ['pending', 'running'].includes(taskStatus.status) && (
                  <Button danger icon={<StopOutlined />} onClick={cancelTask}>
                    取消任务
                  </Button>
                )}
                {taskStatus && ['failed', 'cancelled'].includes(taskStatus.status) && (
                  <Button onClick={resetTaskState}>重新上传</Button>
                )}
              </Space>
            </div>
          )}
        </Card>
      )}

      {currentStep >= 2 && !continuationWorkbenchProjectId && (
        <Card
          title="确认二创工作台配置"
          extra={(
            <Button
              type="primary"
              icon={<CopyOutlined />}
              loading={creatingProject}
              disabled={!preview}
              onClick={createProject}
            >
              {createButtonText}
            </Button>
          )}
        >
          <Spin spinning={loadingPreview || creatingProject}>
            {!preview ? (
              <Empty description="预览加载中" />
            ) : (
              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                {preview.warnings.length > 0 && (
                  <Alert
                    type="warning"
                    showIcon
                    message="解析提示"
                    description={(
                      <ul style={{ margin: 0, paddingLeft: 18 }}>
                        {preview.warnings.map((warning, index) => (
                          <li key={`${warning.code}-${index}`}>
                            [{warning.level}] {warning.message}
                          </li>
                        ))}
                      </ul>
                    )}
                  />
                )}

                <Row gutter={[16, 16]}>
                  <Col xs={24} md={8}>
                    <Card size="small">
                      <Space direction="vertical" size={4}>
                        <Text type="secondary">模式</Text>
                        <Text strong>{MODE_META[preview.remix_mode].title}</Text>
                      </Space>
                    </Card>
                  </Col>
                  <Col xs={24} md={8}>
                    <Card size="small">
                      <Space direction="vertical" size={4}>
                        <Text type="secondary">识别章节</Text>
                        <Text strong>{preview.detected_total_chapters} 章</Text>
                      </Space>
                    </Card>
                  </Col>
                  <Col xs={24} md={8}>
                    <Card size="small">
                      <Space direction="vertical" size={4}>
                        <Text type="secondary">全文字数</Text>
                        <Text strong>{formatWordCount(preview.total_words)}</Text>
                      </Space>
                    </Card>
                  </Col>
                </Row>

                <Card size="small" title="项目建议">
                  <Row gutter={[12, 12]}>
                    <Col xs={24} md={12}>
                      <Text>工作台标题</Text>
                      <Input
                        value={preview.project_suggestion.title}
                        onChange={(event) => handleSuggestionTitleChange(event.target.value)}
                      />
                    </Col>
                    <Col xs={24} md={12}>
                      <Text>题材类型</Text>
                      <Input
                        value={preview.project_suggestion.genre ?? ''}
                        onChange={(event) => updateSuggestion({ genre: event.target.value })}
                      />
                    </Col>
                    <Col xs={24}>
                      <Text>主题定位</Text>
                      <TextArea
                        rows={3}
                        value={preview.project_suggestion.theme ?? ''}
                        onChange={(event) => updateSuggestion({ theme: event.target.value })}
                      />
                    </Col>
                    <Col xs={24}>
                      <Text>项目说明</Text>
                      <TextArea
                        rows={4}
                        value={preview.project_suggestion.description ?? ''}
                        onChange={(event) => updateSuggestion({ description: event.target.value })}
                      />
                    </Col>
                    <Col xs={24} md={12}>
                      <Text>叙事视角</Text>
                      <Input
                        value={preview.project_suggestion.narrative_perspective}
                        onChange={(event) => updateSuggestion({ narrative_perspective: event.target.value })}
                      />
                    </Col>
                    <Col xs={24} md={12}>
                      <Text>目标字数</Text>
                      <InputNumber
                        min={1000}
                        style={{ width: '100%' }}
                        value={preview.project_suggestion.target_words}
                        onChange={(value) => {
                          if (value !== null) {
                            updateSuggestion({ target_words: Number(value) });
                          }
                        }}
                      />
                    </Col>
                  </Row>
                </Card>

                {preview.remix_mode === 'continuation' && (
                  <Card size="small" title="续写起步包">
                    <Space direction="vertical" size={16} style={{ width: '100%' }}>
                      <Alert
                        type="warning"
                        showIcon
                        message="已切换为 Workbench-first 流程"
                        description="当前流程会在创建项目后先进入 Bible / Continuation Plan 审校工作台。此处不再提供可编辑的续写起步包参数，避免配置无效选项。"
                      />
                      <Alert
                        type="info"
                        showIcon
                        message="说明"
                        description="如果后续需要自动起步包能力，将在工作台确认链路中接入，避免当前“可配但不生效”的误导。"
                      />
                    </Space>
                  </Card>
                )}

                {preview.remix_mode === 'inspired' && (
                  <Card size="small" title="同类创作起步包">
                    <Space direction="vertical" size={16} style={{ width: '100%' }}>
                      <Alert
                        type="info"
                        showIcon
                        message="推荐开启"
                        description="创建原书分析工作台后，自动派生一个独立新项目，并先生成一版同类型的新故事骨架。"
                      />

                      <Checkbox
                        checked={autoCreateInspiredPack}
                        onChange={(event) => setAutoCreateInspiredPack(event.target.checked)}
                      >
                        创建工作台后自动派生同类创作项目
                      </Checkbox>

                      {autoCreateInspiredPack && (
                        <Row gutter={[12, 12]}>
                          <Col xs={24} md={12}>
                            <Text>新项目标题</Text>
                            <Input
                              value={inspiredProjectTitle}
                              onChange={(event) => setInspiredProjectTitle(event.target.value)}
                              placeholder="例如：原书名 - 新创作稿"
                            />
                          </Col>
                          <Col xs={24} md={6}>
                            <Text>骨架章节数</Text>
                            <InputNumber
                              min={3}
                              max={50}
                              style={{ width: '100%' }}
                              value={inspiredChapterCount}
                              onChange={(value) => setInspiredChapterCount(Math.max(3, Number(value) || 12))}
                            />
                          </Col>
                          <Col xs={24} md={6}>
                            <Text>新项目模式</Text>
                            <Input value="传统模式 1→1" disabled />
                          </Col>
                          <Col xs={24} md={8}>
                            <Text>改造强度</Text>
                            <Select
                              style={{ width: '100%' }}
                              value={inspiredRemixStrength}
                              onChange={(value) => setInspiredRemixStrength(value as InspiredRemixStrength)}
                              options={INSPIRED_STRENGTH_OPTIONS}
                            />
                          </Col>
                          <Col xs={24} md={16}>
                            <Alert
                              type="success"
                              showIcon
                              message={`当前策略：${INSPIRED_STRENGTH_GUIDE[inspiredRemixStrength].label}`}
                              description={INSPIRED_STRENGTH_GUIDE[inspiredRemixStrength].summary}
                            />
                          </Col>
                          <Col xs={24}>
                            <Text>新故事方向</Text>
                            <TextArea
                              rows={3}
                              value={inspiredConcept}
                              onChange={(event) => setInspiredConcept(event.target.value)}
                              placeholder="例如：保留都市异能+组织对抗的爽点，但改成近未来海港城市背景。"
                            />
                          </Col>
                          <Col xs={24} md={12}>
                            <Text>人物 / 组织改造</Text>
                            <TextArea
                              rows={3}
                              value={inspiredCharacterDirection}
                              onChange={(event) => setInspiredCharacterDirection(event.target.value)}
                              placeholder="例如：主角改成落魄鉴证师，反派组织改成商业财团与地下研究所。"
                            />
                          </Col>
                          <Col xs={24} md={12}>
                            <Text>能力体系改造</Text>
                            <TextArea
                              rows={3}
                              value={inspiredAbilityDirection}
                              onChange={(event) => setInspiredAbilityDirection(event.target.value)}
                              placeholder="例如：把血脉觉醒改成记忆接口、协议共鸣或遗物授权体系。"
                            />
                          </Col>
                          <Col xs={24} md={12}>
                            <Text>世界观改造</Text>
                            <TextArea
                              rows={3}
                              value={inspiredWorldDirection}
                              onChange={(event) => setInspiredWorldDirection(event.target.value)}
                              placeholder="例如：改成雨港都市、废土航路、赛博宗门等不同底层规则。"
                            />
                          </Col>
                          <Col xs={24} md={12}>
                            <Text>剧情细节改造</Text>
                            <TextArea
                              rows={3}
                              value={inspiredPlotDirection}
                              onChange={(event) => setInspiredPlotDirection(event.target.value)}
                              placeholder="例如：首卷从追查失踪案切入，不沿用原书的拜师或觉醒顺序。"
                            />
                          </Col>
                          <Col xs={24}>
                            <Text>禁用元素</Text>
                            <TextArea
                              rows={2}
                              value={inspiredForbiddenElements}
                              onChange={(event) => setInspiredForbiddenElements(event.target.value)}
                              placeholder="例如：不要沿用原书地名、组织简称、神器名、最终反派身份。"
                            />
                          </Col>
                          <Col xs={24}>
                            <Text>补充要求</Text>
                            <TextArea
                              rows={3}
                              value={inspiredRequirements}
                              onChange={(event) => setInspiredRequirements(event.target.value)}
                              placeholder="例如：替换人物姓名和能力体系，避免照搬原书关键事件顺序。"
                            />
                          </Col>
                          <Col xs={24}>
                            <Alert
                              type="info"
                              showIcon
                              message="本次同类创作将自动带上这些改造策略"
                              description={(
                                <ul style={{ margin: 0, paddingLeft: 18 }}>
                                  {inspiredStrategySummary.map((line, index) => (
                                    <li key={`${line}-${index}`}>{line}</li>
                                  ))}
                                </ul>
                              )}
                            />
                          </Col>
                          <Col xs={24}>
                            <Alert
                              type="success"
                              showIcon
                              message="可编辑变体映射表"
                              description="下面这些原元素是系统从整本内容里启发式提取的草案。你可以直接指定谁改成谁、哪些体系要换、哪些剧情母题要重写。"
                            />
                          </Col>
                          <Col xs={24} xl={12}>
                            {renderInspiredSeedEditor(
                              'characters',
                              '人物映射表',
                              '为该人物重新命名，并改写其身份关系或核心性格抓手。',
                            )}
                          </Col>
                          <Col xs={24} xl={12}>
                            {renderInspiredSeedEditor(
                              'organizations',
                              '组织映射表',
                              '为这个组织重新命名，并改写其定位、势力结构或目标。',
                            )}
                          </Col>
                          <Col xs={24} xl={12}>
                            {renderInspiredSeedEditor(
                              'abilities',
                              '能力体系映射表',
                              '替换为新的能力名词，并重写升级逻辑或使用代价。',
                            )}
                          </Col>
                          <Col xs={24} xl={12}>
                            {renderInspiredSeedEditor(
                              'world_elements',
                              '世界观 / 地点映射表',
                              '调整地理背景、权力格局或世界规则，不要直接沿用原设定。',
                            )}
                          </Col>
                          <Col xs={24}>
                            {renderInspiredSeedEditor(
                              'plot_threads',
                              '剧情母题改写表',
                              '改写这一段剧情的触发事件、冲突对象或结局落点。',
                            )}
                          </Col>
                          {inspiredMappingSummary.length > 0 && (
                            <Col xs={24}>
                              <Alert
                                type="info"
                                showIcon
                                message="当前显式映射摘要"
                                description={(
                                  <ul style={{ margin: 0, paddingLeft: 18 }}>
                                    {inspiredMappingSummary.map((line, index) => (
                                      <li key={`${line}-${index}`}>{line}</li>
                                    ))}
                                  </ul>
                                )}
                              />
                            </Col>
                          )}
                          <Col xs={24}>
                            <Card
                              size="small"
                              title="首批正文自动化"
                              style={{ background: 'var(--color-bg-container)' }}
                            >
                              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                                <Checkbox
                                  checked={autoGenerateInspiredContent}
                                  onChange={(event) => setAutoGenerateInspiredContent(event.target.checked)}
                                >
                                  骨架生成后自动启动首批正文生成
                                </Checkbox>

                                {autoGenerateInspiredContent && (
                                  <Row gutter={[12, 12]}>
                                    <Col xs={24} md={8}>
                                      <Text>首批生成章节数</Text>
                                      <InputNumber
                                        min={1}
                                        max={10}
                                        style={{ width: '100%' }}
                                        value={inspiredInitialContentCount}
                                        onChange={(value) => setInspiredInitialContentCount(Math.max(1, Number(value) || 3))}
                                      />
                                    </Col>
                                    <Col xs={24} md={8}>
                                      <Text>单章目标字数</Text>
                                      <InputNumber
                                        min={1000}
                                        max={6000}
                                        step={100}
                                        style={{ width: '100%' }}
                                        value={inspiredChapterTargetWordCount}
                                        onChange={(value) => setInspiredChapterTargetWordCount(Math.max(1000, Number(value) || 2600))}
                                      />
                                    </Col>
                                    <Col xs={24} md={8}>
                                      <Text>完成后跳转</Text>
                                      <Input value="章节页 / 批量生成进度" disabled />
                                    </Col>
                                    <Col xs={24}>
                                      <Checkbox
                                        checked={inspiredEnableChapterAnalysis}
                                        onChange={(event) => setInspiredEnableChapterAnalysis(event.target.checked)}
                                      >
                                        生成正文时同步启动章节分析
                                      </Checkbox>
                                    </Col>
                                  </Row>
                                )}
                              </Space>
                            </Card>
                          </Col>
                        </Row>
                      )}
                    </Space>
                  </Card>
                )}

                <Card
                  size="small"
                  title={`章节预览（显示前 ${visibleChapters.length} 章，共 ${preview.detected_total_chapters} 章）`}
                >
                  <List
                    dataSource={visibleChapters}
                    renderItem={(chapter) => (
                      <List.Item>
                        <List.Item.Meta
                          title={(
                            <Space>
                              <Tag color="blue">第 {chapter.chapter_number} 章</Tag>
                              <span>{chapter.title}</span>
                              <Text type="secondary">{formatWordCount(chapter.word_count)} 字</Text>
                            </Space>
                          )}
                          description={chapter.summary || '暂无摘要'}
                        />
                      </List.Item>
                    )}
                  />
                  {preview.detected_total_chapters > visibleChapters.length && (
                    <Paragraph style={{ marginTop: 12, marginBottom: 0, color: 'var(--color-text-secondary)' }}>
                      为了界面可读性，这里只展示前 {visibleChapters.length} 章；创建工作台时会导入整本内容并按整本启动分析。
                    </Paragraph>
                  )}
                </Card>
              </Space>
            )}
          </Spin>
        </Card>
      )}

      {continuationWorkbenchProjectId && (
        <Card title="续写工作台（Bible / Continuation Plan）" style={{ marginBottom: 16 }}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Alert
              type="success"
              showIcon
              message="项目已创建成功"
              description={(
                <Space wrap>
                  <Text>project_id: {continuationWorkbenchProjectId}</Text>
                  <Button size="small" onClick={() => navigate(`/project/${continuationWorkbenchProjectId}/chapter-analysis`)}>
                    打开章节分析页
                  </Button>
                  <Button size="small" onClick={() => navigate(`/project/${continuationWorkbenchProjectId}/outline`)}>
                    打开大纲页
                  </Button>
                </Space>
              )}
            />

            <BookRemixSourceDiscoveryPanel />

            <BookRemixBibleReview
              value={bibleDraft}
              loading={loadingBibleDraft}
              saving={savingBibleDraft}
              confirming={confirmingBibleDraft}
              regenerating={regeneratingBibleDraft}
              onRefresh={() => loadBibleDraft()}
              onSave={saveBibleDraft}
              onConfirm={confirmBibleDraft}
              onRegenerate={regenerateBibleDraft}
            />

            <BookRemixAnalysisCoveragePanel
              value={analysisCoverage}
              lastStartMissingResult={lastStartMissingResult}
              loading={loadingAnalysisCoverage}
              starting={startingMissingAnalysis}
              onRefresh={() => loadAnalysisCoverage()}
              onStartMissingAnalysis={startMissingAnalysis}
              onOpenChapterAnalysis={() => navigate(`/project/${continuationWorkbenchProjectId}/chapter-analysis`)}
              onOpenChapters={() => navigate(`/project/${continuationWorkbenchProjectId}/chapters`)}
            />

            <BookRemixContinuationProgressSummaryPanel
              value={continuationProgressSummary}
              loading={loadingContinuationProgressSummary}
              onRefresh={() => loadContinuationProgressSummary()}
            />

            <BookRemixChapterChangePackageAuditPanel
              value={chapterChangePackages}
              loading={loadingChapterChangePackages}
              onRefresh={() => loadChapterChangePackages()}
            />

            <BookRemixContinuationPlanPanel
              value={continuationPlan}
              bibleStatus={bibleDraft?.generation_status}
              planOutdated={isContinuationPlanOutdated}
              loading={loadingContinuationPlan}
              generating={generatingContinuationPlan}
              saving={savingContinuationPlan}
              confirming={confirmingContinuationPlan}
              onRefresh={() => loadContinuationPlan()}
              onGenerate={generateContinuationPlanDraft}
              onSave={saveContinuationPlanDraft}
              onConfirm={confirmContinuationPlanDraft}
            />

            <BookRemixContinuationContextPreviewPanel
              value={continuationContextPreview}
              loading={loadingContinuationContextPreview}
              onRefresh={() => loadContinuationContextPreview()}
            />
          </Space>
        </Card>
      )}

      <Modal
        open={starterPackVisible}
        title={starterPackTitle}
        footer={null}
        closable={false}
        maskClosable={false}
      >
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Alert
            type="info"
            showIcon
            message="工作台已经创建成功"
            description="当前正在自动准备后续起步包。完成后会自动跳转到对应项目页。"
          />
          <Progress percent={starterPackProgress} status="active" />
          <Text type="secondary">{starterPackMessage}</Text>
        </Space>
      </Modal>
    </div>
  );
}
