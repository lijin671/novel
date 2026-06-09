from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from app.services.original_novel_full_pack_generation_service import (
    _build_original_novel_ai_prompt,
    audit_original_novel_pack,
    build_original_chapter_plan,
    generate_original_novel_full_pack,
    generate_original_novel_full_pack_with_ai,
    merge_original_chapters_to_single_txt,
)

ARTIFACT_DIR = Path("tmp/bandao-original-rainseason-20260601")


def _writer(chapter_number: int, plan: dict, target_word_count: int) -> str:
    return (
        f"第{chapter_number}章 测试正文\n\n"
        + f"林知夏 Rina 韩书允 Aurora*One {plan['stage']} {plan['time_window']} "
        + ("练习室、录音室和雨声把事业线与情感线接在一起。" * 80)
    )


def test_build_original_chapter_plan_reads_rainseason_outline_and_bible():
    plan = build_original_chapter_plan(1, ARTIFACT_DIR)

    assert plan["title"] == "第1章 首尔的雨没有名字"
    assert plan["project_title"] == "半岛：雨季未命名"
    assert plan["protagonist"]["name_cn"] == "林知夏"
    assert plan["stage"] == "雨季入场"
    assert "真实艺人" in " ".join(plan["copyright_boundary"]["blocked"])


def test_build_original_chapter_plan_uses_optional_title_override_map(tmp_path):
    artifact_dir = tmp_path / "artifact"
    artifact_dir.mkdir()
    shutil.copy2(ARTIFACT_DIR / "rainseason_bible.json", artifact_dir / "rainseason_bible.json")
    shutil.copy2(ARTIFACT_DIR / "outline_001_1000.json", artifact_dir / "outline_001_1000.json")
    (artifact_dir / "chapter_title_overrides_001_1000.json").write_text(
        json.dumps({"titles": {"2": "第2章 独立测试标题"}}, ensure_ascii=False),
        encoding="utf-8",
    )

    plan = build_original_chapter_plan(2, artifact_dir)

    assert plan["title"] == "第2章 独立测试标题"


def test_build_original_novel_ai_prompt_uses_original_bible_not_bandao_specific_names():
    plan = build_original_chapter_plan(2, ARTIFACT_DIR)

    prompt = _build_original_novel_ai_prompt(
        chapter_number=2,
        plan=plan,
        target_word_count=10000,
        previous_chapter_bridge="第1章结尾：林知夏把雨声写进明天。",
    )

    assert "《半岛：雨季未命名》" in prompt
    assert "林知夏 / Rina" in prompt
    assert "韩书允" in prompt
    assert "只吸收类型结构" in prompt
    assert "第1章结尾：林知夏把雨声写进明天。" in prompt
    assert "杨翠" not in prompt
    assert "Rene" not in prompt


def test_generate_original_novel_full_pack_writes_manifest_and_audit(tmp_path):
    output_dir = tmp_path / "pack"

    result = generate_original_novel_full_pack(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        writer=_writer,
        chapter_numbers=[1, 2],
        target_word_count=300,
        audit_after=True,
    )

    assert result["generated_chapter_count"] == 2
    assert result["failed_chapter_count"] == 0
    assert result["audit"]["passed"] is True
    assert result["manifest_path"].exists()
    assert (output_dir / "chapter_0001.txt").exists()
    assert (output_dir / "chapter_0002.txt").exists()

    manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
    assert manifest["type"] == "original_novel_full_pack"
    assert manifest["project_title"] == "半岛：雨季未命名"
    assert manifest["start_chapter_number"] == 1
    assert manifest["end_chapter_number"] == 1000


def test_audit_original_novel_pack_rejects_forbidden_bandao_alias(tmp_path):
    output_dir = tmp_path / "bad-pack"
    output_dir.mkdir()
    (output_dir / "chapter_0001.txt").write_text(
        "第1章 坏章\n\n" + ("杨翠 Rene 公开恋情 " * 120),
        encoding="utf-8",
    )

    report = audit_original_novel_pack(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        start_chapter=1,
        end_chapter=1,
        required_word_count=100,
    )

    assert report["passed"] is False
    assert report["failed_chapter_count"] == 1
    failed = report["failed_chapters_preview"][0]
    assert "forbidden_terms" in failed["reasons"]
    assert "missing_required_terms" in failed["reasons"]


def test_merge_original_chapters_normalizes_headings_and_requires_complete_range(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "chapter_0001.txt").write_text("正文一", encoding="utf-8")
    (output_dir / "chapter_0002.txt").write_text("# 第2章 旧标题\n\n正文二", encoding="utf-8")
    merged = tmp_path / "merged.txt"

    result = merge_original_chapters_to_single_txt(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        merged_path=merged,
        start_chapter=1,
        end_chapter=2,
        normalize_headings=True,
    )

    text = merged.read_text(encoding="utf-8")
    assert result["chapter_count"] == 2
    assert text.startswith("第1章 首尔的雨没有名字\n\n正文一")
    assert "# 第2章" not in text
    assert "第2章 雨季入场：第一次试音里的未读消息与曝光风险——综艺录制后，第一次争执" in text


@pytest.mark.asyncio
async def test_generate_original_novel_full_pack_with_ai_passes_previous_bridge(tmp_path):
    output_dir = tmp_path / "ai-pack"

    class FakeAIService:
        def __init__(self):
            self.calls = []

        async def generate_text(self, **kwargs):
            self.calls.append(kwargs)
            chapter = len(self.calls)
            return {
                "content": f"第{chapter}章 正文\n\n林知夏 Rina 韩书允 Aurora*One "
                + ("雨声、练习室和录音室继续推进。" * 50)
            }

    ai_service = FakeAIService()

    result = await generate_original_novel_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[1, 2],
        target_word_count=200,
        audit_after=False,
    )

    assert result["generated_chapter_count"] == 2
    assert len(ai_service.calls) == 2
    assert "上一章生成正文片段" in ai_service.calls[1]["prompt"]
    assert "林知夏 Rina 韩书允" in ai_service.calls[1]["prompt"]
