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
  'https://github.com/MangoLion/plotbunni',
  'https://github.com/zlx362211854/novelforge-agent',
  'https://github.com/MissingDanial/StyleMuse',
  'https://github.com/mert-ozdemirr/sherlock-counterfactual-modular-graph-rag',
  'https://github.com/booknlp/booknlp',
  'https://github.com/google-deepmind/narrativeqa',
];

const ADDITIONAL_HINT_GROUP_LIMIT = 24;
const WORKFLOW_PATTERN_EVIDENCE_LIMIT = 12;
const WORKFLOW_PATTERN_SOURCE_LIMIT = 3;
const PINNED_HINT_KEYS = new Set([
  'whole_book_analysis_targets',
  'continuation_prompt_hints',
  'style_signature_hints',
  'structured_generation_hints',
  'card_workbench_hints',
  'context_reference_hints',
  'scene_asset_pipeline_hints',
  'publication_pipeline_hints',
  'self_review_policy_hints',
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
  'plotline_thread_tracking_hints',
  'rolling_summary_context_trim_hints',
  'local_first_workspace_hints',
  'prompt_library_hints',
  'scene_level_generation_hints',
  'review_queue_staging_hints',
  'style_guide_layering_hints',
  'entity_schema_custom_fields_hints',
  'content_ref_externalization_hints',
  'graph_healing_hints',
  'contradiction_detection_hints',
  'graph_branching_atomicity_hints',
  'relationship_graph_global_replace_gate_hints',
  'query_lint_contract_hints',
  'premature_ending_guard_hints',
  'layered_memory_model_hints',
  'plot_dependency_graph_hints',
  'plotgrid_scene_matrix_hints',
  'scene_status_dashboard_hints',
  'gradual_reveal_control_hints',
  'setup_payoff_tracking_hints',
  'scene_type_directing_hints',
  'worldpkg_export_hints',
  'alternate_timeline_branching_hints',
  'divergence_guidance_hints',
  'plain_text_project_storage_hints',
  'synopsis_cross_reference_hints',
  'snowflake_premise_expansion_hints',
  'outliner_index_cards_hints',
  'narrative_strand_mapping_hints',
  'character_depth_interview_hints',
  'mindmap_visual_planning_hints',
  'manuscript_export_formats_hints',
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
  'book_mining_genesis_automation_gate_hints',
  'multi_book_autopilot_studio_gate_hints',
  'longrun_commit_projection_health_gate_hints',
  'fresh_context_chapter_iteration_gate_hints',
  'agentwrite_plan_write_pipeline_hints',
  'long_output_length_quality_ruler_hints',
  'long_context_reward_dimension_gate_hints',
  'instance_specific_writing_criteria_gate_hints',
  'material_grounded_query_refinement_hints',
  'hybrid_rubric_pairwise_elo_judge_hints',
  'judge_bias_mitigation_check_hints',
  'plan_reflect_character_chapter_pipeline_hints',
  'human_story_metric_panel_hints',
  'hierarchical_cowriting_story_scaffold_hints',
  'human_coauthor_edit_boundary_hints',
  'recursive_reprompt_revision_loop_hints',
  'reranker_guided_candidate_selection_hints',
  'event_to_sentence_realization_trace_hints',
  'entity_memory_slotfill_grounding_hints',
  'book_memory_bank_context_lattice_hints',
  'ideation_worksheet_foundation_gate_hints',
  'spec_driven_fiction_scene_tasks_hints',
  'toc_aware_source_deconstruction_hints',
  'two_pass_context_glossary_pipeline_hints',
  'inline_author_edit_markup_versioning_hints',
  'chapter_split_deconstruction_export_gate_hints',
  'final_prompt_preview_span_revision_gate_hints',
  'project_skill_agent_loop_gate_hints',
  'knowledge_document_writeback_trace_gate_hints',
  'host_instruction_context_boundary_gate_hints',
  'schema_review_revision_recovery_gate_hints',
  'cjk_bm25_context_retrieval_gate_hints',
  'dynamic_architecture_extension_gate_hints',
  'anti_copy_style_rag_gate_hints',
  'living_codex_editorial_workbench_gate_hints',
  'agent_role_profile_workflow_gate_hints',
  'confirmed_action_audit_recovery_gate_hints',
  'project_isolated_story_bible_query_gate_hints',
  'work_dna_method_transfer_eval_gate_hints',
  'governed_full_reading_continuation_gate_hints',
  'long_term_author_preference_memory_hints',
  'community_graph_source_deconstruction_hints',
  'dual_level_graph_vector_retrieval_hints',
  'schema_guided_graph_extraction_hints',
  'counterfactual_story_graph_rag_gate_hints',
  'character_knowledge_timeline_gate_hints',
  'chinese_segmentation_keyword_gate_hints',
  'chinese_ner_alias_consistency_gate_hints',
  'chinese_text_normalization_gate_hints',
  'chinese_error_correction_review_gate_hints',
  'literary_event_entity_annotation_gate_hints',
  'narrative_event_evolution_graph_gate_hints',
  'sentiment_arc_emotion_trajectory_gate_hints',
  'cross_context_coreference_gate_hints',
  'character_interaction_network_gate_hints',
  'character_quote_attribution_map_hints',
  'readability_pacing_metric_gate_hints',
  'lexical_diversity_voice_audit_hints',
  'keyphrase_motif_extraction_hints',
  'semantic_chunk_boundary_map_hints',
  'chapter_summary_anchor_gate_hints',
  'topic_drift_map_hints',
  'context_faithfulness_eval_gate_hints',
  'retrieval_trace_observability_gate_hints',
  'prompt_regression_eval_suite_hints',
  'source_text_fingerprint_gate_hints',
  'fuzzy_phrase_similarity_gate_hints',
  'diff_span_copy_review_hints',
  'minhash_lsh_near_duplicate_gate_hints',
  'simhash_hamming_similarity_gate_hints',
  'semantic_duplicate_cluster_gate_hints',
  'embedding_similarity_independence_gate_hints',
  'style_axis_diversity_fingerprint_hints',
  'stylometric_author_fingerprint_gate_hints',
  'function_word_syntax_style_gate_hints',
  'authorship_attribution_similarity_gate_hints',
  'style_overfit_regression_gate_hints',
  'paraphrase_independence_review_gate_hints',
  'ai_prose_fingerprint_cluster_gate_hints',
  'trope_inventory_similarity_gate_hints',
  'trope_graph_expectation_map_hints',
  'trope_density_novelty_budget_hints',
  'trope_source_boundary_review_hints',
  'reader_retention_review_gate_hints',
  'serial_reader_reward_contract_gate_hints',
  'reader_rating_signal_model_hints',
  'review_spoiler_sentiment_corpus_hints',
  'beta_reader_archetype_panel_hints',
  'comp_title_market_positioning_hints',
  'local_reader_experience_editor_hints',
  'manuscript_health_ai_prep_gate_hints',
  'anti_statistical_center_chapter_type_gate_hints',
  'prose_lint_style_rule_gate_hints',
  'grammar_spelling_copyedit_gate_hints',
  'copyedit_diagnostic_triage_queue_hints',
  'reader_reward_channel_gate_hints',
  'tri_modal_workflow_validation_gate_hints',
  'scene_promise_mob_review_gate_hints',
  'webnovel_genre_tracker_gate_hints',
  'simulation_causal_ledger_verification_gate_hints',
  'writer_git_exploration_review_gate_hints',
  'narrative_qa_comprehension_gate_hints',
  'chapter_summary_alignment_gate_hints',
  'story_question_answer_validation_gate_hints',
  'causal_why_explanation_gate_hints',
  'story_commonsense_consistency_gate_hints',
  'query_focused_long_summary_gate_hints',
  'source_license_detection_gate_hints',
  'spdx_reuse_compliance_gate_hints',
  'public_domain_corpus_boundary_hints',
  'attribution_derivative_work_gate_hints',
  'source_entity_redaction_gate_hints',
  'custom_entity_label_inventory_hints',
  'placeholder_alias_consistency_map_hints',
  'proper_noun_leakage_review_hints',
  'source_format_import_manifest_hints',
  'pdf_layout_text_extraction_gate_hints',
  'ocr_scanned_page_import_gate_hints',
  'document_partition_chapter_detection_gate_hints',
  'import_provenance_checksum_gate_hints',
  'epub_structure_validation_gate_hints',
  'ebook_accessibility_audit_gate_hints',
  'front_back_matter_metadata_gate_hints',
  'toc_navigation_consistency_gate_hints',
]);

function parseSeedUrls(value: string): string[] {
  return value
    .split(/[\n,]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseLineItems(value: string): string[] {
  return value
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function BookRemixSourceDiscoveryPanel() {
  const [value, setValue] = useState<SourceDiscoveryLatestArtifactResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [repositorySeeds, setRepositorySeeds] = useState(DEFAULT_GITHUB_REPOSITORY_SEEDS.join('\n'));
  const [repositorySeedsEdited, setRepositorySeedsEdited] = useState(false);
  const [githubQueries, setGithubQueries] = useState('');
  const [githubQueriesEdited, setGithubQueriesEdited] = useState(false);
  const [linuxDoRssUrls, setLinuxDoRssUrls] = useState('');
  const [linuxDoRssUrlsEdited, setLinuxDoRssUrlsEdited] = useState(false);

  const loadLatest = async () => {
    setLoading(true);
    try {
      const result = await sourceDiscoveryApi.getLatest();
      setValue(result);
      if (!githubQueriesEdited && result.default_github_queries?.length) {
        setGithubQueries(result.default_github_queries.join('\n'));
      }
      if (!repositorySeedsEdited && result.default_github_repository_urls?.length) {
        setRepositorySeeds(result.default_github_repository_urls.join('\n'));
      }
      if (!linuxDoRssUrlsEdited && result.default_linux_do_rss_urls?.length) {
        setLinuxDoRssUrls(result.default_linux_do_rss_urls.join('\n'));
      }
    } finally {
      setLoading(false);
    }
  };

  const runDiscovery = async () => {
    setRunning(true);
    try {
      await sourceDiscoveryApi.runLedger({
        write_to_docs: true,
        github_queries: githubQueriesEdited || githubQueries.trim() ? parseLineItems(githubQueries) : undefined,
        github_repository_urls: parseSeedUrls(repositorySeeds),
        linux_do_rss_urls: linuxDoRssUrlsEdited || linuxDoRssUrls.trim() ? parseSeedUrls(linuxDoRssUrls) : undefined,
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
        github_queries: githubQueriesEdited || githubQueries.trim() ? parseLineItems(githubQueries) : undefined,
        github_repository_urls: parseSeedUrls(repositorySeeds),
        linux_do_rss_urls: linuxDoRssUrlsEdited || linuxDoRssUrls.trim() ? parseSeedUrls(linuxDoRssUrls) : undefined,
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
                onChange={(event) => {
                  setRepositorySeedsEdited(true);
                  setRepositorySeeds(event.target.value);
                }}
                placeholder="https://github.com/voocel/ainovel-cli"
              />
              <Text type="secondary">
                {`后端默认 seed：${value?.default_github_repository_urls?.length ?? DEFAULT_GITHUB_REPOSITORY_SEEDS.length} 个；手动编辑后本次页面会保留你的输入。`}
              </Text>
            </Space>
          </Card>

          <Card size="small" title="GitHub Search 查询">
            <Space direction="vertical" size={8} style={{ width: '100%' }}>
              <Text type="secondary">
                {'每行一个 GitHub Search 查询。查询内含 in:name,description,readme 这类逗号语法，所以这里只按换行拆分。'}
              </Text>
              <TextArea
                rows={4}
                value={githubQueries}
                onChange={(event) => {
                  setGithubQueriesEdited(true);
                  setGithubQueries(event.target.value);
                }}
                placeholder={'("ai novel" OR "novel writing") in:name,description,readme'}
              />
              <Text type="secondary">
                {`后端默认查询：${value?.default_github_queries?.length ?? 0} 个；清空后刷新会跳过 GitHub Search，只保留显式仓库。`}
              </Text>
            </Space>
          </Card>

          <Card size="small" title="Community RSS 来源">
            <Space direction="vertical" size={8} style={{ width: '100%' }}>
              <Text type="secondary">
                {'每行或逗号分隔一个公开 RSS URL。只读公开摘要，不绕过登录、403、429、WAF 或 CAPTCHA。'}
              </Text>
              <TextArea
                rows={2}
                value={linuxDoRssUrls}
                onChange={(event) => {
                  setLinuxDoRssUrlsEdited(true);
                  setLinuxDoRssUrls(event.target.value);
                }}
                placeholder="https://linux.do/latest.rss"
              />
              <Text type="secondary">
                {`后端默认 RSS：${value?.default_linux_do_rss_urls?.length ?? 0} 个；手动编辑后本次页面会保留你的输入。`}
              </Text>
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
            {renderHintGroup('Core remix kernel gates', [
              ['Continuation prompt hints', patternPackPayload?.continuation_prompt_hints],
              ['Style signature hints', patternPackPayload?.style_signature_hints],
              ['Structured generation hints', patternPackPayload?.structured_generation_hints],
              ['Card workbench hints', patternPackPayload?.card_workbench_hints],
              ['Context reference hints', patternPackPayload?.context_reference_hints],
              ['Scene asset pipeline hints', patternPackPayload?.scene_asset_pipeline_hints],
              ['Publication pipeline hints', patternPackPayload?.publication_pipeline_hints],
              ['Self-review policy hints', patternPackPayload?.self_review_policy_hints],
            ])}
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
              ['Plotline thread tracking gates', patternPackPayload?.plotline_thread_tracking_hints],
              ['Rolling summary context trim gates', patternPackPayload?.rolling_summary_context_trim_hints],
            ])}
            {renderHintGroup('Workspace / scene planning gates', [
              ['Local-first workspace gates', patternPackPayload?.local_first_workspace_hints],
              ['Prompt library gates', patternPackPayload?.prompt_library_hints],
              ['Scene-level generation gates', patternPackPayload?.scene_level_generation_hints],
              ['Review queue staging gates', patternPackPayload?.review_queue_staging_hints],
              ['Style guide layering gates', patternPackPayload?.style_guide_layering_hints],
              ['Entity schema custom field gates', patternPackPayload?.entity_schema_custom_fields_hints],
              ['ContentRef externalization gates', patternPackPayload?.content_ref_externalization_hints],
              ['Graph healing gates', patternPackPayload?.graph_healing_hints],
              ['Contradiction detection gates', patternPackPayload?.contradiction_detection_hints],
              ['Graph branching atomicity gates', patternPackPayload?.graph_branching_atomicity_hints],
              ['Query lint contract gates', patternPackPayload?.query_lint_contract_hints],
            ])}
            {renderHintGroup('Plotgrid / reveal / branch gates', [
              ['Premature ending guards', patternPackPayload?.premature_ending_guard_hints],
              ['Layered memory model gates', patternPackPayload?.layered_memory_model_hints],
              ['Plot dependency graph gates', patternPackPayload?.plot_dependency_graph_hints],
              ['Plotgrid scene matrix gates', patternPackPayload?.plotgrid_scene_matrix_hints],
              ['Scene status dashboard gates', patternPackPayload?.scene_status_dashboard_hints],
              ['Gradual reveal control gates', patternPackPayload?.gradual_reveal_control_hints],
              ['Setup / payoff tracking gates', patternPackPayload?.setup_payoff_tracking_hints],
              ['Scene type directing gates', patternPackPayload?.scene_type_directing_hints],
              ['WorldPkg export gates', patternPackPayload?.worldpkg_export_hints],
              ['Alternate timeline branching gates', patternPackPayload?.alternate_timeline_branching_hints],
              ['Divergence guidance gates', patternPackPayload?.divergence_guidance_hints],
            ])}
            {renderHintGroup('Mature manuscript planning gates', [
              ['Plain text project storage gates', patternPackPayload?.plain_text_project_storage_hints],
              ['Synopsis cross-reference gates', patternPackPayload?.synopsis_cross_reference_hints],
              ['Snowflake premise expansion gates', patternPackPayload?.snowflake_premise_expansion_hints],
              ['Outliner index-card gates', patternPackPayload?.outliner_index_cards_hints],
              ['Narrative strand mapping gates', patternPackPayload?.narrative_strand_mapping_hints],
              ['Character depth interview gates', patternPackPayload?.character_depth_interview_hints],
              ['Mindmap visual planning gates', patternPackPayload?.mindmap_visual_planning_hints],
              ['Manuscript export format gates', patternPackPayload?.manuscript_export_formats_hints],
            ])}
            {renderHintGroup('Causal state-machine / skill workflow gates', [
              ['Causal Dramatica agent pipeline gates', patternPackPayload?.causal_dramatica_agent_pipeline_hints],
              ['Capture distillation production gates', patternPackPayload?.capture_distillation_production_gate_hints],
              ['Skill-orchestrated Chinese novel workflow gates', patternPackPayload?.skill_orchestrated_chinese_novel_workflow_hints],
              ['LangGraph story state machine gates', patternPackPayload?.langgraph_story_state_machine_hints],
              ['Agent role profile workflow gates', patternPackPayload?.agent_role_profile_workflow_gate_hints],
              ['Confirmed action audit recovery gates', patternPackPayload?.confirmed_action_audit_recovery_gate_hints],
              ['Project-isolated story-bible query gates', patternPackPayload?.project_isolated_story_bible_query_gate_hints],
              ['Work-DNA method transfer/eval gates', patternPackPayload?.work_dna_method_transfer_eval_gate_hints],
              ['Governed full-reading continuation gates', patternPackPayload?.governed_full_reading_continuation_gate_hints],
              ['Story daemon evolution loop gates', patternPackPayload?.story_daemon_evolution_loop_hints],
            ])}
            {renderHintGroup('Local RAG / canon QA / patch replay gates', [
              ['Local RAG writing IDE gates', patternPackPayload?.local_rag_writing_ide_gate_hints],
              ['Canon drift continuity QA gates', patternPackPayload?.canon_drift_continuity_qa_gate_hints],
              ['Patch replay manuscript state gates', patternPackPayload?.patch_replay_manuscript_state_gate_hints],
              ['Microkernel skill plugin isolation gates', patternPackPayload?.microkernel_skill_plugin_isolation_gate_hints],
              ['Interactive reader-writer loop gates', patternPackPayload?.interactive_reader_writer_loop_gate_hints],
              ['Abstract style learning skill gates', patternPackPayload?.abstract_style_learning_skill_gate_hints],
              ['Living codex editorial workbench gates', patternPackPayload?.living_codex_editorial_workbench_gate_hints],
            ])}
            {renderHintGroup('Impromptu / offline / atelier gates', [
              ['Impromptu thread-pool chapter gates', patternPackPayload?.impromptu_thread_pool_chapter_gate_hints],
              ['Offline inspiration-bank style gates', patternPackPayload?.offline_inspiration_bank_style_gate_hints],
              ['Atelier phase pipeline gates', patternPackPayload?.atelier_phase_pipeline_gate_hints],
            ])}
            {renderHintGroup('Book-mining / autopilot / longrun gates', [
              ['Book mining genesis automation gates', patternPackPayload?.book_mining_genesis_automation_gate_hints],
              ['Multi-book autopilot studio gates', patternPackPayload?.multi_book_autopilot_studio_gate_hints],
              ['Longrun commit projection health gates', patternPackPayload?.longrun_commit_projection_health_gate_hints],
              ['Fresh-context chapter iteration gates', patternPackPayload?.fresh_context_chapter_iteration_gate_hints],
            ])}
            {renderHintGroup('Long-output planning / reward gates', [
              ['AgentWrite plan-write pipeline gates', patternPackPayload?.agentwrite_plan_write_pipeline_hints],
              ['Long-output length quality ruler gates', patternPackPayload?.long_output_length_quality_ruler_hints],
              ['Long-context reward dimension gates', patternPackPayload?.long_context_reward_dimension_gate_hints],
            ])}
            {renderHintGroup('Writing benchmark / judge gates', [
              ['Instance-specific writing criteria gates', patternPackPayload?.instance_specific_writing_criteria_gate_hints],
              ['Material-grounded query refinement gates', patternPackPayload?.material_grounded_query_refinement_hints],
              ['Hybrid rubric pairwise Elo judge gates', patternPackPayload?.hybrid_rubric_pairwise_elo_judge_hints],
              ['Judge bias mitigation checks', patternPackPayload?.judge_bias_mitigation_check_hints],
              ['Plan-reflect character chapter pipeline gates', patternPackPayload?.plan_reflect_character_chapter_pipeline_hints],
              ['Human story metric panel gates', patternPackPayload?.human_story_metric_panel_hints],
            ])}
            {renderHintGroup('Co-writing / recursive revision gates', [
              ['Hierarchical co-writing story scaffold gates', patternPackPayload?.hierarchical_cowriting_story_scaffold_hints],
              ['Human coauthor edit boundaries', patternPackPayload?.human_coauthor_edit_boundary_hints],
              ['Recursive reprompt revision loop gates', patternPackPayload?.recursive_reprompt_revision_loop_hints],
              ['Reranker-guided candidate selection gates', patternPackPayload?.reranker_guided_candidate_selection_hints],
              ['Event-to-sentence realization trace gates', patternPackPayload?.event_to_sentence_realization_trace_hints],
              ['Entity memory slotfill grounding gates', patternPackPayload?.entity_memory_slotfill_grounding_hints],
            ])}
            {renderHintGroup('Source deconstruction / memory glossary gates', [
              ['Book memory-bank context lattice gates', patternPackPayload?.book_memory_bank_context_lattice_hints],
              ['Spec-driven fiction scene task gates', patternPackPayload?.spec_driven_fiction_scene_tasks_hints],
              ['TOC-aware source deconstruction gates', patternPackPayload?.toc_aware_source_deconstruction_hints],
              ['Two-pass context glossary pipeline gates', patternPackPayload?.two_pass_context_glossary_pipeline_hints],
              ['Inline author edit markup versioning gates', patternPackPayload?.inline_author_edit_markup_versioning_hints],
              ['Chapter split deconstruction export gates', patternPackPayload?.chapter_split_deconstruction_export_gate_hints],
              ['Final-prompt preview span revision gates', patternPackPayload?.final_prompt_preview_span_revision_gate_hints],
              ['Project skill agent-loop gates', patternPackPayload?.project_skill_agent_loop_gate_hints],
              ['Knowledge document writeback trace gates', patternPackPayload?.knowledge_document_writeback_trace_gate_hints],
              ['Host instruction/context boundary gates', patternPackPayload?.host_instruction_context_boundary_gate_hints],
              ['Schema review/revision recovery gates', patternPackPayload?.schema_review_revision_recovery_gate_hints],
              ['Dynamic architecture extension gates', patternPackPayload?.dynamic_architecture_extension_gate_hints],
              ['Anti-copy style RAG gates', patternPackPayload?.anti_copy_style_rag_gate_hints],
            ])}
            {renderHintGroup('Graph memory / retrieval grounding gates', [
              ['Temporal canon context graph gates', patternPackPayload?.temporal_canon_context_graph_hints],
              ['Long-term author preference memory gates', patternPackPayload?.long_term_author_preference_memory_hints],
              ['Community graph source deconstruction gates', patternPackPayload?.community_graph_source_deconstruction_hints],
              ['Dual-level graph vector retrieval gates', patternPackPayload?.dual_level_graph_vector_retrieval_hints],
              ['CJK BM25 context retrieval gates', patternPackPayload?.cjk_bm25_context_retrieval_gate_hints],
              ['Schema-guided graph extraction gates', patternPackPayload?.schema_guided_graph_extraction_hints],
              ['Counterfactual story Graph-RAG gates', patternPackPayload?.counterfactual_story_graph_rag_gate_hints],
              ['Relationship graph global replace gates', patternPackPayload?.relationship_graph_global_replace_gate_hints],
            ])}
            {renderHintGroup('Chinese text processing gates', [
              ['Chinese segmentation / keyword gates', patternPackPayload?.chinese_segmentation_keyword_gate_hints],
              ['Chinese NER / alias consistency gates', patternPackPayload?.chinese_ner_alias_consistency_gate_hints],
              ['Chinese text normalization gates', patternPackPayload?.chinese_text_normalization_gate_hints],
              ['Chinese correction review gates', patternPackPayload?.chinese_error_correction_review_gate_hints],
            ])}
            {renderHintGroup('Narrative event / emotion graph gates', [
              ['Literary event/entity annotation gates', patternPackPayload?.literary_event_entity_annotation_gate_hints],
              ['Narrative event evolution graph gates', patternPackPayload?.narrative_event_evolution_graph_gate_hints],
              ['Sentiment arc / emotion trajectory gates', patternPackPayload?.sentiment_arc_emotion_trajectory_gate_hints],
              ['Cross-context coreference gates', patternPackPayload?.cross_context_coreference_gate_hints],
              ['Character interaction network gates', patternPackPayload?.character_interaction_network_gate_hints],
            ])}
            {renderHintGroup('Book NLP / readability / motif gates', [
              ['Character quote attribution maps', patternPackPayload?.character_quote_attribution_map_hints],
              ['Readability pacing metric gates', patternPackPayload?.readability_pacing_metric_gate_hints],
              ['Lexical diversity voice audits', patternPackPayload?.lexical_diversity_voice_audit_hints],
              ['Keyphrase motif extraction gates', patternPackPayload?.keyphrase_motif_extraction_hints],
            ])}
            {renderHintGroup('Segmentation / summary / RAG eval gates', [
              ['Semantic chunk boundary maps', patternPackPayload?.semantic_chunk_boundary_map_hints],
              ['Chapter summary anchor gates', patternPackPayload?.chapter_summary_anchor_gate_hints],
              ['Topic drift maps', patternPackPayload?.topic_drift_map_hints],
              ['Context faithfulness eval gates', patternPackPayload?.context_faithfulness_eval_gate_hints],
              ['Retrieval trace observability gates', patternPackPayload?.retrieval_trace_observability_gate_hints],
              ['Prompt regression eval suites', patternPackPayload?.prompt_regression_eval_suite_hints],
            ])}
            {renderHintGroup('Copy similarity / near-duplicate gates', [
              ['Source text fingerprint gates', patternPackPayload?.source_text_fingerprint_gate_hints],
              ['Fuzzy phrase similarity gates', patternPackPayload?.fuzzy_phrase_similarity_gate_hints],
              ['Diff-span copy review gates', patternPackPayload?.diff_span_copy_review_hints],
              ['MinHash / LSH near-duplicate gates', patternPackPayload?.minhash_lsh_near_duplicate_gate_hints],
              ['SimHash / Hamming similarity gates', patternPackPayload?.simhash_hamming_similarity_gate_hints],
              ['Semantic duplicate cluster gates', patternPackPayload?.semantic_duplicate_cluster_gate_hints],
              ['Embedding similarity independence gates', patternPackPayload?.embedding_similarity_independence_gate_hints],
            ])}
            {renderHintGroup('Stylometry / style overfit gates', [
              ['Style-axis diversity fingerprint gates', patternPackPayload?.style_axis_diversity_fingerprint_hints],
              ['Stylometric author fingerprint gates', patternPackPayload?.stylometric_author_fingerprint_gate_hints],
              ['Function-word / syntax style gates', patternPackPayload?.function_word_syntax_style_gate_hints],
              ['Authorship attribution similarity gates', patternPackPayload?.authorship_attribution_similarity_gate_hints],
              ['Style-overfit regression gates', patternPackPayload?.style_overfit_regression_gate_hints],
              ['Paraphrase independence review gates', patternPackPayload?.paraphrase_independence_review_gate_hints],
              ['AI-prose fingerprint cluster gates', patternPackPayload?.ai_prose_fingerprint_cluster_gate_hints],
            ])}
            {renderHintGroup('Trope / genre independence gates', [
              ['Trope inventory similarity gates', patternPackPayload?.trope_inventory_similarity_gate_hints],
              ['Trope graph expectation map gates', patternPackPayload?.trope_graph_expectation_map_hints],
              ['Trope density novelty-budget gates', patternPackPayload?.trope_density_novelty_budget_hints],
              ['Trope source boundary review gates', patternPackPayload?.trope_source_boundary_review_hints],
            ])}
            {renderHintGroup('Reader feedback / market positioning gates', [
              ['Reader retention review gates', patternPackPayload?.reader_retention_review_gate_hints],
              ['Serial reader-reward contract gates', patternPackPayload?.serial_reader_reward_contract_gate_hints],
              ['Reader rating signal model gates', patternPackPayload?.reader_rating_signal_model_hints],
              ['Review spoiler / sentiment corpus gates', patternPackPayload?.review_spoiler_sentiment_corpus_hints],
              ['Beta-reader archetype panel gates', patternPackPayload?.beta_reader_archetype_panel_hints],
              ['Comp-title market positioning gates', patternPackPayload?.comp_title_market_positioning_hints],
              ['Local reader-experience editor gates', patternPackPayload?.local_reader_experience_editor_hints],
              ['Manuscript health / AI prep gates', patternPackPayload?.manuscript_health_ai_prep_gate_hints],
              ['Chapter type / anti-statistical-center gates', patternPackPayload?.anti_statistical_center_chapter_type_gate_hints],
            ])}
            {renderHintGroup('Prose lint / grammar copyedit gates', [
              ['Prose lint style rule gates', patternPackPayload?.prose_lint_style_rule_gate_hints],
              ['Grammar spelling copyedit gates', patternPackPayload?.grammar_spelling_copyedit_gate_hints],
              ['Copyedit diagnostic triage queue gates', patternPackPayload?.copyedit_diagnostic_triage_queue_hints],
            ])}
            {renderHintGroup('Reader reward / tri-modal audit gates', [
              ['Reader reward channel gates', patternPackPayload?.reader_reward_channel_gate_hints],
              ['Tri-modal workflow validation gates', patternPackPayload?.tri_modal_workflow_validation_gate_hints],
            ])}
            {renderHintGroup('Scene promise / serial simulation review gates', [
              ['Scene promise mob-review gates', patternPackPayload?.scene_promise_mob_review_gate_hints],
              ['Webnovel genre tracker gates', patternPackPayload?.webnovel_genre_tracker_gate_hints],
              ['Simulation causal-ledger verification gates', patternPackPayload?.simulation_causal_ledger_verification_gate_hints],
              ['Writer Git exploration review gates', patternPackPayload?.writer_git_exploration_review_gate_hints],
            ])}
            {renderHintGroup('Narrative QA / summary / causality gates', [
              ['Narrative QA comprehension gates', patternPackPayload?.narrative_qa_comprehension_gate_hints],
              ['Chapter summary alignment gates', patternPackPayload?.chapter_summary_alignment_gate_hints],
              ['Story question-answer validation gates', patternPackPayload?.story_question_answer_validation_gate_hints],
              ['Causal why-explanation gates', patternPackPayload?.causal_why_explanation_gate_hints],
              ['Story commonsense consistency gates', patternPackPayload?.story_commonsense_consistency_gate_hints],
              ['Query-focused long-summary gates', patternPackPayload?.query_focused_long_summary_gate_hints],
            ])}
            {renderHintGroup('Rights / corpus admission gates', [
              ['Source license detection gates', patternPackPayload?.source_license_detection_gate_hints],
              ['SPDX / REUSE compliance gates', patternPackPayload?.spdx_reuse_compliance_gate_hints],
              ['Public-domain corpus boundaries', patternPackPayload?.public_domain_corpus_boundary_hints],
              ['Attribution / derivative-work gates', patternPackPayload?.attribution_derivative_work_gate_hints],
            ])}
            {renderHintGroup('Entity redaction / leakage gates', [
              ['Source entity redaction gates', patternPackPayload?.source_entity_redaction_gate_hints],
              ['Custom fiction entity label inventories', patternPackPayload?.custom_entity_label_inventory_hints],
              ['Placeholder alias consistency maps', patternPackPayload?.placeholder_alias_consistency_map_hints],
              ['Proper-noun leakage reviews', patternPackPayload?.proper_noun_leakage_review_hints],
            ])}
            {renderHintGroup('Source import / chapter extraction gates', [
              ['Source format import manifests', patternPackPayload?.source_format_import_manifest_hints],
              ['PDF layout text extraction gates', patternPackPayload?.pdf_layout_text_extraction_gate_hints],
              ['OCR scanned-page import gates', patternPackPayload?.ocr_scanned_page_import_gate_hints],
              ['Document partition chapter detection gates', patternPackPayload?.document_partition_chapter_detection_gate_hints],
              ['Import provenance checksum gates', patternPackPayload?.import_provenance_checksum_gate_hints],
            ])}
            {renderHintGroup('EPUB structure / publication QA gates', [
              ['EPUB structure validation gates', patternPackPayload?.epub_structure_validation_gate_hints],
              ['Ebook accessibility audit gates', patternPackPayload?.ebook_accessibility_audit_gate_hints],
              ['Front/back matter metadata gates', patternPackPayload?.front_back_matter_metadata_gate_hints],
              ['TOC navigation consistency gates', patternPackPayload?.toc_navigation_consistency_gate_hints],
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
