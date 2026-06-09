from __future__ import annotations

import re

import pytest

from app.models.project import Project
from app.schemas.book_import import BookImportChapter
from app.services.book_remix_bible_service import BookRemixBibleService
import app.services.book_remix_bible_service as bible_service_module


class StubAIService:
    def __init__(self, payload):
        self.payload = payload
        self.calls: list[dict] = []

    async def call_with_json_retry(self, **kwargs):
        self.calls.append(kwargs)
        return self.payload


@pytest.mark.asyncio
async def test_build_draft_payload_normalizes_required_sections():
    stub_ai_service = StubAIService(
        {
            "world_rules": {"power_system": "strict"},
            "character_cards": [{"name": "Lin"}],
            "timeline": [{"chapter": 1, "event": "opening conflict"}],
            "style_signature": {"pov": "third_person"},
            "hard_constraints": "invalid",
            "generation_notes": ["from-ai", 123],
            "chapter_change_packages": [{"chapter_number": 1, "summary": "ignored draft package"}],
        }
    )
    service = BookRemixBibleService(stub_ai_service)  # type: ignore[arg-type]

    project = Project(user_id="user-1", title="Remix Project")
    source_chapters = [
        BookImportChapter(
            title="Chapter 1",
            content="A" * 600,
            summary="summary-1",
            chapter_number=1,
            outline_title="Chapter 1",
        ),
        BookImportChapter(
            title="Chapter 2",
            content="B" * 600,
            summary="summary-2",
            chapter_number=2,
            outline_title="Chapter 2",
        ),
    ]

    payload = await service.build_draft_payload(
        project=project,
        source_chapters=source_chapters,
    )

    assert payload["world_rules"]["power_system"] == "strict"
    assert payload["character_cards"][0]["name"] == "Lin"
    assert payload["organizations"] == []
    assert payload["timeline"][0]["chapter"] == 1
    assert payload["story_arcs"] == []
    assert payload["foreshadows"]
    assert payload["style_signature"]["pov"] == "third_person"
    assert payload["hard_constraints"]
    assert payload["conflicts"] == []
    assert payload["generation_notes"] == ["from-ai", "123"]
    assert payload["chapter_change_packages"] == [{"chapter_number": 1, "summary": "ignored draft package"}]

    assert len(stub_ai_service.calls) == 1
    call = stub_ai_service.calls[0]
    assert call["max_retries"] == 3
    assert call["expected_type"] == "object"
    assert call["auto_mcp"] is False
    assert "world_rules" in call["prompt"]


@pytest.mark.asyncio
async def test_build_draft_payload_uses_balanced_source_window_and_content_signal():
    stub_ai_service = StubAIService({})
    service = BookRemixBibleService(stub_ai_service)  # type: ignore[arg-type]
    project = Project(user_id="user-1", title="Remix Project")

    source_chapters = []
    for chapter_number in range(1, 15):
        content = (
            f"intro-{chapter_number} "
            + ("正文片段 " * 90)
            + f" tail-token-{chapter_number}"
        )
        summary = f"intro-{chapter_number} 正文片段 正文片段"
        source_chapters.append(
            BookImportChapter(
                title=f"Chapter {chapter_number}",
                content=content,
                summary=summary,
                chapter_number=chapter_number,
                outline_title=f"Chapter {chapter_number}",
            )
        )

    await service.build_draft_payload(
        project=project,
        source_chapters=source_chapters,
    )

    prompt = stub_ai_service.calls[0]["prompt"]
    assert "Chapter 1 [head]" in prompt
    assert "Chapter 14 [tail]" in prompt
    assert "[middle]" in prompt
    assert re.search(r"Chapter (5|7|8|10) \[middle\]", prompt)
    assert "summary_quality: shallow" in prompt
    assert "tail-token-1" in prompt


@pytest.mark.asyncio
async def test_build_draft_payload_injects_source_pattern_pack_into_bible_prompt():
    stub_ai_service = StubAIService({})
    service = BookRemixBibleService(stub_ai_service)  # type: ignore[arg-type]
    project = Project(user_id="user-1", title="Remix Project")
    source_chapters = [
        BookImportChapter(
            title="Chapter 1",
            content="opening conflict and source-book voice",
            summary="opening conflict",
            chapter_number=1,
            outline_title="Chapter 1",
        )
    ]
    source_pattern_pack = {
        "workflow_patterns": [
            {
                "name": "continuation",
                "candidate_count": 2,
                "top_source_url": "https://github.com/voocel/ainovel-cli",
                "risk_flags": ["postinstall"],
            }
        ],
        "bible_enrichment_targets": [
            "world_rules",
            "timeline",
            "character_cards",
            "organizations",
            "story_arcs",
            "style_signature",
            "chapter_change_packages",
        ],
        "continuation_prompt_hints": [
            "续写前先读取世界观、时间线、人物卡、组织关系和情感线。",
            "每章生成后输出本章变化包，供下一章读取。",
        ],
        "style_signature_hints": [
            "续写要保留原书味道，只吸收写法模式。",
        ],
        "self_review_policy_hints": [
            "用户层允许不限次数自评优化；工程层必须使用可验证停止条件。",
        ],
        "safety_constraints": [
            "不导入外部代码、README 长段落、脚本、Docker、MCP 服务或浏览器扩展。",
        ],
    }

    await service.build_draft_payload(
        project=project,
        source_chapters=source_chapters,
        source_pattern_pack=source_pattern_pack,
    )

    prompt = stub_ai_service.calls[0]["prompt"]
    assert "公开来源模式包" in prompt
    assert "continuation" in prompt
    assert "world_rules" in prompt
    assert "organizations" in prompt
    assert "情感线" in prompt
    assert "本章变化包" in prompt
    assert "原书味道" in prompt
    assert "不限次数自评优化" in prompt
    assert "不导入外部代码" in prompt


@pytest.mark.asyncio
async def test_build_draft_payload_loads_latest_pattern_pack_when_not_provided(monkeypatch):
    stub_ai_service = StubAIService({})
    service = BookRemixBibleService(stub_ai_service)  # type: ignore[arg-type]
    resolve_calls: list[dict] = []

    async def fake_resolve(**kwargs):
        resolve_calls.append(kwargs)
        return {
            "workflow_patterns": [{"name": "continuation", "candidate_count": 1}],
            "bible_enrichment_targets": ["timeline", "character_cards"],
            "continuation_prompt_hints": ["auto-loaded source pattern continuation hint"],
            "style_signature_hints": ["preserve original flavor hint"],
            "self_review_policy_hints": ["unlimited review needs stop rules"],
            "safety_constraints": ["do not import external code"],
        }

    monkeypatch.setattr(
        bible_service_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve,
    )

    await service.build_draft_payload(
        project=Project(user_id="user-1", title="Remix Project"),
        source_chapters=[
            BookImportChapter(
                title="Chapter 1",
                content="opening",
                summary="opening",
                chapter_number=1,
                outline_title="Chapter 1",
            )
        ],
    )

    assert resolve_calls
    assert resolve_calls[0]["repo_root"] == bible_service_module.PROJECT_ROOT
    prompt = stub_ai_service.calls[0]["prompt"]
    assert "auto-loaded source pattern continuation hint" in prompt
    assert "preserve original flavor hint" in prompt
    assert "unlimited review needs stop rules" in prompt
    assert "do not import external code" in prompt


@pytest.mark.asyncio
async def test_build_draft_payload_refreshes_stale_pattern_pack_before_prompt(monkeypatch):
    stub_ai_service = StubAIService({})
    service = BookRemixBibleService(stub_ai_service)  # type: ignore[arg-type]
    refresh_calls: list[dict] = []
    load_calls: list[dict] = []

    async def fake_refresh(**kwargs):
        refresh_calls.append(kwargs)
        return {
            "refreshed": True,
            "pattern_pack": {
                "pattern_pack": {
                    "continuation_prompt_hints": [
                        "fresh source discovery hint for continuation"
                    ],
                    "style_signature_hints": [
                        "fresh style signature hint"
                    ],
                }
            },
        }

    def fake_load_latest(**kwargs):
        load_calls.append(kwargs)
        return {
            "continuation_prompt_hints": ["stale hint that should not be used"],
        }

    monkeypatch.setattr(
        bible_service_module.source_discovery_service,
        "evaluate_refresh_need",
        lambda **kwargs: {"refresh_needed": True, "reason": "pattern_pack_stale"},
    )
    monkeypatch.setattr(
        bible_service_module.source_discovery_service,
        "refresh_pattern_pack_if_needed",
        fake_refresh,
    )
    monkeypatch.setattr(
        bible_service_module.source_discovery_service,
        "load_latest_pattern_pack",
        fake_load_latest,
    )

    await service.build_draft_payload(
        project=Project(user_id="user-1", title="Remix Project"),
        source_chapters=[
            BookImportChapter(
                title="Chapter 1",
                content="opening",
                summary="opening",
                chapter_number=1,
                outline_title="Chapter 1",
            )
        ],
    )

    assert refresh_calls
    assert refresh_calls[0]["repo_root"] == bible_service_module.PROJECT_ROOT
    assert refresh_calls[0]["force"] is False
    assert load_calls == []
    prompt = stub_ai_service.calls[0]["prompt"]
    assert "fresh source discovery hint for continuation" in prompt
    assert "fresh style signature hint" in prompt
    assert "stale hint that should not be used" not in prompt


@pytest.mark.asyncio
async def test_build_draft_payload_backfills_style_signature_from_source_text_and_analysis():
    stub_ai_service = StubAIService({})
    service = BookRemixBibleService(stub_ai_service)  # type: ignore[arg-type]
    project = Project(
        user_id="user-style",
        title="Archive City",
        narrative_perspective="limited third person",
    )
    source_chapters = [
        BookImportChapter(
            title="Ledger Rain",
            content=(
                "Lin kept his answer short. The rain moved across the archive windows. "
                "He waited, counted three breaths, and let the clerk finish the lie. "
                '"No one moved the ledger," she said. '
                "Lin did not smile. He only turned the brass key once. "
            ),
            summary="Lin questions the clerk in a restrained archive scene.",
            chapter_number=1,
            outline_title="Ledger Rain",
        ),
        BookImportChapter(
            title="Cold Key",
            content=(
                "The corridor stayed quiet. Lin listened to the lock before he touched it. "
                "A second voice came from behind the map shelf. "
                '"You are late," the rival said. '
                "Lin kept the key in his palm and answered with one word. "
            ),
            summary="Lin carries the key into a quiet confrontation.",
            chapter_number=2,
            outline_title="Cold Key",
        ),
    ]
    analysis_snapshots = [
        {
            "chapter_number": 1,
            "summary": "Restrained tension, sparse dialogue, archive pressure.",
            "emotional_tone": "restrained suspicion",
            "emotional_intensity": 4,
        }
    ]

    payload = await service.build_draft_payload(
        project=project,
        source_chapters=source_chapters,
        analysis_snapshots=analysis_snapshots,
    )

    style_signature = payload["style_signature"]
    assert style_signature["source"] == "fallback_source_text"
    assert style_signature["narrative_perspective"] == "limited third person"
    assert style_signature["sentence_rhythm"]["average_sentence_length"] > 0
    assert style_signature["dialogue_density"] > 0
    assert "restrained suspicion" in style_signature["emotional_temperature"]
    assert style_signature["continuation_requirements"]
    assert any("original voice" in item for item in style_signature["continuation_requirements"])


@pytest.mark.asyncio
async def test_build_draft_payload_backfills_core_sections_and_uses_analysis_digest():
    stub_ai_service = StubAIService(
        {
            "world_rules": {"背景": "韩娱练习生"},
            "character_cards": [{"name": "杨翠", "description": "困在女性身体里的前男性灵魂"}],
            "story_arcs": [{"name": "身份错位生存线"}],
            "timeline": [],
            "foreshadows": [],
            "hard_constraints": [],
            "style_signature": {"voice": "压抑克制"},
            "generation_notes": [],
        }
    )
    service = BookRemixBibleService(stub_ai_service)  # type: ignore[arg-type]
    project = Project(user_id="user-1", title="混在半岛的日子")
    source_chapters = [
        BookImportChapter(
            title="第1章 逃离",
            content="杨翠逃离相亲，揣着仅有的现金前往上海。",
            summary="杨翠逃离相亲，揣着仅有的现金前往上海。",
            chapter_number=1,
            outline_title="第1章 逃离",
        ),
        BookImportChapter(
            title="第2章 魔都的厚度",
            content="她在上海站迷茫，拿到乐华娱乐名片。",
            summary="她在上海站迷茫，拿到乐华娱乐名片。",
            chapter_number=2,
            outline_title="第2章 魔都的厚度",
        ),
    ]
    analysis_snapshots = [
        {
            "chapter_number": 1,
            "title": "第1章 逃离",
            "summary": "杨翠逃离相亲，揣着仅有的现金前往上海。",
            "foreshadows": [{"content": "仅有的现金是否撑得到新的落脚点", "type": "planted"}],
            "plot_points": [{"content": "杨翠决定离开老家，奔向上海"}],
            "character_states": [{"character_name": "杨翠", "state_after": "惶恐但决绝"}],
        }
    ]

    payload = await service.build_draft_payload(
        project=project,
        source_chapters=source_chapters,
        analysis_snapshots=analysis_snapshots,
    )

    assert payload["timeline"]
    assert payload["foreshadows"]
    assert payload["hard_constraints"]
    assert payload["foreshadows"][0]["hook"].startswith("仅有的现金")
    assert "杨翠" in payload["hard_constraints"][0]["rule"]

    prompt = stub_ai_service.calls[0]["prompt"]
    assert "所有字段内容默认使用简体中文表达" in prompt
    assert "已有章节分析摘要" in prompt
    assert "杨翠决定离开老家，奔向上海" in prompt
