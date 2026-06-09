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


def test_default_github_repository_urls_cover_static_review_shortlist():
    normalized_urls = {url.lower() for url in DEFAULT_GITHUB_REPOSITORY_URLS}

    assert "https://github.com/voocel/ainovel-cli" in normalized_urls
    assert "https://github.com/nousresearch/autonovel" in normalized_urls
    assert "https://github.com/leenbj/novel-creator-skill" in normalized_urls
    assert "https://github.com/kazkozdev/novelgenerator" in normalized_urls
    assert "https://github.com/raestrada/storycraftr" in normalized_urls
    assert "https://github.com/yuanshijiloong/author" in normalized_urls
    assert "https://github.com/brandburner/fabula" in normalized_urls


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
    assert "projection_sync_log" in pattern_pack["whole_book_analysis_targets"]
    assert "foreshadowing_debt_items" in pattern_pack["whole_book_analysis_targets"]
    assert "reader_retention_score" in pattern_pack["whole_book_analysis_targets"]
    assert "draft_stage_status" in pattern_pack["whole_book_analysis_targets"]
    assert "rolling_summary" in pattern_pack["whole_book_analysis_targets"]
    assert "story_contract_commit_chain_hints" in pattern_pack
    assert "fact_snapshot_delta_gate_hints" in pattern_pack
    assert "projection_sync_observability_hints" in pattern_pack
    assert "foreshadowing_debt_budget_hints" in pattern_pack
    assert "reader_retention_review_gate_hints" in pattern_pack
    assert "draft_stage_revision_ladder_hints" in pattern_pack
    assert "rolling_summary_context_trim_hints" in pattern_pack
    assert "commit_chain_remap" in pattern_pack["inspired_mapping_targets"]
    assert "fact_delta_remap" in pattern_pack["inspired_mapping_targets"]
    assert "retention_hook_remap" in pattern_pack["inspired_mapping_targets"]

    digest = render_source_pattern_pack_digest(pattern_pack)
    assert "story_contract_commit_chain_hints" in digest
    assert "fact_snapshot_delta_gate_hints" in digest
    assert "rolling_summary_context_trim_hints" in digest


def test_default_discovery_sources_include_serialized_webnovel_projects():
    assert "https://github.com/lingfengQAQ/webnovel-writer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/zy-zmc/tianming-novel-ai-writer" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/lujih/webnovel-writer-opencode" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/starMagic/webnovel-writer-hermes" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/HZ-KMNO/web-novel-writing-guidance-skill" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/jinmawang/claude-novel-writeFlow" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/DuckTraDo/Novel" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/makieali/longform-ai" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert "https://github.com/guchendesigndog/GC-Writer-Assistant" in DEFAULT_GITHUB_REPOSITORY_URLS
    assert any("story contract" in query.lower() for query in DEFAULT_GITHUB_QUERIES)
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
