from __future__ import annotations

from pathlib import Path


def test_book_remix_preview_surfaces_deconstruction_pack():
    repo_root = Path(__file__).resolve().parents[3]
    page_text = (repo_root / "frontend" / "src" / "pages" / "BookRemix.tsx").read_text(encoding="utf-8")
    type_text = (repo_root / "frontend" / "src" / "types" / "bookRemix.ts").read_text(encoding="utf-8")

    assert "deconstruction_pack" in type_text
    assert "BookRemixDeconstructionPack" in type_text
    assert "deconstruction_pack" in page_text
    assert "可审查拆书包" in page_text
    assert "same_type_boundaries" in page_text
    assert "revision_gates" in page_text
    assert "reader_pull" in page_text
    assert "scene_beat_sheet" in page_text
    assert "reader_pull_checklist" in page_text
    assert "hook_payoff_matrix" in page_text
    assert "progress_report_contract" in page_text
    assert "main_obstacle" in page_text
    assert "required_reveal_or_payoff" in page_text
    assert "scene_beat_sheet: Array<Record<string, unknown>>" in type_text
    assert "reader_pull_checklist: string[]" in type_text
    assert "hook_payoff_matrix: Record<string, unknown>" in type_text
    assert "progress_report_contract: Record<string, unknown>" in type_text
