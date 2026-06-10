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
  'https://github.com/leenbj/novel-creator-skill',
  'https://github.com/KazKozDev/NovelGenerator',
  'https://github.com/raestrada/storycraftr',
  'https://github.com/YuanShiJiLoong/author',
  'https://github.com/brandburner/fabula',
  'https://github.com/RhythmicWave/NovelForge',
  'https://github.com/kaigani/codeywood',
  'https://github.com/KoboldAI/KoboldAI-Client',
  'https://github.com/SillyTavern/SillyTavern',
  'https://github.com/envy-ai/ai_rpg',
  'https://github.com/matrixorigin/Memoria',
  'https://github.com/mrigankad/Novel-OS',
  'https://github.com/aikohanasaki/SillyTavern-MemoryBooks',
  'https://github.com/bal-spec/sillytavern-character-memory',
  'https://github.com/XZZKANY/StoryForge',
  'https://github.com/spiritLHLS/novelbuilder',
  'https://github.com/qiuxinyuan321/novel-writer-master',
  'https://github.com/Byk3y/no-slop',
  'https://github.com/nntrivi2001/wordsmith',
  'https://github.com/zy-zmc/tianming-skill',
  'https://github.com/para-droid-ai/NovelizeAI',
  'https://github.com/Moosphan/novel-orchestrator',
  'https://github.com/kirinonakar/Novelgen',
  'https://github.com/abrahamp47/storyforge-wiki',
  'https://github.com/third-order-labs/longform-plugin',
  'https://github.com/hannasdev/mcp-writing',
  'https://github.com/xbraindance/Creative-writing-skill',
  'https://github.com/tiny-flowlab/novel-studio-copilot-cli',
  'https://github.com/guerra2fernando/libriscribe',
  'https://github.com/muckelverk/pulpgen',
  'https://github.com/bhed/sentiers-open-source',
  'https://github.com/rhavekost/author-toolkit',
  'https://github.com/mike-cramblett/novel-novel-generator',
  'https://github.com/denmurray10/Story-Timeline-Builder',
  'https://github.com/jwynia/agent-skills',
  'https://github.com/ydsgangge-ux/dramatica-flow',
  'https://github.com/mmunro3318/story-foundry',
  'https://github.com/Shine8592/novel-writer-skills',
  'https://github.com/modoojunko/awesome-novel-skill',
  'https://github.com/langchain-ai/story-writing',
  'https://github.com/EdwardAThomson/StoryDaemon',
  'https://github.com/datacrystals/AIStoryWriter',
  'https://github.com/sadasdfsaf/canonkit',
  'https://github.com/heider-x/vela',
  'https://github.com/pulpgen-dev/pulpgen',
  'https://github.com/jim60105/HeartReverie',
  'https://github.com/wzxsph/Novel-Claude',
  'https://github.com/liaoma1993/aiAIfiction',
  'https://github.com/vishnu0120754/ReNovel-AI',
  'https://github.com/worldwonderer/zenstory',
  'https://github.com/tuxiangxianzhe/NovelWriter_public',
  'https://github.com/MA-Bihani/Novelia_public',
  'https://github.com/huodebing-alt/Claude-Code-Novel-Agents',
];

const ADDITIONAL_HINT_GROUP_LIMIT = 24;
const WORKFLOW_PATTERN_EVIDENCE_LIMIT = 12;
const WORKFLOW_PATTERN_SOURCE_LIMIT = 3;
const PINNED_HINT_KEYS = new Set([
  'whole_book_analysis_targets',
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
  'character_interaction_network_gate_hints',
  'plotline_thread_tracking_hints',
  'rolling_summary_context_trim_hints',
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
]);

function parseSeedUrls(value: string): string[] {
  return value
    .split(/[\n,]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function BookRemixSourceDiscoveryPanel() {
  const [value, setValue] = useState<SourceDiscoveryLatestArtifactResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [repositorySeeds, setRepositorySeeds] = useState(DEFAULT_GITHUB_REPOSITORY_SEEDS.join('\n'));

  const loadLatest = async () => {
    setLoading(true);
    try {
      setValue(await sourceDiscoveryApi.getLatest());
    } finally {
      setLoading(false);
    }
  };

  const runDiscovery = async () => {
    setRunning(true);
    try {
      await sourceDiscoveryApi.runLedger({
        write_to_docs: true,
        github_repository_urls: parseSeedUrls(repositorySeeds),
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
        github_repository_urls: parseSeedUrls(repositorySeeds),
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
                onChange={(event) => setRepositorySeeds(event.target.value)}
                placeholder="https://github.com/voocel/ainovel-cli"
              />
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
              ['Character interaction network gates', patternPackPayload?.character_interaction_network_gate_hints],
              ['Plotline thread tracking gates', patternPackPayload?.plotline_thread_tracking_hints],
              ['Rolling summary context trim gates', patternPackPayload?.rolling_summary_context_trim_hints],
            ])}
            {renderHintGroup('Causal state-machine / skill workflow gates', [
              ['Causal Dramatica agent pipeline gates', patternPackPayload?.causal_dramatica_agent_pipeline_hints],
              ['Capture distillation production gates', patternPackPayload?.capture_distillation_production_gate_hints],
              ['Skill-orchestrated Chinese novel workflow gates', patternPackPayload?.skill_orchestrated_chinese_novel_workflow_hints],
              ['LangGraph story state machine gates', patternPackPayload?.langgraph_story_state_machine_hints],
              ['Story daemon evolution loop gates', patternPackPayload?.story_daemon_evolution_loop_hints],
            ])}
            {renderHintGroup('Local RAG / canon QA / patch replay gates', [
              ['Local RAG writing IDE gates', patternPackPayload?.local_rag_writing_ide_gate_hints],
              ['Canon drift continuity QA gates', patternPackPayload?.canon_drift_continuity_qa_gate_hints],
              ['Patch replay manuscript state gates', patternPackPayload?.patch_replay_manuscript_state_gate_hints],
              ['Microkernel skill plugin isolation gates', patternPackPayload?.microkernel_skill_plugin_isolation_gate_hints],
              ['Interactive reader-writer loop gates', patternPackPayload?.interactive_reader_writer_loop_gate_hints],
              ['Abstract style learning skill gates', patternPackPayload?.abstract_style_learning_skill_gate_hints],
            ])}
            {renderHintGroup('Impromptu / offline / atelier gates', [
              ['Impromptu thread-pool chapter gates', patternPackPayload?.impromptu_thread_pool_chapter_gate_hints],
              ['Offline inspiration-bank style gates', patternPackPayload?.offline_inspiration_bank_style_gate_hints],
              ['Atelier phase pipeline gates', patternPackPayload?.atelier_phase_pipeline_gate_hints],
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
