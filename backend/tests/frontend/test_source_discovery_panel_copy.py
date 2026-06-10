import json
import re
from pathlib import Path


def test_source_discovery_panel_surfaces_inspired_pattern_pack_fields():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    for field in (
        "inspired_mapping_targets",
        "inspired_prompt_hints",
        "inspired_transformation_hints",
        "inspired_copy_risk_hints",
        "lorebook_context_hints",
        "author_note_layer_hints",
        "world_state_tracking_hints",
        "memory_snapshot_versioning_hints",
        "quality_score_loop_hints",
        "voice_fingerprint_hints",
        "anti_slop_audit_hints",
        "bookrun_audit_trail_gate_hints",
        "provider_budget_smoke_gate_hints",
        "sidecar_memory_profile_boundary_hints",
        "outline_checkpoint_milestone_gate_hints",
        "language_localization_style_profile_gate_hints",
        "progressive_disclosure_skill_protocol_gate_hints",
        "anti_slop_rulepack_triage_gate_hints",
        "user_modifier_project_blueprint_gate_hints",
        "portable_canon_skill_runtime_gate_hints",
        "staged_outline_chunk_window_gate_hints",
        "wiki_canon_graph_lint_gate_hints",
        "plan_draft_log_verify_loop_gate_hints",
        "mcp_scene_index_revision_boundary_hints",
        "verbalized_sampling_diversity_wiki_gate_hints",
        "agentic_editorial_pipeline_gate_hints",
        "craft_role_pipeline_hints",
        "branching_choice_graph_hints",
        "choice_stats_consequence_gate_hints",
        "delivery_manuscript_assembly_hints",
        "export_format_fidelity_audit_hints",
        "character_dialogue_persona_memory_hints",
        "anti_repetition_prompt_rules_hints",
        "temporal_canon_context_graph_hints",
        "character_interaction_network_gate_hints",
        "plotline_thread_tracking_hints",
        "rolling_summary_context_trim_hints",
        "causal_dramatica_agent_pipeline_hints",
        "capture_distillation_production_gate_hints",
        "skill_orchestrated_chinese_novel_workflow_hints",
        "langgraph_story_state_machine_hints",
        "story_daemon_evolution_loop_hints",
        "local_rag_writing_ide_gate_hints",
        "canon_drift_continuity_qa_gate_hints",
        "patch_replay_manuscript_state_gate_hints",
        "microkernel_skill_plugin_isolation_gate_hints",
        "interactive_reader_writer_loop_gate_hints",
        "abstract_style_learning_skill_gate_hints",
        "impromptu_thread_pool_chapter_gate_hints",
        "offline_inspiration_bank_style_gate_hints",
        "atelier_phase_pipeline_gate_hints",
    ):
        assert field in types_text
        assert field in panel_text

    assert "Inspired mapping targets" in panel_text
    assert "Inspired copy-risk hints" in panel_text
    assert "Lorebook context hints" in panel_text
    assert "Memory snapshot versioning hints" in panel_text
    assert "BookRun / skill protocol gates" in panel_text
    assert "Project workbench / memory diversity gates" in panel_text
    assert "Provider budget smoke gates" in panel_text
    assert "Wiki canon graph lint gates" in panel_text
    assert "Authorial agents / interactive delivery gates" in panel_text
    assert "Agentic editorial pipeline gates" in panel_text
    assert "Branching choice graph gates" in panel_text
    assert "Export format fidelity audit gates" in panel_text
    assert "Voice / timeline continuity gates" in panel_text
    assert "Character dialogue persona memory gates" in panel_text
    assert "Anti-repetition prompt rule gates" in panel_text
    assert "Temporal canon context graph gates" in panel_text
    assert "Causal state-machine / skill workflow gates" in panel_text
    assert "Causal Dramatica agent pipeline gates" in panel_text
    assert "Capture distillation production gates" in panel_text
    assert "Skill-orchestrated Chinese novel workflow gates" in panel_text
    assert "LangGraph story state machine gates" in panel_text
    assert "Story daemon evolution loop gates" in panel_text
    assert "Local RAG / canon QA / patch replay gates" in panel_text
    assert "Local RAG writing IDE gates" in panel_text
    assert "Canon drift continuity QA gates" in panel_text
    assert "Patch replay manuscript state gates" in panel_text
    assert "Microkernel skill plugin isolation gates" in panel_text
    assert "Interactive reader-writer loop gates" in panel_text
    assert "Abstract style learning skill gates" in panel_text
    assert "Impromptu / offline / atelier gates" in panel_text
    assert "Impromptu thread-pool chapter gates" in panel_text
    assert "Offline inspiration-bank style gates" in panel_text
    assert "Atelier phase pipeline gates" in panel_text


def test_source_discovery_panel_default_seeds_include_context_memory_projects():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    panel_text = panel.read_text(encoding="utf-8")

    for repo in (
        "KoboldAI/KoboldAI-Client",
        "SillyTavern/SillyTavern",
        "envy-ai/ai_rpg",
        "matrixorigin/Memoria",
        "mrigankad/Novel-OS",
        "aikohanasaki/SillyTavern-MemoryBooks",
        "bal-spec/sillytavern-character-memory",
    ):
        assert repo in panel_text


def test_source_discovery_panel_default_seeds_include_recent_bookrun_and_workbench_sources():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    panel_text = panel.read_text(encoding="utf-8")

    for repo in (
        "XZZKANY/StoryForge",
        "spiritLHLS/novelbuilder",
        "qiuxinyuan321/novel-writer-master",
        "Byk3y/no-slop",
        "nntrivi2001/wordsmith",
        "zy-zmc/tianming-skill",
        "para-droid-ai/NovelizeAI",
        "Moosphan/novel-orchestrator",
        "kirinonakar/Novelgen",
        "abrahamp47/storyforge-wiki",
        "third-order-labs/longform-plugin",
        "hannasdev/mcp-writing",
        "xbraindance/Creative-writing-skill",
        "tiny-flowlab/novel-studio-copilot-cli",
        "guerra2fernando/libriscribe",
        "muckelverk/pulpgen",
        "bhed/sentiers-open-source",
        "rhavekost/author-toolkit",
        "mike-cramblett/novel-novel-generator",
        "denmurray10/Story-Timeline-Builder",
        "jwynia/agent-skills",
        "ydsgangge-ux/dramatica-flow",
        "mmunro3318/story-foundry",
        "Shine8592/novel-writer-skills",
        "modoojunko/awesome-novel-skill",
        "langchain-ai/story-writing",
        "EdwardAThomson/StoryDaemon",
        "datacrystals/AIStoryWriter",
        "sadasdfsaf/canonkit",
        "heider-x/vela",
        "pulpgen-dev/pulpgen",
        "jim60105/HeartReverie",
        "wzxsph/Novel-Claude",
        "liaoma1993/aiAIfiction",
        "vishnu0120754/ReNovel-AI",
        "worldwonderer/zenstory",
        "tuxiangxianzhe/NovelWriter_public",
        "MA-Bihani/Novelia_public",
        "huodebing-alt/Claude-Code-Novel-Agents",
    ):
        assert repo in panel_text


def test_source_discovery_panel_has_dynamic_fallback_for_unpinned_hint_groups():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    pattern_pack = repo_root / "backend" / "app" / "references" / "novel-source-pattern-pack-2026-06-10.json"

    panel_text = panel.read_text(encoding="utf-8")
    pack = json.loads(pattern_pack.read_text(encoding="utf-8"))
    explicitly_rendered_fields = set(re.findall(r"patternPackPayload\?\.([a-zA-Z0-9_]+)", panel_text))
    dynamic_hint_fields = [
        key
        for key, value in pack.items()
        if key.endswith("_hints")
        and isinstance(value, list)
        and value
        and key not in explicitly_rendered_fields
    ]

    assert len(dynamic_hint_fields) > 100
    assert "Additional source-discovered gates" in panel_text
    assert "collectAdditionalHintBlocks" in panel_text
    assert "key.endsWith('_hints')" in panel_text
    assert "!PINNED_HINT_KEYS.has(key)" in panel_text


def test_source_discovery_panel_surfaces_workflow_pattern_evidence():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    panel_text = panel.read_text(encoding="utf-8")

    assert "Workflow pattern evidence" in panel_text
    assert "collectWorkflowPatternEvidence" in panel_text
    assert "renderWorkflowPatternEvidence" in panel_text
    assert "WORKFLOW_PATTERN_EVIDENCE_LIMIT" in panel_text
    assert "WORKFLOW_PATTERN_SOURCE_LIMIT" in panel_text
    assert "pattern.top_source_url" in panel_text
    assert "pattern.sources" in panel_text
    assert "source.posture" in panel_text
    assert "pattern-only 静态吸收" in panel_text
    assert "不 clone、不安装、不执行" in panel_text
