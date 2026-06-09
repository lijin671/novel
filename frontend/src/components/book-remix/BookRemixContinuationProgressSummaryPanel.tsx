import { Alert, Button, Card, Col, Empty, List, Row, Space, Tag, Typography } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import type { BookRemixContinuationProgressSummary } from '../../types/bookRemixBible';

const { Text } = Typography;

export interface BookRemixContinuationProgressSummaryPanelProps {
  value: BookRemixContinuationProgressSummary | null;
  loading?: boolean;
  onRefresh: () => Promise<void>;
}

function stringifyValue(value: unknown): string {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return JSON.stringify(value);
}

function getFieldValue(item: Record<string, unknown>, keys: string[]): string {
  for (const key of keys) {
    const value = item[key];
    const text = stringifyValue(value);
    if (text) return text;
  }
  return '';
}

function formatChapterRange(value: BookRemixContinuationProgressSummary): string {
  const start = value.chapter_range?.start;
  const end = value.chapter_range?.end;
  if (typeof start === 'number' && typeof end === 'number') return `${start}-${end}`;
  if (typeof start === 'number') return `${start}`;
  if (typeof end === 'number') return `${end}`;
  return '暂无';
}

function renderStringList(items: string[], emptyText: string) {
  if (!items.length) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={emptyText} />;
  }

  return (
    <List
      size="small"
      dataSource={items}
      renderItem={(item) => <List.Item>{item}</List.Item>}
    />
  );
}

function renderTimeline(items: Array<Record<string, unknown>>) {
  if (!items.length) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无时间线推进" />;
  }

  return (
    <List
      size="small"
      dataSource={items}
      renderItem={(item) => {
        const chapterNumber = getFieldValue(item, ['chapter_number', 'chapter']);
        const event = getFieldValue(item, ['event', 'summary', 'description']);
        return (
          <List.Item>
            <Space direction="vertical" size={2} style={{ width: '100%' }}>
              {chapterNumber && <Tag color="blue">第 {chapterNumber} 章</Tag>}
              <Text>{event || stringifyValue(item)}</Text>
            </Space>
          </List.Item>
        );
      }}
    />
  );
}

function renderCharacterStates(items: Array<Record<string, unknown>>) {
  if (!items.length) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无角色状态变化" />;
  }

  return (
    <List
      size="small"
      dataSource={items}
      renderItem={(item) => {
        const name = getFieldValue(item, ['character_name', 'name']);
        const chapterNumber = getFieldValue(item, ['chapter_number', 'chapter']);
        const stateAfter = getFieldValue(item, ['state_after', 'state', 'summary']);
        return (
          <List.Item>
            <Space direction="vertical" size={2} style={{ width: '100%' }}>
              <Space wrap>
                {name && <Text strong>{name}</Text>}
                {chapterNumber && <Tag color="purple">第 {chapterNumber} 章</Tag>}
              </Space>
              <Text>{stateAfter || stringifyValue(item)}</Text>
            </Space>
          </List.Item>
        );
      }}
    />
  );
}

function renderEmotionalProgression(items: Array<Record<string, unknown>>) {
  if (!items.length) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无情感走势" />;
  }

  return (
    <List
      size="small"
      dataSource={items}
      renderItem={(item) => {
        const chapterNumber = getFieldValue(item, ['chapter_number', 'chapter']);
        const tone = getFieldValue(item, ['tone', 'primary_emotion', 'emotion']);
        const intensity = getFieldValue(item, ['intensity']);
        const curve = getFieldValue(item, ['curve']);
        return (
          <List.Item>
            <Space direction="vertical" size={2} style={{ width: '100%' }}>
              <Space wrap>
                {chapterNumber && <Tag color="magenta">第 {chapterNumber} 章</Tag>}
                {tone && <Text strong>{tone}</Text>}
                {intensity && <Tag color="volcano">强度 {intensity}</Tag>}
              </Space>
              {curve && <Text type="secondary">{curve}</Text>}
            </Space>
          </List.Item>
        );
      }}
    />
  );
}

export default function BookRemixContinuationProgressSummaryPanel({
  value,
  loading = false,
  onRefresh,
}: BookRemixContinuationProgressSummaryPanelProps) {
  return (
    <Card
      title="Step 1.5 · 全书续写进度"
      extra={(
        <Button icon={<ReloadOutlined />} onClick={() => void onRefresh()} loading={loading}>
          刷新
        </Button>
      )}
    >
      {value ? (
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Alert
            type="info"
            showIcon
            message="章节分析已沉淀为续写状态"
            description="这里展示已写回 Bible 和 Continuation Plan 的全书级进度，下一章续写会读取这些信息。"
          />

          <Space wrap>
            <Text type="secondary">变更包：</Text>
            <Tag color="blue">{value.package_count}</Tag>
            <Text type="secondary">章节范围：</Text>
            <Tag color="geekblue">{formatChapterRange(value)}</Tag>
          </Space>

          <Row gutter={[12, 12]}>
            <Col xs={24} lg={12}>
              <Card size="small" title="时间线推进">
                {renderTimeline(value.timeline_progression)}
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card size="small" title="最新角色状态">
                {renderCharacterStates(value.latest_character_states)}
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card size="small" title="情感走势">
                {renderEmotionalProgression(value.emotional_progression)}
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card size="small" title="已回收伏笔">
                {renderStringList(value.resolved_hooks, '暂无已回收伏笔')}
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card size="small" title="未回收伏笔">
                {renderStringList(value.open_hooks, '暂无未回收伏笔')}
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card size="small" title="已完成计划节点">
                {renderStringList(value.completed_plan_beats, '暂无已完成计划节点')}
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card size="small" title="待完成计划节点">
                {renderStringList(value.pending_plan_beats, '暂无待完成计划节点')}
              </Card>
            </Col>
          </Row>
        </Space>
      ) : (
        <Empty description="暂无全书续写进度；完成章节分析后会自动汇总" />
      )}
    </Card>
  );
}
