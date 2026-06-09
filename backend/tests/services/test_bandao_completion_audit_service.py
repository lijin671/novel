from __future__ import annotations

from pathlib import Path

from app.services.bandao_completion_audit_service import audit_bandao_full_completion

ARTIFACT_DIR = Path("tmp/book-remix-test-ban-dao-20260530")


def test_audit_bandao_full_completion_rejects_sample_pack_as_incomplete():
    sample_dir = ARTIFACT_DIR / "sample_continuation_pack"

    audit = audit_bandao_full_completion(
        continuation_dir=sample_dir,
        artifact_dir=ARTIFACT_DIR,
    )

    assert audit["completed"] is False
    assert audit["target_total_chapters"] == 1000
    assert audit["required_continuation_chapters"] == 800
    assert audit["chapter_files_found"] == 5
    assert audit["chapters_meeting_word_count"] == 0
    assert audit["missing_chapter_count"] == 795
    assert audit["short_chapter_count"] == 5
    assert audit["sample_pack_detected"] is True
    assert "missing_chapters" in audit["reasons"]
    assert "short_chapters" in audit["reasons"]
    assert "sample_pack_not_full_text" in audit["reasons"]


def test_audit_bandao_full_completion_accepts_synthetic_full_pack(tmp_path):
    full_dir = tmp_path / "full"
    full_dir.mkdir()
    body = "杨翠继续按现实时间线推进 solo 工作，不加入 IVE 或 LE SSERAFIM 固定阵容。" * 360
    for chapter_number in range(201, 1001):
        (full_dir / f"chapter_{chapter_number:04d}.txt").write_text(
            f"第{chapter_number}章 测试完整章\n\n{body}",
            encoding="utf-8",
        )

    audit = audit_bandao_full_completion(
        continuation_dir=full_dir,
        artifact_dir=ARTIFACT_DIR,
    )

    assert audit["completed"] is True
    assert audit["chapter_files_found"] == 800
    assert audit["chapters_meeting_word_count"] == 800
    assert audit["missing_chapter_count"] == 0
    assert audit["short_chapter_count"] == 0
    assert audit["sample_pack_detected"] is False
    assert audit["reasons"] == []
