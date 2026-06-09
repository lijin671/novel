import { useEffect, useMemo, useState } from 'react';
import { Alert, Button, Card, Col, Empty, Input, Row, Space, Tag, Typography, message } from 'antd';
import { CheckCircleOutlined, ReloadOutlined, SaveOutlined } from '@ant-design/icons';
import type { BookRemixBible, BookRemixBibleUpdatePayload } from '../../types/bookRemixBible';

const { Text } = Typography;
const { TextArea } = Input;

type EditableFieldKey = 'character_cards' | 'timeline' | 'story_arcs' | 'foreshadows' | 'hard_constraints';

const EDITABLE_FIELD_META: Array<{ key: EditableFieldKey; title: string }> = [
  { key: 'character_cards', title: 'character_cards（可编辑）' },
  { key: 'timeline', title: 'timeline（可编辑）' },
  { key: 'story_arcs', title: 'story_arcs（可编辑）' },
  { key: 'foreshadows', title: 'foreshadows（可编辑）' },
  { key: 'hard_constraints', title: 'hard_constraints（可编辑）' },
];

const STATUS_META: Record<BookRemixBible['generation_status'], { color: string; label: string }> = {
  pending: { color: 'default', label: 'pending' },
  running: { color: 'processing', label: 'running' },
  generated: { color: 'blue', label: 'generated' },
  failed: { color: 'red', label: 'failed' },
  confirmed: { color: 'green', label: 'confirmed' },
};

const EMPTY_DRAFTS: Record<EditableFieldKey, string> = {
  character_cards: '[]',
  timeline: '[]',
  story_arcs: '[]',
  foreshadows: '[]',
  hard_constraints: '[]',
};

export interface BookRemixBibleReviewProps {
  value: BookRemixBible | null;
  loading?: boolean;
  saving?: boolean;
  confirming?: boolean;
  regenerating?: boolean;
  onRefresh: () => Promise<void>;
  onSave: (payload: BookRemixBibleUpdatePayload) => Promise<void>;
  onConfirm: () => Promise<void>;
  onRegenerate?: () => Promise<void>;
}

function stringifyPretty(value: unknown): string {
  return JSON.stringify(value ?? [], null, 2);
}

function parseJsonArray(title: string, rawText: string): Array<Record<string, unknown>> {
  let parsed: unknown;
  try {
    parsed = JSON.parse(rawText || '[]');
  } catch {
    throw new Error(`${title} 不是合法 JSON`);
  }
  if (!Array.isArray(parsed)) {
    throw new Error(`${title} 必须是 JSON 数组`);
  }
  return parsed as Array<Record<string, unknown>>;
}

function renderJsonBlock(value: unknown) {
  const isEmptyArray = Array.isArray(value) && value.length === 0;
  const isEmptyObject = Boolean(
    value
      && typeof value === 'object'
      && !Array.isArray(value)
      && Object.keys(value as Record<string, unknown>).length === 0,
  );

  if (value == null || isEmptyArray || isEmptyObject) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无内容" />;
  }

  return (
    <pre
      style={{
        margin: 0,
        padding: 12,
        maxHeight: 300,
        overflow: 'auto',
        borderRadius: 6,
        background: 'var(--color-bg-container)',
      }}
    >
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

export default function BookRemixBibleReview({
  value,
  loading = false,
  saving = false,
  confirming = false,
  regenerating = false,
  onRefresh,
  onSave,
  onConfirm,
  onRegenerate,
}: BookRemixBibleReviewProps) {
  const [drafts, setDrafts] = useState<Record<EditableFieldKey, string>>(EMPTY_DRAFTS);

  useEffect(() => {
    if (!value) {
      setDrafts(EMPTY_DRAFTS);
      return;
    }
    setDrafts({
      character_cards: stringifyPretty(value.character_cards),
      timeline: stringifyPretty(value.timeline),
      story_arcs: stringifyPretty(value.story_arcs),
      foreshadows: stringifyPretty(value.foreshadows),
      hard_constraints: stringifyPretty(value.hard_constraints),
    });
  }, [value]);

  const hasDraftChanges = useMemo(() => {
    if (!value) return false;
    return (
      drafts.character_cards !== stringifyPretty(value.character_cards)
      || drafts.timeline !== stringifyPretty(value.timeline)
      || drafts.story_arcs !== stringifyPretty(value.story_arcs)
      || drafts.foreshadows !== stringifyPretty(value.foreshadows)
      || drafts.hard_constraints !== stringifyPretty(value.hard_constraints)
    );
  }, [drafts, value]);

  const statusTag = value ? STATUS_META[value.generation_status] : null;
  const canConfirm = value?.generation_status === 'generated' || value?.generation_status === 'confirmed';
  const canRegenerate = value?.generation_status === 'failed';

  const handleSave = async () => {
    try {
      const payload: BookRemixBibleUpdatePayload = {
        character_cards: parseJsonArray('character_cards', drafts.character_cards),
        timeline: parseJsonArray('timeline', drafts.timeline),
        story_arcs: parseJsonArray('story_arcs', drafts.story_arcs),
        foreshadows: parseJsonArray('foreshadows', drafts.foreshadows),
        hard_constraints: parseJsonArray('hard_constraints', drafts.hard_constraints),
      };
      await onSave(payload);
      message.success('Bible 可编辑区已保存');
    } catch (error) {
      const text = error instanceof Error ? error.message : '保存失败';
      message.error(text);
    }
  };

  const handleConfirm = async () => {
    try {
      await onConfirm();
    } catch {
      message.error('确认 Bible 失败');
    }
  };

  const handleRegenerate = async () => {
    if (!onRegenerate) return;
    try {
      await onRegenerate();
    } catch {
      message.error('Bible regeneration failed');
    }
  };

  return (
    <Card
      title="Step 1 · Bible 审校"
      extra={(
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => void onRefresh()} loading={loading}>
            刷新
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => void handleRegenerate()}
            loading={regenerating}
            disabled={!canRegenerate || !onRegenerate}
          >
            Regenerate Bible
          </Button>
          <Button
            icon={<SaveOutlined />}
            type="primary"
            onClick={() => void handleSave()}
            loading={saving}
            disabled={!value || !hasDraftChanges}
          >
            保存可编辑区
          </Button>
          <Button
            icon={<CheckCircleOutlined />}
            onClick={() => void handleConfirm()}
            loading={confirming}
            disabled={!value || !canConfirm}
          >
            确认 Bible
          </Button>
        </Space>
      )}
    >
      {value ? (
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Space wrap>
            <Text type="secondary">generation_status:</Text>
            {statusTag && <Tag color={statusTag.color}>{statusTag.label}</Tag>}
            <Text type="secondary">source_chapter_count: {value.source_chapter_count}</Text>
            {value.confirmed_at && <Text type="secondary">confirmed_at: {value.confirmed_at}</Text>}
          </Space>

          {value.generation_status === 'running' && (
            <Alert
              type="info"
              showIcon
              message="Bible 正在后台生成"
              description="可点击“刷新”获取最新状态；生成完成后请先校对可编辑区再确认。"
            />
          )}
          {value.generation_status === 'failed' && (
            <Alert
              type="warning"
              showIcon
              message="Bible 生成失败"
              description="请先点击“刷新”确认状态，然后在当前工作台点击“Regenerate Bible”重新生成。"
            />
          )}

          <Row gutter={[12, 12]}>
            {EDITABLE_FIELD_META.map((item) => (
              <Col xs={24} lg={12} key={item.key}>
                <Card size="small" title={item.title}>
                  <TextArea
                    rows={9}
                    value={drafts[item.key]}
                    onChange={(event) => {
                      const nextValue = event.target.value;
                      setDrafts((prev) => ({ ...prev, [item.key]: nextValue }));
                    }}
                  />
                </Card>
              </Col>
            ))}
          </Row>

          <Card size="small" title="world_rules（只读）">
            {renderJsonBlock(value.world_rules)}
          </Card>
          <Card size="small" title="organizations（只读）">
            {renderJsonBlock(value.organizations)}
          </Card>
          <Card size="small" title="style_signature（只读）">
            {renderJsonBlock(value.style_signature)}
          </Card>
          <Card size="small" title="conflicts（只读）">
            {renderJsonBlock(value.conflicts)}
          </Card>
          <Card size="small" title="generation_notes（只读）">
            {renderJsonBlock(value.generation_notes)}
          </Card>
        </Space>
      ) : (
        <Empty description="暂无 Bible 草稿（可先点击刷新）" />
      )}
    </Card>
  );
}
