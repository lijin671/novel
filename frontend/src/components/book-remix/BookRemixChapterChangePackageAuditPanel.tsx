import { Alert, Button, Card, Col, Collapse, Empty, List, Row, Space, Tag, Typography } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import type { BookRemixChapterChangePackageList } from '../../types/bookRemixBible';

const { Paragraph, Text } = Typography;

export interface BookRemixChapterChangePackageAuditPanelProps {
  value: BookRemixChapterChangePackageList | null;
  loading?: boolean;
  onRefresh: () => Promise<void>;
}

const TEXT = {
  title: 'Step 1.6 · \u7ae0\u8282\u53d8\u66f4\u5305\u5ba1\u8ba1',
  refresh: '\u5237\u65b0',
  alertMessage: '\u9010\u7ae0\u6838\u5bf9\u5168\u4e66\u62c6\u89e3\u5bf9\u7eed\u5199\u72b6\u6001\u7684\u5f71\u54cd',
  alertDescription: '\u6bcf\u4e2a\u53d8\u66f4\u5305\u90fd\u6765\u81ea\u7ae0\u8282\u5206\u6790\u6216\u4eba\u5de5\u8865\u5145\uff0c\u7528\u4e8e\u89e3\u91ca\u65f6\u95f4\u7ebf\u3001\u89d2\u8272\u72b6\u6001\u3001\u4f0f\u7b14\u548c\u8ba1\u5212\u8282\u70b9\u662f\u600e\u4e48\u88ab\u6539\u5199\u7684\u3002',
  total: '\u53d8\u66f4\u5305\uff1a',
  range: '\u5f53\u524d\u663e\u793a\uff1a',
  source: '\u6765\u6e90',
  changedSections: '\u5f71\u54cd\u5206\u533a',
  timeline: '\u65f6\u95f4\u7ebf',
  characters: '\u89d2\u8272\u72b6\u6001',
  foreshadows: '\u4f0f\u7b14\u53d8\u5316',
  plan: '\u8ba1\u5212\u8fdb\u5ea6',
  guardrail: '生成门禁',
  guardrailPassed: '未触发',
  guardrailRewritten: '已修复',
  guardrailBlocked: '仍需复核',
  guardrailAttempts: '修复次数',
  empty: '\u6682\u65e0\u7ae0\u8282\u53d8\u66f4\u5305\uff1b\u5b8c\u6210\u7ae0\u8282\u5206\u6790\u540e\u4f1a\u81ea\u52a8\u5199\u5165',
  emptySection: '\u6682\u65e0\u8bb0\u5f55',
};

const GUARDRAIL_TYPE_COPY: Record<string, string> = {
  canon_repetition: '重复已确认 Canon',
  repetitive_opening: '开篇复述上一章',
  recap_cue: '承接套话',
  meta_output: '章节元信息外露',
  omniscient_cue: '视角越界',
  empty_output: '空输出',
};

const GUARDRAIL_SEVERITY_COLOR: Record<string, string> = {
  high: 'red',
  medium: 'orange',
  low: 'blue',
};

function stringifyValue(value: unknown): string {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return JSON.stringify(value);
}

function asRecordList(value: unknown): Array<Record<string, unknown>> {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is Record<string, unknown> => Boolean(item && typeof item === 'object' && !Array.isArray(item)));
}

function getFieldValue(item: Record<string, unknown>, keys: string[]): string {
  for (const key of keys) {
    const value = stringifyValue(item[key]);
    if (value) return value;
  }
  return '';
}

function formatPackageTitle(item: Record<string, unknown>, index: number): string {
  const chapterNumber = stringifyValue(item.chapter_number);
  const chapterTitle = stringifyValue(item.chapter_title || item.title);
  if (chapterNumber && chapterTitle) return `\u7b2c ${chapterNumber} \u7ae0 \u00b7 ${chapterTitle}`;
  if (chapterNumber) return `\u7b2c ${chapterNumber} \u7ae0`;
  return chapterTitle || `\u53d8\u66f4\u5305 ${index + 1}`;
}

function renderDetailList(items: Array<Record<string, unknown>>, keys: string[]) {
  if (!items.length) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={TEXT.emptySection} />;
  }

  return (
    <List
      size="small"
      dataSource={items}
      renderItem={(item) => {
        const text = getFieldValue(item, keys) || stringifyValue(item);
        const status = stringifyValue(item.status);
        return (
          <List.Item>
            <Space direction="vertical" size={2} style={{ width: '100%' }}>
              <Text>{text}</Text>
              {status && <Tag>{status}</Tag>}
            </Space>
          </List.Item>
        );
      }}
    />
  );
}

function renderGuardrailCheck(item: Record<string, unknown>) {
  const guardrail = item.guardrail_check;
  if (!guardrail || typeof guardrail !== 'object' || Array.isArray(guardrail)) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={TEXT.guardrailPassed} />;
  }

  const record = guardrail as Record<string, unknown>;
  const applied = Boolean(record.applied);
  const finalPassed = record.final_passed !== false;
  const attempts = stringifyValue(record.attempts || 0);
  const violations = asRecordList(record.violations);
  const statusText = applied ? TEXT.guardrailRewritten : finalPassed ? TEXT.guardrailPassed : TEXT.guardrailBlocked;
  const statusColor = applied ? 'orange' : finalPassed ? 'green' : 'red';

  return (
    <Space direction="vertical" size={8} style={{ width: '100%' }}>
      <Space wrap>
        <Tag color={statusColor}>{statusText}</Tag>
        <Text type="secondary">{TEXT.guardrailAttempts}</Text>
        <Tag>{attempts}</Tag>
      </Space>
      {violations.length > 0 ? (
        <List
          size="small"
          dataSource={violations}
          renderItem={(violation) => {
            const type = stringifyValue(violation.type);
            const severity = stringifyValue(violation.severity);
            const description = stringifyValue(violation.description);
            const context = stringifyValue(violation.context);
            return (
              <List.Item>
                <Space direction="vertical" size={2} style={{ width: '100%' }}>
                  <Space wrap>
                    <Tag color={GUARDRAIL_SEVERITY_COLOR[severity] || 'default'}>{severity || 'unknown'}</Tag>
                    <Tag>{GUARDRAIL_TYPE_COPY[type] || type || 'unknown'}</Tag>
                  </Space>
                  {description && <Text>{description}</Text>}
                  {context && <Text type="secondary">{context}</Text>}
                </Space>
              </List.Item>
            );
          }}
        />
      ) : (
        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={TEXT.emptySection} />
      )}
    </Space>
  );
}

export default function BookRemixChapterChangePackageAuditPanel({
  value,
  loading = false,
  onRefresh,
}: BookRemixChapterChangePackageAuditPanelProps) {
  const items = value?.items ?? [];
  const visibleStart = items.length ? (value?.offset ?? 0) + 1 : 0;
  const visibleEnd = items.length ? (value?.offset ?? 0) + items.length : 0;

  return (
    <Card
      title={TEXT.title}
      extra={(
        <Button icon={<ReloadOutlined />} onClick={() => void onRefresh()} loading={loading}>
          {TEXT.refresh}
        </Button>
      )}
    >
      {value && items.length > 0 ? (
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Alert
            type="info"
            showIcon
            message={TEXT.alertMessage}
            description={TEXT.alertDescription}
          />

          <Space wrap>
            <Text type="secondary">{TEXT.total}</Text>
            <Tag color="blue">{value.package_count}</Tag>
            <Text type="secondary">{TEXT.range}</Text>
            <Tag color="geekblue">{visibleStart}-{visibleEnd}</Tag>
          </Space>

          <Collapse
            items={items.map((item, index) => {
              const source = stringifyValue(item.source);
              const changedSections = Array.isArray(item.changed_sections)
                ? item.changed_sections.map((section) => stringifyValue(section)).filter(Boolean)
                : [];
              return {
                key: `${stringifyValue(item.chapter_id) || stringifyValue(item.chapter_number) || index}`,
                label: formatPackageTitle(item, index),
                extra: source ? <Tag>{source}</Tag> : undefined,
                children: (
                  <Space direction="vertical" size={12} style={{ width: '100%' }}>
                    {item.summary && <Paragraph style={{ marginBottom: 0 }}>{item.summary}</Paragraph>}
                    <Space wrap>
                      {source && (
                        <>
                          <Text type="secondary">{TEXT.source}</Text>
                          <Tag>{source}</Tag>
                        </>
                      )}
                      {changedSections.length > 0 && (
                        <>
                          <Text type="secondary">{TEXT.changedSections}</Text>
                          {changedSections.map((section) => <Tag key={section} color="purple">{section}</Tag>)}
                        </>
                      )}
                    </Space>

                    <Row gutter={[12, 12]}>
                      <Col xs={24} lg={12}>
                        <Card size="small" title={TEXT.timeline}>
                          {renderDetailList(asRecordList(item.timeline_delta), ['event', 'summary', 'content'])}
                        </Card>
                      </Col>
                      <Col xs={24} lg={12}>
                        <Card size="small" title={TEXT.characters}>
                          {renderDetailList(asRecordList(item.character_state_changes), ['state_after', 'summary', 'content', 'character_name'])}
                        </Card>
                      </Col>
                      <Col xs={24} lg={12}>
                        <Card size="small" title={TEXT.foreshadows}>
                          {renderDetailList(asRecordList(item.foreshadow_changes), ['hook', 'summary', 'content', 'title'])}
                        </Card>
                      </Col>
                      <Col xs={24} lg={12}>
                        <Card size="small" title={TEXT.plan}>
                          {renderDetailList(asRecordList(item.plan_progress), ['beat', 'summary', 'content', 'name'])}
                        </Card>
                      </Col>
                      <Col xs={24}>
                        <Card size="small" title={TEXT.guardrail}>
                          {renderGuardrailCheck(item)}
                        </Card>
                      </Col>
                    </Row>
                  </Space>
                ),
              };
            })}
          />
        </Space>
      ) : (
        <Empty description={TEXT.empty} />
      )}
    </Card>
  );
}
