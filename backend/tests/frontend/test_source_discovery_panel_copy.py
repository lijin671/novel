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
