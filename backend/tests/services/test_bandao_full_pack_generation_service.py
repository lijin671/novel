from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.bandao_full_pack_generation_service import (
    _build_bandao_ai_prompt,
    build_bandao_full_pack_ai_run_command,
    generate_bandao_ai_chapter_text,
    generate_bandao_full_pack,
    generate_bandao_full_pack_async,
    generate_bandao_full_pack_with_ai,
)

ARTIFACT_DIR = Path("tmp/book-remix-test-ban-dao-20260530")


def _writer(chapter_number: int, plan: dict, target_word_count: int) -> str:
    del plan
    return f"第{chapter_number}章 测试完整章\n\n" + (
        "杨翠继续按现实时间线推进 solo 工作，不加入 IVE 或 LE SSERAFIM 固定阵容。" * 360
    )


def _short_writer(chapter_number: int, plan: dict, target_word_count: int) -> str:
    del plan, target_word_count
    return f"第{chapter_number}章 短章\n\n杨翠继续前进。"


def test_generate_bandao_full_pack_writes_range_manifest_and_completion_audit(tmp_path):
    output_dir = tmp_path / "full-pack"

    result = generate_bandao_full_pack(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        writer=_writer,
        chapter_numbers=range(201, 1001),
        target_word_count=10000,
    )

    assert result["generated_chapter_count"] == 800
    assert result["skipped_existing_chapter_count"] == 0
    assert result["audit"]["completed"] is True
    assert result["manifest_path"].exists()
    assert (output_dir / "chapter_0201.txt").exists()
    assert (output_dir / "chapter_1000.txt").exists()

    manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
    assert manifest["contains_full_800_chapter_text"] is True
    assert manifest["chapter_count"] == 800
    assert manifest["target_word_count"] == 10000
    assert manifest["chapters"][0]["chapter_number"] == 201
    assert manifest["chapters"][-1]["chapter_number"] == 1000


def test_generate_bandao_full_pack_can_resume_without_overwriting_existing(tmp_path):
    output_dir = tmp_path / "resume-pack"
    output_dir.mkdir()
    existing = output_dir / "chapter_0201.txt"
    existing.write_text("第201章 已有正文\n\n" + ("杨翠继续按现实时间线推进 solo 工作。" * 400), encoding="utf-8")

    result = generate_bandao_full_pack(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        writer=_writer,
        chapter_numbers=[201, 202],
        target_word_count=10000,
        overwrite=False,
        audit_after=False,
    )

    assert result["generated_chapter_count"] == 1
    assert result["skipped_existing_chapter_count"] == 1
    assert "已有正文" in existing.read_text(encoding="utf-8")
    assert (output_dir / "chapter_0202.txt").exists()


def test_generate_bandao_full_pack_rejects_short_writer(tmp_path):
    output_dir = tmp_path / "short-pack"

    result = generate_bandao_full_pack(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        writer=_short_writer,
        chapter_numbers=[201],
        target_word_count=10000,
        audit_after=False,
    )

    assert result["generated_chapter_count"] == 0
    assert result["failed_chapter_count"] == 1
    assert result["failed_chapters"][0]["chapter_number"] == 201
    assert result["failed_chapters"][0]["reason"] == "short_generated_text"
    assert not (output_dir / "chapter_0201.txt").exists()


class _FakeAIService:
    def __init__(self, responses: list[str]):
        self.responses = list(responses)
        self.calls: list[dict] = []

    async def generate_text(self, **kwargs):
        self.calls.append(kwargs)
        return {"content": self.responses.pop(0)}


@pytest.mark.asyncio
async def test_generate_bandao_ai_chapter_text_calls_ai_with_plan_constraints():
    plan = {
        "plot_summary": "第201章承接楼梯间余波。",
        "stage_title": "楼梯间余波与日常修罗场",
        "stage_range": "201-230",
        "character_focus": ["杨翠 / Rene", "张元英", "崔叡娜"],
        "reality_timeline_constraints": "2019-04-01：HEART*IZ / Violeta 回归。",
        "guardrails": ["不公开恋情", "不加入 IVE 或 LE SSERAFIM 固定阵容"],
    }
    ai_service = _FakeAIService(["杨翠继续按现实时间线推进 solo 工作。" * 20])

    text = await generate_bandao_ai_chapter_text(
        ai_service=ai_service,
        chapter_number=201,
        plan=plan,
        target_word_count=100,
        previous_chapter_bridge="第200章结尾：崔叡娜翻身背对。",
    )

    assert len(text) >= 100
    assert len(ai_service.calls) == 1
    call = ai_service.calls[0]
    assert call["max_tokens"] == 2000
    assert call["auto_mcp"] is False
    assert "第201章" in call["prompt"]
    assert "第200章结尾：崔叡娜翻身背对。" in call["prompt"]
    assert "不加入 IVE 或 LE SSERAFIM 固定阵容" in call["prompt"]
    assert "2019-04-01" in call["prompt"]


def test_generate_bandao_ai_prompt_marks_reality_dates_as_must_appear():
    plan = {
        "plot_summary": "第231章进入HEART*IZ回归。",
        "stage_title": "日本活动与 HEART*IZ 回归",
        "stage_range": "231-300",
        "character_focus": [
            "杨翠 / Rene",
            "张元英",
            "崔叡娜",
            "金珉周",
        ],
        "reality_timeline_constraints": "2019-04-01：IZ*ONE 发行 HEART*IZ / Violeta。",
        "guardrails": ["不公开恋情"],
    }

    prompt = _build_bandao_ai_prompt(
        chapter_number=231,
        plan=plan,
        target_word_count=10000,
        previous_chapter_bridge="上一章生成正文片段：测试",
    )

    assert "必须自然写入以下现实时间锚点" in prompt
    assert "2019-04-01" in prompt


def test_generate_bandao_ai_prompt_declares_rene_is_protagonist_alias():
    plan = {
        "plot_summary": "第352章推进巡演后台与队内关系。",
        "stage_title": "巡演、KCON 与夏秋单曲",
        "stage_range": "301-380",
        "character_focus": ["杨翠 / Rene", "张元英", "崔叡娜", "金珉周"],
        "reality_timeline_constraints": "2019-09-25：IZ*ONE 发行日本单曲 Vampire。",
        "guardrails": ["不公开恋情"],
    }

    prompt = _build_bandao_ai_prompt(
        chapter_number=352,
        plan=plan,
        target_word_count=10000,
        previous_chapter_bridge="上一章生成正文片段：测试",
    )

    assert "Rene 是杨翠的英文名" in prompt
    assert "不要把 Rene 写成另一个人" in prompt
    assert "禁止出现“公开恋情”或“官宣恋情”这两个词" in prompt


def test_generate_bandao_ai_prompt_declares_fixed_character_names():
    plan = {
        "plot_summary": "第413章推进停摆期宿舍创作。",
        "stage_title": "2019 风波与停摆",
        "stage_range": "381-460",
        "character_focus": ["杨翠 / Rene", "张元英", "崔叡娜", "金珉周", "权恩菲"],
        "reality_timeline_constraints": "2019-11：Produce 系列投票造假争议爆发。",
        "guardrails": ["不公开恋情"],
    }

    prompt = _build_bandao_ai_prompt(
        chapter_number=413,
        plan=plan,
        target_word_count=10000,
        previous_chapter_bridge="上一章生成正文片段：测试",
    )

    assert "固定译名" in prompt
    assert "权恩菲，不写权恩非" in prompt
    assert "崔叡娜，不写崔叡那" in prompt


def test_generate_bandao_ai_prompt_requires_third_person_narration():
    plan = {
        "plot_summary": "第727章推进解散后solo起步。",
        "stage_title": "解散后 solo 起步",
        "stage_range": "651-760",
        "character_focus": ["杨翠 / Rene", "张元英", "崔叡娜", "金珉周"],
        "reality_timeline_constraints": "2021-04-29：IZ*ONE 组合活动正式结束。",
        "guardrails": ["不公开恋情"],
    }

    prompt = _build_bandao_ai_prompt(
        chapter_number=727,
        plan=plan,
        target_word_count=10000,
        previous_chapter_bridge="上一章生成正文片段：测试",
    )

    assert "必须使用第三人称叙述" in prompt
    assert "不要用第一人称“我”作为叙述视角" in prompt
    assert "主角称为“杨翠”或“Rene”" in prompt


@pytest.mark.asyncio
async def test_generate_bandao_full_pack_async_records_writer_exception_without_stopping(tmp_path):
    output_dir = tmp_path / "async-pack"

    async def writer(chapter_number: int, plan: dict, target_word_count: int) -> str:
        del plan
        if chapter_number == 201:
            raise RuntimeError("AI provider unavailable")
        return f"第{chapter_number}章 正文\n\n" + ("杨翠继续按现实时间线推进 solo 工作。" * 8)

    result = await generate_bandao_full_pack_async(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        writer=writer,
        chapter_numbers=[201, 202],
        target_word_count=100,
        audit_after=False,
    )

    assert result["generated_chapter_count"] == 1
    assert result["failed_chapter_count"] == 1
    assert result["failed_chapters"][0]["chapter_number"] == 201
    assert result["failed_chapters"][0]["reason"] == "writer_error"
    assert not (output_dir / "chapter_0201.txt").exists()
    assert (output_dir / "chapter_0202.txt").exists()


@pytest.mark.asyncio
async def test_generate_bandao_full_pack_with_ai_passes_previous_chapter_bridge(tmp_path):
    output_dir = tmp_path / "ai-pack"
    first = "杨翠在练习室里把楼梯间的事压回心底。" + ("张元英安静地跟在她身边。" * 10)
    second = "崔叡娜用玩笑试探杨翠，车窗外的首尔清晨慢慢亮起来。" + ("成员们继续按现实时间线赶行程。" * 10)
    ai_service = _FakeAIService([first, second])

    result = await generate_bandao_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[201, 202],
        target_word_count=100,
        audit_after=False,
    )

    assert result["generated_chapter_count"] == 2
    assert result["failed_chapter_count"] == 0
    assert (output_dir / "chapter_0201.txt").read_text(encoding="utf-8") == first
    assert (output_dir / "chapter_0202.txt").read_text(encoding="utf-8") == second
    assert "上一章生成正文片段" in ai_service.calls[1]["prompt"]
    assert "杨翠在练习室里把楼梯间的事压回心底" in ai_service.calls[1]["prompt"]


@pytest.mark.asyncio
async def test_generate_bandao_full_pack_with_ai_resumes_bridge_from_existing_file(tmp_path):
    output_dir = tmp_path / "resume-ai-pack"
    output_dir.mkdir()
    existing_201 = (
        "\u7b2c201\u7ae0 \u5df2\u6709\u6b63\u6587 \u697c\u68af\u95f4 "
        "\u5f20\u5143\u82f1 \u5d14\u53e1\u5a1c \u91d1\u73c9\u5468 \u6743\u6069\u83f2\n\n"
        + (
            "\u6768\u7fe0\u628a\u697c\u68af\u95f4\u4e4b\u540e\u7684\u5fc3\u4e8b"
            "\u538b\u8fdb\u6e05\u6668\u884c\u7a0b\u3002"
            * 12
        )
    )
    (output_dir / "chapter_0201.txt").write_text(existing_201, encoding="utf-8")
    ai_service = _FakeAIService(["第202章 新正文\n\n" + ("崔叡娜在车里用玩笑试探她。" * 12)])

    result = await generate_bandao_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[201, 202],
        target_word_count=100,
        audit_after=False,
        overwrite=False,
    )

    assert result["generated_chapter_count"] == 1
    assert result["skipped_existing_chapter_count"] == 1
    assert "上一章生成正文片段" in ai_service.calls[0]["prompt"]
    assert "杨翠把楼梯间之后的心事压进清晨行程" in ai_service.calls[0]["prompt"]


@pytest.mark.asyncio
async def test_generate_bandao_full_pack_with_ai_resumes_bridge_from_previous_existing_file(tmp_path):
    output_dir = tmp_path / "resume-from-previous-ai-pack"
    output_dir.mkdir()
    existing_230 = (
        "\u7b2c230\u7ae0 \u5df2\u6709\u6b63\u6587\n\n"
        + (
            "\u6768\u7fe0\u628a\u4e09\u6708\u672b\u7684\u884c\u7a0b"
            "\u548cHEART*IZ\u51c6\u5907\u63a5\u8d77\u6765\u3002"
            * 12
        )
    )
    (output_dir / "chapter_0230.txt").write_text(existing_230, encoding="utf-8")
    ai_service = _FakeAIService(
        [
            "\u7b2c231\u7ae0 \u65b0\u6b63\u6587\n\n"
            + (
                "Violeta\u56de\u5f52\u51c6\u5907"
                "\u8ba9\u6240\u6709\u4eba\u91cd\u65b0\u7d27\u7ef7\u8d77\u6765\u3002"
                * 12
            )
        ]
    )

    result = await generate_bandao_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[231],
        target_word_count=100,
        audit_after=False,
        overwrite=False,
    )

    assert result["generated_chapter_count"] == 1
    assert "\u4e0a\u4e00\u7ae0\u751f\u6210\u6b63\u6587\u7247\u6bb5" in ai_service.calls[0]["prompt"]
    assert (
        "\u6768\u7fe0\u628a\u4e09\u6708\u672b\u7684\u884c\u7a0b\u548cHEART*IZ"
        in ai_service.calls[0]["prompt"]
    )


@pytest.mark.asyncio
async def test_generate_bandao_full_pack_with_ai_regenerates_existing_failed_regression(tmp_path):
    output_dir = tmp_path / "regenerate-failed-regression-pack"
    output_dir.mkdir()
    existing_231 = (
        "第231章 Rene 张元英 崔叡娜 金珉周 HEART*IZ Violeta "
        + ("缺少现实日期。" * 900)
    )
    (output_dir / "chapter_0231.txt").write_text(existing_231, encoding="utf-8")
    regenerated = (
        "第231章 Rene 张元英 崔叡娜 金珉周 2019-04-01 HEART*IZ Violeta "
        + ("补齐现实日期。" * 900)
    )
    ai_service = _FakeAIService([regenerated])

    result = await generate_bandao_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[231],
        target_word_count=1000,
        audit_after=False,
        overwrite=False,
    )

    assert result["generated_chapter_count"] == 1
    assert result["skipped_existing_chapter_count"] == 0
    assert "2019-04-01" in (output_dir / "chapter_0231.txt").read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_generate_bandao_full_pack_with_ai_reports_failed_generated_regression(tmp_path):
    output_dir = tmp_path / "generated-failed-regression-pack"
    generated = "第381章 杨翠 Produce 风波 " + ("练习室里的雨声压住了所有没说出口的话。" * 900)
    ai_service = _FakeAIService([generated])

    result = await generate_bandao_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[381],
        target_word_count=1000,
        audit_after=False,
    )

    assert result["generated_chapter_count"] == 1
    assert result["failed_chapter_count"] == 0
    assert result["regression_audit"]["passed"] is False
    assert result["regression_audit"]["failed_chapter_count"] == 1
    assert result["regression_audit"]["failed_chapters_preview"][0]["chapter_number"] == 381


@pytest.mark.asyncio
async def test_generate_bandao_full_pack_with_ai_continues_until_target_word_count(tmp_path):
    output_dir = tmp_path / "continued-ai-pack"
    ai_service = _FakeAIService(
        [
            "第201章 正文开段\n\n" + ("杨翠在宿舍里保持沉默。" * 5),
            "她把练习室、车内和节目补拍的细节一层层接上。" * 8,
            "张元英、崔叡娜和金珉周都被行程推着继续往前走。" * 8,
        ]
    )

    result = await generate_bandao_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[201],
        target_word_count=420,
        audit_after=False,
    )

    saved_text = (output_dir / "chapter_0201.txt").read_text(encoding="utf-8")
    assert result["generated_chapter_count"] == 1
    assert result["failed_chapter_count"] == 0
    assert len(ai_service.calls) == 3
    assert "继续第201章正文" in ai_service.calls[1]["prompt"]
    assert "不要重复已经写过的段落" in ai_service.calls[1]["prompt"]
    assert "练习室、车内和节目补拍" in saved_text
    assert "张元英、崔叡娜和金珉周" in saved_text


@pytest.mark.asyncio
async def test_generate_bandao_full_pack_with_ai_honors_extra_continuation_segments(tmp_path):
    output_dir = tmp_path / "extra-segments-ai-pack"
    ai_service = _FakeAIService(
        [
            "第201章 正文开段\n\n" + ("杨翠在宿舍里保持沉默。" * 5),
            "她把练习室的灯光和崔叡娜的试探继续接上。" * 10,
            "张元英在车窗倒影里收回视线。" * 10,
            "金珉周安静地把所有异常记在心里。" * 10,
            "权恩菲把队伍重新拉回行程。" * 10,
        ]
    )

    result = await generate_bandao_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[201],
        target_word_count=620,
        max_segments_per_chapter=5,
        audit_after=False,
    )

    saved_text = (output_dir / "chapter_0201.txt").read_text(encoding="utf-8")
    assert result["generated_chapter_count"] == 1
    assert result["failed_chapter_count"] == 0
    assert len(ai_service.calls) == 5
    assert "权恩菲把队伍重新拉回行程" in saved_text


@pytest.mark.asyncio
async def test_generate_bandao_full_pack_with_ai_uses_retry_when_segment_call_fails_once(tmp_path):
    output_dir = tmp_path / "retry-ai-pack"

    class FlakyAIService:
        def __init__(self):
            self.calls = []

        async def generate_text(self, **kwargs):
            self.calls.append(kwargs)
            if len(self.calls) == 2:
                raise RuntimeError("temporary provider timeout")
            if len(self.calls) == 1:
                return {"content": "第201章 正文开段\n\n" + ("杨翠在宿舍里保持沉默。" * 5)}
            return {"content": "她把练习室、车内和节目补拍的细节一层层接上。" * 30}

    ai_service = FlakyAIService()

    result = await generate_bandao_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[201],
        target_word_count=420,
        max_segments_per_chapter=4,
        max_attempts_per_segment=2,
        retry_delay_seconds=0,
        audit_after=False,
    )

    saved_text = (output_dir / "chapter_0201.txt").read_text(encoding="utf-8")
    assert result["generated_chapter_count"] == 1
    assert result["failed_chapter_count"] == 0
    assert len(ai_service.calls) == 3
    assert "练习室、车内和节目补拍" in saved_text

@pytest.mark.asyncio
async def test_generate_bandao_full_pack_with_ai_reports_short_after_segment_limit(tmp_path):
    output_dir = tmp_path / "segment-limit-ai-pack"
    ai_service = _FakeAIService(
        [
            "第201章 正文开段\n\n" + ("杨翠在宿舍里保持沉默。" * 2),
            "崔叡娜只是短短试探一句。" * 2,
        ]
    )

    result = await generate_bandao_full_pack_with_ai(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        ai_service=ai_service,
        chapter_numbers=[201],
        target_word_count=620,
        max_segments_per_chapter=2,
        audit_after=False,
    )

    assert result["generated_chapter_count"] == 0
    assert result["failed_chapter_count"] == 1
    assert result["failed_chapters"][0]["reason"] == "short_generated_text"
    assert len(ai_service.calls) == 2
    assert not (output_dir / "chapter_0201.txt").exists()


def test_build_bandao_full_pack_ai_run_command_documents_resumable_entrypoint():
    command = build_bandao_full_pack_ai_run_command(
        user_id="tester",
        output_dir=Path("tmp/book-remix-test-ban-dao-20260530/full_continuation_pack"),
        start_chapter=201,
        end_chapter=1000,
        target_word_count=10000,
        model="gpt-test",
    )

    assert "backend.scripts.generate_bandao_full_pack" in command
    assert "--user-id tester" in command
    assert "--start-chapter 201" in command
    assert "--end-chapter 1000" in command
    assert "--target-word-count 10000" in command
    assert "--model gpt-test" in command
