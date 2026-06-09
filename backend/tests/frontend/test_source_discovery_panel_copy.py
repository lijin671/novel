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
    ):
        assert field in types_text
        assert field in panel_text

    assert "Inspired mapping targets" in panel_text
    assert "Inspired copy-risk hints" in panel_text
