import { useEffect, useMemo, useState } from 'react';
import { Alert, Button, Card, Col, Empty, Input, Row, Space, Tag, Typography, message } from 'antd';
import { CheckCircleOutlined, ReloadOutlined, RobotOutlined, SaveOutlined } from '@ant-design/icons';
import type {
  BookRemixBibleGenerationStatus,
  BookRemixContinuationPlan,
  BookRemixContinuationPlanUpdatePayload,
} from '../../types/bookRemixBible';

const { Text } = Typography;
const { TextArea } = Input;

type ArrayFieldKey = 'stage_goals' | 'beats' | 'priority_hooks' | 'guardrails';

const ARRAY_FIELD_META: Array<{ key: ArrayFieldKey; title: string }> = [
  { key: 'stage_goals', title: 'stage_goals（可编辑）' },
  { key: 'beats', title: 'beats（可编辑）' },
  { key: 'priority_hooks', title: 'priority_hooks（可编辑）' },
  { key: 'guardrails', title: 'guardrails（可编辑）' },
];

const STATUS_META: Record<BookRemixContinuationPlan['status'], { color: string; label: string }> = {
  draft: { color: 'blue', label: 'draft' },
  confirmed: { color: 'green', label: 'confirmed' },
};

const EMPTY_ARRAY_DRAFTS: Record<ArrayFieldKey, string> = {
  stage_goals: '[]',
  beats: '[]',
  priority_hooks: '[]',
  guardrails: '[]',
};

export interface BookRemixContinuationPlanPanelProps {
  value: BookRemixContinuationPlan | null;
  bibleStatus?: BookRemixBibleGenerationStatus | null;
  planOutdated?: boolean;
  loading?: boolean;
  generating?: boolean;
  saving?: boolean;
  confirming?: boolean;
  onRefresh: () => Promise<void>;
  onGenerate: (userDirection: string) => Promise<void>;
  onSave: (payload: BookRemixContinuationPlanUpdatePayload) => Promise<void>;
  onConfirm: () => Promise<void>;
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

export default function BookRemixContinuationPlanPanel({
  value,
  bibleStatus,
  planOutdated = false,
  loading = false,
  generating = false,
  saving = false,
  confirming = false,
  onRefresh,
  onGenerate,
  onSave,
  onConfirm,
}: BookRemixContinuationPlanPanelProps) {
  const [userDirection, setUserDirection] = useState('');
  const [summaryDraft, setSummaryDraft] = useState('');
  const [arrayDrafts, setArrayDrafts] = useState<Record<ArrayFieldKey, string>>(EMPTY_ARRAY_DRAFTS);

  useEffect(() => {
    if (!value) {
      setSummaryDraft('');
      setArrayDrafts(EMPTY_ARRAY_DRAFTS);
      return;
    }
    setSummaryDraft(value.summary || '');
    setArrayDrafts({
      stage_goals: stringifyPretty(value.stage_goals),
      beats: stringifyPretty(value.beats),
      priority_hooks: stringifyPretty(value.priority_hooks),
      guardrails: stringifyPretty(value.guardrails),
    });
  }, [value]);

  const canGenerate = bibleStatus === 'confirmed';
  const canConfirm = Boolean(value) && canGenerate && !planOutdated;
  const isStructurallyThin = useMemo(() => {
    if (!value) return false;
    const hasSummary = Boolean((value.summary || '').trim());
    const hasStructuredContent = [
      value.stage_goals,
      value.beats,
      value.priority_hooks,
      value.guardrails,
    ].some((items) => Array.isArray(items) && items.length > 0);
    return hasSummary && !hasStructuredContent;
  }, [value]);
  const hasChanges = useMemo(() => {
    if (!value) return false;
    return (
      summaryDraft !== (value.summary || '')
      || arrayDrafts.stage_goals !== stringifyPretty(value.stage_goals)
      || arrayDrafts.beats !== stringifyPretty(value.beats)
      || arrayDrafts.priority_hooks !== stringifyPretty(value.priority_hooks)
      || arrayDrafts.guardrails !== stringifyPretty(value.guardrails)
    );
  }, [arrayDrafts, summaryDraft, value]);

  const handleGenerate = async () => {
    try {
      await onGenerate(userDirection.trim());
      message.success('续写计划已生成');
    } catch {
      message.error('续写计划生成失败');
    }
  };

  const handleSave = async () => {
    try {
      await onSave({
        summary: summaryDraft,
        stage_goals: parseJsonArray('stage_goals', arrayDrafts.stage_goals),
        beats: parseJsonArray('beats', arrayDrafts.beats),
        priority_hooks: parseJsonArray('priority_hooks', arrayDrafts.priority_hooks),
        guardrails: parseJsonArray('guardrails', arrayDrafts.guardrails),
      });
      message.success('续写计划已保存');
    } catch (error) {
      const text = error instanceof Error ? error.message : '保存失败';
      message.error(text);
    }
  };

  const handleConfirm = async () => {
    try {
      await onConfirm();
    } catch {
      message.error('确认续写计划失败');
    }
  };

  return (
    <Card
      title="Step 2 · Continuation Plan 审校"
      extra={(
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => void onRefresh()} loading={loading}>
            刷新
          </Button>
          <Button
            icon={<RobotOutlined />}
            onClick={() => void handleGenerate()}
            loading={generating}
            disabled={!canGenerate}
          >
            生成计划
          </Button>
          <Button
            icon={<SaveOutlined />}
            type="primary"
            onClick={() => void handleSave()}
            loading={saving}
            disabled={!value || !hasChanges}
          >
            保存计划
          </Button>
          <Button
            icon={<CheckCircleOutlined />}
            onClick={() => void handleConfirm()}
            loading={confirming}
            disabled={!canConfirm}
          >
            确认计划
          </Button>
        </Space>
      )}
    >
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <Card size="small" title="生成方向（可选）">
          <Space direction="vertical" size={10} style={{ width: '100%' }}>
            <TextArea
              rows={3}
              value={userDirection}
              onChange={(event) => setUserDirection(event.target.value)}
              placeholder="例如：先收束上一卷核心悬念，再进入下一阶段升级。"
            />
            {canGenerate && planOutdated && (
              <Alert
                type="warning"
                showIcon
                message="Continuation plan is outdated"
                description="Bible has changed after this plan was generated. Please regenerate the plan before confirming."
              />
            )}
            {isStructurallyThin && (
              <Alert
                type="warning"
                showIcon
                message="Continuation plan is structurally incomplete"
                description="The plan summary exists, but the structured sections are empty. Refresh first; if it still looks thin, regenerate the plan before confirming."
              />
            )}
            {!canGenerate && (
              <Alert
                type="warning"
                showIcon
                message="请先确认 Bible"
                description="续写计划生成依赖已确认的 Bible。"
              />
            )}
          </Space>
        </Card>

        {value ? (
          <>
            <Space wrap>
              <Text type="secondary">status:</Text>
              <Tag color={STATUS_META[value.status].color}>{STATUS_META[value.status].label}</Tag>
              {value.confirmed_at && <Text type="secondary">confirmed_at: {value.confirmed_at}</Text>}
            </Space>

            <Card size="small" title="summary（可编辑）">
              <TextArea
                rows={4}
                value={summaryDraft}
                onChange={(event) => setSummaryDraft(event.target.value)}
              />
            </Card>

            <Row gutter={[12, 12]}>
              {ARRAY_FIELD_META.map((item) => (
                <Col xs={24} lg={12} key={item.key}>
                  <Card size="small" title={item.title}>
                    <TextArea
                      rows={8}
                      value={arrayDrafts[item.key]}
                      onChange={(event) => {
                        const nextValue = event.target.value;
                        setArrayDrafts((prev) => ({ ...prev, [item.key]: nextValue }));
                      }}
                    />
                  </Card>
                </Col>
              ))}
            </Row>
          </>
        ) : (
          <Empty description="暂无续写计划（可先点击“生成计划”）" />
        )}
      </Space>
    </Card>
  );
}
