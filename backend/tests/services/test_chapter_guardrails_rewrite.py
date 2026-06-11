from __future__ import annotations

import json

import pytest

from app.services.chapter_guardrails import (
    GUARDRAIL_REVIEW_JSON_PREFIX,
    ChapterGuardrails,
    apply_chapter_guardrail_check,
    format_guardrail_history_note,
    _format_forbidden_source_names_for_prompt,
)


class StubAIService:
    def __init__(self):
        self.prompts: list[str] = []

    async def generate_text(self, **kwargs):
        self.prompts.append(kwargs["prompt"])
        return {
            "content": "林把账册扣在桌面上，先回答窗外传来的脚步声。档案员停在门口，低声提醒旧敌已经到了楼下。"
        }


class StillCopyingAIService:
    def __init__(self):
        self.prompts: list[str] = []

    async def generate_text(self, **kwargs):
        self.prompts.append(kwargs["prompt"])
        return {
            "content": "新主角把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"
        }


@pytest.mark.asyncio
async def test_apply_chapter_guardrail_check_rewrites_failed_generation_once():
    ai_service = StubAIService()
    original = "第二十章 账册归来\n接上回，林把账册扣在桌面上。林把账册扣在桌面上。"

    result = await apply_chapter_guardrail_check(
        generated_text=original,
        ai_service=ai_service,
        chapter_number=20,
        chapter_title="账册归来",
        chapter_outline="林带着账册进入档案室，面对旧敌逼近。",
        target_word_count=1200,
        chapter_director_plan="{}",
        previous_chapter_summary="林把账册扣在桌面上，意识到旧敌就在楼下。",
        continuation_point="林把账册扣在桌面上。",
    )

    assert result["content"] != original
    assert result["content"].startswith("林把账册扣在桌面上，先回答")
    assert result["applied"] is True
    assert result["attempts"] == 1
    assert result["initial_result"].passed is False
    assert result["final_result"].passed is True
    assert ai_service.prompts
    assert "待修复违规列表" in ai_service.prompts[0]
    assert "原始正文" in ai_service.prompts[0]


@pytest.mark.asyncio
async def test_apply_chapter_guardrail_check_returns_original_when_passed():
    ai_service = StubAIService()
    original = "林把账册扣在桌面上，先回答窗外传来的脚步声。档案员停在门口，低声提醒旧敌已经到了楼下。"

    result = await apply_chapter_guardrail_check(
        generated_text=original,
        ai_service=ai_service,
        chapter_number=20,
        chapter_title="账册归来",
        chapter_outline="林带着账册进入档案室，面对旧敌逼近。",
        target_word_count=1200,
        chapter_director_plan="{}",
        previous_chapter_summary="林把账册扣在桌面上，意识到旧敌就在楼下。",
        continuation_point="林把账册扣在桌面上。",
    )

    assert result["content"] == original
    assert result["applied"] is False
    assert result["attempts"] == 0
    assert ai_service.prompts == []


@pytest.mark.asyncio
async def test_apply_chapter_guardrail_check_rewrites_when_confirmed_canon_is_repeated():
    ai_service = StubAIService()
    original = "林再次追回账册，旧敌再次败退。林把账册重新交给档案员，像一切刚刚发生。"

    result = await apply_chapter_guardrail_check(
        generated_text=original,
        ai_service=ai_service,
        chapter_number=20,
        chapter_title="档案余波",
        chapter_outline="林在账册已追回后进入档案室，处理旧敌留下的新线索。",
        target_word_count=1200,
        chapter_director_plan="{}",
        previous_chapter_summary="第19章《账册归来》：林已经追回账册，旧敌已经败退。",
        continuation_point="林把账册扣在桌面上，意识到旧敌已经败退。",
        remix_continuation_context=(
            "Done planned beats:\n"
            "- Recover ledger status: done\n"
            "Resolved hooks:\n"
            "- Old rival returns status: resolved\n"
            "Recent chapter change packages:\n"
            "- Chapter 19: 账册归来: 林已经追回账册，旧敌已经败退。"
        ),
    )

    assert result["content"] != original
    assert result["applied"] is True
    assert result["initial_result"].passed is False
    assert any(
        violation.type == "canon_repetition"
        for violation in result["initial_result"].violations
    )
    assert "已确认 Canon" in ai_service.prompts[0]
    assert "Recover ledger" in ai_service.prompts[0]


@pytest.mark.asyncio
async def test_apply_chapter_guardrail_check_injects_source_pattern_pack_into_rewrite_prompt():
    ai_service = StubAIService()
    original = "第二十章 账册归来\n接上回，林把账册扣在桌面上。"

    await apply_chapter_guardrail_check(
        generated_text=original,
        ai_service=ai_service,
        chapter_number=20,
        chapter_title="账册归来",
        chapter_outline="林在账册已追回后进入档案室，处理旧敌留下的新线索。",
        target_word_count=1200,
        previous_chapter_summary="林已经追回账册，旧敌已经败退。",
        continuation_point="林把账册扣在桌面上。",
        remix_continuation_context="Done planned beats:\n- Recover ledger status: done",
        source_pattern_pack={
            "continuation_prompt_hints": ["续写前先读取世界观、时间线、人物卡、组织、情感线。"],
            "style_signature_hints": ["保留原书味道，并把风格签名作为硬约束。"],
            "self_review_policy_hints": ["不限次数自评优化必须有停止条件。"],
            "safety_constraints": ["不克隆、不安装、不执行外部项目。"],
        },
    )

    assert ai_service.prompts
    prompt = ai_service.prompts[0]
    assert "公开来源模式约束" in prompt
    assert "续写前先读取世界观" in prompt
    assert "保留原书味道" in prompt
    assert "不限次数自评优化" in prompt
    assert "不克隆、不安装、不执行外部项目" in prompt


def test_chapter_guardrails_flags_inspired_draft_copying_source_phrase():
    guardrails = ChapterGuardrails()
    source_excerpt = "林寒把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"
    generated = (
        "新主角把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"
        "他没有回头，只等楼下脚步声逼近。"
    )

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is False
    assert any(
        violation.type == "inspired_source_copy"
        for violation in result.violations
    )
    violation = next(
        item for item in result.violations
        if item.type == "inspired_source_copy"
    )
    assert violation.severity == "high"
    assert "同类创作" in violation.description
    assert "源书片段" in violation.description


def test_chapter_guardrails_flags_distinctive_source_substring_copy():
    guardrails = ChapterGuardrails()
    source_excerpt = (
        "林寒把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"
        "沈璃站在门外，没有立刻敲门，只等楼下的脚步声逼近。"
        "青岚会的徽记在玻璃上晃了一下。"
    )
    generated = "新主角没有立刻敲门，只等楼下的脚步声逼近。随后他绕到侧门。"

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is False
    assert any(
        violation.type == "inspired_source_copy"
        for violation in result.violations
    )


def test_chapter_guardrails_flags_obfuscated_forbidden_source_name():
    guardrails = ChapterGuardrails()
    generated = "林 寒站在旧档案室门口，青岚 会的徽记在雨里一闪。"

    result = guardrails.check(
        generated,
        forbidden_characters=["林寒", "青岚会"],
    )

    assert result.passed is False
    violations = [violation for violation in result.violations if violation.type == "forbidden_name"]
    assert {violation.context for violation in violations}
    assert any("林寒" in violation.description for violation in violations)
    assert any("青岚会" in violation.description for violation in violations)


def test_chapter_guardrails_flags_winnowing_style_shingle_overlap():
    guardrails = ChapterGuardrails()
    source_excerpt = (
        "林寒把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"
        "沈璃站在门外，没有立刻敲门，只等楼下的脚步声逼近。"
    )
    generated = (
        "新主角把青铜钥匙按进雨水里，又把钥匙从水痕里抽回。"
        "他沿着楼梯停住，旧档案室的窗户一格格亮起来。"
        "随后有人没有立刻敲门，只等楼下的脚步声逼近。"
    )

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is False
    violation = next(
        item for item in result.violations
        if item.type == "inspired_source_copy"
    )
    assert (
        "fingerprint_overlap" in violation.description
        or "ordered_phrase_overlap" in violation.description
        or "distinctive_substring" in violation.description
    )


def test_chapter_guardrails_flags_simhash_near_duplicate_after_light_reorder():
    guardrails = ChapterGuardrails()
    source_excerpt = (
        "雨声压住了档案室外的脚步，林寒把账册推到灯下，"
        "先看封皮上的裂纹，再看印章边缘的潮痕。"
        "沈璃没有催促，只把门缝留出一线。"
    )
    generated = (
        "雨声压住了旧馆外的脚步，新主角把账册推到灯下，"
        "先看封皮边缘的裂纹，再看印章旁边的潮痕。"
        "助手没有催促，只把门缝留出一线。"
    )

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is False
    violation = next(
        item for item in result.violations
        if item.type == "inspired_source_copy"
    )
    assert (
        "simhash_near_duplicate" in violation.description
        or "fuzzy_window_similarity" in violation.description
        or "fingerprint_overlap" in violation.description
    )


def test_inspired_source_copy_violation_carries_source_fingerprint():
    guardrails = ChapterGuardrails()
    source_excerpt = "AlphaLedgerKey opens the rain archive window while BetaClerk waits downstairs."

    result = guardrails.check(
        "NewHero uses the AlphaLedgerKey opens the rain archive window while BetaClerk waits downstairs.",
        inspired_source_excerpts=["", source_excerpt],
    )

    violation = next(
        item for item in result.violations
        if item.type == "inspired_source_copy"
    )

    assert violation.source_excerpt_index == 2
    assert violation.source_excerpt_sha256 == (
        "9835da69f227e028969c3e6e6a95002c33cc15b2aae14cd4ab6f3953002b9884"
    )
    assert violation.source_excerpt_length == len(source_excerpt)
    assert violation.copy_signal in {
        "distinctive_substring",
        "exact_normalized_excerpt",
        "ordered_phrase_overlap",
    }


def test_chapter_guardrails_flags_source_entity_leak_without_phrase_copy():
    guardrails = ChapterGuardrails()
    source_excerpt = "林寒把玄霜令藏进雨里，青岚会的人没有发现。"
    generated = "新主角在新城市里翻出玄霜令，准备拜访青岚会。"

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is False
    violation = next(
        item for item in result.violations
        if item.type == "inspired_source_entity_leak"
    )
    assert violation.severity == "high"
    assert violation.source_excerpt_index == 1
    assert violation.source_excerpt_sha256 == (
        "0724d95c930cf31b525d6bb4c11db1bb6f258408d7e670f6a42e363b768c3f03"
    )
    assert violation.source_excerpt_length == len(source_excerpt)
    assert violation.copy_signal == "source_entity_leak:玄霜令|青岚会"
    assert "玄霜令" in violation.copy_signal
    assert "青岚会" in violation.copy_signal


def test_chapter_guardrails_flags_quoted_short_chinese_source_term_leak():
    guardrails = ChapterGuardrails()
    source_excerpt = "苏眠把《魇灯》放回匣中，告诉同伴这件遗物只在黑潮夜醒来。"
    generated = "新故事换了角色和城市，但女主仍把魇灯当成核心遗物来推动剧情。"

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is False
    violation = next(
        item for item in result.violations
        if item.type == "inspired_source_entity_leak"
    )
    assert violation.copy_signal == "source_entity_leak:魇灯"


def test_chapter_guardrails_does_not_flag_common_quoted_dialogue_as_source_term():
    guardrails = ChapterGuardrails()
    source_excerpt = "苏眠低声说“回来”，然后把门关上，没有再解释。"
    generated = "新故事里的主角回来以后继续查案，没有复用源书的遗物或组织。"

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is True
    assert result.violations == []


def test_chapter_guardrails_flags_ascii_source_entity_leak_without_phrase_copy():
    guardrails = ChapterGuardrails()
    source_excerpt = (
        "AetherLedgerKey belonged to the archive under Moonfall Station. "
        "BetaClerk77 logged it after the eclipse while the wardens changed shifts."
    )
    generated = (
        "The new cast starts in a different city, but the draft keeps "
        "AetherLedgerKey as the vault object and asks BetaClerk77 for help."
    )

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is False
    violation = next(
        item for item in result.violations
        if item.type == "inspired_source_entity_leak"
    )
    assert violation.copy_signal == "source_entity_leak:AetherLedgerKey|BetaClerk77"
    assert violation.source_excerpt_index == 1
    assert violation.source_excerpt_length == len(source_excerpt)


def test_chapter_guardrails_flags_multiword_ascii_source_entity_leak():
    guardrails = ChapterGuardrails()
    source_excerpt = (
        "Moonfall Station kept a hidden bell below the archive. "
        "The older wardens used it only when the eclipse returned."
    )
    generated = (
        "The new plot has different characters and stakes, but the meeting "
        "still happens inside Moonfall Station before the final chase."
    )

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is False
    violation = next(
        item for item in result.violations
        if item.type == "inspired_source_entity_leak"
    )
    assert violation.copy_signal == "source_entity_leak:Moonfall Station"


def test_chapter_guardrails_flags_hyphenated_ascii_codename_entity_leak():
    guardrails = ChapterGuardrails()
    source_excerpt = (
        "PROJECT-ORCHID opened the sealed sky gate after SABLE-9 failed. "
        "The archive team erased every field report before sunrise."
    )
    generated = (
        "The new story changes the city and cast, but still names the secret "
        "operation PROJECT-ORCHID and lets SABLE-9 unlock the final gate."
    )

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is False
    violation = next(
        item for item in result.violations
        if item.type == "inspired_source_entity_leak"
    )
    assert violation.copy_signal == "source_entity_leak:PROJECT-ORCHID|SABLE-9"


def test_chapter_guardrails_does_not_treat_modal_hui_phrases_as_source_entities():
    guardrails = ChapterGuardrails()
    source_excerpt = "他一定会回来，不会把这件事告诉任何人。"
    generated = "新主角一定会继续调查，不会在雨夜停下。"

    result = guardrails.check(
        generated,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result.passed is True
    assert result.violations == []


def test_format_guardrail_history_note_includes_violation_source_fingerprint():
    source_excerpt = "AlphaLedgerKey opens the rain archive window while BetaClerk waits downstairs."
    guardrails = ChapterGuardrails()
    result = guardrails.check(
        "NewHero uses the AlphaLedgerKey opens the rain archive window while BetaClerk waits downstairs.",
        inspired_source_excerpts=[source_excerpt],
    )
    guardrail_meta = {
        "applied": False,
        "attempts": 0,
        "initial_result": result,
        "final_result": result,
    }

    note = format_guardrail_history_note(guardrail_meta)
    summary_line = [
        line for line in note.splitlines()
        if line.startswith(GUARDRAIL_REVIEW_JSON_PREFIX)
    ][0]
    summary = json.loads(summary_line.removeprefix(GUARDRAIL_REVIEW_JSON_PREFIX))

    violation = summary["final_violations"][0]
    assert violation["source_excerpt_index"] == 1
    assert violation["source_excerpt_sha256"] == (
        "9835da69f227e028969c3e6e6a95002c33cc15b2aae14cd4ab6f3953002b9884"
    )
    assert violation["source_excerpt_length"] == len(source_excerpt)
    assert violation["copy_signal"]


def test_format_forbidden_source_names_splits_multi_entity_leak_signal():
    prompt_section = _format_forbidden_source_names_for_prompt(
        [],
        {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_entity_leak",
                    "severity": "high",
                    "description": "source entity leaked",
                    "copy_signal": "source_entity_leak:玄霜令|青岚会",
                }
            ],
        },
    )

    assert "- 玄霜令" in prompt_section
    assert "- 青岚会" in prompt_section
    assert "玄霜令|青岚会" not in prompt_section


def test_format_forbidden_source_names_omits_long_context_entity_candidates():
    prompt_section = _format_forbidden_source_names_for_prompt(
        [],
        {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_entity_leak",
                    "severity": "high",
                    "description": "source entity leaked",
                    "context": "林寒把玄霜令藏进雨里，青岚会的人没有发现。",
                    "copy_signal": "source_entity_leak:玄霜令|青岚会",
                }
            ],
        },
    )

    assert "- 玄霜令" in prompt_section
    assert "- 青岚会" in prompt_section
    assert "林寒把玄霜令" not in prompt_section
    assert "雨里青岚会" not in prompt_section


def test_format_forbidden_source_names_dedupes_explicit_and_detected_entities():
    prompt_section = _format_forbidden_source_names_for_prompt(
        ["青岚会"],
        {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_entity_leak",
                    "severity": "high",
                    "description": "source entity leaked",
                    "copy_signal": "source_entity_leak:玄霜令|青岚会",
                }
            ],
        },
    )

    assert prompt_section.count("- 青岚会") == 1
    assert prompt_section.count("- 玄霜令") == 1


@pytest.mark.asyncio
async def test_apply_chapter_guardrail_check_rewrites_inspired_source_copy():
    ai_service = StubAIService()
    source_excerpt = "林寒把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"
    original = (
        "新主角把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"
        "他没有回头，只等楼下脚步声逼近。"
    )

    result = await apply_chapter_guardrail_check(
        generated_text=original,
        ai_service=ai_service,
        chapter_number=1,
        chapter_title="新雨",
        chapter_outline="写一个独立档案室对峙场景。",
        target_word_count=1200,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result["content"] != original
    assert result["applied"] is True
    assert result["initial_result"].passed is False
    assert any(
        violation.type == "inspired_source_copy"
        for violation in result["initial_result"].violations
    )
    assert "同类创作草稿疑似照搬源书片段" in ai_service.prompts[0]

@pytest.mark.asyncio
async def test_apply_chapter_guardrail_check_injects_forbidden_source_names_into_rewrite_prompt():
    ai_service = StubAIService()
    original = "林寒推开档案室门，青岚会的徽记在雨里一闪。"

    result = await apply_chapter_guardrail_check(
        generated_text=original,
        ai_service=ai_service,
        chapter_number=1,
        chapter_title="新雨",
        chapter_outline="写一个独立档案室对峙场景。",
        target_word_count=1200,
        forbidden_characters=["林寒", "沈璃", "青岚会"],
    )

    assert result["initial_result"].passed is False
    assert ai_service.prompts
    prompt = ai_service.prompts[0]
    assert "源书显性元素禁用清单" in prompt
    assert "- 林寒" in prompt
    assert "- 沈璃" in prompt
    assert "- 青岚会" in prompt
    assert "不得原样沿用" in prompt


@pytest.mark.asyncio
async def test_apply_chapter_guardrail_check_injects_detected_source_entities_into_rewrite_prompt():
    ai_service = StubAIService()
    source_excerpt = "林寒把玄霜令藏进雨里，青岚会的人没有发现。"
    original = "新主角在新城市里翻出玄霜令，准备拜访青岚会。"

    result = await apply_chapter_guardrail_check(
        generated_text=original,
        ai_service=ai_service,
        chapter_number=1,
        chapter_title="新雨",
        chapter_outline="写一个独立档案室对峙场景。",
        target_word_count=1200,
        inspired_source_excerpts=[source_excerpt],
    )

    assert result["initial_result"].passed is False
    assert any(
        violation.type == "inspired_source_entity_leak"
        for violation in result["initial_result"].violations
    )
    assert ai_service.prompts
    prompt = ai_service.prompts[0]
    assert "源书显性元素禁用清单" in prompt
    assert "- 玄霜令" in prompt
    assert "- 青岚会" in prompt


@pytest.mark.asyncio
async def test_apply_chapter_guardrail_check_marks_failed_rewrite_for_manual_review():
    ai_service = StillCopyingAIService()
    source_excerpt = "林寒把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"
    original = "新主角把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"

    result = await apply_chapter_guardrail_check(
        generated_text=original,
        ai_service=ai_service,
        chapter_number=1,
        chapter_title="新雨",
        chapter_outline="写一个独立档案室对峙场景。",
        target_word_count=1200,
        inspired_source_excerpts=[source_excerpt],
        max_rewrites=1,
    )

    assert result["attempts"] == 1
    assert result["final_result"].passed is False
    assert result["acceptance_status"] == "needs_manual_review"
    assert result["manual_review_reasons"]
    assert any("inspired_source_copy" in reason for reason in result["manual_review_reasons"])


@pytest.mark.asyncio
async def test_apply_chapter_guardrail_check_records_source_excerpt_fingerprints():
    ai_service = StillCopyingAIService()
    source_excerpt = "林寒把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"

    result = await apply_chapter_guardrail_check(
        generated_text="新主角把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。",
        ai_service=ai_service,
        chapter_number=1,
        chapter_title="新雨",
        chapter_outline="写一个独立档案室对峙场景。",
        target_word_count=1200,
        inspired_source_excerpts=[source_excerpt],
        max_rewrites=1,
    )

    assert result["source_excerpt_fingerprints"] == [
        {
            "index": 1,
            "sha256": "21b7d3fedf46c0e00f51cd44ac372d802cce2e7103907189444ad47c992a120d",
            "length": len(source_excerpt),
            "preview": source_excerpt,
        }
    ]


def test_format_guardrail_history_note_includes_review_source_hashes():
    first_excerpt = "林寒把青铜钥匙按进雨水里，旧档案室的窗户一格格亮起来。"
    second_excerpt = "沈璃在楼梯尽头回头，档案袋边缘被雨水洇开。"
    guardrail_meta = {
        "applied": True,
        "attempts": 1,
        "source_excerpt_fingerprints": [
            {
                "index": 1,
                "sha256": "a" * 64,
                "length": len(first_excerpt),
                "preview": first_excerpt,
            },
            {
                "index": 2,
                "sha256": "b" * 64,
                "length": len(second_excerpt),
                "preview": second_excerpt,
            },
        ],
        "initial_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                    "context": first_excerpt,
                }
            ],
        },
        "final_result": {
            "passed": False,
            "violations": [
                {
                    "type": "inspired_source_copy",
                    "severity": "high",
                    "description": "source-like span survived rewrite",
                    "context": first_excerpt,
                }
            ],
        },
    }

    note = format_guardrail_history_note(guardrail_meta)
    summary_line = [
        line
        for line in note.splitlines()
        if line.startswith(GUARDRAIL_REVIEW_JSON_PREFIX)
    ][0]
    summary = json.loads(summary_line.removeprefix(GUARDRAIL_REVIEW_JSON_PREFIX))

    assert summary["source_excerpt_fingerprints"] == [
        {
            "index": 1,
            "sha256": "a" * 64,
            "length": len(first_excerpt),
            "preview": first_excerpt,
        },
        {
            "index": 2,
            "sha256": "b" * 64,
            "length": len(second_excerpt),
            "preview": second_excerpt,
        },
    ]
