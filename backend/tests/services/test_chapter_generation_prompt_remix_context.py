from __future__ import annotations

from types import SimpleNamespace

import pytest

import app.api.chapters as chapters_api_module
from app.services.prompt_service import PromptService


_BASE_KWARGS = {
    "remix_continuation_context": "REMIX_CANON_SENTINEL: Inspector Lin must carry the updated ledger state.",
    "project_title": "Continuation Desk",
    "chapter_number": 20,
    "chapter_title": "Archive Aftermath",
    "chapter_outline": "Inspector Lin follows the ledger into the archive.",
    "target_word_count": 1200,
    "genre": "悬疑",
    "narrative_perspective": "第三人称",
    "characters_info": "Inspector Lin",
    "chapter_careers": "Detective",
    "foreshadow_reminders": "Old rival returns",
    "relevant_memories": "Ledger recovered in chapter 19.",
    "previous_chapter_content": "Lin closed the ledger and looked toward the archive.",
    "previous_chapter_summary": "Inspector Lin recovered the ledger.",
    "continuation_point": "Lin closed the ledger and looked toward the archive.",
    "recent_chapters_context": "Chapter 19 resolved the warehouse ledger thread.",
}


@pytest.mark.parametrize(
    "template_key",
    [
        "CHAPTER_GENERATION_ONE_TO_MANY",
        "CHAPTER_GENERATION_ONE_TO_ONE",
        "CHAPTER_GENERATION_ONE_TO_ONE_NEXT",
        "CHAPTER_GENERATION_ONE_TO_MANY_NEXT",
    ],
)
def test_chapter_generation_templates_render_remix_continuation_context(template_key):
    template = getattr(PromptService, template_key)

    prompt = PromptService.format_prompt(template, **_BASE_KWARGS)

    assert "<remix_continuation_context" in prompt
    assert "REMIX_CANON_SENTINEL" in prompt
    assert "Inspector Lin must carry the updated ledger state" in prompt

    assert "本段为已确认 Canon" in prompt
    assert "最新 timeline" in prompt
    assert "未回收伏笔" in prompt
    assert "不得覆盖" in prompt


def test_outline_continue_template_renders_remix_continuation_context():
    prompt = PromptService.format_prompt(
        PromptService.OUTLINE_CONTINUE,
        title="Continuation Desk",
        theme="ledger debt",
        genre="悬疑",
        narrative_perspective="第三人称",
        current_chapter_count=19,
        start_chapter=20,
        end_chapter=21,
        chapter_count=2,
        plot_stage_instruction="承接上一阶段",
        story_direction="继续追查档案室",
        time_period="现代",
        location="档案馆",
        atmosphere="压抑",
        rules="账册已经追回",
        recent_outlines="第19章追回账册。",
        style_anchor="克制短句",
        recent_chapter_samples="林合上账册。",
        remix_continuation_context="REMIX_CANON_SENTINEL: ledger recovered; do not replay recovery.",
        characters_info="Inspector Lin",
        requirements="不要重置状态",
        mcp_references="",
    )

    assert "<remix_continuation_context" in prompt
    assert "REMIX_CANON_SENTINEL" in prompt
    assert "do not replay recovery" in prompt


@pytest.mark.asyncio
async def test_generation_context_falls_back_to_inspired_block_without_continuation_lineage(monkeypatch):
    async def fake_build_continuation_context(*, project, db):
        return ""

    monkeypatch.setattr(
        chapters_api_module,
        "_build_remix_continuation_context_for_prompt",
        fake_build_continuation_context,
    )

    block = await chapters_api_module._build_remix_context_for_generation_prompt(
        project=SimpleNamespace(title="Inspired Draft"),
        db=object(),
        style_content=(
            "你正在基于《源书》做同类型创作，而不是忠实续写或照搬改名。\n"
            "【同类型创作总原则】\n"
            "- 只学习写法模式，不复制原书事实。\n"
            "【源书语气样本】\n"
            "[样本1]\n"
            "Lin kept his answer short. The rain moved across the archive windows.\n"
            "【源书显性元素禁用清单】\n"
            "以下名称只能作为改造参考，正文不得原样沿用：\n"
            "- 林寒, 青岚会\n"
        ),
        source_pattern_pack={
            "inspired_prompt_hints": ["Use source style only as rhythm guidance."],
            "inspired_copy_risk_hints": ["Reject copied source names."],
        },
    )

    assert "【Remix Inspired Creation Context】" in block
    assert "Do not treat this as continuation canon" in block
    assert "Lin kept his answer short" in block
    assert "林寒" in block
    assert "青岚会" in block
    assert "Use source style only as rhythm guidance." in block


@pytest.mark.asyncio
async def test_generation_context_keeps_confirmed_continuation_lineage_over_inspired_style(monkeypatch):
    async def fake_build_continuation_context(*, project, db):
        return "REMIX_CANON_SENTINEL: confirmed continuation wins."

    monkeypatch.setattr(
        chapters_api_module,
        "_build_remix_continuation_context_for_prompt",
        fake_build_continuation_context,
    )

    block = await chapters_api_module._build_remix_context_for_generation_prompt(
        project=SimpleNamespace(title="Continuation Draft"),
        db=object(),
        style_content="【源书显性元素禁用清单】\n- 林寒",
        source_pattern_pack={"inspired_prompt_hints": ["should not render"]},
    )

    assert block == "REMIX_CANON_SENTINEL: confirmed continuation wins."
