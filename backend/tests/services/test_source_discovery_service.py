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
