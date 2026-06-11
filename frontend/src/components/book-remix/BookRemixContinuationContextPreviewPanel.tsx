import { Alert, Button, Card, Empty, Space, Tag, Typography } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import type { BookRemixContinuationContextPreview } from '../../types/bookRemixBible';

const { Paragraph, Text } = Typography;

export interface BookRemixContinuationContextPreviewPanelProps {
  value: BookRemixContinuationContextPreview | null;
  loading?: boolean;
  onRefresh: () => Promise<void>;
}

const TEXT = {
  title: "Step 2.5 \u00b7 \u7eed\u5199\u4e0a\u4e0b\u6587\u9884\u89c8",
  refresh: "\u5237\u65b0",
  readyMessage: "\u4e0b\u4e00\u7ae0\u7eed\u5199\u4f1a\u6ce8\u5165\u8fd9\u6bb5\u4e0a\u4e0b\u6587",
  notReadyMessage: "\u7eed\u5199\u4e0a\u4e0b\u6587\u6682\u4e0d\u53ef\u7528",
  confirmedState: "\u786e\u8ba4\u72b6\u6001\uff1a",
  sourcePatternPack: "\u6765\u6e90\u6a21\u5f0f\u5305\uff1a",
  contextLength: "\u4e0a\u4e0b\u6587\u957f\u5ea6\uff1a",
  estimatedTokens: "\u4f30\u7b97 tokens\uff1a",
  budgetRisk: "\u9884\u7b97\u98ce\u9669\uff1a",
  activatedSections: "\u5df2\u6ce8\u5165\u7247\u6bb5\uff1a",
  activeSourcePatterns: "\u6e90\u6a21\u5f0f\uff1a",
  contextWarnings: "\u9884\u89c8\u63d0\u9192\uff1a",
  confirmed: "\u5df2\u786e\u8ba4",
  loaded: "\u5df2\u6ce8\u5165",
  notLoaded: "\u672a\u6ce8\u5165",
  notReady: "\u672a\u5c31\u7eea",
  emptyNeedsConfirm: "\u786e\u8ba4 Bible \u548c\u7eed\u5199\u8ba1\u5212\u540e\uff0c\u4f1a\u663e\u793a\u5b9e\u9645\u6ce8\u5165\u7ed9\u751f\u6210\u6a21\u578b\u7684\u4e0a\u4e0b\u6587",
  emptyNoPreview: "\u6682\u65e0\u7eed\u5199\u4e0a\u4e0b\u6587\u9884\u89c8",
  readyReason: "\u4e0a\u4e0b\u6587\u5df2\u5c31\u7eea",
};

const REASON_LABELS: Record<string, string> = {
  remix_bible_not_found: "\u5c1a\u672a\u751f\u6210 Bible",
  durable_remix_lineage_missing: "\u7f3a\u5c11\u62c6\u4e66\u6765\u6e90\u6807\u8bb0",
  continuation_plan_not_found: "\u5c1a\u672a\u751f\u6210\u7eed\u5199\u8ba1\u5212",
  remix_bible_not_confirmed: "Bible \u5c1a\u672a\u786e\u8ba4",
  continuation_plan_not_confirmed: "\u7eed\u5199\u8ba1\u5212\u5c1a\u672a\u786e\u8ba4",
  continuation_plan_not_bound_to_current_bible: "\u7eed\u5199\u8ba1\u5212\u672a\u7ed1\u5b9a\u5f53\u524d Bible",
  continuation_plan_stale_against_bible: "\u7eed\u5199\u8ba1\u5212\u5df2\u843d\u540e\u4e8e Bible",
  empty_context: "\u4e0a\u4e0b\u6587\u4e3a\u7a7a",
};

function formatReason(reason?: string | null): string {
  if (!reason) return TEXT.readyReason;
  return REASON_LABELS[reason] || reason;
}

function riskColor(risk?: string): string {
  if (risk === 'high') return 'red';
  if (risk === 'medium') return 'orange';
  return 'green';
}

export default function BookRemixContinuationContextPreviewPanel({
  value,
  loading = false,
  onRefresh,
}: BookRemixContinuationContextPreviewPanelProps) {
  const hasContext = Boolean(value?.has_context && value.context);

  return (
    <Card
      title={TEXT.title}
      extra={(
        <Button icon={<ReloadOutlined />} onClick={() => void onRefresh()} loading={loading}>
          {TEXT.refresh}
        </Button>
      )}
    >
      {value ? (
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Alert
            type={hasContext ? 'success' : 'warning'}
            showIcon
            message={hasContext ? TEXT.readyMessage : TEXT.notReadyMessage}
            description={formatReason(value.reason)}
          />

          <Space wrap>
            <Text type="secondary">{TEXT.confirmedState}</Text>
            <Tag color={value.lineage_confirmed ? 'green' : 'orange'}>
              {value.lineage_confirmed ? TEXT.confirmed : TEXT.notReady}
            </Tag>
            <Text type="secondary">{TEXT.sourcePatternPack}</Text>
            <Tag color={value.source_pattern_pack_loaded ? 'cyan' : 'default'}>
              {value.source_pattern_pack_loaded ? TEXT.loaded : TEXT.notLoaded}
            </Tag>
            <Text type="secondary">{TEXT.contextLength}</Text>
            <Tag color="blue">{value.context_length}</Tag>
            <Text type="secondary">{TEXT.estimatedTokens}</Text>
            <Tag color="purple">{value.context_estimated_tokens ?? 0}</Tag>
            <Text type="secondary">{TEXT.budgetRisk}</Text>
            <Tag color={riskColor(value.context_budget_risk)}>{value.context_budget_risk || 'low'}</Tag>
          </Space>

          {value.activated_sections?.length ? (
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <Text type="secondary">{TEXT.activatedSections}</Text>
              <Space wrap>
                {value.activated_sections.slice(0, 12).map(section => (
                  <Tag key={`${section.key}:${section.summary}`}>{section.key}: {section.summary}</Tag>
                ))}
              </Space>
            </Space>
          ) : null}

          {value.active_source_patterns?.length ? (
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <Text type="secondary">{TEXT.activeSourcePatterns}</Text>
              <Space wrap>
                {value.active_source_patterns.slice(0, 16).map(pattern => (
                  <Tag key={pattern} color="cyan">{pattern}</Tag>
                ))}
              </Space>
            </Space>
          ) : null}

          {value.context_warnings?.length ? (
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <Text type="secondary">{TEXT.contextWarnings}</Text>
              <Space wrap>
                {value.context_warnings.map(warning => (
                  <Tag key={warning} color="orange">{warning}</Tag>
                ))}
              </Space>
            </Space>
          ) : null}

          {hasContext ? (
            <Paragraph
              copyable={{ text: value.context }}
              style={{
                whiteSpace: 'pre-wrap',
                maxHeight: 360,
                overflow: 'auto',
                padding: 12,
                border: '1px solid var(--color-border)',
                borderRadius: 8,
                background: 'var(--color-fill-quaternary)',
                marginBottom: 0,
              }}
            >
              {value.context}
            </Paragraph>
          ) : (
            <Empty description={TEXT.emptyNeedsConfirm} />
          )}
        </Space>
      ) : (
        <Empty description={TEXT.emptyNoPreview} />
      )}
    </Card>
  );
}
