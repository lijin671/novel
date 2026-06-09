import { Alert, Button, Card, Empty, Input, List, Space, Tag, Typography, message } from 'antd';
import { ReloadOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { useEffect, useState } from 'react';
import { sourceDiscoveryApi } from '../../services/api';
import type {
  SourceDiscoveryLatestArtifactResponse,
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
];

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
