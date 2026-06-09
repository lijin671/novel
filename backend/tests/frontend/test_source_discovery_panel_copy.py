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
    ):
        assert field in types_text
        assert field in panel_text

    assert "Inspired mapping targets" in panel_text
    assert "Inspired copy-risk hints" in panel_text
    assert "Lorebook context hints" in panel_text
    assert "Memory snapshot versioning hints" in panel_text


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
