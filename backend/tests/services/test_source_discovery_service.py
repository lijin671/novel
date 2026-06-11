from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.services.source_discovery_service import (
    DEFAULT_GITHUB_QUERIES,
    DEFAULT_GITHUB_REPOSITORY_URLS,
    NovelSourceDiscoveryService,
    parse_linux_do_rss_items,
)
from app.services.source_pattern_pack_prompt import render_source_pattern_pack_digest


def test_build_ledger_classifies_novel_project_and_records_runtime_risks():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "voocel/ainovel-cli",
                "html_url": "https://github.com/voocel/ainovel-cli",
                "description": "AI novel writing CLI for chapter generation, continuation, story bible and style analysis.",
                "stargazers_count": 1280,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-writing", "novel", "llm", "fiction"],
                "updated_at": "2026-05-28T12:00:00Z",
                "root_files": [
                    "package.json",
                    "Dockerfile",
                    "scripts/install.sh",
                    "README.md",
                ],
                "package_scripts": {
                    "postinstall": "node ./scripts/postinstall.js",
                },
            }
        ],
        forum_items=[],
        generated_at="2026-05-31T09:30:00+08:00",
    )

    assert result["candidate_count"] == 1
    candidate = result["candidates"][0]
    assert candidate["source"] == "github"
    assert candidate["url"] == "https://github.com/voocel/ainovel-cli"
    assert candidate["title"] == "voocel/ainovel-cli"
    assert candidate["family"] == "novel-automation"
    assert candidate["posture"] == "pattern-only"
    assert "postinstall" in candidate["risk_flags"]
    assert "docker" in candidate["risk_flags"]
    assert "shell_script" in candidate["risk_flags"]
    assert "chapter_generation" in candidate["absorbed_patterns"]
    assert "continuation" in candidate["absorbed_patterns"]
    assert "style_signature" in candidate["absorbed_patterns"]
    assert result["safety_notes"][0].startswith("只采集公开元数据")


def test_parse_linux_do_rss_and_promote_novel_discussion_as_pattern_only():
    rss = """<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
      <channel>
        <title>LINUX DO</title>
        <item>
          <title>开源 AI 小说续写工具：自动拆书、世界观、时间线和人物卡</title>
          <link>https://linux.do/t/topic/123456</link>
          <description><![CDATA[
            分享一个小说创作工作流，支持 continuation、自我评审、风格复刻、组织关系整理。
          ]]></description>
          <pubDate>Sun, 31 May 2026 01:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    items = parse_linux_do_rss_items(
        rss,
        source_url="https://linux.do/tag/444-tag/444.rss",
    )
    result = NovelSourceDiscoveryService().build_ledger_from_metadata(
        github_repositories=[],
        forum_items=items,
        generated_at="2026-05-31T09:30:00+08:00",
    )

    assert len(items) == 1
    candidate = result["candidates"][0]
    assert candidate["source"] == "linux.do"
    assert candidate["family"] == "novel-automation"
    assert candidate["posture"] == "pattern-only"
    assert candidate["stars"] is None
    assert "book_decomposition" in candidate["absorbed_patterns"]
    assert "worldbuilding" in candidate["absorbed_patterns"]
    assert "timeline" in candidate["absorbed_patterns"]
    assert "character_cards" in candidate["absorbed_patterns"]
    assert "self_review" in candidate["absorbed_patterns"]


def test_chinese_story_metadata_without_english_anchor_expands_full_writing_chain_patterns():
    def zh(value: str) -> str:
        return value.encode("ascii").decode("unicode_escape")

    result = NovelSourceDiscoveryService().build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "demo/zh-novel-agent",
                "html_url": "https://github.com/demo/zh-novel-agent",
                "description": (
                    zh("\\u0041\\u0049 \\u521b\\u4f5c\\u5de5\\u4f5c\\u53f0\\uff0c\\u652f\\u6301\\u7ae0\\u8282\\u751f\\u6210\\u3001\\u7eed\\u5199\\u3001\\u6545\\u4e8b\\u5723\\u7ecf\\u3001\\u98ce\\u683c\\u5206\\u6790\\u3001")
                    + zh("\\u62c6\\u4e66\\u3001\\u4e16\\u754c\\u89c2\\u3001\\u65f6\\u95f4\\u7ebf\\u3001\\u4eba\\u7269\\u3001\\u7ec4\\u7ec7\\u3001\\u60c5\\u611f\\u7ebf\\u3001\\u81ea\\u6211\\u8bc4\\u5ba1\\u548c\\u6539\\u5199\\u3002")
                ),
                "stargazers_count": 512,
                "license": {"spdx_id": "MIT"},
                "topics": [
                    zh("\\u5c0f\\u8bf4"),
                    zh("\\u521b\\u4f5c"),
                    zh("\\u5199\\u4f5c"),
                ],
                "updated_at": "2026-05-31T00:00:00Z",
            }
        ],
        forum_items=[],
        generated_at="2026-05-31T09:30:00+08:00",
    )

    candidate = result["candidates"][0]
    assert {
        "book_decomposition",
        "chapter_generation",
        "continuation",
        "worldbuilding",
        "timeline",
        "character_cards",
        "organization_graph",
        "emotion_arc",
        "style_signature",
        "self_review",
    }.issubset(candidate["absorbed_patterns"])

def test_strong_novel_cli_metadata_maps_to_full_writing_chain_and_richer_pack_fields():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "voocel/ainovel-cli",
                "html_url": "https://github.com/voocel/ainovel-cli",
                "description": (
                    "AI novel writing CLI for chapter generation, continuation, "
                    "story bible and style analysis."
                ),
                "stargazers_count": 1280,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-writing", "novel", "llm", "fiction"],
                "updated_at": "2026-05-28T12:00:00Z",
                "root_files": [
                    "package.json",
                    "Dockerfile",
                    "scripts/install.sh",
                    "README.md",
                ],
                "package_scripts": {
                    "postinstall": "node ./scripts/postinstall.js",
                },
            }
        ],
        forum_items=[],
        generated_at="2026-05-31T09:30:00+08:00",
    )

    candidate = result["candidates"][0]
    assert {
        "book_decomposition",
        "worldbuilding",
        "timeline",
        "character_cards",
        "organization_graph",
        "emotion_arc",
        "self_review",
    }.issubset(candidate["absorbed_patterns"])

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "whole_book_analysis_targets" in pattern_pack
    assert "continuation_state_hints" in pattern_pack
    assert "style_fidelity_hints" in pattern_pack
    assert "self_review_gate_hints" in pattern_pack
    assert "chapter_change_package_hints" in pattern_pack
    assert "world_rules" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_change_packages" in pattern_pack["whole_book_analysis_targets"]
    assert "state snapshot" in " ".join(pattern_pack["continuation_state_hints"]).lower()
    assert "voice" in " ".join(pattern_pack["style_fidelity_hints"]).lower()
    assert "stop" in " ".join(pattern_pack["self_review_gate_hints"]).lower()
    assert "timeline_delta" in " ".join(pattern_pack["chapter_change_package_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "whole_book_analysis_targets" in digest
    assert "continuation_state_hints" in digest
    assert "style_fidelity_hints" in digest
    assert "self_review_gate_hints" in digest
    assert "chapter_change_package_hints" in digest


def test_same_type_creation_pattern_pack_exposes_inspired_guidance():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "demo/inspired-fiction-workbench",
                "html_url": "https://github.com/demo/inspired-fiction-workbench",
                "description": (
                    "AI fiction writing workbench for genre imitation, remix, "
                    "style preservation, character remapping, worldbuilding, "
                    "chapter generation, multi-pass edit, and copy risk review."
                ),
                "stargazers_count": 860,
                "license": {"spdx_id": "MIT"},
                "topics": ["fiction", "novel", "ai-writing", "remix"],
                "updated_at": "2026-06-08T08:00:00Z",
            }
        ],
        forum_items=[],
        generated_at="2026-06-08T09:30:00+08:00",
    )

    candidate = result["candidates"][0]
    assert "same_type_creation" in candidate["absorbed_patterns"]
    assert "style_signature" in candidate["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "inspired_mapping_targets" in pattern_pack
    assert "inspired_prompt_hints" in pattern_pack
    assert "inspired_transformation_hints" in pattern_pack
    assert "inspired_copy_risk_hints" in pattern_pack
    assert "character_remap" in pattern_pack["inspired_mapping_targets"]
    assert "organization_remap" in pattern_pack["inspired_mapping_targets"]
    assert "style" in " ".join(pattern_pack["inspired_prompt_hints"]).lower()
    assert "rename" in " ".join(pattern_pack["inspired_transformation_hints"]).lower()
    assert "copy" in " ".join(pattern_pack["inspired_copy_risk_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "inspired_mapping_targets" in digest
    assert "inspired_prompt_hints" in digest
    assert "inspired_transformation_hints" in digest
    assert "inspired_copy_risk_hints" in digest


def test_reader_reward_and_tri_modal_audit_sources_feed_prompt_pack():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "haowjy/creative-writing-skills",
                "html_url": "https://github.com/haowjy/creative-writing-skills",
                "description": (
                    "Creative writing skills for novels with muse, writer, critic, "
                    "revision-writer, reader-sim, style-creator, chronicler, "
                    "continuity-checker, four reward channels, and kb updates."
                ),
                "stargazers_count": 241,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["creative-writing", "novel", "claude-skills"],
                "updated_at": "2026-06-08T15:08:29Z",
            },
            {
                "full_name": "jblemee/bmad-book-builder",
                "html_url": "https://github.com/jblemee/bmad-book-builder",
                "description": (
                    "AI-assisted novel development with tri-modal Create/Edit/Validate "
                    "workflows, pre-writing checklist, automated audit chain, living "
                    "bible update, character-specific audits, rhythm analysis, and "
                    "continuity editor."
                ),
                "stargazers_count": 30,
                "license": {"spdx_id": "WTFPL"},
                "topics": ["novel", "writing", "bmad"],
                "updated_at": "2026-06-06T19:30:12Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T18:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "reader_reward_channel_gate" in candidates["haowjy/creative-writing-skills"]["absorbed_patterns"]
    assert "tri_modal_workflow_validation_gate" in candidates["jblemee/bmad-book-builder"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "reader_reward_channel_gate_hints" in pattern_pack
    assert "tri_modal_workflow_validation_gate_hints" in pattern_pack
    assert "transportation" in " ".join(pattern_pack["reader_reward_channel_gate_hints"]).lower()
    assert "pre-writing checklist" in " ".join(pattern_pack["tri_modal_workflow_validation_gate_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "reader_reward_channel_gate_hints" in digest
    assert "tri_modal_workflow_validation_gate_hints" in digest


def test_scene_serial_simulation_and_writer_git_sources_feed_prompt_pack():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "Deland78/Claude-Writing-Skills",
                "html_url": "https://github.com/Deland78/Claude-Writing-Skills",
                "description": (
                    "Fiction co-author system with chapter promise, scene architect, "
                    "character truth pass, mob session comment queue, lead editor, "
                    "citation enforcement, and Five Commandments value shift."
                ),
                "stargazers_count": 1,
                "license": None,
                "topics": ["fiction-writing", "claude-skills", "novel"],
                "updated_at": "2026-02-15T05:04:27Z",
            },
            {
                "full_name": "netflypsb/webnovel-mcp",
                "html_url": "https://github.com/netflypsb/webnovel-mcp",
                "description": (
                    "webnovel-mcp serial fiction project scaffolding with foreshadowing "
                    "tracker, timeline tracker, LitRPG stat blocks, romance arc tracker, "
                    "stale characters, chapter gaps, xianxia, and progression fantasy."
                ),
                "stargazers_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["webnovel", "mcp", "serial-fiction"],
                "updated_at": "2026-03-30T02:32:35Z",
            },
            {
                "full_name": "hackertaco/novel-generator",
                "html_url": "https://github.com/hackertaco/novel-generator",
                "description": (
                    "Simulation-first long-form novel generator with world truth, "
                    "belief state, utterance history, causal ledger, verify-long-form, "
                    "canonical validation, and a 300-episode verification horizon."
                ),
                "stargazers_count": 1,
                "license": None,
                "topics": ["novel-generator", "long-form-fiction"],
                "updated_at": "2026-06-07T16:26:59Z",
            },
            {
                "full_name": "eristoddle/git-write",
                "html_url": "https://github.com/eristoddle/git-write",
                "description": (
                    "Writer-friendly Git with explorations, word-by-word comparison, "
                    "beta reader annotations, author control, selective integration, "
                    "and cherry-pick individual changes for manuscripts."
                ),
                "stargazers_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["manuscript", "writing", "git"],
                "updated_at": "2025-09-17T01:23:22Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T20:10:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "scene_promise_mob_review_gate" in candidates["Deland78/Claude-Writing-Skills"]["absorbed_patterns"]
    assert "webnovel_genre_tracker_gate" in candidates["netflypsb/webnovel-mcp"]["absorbed_patterns"]
    assert "simulation_causal_ledger_verification_gate" in candidates["hackertaco/novel-generator"]["absorbed_patterns"]
    assert "writer_git_exploration_review_gate" in candidates["eristoddle/git-write"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "scene_promise_mob_review_gate_hints" in pattern_pack
    assert "webnovel_genre_tracker_gate_hints" in pattern_pack
    assert "simulation_causal_ledger_verification_gate_hints" in pattern_pack
    assert "writer_git_exploration_review_gate_hints" in pattern_pack
    assert "scene cards" in " ".join(pattern_pack["scene_promise_mob_review_gate_hints"]).lower()
    assert "foreshadowing" in " ".join(pattern_pack["webnovel_genre_tracker_gate_hints"]).lower()
    assert "causal ledger" in " ".join(pattern_pack["simulation_causal_ledger_verification_gate_hints"]).lower()
    assert "branches" in " ".join(pattern_pack["writer_git_exploration_review_gate_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "scene_promise_mob_review_gate_hints" in digest
    assert "webnovel_genre_tracker_gate_hints" in digest
    assert "simulation_causal_ledger_verification_gate_hints" in digest
    assert "writer_git_exploration_review_gate_hints" in digest


def test_fresh_context_story_pipeline_sources_feed_prompt_pack():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "dorakingx/novelpilot",
                "html_url": "https://github.com/dorakingx/novelpilot",
                "description": (
                    "Gemma-powered AI writing agent with a nine-agent pipeline: "
                    "Premise Architect, Character Director, World Builder, Plot Strategist, "
                    "Chapter Architect, Prose Writer, Style Editor, Continuity Detective, "
                    "Publisher Agent, typed JSON outputs, Story Bible, Foreshadowing Tracker, "
                    "completed novel reader, PDF and Markdown export."
                ),
                "stargazers_count": 3,
                "license": None,
                "topics": ["novel", "ai-writing", "story-bible"],
                "updated_at": "2026-05-27T00:18:28Z",
            },
            {
                "full_name": "heaversm/ralph-storywriter",
                "html_url": "https://github.com/heaversm/ralph-storywriter",
                "description": (
                    "Ralph Story Writer runs fiction mode chapter by chapter with fresh context, "
                    "no memory fatigue, reads prd.json to find next incomplete chapter, "
                    "reads STORY_BIBLE.md and progress.txt, then Plan -> Write -> Review -> Revise "
                    "with a skill ensemble until all chapters complete."
                ),
                "stargazers_count": 11,
                "license": None,
                "topics": ["fiction", "story-writing", "claude-code"],
                "updated_at": "2026-02-03T01:21:38Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T21:45:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "craft_role_pipeline" in candidates["dorakingx/novelpilot"]["absorbed_patterns"]
    assert "setup_payoff_tracking" in candidates["dorakingx/novelpilot"]["absorbed_patterns"]
    assert "canon_drift_continuity_qa_gate" in candidates["dorakingx/novelpilot"]["absorbed_patterns"]
    assert "fresh_context_chapter_iteration_gate" in candidates["heaversm/ralph-storywriter"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "fresh_context_chapter_iteration_gate_hints" in pattern_pack
    assert "fresh context" in " ".join(pattern_pack["fresh_context_chapter_iteration_gate_hints"]).lower()
    assert "next incomplete chapter" in " ".join(pattern_pack["fresh_context_chapter_iteration_gate_hints"]).lower()
    assert "fresh_context_iteration_report" in pattern_pack["whole_book_analysis_targets"]
    assert "fresh_context_loop_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "fresh_context_chapter_iteration_gate_hints" in digest


def test_author_control_webnovel_handbook_sources_feed_prompt_pack():
    assert "https://github.com/fopearcano/storyplanner" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/giapnguyen74/xnovelist" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/waylean/plotrail" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/XINGANLIU/web-novel-writing-skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/miserylee/webnovel-handbook" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ungden/truyencity2" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("AI is off by default" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("golden-three-chapters" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("PSYKE Story Bible" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "fopearcano/storyplanner",
                "html_url": "https://github.com/fopearcano/storyplanner",
                "description": "Creative writing tool with Narrative Engine, Story Grid, PSYKE Story Bible, continuity graph, and propose-then-confirm assistant actions.",
                "stargazers_count": 1,
                "license": None,
                "topics": ["creative-writing", "story-planning"],
                "updated_at": "2026-06-10T14:00:53Z",
                "root_files": ["README.md", "requirements.txt", "run.py", "scripts"],
            },
            {
                "full_name": "giapnguyen74/xnovelist",
                "html_url": "https://github.com/giapnguyen74/xnovelist",
                "description": "Local-first privacy-first novel editor where AI is off by default, workspace level caps AI reach, automatic snapshots, line-level diff, and drafts await review.",
                "stargazers_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "local-first", "writing"],
                "updated_at": "2026-06-08T14:31:50Z",
                "root_files": ["README.md", "LICENSE", "package.json"],
            },
            {
                "full_name": "waylean/plotrail",
                "html_url": "https://github.com/waylean/plotrail",
                "description": "Canon-aware AI novel writing skill with story bible before drafting, approved chapter contracts, memory ledgers, and continuity review for every chapter.",
                "stargazers_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "fiction", "skill"],
                "updated_at": "2026-06-07T07:11:03Z",
                "root_files": ["README.md", "README.zh-CN.md", "LICENSE", "novel-writer"],
            },
            {
                "full_name": "XINGANLIU/web-novel-writing-skill",
                "html_url": "https://github.com/XINGANLIU/web-novel-writing-skill",
                "description": "Chinese web novel writing skill with 10-stage pipeline, 7 expert roles, 4-layer anti-hallucination, state-sync memory, golden-three-chapters, and anti-AI-pattern gates.",
                "stargazers_count": 2,
                "license": {"spdx_id": "MIT"},
                "topics": ["web-novel", "agentic", "chinese-novel"],
                "updated_at": "2026-06-07T08:49:27Z",
                "root_files": ["README.md", "AGENTS.md", "CLAUDE.md", "plugin.json", "skills"],
            },
            {
                "full_name": "miserylee/webnovel-handbook",
                "html_url": "https://github.com/miserylee/webnovel-handbook",
                "description": "AI-agent handbook for Chinese webnovel workflows with docs/00-index.md routing and integrated drafting beta-reader feedback review revision workflow.",
                "stargazers_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["webnovel", "handbook", "agent-workflow"],
                "updated_at": "2026-06-09T19:07:10Z",
                "root_files": ["README.md", "AGENTS.md", "SAFETY.md", "docs", "skills"],
            },
            {
                "full_name": "ungden/truyencity2",
                "html_url": "https://github.com/ungden/truyencity2",
                "description": "AI-powered Vietnamese webnovel platform with Story Engine v2, Story Factory, 1000-chapter workflow, foreshadowing, timeline, power-system canon, autopilot, and prompt cache cost controls.",
                "stargazers_count": 0,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["webnovel", "story-factory", "autopilot"],
                "updated_at": "2026-06-10T08:23:34Z",
                "root_files": ["README.md", "package.json", "scripts", "supabase"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T23:10:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "narrative_strand_mapping" in candidates["fopearcano/storyplanner"]["absorbed_patterns"]
    assert "author_candidate_canon_confirmation_gate" in candidates["fopearcano/storyplanner"]["absorbed_patterns"]
    assert "local_first_novel_workspace" in candidates["giapnguyen74/xnovelist"]["absorbed_patterns"]
    assert "review_queue_staging" in candidates["giapnguyen74/xnovelist"]["absorbed_patterns"]
    assert "author_candidate_canon_confirmation_gate" in candidates["giapnguyen74/xnovelist"]["absorbed_patterns"]
    assert "canon_drift_continuity_qa_gate" in candidates["waylean/plotrail"]["absorbed_patterns"]
    assert "story_contract_commit_chain" in candidates["waylean/plotrail"]["absorbed_patterns"]
    assert "skill_orchestrated_chinese_novel_workflow" in candidates["XINGANLIU/web-novel-writing-skill"]["absorbed_patterns"]
    assert "boring_opening_quality_gates" in candidates["XINGANLIU/web-novel-writing-skill"]["absorbed_patterns"]
    assert "anti_slop_rulepack_triage_gate" in candidates["XINGANLIU/web-novel-writing-skill"]["absorbed_patterns"]
    assert "progressive_disclosure_skill_protocol_gate" in candidates["miserylee/webnovel-handbook"]["absorbed_patterns"]
    assert "webnovel_genre_tracker_gate" in candidates["ungden/truyencity2"]["absorbed_patterns"]
    assert "multi_book_autopilot_studio_gate" in candidates["ungden/truyencity2"]["absorbed_patterns"]
    assert "provider_budget_smoke_gate" in candidates["ungden/truyencity2"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert pattern_pack["author_candidate_canon_confirmation_gate_hints"]
    assert pattern_pack["progressive_disclosure_skill_protocol_gate_hints"]
    assert pattern_pack["webnovel_genre_tracker_gate_hints"]
    assert pattern_pack["provider_budget_smoke_gate_hints"]
    assert "candidate_canon_confirmation_policy" in pattern_pack["bible_enrichment_targets"]
    assert "multi_book_profile_audit" in pattern_pack["whole_book_analysis_targets"]
    assert "preview" in " ".join(pattern_pack["author_candidate_canon_confirmation_gate_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "author_candidate_canon_confirmation_gate_hints" in digest
    assert "progressive_disclosure_skill_protocol_gate_hints" in digest
    assert "webnovel_genre_tracker_gate_hints" in digest
    assert "provider_budget_smoke_gate_hints" in digest

    assert "https://github.com/dorakingx/novelpilot" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/heaversm/ralph-storywriter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("continuity detective" in query.lower() and "foreshadowing tracker" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("fresh context" in query.lower() and "progress.txt" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_narrative_qa_summary_causality_sources_feed_prompt_pack():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "google-deepmind/narrativeqa",
                "html_url": "https://github.com/google-deepmind/narrativeqa",
                "description": (
                    "NarrativeQA reading comprehension challenge dataset with Wikipedia "
                    "summaries, full stories, qaps.csv, questions and answers."
                ),
                "stargazers_count": 0,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["narrative", "reading-comprehension", "qa"],
                "updated_at": "2026-06-10T09:00:00Z",
            },
            {
                "full_name": "salesforce/booksum",
                "html_url": "https://github.com/salesforce/booksum",
                "description": (
                    "BookSum long-form narrative summarization over novels with "
                    "paragraph-level, chapter-level, and book-level human written summaries "
                    "plus causal and temporal dependencies."
                ),
                "stargazers_count": 0,
                "license": {"spdx_id": "BSD-3-Clause"},
                "topics": ["book", "summarization", "narrative"],
                "updated_at": "2026-06-10T09:00:00Z",
            },
            {
                "full_name": "uci-soe/FairytaleQAData",
                "html_url": "https://github.com/uci-soe/FairytaleQAData",
                "description": (
                    "FairytaleQA narrative comprehension dataset with question-answer "
                    "pairs, cor_section story_section evidence, education experts, "
                    "and 7 narrative elements."
                ),
                "stargazers_count": 0,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["story", "qa", "fairytale"],
                "updated_at": "2026-06-10T09:00:00Z",
            },
            {
                "full_name": "StonyBrookNLP/tellmewhy",
                "html_url": "https://github.com/StonyBrookNLP/tellmewhy",
                "description": (
                    "TellMeWhy why-questions in story narratives with free-form answers, "
                    "helpful_sentences, plausible answer validity human judgments, "
                    "and why characters perform actions."
                ),
                "stargazers_count": 0,
                "license": None,
                "topics": ["narrative", "why-questions"],
                "updated_at": "2026-06-10T09:00:00Z",
            },
            {
                "full_name": "uwnlp/storycommonsense",
                "html_url": "https://github.com/uwnlp/storycommonsense",
                "description": (
                    "Story Commonsense Knowledge for naive psychology, character "
                    "motivations, character emotions, mental states, and simple "
                    "commonsense stories."
                ),
                "stargazers_count": 0,
                "license": None,
                "topics": ["story", "commonsense"],
                "updated_at": "2026-06-10T09:00:00Z",
            },
            {
                "full_name": "nyu-mll/SQuALITY",
                "html_url": "https://github.com/nyu-mll/SQuALITY",
                "description": (
                    "SQuALITY question-focused long-document multi-reference "
                    "summarization dataset where each story asks what is the plot "
                    "of the story and has four reference summaries."
                ),
                "stargazers_count": 0,
                "license": None,
                "topics": ["long-document", "summarization", "story"],
                "updated_at": "2026-06-10T09:00:00Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T21:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "narrative_qa_comprehension_gate" in candidates["google-deepmind/narrativeqa"]["absorbed_patterns"]
    assert "chapter_summary_alignment_gate" in candidates["salesforce/booksum"]["absorbed_patterns"]
    assert "story_question_answer_validation_gate" in candidates["uci-soe/FairytaleQAData"]["absorbed_patterns"]
    assert "causal_why_explanation_gate" in candidates["StonyBrookNLP/tellmewhy"]["absorbed_patterns"]
    assert "story_commonsense_consistency_gate" in candidates["uwnlp/storycommonsense"]["absorbed_patterns"]
    assert "query_focused_long_summary_gate" in candidates["nyu-mll/SQuALITY"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "narrative_qa_comprehension_gate_hints" in pattern_pack
    assert "chapter_summary_alignment_gate_hints" in pattern_pack
    assert "story_question_answer_validation_gate_hints" in pattern_pack
    assert "causal_why_explanation_gate_hints" in pattern_pack
    assert "story_commonsense_consistency_gate_hints" in pattern_pack
    assert "query_focused_long_summary_gate_hints" in pattern_pack
    assert "evidence" in " ".join(pattern_pack["narrative_qa_comprehension_gate_hints"]).lower()
    assert "causal and temporal" in " ".join(pattern_pack["chapter_summary_alignment_gate_hints"]).lower()
    assert "section-grounded" in " ".join(pattern_pack["story_question_answer_validation_gate_hints"]).lower()
    assert "why" in " ".join(pattern_pack["causal_why_explanation_gate_hints"]).lower()
    assert "mental-state" in " ".join(pattern_pack["story_commonsense_consistency_gate_hints"]).lower()
    assert "query-focused" in " ".join(pattern_pack["query_focused_long_summary_gate_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "narrative_qa_comprehension_gate_hints" in digest
    assert "chapter_summary_alignment_gate_hints" in digest
    assert "story_question_answer_validation_gate_hints" in digest
    assert "causal_why_explanation_gate_hints" in digest
    assert "story_commonsense_consistency_gate_hints" in digest
    assert "query_focused_long_summary_gate_hints" in digest


def test_composite_writing_chain_patterns_expose_inspired_guidance_without_explicit_remix():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-08T17:20:00+08:00",
        "candidate_count": 3,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/voocel/ainovel-cli",
                "title": "voocel/ainovel-cli",
                "summary": "AI novel writing CLI with chapter generation.",
                "stars": 454,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["chapter_generation"],
                "score": 38,
            },
            {
                "source": "github",
                "url": "https://github.com/KazKozDev/NovelGenerator",
                "title": "KazKozDev/NovelGenerator",
                "summary": "Fiction generator with developed characters and diverse writing styles.",
                "stars": 134,
                "license": "NOASSERTION",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["character_cards", "style_signature", "self_review"],
                "score": 78,
            },
            {
                "source": "github",
                "url": "https://github.com/raestrada/storycraftr",
                "title": "raestrada/storycraftr",
                "summary": "AI tool for worldbuilding details, outlines, and chapters.",
                "stars": 142,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["worldbuilding"],
                "score": 62,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "same_type_creation" not in {
        pattern["name"] for pattern in pattern_pack["workflow_patterns"]
    }
    assert "character_remap" in pattern_pack["inspired_mapping_targets"]
    assert "world_rule_remap" in pattern_pack["inspired_mapping_targets"]
    assert "style_signature" in pattern_pack["inspired_mapping_targets"]
    assert "new names" in " ".join(pattern_pack["inspired_prompt_hints"]).lower()
    assert "rename" in " ".join(pattern_pack["inspired_transformation_hints"]).lower()
    assert "copied source names" in " ".join(pattern_pack["inspired_copy_risk_hints"]).lower()


def test_render_source_pattern_pack_digest_can_omit_inspired_guidance_for_continuation():
    digest = render_source_pattern_pack_digest(
        {
            "continuation_prompt_hints": ["Keep confirmed continuation canon."],
            "style_fidelity_hints": ["Preserve original voice."],
            "inspired_prompt_hints": ["Generate an independent new story."],
            "inspired_copy_risk_hints": ["Reject copied source names."],
        },
        include_inspired_guidance=False,
    )

    assert "Keep confirmed continuation canon." in digest
    assert "Preserve original voice." in digest
    assert "inspired_prompt_hints" not in digest
    assert "Generate an independent new story." not in digest
    assert "Reject copied source names." not in digest


def test_novelforge_metadata_maps_to_card_schema_context_workflow_patterns():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "RhythmicWave/NovelForge",
                "html_url": "https://github.com/RhythmicWave/NovelForge",
                "description": (
                    "AI assisted longform novel creation engine with schema-first "
                    "card-based creation, JSON Schema structured generation, "
                    "context injection, knowledge graph, workflow agent, "
                    "chapter generation, story bible and progress recovery."
                ),
                "stargazers_count": 921,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": [
                    "ai-writing",
                    "creative-writing",
                    "fiction",
                    "json-schema",
                    "longform",
                    "novel-writing",
                    "outline",
                    "structured-generation",
                ],
                "updated_at": "2026-06-08T11:00:00Z",
            }
        ],
        forum_items=[],
        generated_at="2026-06-09T10:00:00+08:00",
    )

    candidate = result["candidates"][0]
    assert candidate["posture"] == "pattern-only"
    assert candidate["license"] == "AGPL-3.0"
    assert {
        "card_workbench",
        "structured_generation_schema",
        "context_reference",
        "workflow_agent_pipeline",
        "chapter_generation",
    }.issubset(candidate["absorbed_patterns"])

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "card_schema_catalog" in pattern_pack["bible_enrichment_targets"]
    assert "json_schema_outputs" in pattern_pack["bible_enrichment_targets"]
    assert "context_reference_index" in pattern_pack["bible_enrichment_targets"]
    assert "workflow_nodes" in pattern_pack["whole_book_analysis_targets"]
    assert "structured_generation_hints" in pattern_pack
    assert "card_workbench_hints" in pattern_pack
    assert "context_reference_hints" in pattern_pack
    assert "schema" in " ".join(pattern_pack["structured_generation_hints"]).lower()
    assert "cards" in " ".join(pattern_pack["card_workbench_hints"]).lower()
    assert "context references" in " ".join(pattern_pack["context_reference_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "structured_generation_hints" in digest
    assert "card_workbench_hints" in digest
    assert "context_reference_hints" in digest


def test_codeywood_metadata_maps_to_scene_asset_pipeline_without_runtime_import():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "kaigani/codeywood",
                "html_url": "https://github.com/kaigani/codeywood",
                "description": (
                    "Claude Code based skills for AI filmmaking from idea to "
                    "production, screenplay planning, storyboard, shot list, "
                    "scene plan and multi-stage review."
                ),
                "stargazers_count": 21,
                "license": None,
                "topics": ["claude-code", "ai-filmmaking", "storyboard", "screenplay"],
                "updated_at": "2026-06-08T12:00:00Z",
                "root_files": ["README.md", "skills", "scripts"],
            }
        ],
        forum_items=[],
        generated_at="2026-06-09T10:00:00+08:00",
    )

    assert result["candidate_count"] == 1
    candidate = result["candidates"][0]
    assert candidate["family"] == "novel-automation"
    assert candidate["posture"] == "pattern-only"
    assert "license:missing" in candidate["trust_review"]["flags"]
    assert "scene_asset_pipeline" in candidate["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "scene_assets" in pattern_pack["whole_book_analysis_targets"]
    assert "scene_asset_pipeline_hints" in pattern_pack
    assert "scene goal" in " ".join(pattern_pack["scene_asset_pipeline_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "scene_asset_pipeline_hints" in digest


def test_render_ledger_and_digest_include_source_intake_provenance():
    service = NovelSourceDiscoveryService()
    ledger = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "RhythmicWave/NovelForge",
                "html_url": "https://github.com/RhythmicWave/NovelForge",
                "description": "AI novel writing with JSON Schema cards and context injection.",
                "stargazers_count": 921,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["novel-writing", "json-schema"],
                "updated_at": "2026-06-08T11:00:00Z",
            }
        ],
        forum_items=[],
        generated_at="2026-06-09T10:00:00+08:00",
    )
    ledger["provenance_notes"] = [
        "RhythmicWave/NovelForge HEAD: 71db1420d919d676521a15f6999090b37db86fb0.",
        "No clone, install, package hook, Docker stack, MCP server, native binary, shell script, browser extension, or external repository code execution was performed.",
    ]
    ledger["fetch_errors"] = [
        {
            "source": "github",
            "url": "https://api.github.com/repos/RhythmicWave/NovelForge",
            "error": "GitHub REST API unauthenticated rate limit exceeded.",
        }
    ]

    markdown = service.render_ledger_markdown(ledger)
    pattern_pack = service.build_pattern_pack_from_ledger(ledger)
    pattern_pack["source_intake_notes"] = ledger["provenance_notes"]
    digest = render_source_pattern_pack_digest(pattern_pack)

    assert "## Provenance Notes" in markdown
    assert "RhythmicWave/NovelForge HEAD" in markdown
    assert "## Fetch Limits And Failures" in markdown
    assert "rate limit exceeded" in markdown
    assert "source_intake_notes" in digest
    assert "No clone, install" in digest


def test_autonovel_metadata_maps_to_quality_voice_antislop_and_publication_pipeline():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "NousResearch/autonovel",
                "html_url": "https://github.com/NousResearch/autonovel",
                "description": (
                    "Autonomous novel pipeline from seed concept to print-ready PDF, "
                    "ePub, audiobook and landing page. Uses modify-evaluate-keep/discard, "
                    "foundation_score, chapter scoring, plateau detection, voice fingerprint, "
                    "anti-slop scorer, anti-pattern rules, reader panel and dual-persona review."
                ),
                "stargazers_count": 1400,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "fiction", "pipeline", "voice", "epub"],
                "updated_at": "2026-06-09T10:00:00Z",
            }
        ],
        forum_items=[],
        generated_at="2026-06-09T11:00:00+08:00",
    )

    candidate = result["candidates"][0]
    assert {
        "quality_score_loop",
        "voice_fingerprint",
        "anti_slop_audit",
        "publication_pipeline",
        "chapter_generation",
        "style_signature",
        "self_review",
    }.issubset(candidate["absorbed_patterns"])

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "quality_scores" in pattern_pack["whole_book_analysis_targets"]
    assert "voice_fingerprint" in pattern_pack["whole_book_analysis_targets"]
    assert "anti_slop_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "export_targets" in pattern_pack["whole_book_analysis_targets"]
    assert "modify-evaluate-keep/discard" in " ".join(pattern_pack["quality_score_loop_hints"]).lower()
    assert "voice fingerprint" in " ".join(pattern_pack["voice_fingerprint_hints"]).lower()
    assert "ai tells" in " ".join(pattern_pack["anti_slop_audit_hints"]).lower()
    assert "epub" in " ".join(pattern_pack["publication_pipeline_hints"]).lower()
    assert "quality_gate_remap" in pattern_pack["inspired_mapping_targets"]
    assert "voice_fingerprint" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "quality_score_loop_hints" in digest
    assert "voice_fingerprint_hints" in digest
    assert "anti_slop_audit_hints" in digest
    assert "publication_pipeline_hints" in digest


def test_default_discovery_sources_include_structured_writing_and_scene_pipeline_projects():
    assert "https://github.com/RhythmicWave/NovelForge" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/kaigani/codeywood" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/KoboldAI/KoboldAI-Client" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/SillyTavern/SillyTavern" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/envy-ai/ai_rpg" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/matrixorigin/Memoria" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/mrigankad/Novel-OS" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/aikohanasaki/SillyTavern-MemoryBooks" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/bal-spec/sillytavern-character-memory" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("json schema" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("context injection" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("idea to production" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("lorebook" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("rollback" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_static_context_memory_projects_map_to_lorebook_world_state_and_snapshot_patterns():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "KoboldAI/KoboldAI-Client",
                "html_url": "https://github.com/KoboldAI/KoboldAI-Client",
                "description": "Browser-based front-end for AI-assisted writing.",
                "stargazers_count": 1700,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["ai-writing", "novel", "story"],
                "updated_at": "2026-06-09T12:00:00Z",
            },
            {
                "full_name": "SillyTavern/SillyTavern",
                "html_url": "https://github.com/SillyTavern/SillyTavern",
                "description": "LLM frontend for power users.",
                "stargazers_count": 45000,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["llm", "frontend", "roleplay"],
                "updated_at": "2026-06-09T12:00:00Z",
            },
            {
                "full_name": "envy-ai/ai_rpg",
                "html_url": "https://github.com/envy-ai/ai_rpg",
                "description": "AI RPG solo tabletop game master with structured prompts.",
                "stargazers_count": 120,
                "license": None,
                "topics": ["story", "rpg", "worldbuilding"],
                "updated_at": "2026-06-09T12:00:00Z",
            },
            {
                "full_name": "matrixorigin/Memoria",
                "html_url": "https://github.com/matrixorigin/Memoria",
                "description": "Git for AI Agent Memory: Snapshot, Branch, Merge, Rollback.",
                "stargazers_count": 3600,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["memory", "agent", "snapshot"],
                "updated_at": "2026-06-09T12:00:00Z",
            },
            {
                "full_name": "mrigankad/Novel-OS",
                "html_url": "https://github.com/mrigankad/Novel-OS",
                "description": "Multi-agent AI framework that writes full-length novels.",
                "stargazers_count": 12,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "writing", "multi-agent"],
                "updated_at": "2026-06-09T12:00:00Z",
            },
            {
                "full_name": "aikohanasaki/SillyTavern-MemoryBooks",
                "html_url": "https://github.com/aikohanasaki/SillyTavern-MemoryBooks",
                "description": "Saves SillyTavern chat memories to lorebooks.",
                "stargazers_count": 221,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["lorebook", "memory", "story"],
                "updated_at": "2026-06-09T12:00:00Z",
            },
            {
                "full_name": "bal-spec/sillytavern-character-memory",
                "html_url": "https://github.com/bal-spec/sillytavern-character-memory",
                "description": "Extracts structured character memories into Data Bank for vector retrieval.",
                "stargazers_count": 58,
                "license": None,
                "topics": ["character-memory", "vector", "story"],
                "updated_at": "2026-06-09T12:00:00Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-09T12:00:00+08:00",
    )

    patterns_by_title = {candidate["title"]: set(candidate["absorbed_patterns"]) for candidate in result["candidates"]}
    assert "lorebook_context" in patterns_by_title["KoboldAI/KoboldAI-Client"]
    assert "author_note_layer" in patterns_by_title["KoboldAI/KoboldAI-Client"]
    assert "lorebook_context" in patterns_by_title["SillyTavern/SillyTavern"]
    assert "author_note_layer" in patterns_by_title["SillyTavern/SillyTavern"]
    assert "world_state_tracking" in patterns_by_title["envy-ai/ai_rpg"]
    assert "memory_snapshot_versioning" in patterns_by_title["matrixorigin/Memoria"]
    assert "workflow_agent_pipeline" in patterns_by_title["mrigankad/Novel-OS"]
    assert "world_state_tracking" in patterns_by_title["mrigankad/Novel-OS"]
    assert "quality_score_loop" in patterns_by_title["mrigankad/Novel-OS"]
    assert "lorebook_context" in patterns_by_title["aikohanasaki/SillyTavern-MemoryBooks"]
    assert "memory_snapshot_versioning" in patterns_by_title["aikohanasaki/SillyTavern-MemoryBooks"]
    assert "character_cards" in patterns_by_title["bal-spec/sillytavern-character-memory"]
    assert "context_reference" in patterns_by_title["bal-spec/sillytavern-character-memory"]
    assert "world_state_tracking" in patterns_by_title["bal-spec/sillytavern-character-memory"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "lorebook_entries" in pattern_pack["bible_enrichment_targets"]
    assert "activated_lore_entries" in pattern_pack["whole_book_analysis_targets"]
    assert "world_state_entities" in pattern_pack["whole_book_analysis_targets"]
    assert "memory_snapshots" in pattern_pack["whole_book_analysis_targets"]
    assert "lorebook_context_hints" in pattern_pack
    assert "author_note_layer_hints" in pattern_pack
    assert "world_state_tracking_hints" in pattern_pack
    assert "memory_snapshot_versioning_hints" in pattern_pack
    assert "lorebook entries" in " ".join(pattern_pack["lorebook_context_hints"]).lower()
    assert "rollback" in " ".join(pattern_pack["memory_snapshot_versioning_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "lorebook_context_hints" in digest
    assert "author_note_layer_hints" in digest
    assert "world_state_tracking_hints" in digest
    assert "memory_snapshot_versioning_hints" in digest



def test_default_github_repository_urls_remain_backend_authoritative_for_panel_hydration():
    normalized_urls = {url.lower() for url in DEFAULT_GITHUB_REPOSITORY_URLS}

    for url in (
        "https://github.com/arupmaity1/book-writer-mcp",
        "https://github.com/THUDM/LongWriter",
        "https://github.com/google-deepmind/narrativeqa",
        "https://github.com/booknlp/booknlp",
        "https://github.com/getzep/graphiti",
        "https://github.com/licensee/licensee",
    ):
        assert url.lower() in normalized_urls


def test_novel_graph_refresh_sources_map_to_deconstruction_and_graph_review_patterns():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "IDSIA/novel2graph",
                "html_url": "https://github.com/IDSIA/novel2graph",
                "description": "A workflow to extract Knowledge Graph from literary text.",
                "stargazers_count": 84,
                "license": None,
                "topics": ["novel", "knowledge-graph", "literary-text"],
                "updated_at": "2026-06-10T00:00:00Z",
            },
            {
                "full_name": "Drwei3155/story-graph",
                "html_url": "https://github.com/Drwei3155/story-graph",
                "description": "AI auto-generates a visual character relationship graph for novels with natural language search and historical event timeline.",
                "stargazers_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "relationship-graph", "story"],
                "updated_at": "2026-05-20T15:58:36Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T18:30:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert {
        "book_decomposition",
        "character_cards",
        "relationship_graph_global_replace_gate",
        "character_interaction_network_gate",
        "narrative_event_evolution_graph_gate",
        "schema_guided_graph_extraction",
    }.issubset(by_title["IDSIA/novel2graph"]["absorbed_patterns"])
    assert {
        "book_decomposition",
        "timeline",
        "relationship_graph_global_replace_gate",
        "character_interaction_network_gate",
    }.issubset(by_title["Drwei3155/story-graph"]["absorbed_patterns"])

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "relationship_graph_consistency_report" in pattern_pack["whole_book_analysis_targets"]
    assert "narrative_event_chain_report" in pattern_pack["whole_book_analysis_targets"]
    assert "schema_guided_graph_remap" in pattern_pack["inspired_mapping_targets"]
    assert pattern_pack["relationship_graph_global_replace_gate_hints"]
    assert pattern_pack["schema_guided_graph_extraction_hints"]
    assert pattern_pack["character_interaction_network_gate_hints"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "relationship_graph_global_replace_gate_hints" in digest
    assert "schema_guided_graph_extraction_hints" in digest


def test_default_discovery_sources_include_novel_graph_refresh_projects():
    assert "https://github.com/IDSIA/novel2graph" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Drwei3155/story-graph" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("novel2graph" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("character relationship graph" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_discover_public_sources_fetches_explicit_github_repository_urls(monkeypatch):
    requested_urls: list[str] = []

    class FakeResponse:
        text = ""

        def __init__(self, payload: dict):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, **kwargs):
            requested_urls.append(str(url))
            if str(url).endswith("/contents"):
                return FakeResponse(
                    [
                        {"name": "package.json", "type": "file"},
                        {"name": "Dockerfile", "type": "file"},
                        {"name": "scripts", "type": "dir"},
                        {"name": "README.md", "type": "file"},
                    ]
                )
            if str(url).endswith("/contents/package.json"):
                return FakeResponse(
                    {
                        "type": "file",
                        "encoding": "base64",
                        "content": (
                            "eyJzY3JpcHRzIjp7InBvc3RpbnN0YWxsIjoibm9kZSAuL3NjcmlwdHMv"
                            "cG9zdGluc3RhbGwuanMifX0="
                        ),
                    }
                )
            return FakeResponse(
                {
                    "full_name": "voocel/ainovel-cli",
                    "html_url": "https://github.com/voocel/ainovel-cli",
                    "description": (
                        "AI novel writing CLI for chapter generation, continuation, "
                        "story bible and style analysis."
                    ),
                    "stargazers_count": 1280,
                    "license": {"spdx_id": "MIT"},
                    "topics": ["ai-writing", "novel", "fiction"],
                    "updated_at": "2026-05-28T12:00:00Z",
                }
            )

    import app.services.source_discovery_service as source_discovery_module

    monkeypatch.setattr(source_discovery_module.httpx, "AsyncClient", FakeAsyncClient)

    import asyncio

    result = asyncio.run(
        NovelSourceDiscoveryService().discover_public_sources(
            github_queries=[],
            github_repository_urls=["https://github.com/voocel/ainovel-cli"],
            linux_do_rss_urls=[],
        )
    )

    assert requested_urls == [
        "https://api.github.com/repos/voocel/ainovel-cli",
        "https://api.github.com/repos/voocel/ainovel-cli/contents",
        "https://api.github.com/repos/voocel/ainovel-cli/contents/package.json",
    ]
    assert result["candidate_count"] == 1
    candidate = result["candidates"][0]
    assert candidate["title"] == "voocel/ainovel-cli"
    assert candidate["url"] == "https://github.com/voocel/ainovel-cli"
    assert "postinstall" in candidate["risk_flags"]
    assert "docker" in candidate["risk_flags"]
    assert "shell_script" not in candidate["risk_flags"]
    assert "continuation" in candidate["absorbed_patterns"]
    assert "book_decomposition" in candidate["absorbed_patterns"]
    assert result["fetch_errors"] == []


def test_discover_public_sources_records_invalid_explicit_github_repository_url(monkeypatch):
    requested_urls: list[str] = []

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, **kwargs):
            requested_urls.append(str(url))
            raise AssertionError("invalid explicit repository URL must not be fetched")

    import app.services.source_discovery_service as source_discovery_module

    monkeypatch.setattr(source_discovery_module.httpx, "AsyncClient", FakeAsyncClient)

    import asyncio

    result = asyncio.run(
        NovelSourceDiscoveryService().discover_public_sources(
            github_queries=[],
            github_repository_urls=["https://example.com/not/github"],
            linux_do_rss_urls=[],
        )
    )

    assert requested_urls == []
    assert result["candidate_count"] == 0
    assert result["candidates"] == []
    assert result["fetch_errors"] == [
        {
            "source": "github",
            "url": "https://example.com/not/github",
            "error": "invalid_github_repository_url",
        }
    ]


def test_discover_public_sources_merges_duplicate_github_repositories_from_search_and_explicit_urls(monkeypatch):
    requested_urls: list[str] = []

    class FakeResponse:
        def __init__(self, payload: dict):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, **kwargs):
            requested_urls.append(str(url))
            if "search/repositories" in str(url):
                return FakeResponse(
                    {
                        "items": [
                            {
                                "full_name": "demo/fiction-engine",
                                "html_url": "https://github.com/demo/fiction-engine",
                                "description": "A small novel helper.",
                                "stargazers_count": 24,
                                "license": {"spdx_id": "MIT"},
                                "topics": ["novel", "writing"],
                                "updated_at": "2026-05-30T00:00:00Z",
                            }
                        ]
                    }
                )
            return FakeResponse(
                {
                    "full_name": "demo/fiction-engine",
                    "html_url": "https://github.com/demo/fiction-engine",
                    "description": (
                        "AI novel writing CLI for chapter generation, continuation, "
                        "story bible and style analysis."
                    ),
                    "stargazers_count": 128,
                    "license": {"spdx_id": "MIT"},
                    "topics": ["ai-writing", "novel", "fiction", "story"],
                    "root_files": ["package.json", "Dockerfile", "README.md"],
                    "package_scripts": {
                        "postinstall": "node ./scripts/postinstall.js",
                    },
                    "updated_at": "2026-05-31T00:00:00Z",
                }
            )

    import app.services.source_discovery_service as source_discovery_module

    monkeypatch.setattr(source_discovery_module.httpx, "AsyncClient", FakeAsyncClient)

    import asyncio

    result = asyncio.run(
        NovelSourceDiscoveryService().discover_public_sources(
            github_queries=["fiction novel cli"],
            github_repository_urls=["https://github.com/demo/fiction-engine"],
            linux_do_rss_urls=[],
        )
    )

    assert requested_urls == [
        "https://api.github.com/search/repositories",
        "https://api.github.com/repos/demo/fiction-engine",
        "https://api.github.com/repos/demo/fiction-engine/contents",
        "https://api.github.com/repos/demo/fiction-engine/contents/package.json",
    ]
    assert result["candidate_count"] == 1
    candidate = result["candidates"][0]
    assert candidate["summary"].startswith("AI novel writing CLI")
    assert candidate["stars"] == 128
    assert "postinstall" in candidate["risk_flags"]
    assert "chapter_generation" in candidate["absorbed_patterns"]
    assert "continuation" in candidate["absorbed_patterns"]
    assert "style_signature" in candidate["absorbed_patterns"]
    assert "book_decomposition" in candidate["absorbed_patterns"]
    assert result["fetch_errors"] == []


def test_default_github_queries_cover_novel_cli_and_story_generation_families():
    normalized_queries = " | ".join(DEFAULT_GITHUB_QUERIES).lower()

    assert "novel cli" in normalized_queries
    assert "fiction generator" in normalized_queries
    assert "story generation" in normalized_queries
    assert "writing assistant" in normalized_queries
    assert "小说" in normalized_queries
    assert "写作" in normalized_queries
    assert "创作" in normalized_queries
    assert "世界观" in normalized_queries
    assert "时间线" in normalized_queries
    assert "人物卡" in normalized_queries
    assert "narrativeqa" in normalized_queries
    assert "booksum" in normalized_queries
    assert "fairytaleqa" in normalized_queries
    assert "tellmewhy" in normalized_queries
    assert "story commonsense" in normalized_queries
    assert "squality" in normalized_queries


def test_default_github_repository_urls_cover_static_review_shortlist():
    normalized_urls = {url.lower() for url in DEFAULT_GITHUB_REPOSITORY_URLS}

    assert "https://github.com/voocel/ainovel-cli" in normalized_urls
    assert "https://github.com/nousresearch/autonovel" in normalized_urls
    assert "https://github.com/leenbj/novel-creator-skill" in normalized_urls
    assert "https://github.com/kazkozdev/novelgenerator" in normalized_urls
    assert "https://github.com/raestrada/storycraftr" in normalized_urls
    assert "https://github.com/yuanshijiloong/author" in normalized_urls
    assert "https://github.com/brandburner/fabula" in normalized_urls
    assert "https://github.com/google-deepmind/narrativeqa" in normalized_urls
    assert "https://github.com/salesforce/booksum" in normalized_urls
    assert "https://github.com/uci-soe/fairytaleqadata" in normalized_urls
    assert "https://github.com/stonybrooknlp/tellmewhy" in normalized_urls
    assert "https://github.com/uwnlp/storycommonsense" in normalized_urls
    assert "https://github.com/nyu-mll/squality" in normalized_urls


def test_github_candidate_records_metadata_trust_review_and_posture_hint():
    result = NovelSourceDiscoveryService().build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "demo/fast-rise-novel-agent",
                "html_url": "https://github.com/demo/fast-rise-novel-agent",
                "description": (
                    "AI novel writing agent for continuation, story bible, "
                    "chapter generation and style analysis."
                ),
                "stargazers_count": 2500,
                "license": None,
                "topics": ["novel", "fiction", "ai-writing"],
                "owner": {"type": "User"},
                "open_issues_count": 0,
                "has_issues": True,
                "forks_count": 3,
                "has_downloads": True,
                "default_branch": "dev",
                "created_at": "2026-05-20T00:00:00Z",
                "updated_at": "2026-05-31T00:00:00Z",
            }
        ],
        forum_items=[],
        generated_at="2026-06-01T08:00:00+08:00",
    )

    candidate = result["candidates"][0]
    trust_review = candidate["trust_review"]

    assert candidate["posture"] == "pattern-only"
    assert candidate["posture_hint"] == "defer-trust-review"
    assert trust_review["posture_hint"] == "defer-trust-review"
    assert trust_review["review_basis"] == "github_metadata_only"
    assert {
        "license:missing",
        "zero-issues-high-stars",
        "low-fork-high-star-ratio",
        "downloads:enabled-high-stars",
        "default-branch:nonstandard",
        "owner:user-high-star-tool",
        "very-new-high-star-repo",
    }.issubset(set(trust_review["flags"]))

    markdown = NovelSourceDiscoveryService().render_ledger_markdown(result)
    assert "Posture hint: defer-trust-review" in markdown
    assert "Trust flags: license:missing" in markdown


def test_render_and_write_ledger_keeps_discovery_as_non_execution_evidence(tmp_path: Path):
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "story-lab/example",
                "html_url": "https://github.com/story-lab/example",
                "description": "Worldbuilding and timeline templates for AI fiction writing.",
                "stargazers_count": 88,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["worldbuilding", "fiction"],
                "updated_at": "2026-05-30T00:00:00Z",
            }
        ],
        forum_items=[],
        generated_at="2026-05-31T09:30:00+08:00",
    )

    markdown = service.render_ledger_markdown(result)

    assert "# Novel Source Discovery Ledger - 2026-05-31" in markdown
    assert "No clone, install, package hook, Docker stack, MCP server, native binary, shell script, or browser extension was executed." in markdown
    assert "story-lab/example" in markdown
    assert "worldbuilding" in markdown

    written_path = service.write_ledger(
        repo_root=tmp_path,
        result=result,
        date_slug="2026-05-31",
    )

    assert written_path == tmp_path / "docs" / "references" / "novel-source-discovery-2026-05-31.md"
    assert written_path.read_text(encoding="utf-8") == markdown


def test_build_pattern_pack_from_ledger_groups_sources_into_continuation_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-05-31T09:30:00+08:00",
        "candidate_count": 2,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/voocel/ainovel-cli",
                "title": "voocel/ainovel-cli",
                "summary": "AI novel writing CLI with story bible, continuation and style analysis.",
                "stars": 1280,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["postinstall", "docker"],
                "absorbed_patterns": ["chapter_generation", "continuation", "style_signature"],
                "updated_at": "2026-05-28T12:00:00Z",
                "score": 96,
            },
            {
                "source": "linux.do",
                "url": "https://linux.do/t/topic/123456",
                "title": "AI 小说拆书续写工作流",
                "summary": "自动提取世界观、时间线、人物卡、组织关系、情感线并反复自评优化。",
                "stars": None,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": [
                    "book_decomposition",
                    "worldbuilding",
                    "timeline",
                    "character_cards",
                    "organization_graph",
                    "emotion_arc",
                    "self_review",
                ],
                "updated_at": "Sun, 31 May 2026 01:00:00 GMT",
                "score": 84,
            },
        ],
        "safety_notes": ["只采集公开元数据和公开摘要；不克隆、不安装、不执行外部项目。"],
    }

    pack = service.build_pattern_pack_from_ledger(ledger)

    assert pack["generated_at"] == "2026-05-31T09:30:00+08:00"
    assert pack["source_candidate_count"] == 2
    assert pack["source_titles"] == ["voocel/ainovel-cli", "AI 小说拆书续写工作流"]
    assert pack["workflow_patterns"][0]["name"] == "continuation"
    assert pack["workflow_patterns"][0]["top_source_url"] == "https://github.com/voocel/ainovel-cli"
    assert "postinstall" in pack["workflow_patterns"][0]["risk_flags"]
    assert "world_rules" in pack["bible_enrichment_targets"]
    assert "timeline" in pack["bible_enrichment_targets"]
    assert "character_cards" in pack["bible_enrichment_targets"]
    assert "情感线" in "\n".join(pack["continuation_prompt_hints"])
    assert "原书味道" in "\n".join(pack["style_signature_hints"])
    assert "不限次数" in "\n".join(pack["self_review_policy_hints"])
    assert any("不导入外部代码" in item for item in pack["safety_constraints"])


def test_pattern_pack_preserves_candidate_trust_flags_for_prompt_safety():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-01T08:00:00+08:00",
        "candidate_count": 1,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/demo/suspicious-novel-agent",
                "title": "demo/suspicious-novel-agent",
                "summary": "AI novel writing CLI with continuation and style analysis.",
                "stars": 2600,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "posture_hint": "defer-trust-review",
                "risk_flags": [],
                "trust_review": {
                    "review_basis": "github_metadata_only",
                    "posture_hint": "defer-trust-review",
                    "flags": ["license:missing", "zero-issues-high-stars"],
                },
                "absorbed_patterns": ["continuation", "style_signature"],
                "score": 88,
            }
        ],
    }

    pack = service.build_pattern_pack_from_ledger(ledger)
    pattern = pack["workflow_patterns"][0]
    digest = render_source_pattern_pack_digest(pack)

    assert pattern["posture_hint"] == "defer-trust-review"
    assert pattern["trust_flags"] == ["license:missing", "zero-issues-high-stars"]
    assert pattern["sources"][0]["trust_flags"] == ["license:missing", "zero-issues-high-stars"]
    assert "posture_hint: defer-trust-review" in digest
    assert "trust_flags: license:missing, zero-issues-high-stars" in digest


def test_build_pattern_pack_from_ledger_tolerates_empty_or_partial_ledger():
    pack = NovelSourceDiscoveryService().build_pattern_pack_from_ledger(
        {
            "generated_at": "2026-05-31T09:30:00+08:00",
            "candidates": [
                {
                    "title": "missing-patterns",
                    "url": "https://example.test/missing-patterns",
                    "score": 10,
                },
                {
                    "title": "missing-url",
                    "absorbed_patterns": ["continuation"],
                    "score": 50,
                },
            ],
        }
    )

    assert pack["generated_at"] == "2026-05-31T09:30:00+08:00"
    assert pack["source_candidate_count"] == 0
    assert pack["workflow_patterns"] == []
    assert pack["source_titles"] == []
    assert any("不克隆" in item for item in pack["safety_constraints"])


def test_write_pattern_pack_persists_discovery_guidance_as_json(tmp_path: Path):
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-05-31T09:30:00+08:00",
        "candidate_count": 1,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/voocel/ainovel-cli",
                "title": "voocel/ainovel-cli",
                "summary": "AI novel writing CLI with continuation.",
                "stars": 1280,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["continuation", "chapter_generation"],
                "score": 96,
            }
        ],
        "safety_notes": ["只采集公开元数据和公开摘要。"],
    }
    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    written_path = service.write_pattern_pack(
        repo_root=tmp_path,
        pattern_pack=pattern_pack,
        date_slug="2026-05-31",
    )
    loaded = service.load_latest_pattern_pack(repo_root=tmp_path)

    assert written_path == tmp_path / "backend" / "app" / "references" / "novel-source-pattern-pack-2026-05-31.json"
    assert loaded["generated_at"] == "2026-05-31T09:30:00+08:00"
    assert loaded["workflow_patterns"][0]["name"] == "continuation"
    assert "不导入外部代码" in "\n".join(loaded["safety_constraints"])



def test_load_latest_pattern_pack_artifact_returns_payload_and_metadata(tmp_path: Path):
    reference_dir = tmp_path / "backend" / "app" / "references"
    reference_dir.mkdir(parents=True)
    (reference_dir / "novel-source-pattern-pack-2026-05-30.json").write_text(
        json.dumps({"generated_at": "2026-05-30T01:00:00+08:00", "workflow_patterns": []}),
        encoding="utf-8",
    )
    latest_path = reference_dir / "novel-source-pattern-pack-2026-05-31.json"
    latest_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-05-31T09:30:00+08:00",
                "source_candidate_count": 2,
                "source_titles": ["voocel/ainovel-cli"],
                "workflow_patterns": [{"name": "continuation"}],
                "safety_constraints": ["pattern-only"],
            }
        ),
        encoding="utf-8",
    )

    artifact = NovelSourceDiscoveryService().load_latest_pattern_pack_artifact(repo_root=tmp_path)

    assert artifact["found"] is True
    assert artifact["path"] == str(latest_path)
    assert artifact["generated_at"] == "2026-05-31T09:30:00+08:00"
    assert artifact["source_candidate_count"] == 2
    assert artifact["workflow_pattern_count"] == 1
    assert artifact["pattern_pack"]["workflow_patterns"][0]["name"] == "continuation"


def test_load_latest_pattern_pack_artifact_reports_missing_reference_dir(tmp_path: Path):
    artifact = NovelSourceDiscoveryService().load_latest_pattern_pack_artifact(repo_root=tmp_path)

    assert artifact == {
        "found": False,
        "path": None,
        "generated_at": None,
        "source_candidate_count": 0,
        "workflow_pattern_count": 0,
        "source_titles": [],
        "pattern_pack": {},
    }


def test_load_latest_ledger_artifact_returns_latest_markdown(tmp_path: Path):
    reference_dir = tmp_path / "docs" / "references"
    reference_dir.mkdir(parents=True)
    (reference_dir / "novel-source-discovery-2026-05-30.md").write_text(
        "# Novel Source Discovery Ledger - 2026-05-30\n",
        encoding="utf-8",
    )
    latest_path = reference_dir / "novel-source-discovery-2026-05-31.md"
    latest_path.write_text(
        "# Novel Source Discovery Ledger - 2026-05-31\n\n- URL: https://github.com/voocel/ainovel-cli\n",
        encoding="utf-8",
    )

    artifact = NovelSourceDiscoveryService().load_latest_ledger_artifact(repo_root=tmp_path)

    assert artifact["found"] is True
    assert artifact["path"] == str(latest_path)
    assert artifact["date_slug"] == "2026-05-31"
    assert "voocel/ainovel-cli" in artifact["content"]


def test_source_discovery_refresh_needed_when_artifact_missing(tmp_path: Path):
    service = NovelSourceDiscoveryService()

    decision = service.evaluate_refresh_need(
        repo_root=tmp_path,
        now=datetime.fromisoformat("2026-05-31T08:00:00+08:00"),
        max_age_hours=24,
    )

    assert decision["refresh_needed"] is True
    assert decision["reason"] == "pattern_pack_missing"
    assert decision["age_hours"] is None


def test_source_discovery_refresh_needed_when_artifact_stale(tmp_path: Path):
    reference_dir = tmp_path / "backend" / "app" / "references"
    reference_dir.mkdir(parents=True)
    (reference_dir / "novel-source-pattern-pack-2026-05-30.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-05-30T00:00:00+08:00",
                "workflow_patterns": [{"name": "continuation"}],
            }
        ),
        encoding="utf-8",
    )

    decision = NovelSourceDiscoveryService().evaluate_refresh_need(
        repo_root=tmp_path,
        now=datetime.fromisoformat("2026-05-31T08:00:00+08:00"),
        max_age_hours=24,
    )

    assert decision["refresh_needed"] is True
    assert decision["reason"] == "pattern_pack_stale"
    assert decision["generated_at"] == "2026-05-30T00:00:00+08:00"
    assert decision["age_hours"] == 32.0


def test_source_discovery_refresh_not_needed_for_fresh_pattern_pack(tmp_path: Path):
    reference_dir = tmp_path / "backend" / "app" / "references"
    reference_dir.mkdir(parents=True)
    (reference_dir / "novel-source-pattern-pack-2026-05-31.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-05-31T04:00:00+08:00",
                "workflow_patterns": [{"name": "continuation"}],
            }
        ),
        encoding="utf-8",
    )

    decision = NovelSourceDiscoveryService().evaluate_refresh_need(
        repo_root=tmp_path,
        now=datetime.fromisoformat("2026-05-31T08:00:00+08:00"),
        max_age_hours=24,
    )

    assert decision["refresh_needed"] is False
    assert decision["reason"] == "pattern_pack_fresh"
    assert decision["age_hours"] == 4.0



def test_refresh_pattern_pack_if_needed_skips_when_current_pack_is_fresh(tmp_path: Path):
    reference_dir = tmp_path / "backend" / "app" / "references"
    reference_dir.mkdir(parents=True)
    (reference_dir / "novel-source-pattern-pack-2026-05-31.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-05-31T04:00:00+08:00",
                "source_candidate_count": 1,
                "workflow_patterns": [{"name": "continuation"}],
            }
        ),
        encoding="utf-8",
    )

    class NoNetworkService(NovelSourceDiscoveryService):
        async def discover_public_sources(self, **kwargs):  # pragma: no cover - should not run
            raise AssertionError("fresh pattern pack must not trigger public network discovery")

    service = NoNetworkService()

    import asyncio

    result = asyncio.run(
        service.refresh_pattern_pack_if_needed(
            repo_root=tmp_path,
            now=datetime.fromisoformat("2026-05-31T08:00:00+08:00"),
            max_age_hours=24,
        )
    )

    assert result["refreshed"] is False
    assert result["refresh_policy_before"]["reason"] == "pattern_pack_fresh"
    assert result["pattern_pack"]["found"] is True
    assert result["written_path"] is None
    assert result["written_pattern_pack_path"] is None



def test_resolve_fresh_pattern_pack_skips_network_when_current_pack_is_fresh(tmp_path: Path):
    reference_dir = tmp_path / "backend" / "app" / "references"
    reference_dir.mkdir(parents=True)
    (reference_dir / "novel-source-pattern-pack-2026-05-31.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-05-31T04:00:00+08:00",
                "source_candidate_count": 1,
                "workflow_patterns": [{"name": "continuation"}],
                "continuation_prompt_hints": ["fresh continuation hint"],
            }
        ),
        encoding="utf-8",
    )

    class NoNetworkService(NovelSourceDiscoveryService):
        async def discover_public_sources(self, **kwargs):  # pragma: no cover - should not run
            raise AssertionError("fresh pattern pack must not trigger public network discovery")

    import asyncio

    pattern_pack = asyncio.run(
        NoNetworkService().resolve_fresh_pattern_pack(
            repo_root=tmp_path,
            now=datetime.fromisoformat("2026-05-31T08:00:00+08:00"),
            max_age_hours=24,
        )
    )

    assert pattern_pack["workflow_patterns"][0]["name"] == "continuation"
    assert pattern_pack["continuation_prompt_hints"] == ["fresh continuation hint"]


def test_refresh_pattern_pack_if_needed_discovers_and_persists_when_missing(tmp_path: Path):
    class StubDiscoveryService(NovelSourceDiscoveryService):
        def __init__(self) -> None:
            super().__init__()
            self.calls = []

        async def discover_public_sources(self, **kwargs):
            self.calls.append(kwargs)
            return self.build_ledger_from_metadata(
                github_repositories=[
                    {
                        "full_name": "voocel/ainovel-cli",
                        "html_url": "https://github.com/voocel/ainovel-cli",
                        "description": "AI novel writing CLI with chapter generation, continuation and style signature analysis.",
                        "stargazers_count": 1280,
                        "license": {"spdx_id": "MIT"},
                        "topics": ["novel", "fiction", "ai-writing"],
                        "updated_at": "2026-05-31T01:00:00Z",
                    }
                ],
                forum_items=[],
                generated_at="2026-05-31T09:30:00+08:00",
            )

    service = StubDiscoveryService()

    import asyncio

    result = asyncio.run(
        service.refresh_pattern_pack_if_needed(
            repo_root=tmp_path,
            github_queries=["ai novel writing stars:>50"],
            linux_do_rss_urls=["https://linux.do/tag/444-tag/444.rss"],
            now=datetime.fromisoformat("2026-05-31T08:00:00+08:00"),
            max_age_hours=24,
        )
    )

    assert result["refreshed"] is True
    assert result["refresh_policy_before"]["reason"] == "pattern_pack_missing"
    assert result["candidate_count"] == 1
    assert result["pattern_pack"]["found"] is True
    assert result["pattern_pack"]["workflow_pattern_count"] >= 1
    assert Path(result["written_path"]).name == "novel-source-discovery-2026-05-31.md"
    assert Path(result["written_pattern_pack_path"]).name == "novel-source-pattern-pack-2026-05-31.json"
    assert service.calls[0]["github_queries"] == ["ai novel writing stars:>50"]
    assert service.calls[0]["linux_do_rss_urls"] == ["https://linux.do/tag/444-tag/444.rss"]


def test_graph_memory_workspace_sources_map_to_new_book_remix_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "MangoLion/plotbunni",
                "html_url": "https://github.com/MangoLion/plotbunni",
                "description": "",
                "stargazers_count": 412,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "fiction", "writing"],
                "updated_at": "2026-06-09T00:00:00Z",
            },
            {
                "full_name": "loreum-app/loreum",
                "html_url": "https://github.com/loreum-app/loreum",
                "description": "",
                "stargazers_count": 1640,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["worldbuilding", "fiction", "mcp"],
                "updated_at": "2026-06-09T00:00:00Z",
            },
            {
                "full_name": "Lanerra/saga",
                "html_url": "https://github.com/Lanerra/saga",
                "description": "",
                "stargazers_count": 210,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["novel", "knowledge-graph", "langgraph"],
                "updated_at": "2026-06-09T00:00:00Z",
            },
            {
                "full_name": "ModernRelay/omnigraph",
                "html_url": "https://github.com/ModernRelay/omnigraph",
                "description": "",
                "stargazers_count": 98,
                "license": {"spdx_id": "MIT"},
                "topics": ["graph", "branching", "query-language"],
                "updated_at": "2026-06-09T00:00:00Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-09T12:00:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert result["candidate_count"] == 4
    assert {
        "local_first_novel_workspace",
        "prompt_library",
        "scene_level_generation",
    }.issubset(by_title["MangoLion/plotbunni"]["absorbed_patterns"])
    assert {
        "style_guide_layering",
        "review_queue_staging",
        "entity_schema_custom_fields",
        "contradiction_detection",
    }.issubset(by_title["loreum-app/loreum"]["absorbed_patterns"])
    assert {
        "scene_level_generation",
        "content_ref_externalization",
        "graph_healing",
        "contradiction_detection",
    }.issubset(by_title["Lanerra/saga"]["absorbed_patterns"])
    assert {
        "graph_branching_atomicity",
        "query_lint_contract",
        "memory_snapshot_versioning",
    }.issubset(by_title["ModernRelay/omnigraph"]["absorbed_patterns"])


def test_graph_memory_workspace_pattern_pack_exposes_prompt_digest_hints():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-09T12:30:00+08:00",
        "candidate_count": 3,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/MangoLion/plotbunni",
                "title": "MangoLion/plotbunni",
                "summary": "Local-first novel workspace with prompt manager and scene-level AI writer.",
                "stars": 412,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": [
                    "local_first_novel_workspace",
                    "prompt_library",
                    "scene_level_generation",
                ],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/loreum-app/loreum",
                "title": "loreum-app/loreum",
                "summary": "World database with style guide layering, custom entity fields, and review queue.",
                "stars": 1640,
                "license": "AGPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["mcp_server"],
                "absorbed_patterns": [
                    "style_guide_layering",
                    "review_queue_staging",
                    "entity_schema_custom_fields",
                    "contradiction_detection",
                ],
                "score": 112,
            },
            {
                "source": "github",
                "url": "https://github.com/Lanerra/saga",
                "title": "Lanerra/saga",
                "summary": "Scene-level generation with ContentRef, graph healing, and contradiction detection.",
                "stars": 210,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker"],
                "absorbed_patterns": [
                    "content_ref_externalization",
                    "graph_healing",
                    "graph_branching_atomicity",
                    "query_lint_contract",
                ],
                "score": 96,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "local_workspace_scope" in pattern_pack["whole_book_analysis_targets"]
    assert "style_layers" in pattern_pack["bible_enrichment_targets"]
    assert "pending_change_review_queue" in pattern_pack["whole_book_analysis_targets"]
    assert "external_content_refs" in pattern_pack["whole_book_analysis_targets"]
    assert "graph_healing_actions" in pattern_pack["whole_book_analysis_targets"]
    assert "query_lint_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "local_first_workspace_hints" in pattern_pack
    assert "prompt_library_hints" in pattern_pack
    assert "style_guide_layering_hints" in pattern_pack
    assert "review_queue_staging_hints" in pattern_pack
    assert "entity_schema_custom_fields_hints" in pattern_pack
    assert "scene_level_generation_hints" in pattern_pack
    assert "content_ref_externalization_hints" in pattern_pack
    assert "graph_healing_hints" in pattern_pack
    assert "contradiction_detection_hints" in pattern_pack
    assert "graph_branching_atomicity_hints" in pattern_pack
    assert "query_lint_contract_hints" in pattern_pack
    assert "scene_plan_remap" in pattern_pack["inspired_mapping_targets"]
    assert "style_layer_remap" in pattern_pack["inspired_mapping_targets"]
    assert "custom_field_remap" in pattern_pack["inspired_mapping_targets"]
    assert "review_queue_gate" in pattern_pack["inspired_mapping_targets"]
    assert "branch_snapshot_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "local_first_workspace_hints" in digest
    assert "prompt_library_hints" in digest
    assert "style_guide_layering_hints" in digest
    assert "review_queue_staging_hints" in digest
    assert "entity_schema_custom_fields_hints" in digest
    assert "scene_level_generation_hints" in digest
    assert "content_ref_externalization_hints" in digest
    assert "graph_healing_hints" in digest
    assert "contradiction_detection_hints" in digest
    assert "graph_branching_atomicity_hints" in digest
    assert "query_lint_contract_hints" in digest


def test_current_writing_tool_sources_map_to_anti_ending_and_plotgrid_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "doctoroyy/novel-copilot",
                "html_url": "https://github.com/doctoroyy/novel-copilot",
                "description": "AI novel copilot with three-layer memory system, Story Bible, character relationship graph, plot graph, and premature ending detection.",
                "stargazers_count": 9,
                "license": None,
                "topics": ["ai-writing", "novel", "story-bible"],
                "updated_at": "2026-05-15T13:36:07Z",
                "root_files": ["package.json", "wrangler.toml", "scripts"],
            },
            {
                "full_name": "PixeroJan/obsidian-storyline",
                "html_url": "https://github.com/PixeroJan/obsidian-storyline",
                "description": "Book planning tool with board, plotgrid, timeline, plotlines, characters, scenes, locations, and progress tracking.",
                "stargazers_count": 168,
                "license": {"spdx_id": "MIT"},
                "topics": ["obsidian", "writing", "novel"],
                "updated_at": "2026-06-09T07:04:54Z",
                "root_files": ["manifest.json", "package.json"],
            },
            {
                "full_name": "skyfiredao/dreampowers",
                "html_url": "https://github.com/skyfiredao/dreampowers",
                "description": "Chinese novel writing skill pack with gradual reveal, iceberg annotations, three-stage review, setup/payoff foreshadow tracking, and scene-type directing.",
                "stargazers_count": 62,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["novel", "writing", "opencode", "chinese"],
                "updated_at": "2026-06-06T17:56:32Z",
                "root_files": ["install.sh", "uninstall.sh", "skills"],
            },
            {
                "full_name": "ypcypc/WhatIf",
                "html_url": "https://github.com/ypcypc/WhatIf",
                "description": "Extract structured world data from a Chinese novel into WorldPkg, then support player choices, divergence guidance, alternative timeline management, scene adaptation, and memory compression.",
                "stargazers_count": 187,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "lorebook", "game", "ai"],
                "updated_at": "2026-06-08T13:11:30Z",
                "root_files": ["start.py", "backend", "frontend", "tools"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-09T18:40:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert {
        "premature_ending_guard",
        "layered_memory_model",
        "plot_dependency_graph",
    }.issubset(by_title["doctoroyy/novel-copilot"]["absorbed_patterns"])
    assert {
        "plotgrid_scene_matrix",
        "plotline_thread_tracking",
        "scene_status_dashboard",
    }.issubset(by_title["PixeroJan/obsidian-storyline"]["absorbed_patterns"])
    assert {
        "gradual_reveal_control",
        "setup_payoff_tracking",
        "scene_type_directing",
    }.issubset(by_title["skyfiredao/dreampowers"]["absorbed_patterns"])
    assert {
        "worldpkg_export",
        "alternate_timeline_branching",
        "divergence_guidance",
    }.issubset(by_title["ypcypc/WhatIf"]["absorbed_patterns"])


def test_current_writing_tool_pattern_pack_exposes_new_guidance_sections():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-09T18:45:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/doctoroyy/novel-copilot",
                "title": "doctoroyy/novel-copilot",
                "summary": "Three-layer memory, plot graph, and premature ending detection.",
                "stars": 9,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["shell_script"],
                "absorbed_patterns": ["premature_ending_guard", "layered_memory_model", "plot_dependency_graph"],
                "score": 94,
            },
            {
                "source": "github",
                "url": "https://github.com/PixeroJan/obsidian-storyline",
                "title": "PixeroJan/obsidian-storyline",
                "summary": "Plotgrid, timeline, plotlines, scene status, characters and locations.",
                "stars": 168,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["browser_extension"],
                "absorbed_patterns": ["plotgrid_scene_matrix", "plotline_thread_tracking", "scene_status_dashboard"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/skyfiredao/dreampowers",
                "title": "skyfiredao/dreampowers",
                "summary": "Gradual reveal, iceberg annotations, three-stage chapter review, setup/payoff tracking, and scene-type directing.",
                "stars": 62,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["shell_script"],
                "absorbed_patterns": ["gradual_reveal_control", "setup_payoff_tracking", "scene_type_directing"],
                "score": 91,
            },
            {
                "source": "github",
                "url": "https://github.com/ypcypc/WhatIf",
                "title": "ypcypc/WhatIf",
                "summary": "WorldPkg extraction, choice-driven divergence, alternative timelines, scene adaptation and memory compression.",
                "stars": 187,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["worldpkg_export", "alternate_timeline_branching", "divergence_guidance"],
                "score": 88,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "anti_ending_checks" in pattern_pack["whole_book_analysis_targets"]
    assert "plot_dependency_edges" in pattern_pack["bible_enrichment_targets"]
    assert "plotgrid_scene_matrix" in pattern_pack["whole_book_analysis_targets"]
    assert "setup_payoff_ledger" in pattern_pack["bible_enrichment_targets"]
    assert "reveal_budget" in pattern_pack["bible_enrichment_targets"]
    assert "worldpkg_exports" in pattern_pack["whole_book_analysis_targets"]
    assert "premature_ending_guard_hints" in pattern_pack
    assert "plotgrid_scene_matrix_hints" in pattern_pack
    assert "gradual_reveal_control_hints" in pattern_pack
    assert "setup_payoff_tracking_hints" in pattern_pack
    assert "scene_type_directing_hints" in pattern_pack
    assert "alternate_timeline_branching_hints" in pattern_pack
    assert "divergence_guidance_hints" in pattern_pack
    assert "worldpkg_export_hints" in pattern_pack
    assert "ending_guard_remap" in pattern_pack["inspired_mapping_targets"]
    assert "plotline_matrix_remap" in pattern_pack["inspired_mapping_targets"]
    assert "reveal_budget_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "premature_ending_guard_hints" in digest
    assert "plotgrid_scene_matrix_hints" in digest
    assert "setup_payoff_tracking_hints" in digest
    assert "alternate_timeline_branching_hints" in digest


def test_acceptance_loop_sources_map_to_context_memory_critic_and_resume_patterns():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "YfengJ/novel-studio-ai",
                "html_url": "https://github.com/YfengJ/novel-studio-ai",
                "description": "Local-first AI long-form fiction workbench.",
                "stargazers_count": 0,
                "license": None,
                "topics": ["fiction-writing", "novel", "story-bible"],
                "updated_at": "2026-06-09T14:52:52Z",
            },
            {
                "full_name": "davealaw/FictionRefine",
                "html_url": "https://github.com/davealaw/FictionRefine",
                "description": "A two-LLM workflow for iterative story generation and improvement.",
                "stargazers_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["fiction", "llm", "revision"],
                "updated_at": "2026-06-09T10:00:00Z",
            },
            {
                "full_name": "worldwonderer/oh-story-claudecode",
                "html_url": "https://github.com/worldwonderer/oh-story-claudecode",
                "description": "Web novel skill pack for trend scanning, deconstruction, writing and AI tone removal.",
                "stargazers_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["webnovel", "skill", "writing"],
                "updated_at": "2026-06-09T10:00:00Z",
            },
            {
                "full_name": "PenglongHuang/chinese-novelist-skill",
                "html_url": "https://github.com/PenglongHuang/chinese-novelist-skill",
                "description": "Chinese novelist skill with preference memory, interrupted continuation, auto validation and auto rewrite.",
                "stargazers_count": 0,
                "license": None,
                "topics": ["novel", "claude-code-skill"],
                "updated_at": "2026-06-09T10:00:00Z",
            },
            {
                "full_name": "GOAT-AI-lab/GOAT-Storytelling-Agent",
                "html_url": "https://github.com/GOAT-AI-lab/GOAT-Storytelling-Agent",
                "description": "Agent for writing consistent long stories with top-down planning from book spec to chapter scenes.",
                "stargazers_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["storytelling", "agent", "novel"],
                "updated_at": "2026-06-09T10:00:00Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-09T18:00:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }
    assert {
        "context_pack_preview",
        "accepted_chapter_memory",
        "context_reference",
    }.issubset(patterns_by_title["YfengJ/novel-studio-ai"])
    assert {
        "critic_verifier_loop",
        "collapse_prevention",
        "self_review",
    }.issubset(patterns_by_title["davealaw/FictionRefine"])
    assert {
        "trend_deconstruction_pipeline",
        "anti_ai_tone_polish",
    }.issubset(patterns_by_title["worldwonderer/oh-story-claudecode"])
    assert {
        "preference_memory",
        "interrupted_resume_flow",
        "auto_validation_rewrite",
    }.issubset(patterns_by_title["PenglongHuang/chinese-novelist-skill"])
    assert "top_down_story_planning" in patterns_by_title[
        "GOAT-AI-lab/GOAT-Storytelling-Agent"
    ]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "context_pack_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "accepted_chapter_memory_log" in pattern_pack["whole_book_analysis_targets"]
    assert "critic_review_reports" in pattern_pack["whole_book_analysis_targets"]
    assert "collapse_risk_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "trend_deconstruction_notes" in pattern_pack["whole_book_analysis_targets"]
    assert "anti_ai_tone_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "user_preference_memory" in pattern_pack["whole_book_analysis_targets"]
    assert "resume_checkpoint" in pattern_pack["whole_book_analysis_targets"]
    assert "auto_validation_results" in pattern_pack["whole_book_analysis_targets"]
    assert "book_spec" in pattern_pack["whole_book_analysis_targets"]
    assert "context_pack_preview_hints" in pattern_pack
    assert "accepted_chapter_memory_hints" in pattern_pack
    assert "critic_verifier_loop_hints" in pattern_pack
    assert "collapse_prevention_hints" in pattern_pack
    assert "trend_deconstruction_pipeline_hints" in pattern_pack
    assert "anti_ai_tone_polish_hints" in pattern_pack
    assert "preference_memory_hints" in pattern_pack
    assert "interrupted_resume_flow_hints" in pattern_pack
    assert "auto_validation_rewrite_hints" in pattern_pack
    assert "top_down_story_planning_hints" in pattern_pack
    assert "context_pack_boundary" in pattern_pack["inspired_mapping_targets"]
    assert "trope_module_remap" in pattern_pack["inspired_mapping_targets"]
    assert "plan_hierarchy_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "context_pack_preview_hints" in digest
    assert "accepted_chapter_memory_hints" in digest
    assert "critic_verifier_loop_hints" in digest
    assert "collapse_prevention_hints" in digest
    assert "trend_deconstruction_pipeline_hints" in digest
    assert "anti_ai_tone_polish_hints" in digest
    assert "preference_memory_hints" in digest
    assert "interrupted_resume_flow_hints" in digest
    assert "auto_validation_rewrite_hints" in digest
    assert "top_down_story_planning_hints" in digest


def test_default_discovery_sources_include_acceptance_loop_projects():
    assert "https://github.com/YfengJ/novel-studio-ai" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/davealaw/FictionRefine" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ShmilyWithme/Shmily_novel_skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/worldwonderer/oh-story-claudecode" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/PenglongHuang/chinese-novelist-skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/GOAT-AI-lab/GOAT-Storytelling-Agent" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("context pack" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("critic model" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("trend scanning" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("interrupted continuation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("book spec" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_mature_writing_tool_sources_map_to_manuscript_planning_patterns():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "vkbo/novelWriter",
                "html_url": "https://github.com/vkbo/novelWriter",
                "description": "Plain text novel editor with comments, synopsis, cross-referencing and human readable files.",
                "stargazers_count": 2600,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["novel", "writing", "plain-text"],
                "updated_at": "2026-06-09T10:00:00Z",
            },
            {
                "full_name": "olivierkes/manuskript",
                "html_url": "https://github.com/olivierkes/manuskript",
                "description": "Writer tool with Snowflake Method, outliner, index cards, characters, plots, worldbuilding, story line and export formats.",
                "stargazers_count": 2800,
                "license": {"spdx_id": "GPL-3.0-or-later"},
                "topics": ["writing", "novel", "outliner"],
                "updated_at": "2026-06-09T10:00:00Z",
            },
            {
                "full_name": "andreafeccomandi/bibisco",
                "html_url": "https://github.com/andreafeccomandi/bibisco",
                "description": "Novel writing software with chapters, scenes, revisions, premise, fabula, narrative strands, settings and believable characters.",
                "stargazers_count": 1800,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["novel", "writing", "characters"],
                "updated_at": "2026-06-09T10:00:00Z",
            },
            {
                "full_name": "wavemakercards/wavemaker-cards-v4",
                "html_url": "https://github.com/wavemakercards/wavemaker-cards-v4",
                "description": "Creative writing suite with mind mapping, timeline planning, grid planner, character tracking, plot points and Snowflake Method.",
                "stargazers_count": 800,
                "license": {"spdx_id": "MIT"},
                "topics": ["creative-writing", "novel", "planning"],
                "updated_at": "2026-06-09T10:00:00Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-09T20:10:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }
    assert {
        "plain_text_project_storage",
        "synopsis_cross_reference",
    }.issubset(patterns_by_title["vkbo/novelWriter"])
    assert {
        "snowflake_premise_expansion",
        "outliner_index_cards",
        "manuscript_export_formats",
    }.issubset(patterns_by_title["olivierkes/manuskript"])
    assert {
        "narrative_strand_mapping",
        "character_depth_interview",
    }.issubset(patterns_by_title["andreafeccomandi/bibisco"])
    assert {
        "mindmap_visual_planning",
        "snowflake_premise_expansion",
        "outliner_index_cards",
    }.issubset(patterns_by_title["wavemakercards/wavemaker-cards-v4"])


def test_mature_writing_tool_pattern_pack_exposes_manuscript_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-09T20:15:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/vkbo/novelWriter",
                "title": "vkbo/novelWriter",
                "summary": "Plain text project storage, synopsis, comments and cross-referencing.",
                "stars": 2600,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["plain_text_project_storage", "synopsis_cross_reference"],
                "score": 92,
            },
            {
                "source": "github",
                "url": "https://github.com/olivierkes/manuskript",
                "title": "olivierkes/manuskript",
                "summary": "Snowflake premise expansion, outliner, index cards, story line and export formats.",
                "stars": 2800,
                "license": "GPL-3.0-or-later",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["snowflake_premise_expansion", "outliner_index_cards", "manuscript_export_formats"],
                "score": 91,
            },
            {
                "source": "github",
                "url": "https://github.com/andreafeccomandi/bibisco",
                "title": "andreafeccomandi/bibisco",
                "summary": "Premise, fabula, narrative strands, setting context and believable character depth.",
                "stars": 1800,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["narrative_strand_mapping", "character_depth_interview"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/wavemakercards/wavemaker-cards-v4",
                "title": "wavemakercards/wavemaker-cards-v4",
                "summary": "Mind mapping, timeline planning, grid planner, character tracking and Snowflake Method.",
                "stars": 800,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["mindmap_visual_planning", "snowflake_premise_expansion", "outliner_index_cards"],
                "score": 89,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "manuscript_text_units" in pattern_pack["whole_book_analysis_targets"]
    assert "synopsis_cross_refs" in pattern_pack["whole_book_analysis_targets"]
    assert "snowflake_premise_chain" in pattern_pack["whole_book_analysis_targets"]
    assert "index_card_board" in pattern_pack["whole_book_analysis_targets"]
    assert "narrative_strands" in pattern_pack["whole_book_analysis_targets"]
    assert "character_depth_interviews" in pattern_pack["whole_book_analysis_targets"]
    assert "mindmap_nodes" in pattern_pack["whole_book_analysis_targets"]
    assert "export_format_targets" in pattern_pack["whole_book_analysis_targets"]
    assert "plain_text_project_storage_hints" in pattern_pack
    assert "synopsis_cross_reference_hints" in pattern_pack
    assert "snowflake_premise_expansion_hints" in pattern_pack
    assert "outliner_index_cards_hints" in pattern_pack
    assert "narrative_strand_mapping_hints" in pattern_pack
    assert "character_depth_interview_hints" in pattern_pack
    assert "mindmap_visual_planning_hints" in pattern_pack
    assert "manuscript_export_formats_hints" in pattern_pack
    assert "premise_chain_remap" in pattern_pack["inspired_mapping_targets"]
    assert "narrative_strand_remap" in pattern_pack["inspired_mapping_targets"]
    assert "character_depth_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "plain_text_project_storage_hints" in digest
    assert "synopsis_cross_reference_hints" in digest
    assert "snowflake_premise_expansion_hints" in digest
    assert "outliner_index_cards_hints" in digest
    assert "narrative_strand_mapping_hints" in digest
    assert "character_depth_interview_hints" in digest
    assert "mindmap_visual_planning_hints" in digest
    assert "manuscript_export_formats_hints" in digest


def test_default_discovery_sources_include_mature_writing_tools():
    assert "https://github.com/vkbo/novelWriter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/olivierkes/manuskript" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/andreafeccomandi/bibisco" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/wavemakercards/wavemaker-cards-v4" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("plain text" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("snowflake method" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("narrative strands" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("mind mapping" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_inspectable_rewrite_sources_map_to_trace_and_adaptive_patterns():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "Narcooo/inkos",
                "html_url": "https://github.com/Narcooo/inkos",
                "description": "Story creation AI agent with review list, approve-all, continuity auditor, intent.md, context.json, rule-stack.yaml, trace.json, Zod schema and JSON delta validation.",
                "stargazers_count": 7046,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["story", "novel", "writing-agent"],
                "updated_at": "2026-06-09T11:22:23Z",
            },
            {
                "full_name": "MaoXiaoYuZ/Long-Novel-GPT",
                "html_url": "https://github.com/MaoXiaoYuZ/Long-Novel-GPT",
                "description": "Long novel GPT with LLM and RAG, import existing novel, retrieve relevant body snippets and plot outline, modify text snippets and sync update outline.",
                "stargazers_count": 1152,
                "license": {"spdx_id": "unknown"},
                "topics": ["long-novel", "rag", "writing"],
                "updated_at": "2026-06-08T15:08:16Z",
            },
            {
                "full_name": "dylanhogg/gptauthor",
                "html_url": "https://github.com/dylanhogg/gptauthor",
                "description": "Long form multi-chapter stories with human review of synopsis, chapter summaries, previous chapter context, Markdown and HTML export.",
                "stargazers_count": 108,
                "license": {"spdx_id": "MIT"},
                "topics": ["fiction", "story", "chapters"],
                "updated_at": "2026-05-31T23:48:56Z",
            },
            {
                "full_name": "kevboh/longform",
                "html_url": "https://github.com/kevboh/longform",
                "description": "Obsidian longform plugin with ordered manuscript, reorderable nestable scenes, word counts, writing session goals and workflow-based compilation.",
                "stargazers_count": 936,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["obsidian", "novel", "manuscript"],
                "updated_at": "2026-06-09T07:04:52Z",
            },
            {
                "full_name": "principia-ai/WriteHERE",
                "html_url": "https://github.com/principia-ai/WriteHERE",
                "description": "Long-form writing with recursive planning, recursive task decomposition, heterogeneous integration of retrieval, reasoning, and composition, and dynamic adaptation.",
                "stargazers_count": 930,
                "license": {"spdx_id": "unknown"},
                "topics": ["writing", "planning", "fiction"],
                "updated_at": "2026-06-07T12:40:34Z",
            },
            {
                "full_name": "iLearn-Lab/NovelClaw",
                "html_url": "https://github.com/iLearn-Lab/NovelClaw",
                "description": "Inspectable writing workspace with inspectable runs, sessions, storyboards, manuscript surfaces, character and world views, editable memory banks and memory-aware writing control.",
                "stargazers_count": 319,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "memory", "workspace"],
                "updated_at": "2026-06-09T11:15:43Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-09T21:10:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }
    assert {
        "runtime_artifact_trace",
        "schema_validated_state_delta",
        "self_review",
    }.issubset(patterns_by_title["Narcooo/inkos"])
    assert {
        "retrieval_guided_span_rewrite",
        "book_decomposition",
        "context_reference",
    }.issubset(patterns_by_title["MaoXiaoYuZ/Long-Novel-GPT"])
    assert {
        "human_synopsis_gate",
        "chapter_generation",
        "manuscript_export_formats",
    }.issubset(patterns_by_title["dylanhogg/gptauthor"])
    assert {
        "workflow_manuscript_compilation",
        "writing_session_goal_tracking",
        "outliner_index_cards",
    }.issubset(patterns_by_title["kevboh/longform"])
    assert "recursive_adaptive_planning" in patterns_by_title["principia-ai/WriteHERE"]
    assert "inspectable_run_workspace" in patterns_by_title["iLearn-Lab/NovelClaw"]


def test_inspectable_rewrite_pattern_pack_exposes_trace_and_adaptive_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-09T21:15:00+08:00",
        "candidate_count": 6,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/Narcooo/inkos",
                "title": "Narcooo/inkos",
                "summary": "Review gates, runtime artifacts, Zod schema and state delta validation.",
                "stars": 7046,
                "license": "AGPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["runtime_artifact_trace", "schema_validated_state_delta", "self_review"],
                "score": 96,
            },
            {
                "source": "github",
                "url": "https://github.com/MaoXiaoYuZ/Long-Novel-GPT",
                "title": "MaoXiaoYuZ/Long-Novel-GPT",
                "summary": "Retrieve relevant spans and outline, rewrite spans, sync outline.",
                "stars": 1152,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker", "shell_script"],
                "absorbed_patterns": ["retrieval_guided_span_rewrite", "context_reference"],
                "score": 94,
            },
            {
                "source": "github",
                "url": "https://github.com/dylanhogg/gptauthor",
                "title": "dylanhogg/gptauthor",
                "summary": "Human synopsis gate and multi-chapter export.",
                "stars": 108,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["human_synopsis_gate", "chapter_generation", "manuscript_export_formats"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/kevboh/longform",
                "title": "kevboh/longform",
                "summary": "Workflow-based compilation, ordered scenes, word counts and writing goals.",
                "stars": 936,
                "license": "NOASSERTION",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["browser_extension"],
                "absorbed_patterns": ["workflow_manuscript_compilation", "writing_session_goal_tracking"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/principia-ai/WriteHERE",
                "title": "principia-ai/WriteHERE",
                "summary": "Recursive planning and dynamic adaptation.",
                "stars": 930,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["recursive_adaptive_planning"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/iLearn-Lab/NovelClaw",
                "title": "iLearn-Lab/NovelClaw",
                "summary": "Inspectable runs, sessions, storyboards, manuscript surfaces and editable memory banks.",
                "stars": 319,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker", "shell_script", "powershell_script", "native_binary"],
                "absorbed_patterns": ["inspectable_run_workspace", "memory_snapshot_versioning"],
                "score": 82,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "synopsis_review_gate" in pattern_pack["whole_book_analysis_targets"]
    assert "retrieved_text_spans" in pattern_pack["whole_book_analysis_targets"]
    assert "runtime_intent_artifact" in pattern_pack["whole_book_analysis_targets"]
    assert "validated_state_delta_schema" in pattern_pack["whole_book_analysis_targets"]
    assert "adaptive_task_tree" in pattern_pack["whole_book_analysis_targets"]
    assert "manuscript_compile_steps" in pattern_pack["whole_book_analysis_targets"]
    assert "writing_session_goal" in pattern_pack["whole_book_analysis_targets"]
    assert "inspectable_run_sessions" in pattern_pack["whole_book_analysis_targets"]
    assert "human_synopsis_gate_hints" in pattern_pack
    assert "retrieval_guided_span_rewrite_hints" in pattern_pack
    assert "runtime_artifact_trace_hints" in pattern_pack
    assert "schema_validated_state_delta_hints" in pattern_pack
    assert "recursive_adaptive_planning_hints" in pattern_pack
    assert "workflow_manuscript_compilation_hints" in pattern_pack
    assert "writing_session_goal_tracking_hints" in pattern_pack
    assert "inspectable_run_workspace_hints" in pattern_pack
    assert "synopsis_gate_remap" in pattern_pack["inspired_mapping_targets"]
    assert "retrieval_span_remap" in pattern_pack["inspired_mapping_targets"]
    assert "adaptive_task_tree_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "human_synopsis_gate_hints" in digest
    assert "retrieval_guided_span_rewrite_hints" in digest
    assert "runtime_artifact_trace_hints" in digest
    assert "schema_validated_state_delta_hints" in digest
    assert "recursive_adaptive_planning_hints" in digest
    assert "workflow_manuscript_compilation_hints" in digest
    assert "writing_session_goal_tracking_hints" in digest
    assert "inspectable_run_workspace_hints" in digest


def test_default_discovery_sources_include_inspectable_rewrite_projects():
    assert "https://github.com/Narcooo/inkos" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/MaoXiaoYuZ/Long-Novel-GPT" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/dylanhogg/gptauthor" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/kevboh/longform" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/principia-ai/WriteHERE" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/iLearn-Lab/NovelClaw" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("human review of synopsis" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("retrieve relevant" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("intent.md" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("recursive planning" in query.lower() for query in DEFAULT_GITHUB_QUERIES)



def test_production_review_projects_map_to_continuity_voice_and_review_patterns():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "howells/fiction",
                "html_url": "https://github.com/howells/fiction",
                "description": "Fiction writing plugin with specialized agents for architecture, characters, prose, review, editing, continuity and publishing prep; progress.md continuity state and chapter review.",
                "stargazers_count": 512,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["fiction", "novel", "claude-code"],
                "updated_at": "2026-06-09T21:40:00Z",
            },
            {
                "full_name": "mjbae/awesome-novel-studio",
                "html_url": "https://github.com/mjbae/awesome-novel-studio",
                "description": "Web novel production pipeline propose design create polish rewrite, continuity bridge from previous 2 episodes, voice table, polish axes and episode range rewrite impact scope.",
                "stargazers_count": 248,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["web-novel", "writing", "agents"],
                "updated_at": "2026-06-09T21:41:00Z",
            },
            {
                "full_name": "danjdewhurst/story-skills",
                "html_url": "https://github.com/danjdewhurst/story-skills",
                "description": "Fiction project format in plain markdown with YAML frontmatter for story bible, character files, scene state, continuity questions, promises/payoffs, timelines and chapter drafts.",
                "stargazers_count": 120,
                "license": {"spdx_id": "MIT"},
                "topics": ["fiction", "story-bible", "agent-skills"],
                "updated_at": "2026-06-09T21:42:00Z",
            },
            {
                "full_name": "hestudy/snowflake-fiction",
                "html_url": "https://github.com/hestudy/snowflake-fiction",
                "description": "Chinese novel plugin using Snowflake method, scene plan partial rerun, chapter-write continuation, boring-detect, opening check, quality check and novel review.",
                "stargazers_count": 310,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "writing", "snowflake"],
                "updated_at": "2026-06-09T21:43:00Z",
            },
            {
                "full_name": "forsonny/The-Crucible-Writing-System-For-Claude",
                "html_url": "https://github.com/forsonny/The-Crucible-Writing-System-For-Claude",
                "description": "Epic fantasy novel system with 36-beat framework, three interwoven strands, scene-by-scene drafting, bi-chapter review, anti-hallucination verification against planning documents and automatic backups.",
                "stargazers_count": 90,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "fiction", "claude"],
                "updated_at": "2026-06-09T21:44:00Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-09T21:45:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }

    assert "craft_role_pipeline" in patterns_by_title["howells/fiction"]
    assert "continuity_bridge_window" in patterns_by_title["mjbae/awesome-novel-studio"]
    assert "episode_range_rewrite_scope" in patterns_by_title["mjbae/awesome-novel-studio"]
    assert "voice_table_polish_axis" in patterns_by_title["mjbae/awesome-novel-studio"]
    assert "frontmatter_story_schema" in patterns_by_title["danjdewhurst/story-skills"]
    assert "boring_opening_quality_gates" in patterns_by_title["hestudy/snowflake-fiction"]
    assert "beat_strand_framework" in patterns_by_title["forsonny/The-Crucible-Writing-System-For-Claude"]
    assert "anti_hallucination_plan_check" in patterns_by_title["forsonny/The-Crucible-Writing-System-For-Claude"]
    assert "backup_restore_checkpoint" in patterns_by_title["forsonny/The-Crucible-Writing-System-For-Claude"]


def test_production_review_pattern_pack_exposes_continuity_voice_and_audit_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-09T21:50:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/howells/fiction",
                "title": "howells/fiction",
                "summary": "Specialized craft agents, progress.md session tracking and continuity state.",
                "stars": 512,
                "license": "NOASSERTION",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["craft_role_pipeline", "continuation", "chapter_generation"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/mjbae/awesome-novel-studio",
                "title": "mjbae/awesome-novel-studio",
                "summary": "Continuity bridge, voice table and episode range rewrite impact scope.",
                "stars": 248,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["continuity_bridge_window", "voice_table_polish_axis", "episode_range_rewrite_scope"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/danjdewhurst/story-skills",
                "title": "danjdewhurst/story-skills",
                "summary": "YAML frontmatter, continuity questions, promises/payoffs and chapter drafts.",
                "stars": 120,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["frontmatter_story_schema", "setup_payoff_tracking"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/hestudy/snowflake-fiction",
                "title": "hestudy/snowflake-fiction",
                "summary": "Boring detect, opening check and quality review for web novel chapters.",
                "stars": 310,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["boring_opening_quality_gates", "auto_validation_rewrite"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/forsonny/The-Crucible-Writing-System-For-Claude",
                "title": "forsonny/The-Crucible-Writing-System-For-Claude",
                "summary": "36-beat framework, interwoven strands, anti-hallucination checks and restore checkpoints.",
                "stars": 90,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["beat_strand_framework", "anti_hallucination_plan_check", "backup_restore_checkpoint"],
                "score": 82,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "continuity_bridge_window" in pattern_pack["whole_book_analysis_targets"]
    assert "voice_table" in pattern_pack["whole_book_analysis_targets"]
    assert "frontmatter_story_schema" in pattern_pack["whole_book_analysis_targets"]
    assert "plan_verification_results" in pattern_pack["whole_book_analysis_targets"]
    assert "backup_restore_points" in pattern_pack["whole_book_analysis_targets"]
    assert "craft_role_pipeline_hints" in pattern_pack
    assert "frontmatter_story_schema_hints" in pattern_pack
    assert "continuity_bridge_window_hints" in pattern_pack
    assert "voice_table_polish_axis_hints" in pattern_pack
    assert "anti_hallucination_plan_check_hints" in pattern_pack
    assert "voice_table_remap" in pattern_pack["inspired_mapping_targets"]
    assert "continuity_bridge_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "craft_role_pipeline_hints" in digest
    assert "continuity_bridge_window_hints" in digest
    assert "voice_table_polish_axis_hints" in digest
    assert "anti_hallucination_plan_check_hints" in digest


def test_default_discovery_sources_include_production_review_projects():
    assert "https://github.com/howells/fiction" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/mjbae/awesome-novel-studio" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/danjdewhurst/story-skills" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/hestudy/snowflake-fiction" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/forsonny/The-Crucible-Writing-System-For-Claude" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/XuanRanL/webnovel-writer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/forsonny/book-os" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/forjd/better-writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/EdwardAThomson/NovelWriter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("continuity bridge" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("yaml frontmatter" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("anti-hallucination" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("voice calibration" in query.lower() for query in DEFAULT_GITHUB_QUERIES)



def test_consistency_sourcebook_projects_map_to_retrieval_audit_and_stylometry_patterns():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "StableLlamaAI/AugmentedQuill",
                "html_url": "https://github.com/StableLlamaAI/AugmentedQuill",
                "description": "Local-first AI writing assistant with story structure chatbot, Writing Partner, sourcebook entries, project-based story authoring, multi-chapter and multi-book structure, author in the driver seat.",
                "stargazers_count": 77,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["novel", "writing", "sourcebook"],
                "updated_at": "2026-06-09T22:20:00Z",
            },
            {
                "full_name": "AutoFiction-AI/AutoFiction",
                "html_url": "https://github.com/AutoFiction-AI/AutoFiction",
                "description": "Long-form AI novel pipeline with premise, outline, parallel chapter drafting, chapter reviews, full-book review, cross-chapter audit, aggregate findings, revision cycles, weak causality and cross-chapter redundancy checks.",
                "stargazers_count": 902,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["novel", "fiction", "agentic"],
                "updated_at": "2026-06-09T22:21:00Z",
            },
            {
                "full_name": "YILING0013/AI_NovelGenerator",
                "html_url": "https://github.com/YILING0013/AI_NovelGenerator",
                "description": "Novel generator with semantic search engine, vector-based long-term context consistency, knowledge base integration, state tracking, foreshadowing, automatic proofreading, plot contradictions and logical conflicts.",
                "stargazers_count": 1860,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["novel", "rag", "writing"],
                "updated_at": "2026-06-09T22:22:00Z",
            },
            {
                "full_name": "Picrew/ConStory-Bench",
                "html_url": "https://github.com/Picrew/ConStory-Bench",
                "description": "Long story narrative consistency benchmark and ConStory-Checker for consistency errors: characterization, factual detail, narrative style, timeline & plot, world-building & setting, causality violations and abandoned plots.",
                "stargazers_count": 410,
                "license": {"spdx_id": "MIT"},
                "topics": ["story-generation", "benchmark", "consistency"],
                "updated_at": "2026-06-09T22:23:00Z",
            },
            {
                "full_name": "harshaneel/humanize",
                "html_url": "https://github.com/harshaneel/humanize",
                "description": "Static AI text humanization skill using perplexity, burstiness, stylometry, discourse, watermarking, nine humanization levers, specificity insertion, AI-transition removal and factual guardrails.",
                "stargazers_count": 215,
                "license": {"spdx_id": "MIT"},
                "topics": ["writing", "humanize", "ai-detection"],
                "updated_at": "2026-06-09T22:24:00Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-09T22:25:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }

    assert "sourcebook_author_workbench" in patterns_by_title["StableLlamaAI/AugmentedQuill"]
    assert "author_control_boundary" in patterns_by_title["StableLlamaAI/AugmentedQuill"]
    assert "parallel_agent_chapter_pipeline" in patterns_by_title["AutoFiction-AI/AutoFiction"]
    assert "cross_chapter_redundancy_audit" in patterns_by_title["AutoFiction-AI/AutoFiction"]
    assert "semantic_long_context_search" in patterns_by_title["YILING0013/AI_NovelGenerator"]
    assert "contradiction_taxonomy_checker" in patterns_by_title["YILING0013/AI_NovelGenerator"]
    assert "contradiction_taxonomy_checker" in patterns_by_title["Picrew/ConStory-Bench"]
    assert "humanization_stylometry_levers" in patterns_by_title["harshaneel/humanize"]


def test_consistency_sourcebook_pattern_pack_exposes_audit_and_context_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-09T22:30:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/StableLlamaAI/AugmentedQuill",
                "title": "StableLlamaAI/AugmentedQuill",
                "summary": "Sourcebook entries, Writing Partner and author-in-the-driver-seat boundary.",
                "stars": 77,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["postinstall"],
                "absorbed_patterns": ["sourcebook_author_workbench", "author_control_boundary", "local_first_novel_workspace"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/AutoFiction-AI/AutoFiction",
                "title": "AutoFiction-AI/AutoFiction",
                "summary": "Parallel chapter drafting, full-book review, cross-chapter audit, aggregate findings and revision cycles.",
                "stars": 902,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["parallel_agent_chapter_pipeline", "cross_chapter_redundancy_audit", "workflow_agent_pipeline"],
                "score": 92,
            },
            {
                "source": "github",
                "url": "https://github.com/YILING0013/AI_NovelGenerator",
                "title": "YILING0013/AI_NovelGenerator",
                "summary": "Semantic search, vector long-term context consistency, knowledge base refs and automatic proofreading of contradictions.",
                "stars": 1860,
                "license": "AGPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["shell_script"],
                "absorbed_patterns": ["semantic_long_context_search", "contradiction_taxonomy_checker", "context_reference"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/Picrew/ConStory-Bench",
                "title": "Picrew/ConStory-Bench",
                "summary": "ConStory Checker detects narrative consistency bugs across characterization, factual detail, narrative style, timeline/plot, and world rules.",
                "stars": 410,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["contradiction_taxonomy_checker", "collapse_prevention"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/harshaneel/humanize",
                "title": "harshaneel/humanize",
                "summary": "Perplexity, burstiness, stylometry, discourse and nine humanization levers for static AI text humanization.",
                "stars": 215,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["shell_script"],
                "absorbed_patterns": ["humanization_stylometry_levers", "anti_ai_tone_polish", "prose_preflight_voice_calibration"],
                "score": 82,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "sourcebook_entries" in pattern_pack["whole_book_analysis_targets"]
    assert "semantic_context_hits" in pattern_pack["whole_book_analysis_targets"]
    assert "consistency_bug_taxonomy" in pattern_pack["whole_book_analysis_targets"]
    assert "parallel_chapter_jobs" in pattern_pack["whole_book_analysis_targets"]
    assert "cross_chapter_redundancy_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "stylometry_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "sourcebook_author_workbench_hints" in pattern_pack
    assert "semantic_long_context_search_hints" in pattern_pack
    assert "contradiction_taxonomy_checker_hints" in pattern_pack
    assert "parallel_agent_chapter_pipeline_hints" in pattern_pack
    assert "cross_chapter_redundancy_audit_hints" in pattern_pack
    assert "humanization_stylometry_levers_hints" in pattern_pack
    assert "sourcebook_remap" in pattern_pack["inspired_mapping_targets"]
    assert "semantic_context_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "sourcebook_author_workbench_hints" in digest
    assert "contradiction_taxonomy_checker_hints" in digest
    assert "cross_chapter_redundancy_audit_hints" in digest
    assert "humanization_stylometry_levers_hints" in digest


def test_default_discovery_sources_include_consistency_sourcebook_projects():
    assert "https://github.com/StableLlamaAI/AugmentedQuill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/AutoFiction-AI/AutoFiction" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/YILING0013/AI_NovelGenerator" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Picrew/ConStory-Bench" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/harshaneel/humanize" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("sourcebook" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("narrative consistency" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("cross-chapter redundancy" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("perplexity" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_research_multimodal_experiment_projects_are_classified_as_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "Picrew/awesome-llm-story-generation",
                "html_url": "https://github.com/Picrew/awesome-llm-story-generation",
                "description": "Curated list of LLM story/novel/script generation research with planning / decomposition, agent collaboration, sandbox / world simulation, multimodal story generation and evaluation / benchmark categories.",
                "stargazers_count": 80,
                "license": None,
                "topics": ["story-generation", "llm", "novel"],
                "updated_at": "2026-06-09T07:56:32Z",
            },
            {
                "full_name": "Anning01/novelvids",
                "html_url": "https://github.com/Anning01/novelvids",
                "description": "AI 驱动的小说转短剧全流程生产平台：章节拆分、实体提取、角色参考图、分镜、storyboard and video synthesis.",
                "stargazers_count": 219,
                "license": None,
                "topics": ["novel", "video", "storyboard"],
                "updated_at": "2026-05-30T06:12:51Z",
                "root_files": ["pyproject.toml", "main.py", "README.md"],
            },
            {
                "full_name": "MemeCalculate/moyin-creator",
                "html_url": "https://github.com/MemeCalculate/moyin-creator",
                "description": "AI film production tool with script to characters, scenes, director decisions, storyboard, shot planning and final video.",
                "stargazers_count": 3760,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["film-production", "script", "storyboard"],
                "updated_at": "2026-06-09T12:29:33Z",
                "root_files": ["package.json", "electron-builder.yml", "README.md"],
                "package_scripts": {"postinstall": "node scripts/postinstall.js"},
            },
            {
                "full_name": "jncchds/abook",
                "html_url": "https://github.com/jncchds/abook",
                "description": "Agentic book planner with seven agents: Story Bible, Characters, Plot Threads, Chapter Outlines, Writer, Editor and Continuity Checker; RAG context retrieval, full synopsis spine, anti-repetition rules and token stats.",
                "stargazers_count": 430,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["novel", "writing", "rag"],
                "updated_at": "2026-06-09T09:00:00Z",
                "root_files": ["docker-compose.yml", "Dockerfile", "README.md"],
            },
            {
                "full_name": "Prompt-And-Circumstance/StoryMode",
                "html_url": "https://github.com/Prompt-And-Circumstance/StoryMode",
                "description": "SillyTavern extension with 43 genres, story style, author style, mix-and-match settings, narrative arc and scenario blueprint schema.",
                "stargazers_count": 140,
                "license": None,
                "topics": ["story", "fiction", "sillytavern"],
                "updated_at": "2026-06-09T09:30:00Z",
                "root_files": ["package.json", "manifest.json", "README.md"],
            },
            {
                "full_name": "brianlmerritt/explore_writing",
                "html_url": "https://github.com/brianlmerritt/explore_writing",
                "description": "Writing experiment harness with prompt recipes, temperature grid, sampling parameter quality sweep, write/review/top_writing phases and append-only resumable TSV logs.",
                "stargazers_count": 35,
                "license": {"spdx_id": "MIT"},
                "topics": ["writing", "experiments"],
                "updated_at": "2026-06-09T10:00:00Z",
                "root_files": ["requirements.txt", "README.md"],
            },
            {
                "full_name": "forsonny/novel-master-ai",
                "html_url": "https://github.com/forsonny/novel-master-ai",
                "description": "Novel Master AI uses NRD task tree pipeline across arcs/chapters/scenes, revision passes, tagged workflow and continuity reporting.",
                "stargazers_count": 125,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "writing", "mcp"],
                "updated_at": "2026-06-09T10:30:00Z",
                "root_files": ["package.json", "README.md"],
            },
            {
                "full_name": "arian-emami/NovelDreamer",
                "html_url": "https://github.com/arian-emami/NovelDreamer",
                "description": "Novel generator using Wikiquote style/thematic samples, Hero's Journey, Freytag and acts/chapters pre-planning with story structure RAG.",
                "stargazers_count": 88,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "rag", "story"],
                "updated_at": "2026-06-09T11:00:00Z",
                "root_files": ["requirements.txt", "README.md"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-09T23:00:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }

    assert "research_taxonomy_story_map" in patterns_by_title["Picrew/awesome-llm-story-generation"]
    assert "novel_to_multimodal_pipeline" in patterns_by_title["Anning01/novelvids"]
    assert "entity_to_visual_asset_pipeline" in patterns_by_title["Anning01/novelvids"]
    assert "novel_to_multimodal_pipeline" in patterns_by_title["MemeCalculate/moyin-creator"]
    assert "agentic_book_planner_pipeline" in patterns_by_title["jncchds/abook"]
    assert "rag_synopsis_spine" in patterns_by_title["jncchds/abook"]
    assert "anti_repetition_prompt_rules" in patterns_by_title["jncchds/abook"]
    assert "narrative_arc_template_control" in patterns_by_title["Prompt-And-Circumstance/StoryMode"]
    assert "prompt_recipe_experiment_grid" in patterns_by_title["brianlmerritt/explore_writing"]
    assert "append_only_generation_review_log" in patterns_by_title["brianlmerritt/explore_writing"]
    assert "sampling_parameter_quality_sweep" in patterns_by_title["brianlmerritt/explore_writing"]
    assert "nrd_task_tree_pipeline" in patterns_by_title["forsonny/novel-master-ai"]
    assert "story_structure_rag_planning" in patterns_by_title["arian-emami/NovelDreamer"]


def test_research_multimodal_experiment_pattern_pack_exposes_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-09T23:05:00+08:00",
        "candidate_count": 8,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/Picrew/awesome-llm-story-generation",
                "title": "Picrew/awesome-llm-story-generation",
                "summary": "Story generation taxonomy with planning/decomposition, agent collaboration, multimodal, memory and benchmark categories.",
                "stars": 80,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "index-only",
                "risk_flags": [],
                "absorbed_patterns": ["research_taxonomy_story_map"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/Anning01/novelvids",
                "title": "Anning01/novelvids",
                "summary": "Novel-to-short-drama pipeline with entity extraction, reference images, storyboard and video synthesis.",
                "stars": 219,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["runtime_surface"],
                "absorbed_patterns": ["novel_to_multimodal_pipeline", "entity_to_visual_asset_pipeline", "scene_asset_pipeline"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/jncchds/abook",
                "title": "jncchds/abook",
                "summary": "Seven-agent book planner with RAG context retrieval, full synopsis spine, anti-repetition rules and continuity checker.",
                "stars": 430,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker", "mcp_server"],
                "absorbed_patterns": ["agentic_book_planner_pipeline", "rag_synopsis_spine", "anti_repetition_prompt_rules", "workflow_agent_pipeline"],
                "score": 94,
            },
            {
                "source": "github",
                "url": "https://github.com/Prompt-And-Circumstance/StoryMode",
                "title": "Prompt-And-Circumstance/StoryMode",
                "summary": "43 genres, story style, author style, narrative arc and scenario blueprint schema.",
                "stars": 140,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["browser_extension"],
                "absorbed_patterns": ["narrative_arc_template_control", "same_type_creation"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/brianlmerritt/explore_writing",
                "title": "brianlmerritt/explore_writing",
                "summary": "Prompt recipes, sampling grid, rubric review, write/review/top_writing and append-only resumable TSV logs.",
                "stars": 35,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["prompt_recipe_experiment_grid", "append_only_generation_review_log", "sampling_parameter_quality_sweep"],
                "score": 80,
            },
            {
                "source": "github",
                "url": "https://github.com/forsonny/novel-master-ai",
                "title": "forsonny/novel-master-ai",
                "summary": "NRD task tree across arcs, chapters, scenes and revision passes with continuity reporting.",
                "stars": 125,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["mcp_server"],
                "absorbed_patterns": ["nrd_task_tree_pipeline", "continuation"],
                "score": 89,
            },
            {
                "source": "github",
                "url": "https://github.com/arian-emami/NovelDreamer",
                "title": "arian-emami/NovelDreamer",
                "summary": "Wikiquote style/thematic RAG with Hero's Journey, Freytag and act/chapter pre-planning.",
                "stars": 88,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["story_structure_rag_planning", "top_down_story_planning"],
                "score": 82,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "story_generation_taxonomy" in pattern_pack["whole_book_analysis_targets"]
    assert "multimodal_adaptation_chain" in pattern_pack["whole_book_analysis_targets"]
    assert "entity_extraction_results" in pattern_pack["whole_book_analysis_targets"]
    assert "story_bible_agent_outputs" in pattern_pack["whole_book_analysis_targets"]
    assert "full_synopsis_spine" in pattern_pack["whole_book_analysis_targets"]
    assert "anti_repetition_rule_hits" in pattern_pack["whole_book_analysis_targets"]
    assert "prompt_recipe_grid" in pattern_pack["whole_book_analysis_targets"]
    assert "narrative_arc_templates" in pattern_pack["whole_book_analysis_targets"]
    assert "nrd_task_tree" in pattern_pack["whole_book_analysis_targets"]
    assert "hero_journey_beats" in pattern_pack["whole_book_analysis_targets"]
    assert "research_taxonomy_story_map_hints" in pattern_pack
    assert "novel_to_multimodal_pipeline_hints" in pattern_pack
    assert "agentic_book_planner_pipeline_hints" in pattern_pack
    assert "rag_synopsis_spine_hints" in pattern_pack
    assert "prompt_recipe_experiment_grid_hints" in pattern_pack
    assert "narrative_arc_remap" in pattern_pack["inspired_mapping_targets"]
    assert "nrd_task_tree_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "research_taxonomy_story_map_hints" in digest
    assert "agentic_book_planner_pipeline_hints" in digest
    assert "sampling_parameter_quality_sweep_hints" in digest


def test_default_discovery_sources_include_research_multimodal_experiment_projects():
    assert "https://github.com/Picrew/awesome-llm-story-generation" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Anning01/novelvids" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/MemeCalculate/moyin-creator" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jncchds/abook" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Prompt-And-Circumstance/StoryMode" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/brianlmerritt/explore_writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/forsonny/novel-master-ai" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/arian-emami/NovelDreamer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("story generation taxonomy" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("continuity checker" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("narrative arc" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("prompt recipes" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("hero journey" in query.lower() for query in DEFAULT_GITHUB_QUERIES)



def test_serialized_webnovel_projects_are_classified_as_continuity_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "lingfengQAQ/webnovel-writer",
                "html_url": "https://github.com/lingfengQAQ/webnovel-writer",
                "description": "Serialized webnovel writer with Story System contracts, accepted CHAPTER_COMMIT, projection_log, RAG, reviewer, OOC, rhythm and state/index/summary/memory/vector projections.",
                "stargazers_count": 4897,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["webnovel", "ai-writing", "claude-code"],
                "updated_at": "2026-06-09T13:16:34Z",
                "root_files": ["README.md", "package.json", "scripts"],
            },
            {
                "full_name": "zy-zmc/tianming-novel-ai-writer",
                "html_url": "https://github.com/zy-zmc/tianming-novel-ai-writer",
                "description": "AI novel writing system with 15-dimensional fact snapshots, 12 change declaration classes, 6 generation gates, long-distance recall, unified validation and per-chapter state write-back.",
                "stargazers_count": 303,
                "license": None,
                "topics": ["novel", "webnovel", "semantic-search"],
                "updated_at": "2026-06-09T11:58:15Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "RTY798/agent-novel",
                "html_url": "https://github.com/RTY798/agent-novel",
                "description": "Chinese webnovel agent skill with 三型分流, 概率陷阱, event cooldown matrix, unique image test, Story Contract, reverse brake, 3+1 circuit breaker and golden-finger methods.",
                "stargazers_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["agent-skill", "ai-writing", "chinese-webnovel", "nucleus-first", "writing-tool"],
                "updated_at": "2026-06-10T18:16:41Z",
                "root_files": ["README.md", "SKILL.md", "references"],
            },
            {
                "full_name": "starMagic/webnovel-writer-hermes",
                "html_url": "https://github.com/starMagic/webnovel-writer-hermes",
                "description": "Hermes webnovel writer with story contracts, three-tier memory, foreshadowing DebtTracker, dynamic context budget, entity graph RAG, time-sliced state query and six-dimensional parallel review.",
                "stargazers_count": 1,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["webnovel", "hermes-agent", "rag"],
                "updated_at": "2026-06-05T10:31:40Z",
                "root_files": ["README.md", "scripts", "agents"],
            },
            {
                "full_name": "HZ-KMNO/web-novel-writing-guidance-skill",
                "html_url": "https://github.com/HZ-KMNO/web-novel-writing-guidance-skill",
                "description": "Web novel writing guidance skill with chapter blueprint, key-information file, chapter task card, Draft A, Draft B, Draft C de-AI final pass, continuity record and next-chapter handoff.",
                "stargazers_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["web-novel", "skill", "writing"],
                "updated_at": "2026-06-09T07:20:01Z",
                "root_files": ["README.md", "SKILL.md"],
            },
            {
                "full_name": "DuckTraDo/Novel",
                "html_url": "https://github.com/DuckTraDo/Novel",
                "description": "Local-first AI novel pipeline with memory/story_bible.yaml, characters.yaml, foreshadowing.yaml, events.jsonl, timeline.jsonl, chapter_summaries.jsonl, relationship graph, consistency checks, and memory update after each chapter.",
                "stargazers_count": 2,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "continuity", "local-first"],
                "updated_at": "2026-06-03T07:47:48Z",
                "root_files": ["README.md", "pyproject.toml"],
            },
            {
                "full_name": "makieali/longform-ai",
                "html_url": "https://github.com/makieali/longform-ai",
                "description": "Long-form generation engine with rolling summary, character state tracking, timeline events, world state, relevant passages, token budget context trimming, chapter status, edit cycle records and session restore.",
                "stargazers_count": 6,
                "license": {"spdx_id": "MIT"},
                "topics": ["long-form", "novel", "continuity"],
                "updated_at": "2026-06-09T13:14:46Z",
                "root_files": ["README.md", "package.json"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T00:10:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }

    assert "story_contract_commit_chain" in patterns_by_title["lingfengQAQ/webnovel-writer"]
    assert "projection_sync_observability" in patterns_by_title["lingfengQAQ/webnovel-writer"]
    assert "reader_retention_review_gate" in patterns_by_title["lingfengQAQ/webnovel-writer"]
    assert "fact_snapshot_delta_gate" in patterns_by_title["zy-zmc/tianming-novel-ai-writer"]
    assert "anti_statistical_center_chapter_type_gate" in patterns_by_title["RTY798/agent-novel"]
    assert "foreshadowing_debt_budget" in patterns_by_title["starMagic/webnovel-writer-hermes"]
    assert "draft_stage_revision_ladder" in patterns_by_title["HZ-KMNO/web-novel-writing-guidance-skill"]
    assert "rolling_summary_context_trim" in patterns_by_title["DuckTraDo/Novel"]
    assert "rolling_summary_context_trim" in patterns_by_title["makieali/longform-ai"]


def test_serialized_webnovel_pattern_pack_exposes_contract_and_review_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T00:15:00+08:00",
        "candidate_count": 6,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/lingfengQAQ/webnovel-writer",
                "title": "lingfengQAQ/webnovel-writer",
                "summary": "Story contracts, accepted CHAPTER_COMMIT, projection logs, dashboard, doctor, RAG reviewer, OOC, rhythm and reader retention review.",
                "stars": 4897,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["runtime_surface"],
                "absorbed_patterns": [
                    "story_contract_commit_chain",
                    "projection_sync_observability",
                    "reader_retention_review_gate",
                    "continuation",
                    "chapter_generation",
                ],
                "score": 98,
            },
            {
                "source": "github",
                "url": "https://github.com/zy-zmc/tianming-novel-ai-writer",
                "title": "zy-zmc/tianming-novel-ai-writer",
                "summary": "15-dimensional fact snapshots, 12 change declaration classes, six generation gates and state write-back.",
                "stars": 303,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["fact_snapshot_delta_gate", "semantic_long_context_search"],
                "score": 91,
            },
            {
                "source": "github",
                "url": "https://github.com/RTY798/agent-novel",
                "title": "RTY798/agent-novel",
                "summary": "Three-type chapter routing, probability trap, event cooldown matrix, unique-image test, Story Contract and reverse brake.",
                "stars": 1,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["prompt_pack"],
                "absorbed_patterns": ["anti_statistical_center_chapter_type_gate", "chapter_generation", "continuation"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/starMagic/webnovel-writer-hermes",
                "title": "starMagic/webnovel-writer-hermes",
                "summary": "Three-tier memory, foreshadowing DebtTracker, dynamic context-budget reservation and six-dimensional review.",
                "stars": 1,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["foreshadowing_debt_budget", "layered_memory_model", "reader_retention_review_gate"],
                "score": 89,
            },
            {
                "source": "github",
                "url": "https://github.com/HZ-KMNO/web-novel-writing-guidance-skill",
                "title": "HZ-KMNO/web-novel-writing-guidance-skill",
                "summary": "Chapter blueprint, key-information file, task card, Draft A/B/C ladder and continuity handoff.",
                "stars": 1,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["draft_stage_revision_ladder", "anti_ai_tone_polish"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/makieali/longform-ai",
                "title": "makieali/longform-ai",
                "summary": "Rolling summary, character state, timeline events, relevant passages, token-budget context trimming and session restore.",
                "stars": 6,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["postinstall"],
                "absorbed_patterns": ["rolling_summary_context_trim", "accepted_chapter_memory"],
                "score": 84,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "story_contracts" in pattern_pack["whole_book_analysis_targets"]
    assert "accepted_chapter_commits" in pattern_pack["whole_book_analysis_targets"]
    assert "fact_snapshot_dimensions" in pattern_pack["whole_book_analysis_targets"]
    assert "generation_gate_results" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_type_distribution_report" in pattern_pack["whole_book_analysis_targets"]
    assert "event_cooldown_violation_report" in pattern_pack["whole_book_analysis_targets"]
    assert "unique_image_contract_verification_report" in pattern_pack["whole_book_analysis_targets"]
    assert "projection_sync_log" in pattern_pack["whole_book_analysis_targets"]
    assert "foreshadowing_debt_items" in pattern_pack["whole_book_analysis_targets"]
    assert "reader_retention_score" in pattern_pack["whole_book_analysis_targets"]
    assert "draft_stage_status" in pattern_pack["whole_book_analysis_targets"]
    assert "rolling_summary" in pattern_pack["whole_book_analysis_targets"]
    assert "story_contract_commit_chain_hints" in pattern_pack
    assert "fact_snapshot_delta_gate_hints" in pattern_pack
    assert "anti_statistical_center_chapter_type_gate_hints" in pattern_pack
    assert "chapter_type_minimal_flow_policy" in pattern_pack["bible_enrichment_targets"]
    assert "event_cooldown_matrix" in pattern_pack["bible_enrichment_targets"]
    assert "unique_image_story_contract_policy" in pattern_pack["bible_enrichment_targets"]
    assert "projection_sync_observability_hints" in pattern_pack
    assert "foreshadowing_debt_budget_hints" in pattern_pack
    assert "reader_retention_review_gate_hints" in pattern_pack
    assert "draft_stage_revision_ladder_hints" in pattern_pack
    assert "rolling_summary_context_trim_hints" in pattern_pack
    assert "commit_chain_remap" in pattern_pack["inspired_mapping_targets"]
    assert "fact_delta_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chapter_type_flow_remap" in pattern_pack["inspired_mapping_targets"]
    assert "event_cooldown_matrix_remap" in pattern_pack["inspired_mapping_targets"]
    assert "unique_image_contract_remap" in pattern_pack["inspired_mapping_targets"]
    assert "retention_hook_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "story_contract_commit_chain_hints" in digest
    assert "fact_snapshot_delta_gate_hints" in digest
    assert "anti_statistical_center_chapter_type_gate_hints" in digest
    assert "rolling_summary_context_trim_hints" in digest


def test_default_discovery_sources_include_serialized_webnovel_projects():
    assert "https://github.com/lingfengQAQ/webnovel-writer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/zy-zmc/tianming-novel-ai-writer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/RTY798/agent-novel" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/lujih/webnovel-writer-opencode" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/starMagic/webnovel-writer-hermes" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/HZ-KMNO/web-novel-writing-guidance-skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jinmawang/claude-novel-writeFlow" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/DuckTraDo/Novel" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/makieali/longform-ai" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/guchendesigndog/GC-Writer-Assistant" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("story contract" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("event cooldown" in query.lower() and "story contract" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("fact write-back" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("foreshadowing debt" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("draft a" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("rolling summary" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_story_quality_eval_projects_are_classified_as_quality_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "lars76/story-evaluation-llm",
                "html_url": "https://github.com/lars76/story-evaluation-llm",
                "description": "Story evaluation dataset with 15 LLM models, comprehensive quality evaluations, q1-q15 metrics, length score, overall score, character consistency, reader interest, plot resolution and ranked weaknesses.",
                "stargazers_count": 13,
                "license": {"spdx_id": "MIT"},
                "topics": ["story", "evaluation", "llm"],
                "updated_at": "2026-06-09T14:00:00Z",
                "root_files": ["README.md", "LICENSE"],
            },
            {
                "full_name": "lechmazur/writing",
                "html_url": "https://github.com/lechmazur/writing",
                "description": "LLM Creative Story-Writing Benchmark with head-to-head story comparisons, constrained creative briefs, paired story judgments, visible story order swaps, pairwise margins and evaluator agreement.",
                "stargazers_count": 425,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["creative-writing", "benchmark", "llm"],
                "updated_at": "2026-06-09T14:01:00Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "lechmazur/writing_styles",
                "html_url": "https://github.com/lechmazur/writing_styles",
                "description": "Flash fiction style benchmark with style fingerprints, within-model diversity, voice and diction, rhythm and syntax, POV and discourse, structure and pacing, tone, imagery, dialogue, experimentation and closure axes.",
                "stargazers_count": 56,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["style", "fiction", "benchmark"],
                "updated_at": "2026-06-09T14:02:00Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "anirudhlakkaraju/cs4_benchmark",
                "html_url": "https://github.com/anirudhlakkaraju/cs4_benchmark",
                "description": "CS4 evaluates LLM creativity in story generation with prompts of varying constraint specificity, measuring creativity, constraint satisfaction, coherence and perplexity.",
                "stargazers_count": 4,
                "license": {"spdx_id": "MIT"},
                "topics": ["story-generation", "creativity", "benchmark"],
                "updated_at": "2026-06-09T14:03:00Z",
                "root_files": ["README.md", "LICENSE", "run_evaluations.sh"],
            },
            {
                "full_name": "clchinkc/story-bench",
                "html_url": "https://github.com/clchinkc/story-bench",
                "description": "Story Theory Benchmark uses objective story theory frameworks, programmatic checks, LLM judge ensemble, beat interpolation, beat revision, constrained continuation, theory conversion and weighted narrative criteria.",
                "stargazers_count": 37,
                "license": {"spdx_id": "MIT"},
                "topics": ["story", "benchmark", "evaluation"],
                "updated_at": "2026-06-09T14:04:00Z",
                "root_files": ["README.md", "LICENSE"],
            },
            {
                "full_name": "THU-KEG/StoryWriter",
                "html_url": "https://github.com/THU-KEG/StoryWriter",
                "description": "Multi-agent long story generation framework with Outline Agent, Planning Agent and Writing Agent that dynamically compresses story history to generate coherent new content aligned with current events.",
                "stargazers_count": 85,
                "license": None,
                "topics": ["long-story", "multi-agent", "llm"],
                "updated_at": "2026-06-09T14:05:00Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "ZJU-LLMs/OpenStory",
                "html_url": "https://github.com/ZJU-LLMs/OpenStory",
                "description": "OpenStory is a multi-agent inference and simulation framework for story worlds, dynamically adding and removing agents and simulating Dream of the Red Chamber character behavior, social interaction and story evolution.",
                "stargazers_count": 132,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["multi-agent", "story", "simulation"],
                "updated_at": "2026-06-09T14:06:00Z",
                "root_files": ["README.md", "LICENSE", "models_config.yaml"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T01:10:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }

    assert "multidimensional_quality_rubric" in patterns_by_title["lars76/story-evaluation-llm"]
    assert "pairwise_story_comparison_ranking" in patterns_by_title["lechmazur/writing"]
    assert "style_axis_diversity_fingerprint" in patterns_by_title["lechmazur/writing_styles"]
    assert "constraint_specificity_creativity_benchmark" in patterns_by_title["anirudhlakkaraju/cs4_benchmark"]
    assert "story_theory_beat_evaluation" in patterns_by_title["clchinkc/story-bench"]
    assert "event_outline_history_compression" in patterns_by_title["THU-KEG/StoryWriter"]
    assert "agentic_story_world_simulation" in patterns_by_title["ZJU-LLMs/OpenStory"]


def test_story_quality_eval_pattern_pack_exposes_variant_and_rubric_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T01:15:00+08:00",
        "candidate_count": 6,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/lechmazur/writing",
                "title": "lechmazur/writing",
                "summary": "Head-to-head story comparisons with matched creative briefs, order swaps and pairwise margins.",
                "stars": 425,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["pairwise_story_comparison_ranking", "chapter_generation"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/lars76/story-evaluation-llm",
                "title": "lars76/story-evaluation-llm",
                "summary": "q1-q15 quality metrics, overall score and ranked weaknesses for story evaluation.",
                "stars": 13,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["multidimensional_quality_rubric"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/clchinkc/story-bench",
                "title": "clchinkc/story-bench",
                "summary": "Story theory tasks for beat interpolation, revision, constrained continuation and theory conversion.",
                "stars": 37,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["story_theory_beat_evaluation"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/lechmazur/writing_styles",
                "title": "lechmazur/writing_styles",
                "summary": "Style fingerprints and diversity axes for flash fiction.",
                "stars": 56,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["style_axis_diversity_fingerprint", "style_signature"],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/anirudhlakkaraju/cs4_benchmark",
                "title": "anirudhlakkaraju/cs4_benchmark",
                "summary": "Constraint specificity benchmark for creativity, constraint satisfaction and coherence.",
                "stars": 4,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["shell_script"],
                "absorbed_patterns": ["constraint_specificity_creativity_benchmark"],
                "score": 80,
            },
            {
                "source": "github",
                "url": "https://github.com/THU-KEG/StoryWriter",
                "title": "THU-KEG/StoryWriter",
                "summary": "Outline Agent, Planning Agent, Writing Agent and dynamic story history compression.",
                "stars": 85,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["event_outline_history_compression"],
                "score": 78,
            },
            {
                "source": "github",
                "url": "https://github.com/ZJU-LLMs/OpenStory",
                "title": "ZJU-LLMs/OpenStory",
                "summary": "Multi-agent story-world simulation with dynamic agents and character interactions.",
                "stars": 132,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["external_api_surface"],
                "absorbed_patterns": ["agentic_story_world_simulation"],
                "score": 76,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "pairwise_story_comparisons" in pattern_pack["whole_book_analysis_targets"]
    assert "story_quality_rubric_scores" in pattern_pack["whole_book_analysis_targets"]
    assert "story_theory_task_results" in pattern_pack["whole_book_analysis_targets"]
    assert "constraint_specificity_level" in pattern_pack["whole_book_analysis_targets"]
    assert "style_axis_fingerprint" in pattern_pack["whole_book_analysis_targets"]
    assert "event_outline_graph" in pattern_pack["whole_book_analysis_targets"]
    assert "simulated_agent_interactions" in pattern_pack["whole_book_analysis_targets"]
    assert "pairwise_story_comparison_ranking_hints" in pattern_pack
    assert "multidimensional_quality_rubric_hints" in pattern_pack
    assert "story_theory_beat_evaluation_hints" in pattern_pack
    assert "constraint_specificity_creativity_benchmark_hints" in pattern_pack
    assert "style_axis_diversity_fingerprint_hints" in pattern_pack
    assert "event_outline_history_compression_hints" in pattern_pack
    assert "agentic_story_world_simulation_hints" in pattern_pack
    assert "pairwise_variant_remap" in pattern_pack["inspired_mapping_targets"]
    assert "quality_rubric_remap" in pattern_pack["inspired_mapping_targets"]
    assert "style_axis_remap" in pattern_pack["inspired_mapping_targets"]
    assert "constraint_specificity_remap" in pattern_pack["inspired_mapping_targets"]
    assert "agent_world_simulation_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "pairwise_story_comparison_ranking_hints" in digest
    assert "multidimensional_quality_rubric_hints" in digest
    assert "style_axis_diversity_fingerprint_hints" in digest


def test_default_discovery_sources_include_story_quality_eval_projects():
    assert "https://github.com/lars76/story-evaluation-llm" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/lechmazur/writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/lechmazur/writing_styles" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/anirudhlakkaraju/cs4_benchmark" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/clchinkc/story-bench" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/THU-KEG/StoryWriter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ZJU-LLMs/OpenStory" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("head-to-head story" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("q1" in query.lower() and "q15" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("story theory" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("constraint specificity" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("style fingerprints" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

def test_reader_market_feedback_projects_are_classified_as_feedback_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "zygmuntz/goodbooks-10k",
                "html_url": "https://github.com/zygmuntz/goodbooks-10k",
                "description": "Ten thousand fiction books, six million ratings, to-read signals, tags/shelves/genres and book recommendation data from Goodreads for novel reader preference modeling.",
                "stargazers_count": 894,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["books", "fiction", "novel", "goodreads", "ratings", "recommendations", "recommender-systems"],
                "updated_at": "2023-05-17T18:52:16Z",
                "root_files": ["README.md", "ratings.csv", "to_read.csv", "books.csv", "tags.csv"],
            },
            {
                "full_name": "MengtingWan/goodreads",
                "html_url": "https://github.com/MengtingWan/goodreads",
                "description": "Goodreads datasets code samples for fiction book reviews, review statistics, fine-grained spoiler detection, recommendation behavior chains and interaction data.",
                "stargazers_count": 309,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["book-reviews", "fiction", "novel", "dataset", "recommendation-system", "spoilers"],
                "updated_at": "2025-02-04T06:20:31Z",
                "root_files": ["README.md", "reviews.ipynb", "statistics.ipynb"],
            },
            {
                "full_name": "Ckokoski/authorclaw",
                "html_url": "https://github.com/Ckokoski/authorclaw",
                "description": "Autonomous AI writing agent with deep revision, AI beta readers, reader intelligence, comp titles, market positioning, genre trends and reader expectation analysis.",
                "stargazers_count": 70,
                "license": {"spdx_id": "MIT"},
                "topics": ["author", "writing", "agent"],
                "updated_at": "2026-05-01T16:51:18Z",
                "root_files": ["README.md", "package.json", "Dockerfile", "skills/author/beta-reader/SKILL.md"],
            },
            {
                "full_name": "f5alcon/The-Novelists-Atelier",
                "html_url": "https://github.com/f5alcon/The-Novelists-Atelier",
                "description": "Local browser novel writing assistant with micro-tension, reader curiosity tracker, chapter hook, cliffhanger audit, style DNA, token breakdown and local context scopes.",
                "stargazers_count": 11,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["novel", "writing"],
                "updated_at": "2026-05-28T17:34:14Z",
                "root_files": ["README.md", "index.html", "security.md"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T02:30:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "reader_rating_signal_model" in by_title["zygmuntz/goodbooks-10k"]["absorbed_patterns"]
    assert "review_spoiler_sentiment_corpus" in by_title["MengtingWan/goodreads"]["absorbed_patterns"]
    assert "beta_reader_archetype_panel" in by_title["Ckokoski/authorclaw"]["absorbed_patterns"]
    assert "comp_title_market_positioning" in by_title["Ckokoski/authorclaw"]["absorbed_patterns"]
    assert "local_reader_experience_editor" in by_title["f5alcon/The-Novelists-Atelier"]["absorbed_patterns"]
    assert "docker" in by_title["Ckokoski/authorclaw"]["risk_flags"]


def test_reader_market_feedback_pattern_pack_exposes_reader_and_market_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T02:45:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/zygmuntz/goodbooks-10k",
                "title": "zygmuntz/goodbooks-10k",
                "summary": "Goodreads ratings, to-read, shelves and tags for reader preference modeling.",
                "stars": 894,
                "license": "NOASSERTION",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["reader_rating_signal_model", "same_type_creation", "style_signature"],
                "score": 77,
            },
            {
                "source": "github",
                "url": "https://github.com/MengtingWan/goodreads",
                "title": "MengtingWan/goodreads",
                "summary": "Goodreads book reviews, spoiler detection and review statistics.",
                "stars": 309,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["review_spoiler_sentiment_corpus"],
                "score": 70,
            },
            {
                "source": "github",
                "url": "https://github.com/Ckokoski/authorclaw",
                "title": "Ckokoski/authorclaw",
                "summary": "AI beta readers, comp titles, market positioning and reader intelligence.",
                "stars": 70,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker"],
                "absorbed_patterns": ["beta_reader_archetype_panel", "comp_title_market_positioning"],
                "score": 83,
            },
            {
                "source": "github",
                "url": "https://github.com/f5alcon/The-Novelists-Atelier",
                "title": "f5alcon/The-Novelists-Atelier",
                "summary": "Reader curiosity tracker, chapter hook, cliffhanger audit and micro-tension prompts.",
                "stars": 11,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["local_reader_experience_editor"],
                "score": 74,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "reader_rating_matrix" in pattern_pack["whole_book_analysis_targets"]
    assert "review_signal_clusters" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_want_to_continue_scores" in pattern_pack["whole_book_analysis_targets"]
    assert "comp_title_matrix" in pattern_pack["whole_book_analysis_targets"]
    assert "micro_tension_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "reader_rating_signal_map" in pattern_pack["bible_enrichment_targets"]
    assert "beta_reader_archetypes" in pattern_pack["bible_enrichment_targets"]
    assert "reader_rating_signal_model_hints" in pattern_pack
    assert "review_spoiler_sentiment_corpus_hints" in pattern_pack
    assert "beta_reader_archetype_panel_hints" in pattern_pack
    assert "comp_title_market_positioning_hints" in pattern_pack
    assert "local_reader_experience_editor_hints" in pattern_pack
    assert "reader_signal_remap" in pattern_pack["inspired_mapping_targets"]
    assert "review_cluster_remap" in pattern_pack["inspired_mapping_targets"]
    assert "beta_reader_panel_remap" in pattern_pack["inspired_mapping_targets"]
    assert "comp_title_positioning_remap" in pattern_pack["inspired_mapping_targets"]
    assert "reader_experience_hook_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "reader_rating_signal_model_hints" in digest
    assert "review_spoiler_sentiment_corpus_hints" in digest
    assert "beta_reader_archetype_panel_hints" in digest
    assert "comp_title_market_positioning_hints" in digest
    assert "local_reader_experience_editor_hints" in digest


def test_default_discovery_sources_include_reader_market_feedback_projects():
    assert "https://github.com/zygmuntz/goodbooks-10k" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/MengtingWan/goodreads" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/maria-antoniak/goodreads-scraper" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Ckokoski/authorclaw" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/f5alcon/The-Novelists-Atelier" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("goodreads" in query.lower() and "ratings" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("spoiler detection" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("beta reader" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("comp title" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("micro-tension" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_delivery_packaging_projects_are_classified_as_export_and_assembly_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "arupmaity1/book-writer-mcp",
                "html_url": "https://github.com/arupmaity1/book-writer-mcp",
                "description": (
                    "MCP server for AI-assisted book and manuscript writing with story bible, style guide, "
                    "continuity checker, HTML preview, Markdown/DOCX export, title page, table of contents, "
                    "page numbers, configurable fonts, cover design and KDP cover specs."
                ),
                "stargazers_count": 0,
                "license": None,
                "topics": ["mcp", "book-writing", "manuscript", "story-bible", "continuity"],
                "updated_at": "2026-04-05T02:03:06Z",
                "root_files": ["README.md", "package.json", "src", "tsconfig.json"],
            },
            {
                "full_name": "vkbo/novelWriter",
                "html_url": "https://github.com/vkbo/novelWriter",
                "description": "Plain text editor for novels assembled from many smaller text documents with manuscript outline and export.",
                "stargazers_count": 2900,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["novel", "plain-text", "manuscript", "writing"],
                "updated_at": "2026-05-17T12:34:00Z",
                "root_files": ["README.md", "setup.py", "novelwriter"],
            },
            {
                "full_name": "andreafeccomandi/bibisco",
                "html_url": "https://github.com/andreafeccomandi/bibisco",
                "description": (
                    "Open source application for writing novels. Organize chapters and scenes, manage revisions, "
                    "export novel in pdf, docx, or txt, define premise, fabula, narrative strands and settings."
                ),
                "stargazers_count": 2800,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["novel", "writing", "manuscript", "export"],
                "updated_at": "2026-03-12T09:20:00Z",
                "root_files": ["README.md", "package.json", "electron-builder.json"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T03:30:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "delivery_manuscript_assembly" in by_title["arupmaity1/book-writer-mcp"]["absorbed_patterns"]
    assert "export_format_fidelity_audit" in by_title["arupmaity1/book-writer-mcp"]["absorbed_patterns"]
    assert "preview_toc_packaging" in by_title["arupmaity1/book-writer-mcp"]["absorbed_patterns"]
    assert "cover_kdp_metadata_boundary" in by_title["arupmaity1/book-writer-mcp"]["absorbed_patterns"]
    assert "delivery_manuscript_assembly" in by_title["vkbo/novelWriter"]["absorbed_patterns"]
    assert "export_format_fidelity_audit" in by_title["andreafeccomandi/bibisco"]["absorbed_patterns"]
    assert "license:missing" in by_title["arupmaity1/book-writer-mcp"]["trust_review"]["flags"]
    assert "mcp_server" in by_title["arupmaity1/book-writer-mcp"]["risk_flags"]


def test_delivery_packaging_pattern_pack_exposes_final_txt_and_export_audits():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T03:45:00+08:00",
        "candidate_count": 3,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/arupmaity1/book-writer-mcp",
                "title": "arupmaity1/book-writer-mcp",
                "summary": "Book writer MCP with story bible, continuity checker, HTML preview, DOCX export and KDP cover specs.",
                "stars": 0,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["mcp_server"],
                "absorbed_patterns": [
                    "delivery_manuscript_assembly",
                    "export_format_fidelity_audit",
                    "preview_toc_packaging",
                    "cover_kdp_metadata_boundary",
                ],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/vkbo/novelWriter",
                "title": "vkbo/novelWriter",
                "summary": "Plain text novel editor for projects assembled from many smaller text documents.",
                "stars": 2900,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["plain_text_project_storage", "delivery_manuscript_assembly"],
                "score": 80,
            },
            {
                "source": "github",
                "url": "https://github.com/andreafeccomandi/bibisco",
                "title": "andreafeccomandi/bibisco",
                "summary": "Organize chapters and scenes, manage revisions, export novel in pdf, docx, or txt.",
                "stars": 2800,
                "license": "AGPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["manuscript_export_formats", "export_format_fidelity_audit"],
                "score": 78,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "final_manuscript_assembly_plan" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_header_normalization_report" in pattern_pack["whole_book_analysis_targets"]
    assert "export_format_fidelity_report" in pattern_pack["whole_book_analysis_targets"]
    assert "toc_preview_heading_map" in pattern_pack["whole_book_analysis_targets"]
    assert "cover_kdp_metadata_spec" in pattern_pack["whole_book_analysis_targets"]
    assert "delivery_manuscript_assembly_hints" in pattern_pack
    assert "export_format_fidelity_audit_hints" in pattern_pack
    assert "preview_toc_packaging_hints" in pattern_pack
    assert "cover_kdp_metadata_boundary_hints" in pattern_pack
    assert "delivery_packaging_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "delivery_manuscript_assembly_hints" in digest
    assert "export_format_fidelity_audit_hints" in digest
    assert "preview_toc_packaging_hints" in digest
    assert "cover_kdp_metadata_boundary_hints" in digest


def test_default_discovery_sources_include_delivery_packaging_projects():
    assert "https://github.com/arupmaity1/book-writer-mcp" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("docx" in query.lower() and "table of contents" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("kdp" in query.lower() and "cover" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_interactive_narrative_sources_are_classified_as_branch_dialogue_state_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "inkle/ink",
                "html_url": "https://github.com/inkle/ink",
                "description": (
                    "Open source scripting language for writing interactive narrative with highly branching stories, "
                    "choices, knots, stitches, diverts, variables, and weave structure."
                ),
                "stargazers_count": 4795,
                "license": {"spdx_id": "MIT"},
                "topics": ["interactive-fiction", "narrative", "branching-story", "ink"],
                "updated_at": "2026-06-08T22:44:09Z",
                "root_files": ["README.md", "Documentation", "ink-engine-runtime"],
            },
            {
                "full_name": "YarnSpinnerTool/YarnSpinner",
                "html_url": "https://github.com/YarnSpinnerTool/YarnSpinner",
                "description": (
                    "Dialogue tool for writing interactive conversations with lines, options, commands, variables, "
                    "nodes, and branching dialogue scripts."
                ),
                "stargazers_count": 2800,
                "license": {"spdx_id": "MIT"},
                "topics": ["dialogue", "narrative", "game-development", "unity"],
                "updated_at": "2026-06-09T12:09:26Z",
                "root_files": ["README.md", "YarnSpinner.Compiler", "YarnSpinner"],
            },
            {
                "full_name": "klembot/twinejs",
                "html_url": "https://github.com/klembot/twinejs",
                "description": "Twine is a tool for telling interactive, nonlinear stories with passages, links, variables, and story formats.",
                "stargazers_count": 2775,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["interactive-fiction", "nonlinear-story", "twine"],
                "updated_at": "2026-06-09T08:05:36Z",
                "root_files": ["package.json", "src", "public"],
            },
            {
                "full_name": "dfabulich/choicescript",
                "html_url": "https://github.com/dfabulich/choicescript",
                "description": "ChoiceScript is a language for developing multiple-choice games with choices, stats, variables, and achievements.",
                "stargazers_count": 453,
                "license": None,
                "topics": ["interactive-fiction", "choice-games"],
                "updated_at": "2026-05-29T07:35:56Z",
                "root_files": ["web", "package.json", "tests"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T04:20:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "branching_choice_graph" in by_title["inkle/ink"]["absorbed_patterns"]
    assert "node_dialogue_state_machine" in by_title["YarnSpinnerTool/YarnSpinner"]["absorbed_patterns"]
    assert "passage_link_navigation_map" in by_title["klembot/twinejs"]["absorbed_patterns"]
    assert "choice_stats_consequence_gate" in by_title["dfabulich/choicescript"]["absorbed_patterns"]
    assert "branching_choice_graph" in by_title["dfabulich/choicescript"]["absorbed_patterns"]
    assert "license:missing" in by_title["dfabulich/choicescript"]["trust_review"]["flags"]


def test_interactive_narrative_pattern_pack_exposes_branch_dialogue_state_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T04:25:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/inkle/ink",
                "title": "inkle/ink",
                "summary": "Interactive narrative scripting with branching stories, knots, stitches, choices, diverts and variables.",
                "stars": 4795,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["branching_choice_graph", "passage_link_navigation_map"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/YarnSpinnerTool/YarnSpinner",
                "title": "YarnSpinnerTool/YarnSpinner",
                "summary": "Dialogue system with lines, options, commands, variables, and node-based branching conversations.",
                "stars": 2800,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["node_dialogue_state_machine", "choice_stats_consequence_gate"],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/klembot/twinejs",
                "title": "klembot/twinejs",
                "summary": "Interactive nonlinear stories with passages, links, variables, and story formats.",
                "stars": 2775,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["passage_link_navigation_map", "branching_choice_graph"],
                "score": 80,
            },
            {
                "source": "github",
                "url": "https://github.com/dfabulich/choicescript",
                "title": "dfabulich/choicescript",
                "summary": "ChoiceScript multiple-choice games with choices, stats, variables, and achievements.",
                "stars": 453,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["choice_stats_consequence_gate", "branching_choice_graph"],
                "score": 76,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "choice_branch_graph" in pattern_pack["whole_book_analysis_targets"]
    assert "dialogue_node_state_machine" in pattern_pack["whole_book_analysis_targets"]
    assert "passage_link_navigation_map" in pattern_pack["whole_book_analysis_targets"]
    assert "choice_stats_consequence_ledger" in pattern_pack["whole_book_analysis_targets"]
    assert "branching_choice_graph_hints" in pattern_pack
    assert "node_dialogue_state_machine_hints" in pattern_pack
    assert "passage_link_navigation_map_hints" in pattern_pack
    assert "choice_stats_consequence_gate_hints" in pattern_pack
    assert "choice_branch_remap" in pattern_pack["inspired_mapping_targets"]
    assert "dialogue_node_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "branching_choice_graph_hints" in digest
    assert "node_dialogue_state_machine_hints" in digest
    assert "passage_link_navigation_map_hints" in digest
    assert "choice_stats_consequence_gate_hints" in digest


def test_default_discovery_sources_include_interactive_narrative_projects():
    assert "https://github.com/inkle/ink" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/YarnSpinnerTool/YarnSpinner" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/klembot/twinejs" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/dfabulich/choicescript" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("interactive narrative" in query.lower() and "branching" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("dialogue" in query.lower() and "variables" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_copy_similarity_sources_are_classified_as_fingerprint_fuzzy_diff_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "blingenf/copydetect",
                "html_url": "https://github.com/blingenf/copydetect",
                "description": "Code plagiarism detection tool based on Winnowing document fingerprinting and copied slices.",
                "stargazers_count": 326,
                "license": {"spdx_id": "MIT"},
                "topics": ["plagiarism-detection", "winnowing", "fingerprinting"],
                "updated_at": "2026-05-31T10:15:00Z",
                "root_files": ["README.md", "copydetect", "docs"],
            },
            {
                "full_name": "rapidfuzz/RapidFuzz",
                "html_url": "https://github.com/rapidfuzz/RapidFuzz",
                "description": "Rapid fuzzy string matching in Python using Levenshtein Distance and string metrics.",
                "stargazers_count": 3949,
                "license": {"spdx_id": "MIT"},
                "topics": ["fuzzy-matching", "levenshtein", "string-metrics"],
                "updated_at": "2026-06-09T22:18:00Z",
                "root_files": ["README.md", "src", "docs"],
            },
            {
                "full_name": "google/diff-match-patch",
                "html_url": "https://github.com/google/diff-match-patch",
                "description": "Diff Match and Patch library with semantic cleanup, matching, patches, and unit tests.",
                "stargazers_count": 19000,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["diff", "match", "patch"],
                "updated_at": "2024-08-05T12:00:00Z",
                "root_files": ["README.md", "python3", "javascript"],
            },
            {
                "full_name": "agranya99/MOSS-winnowing-seqMatcher",
                "html_url": "https://github.com/agranya99/MOSS-winnowing-seqMatcher",
                "description": "MOSS implementation using Winnowing and SequenceMatcher plagiarism checker.",
                "stargazers_count": 50,
                "license": {"spdx_id": "MIT"},
                "topics": ["moss", "winnowing", "sequence-matcher"],
                "updated_at": "2026-05-18T09:20:00Z",
                "root_files": ["README.md", "winnowing.py", "seqMatcher.py"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T05:20:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "source_text_fingerprint_gate" in by_title["blingenf/copydetect"]["absorbed_patterns"]
    assert "fuzzy_phrase_similarity_gate" in by_title["rapidfuzz/RapidFuzz"]["absorbed_patterns"]
    assert "diff_span_copy_review" in by_title["google/diff-match-patch"]["absorbed_patterns"]
    assert "source_text_fingerprint_gate" in by_title["agranya99/MOSS-winnowing-seqMatcher"]["absorbed_patterns"]


def test_copy_similarity_pattern_pack_exposes_copy_risk_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T05:25:00+08:00",
        "candidate_count": 3,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/blingenf/copydetect",
                "title": "blingenf/copydetect",
                "summary": "Winnowing document fingerprinting and copied-slice report for plagiarism detection.",
                "stars": 326,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["source_text_fingerprint_gate"],
                "score": 80,
            },
            {
                "source": "github",
                "url": "https://github.com/rapidfuzz/RapidFuzz",
                "title": "rapidfuzz/RapidFuzz",
                "summary": "Fuzzy string matching with Levenshtein distance and string metrics.",
                "stars": 3949,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["fuzzy_phrase_similarity_gate"],
                "score": 78,
            },
            {
                "source": "github",
                "url": "https://github.com/google/diff-match-patch",
                "title": "google/diff-match-patch",
                "summary": "Diff Match and Patch library with semantic cleanup and unit tests.",
                "stars": 19000,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["diff_span_copy_review"],
                "score": 76,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "source_fingerprint_overlap_report" in pattern_pack["whole_book_analysis_targets"]
    assert "fuzzy_phrase_similarity_report" in pattern_pack["whole_book_analysis_targets"]
    assert "diff_span_copy_risk_report" in pattern_pack["whole_book_analysis_targets"]
    assert "source_text_fingerprint_gate_hints" in pattern_pack
    assert "fuzzy_phrase_similarity_gate_hints" in pattern_pack
    assert "diff_span_copy_review_hints" in pattern_pack
    assert "fingerprint_baseline_remap" in pattern_pack["inspired_mapping_targets"]
    assert "fuzzy_phrase_threshold_remap" in pattern_pack["inspired_mapping_targets"]
    assert "diff_span_review_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "source_text_fingerprint_gate_hints" in digest
    assert "fuzzy_phrase_similarity_gate_hints" in digest
    assert "diff_span_copy_review_hints" in digest


def test_default_discovery_sources_include_copy_similarity_projects():
    assert "https://github.com/blingenf/copydetect" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/rapidfuzz/RapidFuzz" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/google/diff-match-patch" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/agranya99/MOSS-winnowing-seqMatcher" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("winnowing" in query.lower() and "plagiarism" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("fuzzy string matching" in query.lower() and "levenshtein" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_text_analysis_sources_are_classified_as_character_readability_keyword_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "booknlp/booknlp",
                "html_url": "https://github.com/booknlp/booknlp",
                "description": "BookNLP pipeline for book-length documents with character coreference, quote attribution and entity tokens.",
                "stargazers_count": 920,
                "license": {"spdx_id": "MIT"},
                "topics": ["nlp", "books", "characters", "quote-attribution"],
                "updated_at": "2026-06-09T17:13:08Z",
                "root_files": ["README.md", "booknlp", "examples", "setup.py"],
            },
            {
                "full_name": "textstat/textstat",
                "html_url": "https://github.com/textstat/textstat",
                "description": "Python package to calculate readability statistics of paragraphs, sentences and articles.",
                "stargazers_count": 1372,
                "license": {"spdx_id": "MIT"},
                "topics": ["readability", "text-statistics"],
                "updated_at": "2026-06-03T11:56:41Z",
                "root_files": ["README.md", "docs", "tests", "textstat"],
            },
            {
                "full_name": "LSYS/LexicalRichness",
                "html_url": "https://github.com/LSYS/LexicalRichness",
                "description": "Module to compute textual lexical richness and lexical diversity metrics including MTLD and HD-D.",
                "stargazers_count": 113,
                "license": {"spdx_id": "MIT"},
                "topics": ["lexical-diversity", "mtld", "hdd"],
                "updated_at": "2026-05-07T19:59:03Z",
                "root_files": ["README.rst", "lexicalrichness", "tests", "docs"],
            },
            {
                "full_name": "boudinfl/pke",
                "html_url": "https://github.com/boudinfl/pke",
                "description": "Python Keyphrase Extraction module with unsupervised keyphrase extraction candidates and weighting.",
                "stargazers_count": 1591,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["keyphrase-extraction", "keywords", "nlp"],
                "updated_at": "2026-06-08T02:27:10Z",
                "root_files": ["README.md", "docs", "examples", "pke", "setup.py"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T13:50:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "character_quote_attribution_map" in by_title["booknlp/booknlp"]["absorbed_patterns"]
    assert "readability_pacing_metric_gate" in by_title["textstat/textstat"]["absorbed_patterns"]
    assert "lexical_diversity_voice_audit" in by_title["LSYS/LexicalRichness"]["absorbed_patterns"]
    assert "keyphrase_motif_extraction" in by_title["boudinfl/pke"]["absorbed_patterns"]


def test_text_analysis_pattern_pack_exposes_decomposition_and_voice_metric_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T13:55:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/booknlp/booknlp",
                "title": "booknlp/booknlp",
                "summary": "Book-length NLP pipeline for character coreference, quote attribution, entity tokens and narrative metadata.",
                "stars": 920,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["character_quote_attribution_map"],
                "score": 83,
            },
            {
                "source": "github",
                "url": "https://github.com/textstat/textstat",
                "title": "textstat/textstat",
                "summary": "Readability statistics for text objects, paragraphs and sentences.",
                "stars": 1372,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["readability_pacing_metric_gate"],
                "score": 79,
            },
            {
                "source": "github",
                "url": "https://github.com/LSYS/LexicalRichness",
                "title": "LSYS/LexicalRichness",
                "summary": "Lexical richness and lexical diversity metrics for textual voice analysis.",
                "stars": 113,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["lexical_diversity_voice_audit"],
                "score": 77,
            },
            {
                "source": "github",
                "url": "https://github.com/boudinfl/pke",
                "title": "boudinfl/pke",
                "summary": "Keyphrase extraction candidates and weighting for motif and topic drift review.",
                "stars": 1591,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["keyphrase_motif_extraction"],
                "score": 75,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "character_quote_attribution_report" in pattern_pack["whole_book_analysis_targets"]
    assert "readability_pacing_curve" in pattern_pack["whole_book_analysis_targets"]
    assert "lexical_diversity_voice_report" in pattern_pack["whole_book_analysis_targets"]
    assert "keyphrase_motif_map" in pattern_pack["whole_book_analysis_targets"]
    assert "character_quote_attribution_map_hints" in pattern_pack
    assert "readability_pacing_metric_gate_hints" in pattern_pack
    assert "lexical_diversity_voice_audit_hints" in pattern_pack
    assert "keyphrase_motif_extraction_hints" in pattern_pack
    assert "quote_speaker_remap" in pattern_pack["inspired_mapping_targets"]
    assert "readability_curve_remap" in pattern_pack["inspired_mapping_targets"]
    assert "lexical_diversity_remap" in pattern_pack["inspired_mapping_targets"]
    assert "keyphrase_motif_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "character_quote_attribution_map_hints" in digest
    assert "readability_pacing_metric_gate_hints" in digest
    assert "lexical_diversity_voice_audit_hints" in digest
    assert "keyphrase_motif_extraction_hints" in digest


def test_default_discovery_sources_include_text_analysis_projects():
    assert "https://github.com/booknlp/booknlp" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/textstat/textstat" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/LSYS/LexicalRichness" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/HLasse/TextDescriptives" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/boudinfl/pke" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("quote attribution" in query.lower() and "character" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("readability" in query.lower() and "lexical" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("keyphrase" in query.lower() and "motif" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_segmentation_summary_topic_sources_are_classified_as_chunk_summary_topic_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "benbrandt/text-splitter",
                "html_url": "https://github.com/benbrandt/text-splitter",
                "description": "Semantic text splitter for Markdown, text and code that preserves chunk capacity and boundaries.",
                "stargazers_count": 1500,
                "license": {"spdx_id": "MIT"},
                "topics": ["text-splitting", "chunking", "semantic-chunking"],
                "updated_at": "2026-06-10T07:00:00Z",
                "root_files": ["README.md", "Cargo.toml", "crates", "bindings"],
            },
            {
                "full_name": "langchain-ai/langchain",
                "html_url": "https://github.com/langchain-ai/langchain",
                "description": "Framework with recursive character text splitter, semantic chunker, document transformers and summarization chains.",
                "stargazers_count": 111000,
                "license": {"spdx_id": "MIT"},
                "topics": ["text-splitters", "summarization", "rag"],
                "updated_at": "2026-06-10T09:00:00Z",
                "root_files": ["README.md", "libs", "docs", "pyproject.toml"],
            },
            {
                "full_name": "miso-belica/sumy",
                "html_url": "https://github.com/miso-belica/sumy",
                "description": "Automatic text summarizer with LSA, LexRank, TextRank, Edmundson and Luhn summarizers.",
                "stargazers_count": 3600,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["summarization", "textrank", "lexrank"],
                "updated_at": "2026-06-04T11:00:00Z",
                "root_files": ["README.rst", "sumy", "docs", "tests"],
            },
            {
                "full_name": "dmmiller612/bert-extractive-summarizer",
                "html_url": "https://github.com/dmmiller612/bert-extractive-summarizer",
                "description": "Extractive summarizer using BERT sentence embeddings to select representative sentences.",
                "stargazers_count": 3300,
                "license": {"spdx_id": "MIT"},
                "topics": ["extractive-summarization", "sentence-embeddings"],
                "updated_at": "2026-05-27T12:00:00Z",
                "root_files": ["README.md", "summarizer", "setup.py", "tests"],
            },
            {
                "full_name": "MaartenGr/BERTopic",
                "html_url": "https://github.com/MaartenGr/BERTopic",
                "description": "Topic modeling with transformer embeddings, c-TF-IDF, topic representation and dynamic topic modeling.",
                "stargazers_count": 7200,
                "license": {"spdx_id": "MIT"},
                "topics": ["topic-modeling", "bertopic", "dynamic-topics"],
                "updated_at": "2026-06-09T20:00:00Z",
                "root_files": ["README.md", "bertopic", "docs", "tests"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T15:10:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "semantic_chunk_boundary_map" in by_title["benbrandt/text-splitter"]["absorbed_patterns"]
    assert "semantic_chunk_boundary_map" in by_title["langchain-ai/langchain"]["absorbed_patterns"]
    assert "chapter_summary_anchor_gate" in by_title["miso-belica/sumy"]["absorbed_patterns"]
    assert "chapter_summary_anchor_gate" in by_title["dmmiller612/bert-extractive-summarizer"]["absorbed_patterns"]
    assert "topic_drift_map" in by_title["MaartenGr/BERTopic"]["absorbed_patterns"]


def test_segmentation_summary_topic_pattern_pack_exposes_context_and_inspired_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T15:15:00+08:00",
        "candidate_count": 3,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/benbrandt/text-splitter",
                "title": "benbrandt/text-splitter",
                "summary": "Semantic text splitting for Markdown/text/code with chunk capacities and boundary preservation.",
                "stars": 1500,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["semantic_chunk_boundary_map"],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/miso-belica/sumy",
                "title": "miso-belica/sumy",
                "summary": "Text summarizer with LSA, LexRank, TextRank, Edmundson and Luhn summarizers.",
                "stars": 3600,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["chapter_summary_anchor_gate"],
                "score": 80,
            },
            {
                "source": "github",
                "url": "https://github.com/MaartenGr/BERTopic",
                "title": "MaartenGr/BERTopic",
                "summary": "Topic modeling with transformer embeddings, c-TF-IDF, topic representation and dynamic topic modeling.",
                "stars": 7200,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["topic_drift_map"],
                "score": 78,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "semantic_chunk_boundary_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_summary_anchor_report" in pattern_pack["whole_book_analysis_targets"]
    assert "topic_drift_map" in pattern_pack["whole_book_analysis_targets"]
    assert "semantic_chunk_boundary_map_hints" in pattern_pack
    assert "chapter_summary_anchor_gate_hints" in pattern_pack
    assert "topic_drift_map_hints" in pattern_pack
    assert "chunk_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "summary_anchor_remap" in pattern_pack["inspired_mapping_targets"]
    assert "topic_drift_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "semantic_chunk_boundary_map_hints" in digest
    assert "chapter_summary_anchor_gate_hints" in digest
    assert "topic_drift_map_hints" in digest


def test_default_discovery_sources_include_segmentation_summary_topic_projects():
    assert "https://github.com/benbrandt/text-splitter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/langchain-ai/langchain" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/miso-belica/sumy" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/dmmiller612/bert-extractive-summarizer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/MaartenGr/BERTopic" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("semantic" in query.lower() and "chunk" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("summarization" in query.lower() and "chapter" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("topic modeling" in query.lower() and "topic drift" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_eval_observability_sources_are_classified_as_eval_and_regression_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "explodinggradients/ragas",
                "html_url": "https://github.com/explodinggradients/ragas",
                "description": "Evaluation framework for RAG applications with faithfulness, answer relevancy, context precision, context recall and testset generation.",
                "stargazers_count": 11000,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["rag", "evaluation", "faithfulness", "context-precision"],
                "updated_at": "2026-06-10T11:00:00Z",
                "root_files": ["README.md", "pyproject.toml", "docs", "src"],
            },
            {
                "full_name": "confident-ai/deepeval",
                "html_url": "https://github.com/confident-ai/deepeval",
                "description": "LLM evaluation framework with hallucination metrics, answer relevancy, faithfulness, datasets, GEval, and regression tests.",
                "stargazers_count": 7600,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["llm-evaluation", "hallucination", "regression-testing"],
                "updated_at": "2026-06-10T10:00:00Z",
                "root_files": ["README.md", "deepeval", "docs", "tests"],
            },
            {
                "full_name": "truera/trulens",
                "html_url": "https://github.com/truera/trulens",
                "description": "LLM app observability and evaluation with feedback functions, groundedness, context relevance, answer relevance, and traces.",
                "stargazers_count": 2600,
                "license": {"spdx_id": "MIT"},
                "topics": ["llm-observability", "evaluation", "groundedness", "tracing"],
                "updated_at": "2026-06-09T18:00:00Z",
                "root_files": ["README.md", "src", "docs", "tests"],
            },
            {
                "full_name": "Arize-ai/phoenix",
                "html_url": "https://github.com/Arize-ai/phoenix",
                "description": "AI observability and evaluation platform for tracing, LLM spans, retrieval traces, datasets, experiments and evals.",
                "stargazers_count": 5800,
                "license": {"spdx_id": "Elastic-2.0"},
                "topics": ["observability", "tracing", "llm-evals", "experiments"],
                "updated_at": "2026-06-10T08:00:00Z",
                "root_files": ["README.md", "app", "packages", "docker-compose.yml"],
            },
            {
                "full_name": "promptfoo/promptfoo",
                "html_url": "https://github.com/promptfoo/promptfoo",
                "description": "LLM evals and red teaming with prompt tests, assertions, golden datasets, regression suites and CI evaluation.",
                "stargazers_count": 8500,
                "license": {"spdx_id": "MIT"},
                "topics": ["prompt-testing", "evals", "regression", "red-team"],
                "updated_at": "2026-06-10T06:00:00Z",
                "root_files": ["README.md", "package.json", "src", "site"],
            },
            {
                "full_name": "openai/evals",
                "html_url": "https://github.com/openai/evals",
                "description": "Framework for evaluating LLMs and building custom evals with datasets, samples, graders and regression cases.",
                "stargazers_count": 16000,
                "license": {"spdx_id": "MIT"},
                "topics": ["evals", "llm", "datasets", "graders"],
                "updated_at": "2026-06-08T14:00:00Z",
                "root_files": ["README.md", "evals", "examples", "pyproject.toml"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T16:10:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["explodinggradients/ragas"]["family"] == "novel-automation"
    assert "context_faithfulness_eval_gate" in by_title["explodinggradients/ragas"]["absorbed_patterns"]
    assert "context_faithfulness_eval_gate" in by_title["confident-ai/deepeval"]["absorbed_patterns"]
    assert "prompt_regression_eval_suite" in by_title["confident-ai/deepeval"]["absorbed_patterns"]
    assert "retrieval_trace_observability_gate" in by_title["truera/trulens"]["absorbed_patterns"]
    assert "retrieval_trace_observability_gate" in by_title["Arize-ai/phoenix"]["absorbed_patterns"]
    assert "prompt_regression_eval_suite" in by_title["promptfoo/promptfoo"]["absorbed_patterns"]
    assert "prompt_regression_eval_suite" in by_title["openai/evals"]["absorbed_patterns"]


def test_eval_observability_pattern_pack_exposes_grounding_and_regression_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T16:15:00+08:00",
        "candidate_count": 3,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/explodinggradients/ragas",
                "title": "explodinggradients/ragas",
                "summary": "RAG evaluation with faithfulness, answer relevancy, context precision and context recall.",
                "stars": 11000,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["context_faithfulness_eval_gate"],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/truera/trulens",
                "title": "truera/trulens",
                "summary": "LLM app observability with groundedness, context relevance, answer relevance and traces.",
                "stars": 2600,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["retrieval_trace_observability_gate"],
                "score": 79,
            },
            {
                "source": "github",
                "url": "https://github.com/promptfoo/promptfoo",
                "title": "promptfoo/promptfoo",
                "summary": "Prompt tests, assertions, golden datasets, regression suites and CI evaluation.",
                "stars": 8500,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["prompt_regression_eval_suite"],
                "score": 77,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "context_faithfulness_eval_report" in pattern_pack["whole_book_analysis_targets"]
    assert "retrieval_trace_eval_report" in pattern_pack["whole_book_analysis_targets"]
    assert "prompt_regression_suite" in pattern_pack["whole_book_analysis_targets"]
    assert "faithfulness_eval_thresholds" in pattern_pack["bible_enrichment_targets"]
    assert "context_faithfulness_eval_gate_hints" in pattern_pack
    assert "retrieval_trace_observability_gate_hints" in pattern_pack
    assert "prompt_regression_eval_suite_hints" in pattern_pack
    assert "faithfulness_eval_remap" in pattern_pack["inspired_mapping_targets"]
    assert "retrieval_trace_remap" in pattern_pack["inspired_mapping_targets"]
    assert "prompt_regression_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "context_faithfulness_eval_gate_hints" in digest
    assert "retrieval_trace_observability_gate_hints" in digest
    assert "prompt_regression_eval_suite_hints" in digest


def test_default_discovery_sources_include_eval_observability_projects():
    assert "https://github.com/explodinggradients/ragas" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/confident-ai/deepeval" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/truera/trulens" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Arize-ai/phoenix" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/promptfoo/promptfoo" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/openai/evals" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("faithfulness" in query.lower() and "context precision" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("observability" in query.lower() and "trace" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("prompt" in query.lower() and "regression" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_longwriter_sources_are_classified_as_plan_write_length_and_reward_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "THUDM/LongWriter",
                "html_url": "https://github.com/THUDM/LongWriter",
                "description": "LongWriter unleashes 10,000+ word generation with AgentWrite, LongBench-Write and LongWrite-Ruler evaluation.",
                "stargazers_count": 1865,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["longwriter", "long-form", "evaluation"],
                "updated_at": "2026-06-09T12:52:38Z",
                "root_files": ["README.md", "agentwrite", "evaluation", "requirements.txt"],
            },
            {
                "full_name": "THUDM/LongReward",
                "html_url": "https://github.com/THUDM/LongReward",
                "description": "LongReward scores long-context scenarios for helpfulness, logicality, faithfulness and completeness.",
                "stargazers_count": 62,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["long-context", "reward", "evaluation"],
                "updated_at": "2025-12-29T13:04:31Z",
                "root_files": ["README.md", "long_reward", "evaluation", "requirements.txt"],
            },
            {
                "full_name": "THU-KEG/LongWriter-V",
                "html_url": "https://github.com/THU-KEG/LongWriter-V",
                "description": "LongWriter-V enables ultra-long generation with LongWriter-Agent-V, MMLongBench-Write and LongWrite-V-Ruler.",
                "stargazers_count": 22,
                "license": {"spdx_id": "MIT"},
                "topics": ["longwriter", "ultra-long", "vision-language"],
                "updated_at": "2026-04-11T07:16:02Z",
                "root_files": ["README.md", "agentwrite", "eval", "requirements.txt"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T18:20:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["THUDM/LongWriter"]["family"] == "novel-automation"
    assert "agentwrite_plan_write_pipeline" in by_title["THUDM/LongWriter"]["absorbed_patterns"]
    assert "long_output_length_quality_ruler" in by_title["THUDM/LongWriter"]["absorbed_patterns"]
    assert "long_context_reward_dimension_gate" in by_title["THUDM/LongReward"]["absorbed_patterns"]
    assert "agentwrite_plan_write_pipeline" in by_title["THU-KEG/LongWriter-V"]["absorbed_patterns"]
    assert "long_output_length_quality_ruler" in by_title["THU-KEG/LongWriter-V"]["absorbed_patterns"]


def test_long_output_pattern_pack_exposes_plan_write_ruler_and_reward_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T18:25:00+08:00",
        "candidate_count": 3,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/THUDM/LongWriter",
                "title": "THUDM/LongWriter",
                "summary": "AgentWrite plan.py/write.py plus LongBench-Write and LongWrite-Ruler.",
                "stars": 1865,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["agentwrite_plan_write_pipeline", "long_output_length_quality_ruler"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/THUDM/LongReward",
                "title": "THUDM/LongReward",
                "summary": "Long-context reward dimensions: helpfulness, logicality, faithfulness, completeness.",
                "stars": 62,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["long_context_reward_dimension_gate"],
                "score": 80,
            },
            {
                "source": "github",
                "url": "https://github.com/THU-KEG/LongWriter-V",
                "title": "THU-KEG/LongWriter-V",
                "summary": "LongWriter-Agent-V outline_vlm.py, MMLongBench-Write and LongWrite-V-Ruler.",
                "stars": 22,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["agentwrite_plan_write_pipeline", "long_output_length_quality_ruler"],
                "score": 78,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "agentwrite_plan_artifacts" in pattern_pack["bible_enrichment_targets"]
    assert "long_output_length_targets" in pattern_pack["bible_enrichment_targets"]
    assert "long_context_reward_dimensions" in pattern_pack["bible_enrichment_targets"]
    assert "long_output_length_report" in pattern_pack["whole_book_analysis_targets"]
    assert "long_context_reward_scores" in pattern_pack["whole_book_analysis_targets"]
    assert "plan_write_stage_remap" in pattern_pack["inspired_mapping_targets"]
    assert "long_output_ruler_remap" in pattern_pack["inspired_mapping_targets"]
    assert "reward_dimension_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "agentwrite_plan_write_pipeline_hints" in digest
    assert "long_output_length_quality_ruler_hints" in digest
    assert "long_context_reward_dimension_gate_hints" in digest


def test_default_discovery_sources_include_longwriter_family_projects():
    assert "https://github.com/THUDM/LongWriter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/THUDM/LongReward" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/THU-KEG/LongWriter-V" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("agentwrite" in query.lower() and "longwriter" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("helpfulness" in query.lower() and "completeness" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("ultra-long" in query.lower() and "long output quality" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_writing_benchmark_sources_classify_into_creative_eval_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "X-PLUG/WritingBench",
                "html_url": "https://github.com/X-PLUG/WritingBench",
                "description": "Comprehensive benchmark for generative writing with real-world queries, 5 instance-specific criteria, requirement-dimension scores, model-augmented query generation, and human-in-the-loop refinement.",
                "stargazers_count": 412,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["writing", "benchmark", "llm-evaluation"],
                "updated_at": "2025-11-27T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "benchmark_query", "prompt.py"],
            },
            {
                "full_name": "EQ-bench/creative-writing-bench",
                "html_url": "https://github.com/EQ-bench/creative-writing-bench",
                "description": "Creative Writing Benchmark v3 with hybrid rubric, pairwise matchups, Elo and Glicko-2 scoring, and judge bias mitigation for length, position, verbosity, and poetic incoherence.",
                "stargazers_count": 293,
                "license": None,
                "topics": ["creative-writing", "benchmark", "elo"],
                "updated_at": "2026-06-01T00:00:00Z",
                "root_files": ["README.md", "requirements.txt", ".env.example", "data"],
            },
            {
                "full_name": "EQ-bench/longform-writing-bench",
                "html_url": "https://github.com/EQ-bench/longform-writing-bench",
                "description": "Longform Creative Writing Benchmark evaluates brainstorming and planning, critical reflection, character profiles, 8 chapter novella writing, and narrative consistency.",
                "stargazers_count": 185,
                "license": None,
                "topics": ["longform", "creative-writing", "benchmark"],
                "updated_at": "2026-06-01T00:00:00Z",
                "root_files": ["README.md", "longform_writing_bench.py", "prompts", "results"],
            },
            {
                "full_name": "dig-team/hanna-benchmark-asg",
                "html_url": "https://github.com/dig-team/hanna-benchmark-asg",
                "description": "HANNA human-annotated narratives for automatic story generation evaluation with relevance, coherence, empathy, surprise, engagement, complexity, automatic metrics and LLM explanations.",
                "stargazers_count": 81,
                "license": {"spdx_id": "MIT"},
                "topics": ["story-generation", "evaluation", "dataset"],
                "updated_at": "2024-05-13T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "hanna_stories_annotations.csv", "hanna_metrics_scores_llm.csv"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T19:00:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["X-PLUG/WritingBench"]["family"] == "novel-automation"
    assert "instance_specific_writing_criteria_gate" in by_title["X-PLUG/WritingBench"]["absorbed_patterns"]
    assert "material_grounded_query_refinement" in by_title["X-PLUG/WritingBench"]["absorbed_patterns"]
    assert "hybrid_rubric_pairwise_elo_judge" in by_title["EQ-bench/creative-writing-bench"]["absorbed_patterns"]
    assert "judge_bias_mitigation_check" in by_title["EQ-bench/creative-writing-bench"]["absorbed_patterns"]
    assert "plan_reflect_character_chapter_pipeline" in by_title["EQ-bench/longform-writing-bench"]["absorbed_patterns"]
    assert "human_story_metric_panel" in by_title["dig-team/hanna-benchmark-asg"]["absorbed_patterns"]


def test_writing_benchmark_pattern_pack_exposes_criteria_elo_and_human_metric_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T19:05:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/X-PLUG/WritingBench",
                "title": "X-PLUG/WritingBench",
                "summary": "WritingBench uses 5 instance-specific criteria, requirement dimensions and human-in-the-loop material refinement.",
                "stars": 412,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["instance_specific_writing_criteria_gate", "material_grounded_query_refinement"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/EQ-bench/creative-writing-bench",
                "title": "EQ-bench/creative-writing-bench",
                "summary": "Creative Writing Benchmark v3 uses hybrid rubric, pairwise Elo/Glicko-2 and judge bias mitigation.",
                "stars": 293,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["hybrid_rubric_pairwise_elo_judge", "judge_bias_mitigation_check"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/EQ-bench/longform-writing-bench",
                "title": "EQ-bench/longform-writing-bench",
                "summary": "Longform benchmark chains brainstorm, plan, reflection, character profiles and 8 chapters.",
                "stars": 185,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["plan_reflect_character_chapter_pipeline"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/dig-team/hanna-benchmark-asg",
                "title": "dig-team/hanna-benchmark-asg",
                "summary": "HANNA scores generated stories by relevance, coherence, empathy, surprise, engagement and complexity.",
                "stars": 81,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["human_story_metric_panel"],
                "score": 82,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "instance_specific_writing_criteria" in pattern_pack["bible_enrichment_targets"]
    assert "material_requirement_notes" in pattern_pack["bible_enrichment_targets"]
    assert "hybrid_rubric_pairwise_elo_report" in pattern_pack["whole_book_analysis_targets"]
    assert "plan_reflection_character_profile_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "human_story_metric_scores" in pattern_pack["whole_book_analysis_targets"]
    assert "instance_criteria_remap" in pattern_pack["inspired_mapping_targets"]
    assert "judge_bias_mitigation_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "instance_specific_writing_criteria_gate_hints" in digest
    assert "hybrid_rubric_pairwise_elo_judge_hints" in digest
    assert "human_story_metric_panel_hints" in digest


def test_default_discovery_sources_include_creative_writing_benchmark_projects():
    assert "https://github.com/X-PLUG/WritingBench" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/EQ-bench/creative-writing-bench" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/EQ-bench/longform-writing-bench" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/dig-team/hanna-benchmark-asg" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("instance-specific criteria" in query.lower() and "writingbench" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("elo" in query.lower() and "creative writing benchmark" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("hanna" in query.lower() and "story evaluation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_story_generation_pipeline_sources_classify_into_structure_and_persona_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "google-deepmind/dramatron",
                "html_url": "https://github.com/google-deepmind/dramatron",
                "description": "Dramatron co-writing system uses hierarchical story generation from log line to character descriptions, plot points, location descriptions and dialogue, with human editing and rewriting.",
                "stargazers_count": 2320,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["story-generation", "screenplay", "cowriting"],
                "updated_at": "2026-01-15T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "colab", "dramatron"],
            },
            {
                "full_name": "yangkevin2/emnlp22-re3-story-generation",
                "html_url": "https://github.com/yangkevin2/emnlp22-re3-story-generation",
                "description": "Re3 generates longer stories with recursive reprompting and revision using Plan, Draft, Rewrite, Edit modules, relevance/coherence rerankers, outline reload and dynamic continuation thresholds.",
                "stargazers_count": 522,
                "license": {"spdx_id": "MIT"},
                "topics": ["story-generation", "long-story", "revision"],
                "updated_at": "2022-12-20T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "scripts", "notebooks", "requirements.txt"],
            },
            {
                "full_name": "LC1332/Chat-Haruhi-Suzumiya",
                "html_url": "https://github.com/LC1332/Chat-Haruhi-Suzumiya",
                "description": "Chat-Haruhi imitates anime characters with approximate tone, personality and plot chat, includes extracting characters from novels, personality research and role datasets.",
                "stargazers_count": 8200,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["role-playing", "character", "dialogue"],
                "updated_at": "2026-05-20T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "characters", "research", "notebook"],
            },
            {
                "full_name": "rajammanabrolu/StoryRealization",
                "html_url": "https://github.com/rajammanabrolu/StoryRealization",
                "description": "Story Realization expands plot events into sentences with event creation, slot filling, a memory graph for entities, ensemble thresholds and confidence scores.",
                "stargazers_count": 154,
                "license": None,
                "topics": ["story-generation", "event-to-sentence", "plot"],
                "updated_at": "2020-01-01T00:00:00Z",
                "root_files": ["README.md", "EventCreation", "E2S-Ensemble", "Slotfilling"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T19:30:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["google-deepmind/dramatron"]["family"] == "novel-automation"
    assert "hierarchical_cowriting_story_scaffold" in by_title["google-deepmind/dramatron"]["absorbed_patterns"]
    assert "human_coauthor_edit_boundary" in by_title["google-deepmind/dramatron"]["absorbed_patterns"]
    assert "recursive_reprompt_revision_loop" in by_title["yangkevin2/emnlp22-re3-story-generation"]["absorbed_patterns"]
    assert "reranker_guided_candidate_selection" in by_title["yangkevin2/emnlp22-re3-story-generation"]["absorbed_patterns"]
    assert "character_dialogue_persona_memory" in by_title["LC1332/Chat-Haruhi-Suzumiya"]["absorbed_patterns"]
    assert "event_to_sentence_realization_trace" in by_title["rajammanabrolu/StoryRealization"]["absorbed_patterns"]
    assert "entity_memory_slotfill_grounding" in by_title["rajammanabrolu/StoryRealization"]["absorbed_patterns"]


def test_story_generation_pipeline_pattern_pack_exposes_structure_revision_and_persona_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T19:35:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/google-deepmind/dramatron",
                "title": "google-deepmind/dramatron",
                "summary": "Hierarchical co-writing from logline to characters, plot points, locations and dialogue.",
                "stars": 2320,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["hierarchical_cowriting_story_scaffold", "human_coauthor_edit_boundary"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/yangkevin2/emnlp22-re3-story-generation",
                "title": "yangkevin2/emnlp22-re3-story-generation",
                "summary": "Re3 uses Plan, Draft, Rewrite and Edit with relevance/coherence rerankers.",
                "stars": 522,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["recursive_reprompt_revision_loop", "reranker_guided_candidate_selection"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/LC1332/Chat-Haruhi-Suzumiya",
                "title": "LC1332/Chat-Haruhi-Suzumiya",
                "summary": "Character imitation from tone, personality, plot chat and novel character extraction.",
                "stars": 8200,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["character_dialogue_persona_memory"],
                "score": 87,
            },
            {
                "source": "github",
                "url": "https://github.com/rajammanabrolu/StoryRealization",
                "title": "rajammanabrolu/StoryRealization",
                "summary": "Event-to-sentence realization with slot filling, memory graph, ensemble thresholds and confidence scores.",
                "stars": 154,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["event_to_sentence_realization_trace", "entity_memory_slotfill_grounding"],
                "score": 84,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "logline_character_plot_location_dialogue_scaffold" in pattern_pack["bible_enrichment_targets"]
    assert "recursive_reprompt_revision_policy" in pattern_pack["bible_enrichment_targets"]
    assert "character_persona_dialogue_evidence" in pattern_pack["bible_enrichment_targets"]
    assert "event_to_sentence_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "entity_memory_slotfill_report" in pattern_pack["whole_book_analysis_targets"]
    assert "hierarchical_story_scaffold_remap" in pattern_pack["inspired_mapping_targets"]
    assert "character_persona_memory_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "hierarchical_cowriting_story_scaffold_hints" in digest
    assert "recursive_reprompt_revision_loop_hints" in digest
    assert "character_dialogue_persona_memory_hints" in digest
    assert "event_to_sentence_realization_trace_hints" in digest


def test_default_discovery_sources_include_story_generation_pipeline_projects():
    assert "https://github.com/google-deepmind/dramatron" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/yangkevin2/emnlp22-re3-story-generation" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/LC1332/Chat-Haruhi-Suzumiya" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/rajammanabrolu/StoryRealization" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("dramatron" in query.lower() and "log line" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("recursive reprompting" in query.lower() and "revision" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("chat-haruhi" in query.lower() and "character" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_source_deconstruction_memory_sources_classify_into_context_and_glossary_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "gratajik/book-memory-bank",
                "html_url": "https://github.com/gratajik/book-memory-bank",
                "description": "Book Memory Bank provides a structured documentation system for stateless AI book writing with projectbrief.md, story_structure.md, world_and_characters.md, activeContext.md and progress.md.",
                "stargazers_count": 39,
                "license": None,
                "topics": ["book-writing", "memory-bank", "novel"],
                "updated_at": "2026-05-10T04:07:22Z",
                "root_files": ["Core", "Production", "README.md", "Style", "book-memory_bank.md"],
            },
            {
                "full_name": "adaumann/speckit-preset-fiction-book-writing",
                "html_url": "https://github.com/adaumann/speckit-preset-fiction-book-writing",
                "description": "Spec Kit Fiction preset uses story bible governance through constitution.md, scene-by-scene writing tasks, POV schedule, information asymmetry map, glossary audit and quality gates.",
                "stargazers_count": 11,
                "license": None,
                "topics": ["fiction", "spec-kit", "novel-writing"],
                "updated_at": "2026-06-09T15:28:17Z",
                "root_files": ["README.md", "catalog.community.json", "fiction-book-writing"],
            },
            {
                "full_name": "danngalann/llm-ebook-summarizer",
                "html_url": "https://github.com/danngalann/llm-ebook-summarizer",
                "description": "LLM Ebook Summarizer extracts EPUB files and PDF files with table of contents, nested chapters, parent section introductions, structured markdown notes, quotes and anecdotes.",
                "stargazers_count": 1,
                "license": None,
                "topics": ["ebook", "summarizer", "chapters"],
                "updated_at": "2026-04-25T18:53:52Z",
                "root_files": ["README.md", "epub_extractor.py", "pdf_extractor.py", "merge_markdowns.py"],
            },
            {
                "full_name": "darkautism/ai-novel-translation",
                "html_url": "https://github.com/darkautism/ai-novel-translation",
                "description": "AI Novel Translation uses two-pass translation: Pass 1 (Analysis) creates summary and extracts proper nouns/terms, Pass 2 uses previous chapter summary, cumulative glossary and resume support.",
                "stargazers_count": 0,
                "license": None,
                "topics": ["novel", "translation", "glossary"],
                "updated_at": "2026-02-23T17:47:32Z",
                "root_files": ["Cargo.toml", "Readme.md", "config.yml", "src"],
            },
            {
                "full_name": "lordjabez/story-framework",
                "html_url": "https://github.com/lordjabez/story-framework",
                "description": "Story Framework uses markdown files and git as source of truth with Continuity/timeline.md, Continuity/facts.md, author notes, edit notes, process edit notes and git tag milestones.",
                "stargazers_count": 2,
                "license": {"spdx_id": "MIT-0"},
                "topics": ["fiction", "markdown", "story-framework"],
                "updated_at": "2026-01-22T00:32:02Z",
                "root_files": ["README.md", "Characters", "Continuity", "Drafts", "Final", "LICENSE"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T21:10:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["gratajik/book-memory-bank"]["family"] == "novel-automation"
    assert "book_memory_bank_context_lattice" in by_title["gratajik/book-memory-bank"]["absorbed_patterns"]
    assert "spec_driven_fiction_scene_tasks" in by_title["adaumann/speckit-preset-fiction-book-writing"]["absorbed_patterns"]
    assert "toc_aware_source_deconstruction" in by_title["danngalann/llm-ebook-summarizer"]["absorbed_patterns"]
    assert "two_pass_context_glossary_pipeline" in by_title["darkautism/ai-novel-translation"]["absorbed_patterns"]
    assert "inline_author_edit_markup_versioning" in by_title["lordjabez/story-framework"]["absorbed_patterns"]


def test_source_deconstruction_memory_pattern_pack_exposes_context_glossary_and_edit_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T21:15:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/gratajik/book-memory-bank",
                "title": "gratajik/book-memory-bank",
                "summary": "Memory-bank context lattice for stateless AI book writing.",
                "stars": 39,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["book_memory_bank_context_lattice"],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/adaumann/speckit-preset-fiction-book-writing",
                "title": "adaumann/speckit-preset-fiction-book-writing",
                "summary": "Spec-driven fiction tasks, constitution, POV and glossary gates.",
                "stars": 11,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["spec_driven_fiction_scene_tasks"],
                "score": 81,
            },
            {
                "source": "github",
                "url": "https://github.com/danngalann/llm-ebook-summarizer",
                "title": "danngalann/llm-ebook-summarizer",
                "summary": "TOC-aware source deconstruction for nested chapter summaries.",
                "stars": 1,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["toc_aware_source_deconstruction"],
                "score": 80,
            },
            {
                "source": "github",
                "url": "https://github.com/darkautism/ai-novel-translation",
                "title": "darkautism/ai-novel-translation",
                "summary": "Two-pass chapter summary and cumulative glossary pipeline.",
                "stars": 0,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["two_pass_context_glossary_pipeline"],
                "score": 79,
            },
            {
                "source": "github",
                "url": "https://github.com/lordjabez/story-framework",
                "title": "lordjabez/story-framework",
                "summary": "Inline author notes, edit notes and git revision milestones.",
                "stars": 2,
                "license": "MIT-0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["inline_author_edit_markup_versioning"],
                "score": 78,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "book_memory_bank_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "fiction_constitution" in pattern_pack["bible_enrichment_targets"]
    assert "source_toc_deconstruction_index" in pattern_pack["bible_enrichment_targets"]
    assert "cumulative_glossary" in pattern_pack["bible_enrichment_targets"]
    assert "inline_author_edit_markup_policy" in pattern_pack["bible_enrichment_targets"]
    assert "memory_bank_completeness_report" in pattern_pack["whole_book_analysis_targets"]
    assert "two_pass_glossary_consistency_report" in pattern_pack["whole_book_analysis_targets"]
    assert "memory_bank_context_remap" in pattern_pack["inspired_mapping_targets"]
    assert "glossary_context_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "book_memory_bank_context_lattice_hints" in digest
    assert "spec_driven_fiction_scene_tasks_hints" in digest
    assert "toc_aware_source_deconstruction_hints" in digest
    assert "two_pass_context_glossary_pipeline_hints" in digest
    assert "inline_author_edit_markup_versioning_hints" in digest


def test_default_discovery_sources_include_source_deconstruction_memory_projects():
    assert "https://github.com/gratajik/book-memory-bank" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/adaumann/speckit-preset-fiction-book-writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/danngalann/llm-ebook-summarizer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/darkautism/ai-novel-translation" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/lordjabez/story-framework" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("book memory bank" in query.lower() and "stateless ai" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("spec kit" in query.lower() and "scene-by-scene writing tasks" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("nested chapters" in query.lower() and "parent section introductions" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("two-pass translation" in query.lower() and "cumulative glossary" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_graph_memory_rag_sources_classify_into_temporal_and_retrieval_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "getzep/graphiti",
                "html_url": "https://github.com/getzep/graphiti",
                "description": "Graphiti is a temporal knowledge graph for AI agents with episodes, temporal context, provenance tracking, hybrid search and entity relationship extraction for novel canon memory.",
                "stargazers_count": 15400,
                "license": None,
                "topics": ["knowledge-graph", "agent-memory", "rag"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "graphiti_core", "server", "pyproject.toml"],
            },
            {
                "full_name": "mem0ai/mem0",
                "html_url": "https://github.com/mem0ai/mem0",
                "description": "Mem0 provides a memory layer for AI agents with long-term memory, user preferences, session memory, adaptive personalization, multi-level memory and episodic memory for author preference memory.",
                "stargazers_count": 38200,
                "license": None,
                "topics": ["memory", "ai-agents", "personalization"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "mem0", "server", "pyproject.toml"],
            },
            {
                "full_name": "microsoft/graphrag",
                "html_url": "https://github.com/microsoft/graphrag",
                "description": "GraphRAG extracts structured data from unstructured text into entity extraction, community reports, community summaries, global search and local search for source-book deconstruction.",
                "stargazers_count": 30100,
                "license": {"spdx_id": "MIT"},
                "topics": ["graphrag", "rag", "knowledge-graph"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "graphrag", "pyproject.toml"],
            },
            {
                "full_name": "HKUDS/LightRAG",
                "html_url": "https://github.com/HKUDS/LightRAG",
                "description": "LightRAG uses knowledge graphs and vector embeddings in a dual-level architecture with local, global, hybrid and naive query modes for story context retrieval.",
                "stargazers_count": 24500,
                "license": {"spdx_id": "MIT"},
                "topics": ["rag", "knowledge-graph", "vector-search"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "lightrag", "requirements.txt"],
            },
            {
                "full_name": "neo4j-labs/llm-graph-builder",
                "html_url": "https://github.com/neo4j-labs/llm-graph-builder",
                "description": "LLM Graph Builder extracts nodes, relationships and properties with custom schema, node labels, relationship types, source metadata and Neo4j graph for novel canon extraction.",
                "stargazers_count": 3200,
                "license": None,
                "topics": ["knowledge-graph", "neo4j", "llm"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "frontend", "backend", "docker-compose.yml"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T22:10:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["getzep/graphiti"]["family"] == "novel-automation"
    assert "temporal_canon_context_graph" in by_title["getzep/graphiti"]["absorbed_patterns"]
    assert "long_term_author_preference_memory" in by_title["mem0ai/mem0"]["absorbed_patterns"]
    assert "community_graph_source_deconstruction" in by_title["microsoft/graphrag"]["absorbed_patterns"]
    assert "dual_level_graph_vector_retrieval" in by_title["HKUDS/LightRAG"]["absorbed_patterns"]
    assert "schema_guided_graph_extraction" in by_title["neo4j-labs/llm-graph-builder"]["absorbed_patterns"]


def test_graph_memory_rag_pattern_pack_exposes_temporal_graph_and_retrieval_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T22:15:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/getzep/graphiti",
                "title": "getzep/graphiti",
                "summary": "Temporal canon graph with episodes and provenance.",
                "stars": 15400,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["temporal_canon_context_graph"],
                "score": 92,
            },
            {
                "source": "github",
                "url": "https://github.com/mem0ai/mem0",
                "title": "mem0ai/mem0",
                "summary": "Long-term author preference memory layers.",
                "stars": 38200,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["long_term_author_preference_memory"],
                "score": 91,
            },
            {
                "source": "github",
                "url": "https://github.com/microsoft/graphrag",
                "title": "microsoft/graphrag",
                "summary": "Community graph summaries for source deconstruction.",
                "stars": 30100,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["community_graph_source_deconstruction"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/HKUDS/LightRAG",
                "title": "HKUDS/LightRAG",
                "summary": "Dual-level graph and vector retrieval.",
                "stars": 24500,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["dual_level_graph_vector_retrieval"],
                "score": 89,
            },
            {
                "source": "github",
                "url": "https://github.com/neo4j-labs/llm-graph-builder",
                "title": "neo4j-labs/llm-graph-builder",
                "summary": "Schema-guided node relationship property extraction.",
                "stars": 3200,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker"],
                "absorbed_patterns": ["schema_guided_graph_extraction"],
                "score": 88,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "temporal_canon_graph_schema" in pattern_pack["bible_enrichment_targets"]
    assert "author_preference_memory_layers" in pattern_pack["bible_enrichment_targets"]
    assert "source_entity_community_graph" in pattern_pack["bible_enrichment_targets"]
    assert "graph_vector_retrieval_policy" in pattern_pack["bible_enrichment_targets"]
    assert "canon_graph_extraction_schema" in pattern_pack["bible_enrichment_targets"]
    assert "temporal_canon_graph_report" in pattern_pack["whole_book_analysis_targets"]
    assert "source_community_summary_report" in pattern_pack["whole_book_analysis_targets"]
    assert "graph_vector_retrieval_report" in pattern_pack["whole_book_analysis_targets"]
    assert "temporal_graph_context_remap" in pattern_pack["inspired_mapping_targets"]
    assert "schema_guided_graph_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "temporal_canon_context_graph_hints" in digest
    assert "long_term_author_preference_memory_hints" in digest
    assert "community_graph_source_deconstruction_hints" in digest
    assert "dual_level_graph_vector_retrieval_hints" in digest
    assert "schema_guided_graph_extraction_hints" in digest


def test_default_discovery_sources_include_graph_memory_rag_projects():
    assert "https://github.com/getzep/graphiti" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/mem0ai/mem0" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/microsoft/graphrag" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/HKUDS/LightRAG" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/neo4j-labs/llm-graph-builder" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("temporal knowledge graph" in query.lower() and "agent memory" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("long-term memory" in query.lower() and "personalized ai" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("graphrag" in query.lower() and "community summaries" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("dual-level architecture" in query.lower() and "lightrag" in query.lower() for query in DEFAULT_GITHUB_QUERIES)



def test_prose_copyedit_sources_classify_into_lint_grammar_and_triage_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "vale-cli/vale",
                "html_url": "https://github.com/vale-cli/vale",
                "description": "Vale is a prose linter and style linter with style guide rules, Markdown checks, lint diagnostics, and house style profiles for manuscript copyedit.",
                "stargazers_count": 18000,
                "license": {"spdx_id": "MIT"},
                "topics": ["prose", "linter", "markdown", "writing"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "go.mod", "styles"],
            },
            {
                "full_name": "textlint/textlint",
                "html_url": "https://github.com/textlint/textlint",
                "description": "Textlint is a pluggable natural language linter and text linter for Markdown with configurable rule packages, rule violations and suppression comments.",
                "stargazers_count": 11000,
                "license": {"spdx_id": "MIT"},
                "topics": ["lint", "natural-language", "markdown"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["package.json", "packages", "README.md"],
                "package_scripts": {"test": "pnpm test"},
            },
            {
                "full_name": "amperser/proselint",
                "html_url": "https://github.com/amperser/proselint",
                "description": "Proselint checks prose for cliches, jargon, passive voice, redundancy and copyedit suggestions that should become revision queue diagnostics.",
                "stargazers_count": 4300,
                "license": {"spdx_id": "BSD-3-Clause"},
                "topics": ["prose", "style", "lint"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "setup.py", "proselint"],
            },
            {
                "full_name": "Automattic/harper",
                "html_url": "https://github.com/Automattic/harper",
                "description": "Harper is an offline grammar checker with spelling and grammar diagnostics, copyedit suggestions, language server support and proofreading for prose.",
                "stargazers_count": 8500,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["grammar", "spellcheck", "lsp", "writing"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "Cargo.toml", "packages"],
            },
            {
                "full_name": "languagetool-org/languagetool",
                "html_url": "https://github.com/languagetool-org/languagetool",
                "description": "LanguageTool provides multilingual grammar checker, spell checker, proofreading, style and copyediting rules with server and client surfaces.",
                "stargazers_count": 13000,
                "license": {"spdx_id": "LGPL-2.1"},
                "topics": ["grammar", "spell-checker", "proofreading"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "pom.xml", "languagetool-core"],
            },
            {
                "full_name": "btford/write-good",
                "html_url": "https://github.com/btford/write-good",
                "description": "Write-good is a prose style checker for passive voice, weasel words, adverbs, cliches, hard-to-read text, suggestions and lint diagnostics.",
                "stargazers_count": 5600,
                "license": {"spdx_id": "MIT"},
                "topics": ["writing", "style", "prose"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "package.json"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T23:30:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["vale-cli/vale"]["family"] == "novel-automation"
    assert "prose_lint_style_rule_gate" in by_title["vale-cli/vale"]["absorbed_patterns"]
    assert "copyedit_diagnostic_triage_queue" in by_title["textlint/textlint"]["absorbed_patterns"]
    assert "prose_lint_style_rule_gate" in by_title["amperser/proselint"]["absorbed_patterns"]
    assert "grammar_spelling_copyedit_gate" in by_title["Automattic/harper"]["absorbed_patterns"]
    assert "grammar_spelling_copyedit_gate" in by_title["languagetool-org/languagetool"]["absorbed_patterns"]
    assert "copyedit_diagnostic_triage_queue" in by_title["btford/write-good"]["absorbed_patterns"]


def test_prose_copyedit_pattern_pack_exposes_lint_grammar_and_triage_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T23:35:00+08:00",
        "candidate_count": 3,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/vale-cli/vale",
                "title": "vale-cli/vale",
                "summary": "Prose lint house-style rule gate for Markdown manuscripts.",
                "stars": 18000,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["prose_lint_style_rule_gate"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/Automattic/harper",
                "title": "Automattic/harper",
                "summary": "Offline grammar and spelling copyedit gate.",
                "stars": 8500,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["grammar_spelling_copyedit_gate"],
                "score": 89,
            },
            {
                "source": "github",
                "url": "https://github.com/textlint/textlint",
                "title": "textlint/textlint",
                "summary": "Lint diagnostic triage queue with accepted ignored rule decisions.",
                "stars": 11000,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["copyedit_diagnostic_triage_queue"],
                "score": 88,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "prose_lint_rule_profile" in pattern_pack["bible_enrichment_targets"]
    assert "grammar_spelling_boundary_rules" in pattern_pack["bible_enrichment_targets"]
    assert "copyedit_diagnostic_queue" in pattern_pack["bible_enrichment_targets"]
    assert "prose_lint_report" in pattern_pack["whole_book_analysis_targets"]
    assert "grammar_spelling_report" in pattern_pack["whole_book_analysis_targets"]
    assert "copyedit_diagnostic_triage_report" in pattern_pack["whole_book_analysis_targets"]
    assert "prose_lint_rule_remap" in pattern_pack["inspired_mapping_targets"]
    assert "grammar_copyedit_exception_remap" in pattern_pack["inspired_mapping_targets"]
    assert "copyedit_triage_policy_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "prose_lint_style_rule_gate_hints" in digest
    assert "grammar_spelling_copyedit_gate_hints" in digest
    assert "copyedit_diagnostic_triage_queue_hints" in digest


def test_default_discovery_sources_include_prose_copyedit_projects():
    assert "https://github.com/vale-cli/vale" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/textlint/textlint" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/amperser/proselint" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Automattic/harper" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/languagetool-org/languagetool" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/btford/write-good" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("prose lint" in query.lower() and "copyedit" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("grammar checker" in query.lower() and "proofreading" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("natural language linter" in query.lower() and "write-good" in query.lower() for query in DEFAULT_GITHUB_QUERIES)



def test_chinese_text_processing_sources_classify_into_segmentation_entity_normalization_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "fxsjy/jieba",
                "html_url": "https://github.com/fxsjy/jieba",
                "description": "Jieba provides Chinese word segmentation, custom dictionary support, TF-IDF and TextRank keyword extraction for Chinese manuscript text analysis.",
                "stargazers_count": 33500,
                "license": {"spdx_id": "MIT"},
                "topics": ["chinese", "word-segmentation", "keyword-extraction"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "jieba", "setup.py"],
            },
            {
                "full_name": "hankcs/HanLP",
                "html_url": "https://github.com/hankcs/HanLP",
                "description": "HanLP supports Chinese word segmentation, Chinese NER, named entity recognition, aliases, person name, location name and organization name analysis.",
                "stargazers_count": 36500,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["nlp", "chinese", "ner"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "plugins", "hanlp"],
            },
            {
                "full_name": "HIT-SCIR/ltp",
                "html_url": "https://github.com/HIT-SCIR/ltp",
                "description": "LTP is a Chinese NLP toolkit with segmentation, POS, Chinese NER, entity recognition, dependency and semantic role analysis.",
                "stargazers_count": 7800,
                "license": None,
                "topics": ["chinese", "nlp", "ner"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "ltp", "pyproject.toml"],
            },
            {
                "full_name": "BYVoid/OpenCC",
                "html_url": "https://github.com/BYVoid/OpenCC",
                "description": "OpenCC provides Simplified Chinese and Traditional Chinese conversion, Chinese conversion and text normalization for variants.",
                "stargazers_count": 9600,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["opencc", "chinese", "normalization"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "CMakeLists.txt", "data"],
            },
            {
                "full_name": "shibing624/pycorrector",
                "html_url": "https://github.com/shibing624/pycorrector",
                "description": "PyCorrector provides Chinese spelling correction, Chinese text correction, confusion set review and proofreading workflows.",
                "stargazers_count": 8400,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["chinese", "correction", "proofreading"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "pycorrector", "requirements.txt"],
            },
            {
                "full_name": "messense/jieba-rs",
                "html_url": "https://github.com/messense/jieba-rs",
                "description": "Jieba-rs is a Rust Chinese tokenizer for Chinese word segmentation with deterministic dictionary behavior.",
                "stargazers_count": 2100,
                "license": {"spdx_id": "MIT"},
                "topics": ["jieba", "rust", "chinese"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "Cargo.toml", "src"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T00:10:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["fxsjy/jieba"]["family"] == "novel-automation"
    assert "chinese_segmentation_keyword_gate" in by_title["fxsjy/jieba"]["absorbed_patterns"]
    assert "chinese_segmentation_keyword_gate" in by_title["messense/jieba-rs"]["absorbed_patterns"]
    assert "chinese_ner_alias_consistency_gate" in by_title["hankcs/HanLP"]["absorbed_patterns"]
    assert "chinese_ner_alias_consistency_gate" in by_title["HIT-SCIR/ltp"]["absorbed_patterns"]
    assert "chinese_text_normalization_gate" in by_title["BYVoid/OpenCC"]["absorbed_patterns"]
    assert "chinese_error_correction_review_gate" in by_title["shibing624/pycorrector"]["absorbed_patterns"]


def test_chinese_text_processing_pattern_pack_exposes_review_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-11T00:15:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/fxsjy/jieba",
                "title": "fxsjy/jieba",
                "summary": "Chinese segmentation and keyword extraction profile.",
                "stars": 33500,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["chinese_segmentation_keyword_gate"],
                "score": 94,
            },
            {
                "source": "github",
                "url": "https://github.com/hankcs/HanLP",
                "title": "hankcs/HanLP",
                "summary": "Chinese NER and alias consistency review.",
                "stars": 36500,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["chinese_ner_alias_consistency_gate"],
                "score": 93,
            },
            {
                "source": "github",
                "url": "https://github.com/BYVoid/OpenCC",
                "title": "BYVoid/OpenCC",
                "summary": "Chinese text normalization for Simplified and Traditional variants.",
                "stars": 9600,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["chinese_text_normalization_gate"],
                "score": 92,
            },
            {
                "source": "github",
                "url": "https://github.com/shibing624/pycorrector",
                "title": "shibing624/pycorrector",
                "summary": "Chinese correction review and confusion set exceptions.",
                "stars": 8400,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["chinese_error_correction_review_gate"],
                "score": 91,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "chinese_segmentation_dictionary" in pattern_pack["bible_enrichment_targets"]
    assert "chinese_entity_alias_ledger" in pattern_pack["bible_enrichment_targets"]
    assert "chinese_text_normalization_policy" in pattern_pack["bible_enrichment_targets"]
    assert "chinese_correction_review_queue" in pattern_pack["bible_enrichment_targets"]
    assert "chinese_segmentation_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chinese_entity_alias_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chinese_text_normalization_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chinese_error_correction_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chinese_segmentation_dictionary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chinese_entity_alias_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chinese_normalization_policy_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chinese_correction_exception_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "chinese_segmentation_keyword_gate_hints" in digest
    assert "chinese_ner_alias_consistency_gate_hints" in digest
    assert "chinese_text_normalization_gate_hints" in digest
    assert "chinese_error_correction_review_gate_hints" in digest


def test_default_discovery_sources_include_chinese_text_processing_projects():
    assert "https://github.com/fxsjy/jieba" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/messense/jieba-rs" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/hankcs/HanLP" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/HIT-SCIR/ltp" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/BYVoid/OpenCC" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/shibing624/pycorrector" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("chinese word segmentation" in query.lower() and "jieba" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("chinese ner" in query.lower() and "alias" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("opencc" in query.lower() and "simplified chinese" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    assert any("chinese spelling correction" in query.lower() and "pycorrector" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_source_import_ocr_sources_classify_into_import_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "aerkalov/ebooklib",
                "html_url": "https://github.com/aerkalov/ebooklib",
                "description": "EbookLib handles EPUB ebook reading and writing with OPF metadata, spine, table of contents, TOC and source import manifests.",
                "stargazers_count": 2300,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["epub", "ebook", "opf"],
                "updated_at": "2026-06-11T00:30:00Z",
                "root_files": ["README.md", "setup.py", "ebooklib"],
            },
            {
                "full_name": "pdfminer/pdfminer.six",
                "html_url": "https://github.com/pdfminer/pdfminer.six",
                "description": "Pdfminer.six performs PDF text extraction, layout analysis, page coordinates, reading order and text blocks for PDF pages.",
                "stargazers_count": 6700,
                "license": {"spdx_id": "MIT"},
                "topics": ["pdf", "text-extraction", "layout-analysis"],
                "updated_at": "2026-06-11T00:30:00Z",
                "root_files": ["README.md", "pyproject.toml", "pdfminer"],
            },
            {
                "full_name": "pymupdf/PyMuPDF",
                "html_url": "https://github.com/pymupdf/PyMuPDF",
                "description": "PyMuPDF exposes PDF page text blocks, coordinates, images, metadata and PDF text extraction layout surfaces.",
                "stargazers_count": 6000,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["pdf", "mupdf", "text-extraction"],
                "updated_at": "2026-06-11T00:30:00Z",
                "root_files": ["README.md", "pyproject.toml", "src"],
            },
            {
                "full_name": "ocrmypdf/OCRmyPDF",
                "html_url": "https://github.com/ocrmypdf/OCRmyPDF",
                "description": "OCRmyPDF adds OCR text layers to scanned PDF files with hOCR, Tesseract, OCR confidence review and scanned page import behavior.",
                "stargazers_count": 3300,
                "license": {"spdx_id": "MPL-2.0"},
                "topics": ["ocr", "pdf", "tesseract"],
                "updated_at": "2026-06-11T00:30:00Z",
                "root_files": ["README.md", "pyproject.toml", "src"],
            },
            {
                "full_name": "tesseract-ocr/tesseract",
                "html_url": "https://github.com/tesseract-ocr/tesseract",
                "description": "Tesseract is an OCR engine for image text recognition, scanned pages, OCR confidence and language models.",
                "stargazers_count": 69000,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["ocr", "tesseract", "image-text"],
                "updated_at": "2026-06-11T00:30:00Z",
                "root_files": ["README.md", "CMakeLists.txt", "src"],
            },
            {
                "full_name": "Unstructured-IO/unstructured",
                "html_url": "https://github.com/Unstructured-IO/unstructured",
                "description": "Unstructured partitions PDFs, EPUBs, DOCX and HTML into document elements with partition_pdf, partition_epub, title elements and chapter detection.",
                "stargazers_count": 12000,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["document-partition", "pdf", "epub"],
                "updated_at": "2026-06-11T00:30:00Z",
                "root_files": ["README.md", "pyproject.toml", "unstructured"],
            },
            {
                "full_name": "jgm/pandoc",
                "html_url": "https://github.com/jgm/pandoc",
                "description": "Pandoc converts document formats with metadata, table of contents, markdown, docx, epub and format conversion logs for source import provenance.",
                "stargazers_count": 39000,
                "license": {"spdx_id": "GPL-2.0-or-later"},
                "topics": ["pandoc", "document-conversion", "markdown"],
                "updated_at": "2026-06-11T00:30:00Z",
                "root_files": ["README.md", "pandoc.cabal", "src"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T00:35:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["aerkalov/ebooklib"]["family"] == "novel-automation"
    assert "source_format_import_manifest" in by_title["aerkalov/ebooklib"]["absorbed_patterns"]
    assert "import_provenance_checksum_gate" in by_title["jgm/pandoc"]["absorbed_patterns"]
    assert "pdf_layout_text_extraction_gate" in by_title["pdfminer/pdfminer.six"]["absorbed_patterns"]
    assert "pdf_layout_text_extraction_gate" in by_title["pymupdf/PyMuPDF"]["absorbed_patterns"]
    assert "ocr_scanned_page_import_gate" in by_title["ocrmypdf/OCRmyPDF"]["absorbed_patterns"]
    assert "ocr_scanned_page_import_gate" in by_title["tesseract-ocr/tesseract"]["absorbed_patterns"]
    assert "document_partition_chapter_detection_gate" in by_title["Unstructured-IO/unstructured"]["absorbed_patterns"]


def test_source_import_ocr_pattern_pack_exposes_import_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-11T00:40:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/aerkalov/ebooklib",
                "title": "aerkalov/ebooklib",
                "summary": "EPUB source import manifest with TOC, spine and metadata.",
                "stars": 2300,
                "license": "AGPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["source_format_import_manifest"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/pdfminer/pdfminer.six",
                "title": "pdfminer/pdfminer.six",
                "summary": "PDF layout text extraction with page spans and reading order.",
                "stars": 6700,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["pdf_layout_text_extraction_gate"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/ocrmypdf/OCRmyPDF",
                "title": "ocrmypdf/OCRmyPDF",
                "summary": "Scanned-page OCR confidence review before source deconstruction.",
                "stars": 3300,
                "license": "MPL-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["ocr_scanned_page_import_gate"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/Unstructured-IO/unstructured",
                "title": "Unstructured-IO/unstructured",
                "summary": "Document partition into typed elements and chapter headings.",
                "stars": 12000,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["document_partition_chapter_detection_gate"],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/jgm/pandoc",
                "title": "jgm/pandoc",
                "summary": "Format conversion provenance, parser settings and checksums.",
                "stars": 39000,
                "license": "GPL-2.0-or-later",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["import_provenance_checksum_gate"],
                "score": 80,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "source_import_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "pdf_page_span_map" in pattern_pack["bible_enrichment_targets"]
    assert "ocr_page_confidence_report" in pattern_pack["bible_enrichment_targets"]
    assert "document_element_partition_map" in pattern_pack["bible_enrichment_targets"]
    assert "source_file_checksum_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "source_import_manifest_report" in pattern_pack["whole_book_analysis_targets"]
    assert "pdf_layout_extraction_report" in pattern_pack["whole_book_analysis_targets"]
    assert "ocr_confidence_report" in pattern_pack["whole_book_analysis_targets"]
    assert "document_partition_report" in pattern_pack["whole_book_analysis_targets"]
    assert "import_checksum_report" in pattern_pack["whole_book_analysis_targets"]
    assert "source_import_structure_remap" in pattern_pack["inspired_mapping_targets"]
    assert "pdf_layout_evidence_remap" in pattern_pack["inspired_mapping_targets"]
    assert "ocr_uncertainty_review_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chapter_partition_structure_remap" in pattern_pack["inspired_mapping_targets"]
    assert "import_provenance_lineage_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "source_format_import_manifest_hints" in digest
    assert "pdf_layout_text_extraction_gate_hints" in digest
    assert "ocr_scanned_page_import_gate_hints" in digest
    assert "document_partition_chapter_detection_gate_hints" in digest
    assert "import_provenance_checksum_gate_hints" in digest


def test_default_discovery_sources_include_source_import_ocr_projects():
    assert "https://github.com/aerkalov/ebooklib" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/pdfminer/pdfminer.six" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/pymupdf/PyMuPDF" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ocrmypdf/OCRmyPDF" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/tesseract-ocr/tesseract" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Unstructured-IO/unstructured" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jgm/pandoc" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("epub" in query.lower() and "spine" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("pdf text extraction" in query.lower() and "layout analysis" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("ocr" in query.lower() and "tesseract" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("document partition" in query.lower() and "partition_pdf" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_narrative_event_emotion_sources_classify_into_graph_arc_and_network_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "dbamman/litbank",
                "html_url": "https://github.com/dbamman/litbank",
                "description": "Annotated dataset of 100 works of fiction with literary entities, literary event detection, and coreference in English literature.",
                "stargazers_count": 376,
                "license": None,
                "topics": ["litbank", "fiction", "literary-entities"],
                "updated_at": "2026-06-05T16:42:27Z",
                "root_files": ["README.md", "entities", "events", "coref"],
            },
            {
                "full_name": "eecrazy/ConstructingNEEG_IJCAI_2018",
                "html_url": "https://github.com/eecrazy/ConstructingNEEG_IJCAI_2018",
                "description": "Constructing Narrative Event Evolutionary Graph for Script Event Prediction with narrative event chains and event graph modeling.",
                "stargazers_count": 165,
                "license": None,
                "topics": ["narrative-event", "event-graph"],
                "updated_at": "2025-11-19T11:12:54Z",
                "root_files": ["README.md", "code", "data"],
            },
            {
                "full_name": "doug919/narrative_graph_emnlp2020",
                "html_url": "https://github.com/doug919/narrative_graph_emnlp2020",
                "description": "Weakly-supervised modeling of contextualized event embedding for discourse relations and narrative graph event relation modeling.",
                "stargazers_count": 6,
                "license": {"spdx_id": "MIT"},
                "topics": ["event-embedding", "discourse-relations"],
                "updated_at": "2022-10-06T06:40:45Z",
                "root_files": ["README.md", "requirements.txt"],
            },
            {
                "full_name": "mjockers/syuzhet",
                "html_url": "https://github.com/mjockers/syuzhet",
                "description": "An R package for the extraction of sentiment and sentiment-based plot arcs from text.",
                "stargazers_count": 350,
                "license": None,
                "topics": ["sentiment", "plot-arcs"],
                "updated_at": "2026-06-09T14:07:41Z",
                "root_files": ["README.md", "DESCRIPTION"],
            },
            {
                "full_name": "jon-chun/sentimentarcs_notebooks",
                "html_url": "https://github.com/jon-chun/sentimentarcs_notebooks",
                "description": "SentimentArcs is a large ensemble of sentiment analysis models to analyze emotion in text over time.",
                "stargazers_count": 43,
                "license": {"spdx_id": "MIT"},
                "topics": ["sentiment-arcs", "emotion"],
                "updated_at": "2026-04-07T10:17:09Z",
                "root_files": ["README.md", "notebooks"],
            },
            {
                "full_name": "SapienzaNLP/xcore",
                "html_url": "https://github.com/SapienzaNLP/xcore",
                "description": "xCoRe is an all-in-one model for cross-context coreference resolution across short, long and multiple contexts.",
                "stargazers_count": 11,
                "license": None,
                "topics": ["coreference", "cross-context"],
                "updated_at": "2026-04-02T11:34:03Z",
                "root_files": ["README.md", "requirements.txt"],
            },
            {
                "full_name": "anastasia-zhukova/XCoref",
                "html_url": "https://github.com/anastasia-zhukova/XCoref",
                "description": "XCoref is a cross-document coreference resolution system for entity, event, and abstract concepts.",
                "stargazers_count": 3,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["coreference", "cross-document"],
                "updated_at": "2026-03-05T17:41:07Z",
                "root_files": ["README.md", "setup.py"],
            },
            {
                "full_name": "hzjken/character-network",
                "html_url": "https://github.com/hzjken/character-network",
                "description": "Using network graph, NLP entity recognition and sentiment analysis to analyse relationships among characters in a novel.",
                "stargazers_count": 62,
                "license": None,
                "topics": ["character-network", "novel"],
                "updated_at": "2026-05-13T02:10:18Z",
                "root_files": ["README.md", "notebooks"],
            },
            {
                "full_name": "devbret/character-interactions",
                "html_url": "https://github.com/devbret/character-interactions",
                "description": "Extract characters, infer relationships using linguistic signals and visualize literary character interactions as a network graph.",
                "stargazers_count": 4,
                "license": {"spdx_id": "MIT"},
                "topics": ["character-interactions", "literary-network"],
                "updated_at": "2026-05-09T05:18:09Z",
                "root_files": ["README.md", "package.json"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T01:30:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["dbamman/litbank"]["family"] == "novel-automation"
    assert "literary_event_entity_annotation_gate" in by_title["dbamman/litbank"]["absorbed_patterns"]
    assert "narrative_event_evolution_graph_gate" in by_title["eecrazy/ConstructingNEEG_IJCAI_2018"]["absorbed_patterns"]
    assert "narrative_event_evolution_graph_gate" in by_title["doug919/narrative_graph_emnlp2020"]["absorbed_patterns"]
    assert "sentiment_arc_emotion_trajectory_gate" in by_title["mjockers/syuzhet"]["absorbed_patterns"]
    assert "sentiment_arc_emotion_trajectory_gate" in by_title["jon-chun/sentimentarcs_notebooks"]["absorbed_patterns"]
    assert "cross_context_coreference_gate" in by_title["SapienzaNLP/xcore"]["absorbed_patterns"]
    assert "cross_context_coreference_gate" in by_title["anastasia-zhukova/XCoref"]["absorbed_patterns"]
    assert "character_interaction_network_gate" in by_title["hzjken/character-network"]["absorbed_patterns"]
    assert "character_interaction_network_gate" in by_title["devbret/character-interactions"]["absorbed_patterns"]


def test_narrative_event_emotion_pattern_pack_exposes_graph_arc_and_network_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-11T01:35:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/dbamman/litbank",
                "title": "dbamman/litbank",
                "summary": "Literary entity and event annotation for source-book deconstruction.",
                "stars": 376,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["literary_event_entity_annotation_gate"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/eecrazy/ConstructingNEEG_IJCAI_2018",
                "title": "eecrazy/ConstructingNEEG_IJCAI_2018",
                "summary": "Narrative event evolutionary graph and event-chain review.",
                "stars": 165,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["narrative_event_evolution_graph_gate"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/mjockers/syuzhet",
                "title": "mjockers/syuzhet",
                "summary": "Sentiment-based plot arcs and emotion trajectories.",
                "stars": 350,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["sentiment_arc_emotion_trajectory_gate"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/SapienzaNLP/xcore",
                "title": "SapienzaNLP/xcore",
                "summary": "Cross-context coreference and mention cluster stability.",
                "stars": 11,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["cross_context_coreference_gate"],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/hzjken/character-network",
                "title": "hzjken/character-network",
                "summary": "Character interaction network and relationship polarity review.",
                "stars": 62,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["character_interaction_network_gate"],
                "score": 80,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "literary_entity_event_annotation_schema" in pattern_pack["bible_enrichment_targets"]
    assert "narrative_event_chain_graph" in pattern_pack["bible_enrichment_targets"]
    assert "sentiment_arc_baseline" in pattern_pack["bible_enrichment_targets"]
    assert "cross_context_coreference_ledger" in pattern_pack["bible_enrichment_targets"]
    assert "character_interaction_network" in pattern_pack["bible_enrichment_targets"]
    assert "literary_entity_event_annotation_report" in pattern_pack["whole_book_analysis_targets"]
    assert "narrative_event_chain_report" in pattern_pack["whole_book_analysis_targets"]
    assert "sentiment_arc_emotion_report" in pattern_pack["whole_book_analysis_targets"]
    assert "cross_context_coreference_report" in pattern_pack["whole_book_analysis_targets"]
    assert "character_interaction_network_report" in pattern_pack["whole_book_analysis_targets"]
    assert "literary_annotation_role_remap" in pattern_pack["inspired_mapping_targets"]
    assert "event_chain_causality_remap" in pattern_pack["inspired_mapping_targets"]
    assert "sentiment_arc_emotion_remap" in pattern_pack["inspired_mapping_targets"]
    assert "cross_context_coreference_remap" in pattern_pack["inspired_mapping_targets"]
    assert "character_network_relationship_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "literary_event_entity_annotation_gate_hints" in digest
    assert "narrative_event_evolution_graph_gate_hints" in digest
    assert "sentiment_arc_emotion_trajectory_gate_hints" in digest
    assert "cross_context_coreference_gate_hints" in digest
    assert "character_interaction_network_gate_hints" in digest


def test_default_discovery_sources_include_narrative_event_emotion_projects():
    assert "https://github.com/dbamman/litbank" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/eecrazy/ConstructingNEEG_IJCAI_2018" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/acolas1/EventNarrative" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/doug919/narrative_graph_emnlp2020" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/mjockers/syuzhet" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jon-chun/sentimentarcs_notebooks" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/SapienzaNLP/xcore" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/anastasia-zhukova/XCoref" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/hzjken/character-network" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/devbret/character-interactions" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("litbank" in query.lower() and "literary event detection" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("narrative event evolutionary graph" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("sentiment arcs" in query.lower() and "emotion in text over time" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("cross-context coreference" in query.lower() and "xcoref" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("character network" in query.lower() and "character interactions" in query.lower() for query in DEFAULT_GITHUB_QUERIES)



def test_stylometry_style_overfit_sources_classify_into_author_similarity_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "computationalstylistics/stylo",
                "html_url": "https://github.com/computationalstylistics/stylo",
                "description": "R package for computational stylistics, stylometric analyses, and authorship attribution.",
                "stargazers_count": 624,
                "license": None,
                "topics": ["stylometry", "authorship-attribution", "computational-stylistics"],
                "updated_at": "2026-05-29T12:00:00Z",
                "root_files": ["README.md", "DESCRIPTION"],
            },
            {
                "full_name": "fastdatascience/faststylometry",
                "html_url": "https://github.com/fastdatascience/faststylometry",
                "description": "Fast Stylometry Python library with Burrows Delta and style similarity for authorship attribution.",
                "stargazers_count": 65,
                "license": {"spdx_id": "MIT"},
                "topics": ["stylometry", "burrows-delta"],
                "updated_at": "2026-03-11T09:00:00Z",
                "root_files": ["README.md", "pyproject.toml"],
            },
            {
                "full_name": "Hassaan-Elahi/Writing-Styles-Classification-Using-Stylometric-Analysis",
                "html_url": "https://github.com/Hassaan-Elahi/Writing-Styles-Classification-Using-Stylometric-Analysis",
                "description": "Classifies different writing styles in a document with sentence length, readability scores, vocabulary richness and frequencies.",
                "stargazers_count": 115,
                "license": {"spdx_id": "MIT"},
                "topics": ["style-change", "stylometry"],
                "updated_at": "2025-12-02T09:00:00Z",
                "root_files": ["README.md", "notebooks"],
            },
            {
                "full_name": "pan-webis-de/pan-code",
                "html_url": "https://github.com/pan-webis-de/pan-code",
                "description": "Code used for evaluation and baselines in PAN shared tasks including authorship attribution and style change detection.",
                "stargazers_count": 200,
                "license": {"spdx_id": "MIT"},
                "topics": ["pan", "authorship-attribution", "style-change-detection"],
                "updated_at": "2026-01-17T09:00:00Z",
                "root_files": ["README.md", "LICENSE"],
            },
            {
                "full_name": "ngpepin/stylometric-transfer",
                "html_url": "https://github.com/ngpepin/stylometric-transfer",
                "description": "Stylometric profiling plus controllable author-style transfer using explicit JSON style fingerprints, similarity methods and style constraints.",
                "stargazers_count": 18,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["stylometric-transfer", "style-fingerprint"],
                "updated_at": "2026-06-03T09:00:00Z",
                "root_files": ["README.md", "prompts.json", "fingerprint_api.py"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T12:00:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["computationalstylistics/stylo"]["family"] == "novel-automation"
    assert "stylometric_author_fingerprint_gate" in by_title["computationalstylistics/stylo"]["absorbed_patterns"]
    assert "authorship_attribution_similarity_gate" in by_title["fastdatascience/faststylometry"]["absorbed_patterns"]
    assert "function_word_syntax_style_gate" in by_title["Hassaan-Elahi/Writing-Styles-Classification-Using-Stylometric-Analysis"]["absorbed_patterns"]
    assert "style_overfit_regression_gate" in by_title["pan-webis-de/pan-code"]["absorbed_patterns"]
    assert "paraphrase_independence_review_gate" in by_title["ngpepin/stylometric-transfer"]["absorbed_patterns"]


def test_stylometry_style_overfit_pattern_pack_exposes_author_similarity_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T12:10:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/computationalstylistics/stylo",
                "title": "computationalstylistics/stylo",
                "summary": "Computational stylistics and authorship attribution for explicit style fingerprints.",
                "stars": 624,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["stylometric_author_fingerprint_gate"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/mullerpeter/authorstyle",
                "title": "mullerpeter/authorstyle",
                "summary": "PAN corpora and stylometric features such as function-word and syntax style ledgers.",
                "stars": 20,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["function_word_syntax_style_gate"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/fastdatascience/faststylometry",
                "title": "fastdatascience/faststylometry",
                "summary": "Burrows Delta and style similarity for authorship attribution distance checks.",
                "stars": 65,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["authorship_attribution_similarity_gate"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/ivannikov-lab/style-change-analysis",
                "title": "ivannikov-lab/style-change-analysis",
                "summary": "Style change detection and style breach windows for style-overfit regression.",
                "stars": 6,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["style_overfit_regression_gate"],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/ngpepin/stylometric-transfer",
                "title": "ngpepin/stylometric-transfer",
                "summary": "Author-style transfer with style fingerprint and similarity methods requires paraphrase independence review.",
                "stars": 18,
                "license": "PolyForm-Noncommercial-1.0.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["prompt_model_provider"],
                "absorbed_patterns": ["paraphrase_independence_review_gate"],
                "score": 80,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "stylometric_author_fingerprint_baseline" in pattern_pack["bible_enrichment_targets"]
    assert "function_word_syntax_style_baseline" in pattern_pack["bible_enrichment_targets"]
    assert "authorship_similarity_thresholds" in pattern_pack["bible_enrichment_targets"]
    assert "style_overfit_regression_cases" in pattern_pack["bible_enrichment_targets"]
    assert "paraphrase_independence_review_policy" in pattern_pack["bible_enrichment_targets"]
    assert "stylometric_author_fingerprint_report" in pattern_pack["whole_book_analysis_targets"]
    assert "function_word_syntax_report" in pattern_pack["whole_book_analysis_targets"]
    assert "authorship_similarity_report" in pattern_pack["whole_book_analysis_targets"]
    assert "style_overfit_regression_report" in pattern_pack["whole_book_analysis_targets"]
    assert "paraphrase_independence_report" in pattern_pack["whole_book_analysis_targets"]
    assert "stylometric_fingerprint_remap" in pattern_pack["inspired_mapping_targets"]
    assert "function_word_syntax_remap" in pattern_pack["inspired_mapping_targets"]
    assert "authorship_similarity_threshold_remap" in pattern_pack["inspired_mapping_targets"]
    assert "style_overfit_regression_remap" in pattern_pack["inspired_mapping_targets"]
    assert "paraphrase_independence_policy_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "stylometric_author_fingerprint_gate_hints" in digest
    assert "function_word_syntax_style_gate_hints" in digest
    assert "authorship_attribution_similarity_gate_hints" in digest
    assert "style_overfit_regression_gate_hints" in digest
    assert "paraphrase_independence_review_gate_hints" in digest


def test_default_discovery_sources_include_stylometry_style_overfit_projects():
    assert "https://github.com/computationalstylistics/stylo" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/fastdatascience/faststylometry" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Hassaan-Elahi/Writing-Styles-Classification-Using-Stylometric-Analysis" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/michaeleby1/stylometric-analysis-project-gutenberg" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/pan-webis-de/pan-code" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/mullerpeter/authorstyle" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ivannikov-lab/style-change-analysis" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/sam0jones0/pyantistylometry" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ngpepin/stylometric-transfer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ContextLab/llm-stylometry" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/llm-authorship/survey" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("stylometry" in query.lower() and "authorship attribution" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("function words" in query.lower() and "stylometry" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("style change detection" in query.lower() and "pan" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("stylometric transfer" in query.lower() and "style fingerprint" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("anti-stylometry" in query.lower() and "paraphrase independence" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_dedup_similarity_sources_classify_into_independence_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "ChenghaoMou/text-dedup",
                "html_url": "https://github.com/ChenghaoMou/text-dedup",
                "description": "All-in-one text de-duplication with exact, MinHash, SimHash, and semantic deduplication.",
                "stargazers_count": 759,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["text-dedup", "minhash", "simhash"],
                "updated_at": "2026-06-09T12:52:49Z",
                "root_files": ["README.md", "pyproject.toml"],
            },
            {
                "full_name": "ekzhu/datasketch",
                "html_url": "https://github.com/ekzhu/datasketch",
                "description": "MinHash, LSH, LSH Forest and Weighted MinHash for estimating Jaccard similarity.",
                "stargazers_count": 2928,
                "license": {"spdx_id": "MIT"},
                "topics": ["minhash", "lsh", "jaccard"],
                "updated_at": "2026-06-07T05:39:08Z",
                "root_files": ["README.rst", "setup.py"],
            },
            {
                "full_name": "seomoz/simhash-py",
                "html_url": "https://github.com/seomoz/simhash-py",
                "description": "Simhash and near-duplicate detection with Hamming distance over similar hashes.",
                "stargazers_count": 422,
                "license": {"spdx_id": "MIT"},
                "topics": ["simhash", "near-duplicate"],
                "updated_at": "2026-06-09T06:16:20Z",
                "root_files": ["README.md", "setup.py"],
            },
            {
                "full_name": "MinishLab/semhash",
                "html_url": "https://github.com/MinishLab/semhash",
                "description": "Fast multimodal semantic deduplication and filtering for semantic duplicates.",
                "stargazers_count": 936,
                "license": {"spdx_id": "MIT"},
                "topics": ["semantic-deduplication", "filtering"],
                "updated_at": "2026-06-08T09:48:32Z",
                "root_files": ["README.md", "pyproject.toml"],
            },
            {
                "full_name": "facebookresearch/faiss",
                "html_url": "https://github.com/facebookresearch/faiss",
                "description": "Efficient similarity search and clustering of dense vectors for nearest neighbor retrieval.",
                "stargazers_count": 40240,
                "license": {"spdx_id": "MIT"},
                "topics": ["similarity-search", "dense-vectors"],
                "updated_at": "2026-06-09T22:45:04Z",
                "root_files": ["README.md", "CMakeLists.txt"],
            },
            {
                "full_name": "google-research/deduplicate-text-datasets",
                "html_url": "https://github.com/google-research/deduplicate-text-datasets",
                "description": "Deduplicating training data with ExactSubstr and NearDup to remove repeated sequences from language model datasets.",
                "stargazers_count": 1273,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["deduplication", "datasets"],
                "updated_at": "2026-05-26T07:58:09Z",
                "root_files": ["README.md", "Cargo.toml"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T13:00:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["ChenghaoMou/text-dedup"]["family"] == "novel-automation"
    assert "minhash_lsh_near_duplicate_gate" in by_title["ChenghaoMou/text-dedup"]["absorbed_patterns"]
    assert "simhash_hamming_similarity_gate" in by_title["ChenghaoMou/text-dedup"]["absorbed_patterns"]
    assert "semantic_duplicate_cluster_gate" in by_title["ChenghaoMou/text-dedup"]["absorbed_patterns"]
    assert "minhash_lsh_near_duplicate_gate" in by_title["ekzhu/datasketch"]["absorbed_patterns"]
    assert "simhash_hamming_similarity_gate" in by_title["seomoz/simhash-py"]["absorbed_patterns"]
    assert "semantic_duplicate_cluster_gate" in by_title["MinishLab/semhash"]["absorbed_patterns"]
    assert "embedding_similarity_independence_gate" in by_title["facebookresearch/faiss"]["absorbed_patterns"]
    assert "corpus_leakage_dedup_review_gate" in by_title["google-research/deduplicate-text-datasets"]["absorbed_patterns"]


def test_dedup_similarity_pattern_pack_exposes_independence_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T13:10:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/ekzhu/datasketch",
                "title": "ekzhu/datasketch",
                "summary": "MinHash LSH and Jaccard similarity for near duplicate text windows.",
                "stars": 2928,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["minhash_lsh_near_duplicate_gate"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/seomoz/simhash-py",
                "title": "seomoz/simhash-py",
                "summary": "SimHash Hamming distance for near duplicate documents.",
                "stars": 422,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["native_binary"],
                "absorbed_patterns": ["simhash_hamming_similarity_gate"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/MinishLab/semhash",
                "title": "MinishLab/semhash",
                "summary": "Semantic deduplication and filtering for semantic duplicates.",
                "stars": 936,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["semantic_duplicate_cluster_gate"],
                "score": 87,
            },
            {
                "source": "github",
                "url": "https://github.com/facebookresearch/faiss",
                "title": "facebookresearch/faiss",
                "summary": "Similarity search and clustering of dense vectors for nearest neighbor source checks.",
                "stars": 40240,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["native_binary"],
                "absorbed_patterns": ["embedding_similarity_independence_gate"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/google-research/deduplicate-text-datasets",
                "title": "google-research/deduplicate-text-datasets",
                "summary": "ExactSubstr and NearDup dataset deduplication for corpus leakage review.",
                "stars": 1273,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["native_binary"],
                "absorbed_patterns": ["corpus_leakage_dedup_review_gate"],
                "score": 85,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "minhash_lsh_thresholds" in pattern_pack["bible_enrichment_targets"]
    assert "simhash_hamming_thresholds" in pattern_pack["bible_enrichment_targets"]
    assert "semantic_duplicate_cluster_thresholds" in pattern_pack["bible_enrichment_targets"]
    assert "embedding_similarity_independence_thresholds" in pattern_pack["bible_enrichment_targets"]
    assert "corpus_leakage_review_policy" in pattern_pack["bible_enrichment_targets"]
    assert "minhash_lsh_overlap_report" in pattern_pack["whole_book_analysis_targets"]
    assert "simhash_hamming_report" in pattern_pack["whole_book_analysis_targets"]
    assert "semantic_duplicate_cluster_report" in pattern_pack["whole_book_analysis_targets"]
    assert "embedding_similarity_independence_report" in pattern_pack["whole_book_analysis_targets"]
    assert "corpus_leakage_dedup_report" in pattern_pack["whole_book_analysis_targets"]
    assert "minhash_lsh_threshold_remap" in pattern_pack["inspired_mapping_targets"]
    assert "simhash_hamming_threshold_remap" in pattern_pack["inspired_mapping_targets"]
    assert "semantic_cluster_independence_remap" in pattern_pack["inspired_mapping_targets"]
    assert "embedding_neighbor_independence_remap" in pattern_pack["inspired_mapping_targets"]
    assert "corpus_leakage_boundary_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "minhash_lsh_near_duplicate_gate_hints" in digest
    assert "simhash_hamming_similarity_gate_hints" in digest
    assert "semantic_duplicate_cluster_gate_hints" in digest
    assert "embedding_similarity_independence_gate_hints" in digest
    assert "corpus_leakage_dedup_review_gate_hints" in digest


def test_default_discovery_sources_include_dedup_similarity_projects():
    assert "https://github.com/ChenghaoMou/text-dedup" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/google-research/deduplicate-text-datasets" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ekzhu/datasketch" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/seomoz/simhash-py" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/1e0ng/simhash" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/MinishLab/semhash" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/UKPLab/sentence-transformers" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/facebookresearch/faiss" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/facebookresearch/SemDeDup" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("minhash" in query.lower() and "jaccard" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("simhash" in query.lower() and "hamming distance" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("semantic deduplication" in query.lower() and "faiss" in query.lower() for query in DEFAULT_GITHUB_QUERIES)



def test_trope_sources_classify_into_same_type_independence_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "MitchSaltykov/TVTropes-correlation",
                "html_url": "https://github.com/MitchSaltykov/TVTropes-correlation",
                "description": "Look at two works and determine how similar they are in terms of the tropes they use.",
                "stargazers_count": 10,
                "license": None,
                "topics": ["tvtropes", "similarity"],
                "updated_at": "2026-06-09T00:00:00Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "jwzimmer-zz/tv-tropes",
                "html_url": "https://github.com/jwzimmer-zz/tv-tropes",
                "description": "Network of tropes from TV Tropes wiki for trope graph co-occurrence.",
                "stargazers_count": 5,
                "license": {"spdx_id": "MIT"},
                "topics": ["tvtropes", "network"],
                "updated_at": "2026-06-09T00:00:00Z",
                "root_files": ["README.md", "LICENSE"],
            },
            {
                "full_name": "slowwavesleep/TvTropesMovieData",
                "html_url": "https://github.com/slowwavesleep/TvTropesMovieData",
                "description": "Movies and their tropes dataset for trope inventory and trope density review.",
                "stargazers_count": 5,
                "license": {"spdx_id": "CC-BY-SA-4.0"},
                "topics": ["movie-tropes", "dataset"],
                "updated_at": "2026-06-09T00:00:00Z",
                "root_files": ["README.md", "LICENSE"],
            },
            {
                "full_name": "rhgarcia/tropescraper",
                "html_url": "https://github.com/rhgarcia/tropescraper",
                "description": "A tropes scraper for TV Tropes metadata.",
                "stargazers_count": 34,
                "license": {"spdx_id": "LGPL-3.0"},
                "topics": ["tvtropes", "scraper"],
                "updated_at": "2026-06-09T00:00:00Z",
                "root_files": ["README.md", "setup.py"],
            },
            {
                "full_name": "Sirver51/tvtropes-parser",
                "html_url": "https://github.com/Sirver51/tvtropes-parser",
                "description": "Parses a TV Tropes page into sections. Not intended for mass scraping.",
                "stargazers_count": 2,
                "license": None,
                "topics": ["tvtropes", "parser"],
                "updated_at": "2026-06-09T00:00:00Z",
                "root_files": ["README.md", "build.gradle.kts"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T16:00:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["MitchSaltykov/TVTropes-correlation"]["family"] == "novel-automation"
    assert "trope_inventory_similarity_gate" in by_title["MitchSaltykov/TVTropes-correlation"]["absorbed_patterns"]
    assert "trope_graph_expectation_map" in by_title["jwzimmer-zz/tv-tropes"]["absorbed_patterns"]
    assert "trope_density_novelty_budget" in by_title["slowwavesleep/TvTropesMovieData"]["absorbed_patterns"]
    assert "trope_source_boundary_review" in by_title["rhgarcia/tropescraper"]["absorbed_patterns"]
    assert "network_scraper" in by_title["rhgarcia/tropescraper"]["risk_flags"]
    assert "trope_source_boundary_review" in by_title["Sirver51/tvtropes-parser"]["absorbed_patterns"]


def test_trope_pattern_pack_exposes_independence_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T16:10:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/MitchSaltykov/TVTropes-correlation",
                "title": "MitchSaltykov/TVTropes-correlation",
                "summary": "Compare two works by trope overlap.",
                "stars": 10,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["trope_inventory_similarity_gate"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/jwzimmer-zz/tv-tropes",
                "title": "jwzimmer-zz/tv-tropes",
                "summary": "Trope graph and network of tropes.",
                "stars": 5,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["trope_graph_expectation_map"],
                "score": 87,
            },
            {
                "source": "github",
                "url": "https://github.com/slowwavesleep/TvTropesMovieData",
                "title": "slowwavesleep/TvTropesMovieData",
                "summary": "Movie trope dataset for density review.",
                "stars": 5,
                "license": "CC-BY-SA-4.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["trope_density_novelty_budget"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/rhgarcia/tropescraper",
                "title": "rhgarcia/tropescraper",
                "summary": "Trope scraper for source boundary review.",
                "stars": 34,
                "license": "LGPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["network_scraper"],
                "absorbed_patterns": ["trope_source_boundary_review"],
                "score": 85,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "trope_inventory_baseline" in pattern_pack["bible_enrichment_targets"]
    assert "trope_graph_expectation_map" in pattern_pack["bible_enrichment_targets"]
    assert "trope_density_novelty_budget" in pattern_pack["bible_enrichment_targets"]
    assert "trope_source_boundary_policy" in pattern_pack["bible_enrichment_targets"]
    assert "trope_similarity_report" in pattern_pack["whole_book_analysis_targets"]
    assert "trope_density_report" in pattern_pack["whole_book_analysis_targets"]
    assert "trope_inventory_similarity_gate_hints" in pattern_pack
    assert "trope_graph_expectation_map_hints" in pattern_pack
    assert "trope_density_novelty_budget_hints" in pattern_pack
    assert "trope_source_boundary_review_hints" in pattern_pack

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "trope_inventory_similarity_gate_hints" in digest
    assert "trope_source_boundary_review_hints" in digest
    assert "trope_source_boundary_review" in [pattern["name"] for pattern in pattern_pack["workflow_patterns"]]


def test_default_discovery_sources_include_trope_independence_projects():
    assert "https://github.com/MitchSaltykov/TVTropes-correlation" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jwzimmer-zz/tv-tropes" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/slowwavesleep/TvTropesMovieData" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/rhgarcia/tropescraper" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Sirver51/tvtropes-parser" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("tvtropes" in query.lower() and "trope correlation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("trope graph" in query.lower() and "trope similarity" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_source_rights_projects_classify_into_admission_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "licensee/licensee",
                "html_url": "https://github.com/licensee/licensee",
                "description": "License detection and license matcher for repository license metadata.",
                "stargazers_count": 4000,
                "forks_count": 400,
                "open_issues_count": 120,
                "license": {"spdx_id": "MIT"},
                "topics": ["licensee", "license-detection"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "LICENSE.md"],
            },
            {
                "full_name": "fsfe/reuse-tool",
                "html_url": "https://github.com/fsfe/reuse-tool",
                "description": "REUSE compliance tool with SPDX-License-Identifier and SPDX FileCopyrightText recommendations.",
                "stargazers_count": 1600,
                "forks_count": 200,
                "open_issues_count": 80,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["reuse", "spdx"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "pyproject.toml", "LICENSES"],
            },
            {
                "full_name": "spdx/license-list-data",
                "html_url": "https://github.com/spdx/license-list-data",
                "description": "SPDX License List Data for license terms, copyright, attribution, and generated license metadata.",
                "stargazers_count": 700,
                "license": None,
                "topics": ["spdx", "license-list"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "json", "templates"],
            },
            {
                "full_name": "c-w/Gutenberg",
                "html_url": "https://github.com/c-w/Gutenberg",
                "description": "Project Gutenberg metadata and body of public domain texts for book corpus cleaning.",
                "stargazers_count": 1400,
                "forks_count": 180,
                "open_issues_count": 20,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["gutenberg", "public-domain", "books"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "LICENSE.txt"],
            },
            {
                "full_name": "Imkun-on/gutenberg-corpus-cli",
                "html_url": "https://github.com/Imkun-on/gutenberg-corpus-cli",
                "description": "Build public-domain book corpora from Project Gutenberg metadata with download texts, parallel downloads, SQLite catalog, and full-text search.",
                "stargazers_count": 4,
                "license": {"spdx_id": "MIT"},
                "topics": ["gutenberg", "corpus"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "pyproject.toml"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T17:10:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert by_title["licensee/licensee"]["family"] == "novel-automation"
    assert "source_license_detection_gate" in by_title["licensee/licensee"]["absorbed_patterns"]
    assert "spdx_reuse_compliance_gate" in by_title["fsfe/reuse-tool"]["absorbed_patterns"]
    assert "spdx_reuse_compliance_gate" in by_title["spdx/license-list-data"]["absorbed_patterns"]
    assert "attribution_derivative_work_gate" in by_title["spdx/license-list-data"]["absorbed_patterns"]
    assert "public_domain_corpus_boundary" in by_title["c-w/Gutenberg"]["absorbed_patterns"]
    assert "public_domain_corpus_boundary" in by_title["Imkun-on/gutenberg-corpus-cli"]["absorbed_patterns"]
    assert "corpus_downloader" in by_title["Imkun-on/gutenberg-corpus-cli"]["risk_flags"]


def test_source_rights_pattern_pack_exposes_provenance_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T17:20:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/licensee/licensee",
                "title": "licensee/licensee",
                "summary": "License detection for repository source admission.",
                "stars": 4000,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["source_license_detection_gate"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/fsfe/reuse-tool",
                "title": "fsfe/reuse-tool",
                "summary": "SPDX and REUSE metadata compliance for source provenance.",
                "stars": 1600,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["spdx_reuse_compliance_gate"],
                "score": 89,
            },
            {
                "source": "github",
                "url": "https://github.com/c-w/Gutenberg",
                "title": "c-w/Gutenberg",
                "summary": "Project Gutenberg public-domain corpus metadata boundary.",
                "stars": 1400,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["public_domain_corpus_boundary"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/spdx/license-list-data",
                "title": "spdx/license-list-data",
                "summary": "License terms and attribution metadata for derivative-use review.",
                "stars": 700,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["attribution_derivative_work_gate"],
                "score": 87,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "source_license_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "spdx_reuse_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "public_domain_source_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "attribution_derivative_policy" in pattern_pack["bible_enrichment_targets"]
    assert "source_license_review_report" in pattern_pack["whole_book_analysis_targets"]
    assert "spdx_reuse_compliance_report" in pattern_pack["whole_book_analysis_targets"]
    assert "public_domain_source_report" in pattern_pack["whole_book_analysis_targets"]
    assert "attribution_derivative_review" in pattern_pack["whole_book_analysis_targets"]
    assert pattern_pack["source_license_detection_gate_hints"]
    assert pattern_pack["spdx_reuse_compliance_gate_hints"]
    assert pattern_pack["public_domain_corpus_boundary_hints"]
    assert pattern_pack["attribution_derivative_work_gate_hints"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "source_license_detection_gate_hints" in digest
    assert "spdx_reuse_compliance_gate_hints" in digest
    assert "public_domain_corpus_boundary_hints" in digest
    assert "attribution_derivative_work_gate_hints" in digest


def test_default_discovery_sources_include_source_rights_projects():
    assert "https://github.com/licensee/licensee" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/fsfe/reuse-tool" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/spdx/license-list-data" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/c-w/Gutenberg" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Imkun-on/gutenberg-corpus-cli" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("license detection" in query.lower() and "spdx" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("project gutenberg" in query.lower() and "public domain" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_entity_redaction_projects_classify_into_leakage_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "microsoft/presidio",
                "html_url": "https://github.com/microsoft/presidio",
                "description": "Framework for detecting, redacting, masking, and anonymizing sensitive data across text with NLP, pattern matching, and customizable pipelines.",
                "stargazers_count": 8527,
                "forks_count": 1000,
                "open_issues_count": 200,
                "license": {"spdx_id": "MIT"},
                "topics": ["pii", "redaction", "anonymization", "nlp"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.MD", "LICENSE", "docker-compose.yml", "presidio-analyzer", "presidio-anonymizer"],
            },
            {
                "full_name": "LeapBeyond/scrubadub",
                "html_url": "https://github.com/LeapBeyond/scrubadub",
                "description": "Clean personally identifiable information from text with detectors, postprocessors, replacers, and anonymous IDs.",
                "stargazers_count": 425,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["pii", "anonymization"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.rst", "LICENSE", "setup.py"],
            },
            {
                "full_name": "urchade/GLiNER",
                "html_url": "https://github.com/urchade/GLiNER",
                "description": "Generalist and Lightweight Model for Named Entity Recognition. Extract any entity types from texts.",
                "stargazers_count": 3264,
                "forks_count": 300,
                "open_issues_count": 50,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["named-entity-recognition", "ner"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "gliner"],
            },
            {
                "full_name": "flairNLP/flair",
                "html_url": "https://github.com/flairNLP/flair",
                "description": "NLP framework with named entity recognition and NER models across languages.",
                "stargazers_count": 14376,
                "forks_count": 1500,
                "open_issues_count": 300,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["nlp", "ner"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "flair"],
            },
            {
                "full_name": "explosion/spaCy",
                "html_url": "https://github.com/explosion/spaCy",
                "description": "Industrial-strength NLP in Python with pretrained pipelines, named entity recognition, text classification, and custom pipeline components.",
                "stargazers_count": 33643,
                "forks_count": 5000,
                "open_issues_count": 400,
                "license": {"spdx_id": "MIT"},
                "topics": ["nlp", "ner", "pipeline"],
                "updated_at": "2026-06-10T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "pyproject.toml"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T18:10:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "source_entity_redaction_gate" in by_title["microsoft/presidio"]["absorbed_patterns"]
    assert "placeholder_alias_consistency_map" in by_title["microsoft/presidio"]["absorbed_patterns"]
    assert "docker" in by_title["microsoft/presidio"]["risk_flags"]
    assert "source_entity_redaction_gate" in by_title["LeapBeyond/scrubadub"]["absorbed_patterns"]
    assert "placeholder_alias_consistency_map" in by_title["LeapBeyond/scrubadub"]["absorbed_patterns"]
    assert "custom_entity_label_inventory" in by_title["urchade/GLiNER"]["absorbed_patterns"]
    assert "proper_noun_leakage_review" in by_title["urchade/GLiNER"]["absorbed_patterns"]
    assert "custom_entity_label_inventory" in by_title["flairNLP/flair"]["absorbed_patterns"]
    assert "custom_entity_label_inventory" in by_title["explosion/spaCy"]["absorbed_patterns"]


def test_entity_redaction_pattern_pack_exposes_leakage_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T18:20:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/microsoft/presidio",
                "title": "microsoft/presidio",
                "summary": "Detect and redact source-specific entities before drafting.",
                "stars": 8527,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker"],
                "absorbed_patterns": ["source_entity_redaction_gate"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/urchade/GLiNER",
                "title": "urchade/GLiNER",
                "summary": "Custom fiction entity labels for source inventories.",
                "stars": 3264,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["custom_entity_label_inventory"],
                "score": 89,
            },
            {
                "source": "github",
                "url": "https://github.com/LeapBeyond/scrubadub",
                "title": "LeapBeyond/scrubadub",
                "summary": "Placeholder and anonymous id consistency for redacted source text.",
                "stars": 425,
                "license": "Apache-2.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["placeholder_alias_consistency_map"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/explosion/spaCy",
                "title": "explosion/spaCy",
                "summary": "Proper noun and entity leakage review for fiction drafts.",
                "stars": 33643,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["proper_noun_leakage_review"],
                "score": 87,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "source_entity_redaction_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "custom_fiction_entity_label_set" in pattern_pack["bible_enrichment_targets"]
    assert "placeholder_alias_map" in pattern_pack["bible_enrichment_targets"]
    assert "proper_noun_blocklist" in pattern_pack["bible_enrichment_targets"]
    assert "source_entity_redaction_report" in pattern_pack["whole_book_analysis_targets"]
    assert "custom_entity_label_inventory" in pattern_pack["whole_book_analysis_targets"]
    assert "placeholder_alias_consistency_report" in pattern_pack["whole_book_analysis_targets"]
    assert "proper_noun_leakage_report" in pattern_pack["whole_book_analysis_targets"]
    assert pattern_pack["source_entity_redaction_gate_hints"]
    assert pattern_pack["custom_entity_label_inventory_hints"]
    assert pattern_pack["placeholder_alias_consistency_map_hints"]
    assert pattern_pack["proper_noun_leakage_review_hints"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "source_entity_redaction_gate_hints" in digest
    assert "custom_entity_label_inventory_hints" in digest
    assert "placeholder_alias_consistency_map_hints" in digest
    assert "proper_noun_leakage_review_hints" in digest


def test_default_discovery_sources_include_entity_redaction_projects():
    assert "https://github.com/microsoft/presidio" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/LeapBeyond/scrubadub" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/urchade/GLiNER" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/flairNLP/flair" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/explosion/spaCy" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("de-identification" in query.lower() and "redaction" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("zero-shot ner" in query.lower() and "custom entity types" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_ebook_quality_projects_classify_into_publication_quality_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "w3c/epubcheck",
                "html_url": "https://github.com/w3c/epubcheck",
                "description": "EPUB conformance checker validating OPF manifest, package document, container.xml, spine validation, media-type validation, and navigation document.",
                "stargazers_count": 1800,
                "forks_count": 400,
                "license": {"spdx_id": "BSD-3-Clause"},
                "topics": ["epub", "validation", "ebook"],
                "updated_at": "2026-06-10T19:00:00Z",
                "root_files": ["README.md", "LICENSE.md", "pom.xml"],
            },
            {
                "full_name": "daisy/ace",
                "html_url": "https://github.com/daisy/ace",
                "description": "Ace by DAISY is an EPUB accessibility checker for accessibility metadata, WCAG, screen reader behavior, landmarks, alt text, and hazards.",
                "stargazers_count": 650,
                "forks_count": 120,
                "license": {"spdx_id": "MIT"},
                "topics": ["epub", "accessibility", "wcag"],
                "updated_at": "2026-06-10T19:05:00Z",
                "root_files": ["README.md", "LICENSE.txt", "package.json"],
            },
            {
                "full_name": "standardebooks/tools",
                "html_url": "https://github.com/standardebooks/tools",
                "description": "Tools to produce ebooks with front matter, back matter, titlepage, endnotes, colophon, publication metadata, and build checks.",
                "stargazers_count": 1430,
                "forks_count": 210,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["epub", "ebooks", "publishing"],
                "updated_at": "2026-06-10T19:10:00Z",
                "root_files": ["README.md", "LICENSE.md"],
            },
            {
                "full_name": "Sigil-Ebook/Sigil",
                "html_url": "https://github.com/Sigil-Ebook/Sigil",
                "description": "EPUB editor with nav TOC, NCX, table of contents, spine order, heading hierarchy, landmarks, and reader navigation surfaces.",
                "stargazers_count": 6000,
                "forks_count": 700,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["epub", "ebook-editor"],
                "updated_at": "2026-06-10T19:15:00Z",
                "root_files": ["README.md", "COPYING.txt"],
            },
            {
                "full_name": "w3c/epub-tests",
                "html_url": "https://github.com/w3c/epub-tests",
                "description": "EPUB tests for EPUB 3 specifications covering package document, navigation document, spine order, and validation fixtures.",
                "stargazers_count": 120,
                "forks_count": 70,
                "license": {"spdx_id": "W3C"},
                "topics": ["epub", "tests"],
                "updated_at": "2026-06-10T19:20:00Z",
                "root_files": ["README.md", "LICENSE.md"],
            },
            {
                "full_name": "daisy/epub-accessibility-tests",
                "html_url": "https://github.com/daisy/epub-accessibility-tests",
                "description": "EPUB accessibility tests for reading system accessibility and reader navigation behavior.",
                "stargazers_count": 90,
                "forks_count": 25,
                "license": None,
                "topics": ["epub", "accessibility", "tests"],
                "updated_at": "2026-06-10T19:25:00Z",
                "root_files": ["README.md"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T19:30:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "epub_structure_validation_gate" in by_title["w3c/epubcheck"]["absorbed_patterns"]
    assert "toc_navigation_consistency_gate" in by_title["w3c/epubcheck"]["absorbed_patterns"]
    assert "ebook_accessibility_audit_gate" in by_title["daisy/ace"]["absorbed_patterns"]
    assert "front_back_matter_metadata_gate" in by_title["standardebooks/tools"]["absorbed_patterns"]
    assert "toc_navigation_consistency_gate" in by_title["Sigil-Ebook/Sigil"]["absorbed_patterns"]
    assert "epub_structure_validation_gate" in by_title["w3c/epub-tests"]["absorbed_patterns"]
    assert "ebook_accessibility_audit_gate" in by_title["daisy/epub-accessibility-tests"]["absorbed_patterns"]
    assert "license:missing" in by_title["daisy/epub-accessibility-tests"]["trust_review"]["flags"]


def test_ebook_quality_pattern_pack_exposes_delivery_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T19:35:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/w3c/epubcheck",
                "title": "w3c/epubcheck",
                "summary": "EPUB conformance validation for OPF, spine, nav, media type, and package structure.",
                "stars": 1800,
                "license": "BSD-3-Clause",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["epub_structure_validation_gate"],
                "score": 90,
            },
            {
                "source": "github",
                "url": "https://github.com/daisy/ace",
                "title": "daisy/ace",
                "summary": "EPUB accessibility audit for metadata, landmarks, reading order and alt text.",
                "stars": 650,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["ebook_accessibility_audit_gate"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/standardebooks/tools",
                "title": "standardebooks/tools",
                "summary": "Ebook production tools with front matter, back matter, titlepage, endnotes, colophon and metadata checks.",
                "stars": 1430,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["front_back_matter_metadata_gate"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/Sigil-Ebook/Sigil",
                "title": "Sigil-Ebook/Sigil",
                "summary": "EPUB editor surfaces for TOC, nav, NCX, spine order and reader navigation.",
                "stars": 6000,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["toc_navigation_consistency_gate"],
                "score": 85,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "epub_validation_policy" in pattern_pack["bible_enrichment_targets"]
    assert "ebook_accessibility_policy" in pattern_pack["bible_enrichment_targets"]
    assert "front_back_matter_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "toc_navigation_policy" in pattern_pack["bible_enrichment_targets"]
    assert "epub_validation_report" in pattern_pack["whole_book_analysis_targets"]
    assert "ebook_accessibility_report" in pattern_pack["whole_book_analysis_targets"]
    assert "front_back_matter_report" in pattern_pack["whole_book_analysis_targets"]
    assert "toc_navigation_consistency_report" in pattern_pack["whole_book_analysis_targets"]
    assert pattern_pack["epub_structure_validation_gate_hints"]
    assert pattern_pack["ebook_accessibility_audit_gate_hints"]
    assert pattern_pack["front_back_matter_metadata_gate_hints"]
    assert pattern_pack["toc_navigation_consistency_gate_hints"]
    assert "epub_validation_delivery_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "epub_structure_validation_gate_hints" in digest
    assert "ebook_accessibility_audit_gate_hints" in digest
    assert "front_back_matter_metadata_gate_hints" in digest
    assert "toc_navigation_consistency_gate_hints" in digest


def test_default_discovery_sources_include_ebook_quality_projects():
    assert "https://github.com/w3c/epubcheck" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/daisy/ace" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/standardebooks/tools" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Sigil-Ebook/Sigil" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/w3c/epub-tests" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/daisy/epub-accessibility-tests" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("epubcheck" in query.lower() and "spine validation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("epub accessibility" in query.lower() and "wcag" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("front matter" in query.lower() and "colophon" in query.lower() for query in DEFAULT_GITHUB_QUERIES)



def test_agentic_editorial_craft_projects_classify_into_workbench_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "john-paul-ruf/novel-engine",
                "html_url": "https://github.com/john-paul-ruf/novel-engine",
                "description": "Novel Engine is a book-building system with seven specialized AI agents, an editorial production pipeline, professional editorial team, copy-editing and manuscript compile steps.",
                "stargazers_count": 40,
                "forks_count": 4,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["ai-writing", "creative-writing", "multi-agent", "novel-writing"],
                "updated_at": "2026-06-10T20:00:00Z",
                "root_files": ["README.md", "package.json", "src"],
            },
            {
                "full_name": "ThomasHoussin/Claude-Book",
                "html_url": "https://github.com/ThomasHoussin/Claude-Book",
                "description": "Claude Book is a multi-agent framework for writing novels with Claude Code, permanent bible files, transient state, state/current, chapter-NN archived states, timeline history, and state file templates.",
                "stargazers_count": 88,
                "forks_count": 10,
                "license": {"spdx_id": "MIT"},
                "topics": ["claude-code", "creative-writing", "multiagent-systems"],
                "updated_at": "2026-06-10T20:05:00Z",
                "root_files": ["README.md", "CLAUDE.md", ".claude", "agents", "bible", "state"],
            },
            {
                "full_name": "DoktorDaveJoos/manuscript",
                "html_url": "https://github.com/DoktorDaveJoos/Manuscript",
                "description": "Local-first desktop app for novelists with structural analysis, pacing visualization, prose refinement, local SQLite storage, acts, beats, plot points and chapters.",
                "stargazers_count": 4,
                "forks_count": 0,
                "license": None,
                "topics": ["novels", "writing", "writing-tool"],
                "updated_at": "2026-06-10T20:10:00Z",
                "root_files": ["README.md", "app", "database", "resources"],
            },
            {
                "full_name": "geobond13/fiction-forge",
                "html_url": "https://github.com/geobond13/fiction-forge",
                "description": "Fiction Forge includes a prose pattern scanner for AI writing fingerprints, overused patterns, em-dashes, show-then-tell, hedging language, voice drift, severity scoring and cluster detection.",
                "stargazers_count": 12,
                "forks_count": 2,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-editing", "fiction", "mcp", "novel", "prose-linting"],
                "updated_at": "2026-06-10T20:15:00Z",
                "root_files": ["README.md", "pyproject.toml", "mcp", "templates"],
            },
            {
                "full_name": "shenminglinyi/PlotPilot",
                "html_url": "https://github.com/shenminglinyi/PlotPilot",
                "description": "PlotPilot is a narrative engine kernel for AI long-form creation with persistent memory, knowledge graph, narrative DAG workflows and customized review pipelines.",
                "stargazers_count": 1060,
                "forks_count": 100,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["novel", "ai-writing"],
                "updated_at": "2026-06-10T20:20:00Z",
                "root_files": ["README.md", "backend", "frontend", "docs"],
            },
            {
                "full_name": "peter88213/novelibre",
                "html_url": "https://github.com/peter88213/novelibre",
                "description": "novelibre keeps section metadata associated with chapters, relates characters, locations and items to sections, and assigns plot lines and plot points for large-novel planning.",
                "stargazers_count": 42,
                "forks_count": 9,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["novel", "novel-writing", "writer-tools"],
                "updated_at": "2026-06-10T20:25:00Z",
                "root_files": ["README.md", "src", "docs", "LICENSE"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T20:30:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "agentic_editorial_pipeline_gate" in by_title["john-paul-ruf/novel-engine"]["absorbed_patterns"]
    assert "agentic_editorial_pipeline_gate" in by_title["ThomasHoussin/Claude-Book"]["absorbed_patterns"]
    assert "chapter_state_archive_ladder" in by_title["ThomasHoussin/Claude-Book"]["absorbed_patterns"]
    assert "section_metadata_traceability_gate" in by_title["DoktorDaveJoos/manuscript"]["absorbed_patterns"]
    assert "ai_prose_fingerprint_cluster_gate" in by_title["geobond13/fiction-forge"]["absorbed_patterns"]
    assert "section_metadata_traceability_gate" in by_title["shenminglinyi/PlotPilot"]["absorbed_patterns"]
    assert "section_metadata_traceability_gate" in by_title["peter88213/novelibre"]["absorbed_patterns"]
    assert "license:missing" in by_title["DoktorDaveJoos/manuscript"]["trust_review"]["flags"]


def test_static_manuscript_health_ai_prep_source_maps_to_health_gate():
    assert "https://github.com/DoktorDaveJoos/manuscript" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any(
        "manuscript health score" in query.lower() and "ai preparation pipeline" in query.lower()
        for query in DEFAULT_GITHUB_QUERIES
    )

    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "DoktorDaveJoos/manuscript",
                "html_url": "https://github.com/DoktorDaveJoos/manuscript",
                "description": (
                    "Local-first desktop app for novelists with manuscript health score, "
                    "Story Heartbeat Canvas, Plot Health Dashboard, chapter ending analysis, "
                    "AI preparation pipeline, semantic chunks with overlap, story bible "
                    "population, style extraction, RAG, error recovery and circuit breaker."
                ),
                "stargazers_count": 5,
                "forks_count": 0,
                "license": None,
                "topics": ["literature", "novels", "writing", "writing-tool"],
                "updated_at": "2026-06-10T17:49:04Z",
                "root_files": ["README.md", "app", "database", "resources"],
            }
        ],
        forum_items=[],
        generated_at="2026-06-11T09:00:00+08:00",
    )

    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}
    candidate = by_title["DoktorDaveJoos/manuscript"]

    assert "manuscript_health_ai_prep_gate" in candidate["absorbed_patterns"]
    assert "license:missing" in candidate["trust_review"]["flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "manuscript_health_ai_prep_gate_hints" in pattern_pack
    assert "manuscript_health_score_axes" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_ending_taxonomy" in pattern_pack["bible_enrichment_targets"]
    assert "ai_preparation_phase_policy" in pattern_pack["bible_enrichment_targets"]
    assert "manuscript_health_score_timeline" in pattern_pack["whole_book_analysis_targets"]
    assert "story_heartbeat_canvas_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_ending_classification_report" in pattern_pack["whole_book_analysis_targets"]
    assert "ai_preparation_recovery_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "manuscript_health_axis_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chapter_ending_taxonomy_remap" in pattern_pack["inspired_mapping_targets"]
    assert "ai_preparation_pipeline_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("ending cadence" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("health trends" in hint for hint in pattern_pack["inspired_transformation_hints"])
    assert any("heartbeat/pacing curve" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "manuscript_health_ai_prep_gate_hints" in digest
    assert "chapter_ending_taxonomy_remap" in digest


def test_agentic_editorial_craft_pattern_pack_exposes_state_metadata_and_fingerprint_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T20:35:00+08:00",
        "candidate_count": 4,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/john-paul-ruf/novel-engine",
                "title": "john-paul-ruf/novel-engine",
                "summary": "Agentic editorial pipeline with author boundary and manuscript compile stages.",
                "stars": 40,
                "license": "AGPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["agentic_editorial_pipeline_gate"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/ThomasHoussin/Claude-Book",
                "title": "ThomasHoussin/Claude-Book",
                "summary": "Permanent bible and per-chapter archived transient state ladder.",
                "stars": 88,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["chapter_state_archive_ladder"],
                "score": 87,
            },
            {
                "source": "github",
                "url": "https://github.com/peter88213/novelibre",
                "title": "peter88213/novelibre",
                "summary": "Section metadata traceability for cast, locations, items, plot lines and plot points.",
                "stars": 42,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["section_metadata_traceability_gate"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/geobond13/fiction-forge",
                "title": "geobond13/fiction-forge",
                "summary": "AI prose fingerprint scanner with severity clusters and voice drift findings.",
                "stars": 12,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["ai_prose_fingerprint_cluster_gate"],
                "score": 85,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "editorial_role_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_state_archive_policy" in pattern_pack["bible_enrichment_targets"]
    assert "section_metadata_schema" in pattern_pack["bible_enrichment_targets"]
    assert "ai_prose_fingerprint_scan_policy" in pattern_pack["bible_enrichment_targets"]
    assert "editorial_pipeline_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_state_archive_diff_report" in pattern_pack["whole_book_analysis_targets"]
    assert "section_metadata_coverage_report" in pattern_pack["whole_book_analysis_targets"]
    assert "ai_prose_fingerprint_cluster_report" in pattern_pack["whole_book_analysis_targets"]
    assert pattern_pack["agentic_editorial_pipeline_gate_hints"]
    assert pattern_pack["chapter_state_archive_ladder_hints"]
    assert pattern_pack["section_metadata_traceability_gate_hints"]
    assert pattern_pack["ai_prose_fingerprint_cluster_gate_hints"]
    assert "editorial_role_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chapter_state_ladder_remap" in pattern_pack["inspired_mapping_targets"]
    assert "section_metadata_traceability_remap" in pattern_pack["inspired_mapping_targets"]
    assert "prose_fingerprint_threshold_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "agentic_editorial_pipeline_gate_hints" in digest
    assert "chapter_state_archive_ladder_hints" in digest
    assert "section_metadata_traceability_gate_hints" in digest
    assert "ai_prose_fingerprint_cluster_gate_hints" in digest


def test_default_discovery_sources_include_agentic_editorial_craft_projects():
    assert "https://github.com/john-paul-ruf/novel-engine" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ThomasHoussin/Claude-Book" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/DoktorDaveJoos/Manuscript" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/geobond13/fiction-forge" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/shenminglinyi/PlotPilot" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/peter88213/novelibre" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("multi-agent framework" in query.lower() and "editorial pipeline" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("permanent bible" in query.lower() and "chapter state" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("section metadata" in query.lower() and "pacing visualization" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("ai writing fingerprints" in query.lower() and "cluster detection" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_chinese_longform_control_projects_classify_into_control_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "WENZIZZHENG/story-spec",
                "html_url": "https://github.com/WENZIZZHENG/story-spec",
                "description": "Chinese long-form fiction co-creation workbench.",
                "stargazers_count": 216,
                "forks_count": 19,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-writing", "creative-writing", "novel"],
                "updated_at": "2026-06-10T21:00:00Z",
                "root_files": ["README.md", "package.json", "agents", "docs"],
            },
            {
                "full_name": "KKKenChow/ai-novel-writer",
                "html_url": "https://github.com/KKKenChow/ai-novel-writer",
                "description": "Chinese full-chain local RAG novel tool with staged chapter generation.",
                "stargazers_count": 580,
                "forks_count": 65,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "rag", "creative-writing"],
                "updated_at": "2026-06-10T21:05:00Z",
                "root_files": ["README.md", "app.py", "requirements.txt"],
            },
            {
                "full_name": "papysans/Morpheus",
                "html_url": "https://github.com/papysans/Morpheus",
                "description": "Chinese multi-agent long-form writing workbench.",
                "stargazers_count": 742,
                "forks_count": 59,
                "license": None,
                "topics": ["novel", "multi-agent", "long-form-writing"],
                "updated_at": "2026-06-10T21:10:00Z",
                "root_files": ["README.md", "backend", "frontend", "docker-compose.yml"],
            },
            {
                "full_name": "jingtai123/Novel-Control-Station-Skill",
                "html_url": "https://github.com/jingtai123/Novel-Control-Station-Skill",
                "description": "Chinese long-form fiction control skill with chapter control cards and dynamic state write-back.",
                "stargazers_count": 68,
                "forks_count": 7,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "claude-code-skill", "writing"],
                "updated_at": "2026-06-10T21:15:00Z",
                "root_files": ["README.md", "SKILL.md", "scripts"],
            },
            {
                "full_name": "xindoo/sumeru",
                "html_url": "https://github.com/xindoo/sumeru",
                "description": "Chinese webnovel AI Agent skill collection.",
                "stargazers_count": 91,
                "forks_count": 8,
                "license": None,
                "topics": ["webnovel", "ai-agent", "writing"],
                "updated_at": "2026-06-10T21:20:00Z",
                "root_files": ["README.md", ".sumeru", "skills"],
            },
            {
                "full_name": "AI-Practical-Lab/ai-novel",
                "html_url": "https://github.com/AI-Practical-Lab/ai-novel",
                "description": "AI-driven novel creation assistant with structured world, character, outline, and chapter management.",
                "stargazers_count": 102,
                "forks_count": 13,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-writing", "novel", "creative-writing"],
                "updated_at": "2026-06-10T21:25:00Z",
                "root_files": ["README.md", "frontend", "backend", "package.json"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T21:30:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }

    assert "author_candidate_canon_confirmation_gate" in patterns_by_title["WENZIZZHENG/story-spec"]
    assert {
        "progressive_spoiler_context_window_gate",
        "relationship_graph_global_replace_gate",
    }.issubset(patterns_by_title["KKKenChow/ai-novel-writer"])
    assert "trace_replay_revision_workspace_gate" in patterns_by_title["papysans/Morpheus"]
    assert "chapter_control_card_writeback_gate" in patterns_by_title["jingtai123/Novel-Control-Station-Skill"]
    assert {
        "chapter_control_card_writeback_gate",
        "continuation",
        "self_review",
    }.issubset(patterns_by_title["xindoo/sumeru"])
    assert "progressive_spoiler_context_window_gate" in patterns_by_title["AI-Practical-Lab/ai-novel"]
    by_title = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "license:missing" in by_title["papysans/Morpheus"]["trust_review"]["flags"]
    assert "license:missing" in by_title["xindoo/sumeru"]["trust_review"]["flags"]


def test_chinese_longform_control_pattern_pack_exposes_confirmation_spoiler_writeback_trace_and_graph_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T21:35:00+08:00",
        "candidate_count": 5,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/WENZIZZHENG/story-spec",
                "title": "WENZIZZHENG/story-spec",
                "summary": "Candidate-not-canon preview/confirm/apply workbench.",
                "stars": 216,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["author_candidate_canon_confirmation_gate"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/KKKenChow/ai-novel-writer",
                "title": "KKKenChow/ai-novel-writer",
                "summary": "Spoiler filtering, future chapter validation, global replacement, and relationship graphs.",
                "stars": 580,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["progressive_spoiler_context_window_gate", "relationship_graph_global_replace_gate"],
                "score": 87,
            },
            {
                "source": "github",
                "url": "https://github.com/papysans/Morpheus",
                "title": "papysans/Morpheus",
                "summary": "Trace replay and chapter revision workspace.",
                "stars": 742,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker"],
                "absorbed_patterns": ["trace_replay_revision_workspace_gate"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/jingtai123/Novel-Control-Station-Skill",
                "title": "jingtai123/Novel-Control-Station-Skill",
                "summary": "Chapter control card and dynamic state write-back.",
                "stars": 68,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["chapter_control_card_writeback_gate"],
                "score": 85,
            },
            {
                "source": "github",
                "url": "https://github.com/AI-Practical-Lab/ai-novel",
                "title": "AI-Practical-Lab/ai-novel",
                "summary": "Structured Chinese novel workflow and context-window lessons.",
                "stars": 102,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["progressive_spoiler_context_window_gate"],
                "score": 84,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "candidate_canon_confirmation_policy" in pattern_pack["bible_enrichment_targets"]
    assert "spoiler_context_window_policy" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_control_card_schema" in pattern_pack["bible_enrichment_targets"]
    assert "trace_replay_review_policy" in pattern_pack["bible_enrichment_targets"]
    assert "relationship_graph_update_policy" in pattern_pack["bible_enrichment_targets"]
    assert "candidate_canon_confirmation_report" in pattern_pack["whole_book_analysis_targets"]
    assert "future_chapter_leakage_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "dynamic_state_writeback_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "revision_decision_trace_log" in pattern_pack["whole_book_analysis_targets"]
    assert "global_replace_propagation_findings" in pattern_pack["whole_book_analysis_targets"]
    assert pattern_pack["author_candidate_canon_confirmation_gate_hints"]
    assert pattern_pack["progressive_spoiler_context_window_gate_hints"]
    assert pattern_pack["chapter_control_card_writeback_gate_hints"]
    assert pattern_pack["trace_replay_revision_workspace_gate_hints"]
    assert pattern_pack["relationship_graph_global_replace_gate_hints"]
    assert "candidate_canon_decision_remap" in pattern_pack["inspired_mapping_targets"]
    assert "spoiler_context_window_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chapter_control_card_remap" in pattern_pack["inspired_mapping_targets"]
    assert "trace_replay_decision_remap" in pattern_pack["inspired_mapping_targets"]
    assert "relationship_graph_replace_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "author_candidate_canon_confirmation_gate_hints" in digest
    assert "progressive_spoiler_context_window_gate_hints" in digest
    assert "chapter_control_card_writeback_gate_hints" in digest
    assert "trace_replay_revision_workspace_gate_hints" in digest
    assert "relationship_graph_global_replace_gate_hints" in digest
    assert "candidate canon decisions" in digest
    assert "source-analysis traces" in digest


def test_default_discovery_sources_include_chinese_longform_control_projects():
    assert "https://github.com/WENZIZZHENG/story-spec" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/KKKenChow/ai-novel-writer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/papysans/Morpheus" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jingtai123/Novel-Control-Station-Skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/xindoo/sumeru" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/AI-Practical-Lab/ai-novel" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("preview confirm apply" in query.lower() and "candidate is not canon" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("spoiler filtering" in query.lower() and "future chapter" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("chapter control card" in query.lower() and "dynamic state" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("trace replay" in query.lower() and "chapter workbench" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("global find replace" in query.lower() and "relationship graph" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_bookrun_skill_protocol_sources_map_to_runtime_boundary_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "XZZKANY/StoryForge",
                "html_url": "https://github.com/XZZKANY/StoryForge",
                "description": "BookRun Blueprint Judge/Repair export audit and real LLM smoke gates for Chinese long-form novels.",
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["novel", "long-form-writing"],
                "updated_at": "2026-06-10T21:50:00Z",
                "root_files": ["README.md", "package.json", "docker-compose.yml", "scripts"],
            },
            {
                "full_name": "spiritLHLS/novelbuilder",
                "html_url": "https://github.com/spiritLHLS/novelbuilder",
                "description": "AI long-form fiction workbench with Go API Gateway, Python Sidecar, graph/vector memory, deployment profiles, Qdrant and Neo4j.",
                "stargazers_count": 9,
                "forks_count": 1,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["novel", "agent", "rag"],
                "updated_at": "2026-06-10T21:51:00Z",
                "root_files": ["README.md", "LICENSE", "Dockerfile", "python-sidecar"],
            },
            {
                "full_name": "qiuxinyuan321/novel-writer-master",
                "html_url": "https://github.com/qiuxinyuan321/novel-writer-master",
                "description": "AI-assisted novel writing tool with anti-AI-rate engine, layered outline, checkpoint constraints, narrative milestones, and Story Bible truth source.",
                "stargazers_count": 1,
                "forks_count": 0,
                "license": None,
                "topics": ["novel", "writing"],
                "updated_at": "2026-06-10T21:52:00Z",
                "root_files": ["README.md", "pyproject.toml"],
            },
            {
                "full_name": "Byk3y/no-slop",
                "html_url": "https://github.com/Byk3y/no-slop",
                "description": "A prose linter and rulepack for AI writing patterns, banned vocabulary, simple copulas, vague attribution, and triage.",
                "stargazers_count": 4,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["writing", "prose", "claude-code"],
                "updated_at": "2026-06-10T21:53:00Z",
                "root_files": ["README.md", "SKILL.md", "banned-vocabulary.md"],
            },
            {
                "full_name": "nntrivi2001/wordsmith",
                "html_url": "https://github.com/nntrivi2001/wordsmith",
                "description": "Long-form webnovel system with eight skills, seven agents, local RAG, dashboard, resume, learn workflow, and Vietnamese writing patterns.",
                "stargazers_count": 2,
                "forks_count": 0,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["webnovel", "claude-code"],
                "updated_at": "2026-06-10T21:54:00Z",
                "root_files": ["README.md", "LICENSE", "requirements.txt", "wordsmith"],
            },
            {
                "full_name": "zy-zmc/tianming-skill",
                "html_url": "https://github.com/zy-zmc/tianming-skill",
                "description": "Long-form novel skill with progressive disclosure, intent-based command routing, protocol files, knowledge base binding, and language style guide.",
                "stargazers_count": 12,
                "forks_count": 1,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["novel", "skill", "writing"],
                "updated_at": "2026-06-10T21:55:00Z",
                "root_files": ["README.md", "SKILL.md", "LICENSE", "protocols", "codex"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T21:55:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }

    assert {"bookrun_audit_trail_gate", "provider_budget_smoke_gate"}.issubset(
        patterns_by_title["XZZKANY/StoryForge"]
    )
    assert {"sidecar_memory_profile_boundary", "provider_budget_smoke_gate"}.issubset(
        patterns_by_title["spiritLHLS/novelbuilder"]
    )
    assert {"outline_checkpoint_milestone_gate", "anti_slop_rulepack_triage_gate"}.issubset(
        patterns_by_title["qiuxinyuan321/novel-writer-master"]
    )
    assert "anti_slop_rulepack_triage_gate" in patterns_by_title["Byk3y/no-slop"]
    assert "language_localization_style_profile_gate" in patterns_by_title["nntrivi2001/wordsmith"]
    assert {
        "progressive_disclosure_skill_protocol_gate",
        "language_localization_style_profile_gate",
    }.issubset(patterns_by_title["zy-zmc/tianming-skill"])


def test_bookrun_skill_protocol_pattern_pack_exposes_runtime_and_style_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T21:58:00+08:00",
        "candidate_count": 7,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/XZZKANY/StoryForge",
                "title": "XZZKANY/StoryForge",
                "summary": "BookRun, Blueprint, Judge/Repair, export audit and provider smoke gates.",
                "stars": 0,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker", "shell_script"],
                "absorbed_patterns": ["bookrun_audit_trail_gate", "provider_budget_smoke_gate"],
                "score": 89,
            },
            {
                "source": "github",
                "url": "https://github.com/spiritLHLS/novelbuilder",
                "title": "spiritLHLS/novelbuilder",
                "summary": "Go API gateway, Python sidecar, graph/vector memory and deployment profiles.",
                "stars": 9,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["docker"],
                "absorbed_patterns": ["sidecar_memory_profile_boundary", "provider_budget_smoke_gate"],
                "score": 88,
            },
            {
                "source": "github",
                "url": "https://github.com/qiuxinyuan321/novel-writer-master",
                "title": "qiuxinyuan321/novel-writer-master",
                "summary": "Layered outline, checkpoint constraints, narrative milestones, and anti-AI prose review.",
                "stars": 1,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["outline_checkpoint_milestone_gate", "anti_slop_rulepack_triage_gate"],
                "score": 87,
            },
            {
                "source": "github",
                "url": "https://github.com/Byk3y/no-slop",
                "title": "Byk3y/no-slop",
                "summary": "Banned vocabulary, simple copulas, vague attribution, and prose rule triage.",
                "stars": 4,
                "license": "MIT",
                "family": "writing-quality",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["anti_slop_rulepack_triage_gate"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/nntrivi2001/wordsmith",
                "title": "nntrivi2001/wordsmith",
                "summary": "Vietnamese writing patterns, skills, agents, local RAG, dashboard, resume and learn workflow.",
                "stars": 2,
                "license": "GPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["language_localization_style_profile_gate", "progressive_disclosure_skill_protocol_gate"],
                "score": 85,
            },
            {
                "source": "github",
                "url": "https://github.com/zy-zmc/tianming-skill",
                "title": "zy-zmc/tianming-skill",
                "summary": "Progressive disclosure, protocol files, intent-based command routing, knowledge base and style samples.",
                "stars": 12,
                "license": "CC-BY-NC-SA-4.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["progressive_disclosure_skill_protocol_gate", "language_localization_style_profile_gate"],
                "score": 84,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "bookrun_audit_trail_policy" in pattern_pack["bible_enrichment_targets"]
    assert "provider_budget_smoke_policy" in pattern_pack["bible_enrichment_targets"]
    assert "sidecar_memory_boundary_policy" in pattern_pack["bible_enrichment_targets"]
    assert "outline_checkpoint_milestone_policy" in pattern_pack["bible_enrichment_targets"]
    assert "language_style_profile" in pattern_pack["bible_enrichment_targets"]
    assert "skill_protocol_route_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "anti_slop_rulepack" in pattern_pack["bible_enrichment_targets"]
    assert "bookrun_audit_trail_report" in pattern_pack["whole_book_analysis_targets"]
    assert "provider_budget_smoke_report" in pattern_pack["whole_book_analysis_targets"]
    assert "sidecar_memory_profile_report" in pattern_pack["whole_book_analysis_targets"]
    assert "outline_checkpoint_milestone_report" in pattern_pack["whole_book_analysis_targets"]
    assert "language_style_profile_report" in pattern_pack["whole_book_analysis_targets"]
    assert "skill_protocol_route_report" in pattern_pack["whole_book_analysis_targets"]
    assert "anti_slop_rulepack_triage_report" in pattern_pack["whole_book_analysis_targets"]
    assert pattern_pack["bookrun_audit_trail_gate_hints"]
    assert pattern_pack["provider_budget_smoke_gate_hints"]
    assert pattern_pack["sidecar_memory_profile_boundary_hints"]
    assert pattern_pack["outline_checkpoint_milestone_gate_hints"]
    assert pattern_pack["language_localization_style_profile_gate_hints"]
    assert pattern_pack["progressive_disclosure_skill_protocol_gate_hints"]
    assert pattern_pack["anti_slop_rulepack_triage_gate_hints"]
    assert "bookrun_audit_trail_remap" in pattern_pack["inspired_mapping_targets"]
    assert "provider_budget_profile_remap" in pattern_pack["inspired_mapping_targets"]
    assert "sidecar_memory_profile_remap" in pattern_pack["inspired_mapping_targets"]
    assert "outline_milestone_remap" in pattern_pack["inspired_mapping_targets"]
    assert "language_style_profile_remap" in pattern_pack["inspired_mapping_targets"]
    assert "skill_protocol_route_remap" in pattern_pack["inspired_mapping_targets"]
    assert "anti_slop_rulepack_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "bookrun_audit_trail_gate_hints" in digest
    assert "provider_budget_smoke_gate_hints" in digest
    assert "sidecar_memory_profile_boundary_hints" in digest
    assert "outline_checkpoint_milestone_gate_hints" in digest
    assert "language_localization_style_profile_gate_hints" in digest
    assert "progressive_disclosure_skill_protocol_gate_hints" in digest
    assert "anti_slop_rulepack_triage_gate_hints" in digest


def test_default_discovery_sources_include_bookrun_skill_protocol_projects():
    assert "https://github.com/XZZKANY/StoryForge" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/spiritLHLS/novelbuilder" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/qiuxinyuan321/novel-writer-master" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Byk3y/no-slop" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/nntrivi2001/wordsmith" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/zy-zmc/tianming-skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("bookrun" in query.lower() and "judge/repair" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("provider budget" in query.lower() and "smoke gate" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("python sidecar" in query.lower() and "deployment profiles" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("outline checkpoint" in query.lower() and "narrative milestones" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("language style guide" in query.lower() and "vietnamese writing patterns" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("progressive disclosure" in query.lower() and "protocol files" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("no-slop" in query.lower() and "banned vocabulary" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_project_workbench_memory_sources_map_to_blueprint_and_wiki_patterns():
    service = NovelSourceDiscoveryService()

    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "para-droid-ai/NovelizeAI",
                "html_url": "https://github.com/para-droid-ai/NovelizeAI",
                "description": "Novel app with project modifiers, AI-driven initial planning, chapter review, live timings, system log, and project state export JSON.",
                "stargazers_count": 0,
                "license": None,
                "topics": ["novel", "writing", "gemini"],
                "updated_at": "2026-06-10T22:10:00Z",
                "root_files": ["README.md", "package.json"],
            },
            {
                "full_name": "Moosphan/novel-orchestrator",
                "html_url": "https://github.com/Moosphan/novel-orchestrator",
                "description": "Long-form fiction engine with canon governance, story/*.md, markdown frontmatter, portable skill runtime, SQLite state, artifacts, checkpoints, and canon-sync.",
                "stargazers_count": 5,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["novel", "agent", "canon"],
                "updated_at": "2026-06-10T22:11:00Z",
                "root_files": ["README.md", "LICENSE", "pyproject.toml"],
            },
            {
                "full_name": "kirinonakar/Novelgen",
                "html_url": "https://github.com/kirinonakar/Novelgen",
                "description": "AI story generator with sliding-window memory, focused plot context, adjacent parts, CJK-aware counter, start/end chapter range refinement, batch start, and resume interrupted generation.",
                "stargazers_count": 7,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "tauri", "writing"],
                "updated_at": "2026-06-10T22:12:00Z",
                "root_files": ["README.md", "LICENSE", "src-tauri"],
            },
            {
                "full_name": "abrahamp47/storyforge-wiki",
                "html_url": "https://github.com/abrahamp47/storyforge-wiki",
                "description": "Story bible wiki with canon lint, wiki-query, wiki-graph, continuity warnings, timeline contradictions, unresolved setup/payoff, and relationship graph.",
                "stargazers_count": 2,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "worldbuilding", "wiki"],
                "updated_at": "2026-06-10T22:13:00Z",
                "root_files": ["README.md", "LICENSE", "wiki", "raw"],
            },
            {
                "full_name": "third-order-labs/longform-plugin",
                "html_url": "https://github.com/third-order-labs/longform-plugin",
                "description": "Longform writing workflow with Plan -> Draft -> Log -> Verify loop, living documents, scene logs, thread tracking, foreshadowing checklists, review and wrap.",
                "stargazers_count": 3,
                "license": {"spdx_id": "MIT"},
                "topics": ["longform", "novel", "claude"],
                "updated_at": "2026-06-10T22:14:00Z",
                "root_files": ["README.md", "LICENSE", "commands"],
            },
            {
                "full_name": "hannasdev/mcp-writing",
                "html_url": "https://github.com/hannasdev/mcp-writing",
                "description": "MCP writing service with metadata-first analysis, SQLite-canonical scene files, targeted scene reading, safe scene revision, AI-assisted prose editing with confirmation, git history, review bundles, and Scrivener Direct extraction.",
                "stargazers_count": 11,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["mcp", "novel", "writing"],
                "updated_at": "2026-06-10T22:15:00Z",
                "root_files": ["README.md", "LICENSE", "package.json"],
            },
            {
                "full_name": "xbraindance/Creative-writing-skill",
                "html_url": "https://github.com/xbraindance/Creative-writing-skill",
                "description": "Creative writing skill using Verbalized Sampling to avoid mode collapse, distribution of responses with probability score, writer's wiki, auto-files, and automatic character and setting detection.",
                "stargazers_count": 6,
                "license": {"spdx_id": "MIT"},
                "topics": ["creative-writing", "skill", "novel"],
                "updated_at": "2026-06-10T22:16:00Z",
                "root_files": ["README.md", "LICENSE", "SKILL.md"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T22:16:00+08:00",
    )

    patterns_by_title = {
        candidate["title"]: set(candidate["absorbed_patterns"])
        for candidate in result["candidates"]
    }

    assert "user_modifier_project_blueprint_gate" in patterns_by_title["para-droid-ai/NovelizeAI"]
    assert "portable_canon_skill_runtime_gate" in patterns_by_title["Moosphan/novel-orchestrator"]
    assert "staged_outline_chunk_window_gate" in patterns_by_title["kirinonakar/Novelgen"]
    assert "wiki_canon_graph_lint_gate" in patterns_by_title["abrahamp47/storyforge-wiki"]
    assert "plan_draft_log_verify_loop_gate" in patterns_by_title["third-order-labs/longform-plugin"]
    assert "mcp_scene_index_revision_boundary" in patterns_by_title["hannasdev/mcp-writing"]
    assert "verbalized_sampling_diversity_wiki_gate" in patterns_by_title["xbraindance/Creative-writing-skill"]


def test_project_workbench_memory_pattern_pack_exposes_blueprint_wiki_and_scene_guidance():
    service = NovelSourceDiscoveryService()
    ledger = {
        "generated_at": "2026-06-10T22:20:00+08:00",
        "candidate_count": 7,
        "candidates": [
            {
                "source": "github",
                "url": "https://github.com/para-droid-ai/NovelizeAI",
                "title": "para-droid-ai/NovelizeAI",
                "summary": "Project modifiers, initial planning, chapter review, timing log, and project-state export.",
                "stars": 0,
                "license": "unknown",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["provider"],
                "absorbed_patterns": ["user_modifier_project_blueprint_gate"],
                "score": 84,
            },
            {
                "source": "github",
                "url": "https://github.com/Moosphan/novel-orchestrator",
                "title": "Moosphan/novel-orchestrator",
                "summary": "Canon governance, frontmatter, portable skill runtime, SQLite state, artifacts, and canon-sync.",
                "stars": 5,
                "license": "PolyForm-Noncommercial",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["provider"],
                "absorbed_patterns": ["portable_canon_skill_runtime_gate"],
                "score": 86,
            },
            {
                "source": "github",
                "url": "https://github.com/kirinonakar/Novelgen",
                "title": "kirinonakar/Novelgen",
                "summary": "Staged long-outline planning, sliding-window memory, CJK-aware token counter, and chapter-range refinement.",
                "stars": 7,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["provider"],
                "absorbed_patterns": ["staged_outline_chunk_window_gate"],
                "score": 85,
            },
            {
                "source": "github",
                "url": "https://github.com/abrahamp47/storyforge-wiki",
                "title": "abrahamp47/storyforge-wiki",
                "summary": "Story bible wiki, canon lint, continuity query, timeline contradiction, setup/payoff and relationship graph checks.",
                "stars": 2,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["wiki_canon_graph_lint_gate"],
                "score": 83,
            },
            {
                "source": "github",
                "url": "https://github.com/third-order-labs/longform-plugin",
                "title": "third-order-labs/longform-plugin",
                "summary": "Plan Draft Log Verify loop with living documents, scene logs, thread tracking and foreshadowing checklists.",
                "stars": 3,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["plan_draft_log_verify_loop_gate"],
                "score": 82,
            },
            {
                "source": "github",
                "url": "https://github.com/hannasdev/mcp-writing",
                "title": "hannasdev/mcp-writing",
                "summary": "Metadata-first scene index, safe scene revision, confirmation, git history, review bundles and Scrivener import.",
                "stars": 11,
                "license": "AGPL-3.0",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": ["mcp", "docker"],
                "absorbed_patterns": ["mcp_scene_index_revision_boundary"],
                "score": 81,
            },
            {
                "source": "github",
                "url": "https://github.com/xbraindance/Creative-writing-skill",
                "title": "xbraindance/Creative-writing-skill",
                "summary": "Verbalized Sampling, mode collapse mitigation, probability-scored diverse variants, and writer wiki auto filing.",
                "stars": 6,
                "license": "MIT",
                "family": "novel-automation",
                "posture": "pattern-only",
                "risk_flags": [],
                "absorbed_patterns": ["verbalized_sampling_diversity_wiki_gate"],
                "score": 80,
            },
        ],
    }

    pattern_pack = service.build_pattern_pack_from_ledger(ledger)

    assert "user_modifier_blueprint_policy" in pattern_pack["bible_enrichment_targets"]
    assert "portable_canon_runtime_policy" in pattern_pack["bible_enrichment_targets"]
    assert "staged_outline_chunk_policy" in pattern_pack["bible_enrichment_targets"]
    assert "wiki_canon_lint_policy" in pattern_pack["bible_enrichment_targets"]
    assert "plan_draft_log_verify_policy" in pattern_pack["bible_enrichment_targets"]
    assert "scene_index_revision_boundary_policy" in pattern_pack["bible_enrichment_targets"]
    assert "verbalized_sampling_diversity_policy" in pattern_pack["bible_enrichment_targets"]
    assert "project_modifier_blueprint_report" in pattern_pack["whole_book_analysis_targets"]
    assert "portable_canon_runtime_report" in pattern_pack["whole_book_analysis_targets"]
    assert "staged_outline_chunk_window_report" in pattern_pack["whole_book_analysis_targets"]
    assert "wiki_canon_graph_lint_report" in pattern_pack["whole_book_analysis_targets"]
    assert "plan_draft_log_verify_report" in pattern_pack["whole_book_analysis_targets"]
    assert "scene_index_revision_boundary_report" in pattern_pack["whole_book_analysis_targets"]
    assert "verbalized_sampling_diversity_report" in pattern_pack["whole_book_analysis_targets"]
    assert pattern_pack["user_modifier_project_blueprint_gate_hints"]
    assert pattern_pack["portable_canon_skill_runtime_gate_hints"]
    assert pattern_pack["staged_outline_chunk_window_gate_hints"]
    assert pattern_pack["wiki_canon_graph_lint_gate_hints"]
    assert pattern_pack["plan_draft_log_verify_loop_gate_hints"]
    assert pattern_pack["mcp_scene_index_revision_boundary_hints"]
    assert pattern_pack["verbalized_sampling_diversity_wiki_gate_hints"]
    assert "project_blueprint_modifier_remap" in pattern_pack["inspired_mapping_targets"]
    assert "portable_canon_runtime_remap" in pattern_pack["inspired_mapping_targets"]
    assert "staged_outline_window_remap" in pattern_pack["inspired_mapping_targets"]
    assert "wiki_canon_graph_remap" in pattern_pack["inspired_mapping_targets"]
    assert "plan_draft_log_verify_remap" in pattern_pack["inspired_mapping_targets"]
    assert "scene_index_revision_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "verbalized_sampling_diversity_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "user_modifier_project_blueprint_gate_hints" in digest
    assert "portable_canon_skill_runtime_gate_hints" in digest
    assert "staged_outline_chunk_window_gate_hints" in digest
    assert "wiki_canon_graph_lint_gate_hints" in digest
    assert "plan_draft_log_verify_loop_gate_hints" in digest
    assert "mcp_scene_index_revision_boundary_hints" in digest
    assert "verbalized_sampling_diversity_wiki_gate_hints" in digest


def test_default_discovery_sources_include_project_workbench_memory_projects():
    assert "https://github.com/para-droid-ai/NovelizeAI" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Moosphan/novel-orchestrator" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/kirinonakar/Novelgen" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/abrahamp47/storyforge-wiki" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/third-order-labs/longform-plugin" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/hannasdev/mcp-writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/xbraindance/Creative-writing-skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("project modifiers" in query.lower() and "chapter review" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("canon governance" in query.lower() and "sqlite state" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("sliding-window memory" in query.lower() and "chapter range refinement" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("story bible wiki" in query.lower() and "relationship graph" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_default_discovery_sources_include_authorial_agent_interactive_delivery_projects():
    assert "https://github.com/tiny-flowlab/novel-studio-copilot-cli" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/guerra2fernando/libriscribe" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/muckelverk/pulpgen" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/bhed/sentiers-open-source" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("interactive narrative" in query.lower() and "choice graph" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_static_authorial_agent_interactive_delivery_sources_map_to_workflow_gates():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "tiny-flowlab/novel-studio-copilot-cli",
                "html_url": "https://github.com/tiny-flowlab/novel-studio-copilot-cli",
                "description": "",
                "stargazers_count": 6,
                "license": {"spdx_id": "MIT"},
                "topics": [],
                "updated_at": "2026-06-10T03:00:00Z",
                "root_files": ["README.md", "AGENTS.md", "LICENSE"],
            },
            {
                "full_name": "guerra2fernando/libriscribe",
                "html_url": "https://github.com/guerra2fernando/libriscribe",
                "description": "",
                "stargazers_count": 2,
                "license": {},
                "topics": [],
                "updated_at": "2026-06-10T03:00:00Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "muckelverk/pulpgen",
                "html_url": "https://github.com/muckelverk/pulpgen",
                "description": "",
                "stargazers_count": 10,
                "license": {"spdx_id": "MIT"},
                "topics": [],
                "updated_at": "2026-06-10T03:00:00Z",
                "root_files": ["README.md", "pyproject.toml", "LICENSE"],
            },
            {
                "full_name": "bhed/sentiers-open-source",
                "html_url": "https://github.com/bhed/sentiers-open-source",
                "description": "",
                "stargazers_count": 3,
                "license": {"spdx_id": "MIT"},
                "topics": [],
                "updated_at": "2026-06-10T03:00:00Z",
                "root_files": ["README.md", "LICENSE"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T12:00:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "agentic_editorial_pipeline_gate" in candidates["tiny-flowlab/novel-studio-copilot-cli"]["absorbed_patterns"]
    assert "craft_role_pipeline" in candidates["tiny-flowlab/novel-studio-copilot-cli"]["absorbed_patterns"]
    assert "craft_role_pipeline" in candidates["guerra2fernando/libriscribe"]["absorbed_patterns"]
    assert "delivery_manuscript_assembly" in candidates["muckelverk/pulpgen"]["absorbed_patterns"]
    assert "export_format_fidelity_audit" in candidates["muckelverk/pulpgen"]["absorbed_patterns"]
    assert "branching_choice_graph" in candidates["bhed/sentiers-open-source"]["absorbed_patterns"]
    assert "choice_stats_consequence_gate" in candidates["bhed/sentiers-open-source"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "agentic_editorial_pipeline_gate_hints" in pattern_pack
    assert "branching_choice_graph_hints" in pattern_pack
    assert "delivery_manuscript_assembly_hints" in pattern_pack
    assert any("plan draft log verify" in query.lower() and "living documents" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("metadata-first analysis" in query.lower() and "safe scene revision" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("verbalized sampling" in query.lower() and "writer wiki" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_default_discovery_sources_include_voice_timeline_skill_catalog_projects():
    assert "https://github.com/rhavekost/author-toolkit" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/mike-cramblett/novel-novel-generator" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/denmurray10/Story-Timeline-Builder" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jwynia/agent-skills" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("rolling summary" in query.lower() and "character state tracking" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("interactive narrative" in query.lower() and "choice graph" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_static_voice_timeline_skill_catalog_sources_map_to_safe_postures():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "rhavekost/author-toolkit",
                "html_url": "https://github.com/rhavekost/author-toolkit",
                "description": "",
                "stargazers_count": 3,
                "license": {},
                "topics": [],
                "updated_at": "2026-06-10T03:00:00Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "mike-cramblett/novel-novel-generator",
                "html_url": "https://github.com/mike-cramblett/novel-novel-generator",
                "description": "",
                "stargazers_count": 4,
                "license": {},
                "topics": [],
                "updated_at": "2026-06-10T03:00:00Z",
                "root_files": ["README.md", "package.json"],
            },
            {
                "full_name": "denmurray10/Story-Timeline-Builder",
                "html_url": "https://github.com/denmurray10/Story-Timeline-Builder",
                "description": "",
                "stargazers_count": 1,
                "license": {},
                "topics": [],
                "updated_at": "2026-06-10T03:00:00Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "jwynia/agent-skills",
                "html_url": "https://github.com/jwynia/agent-skills",
                "description": "",
                "stargazers_count": 42,
                "license": {},
                "topics": [],
                "updated_at": "2026-06-10T03:00:00Z",
                "root_files": ["README.md", "AGENTS.md"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T13:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert candidates["jwynia/agent-skills"]["posture"] == "index-only"
    assert candidates["jwynia/agent-skills"]["posture_hint"] == "catalog-index-only"
    assert candidates["jwynia/agent-skills"]["absorbed_patterns"] == ["source_discovery"]
    assert "craft_role_pipeline" in candidates["rhavekost/author-toolkit"]["absorbed_patterns"]
    assert "voice_fingerprint" in candidates["rhavekost/author-toolkit"]["absorbed_patterns"]
    assert "anti_repetition_prompt_rules" in candidates["mike-cramblett/novel-novel-generator"]["absorbed_patterns"]
    assert "voice_fingerprint" in candidates["mike-cramblett/novel-novel-generator"]["absorbed_patterns"]
    assert "character_interaction_network_gate" in candidates["denmurray10/Story-Timeline-Builder"]["absorbed_patterns"]
    assert "temporal_canon_context_graph" in candidates["denmurray10/Story-Timeline-Builder"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "character_interaction_network_gate_hints" in pattern_pack
    assert "temporal_canon_context_graph_hints" in pattern_pack
    assert "anti_repetition_prompt_rules_hints" in pattern_pack


def test_default_discovery_sources_include_causal_state_machine_skill_workflow_projects():
    assert "https://github.com/ydsgangge-ux/dramatica-flow" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/mmunro3318/story-foundry" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Shine8592/novel-writer-skills" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/modoojunko/awesome-novel-skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/langchain-ai/story-writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/EdwardAThomson/StoryDaemon" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("dramatica" in query.lower() and "causal chain" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("capture" in query.lower() and "distillation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("openclaw" in query.lower() and "chinese novel" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("langgraph" in query.lower() and "story state" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_static_causal_state_machine_skill_sources_map_to_workflow_gates():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "ydsgangge-ux/dramatica-flow",
                "html_url": "https://github.com/ydsgangge-ux/dramatica-flow",
                "description": "AI novel engine with Dramatica theory, causal chain management, multi-line narration and 5-layer Agent pipeline.",
                "stargazers_count": 163,
                "license": {},
                "topics": ["ai-writing", "novel-writing", "dramatica", "story-generation"],
                "updated_at": "2026-06-10T05:17:18Z",
                "root_files": ["README.md", "pyproject.toml", "install.sh", "install.bat", "tests"],
            },
            {
                "full_name": "mmunro3318/story-foundry",
                "html_url": "https://github.com/mmunro3318/story-foundry",
                "description": "Agentic platform to assist an author in ideation and writing a novel with Capture -> Distillation -> Production stages.",
                "stargazers_count": 3,
                "license": {},
                "topics": [],
                "updated_at": "2026-05-13T07:29:39Z",
                "root_files": ["README.md", "CLAUDE.md", "agent-template.md", "workflow"],
            },
            {
                "full_name": "Shine8592/novel-writer-skills",
                "html_url": "https://github.com/Shine8592/novel-writer-skills",
                "description": "Zero-cost AI Chinese novel writing with 3 OpenClaw skills, web-novel workflow, and provider budget constraints.",
                "stargazers_count": 9,
                "license": {},
                "topics": ["openclaw-skill", "chinese-novel", "novel-generator", "web-novel"],
                "updated_at": "2026-06-07T05:41:25Z",
                "root_files": ["README.md", "SKILL.md"],
            },
            {
                "full_name": "modoojunko/awesome-novel-skill",
                "html_url": "https://github.com/modoojunko/awesome-novel-skill",
                "description": "AI agent novel writing partner from worldbuilding to character shaping, chapter planning, prose writing, SKILL.md, agents, memory and templates.",
                "stargazers_count": 202,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["agent-skill", "ai-fiction", "ai-novel", "novel-writing", "story-generation"],
                "updated_at": "2026-06-10T03:07:38Z",
                "root_files": ["README.md", "SKILL.md", "install.sh", "install.ps1", "agents"],
            },
            {
                "full_name": "langchain-ai/story-writing",
                "html_url": "https://github.com/langchain-ai/story-writing",
                "description": "LangGraph story-writing sample with story state flow, agent.py and langgraph.json for stateful planning.",
                "stargazers_count": 155,
                "license": {},
                "topics": [],
                "updated_at": "2026-06-04T14:17:57Z",
                "root_files": ["README.md", "agent.py", "langgraph.json", "requirements.txt", "test.py"],
            },
            {
                "full_name": "EdwardAThomson/StoryDaemon",
                "html_url": "https://github.com/EdwardAThomson/StoryDaemon",
                "description": "StoryDaemon generates long-form fiction through an autonomous agent that plans, writes, and evolves stories organically.",
                "stargazers_count": 23,
                "license": {},
                "topics": ["creative-writing", "llms"],
                "updated_at": "2026-06-04T11:17:31Z",
                "root_files": ["README.md", "CLAUDE.md", "requirements.txt", "scripts", "tests"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T14:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "causal_dramatica_agent_pipeline" in candidates["ydsgangge-ux/dramatica-flow"]["absorbed_patterns"]
    assert "foreshadowing_debt_budget" in candidates["ydsgangge-ux/dramatica-flow"]["absorbed_patterns"]
    assert "capture_distillation_production_gate" in candidates["mmunro3318/story-foundry"]["absorbed_patterns"]
    assert "skill_orchestrated_chinese_novel_workflow" in candidates["Shine8592/novel-writer-skills"]["absorbed_patterns"]
    assert "provider_budget_smoke_gate" in candidates["Shine8592/novel-writer-skills"]["absorbed_patterns"]
    assert "skill_orchestrated_chinese_novel_workflow" in candidates["modoojunko/awesome-novel-skill"]["absorbed_patterns"]
    assert "langgraph_story_state_machine" in candidates["langchain-ai/story-writing"]["absorbed_patterns"]
    assert "story_daemon_evolution_loop" in candidates["EdwardAThomson/StoryDaemon"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "causal_dramatica_agent_pipeline_hints" in pattern_pack
    assert "capture_distillation_production_gate_hints" in pattern_pack
    assert "skill_orchestrated_chinese_novel_workflow_hints" in pattern_pack
    assert "langgraph_story_state_machine_hints" in pattern_pack
    assert "story_daemon_evolution_loop_hints" in pattern_pack
    assert "causal_dramatica_thread_map" in pattern_pack["bible_enrichment_targets"]
    assert "story_state_machine_schema" in pattern_pack["bible_enrichment_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "causal_dramatica_agent_pipeline_hints" in digest
    assert "skill_orchestrated_chinese_novel_workflow_hints" in digest



def test_default_discovery_sources_include_local_rag_canon_patch_projects():
    assert "https://github.com/datacrystals/AIStoryWriter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/sadasdfsaf/canonkit" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/heider-x/vela" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/pulpgen-dev/pulpgen" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jim60105/HeartReverie" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/wzxsph/Novel-Claude" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/liaoma1993/aiAIfiction" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/vishnu0120754/ReNovel-AI" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/worldwonderer/zenstory" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("local-first" in query.lower() and "local rag" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("canon drift" in query.lower() and "continuity checker" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("patch-nn" in query.lower() and "outline.xml" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("microkernel" in query.lower() and "eventbus" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_static_local_rag_canon_patch_sources_map_to_workflow_gates():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "datacrystals/AIStoryWriter",
                "html_url": "https://github.com/datacrystals/AIStoryWriter",
                "description": "LLM story writer with outline, chapter outline, chapter writer, revision, evaluation and local Ollama model support.",
                "stargazers_count": 251,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["story", "ai-writing", "long-output"],
                "updated_at": "2026-06-08T18:52:40Z",
                "root_files": ["README.md", "requirements.txt", "Write.py", "Evaluate.py", "LICENSE"],
            },
            {
                "full_name": "sadasdfsaf/canonkit",
                "html_url": "https://github.com/sadasdfsaf/canonkit",
                "description": "Local-first story bible and continuity checker for fiction teams and solo authors focused on canon drift and scene context packs.",
                "stargazers_count": 0,
                "license": {},
                "topics": ["fiction", "story-bible", "continuity"],
                "updated_at": "2026-03-30T05:54:12Z",
                "root_files": ["README.md", "package.json", "src"],
            },
            {
                "full_name": "heider-x/vela",
                "html_url": "https://github.com/heider-x/vela",
                "description": "AI novel writing IDE with local-first privacy BYOK local RAG knowledge base, auto outline, chapter drafting, rewrite refine review loop.",
                "stargazers_count": 367,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["novel", "rag", "creative-writing"],
                "updated_at": "2026-06-09T15:58:51Z",
                "root_files": ["README.md", "package.json", "electron", "LICENSE"],
            },
            {
                "full_name": "pulpgen-dev/pulpgen",
                "html_url": "https://github.com/pulpgen-dev/pulpgen",
                "description": "AI novel drafting agent with outline.xml, patch-NN.xml sequential dispatch logs, final.xml, final.html, version-NN.html and interactive AI-assisted editing.",
                "stargazers_count": 16,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "drafting-agent", "manuscript"],
                "updated_at": "2026-03-17T17:17:33Z",
                "root_files": ["README.md", "pyproject.toml", "pulpgen.py", "LICENSE"],
            },
            {
                "full_name": "jim60105/HeartReverie",
                "html_url": "https://github.com/jim60105/HeartReverie",
                "description": "AI interactive novel engine where reader guidance writes stories into chapter files with markdown lore codex and plugin.json hook ecosystem.",
                "stargazers_count": 2,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["interactive-fiction", "ai-writing"],
                "updated_at": "2026-06-04T21:48:57Z",
                "root_files": ["README.md", "deno.json", "Containerfile", "scripts", "plugins"],
            },
            {
                "full_name": "wzxsph/Novel-Claude",
                "html_url": "https://github.com/wzxsph/Novel-Claude",
                "description": "Agentic long-form web novel framework with microkernel plugin architecture, EventBus, PluginManager, NovelContext, RAG memory skill and Skill Builder Agent.",
                "stargazers_count": 5,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["novel", "agentic", "plugin"],
                "updated_at": "2026-06-07T08:49:33Z",
                "root_files": ["README.md", "requirements.txt", "skills", "prompts", "cli.py"],
            },
            {
                "full_name": "liaoma1993/aiAIfiction",
                "html_url": "https://github.com/liaoma1993/aiAIfiction",
                "description": "AI Fiction Studio long-form web novel workbench with style learning Skill, representative sampling, character voice matrix, quality audit and repair dashboard.",
                "stargazers_count": 8,
                "license": {},
                "topics": ["novel", "ai-writing", "style-learning"],
                "updated_at": "2026-06-10T02:49:08Z",
                "root_files": ["README.md", "docker-compose.yml", "backend", "frontend", "scripts"],
            },
            {
                "full_name": "vishnu0120754/ReNovel-AI",
                "html_url": "https://github.com/vishnu0120754/ReNovel-AI",
                "description": "Novel revision workspace with long-term memory, three-way collaboration, card-based editing, import, automated revisions and narrative expansion.",
                "stargazers_count": 12,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["rag", "writing", "revision"],
                "updated_at": "2026-06-10T04:22:53Z",
                "root_files": ["README.md", "requirements.txt", "Run.bat", "main.py"],
            },
            {
                "full_name": "worldwonderer/zenstory",
                "html_url": "https://github.com/worldwonderer/zenstory",
                "description": "AI novel workbench where agents create character cards, deconstruct reference material, plan outlines, write chapters, quality review, material library, hybrid RAG and context compression.",
                "stargazers_count": 6,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "agents", "rag"],
                "updated_at": "2026-06-06T19:09:12Z",
                "root_files": ["README.md", "package.json", "docker-compose.yml", "scripts", "apps"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T15:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "local_rag_writing_ide_gate" in candidates["heider-x/vela"]["absorbed_patterns"]
    assert "local_rag_writing_ide_gate" in candidates["worldwonderer/zenstory"]["absorbed_patterns"]
    assert "canon_drift_continuity_qa_gate" in candidates["sadasdfsaf/canonkit"]["absorbed_patterns"]
    assert "patch_replay_manuscript_state_gate" in candidates["pulpgen-dev/pulpgen"]["absorbed_patterns"]
    assert "microkernel_skill_plugin_isolation_gate" in candidates["wzxsph/Novel-Claude"]["absorbed_patterns"]
    assert "interactive_reader_writer_loop_gate" in candidates["jim60105/HeartReverie"]["absorbed_patterns"]
    assert "interactive_reader_writer_loop_gate" in candidates["vishnu0120754/ReNovel-AI"]["absorbed_patterns"]
    assert "abstract_style_learning_skill_gate" in candidates["liaoma1993/aiAIfiction"]["absorbed_patterns"]
    assert "chapter_generation" in candidates["datacrystals/AIStoryWriter"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "local_rag_writing_ide_gate_hints" in pattern_pack
    assert "canon_drift_continuity_qa_gate_hints" in pattern_pack
    assert "patch_replay_manuscript_state_gate_hints" in pattern_pack
    assert "microkernel_skill_plugin_isolation_gate_hints" in pattern_pack
    assert "interactive_reader_writer_loop_gate_hints" in pattern_pack
    assert "abstract_style_learning_skill_gate_hints" in pattern_pack
    assert "canon_drift_rulebook" in pattern_pack["bible_enrichment_targets"]
    assert "patch_replay_state_log" in pattern_pack["whole_book_analysis_targets"]
    assert "abstract_style_profile_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "local_rag_writing_ide_gate_hints" in digest
    assert "abstract_style_learning_skill_gate_hints" in digest


def test_default_discovery_sources_include_impromptu_offline_atelier_projects():
    assert "https://github.com/tuxiangxianzhe/NovelWriter_public" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/MA-Bihani/Novelia_public" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/huodebing-alt/Claude-Code-Novel-Agents" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("open_threads" in query and "single-chapter blueprint" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("inspiration bank" in query.lower() and "style mimicry" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("novel atelier" in query.lower() and "hook auditor" in query.lower() for query in DEFAULT_GITHUB_QUERIES)


def test_static_impromptu_offline_atelier_sources_map_to_workflow_gates():
    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "tuxiangxianzhe/NovelWriter_public",
                "html_url": "https://github.com/tuxiangxianzhe/NovelWriter_public",
                "description": "AI novel platform with improvised writing mode, open_threads foreshadowing pool, single-chapter blueprint, scene segmented generation, style imitation, continuation expansion and AI tone removal.",
                "stargazers_count": 73,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["novel", "ai-writing", "continuation"],
                "updated_at": "2026-05-26T09:00:00Z",
                "root_files": ["README.md", "LICENSE", "backend", "frontend", "docker-compose.yml"],
            },
            {
                "full_name": "MA-Bihani/Novelia_public",
                "html_url": "https://github.com/MA-Bihani/Novelia_public",
                "description": "Local-first offline creative writing environment with Ollama local RAG, Inspiration bank, Continue and Rewrite modes, style mimicry, dynamic style engine and filesystem book chapter storage.",
                "stargazers_count": 4,
                "license": {"spdx_id": "MIT"},
                "topics": ["creative-writing", "local-rag", "style-mimicry"],
                "updated_at": "2026-06-10T04:10:00Z",
                "root_files": ["README.md", "package.json", "electron", "src"],
            },
            {
                "full_name": "huodebing-alt/Claude-Code-Novel-Agents",
                "html_url": "https://github.com/huodebing-alt/Claude-Code-Novel-Agents",
                "description": "Claude Code novel atelier with 50 agents, 70 skills, 6-phase pipeline, detailed beat planner, hook auditor, infinite-serial mode, full semi manual human control modes and continuity reader.",
                "stargazers_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["claude-code", "novel", "agents"],
                "updated_at": "2026-06-07T13:41:58Z",
                "root_files": ["README.md", "LICENSE", "agents", "skills", "docs"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T16:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "impromptu_thread_pool_chapter_gate" in candidates["tuxiangxianzhe/NovelWriter_public"]["absorbed_patterns"]
    assert "offline_inspiration_bank_style_gate" in candidates["MA-Bihani/Novelia_public"]["absorbed_patterns"]
    assert "atelier_phase_pipeline_gate" in candidates["huodebing-alt/Claude-Code-Novel-Agents"]["absorbed_patterns"]
    assert "continuation" in candidates["tuxiangxianzhe/NovelWriter_public"]["absorbed_patterns"]
    assert "style_signature" in candidates["MA-Bihani/Novelia_public"]["absorbed_patterns"]
    assert "craft_role_pipeline" in candidates["huodebing-alt/Claude-Code-Novel-Agents"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "impromptu_thread_pool_chapter_gate_hints" in pattern_pack
    assert "offline_inspiration_bank_style_gate_hints" in pattern_pack
    assert "atelier_phase_pipeline_gate_hints" in pattern_pack
    assert "open_thread_pool_schema" in pattern_pack["bible_enrichment_targets"]
    assert "inspiration_bank_scope_report" in pattern_pack["whole_book_analysis_targets"]
    assert "atelier_phase_beat_tree_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "impromptu_thread_pool_chapter_gate_hints" in digest
    assert "offline_inspiration_bank_style_gate_hints" in digest
    assert "atelier_phase_pipeline_gate_hints" in digest


def test_static_book_mining_autopilot_longrun_sources_map_to_workflow_gates():
    assert "https://github.com/cchheerrss/ai-novel-trilogy" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/zhitongblog/novel-studio" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/DinhLucent/webnovel-longrun-aigen-docs" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Deland78/Claude-Writing-Skills" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/netflypsb/webnovel-mcp" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/hackertaco/novel-generator" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/eristoddle/git-write" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("book-mining" in query and "canon-seed" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("multi-book" in query and "autopilot" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("CHAPTER_COMMIT" in query and ".story-system" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "cchheerrss/ai-novel-trilogy",
                "html_url": "https://github.com/cchheerrss/ai-novel-trilogy",
                "description": "Three-system AI webnovel pipeline: book-mining -> novel-genesis -> novel-automation with pattern assembly, market scan, scoring gate, canon-seed handoff and pattern-aware quality gates.",
                "stargazers_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["webnovel", "book-mining", "novel-automation"],
                "updated_at": "2026-06-04T07:36:49Z",
                "root_files": ["README.md", "LICENSE", "book-mining", "novel-genesis", "novel-automation"],
            },
            {
                "full_name": "zhitongblog/novel-studio",
                "html_url": "https://github.com/zhitongblog/novel-studio",
                "description": "Multi-book webnovel studio with Unterm profile isolation, Codex Claude Gemini CLI orchestration, autopilot, maxAutoContinue, fullCheckEvery and full-book logic check cadence.",
                "stargazers_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "autopilot", "multi-book"],
                "updated_at": "2026-06-09T08:58:23Z",
                "root_files": ["README.md", "package.json", "mcp.json", "desktop", "src"],
            },
            {
                "full_name": "DinhLucent/webnovel-longrun-aigen-docs",
                "html_url": "https://github.com/DinhLucent/webnovel-longrun-aigen-docs",
                "description": "Webnovel Longrun AIGen uses .story-system source of truth, accepted CHAPTER_COMMIT, .webnovel state.json index.db summaries memory_scratchpad read-model projections and read-only dashboard.",
                "stargazers_count": 0,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["webnovel", "longrun", "memory"],
                "updated_at": "2026-05-17T06:32:24Z",
                "root_files": ["README.md", "LICENSE", "docs/assets/system-architecture.svg"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T17:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "book_mining_genesis_automation_gate" in candidates["cchheerrss/ai-novel-trilogy"]["absorbed_patterns"]
    assert "multi_book_autopilot_studio_gate" in candidates["zhitongblog/novel-studio"]["absorbed_patterns"]
    assert "longrun_commit_projection_health_gate" in candidates["DinhLucent/webnovel-longrun-aigen-docs"]["absorbed_patterns"]
    assert "trend_deconstruction_pipeline" in candidates["cchheerrss/ai-novel-trilogy"]["absorbed_patterns"]
    assert "continuation" in candidates["zhitongblog/novel-studio"]["absorbed_patterns"]
    assert "accepted_chapter_memory" in candidates["DinhLucent/webnovel-longrun-aigen-docs"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "book_mining_genesis_automation_gate_hints" in pattern_pack
    assert "multi_book_autopilot_studio_gate_hints" in pattern_pack
    assert "longrun_commit_projection_health_gate_hints" in pattern_pack
    assert "canon_seed_handoff_schema" in pattern_pack["bible_enrichment_targets"]
    assert "multi_book_profile_audit" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_commit_projection_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "book_mining_genesis_automation_gate_hints" in digest
    assert "multi_book_autopilot_studio_gate_hints" in digest
    assert "longrun_commit_projection_health_gate_hints" in digest


def test_static_document_conversion_literary_similarity_sources_map_to_import_gates():
    assert "https://github.com/microsoft/markitdown" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/docling-project/docling" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/opendatalab/MinerU" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/datalab-to/marker" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/lancopku/Chinese-Literature-NER-RE-Dataset" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ropensci/textreuse" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/cophi-wue/pydelta" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("markitdown" in query.lower() and "llm-ready" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("pdf to markdown" in query.lower() and "document parser" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("discourse-level ner" in query.lower() and "relation extraction" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("text reuse" in query.lower() and "pydelta" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "microsoft/markitdown",
                "html_url": "https://github.com/microsoft/markitdown",
                "description": "Python tool for converting files and office documents to Markdown with PDF, EPUB, DOCX, OCR and JSON optional surfaces for chapter import.",
                "stargazers_count": 149957,
                "license": {"spdx_id": "MIT"},
                "topics": ["markdown", "microsoft-office", "pdf", "autogen"],
                "updated_at": "2026-06-10T14:20:51Z",
                "root_files": ["README.md", "LICENSE", "Dockerfile", "packages"],
            },
            {
                "full_name": "docling-project/docling",
                "html_url": "https://github.com/docling-project/docling",
                "description": "Document parser for GenAI-ready conversion: PDF, DOCX, HTML, markdown, JSON, OCR, layout analysis, pdf-to-json, pdf-to-text and document parsing.",
                "stargazers_count": 61313,
                "license": {"spdx_id": "MIT"},
                "topics": ["document-parser", "pdf-to-json", "pdf-to-text", "markdown"],
                "updated_at": "2026-06-10T14:14:33Z",
                "root_files": ["README.md", "LICENSE", "Dockerfile", "AGENTS.md", "docling"],
            },
            {
                "full_name": "opendatalab/MinerU",
                "html_url": "https://github.com/opendatalab/MinerU",
                "description": "Transforms complex PDFs and Office docs into LLM-ready markdown and JSON with layout analysis, OCR, pdf parser and pdf extractor surfaces.",
                "stargazers_count": 67126,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["pdf", "ocr", "layout-analysis", "pdf-parser"],
                "updated_at": "2026-06-10T14:15:34Z",
                "root_files": ["README.md", "README_zh-CN.md", "LICENSE.md", "docker", "mineru"],
            },
            {
                "full_name": "datalab-to/marker",
                "html_url": "https://github.com/datalab-to/marker",
                "description": "Convert PDF to markdown and JSON with high accuracy, OCR, layout, chunk conversion, PDF-to-Markdown, DOCX and EPUB import surfaces.",
                "stargazers_count": 35954,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["pdf", "markdown", "ocr"],
                "updated_at": "2026-06-10T14:01:51Z",
                "root_files": ["README.md", "LICENSE", "chunk_convert.py", "marker_app.py", "marker_server.py"],
            },
            {
                "full_name": "lancopku/Chinese-Literature-NER-RE-Dataset",
                "html_url": "https://github.com/lancopku/Chinese-Literature-NER-RE-Dataset",
                "description": "A discourse-level named entity recognition and relation extraction dataset for Chinese literature text with entity and relation annotation format.",
                "stargazers_count": 424,
                "license": None,
                "topics": ["chinese-literature", "ner", "relation-extraction"],
                "updated_at": "2026-05-26T11:52:04Z",
                "root_files": ["README.md", "ner", "relation_extraction"],
            },
            {
                "full_name": "ropensci/textreuse",
                "html_url": "https://github.com/ropensci/textreuse",
                "description": "Detect text reuse and document similarity using pairwise comparisons, MinHash, locality sensitive hashing and text alignment.",
                "stargazers_count": 200,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["textreuse", "text-reuse", "similarity"],
                "updated_at": "2026-05-07T15:22:57Z",
                "root_files": ["README.md", "DESCRIPTION", "LICENSE", "R"],
            },
            {
                "full_name": "cophi-wue/pydelta",
                "html_url": "https://github.com/cophi-wue/pydelta",
                "description": "Experimental implementation of Burrow's Delta in Python 3 for computational stylistics and author style distance metrics.",
                "stargazers_count": 22,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["stylometry", "burrows-delta"],
                "updated_at": "2026-04-22T08:49:29Z",
                "root_files": ["README.rst", "licence.txt", "Delta-Intro.ipynb", "delta"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T22:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "source_format_import_manifest" in candidates["microsoft/markitdown"]["absorbed_patterns"]
    assert "document_partition_chapter_detection_gate" in candidates["docling-project/docling"]["absorbed_patterns"]
    assert "pdf_layout_text_extraction_gate" in candidates["opendatalab/MinerU"]["absorbed_patterns"]
    assert "ocr_scanned_page_import_gate" in candidates["datalab-to/marker"]["absorbed_patterns"]
    assert "chinese_ner_alias_consistency_gate" in candidates["lancopku/Chinese-Literature-NER-RE-Dataset"]["absorbed_patterns"]
    assert "source_text_fingerprint_gate" in candidates["ropensci/textreuse"]["absorbed_patterns"]
    assert "minhash_lsh_near_duplicate_gate" in candidates["ropensci/textreuse"]["absorbed_patterns"]
    assert "stylometric_author_fingerprint_gate" in candidates["cophi-wue/pydelta"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "source_format_import_manifest_hints" in pattern_pack
    assert "pdf_layout_text_extraction_gate_hints" in pattern_pack
    assert "ocr_scanned_page_import_gate_hints" in pattern_pack
    assert "document_partition_chapter_detection_gate_hints" in pattern_pack
    assert "chinese_ner_alias_consistency_gate_hints" in pattern_pack
    assert "source_text_fingerprint_gate_hints" in pattern_pack
    assert "stylometric_author_fingerprint_gate_hints" in pattern_pack
    assert "source_import_manifest_report" in pattern_pack["whole_book_analysis_targets"]
    assert "source_import_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "chinese_entity_alias_ledger" in pattern_pack["bible_enrichment_targets"]
    assert "stylometric_author_fingerprint_report" in pattern_pack["whole_book_analysis_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "source_format_import_manifest_hints" in digest
    assert "chinese_ner_alias_consistency_gate_hints" in digest
    assert "stylometric_author_fingerprint_gate_hints" in digest



def test_static_mode_contract_source_study_workspace_sources_map_to_generation_gates():
    assert "https://github.com/FURUYAN1234/story-maker" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/yuanbw2025/storyforge" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/dedyrio/novelwriter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/qq1375828505/AI-Fic-IDE" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("mode contract" in query.lower() and "style analyzer" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("masterworks" in query.lower() and "chapter beats" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("world model" in query.lower() and "style consistent" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("ai-fic-ide" in query.lower() and "history snapshots" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "FURUYAN1234/story-maker",
                "html_url": "https://github.com/FURUYAN1234/story-maker",
                "description": "Static story generator with output mode, visible creative axes, audience, ending style, narrator, source material, optional style analysis, selected-mode priority, mode contract and under-length rewrite handling.",
                "stargazers_count": 18,
                "license": None,
                "topics": ["story-generator", "creative-writing", "style-analysis"],
                "updated_at": "2026-06-10T14:29:00Z",
                "root_files": ["README.md", "package.json", "src", "vite.config.ts"],
            },
            {
                "full_name": "yuanbw2025/storyforge",
                "html_url": "https://github.com/yuanbw2025/storyforge",
                "description": "Offline browser AI writing studio with visible editable savable prompt templates, prompt workflows, IndexedDB, chunked import, three-layer memory, consistency checks, master study, masterWorks, masterChapterBeats, masterStyleMetrics and masterInsights that do not pollute creative data.",
                "stargazers_count": 101,
                "license": None,
                "topics": ["novel", "prompt-workflows", "offline"],
                "updated_at": "2026-06-10T13:25:52Z",
                "root_files": ["README.md", "CLAUDE.md", "docs", "package.json", "src"],
            },
            {
                "full_name": "dedyrio/novelwriter",
                "html_url": "https://github.com/dedyrio/novelwriter",
                "description": "AI story writer that imports existing stories, extracts characters relationships and world details, keeps a clear world model, applies story rules, preserves style consistent continuation, and ships Windows installer download links.",
                "stargazers_count": 0,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["novel", "ai-writing", "world-model"],
                "updated_at": "2026-06-10T11:56:49Z",
                "root_files": ["README.md", "LICENSE", "web", "docs", "Dockerfile"],
            },
            {
                "full_name": "qq1375828505/AI-Fic-IDE",
                "html_url": "https://github.com/qq1375828505/AI-Fic-IDE",
                "description": "Android native web novel writing IDE with character cards, setting cards, foreshadowing states, AI memory, cross-chapter global search replace, autosave, history snapshots, local models, MCP plugin marketplace, ADB, Root and accessibility surfaces.",
                "stargazers_count": 0,
                "license": {"spdx_id": "LGPL-3.0"},
                "topics": ["android", "webnovel", "ai-writing"],
                "updated_at": "2026-06-10T14:29:08Z",
                "root_files": ["README.md", "LICENSE", "app", "gradle", "AndroidManifest.xml"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T23:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "mode_contract_generation_gate" in candidates["FURUYAN1234/story-maker"]["absorbed_patterns"]
    assert "style_signature" in candidates["FURUYAN1234/story-maker"]["absorbed_patterns"]
    assert "source_study_method_bank_isolation_gate" in candidates["yuanbw2025/storyforge"]["absorbed_patterns"]
    assert "prompt_library" in candidates["yuanbw2025/storyforge"]["absorbed_patterns"]
    assert "world_state_tracking" in candidates["dedyrio/novelwriter"]["absorbed_patterns"]
    assert "style_signature" in candidates["dedyrio/novelwriter"]["absorbed_patterns"]
    assert "memory_snapshot_versioning" in candidates["qq1375828505/AI-Fic-IDE"]["absorbed_patterns"]
    assert "relationship_graph_global_replace_gate" in candidates["qq1375828505/AI-Fic-IDE"]["absorbed_patterns"]
    assert "mcp_server" in candidates["qq1375828505/AI-Fic-IDE"]["risk_flags"]
    assert "device_control" in candidates["qq1375828505/AI-Fic-IDE"]["risk_flags"]
    assert "docker" in candidates["dedyrio/novelwriter"]["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "mode_contract_generation_gate_hints" in pattern_pack
    assert "source_study_method_bank_isolation_gate_hints" in pattern_pack
    assert "generation_mode_contracts" in pattern_pack["bible_enrichment_targets"]
    assert "source_study_method_bank" in pattern_pack["bible_enrichment_targets"]
    assert "mode_contract_matrix" in pattern_pack["whole_book_analysis_targets"]
    assert "source_study_method_bank_report" in pattern_pack["whole_book_analysis_targets"]
    assert "mode_contract_axis_remap" in pattern_pack["inspired_mapping_targets"]
    assert "method_bank_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "mode_contract_generation_gate_hints" in digest
    assert "source_study_method_bank_isolation_gate_hints" in digest


def test_static_human_machine_batch_workspace_sources_map_to_continuation_gates():
    assert "https://github.com/leehong0704/ai-novel" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/wynnforthework/ai-novel-weaver" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/fuchen2020/BatchScribe" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/xy9144/flutter-novel-main" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/duoyang666/ai_novel" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("inline edit" in query.lower() and "ai polishing" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("hierarchical planning" in query.lower() and "memory weave" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("batch generation" in query.lower() and "homogeneity" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("本地数据" in query and "进度追踪" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "leehong0704/ai-novel",
                "html_url": "https://github.com/leehong0704/ai-novel",
                "description": "AI小说生成器 desktop tool for human-machine co-creation, 生成即起点, 微调见真章, AI polishing, precise modification, local memory and chapter generation.",
                "stargazers_count": 19,
                "license": {"spdx_id": "EPL-1.0"},
                "topics": ["ai-novel", "webnovel", "desktop"],
                "updated_at": "2026-06-09T20:28:53Z",
                "root_files": ["README.md", "LICENSE", "release/ai-novel.zip", "requirements.txt"],
            },
            {
                "full_name": "wynnforthework/ai-novel-weaver",
                "html_url": "https://github.com/wynnforthework/ai-novel-weaver",
                "description": "AI Novel Weaver web platform with orchestrator-driven generate validate improve loop, hierarchical planning from volume and arc to chapter, memory weave, one-click 拆书 and local deployment.",
                "stargazers_count": 36,
                "license": None,
                "topics": ["ai-novel", "orchestrator", "writing"],
                "updated_at": "2026-06-10T12:23:28Z",
                "root_files": ["README.md", "package.json", "src", "public"],
            },
            {
                "full_name": "fuchen2020/BatchScribe",
                "html_url": "https://github.com/fuchen2020/BatchScribe",
                "description": "BatchScribe Windows AI novel generator supports batch generation, continuation, same type creation, story type, style controls, prompt configuration, copy review and chapter memory.",
                "stargazers_count": 14,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["ai-writing", "novel", "windows"],
                "updated_at": "2026-06-06T03:06:07Z",
                "root_files": ["README.md", "README_EN.md", "LICENSE", "requirements.txt"],
            },
            {
                "full_name": "xy9144/flutter-novel-main",
                "html_url": "https://github.com/xy9144/flutter-novel-main",
                "description": "Flutter AI小说生成器 with outline, volume planning, range planning, chapter planning, auto continuation, progress tracking, homogeneity prompt revision, random title and random topic, local Ollama interface.",
                "stargazers_count": 63,
                "license": {"spdx_id": "MIT"},
                "topics": ["flutter", "ai-writing", "novel"],
                "updated_at": "2026-06-10T13:18:11Z",
                "root_files": ["README.md", "LICENSE", "pubspec.yaml", "android", "windows"],
            },
            {
                "full_name": "duoyang666/ai_novel",
                "html_url": "https://github.com/duoyang666/ai_novel",
                "description": "Chinese AI writing and knowledge-base app with local data, public download links, 自动升级 upgrade.zip, batch writing, continuation, 爽点, rhythm and chapter generation.",
                "stargazers_count": 726,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["ai-novel", "knowledge-base", "writing"],
                "updated_at": "2026-06-10T02:18:30Z",
                "root_files": ["README.md", "LICENSE", "group", "upgrade.zip"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T23:45:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "inline_human_machine_coauthoring_gate" in candidates["leehong0704/ai-novel"]["absorbed_patterns"]
    assert "binary_distribution" in candidates["leehong0704/ai-novel"]["risk_flags"]
    assert "hierarchical_orchestrator_generation_gate" in candidates["wynnforthework/ai-novel-weaver"]["absorbed_patterns"]
    assert "book_decomposition" in candidates["wynnforthework/ai-novel-weaver"]["absorbed_patterns"]
    assert "batch_continuation_progress_queue_gate" in candidates["fuchen2020/BatchScribe"]["absorbed_patterns"]
    assert "same_type_creation" in candidates["fuchen2020/BatchScribe"]["absorbed_patterns"]
    assert "homogeneity_prompt_variation_gate" in candidates["xy9144/flutter-novel-main"]["absorbed_patterns"]
    assert "local_author_data_boundary_gate" in candidates["xy9144/flutter-novel-main"]["absorbed_patterns"]
    assert "local_author_data_boundary_gate" in candidates["duoyang666/ai_novel"]["absorbed_patterns"]
    assert "auto_update" in candidates["duoyang666/ai_novel"]["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "inline_human_machine_coauthoring_gate_hints" in pattern_pack
    assert "hierarchical_orchestrator_generation_gate_hints" in pattern_pack
    assert "batch_continuation_progress_queue_gate_hints" in pattern_pack
    assert "homogeneity_prompt_variation_gate_hints" in pattern_pack
    assert "local_author_data_boundary_gate_hints" in pattern_pack
    assert "inline_revision_policy" in pattern_pack["bible_enrichment_targets"]
    assert "hierarchical_generation_plan" in pattern_pack["bible_enrichment_targets"]
    assert "batch_continuation_queue" in pattern_pack["bible_enrichment_targets"]
    assert "local_author_data_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "volume_arc_chapter_plan" in pattern_pack["whole_book_analysis_targets"]
    assert "inline_revision_span_remap" in pattern_pack["inspired_mapping_targets"]
    assert "variation_axis_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "inline_human_machine_coauthoring_gate_hints" in digest
    assert "hierarchical_orchestrator_generation_gate_hints" in digest
    assert "batch_continuation_progress_queue_gate_hints" in digest
    assert "homogeneity_prompt_variation_gate_hints" in digest
    assert "local_author_data_boundary_gate_hints" in digest



def test_static_local_prompt_draft_privacy_sources_map_to_workbench_gates():
    assert "https://github.com/Deng-m1/MaliangAINovalWriter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ponysb/91Writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/hezhengtao/MortalAINovel-AIWritingSystem-ai-" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/linnnn89/novel-agent-workbench" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/qnbs/StoryCraft-Studio" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("prompt preset" in query.lower() and "prompt variables" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("txt import" in query.lower() and "chapter outline" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("style dna" in query.lower() and "reference library" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("draft vs confirmed" in query.lower() and "metadata-only index" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "Deng-m1/MaliangAINovalWriter",
                "html_url": "https://github.com/Deng-m1/MaliangAINovalWriter",
                "description": "Maliang AI novel platform with txt import, chapter outline migration, prompt preset management, private API key pool, LLM observability, token cost traces, and knowledge extraction review.",
                "stargazers_count": 789,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["ainovel", "writer-tools"],
                "updated_at": "2026-04-15T09:09:38Z",
                "root_files": ["README.md", "LICENSE", "NOTICE", "deploy", "AINoval", "AINovalServer"],
            },
            {
                "full_name": "ponysb/91Writing",
                "html_url": "https://github.com/ponysb/91Writing",
                "description": "91Writing supports smart continuation with custom direction, prompt template categories, variable system, template import, usage stats, token cost management, local data and selective import export.",
                "stargazers_count": 1552,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-writing", "novel"],
                "updated_at": "2025-10-14T07:16:20Z",
                "root_files": ["README.md", "LICENSE", "Dockerfile", "docker-compose.yml", "package.json", "prompt.txt", "prompts-example.json"],
            },
            {
                "full_name": "hezhengtao/MortalAINovel-AIWritingSystem-ai-",
                "html_url": "https://github.com/hezhengtao/MortalAINovel-AIWritingSystem-ai-",
                "description": "MortalWrite local desktop AI novel assistant with local workspace, continuation, polishing, style imitation, character cards, relationship graph, inspiration brainstorming, and book-decomposition knowledge base that analyzes writing DNA.",
                "stargazers_count": 19,
                "license": None,
                "topics": ["ai-novel", "desktop"],
                "updated_at": "2025-12-29T03:10:05Z",
                "root_files": ["README.md", "README_EN.md", "requirements.txt", "MortalWrite.spec", "run.py", "main.py"],
            },
            {
                "full_name": "linnnn89/novel-agent-workbench",
                "html_url": "https://github.com/linnnn89/novel-agent-workbench",
                "description": "Local AI novel workbench with Memory Bank, world settings, chapter drafts, AI review, revision requests, rewrite candidates, candidate comparison, confirmed chapters, provider gates and audit metadata.",
                "stargazers_count": 1,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["ai-writing", "chinese-novel", "desktop-app"],
                "updated_at": "2026-06-01T15:45:30Z",
                "root_files": ["README.md", "LICENSE", "BUILD_NovelAgentWorkbench.bat", "START_NovelAgentWorkbench.cmd", "pyproject.toml", "scripts", "src", "tests"],
            },
            {
                "full_name": "qnbs/StoryCraft-Studio",
                "html_url": "https://github.com/qnbs/StoryCraft-Studio",
                "description": "Offline-first AI writing studio with IndexedDB local storage, PWA and desktop mode, privacy-preserving index, metadata-only cross-project search, template remixing, encrypted API keys, WebLLM, ONNX and Transformers local AI fallbacks.",
                "stargazers_count": 2,
                "license": {"spdx_id": "MIT"},
                "topics": ["offline-first", "ai-writing", "novel-writing", "pwa", "local-ai"],
                "updated_at": "2026-06-10T12:49:30Z",
                "root_files": ["README.md", "LICENSE", "Dockerfile", "package.json", "pnpm-lock.yaml", "src-tauri", "public", "register-sw.ts"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T23:58:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}

    assert "prompt_preset_variable_library_gate" in candidates["Deng-m1/MaliangAINovalWriter"]["absorbed_patterns"]
    assert "imported_manuscript_migration_outline_gate" in candidates["Deng-m1/MaliangAINovalWriter"]["absorbed_patterns"]
    assert "provider_key_surface" in candidates["Deng-m1/MaliangAINovalWriter"]["risk_flags"]
    assert "prompt_preset_variable_library_gate" in candidates["ponysb/91Writing"]["absorbed_patterns"]
    assert "provider_key_surface" in candidates["ponysb/91Writing"]["risk_flags"]
    assert "style_dna_reference_library_gate" in candidates["hezhengtao/MortalAINovel-AIWritingSystem-ai-"]["absorbed_patterns"]
    assert "draft_candidate_promotion_gate" in candidates["linnnn89/novel-agent-workbench"]["absorbed_patterns"]
    assert "windows_script" in candidates["linnnn89/novel-agent-workbench"]["risk_flags"]
    assert "privacy_preserving_local_index_gate" in candidates["qnbs/StoryCraft-Studio"]["absorbed_patterns"]
    assert "browser_storage_surface" in candidates["qnbs/StoryCraft-Studio"]["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "prompt_preset_variable_library_gate_hints" in pattern_pack
    assert "imported_manuscript_migration_outline_gate_hints" in pattern_pack
    assert "style_dna_reference_library_gate_hints" in pattern_pack
    assert "draft_candidate_promotion_gate_hints" in pattern_pack
    assert "privacy_preserving_local_index_gate_hints" in pattern_pack
    assert "prompt_preset_registry" in pattern_pack["bible_enrichment_targets"]
    assert "imported_manuscript_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "style_dna_reference_library" in pattern_pack["bible_enrichment_targets"]
    assert "confirmed_chapter_promotion_rules" in pattern_pack["bible_enrichment_targets"]
    assert "metadata_only_search_scope" in pattern_pack["bible_enrichment_targets"]
    assert "draft_review_rewrite_candidates" in pattern_pack["whole_book_analysis_targets"]
    assert "local_metadata_index_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "style_dna_abstraction_remap" in pattern_pack["inspired_mapping_targets"]
    assert "draft_candidate_promotion_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("draft candidate" in hint.lower() for hint in pattern_pack["continuation_prompt_hints"])
    assert any("manuscript plaintext" in hint.lower() for hint in pattern_pack["privacy_preserving_local_index_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "prompt_preset_variable_library_gate_hints" in digest
    assert "imported_manuscript_migration_outline_gate_hints" in digest
    assert "style_dna_reference_library_gate_hints" in digest
    assert "draft_candidate_promotion_gate_hints" in digest
    assert "privacy_preserving_local_index_gate_hints" in digest


def test_static_ai_auto_novel_source_maps_to_splitter_prompt_preview_gates():
    assert "https://github.com/wfcz10086/AI-automatically-generates-novels" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("智能拆书" in query and "章节分割" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("最终提示词" in query and "右键润色" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "wfcz10086/AI-automatically-generates-novels",
                "html_url": "https://github.com/wfcz10086/AI-automatically-generates-novels",
                "description": (
                    "Chinese AI novel assistant with smart book decomposition, chapter splitting, "
                    "custom拆书提示词, per-chapter analysis, export data, final prompt preview, "
                    "right-click selected_text polishing, prompt variables, shift+L shortcut entries, "
                    "title and summary generation, API keys, /gen and /gen2 model endpoints."
                ),
                "stargazers_count": 881,
                "forks_count": 180,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["ai-writing", "novel", "prompt"],
                "updated_at": "2025-07-01T01:34:39Z",
                "root_files": [
                    "README.md",
                    "LICENSE",
                    "requirements.txt",
                    "static/book-splitter.js",
                    "static/prompt-editor.js",
                    "templates/index.html",
                ],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T13:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    candidate = candidates["wfcz10086/AI-automatically-generates-novels"]
    assert "chapter_split_deconstruction_export_gate" in candidate["absorbed_patterns"]
    assert "final_prompt_preview_span_revision_gate" in candidate["absorbed_patterns"]
    assert "prompt_preset_variable_library_gate" in candidate["absorbed_patterns"]
    assert "provider_key_surface" in candidate["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "chapter_split_deconstruction_export_gate_hints" in pattern_pack
    assert "final_prompt_preview_span_revision_gate_hints" in pattern_pack
    assert "chapter_splitter_prompt_policy" in pattern_pack["bible_enrichment_targets"]
    assert "final_prompt_preview_policy" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_split_deconstruction_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "final_prompt_preview_audit" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_split_deconstruction_remap" in pattern_pack["inspired_mapping_targets"]
    assert "final_prompt_preview_span_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("export manifest" in hint.lower() for hint in pattern_pack["continuation_prompt_hints"])
    assert any("approval packet" in hint.lower() for hint in pattern_pack["final_prompt_preview_span_revision_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "chapter_split_deconstruction_export_gate_hints" in digest
    assert "final_prompt_preview_span_revision_gate_hints" in digest


def test_static_book_beta_reader_sources_map_to_context_review_and_research_gates():
    assert "https://github.com/dlintin/sidekickwriter" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/gennitdev/ai-beta-reader-frontend" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/gennitdev/ai-beta-reader-backend" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/wesleyscholl/book-generator" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("chapter descriptions" in query.lower() and "previous chapters" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("ai beta reader" in query.lower() and "previous chapter summaries" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("citation styles" in query.lower() and "research" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "dlintin/sidekickwriter",
                "html_url": "https://github.com/dlintin/sidekickwriter",
                "description": "AI-powered book writing platform with guided mode, pro mode, writing style selection, character development, chapter-by-chapter outline generation, chapter descriptions aware of previous chapters for continuity, full book generation, real-time streaming text, inline editing, regenerate specific chapters without losing the rest, AI research engine, web search integration, academic databases and citation styles.",
                "stargazers_count": 106,
                "license": None,
                "topics": ["ai-writing", "book-writing", "novel"],
                "updated_at": "2026-06-10T09:30:00Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "gennitdev/ai-beta-reader-frontend",
                "html_url": "https://github.com/gennitdev/ai-beta-reader-frontend",
                "description": "AI Beta Reader frontend for managing books and chapters, rich markdown editing, smart chapter summaries that track plot points, characters and key events, contextual AI reviews that use summaries of previous chapters as context, multiple review styles, sql.js local storage, Google Drive OAuth cloud sync and OpenAI review services.",
                "stargazers_count": 3,
                "license": None,
                "topics": ["beta-reader", "novel", "vue"],
                "updated_at": "2026-06-09T14:20:00Z",
                "root_files": ["README.md", "package.json", "src", "vite.config.ts"],
            },
            {
                "full_name": "gennitdev/ai-beta-reader-backend",
                "html_url": "https://github.com/gennitdev/ai-beta-reader-backend",
                "description": "AI Beta Reader Express REST API for getting AI-generated feedback on chapters with context from previous chapter summaries, OpenAI Responses API, Auth0 JWT, PostgreSQL database, OPENAI_API_KEY and DATABASE_URL configuration.",
                "stargazers_count": 1,
                "license": None,
                "topics": ["beta-reader", "express", "openai"],
                "updated_at": "2026-06-08T08:12:00Z",
                "root_files": ["README.md", "package.json", ".env.example", "src"],
            },
            {
                "full_name": "wesleyscholl/book-generator",
                "html_url": "https://github.com/wesleyscholl/book-generator",
                "description": "Autonomous book creation pipeline using shell scripts and helper tools to pick topics, generate detailed outlines, generate extend and edit chapters, run quality and plagiarism checks, assemble complete manuscript with title pages table of contents copyright pages appendices acknowledgements, and export EPUB PDF for Amazon KDP with configurable provider API keys.",
                "stargazers_count": 84,
                "license": None,
                "topics": ["book-generator", "ai-writing", "publishing"],
                "updated_at": "2026-06-09T11:45:00Z",
                "root_files": ["README.md", "requirements.txt", "scripts/generate.sh", "scripts/publish.sh"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-10T23:59:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "chapter_description_continuity_bridge_gate" in candidates["dlintin/sidekickwriter"]["absorbed_patterns"]
    assert "selective_streaming_regeneration_gate" in candidates["dlintin/sidekickwriter"]["absorbed_patterns"]
    assert "research_citation_boundary_gate" in candidates["dlintin/sidekickwriter"]["absorbed_patterns"]
    assert "beta_reader_summary_context_gate" in candidates["gennitdev/ai-beta-reader-frontend"]["absorbed_patterns"]
    assert "cloud_sync_oauth_surface" in candidates["gennitdev/ai-beta-reader-frontend"]["risk_flags"]
    assert "beta_reader_summary_context_gate" in candidates["gennitdev/ai-beta-reader-backend"]["absorbed_patterns"]
    assert "provider_key_surface" in candidates["gennitdev/ai-beta-reader-backend"]["risk_flags"]
    assert "research_citation_boundary_gate" in candidates["wesleyscholl/book-generator"]["absorbed_patterns"]
    assert "shell_script" in candidates["wesleyscholl/book-generator"]["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "chapter_description_continuity_bridge_gate_hints" in pattern_pack
    assert "selective_streaming_regeneration_gate_hints" in pattern_pack
    assert "research_citation_boundary_gate_hints" in pattern_pack
    assert "beta_reader_summary_context_gate_hints" in pattern_pack
    assert "chapter_description_contracts" in pattern_pack["bible_enrichment_targets"]
    assert "research_citation_policy" in pattern_pack["bible_enrichment_targets"]
    assert "beta_reader_feedback_styles" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_description_context_bridge" in pattern_pack["whole_book_analysis_targets"]
    assert "previous_summary_review_context" in pattern_pack["whole_book_analysis_targets"]
    assert "research_citation_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_description_continuity_remap" in pattern_pack["inspired_mapping_targets"]
    assert "research_source_citation_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("previous chapter summaries" in hint.lower() for hint in pattern_pack["beta_reader_summary_context_gate_hints"])
    assert any("specific chapter" in hint.lower() for hint in pattern_pack["selective_streaming_regeneration_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "chapter_description_continuity_bridge_gate_hints" in digest
    assert "selective_streaming_regeneration_gate_hints" in digest
    assert "research_citation_boundary_gate_hints" in digest
    assert "beta_reader_summary_context_gate_hints" in digest


def test_static_style_continuation_sources_map_to_audit_and_verification_gates():
    assert "https://github.com/Boundless-Fang/StyleSync-Novel" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/eluckydog/DreamQuill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/304769384-png/fanqie-novel-skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/leistung/novel-write" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/VerifiedOrganic/spindle" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/daveremy/edword" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/adameya2004-oss/CraftEngine" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("style vocabulary" in query.lower() and "world cards" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("pure-prompt" in query.lower() and "wrap-up mode" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("delta extraction" in query.lower() and "chain-of-verification" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("22-book" in query.lower() and "style preset" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "Boundless-Fang/StyleSync-Novel",
                "html_url": "https://github.com/Boundless-Fang/StyleSync-Novel",
                "description": "Chinese StyleSync-Novel prototype for AI novel creation with style analysis, vocabulary library, worldbuilding extraction, character card extraction, setting completion, chapter outline generation, body generation, chapter-local modification, prompt injection tuning, DeepSeek API key and SiliconFlow API key.",
                "stargazers_count": 5,
                "license": None,
                "topics": ["novel", "style-imitation", "ai-writing"],
                "updated_at": "2026-06-08T16:42:35Z",
                "root_files": ["README.md", "requirements.txt", ".env.example"],
            },
            {
                "full_name": "eluckydog/DreamQuill",
                "html_url": "https://github.com/eluckydog/DreamQuill",
                "description": "Pure-prompt novel writing agent with no install and no API key. It measures prompt-only capability boundaries, continuity guard, setting cards, 10 chapter stress test, 5000-6000 character wrap-up mode, comfort zone decay and limits of prompt-only systems.",
                "stargazers_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["prompt", "novel", "style-imitation"],
                "updated_at": "2026-05-28T14:18:50Z",
                "root_files": ["README.md", "LICENSE", "prompts/startup.md"],
            },
            {
                "full_name": "304769384-png/fanqie-novel-skill",
                "html_url": "https://github.com/304769384-png/fanqie-novel-skill",
                "description": "Fanqie novel skill with AI de-flavoring by replacement, progress tracking dashboard, minimum audit set, chapter checks, battle scene audit, dialogue ratio monitor, cycle pattern detection every 5 chapters, full audit every 10 chapters, chapter summaries and style guide.",
                "stargazers_count": 14,
                "license": None,
                "topics": ["webnovel", "skill", "ai-writing"],
                "updated_at": "2026-06-10T08:40:19Z",
                "root_files": ["README.md", "outline.md", "chapter_summaries.md", "style_guide.md"],
            },
            {
                "full_name": "leistung/novel-write",
                "html_url": "https://github.com/leistung/novel-write",
                "description": "LangChain and LangGraph AI novel writing assistant with Architect, Writer, Consistency Checker and Author agents. Supports creation, next chapter continuation, chapter rewrite, rewrite from chapter n, outline change impact analysis, reject retry up to 3 times, score below 80 returning to planning, current state and pending hooks.",
                "stargazers_count": 5,
                "license": None,
                "topics": ["novel", "langgraph", "multi-agent"],
                "updated_at": "2026-05-17T08:06:26Z",
                "root_files": ["README.md", "requirements.txt", ".env.example"],
            },
            {
                "full_name": "VerifiedOrganic/spindle",
                "html_url": "https://github.com/VerifiedOrganic/spindle",
                "description": "Local-first MCP fiction planning companion with story bible, context packet assembly, recent chapter summaries, narrative promises, branch and save points, restore earlier scene versions, continuity and consistency checks, dual-persona editorial reviews, canonical fact extraction and EPUB export.",
                "stargazers_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["mcp", "story-bible", "novel"],
                "updated_at": "2026-06-04T01:51:38Z",
                "root_files": ["README.md", "LICENSE", "Cargo.toml"],
            },
            {
                "full_name": "daveremy/edword",
                "html_url": "https://github.com/daveremy/edword",
                "description": "AI-powered editorial analysis for book manuscripts using memory-augmented extraction with chain-of-verification. Builds index chapter by chapter, extracts structured facts from current chapter, deterministic accumulation into a knowledge graph, verifies candidate findings with targeted questions, continuity checking, codex validation and incremental processing.",
                "stargazers_count": 0,
                "license": None,
                "topics": ["manuscript", "analysis", "mcp"],
                "updated_at": "2026-01-27T04:16:05Z",
                "root_files": ["README.md", "pyproject.toml"],
            },
            {
                "full_name": "adameya2004-oss/CraftEngine",
                "html_url": "https://github.com/adameya2004-oss/CraftEngine",
                "description": "SillyTavern extension that scores writing quality using metrics from 22 published novels, smart rewriter below threshold, style presets from 22-book statistical analysis, imported book style learning, character voice profiles, rhythm, sensory density, slop detection, dialogue, repetition and ending quality metrics.",
                "stargazers_count": 0,
                "license": None,
                "topics": ["style", "quality", "rewriter"],
                "updated_at": "2026-03-26T10:11:19Z",
                "root_files": ["README.md", "manifest.json"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T00:45:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "style_vocab_world_card_extraction_gate" in candidates["Boundless-Fang/StyleSync-Novel"]["absorbed_patterns"]
    assert "provider_key_surface" in candidates["Boundless-Fang/StyleSync-Novel"]["risk_flags"]
    assert "prompt_only_decay_ceiling_gate" in candidates["eluckydog/DreamQuill"]["absorbed_patterns"]
    assert "serial_platform_minimum_audit_gate" in candidates["304769384-png/fanqie-novel-skill"]["absorbed_patterns"]
    assert "multi_agent_reject_retry_review_gate" in candidates["leistung/novel-write"]["absorbed_patterns"]
    assert "story_bible_context_packet_branch_gate" in candidates["VerifiedOrganic/spindle"]["absorbed_patterns"]
    assert "mcp_server" in candidates["VerifiedOrganic/spindle"]["risk_flags"]
    assert "memory_augmented_delta_verification_gate" in candidates["daveremy/edword"]["absorbed_patterns"]
    assert "statistical_style_benchmark_rewrite_gate" in candidates["adameya2004-oss/CraftEngine"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "style_vocab_world_card_extraction_gate_hints" in pattern_pack
    assert "multi_agent_reject_retry_review_gate_hints" in pattern_pack
    assert "prompt_only_decay_ceiling_gate_hints" in pattern_pack
    assert "serial_platform_minimum_audit_gate_hints" in pattern_pack
    assert "story_bible_context_packet_branch_gate_hints" in pattern_pack
    assert "memory_augmented_delta_verification_gate_hints" in pattern_pack
    assert "statistical_style_benchmark_rewrite_gate_hints" in pattern_pack
    assert "style_vocabulary_library" in pattern_pack["bible_enrichment_targets"]
    assert "minimum_chapter_audit_set" in pattern_pack["bible_enrichment_targets"]
    assert "delta_fact_index" in pattern_pack["bible_enrichment_targets"]
    assert "story_bible_context_packet" in pattern_pack["bible_enrichment_targets"]
    assert "statistical_style_benchmark_policy" in pattern_pack["bible_enrichment_targets"]
    assert "pure_prompt_decay_report" in pattern_pack["whole_book_analysis_targets"]
    assert "multi_agent_retry_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "delta_extraction_verification_report" in pattern_pack["whole_book_analysis_targets"]
    assert "style_benchmark_rewrite_report" in pattern_pack["whole_book_analysis_targets"]
    assert "style_vocabulary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "statistical_style_benchmark_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("deterministic accumulation" in hint.lower() for hint in pattern_pack["memory_augmented_delta_verification_gate_hints"])
    assert any("22-book" in hint.lower() for hint in pattern_pack["statistical_style_benchmark_rewrite_gate_hints"])
    assert any("prompt-only" in hint.lower() for hint in pattern_pack["prompt_only_decay_ceiling_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "style_vocab_world_card_extraction_gate_hints" in digest
    assert "multi_agent_reject_retry_review_gate_hints" in digest
    assert "prompt_only_decay_ceiling_gate_hints" in digest
    assert "serial_platform_minimum_audit_gate_hints" in digest
    assert "story_bible_context_packet_branch_gate_hints" in digest
    assert "memory_augmented_delta_verification_gate_hints" in digest
    assert "statistical_style_benchmark_rewrite_gate_hints" in digest


def test_static_webnovel_dashboard_skill_publish_sources_map_to_workflow_gates():
    assert "https://github.com/per-hap-s/webnovel-writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/imerzzhu/ai-novel-writing-skills" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/dyrcjqlgcj/webnovel-director" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Saemer2023/webnovel-writer-opencode" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/yuzhoubazhu/novel-studio" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("web dashboard" in query.lower() and ".webnovel" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("webnovel skills" in query.lower() and "hot memes" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("truth file" in query.lower() and "relationship_graph" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("one-click publish" in query.lower() and "browser automation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("multi-work" in query.lower() and "manual continuation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "per-hap-s/webnovel-writing",
                "html_url": "https://github.com/per-hap-s/webnovel-writing",
                "description": "AI-assisted long-form webnovel workbench with Web Dashboard, task orchestration for init plan write review repair query resume, quality review panels, .webnovel state directory, revision backups, reports, Windows bat and PowerShell launchers, consistency continuity OOC pacing and reader pull checks.",
                "stargazers_count": 1,
                "license": None,
                "topics": ["webnovel", "dashboard", "ai-writing"],
                "updated_at": "2026-06-10T10:20:00Z",
                "root_files": ["README.md", "tools/Start-Webnovel-Writer.bat", "tools/Launch-Webnovel-Dashboard.ps1"],
            },
            {
                "full_name": "imerzzhu/ai-novel-writing-skills",
                "html_url": "https://github.com/imerzzhu/ai-novel-writing-skills",
                "description": "MIT public Codex Skills package for Chinese webnovel writing with webnovel skills for topic planning, outlining, chapter drafting, continuation, expansion, rewrite, story logic review, prose polish, final manuscript checks, webnovel-hot-memes, platform voice, comment-section energy, webnovel-female-radar emotional rhythm, relationship tension and open source boundary excluding private rank snapshots.",
                "stargazers_count": 2,
                "license": {"spdx_id": "MIT"},
                "topics": ["codex-skills", "webnovel", "ai-writing"],
                "updated_at": "2026-06-11T07:45:00Z",
                "root_files": ["README.md", "LICENSE", "skills/webnovel-write/SKILL.md"],
            },
            {
                "full_name": "dyrcjqlgcj/webnovel-director",
                "html_url": "https://github.com/dyrcjqlgcj/webnovel-director",
                "description": "Chinese structured webnovel scheduler that splits material selection, outline, writing, review and writeback into independent phases. Supports OpenClaw and Claude Code skill install, provider API key configuration, dashboard P0 project setup P1 overview P2 outline management P3 writing pipeline, L2 L3 review, task packages, Truth files including current_state resource_ledger relationship_graph hooks.",
                "stargazers_count": 9,
                "license": {"spdx_id": "MIT"},
                "topics": ["webnovel", "openclaw", "dashboard"],
                "updated_at": "2026-06-10T18:12:00Z",
                "root_files": ["README.md", "SKILL.md", "requirements.txt"],
            },
            {
                "full_name": "Saemer2023/webnovel-writer-opencode",
                "html_url": "https://github.com/Saemer2023/webnovel-writer-opencode",
                "description": "OpenCode long-form webnovel AI creation system with RAG context management, 10 writing skills, 6 dedicated agents, quality checks for consistency OOC pleasure density pacing and reader pull, 37 templates, dashboard, one-click Fanqie publish, browser automation login, HTTP API upload, upstream read-only source plus sync-upstream.ps1, install.py interactive installer.",
                "stargazers_count": 18,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["opencode", "webnovel", "rag"],
                "updated_at": "2026-06-09T09:30:00Z",
                "root_files": ["README.md", "LICENSE", "CLAUDE.md", "install.py", "sync-upstream.ps1"],
            },
            {
                "full_name": "yuzhoubazhu/novel-studio",
                "html_url": "https://github.com/yuzhoubazhu/novel-studio",
                "description": "AI Agent platform for novel creators solving character setting collapse, plot memory loss and rigid AI-style wording. Supports multi-work management, writing style imitation, manual continuation and automatic continuation modes for long-form writing.",
                "stargazers_count": 0,
                "license": None,
                "topics": ["novel", "agent", "style-imitation"],
                "updated_at": "2026-06-10T05:20:00Z",
                "root_files": ["README.md"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T01:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "dashboard_task_quality_resume_gate" in candidates["per-hap-s/webnovel-writing"]["absorbed_patterns"]
    assert "powershell_script" in candidates["per-hap-s/webnovel-writing"]["risk_flags"]
    assert "webnovel_skill_suite_release_boundary_gate" in candidates["imerzzhu/ai-novel-writing-skills"]["absorbed_patterns"]
    assert "platform_voice_meme_emotion_gate" in candidates["imerzzhu/ai-novel-writing-skills"]["absorbed_patterns"]
    assert "skill_install_surface" in candidates["imerzzhu/ai-novel-writing-skills"]["risk_flags"]
    assert "truth_file_phase_dashboard_gate" in candidates["dyrcjqlgcj/webnovel-director"]["absorbed_patterns"]
    assert "provider_key_surface" in candidates["dyrcjqlgcj/webnovel-director"]["risk_flags"]
    assert "platform_publish_automation_boundary_gate" in candidates["Saemer2023/webnovel-writer-opencode"]["absorbed_patterns"]
    assert "platform_publish_automation_surface" in candidates["Saemer2023/webnovel-writer-opencode"]["risk_flags"]
    assert "python_installer" in candidates["Saemer2023/webnovel-writer-opencode"]["risk_flags"]
    assert "multi_work_style_imitation_mode_gate" in candidates["yuzhoubazhu/novel-studio"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "dashboard_task_quality_resume_gate_hints" in pattern_pack
    assert "webnovel_skill_suite_release_boundary_gate_hints" in pattern_pack
    assert "truth_file_phase_dashboard_gate_hints" in pattern_pack
    assert "platform_publish_automation_boundary_gate_hints" in pattern_pack
    assert "multi_work_style_imitation_mode_gate_hints" in pattern_pack
    assert "webnovel_task_orchestration_state" in pattern_pack["bible_enrichment_targets"]
    assert "skill_suite_release_boundary" in pattern_pack["bible_enrichment_targets"]
    assert "truth_file_canon_ledgers" in pattern_pack["bible_enrichment_targets"]
    assert "publish_automation_safety_policy" in pattern_pack["bible_enrichment_targets"]
    assert "multi_work_style_imitation_modes" in pattern_pack["bible_enrichment_targets"]
    assert "dashboard_resume_quality_report" in pattern_pack["whole_book_analysis_targets"]
    assert "skill_suite_stage_coverage_report" in pattern_pack["whole_book_analysis_targets"]
    assert "truth_file_writeback_report" in pattern_pack["whole_book_analysis_targets"]
    assert "publish_automation_boundary_report" in pattern_pack["whole_book_analysis_targets"]
    assert "multi_work_style_mode_report" in pattern_pack["whole_book_analysis_targets"]
    assert "style_imitation_mode_remap" in pattern_pack["inspired_mapping_targets"]
    assert "truth_file_relationship_graph_remap" in pattern_pack["inspired_mapping_targets"]
    assert any(".webnovel" in hint.lower() for hint in pattern_pack["dashboard_task_quality_resume_gate_hints"])
    assert any("truth file" in hint.lower() for hint in pattern_pack["truth_file_phase_dashboard_gate_hints"])
    assert any("one-click publish" in hint.lower() for hint in pattern_pack["platform_publish_automation_boundary_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "dashboard_task_quality_resume_gate_hints" in digest
    assert "webnovel_skill_suite_release_boundary_gate_hints" in digest
    assert "truth_file_phase_dashboard_gate_hints" in digest
    assert "platform_publish_automation_boundary_gate_hints" in digest
    assert "multi_work_style_imitation_mode_gate_hints" in digest


def test_static_prose_pov_phase_snapshot_sources_map_to_source_study_gates():
    assert "https://github.com/prosegrinder/python-prosegrinder" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/oxinabox/NovelPerspective" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/d-wwei/great-writer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/vulogov/blackInkhaven" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("point of view" in query.lower() and "dialogue" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("6-phase pipeline" in query.lower() and "4-pass polish" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("semantic index" in query.lower() and "versioned snapshots" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "prosegrinder/python-prosegrinder",
                "html_url": "https://github.com/prosegrinder/python-prosegrinder",
                "description": (
                    "Prose text counter for novels with word count, sentence count, paragraph count, "
                    "syllable count, point of view, dialogue, narrative and readability scores."
                ),
                "stargazers_count": 20,
                "forks_count": 2,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["prose", "readability", "fiction", "text-analysis"],
                "updated_at": "2026-06-11T02:00:00Z",
                "root_files": ["README.md", "pyproject.toml", "LICENSE"],
            },
            {
                "full_name": "oxinabox/NovelPerspective",
                "html_url": "https://github.com/oxinabox/NovelPerspective",
                "description": (
                    "NovelPerspective identifies point of view characters in ebook chapters and can "
                    "include or exclude character story-lines for rereading."
                ),
                "stargazers_count": 46,
                "forks_count": 8,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "point-of-view", "machine-learning"],
                "updated_at": "2026-06-11T02:05:00Z",
                "root_files": ["README.md", "LICENSE.md", "proto", "serve"],
            },
            {
                "full_name": "d-wwei/great-writer",
                "html_url": "https://github.com/d-wwei/great-writer",
                "description": (
                    "Great Writer is a bilingual writing system for AI agents with a 6-phase pipeline, "
                    "9 writing modes, 15 writing principles and 4-pass polish to remove AI traces."
                ),
                "stargazers_count": 470,
                "forks_count": 31,
                "license": {"spdx_id": "MIT"},
                "topics": ["writing", "ai-agent", "prompting"],
                "updated_at": "2026-06-11T02:10:00Z",
                "root_files": ["README.md", "README.zh.md", "LICENSE"],
            },
            {
                "full_name": "vulogov/blackInkhaven",
                "html_url": "https://github.com/vulogov/blackInkhaven",
                "description": (
                    "Inkhaven is a terminal book-writing app with hierarchical Typst manuscript nodes, "
                    "local semantic index, DuckDB metadata, AI assistant, versioned snapshots, backups, "
                    "lexicon books for characters and places, and LLM provider routing."
                ),
                "stargazers_count": 10,
                "forks_count": 0,
                "license": {"spdx_id": "Unlicense"},
                "topics": ["book-writing", "semantic-search", "local-first"],
                "updated_at": "2026-06-11T02:15:00Z",
                "root_files": ["README.md", "Cargo.toml", "Documentation", "LICENSE"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T02:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "prose_metric_pov_dialogue_gate" in candidates["prosegrinder/python-prosegrinder"]["absorbed_patterns"]
    assert "pov_character_thread_filter_gate" in candidates["oxinabox/NovelPerspective"]["absorbed_patterns"]
    assert "agent_writing_phase_polish_gate" in candidates["d-wwei/great-writer"]["absorbed_patterns"]
    assert "hierarchical_semantic_snapshot_workspace_gate" in candidates["vulogov/blackInkhaven"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "prose_metric_baseline_policy" in pattern_pack["bible_enrichment_targets"]
    assert "pov_character_thread_map" in pattern_pack["bible_enrichment_targets"]
    assert "phase_polish_mode_policy" in pattern_pack["bible_enrichment_targets"]
    assert "hierarchical_text_node_snapshot_policy" in pattern_pack["bible_enrichment_targets"]
    assert "pov_dialogue_narrative_metric_report" in pattern_pack["whole_book_analysis_targets"]
    assert "pov_character_thread_filter_report" in pattern_pack["whole_book_analysis_targets"]
    assert "phase_polish_ai_trace_report" in pattern_pack["whole_book_analysis_targets"]
    assert "hierarchical_semantic_snapshot_report" in pattern_pack["whole_book_analysis_targets"]
    assert "prose_metric_pov_dialogue_gate_hints" in pattern_pack
    assert "pov_character_thread_filter_gate_hints" in pattern_pack
    assert "agent_writing_phase_polish_gate_hints" in pattern_pack
    assert "hierarchical_semantic_snapshot_workspace_gate_hints" in pattern_pack
    assert "pov_dialogue_metric_remap" in pattern_pack["inspired_mapping_targets"]
    assert "phase_polish_mode_remap" in pattern_pack["inspired_mapping_targets"]
    assert "hierarchical_snapshot_namespace_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "prose_metric_pov_dialogue_gate_hints" in digest
    assert "pov_character_thread_filter_gate_hints" in digest
    assert "agent_writing_phase_polish_gate_hints" in digest
    assert "hierarchical_semantic_snapshot_workspace_gate_hints" in digest


def test_static_book_writing_graph_rights_vscode_sources_map_to_workspace_gates():
    assert "https://github.com/lhfer/codex-novel-to-comic-studio" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/yosrikhiari/Versatile" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/okeylanders/prose-minion-vscode" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/wwessex/Writer1" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("rights gate" in query.lower() and "visual bible" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("indexeddb" in query.lower() and "story network" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("vscode" in query.lower() and "prose analysis" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "lhfer/codex-novel-to-comic-studio",
                "html_url": "https://github.com/lhfer/codex-novel-to-comic-studio",
                "description": (
                    "Codex Novel-to-Comic Studio turns EPUB/TXT novels into comic packages through "
                    "a rights gate, source parsing, narrative bible, visual bible, page scripts, QC, "
                    "PDF and CBZ export."
                ),
                "stargazers_count": 2,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["codex", "novel", "comic", "story-bible"],
                "updated_at": "2026-06-11T03:00:00Z",
                "root_files": ["README.md", "README.zh-CN.md", "LICENSE", "docs"],
            },
            {
                "full_name": "yosrikhiari/Versatile",
                "html_url": "https://github.com/yosrikhiari/Versatile",
                "description": (
                    "Versatile is a local fiction writing assistant with IndexedDB autosave, flow sessions, "
                    "Ollama AI Spark and Polish tools, story generator, story bible, timeline, scene cards, "
                    "and visual story network graph."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["fiction-writing", "ollama", "story-bible"],
                "updated_at": "2026-06-11T03:05:00Z",
                "root_files": ["README.md", "package.json", "src"],
            },
            {
                "full_name": "okeylanders/prose-minion-vscode",
                "html_url": "https://github.com/okeylanders/prose-minion-vscode",
                "description": (
                    "Prose Minion VS Code extension provides AI-powered prose analysis, professional prose metrics, "
                    "contextual manuscript analysis, chapter analysis, story bible and source analysis inside VS Code."
                ),
                "stargazers_count": 19,
                "forks_count": 1,
                "license": {"spdx_id": "NOASSERTION"},
                "topics": ["vscode-extension", "creative-writing", "prose-analysis"],
                "updated_at": "2026-06-11T03:10:00Z",
                "root_files": ["README.md", "package.json", "LICENSE", "src"],
            },
            {
                "full_name": "wwessex/Writer1",
                "html_url": "https://github.com/wwessex/Writer1",
                "description": (
                    "DraftHarbour Studio is an offline/online novel word processor PWA with chapter-isolated editing, "
                    "IndexedDB autosave, optional sync, version history, diff previews, restore, and DOCX/PDF/RTF export."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["novel", "pwa", "offline"],
                "updated_at": "2026-06-11T03:15:00Z",
                "root_files": ["README.md", "package.json", "index.html"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T03:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "rights_first_adaptation_pipeline_gate" in candidates["lhfer/codex-novel-to-comic-studio"]["absorbed_patterns"]
    assert "local_flow_story_graph_workspace_gate" in candidates["yosrikhiari/Versatile"]["absorbed_patterns"]
    assert "editor_context_prose_analysis_gate" in candidates["okeylanders/prose-minion-vscode"]["absorbed_patterns"]
    assert "offline_chapter_revision_export_gate" in candidates["wwessex/Writer1"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "rights_clearance_adaptation_policy" in pattern_pack["bible_enrichment_targets"]
    assert "flow_session_story_graph_policy" in pattern_pack["bible_enrichment_targets"]
    assert "editor_context_analysis_scope_policy" in pattern_pack["bible_enrichment_targets"]
    assert "offline_chapter_document_boundary" in pattern_pack["bible_enrichment_targets"]
    assert "rights_source_adaptation_gate_report" in pattern_pack["whole_book_analysis_targets"]
    assert "local_flow_story_graph_report" in pattern_pack["whole_book_analysis_targets"]
    assert "editor_context_prose_analysis_report" in pattern_pack["whole_book_analysis_targets"]
    assert "offline_revision_export_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "rights_first_adaptation_pipeline_gate_hints" in pattern_pack
    assert "local_flow_story_graph_workspace_gate_hints" in pattern_pack
    assert "editor_context_prose_analysis_gate_hints" in pattern_pack
    assert "offline_chapter_revision_export_gate_hints" in pattern_pack
    assert "rights_adaptation_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "local_flow_story_graph_remap" in pattern_pack["inspired_mapping_targets"]
    assert "editor_context_analysis_remap" in pattern_pack["inspired_mapping_targets"]
    assert "offline_chapter_export_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "rights_first_adaptation_pipeline_gate_hints" in digest
    assert "local_flow_story_graph_workspace_gate_hints" in digest
    assert "editor_context_prose_analysis_gate_hints" in digest
    assert "offline_chapter_revision_export_gate_hints" in digest


def test_static_ai_book_writer_product_prompt_sources_map_to_continuation_gates():
    assert "https://github.com/adamwlarson/ai-book-writer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/302ai/302_novel_writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/christiandarkin/creative-writers-toolkit" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("autogen" in query.lower() and "memory keeper" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("302.ai" in query.lower() and "ai-assisted writing" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("character outlines" in query.lower() and "story synopses" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "adamwlarson/ai-book-writer",
                "html_url": "https://github.com/adamwlarson/ai-book-writer",
                "description": (
                    "AutoGen Book Generator uses collaborative AI agents: Story Planner, World Builder, "
                    "Memory Keeper, Writer, Editor, and Outline Creator to generate outlines, chapters, "
                    "continuity and structured narratives."
                ),
                "stargazers_count": 20,
                "forks_count": 2,
                "license": None,
                "topics": ["autogen", "book", "multi-agent", "writing"],
                "updated_at": "2026-06-11T04:00:00Z",
                "root_files": ["README.md", "requirements.txt", "src"],
            },
            {
                "full_name": "302ai/302_novel_writing",
                "html_url": "https://github.com/302ai/302_novel_writing",
                "description": (
                    "302.AI Novel Writing is an open-source AI-assisted writing product with manual editing, "
                    "AI writing sidebar, diverse writing styles, intelligent plot planning, real-time editing, "
                    "cover generation, online service and self-deploy options."
                ),
                "stargazers_count": 52,
                "forks_count": 11,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["ai-writing", "novel", "nextjs"],
                "updated_at": "2026-06-11T04:05:00Z",
                "root_files": ["README.md", "README_zh.md", "LICENSE", "package.json"],
            },
            {
                "full_name": "christiandarkin/creative-writers-toolkit",
                "html_url": "https://github.com/christiandarkin/creative-writers-toolkit",
                "description": (
                    "Creative Writers' Toolkit explores GPT-3 creative writing flows that create character outlines, "
                    "story synopses, treatments, plot outlines and scene lists for stories, screenplays and novels."
                ),
                "stargazers_count": 16,
                "forks_count": 3,
                "license": None,
                "topics": ["creative-writing", "gpt3", "story"],
                "updated_at": "2026-06-11T04:10:00Z",
                "root_files": ["README.md", "characters", "synopsis", "scenes"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T04:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "multi_agent_outline_continuity_review_gate" in candidates["adamwlarson/ai-book-writer"]["absorbed_patterns"]
    assert "hosted_ai_sidebar_product_boundary_gate" in candidates["302ai/302_novel_writing"]["absorbed_patterns"]
    assert "creative_scaffold_prompt_sequence_gate" in candidates["christiandarkin/creative-writers-toolkit"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "multi_agent_role_boundary_policy" in pattern_pack["bible_enrichment_targets"]
    assert "hosted_ai_product_boundary_policy" in pattern_pack["bible_enrichment_targets"]
    assert "creative_scaffold_sequence_policy" in pattern_pack["bible_enrichment_targets"]
    assert "multi_agent_outline_continuity_review_report" in pattern_pack["whole_book_analysis_targets"]
    assert "hosted_ai_sidebar_boundary_report" in pattern_pack["whole_book_analysis_targets"]
    assert "creative_scaffold_sequence_report" in pattern_pack["whole_book_analysis_targets"]
    assert "multi_agent_outline_continuity_review_gate_hints" in pattern_pack
    assert "hosted_ai_sidebar_product_boundary_gate_hints" in pattern_pack
    assert "creative_scaffold_prompt_sequence_gate_hints" in pattern_pack
    assert "agent_role_continuity_review_remap" in pattern_pack["inspired_mapping_targets"]
    assert "hosted_ai_sidebar_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "creative_scaffold_sequence_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "multi_agent_outline_continuity_review_gate_hints" in digest
    assert "hosted_ai_sidebar_product_boundary_gate_hints" in digest
    assert "creative_scaffold_prompt_sequence_gate_hints" in digest


def test_static_story_system_script_translation_sources_map_to_adaptation_gates():
    assert "https://github.com/bybren-llc/story-systems-template" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/1want2beaQuant/ai-novel2script" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Shirochi-stack/Glossarion" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/oodadoudou/Transoria" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("writers' room" in query.lower() and "fountain" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("novel to screenplay" in query.lower() and "yaml" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("glossary" in query.lower() and "epub rebuilding" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "bybren-llc/story-systems-template",
                "html_url": "https://github.com/bybren-llc/story-systems-template",
                "description": (
                    "Story Systems Template is a creative project template for screenplays and novels. "
                    "It provides an 11-person AI team, writers' room stop authority, shared knowledge, "
                    "multi-AI harness, Fountain export, scene review, GUI and upstream sync."
                ),
                "stargazers_count": 35,
                "forks_count": 2,
                "license": {"spdx_id": "MIT"},
                "topics": ["screenplay", "novel", "multi-ai", "fountain"],
                "updated_at": "2026-06-11T05:00:00Z",
                "root_files": ["README.md", "LICENSE", "package.json", "agents"],
            },
            {
                "full_name": "1want2beaQuant/ai-novel2script",
                "html_url": "https://github.com/1want2beaQuant/ai-novel2script",
                "description": (
                    "AI 小说转剧本工具 converts 3+ chapter novels to structured screenplay YAML, "
                    "acts, scenes, action, dialogue, transitions, structure_map, story_bible, "
                    "adaptation_report, coverage_report, quality gates and Fountain export."
                ),
                "stargazers_count": 2,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "screenplay", "yaml", "fountain"],
                "updated_at": "2026-06-11T05:05:00Z",
                "root_files": ["README.md", "LICENSE", "pyproject.toml", "src"],
            },
            {
                "full_name": "Shirochi-stack/Glossarion",
                "html_url": "https://github.com/Shirochi-stack/Glossarion",
                "description": (
                    "Glossarion is an AI-powered translation suite for light novels, web novels, manga and documents "
                    "with contextual translation, glossary system, quality assurance, EPUB rebuilding, 40+ providers, "
                    "duplicate detection and GUI review controls."
                ),
                "stargazers_count": 80,
                "forks_count": 7,
                "license": {"spdx_id": "MIT"},
                "topics": ["translation", "glossary", "epub", "novel"],
                "updated_at": "2026-06-11T05:10:00Z",
                "root_files": ["README.md", "LICENSE", "requirements.txt", "assets"],
            },
            {
                "full_name": "oodadoudou/Transoria",
                "html_url": "https://github.com/oodadoudou/Transoria",
                "description": (
                    "Transoria is a desktop novel translation app with term extraction, term review, translation, "
                    "proofreading, batch text replacement, EPUB tools, task IDs, resume/retry, low-confidence sorting, "
                    "source-residue labels and copyright/right-use warnings."
                ),
                "stargazers_count": 30,
                "forks_count": 1,
                "license": None,
                "topics": ["novel-translation", "glossary", "desktop", "epub"],
                "updated_at": "2026-06-11T05:15:00Z",
                "root_files": ["README.md", "pyproject.toml", "frontend", "backend"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T05:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "writers_room_stop_authority_gate" in candidates["bybren-llc/story-systems-template"]["absorbed_patterns"]
    assert "novel_to_screenplay_structure_coverage_gate" in candidates["1want2beaQuant/ai-novel2script"]["absorbed_patterns"]
    assert "translation_glossary_context_qa_gate" in candidates["Shirochi-stack/Glossarion"]["absorbed_patterns"]
    assert "desktop_translation_batch_replacement_boundary_gate" in candidates["oodadoudou/Transoria"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "writers_room_role_stop_policy" in pattern_pack["bible_enrichment_targets"]
    assert "screenplay_structure_coverage_policy" in pattern_pack["bible_enrichment_targets"]
    assert "translation_glossary_context_policy" in pattern_pack["bible_enrichment_targets"]
    assert "batch_replacement_translation_boundary" in pattern_pack["bible_enrichment_targets"]
    assert "writers_room_stop_review_report" in pattern_pack["whole_book_analysis_targets"]
    assert "novel_to_screenplay_structure_map_report" in pattern_pack["whole_book_analysis_targets"]
    assert "translation_glossary_context_qa_report" in pattern_pack["whole_book_analysis_targets"]
    assert "desktop_batch_replacement_boundary_report" in pattern_pack["whole_book_analysis_targets"]
    assert "writers_room_stop_authority_gate_hints" in pattern_pack
    assert "novel_to_screenplay_structure_coverage_gate_hints" in pattern_pack
    assert "translation_glossary_context_qa_gate_hints" in pattern_pack
    assert "desktop_translation_batch_replacement_boundary_gate_hints" in pattern_pack
    assert "writers_room_role_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "screenplay_adaptation_structure_remap" in pattern_pack["inspired_mapping_targets"]
    assert "translation_glossary_namespace_remap" in pattern_pack["inspired_mapping_targets"]
    assert "batch_replacement_boundary_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "writers_room_stop_authority_gate_hints" in digest
    assert "novel_to_screenplay_structure_coverage_gate_hints" in digest
    assert "translation_glossary_context_qa_gate_hints" in digest
    assert "desktop_translation_batch_replacement_boundary_gate_hints" in digest


def test_factual_grounding_long_context_sources_map_to_verification_gates():
    assert "https://github.com/shmsw25/FActScore" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/potsawee/selfcheckgpt" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/amazon-science/RefChecker" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/THUDM/LongBench" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/NVIDIA/RULER" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/gkamradt/LLMTest_NeedleInAHaystack" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/booydar/babilong" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/OpenBMB/InfiniteBench" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/princeton-nlp/HELMET" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("factscore" in query.lower() and "atomic facts" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("selfcheckgpt" in query.lower() and "hallucination" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("refchecker" in query.lower() and "claim" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("needle" in query.lower() and "haystack" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("babilong" in query.lower() and "distributed facts" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "shmsw25/FActScore",
                "html_url": "https://github.com/shmsw25/FActScore",
                "description": (
                    "FActScore evaluates factuality of long-form generation by decomposing biographies "
                    "into atomic facts and estimating factual precision using retrieval and support decisions."
                ),
                "stargazers_count": 441,
                "forks_count": 58,
                "license": {"spdx_id": "MIT"},
                "topics": ["factuality", "long-form-generation", "atomic-facts"],
                "updated_at": "2025-04-13T20:41:02Z",
                "root_files": ["README.md", "LICENSE", "factscore", "setup.py"],
            },
            {
                "full_name": "potsawee/selfcheckgpt",
                "html_url": "https://github.com/potsawee/selfcheckgpt",
                "description": (
                    "SelfCheckGPT detects hallucinations with zero-resource black-box self-consistency checks "
                    "across sampled passages, sentence-level scores and factual consistency signals."
                ),
                "stargazers_count": 619,
                "forks_count": 80,
                "license": {"spdx_id": "MIT"},
                "topics": ["hallucination-detection", "self-consistency", "llm"],
                "updated_at": "2024-06-26T16:17:02Z",
                "root_files": ["README.md", "LICENSE", "selfcheckgpt", "setup.py"],
            },
            {
                "full_name": "amazon-science/RefChecker",
                "html_url": "https://github.com/amazon-science/RefChecker",
                "description": (
                    "RefChecker performs fine-grained hallucination detection by extracting claims and "
                    "checking claim consistency against reference documents with benchmark and evaluation tools."
                ),
                "stargazers_count": 380,
                "forks_count": 39,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["hallucination", "claim-checking", "factual-consistency"],
                "updated_at": "2025-11-10T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "refchecker", "requirements.txt"],
            },
            {
                "full_name": "THUDM/LongBench",
                "html_url": "https://github.com/THUDM/LongBench",
                "description": (
                    "LongBench is a benchmark for bilingual and multitask long context understanding with "
                    "retrieval, QA, summarization and long-context evaluation."
                ),
                "stargazers_count": 4200,
                "forks_count": 420,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["long-context", "benchmark", "retrieval"],
                "updated_at": "2026-01-15T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "requirements.txt", "pred.py"],
            },
            {
                "full_name": "NVIDIA/RULER",
                "html_url": "https://github.com/NVIDIA/RULER",
                "description": (
                    "RULER evaluates long context language models with synthetic tasks, needle in a haystack, "
                    "variable tracking, aggregation, QA and multi-hop retrieval stress tests."
                ),
                "stargazers_count": 1700,
                "forks_count": 180,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["long-context", "needle-in-a-haystack", "benchmark"],
                "updated_at": "2026-06-05T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "scripts", "requirements.txt"],
            },
            {
                "full_name": "gkamradt/LLMTest_NeedleInAHaystack",
                "html_url": "https://github.com/gkamradt/LLMTest_NeedleInAHaystack",
                "description": (
                    "Needle In A Haystack tests whether an LLM can retrieve a hidden fact from long context "
                    "at different context lengths and insertion depths."
                ),
                "stargazers_count": 3100,
                "forks_count": 380,
                "license": {"spdx_id": "MIT"},
                "topics": ["needle-in-a-haystack", "long-context", "retrieval"],
                "updated_at": "2024-11-20T00:00:00Z",
                "root_files": ["README.md", "LICENSE.txt", "main.py"],
            },
            {
                "full_name": "booydar/babilong",
                "html_url": "https://github.com/booydar/babilong",
                "description": (
                    "BABILong evaluates models on long context question answering where distributed facts "
                    "must be found and reasoned over across long-form documents."
                ),
                "stargazers_count": 320,
                "forks_count": 30,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["long-context", "qa", "distributed-facts"],
                "updated_at": "2025-09-12T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "babilong"],
            },
            {
                "full_name": "OpenBMB/InfiniteBench",
                "html_url": "https://github.com/OpenBMB/InfiniteBench",
                "description": (
                    "InfiniteBench evaluates extremely long context models on retrieval, QA, synthetic tasks, "
                    "code, math and summarization across very large context windows."
                ),
                "stargazers_count": 1500,
                "forks_count": 130,
                "license": {"spdx_id": "Apache-2.0"},
                "topics": ["long-context", "benchmark", "qa"],
                "updated_at": "2025-10-10T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "src"],
            },
            {
                "full_name": "princeton-nlp/HELMET",
                "html_url": "https://github.com/princeton-nlp/HELMET",
                "description": (
                    "HELMET is a holistic evaluation suite for long-context language models with retrieval, "
                    "question answering, summarization, multi-hop and benchmark aggregation."
                ),
                "stargazers_count": 540,
                "forks_count": 45,
                "license": {"spdx_id": "MIT"},
                "topics": ["long-context", "benchmark", "evaluation"],
                "updated_at": "2025-03-22T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "helmet"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T06:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "atomic_fact_precision_gate" in candidates["shmsw25/FActScore"]["absorbed_patterns"]
    assert "self_consistency_hallucination_gate" in candidates["potsawee/selfcheckgpt"]["absorbed_patterns"]
    assert "reference_claim_verification_gate" in candidates["amazon-science/RefChecker"]["absorbed_patterns"]
    assert "long_context_benchmark_task_suite_gate" in candidates["THUDM/LongBench"]["absorbed_patterns"]
    assert "needle_haystack_context_recall_gate" in candidates["NVIDIA/RULER"]["absorbed_patterns"]
    assert "needle_haystack_context_recall_gate" in candidates["gkamradt/LLMTest_NeedleInAHaystack"]["absorbed_patterns"]
    assert "distributed_fact_chain_recall_gate" in candidates["booydar/babilong"]["absorbed_patterns"]
    assert "long_context_benchmark_task_suite_gate" in candidates["OpenBMB/InfiniteBench"]["absorbed_patterns"]
    assert "long_context_benchmark_task_suite_gate" in candidates["princeton-nlp/HELMET"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "atomic_fact_ledger_policy" in pattern_pack["bible_enrichment_targets"]
    assert "self_consistency_hallucination_review_policy" in pattern_pack["bible_enrichment_targets"]
    assert "reference_claim_grounding_policy" in pattern_pack["bible_enrichment_targets"]
    assert "long_context_recall_probe_policy" in pattern_pack["bible_enrichment_targets"]
    assert "distributed_fact_chain_policy" in pattern_pack["bible_enrichment_targets"]
    assert "atomic_fact_precision_report" in pattern_pack["whole_book_analysis_targets"]
    assert "self_consistency_hallucination_report" in pattern_pack["whole_book_analysis_targets"]
    assert "reference_claim_verification_report" in pattern_pack["whole_book_analysis_targets"]
    assert "long_context_recall_stress_report" in pattern_pack["whole_book_analysis_targets"]
    assert "distributed_fact_chain_recall_report" in pattern_pack["whole_book_analysis_targets"]
    assert "atomic_fact_precision_gate_hints" in pattern_pack
    assert "self_consistency_hallucination_gate_hints" in pattern_pack
    assert "reference_claim_verification_gate_hints" in pattern_pack
    assert "long_context_benchmark_task_suite_gate_hints" in pattern_pack
    assert "needle_haystack_context_recall_gate_hints" in pattern_pack
    assert "distributed_fact_chain_recall_gate_hints" in pattern_pack
    assert "atomic_fact_precision_remap" in pattern_pack["inspired_mapping_targets"]
    assert "reference_claim_grounding_remap" in pattern_pack["inspired_mapping_targets"]
    assert "long_context_recall_probe_remap" in pattern_pack["inspired_mapping_targets"]
    assert "distributed_fact_chain_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "atomic_fact_precision_gate_hints" in digest
    assert "self_consistency_hallucination_gate_hints" in digest
    assert "reference_claim_verification_gate_hints" in digest
    assert "long_context_benchmark_task_suite_gate_hints" in digest
    assert "needle_haystack_context_recall_gate_hints" in digest
    assert "distributed_fact_chain_recall_gate_hints" in digest



def test_chinese_webnovel_platform_kb_and_resilient_engine_sources_map_to_retention_gates():
    assert "https://github.com/TianHengZhuang/Chinese-WebNovel-Master" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/tance-mang/chinese-webnovel-skills" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/yaopushen/webnovel-kb" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/ohh-000/longform-novel-engine" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Jackela/Novel-Engine" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("platform-specific reader preferences" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("????" in query and "????" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("custom caching protocol" in query.lower() and "graceful degradation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("reader simulator" in query.lower() and "quality gate" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "TianHengZhuang/Chinese-WebNovel-Master",
                "html_url": "https://github.com/TianHengZhuang/Chinese-WebNovel-Master",
                "description": (
                    "Chinese WebNovel Master is a multi-agent Chinese web fiction workflow with platform-specific "
                    "reader preferences, platform suitability for Tomato Novel, Qidian, Feilu and Jinjiang, "
                    "commercial storytelling workflows, suspense hook systems, retention optimization frameworks, "
                    "platform-specific tags, titles, synopsis and launch strategy."
                ),
                "stargazers_count": 2,
                "forks_count": 0,
                "license": None,
                "topics": ["webnovel", "chinese-fiction", "writing"],
                "updated_at": "2026-05-29T04:27:43Z",
                "root_files": ["README.md", "SKILL.md", "assets"],
            },
            {
                "full_name": "tance-mang/chinese-webnovel-skills",
                "html_url": "https://github.com/tance-mang/chinese-webnovel-skills",
                "description": (
                    "WebNovel Studio provides 27 Chinese webnovel skills for topic selection, inspiration, outline, "
                    "golden opening, cheat system, character setup, prose expansion, ????, rhythm labeling, "
                    "????, de-AI polish, submission review, platform trends, fanfic compliance and export setup."
                ),
                "stargazers_count": 2,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["claude-code", "webnovel", "skills"],
                "updated_at": "2026-06-10T14:44:23Z",
                "root_files": ["README.md", "LICENSE", "skills", "cli"],
            },
            {
                "full_name": "yaopushen/webnovel-kb",
                "html_url": "https://github.com/yaopushen/webnovel-kb",
                "description": (
                    "WebNovel Knowledge Base is a ????????? MCP ??? with TXT import, semantic search, "
                    "BM25, hybrid search, rerank, plot pattern extraction, writing template extraction, style analysis, "
                    "chapter outline extraction, classic chapter imitation rewrite, OAuth PKCE and async tasks."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": None,
                "topics": ["mcp", "knowledge-base", "webnovel"],
                "updated_at": "2026-06-10T13:55:51Z",
                "root_files": ["README.md", "requirements.txt", ".env.example", "webnovel_kb"],
            },
            {
                "full_name": "ohh-000/longform-novel-engine",
                "html_url": "https://github.com/ohh-000/longform-novel-engine",
                "description": (
                    "Longform Novel Engine coordinates Director, Opening Audition, Writer executing the Director blueprint, "
                    "Critic auditing blueprint adherence, Patch Reviser, Reader Simulator for confusion boredom payoff and "
                    "next-chapter pull, Archivist, State Validator, strict-quality gates, hidden secrets, open foreshadowing, "
                    "world rules and corrupted long-running story state prevention."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["long-context", "multi-agent", "fiction"],
                "updated_at": "2026-05-17T09:49:13Z",
                "root_files": ["README.md", "pyproject.toml", "engine", "tests"],
            },
            {
                "full_name": "Jackela/Novel-Engine",
                "html_url": "https://github.com/Jackela/Novel-Engine",
                "description": (
                    "Novel Engine is a local-first novel writing engine with complete chapter Markdown source of truth, "
                    "sidecar JSON evidence, artifacts/runs/{run_id}, events, raw model output, custom caching protocol "
                    "that avoids duplicate API calls, thread-safe concurrency, graceful degradation, circuit breaker, "
                    "comprehensive logging, review report and manuscript export."
                ),
                "stargazers_count": 6,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "local-first", "multi-agent"],
                "updated_at": "2026-06-09T05:59:07Z",
                "root_files": ["README.md", "pyproject.toml", "frontend", "tests"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T07:40:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "platform_kb_retention_strategy_gate" in candidates["TianHengZhuang/Chinese-WebNovel-Master"]["absorbed_patterns"]
    assert "chapter_end_hook_retention_ladder_gate" in candidates["TianHengZhuang/Chinese-WebNovel-Master"]["absorbed_patterns"]
    assert "platform_kb_retention_strategy_gate" in candidates["tance-mang/chinese-webnovel-skills"]["absorbed_patterns"]
    assert "chapter_end_hook_retention_ladder_gate" in candidates["tance-mang/chinese-webnovel-skills"]["absorbed_patterns"]
    assert "webnovel_kb_mcp_runtime_boundary_gate" in candidates["yaopushen/webnovel-kb"]["absorbed_patterns"]
    assert "long_context_role_boundary_state_validation_gate" in candidates["ohh-000/longform-novel-engine"]["absorbed_patterns"]
    assert "chapter_end_hook_retention_ladder_gate" in candidates["ohh-000/longform-novel-engine"]["absorbed_patterns"]
    assert "agent_cache_concurrency_recovery_gate" in candidates["Jackela/Novel-Engine"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "platform_reader_preference_matrix" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_end_hook_ladder" in pattern_pack["bible_enrichment_targets"]
    assert "webnovel_kb_runtime_boundary_policy" in pattern_pack["bible_enrichment_targets"]
    assert "generation_cache_idempotency_policy" in pattern_pack["bible_enrichment_targets"]
    assert "long_context_role_visibility_policy" in pattern_pack["bible_enrichment_targets"]
    assert "platform_reader_preference_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_end_hook_ladder_report" in pattern_pack["whole_book_analysis_targets"]
    assert "webnovel_kb_boundary_report" in pattern_pack["whole_book_analysis_targets"]
    assert "agent_cache_idempotency_report" in pattern_pack["whole_book_analysis_targets"]
    assert "long_context_role_boundary_report" in pattern_pack["whole_book_analysis_targets"]
    assert "platform_kb_retention_strategy_gate_hints" in pattern_pack
    assert "chapter_end_hook_retention_ladder_gate_hints" in pattern_pack
    assert "webnovel_kb_mcp_runtime_boundary_gate_hints" in pattern_pack
    assert "agent_cache_concurrency_recovery_gate_hints" in pattern_pack
    assert "long_context_role_boundary_state_validation_gate_hints" in pattern_pack
    assert "platform_reader_preference_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chapter_end_hook_ladder_remap" in pattern_pack["inspired_mapping_targets"]
    assert "webnovel_kb_namespace_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "agent_cache_idempotency_remap" in pattern_pack["inspired_mapping_targets"]
    assert "long_context_role_visibility_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "platform_kb_retention_strategy_gate_hints" in digest
    assert "chapter_end_hook_retention_ladder_gate_hints" in digest
    assert "webnovel_kb_mcp_runtime_boundary_gate_hints" in digest
    assert "agent_cache_concurrency_recovery_gate_hints" in digest
    assert "long_context_role_boundary_state_validation_gate_hints" in digest


def test_memory_tribunal_checkpoint_sources_map_to_governance_gates():
    assert "https://github.com/Mochocyang/QMAI" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/knoai/knowrite" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/AxolDad/novelist" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Nicholas-Yu/InkPilot" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/guohei/fanqie-plus" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/armchairfuturist-code/novel-writer-harness" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("chapter ingestion" in query.lower() and "context package" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("parallel critic tribunal" in query.lower() and "issue tracking" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("fitness dashboard" in query.lower() and "temporal truth database" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("golden three chapters" in query.lower() and "platform compliance" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("outline structural validator" in query.lower() and "debate court" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("ai is the amplifier" in query.lower() and "ai-taste detection" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "Mochocyang/QMAI",
                "html_url": "https://github.com/Mochocyang/QMAI",
                "description": (
                    "QMAI chapter ingestion workflow with context package, token budget, hybrid retrieval, chapter summary, "
                    "ending hook, relationship changes, foreshadowing, graph nodes and memory units with human confirmation."
                ),
                "stargazers_count": 478,
                "forks_count": 0,
                "license": None,
                "topics": ["ai-writing", "novel", "memory"],
                "updated_at": "2026-06-11T00:00:00Z",
                "root_files": ["README.md", "LICENSE", "releases"],
            },
            {
                "full_name": "knoai/knowrite",
                "html_url": "https://github.com/knoai/knowrite",
                "description": (
                    "Knowrite uses Temporal Truth Database, Author Fingerprint, RAG Memory, Fitness dashboard, "
                    "five-dimensional fitness, Automated Prompt Evolution, strict industrial-grade review and trace debugger."
                ),
                "stargazers_count": 15,
                "forks_count": 0,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["ai-writing", "novel", "rag"],
                "updated_at": "2026-06-11T00:00:00Z",
                "root_files": ["README.md", "package.json", "docker-compose.yml"],
            },
            {
                "full_name": "AxolDad/novelist",
                "html_url": "https://github.com/AxolDad/novelist",
                "description": (
                    "Novelist has SQLite memory core, world state, arcs, characters, Parallel Critic Tribunal, "
                    "agentic tribunal, prose redundancy arc critic agents, vote on every draft and Beads issue tracking."
                ),
                "stargazers_count": 2,
                "forks_count": 0,
                "license": None,
                "topics": ["streamlit", "novel", "multi-agent"],
                "updated_at": "2026-06-11T00:00:00Z",
                "root_files": ["README.md", "requirements.txt", "app.py"],
            },
            {
                "full_name": "Nicholas-Yu/InkPilot",
                "html_url": "https://github.com/Nicholas-Yu/InkPilot",
                "description": (
                    "InkPilot says AI is the amplifier not the voice, AI 80% + Human 20%, human-ai collaboration, "
                    "final decisions are yours, consistency checking, AI-taste detection and foreshadowing tracker."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["obsidian", "fiction-writing"],
                "updated_at": "2026-06-11T00:00:00Z",
                "root_files": ["README.md", "manifest.json"],
            },
            {
                "full_name": "guohei/fanqie-plus",
                "html_url": "https://github.com/guohei/fanqie-plus",
                "description": (
                    "Fanqie/Tomato-style webnovel workflow with golden three chapters, 8w, 10w, 15w checkpoints, "
                    "platform compliance, 10-chapter consistency audits, pacing ledger and Fanqie-ready plain text."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": None,
                "topics": ["fanqie", "webnovel", "skill"],
                "updated_at": "2026-06-11T00:00:00Z",
                "root_files": ["README.md", "install.sh", "skills"],
            },
            {
                "full_name": "armchairfuturist-code/novel-writer-harness",
                "html_url": "https://github.com/armchairfuturist-code/novel-writer-harness",
                "description": (
                    "Novel writer harness with outline structural validator, character coverage, foreshadowing completeness, "
                    "emotional arc progression, beat density, information boundaries, structured change declarations, "
                    "---CHANGES--- JSON, 12 categories of state transitions and debate court."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["novel", "storyforge", "outline"],
                "updated_at": "2026-06-11T00:00:00Z",
                "root_files": ["README.md", "prompts", "requirements.txt"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T08:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "chapter_memory_ingestion_context_budget_gate" in candidates["Mochocyang/QMAI"]["absorbed_patterns"]
    assert "human_ai_decision_authority_gate" in candidates["Mochocyang/QMAI"]["absorbed_patterns"]
    assert "prompt_evolution_fitness_governance_gate" in candidates["knoai/knowrite"]["absorbed_patterns"]
    assert "parallel_critic_tribunal_issue_gate" in candidates["AxolDad/novelist"]["absorbed_patterns"]
    assert "human_ai_decision_authority_gate" in candidates["Nicholas-Yu/InkPilot"]["absorbed_patterns"]
    assert "fanqie_checkpoint_compliance_audit_gate" in candidates["guohei/fanqie-plus"]["absorbed_patterns"]
    assert "outline_validator_change_declaration_gate" in candidates["armchairfuturist-code/novel-writer-harness"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "chapter_memory_ingestion_policy" in pattern_pack["bible_enrichment_targets"]
    assert "human_ai_decision_authority_policy" in pattern_pack["bible_enrichment_targets"]
    assert "critic_tribunal_role_policy" in pattern_pack["bible_enrichment_targets"]
    assert "prompt_evolution_fitness_policy" in pattern_pack["bible_enrichment_targets"]
    assert "fanqie_checkpoint_compliance_policy" in pattern_pack["bible_enrichment_targets"]
    assert "outline_validator_change_declaration_policy" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_ingestion_memory_report" in pattern_pack["whole_book_analysis_targets"]
    assert "parallel_critic_tribunal_report" in pattern_pack["whole_book_analysis_targets"]
    assert "prompt_evolution_fitness_report" in pattern_pack["whole_book_analysis_targets"]
    assert "fanqie_checkpoint_compliance_report" in pattern_pack["whole_book_analysis_targets"]
    assert "outline_structural_validator_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_memory_ingestion_context_budget_gate_hints" in pattern_pack
    assert "human_ai_decision_authority_gate_hints" in pattern_pack
    assert "parallel_critic_tribunal_issue_gate_hints" in pattern_pack
    assert "prompt_evolution_fitness_governance_gate_hints" in pattern_pack
    assert "fanqie_checkpoint_compliance_audit_gate_hints" in pattern_pack
    assert "outline_validator_change_declaration_gate_hints" in pattern_pack
    assert "chapter_memory_context_remap" in pattern_pack["inspired_mapping_targets"]
    assert "human_ai_authority_remap" in pattern_pack["inspired_mapping_targets"]
    assert "critic_tribunal_issue_remap" in pattern_pack["inspired_mapping_targets"]
    assert "prompt_fitness_evolution_remap" in pattern_pack["inspired_mapping_targets"]
    assert "fanqie_checkpoint_strategy_remap" in pattern_pack["inspired_mapping_targets"]
    assert "outline_change_declaration_remap" in pattern_pack["inspired_mapping_targets"]
    assert "author decision" in " ".join(pattern_pack["human_ai_decision_authority_gate_hints"]).lower()
    assert "trace debugger" in " ".join(pattern_pack["prompt_evolution_fitness_governance_gate_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "chapter_memory_ingestion_context_budget_gate_hints" in digest
    assert "human_ai_decision_authority_gate_hints" in digest
    assert "parallel_critic_tribunal_issue_gate_hints" in digest
    assert "prompt_evolution_fitness_governance_gate_hints" in digest
    assert "fanqie_checkpoint_compliance_audit_gate_hints" in digest
    assert "outline_validator_change_declaration_gate_hints" in digest


def test_deconstruction_platform_memory_and_codex_sources_map_to_intake_gates():
    assert "https://github.com/QQ-L-XX/novel-deconstruct" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/d3nnywong/qidian-mcp-server" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/KanishkaV25/StorySync" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/senjinthedragon/Smart-Memory" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/astrapi69/bibliogon" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/rxb123ahuan/codexwriteskill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("novel deconstruction" in query.lower() and "scene-level deconstruction" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("qidian" in query.lower() and "chapter structure" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("memory context budget" in query.lower() and "activation triggers" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("@-mentions" in query.lower() and "appearance tracker" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("story.md" in query.lower() and ".codex-story" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "QQ-L-XX/novel-deconstruct",
                "html_url": "https://github.com/QQ-L-XX/novel-deconstruct",
                "description": (
                    "Novel Deconstruction AI拆书 skill with scene-level deep deconstruction, chapter-by-chapter "
                    "quantitative scan, 18-chapter structured report, McKee, Xu Rongzhe, Fanqie URL input, "
                    "font decoding, API capture and OCR dependencies."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "deconstruction", "writing-research"],
                "updated_at": "2026-06-11T08:30:00Z",
                "root_files": ["README.md", "LICENSE", "requirements.txt"],
            },
            {
                "full_name": "d3nnywong/qidian-mcp-server",
                "html_url": "https://github.com/d3nnywong/qidian-mcp-server",
                "description": (
                    "Qidian MCP server for rankings, book details, qidian_scan_ranking, qidian_chapter_structure, "
                    "free chapters, qidian_deconstruct, market research and ANTHROPIC_API_KEY."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": None,
                "topics": ["qidian", "mcp", "webnovel"],
                "updated_at": "2026-04-20T03:32:26Z",
                "root_files": ["README.md", "server.py", "pyproject.toml"],
            },
            {
                "full_name": "KanishkaV25/StorySync",
                "html_url": "https://github.com/KanishkaV25/StorySync",
                "description": (
                    "StorySync continuity assistant for fiction writers with story bible generation, structured memory facts, "
                    "semantic retrieval, ChromaDB vector memory, continuity checking and rewrite assistance."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["fiction", "rag", "continuity"],
                "updated_at": "2026-06-09T19:24:54Z",
                "root_files": ["README.md", "requirements.txt", ".env.example"],
            },
            {
                "full_name": "senjinthedragon/Smart-Memory",
                "html_url": "https://github.com/senjinthedragon/Smart-Memory",
                "description": (
                    "Smart Memory extension with long-term memory, session memory, short-term memory, memory context budget, "
                    "activation triggers, fact retirement, retired and replaced facts, entity state, relationship history, "
                    "scene history, story arcs and rolling summaries."
                ),
                "stargazers_count": 20,
                "forks_count": 0,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["sillytavern", "memory", "story"],
                "updated_at": "2026-06-08T11:11:42Z",
                "root_files": ["README.md", "LICENSE", "package.json", "manifest.json"],
            },
            {
                "full_name": "astrapi69/bibliogon",
                "html_url": "https://github.com/astrapi69/bibliogon",
                "description": (
                    "Bibliogon book authoring platform with Story Bible, @-mentions, auto-detect, link automatically, "
                    "appearance tracker, Arc View swim-lane timeline, entity disappears warnings, absence gap checks, "
                    "continuity polylines and Story Bible Markdown export."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["book", "story-bible", "authoring"],
                "updated_at": "2026-06-10T17:38:16Z",
                "root_files": ["README.md", "LICENSE", "package.json"],
            },
            {
                "full_name": "rxb123ahuan/codexwriteskill",
                "html_url": "https://github.com/rxb123ahuan/codexwriteskill",
                "description": (
                    "Codex-readable story workspace with STORY.md, .codex-story rules, tracking files, story-long-analyze, "
                    "story-short-analyze, story-long-scan, story-short-scan and Codex Skills installer commands."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["codex", "skills", "novel"],
                "updated_at": "2026-05-16T16:28:01Z",
                "root_files": ["README.md", "LICENSE", "skills"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T09:00:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "scene_deconstruction_theory_report_gate" in candidates["QQ-L-XX/novel-deconstruct"]["absorbed_patterns"]
    assert "platform_ranking_research_boundary_gate" in candidates["d3nnywong/qidian-mcp-server"]["absorbed_patterns"]
    assert "tiered_memory_fact_retirement_gate" in candidates["senjinthedragon/Smart-Memory"]["absorbed_patterns"]
    assert "entity_mention_arc_timeline_gate" in candidates["astrapi69/bibliogon"]["absorbed_patterns"]
    assert "codex_story_skill_project_scaffold_gate" in candidates["rxb123ahuan/codexwriteskill"]["absorbed_patterns"]
    assert "canon_drift_continuity_qa_gate" in candidates["KanishkaV25/StorySync"]["absorbed_patterns"]
    assert "mcp_server" in candidates["d3nnywong/qidian-mcp-server"]["risk_flags"]
    assert "provider_key_surface" in candidates["d3nnywong/qidian-mcp-server"]["risk_flags"]
    assert "skill_install_surface" in candidates["rxb123ahuan/codexwriteskill"]["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "scene_deconstruction_axis_policy" in pattern_pack["bible_enrichment_targets"]
    assert "platform_ranking_research_policy" in pattern_pack["bible_enrichment_targets"]
    assert "tiered_memory_budget_policy" in pattern_pack["bible_enrichment_targets"]
    assert "entity_mention_appearance_index" in pattern_pack["bible_enrichment_targets"]
    assert "codex_story_project_scaffold" in pattern_pack["bible_enrichment_targets"]
    assert "scene_deconstruction_theory_report" in pattern_pack["whole_book_analysis_targets"]
    assert "platform_ranking_research_report" in pattern_pack["whole_book_analysis_targets"]
    assert "tiered_memory_budget_report" in pattern_pack["whole_book_analysis_targets"]
    assert "entity_appearance_gap_report" in pattern_pack["whole_book_analysis_targets"]
    assert "codex_story_scaffold_audit" in pattern_pack["whole_book_analysis_targets"]
    assert "scene_function_theory_axis_remap" in pattern_pack["inspired_mapping_targets"]
    assert "market_signal_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "memory_tier_supersession_remap" in pattern_pack["inspired_mapping_targets"]
    assert "entity_appearance_arc_remap" in pattern_pack["inspired_mapping_targets"]
    assert "codex_story_scaffold_remap" in pattern_pack["inspired_mapping_targets"]
    assert "source access" in " ".join(pattern_pack["scene_deconstruction_theory_report_gate_hints"]).lower()
    assert "qidian" in " ".join(pattern_pack["platform_ranking_research_boundary_gate_hints"]).lower()
    assert "supersede" in " ".join(pattern_pack["tiered_memory_fact_retirement_gate_hints"]).lower()
    assert "absence-gap" in " ".join(pattern_pack["entity_mention_arc_timeline_gate_hints"]).lower()
    assert "story.md" in " ".join(pattern_pack["codex_story_skill_project_scaffold_gate_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "scene_deconstruction_theory_report_gate_hints" in digest
    assert "platform_ranking_research_boundary_gate_hints" in digest
    assert "tiered_memory_fact_retirement_gate_hints" in digest
    assert "entity_mention_arc_timeline_gate_hints" in digest
    assert "codex_story_skill_project_scaffold_gate_hints" in digest


def test_ai_ism_markdown_canon_chain_sources_map_to_intake_gates():
    assert "https://github.com/conorbronsdon/avoid-ai-writing" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Lance-517/ChainWriter-Framework" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Kronic90/Mimirs-Memory-Hub" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/awzheng/Mangaroo" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/aileks/realm-sync" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("detect-only" in query.lower() and "voice profile" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("yaml frontmatter" in query.lower() and "promises/payoffs" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("local-first story bible" in query.lower() and "evidence-backed suggestions" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("chainable expert ai" in query.lower() and "expert modules" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "conorbronsdon/avoid-ai-writing",
                "html_url": "https://github.com/conorbronsdon/avoid-ai-writing",
                "description": (
                    "Portable MIT writing skill for AI writing patterns, AI-isms, detect-only, edit-in-place, "
                    "voice profile, iterate-to-convergence, prose fingerprints, voice drift, severity scoring, "
                    "novelty inflation and publishing copy guardrails."
                ),
                "stargazers_count": 1766,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["writing", "ai-writing", "skill"],
                "updated_at": "2026-06-10T19:46:02Z",
                "root_files": ["README.md", "LICENSE", "SKILL.md", "package.json"],
            },
            {
                "full_name": "danjdewhurst/story-skills",
                "html_url": "https://github.com/danjdewhurst/story-skills",
                "description": (
                    "Agent Skills project format with story bible, markdown files, YAML frontmatter, "
                    "continuity questions, promises/payoffs, scene state, chapter drafts, story validate, "
                    "factions, artifacts and timelines."
                ),
                "stargazers_count": 64,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["story-bible", "agent-skills", "writing"],
                "updated_at": "2026-06-10T18:25:55Z",
                "root_files": ["README.md", "LICENSE", "package.json"],
            },
            {
                "full_name": "sadasdfsaf/canonkit",
                "html_url": "https://github.com/sadasdfsaf/canonkit",
                "description": (
                    "Local-first story bible and continuity checker for fiction teams and solo authors, "
                    "canon drift, evidence-backed suggestions, contradictions, context packs, project storage, "
                    "JSON import and export, entity facts and local-first browser persistence."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["story-bible", "continuity", "fiction"],
                "updated_at": "2026-03-30T05:54:12Z",
                "root_files": ["README.md", "package.json"],
            },
            {
                "full_name": "Lance-517/ChainWriter-Framework",
                "html_url": "https://github.com/Lance-517/ChainWriter-Framework",
                "description": (
                    "ChainWriter semi-automated AI writing pipeline with chainable expert AI modules, "
                    "perfect alignment, boundless creativity, alignment framework, Special Instruction Set, "
                    "deconstructs complex literary creation and stress-tested module boundaries."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-writing", "framework", "fiction"],
                "updated_at": "2025-11-24T15:30:03Z",
                "root_files": ["README.md", "LICENSE"],
            },
            {
                "full_name": "awzheng/Mangaroo",
                "html_url": "https://github.com/awzheng/Mangaroo",
                "description": (
                    "Story visualizer with Story Bible Technology, visual consistency, character appearances, "
                    "settings and visual elements, art style, visual continuity, visual rules, image bible, "
                    "Gemini API key and PDF illustrator app surfaces."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["story-bible", "illustration", "visual"],
                "updated_at": "2026-03-30T18:35:14Z",
                "root_files": ["README.md", "package.json"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T10:00:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    assert "ai_ism_detect_edit_convergence_gate" in candidates["conorbronsdon/avoid-ai-writing"]["absorbed_patterns"]
    assert "markdown_skill_story_project_contract_gate" in candidates["danjdewhurst/story-skills"]["absorbed_patterns"]
    assert "canon_evidence_suggestion_review_gate" in candidates["sadasdfsaf/canonkit"]["absorbed_patterns"]
    assert "expert_chain_alignment_creativity_gate" in candidates["Lance-517/ChainWriter-Framework"]["absorbed_patterns"]
    assert "visual_story_bible_continuity_gate" in candidates["awzheng/Mangaroo"]["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)

    assert "ai_ism_detection_policy" in pattern_pack["bible_enrichment_targets"]
    assert "markdown_story_file_contract" in pattern_pack["bible_enrichment_targets"]
    assert "evidence_backed_canon_warning_policy" in pattern_pack["bible_enrichment_targets"]
    assert "expert_chain_stage_contracts" in pattern_pack["bible_enrichment_targets"]
    assert "visual_story_bible_policy" in pattern_pack["bible_enrichment_targets"]
    assert "ai_ism_detection_report" in pattern_pack["whole_book_analysis_targets"]
    assert "markdown_story_contract_audit" in pattern_pack["whole_book_analysis_targets"]
    assert "evidence_backed_canon_warning_report" in pattern_pack["whole_book_analysis_targets"]
    assert "expert_chain_stage_outputs" in pattern_pack["whole_book_analysis_targets"]
    assert "visual_story_bible_report" in pattern_pack["whole_book_analysis_targets"]
    assert "ai_ism_convergence_remap" in pattern_pack["inspired_mapping_targets"]
    assert "markdown_story_contract_remap" in pattern_pack["inspired_mapping_targets"]
    assert "canon_evidence_suggestion_remap" in pattern_pack["inspired_mapping_targets"]
    assert "expert_chain_stage_remap" in pattern_pack["inspired_mapping_targets"]
    assert "visual_bible_continuity_remap" in pattern_pack["inspired_mapping_targets"]
    assert "detect-only" in " ".join(pattern_pack["ai_ism_detect_edit_convergence_gate_hints"]).lower()
    assert "yaml frontmatter" in " ".join(pattern_pack["markdown_skill_story_project_contract_gate_hints"]).lower()
    assert "evidence" in " ".join(pattern_pack["canon_evidence_suggestion_review_gate_hints"]).lower()
    assert "alignment" in " ".join(pattern_pack["expert_chain_alignment_creativity_gate_hints"]).lower()
    assert "visual story bible" in " ".join(pattern_pack["visual_story_bible_continuity_gate_hints"]).lower()

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "ai_ism_detect_edit_convergence_gate_hints" in digest
    assert "markdown_skill_story_project_contract_gate_hints" in digest
    assert "canon_evidence_suggestion_review_gate_hints" in digest
    assert "expert_chain_alignment_creativity_gate_hints" in digest
    assert "visual_story_bible_continuity_gate_hints" in digest


def test_static_characterarc_source_maps_to_skill_loop_knowledge_trace_gates():
    assert "https://github.com/uu201/character-arc" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("Agent Loop" in query and "skill_load" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("knowledge_save_document" in query and "usedKnowledge" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "uu201/character-arc",
                "html_url": "https://github.com/uu201/character-arc",
                "description": (
                    "CharacterArc desktop AI novel workbench with local SQLite project isolation, "
                    "project settings, relationship graph, outline timeline, chapter editor versions, "
                    "knowledge center documents, reference deep analysis, style fingerprint extraction, "
                    "built-in and project-level Skill packages, Agent Loop, skill_load, tool registry, "
                    "task progress, AI run records, knowledge_save_document writeback, usedKnowledge, "
                    "usedSkills, run meta, prompt logs, API keys, txt docx and JSON workspace snapshot export."
                ),
                "stargazers_count": 241,
                "forks_count": 18,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-writing", "novel", "electron", "skill"],
                "updated_at": "2026-06-10T08:40:33Z",
                "root_files": [
                    "README.md",
                    "LICENSE",
                    "package.json",
                    "pnpm-lock.yaml",
                    "electron/main/ai/agent/streaming-orchestrator.ts",
                    "electron/main/ai/tasks/reference-deep-analyze.ts",
                    "electron/main/ai/tasks/style-fingerprint-extract.ts",
                    "electron/main/ai/runtime/run-meta.ts",
                    "electron/main/archive/project-archive.ts",
                ],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T14:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    candidate = candidates["uu201/character-arc"]
    assert "project_skill_agent_loop_gate" in candidate["absorbed_patterns"]
    assert "knowledge_document_writeback_trace_gate" in candidate["absorbed_patterns"]
    assert "local_first_novel_workspace" in candidate["absorbed_patterns"]
    assert "provider_key_surface" in candidate["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "project_skill_selection_policy" in pattern_pack["bible_enrichment_targets"]
    assert "knowledge_document_writeback_policy" in pattern_pack["bible_enrichment_targets"]
    assert "project_skill_selection_audit" in pattern_pack["whole_book_analysis_targets"]
    assert "knowledge_writeback_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "project_skill_agent_loop_remap" in pattern_pack["inspired_mapping_targets"]
    assert "knowledge_writeback_trace_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("skill_load" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("typed knowledge documents" in hint for hint in pattern_pack["knowledge_document_writeback_trace_gate_hints"])
    assert any("max Agent Loop steps" in hint for hint in pattern_pack["project_skill_agent_loop_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "project_skill_agent_loop_gate_hints" in digest
    assert "knowledge_document_writeback_trace_gate_hints" in digest


def test_static_novelforge_source_maps_to_host_schema_retrieval_architecture_gates():
    assert "https://github.com/zlx362211854/novelforge-agent" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("modelHint" in query and "prompt caching" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("chapter_review" in query and "forceAdvanced" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("BM25" in query and "memory cards" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "zlx362211854/novelforge-agent",
                "html_url": "https://github.com/zlx362211854/novelforge-agent",
                "description": (
                    "Local-first long-form novel workflow engine for MCP hosts and CLI shells. "
                    "State machine, zod schemas, BM25 retrieval, persistent project state, no LLM dependency, "
                    "host's LLM generates artifacts, exact instruction and packed context, expectedFormat, "
                    "modelHint, segments, prompt caching, chapter_review, requiredBeats, chapter_revision, "
                    "revisionCounts, forceAdvanced, rejected submissions, architecture_extension, plannedTotalChapters, "
                    "chaptersPerRun, CJK bigram tokenizer, memory cards, story-bible sections."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["mcp", "novel", "fiction", "workflow", "bm25"],
                "updated_at": "2026-06-10T08:33:52Z",
                "root_files": [
                    "README.md",
                    "README.zh-CN.md",
                    "LICENSE",
                    "package.json",
                    "src/core/workflow.ts",
                    "src/core/schemas.ts",
                    "src/core/contextBuilder.ts",
                    "src/core/agentLog.ts",
                    "src/mcp/tools.ts",
                    "scripts/e2e.sh",
                ],
                "package_scripts": {
                    "prepare": "npm run build",
                    "inspect": "npm run build && npx -y @modelcontextprotocol/inspector node dist/src/mcp/server.js",
                    "test:e2e": "npm run build && bash scripts/e2e.sh",
                },
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T15:40:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    candidate = candidates["zlx362211854/novelforge-agent"]
    assert "host_instruction_context_boundary_gate" in candidate["absorbed_patterns"]
    assert "schema_review_revision_recovery_gate" in candidate["absorbed_patterns"]
    assert "cjk_bm25_context_retrieval_gate" in candidate["absorbed_patterns"]
    assert "dynamic_architecture_extension_gate" in candidate["absorbed_patterns"]
    assert "workflow_agent_pipeline" in candidate["absorbed_patterns"]
    assert "structured_generation_schema" in candidate["absorbed_patterns"]
    assert "mcp_server" in candidate["risk_flags"]
    assert "shell_script" in candidate["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "host_instruction_context_contract" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_acceptance_schema" in pattern_pack["bible_enrichment_targets"]
    assert "cjk_lexical_retrieval_scope" in pattern_pack["bible_enrichment_targets"]
    assert "architecture_extension_policy" in pattern_pack["bible_enrichment_targets"]
    assert "host_instruction_context_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_acceptance_gate_report" in pattern_pack["whole_book_analysis_targets"]
    assert "cjk_bm25_retrieval_report" in pattern_pack["whole_book_analysis_targets"]
    assert "architecture_extension_checkpoint" in pattern_pack["whole_book_analysis_targets"]
    assert "host_instruction_context_remap" in pattern_pack["inspired_mapping_targets"]
    assert "schema_review_revision_remap" in pattern_pack["inspired_mapping_targets"]
    assert "cjk_retrieval_context_remap" in pattern_pack["inspired_mapping_targets"]
    assert "architecture_extension_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("host LLM" in hint for hint in pattern_pack["host_instruction_context_boundary_gate_hints"])
    assert any("revisionCounts" in hint for hint in pattern_pack["schema_review_revision_recovery_gate_hints"])
    assert any("CJK-aware BM25" in hint for hint in pattern_pack["cjk_bm25_context_retrieval_gate_hints"])
    assert any("architecture_extension" in hint for hint in pattern_pack["dynamic_architecture_extension_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "host_instruction_context_boundary_gate_hints" in digest
    assert "schema_review_revision_recovery_gate_hints" in digest
    assert "cjk_bm25_context_retrieval_gate_hints" in digest
    assert "dynamic_architecture_extension_gate_hints" in digest


def test_stylemuse_storyforge_moyun_sources_add_anti_copy_style_rag_gates():
    assert "https://github.com/MissingDanial/StyleMuse" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/91zgaoge/StoryForge" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/wuyinglai/moyun-studio" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("style imitation" in query and "anti-copy" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "MissingDanial/StyleMuse",
                "html_url": "https://github.com/MissingDanial/StyleMuse",
                "description": (
                    "StyleMuse is a RAG based author style imitation system for epub/txt uploads. "
                    "It analyzes writing style, builds a vector index, retrieves relevant passages, "
                    "uses retrieval filtering, post-generation repetition detection, prompt constraints, "
                    "anti-copy and plagiarism prevention before generating original imitation prose, "
                    "with OpenAI-compatible providers and user API keys."
                ),
                "stargazers_count": 2,
                "forks_count": 0,
                "license": None,
                "topics": ["style-imitation", "rag", "writing", "novel"],
                "updated_at": "2026-06-09T09:11:35Z",
                "root_files": [
                    "README.md",
                    "Dockerfile",
                    "docker-compose.yml",
                    ".env.example",
                    "requirements.txt",
                    "app.py",
                    "main.py",
                    "prompts",
                    "skills",
                    "tests",
                ],
            },
            {
                "full_name": "91zgaoge/StoryForge",
                "html_url": "https://github.com/91zgaoge/StoryForge",
                "description": (
                    "StoryForge is an AI director-style novel creation system with backstage story, "
                    "character, scene and worldbuilding management, frontstage immersive drafting, "
                    "knowledge graph, foreshadowing tracking, StyleDNA, collaboration, and seven-stage workflow."
                ),
                "stargazers_count": 31,
                "forks_count": 8,
                "license": None,
                "topics": ["novel", "tauri", "storyforge", "styledna"],
                "updated_at": "2026-06-10T10:01:26Z",
                "root_files": [
                    "README.md",
                    "Cargo.toml",
                    "package.json",
                    "docker-compose.yml",
                    "deploy.sh",
                    "run-dev.ps1",
                    "src-tauri",
                    "src-frontend",
                    ".env.example",
                ],
            },
            {
                "full_name": "wuyinglai/moyun-studio",
                "html_url": "https://github.com/wuyinglai/moyun-studio",
                "description": (
                    "Moyun Studio is a local-first AI fiction writing studio with scene-level sec-*.md writing, "
                    "candidate-based safe revision, story memory files recent-context.md and story-state.md, "
                    "Lite and Professional entry points, YAML prompt pipelines, and local workspace file storage."
                ),
                "stargazers_count": 1,
                "forks_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["fiction", "local-first", "safe-revision"],
                "updated_at": "2026-06-10T17:35:14Z",
                "root_files": [
                    "README.md",
                    "LICENSE",
                    ".env.example",
                    "backend",
                    "frontend",
                    "prompts",
                    "scripts",
                    "kill_port_8000.ps1",
                    "tests",
                ],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T17:50:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    stylemuse = candidates["MissingDanial/StyleMuse"]
    assert "same_type_creation" in stylemuse["absorbed_patterns"]
    assert "anti_copy_style_rag_gate" in stylemuse["absorbed_patterns"]
    assert "context_reference" in stylemuse["absorbed_patterns"]
    assert "docker" in stylemuse["risk_flags"]
    assert "provider_key_surface" in stylemuse["risk_flags"]

    storyforge = candidates["91zgaoge/StoryForge"]
    assert "style_dna_reference_library_gate" in storyforge["absorbed_patterns"]
    assert "setup_payoff_tracking" in storyforge["absorbed_patterns"]
    assert "docker" in storyforge["risk_flags"]
    assert "shell_script" in storyforge["risk_flags"]
    assert "powershell_script" in storyforge["risk_flags"]

    moyun = candidates["wuyinglai/moyun-studio"]
    assert "local_first_novel_workspace" in moyun["absorbed_patterns"]
    assert "draft_candidate_promotion_gate" in moyun["absorbed_patterns"]
    assert "workflow_agent_pipeline" in moyun["absorbed_patterns"]
    assert "powershell_script" in moyun["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "anti_copy_style_rag_policy" in pattern_pack["bible_enrichment_targets"]
    assert "style_retrieval_similarity_review" in pattern_pack["bible_enrichment_targets"]
    assert "anti_copy_style_rag_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("style-imitation RAG" in hint for hint in pattern_pack["anti_copy_style_rag_gate_hints"])
    assert any("retrieved chunks" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "anti_copy_style_rag_gate_hints" in digest



def test_counterfactual_graph_rag_sources_add_story_graph_remix_gates():
    assert "https://github.com/mert-ozdemirr/sherlock-counterfactual-modular-graph-rag" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/SutraMind/GraphRAG-story" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("counterfactual" in query and "narrative reasoning" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "mert-ozdemirr/sherlock-counterfactual-modular-graph-rag",
                "html_url": "https://github.com/mert-ozdemirr/sherlock-counterfactual-modular-graph-rag",
                "description": (
                    "Modular Graph-RAG pipeline for narrative reasoning and counterfactual story generation "
                    "over the Sherlock Holmes canon. It extracts propositions from canonical chapter text, "
                    "builds narrative graph chunks with event, fact, entity, evidence, next_narrative and "
                    "next_realtime edges, retrieves verified story context, and generates alternative storylines."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["graphrag", "counterfactual", "narrative-reasoning"],
                "updated_at": "2026-01-26T12:53:25Z",
                "root_files": ["README.md", "pyproject.toml", "uv.lock", "scripts"],
            },
            {
                "full_name": "SutraMind/GraphRAG-story",
                "html_url": "https://github.com/SutraMind/GraphRAG-story",
                "description": (
                    "Hybrid RAG story analysis system with graph traversal and vector search. It parses story files "
                    "into chapter and paragraph ids, extracts entities and relationships, builds a Neo4j knowledge graph, "
                    "routes queries across GRAPH, VECTOR, and HYBRID modes, and validates chapter and relationship counts."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["graphrag", "story-analysis", "hybrid-rag"],
                "updated_at": "2026-03-29T14:31:23Z",
                "root_files": ["README.md", "app", "config", "pipeline", "rag", "requirements.txt"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T18:40:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    sherlock = candidates["mert-ozdemirr/sherlock-counterfactual-modular-graph-rag"]
    assert "counterfactual_story_graph_rag_gate" in sherlock["absorbed_patterns"]
    assert "context_reference" in sherlock["absorbed_patterns"]
    assert "community_graph_source_deconstruction" in sherlock["absorbed_patterns"]
    assert "license:missing" in sherlock["trust_review"]["flags"]

    story_rag = candidates["SutraMind/GraphRAG-story"]
    assert "counterfactual_story_graph_rag_gate" in story_rag["absorbed_patterns"]
    assert "dual_level_graph_vector_retrieval" in story_rag["absorbed_patterns"]
    assert "community_graph_source_deconstruction" in story_rag["absorbed_patterns"]
    assert "license:missing" in story_rag["trust_review"]["flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "counterfactual_divergence_policy" in pattern_pack["bible_enrichment_targets"]
    assert "verified_story_graph_context_policy" in pattern_pack["bible_enrichment_targets"]
    assert "counterfactual_divergence_points" in pattern_pack["whole_book_analysis_targets"]
    assert "narrative_vs_realtime_event_edges" in pattern_pack["whole_book_analysis_targets"]
    assert "counterfactual_graph_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("divergence card" in hint for hint in pattern_pack["counterfactual_story_graph_rag_gate_hints"])
    assert any("divergence point" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("source event path" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "counterfactual_story_graph_rag_gate_hints" in digest


def test_webnovel_architect_sources_add_serial_reader_reward_contract_gates():
    assert "https://github.com/ansrhkddns-web/k-webnovel-architect" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/0503xqy/novel-writer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("reader reward" in query and "paid conversion" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "ansrhkddns-web/k-webnovel-architect",
                "html_url": "https://github.com/ansrhkddns-web/k-webnovel-architect",
                "description": (
                    "Korean webnovel commercial serialization planner with reader persona demand, "
                    "reader reward, opening hook, episode roadmap, chapter production brief, "
                    "paid conversion point, platform packaging checklist, and retention diagnostics."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["webnovel", "commercial-serialization", "reader-reward"],
                "updated_at": "2026-05-07T15:03:53Z",
                "root_files": ["README.md", "SKILL.md", "agents", "references"],
            },
            {
                "full_name": "0503xqy/novel-writer",
                "html_url": "https://github.com/0503xqy/novel-writer",
                "description": (
                    "Commercial webnovel production skill for platform serial fiction with opening hook, "
                    "chapter contract, emotional reward, retention risk, paid chapter trust, and revision ledgers."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["webnovel", "chapter-contract", "retention"],
                "updated_at": "2026-05-21T09:35:25Z",
                "root_files": ["README.MD", "SKILL.md", "agents", "references", "scripts"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T20:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    architect = candidates["ansrhkddns-web/k-webnovel-architect"]
    assert "serial_reader_reward_contract_gate" in architect["absorbed_patterns"]
    assert "reader_reward_channel_gate" in architect["absorbed_patterns"]
    assert architect["trust_review"]["flags"] == []

    writer = candidates["0503xqy/novel-writer"]
    assert "serial_reader_reward_contract_gate" in writer["absorbed_patterns"]
    assert "license:missing" in writer["trust_review"]["flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "serial_reader_reward_contract" in pattern_pack["bible_enrichment_targets"]
    assert "platform_packaging_boundary_policy" in pattern_pack["bible_enrichment_targets"]
    assert "reader_reward_map" in pattern_pack["whole_book_analysis_targets"]
    assert "opening_hook_contract" in pattern_pack["whole_book_analysis_targets"]
    assert "free_to_paid_turning_points" in pattern_pack["whole_book_analysis_targets"]
    assert "platform_packaging_fit_report" in pattern_pack["whole_book_analysis_targets"]
    assert "serial_reward_contract_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("chapter contract" in hint for hint in pattern_pack["serial_reader_reward_contract_gate_hints"])
    assert any("next-payment trust signal" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("reader-promise wording" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "serial_reader_reward_contract_gate_hints" in digest


def test_inkwell_source_adds_living_codex_editorial_workbench_gates():
    assert "https://github.com/Meryouc/inkwell" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("living codex" in query and "editorial passes" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "Meryouc/inkwell",
                "html_url": "https://github.com/Meryouc/inkwell",
                "description": (
                    "Inkwell is a local-first manuscript workshop and VS Code fork for fiction. "
                    "It has a manuscript tree for acts, chapters and scenes, a living codex for "
                    "characters, places, items, lore and factions with YAML frontmatter, a continuity "
                    "engine for timeline math, geography, promise/payoff and relationship-state evolution, "
                    "plus editorial passes for developmental, line and copy editing with pacing curve, "
                    "emotional tempo, POV balance, sentence-length histogram and dialogue ratio diagnostics, "
                    "and BYOK provider API keys stored in the OS keystore."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["fiction", "manuscript", "living-codex", "editorial"],
                "updated_at": "2026-05-31T12:05:02Z",
                "root_files": [
                    "README.md",
                    "LICENSE-INKWELL.md",
                    "LICENSE.txt",
                    "package.json",
                    "launch-inkwell.bat",
                    "src/vs/inkwell/browser",
                ],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T22:30:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    inkwell = candidates["Meryouc/inkwell"]
    assert "living_codex_editorial_workbench_gate" in inkwell["absorbed_patterns"]
    assert "local_first_novel_workspace" in inkwell["absorbed_patterns"]
    assert "editor_context_prose_analysis_gate" in inkwell["absorbed_patterns"]
    assert "provider_key_surface" in inkwell["risk_flags"]
    assert "windows_script" in inkwell["risk_flags"]
    assert inkwell["trust_review"]["flags"] == []

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "living_codex_scene_link_policy" in pattern_pack["bible_enrichment_targets"]
    assert "editorial_pass_diagnostic_policy" in pattern_pack["bible_enrichment_targets"]
    assert "manuscript_tree_scene_map" in pattern_pack["whole_book_analysis_targets"]
    assert "codex_scene_reference_report" in pattern_pack["whole_book_analysis_targets"]
    assert "editorial_pass_diagnostics" in pattern_pack["whole_book_analysis_targets"]
    assert "continuity_engine_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "living_codex_scene_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("manuscript tree node" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("editorial pass type" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("typed diagnostics" in hint for hint in pattern_pack["living_codex_editorial_workbench_gate_hints"])
    assert any("codex backlink map" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "living_codex_editorial_workbench_gate_hints" in digest


def test_novelos_source_adds_agent_role_profile_workflow_gates():
    assert "https://github.com/ayermac/novelos" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("agent-level llm routing" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "ayermac/novelos",
                "html_url": "https://github.com/ayermac/novelos",
                "description": (
                    "Novelos is a local-first AI workbench for long-form fiction. "
                    "It uses a LangGraph agent chapter workflow with planner, screenwriter, "
                    "author, polisher, editor, memory curator, and publisher roles. "
                    "The workbench shows workflow timeline and run details with node events, "
                    "artifacts, LLM latency/tokens, Run Doctor recovery, project memory, "
                    "LLM profiles, LLM profile routing, agent-level LLM routing, and API keys."
                ),
                "stargazers_count": 5,
                "forks_count": 2,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "fiction", "langgraph", "multi-agent"],
                "updated_at": "2026-06-10T16:24:51Z",
                "root_files": [
                    "README.md",
                    "LICENSE",
                    "pyproject.toml",
                    "frontend/package.json",
                    "desktop/package.json",
                    "packaging/scripts/build-desktop-mac.sh",
                ],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T23:10:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    novelos = candidates["ayermac/novelos"]
    assert "agent_role_profile_workflow_gate" in novelos["absorbed_patterns"]
    assert "workflow_agent_pipeline" in novelos["absorbed_patterns"]
    assert "provider_budget_smoke_gate" in novelos["absorbed_patterns"]
    assert "provider_key_surface" in novelos["risk_flags"]
    assert "shell_script" in novelos["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "agent_role_profile_policy" in pattern_pack["bible_enrichment_targets"]
    assert "workflow_timeline_event_policy" in pattern_pack["bible_enrichment_targets"]
    assert "agent_role_profile_matrix" in pattern_pack["whole_book_analysis_targets"]
    assert "workflow_timeline_run_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "agent_llm_route_audit" in pattern_pack["whole_book_analysis_targets"]
    assert "memory_curator_publish_boundary_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "agent_role_profile_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("role profile" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("workflow timeline events" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("canon-write permission" in hint for hint in pattern_pack["agent_role_profile_workflow_gate_hints"])
    assert any("route profiles" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "agent_role_profile_workflow_gate_hints" in digest


def test_storygraph_source_adds_character_knowledge_timeline_gates():
    assert "https://github.com/v-saprykin/storygraph" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("knowledge states" in query and "narrative graph" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "v-saprykin/storygraph",
                "html_url": "https://github.com/v-saprykin/storygraph",
                "description": (
                    "StoryGraph converts long-form fiction into a validated narrative graph: "
                    "manuscript text to chapters, scenes, narrative events, characters, "
                    "relationships, plotlines, timelines and analytical queries. "
                    "It asks which facts are known by which characters at a given point, "
                    "which plotlines have no clear resolution, which characters disappear "
                    "for too long, which scenes do not change the state of the story world, "
                    "and what breaks if a key event is changed. It models causal links, "
                    "character states, knowledge states, timeline versions and human review."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "fiction", "narrative-graph", "knowledge-states"],
                "updated_at": "2026-06-10T23:30:00Z",
                "root_files": ["README.md", "LICENSE", "ROADMAP.md", "docker-compose.yml"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T23:40:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    storygraph = candidates["v-saprykin/storygraph"]
    assert "character_knowledge_timeline_gate" in storygraph["absorbed_patterns"]
    assert "counterfactual_story_graph_rag_gate" in storygraph["absorbed_patterns"]
    assert "plotline_thread_tracking" in storygraph["absorbed_patterns"]
    assert "docker" in storygraph["risk_flags"]
    assert storygraph["trust_review"]["flags"] == []

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "character_knowledge_state_policy" in pattern_pack["bible_enrichment_targets"]
    assert "pov_secret_visibility_policy" in pattern_pack["bible_enrichment_targets"]
    assert "character_knowledge_timeline" in pattern_pack["whole_book_analysis_targets"]
    assert "secret_visibility_matrix" in pattern_pack["whole_book_analysis_targets"]
    assert "non_state_changing_scene_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "missing_character_presence_report" in pattern_pack["whole_book_analysis_targets"]
    assert "character_knowledge_visibility_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("allowed to know" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("knowledge-state deltas" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("knowledge-state timeline" in hint for hint in pattern_pack["character_knowledge_timeline_gate_hints"])
    assert any("secret matrix" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "character_knowledge_timeline_gate_hints" in digest


def test_continuation_production_control_sources_add_checkpoint_memory_semantic_thread_gates():
    assert "https://github.com/ExplosiveCoderflome/AI-Novel-Writing-Assistant" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/iLearn-Lab/NovelClaw" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/YILING0013/AI_NovelGenerator" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/v-saprykin/storygraph" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("automatic director checkpoint" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("semantic context consistency" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "ExplosiveCoderflome/AI-Novel-Writing-Assistant",
                "html_url": "https://github.com/ExplosiveCoderflome/AI-Novel-Writing-Assistant",
                "description": (
                    "Chinese AI novel writing assistant with book decomposition, automatic director checkpoint chain, "
                    "director stage checkpoint gate, role asset quality review gate, chapter tasks, quality guardrails, "
                    "genre/style management, and long-form production pipeline patterns."
                ),
                "stargazers_count": 134,
                "forks_count": 8,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-novel", "writing", "director", "checkpoint"],
                "updated_at": "2026-06-11T08:00:00Z",
            },
            {
                "full_name": "iLearn-Lab/NovelClaw",
                "html_url": "https://github.com/iLearn-Lab/NovelClaw",
                "description": (
                    "Long-form fiction workspace with inspectable runs, inspectable memory workspace gate, "
                    "memory-aware chapter workspace, sessions, storyboards, manuscript surfaces, character/world views, "
                    "editable memory banks and memory-aware writing control."
                ),
                "stargazers_count": 319,
                "forks_count": 31,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "memory", "workspace"],
                "updated_at": "2026-06-11T08:05:00Z",
            },
            {
                "full_name": "YILING0013/AI_NovelGenerator",
                "html_url": "https://github.com/YILING0013/AI_NovelGenerator",
                "description": (
                    "Automatic novel generator with semantic context consistency gate, semantic search, "
                    "vector-based long-term context consistency, knowledge base integration, state tracking, "
                    "foreshadowing, automatic proofreading, plot contradictions and logical conflicts."
                ),
                "stargazers_count": 1860,
                "forks_count": 165,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["novel", "rag", "semantic-search"],
                "updated_at": "2026-06-11T08:10:00Z",
            },
            {
                "full_name": "v-saprykin/storygraph",
                "html_url": "https://github.com/v-saprykin/storygraph",
                "description": (
                    "StoryGraph converts fiction into a validated narrative graph with multi-thread knowledge timeline gate, "
                    "character knowledge states, plotlines, causal links, timeline versions, and human review."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "narrative-graph", "timeline"],
                "updated_at": "2026-06-11T08:15:00Z",
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T16:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    director = candidates["ExplosiveCoderflome/AI-Novel-Writing-Assistant"]
    novelclaw = candidates["iLearn-Lab/NovelClaw"]
    semantic = candidates["YILING0013/AI_NovelGenerator"]
    storygraph = candidates["v-saprykin/storygraph"]
    assert "automatic_director_checkpoint_chain" in director["absorbed_patterns"]
    assert "director_stage_checkpoint_gate" in director["absorbed_patterns"]
    assert "role_asset_quality_review_gate" in director["absorbed_patterns"]
    assert "inspectable_memory_workspace_gate" in novelclaw["absorbed_patterns"]
    assert "memory_aware_chapter_workspace" in novelclaw["absorbed_patterns"]
    assert "semantic_context_consistency_gate" in semantic["absorbed_patterns"]
    assert "multi_thread_knowledge_timeline_gate" in storygraph["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "production_checkpoint_policy" in pattern_pack["bible_enrichment_targets"]
    assert "memory_workspace_review_policy" in pattern_pack["bible_enrichment_targets"]
    assert "semantic_context_consistency_policy" in pattern_pack["bible_enrichment_targets"]
    assert "thread_knowledge_timeline_policy" in pattern_pack["bible_enrichment_targets"]
    assert "director_checkpoint_chain" in pattern_pack["whole_book_analysis_targets"]
    assert "memory_workspace_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "semantic_context_consistency_report" in pattern_pack["whole_book_analysis_targets"]
    assert "thread_knowledge_timeline" in pattern_pack["whole_book_analysis_targets"]
    assert any("director checkpoint" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("memory workspace" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("semantic context" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("thread knowledge" in hint for hint in pattern_pack["multi_thread_knowledge_timeline_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "automatic_director_checkpoint_chain_hints" in digest
    assert "inspectable_memory_workspace_gate_hints" in digest
    assert "semantic_context_consistency_gate_hints" in digest
    assert "multi_thread_knowledge_timeline_gate_hints" in digest


def test_bookboard_source_adds_manuscript_card_board_and_chapter_timeline_gates():
    assert "https://github.com/markalexwatson/bookboard" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("digital corkboard" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "markalexwatson/bookboard",
                "html_url": "https://github.com/markalexwatson/bookboard",
                "description": (
                    "Visual planning tool for novelists with digital corkboard cards for characters, themes, "
                    "locations, objects and scenes. Imports Markdown manuscripts, extracts structure with AI, "
                    "keeps a chapter timeline with drag-to-reorder editing, preserves front matter, merges duplicate cards, "
                    "exports manuscript text, story bible document and JSON backup, auto-saves in localStorage, "
                    "and can sync through Google Drive with local API keys."
                ),
                "stargazers_count": 2,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "planning", "manuscript", "story-bible"],
                "updated_at": "2026-06-11T12:00:00Z",
                "root_files": ["README.md", "LICENSE", "index.html"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T01:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    bookboard = candidates["markalexwatson/bookboard"]
    assert "manuscript_card_board_extraction_gate" in bookboard["absorbed_patterns"]
    assert "chapter_timeline_frontmatter_export_gate" in bookboard["absorbed_patterns"]
    assert "cloud_sync_oauth_surface" in bookboard["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "manuscript_card_board_policy" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_timeline_export_policy" in pattern_pack["bible_enrichment_targets"]
    assert "manuscript_card_board_extraction_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_timeline_frontmatter_export_report" in pattern_pack["whole_book_analysis_targets"]
    assert "card_board_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("card board" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("chapter timeline" in hint for hint in pattern_pack["chapter_timeline_frontmatter_export_gate_hints"])
    assert any("digital corkboard" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "manuscript_card_board_extraction_gate_hints" in digest
    assert "chapter_timeline_frontmatter_export_gate_hints" in digest


def test_inkwell_source_adds_binder_snapshot_and_relationship_analytics_gates():
    assert "https://github.com/talktofess/inkwell" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("manuscript binder" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "talktofess/inkwell",
                "html_url": "https://github.com/talktofess/inkwell",
                "description": (
                    "Novel Writing Studio with manuscript binder folders to chapters to scenes, "
                    "reorderable scenes with status colours, POV and location, per-scene word targets, "
                    "corkboard outliner, story bible with characters, locations, factions, items and lore, "
                    "custom attributes, relationships and automatic appears in scene links, writing analytics "
                    "with daily goal ring, activity heatmap, projected finish date and deadline pacing, "
                    "manual and automatic per-scene snapshots with restore, and Markdown, DOCX, EPUB and PDF export "
                    "compiled from the binder in reading order. Uses Supabase service_role key and passphrase auth."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["novel", "writing-studio", "story-bible", "manuscript"],
                "updated_at": "2026-06-07T13:01:25Z",
                "root_files": ["README.md", "package.json", "supabase/schema.sql"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T02:15:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    inkwell = candidates["talktofess/inkwell"]
    assert "manuscript_binder_scene_snapshot_gate" in inkwell["absorbed_patterns"]
    assert "story_bible_relationship_analytics_gate" in inkwell["absorbed_patterns"]
    assert "provider_key_surface" in inkwell["risk_flags"]
    assert "cloud_sync_oauth_surface" in inkwell["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "manuscript_binder_scene_snapshot_policy" in pattern_pack["bible_enrichment_targets"]
    assert "story_bible_relationship_analytics_policy" in pattern_pack["bible_enrichment_targets"]
    assert "binder_scene_snapshot_report" in pattern_pack["whole_book_analysis_targets"]
    assert "story_bible_relationship_analytics_report" in pattern_pack["whole_book_analysis_targets"]
    assert any("binder" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("appears in" in hint for hint in pattern_pack["story_bible_relationship_analytics_gate_hints"])
    assert any("snapshot" in hint for hint in pattern_pack["manuscript_binder_scene_snapshot_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "manuscript_binder_scene_snapshot_gate_hints" in digest
    assert "story_bible_relationship_analytics_gate_hints" in digest


def test_auto_story_tools_source_adds_seed_bible_foundation_loop_gates():
    assert "https://github.com/levineam/auto-story-tools" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("foundation loop" in query.lower() or "seed" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "levineam/auto-story-tools",
                "html_url": "https://github.com/levineam/auto-story-tools",
                "description": (
                    "Autonomous story generation pipeline from seed to story bible to screenplay or novel. "
                    "It validates the seed concept, then generates layers in dependency order: world, characters, "
                    "voice, mystery, outline, canon and foreshadowing. The foundation loop evaluates with an LLM judge, "
                    "mechanical slop detector, cross-layer consistency checker and reader panel, targets the weakest dimension, "
                    "regenerates that layer, keep/discard compares score, restores previous version if worse, and repeats until "
                    "foundation_score and lore_score thresholds pass. Outputs seed.txt, world.md, characters.md, outline.md, "
                    "voice.md, canon.md, MYSTERY.md, foreshadowing.md, state.json, eval_logs and results.tsv. Uses provider API keys, "
                    "optional API base gateway/proxy, uv sync, OpenClaw integration and direct model calls."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai", "story", "outline", "screenplay", "fiction", "writing"],
                "updated_at": "2026-03-26T13:34:25Z",
                "root_files": ["README.md", "LICENSE", "pyproject.toml", "integrations/openclaw"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T02:40:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    auto_story = candidates["levineam/auto-story-tools"]
    assert "seed_to_bible_foundation_loop_gate" in auto_story["absorbed_patterns"]
    assert "layered_story_bible_artifact_contract_gate" in auto_story["absorbed_patterns"]
    assert "provider_key_surface" in auto_story["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "seed_validation_foundation_policy" in pattern_pack["bible_enrichment_targets"]
    assert "layered_story_bible_artifact_policy" in pattern_pack["bible_enrichment_targets"]
    assert "foundation_loop_score_report" in pattern_pack["whole_book_analysis_targets"]
    assert "layered_story_bible_artifact_report" in pattern_pack["whole_book_analysis_targets"]
    assert any("foundation loop" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("seed" in hint for hint in pattern_pack["seed_to_bible_foundation_loop_gate_hints"])
    assert any("canon.md" in hint for hint in pattern_pack["layered_story_bible_artifact_contract_gate_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "seed_to_bible_foundation_loop_gate_hints" in digest
    assert "layered_story_bible_artifact_contract_gate_hints" in digest


def test_novel_writing_workflow_source_adds_contract_and_pr_editorial_gates():
    assert "https://github.com/author-repo-testing/novel-writing-workflow" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("project-contract.md" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "author-repo-testing/novel-writing-workflow",
                "html_url": "https://github.com/author-repo-testing/novel-writing-workflow",
                "description": (
                    "GitHub practice workbook for authors with a novel_template workspace. "
                    "PROJECT-CONTRACT.md is the standing author AI collaboration agreement and inherits from ../AGENTS.md; "
                    "when the project contract and AGENTS conflict, the AI must surface the conflict and not silently pick one. "
                    "The contract records automation level, explanation depth, commit cadence, tracking format, research pattern, "
                    "author boundaries and renegotiation triggers. The workflow maps manuscript collaboration to branches, commits and pull requests: "
                    "line-level edits as PRs, structural feedback as issues, every round time-stamped in history, story bible, drafts, editorial notes, "
                    "continuity log, beta reader feedback, style sheet proposals and a PR template asking what changed, why, and what feedback is requested."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "writing", "github", "author", "ai-collaboration"],
                "updated_at": "2026-06-10T09:15:00Z",
                "root_files": ["README.md", "AGENTS.md", "LICENSE", "novel_template", ".github"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T03:10:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    workflow = candidates["author-repo-testing/novel-writing-workflow"]
    assert "author_ai_project_contract_review_gate" in workflow["absorbed_patterns"]
    assert "manuscript_pr_editorial_workflow_gate" in workflow["absorbed_patterns"]
    assert workflow["license"] == "MIT"

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "author_ai_project_contract_policy" in pattern_pack["bible_enrichment_targets"]
    assert "manuscript_pr_review_policy" in pattern_pack["bible_enrichment_targets"]
    assert "project_contract_conflict_report" in pattern_pack["whole_book_analysis_targets"]
    assert "editorial_pr_review_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "project_contract_remap" in pattern_pack["inspired_mapping_targets"]
    assert "editorial_review_trace_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("project contract" in hint.lower() for hint in pattern_pack["continuation_prompt_hints"])
    assert any("conflict" in hint.lower() for hint in pattern_pack["author_ai_project_contract_review_gate_hints"])
    assert any("PR-style" in hint for hint in pattern_pack["manuscript_pr_editorial_workflow_gate_hints"])
    assert any("upstream contract text" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "author_ai_project_contract_review_gate_hints" in digest
    assert "manuscript_pr_editorial_workflow_gate_hints" in digest


def test_short_drama_story_bible_template_source_adds_episode_visual_anchor_gates():
    assert "https://github.com/clipcurator/ai-short-drama-story-bible-template" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("short drama story bible" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "clipcurator/ai-short-drama-story-bible-template",
                "html_url": "https://github.com/clipcurator/ai-short-drama-story-bible-template",
                "description": (
                    "AI Short Drama Story Bible Template for keeping AI short drama characters, episode rules, "
                    "visual canon and continuity memory consistent. Core sections include series premise, character canon, "
                    "relationship rules, visual anchors, episode boundaries and continuity memory. Review signals require "
                    "the bible separates permanent canon from temporary scene notes, character rules are reusable across episodes, "
                    "visual anchors are specific enough for prompt handoff, and new episodes can be checked against existing memory. "
                    "The workflow brief supports source material, product notes, script context, video context and review data; "
                    "the scorecard reviews visual anchors, episode boundaries, continuity memory, keep/revise/drop decisions, "
                    "and checks before publishing, editing, generating assets or updating a directory page."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["short-drama", "story-bible", "continuity", "visual-canon", "templates"],
                "updated_at": "2026-06-09T11:20:00Z",
                "root_files": ["README.md", "README.zh-CN.md", "LICENSE", "docs", "templates"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T03:35:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    template = candidates["clipcurator/ai-short-drama-story-bible-template"]
    assert "short_drama_story_bible_template_gate" in template["absorbed_patterns"]
    assert "visual_anchor_prompt_handoff_gate" in template["absorbed_patterns"]
    assert "visual_story_bible_continuity_gate" in template["absorbed_patterns"]
    assert template["license"] == "MIT"

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "short_drama_story_bible_policy" in pattern_pack["bible_enrichment_targets"]
    assert "visual_anchor_prompt_handoff_policy" in pattern_pack["bible_enrichment_targets"]
    assert "short_drama_bible_completeness_report" in pattern_pack["whole_book_analysis_targets"]
    assert "visual_anchor_prompt_handoff_report" in pattern_pack["whole_book_analysis_targets"]
    assert "short_drama_episode_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "visual_anchor_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("短剧" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("temporary scene notes" in hint for hint in pattern_pack["short_drama_story_bible_template_gate_hints"])
    assert any("Prompt handoff" in hint for hint in pattern_pack["visual_anchor_prompt_handoff_gate_hints"])
    assert any("media prompts" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "short_drama_story_bible_template_gate_hints" in digest
    assert "visual_anchor_prompt_handoff_gate_hints" in digest


def test_short_drama_character_continuity_cluster_adds_memory_worldbuilding_gates():
    assert "https://github.com/clipcurator/ai-character-continuity-kit" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/clipcurator/ai-short-drama-worldbuilding-kit" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/clipcurator/ai-short-drama-character-memory-templates" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("character continuity kit" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("short drama worldbuilding" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("character memory templates" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "clipcurator/ai-character-continuity-kit",
                "html_url": "https://github.com/clipcurator/ai-character-continuity-kit",
                "description": (
                    "AI character continuity kit for AI film, vertical drama, micro-drama, storyboard and script-to-video workflows. "
                    "Continuity dimensions include identity with name, age range, story role, archetype and first appearance; "
                    "visual anchor with face, hair, body type, clothing, palette and props; personality with desire, fear, speech style, "
                    "decision style and moral boundary; relationship map with ally, rival, family, romance and secret; and episode memory "
                    "with change, injury, promise, secret revealed and continuity note. Stable visual anchors include face, silhouette, "
                    "clothing, color palette and signature props, while flexible elements include expressions, action poses, lighting and scene wardrobe."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["character-continuity", "short-drama", "visual-consistency", "script-to-video"],
                "updated_at": "2026-06-09T12:10:00Z",
                "root_files": ["README.md", "README.zh-CN.md", "LICENSE", "docs", "templates", "data"],
            },
            {
                "full_name": "clipcurator/ai-short-drama-worldbuilding-kit",
                "html_url": "https://github.com/clipcurator/ai-short-drama-worldbuilding-kit",
                "description": (
                    "AI short drama worldbuilding kit for vertical drama, micro-drama, script-to-video and AI storyboard workflows. "
                    "Worldbuilding layers define premise, rules, locations, power map, timeline, secrets and continuity memory. "
                    "The workflow builds premise and genre promise, world rules and conflict engine, recurring locations and visual anchors, "
                    "character power relationships, secrets, reveals and episode memory before writing scripts or generating storyboards. "
                    "Social, emotional or supernatural rules prevent random plot logic, and the power map says who has power over whom."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["short-drama", "worldbuilding", "vertical-drama", "script-to-video"],
                "updated_at": "2026-06-09T12:20:00Z",
                "root_files": ["README.md", "README.zh-CN.md", "LICENSE", "docs", "templates", "data"],
            },
            {
                "full_name": "clipcurator/ai-short-drama-character-memory-templates",
                "html_url": "https://github.com/clipcurator/ai-short-drama-character-memory-templates",
                "description": (
                    "AI Short Drama Character Memory Templates for reusable character memory, relationship state, visual anchors and emotional continuity. "
                    "Memory fields include stable identity, visual anchors, relationship state, current emotional arc, scene memory and forbidden changes. "
                    "Review signals require memory fields stable across episodes, relationship changes have a source scene, visual anchors stay separate from temporary wardrobe, "
                    "and revision notes explain what changed and why before publishing, editing or generating assets."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["short-drama", "character-memory", "continuity", "visual-anchors"],
                "updated_at": "2026-06-09T12:30:00Z",
                "root_files": ["README.md", "LICENSE", "docs", "templates"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T04:10:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    continuity = candidates["clipcurator/ai-character-continuity-kit"]
    worldbuilding = candidates["clipcurator/ai-short-drama-worldbuilding-kit"]
    memory = candidates["clipcurator/ai-short-drama-character-memory-templates"]
    assert "character_continuity_dimension_schema_gate" in continuity["absorbed_patterns"]
    assert "visual_anchor_prompt_handoff_gate" in continuity["absorbed_patterns"]
    assert "short_drama_worldbuilding_layer_gate" in worldbuilding["absorbed_patterns"]
    assert "short_drama_character_memory_forbidden_change_gate" in memory["absorbed_patterns"]
    assert "visual_anchor_prompt_handoff_gate" in memory["absorbed_patterns"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "character_continuity_dimension_policy" in pattern_pack["bible_enrichment_targets"]
    assert "short_drama_worldbuilding_layer_policy" in pattern_pack["bible_enrichment_targets"]
    assert "character_memory_forbidden_change_policy" in pattern_pack["bible_enrichment_targets"]
    assert "character_continuity_dimension_report" in pattern_pack["whole_book_analysis_targets"]
    assert "short_drama_worldbuilding_layer_report" in pattern_pack["whole_book_analysis_targets"]
    assert "character_memory_forbidden_change_report" in pattern_pack["whole_book_analysis_targets"]
    assert "character_continuity_schema_remap" in pattern_pack["inspired_mapping_targets"]
    assert "worldbuilding_layer_remap" in pattern_pack["inspired_mapping_targets"]
    assert "character_memory_forbidden_change_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("identity" in hint for hint in pattern_pack["character_continuity_dimension_schema_gate_hints"])
    assert any("Forbidden changes" in hint for hint in pattern_pack["short_drama_character_memory_forbidden_change_gate_hints"])
    assert any("power map" in hint for hint in pattern_pack["short_drama_worldbuilding_layer_gate_hints"])
    assert any("power maps" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "character_continuity_dimension_schema_gate_hints" in digest
    assert "short_drama_character_memory_forbidden_change_gate_hints" in digest
    assert "short_drama_worldbuilding_layer_gate_hints" in digest


def test_short_drama_script_to_video_cluster_adds_format_storyboard_handoff_gates():
    assert "https://github.com/clipcurator/vertical-drama-script-formats" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/clipcurator/ai-storyboard-prompts" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/clipcurator/script-to-video-playbook" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/clipcurator/ai-short-drama-production-workflows" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("vertical drama script format" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("storyboard shot list" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("script to video playbook" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("ai short drama production workflows" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "clipcurator/vertical-drama-script-formats",
                "html_url": "https://github.com/clipcurator/vertical-drama-script-formats",
                "description": (
                    "Vertical drama script formats for 1-3 minute mobile-first episodes. "
                    "The episode structure separates hook, setup, escalation, turn and cliffhanger, "
                    "and the scene format records episode number, scene number, location and time, characters, "
                    "visual beat, action, dialogue, camera or framing note, continuity note and next beat. "
                    "The template checks that the hook lands in the first 3-5 seconds and each ending leaves a cliffhanger question."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["vertical-drama", "script-format", "short-drama", "script-to-video"],
                "updated_at": "2026-06-11T04:10:00Z",
                "root_files": ["README.md", "LICENSE", "docs", "templates", "data/script-format-schema.json"],
            },
            {
                "full_name": "clipcurator/ai-storyboard-prompts",
                "html_url": "https://github.com/clipcurator/ai-storyboard-prompts",
                "description": (
                    "AI storyboard prompts for character design, scene concept generation, storyboard planning, "
                    "camera movement prompts and script-to-video workflows. The script to storyboard prompt asks for "
                    "shot number, shot type, subject, action, camera angle, camera movement, visual prompt and duration estimate, "
                    "while preserving narrative clarity, emotional progression and vertical frame constraints."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "CC-BY-4.0"},
                "topics": ["storyboard", "prompts", "camera-movement", "script-to-video"],
                "updated_at": "2026-06-11T04:20:00Z",
                "root_files": ["README.md", "LICENSE", "prompts", "templates/storyboard-shot-list-template.md"],
            },
            {
                "full_name": "clipcurator/script-to-video-playbook",
                "html_url": "https://github.com/clipcurator/script-to-video-playbook",
                "description": (
                    "Script to Video Playbook for moving from idea or script to story structure, characters and scenes, "
                    "storyboard, camera movement and short video output. It defines idea-first workflow and script-first workflow, "
                    "including script ingestion, scene breakdown, character extraction, scene and prop planning, storyboard generation, "
                    "camera movement planning, video output and human review points."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "CC-BY-4.0"},
                "topics": ["script-to-video", "short-drama", "storyboard", "workflow"],
                "updated_at": "2026-06-11T04:30:00Z",
                "root_files": ["README.md", "LICENSE", "docs", "templates/script-to-video-workflow-template.md"],
            },
            {
                "full_name": "clipcurator/ai-short-drama-production-workflows",
                "html_url": "https://github.com/clipcurator/ai-short-drama-production-workflows",
                "description": (
                    "AI Short Drama Production Workflows for a connected pipeline from concept validation, worldbuilding, "
                    "character system design, outline, script, visual assets, storyboard, camera movement and short drama video. "
                    "The workflow includes script to assets extraction of characters, locations, props, time of day, emotional beats, "
                    "visual moments and dialogue-heavy scenes, plus release packaging, human review points, script coherence and video output readiness."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "CC-BY-4.0"},
                "topics": ["short-drama", "production-workflow", "script-to-assets", "storyboard-to-video"],
                "updated_at": "2026-06-11T04:40:00Z",
                "root_files": ["README.md", "LICENSE", "docs", "templates/short-drama-project-bible.md"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T05:05:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    script_format = candidates["clipcurator/vertical-drama-script-formats"]
    storyboard = candidates["clipcurator/ai-storyboard-prompts"]
    playbook = candidates["clipcurator/script-to-video-playbook"]
    production = candidates["clipcurator/ai-short-drama-production-workflows"]
    assert "vertical_drama_script_format_gate" in script_format["absorbed_patterns"]
    assert "storyboard_shot_list_prompt_gate" in storyboard["absorbed_patterns"]
    assert "script_to_video_workflow_handoff_gate" in playbook["absorbed_patterns"]
    assert "short_drama_production_stage_gate" in production["absorbed_patterns"]
    assert script_format["license"] == "MIT"
    assert storyboard["license"] == "CC-BY-4.0"

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "vertical_drama_episode_format_policy" in pattern_pack["bible_enrichment_targets"]
    assert "storyboard_shot_list_prompt_policy" in pattern_pack["bible_enrichment_targets"]
    assert "script_to_video_handoff_policy" in pattern_pack["bible_enrichment_targets"]
    assert "short_drama_production_stage_policy" in pattern_pack["bible_enrichment_targets"]
    assert "vertical_drama_script_format_report" in pattern_pack["whole_book_analysis_targets"]
    assert "storyboard_shot_list_prompt_report" in pattern_pack["whole_book_analysis_targets"]
    assert "script_to_video_handoff_report" in pattern_pack["whole_book_analysis_targets"]
    assert "short_drama_production_stage_report" in pattern_pack["whole_book_analysis_targets"]
    assert "vertical_episode_format_remap" in pattern_pack["inspired_mapping_targets"]
    assert "storyboard_shot_function_remap" in pattern_pack["inspired_mapping_targets"]
    assert "script_to_video_stage_handoff_remap" in pattern_pack["inspired_mapping_targets"]
    assert "production_stage_gate_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("first 3-5 seconds" in hint for hint in pattern_pack["vertical_drama_script_format_gate_hints"])
    assert any("story-carrying shots" in hint for hint in pattern_pack["storyboard_shot_list_prompt_gate_hints"])
    assert any("idea-first or script-first" in hint for hint in pattern_pack["script_to_video_workflow_handoff_gate_hints"])
    assert any("Release readiness" in hint for hint in pattern_pack["short_drama_production_stage_gate_hints"])
    assert any("竖屏短剧" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("shot lists" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("source shot order" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "vertical_drama_script_format_gate_hints" in digest
    assert "storyboard_shot_list_prompt_gate_hints" in digest
    assert "script_to_video_workflow_handoff_gate_hints" in digest
    assert "short_drama_production_stage_gate_hints" in digest


def test_short_drama_shot_hook_pack_sources_add_reusable_visual_gates():
    assert "https://github.com/clipcurator/ai-drama-shot-list-templates" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/clipcurator/vertical-drama-hook-templates" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/clipcurator/ai-short-drama-storyboard-shot-packs" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("ai drama shot list templates" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("vertical drama hook templates" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("storyboard shot packs" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "clipcurator/ai-drama-shot-list-templates",
                "html_url": "https://github.com/clipcurator/ai-drama-shot-list-templates",
                "description": (
                    "AI Drama Shot List Templates translate scripts into camera-ready and storyboard-ready production notes. "
                    "Shot list fields include scene, shot number, character, visual beat, shot size, camera movement, emotion and continuity note. "
                    "Camera patterns include slow push-in for realization, over-the-shoulder for confrontation, close-up insert for clue props, "
                    "handheld follow for panic and static wide shot for power distance or isolation. The shot list schema keeps duration, shot size and continuity reusable."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["shot-list", "short-drama", "camera-movement", "script-to-video"],
                "updated_at": "2026-06-11T05:10:00Z",
                "root_files": ["README.md", "LICENSE", "docs", "templates", "data/shot-list-schema.json"],
            },
            {
                "full_name": "clipcurator/vertical-drama-hook-templates",
                "html_url": "https://github.com/clipcurator/vertical-drama-hook-templates",
                "description": (
                    "Vertical Drama Hook Templates provide reusable first-five-second hooks, emotional reversals and cliffhanger openings. "
                    "Hook families include shock reveal, status reversal, secret exposure, forbidden choice, visual contradiction and countdown pressure. "
                    "Template fields track opening image, first spoken line, conflict signal, reversal beat, cliffhanger question and storyboard note, "
                    "with review before publishing, editing or generating assets."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["vertical-drama", "hooks", "cliffhanger", "short-drama"],
                "updated_at": "2026-06-11T05:20:00Z",
                "root_files": ["README.md", "README.zh-CN.md", "LICENSE", "docs/hook-patterns.md", "templates"],
            },
            {
                "full_name": "clipcurator/ai-short-drama-storyboard-shot-packs",
                "html_url": "https://github.com/clipcurator/ai-short-drama-storyboard-shot-packs",
                "description": (
                    "AI Short Drama Storyboard Shot Packs provide reusable storyboard and shot-list packs for turning short drama scripts into visual AI production prompts. "
                    "Shot pack types include cold-open tension pack, dialogue power shift pack, reveal and reaction pack, romance close-up pack and cliffhanger ending pack. "
                    "Storyboard fields include scene objective, frame composition, character emotion, camera movement, continuity risk and generation prompt, "
                    "with a review checklist for vertical-safe framing, character continuity, readable emotion, clear object focus and episode-to-episode continuity."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["storyboard", "shot-pack", "short-drama", "visual-prompts"],
                "updated_at": "2026-06-11T05:30:00Z",
                "root_files": ["README.md", "README.zh-CN.md", "LICENSE", "templates"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T05:40:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    shot_list = candidates["clipcurator/ai-drama-shot-list-templates"]
    hooks = candidates["clipcurator/vertical-drama-hook-templates"]
    packs = candidates["clipcurator/ai-short-drama-storyboard-shot-packs"]
    assert "drama_shot_list_camera_pattern_gate" in shot_list["absorbed_patterns"]
    assert "storyboard_shot_list_prompt_gate" in shot_list["absorbed_patterns"]
    assert "vertical_hook_cliffhanger_template_gate" in hooks["absorbed_patterns"]
    assert "storyboard_shot_pack_reuse_gate" in packs["absorbed_patterns"]
    assert shot_list["license"] == "MIT"
    assert hooks["license"] == "MIT"
    assert packs["license"] == "MIT"

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "drama_shot_list_schema_policy" in pattern_pack["bible_enrichment_targets"]
    assert "vertical_hook_template_policy" in pattern_pack["bible_enrichment_targets"]
    assert "storyboard_shot_pack_policy" in pattern_pack["bible_enrichment_targets"]
    assert "drama_shot_list_schema_report" in pattern_pack["whole_book_analysis_targets"]
    assert "vertical_hook_template_report" in pattern_pack["whole_book_analysis_targets"]
    assert "storyboard_shot_pack_reuse_report" in pattern_pack["whole_book_analysis_targets"]
    assert "shot_list_camera_pattern_remap" in pattern_pack["inspired_mapping_targets"]
    assert "hook_family_question_remap" in pattern_pack["inspired_mapping_targets"]
    assert "shot_pack_scene_function_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("slow push-in" in hint for hint in pattern_pack["drama_shot_list_camera_pattern_gate_hints"])
    assert any("first five seconds" in hint for hint in pattern_pack["vertical_hook_cliffhanger_template_gate_hints"])
    assert any("cold-open tension" in hint for hint in pattern_pack["storyboard_shot_pack_reuse_gate_hints"])
    assert any("first-five-second question" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("source frame composition" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "drama_shot_list_camera_pattern_gate_hints" in digest
    assert "vertical_hook_cliffhanger_template_gate_hints" in digest
    assert "storyboard_shot_pack_reuse_gate_hints" in digest


def test_novel_template_source_adds_ideation_worksheet_foundation_gates():
    assert "https://github.com/10Legs/novel-template" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("ideation worksheets" in query and "Ghost/Lie/Want/Need" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "10Legs/novel-template",
                "html_url": "https://github.com/10Legs/novel-template",
                "description": (
                    "Claude Code harness for writing novels from blank page to finished manuscript. "
                    "It guides ideation, outlining, drafting, revision and final polish with "
                    "10 specialized agents, 16 slash commands, 9 craft skill knowledge bases, "
                    "automated workflow hooks and 5 ideation worksheets. The worksheets cover "
                    "premise discovery, character genesis using Ghost/Lie/Want/Need, world building, "
                    "structure blueprint and theme discovery. The /ideate flow is non-skippable, "
                    "asks for options and craft patterns, tracks continuity and does not write the novel."
                ),
                "stargazers_count": 3,
                "forks_count": 0,
                "license": None,
                "topics": ["novel", "claude-code", "writing-harness", "ideation"],
                "updated_at": "2026-06-10T21:48:32Z",
                "root_files": [
                    "README.md",
                    "CLAUDE.md",
                    "ideation/01-premise-discovery.md",
                    "ideation/02-character-genesis.md",
                    "ideation/03-world-building.md",
                    "ideation/04-structure-blueprint.md",
                    "ideation/05-theme-discovery.md",
                    ".claude/agents",
                    ".claude/commands",
                    ".claude/skills",
                    ".claude/hooks",
                ],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T00:15:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    template = candidates["10Legs/novel-template"]
    assert "ideation_worksheet_foundation_gate" in template["absorbed_patterns"]
    assert "skill_install_surface" in template["risk_flags"]
    assert "license:missing" in template["trust_review"]["flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "ideation_worksheet_policy" in pattern_pack["bible_enrichment_targets"]
    assert "premise_theme_question_contract" in pattern_pack["bible_enrichment_targets"]
    assert "ideation_worksheet_completion_report" in pattern_pack["whole_book_analysis_targets"]
    assert "premise_character_world_structure_theme_matrix" in pattern_pack["whole_book_analysis_targets"]
    assert "worksheet_to_outline_gap_questions" in pattern_pack["whole_book_analysis_targets"]
    assert "ideation_worksheet_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("worksheet ids" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("foundation worksheet" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("filled once" in hint for hint in pattern_pack["ideation_worksheet_foundation_gate_hints"])
    assert any("source worksheets" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("Ghost/Lie/Want/Need grid" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "ideation_worksheet_foundation_gate_hints" in digest



def test_inkos_source_adds_confirmed_action_audit_recovery_gates():
    assert "https://github.com/Narcooo/inkos" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("37-dimension audit" in query and "JSON Delta" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "Narcooo/inkos",
                "html_url": "https://github.com/Narcooo/inkos",
                "description": (
                    "InkOS is a local AI creation system for long-form novels, fan fiction, "
                    "style imitation, continuation, and interactive worlds. Studio Chat, CLI, "
                    "and TUI share an action surface; heavy actions require confirmation, "
                    "completion is based on real tool results, context is protected / compressible, "
                    "the Continuity Auditor runs a 37-dimension audit, at most one automatic "
                    "revision pass is allowed, unresolved critical findings remain visible, "
                    "the Writer emits a pre-write checklist and post-write settlement table, "
                    "automatic state snapshots support rollback, file locking prevents concurrent "
                    "writes, provider API keys and custom endpoints are configured by users, "
                    "and JSON deltas go through applyRuntimeStateDelta and validateRuntimeState."
                ),
                "stargazers_count": 7110,
                "forks_count": 1344,
                "license": {"spdx_id": "AGPL-3.0"},
                "topics": ["ai-novel-writing", "novel-generator", "creative-writing-ai", "openclaw-skill"],
                "updated_at": "2026-06-10T23:19:22Z",
                "root_files": [
                    "README.md",
                    "README.en.md",
                    "LICENSE",
                    "package.json",
                    "pnpm-lock.yaml",
                    "skills/SKILL.md",
                    ".env.example",
                    "scripts",
                ],
                "package_scripts": {
                    "build": "pnpm -r build",
                    "dev": "pnpm -r --parallel dev",
                    "test": "pnpm -r test",
                    "release": "pnpm build && pnpm test",
                },
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T09:10:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    inkos = candidates["Narcooo/inkos"]
    assert "confirmed_action_audit_recovery_gate" in inkos["absorbed_patterns"]
    assert "same_type_creation" in inkos["absorbed_patterns"]
    assert "schema_validated_state_delta" in inkos["absorbed_patterns"]
    assert "memory_snapshot_versioning" in inkos["absorbed_patterns"]
    assert "provider_key_surface" in inkos["risk_flags"]
    assert "skill_install_surface" in inkos["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "confirmed_action_surface_policy" in pattern_pack["bible_enrichment_targets"]
    assert "audit_revision_recovery_policy" in pattern_pack["bible_enrichment_targets"]
    assert "action_confirmation_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "pre_write_checklist" in pattern_pack["whole_book_analysis_targets"]
    assert "unresolved_critical_findings_queue" in pattern_pack["whole_book_analysis_targets"]
    assert "immutable_state_delta_validation" in pattern_pack["whole_book_analysis_targets"]
    assert "confirmed_action_recovery_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("confirmed action" in hint for hint in pattern_pack["confirmed_action_audit_recovery_gate_hints"])
    assert any("completion must come from artifacts" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("unresolved critical findings" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("action/audit contract" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("revision debt" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "confirmed_action_audit_recovery_gate_hints" in digest


def test_static_project_isolated_story_bible_query_sources_add_query_gates():
    assert "https://github.com/fidelnamisi/story-bible-assistant" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/byteyilabs/novellis-app" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("project-based isolation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("local-first narrative ai" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "fidelnamisi/story-bible-assistant",
                "html_url": "https://github.com/fidelnamisi/story-bible-assistant",
                "description": (
                    "Story Bible Assistant is a local web app for writers that queries source files "
                    "across multiple story projects using AI. Each project is isolated, files never mix, "
                    "reads fresh on every query, no database, live file stats, TXT/MD/DOCX/PDF support, "
                    "120000 character truncation and DeepSeek API boundary."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["story-bible", "writing-assistant", "local"],
                "updated_at": "2026-03-09T09:45:43Z",
                "root_files": ["README.md", "LICENSE", "server.js", "public", "projects"],
            },
            {
                "full_name": "byteyilabs/novellis-app",
                "html_url": "https://github.com/byteyilabs/novellis-app",
                "description": (
                    "Novellis is a privacy-first local-LLM narrative workspace with local-first narrative AI, "
                    "manuscript ingestion, narrative intelligence, timeline visualization, visual knowledge graph, "
                    "AI copilot, Ollama offline mode and optional cloud providers."
                ),
                "stargazers_count": 2,
                "forks_count": 0,
                "license": None,
                "topics": ["worldbuilding", "knowledge-graph", "local-llm"],
                "updated_at": "2026-01-04T20:19:44Z",
                "root_files": ["README.md", "package.json", "src"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-12T10:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    story_bible = candidates["fidelnamisi/story-bible-assistant"]
    novellis = candidates["byteyilabs/novellis-app"]
    assert "project_isolated_story_bible_query_gate" in story_bible["absorbed_patterns"]
    assert "project_isolated_story_bible_query_gate" in novellis["absorbed_patterns"]
    assert "license:missing" in novellis["trust_review"]["flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "project_isolated_story_query_policy" in pattern_pack["bible_enrichment_targets"]
    assert "story_query_material_manifest" in pattern_pack["bible_enrichment_targets"]
    assert "project_isolated_query_manifest" in pattern_pack["whole_book_analysis_targets"]
    assert "story_bible_answer_grounding_report" in pattern_pack["whole_book_analysis_targets"]
    assert "project_isolated_story_bible_query_gate_hints" in pattern_pack
    assert "project_isolated_story_query_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("query manifest" in hint for hint in pattern_pack["project_isolated_story_bible_query_gate_hints"])
    assert any("source-file manifest" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("scoped evidence cards" in hint for hint in pattern_pack["inspired_transformation_hints"])
    assert any("provider payload boundary" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "project_isolated_story_bible_query_gate_hints" in digest


def test_static_work_dna_and_governed_reading_sources_add_continuation_gates():
    assert "https://github.com/Shiaoming123/works-dna-extractor" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/xjxjdnsnak-cell/novel-reader" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("works dna" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("full_scope_allowed" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "Shiaoming123/works-dna-extractor",
                "html_url": "https://github.com/Shiaoming123/works-dna-extractor",
                "description": (
                    "Works DNA Extractor extracts operational Work DNA from fiction: "
                    "narrative engine, POV, scene architecture, language texture, "
                    "dialogue system, emotional algorithm, information control, "
                    "character grammar, style transfer, quality evaluation and fit repair. "
                    "It guides continuation and rewriting by method rather than surface wording."
                ),
                "stargazers_count": 2,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["ai-writing", "novel", "style-transfer", "skill"],
                "updated_at": "2026-05-24T12:18:34Z",
                "root_files": ["README.md", "LICENSE", "SKILL.md", ".claude/skills"],
            },
            {
                "full_name": "xjxjdnsnak-cell/novel-reader",
                "html_url": "https://github.com/xjxjdnsnak-cell/novel-reader",
                "description": (
                    "Novel Reader provides governed full reading with read-session, "
                    "required_coverage_complete, finalized, full_scope_allowed, "
                    "L1/L2/L3 coverage, source-grounded evidence, style evidence, "
                    "future-plot prediction packets and continuation packages."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": None,
                "topics": ["novel", "reading", "continuation", "claude-code"],
                "updated_at": "2026-05-28T03:57:57Z",
                "root_files": ["README.md", "bin", "novel_reader"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T08:35:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    work_dna = candidates["Shiaoming123/works-dna-extractor"]
    novel_reader = candidates["xjxjdnsnak-cell/novel-reader"]
    assert "work_dna_method_transfer_eval_gate" in work_dna["absorbed_patterns"]
    assert "governed_full_reading_continuation_gate" in novel_reader["absorbed_patterns"]
    assert "skill_install_surface" in work_dna["risk_flags"]
    assert "license:missing" in novel_reader["trust_review"]["flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "work_dna_method_profile" in pattern_pack["bible_enrichment_targets"]
    assert "work_dna_transfer_eval_policy" in pattern_pack["bible_enrichment_targets"]
    assert "governed_reading_coverage_policy" in pattern_pack["bible_enrichment_targets"]
    assert "full_scope_continuation_package_policy" in pattern_pack["bible_enrichment_targets"]
    assert "work_dna_extraction_report" in pattern_pack["whole_book_analysis_targets"]
    assert "work_dna_fit_repair_report" in pattern_pack["whole_book_analysis_targets"]
    assert "reading_session_coverage_matrix" in pattern_pack["whole_book_analysis_targets"]
    assert "full_scope_continuation_readiness_report" in pattern_pack["whole_book_analysis_targets"]
    assert "work_dna_method_remap" in pattern_pack["inspired_mapping_targets"]
    assert "governed_reading_continuation_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("method axes" in hint for hint in pattern_pack["work_dna_method_transfer_eval_gate_hints"])
    assert any("full_scope_allowed" in hint for hint in pattern_pack["governed_full_reading_continuation_gate_hints"])
    assert any("work-DNA axes" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("full_scope_allowed" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("source prose" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("full_scope_allowed" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "work_dna_method_transfer_eval_gate_hints" in digest
    assert "governed_full_reading_continuation_gate_hints" in digest


def test_static_gamebook_and_forensic_style_sources_add_branching_copy_risk_gates():
    assert "https://github.com/alanl1234/gamebook" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/TABARC-Code/Forensic-Writing-Style-Analysis-Cloning-Claude-Skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("interactive gamebook" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("forensic style auditor" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "alanl1234/gamebook",
                "html_url": "https://github.com/alanl1234/gamebook",
                "description": (
                    "Gamebook transforms any document into an interactive gamebook with "
                    "chapter structure parsing, character extraction, style fingerprint, "
                    "game structure, chapter cards, branching choices, multiple endings, "
                    "save points, game state, and variable consequences."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["gamebook", "interactive-fiction", "ai-skill", "branching"],
                "updated_at": "2026-06-03T18:42:09Z",
                "root_files": ["README.md", "LICENSE", ".claude/skills", "SKILL.md"],
            },
            {
                "full_name": "TABARC-Code/Forensic-Writing-Style-Analysis-Cloning-Claude-Skill",
                "html_url": "https://github.com/TABARC-Code/Forensic-Writing-Style-Analysis-Cloning-Claude-Skill",
                "description": (
                    "Forensic Style Auditor performs forensic writing style analysis and cloning. "
                    "It reverse-engineers any writer using ten forensic dimensions including "
                    "sentence architecture, burstiness, paragraph cadence, lexical fingerprints, "
                    "dialogue mechanics, clone key, drifted style checks, old/new rule pairs, "
                    "and a pre-delivery checklist for continuation scenes."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["claude-skill", "style-analysis", "forensic-writing", "writing"],
                "updated_at": "2026-05-10T21:39:36Z",
                "root_files": ["README.md", "LICENSE", ".claude/skills", "SKILL.md"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T09:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    gamebook = candidates["alanl1234/gamebook"]
    forensic = candidates["TABARC-Code/Forensic-Writing-Style-Analysis-Cloning-Claude-Skill"]
    assert "document_gamebook_branching_adapter_gate" in gamebook["absorbed_patterns"]
    assert "forensic_style_clone_audit_risk_gate" in forensic["absorbed_patterns"]
    assert "skill_install_surface" in gamebook["risk_flags"]
    assert "skill_install_surface" in forensic["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "branching_adaptation_contract" in pattern_pack["bible_enrichment_targets"]
    assert "interactive_state_schema_policy" in pattern_pack["bible_enrichment_targets"]
    assert "forensic_style_dimension_policy" in pattern_pack["bible_enrichment_targets"]
    assert "style_clone_consent_boundary" in pattern_pack["bible_enrichment_targets"]
    assert "chapter_branch_card_report" in pattern_pack["whole_book_analysis_targets"]
    assert "choice_consequence_state_matrix" in pattern_pack["whole_book_analysis_targets"]
    assert "forensic_style_dimension_audit_report" in pattern_pack["whole_book_analysis_targets"]
    assert "clone_drift_risk_review" in pattern_pack["whole_book_analysis_targets"]
    assert "document_gamebook_branching_remap" in pattern_pack["inspired_mapping_targets"]
    assert "forensic_style_dimension_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("chapter cards" in hint for hint in pattern_pack["document_gamebook_branching_adapter_gate_hints"])
    assert any("voice cloning" in hint for hint in pattern_pack["forensic_style_clone_audit_risk_gate_hints"])
    assert any("branching adaptation" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("no-clone boundary" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("branch choice ids" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("consent/license posture" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("named-author clone" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("voice clone" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "document_gamebook_branching_adapter_gate_hints" in digest
    assert "forensic_style_clone_audit_risk_gate_hints" in digest


def test_static_narrative_engine_and_storyforge_sources_add_import_consequence_gates():
    assert "https://github.com/scslmd/Narrative-Engine" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/Ikyletwar/StoryForge-AI" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("storytelling DNA" in query for query in DEFAULT_GITHUB_QUERIES)
    assert any("Consequence Ledger" in query for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "scslmd/Narrative-Engine",
                "html_url": "https://github.com/scslmd/Narrative-Engine",
                "description": (
                    "Narrative Engine supports story import from existing completed stories, "
                    "multi-pass story import, guided setup wizard, pattern extraction of "
                    "storytelling DNA, canon-congruent sequels or alternates, "
                    "Same World / New Characters / Transposed generation modes, "
                    "selection-aware manuscript assist, version conflict protection, "
                    "structured revision passes, and promote draft to manuscript workflows."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["novel", "story-import", "revision", "local-models"],
                "updated_at": "2026-05-31T08:22:30Z",
                "root_files": ["README.md", "package.json", "backend", "frontend"],
            },
            {
                "full_name": "Ikyletwar/StoryForge-AI",
                "html_url": "https://github.com/Ikyletwar/StoryForge-AI",
                "description": (
                    "StoryForge-AI uses Story Bible + Consequence Ledger + Narasi Terakhir. "
                    "It tracks storyState, continuation turn context, five latest consequences, "
                    "thirty-entry consequence ledger, Last 8 Actions, current character status, "
                    "auto-save, and periodic story bible compression."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["interactive-story", "story-bible", "consequence-ledger"],
                "updated_at": "2026-03-21T04:48:49Z",
                "root_files": ["README.md", "LICENSE", "index.html"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T10:05:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    narrative_engine = candidates["scslmd/Narrative-Engine"]
    storyforge = candidates["Ikyletwar/StoryForge-AI"]
    assert "story_import_pattern_revision_gate" in narrative_engine["absorbed_patterns"]
    assert "consequence_ledger_last_actions_context_gate" in storyforge["absorbed_patterns"]
    assert "license:missing" in narrative_engine["trust_review"]["flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "source_story_import_policy" in pattern_pack["bible_enrichment_targets"]
    assert "pattern_extraction_revision_policy" in pattern_pack["bible_enrichment_targets"]
    assert "turn_context_consequence_policy" in pattern_pack["bible_enrichment_targets"]
    assert "last_actions_state_compression_policy" in pattern_pack["bible_enrichment_targets"]
    assert "source_story_import_pass_report" in pattern_pack["whole_book_analysis_targets"]
    assert "pattern_extraction_revision_conflict_report" in pattern_pack["whole_book_analysis_targets"]
    assert "consequence_ledger_turn_context_report" in pattern_pack["whole_book_analysis_targets"]
    assert "last_actions_compression_drift_report" in pattern_pack["whole_book_analysis_targets"]
    assert "story_import_pattern_mode_remap" in pattern_pack["inspired_mapping_targets"]
    assert "consequence_ledger_turn_context_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("Import existing stories" in hint for hint in pattern_pack["story_import_pattern_revision_gate_hints"])
    assert any("bounded consequence ledger" in hint for hint in pattern_pack["consequence_ledger_last_actions_context_gate_hints"])
    assert any("story import pass ids" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("last action window" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("version conflict findings" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("story bible checksum" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("generation mode" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("last-action window" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("alternates overwrite accepted canon" in hint for hint in pattern_pack["inspired_copy_risk_hints"])
    assert any("save/snapshot id" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "story_import_pattern_revision_gate_hints" in digest
    assert "consequence_ledger_last_actions_context_gate_hints" in digest



def test_static_creative_writing_assistant_source_adds_multiaxis_provider_gate():
    assert "https://github.com/kernullist/creative-writing-assistant" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("literary depth" in query.lower() and "style simulation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "kernullist/creative-writing-assistant",
                "html_url": "https://github.com/kernullist/creative-writing-assistant",
                "description": (
                    "Creative Writing Assistant analyzes style, literary depth, genre classification, "
                    "plot development, style simulation, multi-chapter novel generation with SSE progress, "
                    "language selection, exports, REST API, CLI, multiple providers and API keys."
                ),
                "stargazers_count": 0,
                "forks_count": 1,
                "license": {"spdx_id": "MIT"},
                "topics": ["creative-writing", "style-analysis", "novel-generation"],
                "updated_at": "2026-04-20T04:46:03Z",
                "root_files": ["README.md", "LICENSE", ".env.example", "requirements.txt", "src", "web_app.py", "tests"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T09:10:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    creative = candidates["kernullist/creative-writing-assistant"]
    assert "creative_writing_multiaxis_provider_gate" in creative["absorbed_patterns"]
    assert "provider_key_surface" in creative["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "creative_writing_axis_toggle_policy" in pattern_pack["bible_enrichment_targets"]
    assert "provider_language_export_boundary" in pattern_pack["bible_enrichment_targets"]
    assert "creative_writing_axis_analysis_report" in pattern_pack["whole_book_analysis_targets"]
    assert "provider_language_export_boundary_report" in pattern_pack["whole_book_analysis_targets"]
    assert "creative_writing_axis_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("enabled axes" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("selected analysis axes" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("Separate writing analysis axes" in hint for hint in pattern_pack["creative_writing_multiaxis_provider_gate_hints"])
    assert any("style simulation" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "creative_writing_multiaxis_provider_gate_hints" in digest


def test_static_meridians_source_adds_system_world_fate_simulation_gate():
    assert "https://github.com/jasonyu0100/meridians" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("force fields" in query.lower() and "narrative simulation" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "jasonyu0100/meridians",
                "html_url": "https://github.com/jasonyu0100/meridians",
                "description": (
                    "Meridians turns long-form text into a typed, queryable, simulatable knowledge structure. "
                    "It extracts actors, locations, artifacts, threads, and system rules, then uses System, World, "
                    "and Fate force fields with deterministic formulas, force trajectories, pacing fingerprints, "
                    "prose profiles, phase graph, causal reasoning graph, scene structures, beat plans, and prose. "
                    "State and embeddings live in IndexedDB and setup references OpenRouter API key, OpenAI API key, "
                    "and Replicate API token."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["narrative-simulation", "knowledge-graph", "creative-writing"],
                "updated_at": "2026-06-10T04:55:42Z",
                "root_files": ["README.md", "LICENSE", "package.json", ".env.example", "src", "public"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T09:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    meridians = candidates["jasonyu0100/meridians"]
    assert "system_world_fate_simulation_gate" in meridians["absorbed_patterns"]
    assert "provider_key_surface" in meridians["risk_flags"]
    assert "browser_storage_surface" in meridians["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "system_world_fate_force_field_policy" in pattern_pack["bible_enrichment_targets"]
    assert "typed_story_graph_delta_schema" in pattern_pack["bible_enrichment_targets"]
    assert "system_world_fate_force_field_report" in pattern_pack["whole_book_analysis_targets"]
    assert "phase_crg_scene_beat_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "force_field_topology_remap" in pattern_pack["inspired_mapping_targets"]
    assert "typed_story_graph_schema_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("System/World/Fate force-field snapshot" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("typed graph nodes" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("typed graph" in hint for hint in pattern_pack["system_world_fate_simulation_gate_hints"])
    assert any("abstract System/World/Fate pressure topology" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("source force-field graph" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "system_world_fate_simulation_gate_hints" in digest


def test_static_writeassist_source_adds_constraint_harness_review_worktree_gate():
    assert "https://github.com/justinjorgensen/writeassist" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("harness-level enforcement" in query.lower() and "pretooluse" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "justinjorgensen/writeassist",
                "html_url": "https://github.com/justinjorgensen/writeassist",
                "description": (
                    "WriteAssist is a constraint-driven multi-agent writing framework for Claude Code. "
                    "It uses harness-level enforcement with a PreToolUse guard and final scanner, "
                    "least-privilege reviewers limited to Read, Grep, Glob, creator/reviewer separation, "
                    "isolated auditable revision passes in git worktree branches, auto-revise-chapter, "
                    "review-chapter parallel named-agent review with seven gating critics and a four-tier rubric, "
                    "plus import-book conflict ledger recovery for existing drafts."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["creative-writing", "claude-code", "review"],
                "updated_at": "2026-06-09T21:16:57Z",
                "root_files": ["README.md", "LICENSE", "CLAUDE.md", ".claude/scripts/em-dash-guard.sh"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T09:35:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    writeassist = candidates["justinjorgensen/writeassist"]
    assert "constraint_harness_review_worktree_gate" in writeassist["absorbed_patterns"]
    assert "shell_hook_surface" in writeassist["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "author_constraint_harness_policy" in pattern_pack["bible_enrichment_targets"]
    assert "least_privilege_reviewer_role_policy" in pattern_pack["bible_enrichment_targets"]
    assert "isolated_revision_worktree_policy" in pattern_pack["bible_enrichment_targets"]
    assert "constraint_gate_violation_report" in pattern_pack["whole_book_analysis_targets"]
    assert "least_privilege_reviewer_role_report" in pattern_pack["whole_book_analysis_targets"]
    assert "isolated_revision_worktree_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "parallel_critic_panel_report" in pattern_pack["whole_book_analysis_targets"]
    assert "import_conflict_ledger_report" in pattern_pack["whole_book_analysis_targets"]
    assert "constraint_rubric_remap" in pattern_pack["inspired_mapping_targets"]
    assert "reviewer_role_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "isolated_revision_branch_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("hard author constraints" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("reviewer role/tool boundary" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("deterministic pre-write and final-state gates" in hint for hint in pattern_pack["constraint_harness_review_worktree_gate_hints"])
    assert any("upstream hooks or command text" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("project-native checklists" in hint for hint in pattern_pack["inspired_transformation_hints"])
    assert any("prompt wording" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "constraint_harness_review_worktree_gate_hints" in digest


def test_static_claude_book_source_adds_state_current_reviewer_loop_gate():
    assert "https://github.com/ThomasHoussin/Claude-Book" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("state/current" in query.lower() and "perplexity-improver" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "ThomasHoussin/Claude-Book",
                "html_url": "https://github.com/ThomasHoussin/Claude-Book",
                "description": (
                    "Claude Book Framework uses a permanent bible and transient state/current symlink. "
                    "It analyzes source books with book-analyzer, merges bibles, generates original storylines, "
                    "then orchestrates planner, writer, perplexity-improver, style-linter, character-reviewer, "
                    "continuity-reviewer, and state-updater. Failed gates loop the writer with reports for max 3 iterations. "
                    "State is archived as state/chapter-NN and appended into timeline/history."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": {"spdx_id": "MIT"},
                "topics": ["novel", "claude-code", "multi-agent"],
                "updated_at": "2025-11-12T15:06:20Z",
                "root_files": ["README.md", "LICENSE", "CLAUDE.md", ".claude/skills", ".claude/agents", "ebook/build-ebook.ps1"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T10:20:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    claude_book = candidates["ThomasHoussin/Claude-Book"]
    assert "state_current_reviewer_loop_gate" in claude_book["absorbed_patterns"]
    assert "skill_install_surface" in claude_book["risk_flags"]
    assert "powershell_script" in claude_book["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "permanent_bible_transient_state_policy" in pattern_pack["bible_enrichment_targets"]
    assert "state_current_chapter_snapshot_policy" in pattern_pack["bible_enrichment_targets"]
    assert "post_chapter_reviewer_loop_policy" in pattern_pack["bible_enrichment_targets"]
    assert "state_current_continuity_report" in pattern_pack["whole_book_analysis_targets"]
    assert "chapter_snapshot_delta_report" in pattern_pack["whole_book_analysis_targets"]
    assert "perplexity_cliche_style_lint_report" in pattern_pack["whole_book_analysis_targets"]
    assert "character_continuity_reviewer_loop_report" in pattern_pack["whole_book_analysis_targets"]
    assert "timeline_history_append_report" in pattern_pack["whole_book_analysis_targets"]
    assert "bible_state_boundary_remap" in pattern_pack["inspired_mapping_targets"]
    assert "chapter_reviewer_loop_remap" in pattern_pack["inspired_mapping_targets"]
    assert "timeline_snapshot_delta_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("accepted bible separately from transient state/current facts" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("state/current input checksum" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("permanent bible material separate" in hint for hint in pattern_pack["state_current_reviewer_loop_gate_hints"])
    assert any("source state/current facts" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("local continuation packets" in hint for hint in pattern_pack["inspired_transformation_hints"])
    assert any("snapshot delta" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "state_current_reviewer_loop_gate_hints" in digest


def test_static_novelforge_ai_source_adds_versioned_scene_fact_review_pipeline_gate():
    assert "https://github.com/hayrgpt-rgb/NovelForge-AI" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("scene cards" in query.lower() and "reviewreports" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "hayrgpt-rgb/NovelForge-AI",
                "html_url": "https://github.com/hayrgpt-rgb/NovelForge-AI",
                "description": (
                    "NovelForge AI is a version-safe, traceable AI generation platform. "
                    "Its pipeline is idea -> story bible -> full outline -> chapter outline -> scene cards -> "
                    "scene draft -> fact extraction -> review -> revision -> memory update -> export. "
                    "It uses AI scene draft jobs, SceneVersion records, accept/archive controls, side-by-side version viewing, "
                    "fact approval/rejection, memory chunk creation, focused fact/memory/reference-asset/state retrieval, "
                    "persistent continuity reports, multi-pass editorial ReviewReports, Story State ledger, Canon dashboard, "
                    "accepted-version Markdown export, Pydantic schemas, Docker Compose, PostgreSQL, Redis, RQ, OpenAI API keys."
                ),
                "stargazers_count": 0,
                "forks_count": 0,
                "license": None,
                "topics": ["novel", "scene-cards", "continuity"],
                "updated_at": "2026-06-11T11:10:00Z",
                "root_files": ["README.md", "AGENTS.md", "docker-compose.yml", ".env.example", "backend", "frontend"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T11:15:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    novelforge = candidates["hayrgpt-rgb/NovelForge-AI"]
    assert "versioned_scene_fact_review_pipeline_gate" in novelforge["absorbed_patterns"]
    assert "license:missing" in novelforge["trust_review"]["flags"]
    assert "docker" in novelforge["risk_flags"]
    assert "provider_key_surface" in novelforge["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "version_safe_scene_draft_policy" in pattern_pack["bible_enrichment_targets"]
    assert "fact_approval_memory_update_policy" in pattern_pack["bible_enrichment_targets"]
    assert "review_report_export_readiness_policy" in pattern_pack["bible_enrichment_targets"]
    assert "scene_version_lineage_report" in pattern_pack["whole_book_analysis_targets"]
    assert "fact_extraction_approval_report" in pattern_pack["whole_book_analysis_targets"]
    assert "memory_chunk_retrieval_trace" in pattern_pack["whole_book_analysis_targets"]
    assert "continuity_reviewreport_findings" in pattern_pack["whole_book_analysis_targets"]
    assert "canon_dashboard_export_readiness_report" in pattern_pack["whole_book_analysis_targets"]
    assert "scene_version_lineage_remap" in pattern_pack["inspired_mapping_targets"]
    assert "fact_memory_approval_remap" in pattern_pack["inspired_mapping_targets"]
    assert "canon_dashboard_review_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("scene-card id" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("scene version lineage" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("Fact extraction is not automatic canon" in hint for hint in pattern_pack["versioned_scene_fact_review_pipeline_gate_hints"])
    assert any("scene-card schema" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("approved fact deltas" in hint for hint in pattern_pack["inspired_transformation_hints"])
    assert any("unapproved extracted facts" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "versioned_scene_fact_review_pipeline_gate_hints" in digest


def test_static_style_axis_and_local_editor_sources_add_voice_block_revision_gates():
    assert "https://github.com/viktorbezdek/definitive-llm-writing-style-guide" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jpotts18/stylometry" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/egonSchiele/chisel" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("llm writing style" in query.lower() and "style dimensions" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("stylometry" in query.lower() and "feature extraction" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
    assert any("local writing app" in query.lower() and "chapter blocks" in query.lower() for query in DEFAULT_GITHUB_QUERIES)

    service = NovelSourceDiscoveryService()
    result = service.build_ledger_from_metadata(
        github_repositories=[
            {
                "full_name": "viktorbezdek/definitive-llm-writing-style-guide",
                "html_url": "https://github.com/viktorbezdek/definitive-llm-writing-style-guide",
                "description": (
                    "Definitive guide to LLM writing styles with personality traits, cultural background, "
                    "narrative techniques, tone, persona, linguistic identity, style dimensions, "
                    "agreeableness, openness, conscientiousness, metaphor, archaism and ethical responsibility."
                ),
                "stargazers_count": 1,
                "forks_count": 0,
                "license": None,
                "topics": ["llm", "writing-style", "persona", "creative-writing"],
                "updated_at": "2026-06-11T06:20:00Z",
                "root_files": ["README.md"],
            },
            {
                "full_name": "jpotts18/stylometry",
                "html_url": "https://github.com/jpotts18/stylometry",
                "description": (
                    "Stylometry reference library for extracting features from text using NLTK. "
                    "It studies linguistic style, authorship attribution, anonymous documents, "
                    "raw text feature extraction and statistical analysis of written language."
                ),
                "stargazers_count": 42,
                "forks_count": 12,
                "license": None,
                "topics": ["stylometry", "feature-extraction", "authorship-attribution"],
                "updated_at": "2024-12-10T09:00:00Z",
                "root_files": ["README.md", "setup.py", "stylometry"],
            },
            {
                "full_name": "egonSchiele/chisel",
                "html_url": "https://github.com/egonSchiele/chisel",
                "description": (
                    "Chisel is a local writing app for organizing book chapters into blocks, "
                    "local private data, AI editing help, speech-to-text via whisper.cpp, "
                    "llama.cpp local models, OpenAI API key option, releases/release/ downloads, "
                    "and native app binary distribution."
                ),
                "stargazers_count": 240,
                "forks_count": 8,
                "license": {"spdx_id": "GPL-3.0"},
                "topics": ["writing-app", "local-first", "book", "llama-cpp"],
                "updated_at": "2026-04-28T12:00:00Z",
                "root_files": ["README.md", "LICENSE", "src", "releases", "package.json"],
            },
        ],
        forum_items=[],
        generated_at="2026-06-11T18:10:00+08:00",
    )

    candidates = {candidate["title"]: candidate for candidate in result["candidates"]}
    style_guide = candidates["viktorbezdek/definitive-llm-writing-style-guide"]
    stylometry = candidates["jpotts18/stylometry"]
    chisel = candidates["egonSchiele/chisel"]
    assert "llm_style_dimension_matrix_gate" in style_guide["absorbed_patterns"]
    assert "stylometry_feature_extraction_baseline_gate" in stylometry["absorbed_patterns"]
    assert "local_block_manuscript_workspace_gate" in chisel["absorbed_patterns"]
    assert "license:missing" in style_guide["trust_review"]["flags"]
    assert "license:missing" in stylometry["trust_review"]["flags"]
    assert "binary_distribution" in chisel["risk_flags"]
    assert "provider_key_surface" in chisel["risk_flags"]

    pattern_pack = service.build_pattern_pack_from_ledger(result)
    assert "llm_style_dimension_matrix_policy" in pattern_pack["bible_enrichment_targets"]
    assert "stylometry_feature_baseline_policy" in pattern_pack["bible_enrichment_targets"]
    assert "local_block_manuscript_workspace_policy" in pattern_pack["bible_enrichment_targets"]
    assert "llm_style_dimension_matrix_report" in pattern_pack["whole_book_analysis_targets"]
    assert "stylometry_feature_baseline_report" in pattern_pack["whole_book_analysis_targets"]
    assert "local_block_workspace_revision_report" in pattern_pack["whole_book_analysis_targets"]
    assert "style_dimension_matrix_remap" in pattern_pack["inspired_mapping_targets"]
    assert "stylometry_feature_baseline_remap" in pattern_pack["inspired_mapping_targets"]
    assert "local_block_revision_remap" in pattern_pack["inspired_mapping_targets"]
    assert any("personality" in hint for hint in pattern_pack["llm_style_dimension_matrix_gate_hints"])
    assert any("feature extraction" in hint for hint in pattern_pack["stylometry_feature_extraction_baseline_gate_hints"])
    assert any("chapter blocks" in hint for hint in pattern_pack["local_block_manuscript_workspace_gate_hints"])
    assert any("style dimension matrix" in hint for hint in pattern_pack["continuation_prompt_hints"])
    assert any("chapter-block" in hint for hint in pattern_pack["continuation_state_hints"])
    assert any("style dimensions" in hint for hint in pattern_pack["inspired_prompt_hints"])
    assert any("stylometric feature ranges" in hint for hint in pattern_pack["inspired_transformation_hints"])
    assert any("persona/style matrix" in hint for hint in pattern_pack["inspired_copy_risk_hints"])

    digest = render_source_pattern_pack_digest(pattern_pack, include_inspired_guidance=True)
    assert "llm_style_dimension_matrix_gate_hints" in digest
    assert "stylometry_feature_extraction_baseline_gate_hints" in digest
    assert "local_block_manuscript_workspace_gate_hints" in digest
