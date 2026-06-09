import { Alert, Button, Card, Col, Empty, List, Progress, Row, Space, Tag, Typography } from 'antd';
import { PlayCircleOutlined, ReloadOutlined, WarningOutlined } from '@ant-design/icons';
import type {
  BookRemixAnalysisCoverage,
  BookRemixAnalysisCoverageActionPlanItem,
  BookRemixAnalysisCoverageChapter,
  BookRemixStartMissingAnalysisResult,
} from '../../types/bookRemixBible';

const { Text } = Typography;

export interface BookRemixAnalysisCoveragePanelProps {
  value: BookRemixAnalysisCoverage | null;
  loading?: boolean;
  starting?: boolean;
  lastStartMissingResult?: BookRemixStartMissingAnalysisResult | null;
  onRefresh: () => Promise<void>;
  onStartMissingAnalysis?: () => Promise<void>;
  onOpenChapterAnalysis?: () => void;
  onOpenChapters?: () => void;
}

const TEXT = {
  title: 'Step 1.4 \u5168\u4e66\u62c6\u89e3\u89e3\u6790\u8986\u76d6\u7387\u4e0e\u7f3a\u53e3',
  refresh: '\u5237\u65b0',
  startMissing: '\u8865\u8dd1\u7f3a\u53e3\u5206\u6790',
  openChapterAnalysis: '\u6253\u5f00\u7ae0\u8282\u5206\u6790\u9875',
  openChapters: '\u53bb\u7ae0\u8282\u7eed\u5199\u9875',
  readyMessage: '\u5168\u4e66\u62c6\u89e3\u89e3\u6790\u5df2\u8986\u76d6\u6e90\u7ae0\u8282',
  gapMessage: '\u7eed\u5199\u4e0a\u4e0b\u6587\u8fd8\u6709\u7f3a\u53e3',
  readyDescription: '\u6e90\u7ae0\u8282\u5df2\u5b8c\u6210\u5206\u6790\uff0c\u7ae0\u8282\u53d8\u66f4\u5305\u5df2\u5199\u56de\u7eed\u5199\u72b6\u6001\u3002',
  gapDescription: '\u4e0b\u65b9\u5217\u51fa\u8fd8\u6ca1\u6709\u5206\u6790\u6216\u6ca1\u6709\u5199\u56de\u53d8\u66f4\u5305\u7684\u7ae0\u8282\u3002\u8fd9\u4e9b\u7f3a\u53e3\u4f1a\u8ba9\u540e\u7eed\u7eed\u5199\u4e0a\u4e0b\u6587\u53d8\u8584\u3002',
  sourceChapters: '\u6e90\u7ae0\u8282',
  analyzed: '\u5df2\u5206\u6790',
  synced: '\u5df2\u5199\u56de',
  analysisCoverage: '\u89e3\u6790\u8986\u76d6\u7387',
  syncCoverage: '\u5199\u56de\u8986\u76d6\u7387',
  missingAnalysis: '\u672a\u5206\u6790\u7ae0\u8282',
  missingPackages: '\u672a\u5199\u56de\u53d8\u66f4\u5305',
  missingSources: '\u7f3a\u5931\u6e90\u7ae0\u8282\u5e8f\u53f7',
  actionPlan: '\u7f3a\u53e3\u5904\u7406\u8ba1\u5212',
  continuationRisk: '\u7eed\u5199\u524d\u98ce\u9669',
  blockingChapters: '\u963b\u65ad\u7ae0\u8282',
  warningChapters: '\u504f\u8584\u7ae0\u8282',
  highRiskAction: '\u5f53\u524d\u5b58\u5728\u963b\u65ad\u7ae0\u8282\u3002\u5efa\u8bae\u5148\u8865\u8dd1\u7f3a\u53e3\u5206\u6790\uff0c\u6216\u6253\u5f00\u7ae0\u8282\u5206\u6790\u9875\u4eba\u5de5\u786e\u8ba4\uff1b\u786e\u8ba4\u540e\u518d\u56de\u5230\u7ae0\u8282\u9875\u7eed\u5199\u3002',
  riskReasons: '\u98ce\u9669\u539f\u56e0',
  emptyMissingAnalysis: '\u6ca1\u6709\u672a\u5206\u6790\u7ae0\u8282',
  emptyMissingPackages: '\u6ca1\u6709\u672a\u5199\u56de\u53d8\u66f4\u5305\u7684\u7ae0\u8282',
  emptyMissingSources: '\u6ca1\u6709\u7f3a\u5931\u6e90\u7ae0\u8282',
  emptyActionPlan: '\u6ca1\u6709\u5f85\u5904\u7406\u7f3a\u53e3',
  lastStartMissingResult: '\u6700\u8fd1\u8865\u8dd1\u7ed3\u679c',
  startedTasks: '\u521b\u5efa\u4efb\u52a1',
  syncedExisting: '\u5199\u56de\u5df2\u6709\u5206\u6790',
  skippedRunning: '\u8df3\u8fc7\u8fd0\u884c\u4e2d',
  skippedNoContent: '\u8df3\u8fc7\u7a7a\u6b63\u6587',
  targetChapters: '\u76ee\u6807\u7ae0\u8282',
  syncedChapters: '\u5199\u56de\u7ae0\u8282',
  noChapterTags: '\u65e0',
  empty: '\u6682\u65e0\u89e3\u6790\u8986\u76d6\u7387\u6570\u636e\uff1b\u9700\u8981\u5148\u751f\u6210 Bible',
};

const RISK_ALERT_TYPE = {
  low: 'success',
  medium: 'warning',
  high: 'error',
} as const;

const ACTION_COPY: Record<string, { label: string; color: string }> = {
  restore_source_chapter: { label: '\u6062\u590d\u6e90\u7ae0\u8282', color: 'red' },
  sync_existing_analysis: { label: '\u5199\u56de\u5df2\u6709\u5206\u6790', color: 'blue' },
  wait_running_analysis: { label: '\u7b49\u5f85\u8fd0\u884c\u4e2d\u5206\u6790', color: 'gold' },
  fill_chapter_content: { label: '\u8865\u9f50\u7ae0\u8282\u6b63\u6587', color: 'volcano' },
  queue_analysis: { label: '\u6392\u961f\u8865\u8dd1\u5206\u6790', color: 'purple' },
};

function renderChapterList(items: BookRemixAnalysisCoverageChapter[], emptyText: string) {
  if (!items.length) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={emptyText} />;
  }

  return (
    <List
      size="small"
      dataSource={items}
      renderItem={(item) => (
        <List.Item>
          <Space direction="vertical" size={2} style={{ width: '100%' }}>
            <Space wrap>
              <Tag color="orange">\u7b2c {item.chapter_number} \u7ae0</Tag>
              <Text strong>{item.chapter_title || '\u672a\u547d\u540d\u7ae0\u8282'}</Text>
            </Space>
            {item.status && <Text type="secondary">{item.status}</Text>}
          </Space>
        </List.Item>
      )}
    />
  );
}

function renderMissingSources(items: number[]) {
  if (!items.length) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={TEXT.emptyMissingSources} />;
  }

  return (
    <Space wrap>
      {items.map((item) => <Tag key={item} color="red">\u7b2c {item} \u7ae0</Tag>)}
    </Space>
  );
}

function renderChapterNumberTags(items: number[]) {
  return (
    <Space wrap>
      {items.map((item) => <Tag key={item} color="default">第 {item} 章</Tag>)}
    </Space>
  );
}

function renderActionPlan(items: BookRemixAnalysisCoverageActionPlanItem[]) {
  if (!items.length) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={TEXT.emptyActionPlan} />;
  }

  return (
    <List
      size="small"
      dataSource={items}
      renderItem={(item) => {
        const copy = ACTION_COPY[item.action] ?? { label: item.action, color: 'default' };
        return (
          <List.Item>
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <Space wrap>
                <Tag color={copy.color}>{copy.label}</Tag>
                <Text type="secondary">{item.chapter_count} 章</Text>
                <Text type="secondary">{item.reason}</Text>
              </Space>
              {renderChapterNumberTags(item.chapter_numbers)}
            </Space>
          </List.Item>
        );
      }}
    />
  );
}

function renderContinuationRisk(
  value: BookRemixAnalysisCoverage,
  options: {
    onStartMissingAnalysis?: () => Promise<void>;
    onOpenChapterAnalysis?: () => void;
    onOpenChapters?: () => void;
    starting?: boolean;
  } = {},
) {
  const risk = value.continuation_risk;
  if (!risk) return null;
  const isBlocking = risk.can_continue === false || risk.level === 'high';

  return (
    <Alert
      type={RISK_ALERT_TYPE[risk.level] || 'warning'}
      showIcon
      message={`${TEXT.continuationRisk}：${risk.label}`}
      description={(
        <Space direction="vertical" size={8} style={{ width: '100%' }}>
          <Text>{risk.message}</Text>
          {isBlocking && <Text type="secondary">{TEXT.highRiskAction}</Text>}
          <Space wrap>
            <Text type="secondary">{TEXT.blockingChapters}</Text>
            {renderResultChapterTags(risk.blocking_chapter_numbers)}
            <Text type="secondary">{TEXT.warningChapters}</Text>
            {renderResultChapterTags(risk.warning_chapter_numbers)}
          </Space>
          {risk.reason_labels?.length > 0 && (
            <Space wrap>
              <Text type="secondary">{TEXT.riskReasons}</Text>
              {risk.reason_labels.map((label) => <Tag key={label} color="volcano">{label}</Tag>)}
            </Space>
          )}
          {isBlocking && (
            <Space wrap>
              {options.onStartMissingAnalysis && (
                <Button
                  size="small"
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  loading={options.starting}
                  onClick={() => void options.onStartMissingAnalysis?.()}
                >
                  {TEXT.startMissing}
                </Button>
              )}
              {options.onOpenChapterAnalysis && (
                <Button size="small" icon={<WarningOutlined />} onClick={options.onOpenChapterAnalysis}>
                  {TEXT.openChapterAnalysis}
                </Button>
              )}
              {options.onOpenChapters && (
                <Button size="small" onClick={options.onOpenChapters}>
                  {TEXT.openChapters}
                </Button>
              )}
            </Space>
          )}
        </Space>
      )}
    />
  );
}


function renderResultChapterTags(items: number[]) {
  if (!items.length) {
    return <Tag color="default">{TEXT.noChapterTags}</Tag>;
  }

  return renderChapterNumberTags(items);
}

function renderStartMissingResult(result: BookRemixStartMissingAnalysisResult | null | undefined) {
  if (!result) return null;

  return (
    <Card size="small" title={TEXT.lastStartMissingResult}>
      <Space direction="vertical" size={12} style={{ width: '100%' }}>
        <Space wrap>
          <Text type="secondary">{TEXT.startedTasks}</Text>
          <Tag color={result.total_started > 0 ? 'purple' : 'default'}>{result.total_started}</Tag>
          <Text type="secondary">{TEXT.syncedExisting}</Text>
          <Tag color={result.total_synced_existing > 0 ? 'blue' : 'default'}>{result.total_synced_existing}</Tag>
          <Text type="secondary">{TEXT.skippedRunning}</Text>
          <Tag color={result.total_skipped_running > 0 ? 'gold' : 'default'}>{result.total_skipped_running}</Tag>
          <Text type="secondary">{TEXT.skippedNoContent}</Text>
          <Tag color={result.total_skipped_no_content > 0 ? 'volcano' : 'default'}>{result.total_skipped_no_content}</Tag>
        </Space>
        <Space direction="vertical" size={6} style={{ width: '100%' }}>
          <Text type="secondary">{TEXT.targetChapters}</Text>
          {renderResultChapterTags(result.target_chapter_numbers)}
        </Space>
        <Space direction="vertical" size={6} style={{ width: '100%' }}>
          <Text type="secondary">{TEXT.syncedChapters}</Text>
          {renderResultChapterTags(result.synced_existing_chapters)}
        </Space>
      </Space>
    </Card>
  );
}

export default function BookRemixAnalysisCoveragePanel({
  value,
  loading = false,
  starting = false,
  lastStartMissingResult = null,
  onRefresh,
  onStartMissingAnalysis,
  onOpenChapterAnalysis,
  onOpenChapters,
}: BookRemixAnalysisCoveragePanelProps) {
  const ready = Boolean(value?.fully_analyzed && value?.fully_synced);
  const hasAnalysisGaps = Boolean(
    value
    && (
      value.missing_source_chapters.length > 0
      || value.missing_analysis_chapters.length > 0
      || value.missing_change_package_chapters.length > 0
    ),
  );

  return (
    <Card
      title={TEXT.title}
      extra={(
        <Space wrap>
          <Button
            icon={<PlayCircleOutlined />}
            onClick={() => void onStartMissingAnalysis?.()}
            loading={starting}
            disabled={!onStartMissingAnalysis || !hasAnalysisGaps}
          >
            {TEXT.startMissing}
          </Button>
          <Button icon={<ReloadOutlined />} onClick={() => void onRefresh()} loading={loading}>
            {TEXT.refresh}
          </Button>
        </Space>
      )}
    >
      {value ? (
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Alert
            type={ready ? 'success' : 'warning'}
            showIcon
            message={ready ? TEXT.readyMessage : TEXT.gapMessage}
            description={ready ? TEXT.readyDescription : TEXT.gapDescription}
          />

          {renderContinuationRisk(value, {
            onStartMissingAnalysis,
            onOpenChapterAnalysis,
            onOpenChapters,
            starting,
          })}

          {renderStartMissingResult(lastStartMissingResult)}

          <Space wrap>
            <Text type="secondary">{TEXT.sourceChapters}</Text>
            <Tag color="blue">{value.source_chapters_count}/{value.source_chapter_count}</Tag>
            <Text type="secondary">{TEXT.analyzed}</Text>
            <Tag color={value.fully_analyzed ? 'green' : 'orange'}>{value.analyzed_chapter_count}</Tag>
            <Text type="secondary">{TEXT.synced}</Text>
            <Tag color={value.fully_synced ? 'green' : 'orange'}>{value.chapter_change_package_count}</Tag>
          </Space>

          <Row gutter={[12, 12]}>
            <Col xs={24} md={12}>
              <Card size="small" title={TEXT.analysisCoverage}>
                <Progress percent={value.analysis_coverage_percent} status={value.fully_analyzed ? 'success' : 'active'} />
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card size="small" title={TEXT.syncCoverage}>
                <Progress percent={value.change_package_coverage_percent} status={value.fully_synced ? 'success' : 'active'} />
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card size="small" title={TEXT.missingAnalysis}>
                {renderChapterList(value.missing_analysis_chapters, TEXT.emptyMissingAnalysis)}
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card size="small" title={TEXT.missingPackages}>
                {renderChapterList(value.missing_change_package_chapters, TEXT.emptyMissingPackages)}
              </Card>
            </Col>
            <Col xs={24}>
              <Card size="small" title={TEXT.missingSources}>
                {renderMissingSources(value.missing_source_chapters)}
              </Card>
            </Col>
            <Col xs={24}>
              <Card size="small" title={TEXT.actionPlan}>
                {renderActionPlan(value.analysis_action_plan)}
              </Card>
            </Col>
          </Row>
        </Space>
      ) : (
        <Empty description={TEXT.empty} />
      )}
    </Card>
  );
}
