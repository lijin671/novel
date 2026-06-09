from __future__ import annotations

import json
from pathlib import Path

from app.services.bandao_sample_generation_service import (
    build_bandao_sample_chapter_text,
    build_bandao_sample_continuation_pack,
    validate_bandao_sample_continuation_pack,
)

ARTIFACT_DIR = Path("tmp/book-remix-test-ban-dao-20260530")


def test_build_bandao_sample_chapter_text_generates_checkable_201_sample():
    sample = build_bandao_sample_chapter_text(201, artifact_dir=ARTIFACT_DIR, target_word_count=1200)

    assert sample.startswith("第201章 沉默的清晨")
    assert "杨翠" in sample
    assert "张元英" in sample
    assert "崔叡娜" in sample
    assert "金珉周" in sample
    assert "不公开恋情" in sample
    assert "楼梯间" in sample
    assert "2021-04-29" not in sample
    assert len(sample) >= 1200


def test_build_bandao_sample_chapter_text_projects_late_reality_constraints():
    sample = build_bandao_sample_chapter_text(1000, artifact_dir=ARTIFACT_DIR, target_word_count=1200)

    assert sample.startswith("第1000章")
    assert "2021-04-29" in sample
    assert "IVE" in sample
    assert "LE SSERAFIM" in sample
    assert "不加入 IVE 或 LE SSERAFIM 固定阵容" in sample
    assert "solo" in sample.lower()
    assert len(sample) >= 1200


def test_build_bandao_sample_continuation_pack_writes_samples_and_validation_report(tmp_path):
    output_dir = tmp_path / "bandao-samples"

    pack = build_bandao_sample_continuation_pack(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_numbers=[201, 231, 381, 761, 1000],
        target_word_count=1200,
    )
    validation = validate_bandao_sample_continuation_pack(pack["manifest_path"])

    assert pack["chapter_count"] == 5
    assert pack["contains_full_800_chapter_text"] is False
    assert pack["target_total_chapters"] == 1000
    assert pack["sample_chapters"] == [201, 231, 381, 761, 1000]
    assert validation["passed"] is True
    assert validation["target_total_chapters"] == 1000
    assert validation["sample_chapter_count"] == 5
    assert validation["min_word_count"] >= 1200
    assert validation["contains_full_800_chapter_text"] is False

    manifest = json.loads(pack["manifest_path"].read_text(encoding="utf-8"))
    sample_201_path = Path(manifest["samples"][0]["path"])
    assert sample_201_path.exists()
    assert "第200章" in sample_201_path.read_text(encoding="utf-8")

    report_path = Path(validation["report_path"])
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["chapters"]["201"]["required_terms_present"] is True
