from __future__ import annotations

import pytest

from backend.scripts import generate_original_novel_full_pack as script


def test_parse_chapter_numbers_uses_inclusive_range(tmp_path):
    args = script.parse_args([
        "--output-dir", str(tmp_path),
        "--start-chapter", "1",
        "--end-chapter", "3",
    ])

    assert script.chapter_numbers_from_args(args) == [1, 2, 3]


def test_dry_run_reports_original_scope(tmp_path):
    args = script.parse_args([
        "--output-dir", str(tmp_path),
        "--start-chapter", "1",
        "--end-chapter", "2",
        "--target-word-count", "10000",
        "--dry-run",
    ])

    summary = script.build_dry_run_summary(args)

    assert summary["dry_run"] is True
    assert summary["chapter_count"] == 2
    assert summary["estimated_total_words"] == 20000
    assert "bandao-original-rainseason-20260601" in summary["artifact_dir"]


@pytest.mark.asyncio
async def test_main_synthetic_generates_without_ai_service(tmp_path, monkeypatch):
    async def should_not_get_engine(user_id):
        raise AssertionError(f"synthetic should not open database for {user_id}")

    monkeypatch.setattr(script, "get_engine", should_not_get_engine)
    args = script.parse_args([
        "--output-dir", str(tmp_path),
        "--start-chapter", "1",
        "--end-chapter", "2",
        "--target-word-count", "300",
        "--synthetic",
    ])

    result = await script.main(args)

    assert result["generated_chapter_count"] == 2
    assert result["failed_chapter_count"] == 0
    assert (tmp_path / "chapter_0001.txt").exists()
    assert result["audit"]["passed"] is True


@pytest.mark.asyncio
async def test_main_merge_txt_only_does_not_build_ai_service(tmp_path, monkeypatch):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "chapter_0001.txt").write_text("正文一", encoding="utf-8")
    merged_path = tmp_path / "merged.txt"

    async def should_not_get_engine(user_id):
        raise AssertionError(f"merge-txt should not open database for {user_id}")

    monkeypatch.setattr(script, "get_engine", should_not_get_engine)
    args = script.parse_args([
        "--output-dir", str(output_dir),
        "--start-chapter", "1",
        "--end-chapter", "1",
        "--merge-txt",
        "--merged-path", str(merged_path),
        "--normalize-headings",
    ])

    result = await script.main(args)

    assert result["merged_txt"]["path"] == str(merged_path)
    assert merged_path.exists()
    assert merged_path.read_text(encoding="utf-8").startswith("第1章 首尔的雨没有名字")
