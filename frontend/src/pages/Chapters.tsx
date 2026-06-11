import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { List, Button, Modal, Form, Input, Select, message, Empty, Space, Badge, Tag, Card, InputNumber, Alert, Radio, Descriptions, Collapse, Popconfirm, Pagination } from 'antd';
import { EditOutlined, FileTextOutlined, ThunderboltOutlined, LockOutlined, DownloadOutlined, SettingOutlined, FundOutlined, SyncOutlined, CheckCircleOutlined, CloseCircleOutlined, RocketOutlined, StopOutlined, InfoCircleOutlined, CaretRightOutlined, DeleteOutlined, BookOutlined, FormOutlined, PlusOutlined, ReadOutlined } from '@ant-design/icons';
import { useStore } from '../store';
import { useChapterSync } from '../store/hooks';
import { projectApi, writingStyleApi, chapterApi, outlineApi, bookRemixApi } from '../services/api';
import type {
  Chapter,
  ChapterGuardrailReviewResponse,
  ChapterGuardrailViolation,
  ChapterUpdate,
  ApiError,
  WritingStyle,
  AnalysisTask,
  ExpansionPlanData,
} from '../types';
import type { TextAreaRef } from 'antd/es/input/TextArea';
import ChapterAnalysis from '../components/ChapterAnalysis';
import ExpansionPlanEditor from '../components/ExpansionPlanEditor';
import { SSELoadingOverlay } from '../components/SSELoadingOverlay';
import { SSEProgressModal } from '../components/SSEProgressModal';
import ChapterReader from '../components/ChapterReader';
import PartialRegenerateToolbar from '../components/PartialRegenerateToolbar';
import PartialRegenerateModal from '../components/PartialRegenerateModal';
const { TextArea } = Input;
// localStorage 缓存键名
const WORD_COUNT_CACHE_KEY = 'chapter_default_word_count';
const DEFAULT_WORD_COUNT = 3000;
const CONTINUATION_PLAN_STORAGE_PREFIX = 'chapters_continuation_plan';
const DEFAULT_CONTINUATION_SEGMENT_SIZE = 10;
const MAX_CONTINUATION_CHAPTERS = 200;
type BatchGeneratePayload = Parameters<typeof chapterApi.batchGenerate>[1];
type ContinuationRiskHighDetail = {
  code?: string;
  message?: string;
  continuation_risk?: ContinuationRiskSummary;
};
type ContinuationRiskSummary = {
  level?: string;
  label?: string;
  can_continue?: boolean;
  message?: string;
  blocking_chapter_numbers?: number[];
  warning_chapter_numbers?: number[];
  reasons?: string[];
  reason_labels?: string[];
};
const getApiErrorDetail = (error: unknown): string | ContinuationRiskHighDetail | undefined => {
  const apiError = error as ApiError;
  return apiError.response?.data?.detail;
};
const getApiErrorMessage = (error: unknown): string => {
  const detail = getApiErrorDetail(error);
  if (typeof detail === 'string') {
    return detail;
  }
  if (detail?.message) {
    return detail.message;
  }
  return (error as Error).message || '未知错误';
};
const getContinuationRiskHighDetail = (error: unknown): ContinuationRiskHighDetail | null => {
  const detail = getApiErrorDetail(error);
  if (detail && typeof detail === 'object' && detail.code === 'continuation_risk_high') {
    return detail;
  }
  return null;
};
const formatChapterNumbers = (items?: number[]): string =>
  items?.length ? items.map(number => `第${number}章`).join('、') : '';

const buildContinuationRiskSummaryContent = (
  risk?: ContinuationRiskSummary | null,
  fallbackMessage = '续写前仍有阻断章节，建议先补齐全书拆解缺口。'
): string => {
  const blocking = formatChapterNumbers(risk?.blocking_chapter_numbers);
  const warning = formatChapterNumbers(risk?.warning_chapter_numbers);
  const labels = risk?.reason_labels?.length
    ? `风险原因：${risk.reason_labels.join('、')}`
    : '';
  return [
    risk?.message || fallbackMessage,
    blocking ? `阻断章节：${blocking}` : '仍有阻断章节未补齐',
    warning ? `上下文偏薄章节：${warning}` : '',
    labels,
    '可到“书籍重混 / 分析覆盖率”面板补跑缺口分析。',
  ]
    .filter(Boolean)
    .join('\n');
};
const buildContinuationRiskConfirmContent = (detail: ContinuationRiskHighDetail): string =>
  buildContinuationRiskSummaryContent(
    detail.continuation_risk,
    detail.message || '续写前仍有阻断章节，建议先补齐全书拆解缺口。'
  );
type BatchProgressState = {
  status: string;
  total: number;
  completed: number;
  current_chapter_number: number | null;
  current_stage?: string | null;
  stage_message?: string | null;
  current_stage_progress?: number | null;
  current_retry_count?: number | null;
  max_retries?: number | null;
  estimated_time_minutes?: number;
  error_message?: string | null;
};
const BATCH_STATUS_POLL_INTERVAL_MS = 4000;
const BATCH_VIEW_REFRESH_INTERVAL_MS = 12000;
type ContinuationFormValues = {
  chapterCount: number;
  storyDirection?: string;
  plotStage: 'development' | 'climax' | 'ending';
  chaptersPerOutline: number;
  styleId?: number;
  targetWordCount?: number;
  model?: string;
};
type ContinuationPlanState = {
  projectId: string;
  totalChapters: number;
  remainingChapters: number;
  segmentSize: number;
  chaptersPerOutline: number;
  storyDirection?: string;
  plotStage: 'development' | 'climax' | 'ending';
  styleId?: number;
  targetWordCount: number;
  model?: string;
  currentBatchId?: string | null;
  currentBatchPlannedCount?: number;
  status: 'preparing' | 'running' | 'failed' | 'cancelled';
  forceHighRiskContinuation?: boolean;
  updatedAt: string;
};
// 从 localStorage 读取缓存的字数
const getCachedWordCount = (): number => {
  try {
    const cached = localStorage.getItem(WORD_COUNT_CACHE_KEY);
    if (cached) {
      const value = parseInt(cached, 10);
      if (!isNaN(value) && value >= 500 && value <= 10000) {
        return value;
      }
    }
  } catch (error) {
    console.warn('读取字数缓存失败:', error);
  }
  return DEFAULT_WORD_COUNT;
};
// 保存字数到 localStorage
const setCachedWordCount = (value: number): void => {
  try {
    localStorage.setItem(WORD_COUNT_CACHE_KEY, String(value));
  } catch (error) {
    console.warn('保存字数缓存失败:', error);
  }
};
const getContinuationPlanStorageKey = (projectId: string): string =>
  `${CONTINUATION_PLAN_STORAGE_PREFIX}:${projectId}`;
const loadContinuationPlan = (projectId: string): ContinuationPlanState | null => {
  try {
    const cached = localStorage.getItem(getContinuationPlanStorageKey(projectId));
    if (!cached) {
      return null;
    }
    const parsed = JSON.parse(cached) as Partial<ContinuationPlanState>;
    if (!parsed || parsed.projectId !== projectId) {
      return null;
    }
    if (
      typeof parsed.totalChapters !== 'number'
      || typeof parsed.remainingChapters !== 'number'
      || typeof parsed.chaptersPerOutline !== 'number'
      || typeof parsed.targetWordCount !== 'number'
      || !parsed.plotStage
    ) {
      return null;
    }
    return {
      projectId,
      totalChapters: parsed.totalChapters,
      remainingChapters: parsed.remainingChapters,
      segmentSize: typeof parsed.segmentSize === 'number' ? parsed.segmentSize : DEFAULT_CONTINUATION_SEGMENT_SIZE,
      chaptersPerOutline: parsed.chaptersPerOutline,
      storyDirection: parsed.storyDirection,
      plotStage: parsed.plotStage,
      styleId: parsed.styleId,
      targetWordCount: parsed.targetWordCount,
      model: parsed.model,
      currentBatchId: parsed.currentBatchId ?? null,
      currentBatchPlannedCount: parsed.currentBatchPlannedCount,
      status: parsed.status || 'preparing',
      forceHighRiskContinuation: parsed.forceHighRiskContinuation === true,
      updatedAt: parsed.updatedAt || new Date().toISOString(),
    };
  } catch (error) {
    console.warn('çè¯²å½ç¼îåçâ³åç¼æ³ç¨æ¾¶è¾«è§¦:', error);
    return null;
  }
};
const persistContinuationPlan = (plan: ContinuationPlanState): void => {
  try {
    localStorage.setItem(getContinuationPlanStorageKey(plan.projectId), JSON.stringify(plan));
  } catch (error) {
    console.warn('æ·æ¿ç¨ç¼îåçâ³åç¼æ³ç¨æ¾¶è¾«è§¦:', error);
  }
};
const clearContinuationPlan = (projectId: string): void => {
  try {
    localStorage.removeItem(getContinuationPlanStorageKey(projectId));
  } catch (error) {
    console.warn('å¨å¯æç¼îåçâ³åç¼æ³ç¨æ¾¶è¾«è§¦:', error);
  }
};
const shouldBlockContinuationByRisk = (risk?: ContinuationRiskSummary | null): boolean => (
  Boolean(risk && (risk.can_continue === false || risk.level === 'high'))
);
export default function Chapters() {
  const { currentProject, chapters, outlines, setCurrentChapter, setCurrentProject } = useStore();
  const [modal, contextHolder] = Modal.useModal();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isContinuing, setIsContinuing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();
  const [editorForm] = Form.useForm();
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const contentTextAreaRef = useRef<TextAreaRef>(null);
  const [writingStyles, setWritingStyles] = useState<WritingStyle[]>([]);
  const [selectedStyleId, setSelectedStyleId] = useState<number | undefined>();
  const [targetWordCount, setTargetWordCount] = useState<number>(getCachedWordCount);
  const [availableModels, setAvailableModels] = useState<Array<{ value: string, label: string }>>([]);
  const [selectedModel, setSelectedModel] = useState<string | undefined>();
  const [batchSelectedModel, setBatchSelectedModel] = useState<string | undefined>(); // 批量生成的模型选择
  const [temporaryNarrativePerspective, setTemporaryNarrativePerspective] = useState<string | undefined>(); // 临时人称选择
  const [analysisVisible, setAnalysisVisible] = useState(false);
  const [analysisChapterId, setAnalysisChapterId] = useState<string | null>(null);
  // 分析任务状态管理
  const [analysisTasksMap, setAnalysisTasksMap] = useState<Record<string, AnalysisTask>>({});
  const analysisPollingIntervalRef = useRef<number | null>(null);
  const activeAnalysisPollingIdsRef = useRef<Set<string>>(new Set());
  // 列表查询与分页状态
  const [chapterSearchKeyword, setChapterSearchKeyword] = useState('');
  const [chapterPage, setChapterPage] = useState(1);
  const [chapterPageSize, setChapterPageSize] = useState(20);
  // é
// 读器状态
  const [readerVisible, setReaderVisible] = useState(false);
  const [readingChapter, setReadingChapter] = useState<Chapter | null>(null);
  // 规划编辑状态
  const [planEditorVisible, setPlanEditorVisible] = useState(false);
  const [editingPlanChapter, setEditingPlanChapter] = useState<Chapter | null>(null);
  // 局部重写状态
  const [partialRegenerateToolbarVisible, setPartialRegenerateToolbarVisible] = useState(false);
  const [partialRegenerateToolbarPosition, setPartialRegenerateToolbarPosition] = useState({ top: 0, left: 0 });
  const [selectedTextForRegenerate, setSelectedTextForRegenerate] = useState('');
  const [selectionStartPosition, setSelectionStartPosition] = useState(0);
  const [selectionEndPosition, setSelectionEndPosition] = useState(0);
  const [partialRegenerateModalVisible, setPartialRegenerateModalVisible] = useState(false);
  // 单章节生成进度状态
  const [singleChapterProgress, setSingleChapterProgress] = useState(0);
  const [singleChapterProgressMessage, setSingleChapterProgressMessage] = useState('');
  // æ¹éçæç¸å
// ³ç¶æ
  const [batchGenerateVisible, setBatchGenerateVisible] = useState(false);
  const [batchGenerating, setBatchGenerating] = useState(false);
  const [batchAnalyzingUnanalyzed, setBatchAnalyzingUnanalyzed] = useState(false);
  const [batchTaskId, setBatchTaskId] = useState<string | null>(null);
  const [batchForm] = Form.useForm();
  const [continuationForm] = Form.useForm();
  const [manualCreateForm] = Form.useForm();
  const [batchProgress, setBatchProgress] = useState<BatchProgressState | null>(null);
  const batchPollingIntervalRef = useRef<number | null>(null);
  const batchPollingRequestInFlightRef = useRef(false);
  const batchLastListRefreshAtRef = useRef(0);
  const batchLastRefreshSnapshotRef = useRef<{
    completed: number;
    currentChapterNumber: number | null;
  } | null>(null);
  const [continuationVisible, setContinuationVisible] = useState(false);
  const [continuationRunning, setContinuationRunning] = useState(false);
  const [continuationProgress, setContinuationProgress] = useState(0);
  const [continuationMessage, setContinuationMessage] = useState('');
  const [continuationSelectedModel, setContinuationSelectedModel] = useState<string | undefined>();
  const [continuationPlanState, setContinuationPlanState] = useState<ContinuationPlanState | null>(null);
  const continuationPlanStateRef = useRef<ContinuationPlanState | null>(null);
  const continuationPlanRunningRef = useRef(false);
  useEffect(() => {
    continuationPlanStateRef.current = continuationPlanState;
  }, [continuationPlanState]);
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  // å¤çææ¬éä¸­ - æ£æµéä¸­ææ¬å¹¶æ¾ç¤ºæµ®å¨å·¥å
// ·æ
  const handleTextSelection = useCallback(() => {
    // 只在编辑器打开时处理选中
    if (!isEditorOpen || isGenerating) {
      setPartialRegenerateToolbarVisible(false);
      return;
    }
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) {
      setPartialRegenerateToolbarVisible(false);
      return;
    }
    const selectedText = selection.toString().trim();
    // è³å°éä¸­10ä¸ªå­ç¬¦ææ¾ç¤ºå·¥å
// ·æ
    if (selectedText.length < 10) {
      setPartialRegenerateToolbarVisible(false);
      return;
    }
    // æ£æ¥éä¸­æ¯å¦å¨ TextArea å
    const textArea = contentTextAreaRef.current?.resizableTextArea?.textArea;
    if (!textArea) {
      setPartialRegenerateToolbarVisible(false);
      return;
    }
    // æ£æ¥éä¸­æ¯å¦å¨ textarea å
// （需要特殊处理，因为 textarea 的选中不会创建 range）
    if (document.activeElement !== textArea) {
      setPartialRegenerateToolbarVisible(false);
      return;
    }
    // 获取 textarea 中的选中位置
    const start = textArea.selectionStart;
    const end = textArea.selectionEnd;
    const textContent = textArea.value;
    const selectedInTextArea = textContent.substring(start, end);
    if (selectedInTextArea.trim().length < 10) {
      setPartialRegenerateToolbarVisible(false);
      return;
    }
    // è®¡ç®æµ®å¨å·¥å
// ·æ ä½ç½®
    const rect = textArea.getBoundingClientRect();
    const computedStyle = window.getComputedStyle(textArea);
    const lineHeight = parseFloat(computedStyle.lineHeight) || 24;
    const paddingTop = parseFloat(computedStyle.paddingTop) || 0;
    // 计算选中文本起始位置所在的行号
    const textBeforeSelection = textContent.substring(0, start);
    const startLine = textBeforeSelection.split('\\n').length - 1;
    // 计算选中文本在 textarea 中的视觉位置
    // éè¦èè scrollTopï¼textarea å
// 部滚动偏移）
    const scrollTop = textArea.scrollTop;
    const visualTop = (startLine * lineHeight) + paddingTop - scrollTop;
    // å·¥å
// ·æ ä½ç½®ï¼textarea é¡¶é¨ + éä¸­ææ¬çè§è§ä½ç½® - å·¥å
// ·æ é«åº¦åç§»
    const toolbarTop = rect.top + visualTop - 45;
    // æ°´å¹³ä½ç½®ï¼æ¾å¨ textarea çå³ä¾§åºåï¼é¿å
// é®æ¡ææ¬
    const toolbarLeft = rect.right - 180;
    setSelectedTextForRegenerate(selectedInTextArea);
    setSelectionStartPosition(start);
    setSelectionEndPosition(end);
    // è®¡ç®å·¥å
// ·æ ä½ç½®ï¼å¦æéä¸­ä½ç½®ä¸å¨å¯è§åºåå
// ，固定在边缘
    let finalTop = toolbarTop;
    if (visualTop < 0) {
      finalTop = rect.top + 10;
    } else if (visualTop > textArea.clientHeight) {
      finalTop = rect.bottom - 50;
    }
    setPartialRegenerateToolbarPosition({
      top: Math.max(rect.top + 10, Math.min(finalTop, rect.bottom - 50)),
      left: Math.min(Math.max(rect.left + 20, toolbarLeft), window.innerWidth - 200),
    });
    setPartialRegenerateToolbarVisible(true);
  }, [isEditorOpen, isGenerating]);
  // æ´æ°å·¥å
// ·æ ä½ç½®çå½æ°ï¼ä¸æ£æµéä¸­ï¼åªæ´æ°ä½ç½®ï¼
  const updateToolbarPosition = useCallback(() => {
    if (!partialRegenerateToolbarVisible || !selectedTextForRegenerate) return;
    const textArea = contentTextAreaRef.current?.resizableTextArea?.textArea;
    if (!textArea) return;
    const rect = textArea.getBoundingClientRect();
    const computedStyle = window.getComputedStyle(textArea);
    const lineHeight = parseFloat(computedStyle.lineHeight) || 24;
    const paddingTop = parseFloat(computedStyle.paddingTop) || 0;
    const textContent = textArea.value;
    const textBeforeSelection = textContent.substring(0, selectionStartPosition);
    const startLine = textBeforeSelection.split('\\n').length - 1;
    const scrollTop = textArea.scrollTop;
    const visualTop = (startLine * lineHeight) + paddingTop - scrollTop;
    const toolbarTop = rect.top + visualTop - 45;
    // 固定在 textarea 右上角，不随选中位置变化
    const toolbarLeft = rect.right - 180;
    // å·¥å
// ·æ åºå®å¨ textarea å¯è§åºåå
// ，即使选中文本滚出视野也保持显示
    // å¦æéä¸­ä½ç½®å¨å¯è§åºåå
// ，跟随选中位置
    // 如果滚出视野，固定在顶部或底部边缘
    let finalTop = toolbarTop;
    if (visualTop < 0) {
      // éä¸­ä½ç½®å¨ä¸æ¹è§éå¤ï¼å·¥å
// ·æ åºå®å¨é¡¶é¨
      finalTop = rect.top + 10;
    } else if (visualTop > textArea.clientHeight) {
      // éä¸­ä½ç½®å¨ä¸æ¹è§éå¤ï¼å·¥å
// ·æ åºå®å¨åºé¨
      finalTop = rect.bottom - 50;
    }
    setPartialRegenerateToolbarPosition({
      top: Math.max(rect.top + 10, Math.min(finalTop, rect.bottom - 50)),
      left: Math.min(Math.max(rect.left + 20, toolbarLeft), window.innerWidth - 200),
    });
  }, [partialRegenerateToolbarVisible, selectedTextForRegenerate, selectionStartPosition]);
  // 监听选中事件
  useEffect(() => {
    if (!isEditorOpen) return;
    const textArea = contentTextAreaRef.current?.resizableTextArea?.textArea;
    if (!textArea) return;
    const handleMouseUp = () => {
      // 鼠标释放时检查选中
      setTimeout(handleTextSelection, 50);
    };
    const handleKeyUp = (e: KeyboardEvent) => {
      // Shift + 方向键选中时检查
      if (e.shiftKey && ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
        setTimeout(handleTextSelection, 50);
      }
    };
    const handleScroll = () => {
      // 滚动时更新位置（使用 requestAnimationFrame 优化性能）
      requestAnimationFrame(updateToolbarPosition);
    };
    // 监听 textarea 滚动
    textArea.addEventListener('mouseup', handleMouseUp);
    textArea.addEventListener('keyup', handleKeyUp);
    textArea.addEventListener('scroll', handleScroll);
    // åæ¶çå¬ Modal body æ»å¨ï¼Modal å
// 容可能在外层容器滚动）
    const modalBody = textArea.closest('.ant-modal-body');
    if (modalBody) {
      modalBody.addEventListener('scroll', handleScroll);
    }
    // 监听窗口大小变化
    window.addEventListener('resize', handleScroll);
    return () => {
      textArea.removeEventListener('mouseup', handleMouseUp);
      textArea.removeEventListener('keyup', handleKeyUp);
      textArea.removeEventListener('scroll', handleScroll);
      if (modalBody) {
        modalBody.removeEventListener('scroll', handleScroll);
      }
      window.removeEventListener('resize', handleScroll);
    };
  }, [isEditorOpen, handleTextSelection, updateToolbarPosition]);
  // ç¹å»å
// ¶ä»åºåæ¶éèå·¥å
// ·æ
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      // å¦æç¹å»çæ¯å·¥å
// ·æ ï¼ä¸éè
      if (target.closest('[data-partial-regenerate-toolbar]')) {
        return;
      }
      // 如果点击的是 textarea，不隐藏
      if (target.tagName === 'TEXTAREA') {
        return;
      }
      // å¦æç¹å»çæ¯ Modal å
// é¨ï¼å
// 括滚动条），不隐藏
      if (target.closest('.ant-modal-content')) {
        return;
      }
      // ç¹å» Modal å¤é¨æéèå·¥å
// ·æ
      setPartialRegenerateToolbarVisible(false);
    };
    if (partialRegenerateToolbarVisible) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [partialRegenerateToolbarVisible]);
  const {
    refreshChapters,
    updateChapter,
    deleteChapter,
    generateChapterContentStream
  } = useChapterSync();
  useEffect(() => {
    if (!currentProject?.id) {
      setContinuationPlanState(null);
      continuationPlanStateRef.current = null;
      return;
    }
    let cancelled = false;
    void (async () => {
      const latestChapters = await refreshChapters();
      if (cancelled) {
        return;
      }
      await loadWritingStyles();
      if (cancelled) {
        return;
      }
      await loadAnalysisTasks(latestChapters);
      if (cancelled) {
        return;
      }
      let hasActiveBatchTask = false;
      try {
        const response = await fetch(`/api/chapters/project/${currentProject.id}/batch-generate/active`);
        if (response.ok) {
          const data = await response.json();
          if (data.has_active_task && data.task) {
            hasActiveBatchTask = true;
          }
        }
      } catch (error) {
        console.error('检查批量生成任务失败', error);
      }
      if (cancelled) {
        return;
      }
      const storedPlan = loadContinuationPlan(currentProject.id);
      if (storedPlan) {
        const restoredPlan: ContinuationPlanState =
          hasActiveBatchTask
            ? {
                ...storedPlan,
                status: 'running',
                updatedAt: new Date().toISOString(),
              }
            : {
                ...storedPlan,
                currentBatchId: null,
                currentBatchPlannedCount: undefined,
                status:
                  storedPlan.remainingChapters > 0
                  && storedPlan.status !== 'failed'
                  && storedPlan.status !== 'cancelled'
                    ? 'preparing'
                    : storedPlan.status,
                updatedAt: new Date().toISOString(),
              };
        setContinuationPlanState(restoredPlan);
        continuationPlanStateRef.current = restoredPlan;
        persistContinuationPlan(restoredPlan);
      } else {
        setContinuationPlanState(null);
        continuationPlanStateRef.current = null;
      }
      await checkAndRestoreBatchTask();
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentProject?.id]);
  // æ¸
// 理轮询定时器
  useEffect(() => {
    const batchPollingInterval = batchPollingIntervalRef.current;
    return () => {
      if (analysisPollingIntervalRef.current) {
        clearInterval(analysisPollingIntervalRef.current);
        analysisPollingIntervalRef.current = null;
      }
      if (batchPollingInterval) {
        clearInterval(batchPollingInterval);
      }
    };
  }, []);
  const clearAnalysisPollingIfIdle = useCallback(() => {
    if (activeAnalysisPollingIdsRef.current.size === 0 && analysisPollingIntervalRef.current) {
      clearInterval(analysisPollingIntervalRef.current);
      analysisPollingIntervalRef.current = null;
    }
  }, []);
  const pollActiveAnalysisTasks = useCallback(async () => {
    if (!currentProject?.id) return;
    const activeIds = Array.from(activeAnalysisPollingIdsRef.current);
    if (activeIds.length === 0) {
      clearAnalysisPollingIfIdle();
      return;
    }
    try {
      const response = await chapterApi.getBatchAnalysisStatuses(currentProject.id, activeIds);
      const tasksMap = response.items || {};
      setAnalysisTasksMap(prev => ({
        ...prev,
        ...tasksMap,
      }));
      activeIds.forEach((chapterId) => {
        const task = tasksMap[chapterId];
        if (!task || task.status === 'completed' || task.status === 'failed' || task.status === 'none') {
          activeAnalysisPollingIdsRef.current.delete(chapterId);
          if (task?.status === 'completed') {
            message.success('章节分析完成');
          } else if (task?.status === 'failed') {
            message.error(`章节分析失败: ${task.error_message || '未知错误'}`);
          }
        }
      });
      clearAnalysisPollingIfIdle();
    } catch (error) {
      console.error('批量轮询分析任务失败:', error);
    }
  }, [clearAnalysisPollingIfIdle, currentProject?.id]);
  const ensureAnalysisPolling = useCallback(() => {
    if (analysisPollingIntervalRef.current) return;
    analysisPollingIntervalRef.current = window.setInterval(() => {
      void pollActiveAnalysisTasks();
    }, 2000);
    // 立即执行一次
    void pollActiveAnalysisTasks();
  }, [pollActiveAnalysisTasks]);
  // å è½½ææç« èçåæä»»å¡ç¶æï¼æ¹éæ¥å£ï¼é¿å
// éç« è¯·æ±é£æ´ï¼
  // 接受可选的 chaptersToLoad 参数，解决 React 状态更新延迟导致的问题
  const loadAnalysisTasks = async (
    chaptersToLoad?: typeof chapters,
    options?: { enableAutoPolling?: boolean }
  ) => {
    const targetChapters = chaptersToLoad || chapters;
    if (!targetChapters || targetChapters.length === 0 || !currentProject?.id) return;
    const enableAutoPolling = options?.enableAutoPolling ?? true;
    const chapterIds = targetChapters
      .filter(chapter => chapter.content && chapter.content.trim() !== '')
      .map(chapter => chapter.id);
    if (chapterIds.length === 0) {
      setAnalysisTasksMap({});
      activeAnalysisPollingIdsRef.current.clear();
      clearAnalysisPollingIfIdle();
      return;
    }
    try {
      const response = await chapterApi.getBatchAnalysisStatuses(currentProject.id, chapterIds);
      const tasksMap = response.items || {};
      setAnalysisTasksMap(tasksMap);
      activeAnalysisPollingIdsRef.current.clear();
      if (enableAutoPolling) {
        Object.entries(tasksMap).forEach(([chapterId, task]) => {
          if (task?.status === 'pending' || task?.status === 'running') {
            activeAnalysisPollingIdsRef.current.add(chapterId);
          }
        });
      }
      if (enableAutoPolling && activeAnalysisPollingIdsRef.current.size > 0) {
        ensureAnalysisPolling();
      } else {
        clearAnalysisPollingIfIdle();
      }
    } catch (error) {
      console.error('批量加载分析任务状态失败:', error);
    }
  };
  // å¯å¨åä¸ªç« èçä»»å¡è½®è¯¢ï¼å
// 部合并到批量轮询）
  const startPollingTask = (chapterId: string) => {
    activeAnalysisPollingIdsRef.current.add(chapterId);
    ensureAnalysisPolling();
  };
  const loadWritingStyles = async () => {
    if (!currentProject?.id) return;
    try {
      const response = await writingStyleApi.getProjectStyles(currentProject.id);
      setWritingStyles(response.styles);
      // 设置默认风格为初始选中
      const defaultStyle = response.styles.find(s => s.is_default);
      if (defaultStyle) {
        setSelectedStyleId(defaultStyle.id);
      }
    } catch (error) {
      console.error('加载写作风格失败:', error);
      message.error('加载写作风格失败');
    }
  };
  const loadAvailableModels = async () => {
    try {
      // ä»è®¾ç½®APIè·åç¨æ·é
// ç½®çæ¨¡ååè¡¨
      const settingsResponse = await fetch('/api/settings');
      if (settingsResponse.ok) {
        const settings = await settingsResponse.json();
        const { api_key, api_base_url, api_provider } = settings;
        if (api_key && api_base_url) {
          try {
            const modelsResponse = await fetch(
              `/api/settings/models?api_key=${encodeURIComponent(api_key)}&api_base_url=${encodeURIComponent(api_base_url)}&provider=${api_provider}`
            );
            if (modelsResponse.ok) {
              const data = await modelsResponse.json();
              if (data.models && data.models.length > 0) {
                setAvailableModels(data.models);
                // è®¾ç½®é»è®¤æ¨¡åä¸ºå½åé
// ç½®çæ¨¡å
                setSelectedModel(settings.llm_model);
                return settings.llm_model; // 返回模型名称
              }
            }
          } catch {
            console.log('获取模型列表失败，将使用默认模型');
          }
        }
      }
    } catch (error) {
      console.error('加载可用模型失败:', error);
    }
    return null;
  };
  // 检查并恢复批量生成任务
  const checkAndRestoreBatchTask = async () => {
    if (!currentProject?.id) return null;
    try {
      const response = await fetch(`/api/chapters/project/${currentProject.id}/batch-generate/active`);
      if (!response.ok) return null;
      const data = await response.json();
      if (data.has_active_task && data.task) {
        const task = data.task;
        setBatchTaskId(task.batch_id);
        setBatchProgress({
          status: task.status,
          total: task.total,
          completed: task.completed,
          current_chapter_number: task.current_chapter_number,
          current_stage: task.current_stage,
          stage_message: task.stage_message,
          current_stage_progress: task.current_stage_progress,
        });
        setBatchGenerating(true);
        setBatchGenerateVisible(false);
        startBatchPolling(task.batch_id);
        message.info('检测到未完成的批量生成任务，已自动恢复');
      }
    } catch (error) {
      console.error('检查批量生成任务失败:', error);
    }
  };
  const showBrowserNotification = (title: string, body: string, type: 'success' | 'error' | 'info' = 'info') => {
    // 检查浏览器是否支持通知
    if (!('Notification' in window)) {
      console.log('浏览器不支持通知功能');
      return;
    }
    // 检查通知权限
    if (Notification.permission === 'granted') {
      // 选择图标
      const icon = type === 'success' ? '/logo.svg' : type === 'error' ? '/favicon.ico' : '/logo.svg';
      const notification = new Notification(title, {
        body,
        icon,
        badge: '/favicon.ico',
        tag: 'batch-generation', // 相同tag会替换旧通知
        requireInteraction: false, // 自动关闭
        silent: false, // 播放提示音
      });
      // 点击通知时聚焦到窗口
      notification.onclick = () => {
        window.focus();
        notification.close();
      };
      // 5秒后自动关闭
      setTimeout(() => {
        notification.close();
      }, 5000);
    } else if (Notification.permission !== 'denied') {
      // 如果权限未被明确拒绝，尝试请求权限
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          showBrowserNotification(title, body, type);
        }
      });
    }
  };
  // æç« èå·æåºå¹¶æå¤§çº²åç»ç« è (å¿
// é¡»å¨æ©è¿åä¹åè°ç¨ï¼é¿å
// è¿å Hooks è§å)
  const { sortedChapters } = useMemo(() => {
    const sorted = [...chapters].sort((a, b) => a.chapter_number - b.chapter_number);
    const groups: Record<string, {
      outlineId: string | null;
      outlineTitle: string;
      outlineOrder: number;
      chapters: Chapter[];
    }> = {};
    sorted.forEach(chapter => {
      const key = chapter.outline_id || 'uncategorized';
      if (!groups[key]) {
        groups[key] = {
          outlineId: chapter.outline_id || null,
          outlineTitle: chapter.outline_title || '未分类章节',
          outlineOrder: chapter.outline_order ?? 999,
          chapters: []
        };
      }
      groups[key].chapters.push(chapter);
    });
    return { sortedChapters: sorted };
  }, [chapters]);
  // 章节查询过滤（前端过滤，减少渲染压力）
  const filteredSortedChapters = useMemo(() => {
    const keyword = chapterSearchKeyword.trim().toLowerCase();
    if (!keyword) return sortedChapters;
    return sortedChapters.filter((chapter) => {
      return (
        String(chapter.chapter_number).includes(keyword) ||
        chapter.title.toLowerCase().includes(keyword) ||
        (chapter.outline_title || '').toLowerCase().includes(keyword)
      );
    });
  }, [sortedChapters, chapterSearchKeyword]);
  // 分页后的扁平章节
  const pagedSortedChapters = useMemo(() => {
    const start = (chapterPage - 1) * chapterPageSize;
    return filteredSortedChapters.slice(start, start + chapterPageSize);
  }, [filteredSortedChapters, chapterPage, chapterPageSize]);
  // one-to-many 模式分页后再按大纲分组
  const pagedGroupedChapters = useMemo(() => {
    const groups: Record<string, {
      outlineId: string | null;
      outlineTitle: string;
      outlineOrder: number;
      chapters: Chapter[];
    }> = {};
    pagedSortedChapters.forEach(chapter => {
      const key = chapter.outline_id || 'uncategorized';
      if (!groups[key]) {
        groups[key] = {
          outlineId: chapter.outline_id || null,
          outlineTitle: chapter.outline_title || '未分类章节',
          outlineOrder: chapter.outline_order ?? 999,
          chapters: []
        };
      }
      groups[key].chapters.push(chapter);
    });
    return Object.values(groups).sort((a, b) => a.outlineOrder - b.outlineOrder);
  }, [pagedSortedChapters]);
  // 搜索词或分页大小变化时重置到第一页
  useEffect(() => {
    setChapterPage(1);
  }, [chapterSearchKeyword, chapterPageSize, currentProject?.outline_mode]);
  // 数据变化导致页码越界时自动纠正
  useEffect(() => {
    const maxPage = Math.max(1, Math.ceil(filteredSortedChapters.length / chapterPageSize));
    if (chapterPage > maxPage) {
      setChapterPage(maxPage);
    }
  }, [filteredSortedChapters.length, chapterPage, chapterPageSize]);
  // é¢è®¡ç®æ¯ç« å¯çæç¶æï¼é¿å
// å¨æ¸²æé¶æ®µéå¤ O(nÂ²) æ«æ
  const chapterGenerateGateMap = useMemo(() => {
    const gateMap: Record<string, { canGenerate: boolean; reason: string }> = {};
    const incompleteChapterNumbers: number[] = [];
    const unanalyzedChapters: Array<{ chapterNumber: number; reason: string }> = [];
    sortedChapters.forEach((chapter) => {
      if (incompleteChapterNumbers.length > 0) {
        gateMap[chapter.id] = {
          canGenerate: false,
          reason: `éè¦å
å®æåç½®ç« èï¼ç¬¬ ${incompleteChapterNumbers.join('ã')} ç« `
        };
      } else if (unanalyzedChapters.length > 0) {
        gateMap[chapter.id] = {
          canGenerate: false,
          reason: `éè¦å
åæåç½®ç« èï¼ç¬¬ ${unanalyzedChapters.map(c => c.chapterNumber).join('ã')} ç«  (${unanalyzedChapters.map(c => c.reason).join('ã')})`
        };
      } else {
        gateMap[chapter.id] = { canGenerate: true, reason: '' };
      }
      // å°å½åç« çº³å
// ¥âåç»­ç« èâçåç½®æ¡ä»¶
      if (!chapter.content || chapter.content.trim() === '') {
        incompleteChapterNumbers.push(chapter.chapter_number);
      } else if (chapter.status === 'review_required') {
        incompleteChapterNumbers.push(chapter.chapter_number);
      }
      const task = analysisTasksMap[chapter.id];
      if (!task || !task.has_task) {
        unanalyzedChapters.push({ chapterNumber: chapter.chapter_number, reason: '未分析' });
      } else if (task.status === 'pending') {
        unanalyzedChapters.push({ chapterNumber: chapter.chapter_number, reason: 'ç­å¾分析' });
      } else if (task.status === 'running') {
        unanalyzedChapters.push({ chapterNumber: chapter.chapter_number, reason: '分析中' });
      } else if (task.status === 'failed') {
        unanalyzedChapters.push({ chapterNumber: chapter.chapter_number, reason: '分析失败' });
      } else if (task.status !== 'completed') {
        unanalyzedChapters.push({ chapterNumber: chapter.chapter_number, reason: '状态未知' });
      }
    });
    return gateMap;
  }, [sortedChapters, analysisTasksMap]);
  // 当前可被“一键分析”的章节：有内容且未处于完成/进行中。
  const batchAnalyzableChapterCount = useMemo(() => {
    return sortedChapters.filter((chapter) => {
      if (!chapter.content || chapter.content.trim() === '') return false;
      const task = analysisTasksMap[chapter.id];
      if (!task || !task.has_task) return true;
      return task.status !== 'completed' && task.status !== 'pending' && task.status !== 'running';
    }).length;
  }, [sortedChapters, analysisTasksMap]);
  if (!currentProject) return null;
  // 获取人称的中文显示文本（同时支持中英文值）
  const getNarrativePerspectiveText = (perspective?: string): string => {
    const texts: Record<string, string> = {
      // 英文枚举值映射，兼容旧数据。
      'first_person': '第一人称（我）',
      'third_person': '第三人称（他/她）',
      'omniscient': '全知视角',
      // 中文值映射（项目设置使用）
      '第一人称': '第一人称（我）',
      '第三人称': '第三人称（他/她）',
      '全知视角': '全知视角',
    };
    return texts[perspective || ''] || '第三人称（默认）';
  };
  const canGenerateChapter = (chapter: Chapter): boolean => {
    return chapterGenerateGateMap[chapter.id]?.canGenerate ?? true;
  };
  const getGenerateDisabledReason = (chapter: Chapter): string => {
    return chapterGenerateGateMap[chapter.id]?.reason || '';
  };
  const refreshBatchRelatedViews = useCallback(async (
    options?: { includeProject?: boolean; enableAnalysisPolling?: boolean }
  ) => {
    const includeProject = options?.includeProject ?? false;
    const enableAnalysisPolling = options?.enableAnalysisPolling ?? true;
    const latestChapters = await refreshChapters();
    await loadAnalysisTasks(latestChapters, { enableAutoPolling: enableAnalysisPolling });
    if (includeProject && currentProject?.id) {
      const updatedProject = await projectApi.getProject(currentProject.id);
      setCurrentProject(updatedProject);
    }
    return latestChapters;
  }, [currentProject?.id, loadAnalysisTasks, refreshChapters, setCurrentProject]);
  const resetBatchRefreshTracking = useCallback(() => {
    batchPollingRequestInFlightRef.current = false;
    batchLastListRefreshAtRef.current = 0;
    batchLastRefreshSnapshotRef.current = null;
  }, []);
  const shouldRefreshBatchViews = useCallback((status: BatchProgressState) => {
    const currentChapterNumber = status.current_chapter_number ?? null;
    const snapshot = batchLastRefreshSnapshotRef.current;
    const now = Date.now();
    const shouldRefresh = (
      !snapshot
      || snapshot.completed !== status.completed
      || snapshot.currentChapterNumber !== currentChapterNumber
      || now - batchLastListRefreshAtRef.current >= BATCH_VIEW_REFRESH_INTERVAL_MS
    );
    batchLastRefreshSnapshotRef.current = {
      completed: status.completed,
      currentChapterNumber,
    };
    if (shouldRefresh) {
      batchLastListRefreshAtRef.current = now;
    }
    return shouldRefresh;
  }, []);
  const getPendingChapters = useCallback((chapterList?: Chapter[]) => {
    const source = (chapterList || sortedChapters).slice().sort((a, b) => a.chapter_number - b.chapter_number);
    return source.filter((chapter) => !chapter.content || chapter.content.trim() === '');
  }, [sortedChapters]);
  const getContiguousPendingChapters = useCallback((chapterList?: Chapter[]) => {
    const pendingChapters = getPendingChapters(chapterList);
    if (pendingChapters.length === 0) {
      return [];
    }
    const contiguousChapters: Chapter[] = [pendingChapters[0]];
    for (let index = 1; index < pendingChapters.length; index += 1) {
      const previousChapter = pendingChapters[index - 1];
      const currentChapter = pendingChapters[index];
      if (currentChapter.chapter_number !== previousChapter.chapter_number + 1) {
        break;
      }
      contiguousChapters.push(currentChapter);
    }
    return contiguousChapters;
  }, [getPendingChapters]);
  const getBatchProgressPercent = useCallback((progress: BatchProgressState | null) => {
    if (!progress) {
      return 0;
    }
    if (progress.status === 'completed') {
      return 100;
    }
    if (!progress.total || progress.total <= 0) {
      return Math.max(0, Math.min(100, progress.current_stage_progress ?? 0));
    }
    const completedPercent = (progress.completed / progress.total) * 100;
    const stageCanBlend =
      Boolean(progress.current_chapter_number)
      && !['completed', 'failed', 'cancelled', 'finalizing'].includes(progress.current_stage || '');
    const stagePercent = stageCanBlend
      ? ((progress.current_stage_progress ?? 0) / 100) * (100 / progress.total)
      : 0;
    return Math.max(0, Math.min(100, Math.round(completedPercent + stagePercent)));
  }, []);
  const buildBatchProgressMessage = useCallback((progress: BatchProgressState | null) => {
    if (!progress) {
      return '批量生成准备中...';
    }
    const progressSuffix = `(${progress.completed}/${progress.total})`;
    if (progress.stage_message && progress.stage_message.trim()) {
      return `${progress.stage_message} ${progressSuffix}`;
    }
    if (progress.current_chapter_number) {
      return `正在处理第 ${progress.current_chapter_number} 章 ${progressSuffix}`;
    }
    return `批量生成进行中 ${progressSuffix}`;
  }, []);
  const launchBatchGeneration = useCallback(async (requestBody: BatchGeneratePayload) => {
    if (!currentProject?.id) {
      throw new Error('当前项目不存在');
    }
    const result = await chapterApi.batchGenerate(currentProject.id, requestBody);
    setBatchTaskId(result.batch_id);
    setBatchProgress({
      status: 'running',
      total: result.chapters_to_generate.length,
      completed: 0,
      current_chapter_number: requestBody.start_chapter_number,
      current_stage: 'queued',
      stage_message: result.message || '批量任务已创建，等待开始',
      current_stage_progress: 0,
      estimated_time_minutes: result.estimated_time_minutes,
    });
    setBatchGenerating(true);
    setBatchGenerateVisible(false);
    startBatchPolling(result.batch_id);
    return result;
  }, [currentProject?.id]);
  /*
  /*
  /*
  /*
  // 旧版自动续写逻辑（已废弃）
    if (!currentProject?.id || plan.projectId !== currentProject.id) {
      return;
    }
    if (continuationPlanRunningRef.current) {
      return;
    }
    continuationPlanRunningRef.current = true;
    const segmentTarget = Math.min(plan.segmentSize, plan.remainingChapters);
    const chaptersPerOutline = Math.max(plan.chaptersPerOutline || 1, 1);
    try {
      setContinuationRunning(true);
      setContinuationProgress(5);
      setContinuationMessage(`正在准备自动续写本轮 ${segmentTarget} 章...`);
      let latestChapters = await refreshChapters();
      let pendingChapters = getContiguousPendingChapters(latestChapters);
      const missingChapterCount = Math.max(0, segmentTarget - pendingChapters.length);
      if (missingChapterCount > 0) {
        const outlineCount = currentProject.outline_mode === 'one-to-many'
          ? Math.max(1, Math.ceil(missingChapterCount / chaptersPerOutline))
          : missingChapterCount;
        const outlineResult = await outlineApi.generateOutlineStream(
          {
            project_id: currentProject.id,
            genre: currentProject.genre,
            theme: currentProject.theme || currentProject.description || '延续当前故事主线',
            chapter_count: outlineCount,
            narrative_perspective: currentProject.narrative_perspective || '第三人称',
            target_words: currentProject.target_words,
            mode: 'continue',
            story_direction: plan.storyDirection?.trim() || undefined,
            plot_stage: plan.plotStage,
            model: plan.model,
          },
          {
            onProgress: (progressMessage, progress) => {
              setContinuationProgress(Math.max(10, Math.min(55, progress ?? 10)));
              setContinuationMessage(progressMessage || '正在补充续写大纲...');
            },
          },
        );
        await loadWritingStyles();
        latestChapters = await refreshChapters();
        pendingChapters = getContiguousPendingChapters(latestChapters);
        if (pendingChapters.length < segmentTarget && currentProject.outline_mode === 'one-to-many') {
          const outlinesToExpand = outlineResult.outlines?.length
            ? outlineResult.outlines
            : [];
          if (!outlinesToExpand.length) {
            throw new Error('未找到可展开的续写大纲');
          }
          await outlineApi.batchExpandOutlinesStream(
            {
              project_id: currentProject.id,
              outline_ids: outlinesToExpand.map((item) => item.id),
              chapters_per_outline: chaptersPerOutline,
              expansion_strategy: 'balanced',
              auto_create_chapters: true,
              model: plan.model,
            },
            {
              onProgress: (progressMessage, progress) => {
                const normalizedProgress = progress == null ? 60 : Math.min(90, Math.max(60, progress));
                setContinuationProgress(normalizedProgress);
                setContinuationMessage(progressMessage || '正在将续写大纲展开为章节...');
              },
            },
          );
          await loadWritingStyles();
          latestChapters = await refreshChapters();
          pendingChapters = getContiguousPendingChapters(latestChapters);
        }
      }
      if (pendingChapters.length === 0) {
        throw new Error('未找到可续写的空白章节');
      }
      const firstPendingChapter = pendingChapters[0];
      if (!canGenerateChapter(firstPendingChapter)) {
        throw new Error(getGenerateDisabledReason(firstPendingChapter));
      }
      const requestCount = Math.min(segmentTarget, pendingChapters.length);
      const runningPlan: ContinuationPlanState = {
        ...plan,
        currentBatchId: null,
        currentBatchPlannedCount: requestCount,
        status: 'running',
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(runningPlan);
      continuationPlanStateRef.current = runningPlan;
      persistContinuationPlan(runningPlan);
      setContinuationProgress(95);
      setContinuationMessage(`本轮 ${requestCount} 章已准备就绪，正在启动...`);
      const result = await launchBatchGeneration({
        start_chapter_number: firstPendingChapter.chapter_number,
        count: requestCount,
        enable_analysis: true,
        enable_workflow: true,
        workflow_auto_regenerate: true,
        workflow_max_rounds: 2,
        workflow_min_score: 7.8,
        style_id: plan.styleId,
        target_word_count: plan.targetWordCount,
        model: plan.model,
        force_high_risk_continuation: plan.forceHighRiskContinuation || undefined,
      });
      const startedPlan: ContinuationPlanState = {
        ...runningPlan,
        currentBatchId: result.batch_id,
        forceHighRiskContinuation: false,
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(startedPlan);
      continuationPlanStateRef.current = startedPlan;
      persistContinuationPlan(startedPlan);
    } catch (error) {
      const err = error as Error;
      const failedPlan: ContinuationPlanState = {
        ...plan,
        currentBatchId: null,
        currentBatchPlannedCount: undefined,
        status: 'failed',
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(failedPlan);
      continuationPlanStateRef.current = failedPlan;
      persistContinuationPlan(failedPlan);
      message.error(`自动续写失败：${err.message || '未知错误'}`);
    } finally {
      setContinuationRunning(false);
      continuationPlanRunningRef.current = false;
    }
  }, [
    canGenerateChapter,
    currentProject,
    getContiguousPendingChapters,
    getGenerateDisabledReason,
    launchBatchGeneration,
    refreshChapters,
  ]);
  */
  /* 旧版自动续写逻辑（已废弃）
    if (!currentProject?.id || plan.projectId !== currentProject.id) {
      return;
    }
    if (continuationPlanRunningRef.current) {
      return;
    }
    continuationPlanRunningRef.current = true;
    const segmentTarget = Math.min(plan.segmentSize, plan.remainingChapters);
    const chaptersPerOutline = Math.max(plan.chaptersPerOutline || 1, 1);
    try {
      setContinuationRunning(true);
      setContinuationProgress(5);
      setContinuationMessage(`正在准备自动续写本轮 ${segmentTarget} 章...`);
      let latestChapters = await refreshChapters();
      let pendingChapters = getContiguousPendingChapters(latestChapters);
      const missingChapterCount = Math.max(0, segmentTarget - pendingChapters.length);
      if (missingChapterCount > 0) {
        const outlineCount = currentProject.outline_mode === 'one-to-many'
          ? Math.max(1, Math.ceil(missingChapterCount / chaptersPerOutline))
          : missingChapterCount;
        const outlineResult = await outlineApi.generateOutlineStream(
          {
            project_id: currentProject.id,
            genre: currentProject.genre,
            theme: currentProject.theme || currentProject.description || '延续当前故事主线',
            chapter_count: outlineCount,
            narrative_perspective: currentProject.narrative_perspective || '第三人称',
            target_words: currentProject.target_words,
            mode: 'continue',
            story_direction: plan.storyDirection?.trim() || undefined,
            plot_stage: plan.plotStage,
            model: plan.model,
          },
          {
            onProgress: (progressMessage, progress) => {
              setContinuationProgress(Math.max(10, Math.min(55, progress ?? 10)));
              setContinuationMessage(progressMessage || '正在补充续写大纲...');
            },
          },
        );
        await loadWritingStyles();
        latestChapters = await refreshChapters();
        pendingChapters = getContiguousPendingChapters(latestChapters);
        if (pendingChapters.length < segmentTarget && currentProject.outline_mode === 'one-to-many') {
          const outlinesToExpand = outlineResult.outlines?.length
            ? outlineResult.outlines
            : [];
          if (!outlinesToExpand.length) {
            throw new Error('未找到可展开的续写大纲');
          }
          await outlineApi.batchExpandOutlinesStream(
            {
              project_id: currentProject.id,
              outline_ids: outlinesToExpand.map((item) => item.id),
              chapters_per_outline: chaptersPerOutline,
              expansion_strategy: 'balanced',
              auto_create_chapters: true,
              model: plan.model,
            },
            {
              onProgress: (progressMessage, progress) => {
                const normalizedProgress = progress == null ? 60 : Math.min(90, Math.max(60, progress));
                setContinuationProgress(normalizedProgress);
                setContinuationMessage(progressMessage || '正在将续写大纲展开为章节...');
              },
            },
          );
          await loadWritingStyles();
          latestChapters = await refreshChapters();
          pendingChapters = getContiguousPendingChapters(latestChapters);
        }
      }
      if (pendingChapters.length === 0) {
        throw new Error('未找到可续写的空白章节');
      }
      const firstPendingChapter = pendingChapters[0];
      if (!canGenerateChapter(firstPendingChapter)) {
        throw new Error(getGenerateDisabledReason(firstPendingChapter));
      }
      const requestCount = Math.min(segmentTarget, pendingChapters.length);
      const runningPlan: ContinuationPlanState = {
        ...plan,
        currentBatchId: null,
        currentBatchPlannedCount: requestCount,
        status: 'running',
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(runningPlan);
      continuationPlanStateRef.current = runningPlan;
      persistContinuationPlan(runningPlan);
      setContinuationProgress(95);
      setContinuationMessage(`本轮 ${requestCount} 章已准备就绪，正在启动...`);
      const result = await launchBatchGeneration({
        start_chapter_number: firstPendingChapter.chapter_number,
        count: requestCount,
        enable_analysis: true,
        enable_workflow: true,
        workflow_auto_regenerate: true,
        workflow_max_rounds: 2,
        workflow_min_score: 7.8,
        style_id: plan.styleId,
        target_word_count: plan.targetWordCount,
        model: plan.model,
        force_high_risk_continuation: plan.forceHighRiskContinuation || undefined,
      });
      const startedPlan: ContinuationPlanState = {
        ...runningPlan,
        currentBatchId: result.batch_id,
        forceHighRiskContinuation: false,
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(startedPlan);
      continuationPlanStateRef.current = startedPlan;
      persistContinuationPlan(startedPlan);
    } catch (error) {
      const err = error as Error;
      const failedPlan: ContinuationPlanState = {
        ...plan,
        currentBatchId: null,
        currentBatchPlannedCount: undefined,
        status: 'failed',
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(failedPlan);
      continuationPlanStateRef.current = failedPlan;
      persistContinuationPlan(failedPlan);
      message.error(`自动续写失败：${err.message || '未知错误'}`);
    } finally {
      setContinuationRunning(false);
      continuationPlanRunningRef.current = false;
    }
  }, [
    canGenerateChapter,
    currentProject,
    getContiguousPendingChapters,
    getGenerateDisabledReason,
    launchBatchGeneration,
    refreshChapters,
  ]);
  */
  /* 旧版自动续写逻辑（已废弃）
    if (!currentProject?.id || plan.projectId !== currentProject.id) {
      return;
    }
    if (continuationPlanRunningRef.current) {
      return;
    }
    continuationPlanRunningRef.current = true;
    const segmentTarget = Math.min(plan.segmentSize, plan.remainingChapters);
    const chaptersPerOutline = Math.max(plan.chaptersPerOutline || 1, 1);
    try {
      setContinuationRunning(true);
      setContinuationProgress(5);
      setContinuationMessage(`正在准备自动续写本轮 ${segmentTarget} 章...`);
      let latestChapters = await refreshChapters();
      let pendingChapters = getContiguousPendingChapters(latestChapters);
      const missingChapterCount = Math.max(0, segmentTarget - pendingChapters.length);
      if (missingChapterCount > 0) {
        const outlineCount = currentProject.outline_mode === 'one-to-many'
          ? Math.max(1, Math.ceil(missingChapterCount / chaptersPerOutline))
          : missingChapterCount;
        const outlineResult = await outlineApi.generateOutlineStream(
          {
            project_id: currentProject.id,
            genre: currentProject.genre,
            theme: currentProject.theme || currentProject.description || '延续当前故事主线',
            chapter_count: outlineCount,
            narrative_perspective: currentProject.narrative_perspective || '第三人称',
            target_words: currentProject.target_words,
            mode: 'continue',
            story_direction: plan.storyDirection?.trim() || undefined,
            plot_stage: plan.plotStage,
            model: plan.model,
          },
          {
            onProgress: (progressMessage, progress) => {
              setContinuationProgress(Math.max(10, Math.min(55, progress ?? 10)));
              setContinuationMessage(progressMessage || '正在补充续写大纲...');
            },
          },
        );
        await loadWritingStyles();
        latestChapters = await refreshChapters();
        pendingChapters = getContiguousPendingChapters(latestChapters);
        if (pendingChapters.length < segmentTarget && currentProject.outline_mode === 'one-to-many') {
          const outlinesToExpand = outlineResult.outlines?.length
            ? outlineResult.outlines
            : [];
          if (!outlinesToExpand.length) {
            throw new Error('未找到可展开的续写大纲');
          }
          await outlineApi.batchExpandOutlinesStream(
            {
              project_id: currentProject.id,
              outline_ids: outlinesToExpand.map((item) => item.id),
              chapters_per_outline: chaptersPerOutline,
              expansion_strategy: 'balanced',
              auto_create_chapters: true,
              model: plan.model,
            },
            {
              onProgress: (progressMessage, progress) => {
                const normalizedProgress = progress == null ? 60 : Math.min(90, Math.max(60, progress));
                setContinuationProgress(normalizedProgress);
                setContinuationMessage(progressMessage || '正在将续写大纲展开为章节...');
              },
            },
          );
          await loadWritingStyles();
          latestChapters = await refreshChapters();
          pendingChapters = getContiguousPendingChapters(latestChapters);
        }
      }
      if (pendingChapters.length === 0) {
        throw new Error('未找到可续写的空白章节');
      }
      const firstPendingChapter = pendingChapters[0];
      if (!canGenerateChapter(firstPendingChapter)) {
        throw new Error(getGenerateDisabledReason(firstPendingChapter));
      }
      const requestCount = Math.min(segmentTarget, pendingChapters.length);
      const runningPlan: ContinuationPlanState = {
        ...plan,
        currentBatchId: null,
        currentBatchPlannedCount: requestCount,
        status: 'running',
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(runningPlan);
      continuationPlanStateRef.current = runningPlan;
      persistContinuationPlan(runningPlan);
      setContinuationProgress(95);
      setContinuationMessage(`本轮 ${requestCount} 章已准备就绪，正在启动...`);
      const result = await launchBatchGeneration({
        start_chapter_number: firstPendingChapter.chapter_number,
        count: requestCount,
        enable_analysis: true,
        enable_workflow: true,
        workflow_auto_regenerate: true,
        workflow_max_rounds: 2,
        workflow_min_score: 7.8,
        style_id: plan.styleId,
        target_word_count: plan.targetWordCount,
        model: plan.model,
        force_high_risk_continuation: plan.forceHighRiskContinuation || undefined,
      });
      const startedPlan: ContinuationPlanState = {
        ...runningPlan,
        currentBatchId: result.batch_id,
        forceHighRiskContinuation: false,
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(startedPlan);
      continuationPlanStateRef.current = startedPlan;
      persistContinuationPlan(startedPlan);
    } catch (error) {
      const err = error as Error;
      const failedPlan: ContinuationPlanState = {
        ...plan,
        currentBatchId: null,
        currentBatchPlannedCount: undefined,
        status: 'failed',
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(failedPlan);
      continuationPlanStateRef.current = failedPlan;
      persistContinuationPlan(failedPlan);
      message.error(`自动续写失败：${err.message || '未知错误'}`);
    } finally {
      setContinuationRunning(false);
      continuationPlanRunningRef.current = false;
    }
  }, [
    canGenerateChapter,
    currentProject,
    getContiguousPendingChapters,
    getGenerateDisabledReason,
    launchBatchGeneration,
    refreshChapters,
  ]);
  */
  /* 旧版自动续写逻辑（已废弃）
    if (!currentProject?.id || plan.projectId !== currentProject.id) {
      return;
    }
    if (continuationPlanRunningRef.current) {
      return;
    }
    continuationPlanRunningRef.current = true;
    const segmentTarget = Math.min(plan.segmentSize, plan.remainingChapters);
    const chaptersPerOutline = Math.max(plan.chaptersPerOutline || 1, 1);
    try {
      setContinuationRunning(true);
      setContinuationProgress(5);
      setContinuationMessage(`正在准备自动续写本轮 ${segmentTarget} 章...`);
      let latestChapters = await refreshChapters();
      let pendingChapters = getContiguousPendingChapters(latestChapters);
      const missingChapterCount = Math.max(0, segmentTarget - pendingChapters.length);
      if (missingChapterCount > 0) {
        const outlineCount = currentProject.outline_mode === 'one-to-many'
          ? Math.max(1, Math.ceil(missingChapterCount / chaptersPerOutline))
          : missingChapterCount;
        const outlineResult = await outlineApi.generateOutlineStream(
          {
            project_id: currentProject.id,
            genre: currentProject.genre,
            theme: currentProject.theme || currentProject.description || '延续当前故事主线',
            chapter_count: outlineCount,
            narrative_perspective: currentProject.narrative_perspective || '第三人称',
            target_words: currentProject.target_words,
            mode: 'continue',
            story_direction: plan.storyDirection?.trim() || undefined,
            plot_stage: plan.plotStage,
            model: plan.model,
          },
          {
            onProgress: (progressMessage, progress) => {
              setContinuationProgress(Math.max(10, Math.min(55, progress ?? 10)));
              setContinuationMessage(progressMessage || '正在补充续写大纲...');
            },
          },
        );
        await loadWritingStyles();
        latestChapters = await refreshChapters();
        pendingChapters = getContiguousPendingChapters(latestChapters);
        if (pendingChapters.length < segmentTarget && currentProject.outline_mode === 'one-to-many') {
          const outlinesToExpand = outlineResult.outlines?.length
            ? outlineResult.outlines
            : [];
          if (!outlinesToExpand.length) {
            throw new Error('未找到可展开的续写大纲');
          }
          await outlineApi.batchExpandOutlinesStream(
            {
              project_id: currentProject.id,
              outline_ids: outlinesToExpand.map((item) => item.id),
              chapters_per_outline: chaptersPerOutline,
              expansion_strategy: 'balanced',
              auto_create_chapters: true,
              model: plan.model,
            },
            {
              onProgress: (progressMessage, progress) => {
                const normalizedProgress = progress == null ? 60 : Math.min(90, Math.max(60, progress));
                setContinuationProgress(normalizedProgress);
                setContinuationMessage(progressMessage || '正在将续写大纲展开为章节...');
              },
            },
          );
          await loadWritingStyles();
          latestChapters = await refreshChapters();
          pendingChapters = getContiguousPendingChapters(latestChapters);
        }
      }
      if (pendingChapters.length === 0) {
        throw new Error('未找到可续写的空白章节');
      }
      const firstPendingChapter = pendingChapters[0];
      if (!canGenerateChapter(firstPendingChapter)) {
        throw new Error(getGenerateDisabledReason(firstPendingChapter));
      }
      const requestCount = Math.min(segmentTarget, pendingChapters.length);
      const runningPlan: ContinuationPlanState = {
        ...plan,
        currentBatchId: null,
        currentBatchPlannedCount: requestCount,
        status: 'running',
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(runningPlan);
      continuationPlanStateRef.current = runningPlan;
      persistContinuationPlan(runningPlan);
      setContinuationProgress(95);
      setContinuationMessage(`本轮 ${requestCount} 章已准备就绪，正在启动...`);
      const result = await launchBatchGeneration({
        start_chapter_number: firstPendingChapter.chapter_number,
        count: requestCount,
        enable_analysis: true,
        enable_workflow: true,
        workflow_auto_regenerate: true,
        workflow_max_rounds: 2,
        workflow_min_score: 7.8,
        style_id: plan.styleId,
        target_word_count: plan.targetWordCount,
        model: plan.model,
        force_high_risk_continuation: plan.forceHighRiskContinuation || undefined,
      });
      const startedPlan: ContinuationPlanState = {
        ...runningPlan,
        currentBatchId: result.batch_id,
        forceHighRiskContinuation: false,
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(startedPlan);
      continuationPlanStateRef.current = startedPlan;
      persistContinuationPlan(startedPlan);
    } catch (error) {
      const err = error as Error;
      const failedPlan: ContinuationPlanState = {
        ...plan,
        currentBatchId: null,
        currentBatchPlannedCount: undefined,
        status: 'failed',
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(failedPlan);
      continuationPlanStateRef.current = failedPlan;
      persistContinuationPlan(failedPlan);
      message.error(`自动续写失败：${err.message || '未知错误'}`);
    } finally {
      setContinuationRunning(false);
      continuationPlanRunningRef.current = false;
    }
  }, [
    canGenerateChapter,
    currentProject,
    getContiguousPendingChapters,
    getGenerateDisabledReason,
    launchBatchGeneration,
    refreshChapters,
  ]);
  */
  const runContinuationPlanRound = useCallback(async (plan: ContinuationPlanState) => {
    if (!currentProject?.id || plan.projectId !== currentProject.id) {
      return;
    }
    if (continuationPlanRunningRef.current) {
      return;
    }
    continuationPlanRunningRef.current = true;
    const segmentTarget = Math.min(plan.segmentSize, plan.remainingChapters);
    const chaptersPerOutline = Math.max(plan.chaptersPerOutline || 1, 1);
    try {
      setContinuationRunning(true);
      setContinuationProgress(5);
      setContinuationMessage(`正在准备自动续写本轮 ${segmentTarget} 章...`);
      let latestChapters = await refreshChapters();
      let pendingChapters = getContiguousPendingChapters(latestChapters);
      const missingChapterCount = Math.max(0, segmentTarget - pendingChapters.length);
      if (missingChapterCount > 0) {
        const outlineCount = currentProject.outline_mode === 'one-to-many'
          ? Math.max(1, Math.ceil(missingChapterCount / chaptersPerOutline))
          : missingChapterCount;
        const outlineResult = await outlineApi.generateOutlineStream(
          {
            project_id: currentProject.id,
            genre: currentProject.genre,
            theme: currentProject.theme || currentProject.description || '延续当前故事主线',
            chapter_count: outlineCount,
            narrative_perspective: currentProject.narrative_perspective || '第三人称',
            target_words: currentProject.target_words,
            mode: 'continue',
            story_direction: plan.storyDirection?.trim() || undefined,
            plot_stage: plan.plotStage,
            model: plan.model,
          },
          {
            onProgress: (progressMessage, progress) => {
              setContinuationProgress(Math.max(10, Math.min(55, progress ?? 10)));
              setContinuationMessage(progressMessage || '正在补充续写大纲...');
            },
          },
        );
        await loadWritingStyles();
        latestChapters = await refreshChapters();
        pendingChapters = getContiguousPendingChapters(latestChapters);
        if (pendingChapters.length < segmentTarget && currentProject.outline_mode === 'one-to-many') {
          const outlinesToExpand = outlineResult.outlines?.length
            ? outlineResult.outlines
            : [];
          if (!outlinesToExpand.length) {
            throw new Error('未找到可展开的续写大纲');
          }
          await outlineApi.batchExpandOutlinesStream(
            {
              project_id: currentProject.id,
              outline_ids: outlinesToExpand.map((item) => item.id),
              chapters_per_outline: chaptersPerOutline,
              expansion_strategy: 'balanced',
              auto_create_chapters: true,
              model: plan.model,
            },
            {
              onProgress: (progressMessage, progress) => {
                const normalizedProgress = progress == null ? 60 : Math.min(90, Math.max(60, progress));
                setContinuationProgress(normalizedProgress);
                setContinuationMessage(progressMessage || '正在将续写大纲展开为章节...');
              },
            },
          );
          await loadWritingStyles();
          latestChapters = await refreshChapters();
          pendingChapters = getContiguousPendingChapters(latestChapters);
        }
      }
      if (pendingChapters.length === 0) {
        throw new Error('未找到可续写的空白章节');
      }
      const firstPendingChapter = pendingChapters[0];
      if (!canGenerateChapter(firstPendingChapter)) {
        throw new Error(getGenerateDisabledReason(firstPendingChapter));
      }
      const requestCount = Math.min(segmentTarget, pendingChapters.length);
      const runningPlan: ContinuationPlanState = {
        ...plan,
        currentBatchId: null,
        currentBatchPlannedCount: requestCount,
        status: 'running',
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(runningPlan);
      continuationPlanStateRef.current = runningPlan;
      persistContinuationPlan(runningPlan);
      setContinuationProgress(95);
      setContinuationMessage(`本轮 ${requestCount} 章已准备就绪，正在启动...`);
      const result = await launchBatchGeneration({
        start_chapter_number: firstPendingChapter.chapter_number,
        count: requestCount,
        enable_analysis: true,
        enable_workflow: true,
        workflow_auto_regenerate: true,
        workflow_max_rounds: 2,
        workflow_min_score: 7.8,
        style_id: plan.styleId,
        target_word_count: plan.targetWordCount,
        model: plan.model,
        force_high_risk_continuation: plan.forceHighRiskContinuation || undefined,
      });
      const startedPlan: ContinuationPlanState = {
        ...runningPlan,
        currentBatchId: result.batch_id,
        forceHighRiskContinuation: false,
        updatedAt: new Date().toISOString(),
      };
      setContinuationPlanState(startedPlan);
      continuationPlanStateRef.current = startedPlan;
      persistContinuationPlan(startedPlan);
    } catch (error) {
      const riskDetail = getContinuationRiskHighDetail(error);
      if (riskDetail && !plan.forceHighRiskContinuation) {
        const confirmPlan: ContinuationPlanState = {
          ...plan,
          currentBatchId: null,
          currentBatchPlannedCount: undefined,
          status: 'failed',
          updatedAt: new Date().toISOString(),
        };
        setContinuationPlanState(confirmPlan);
        continuationPlanStateRef.current = confirmPlan;
        persistContinuationPlan(confirmPlan);
        modal.confirm({
          title: '续写前风险较高',
          content: buildContinuationRiskConfirmContent(riskDetail),
          okText: '强制继续',
          cancelText: '先补齐缺口',
          centered: true,
          onOk: () => {
            const forcedPlan: ContinuationPlanState = {
              ...confirmPlan,
              forceHighRiskContinuation: true,
              status: 'preparing',
              updatedAt: new Date().toISOString(),
            };
            setContinuationPlanState(forcedPlan);
            continuationPlanStateRef.current = forcedPlan;
            persistContinuationPlan(forcedPlan);
            void runContinuationPlanRound(forcedPlan);
          },
          onCancel: handleStartMissingAnalysisForContinuation,
        });
      } else {
        const failedPlan: ContinuationPlanState = {
          ...plan,
          currentBatchId: null,
          currentBatchPlannedCount: undefined,
          status: 'failed',
          updatedAt: new Date().toISOString(),
        };
        setContinuationPlanState(failedPlan);
        continuationPlanStateRef.current = failedPlan;
        persistContinuationPlan(failedPlan);
        message.error('自动续写失败：' + getApiErrorMessage(error));
      }
    } finally {
      setContinuationRunning(false);
      continuationPlanRunningRef.current = false;
    }
  }, [
    canGenerateChapter,
    currentProject,
    getContiguousPendingChapters,
    getGenerateDisabledReason,
    launchBatchGeneration,
    refreshChapters,
  ]);
  useEffect(() => {
    if (!currentProject?.id || !continuationPlanState) {
      return;
    }
    if (continuationPlanState.projectId !== currentProject.id) {
      return;
    }
    if (continuationPlanState.status !== 'preparing' || continuationPlanState.remainingChapters <= 0) {
      return;
    }
    if (batchGenerating) {
      return;
    }
    void runContinuationPlanRound(continuationPlanState);
  }, [batchGenerating, continuationPlanState, currentProject?.id, runContinuationPlanRound]);
  const handleOpenModal = (id: string) => {
    const chapter = chapters.find(c => c.id === id);
    if (chapter) {
      form.setFieldsValue(chapter);
      setEditingId(id);
      setIsModalOpen(true);
    }
  };
  const handleSubmit = async (values: ChapterUpdate) => {
    if (!editingId) return;
    try {
      await updateChapter(editingId, values);
      // å·æ°ç« èåè¡¨ä»¥è·åå®æ´çç« èæ°æ®ï¼å
// 括outline_title等联查字段）
      await refreshChapters();
      message.success('章节更新成功');
      setIsModalOpen(false);
      form.resetFields();
    } catch {
      message.error('操作失败');
    }
  };
  const handleOpenEditor = (id: string) => {
    const chapter = chapters.find(c => c.id === id);
    if (chapter) {
      setCurrentChapter(chapter);
      editorForm.setFieldsValue({
        title: chapter.title,
        content: chapter.content,
      });
      setEditingId(id);
      setTemporaryNarrativePerspective(undefined); // 重置人称选择
      setIsEditorOpen(true);
      // 打开编辑窗口时加载模型列表
      loadAvailableModels();
    }
  };
  const handleEditorSubmit = async (values: ChapterUpdate) => {
    if (!editingId || !currentProject) return;
    try {
      await updateChapter(editingId, values);
      // 刷新项目信息以更新总字数统计
      const updatedProject = await projectApi.getProject(currentProject.id);
      setCurrentProject(updatedProject);
      message.success('章节保存成功');
      setIsEditorOpen(false);
    } catch {
      message.error('保存失败');
    }
  };
  const handleGenerate = async (options?: { forceHighRiskContinuation?: boolean }) => {
    if (!editingId) return;
    try {
      setIsContinuing(true);
      setIsGenerating(true);
      setSingleChapterProgress(0);
      setSingleChapterProgressMessage('准备开始生成...');
      const result = await generateChapterContentStream(
        editingId,
        (content) => {
          editorForm.setFieldsValue({ content });
          if (contentTextAreaRef.current) {
            const textArea = contentTextAreaRef.current.resizableTextArea?.textArea;
            if (textArea) {
              textArea.scrollTop = textArea.scrollHeight;
            }
          }
        },
        selectedStyleId,
        targetWordCount,
        (progressMsg, progressValue) => {
          // 进度回调
          setSingleChapterProgress(progressValue);
          setSingleChapterProgressMessage(progressMsg);
        },
        selectedModel,  // 传递选中的模型
        temporaryNarrativePerspective,  // 传递临时人称参数
        options?.forceHighRiskContinuation
      );
      if (result?.guardrail_review_required) {
        const reasons = result.guardrail_review_reasons?.join('、') || '护栏最终未通过';
        message.warning(`AI创作已保存，但需人工复核：${reasons}`);
      } else {
        message.success('AI创作成功，正在分析章节内容...');
      }
      // 如果返回了分析任务ID，启动轮询
      if (result?.analysis_task_id) {
        const taskId = result.analysis_task_id;
        setAnalysisTasksMap(prev => ({
          ...prev,
          [editingId]: {
            has_task: true,
            task_id: taskId,
            chapter_id: editingId,
            status: 'pending',
            progress: 0
          }
        }));
        // 启动轮询
        startPollingTask(editingId);
      }
    } catch (error) {
      const riskDetail = getContinuationRiskHighDetail(error);
      if (riskDetail && !options?.forceHighRiskContinuation) {
        modal.confirm({
          title: '续写前风险较高',
          content: buildContinuationRiskConfirmContent(riskDetail),
          okText: '强制继续',
          cancelText: '先补齐缺口',
          centered: true,
          onOk: () => handleGenerate({ forceHighRiskContinuation: true }),
        });
      } else {
        message.error('AI创作失败：' + getApiErrorMessage(error));
      }
    } finally {
      setIsContinuing(false);
      setIsGenerating(false);
      setSingleChapterProgress(0);
      setSingleChapterProgressMessage('');
    }
  };
  const showGenerateModal = (chapter: Chapter) => {
    const previousChapters = chapters.filter(
      c => c.chapter_number < chapter.chapter_number
    ).sort((a, b) => a.chapter_number - b.chapter_number);
    const selectedStyle = writingStyles.find(s => s.id === selectedStyleId);
    const instance = modal.confirm({
      title: 'AI创作章节内容',
      width: 700,
      centered: true,
      content: (
        <div style={{ marginTop: 16 }}>
          <p>AIå°æ ¹æ®ä»¥ä¸ä¿¡æ¯åä½æ¬ç« å
容：</p>
          <ul>
            <li>章节大纲和要求</li>
            <li>项目的世界观设定</li>
            <li>ç¸å
³è§è²ä¿¡æ¯</li>
            <li><strong>åé¢å·²å®æç« èçå
å®¹ï¼ç¡®ä¿å§æ
连贯）</strong></li>
            {selectedStyle && (
              <li><strong>写作风格：{selectedStyle.name}</strong></li>
            )}
            <li><strong>目标字数：{targetWordCount}字</strong></li>
          </ul>
          {previousChapters.length > 0 && (
            <div style={{
              marginTop: 16,
              padding: 12,
              background: 'var(--color-info-bg)',
              borderRadius: 4,
              border: '1px solid var(--color-info-border)'
            }}>
              <div style={{ marginBottom: 8, fontWeight: 500, color: 'var(--color-primary)' }}>
                ð å°å¼ç¨çåç½®ç« èï¼å
±{previousChapters.length}ç« ï¼ï¼
              </div>
              <div style={{ maxHeight: 150, overflowY: 'auto' }}>
                {previousChapters.map(ch => (
                  <div key={ch.id} style={{ padding: '4px 0', fontSize: 13 }}>
                    ✓ 第{ch.chapter_number}章：{ch.title} ({ch.word_count || 0}字)
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                ð¡ AIä¼åèè¿äºç« èå
å®¹ï¼ç¡®ä¿æ
节连贯、角色状态一致
              </div>
            </div>
          )}
          <p style={{ color: '#ff4d4f', marginTop: 16, marginBottom: 0 }}>
            â ï¸ æ³¨æï¼æ­¤æä½å°è¦çå½åç« èå
容
          </p>
        </div>
      ),
      okText: '开始创作',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: async () => {
        instance.update({
          okButtonProps: { danger: true, loading: true },
          cancelButtonProps: { disabled: true },
          closable: false,
          maskClosable: false,
          keyboard: false,
        });
        try {
          if (!selectedStyleId) {
            message.error('请先选择写作风格');
            instance.update({
              okButtonProps: { danger: true, loading: false },
              cancelButtonProps: { disabled: false },
              closable: true,
              maskClosable: true,
              keyboard: true,
            });
            return;
          }
          await handleGenerate();
          instance.destroy();
        } catch {
          instance.update({
            okButtonProps: { danger: true, loading: false },
            cancelButtonProps: { disabled: false },
            closable: true,
            maskClosable: true,
            keyboard: true,
          });
        }
      },
      onCancel: () => {
        if (isGenerating) {
          message.warning('AI正在创作中，请等待完成');
          return false;
        }
      },
    });
  };
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'draft': 'default',
      'writing': 'processing',
      'completed': 'success',
      'review_required': 'error',
    };
    return colors[status] || 'default';
  };
  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      'draft': '草稿',
      'writing': '创作中',
      'completed': '已完成',
      'review_required': '需人工复核',
    };
    return texts[status] || status;
  };
  const handleExport = () => {
    if (chapters.length === 0) {
      message.warning('当前项目没有章节，无法导出');
      return;
    }
    modal.confirm({
      title: '导出项目章节',
      content: `确定要将《${currentProject.title}》的所有章节导出为TXT文件吗？`,
      centered: true,
      okText: '确定导出',
      cancelText: '取消',
      onOk: () => {
        try {
          projectApi.exportProject(currentProject.id);
          message.success('开始下载导出文件');
        } catch {
          message.error('导出失败，请重试');
        }
      },
    });
  };
  const handleShowAnalysis = (chapterId: string) => {
    setAnalysisChapterId(chapterId);
    setAnalysisVisible(true);
  };
  const formatGuardrailReasons = (reasons?: string[]) => (
    reasons && reasons.length > 0 ? reasons.join('、') : '暂无结构化失败信号'
  );
  const renderGuardrailViolations = (violations?: ChapterGuardrailViolation[]) => {
    if (!violations || violations.length === 0) {
      return <div style={{ color: 'rgba(0,0,0,0.45)' }}>暂无结构化违规明细</div>;
    }
    return (
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        {violations.map((violation, index) => (
          <Alert
            key={`${violation.type || 'violation'}-${index}`}
            type={violation.severity === 'high' ? 'error' : 'warning'}
            showIcon
            message={`${violation.type || 'unknown'}${violation.severity ? ` / ${violation.severity}` : ''}`}
            description={
              <div style={{ whiteSpace: 'pre-wrap' }}>
                {violation.description || '无描述'}
                {violation.context ? `\n上下文：${violation.context}` : ''}
              </div>
            }
          />
        ))}
      </Space>
    );
  };
  const renderGuardrailReviewContent = (reviewResponse: ChapterGuardrailReviewResponse) => {
    const review = reviewResponse.guardrail_review;
    return (
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Alert
          type="warning"
          showIcon
          message="该章节已保存，但护栏最终未通过。复核通过会恢复分析、伏笔写回和续写状态写回。"
        />
        <Descriptions size="small" column={1} bordered>
          <Descriptions.Item label="章节状态">{reviewResponse.chapter_status}</Descriptions.Item>
          <Descriptions.Item label="准入状态">{review?.acceptance_status || 'unknown'}</Descriptions.Item>
          <Descriptions.Item label="修复次数">{review?.attempts ?? 0}</Descriptions.Item>
          <Descriptions.Item label="失败信号">
            {formatGuardrailReasons(review?.manual_review_reasons)}
          </Descriptions.Item>
        </Descriptions>
        {reviewResponse.latest_history_prompt_note && (
          <Alert
            type="info"
            showIcon
            message="最近生成历史记录"
            description={<div style={{ whiteSpace: 'pre-wrap' }}>{reviewResponse.latest_history_prompt_note}</div>}
          />
        )}
        <Collapse size="small">
          <Collapse.Panel header="最终未通过明细" key="final">
            {renderGuardrailViolations(review?.final_violations)}
          </Collapse.Panel>
          <Collapse.Panel header="初始触发明细" key="initial">
            {renderGuardrailViolations(review?.initial_violations)}
          </Collapse.Panel>
        </Collapse>
      </Space>
    );
  };
  const handleOpenGuardrailReview = async (chapter: Chapter) => {
    try {
      const reviewResponse = await chapterApi.getGuardrailReview(chapter.id);
      const reasons = reviewResponse.guardrail_review?.manual_review_reasons || [];
      modal.confirm({
        title: `第${chapter.chapter_number}章人工复核`,
        icon: <CheckCircleOutlined />,
        content: renderGuardrailReviewContent(reviewResponse),
        okText: '复核通过并恢复链路',
        cancelText: '关闭',
        width: isMobile ? 'calc(100vw - 32px)' : 760,
        centered: true,
        onOk: async () => {
          const result = await chapterApi.approveGuardrailReview(chapter.id, {
            review_note: `前端人工复核通过；失败信号：${formatGuardrailReasons(reasons)}`,
          });
          if (result.analysis_task_id) {
            setAnalysisTasksMap(prev => ({
              ...prev,
              [chapter.id]: {
                has_task: true,
                task_id: result.analysis_task_id || null,
                chapter_id: chapter.id,
                status: 'pending',
                progress: 0,
              },
            }));
            startPollingTask(chapter.id);
          }
          await refreshChapters();
          message.success('人工复核已通过，已恢复后续分析与续写状态写回');
        },
      });
    } catch (error) {
      message.error(`加载复核信息失败：${getApiErrorMessage(error)}`);
    }
  };
  const renderGuardrailReviewAction = (item: Chapter, compact = false) => (
    item.status === 'review_required' ? (
      <Button
        type="text"
        danger
        icon={<CheckCircleOutlined />}
        onClick={() => handleOpenGuardrailReview(item)}
        size={compact ? 'small' : undefined}
        title="查看护栏失败原因，人工复核通过后恢复分析和续写状态写回"
      >
        {compact ? undefined : '复核'}
      </Button>
    ) : null
  );
  // 一键按章节顺序分析未分析章节
  const handleBatchAnalyzeUnanalyzed = async () => {
    if (!currentProject?.id) return;
    try {
      setBatchAnalyzingUnanalyzed(true);
      const result = await chapterApi.batchAnalyzeUnanalyzed(currentProject.id);
      if (result.total_started > 0) {
        setAnalysisTasksMap((prev) => ({
          ...prev,
          ...result.started_tasks,
        }));
        Object.keys(result.started_tasks).forEach((chapterId) => {
          startPollingTask(chapterId);
        });
        message.success(
          `å·²å å
¥ ${result.total_started} ç« é¡ºåºåæéåï¼è·³è¿å·²åæ ${result.total_already_completed} ç« ï¼åæä¸­/æéä¸­ ${result.total_skipped_running} ç« ï¼`
        );
      } else {
        message.info('æ²¡æå¯å¯å¨åæçç« èï¼å½åç« èè¦ä¹æ å容、要么已分析完成、要么正在分析中');
      }
      // 刷新一次状态，确保前端与后端一致
      await loadAnalysisTasks();
    } catch (error: unknown) {
      const err = error as Error;
      message.error(`一键分析失败：${err.message || '未知错误'}`);
    } finally {
      setBatchAnalyzingUnanalyzed(false);
    }
  };
  // 批量生成函数
  const handleBatchGenerate = async (values: {
    startChapterNumber: number;
    count: number;
    enableAnalysis: boolean;
    styleId?: number;
    targetWordCount?: number;
    model?: string;
  }) => {
    if (!currentProject?.id) return;
    const styleId = values.styleId || selectedStyleId;
    const wordCount = values.targetWordCount || targetWordCount;
    const model = batchSelectedModel;
    if (!styleId) {
      message.error('请选择写作风格');
      return;
    }
    const requestBody: BatchGeneratePayload = {
      start_chapter_number: values.startChapterNumber,
      count: values.count,
      enable_analysis: true,
      style_id: styleId,
      target_word_count: wordCount,
    };
    if (model) {
      requestBody.model = model;
    }
    const startBatch = async (payload: BatchGeneratePayload) => {
      const result = await launchBatchGeneration(payload);
      message.success(`批量生成任务已创建，预计需要 ${result.estimated_time_minutes} 分钟`);
      showBrowserNotification(
        '批量生成已启动',
        `开始生成 ${result.chapters_to_generate.length} 章，预计需要 ${result.estimated_time_minutes} 分钟`,
        'info'
      );
    };
    try {
      await startBatch(requestBody);
    } catch (error: unknown) {
      const riskDetail = getContinuationRiskHighDetail(error);
      if (riskDetail) {
        modal.confirm({
          title: '续写前风险较高',
          content: buildContinuationRiskConfirmContent(riskDetail),
          okText: '强制继续',
          cancelText: '先补齐缺口',
          centered: true,
          onOk: () => startBatch({
            ...requestBody,
            force_high_risk_continuation: true,
          }),
          onCancel: handleStartMissingAnalysisForContinuation,
        });
      } else {
        message.error('创建批量生成任务失败：' + getApiErrorMessage(error));
        setBatchGenerating(false);
        setBatchGenerateVisible(false);
      }
    }
  };
  const startBatchPolling = (taskId: string) => {
    if (batchPollingIntervalRef.current) {
      clearInterval(batchPollingIntervalRef.current);
    }
    resetBatchRefreshTracking();
    activeAnalysisPollingIdsRef.current.clear();
    clearAnalysisPollingIfIdle();
    const poll = async () => {
      if (batchPollingRequestInFlightRef.current) {
        return;
      }
      batchPollingRequestInFlightRef.current = true;
      try {
        const response = await fetch(`/api/chapters/batch-generate/${taskId}/status`);
        if (!response.ok) return;
        const status: BatchProgressState = await response.json();
        setBatchProgress({
          status: status.status,
          total: status.total,
          completed: status.completed,
          current_chapter_number: status.current_chapter_number,
          current_stage: status.current_stage,
          stage_message: status.stage_message,
          current_stage_progress: status.current_stage_progress,
          current_retry_count: status.current_retry_count,
          max_retries: status.max_retries,
          estimated_time_minutes: status.estimated_time_minutes,
          error_message: status.error_message,
        });
        if (status.status === 'running') {
          if (shouldRefreshBatchViews(status)) {
            await refreshBatchRelatedViews({
              includeProject: false,
              enableAnalysisPolling: false,
            });
          }
        }
        if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
          if (batchPollingIntervalRef.current) {
            clearInterval(batchPollingIntervalRef.current);
            batchPollingIntervalRef.current = null;
          }
          setBatchGenerating(false);
          await refreshBatchRelatedViews({
            includeProject: true,
            enableAnalysisPolling: false,
          });
          resetBatchRefreshTracking();
          const activePlan = continuationPlanStateRef.current;
          const isContinuationBatch = Boolean(
            activePlan
            && currentProject?.id
            && activePlan.projectId === currentProject.id
            && (!activePlan.currentBatchId || activePlan.currentBatchId === taskId)
          );
          if (status.status === 'completed') {
            if (isContinuationBatch && activePlan) {
              const finishedCount = activePlan.currentBatchPlannedCount || status.completed || 0;
              const remainingChapters = Math.max(0, activePlan.remainingChapters - finishedCount);
              if (remainingChapters > 0) {
                const nextPlan: ContinuationPlanState = {
                  ...activePlan,
                  remainingChapters,
                  currentBatchId: null,
                  currentBatchPlannedCount: undefined,
                  status: 'preparing',
                  updatedAt: new Date().toISOString(),
                };
                setContinuationPlanState(nextPlan);
                continuationPlanStateRef.current = nextPlan;
                persistContinuationPlan(nextPlan);
                const completedChapters = nextPlan.totalChapters - nextPlan.remainingChapters;
                message.success(
                  `自动续写已完成 ${completedChapters}/${nextPlan.totalChapters} 章，正在准备下一轮...`
                );
                showBrowserNotification(
                  '一键续写进行中',
                  `已完成 ${completedChapters}/${nextPlan.totalChapters} 章，正在继续`,
                  'success'
                );
                setBatchGenerateVisible(false);
                setBatchTaskId(null);
                setBatchProgress(null);
                void runContinuationPlanRound(nextPlan);
              } else {
                setContinuationPlanState(null);
                continuationPlanStateRef.current = null;
                clearContinuationPlan(activePlan.projectId);
                message.success(`一键续写完成，共完成 ${activePlan.totalChapters} 章`);
                showBrowserNotification(
                  '一键续写完成',
                  `《${currentProject?.title || '项目'}》自动续写 ${activePlan.totalChapters} 章已全部完成`,
                  'success'
                );
                setTimeout(() => {
                  setBatchGenerateVisible(false);
                  setBatchTaskId(null);
                  setBatchProgress(null);
                }, 2000);
              }
            } else {
              message.success(`批量生成完成，成功生成 ${status.completed} 章`);
              showBrowserNotification(
                '批量生成完成',
                `《${currentProject?.title || '项目'}》成功生成 ${status.completed} 章节`,
                'success'
              );
              setTimeout(() => {
                setBatchGenerateVisible(false);
                setBatchTaskId(null);
                setBatchProgress(null);
              }, 2000);
            }
          } else if (status.status === 'failed') {
            if (isContinuationBatch && activePlan) {
              const failedPlan: ContinuationPlanState = {
                ...activePlan,
                currentBatchId: null,
                currentBatchPlannedCount: undefined,
                status: 'failed',
                updatedAt: new Date().toISOString(),
              };
              setContinuationPlanState(failedPlan);
              continuationPlanStateRef.current = failedPlan;
              persistContinuationPlan(failedPlan);
            }
            message.error(`批量生成失败：${status.error_message || '未知错误'}`);
            showBrowserNotification(
              '批量生成失败',
              status.error_message || '未知错误',
              'error'
            );
            setTimeout(() => {
              setBatchGenerateVisible(false);
              setBatchTaskId(null);
              setBatchProgress(null);
            }, 2000);
          } else if (status.status === 'cancelled') {
            if (isContinuationBatch && activePlan) {
              const cancelledPlan: ContinuationPlanState = {
                ...activePlan,
                currentBatchId: null,
                currentBatchPlannedCount: undefined,
                status: 'cancelled',
                updatedAt: new Date().toISOString(),
              };
              setContinuationPlanState(cancelledPlan);
              continuationPlanStateRef.current = cancelledPlan;
              persistContinuationPlan(cancelledPlan);
            }
            message.warning('批量生成已取消');
            setTimeout(() => {
              setBatchGenerateVisible(false);
              setBatchTaskId(null);
              setBatchProgress(null);
            }, 2000);
          }
        }
      } catch (error) {
        console.error('轮询批量生成状态失败:', error);
      } finally {
        batchPollingRequestInFlightRef.current = false;
      }
    };
    void poll();
    batchPollingIntervalRef.current = window.setInterval(() => {
      void poll();
    }, BATCH_STATUS_POLL_INTERVAL_MS);
  };
  const handleCancelBatchGenerate = async () => {
    if (!batchTaskId) return;
    try {
      const response = await fetch(`/api/chapters/batch-generate/${batchTaskId}/cancel`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('取消失败');
      }
      message.success('批量生成已取消');
      if (batchPollingIntervalRef.current) {
        clearInterval(batchPollingIntervalRef.current);
        batchPollingIntervalRef.current = null;
      }
      await refreshBatchRelatedViews({
        includeProject: true,
        enableAnalysisPolling: false,
      });
      resetBatchRefreshTracking();
      if (continuationPlanStateRef.current?.projectId === currentProject?.id) {
        clearContinuationPlan(continuationPlanStateRef.current.projectId);
        continuationPlanStateRef.current = null;
        setContinuationPlanState(null);
      }
      setBatchGenerating(false);
      setBatchGenerateVisible(false);
      setBatchTaskId(null);
      setBatchProgress(null);
    } catch (error: unknown) {
      const err = error as Error;
      message.error(`取消失败：${err.message || '未知错误'}`);
    }
  };
  const handleOpenBatchGenerate = async () => {
    const firstIncompleteChapter = sortedChapters.find(
      ch => !ch.content || ch.content.trim() === ''
    );
    if (!firstIncompleteChapter) {
      message.info('所有章节都已生成内容');
      return;
    }
    if (!canGenerateChapter(firstIncompleteChapter)) {
      const reason = getGenerateDisabledReason(firstIncompleteChapter);
      message.warning(reason);
      return;
    }
    const defaultModel = await loadAvailableModels();
    setBatchSelectedModel(defaultModel || undefined);
    batchForm.setFieldsValue({
      startChapterNumber: firstIncompleteChapter.chapter_number,
      count: 5,
      enableAnalysis: false,
      styleId: selectedStyleId,
      targetWordCount: getCachedWordCount(),
    });
    setBatchGenerateVisible(true);
  };
  const handleOpenContinuation = async () => {
    if (!currentProject?.id) {
      return;
    }
    const defaultModel = await loadAvailableModels();
    setContinuationSelectedModel(defaultModel || undefined);
    continuationForm.setFieldsValue({
      chapterCount: 10,
      plotStage: 'development',
      chaptersPerOutline: 1,
      storyDirection: '',
      styleId: undefined,
      targetWordCount: getCachedWordCount(),
      model: defaultModel || undefined,
    });
    setContinuationVisible(true);
  };
  const startContinuationPlan = (plan: ContinuationPlanState, totalChapters: number) => {
    setContinuationPlanState(plan);
    continuationPlanStateRef.current = plan;
    persistContinuationPlan(plan);
    const roundCount = Math.ceil(totalChapters / DEFAULT_CONTINUATION_SEGMENT_SIZE);
    message.success(
      totalChapters > DEFAULT_CONTINUATION_SEGMENT_SIZE
        ? `一键续写已启动，共 ${totalChapters} 章，将分 ${roundCount} 轮自动续写`
        : `一键续写已启动，共 ${totalChapters} 章`
    );
    showBrowserNotification(
      '一键续写已启动',
      totalChapters > DEFAULT_CONTINUATION_SEGMENT_SIZE
        ? `将按每 ${DEFAULT_CONTINUATION_SEGMENT_SIZE} 章一轮，自动补大纲并续写正文`
        : `开始续写 ${totalChapters} 章`,
      'info'
    );
  };
  const handleStartMissingAnalysisForContinuation = async () => {
    if (!currentProject?.id) {
      return;
    }
    try {
      const result = await bookRemixApi.startMissingAnalysis(currentProject.id);
      const syncedCount = result.total_synced_existing || 0;
      const startedCount = result.total_started || 0;
      if (syncedCount > 0 || startedCount > 0) {
        message.success(`已同步 ${syncedCount} 个已有分析包，启动 ${startedCount} 个缺口分析任务`);
      } else {
        message.info('现有章节已全部完成拆解同步');
      }
    } catch (error) {
      message.error('补齐拆解失败：' + getApiErrorMessage(error));
    }
  };
  const handleOneClickContinuation = async (values: ContinuationFormValues) => {
    if (!currentProject?.id) {
      return;
    }
    if (batchGenerating || continuationPlanRunningRef.current) {
      message.warning('\u5f53\u524d\u5df2\u6709\u7eed\u5199\u6216\u6279\u91cf\u751f\u6210\u4efb\u52a1\u5728\u8fdb\u884c');
      return;
    }
    const totalChapters = Math.max(1, Math.min(MAX_CONTINUATION_CHAPTERS, values.chapterCount || 1));
    const nextPlan: ContinuationPlanState = {
      projectId: currentProject.id,
      totalChapters,
      remainingChapters: totalChapters,
      segmentSize: DEFAULT_CONTINUATION_SEGMENT_SIZE,
      chaptersPerOutline: Math.max(values.chaptersPerOutline || 1, 1),
      storyDirection: values.storyDirection?.trim() || undefined,
      plotStage: values.plotStage,
      styleId: values.styleId,
      targetWordCount: values.targetWordCount || targetWordCount,
      model: continuationSelectedModel || values.model,
      currentBatchId: null,
      currentBatchPlannedCount: undefined,
      status: 'preparing',
      updatedAt: new Date().toISOString(),
    };

    try {
      const coverage = await bookRemixApi.getAnalysisCoverage(currentProject.id);
      const risk = coverage.continuation_risk;
      if (shouldBlockContinuationByRisk(risk)) {
        modal.confirm({
          title: '\u7eed\u5199\u524d\u98ce\u9669\u8f83\u9ad8',
          content: buildContinuationRiskSummaryContent(risk),
          okText: '\u5f3a\u5236\u7ee7\u7eed\u672c\u8f6e',
          cancelText: '\u5148\u8865\u9f50\u7f3a\u53e3',
          centered: true,
          onOk: () => {
            setContinuationVisible(false);
            startContinuationPlan({
              ...nextPlan,
              forceHighRiskContinuation: true,
              updatedAt: new Date().toISOString(),
            }, totalChapters);
          },
          onCancel: handleStartMissingAnalysisForContinuation,
        });
        return;
      }
    } catch (error) {
      console.warn('\u7eed\u5199\u98ce\u9669\u9884\u68c0\u5931\u8d25\uff0c\u5c06\u4ea4\u7531\u540e\u7aef\u95e8\u7981\u5904\u7406:', error);
    }

    setContinuationVisible(false);
    startContinuationPlan(nextPlan, totalChapters);
  };
  const showManualCreateChapterModal = () => {
    // 计算下一个章节号
    const nextChapterNumber = chapters.length > 0
      ? Math.max(...chapters.map(c => c.chapter_number)) + 1
      : 1;
    modal.confirm({
      title: '手动创建章节',
      width: 600,
      centered: true,
      content: (
        <Form
          form={manualCreateForm}
          layout="vertical"
          initialValues={{
            chapter_number: nextChapterNumber,
            status: 'draft'
          }}
          style={{ marginTop: 16 }}
        >
          <Form.Item
            label="章节序号"
            name="chapter_number"
            rules={[{ required: true, message: 'è¯·è¾å¥ç« èåºå·' }]}
            tooltip="å»ºè®®æé¡ºåºåå»ºç« èï¼ç¡®ä¿å容连贯性"
          >
            <InputNumber min={1} style={{ width: '100%' }} placeholder="自动计算的下一个序号" />
          </Form.Item>
          <Form.Item
            label="章节标题"
            name="title"
            rules={[{ required: true, message: 'è¯·è¾å¥æ é¢' }]}
          >
            <Input placeholder="例如：第一章 初遇" />
          </Form.Item>
          <Form.Item
            label="å³èå¤§çº²"
            name="outline_id"
            rules={[{ required: true, message: 'è¯·éæ©å³èçå¤§çº²' }]}
            tooltip="one-to-manyæ¨¡å¼ä¸ï¼ç« èå¿é¡»å³èå°å¤§çº²"
          >
            <Select placeholder="请选择所属大纲">
              {/* 直接使用 store 中的 outlines 数据，而不是从现有章节中提取 */}
              {[...outlines]
                .sort((a, b) => a.order_index - b.order_index)
                .map(outline => (
                  <Select.Option key={outline.id} value={outline.id}>
                    第{outline.order_index}卷：{outline.title}
                  </Select.Option>
                ))}
            </Select>
          </Form.Item>
          <Form.Item
            label="章节摘要（可选）"
            name="summary"
            tooltip="ç®è¦æè¿°æ¬ç« çä¸»è¦åå®¹åæ节发展"
          >
            <TextArea
              rows={4}
              placeholder="ç®è¦æè¿°æ¬ç« å容..."
            />
          </Form.Item>
          <Form.Item
            label="状态"
            name="status"
          >
            <Select>
              <Select.Option value="draft">草稿</Select.Option>
              <Select.Option value="writing">创作中</Select.Option>
              <Select.Option value="completed">已完成</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      ),
      okText: '创建',
      cancelText: '取消',
      onOk: async () => {
        const values = await manualCreateForm.validateFields();
        // 检查章节序号是否已存在
        const conflictChapter = chapters.find(
          ch => ch.chapter_number === values.chapter_number
        );
        if (conflictChapter) {
          // 显示冲突提示Modal
          modal.confirm({
            title: '章节序号冲突',
            icon: <InfoCircleOutlined style={{ color: '#ff4d4f' }} />,
            width: 500,
            centered: true,
            content: (
              <div>
                <p style={{ marginBottom: 12 }}>
                  第 <strong>{values.chapter_number}</strong> 章已存在：
                </p>
                <div style={{
                  padding: 12,
                  background: '#fff7e6',
                  borderRadius: 4,
                  border: '1px solid #ffd591',
                  marginBottom: 12
                }}>
                  <div><strong>标题：</strong>{conflictChapter.title}</div>
                  <div><strong>状态：</strong>{getStatusText(conflictChapter.status)}</div>
                  <div><strong>字数：</strong>{conflictChapter.word_count || 0}字</div>
                  {conflictChapter.outline_title && (
                    <div><strong>所属大纲：</strong>{conflictChapter.outline_title}</div>
                  )}
                </div>
                <p style={{ color: '#ff4d4f', marginBottom: 8 }}>
                  ⚠️ 是否删除旧章节并创建新章节？
                </p>
                <p style={{ fontSize: 12, color: '#666', marginBottom: 0 }}>
                  删除后无法恢复，章节内容和分析结果都将被删除。
                </p>
              </div>
            ),
            okText: '删除并创建',
            okButtonProps: { danger: true },
            cancelText: '取消',
            onOk: async () => {
              try {
                // 删除旧章节
                await handleDeleteChapter(conflictChapter.id);
                // 等待一小段时间确保删除完成
                await new Promise(resolve => setTimeout(resolve, 300));
                // 创建新章节
                await chapterApi.createChapter({
                  project_id: currentProject.id,
                  ...values
                });
                message.success('已删除旧章节并创建新章节');
                await refreshChapters();
                // 刷新项目信息以更新字数统计
                const updatedProject = await projectApi.getProject(currentProject.id);
                setCurrentProject(updatedProject);
                manualCreateForm.resetFields();
              } catch (error: unknown) {
                const err = error as Error;
                message.error('操作失败：' + (err.message || '未知错误'));
                throw error;
              }
            }
          });
          // é»æ­¢å¤å±Modalå
// ³é­
          return Promise.reject();
        }
        // 没有冲突，直接创建
        try {
          await chapterApi.createChapter({
            project_id: currentProject.id,
            ...values
          });
          message.success('章节创建成功');
          await refreshChapters();
          // 刷新项目信息以更新字数统计
          const updatedProject = await projectApi.getProject(currentProject.id);
          setCurrentProject(updatedProject);
          manualCreateForm.resetFields();
        } catch (error: unknown) {
          const err = error as Error;
          message.error('创建失败：' + (err.message || '未知错误'));
          throw error;
        }
      }
    });
  };
  // 渲染分析状态标签
  const renderAnalysisStatus = (chapterId: string) => {
    const task = analysisTasksMap[chapterId];
    if (!task) {
      return null;
    }
    switch (task.status) {
      case 'pending': {
        const isResuming = task.error_message && task.error_message.includes('自动续跑');
        return (
          <Tag
            icon={<SyncOutlined spin />}
            color={isResuming ? 'warning' : 'processing'}
            title={task.error_message || undefined}
          >
            {isResuming ? '续跑分析中' : '等待分析'}
          </Tag>
        );
      }
      case 'running': {
        // 检查是否正在重试，后端会在 error_message 中包含“重试”信息。
        const isRetrying = task.error_message && task.error_message.includes('重试');
        return (
          <Tag
            icon={<SyncOutlined spin />}
            color={isRetrying ? "warning" : "processing"}
            title={task.error_message || undefined}
          >
            {isRetrying ? `重试中 ${task.progress}%` : `分析中 ${task.progress}%`}
          </Tag>
        );
      }
      case 'completed':
        return (
          <Tag icon={<CheckCircleOutlined />} color="success">
            已分析
          </Tag>
        );
      case 'failed':
        return (
          <Tag icon={<CloseCircleOutlined />} color="error" title={task.error_message || undefined}>
            分析失败
          </Tag>
        );
      default:
        return null;
    }
  };
  // æ¾ç¤ºå±å¼è§åè¯¦æ
  const showExpansionPlanModal = (chapter: Chapter) => {
    if (!chapter.expansion_plan) return;
    try {
      const planData: ExpansionPlanData = JSON.parse(chapter.expansion_plan);
      modal.info({
        title: (
          <Space style={{ flexWrap: 'wrap' }}>
            <InfoCircleOutlined style={{ color: 'var(--color-primary)' }} />
            <span style={{ wordBreak: 'break-word' }}>第{chapter.chapter_number}章展开规划</span>
          </Space>
        ),
        width: isMobile ? 'calc(100vw - 32px)' : 800,
        centered: true,
        style: isMobile ? {
          maxWidth: 'calc(100vw - 32px)',
          margin: '0 auto',
          padding: '0 16px'
        } : undefined,
        styles: {
          body: {
            maxHeight: isMobile ? 'calc(100vh - 200px)' : 'calc(80vh - 110px)',
            overflowY: 'auto'
          }
        },
        content: (
          <div style={{ marginTop: 16 }}>
            <Descriptions
              column={1}
              size="small"
              bordered
              labelStyle={{
                whiteSpace: 'normal',
                wordBreak: 'break-word',
                width: isMobile ? '80px' : '100px'
              }}
              contentStyle={{
                whiteSpace: 'normal',
                wordBreak: 'break-word',
                overflowWrap: 'break-word'
              }}
            >
              <Descriptions.Item label="章节标题">
                <strong style={{
                  wordBreak: 'break-word',
                  whiteSpace: 'normal',
                  overflowWrap: 'break-word'
                }}>
                  {chapter.title}
                </strong>
              </Descriptions.Item>
              <Descriptions.Item label="æ感基调">
                <Tag
                  color="blue"
                  style={{
                    whiteSpace: 'normal',
                    wordBreak: 'break-word',
                    height: 'auto',
                    lineHeight: '1.5',
                    padding: '4px 8px'
                  }}
                >
                  {planData.emotional_tone}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="冲突类型">
                <Tag
                  color="orange"
                  style={{
                    whiteSpace: 'normal',
                    wordBreak: 'break-word',
                    height: 'auto',
                    lineHeight: '1.5',
                    padding: '4px 8px'
                  }}
                >
                  {planData.conflict_type}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="预估字数">
                <Tag color="green">{planData.estimated_words}字</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="叙事目标">
                <span style={{
                  wordBreak: 'break-word',
                  whiteSpace: 'normal',
                  overflowWrap: 'break-word'
                }}>
                  {planData.narrative_goal}
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="å³é®äºä»¶">
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  {planData.key_events.map((event, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '4px 0',
                        wordBreak: 'break-word',
                        whiteSpace: 'normal',
                        overflowWrap: 'break-word'
                      }}
                    >
                      <Tag color="purple" style={{ flexShrink: 0 }}>{idx + 1}</Tag>{' '}
                      <span style={{
                        wordBreak: 'break-word',
                        whiteSpace: 'normal',
                        overflowWrap: 'break-word'
                      }}>
                        {event}
                      </span>
                    </div>
                  ))}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="涉及角色">
                <Space wrap style={{ maxWidth: '100%' }}>
                  {planData.character_focus.map((char, idx) => (
                    <Tag
                      key={idx}
                      color="cyan"
                      style={{
                        whiteSpace: 'normal',
                        wordBreak: 'break-word',
                        height: 'auto',
                        lineHeight: '1.5'
                      }}
                    >
                      {char}
                    </Tag>
                  ))}
                </Space>
              </Descriptions.Item>
              {planData.scenes && planData.scenes.length > 0 && (
                <Descriptions.Item label="场景规划">
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    {planData.scenes.map((scene, idx) => (
                      <Card
                        key={idx}
                        size="small"
                        style={{
                          backgroundColor: '#fafafa',
                          maxWidth: '100%',
                          overflow: 'hidden'
                        }}
                      >
                        <div style={{
                          marginBottom: 4,
                          wordBreak: 'break-word',
                          whiteSpace: 'normal',
                          overflowWrap: 'break-word'
                        }}>
                          <strong>📍 地点：</strong>
                          <span style={{
                            wordBreak: 'break-word',
                            whiteSpace: 'normal',
                            overflowWrap: 'break-word'
                          }}>
                            {scene.location}
                          </span>
                        </div>
                        <div style={{ marginBottom: 4 }}>
                          <strong>👥 角色：</strong>
                          <Space
                            size="small"
                            wrap
                            style={{
                              marginLeft: isMobile ? 0 : 8,
                              marginTop: isMobile ? 4 : 0,
                              display: isMobile ? 'flex' : 'inline-flex'
                            }}
                          >
                            {scene.characters.map((char, charIdx) => (
                              <Tag
                                key={charIdx}
                                style={{
                                  whiteSpace: 'normal',
                                  wordBreak: 'break-word',
                                  height: 'auto'
                                }}
                              >
                                {char}
                              </Tag>
                            ))}
                          </Space>
                        </div>
                        <div style={{
                          wordBreak: 'break-word',
                          whiteSpace: 'normal',
                          overflowWrap: 'break-word'
                        }}>
                          <strong>🎯 目的：</strong>
                          <span style={{
                            wordBreak: 'break-word',
                            whiteSpace: 'normal',
                            overflowWrap: 'break-word'
                          }}>
                            {scene.purpose}
                          </span>
                        </div>
                      </Card>
                    ))}
                  </Space>
                </Descriptions.Item>
              )}
            </Descriptions>
            <Alert
              message="提示"
              description="è¿äºæ¯AIå¨å¤§çº²å±å¼æ¶çæçè§åä¿¡æ¯ï¼å¯ä»¥ä½ä¸ºåä½ç« èå容时的参考。"
              type="info"
              showIcon
              style={{ marginTop: 16 }}
            />
          </div>
        ),
        okText: 'å³é­',
      });
    } catch (error) {
      console.error('解析展开规划失败:', error);
      message.error('展开规划数据格式错误');
    }
  };
  // 删除章节处理函数
  const handleDeleteChapter = async (chapterId: string) => {
    try {
      await deleteChapter(chapterId);
      // 刷新章节列表
      await refreshChapters();
      // 刷新项目信息以更新总字数统计
      if (currentProject) {
        const updatedProject = await projectApi.getProject(currentProject.id);
        setCurrentProject(updatedProject);
      }
      message.success('章节删除成功');
    } catch (error: unknown) {
      const err = error as Error;
      message.error('删除章节失败：' + (err.message || '未知错误'));
    }
  };
  // 打开规划编辑器
  const handleOpenPlanEditor = (chapter: Chapter) => {
    // 直接打开编辑器,如果没有规划数据则创建新的
    setEditingPlanChapter(chapter);
    setPlanEditorVisible(true);
  };
  // 保存规划信息
  const handleSavePlan = async (planData: ExpansionPlanData) => {
    if (!editingPlanChapter) return;
    try {
      const response = await fetch(`/api/chapters/${editingPlanChapter.id}/expansion-plan`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(planData),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '更新失败');
      }
      // 刷新章节列表
      await refreshChapters();
      message.success('规划信息更新成功');
      // å
// ³é­ç¼è¾å¨
      setPlanEditorVisible(false);
      setEditingPlanChapter(null);
    } catch (error: unknown) {
      const err = error as Error;
      message.error('保存规划失败：' + (err.message || '未知错误'));
      throw error;
    }
  };
  // æå¼é
// 读器
  const handleOpenReader = (chapter: Chapter) => {
    setReadingChapter(chapter);
    setReaderVisible(true);
  };
  // é
// 读器切换章节
  const handleReaderChapterChange = async (chapterId: string) => {
    try {
      const response = await fetch(`/api/chapters/${chapterId}`);
      if (!response.ok) throw new Error('获取章节失败');
      const newChapter = await response.json();
      setReadingChapter(newChapter);
    } catch {
      message.error('加载章节失败');
    }
  };
  // 打开局部重写弹窗
  const handleOpenPartialRegenerate = () => {
    setPartialRegenerateToolbarVisible(false);
    setPartialRegenerateModalVisible(true);
  };
  // 应用局部重写结果
  const handleApplyPartialRegenerate = (newText: string, startPos: number, endPos: number) => {
    // è·åå½åå
// 容
    const currentContent = editorForm.getFieldValue('content') || '';
    // 替换选中部分
    const newContent = currentContent.substring(0, startPos) + newText + currentContent.substring(endPos);
    // 更新表单
    editorForm.setFieldsValue({ content: newContent });
    // å
// ³é­å¼¹çª
    setPartialRegenerateModalVisible(false);
    message.success('局部重写已应用');
  };
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {contextHolder}
      <div style={{
        position: 'sticky',
        top: 0,
        zIndex: 10,
        backgroundColor: 'var(--color-bg-container)',
        padding: isMobile ? '12px 0' : '16px 0',
        marginBottom: isMobile ? 12 : 16,
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        gap: isMobile ? 12 : 0,
        justifyContent: 'space-between',
        alignItems: isMobile ? 'stretch' : 'center'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <h2 style={{ margin: 0, fontSize: isMobile ? 18 : 24 }}>
            <BookOutlined style={{ marginRight: 8 }} />
            章节管理
          </h2>
          <Tag
            color={currentProject.outline_mode === 'one-to-one' ? 'blue' : 'green'}
            style={{ width: 'fit-content' }}
          >
            {currentProject.outline_mode === 'one-to-one'
              ? '传统模式：章节由大纲管理，请在大纲页面操作'
              : '细化模式：章节可在大纲页面展开'}
          </Tag>
        </div>
        <Space direction={isMobile ? 'vertical' : 'horizontal'} style={{ width: isMobile ? '100%' : 'auto' }}>
          <Input.Search
            allowClear
            placeholder="搜索章节（序号/标题/大纲）"
            value={chapterSearchKeyword}
            onChange={(e) => setChapterSearchKeyword(e.target.value)}
            style={{ width: isMobile ? '100%' : 280 }}
          />
          {currentProject.outline_mode === 'one-to-many' && (
            <Button
              icon={<PlusOutlined />}
              onClick={showManualCreateChapterModal}
              block={isMobile}
              size={isMobile ? 'middle' : 'middle'}
            >
              手动创建
            </Button>
          )}
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={handleBatchAnalyzeUnanalyzed}
            loading={batchAnalyzingUnanalyzed}
            disabled={chapters.length === 0 || batchAnalyzableChapterCount === 0}
            block={isMobile}
            size={isMobile ? 'middle' : 'middle'}
            style={{ background: '#fa8c16', borderColor: '#fa8c16' }}
            title={batchAnalyzableChapterCount === 0 ? '暂无可一键分析章节' : `可一键分析 ${batchAnalyzableChapterCount} 章`}
          >
            一键分析{batchAnalyzableChapterCount > 0 ? ` (${batchAnalyzableChapterCount})` : ''}
          </Button>
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={handleOpenContinuation}
            disabled={chapters.length === 0}
            block={isMobile}
            size={isMobile ? 'middle' : 'middle'}
            style={{ background: '#13c2c2', borderColor: '#13c2c2' }}
          >
            {'一键续写'}
          </Button>
            <Button
            type="primary"
            icon={<RocketOutlined />}
            onClick={handleOpenBatchGenerate}
            disabled={chapters.length === 0}
            block={isMobile}
            size={isMobile ? 'middle' : 'middle'}
            style={{ background: '#722ed1', borderColor: '#722ed1' }}
          >
            批量生成
          </Button>
          <Button
            type="default"
            icon={<DownloadOutlined />}
            onClick={handleExport}
            disabled={chapters.length === 0}
            block={isMobile}
            size={isMobile ? 'middle' : 'middle'}
          >
            导出为TXT
          </Button>
        </Space>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
        {chapters.length === 0 ? (
          <Empty description="还没有章节，开始创作吧！" />
        ) : filteredSortedChapters.length === 0 ? (
          <Empty description="没有找到匹配章节" />
        ) : currentProject.outline_mode === 'one-to-one' ? (
          // one-to-one 模式：直接显示扁平列表
          <List
            dataSource={pagedSortedChapters}
            renderItem={(item) => (
              <List.Item
                id={`chapter-item-${item.id}`}
                style={{
                  padding: '16px',
                  marginBottom: 16,
                  background: '#fff',
                  borderRadius: 8,
                  border: '1px solid #f0f0f0',
                  flexDirection: isMobile ? 'column' : 'row',
                  alignItems: isMobile ? 'flex-start' : 'center',
                }}
                actions={isMobile ? undefined : [
                  <Button
                    type="text"
                    icon={<ReadOutlined />}
                    onClick={() => handleOpenReader(item)}
                    disabled={!item.content || item.content.trim() === ''}
                    title={!item.content || item.content.trim() === '' ? '无内容' : '沉浸式阅读'}
                  >
                    阅读
                  </Button>,
                  <Button
                    type="text"
                    icon={<EditOutlined />}
                    onClick={() => handleOpenEditor(item.id)}
                  >
                    编辑
                  </Button>,
                  renderGuardrailReviewAction(item),
                  (() => {
                    const task = analysisTasksMap[item.id];
                    const isAnalyzing = task && (task.status === 'pending' || task.status === 'running');
                    const hasContent = item.content && item.content.trim() !== '';
                    return (
                      <Button
                        type="text"
                        icon={isAnalyzing ? <SyncOutlined spin /> : <FundOutlined />}
                        onClick={() => handleShowAnalysis(item.id)}
                        disabled={!hasContent || isAnalyzing}
                        loading={isAnalyzing}
                        title={
                          !hasContent ? '请先填写章节内容' :
                            isAnalyzing ? '分析进行中，请稍候...' :
                              ''
                        }
                      >
                        {isAnalyzing ? '分析中' : '分析'}
                      </Button>
                    );
                  })(),
                  <Button
                    type="text"
                    icon={<SettingOutlined />}
                    onClick={() => handleOpenModal(item.id)}
                  >
                    修改
                  </Button>,
                ]}
              >
                <div style={{ width: '100%' }}>
                  <List.Item.Meta
                    avatar={!isMobile && <FileTextOutlined style={{ fontSize: 32, color: 'var(--color-primary)' }} />}
                    title={
                      <div style={{
                        display: 'flex',
                        flexDirection: isMobile ? 'column' : 'row',
                        alignItems: isMobile ? 'flex-start' : 'center',
                        gap: isMobile ? 6 : 12,
                        width: '100%'
                      }}>
                        <span style={{ fontSize: isMobile ? 14 : 16, fontWeight: 500, flexShrink: 0 }}>
                          第{item.chapter_number}章：{item.title}
                        </span>
                        <Space wrap size={isMobile ? 4 : 8}>
                          <Tag color={getStatusColor(item.status)}>{getStatusText(item.status)}</Tag>
                          <Badge count={`${item.word_count || 0}字`} style={{ backgroundColor: 'var(--color-success)' }} />
                          {renderAnalysisStatus(item.id)}
                          {!canGenerateChapter(item) && (
                            <Tag icon={<LockOutlined />} color="warning" title={getGenerateDisabledReason(item)}>
                              需前置章节
                            </Tag>
                          )}
                        </Space>
                      </div>
                    }
                    description={
                      item.content ? (
                        <div style={{ marginTop: 8, color: 'rgba(0,0,0,0.65)', lineHeight: 1.6, fontSize: isMobile ? 12 : 14 }}>
                          {item.content.substring(0, isMobile ? 80 : 150)}
                          {item.content.length > (isMobile ? 80 : 150) && '...'}
                        </div>
                      ) : (
                        <span style={{ color: 'rgba(0,0,0,0.45)', fontSize: isMobile ? 12 : 14 }}>无内容</span>
                      )
                    }
                  />
                  {isMobile && (
                    <Space style={{ marginTop: 12, width: '100%', justifyContent: 'flex-end' }} wrap>
                      <Button
                        type="text"
                        icon={<ReadOutlined />}
                        onClick={() => handleOpenReader(item)}
                        size="small"
                        disabled={!item.content || item.content.trim() === ''}
                        title={!item.content || item.content.trim() === '' ? '无内容' : '阅读'}
                      />
                      <Button
                        type="text"
                        icon={<EditOutlined />}
                        onClick={() => handleOpenEditor(item.id)}
                        size="small"
                        title="编辑"
                      />
                      {renderGuardrailReviewAction(item, true)}
                      {(() => {
                        const task = analysisTasksMap[item.id];
                        const isAnalyzing = task && (task.status === 'pending' || task.status === 'running');
                        const hasContent = item.content && item.content.trim() !== '';
                        return (
                          <Button
                            type="text"
                            icon={isAnalyzing ? <SyncOutlined spin /> : <FundOutlined />}
                            onClick={() => handleShowAnalysis(item.id)}
                            size="small"
                            disabled={!hasContent || isAnalyzing}
                            loading={isAnalyzing}
                            title={
                              !hasContent ? '请先填写章节内容' :
                                isAnalyzing ? '分析中' :
                                  '分析'
                            }
                          />
                        );
                      })()}
                      <Button
                        type="text"
                        icon={<SettingOutlined />}
                        onClick={() => handleOpenModal(item.id)}
                        size="small"
                        title="修改"
                      />
                    </Space>
                  )}
                </div>
              </List.Item>
            )}
          />
        ) : (
          // one-to-many 模式：按大纲分组显示
          <Collapse
            bordered={false}
            defaultActiveKey={pagedGroupedChapters.length > 0 ? ['0'] : []}
            destroyInactivePanel
            expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} />}
            style={{ background: 'transparent' }}
          >
            {pagedGroupedChapters.map((group, groupIndex) => (
              <Collapse.Panel
                key={groupIndex.toString()}
                header={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <Tag color={group.outlineId ? 'blue' : 'default'} style={{ margin: 0 }}>
                      {group.outlineId ? `📖 大纲 ${group.outlineOrder}` : '📝 未分类'}
                    </Tag>
                    <span style={{ fontWeight: 600, fontSize: 16 }}>
                      {group.outlineTitle}
                    </span>
                    <Badge
                      count={`${group.chapters.length} 章`}
                      style={{ backgroundColor: 'var(--color-success)' }}
                    />
                    <Badge
                      count={`${group.chapters.reduce((sum, ch) => sum + (ch.word_count || 0), 0)} 字`}
                      style={{ backgroundColor: 'var(--color-primary)' }}
                    />
                  </div>
                }
                style={{
                  marginBottom: 16,
                  background: '#fff',
                  borderRadius: 8,
                  border: '1px solid #f0f0f0',
                }}
              >
                <List
                  dataSource={group.chapters}
                  renderItem={(item) => (
                    <List.Item
                      id={`chapter-item-${item.id}`}
                      style={{
                        padding: '16px 0',
                        borderRadius: 8,
                        transition: 'background 0.3s ease',
                        flexDirection: isMobile ? 'column' : 'row',
                        alignItems: isMobile ? 'flex-start' : 'center',
                      }}
                      actions={isMobile ? undefined : [
                        <Button
                          type="text"
                          icon={<ReadOutlined />}
                          onClick={() => handleOpenReader(item)}
                          disabled={!item.content || item.content.trim() === ''}
                          title={!item.content || item.content.trim() === '' ? '无内容' : '沉浸式阅读'}
                        >
                          阅读
                        </Button>,
                        <Button
                          type="text"
                          icon={<EditOutlined />}
                          onClick={() => handleOpenEditor(item.id)}
                        >
                          编辑
                        </Button>,
                        renderGuardrailReviewAction(item),
                        (() => {
                          const task = analysisTasksMap[item.id];
                          const isAnalyzing = task && (task.status === 'pending' || task.status === 'running');
                          const hasContent = item.content && item.content.trim() !== '';
                          return (
                            <Button
                              type="text"
                              icon={isAnalyzing ? <SyncOutlined spin /> : <FundOutlined />}
                              onClick={() => handleShowAnalysis(item.id)}
                              disabled={!hasContent || isAnalyzing}
                              loading={isAnalyzing}
                              title={
                                !hasContent ? '请先填写章节内容' :
                                  isAnalyzing ? '分析进行中，请稍候...' :
                                    ''
                              }
                            >
                              {isAnalyzing ? '分析中' : '分析'}
                            </Button>
                          );
                        })(),
                        <Button
                          type="text"
                          icon={<SettingOutlined />}
                          onClick={() => handleOpenModal(item.id)}
                        >
                          修改
                        </Button>,
                        // 只在 one-to-many 模式下显示删除按钮
                        ...(currentProject.outline_mode === 'one-to-many' ? [
                          <Popconfirm
                            title="确定删除这个章节吗？"
                            description="删除后无法恢复，章节内容和分析结果都将被删除。"
                            onConfirm={() => handleDeleteChapter(item.id)}
                            okText="确定删除"
                            cancelText="取消"
                            okButtonProps={{ danger: true }}
                          >
                            <Button
                              type="text"
                              danger
                              icon={<DeleteOutlined />}
                            >
                              删除
                            </Button>
                          </Popconfirm>
                        ] : []),
                      ]}
                    >
                      <div style={{ width: '100%' }}>
                        <List.Item.Meta
                          avatar={!isMobile && <FileTextOutlined style={{ fontSize: 32, color: 'var(--color-primary)' }} />}
                          title={
                            <div style={{
                              display: 'flex',
                              flexDirection: isMobile ? 'column' : 'row',
                              alignItems: isMobile ? 'flex-start' : 'center',
                              gap: isMobile ? 6 : 12,
                              width: '100%'
                            }}>
                              <span style={{ fontSize: isMobile ? 14 : 16, fontWeight: 500, flexShrink: 0 }}>
                                第{item.chapter_number}章：{item.title}
                              </span>
                              <Space wrap size={isMobile ? 4 : 8}>
                                <Tag color={getStatusColor(item.status)}>{getStatusText(item.status)}</Tag>
                                <Badge count={`${item.word_count || 0}字`} style={{ backgroundColor: 'var(--color-success)' }} />
                                {renderAnalysisStatus(item.id)}
                                {!canGenerateChapter(item) && (
                                  <Tag icon={<LockOutlined />} color="warning" title={getGenerateDisabledReason(item)}>
                                    需前置章节
                                  </Tag>
                                )}
                                <Space size={4}>
                                  {item.expansion_plan && (
                                    <InfoCircleOutlined
                                      title="查看展开详情"
                                      style={{ color: 'var(--color-primary)', cursor: 'pointer', fontSize: 16 }}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        showExpansionPlanModal(item);
                                      }}
                                    />
                                  )}
                                  <FormOutlined
                                    title={item.expansion_plan ? "编辑规划信息" : "创建规划信息"}
                                    style={{ color: 'var(--color-success)', cursor: 'pointer', fontSize: 16 }}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleOpenPlanEditor(item);
                                    }}
                                  />
                                </Space>
                              </Space>
                            </div>
                          }
                          description={
                            item.content ? (
                              <div style={{ marginTop: 8, color: 'rgba(0,0,0,0.65)', lineHeight: 1.6, fontSize: isMobile ? 12 : 14 }}>
                                {item.content.substring(0, isMobile ? 80 : 150)}
                                {item.content.length > (isMobile ? 80 : 150) && '...'}
                              </div>
                            ) : (
                              <span style={{ color: 'rgba(0,0,0,0.45)', fontSize: isMobile ? 12 : 14 }}>无内容</span>
                            )
                          }
                        />
                        {isMobile && (
                          <Space style={{ marginTop: 12, width: '100%', justifyContent: 'flex-end' }} wrap>
                            <Button
                              type="text"
                              icon={<ReadOutlined />}
                              onClick={() => handleOpenReader(item)}
                              size="small"
                              disabled={!item.content || item.content.trim() === ''}
                              title={!item.content || item.content.trim() === '' ? '无内容' : '阅读'}
                            />
                            <Button
                              type="text"
                              icon={<EditOutlined />}
                              onClick={() => handleOpenEditor(item.id)}
                              size="small"
                              title="编辑"
                            />
                            {renderGuardrailReviewAction(item, true)}
                            {(() => {
                              const task = analysisTasksMap[item.id];
                              const isAnalyzing = task && (task.status === 'pending' || task.status === 'running');
                              const hasContent = item.content && item.content.trim() !== '';
                              return (
                                <Button
                                  type="text"
                                  icon={isAnalyzing ? <SyncOutlined spin /> : <FundOutlined />}
                                  onClick={() => handleShowAnalysis(item.id)}
                                  size="small"
                                  disabled={!hasContent || isAnalyzing}
                                  loading={isAnalyzing}
                                  title={
                                    !hasContent ? '请先填写章节内容' :
                                      isAnalyzing ? '分析中' :
                                        '分析'
                                  }
                                />
                              );
                            })()}
                            <Button
                              type="text"
                              icon={<SettingOutlined />}
                              onClick={() => handleOpenModal(item.id)}
                              size="small"
                              title="修改"
                            />
                            {/* 只在 one-to-many 模式下显示删除按钮 */}
                            {currentProject.outline_mode === 'one-to-many' && (
                              <Popconfirm
                                title="确定删除？"
                                description="删除后无法恢复"
                                onConfirm={() => handleDeleteChapter(item.id)}
                                okText="删除"
                                cancelText="取消"
                                okButtonProps={{ danger: true }}
                              >
                                <Button
                                  type="text"
                                  danger
                                  icon={<DeleteOutlined />}
                                  size="small"
                                  title="删除章节"
                                />
                              </Popconfirm>
                            )}
                          </Space>
                        )}
                      </div>
                    </List.Item>
                  )}
                />
              </Collapse.Panel>
            ))}
          </Collapse>
        )}
      </div>
      {filteredSortedChapters.length > 0 && (
        <div style={{ paddingTop: 12, display: 'flex', justifyContent: 'flex-end' }}>
          <Pagination
            current={chapterPage}
            pageSize={chapterPageSize}
            total={filteredSortedChapters.length}
            showSizeChanger
            pageSizeOptions={['10', '20', '50', '100']}
            onChange={(page, size) => {
              setChapterPage(page);
              if (size !== chapterPageSize) {
                setChapterPageSize(size);
                setChapterPage(1);
              }
            }}
            showTotal={(total) => `å
± ${total} æ¡`}
            size={isMobile ? 'small' : 'default'}
          />
        </div>
      )}
      <Modal
        title={editingId ? '编辑章节信息' : '添加章节'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        centered
        width={isMobile ? 'calc(100vw - 32px)' : 520}
        style={isMobile ? {
          maxWidth: 'calc(100vw - 32px)',
          margin: '0 auto',
          padding: '0 16px'
        } : undefined}
        styles={{
          body: {
            maxHeight: isMobile ? 'calc(100vh - 200px)' : 'calc(80vh - 110px)',
            overflowY: 'auto'
          }
        }}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            label="章节标题"
            name="title"
            tooltip={
              currentProject.outline_mode === 'one-to-one'
                ? "章节标题由大纲管理，请在大纲页面修改"
                : "一对多模式下可以修改章节标题"
            }
            rules={
              currentProject.outline_mode === 'one-to-many'
                ? [{ required: true, message: '请输入章节标题' }]
                : undefined
            }
          >
            <Input
              placeholder="请输入章节标题"
              disabled={currentProject.outline_mode === 'one-to-one'}
            />
          </Form.Item>
          <Form.Item
            label="章节序号"
            name="chapter_number"
            tooltip="章节序号不允许修改，请删除对应大纲后重新生成"
          >
            <Input type="number" placeholder="章节排序序号" disabled />
          </Form.Item>
          <Form.Item label="状态" name="status">
            <Select placeholder="选择状态">
              <Select.Option value="draft">草稿</Select.Option>
              <Select.Option value="writing">创作中</Select.Option>
              <Select.Option value="review_required">需人工复核</Select.Option>
              <Select.Option value="completed">已完成</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space style={{ float: 'right' }}>
              <Button onClick={() => setIsModalOpen(false)}>取消</Button>
              <Button type="primary" htmlType="submit">
                更新
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
      <Modal
        title="编辑章节内容"
        open={isEditorOpen}
        onCancel={() => {
          if (isGenerating) {
            message.warning('AI 正在创作中，请等待完成后再关闭');
            return;
          }
          setIsEditorOpen(false);
        }}
        closable={!isGenerating}
        maskClosable={false}
        keyboard={!isGenerating}
        width={isMobile ? 'calc(100vw - 32px)' : '85%'}
        centered
        style={isMobile ? {
          maxWidth: 'calc(100vw - 32px)',
          margin: '0 auto',
          padding: '0 16px'
        } : undefined}
        styles={{
          body: {
            maxHeight: isMobile ? 'calc(100vh - 200px)' : 'calc(100vh - 110px)',
            overflowY: 'auto',
            padding: isMobile ? '16px 12px' : '8px'
          }
        }}
        footer={null}
      >
        <Form form={editorForm} layout="vertical" onFinish={handleEditorSubmit}>
          {/* 章节标题和AI创作按钮 */}
          <Form.Item
            label="章节标题"
            tooltip="（1-1模式请在大纲修改，1-N模式请使用修改按钮编辑）"
            style={{ marginBottom: isMobile ? 16 : 12 }}
          >
            <Space.Compact style={{ width: '100%' }}>
              <Form.Item name="title" noStyle>
                <Input disabled style={{ flex: 1 }} />
              </Form.Item>
              {editingId && (() => {
                const currentChapter = chapters.find(c => c.id === editingId);
                const canGenerate = currentChapter ? canGenerateChapter(currentChapter) : false;
                const disabledReason = currentChapter ? getGenerateDisabledReason(currentChapter) : '';
                return (
                  <Button
                    type="primary"
                    icon={canGenerate ? <ThunderboltOutlined /> : <LockOutlined />}
                    onClick={() => currentChapter && showGenerateModal(currentChapter)}
                    loading={isContinuing}
                    disabled={!canGenerate}
                    danger={!canGenerate}
                    style={{ fontWeight: 'bold' }}
                    title={!canGenerate ? disabledReason : '根据大纲和配置创作章节内容'}
                  >
                    {isMobile ? 'AI' : 'AI创作'}
                  </Button>
                );
              })()}
            </Space.Compact>
          </Form.Item>
          {/* 第一行：写作风格 + 叙事角度 */}
          <div style={{
            display: isMobile ? 'block' : 'flex',
            gap: isMobile ? 0 : 16,
            marginBottom: isMobile ? 0 : 12
          }}>
            <Form.Item
              label="写作风格"
              tooltip="选择AI创作时使用的写作风格"
              required
              style={{ flex: 1, marginBottom: isMobile ? 16 : 0 }}
            >
              <Select
                placeholder="请选择写作风格"
                value={selectedStyleId}
                onChange={setSelectedStyleId}
                disabled={isGenerating}
                status={!selectedStyleId ? 'error' : undefined}
              >
                {writingStyles.map(style => (
                  <Select.Option key={style.id} value={style.id}>
                    {style.name}{style.is_default && ' (默认)'}
                  </Select.Option>
                ))}
              </Select>
              {!selectedStyleId && (
                <div style={{ color: '#ff4d4f', fontSize: 12, marginTop: 4 }}>请选择写作风格</div>
              )}
            </Form.Item>
            <Form.Item
              label="叙事角度"
              tooltip="ç¬¬ä¸äººç§°(æ)ä»£å¥æå¼ºï¼ç¬¬ä¸äººç§°(ä»/å¥¹)æ´å®¢è§ï¼å¨ç¥è§è§æ´æä¸å"
              style={{ flex: 1, marginBottom: isMobile ? 16 : 0 }}
            >
              <Select
                placeholder={`项目默认: ${getNarrativePerspectiveText(currentProject?.narrative_perspective)}`}
                value={temporaryNarrativePerspective}
                onChange={setTemporaryNarrativePerspective}
                allowClear
                disabled={isGenerating}
              >
                <Select.Option value="第一人称">第一人称(我)</Select.Option>
                <Select.Option value="第三人称">第三人称(他/她)</Select.Option>
                <Select.Option value="å¨ç¥è§è§">å
¨ç¥è§è§</Select.Option>
              </Select>
              {temporaryNarrativePerspective && (
                <div style={{ color: 'var(--color-success)', fontSize: 12, marginTop: 4 }}>
                  ✓ {getNarrativePerspectiveText(temporaryNarrativePerspective)}
                </div>
              )}
            </Form.Item>
          </div>
          {/* 第二行：目标字数 + AI模型 */}
          <div style={{
            display: isMobile ? 'block' : 'flex',
            gap: isMobile ? 0 : 16,
            marginBottom: isMobile ? 16 : 12
          }}>
            <Form.Item
              label="目标字数"
              tooltip="AIçæç« èæ¶çç®æ å­æ°ï¼å®é可能略有偏差（修改后会自动记住）"
              style={{ flex: 1, marginBottom: isMobile ? 16 : 0 }}
            >
              <InputNumber
                min={500}
                max={10000}
                step={100}
                value={targetWordCount}
                onChange={(value) => {
                  const newValue = value || DEFAULT_WORD_COUNT;
                  setTargetWordCount(newValue);
                  setCachedWordCount(newValue);
                }}
                disabled={isGenerating}
                style={{ width: '100%' }}
                formatter={(value) => `${value} 字`}
                parser={(value) => parseInt(value?.replace(' 字', '') || '0', 10) as unknown as 500}
              />
            </Form.Item>
            <Form.Item
              label="AI模型"
              tooltip="éæ©ç¨äºçæç« èå容的AI模型，不选择则使用默认模型"
              style={{ flex: 1, marginBottom: isMobile ? 16 : 0 }}
            >
              <Select
                placeholder={selectedModel ? `默认: ${availableModels.find(m => m.value === selectedModel)?.label || selectedModel}` : "使用默认模型"}
                value={selectedModel}
                onChange={setSelectedModel}
                allowClear
                disabled={isGenerating}
                showSearch
                optionFilterProp="label"
              >
                {availableModels.map(model => (
                  <Select.Option key={model.value} value={model.value} label={model.label}>
                    {model.label}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          </div>
          <Form.Item label="ç« èå容" name="content">
            <TextArea
              ref={contentTextAreaRef}
              rows={isMobile ? 12 : 20}
              placeholder="开始写作..."
              style={{ fontFamily: 'monospace', fontSize: isMobile ? 12 : 14 }}
              disabled={isGenerating}
            />
          </Form.Item>
          {/* å±é¨éåæµ®å¨å·¥å
·æ  */}
          <div data-partial-regenerate-toolbar>
            <PartialRegenerateToolbar
              visible={partialRegenerateToolbarVisible && !isGenerating}
              position={partialRegenerateToolbarPosition}
              selectedText={selectedTextForRegenerate}
              onRegenerate={handleOpenPartialRegenerate}
            />
          </div>
          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end', flexDirection: isMobile ? 'column' : 'row', alignItems: isMobile ? 'stretch' : 'center' }}>
              <Space style={{ width: isMobile ? '100%' : 'auto' }}>
                <Button
                  onClick={() => {
                    if (isGenerating) {
                      message.warning('AIæ­£å¨åä½ä¸­ï¼è¯·ç­å¾å®æååå³é­');
                      return;
                    }
                    setIsEditorOpen(false);
                  }}
                  block={isMobile}
                  disabled={isGenerating}
                >
                  取消
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  block={isMobile}
                  disabled={isGenerating}
                >
                  保存章节
                </Button>
              </Space>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
      {analysisChapterId && (
        <ChapterAnalysis
          chapterId={analysisChapterId}
          visible={analysisVisible}
          onClose={() => {
            setAnalysisVisible(false);
            // å·æ°ç« èåè¡¨ä»¥æ¾ç¤ºææ°å
// 容
            refreshChapters();
            // 刷新项目信息以更新字数统计
            if (currentProject) {
              projectApi.getProject(currentProject.id)
                .then(updatedProject => {
                  setCurrentProject(updatedProject);
                })
                .catch(error => {
                  console.error('刷新项目信息失败:', error);
                });
            }
            // å»¶è¿500msåæ¹éå·æ°åæç¶æï¼é¿å
// åç« æ¥å£é«é¢è°ç¨
            setTimeout(() => {
              loadAnalysisTasks();
            }, 500);
            setAnalysisChapterId(null);
          }}
        />
      )}
      {/* 批量生成对话框 */}
      <Modal
        title={
          <Space>
            <RocketOutlined style={{ color: '#722ed1' }} />
            <span>æ¹éçæç« èå
容</span>
          </Space>
        }
        open={batchGenerateVisible}
        onCancel={() => {
          if (batchGenerating) {
            modal.confirm({
              title: '确认取消',
              content: '批量生成正在进行中，确定要取消吗？',
              okText: '确定取消',
              cancelText: '继续生成',
              centered: true,
              onOk: () => {
                handleCancelBatchGenerate();
                setBatchGenerateVisible(false);
              },
            });
          } else {
            setBatchGenerateVisible(false);
          }
        }}
        footer={!batchGenerating ? (
          <Space style={{ width: '100%', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
            <Button onClick={() => setBatchGenerateVisible(false)}>
              取消
            </Button>
            <Button type="primary" icon={<RocketOutlined />} onClick={() => batchForm.submit()}>
              开始批量生成
            </Button>
          </Space>
        ) : null}
        width={isMobile ? 'calc(100vw - 32px)' : 700}
        centered
        closable={!batchGenerating}
        maskClosable={!batchGenerating}
        style={isMobile ? {
          maxWidth: 'calc(100vw - 32px)',
          margin: '0 auto',
          padding: '0 16px'
        } : undefined}
        styles={{
          body: {
            maxHeight: isMobile ? 'calc(100vh - 200px)' : 'calc(100vh - 260px)',
            overflowY: 'auto',
            overflowX: 'hidden'
          }
        }}
      >
        {!batchGenerating ? (
          <Form
            form={batchForm}
            layout="vertical"
            onFinish={handleBatchGenerate}
            initialValues={{
              startChapterNumber: sortedChapters.find(ch => !ch.content || ch.content.trim() === '')?.chapter_number || 1,
              count: 5,
              enableAnalysis: true,
              styleId: selectedStyleId,
              targetWordCount: getCachedWordCount(),
              model: selectedModel,
            }}
          >
            <Alert
              message="批量生成说明：严格按序生成 | 统一风格字数 | 任一失败则终止"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            {/* 第一行：起始章节 + 生成数量 */}
            <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: isMobile ? 0 : 16 }}>
              <Form.Item
                label="起始章节"
                name="startChapterNumber"
                rules={[{ required: true, message: '请选择' }]}
                style={{ flex: 1, marginBottom: 12 }}
              >
                <Select placeholder="选择起始章节">
                  {sortedChapters
                    .filter(ch => !ch.content || ch.content.trim() === '')
                    .filter(ch => canGenerateChapter(ch))
                    .map(ch => (
                      <Select.Option key={ch.id} value={ch.chapter_number}>
                        第{ch.chapter_number}章：{ch.title}
                      </Select.Option>
                    ))}
                </Select>
              </Form.Item>
              <Form.Item
                label="生成数量"
                name="count"
                rules={[{ required: true, message: '请选择' }]}
                style={{ marginBottom: 12 }}
              >
                <Radio.Group buttonStyle="solid" size={isMobile ? 'small' : 'middle'}>
                  <Radio.Button value={5}>5章</Radio.Button>
                  <Radio.Button value={10}>10章</Radio.Button>
                  <Radio.Button value={15}>15章</Radio.Button>
                  <Radio.Button value={20}>20章</Radio.Button>
                </Radio.Group>
              </Form.Item>
            </div>
            {/* 第二行：写作风格 + 目标字数 */}
            <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: isMobile ? 0 : 16 }}>
              <Form.Item
                label="写作风格"
                name="styleId"
                rules={[{ required: true, message: '请选择' }]}
                style={{ flex: 1, marginBottom: 12 }}
              >
                <Select placeholder="请选择写作风格" showSearch optionFilterProp="children">
                  {writingStyles.map(style => (
                    <Select.Option key={style.id} value={style.id}>
                      {style.name}{style.is_default && ' (默认)'}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                label="目标字数"
                name="targetWordCount"
                rules={[{ required: true, message: '请设置' }]}
                tooltip="修改后自动记住"
                style={{ flex: 1, marginBottom: 12 }}
              >
                <InputNumber
                  min={500}
                  max={10000}
                  step={100}
                  style={{ width: '100%' }}
                  formatter={(value) => `${value} 字`}
                  parser={(value) => parseInt(value?.replace(' 字', '') || '0', 10) as unknown as 500}
                  onChange={(value) => {
                    if (value) {
                      setCachedWordCount(value);
                    }
                  }}
                />
              </Form.Item>
            </div>
            {/* 第三行：AI模型 + 同步分析 */}
            <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: isMobile ? 0 : 16 }}>
              <Form.Item
                label="AI模型"
                tooltip="不选则使用默认模型"
                style={{ flex: 1, marginBottom: 12 }}
              >
                <Select
                  placeholder={batchSelectedModel ? `默认: ${availableModels.find(m => m.value === batchSelectedModel)?.label || batchSelectedModel}` : "使用默认模型"}
                  value={batchSelectedModel}
                  onChange={setBatchSelectedModel}
                  allowClear
                  showSearch
                  optionFilterProp="label"
                >
                  {availableModels.map(model => (
                    <Select.Option key={model.value} value={model.value} label={model.label}>
                      {model.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                label="同步分析"
                name="enableAnalysis"
                tooltip="å¿é¡»å¼å¯ï¼ç¡®ä¿å§æ连贯"
                style={{ marginBottom: 12 }}
              >
                <Radio.Group disabled>
                  <Radio value={true}>
                    <span style={{ fontSize: 12, color: '#52c41a' }}>✓ 自动更新角色状态</span>
                  </Radio>
                </Radio.Group>
              </Form.Item>
            </div>
          </Form>
        ) : (
          <div>
            <Alert
              message="温馨提示"
              description={
                <ul style={{ margin: '8px 0 0 0', paddingLeft: 20 }}>
                  <li>æ¹éçæéè¦ä¸å®æ¶é´ï¼å¯ä»¥åæ¢å°å
¶ä»é¡µé¢</li>
                  <li>å
³é­é¡µé¢åéæ°æå¼ï¼ä¼èªå¨æ¢å¤ä»»å¡è¿åº¦</li>
                  <li>可以随时点击"取消任务"按钮中止生成</li>
                  {batchProgress?.estimated_time_minutes && batchProgress.completed === 0 && (
                    <li>⏱️ 预计耗时：约 {batchProgress.estimated_time_minutes} 分钟</li>
                  )}
                </ul>
              }
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <div style={{ textAlign: 'center' }}>
              <Button
                danger
                icon={<StopOutlined />}
                onClick={() => {
                  modal.confirm({
                    title: '确认取消',
                    content: '确定要取消批量生成吗？已生成的章节将保留。',
                    okText: '确定取消',
                    cancelText: '继续生成',
                    okButtonProps: { danger: true },
                    onOk: handleCancelBatchGenerate,
                  });
                }}
              >
                取消任务
              </Button>
            </div>
          </div>
        )}
      </Modal>
      {/* 单章节生成进度显示 */}
      <Modal
        title={'一键续写'}
        open={continuationVisible}
        onCancel={() => setContinuationVisible(false)}
        footer={null}
        width={isMobile ? 'calc(100vw - 32px)' : 640}
        centered
        destroyOnHidden
      >
        <Form
          form={continuationForm}
          layout="vertical"
          onFinish={handleOneClickContinuation}
          initialValues={{
            chapterCount: 10,
            plotStage: 'development',
            chaptersPerOutline: 1,
            storyDirection: '',
            styleId: undefined,
            targetWordCount: getCachedWordCount(),
            model: continuationSelectedModel,
          }}
        >
          <Alert
            message={'没有空章节时，会自动补大纲、展开章节并启动续写正文'}
            description={'超过 10 章时，会按每 10 章一轮自动滚动续写，每轮都会补大纲并继续生成正文'}
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: isMobile ? 0 : 16 }}>
            <Form.Item
              label={'续写总章数'}
              name="chapterCount"
              rules={[{ required: true, message: '请设置续写章数' }]}
              style={{ flex: 1, marginBottom: 12 }}
            >
              <InputNumber min={1} max={MAX_CONTINUATION_CHAPTERS} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item
              label={'剧情阶段'}
              name="plotStage"
              rules={[{ required: true, message: '请选择剧情阶段' }]}
              style={{ flex: 1, marginBottom: 12 }}
            >
              <Radio.Group buttonStyle="solid" size={isMobile ? 'small' : 'middle'}>
                <Radio.Button value="development">{'发展'}</Radio.Button>
                <Radio.Button value="climax">{'高潮'}</Radio.Button>
                <Radio.Button value="ending">{'结局'}</Radio.Button>
              </Radio.Group>
            </Form.Item>
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: -4, marginBottom: 12 }}>
            {[10, 20, 50, 100].map((count) => (
              <Button key={count} size="small" onClick={() => continuationForm.setFieldValue('chapterCount', count)}>
                {count} 章
              </Button>
            ))}
          </div>
          <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: isMobile ? 0 : 16 }}>
            <Form.Item
              label={'写作风格（可选）'}
              name="styleId"
              tooltip={'不选时会自动使用项目根据前文提炼的忠实续写风格'}
              style={{ flex: 1, marginBottom: 12 }}
            >
              <Select placeholder={'不选则自动使用项目续写风格'} allowClear showSearch optionFilterProp="children">
                {writingStyles.map(style => (
                  <Select.Option key={style.id} value={style.id}>
                    {style.name}{style.is_default && ' (默认)'}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              label={'目标字数'}
              name="targetWordCount"
              rules={[{ required: true, message: '请设置目标字数' }]}
              style={{ flex: 1, marginBottom: 12 }}
            >
              <InputNumber
                min={500}
                max={10000}
                step={100}
                style={{ width: '100%' }}
                onChange={(value) => {
                  if (value) {
                    setCachedWordCount(value);
                  }
                }}
              />
            </Form.Item>
          </div>
          <div style={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: isMobile ? 0 : 16 }}>
            <Form.Item
              label={'每个新大纲展开章数'}
              name="chaptersPerOutline"
              rules={[{ required: true, message: '请设置大纲展开章数' }]}
              tooltip={'仅在无空章节需要自动补大纲时生效'}
              style={{ flex: 1, marginBottom: 12 }}
            >
              <InputNumber min={1} max={5} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label={'AI 模型'} style={{ flex: 1, marginBottom: 12 }}>
              <Select
                placeholder={continuationSelectedModel ? `默认: ${availableModels.find(m => m.value === continuationSelectedModel)?.label || continuationSelectedModel}` : '使用默认模型'}
                value={continuationSelectedModel}
                onChange={setContinuationSelectedModel}
                allowClear
                showSearch
                optionFilterProp="label"
              >
                {availableModels.map(model => (
                  <Select.Option key={model.value} value={model.value} label={model.label}>
                    {model.label}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          </div>
          <Form.Item
            label={'续写方向'}
            name="storyDirection"
            tooltip={'可选，不填则按当前剧情自动推进'}
            style={{ marginBottom: 16 }}
          >
            <TextArea rows={4} placeholder={'例如：推进主角与反派的正面冲突，同时埋下新伏笔'} />
          </Form.Item>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, flexWrap: 'wrap' }}>
            <Button onClick={() => setContinuationVisible(false)}>{'取消'}</Button>
            <Button type="primary" icon={<ThunderboltOutlined />} onClick={() => continuationForm.submit()}>
              {'开始一键续写'}
            </Button>
          </div>
        </Form>
      </Modal>
      <SSEProgressModal
        visible={continuationRunning}
        progress={continuationProgress}
        message={continuationMessage || '正在准备续写任务...'}
        title={'一键续写进行中'}
      />
      <SSELoadingOverlay
        loading={isGenerating}
        progress={singleChapterProgress}
        message={singleChapterProgressMessage}
      />
      {/* 批量生成进度显示 - 使用统一的进度组件 */}
      <SSEProgressModal
        visible={batchGenerating}
        progress={getBatchProgressPercent(batchProgress)}
        message={buildBatchProgressMessage(batchProgress)}
        title={'批量生成章节'}
        onCancel={() => {
          modal.confirm({
            title: '确认取消',
            content: '确定要取消批量生成吗？已生成的章节将保留。',
            okText: '确定取消',
            cancelText: '继续生成',
            okButtonProps: { danger: true },
            centered: true,
            onOk: handleCancelBatchGenerate,
          });
        }}
        cancelButtonText={'取消任务'}
      />
      {/* ç« èé
读器 */}
      {readingChapter && (
        <ChapterReader
          visible={readerVisible}
          chapter={readingChapter}
          onClose={() => {
            setReaderVisible(false);
            setReadingChapter(null);
          }}
          onChapterChange={handleReaderChapterChange}
        />
      )}
      {/* 局部重写弹窗 */}
      {editingId && (
        <PartialRegenerateModal
          visible={partialRegenerateModalVisible}
          chapterId={editingId}
          selectedText={selectedTextForRegenerate}
          startPosition={selectionStartPosition}
          endPosition={selectionEndPosition}
          styleId={selectedStyleId}
          onClose={() => setPartialRegenerateModalVisible(false)}
          onApply={handleApplyPartialRegenerate}
        />
      )}
      {/* 规划编辑器 */}
      {editingPlanChapter && currentProject && (() => {
        let parsedPlanData = null;
        try {
          if (editingPlanChapter.expansion_plan) {
            parsedPlanData = JSON.parse(editingPlanChapter.expansion_plan);
          }
        } catch (error) {
          console.error('解析规划数据失败:', error);
        }
        return (
          <ExpansionPlanEditor
            visible={planEditorVisible}
            planData={parsedPlanData}
            chapterSummary={editingPlanChapter.summary || null}
            projectId={currentProject.id}
            onSave={handleSavePlan}
            onCancel={() => {
              setPlanEditorVisible(false);
              setEditingPlanChapter(null);
            }}
          />
        );
      })()}
    </div>
  );
}
