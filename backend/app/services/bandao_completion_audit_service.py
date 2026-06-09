from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.services.bandao_batch_queue_plan import (
    BANDAO_CONTINUATION_COUNT,
    BANDAO_START_CHAPTER,
    BANDAO_TARGET_TOTAL_CHAPTERS,
    BANDAO_TARGET_WORD_COUNT,
)


def _compact_word_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text or ""))


def _chapter_file_candidates(directory: Path, chapter_number: int) -> list[Path]:
    patterns = [
        f"chapter_{chapter_number:04d}.txt",
        f"chapter_{chapter_number}.txt",
        f"chapter_{chapter_number:04d}_sample.txt",
        f"chapter_{chapter_number}_sample.txt",
    ]
    return [directory / pattern for pattern in patterns]


def _find_chapter_file(directory: Path, chapter_number: int) -> Path | None:
    for candidate in _chapter_file_candidates(directory, chapter_number):
        if candidate.exists() and candidate.is_file():
            return candidate
    matches = sorted(directory.glob(f"*{chapter_number}*.txt"))
    return matches[0] if matches else None


def _detect_sample_pack(continuation_dir: Path) -> bool:
    manifest_path = continuation_dir / "sample_manifest.json"
    if not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return True
    if manifest.get("contains_full_800_chapter_text") is False:
        return True
    return str(manifest.get("type") or "").startswith("bandao_sample_")


def audit_bandao_full_completion(
    *,
    continuation_dir: Path,
    artifact_dir: Path,
    required_word_count: int = BANDAO_TARGET_WORD_COUNT,
) -> dict[str, Any]:
    """审计《混在半岛的日子》是否真的完成 201-1000 万字续写。

    只根据当前文件产物做可验证判断。样本文包、占位、短章都不能通过。
    """
    del artifact_dir  # 保留参数用于未来交叉校验源书报告和现实时间线。

    found: dict[int, dict[str, Any]] = {}
    missing: list[int] = []
    short: list[dict[str, Any]] = []

    for chapter_number in range(BANDAO_START_CHAPTER, BANDAO_TARGET_TOTAL_CHAPTERS + 1):
        path = _find_chapter_file(continuation_dir, chapter_number)
        if path is None:
            missing.append(chapter_number)
            continue
        text = path.read_text(encoding="utf-8")
        word_count = _compact_word_count(text)
        entry = {"path": str(path), "word_count": word_count}
        found[chapter_number] = entry
        if word_count < required_word_count:
            short.append({"chapter_number": chapter_number, **entry})

    sample_pack_detected = _detect_sample_pack(continuation_dir)
    reasons: list[str] = []
    if missing:
        reasons.append("missing_chapters")
    if short:
        reasons.append("short_chapters")
    if sample_pack_detected:
        reasons.append("sample_pack_not_full_text")

    completed = not reasons and len(found) == BANDAO_CONTINUATION_COUNT
    report = {
        "completed": completed,
        "continuation_dir": str(continuation_dir),
        "target_total_chapters": BANDAO_TARGET_TOTAL_CHAPTERS,
        "start_chapter_number": BANDAO_START_CHAPTER,
        "end_chapter_number": BANDAO_TARGET_TOTAL_CHAPTERS,
        "required_continuation_chapters": BANDAO_CONTINUATION_COUNT,
        "required_word_count_per_chapter": required_word_count,
        "chapter_files_found": len(found),
        "chapters_meeting_word_count": len(found) - len(short),
        "missing_chapter_count": len(missing),
        "short_chapter_count": len(short),
        "sample_pack_detected": sample_pack_detected,
        "reasons": reasons,
        "missing_chapters_preview": missing[:20],
        "short_chapters_preview": short[:20],
    }

    report_path = continuation_dir / "full_completion_audit_report.json"
    if continuation_dir.exists() and continuation_dir.is_dir():
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        report["report_path"] = str(report_path)
    return report
