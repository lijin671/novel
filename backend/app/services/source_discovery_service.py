"""公开小说项目发现与沉淀服务。

这个服务只处理公开元数据和摘要，不克隆、不安装、不执行外部项目。
"""

from __future__ import annotations

import html
import base64
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import httpx


GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
GITHUB_REPO_API_URL = "https://api.github.com/repos/{owner}/{repo}"
GITHUB_REPO_CONTENTS_API_URL = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
DEFAULT_GITHUB_QUERIES = (
    '("ai novel" OR "novel writing" OR "fiction writing") in:name,description,readme',
    '("novel cli" OR "fiction generator" OR "story generation") in:name,description,readme',
    '("story bible" OR "worldbuilding" OR "chapter generation") in:name,description,readme',
    '("writing assistant" OR "style analysis" OR "same type creation") in:name,description,readme',
    '("world info" OR "lorebook" OR "author note" OR "memory book") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("snapshot" OR "branch" OR "rollback") ("memory" OR "context") ("agent" OR "story") in:name,description,readme',
    '("local-first" OR "IndexedDB" OR "workspace") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("review queue" OR "PendingChange" OR "staging area") ("novel" OR "fiction" OR "worldbuilding") in:name,description,readme',
    '("style guide" OR "character voice" OR "scene override") ("novel" OR "fiction" OR "worldbuilding") in:name,description,readme',
    '("ContentRef" OR "graph healing" OR "contradiction detection") ("novel" OR "fiction" OR "narrative") in:name,description,readme',
    '("premature ending" OR "three-layer memory" OR "plot graph") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("plotgrid" OR "plotline" OR "scene status") ("novel" OR "fiction" OR "writing") in:name,description,readme',
    '("gradual reveal" OR "setup/payoff" OR "scene-type directing") ("novel" OR "fiction" OR "writing") in:name,description,readme',
    '("WorldPkg" OR "alternative timeline" OR "divergence guidance") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("context pack" OR "accepted chapter" OR "continuity check") ("novel" OR "fiction" OR "story bible") in:name,description,readme',
    '("writer model" OR "critic model" OR "verifier") ("story" OR "fiction" OR "novel") in:name,description,readme',
    '("trend scanning" OR "deconstruction" OR "AI tone removal") ("web novel" OR "novel writing") in:name,description,readme',
    '("interrupted continuation" OR "resume writing" OR "auto validation") ("novel" OR "chapter") in:name,description,readme',
    '("top down" OR "book spec" OR "chapter scenes") ("storytelling agent" OR "long stories") in:name,description,readme',
    '("json schema" OR "schema-first" OR "structured generation") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("card" OR "cards" OR "context injection" OR "knowledge graph") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("workflow agent" OR "workflow studio" OR "progress recovery") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("scene" OR "shot" OR "idea to production" OR "storyboard") ("AI" OR "Claude Code") in:name,description,readme',
    '("世界观" OR "时间线" OR "人物卡") "AI" in:name,description,readme',
    '("同类型创作" OR "风格复刻" OR "续写") "AI" in:name,description,readme',
    '("卡片" OR "结构化生成" OR "上下文注入" OR "知识图谱") "AI" in:name,description,readme',
    '("小说" OR "写作" OR "创作") "AI" in:name,description,readme',
)
DEFAULT_GITHUB_REPOSITORY_URLS = (
    "https://github.com/voocel/ainovel-cli",
    "https://github.com/NousResearch/autonovel",
    "https://github.com/leenbj/novel-creator-skill",
    "https://github.com/KazKozDev/NovelGenerator",
    "https://github.com/raestrada/storycraftr",
    "https://github.com/YuanShiJiLoong/author",
    "https://github.com/brandburner/fabula",
    "https://github.com/RhythmicWave/NovelForge",
    "https://github.com/kaigani/codeywood",
    "https://github.com/KoboldAI/KoboldAI-Client",
    "https://github.com/SillyTavern/SillyTavern",
    "https://github.com/envy-ai/ai_rpg",
    "https://github.com/matrixorigin/Memoria",
    "https://github.com/mrigankad/Novel-OS",
    "https://github.com/aikohanasaki/SillyTavern-MemoryBooks",
    "https://github.com/bal-spec/sillytavern-character-memory",
    "https://github.com/MangoLion/plotbunni",
    "https://github.com/loreum-app/loreum",
    "https://github.com/ExplosiveCoderflome/AI-Novel-Writing-Assistant",
    "https://github.com/Lanerra/saga",
    "https://github.com/ModernRelay/omnigraph",
    "https://github.com/doctoroyy/novel-copilot",
    "https://github.com/PixeroJan/obsidian-storyline",
    "https://github.com/skyfiredao/dreampowers",
    "https://github.com/ypcypc/WhatIf",
    "https://github.com/YfengJ/novel-studio-ai",
    "https://github.com/davealaw/FictionRefine",
    "https://github.com/ShmilyWithme/Shmily_novel_skill",
    "https://github.com/worldwonderer/oh-story-claudecode",
    "https://github.com/PenglongHuang/chinese-novelist-skill",
    "https://github.com/GOAT-AI-lab/GOAT-Storytelling-Agent",
)
DEFAULT_LINUX_DO_RSS_URLS = (
    "https://linux.do/tag/444-tag/444.rss",
    "https://linux.do/tag/2234-tag/2234.rss",
    "https://linux.do/latest.rss",
)

NOVEL_KEYWORDS = (
    "novel",
    "fiction",
    "story",
    "chapter",
    "writing",
    "author",
    "worldbuilding",
    "story bible",
    "continuation",
    "续写",
    "小说",
    "拆书",
    "网文",
    "二创",
    "世界观",
    "时间线",
    "人物卡",
)
NARRATIVE_PRODUCTION_KEYWORDS = (
    "filmmaking",
    "film production",
    "screenplay",
    "storyboard",
    "shot list",
    "scene plan",
    "idea to production",
    "narrative production",
    "movie",
    "video production",
    "影视",
    "电影",
    "剧本",
    "分镜",
    "镜头",
    "场景资产",
)
PATTERN_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("book_decomposition", ("拆书", "拆解", "解析", "book decomposition", "book analysis", "source book")),
    ("chapter_generation", ("chapter generation", "autonomous novel pipeline", "novel pipeline", "seed concept to print-ready", "章节生成", "生成章节", "章节创作", "小说生成", "创作平台", "写作平台")),
    ("continuation", ("continuation", "continue", "续写", "断更续写", "继续写")),
    ("same_type_creation", ("同类型", "inspired", "remix", "二创", "同人", "同类创作", "风格复刻")),
    ("worldbuilding", ("worldbuilding", "世界观", "设定", "world rules")),
    ("timeline", ("timeline", "时间线", "chronology")),
    ("character_cards", ("character", "人物", "角色", "人物卡")),
    ("organization_graph", ("organization", "faction", "组织", "势力")),
    ("emotion_arc", ("emotion", "情感", "relationship", "关系")),
    ("style_signature", ("style", "voice", "风格", "文风", "味道")),
    ("self_review", ("review", "critique", "评审", "自评", "自我评审", "优化", "rewrite")),
    ("card_workbench", ("card", "cards", "card-based", "card workbench", "卡片", "卡片式", "卡片创作")),
    ("structured_generation_schema", ("schema", "json schema", "schema-first", "structured generation", "结构化", "结构化生成", "动态输出模型", "输出模型")),
    ("context_reference", ("context injection", "context reference", "context-aware", "@dsl", "knowledge graph", "vector retrieval", "vector storage", "retrieved automatically", "retrieval", "injection viewer", "上下文注入", "上下文引用", "知识图谱", "引用")),
    ("workflow_agent_pipeline", ("workflow agent", "workflow studio", "workflow system", "persistent workflow", "progress recovery", "multi-agent", "editorial pipeline", "agent handoff", "工作流", "工作流系统", "中断恢复", "触发器")),
    ("scene_asset_pipeline", ("idea to production", "filmmaking", "film production", "screenplay", "storyboard", "shot", "shot list", "scene asset", "scene plan", "镜头", "分镜", "场景资产")),
    ("quality_score_loop", ("modify-evaluate-keep", "keep/discard", "foundation_score", "quality score", "chapter quality", "score >", "plateau detection", "reader panel", "llm judge", "dual-persona review", "质量评分", "读者面板", "平台期检测")),
    ("voice_fingerprint", ("voice fingerprint", "voice analysis", "voice discovery", "voice.md", "声纹", "文风指纹", "语气指纹", "声音发现")),
    ("anti_slop_audit", ("anti-slop", "anti-pattern", "slop scorer", "ai tell", "mechanical slop", "anti-pattern rules", "反 AI", "反套路", "AI 味", "机械感")),
    ("publication_pipeline", ("print-ready", "epub", "audiobook", "landing page", "typeset", "latex", "export", "publish", "publication", "有声书", "排版", "出版", "交付流水线")),
    ("lorebook_context", ("world info", "worldinfo", "lorebook", "memory book", "keyword activation", "recursive scan", "scan depth", "insertion order", "context budget", "世界信息", "设定集", "关键词激活", "递归扫描")),
    ("author_note_layer", ("author's note", "authors note", "author note", "insertion frequency", "in-chat", "chat memory", "作者注释", "作者备注", "提示词层")),
    ("world_state_tracking", ("solo tabletop game master", "players, locations, regions, and items", "world state", "story state", "persistent state", "central state", "state parser", "event memory", "event memories", "fact memory", "fact memories", "emotional memory", "emotional memories", "relationship memory", "relationship memories", "scene log", "review logs", "structured prompts", "世界状态", "实体状态", "场景日志")),
    ("memory_snapshot_versioning", ("git for ai agent memory", "snapshot", "branch", "merge", "rollback", "memory versioning", "memory branch", "compaction", "consolidation", "memory rollup", "memory rollups", "multi-tier memory", "记忆快照", "记忆分支", "回滚")),
    ("local_first_novel_workspace", ("local-first", "local first", "offline access", "indexeddb", "multi-novel", "active novel", "workspace", "local data persistence", "novel workspace", "本地优先", "离线访问", "多小说工作区")),
    ("prompt_library", ("prompt manager", "prompt library", "task-specific prompt", "task prompts", "system prompt", "reset prompts", "prompt template", "提示词库", "提示词管理", "任务提示词")),
    ("scene_level_generation", ("scene-level generation", "scene level generation", "scene-by-scene", "scene drafts", "plan scenes", "draft scene", "scene text writing", "generate prose for each scene", "场景级生成", "逐场景生成")),
    ("review_queue_staging", ("review queue", "pendingchange", "pending change", "staging area", "diff view", "accept edit reject", "accept all", "staged not applied", "审查队列", "暂存区", "待审核变更")),
    ("style_guide_layering", ("style guide", "base style guide", "scene override", "scene overrides", "character voice", "character voices", "voicenotes", "voice notes", "pov conventions", "dialogue rules", "风格指南", "场景覆写", "角色语音")),
    ("entity_schema_custom_fields", ("custom entity types", "custom entity type", "custom fields", "custom field schemas", "fieldschema", "field schema", "entity types", "field schemas", "自定义实体", "自定义字段", "字段模式")),
    ("content_ref_externalization", ("contentref", "content ref", "content externalization", "externalized content", "large text blobs", ".saga/content", "lightweight checkpoints", "外置内容", "内容引用")),
    ("graph_healing", ("graph healing", "quality assurance", "merge duplicate entities", "duplicate entities", "enrich provisional nodes", "graph consistency", "图谱修复", "图谱清理")),
    ("contradiction_detection", ("contradiction detection", "contradiction analysis", "contradiction", "contradictions", "consistency checks", "timeline issues", "relationship evolution", "abrupt relationship changes", "trait consistency", "矛盾检测", "一致性检查")),
    ("graph_branching_atomicity", ("git-style versioning", "branching", "branch merge", "snapshot isolation", "atomic", "manifest", "multi-table publish", "commit dag", "three-way", "row-level merge", "图分支", "原子提交")),
    ("query_lint_contract", ("query lint", "schema lint", "linter", "typed ir", "query language", ".gq", ".pg", "strict validation", "查询检查", "模式检查")),
    ("premature_ending_guard", ("premature ending", "premature ending detection", "false ending", "early resolution", "anti-ending", "ending guard", "过早完结", "提前完结", "烂尾检测")),
    ("layered_memory_model", ("three-layer memory", "three layer memory", "layered memory", "base memory", "character state", "plot graph", "分层记忆", "三层记忆")),
    ("plot_dependency_graph", ("plot graph", "plot dependency", "dependency graph", "foreshadowing and dependency", "character relationship graph", "setup dependency", "payoff dependency", "情节依赖", "伏笔依赖")),
    ("plotgrid_scene_matrix", ("plotgrid", "plot grid", "scene matrix", "scene rows", "spreadsheet-style grid", "scenes against plotlines", "场景矩阵", "情节网格")),
    ("plotline_thread_tracking", ("plotline", "plotlines", "story threads", "thread tracking", "subway map", "shared scenes", "剧情线", "线索追踪")),
    ("scene_status_dashboard", ("scene status", "status badge", "scene cards", "kanban-style scene cards", "scene progress", "scene dashboard", "场景状态", "场景看板")),
    ("gradual_reveal_control", ("gradual reveal", "iceberg annotations", "iceberg annotation", "underwater", "reveal check", "信息释放", "冰山", "逐步揭示")),
    ("setup_payoff_tracking", ("setup/payoff", "setup payoff", "foreshadowing tracking", "payoff", "setup chapter", "expected payoff", "伏笔回收", "埋设回收")),
    ("scene_type_directing", ("scene-type directing", "scene type directing", "action scene", "emotional scene", "dialogue scene", "camera-language", "scene directing", "场景类型", "动作场景", "情感场景", "对话场景", "镜头语言")),
    ("worldpkg_export", ("worldpkg", "world package", "structured world data", "extract world data", "lorebook extraction", "entity state transitions", "世界数据包", "世界数据")),
    ("alternate_timeline_branching", ("alternative timeline", "alternate timeline", "what-if", "choice-driven", "branch storyline", "same world as a player", "timeline management", "平行时间线", "分歧时间线")),
    ("divergence_guidance", ("divergence guidance", "branch drift", "player choices", "every choice", "choice reshape", "scene adaptation", "改写剧情", "分歧引导")),
    ("context_pack_preview", ("context pack", "context pack preview", "build context pack", "confirmed memory", "retrieval memory", "hybrid retrieval", "keyword search", "local vector search", "graph facts", "context preview", "上下文包", "上下文预览")),
    ("accepted_chapter_memory", ("accepted chapter", "accept chapter", "accepted chapters", "drafts do not update canon", "extract memory", "accepted chapter write", "reuse memory in the next chapter", "accept flow", "正式接受", "章节验收")),
    ("critic_verifier_loop", ("critic", "verifier", "writer model", "critic model", "two-llm", "two llm", "reviewing, revising, and verification", "automated revision cycles", "quality thresholds", "detailed feedback", "评审模型", "验证模型")),
    ("collapse_prevention", ("story collapse", "prevents story collapse", "story collapse prevention", "handles model failures", "validates outputs", "failure handling", "collapse", "崩坏", "剧情崩坏")),
    ("trend_deconstruction_pipeline", ("trend scanning", "scan trending charts", "deconstruct", "deconstruction", "reverse-engineering hits", "plot modularization", "module library", "tropes", "commercialize", "hooks, payoff density", "扫榜", "拆文", "爆款", "套路", "模块库")),
    ("anti_ai_tone_polish", ("ai tone removal", "remove ai tone", "deslop", "deep polish", "ai痕迹", "去ai味", "去 AI 味", "ai tone", "natural and fluent", "文字自然流畅")),
    ("preference_memory", ("preference memory", "creative memory", "learns your preferences", "user preference", "personalized", "memory-demo", "偏好记忆")),
    ("interrupted_resume_flow", ("interrupted continuation", "resume from breakpoint", "detect unfinished", "resume writing", "interruption", "中断续写", "断点续写")),
    ("auto_validation_rewrite", ("auto validation", "automatic validation", "auto repair", "auto rewrite", "word count and coherence", "not qualified auto rewrite", "自动校验", "自动修复")),
    ("top_down_story_planning", ("top down", "top-down", "book spec", "enhance book spec", "create plot chapters", "enhance plot chapters", "split chapters into scenes", "chapter scenes", "scene scale", "from topic to scene", "顶层设计", "分章分场")),
)
RISK_FILE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("postinstall", ("postinstall",)),
    ("docker", ("dockerfile", "docker-compose", "compose.yaml", "compose.yml")),
    ("shell_script", (".sh", "install.sh", "setup.sh")),
    ("powershell_script", (".ps1", "install.ps1", "setup.ps1")),
    ("native_binary", (".exe", ".dll", ".so", ".dylib")),
    ("browser_extension", ("manifest.json", "chrome-extension", "extension")),
    ("mcp_server", ("mcp", "server.py", "server.ts")),
)
STATIC_REPOSITORY_PATTERN_OVERRIDES: dict[str, str] = {
    "koboldai/koboldai-client": (
        "AI-assisted writing front-end for story and novel use cases. "
        "Public README describes Memory, Author's Note, World Info, Save & Load, "
        "regular story writing, novel models, adventure mode, and writing assistant workflows."
    ),
    "sillytavern/sillytavern": (
        "LLM fiction and roleplay front-end with WorldInfo lorebooks. "
        "Official public docs describe World Info / Lorebooks / Memory Books, keyword activation, "
        "scan depth, recursive scanning, insertion order, token budget, Author's Note, and context injection."
    ),
    "envy-ai/ai_rpg": (
        "AI RPG turns a model into a solo tabletop game master for story generation. "
        "Public README describes structured prompts, players, locations, regions, items, world state, settings, and review logs."
    ),
    "matrixorigin/memoria": (
        "AI agent memory infrastructure with snapshot, branch, merge, rollback, and Git-like memory versioning. "
        "Pattern-only adaptation for long-form novel continuation state snapshots and reversible context changes."
    ),
    "mrigankad/novel-os": (
        "Multi-agent fiction writing framework with persistent story state, central StoryState JSON, "
        "deterministic continuity engine, five-role editorial pipeline, chapter quality scores, and state parser merge flow."
    ),
    "aikohanasaki/sillytavern-memorybooks": (
        "SillyTavern memory extension for structured memory creation into lorebooks. "
        "Public README describes scenes as memories, clips, side prompts, JSON summaries, compaction, consolidation, "
        "lorebook ordering, and multi-tier memory rollups."
    ),
    "bal-spec/sillytavern-character-memory": (
        "SillyTavern character memory extension that extracts structured relationship, event, fact, and emotional memories "
        "into editable markdown Data Bank files with vector retrieval, injection viewer, token breakdown, health checks, and undoable memory control."
    ),
    "mangolion/plotbunni": (
        "Novel writing workspace with local-first IndexedDB multi-novel storage, Act / Chapter / Scene hierarchy, "
        "Concept Cache, task-specific Prompt Manager, AI Novel Writer, token-aware context sizing, and sequential scene-level generation."
    ),
    "loreum-app/loreum": (
        "Fictional worldbuilding database for novels and story projects. Public docs describe entities, relationships, timelines, "
        "storyboard, custom entity field schemas, Style Guide layering from base style to scene overrides to character voices, "
        "MCP write staging through PendingChange Review Queue, and contradiction analysis."
    ),
    "explosivecoderflome/ai-novel-writing-assistant": (
        "Chinese AI novel writing assistant with book decomposition, director workflow, fact ledger, chapter tasks, "
        "quality guardrails, genre/style management, and long-form production pipeline patterns."
    ),
    "lanerra/saga": (
        "Long-form fiction engine using checkpointed LangGraph and a Neo4j canon graph. Public docs describe scene-level generation, "
        "scene-based extraction, ContentRef externalization for large text artifacts, contradiction detection, revision loops, and graph healing."
    ),
    "modernrelay/omnigraph": (
        "Versioned graph engine useful as a pattern source for novel canon graphs: Git-style snapshots and branches, "
        "atomic graph-level commits, row-level merge conflicts, schema/query linting, and branch-safe mutation contracts."
    ),
    "doctoroyy/novel-copilot": (
        "AI-driven novel writing assistant with Story Bible generation, a three-layer memory model, character state snapshots, "
        "character relationship graph APIs, plot graph / foreshadowing dependency graph, and premature ending detection."
    ),
    "pixerojan/obsidian-storyline": (
        "Obsidian book planning plugin with plotgrid scene matrix, board scene cards, timeline, plotlines subway map, "
        "scene status badges, character/location/codex tags, continuous scrivenings view, and progress tracking."
    ),
    "skyfiredao/dreampowers": (
        "Chinese novel writing skill pack. Public README describes gradual reveal, iceberg annotations, three-stage chapter review, "
        "setup/payoff foreshadow tracking, scene-type directing for action/emotional/dialogue scenes, and camera-language description methodology."
    ),
    "ypcypc/whatif": (
        "Chinese novel-to-interactive-world project that extracts events, characters, locations, items, lorebook data, "
        "entity state transitions, and WorldPkg packages, then supports choice-driven divergence, alternative timeline management, scene adaptation, and memory compression."
    ),
    "yfengj/novel-studio-ai": (
        "Local-first long-form fiction workbench. Public README describes story and style bibles, volume outlines, five-chapter arc packs, "
        "chapter outlines, scene beats, Chapter Studio context-pack preview, continuity check, style revision, accept flow, character state versions, "
        "graph facts, hybrid retrieval, local vector search, and accepted-chapter memory extraction."
    ),
    "davealaw/fictionrefine": (
        "Two-LLM story workflow using a writer/reviser model and a critic/verifier model. Public README describes multi-dimensional critique, "
        "iterative review/revision/verification cycles, quality thresholds, output validation, failure handling, and story-collapse prevention."
    ),
    "shmilywithme/shmily_novel_skill": (
        "Chinese web-novel writing assistant for Claude Code and Codex Skill surfaces. Public docs describe a long-form workbench, chapter station, story map, "
        "library, AI writer room, dashboard, previous/next chapter navigation, chapter planning, review health check, continuation, polishing, and local CLI diagnostics."
    ),
    "worldwonderer/oh-story-claudecode": (
        "Chinese web-novel skill pack for trend scanning, deconstruction, writing, AI-tone removal, and cover generation. Public README frames tropes as deterministic "
        "emotional payoff and emphasizes reverse-engineering hits, plot modularization, layered state management, hooks, payoff density, and expectation management."
    ),
    "penglonghuang/chinese-novelist-skill": (
        "Chinese novelist skill. Public README/SKILL describe three-layer progressive Q&A, preference memory, interrupted continuation, serial/subagent/Agent Teams writing modes, "
        "automatic word-count/coherence validation, auto repair/rewrite, conflict-driven chapters, chapter-end hooks, and deep polish to remove AI traces."
    ),
    "goat-ai-lab/goat-storytelling-agent": (
        "Long-story generation agent. Public README describes a top-down pipeline from topic to book specification, enhanced book spec, plot chapters, enhanced chapter plan, "
        "splitting chapters into scenes, and writing each scene with previous-scene context for scale-controllable storytelling."
    ),
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _text(value: Any) -> str:
    return str(value or "").strip()


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _lower_haystack(*parts: Any) -> str:
    return "\n".join(str(part or "") for part in parts).lower()


def _contains_keyword(haystack: str, keyword: str) -> bool:
    needle = keyword.lower()
    if not needle:
        return False
    if re.fullmatch(r"[a-z0-9_]+", needle):
        return re.search(rf"(?<![a-z0-9_]){re.escape(needle)}(?![a-z0-9_])", haystack) is not None
    return needle in haystack


def _date_slug(generated_at: str) -> str:
    match = re.match(r"^(\d{4}-\d{2}-\d{2})", generated_at or "")
    return match.group(1) if match else datetime.now().strftime("%Y-%m-%d")


def _parse_datetime(value: Any) -> datetime | None:
    raw = _text(value)
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_linux_do_rss_items(rss_text: str, *, source_url: str) -> list[dict[str, Any]]:
    """解析 Linux.do RSS，返回只含公开摘要的候选元数据。"""
    root = ET.fromstring(rss_text)
    items: list[dict[str, Any]] = []
    for item in root.findall(".//item"):
        title = _text(item.findtext("title"))
        link = _text(item.findtext("link"))
        description = _strip_html(item.findtext("description") or "")
        published_at = _text(item.findtext("pubDate"))
        if not title and not link:
            continue
        items.append(
            {
                "source": "linux.do",
                "source_url": source_url,
                "title": title,
                "url": link,
                "summary": description[:500],
                "published_at": published_at,
            }
        )
    return items


class NovelSourceDiscoveryService:
    """小说自动化公开源发现、分类与 Markdown ledger 沉淀。"""

    async def discover_public_sources(
        self,
        *,
        github_queries: Iterable[str] = DEFAULT_GITHUB_QUERIES,
        github_repository_urls: Iterable[str] = DEFAULT_GITHUB_REPOSITORY_URLS,
        linux_do_rss_urls: Iterable[str] = DEFAULT_LINUX_DO_RSS_URLS,
        github_token: str | None = None,
        per_github_query: int = 10,
        per_rss_feed: int = 20,
        timeout_seconds: float = 20.0,
    ) -> dict[str, Any]:
        """从 GitHub Search API 和 Linux.do RSS 拉取公开元数据。"""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        github_repositories: list[dict[str, Any]] = []
        forum_items: list[dict[str, Any]] = []
        fetch_errors: list[dict[str, str]] = []

        async with httpx.AsyncClient(timeout=timeout_seconds, headers={"User-Agent": "MuMuAINovel-source-discovery"}) as client:
            for query in github_queries:
                try:
                    response = await client.get(
                        GITHUB_SEARCH_URL,
                        params={
                            "q": query,
                            "sort": "stars",
                            "order": "desc",
                            "per_page": max(1, min(per_github_query, 50)),
                        },
                        headers=headers,
                    )
                    response.raise_for_status()
                    payload = response.json()
                    github_repositories.extend(_as_list(payload.get("items")))
                except Exception as exc:  # pragma: no cover - 网络边界由集成环境验证
                    fetch_errors.append({"source": "github", "query": query, "error": str(exc)})

            for repository_url in github_repository_urls:
                owner_repo = self._parse_github_owner_repo(repository_url)
                if not owner_repo:
                    fetch_errors.append({"source": "github", "url": str(repository_url), "error": "invalid_github_repository_url"})
                    continue
                owner, repo = owner_repo
                try:
                    response = await client.get(
                        GITHUB_REPO_API_URL.format(owner=owner, repo=repo),
                        headers=headers,
                    )
                    response.raise_for_status()
                    payload = response.json()
                    if isinstance(payload, dict):
                        payload.update(
                            await self._fetch_explicit_github_static_surface(
                                client=client,
                                owner=owner,
                                repo=repo,
                                headers=headers,
                            )
                        )
                        github_repositories.append(payload)
                except Exception as exc:  # pragma: no cover - network boundary
                    fetch_errors.append({"source": "github", "url": str(repository_url), "error": str(exc)})

            for url in linux_do_rss_urls:
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    forum_items.extend(parse_linux_do_rss_items(response.text, source_url=url)[:per_rss_feed])
                except Exception as exc:  # pragma: no cover - 网络边界由集成环境验证
                    fetch_errors.append({"source": "linux.do", "url": url, "error": str(exc)})

        ledger = self.build_ledger_from_metadata(
            github_repositories=github_repositories,
            forum_items=forum_items,
            generated_at=_now_iso(),
        )
        ledger["fetch_errors"] = fetch_errors
        return ledger

    def build_ledger_from_metadata(
        self,
        *,
        github_repositories: Iterable[dict[str, Any]],
        forum_items: Iterable[dict[str, Any]],
        generated_at: str | None = None,
    ) -> dict[str, Any]:
        generated = generated_at or _now_iso()
        raw_candidates: list[dict[str, Any]] = []

        for repository in github_repositories:
            candidate = self._candidate_from_github(repository)
            if not self._is_novel_candidate(candidate):
                continue
            raw_candidates.append(candidate)

        for item in forum_items:
            candidate = self._candidate_from_forum(item)
            if not self._is_novel_candidate(candidate):
                continue
            raw_candidates.append(candidate)

        candidates = self._rank_and_dedupe_candidates(raw_candidates)
        candidates.sort(key=lambda item: (item["score"], item.get("stars") or 0), reverse=True)
        return {
            "generated_at": generated,
            "candidate_count": len(candidates),
            "candidates": candidates,
            "safety_notes": [
                "只采集公开元数据和公开摘要；不克隆、不安装、不执行外部项目。",
                "GitHub 与论坛候选默认按 pattern-only 沉淀，后续吸收必须单独做许可证、安装面和安全边界复核。",
                "Linux.do 仅使用公开 RSS/页面可访问摘要；不绕过登录、403、429、WAF 或 CAPTCHA。",
            ],
        }

    def build_pattern_pack_from_ledger(self, ledger: dict[str, Any]) -> dict[str, Any]:
        """把发现 ledger 压缩成可注入拆书/续写提示词的模式包。

        这个方法只读取公开元数据派生出的模式，不修改 ledger，
        也不表示可以导入、安装或执行外部项目代码。
        """
        candidates = self._pack_candidates(ledger)
        grouped_patterns: dict[str, dict[str, Any]] = {}

        for candidate in candidates:
            source_summary = self._pack_source_summary(candidate)
            for pattern_name in _as_list(candidate.get("absorbed_patterns")):
                normalized_name = _text(pattern_name)
                if not normalized_name:
                    continue

                group = grouped_patterns.setdefault(
                    normalized_name,
                    {
                        "name": normalized_name,
                        "candidate_count": 0,
                        "top_source_url": "",
                        "risk_flags": [],
                        "sources": [],
                    },
                )
                group["sources"].append(source_summary)

        workflow_patterns = []
        for pattern_name, group in grouped_patterns.items():
            sources = sorted(
                group["sources"],
                key=lambda item: (
                    int(item.get("score") or 0),
                    int(item.get("stars") or 0),
                    _text(item.get("title")),
                ),
                reverse=True,
            )
            risk_flags = self._dedupe_texts(
                flag
                for source in sources
                for flag in _as_list(source.get("risk_flags"))
            )
            trust_flags = self._dedupe_texts(
                flag
                for source in sources
                for flag in _as_list(source.get("trust_flags"))
            )
            posture_hint = (
                "defer-trust-review"
                if any(_text(source.get("posture_hint")) == "defer-trust-review" for source in sources)
                else "metadata-triage"
            )
            workflow_patterns.append(
                {
                    "name": pattern_name,
                    "candidate_count": len(sources),
                    "top_source_url": _text(sources[0].get("url")) if sources else "",
                    "posture_hint": posture_hint,
                    "risk_flags": risk_flags,
                    "trust_flags": trust_flags,
                    "sources": sources,
                }
            )

        workflow_patterns.sort(
            key=lambda item: (
                -self._pattern_priority(_text(item.get("name"))),
                -max((int(source.get("score") or 0) for source in item.get("sources") or []), default=0),
                -int(item.get("candidate_count") or 0),
                _text(item.get("name")),
            )
        )

        available_patterns = {_text(item.get("name")) for item in workflow_patterns}
        return {
            "generated_at": _text(ledger.get("generated_at")),
            "source_candidate_count": len(candidates),
            "source_titles": [_text(candidate.get("title")) for candidate in candidates],
            "workflow_patterns": workflow_patterns,
            "whole_book_analysis_targets": self._build_whole_book_analysis_targets(available_patterns),
            "bible_enrichment_targets": self._build_bible_enrichment_targets(available_patterns),
            "continuation_prompt_hints": self._build_continuation_prompt_hints(available_patterns),
            "continuation_state_hints": self._build_continuation_state_hints(available_patterns),
            "style_signature_hints": self._build_style_signature_hints(available_patterns),
            "style_fidelity_hints": self._build_style_fidelity_hints(available_patterns),
            "structured_generation_hints": self._build_structured_generation_hints(available_patterns),
            "card_workbench_hints": self._build_card_workbench_hints(available_patterns),
            "context_reference_hints": self._build_context_reference_hints(available_patterns),
            "scene_asset_pipeline_hints": self._build_scene_asset_pipeline_hints(available_patterns),
            "quality_score_loop_hints": self._build_quality_score_loop_hints(available_patterns),
            "voice_fingerprint_hints": self._build_voice_fingerprint_hints(available_patterns),
            "anti_slop_audit_hints": self._build_anti_slop_audit_hints(available_patterns),
            "publication_pipeline_hints": self._build_publication_pipeline_hints(available_patterns),
            "lorebook_context_hints": self._build_lorebook_context_hints(available_patterns),
            "author_note_layer_hints": self._build_author_note_layer_hints(available_patterns),
            "world_state_tracking_hints": self._build_world_state_tracking_hints(available_patterns),
            "memory_snapshot_versioning_hints": self._build_memory_snapshot_versioning_hints(available_patterns),
            "local_first_workspace_hints": self._build_local_first_workspace_hints(available_patterns),
            "prompt_library_hints": self._build_prompt_library_hints(available_patterns),
            "style_guide_layering_hints": self._build_style_guide_layering_hints(available_patterns),
            "review_queue_staging_hints": self._build_review_queue_staging_hints(available_patterns),
            "entity_schema_custom_fields_hints": self._build_entity_schema_custom_fields_hints(available_patterns),
            "scene_level_generation_hints": self._build_scene_level_generation_hints(available_patterns),
            "content_ref_externalization_hints": self._build_content_ref_externalization_hints(available_patterns),
            "graph_healing_hints": self._build_graph_healing_hints(available_patterns),
            "contradiction_detection_hints": self._build_contradiction_detection_hints(available_patterns),
            "graph_branching_atomicity_hints": self._build_graph_branching_atomicity_hints(available_patterns),
            "query_lint_contract_hints": self._build_query_lint_contract_hints(available_patterns),
            "premature_ending_guard_hints": self._build_premature_ending_guard_hints(available_patterns),
            "layered_memory_model_hints": self._build_layered_memory_model_hints(available_patterns),
            "plot_dependency_graph_hints": self._build_plot_dependency_graph_hints(available_patterns),
            "plotgrid_scene_matrix_hints": self._build_plotgrid_scene_matrix_hints(available_patterns),
            "plotline_thread_tracking_hints": self._build_plotline_thread_tracking_hints(available_patterns),
            "scene_status_dashboard_hints": self._build_scene_status_dashboard_hints(available_patterns),
            "gradual_reveal_control_hints": self._build_gradual_reveal_control_hints(available_patterns),
            "setup_payoff_tracking_hints": self._build_setup_payoff_tracking_hints(available_patterns),
            "scene_type_directing_hints": self._build_scene_type_directing_hints(available_patterns),
            "worldpkg_export_hints": self._build_worldpkg_export_hints(available_patterns),
            "alternate_timeline_branching_hints": self._build_alternate_timeline_branching_hints(available_patterns),
            "divergence_guidance_hints": self._build_divergence_guidance_hints(available_patterns),
            "context_pack_preview_hints": self._build_context_pack_preview_hints(available_patterns),
            "accepted_chapter_memory_hints": self._build_accepted_chapter_memory_hints(available_patterns),
            "critic_verifier_loop_hints": self._build_critic_verifier_loop_hints(available_patterns),
            "collapse_prevention_hints": self._build_collapse_prevention_hints(available_patterns),
            "trend_deconstruction_pipeline_hints": self._build_trend_deconstruction_pipeline_hints(available_patterns),
            "anti_ai_tone_polish_hints": self._build_anti_ai_tone_polish_hints(available_patterns),
            "preference_memory_hints": self._build_preference_memory_hints(available_patterns),
            "interrupted_resume_flow_hints": self._build_interrupted_resume_flow_hints(available_patterns),
            "auto_validation_rewrite_hints": self._build_auto_validation_rewrite_hints(available_patterns),
            "top_down_story_planning_hints": self._build_top_down_story_planning_hints(available_patterns),
            "inspired_mapping_targets": self._build_inspired_mapping_targets(available_patterns),
            "inspired_prompt_hints": self._build_inspired_prompt_hints(available_patterns),
            "inspired_transformation_hints": self._build_inspired_transformation_hints(available_patterns),
            "inspired_copy_risk_hints": self._build_inspired_copy_risk_hints(available_patterns),
            "self_review_policy_hints": self._build_self_review_policy_hints(available_patterns),
            "self_review_gate_hints": self._build_self_review_gate_hints(available_patterns),
            "chapter_change_package_hints": self._build_chapter_change_package_hints(available_patterns),
            "safety_constraints": self._build_pattern_pack_safety_constraints(ledger),
        }

    def render_ledger_markdown(self, result: dict[str, Any]) -> str:
        generated_at = _text(result.get("generated_at"))
        date = _date_slug(generated_at)
        lines = [
            f"# Novel Source Discovery Ledger - {date}",
            "",
            "## Scope",
            "",
            "This ledger records public metadata candidates for MuMuAINovel novel automation.",
            "No clone, install, package hook, Docker stack, MCP server, native binary, shell script, or browser extension was executed.",
            "",
            "## Safety Notes",
            "",
        ]
        for note in _as_list(result.get("safety_notes")):
            lines.append(f"- {note}")

        provenance_notes = [_text(note) for note in _as_list(result.get("provenance_notes")) if _text(note)]
        if provenance_notes:
            lines.extend(
                [
                    "",
                    "## Provenance Notes",
                    "",
                ]
            )
            for note in provenance_notes:
                lines.append(f"- {note}")

        fetch_errors = [item for item in _as_list(result.get("fetch_errors")) if isinstance(item, dict)]
        if fetch_errors:
            lines.extend(
                [
                    "",
                    "## Fetch Limits And Failures",
                    "",
                ]
            )
            for item in fetch_errors:
                source = _text(item.get("source")) or "unknown"
                target = _text(item.get("url") or item.get("query")) or "unknown"
                error = _text(item.get("error")) or "unknown"
                lines.append(f"- {source}: {target} — {error}")

        lines.extend(
            [
                "",
                "## Candidates",
                "",
            ]
        )
        candidates = _as_list(result.get("candidates"))
        if not candidates:
            lines.append("- No relevant candidates found in this run.")
        for candidate in candidates:
            patterns = ", ".join(_as_list(candidate.get("absorbed_patterns"))) or "none"
            risks = ", ".join(_as_list(candidate.get("risk_flags"))) or "none"
            stars = candidate.get("stars")
            stars_text = "n/a" if stars is None else str(stars)
            license_text = _text(candidate.get("license")) or "unknown"
            posture_hint = _text(candidate.get("posture_hint")) or "metadata-triage"
            trust_review = candidate.get("trust_review") if isinstance(candidate.get("trust_review"), dict) else {}
            trust_flags = ", ".join(_as_list(trust_review.get("flags"))) or "none"
            lines.extend(
                [
                    f"### {candidate.get('title')}",
                    "",
                    f"- URL: {candidate.get('url')}",
                    f"- Source: {candidate.get('source')}",
                    f"- Family: {candidate.get('family')}",
                    f"- Posture: {candidate.get('posture')}",
                    f"- Posture hint: {posture_hint}",
                    f"- Stars: {stars_text}",
                    f"- License: {license_text}",
                    f"- Risk flags: {risks}",
                    f"- Trust flags: {trust_flags}",
                    f"- Absorbed patterns: {patterns}",
                    f"- Summary: {_text(candidate.get('summary'))}",
                    "",
                ]
            )

        lines.extend(
            [
                "## Next Absorption Targets",
                "",
                "- Use candidates as pattern references for source-book analysis, continuation state, style signature, and self-review loops.",
                "- Do not import upstream runtime code without a separate local safety contract.",
                "",
            ]
        )
        return "\n".join(lines)

    def write_ledger(
        self,
        *,
        repo_root: Path,
        result: dict[str, Any],
        date_slug: str | None = None,
    ) -> Path:
        date = date_slug or _date_slug(_text(result.get("generated_at")))
        target = repo_root / "docs" / "references" / f"novel-source-discovery-{date}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.render_ledger_markdown(result), encoding="utf-8")
        return target

    def write_pattern_pack(
        self,
        *,
        repo_root: Path,
        pattern_pack: dict[str, Any],
        date_slug: str | None = None,
    ) -> Path:
        date = date_slug or _date_slug(_text(pattern_pack.get("generated_at")))
        target = repo_root / "backend" / "app" / "references" / f"novel-source-pattern-pack-{date}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(pattern_pack, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return target

    def load_latest_pattern_pack(self, *, repo_root: Path) -> dict[str, Any]:
        reference_dir = repo_root / "backend" / "app" / "references"
        if not reference_dir.exists():
            return {}

        candidates = sorted(reference_dir.glob("novel-source-pattern-pack-*.json"))
        if not candidates:
            return {}

        try:
            payload = json.loads(candidates[-1].read_text(encoding="utf-8"))
        except Exception:
            return {}
        return payload if isinstance(payload, dict) else {}

    def load_latest_pattern_pack_artifact(self, *, repo_root: Path) -> dict[str, Any]:
        """Return the latest persisted pattern pack with UI-friendly metadata."""
        empty = {
            "found": False,
            "path": None,
            "generated_at": None,
            "source_candidate_count": 0,
            "workflow_pattern_count": 0,
            "source_titles": [],
            "pattern_pack": {},
        }
        reference_dir = repo_root / "backend" / "app" / "references"
        if not reference_dir.exists():
            return empty

        candidates = sorted(reference_dir.glob("novel-source-pattern-pack-*.json"))
        if not candidates:
            return empty

        latest = candidates[-1]
        try:
            payload = json.loads(latest.read_text(encoding="utf-8"))
        except Exception:
            return empty
        if not isinstance(payload, dict):
            return empty

        workflow_patterns = self._as_dict_list(payload.get("workflow_patterns"))
        source_titles = self._dedupe_texts(_as_list(payload.get("source_titles")))
        return {
            "found": True,
            "path": str(latest),
            "generated_at": _text(payload.get("generated_at")) or None,
            "source_candidate_count": int(payload.get("source_candidate_count") or 0),
            "workflow_pattern_count": len(workflow_patterns),
            "source_titles": source_titles,
            "pattern_pack": payload,
        }

    def evaluate_refresh_need(
        self,
        *,
        repo_root: Path,
        now: datetime | None = None,
        max_age_hours: float = 24.0,
    ) -> dict[str, Any]:
        """Decide whether the persisted public source pattern pack should refresh."""
        artifact = self.load_latest_pattern_pack_artifact(repo_root=repo_root)
        if not artifact.get("found"):
            return {
                "refresh_needed": True,
                "reason": "pattern_pack_missing",
                "generated_at": None,
                "age_hours": None,
                "max_age_hours": max_age_hours,
            }

        generated_at = _text(artifact.get("generated_at"))
        try:
            generated_time = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        except ValueError:
            return {
                "refresh_needed": True,
                "reason": "pattern_pack_invalid_timestamp",
                "generated_at": generated_at or None,
                "age_hours": None,
                "max_age_hours": max_age_hours,
            }

        current_time = now or datetime.now(timezone.utc).astimezone()
        if generated_time.tzinfo is None and current_time.tzinfo is not None:
            generated_time = generated_time.replace(tzinfo=current_time.tzinfo)
        elif generated_time.tzinfo is not None and current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=generated_time.tzinfo)

        age_hours = round((current_time - generated_time).total_seconds() / 3600, 2)
        refresh_needed = age_hours > max_age_hours
        return {
            "refresh_needed": refresh_needed,
            "reason": "pattern_pack_stale" if refresh_needed else "pattern_pack_fresh",
            "generated_at": generated_at,
            "age_hours": age_hours,
            "max_age_hours": max_age_hours,
        }

    async def refresh_pattern_pack_if_needed(
        self,
        *,
        repo_root: Path,
        github_queries: Iterable[str] = DEFAULT_GITHUB_QUERIES,
        github_repository_urls: Iterable[str] = DEFAULT_GITHUB_REPOSITORY_URLS,
        linux_do_rss_urls: Iterable[str] = DEFAULT_LINUX_DO_RSS_URLS,
        github_token: str | None = None,
        per_github_query: int = 10,
        per_rss_feed: int = 20,
        timeout_seconds: float = 20.0,
        now: datetime | None = None,
        max_age_hours: float = 24.0,
        force: bool = False,
    ) -> dict[str, Any]:
        """Refresh persisted public source artifacts only when missing, stale, or forced."""
        refresh_policy_before = self.evaluate_refresh_need(
            repo_root=repo_root,
            now=now,
            max_age_hours=max_age_hours,
        )
        if not force and not refresh_policy_before.get("refresh_needed"):
            return {
                "refreshed": False,
                "refresh_policy_before": refresh_policy_before,
                "refresh_policy_after": refresh_policy_before,
                "refresh_reason": refresh_policy_before.get("reason") or "pattern_pack_fresh",
                "candidate_count": 0,
                "candidates": [],
                "fetch_errors": [],
                "written_path": None,
                "written_pattern_pack_path": None,
                "pattern_pack": self.load_latest_pattern_pack_artifact(repo_root=repo_root),
                "ledger": self.load_latest_ledger_artifact(repo_root=repo_root),
            }

        ledger = await self.discover_public_sources(
            github_queries=github_queries,
            github_repository_urls=github_repository_urls,
            linux_do_rss_urls=linux_do_rss_urls,
            github_token=github_token,
            per_github_query=per_github_query,
            per_rss_feed=per_rss_feed,
            timeout_seconds=timeout_seconds,
        )
        pattern_pack = self.build_pattern_pack_from_ledger(ledger)
        written_path = self.write_ledger(repo_root=repo_root, result=ledger)
        written_pattern_pack_path = self.write_pattern_pack(
            repo_root=repo_root,
            pattern_pack=pattern_pack,
        )

        refresh_policy_after = self.evaluate_refresh_need(
            repo_root=repo_root,
            now=now,
            max_age_hours=max_age_hours,
        )

        return {
            "refreshed": True,
            "refresh_policy_before": refresh_policy_before,
            "refresh_policy_after": refresh_policy_after,
            "refresh_reason": refresh_policy_before.get("reason") or "pattern_pack_missing",
            "candidate_count": int(ledger.get("candidate_count") or 0),
            "candidates": _as_list(ledger.get("candidates")),
            "fetch_errors": _as_list(ledger.get("fetch_errors")),
            "written_path": str(written_path),
            "written_pattern_pack_path": str(written_pattern_pack_path),
            "pattern_pack": self.load_latest_pattern_pack_artifact(repo_root=repo_root),
            "ledger": self.load_latest_ledger_artifact(repo_root=repo_root),
        }

    async def resolve_fresh_pattern_pack(
        self,
        *,
        repo_root: Path,
        now: datetime | None = None,
        max_age_hours: float = 24.0,
        force: bool = False,
    ) -> dict[str, Any]:
        """Return a fresh-enough persisted pattern pack, refreshing source metadata if needed."""
        refresh_policy = self.evaluate_refresh_need(
            repo_root=repo_root,
            now=now,
            max_age_hours=max_age_hours,
        )
        if not force and not refresh_policy.get("refresh_needed"):
            return self.load_latest_pattern_pack(repo_root=repo_root)

        refresh_result = await self.refresh_pattern_pack_if_needed(
            repo_root=repo_root,
            now=now,
            max_age_hours=max_age_hours,
            force=force,
        )
        pattern_pack_artifact = refresh_result.get("pattern_pack")
        if isinstance(pattern_pack_artifact, dict):
            pattern_pack = pattern_pack_artifact.get("pattern_pack")
            if isinstance(pattern_pack, dict):
                return pattern_pack
        return self.load_latest_pattern_pack(repo_root=repo_root)

    def load_latest_ledger_artifact(self, *, repo_root: Path) -> dict[str, Any]:
        """Return the latest persisted source discovery markdown ledger."""
        empty = {
            "found": False,
            "path": None,
            "date_slug": None,
            "content": "",
        }
        reference_dir = repo_root / "docs" / "references"
        if not reference_dir.exists():
            return empty

        candidates = sorted(reference_dir.glob("novel-source-discovery-*.md"))
        if not candidates:
            return empty

        latest = candidates[-1]
        try:
            content = latest.read_text(encoding="utf-8")
        except Exception:
            return empty
        date_match = re.search(r"novel-source-discovery-(\d{4}-\d{2}-\d{2})\.md$", latest.name)
        return {
            "found": True,
            "path": str(latest),
            "date_slug": date_match.group(1) if date_match else None,
            "content": content,
        }

    def _pack_candidates(self, ledger: dict[str, Any]) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        for candidate in _as_list((ledger or {}).get("candidates")):
            if not isinstance(candidate, dict):
                continue
            url = _text(candidate.get("url"))
            if not url or url in seen_urls:
                continue
            patterns = [_text(pattern) for pattern in _as_list(candidate.get("absorbed_patterns")) if _text(pattern)]
            if not patterns:
                continue
            seen_urls.add(url)
            candidates.append({**candidate, "absorbed_patterns": patterns})
        candidates.sort(
            key=lambda item: (
                int(item.get("score") or 0),
                int(item.get("stars") or 0),
                _text(item.get("title")),
            ),
            reverse=True,
        )
        return candidates

    def _as_dict_list(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    def _pack_source_summary(self, candidate: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": _text(candidate.get("title")),
            "url": _text(candidate.get("url")),
            "source": _text(candidate.get("source")),
            "summary": _text(candidate.get("summary"))[:280],
            "stars": candidate.get("stars"),
            "license": _text(candidate.get("license")) or "unknown",
            "posture": _text(candidate.get("posture")) or "pattern-only",
            "posture_hint": _text(candidate.get("posture_hint")) or "metadata-triage",
            "risk_flags": self._dedupe_texts(_as_list(candidate.get("risk_flags"))),
            "trust_flags": self._dedupe_texts(
                _as_list(
                    candidate.get("trust_review", {}).get("flags")
                    if isinstance(candidate.get("trust_review"), dict)
                    else []
                )
            ),
            "score": int(candidate.get("score") or 0),
        }

    def _pattern_priority(self, pattern_name: str) -> int:
        priority = {
            "continuation": 100,
            "book_decomposition": 95,
            "chapter_generation": 90,
            "same_type_creation": 85,
            "worldbuilding": 80,
            "timeline": 75,
            "character_cards": 70,
            "organization_graph": 65,
            "emotion_arc": 60,
            "style_signature": 55,
            "self_review": 50,
            "structured_generation_schema": 48,
            "card_workbench": 46,
            "context_reference": 44,
            "workflow_agent_pipeline": 42,
            "scene_asset_pipeline": 40,
            "quality_score_loop": 38,
            "voice_fingerprint": 36,
            "anti_slop_audit": 34,
            "publication_pipeline": 20,
            "lorebook_context": 48,
            "author_note_layer": 32,
            "world_state_tracking": 45,
            "memory_snapshot_versioning": 37,
            "local_first_novel_workspace": 53,
            "prompt_library": 41,
            "scene_level_generation": 58,
            "review_queue_staging": 52,
            "style_guide_layering": 57,
            "entity_schema_custom_fields": 51,
            "content_ref_externalization": 49,
            "graph_healing": 47,
            "contradiction_detection": 62,
            "graph_branching_atomicity": 43,
            "query_lint_contract": 39,
            "premature_ending_guard": 61,
            "layered_memory_model": 54,
            "plot_dependency_graph": 56,
            "plotgrid_scene_matrix": 55,
            "plotline_thread_tracking": 54,
            "scene_status_dashboard": 42,
            "gradual_reveal_control": 59,
            "setup_payoff_tracking": 60,
            "scene_type_directing": 50,
            "worldpkg_export": 44,
            "alternate_timeline_branching": 46,
            "divergence_guidance": 45,
            "context_pack_preview": 63,
            "accepted_chapter_memory": 64,
            "critic_verifier_loop": 57,
            "collapse_prevention": 56,
            "trend_deconstruction_pipeline": 49,
            "anti_ai_tone_polish": 35,
            "preference_memory": 33,
            "interrupted_resume_flow": 52,
            "auto_validation_rewrite": 51,
            "top_down_story_planning": 59,
            "source_discovery": 10,
        }
        return priority.get(pattern_name, 1)

    def _build_bible_enrichment_targets(self, patterns: set[str]) -> list[str]:
        targets = ["world_rules", "timeline", "character_cards", "style_signature", "hard_constraints"]
        if "card_workbench" in patterns:
            targets.append("card_schema_catalog")
            targets.append("field_level_cards")
        if "structured_generation_schema" in patterns:
            targets.append("json_schema_outputs")
            targets.append("schema_validation_rules")
        if "context_reference" in patterns:
            targets.append("context_reference_index")
            targets.append("knowledge_graph_links")
        if "lorebook_context" in patterns:
            targets.append("lorebook_entries")
            targets.append("activation_keywords")
            targets.append("context_insertion_rules")
        if "local_first_novel_workspace" in patterns:
            targets.append("workspace_scope")
            targets.append("project_local_state")
        if "prompt_library" in patterns:
            targets.append("task_prompt_templates")
        if "style_guide_layering" in patterns:
            targets.append("style_layers")
            targets.append("character_voice_notes")
            targets.append("scene_style_overrides")
        if "review_queue_staging" in patterns:
            targets.append("pending_change_review_queue")
        if "entity_schema_custom_fields" in patterns:
            targets.append("genre_custom_fields")
            targets.append("entity_field_schema")
        if "scene_level_generation" in patterns:
            targets.append("scene_plan")
            targets.append("scene_draft_units")
        if "content_ref_externalization" in patterns:
            targets.append("external_content_refs")
        if "graph_healing" in patterns:
            targets.append("graph_healing_actions")
        if "contradiction_detection" in patterns:
            targets.append("contradiction_findings")
        if "graph_branching_atomicity" in patterns:
            targets.append("canon_branch_snapshots")
        if "query_lint_contract" in patterns:
            targets.append("query_lint_rules")
        if "layered_memory_model" in patterns:
            targets.append("memory_layers")
            targets.append("character_state_layer")
        if "plot_dependency_graph" in patterns:
            targets.append("plot_dependency_edges")
        if "plotgrid_scene_matrix" in patterns:
            targets.append("scene_matrix_fields")
        if "plotline_thread_tracking" in patterns:
            targets.append("plotline_threads")
        if "scene_status_dashboard" in patterns:
            targets.append("scene_status_catalog")
        if "gradual_reveal_control" in patterns:
            targets.append("reveal_budget")
            targets.append("iceberg_annotations")
        if "setup_payoff_tracking" in patterns:
            targets.append("setup_payoff_ledger")
        if "scene_type_directing" in patterns:
            targets.append("scene_type_directives")
        if "worldpkg_export" in patterns:
            targets.append("worldpkg_schema")
            targets.append("entity_state_transitions")
        if "alternate_timeline_branching" in patterns:
            targets.append("alternate_timeline_branches")
        if "divergence_guidance" in patterns:
            targets.append("divergence_guidance_rules")
        if "context_pack_preview" in patterns:
            targets.append("context_pack_manifest")
            targets.append("retrieval_reason_index")
        if "accepted_chapter_memory" in patterns:
            targets.append("accepted_chapter_memory_log")
            targets.append("canon_write_back_rules")
        if "critic_verifier_loop" in patterns:
            targets.append("critic_review_schema")
        if "collapse_prevention" in patterns:
            targets.append("collapse_risk_rules")
        if "trend_deconstruction_pipeline" in patterns:
            targets.append("trope_module_library")
            targets.append("reader_expectation_profile")
        if "anti_ai_tone_polish" in patterns:
            targets.append("anti_ai_tone_rules")
        if "preference_memory" in patterns:
            targets.append("user_preference_memory")
        if "interrupted_resume_flow" in patterns:
            targets.append("resume_checkpoint")
        if "auto_validation_rewrite" in patterns:
            targets.append("auto_validation_rules")
        if "top_down_story_planning" in patterns:
            targets.append("book_spec")
            targets.append("chapter_scene_plan")
        if "organization_graph" in patterns:
            targets.append("organizations")
        if "emotion_arc" in patterns:
            targets.append("conflicts")
            targets.append("story_arcs")
        if "book_decomposition" in patterns or "continuation" in patterns:
            targets.append("foreshadows")
            targets.append("chapter_change_packages")
        return self._dedupe_texts(targets)

    def _build_whole_book_analysis_targets(self, patterns: set[str]) -> list[str]:
        targets = [
            "world_rules",
            "timeline",
            "character_cards",
            "organizations",
            "conflicts",
            "story_arcs",
            "foreshadows",
            "style_signature",
            "chapter_change_packages",
        ]
        if "card_workbench" in patterns:
            targets.extend(["card_types", "card_field_dependencies"])
        if "structured_generation_schema" in patterns:
            targets.extend(["schema_bound_outputs", "required_fields", "validation_failures"])
        if "context_reference" in patterns:
            targets.extend(["context_references", "knowledge_graph_edges", "retrieval_scope"])
        if "workflow_agent_pipeline" in patterns:
            targets.extend(["workflow_nodes", "workflow_triggers", "resume_checkpoint"])
        if "scene_asset_pipeline" in patterns:
            targets.extend(["scene_assets", "shot_beats", "production_step_outputs"])
        if "quality_score_loop" in patterns:
            targets.extend(["quality_scores", "keep_discard_decisions", "plateau_detection"])
        if "voice_fingerprint" in patterns:
            targets.extend(["voice_fingerprint", "voice_guardrails", "voice_discovery_notes"])
        if "anti_slop_audit" in patterns:
            targets.extend(["anti_slop_findings", "anti_pattern_findings"])
        if "publication_pipeline" in patterns:
            targets.extend(["export_targets", "delivery_artifacts"])
        if "lorebook_context" in patterns:
            targets.extend(["activated_lore_entries", "context_budget_usage", "recursive_context_links"])
        if "author_note_layer" in patterns:
            targets.extend(["author_note_layer", "style_directive_layer", "insertion_frequency"])
        if "world_state_tracking" in patterns:
            targets.extend(["world_state_entities", "location_state", "inventory_state", "scene_logs"])
        if "memory_snapshot_versioning" in patterns:
            targets.extend(["memory_snapshots", "state_branches", "rollback_points", "merge_conflicts"])
        if "local_first_novel_workspace" in patterns:
            targets.extend(["local_workspace_scope", "active_project_state", "workspace_metadata"])
        if "prompt_library" in patterns:
            targets.extend(["task_prompt_library", "prompt_template_versions", "prompt_scope"])
        if "style_guide_layering" in patterns:
            targets.extend(["style_layers", "scene_style_overrides", "character_voice_notes"])
        if "review_queue_staging" in patterns:
            targets.extend(["pending_change_review_queue", "staged_ai_outputs", "accept_reject_decisions"])
        if "entity_schema_custom_fields" in patterns:
            targets.extend(["entity_field_schema", "genre_custom_fields", "field_validation_rules"])
        if "scene_level_generation" in patterns:
            targets.extend(["scene_plan", "scene_drafts", "scene_context_slices", "scene_extraction_results"])
        if "content_ref_externalization" in patterns:
            targets.extend(["external_content_refs", "content_ref_checksums", "large_artifact_index"])
        if "graph_healing" in patterns:
            targets.extend(["graph_healing_actions", "duplicate_entity_candidates", "orphan_state_cleanup"])
        if "contradiction_detection" in patterns:
            targets.extend(["contradiction_findings", "timeline_conflicts", "relationship_drift"])
        if "graph_branching_atomicity" in patterns:
            targets.extend(["canon_branch_snapshots", "branch_merge_conflicts", "atomic_state_publish"])
        if "query_lint_contract" in patterns:
            targets.extend(["query_lint_findings", "schema_lint_findings", "mutation_contract_checks"])
        if "premature_ending_guard" in patterns:
            targets.extend(["anti_ending_checks", "false_resolution_findings"])
        if "layered_memory_model" in patterns:
            targets.extend(["memory_layer_coverage", "character_state_layer", "plot_graph_layer"])
        if "plot_dependency_graph" in patterns:
            targets.extend(["plot_dependency_edges", "setup_payoff_dependencies"])
        if "plotgrid_scene_matrix" in patterns:
            targets.extend(["plotgrid_scene_matrix", "scene_thread_cells", "pov_location_emotion_columns"])
        if "plotline_thread_tracking" in patterns:
            targets.extend(["plotline_threads", "thread_status_map"])
        if "scene_status_dashboard" in patterns:
            targets.extend(["scene_status_dashboard", "scene_progress_states"])
        if "gradual_reveal_control" in patterns:
            targets.extend(["reveal_budget", "iceberg_annotations", "revealed_hidden_fact_ratio"])
        if "setup_payoff_tracking" in patterns:
            targets.extend(["setup_payoff_ledger", "payoff_windows", "unpaid_setup_risk"])
        if "scene_type_directing" in patterns:
            targets.extend(["scene_type_directives", "action_emotional_dialogue_modes", "camera_language_notes"])
        if "worldpkg_export" in patterns:
            targets.extend(["worldpkg_exports", "lorebook_export_units", "entity_state_transition_exports"])
        if "alternate_timeline_branching" in patterns:
            targets.extend(["alternate_timeline_branches", "branch_divergence_points"])
        if "divergence_guidance" in patterns:
            targets.extend(["divergence_guidance", "choice_to_consequence_map", "scene_adaptation_notes"])
        if "context_pack_preview" in patterns:
            targets.extend(["context_pack_manifest", "retrieval_evidence", "omitted_context_candidates"])
        if "accepted_chapter_memory" in patterns:
            targets.extend(["accepted_chapter_memory_log", "canon_write_back_events", "draft_acceptance_boundary"])
        if "critic_verifier_loop" in patterns:
            targets.extend(["critic_review_reports", "revision_actions", "verification_results"])
        if "collapse_prevention" in patterns:
            targets.extend(["collapse_risk_findings", "model_failure_retries", "invalid_output_rejections"])
        if "trend_deconstruction_pipeline" in patterns:
            targets.extend(["trend_deconstruction_notes", "trope_modules", "payoff_density_map", "reader_expectation_curve"])
        if "anti_ai_tone_polish" in patterns:
            targets.extend(["anti_ai_tone_findings", "naturalness_rewrite_actions"])
        if "preference_memory" in patterns:
            targets.extend(["user_preference_memory", "preference_application_notes"])
        if "interrupted_resume_flow" in patterns:
            targets.extend(["resume_checkpoint", "interrupted_task_state"])
        if "auto_validation_rewrite" in patterns:
            targets.extend(["auto_validation_results", "rewrite_attempts", "word_count_coherence_checks"])
        if "top_down_story_planning" in patterns:
            targets.extend(["book_spec", "act_plan", "chapter_scene_plan", "previous_scene_context"])
        if "emotion_arc" in patterns:
            targets.extend(["emotional_arc", "emotion_curve"])
        if "book_decomposition" in patterns or "continuation" in patterns:
            targets.append("source_state_snapshot")
        return self._dedupe_texts(targets)

    def _build_continuation_prompt_hints(self, patterns: set[str]) -> list[str]:
        hints = [
            "续写前先读取圣经草稿中的世界观、时间线、人物卡、组织关系、冲突与伏笔。",
            "下一章必须承接原书尾章的状态变化，不重置人物关系、情感线和因果线。",
        ]
        if "emotion_arc" in patterns:
            hints.append("把情感线当作连续状态处理：记录本章前后关系压力、误会、信任和欲望变化。")
        if "organization_graph" in patterns:
            hints.append("组织和势力关系要进入续写约束，避免角色突然脱离已有阵营逻辑。")
        if "chapter_generation" in patterns:
            hints.append("每章生成后输出本章变化包，供下一章读取。")
        if "quality_score_loop" in patterns:
            hints.append("章节草稿采用 keep/discard 质量门：低于阈值重试，高于阈值保留并进入下一章，避免无限打磨阻断长篇进度。")
        if "anti_slop_audit" in patterns:
            hints.append("生成前带入反 AI 味规则，生成后先清理机械感、同构段落和空泛正确对白，再进入人工式评审。")
        if "structured_generation_schema" in patterns:
            hints.append("把续写前置分析和章节变化包拆成固定 schema 字段，缺字段时先补齐状态再生成正文。")
        if "card_workbench" in patterns:
            hints.append("把人物、组织、地点、伏笔、情感线拆成可复用卡片，章节提示词只引用本章需要的卡片字段。")
        if "context_reference" in patterns:
            hints.append("显式列出本章引用的上下文来源，避免把未检索或未确认的信息写入续写正史。")
        if "lorebook_context" in patterns:
            hints.append("Activate lorebook entries by chapter goal and keywords; inject only the entries needed by the current scene.")
        if "author_note_layer" in patterns:
            hints.append("Use the author-note layer for local style or scene reminders, never as a replacement for bible, plan, or change-package state.")
        if "workflow_agent_pipeline" in patterns:
            hints.append("把拆书、建卡、生成、评审、回写拆成可恢复工作流节点，失败后从最近 checkpoint 继续。")
        if "scene_level_generation" in patterns:
            hints.append("先规划场景列表，再逐场景生成；每个场景只注入本场需要的人物、地点、伏笔和前文切片。")
        if "contradiction_detection" in patterns:
            hints.append("章节进入正史前先检查时间线、人物状态、关系演化和设定规则是否互相冲突。")
        if "premature_ending_guard" in patterns:
            hints.append("章节验收前检查是否过早解决主冲突、跳过伏笔回收窗口，或把阶段性胜利误写成全书终局。")
        if "gradual_reveal_control" in patterns:
            hints.append("控制信息释放：本章只揭示当前行动能自然暴露的设定，隐藏层设定留给后续触发。")
        if "setup_payoff_tracking" in patterns:
            hints.append("每次回收伏笔前先核对 setup/payoff ledger，避免无铺垫回收或重复回收。")
        if "scene_type_directing" in patterns:
            hints.append("每个场景先声明动作、情感、对话或转场类型，再选择节奏、镜头感和信息密度。")
        if "context_pack_preview" in patterns:
            hints.append("生成前预览本章 context pack：只注入当前章节目标、已验收记忆、相关图谱事实和检索理由。")
        if "accepted_chapter_memory" in patterns:
            hints.append("草稿不直接写入正史；只有通过验收的章节才能抽取记忆并回写下一章可读状态。")
        if "critic_verifier_loop" in patterns:
            hints.append("把作者模型和评审模型职责分离：评审只输出问题、证据和返工项，不替代正史写回。")
        if "collapse_prevention" in patterns:
            hints.append("检测剧情崩坏风险：无效输出、人物断裂、因果坍塌或模型失败时先返工，不进入批量续写。")
        if "trend_deconstruction_pipeline" in patterns:
            hints.append("同类型仿写先拆题材套路、情绪满足、钩子密度和期待管理，再转化为本书的新模块。")
        if "anti_ai_tone_polish" in patterns:
            hints.append("最终润色要去 AI 味：减少解释腔、模板句、空泛总结，让动作、对白和细节承担信息。")
        if "interrupted_resume_flow" in patterns:
            hints.append("续写任务恢复时先读取断点、最后验收章节、未完成章节和最近失败原因，再继续生成。")
        if "auto_validation_rewrite" in patterns:
            hints.append("章节验收包含字数、连贯性、钩子、风格和状态写回；不合格章节进入有限轮次自动重写。")
        if "top_down_story_planning" in patterns:
            hints.append("长篇规划从 book spec 到卷/章/场景逐级展开，当前场景写作必须承接上一场景文本状态。")
        return hints

    def _build_continuation_state_hints(self, patterns: set[str]) -> list[str]:
        hints = [
            "Persist a state snapshot at each chapter ending: world, timeline, characters, organizations, emotion, and hooks must be readable by the next chapter.",
            "Read recent chapter_change_packages before choosing the next continuation start, conflict, and causal bridge.",
        ]
        if "emotion_arc" in patterns:
            hints.append("Treat emotional arc as inherited state, not as one-off plot decoration.")
        if "book_decomposition" in patterns or "continuation" in patterns:
            hints.append("Write back the state snapshot, chapter change package, and unresolved hooks after every continuation pass.")
        if "quality_score_loop" in patterns:
            hints.append("Store score, accepted/rejected decision, retry reason, and plateau signal with each chapter state.")
        if "structured_generation_schema" in patterns:
            hints.append("Validate state snapshots against a schema before the next generation pass; missing required fields block drafting.")
        if "card_workbench" in patterns:
            hints.append("Update card-level fields instead of overwriting the whole bible when one chapter changes only part of a character, faction, or hook.")
        if "context_reference" in patterns:
            hints.append("Keep a compact context reference list with source artifact, card id, chapter id, and reason for inclusion.")
        if "lorebook_context" in patterns:
            hints.append("Persist which lorebook entries were activated, why they were selected, and how many context tokens they consumed.")
        if "world_state_tracking" in patterns:
            hints.append("Track state by entity and location after each scene so long continuations can update only the affected slice.")
        if "memory_snapshot_versioning" in patterns:
            hints.append("Create rollback points before major bible, plan, or chapter-state rewrites so rejected continuations can be reverted.")
        if "workflow_agent_pipeline" in patterns:
            hints.append("Store workflow node status, retry count, and last accepted artifact so long runs can resume without rereading unrelated context.")
        if "content_ref_externalization" in patterns:
            hints.append("Store large drafts, scene plans, and extraction payloads as external content refs with size and checksum instead of bloating the live state.")
        if "graph_branching_atomicity" in patterns:
            hints.append("Use a branch/snapshot boundary for risky multi-step canon updates; merge only after all state slices pass review.")
        if "layered_memory_model" in patterns:
            hints.append("Keep memory layers separate: stable bible, current character state, and plot dependency graph should be updated by different evidence.")
        if "plot_dependency_graph" in patterns:
            hints.append("Persist plot dependency edges so a payoff can prove which setup, clue, promise, or unresolved hook authorized it.")
        if "plotgrid_scene_matrix" in patterns:
            hints.append("Keep a scene matrix row for each planned scene with plotline, POV, location, emotion, status, and linked hooks.")
        if "alternate_timeline_branching" in patterns:
            hints.append("Store alternate timelines as branch state; never merge divergence choices back into faithful continuation canon without explicit approval.")
        if "worldpkg_export" in patterns:
            hints.append("Export reusable world packages as derived artifacts; canonical state remains the reviewed bible and chapter change packages.")
        if "context_pack_preview" in patterns:
            hints.append("Persist the context pack manifest with included facts, retrieval reason, token budget, and omitted-but-relevant candidates.")
        if "accepted_chapter_memory" in patterns:
            hints.append("Mark draft, reviewed, accepted, and rejected chapter states separately so rejected prose cannot leak into memory.")
        if "critic_verifier_loop" in patterns:
            hints.append("Store critic feedback, revision action, and verifier result beside each attempt for replayable quality history.")
        if "collapse_prevention" in patterns:
            hints.append("When a chapter fails validation, persist the collapse reason and resume from the last accepted state.")
        if "preference_memory" in patterns:
            hints.append("Keep user preference memory separate from canon; apply it as style/format preference, not as story fact.")
        if "interrupted_resume_flow" in patterns:
            hints.append("Every long run should keep a resumable checkpoint: current phase, chapter, scene, accepted artifact, and next action.")
        if "auto_validation_rewrite" in patterns:
            hints.append("Record validation pass/fail status, rewrite count, and remaining retry budget before moving to the next chapter.")
        if "top_down_story_planning" in patterns:
            hints.append("Persist the hierarchy from book spec to act, chapter, scene, and previous-scene context so partial generation can resume at the right scale.")
        return hints

    def _build_style_signature_hints(self, patterns: set[str]) -> list[str]:
        hints = [
            "抽取叙事视角、句长、段落节奏、对白密度、情绪温度和爽点释放方式。",
            "续写要保留原书味道，但只吸收写法模式，不复制外部项目代码或长文本。",
        ]
        if "style_signature" in patterns:
            hints.append("把风格签名作为硬约束写入续写提示词，而不是只写成泛化风格建议。")
        if "voice_fingerprint" in patterns:
            hints.append("维护 voice fingerprint：分离固定风格护栏和本书生成过程中发现的具体语气、节奏、比喻习惯。")
        if "structured_generation_schema" in patterns:
            hints.append("把风格签名拆成可校验字段：句长、对白率、段落密度、视角习惯、情绪温度和场景切换速度。")
        if "scene_asset_pipeline" in patterns:
            hints.append("用场景/镜头级资产表抽取叙事节奏：每场的目标、冲突、转折、道具和情绪出口都要可追踪。")
        if "style_guide_layering" in patterns:
            hints.append("按全书基础风格、当前场景覆写、出场角色声纹三层组织风格约束。")
        return hints

    def _build_style_fidelity_hints(self, patterns: set[str]) -> list[str]:
        hints = [
            "Preserve the original voice, cadence, and narrative temperature; style preservation is a hard constraint, not a loose suggestion.",
            "Keep the source book's flavor by matching sentence rhythm, POV behavior, scene density, and emotional pressure.",
        ]
        if "style_signature" in patterns:
            hints.append("Use the style signature as a guardrail that constrains the rewrite, not as a generic inspiration note.")
        if "voice_fingerprint" in patterns:
            hints.append("Compare each accepted draft against the voice fingerprint before it can update canon or downstream chapter state.")
        if "structured_generation_schema" in patterns:
            hints.append("Measure fidelity from structured style fields before accepting a chapter draft.")
        if "scene_asset_pipeline" in patterns:
            hints.append("Preserve scene rhythm by matching conflict entry, beat escalation, and exit timing rather than copying wording.")
        if "style_guide_layering" in patterns:
            hints.append("Apply base style first, then scene overrides, then character voice notes for dialogue-heavy scenes.")
        return hints

    def _build_structured_generation_hints(self, patterns: set[str]) -> list[str]:
        hints: list[str] = []
        if "structured_generation_schema" in patterns:
            hints.extend(
                [
                    "Use schema-bound outputs for bible extraction, chapter intent, change packages, review findings, and retry decisions.",
                    "Treat schema validation failure as a drafting blocker; repair missing or inconsistent fields before continuing.",
                ]
            )
        if "card_workbench" in patterns:
            hints.append("Generate and revise at field/card granularity so one bad field can be regenerated without discarding the whole artifact.")
        if "context_reference" in patterns:
            hints.append("Every generated field should declare which local context, card, chapter, or pattern-pack item supports it.")
        if "workflow_agent_pipeline" in patterns:
            hints.append("Workflow nodes should pass typed artifacts instead of free-form summaries between analysis, drafting, review, and write-back.")
        if "entity_schema_custom_fields" in patterns:
            hints.append("Genre-specific entity fields should be explicit schema slots so wuxia, sci-fi, fantasy, or urban stories can track different canon facts.")
        if "query_lint_contract" in patterns:
            hints.append("Lint schema and mutation contracts before accepting generated state updates.")
        return self._dedupe_texts(hints)

    def _build_card_workbench_hints(self, patterns: set[str]) -> list[str]:
        if "card_workbench" not in patterns:
            return []
        hints = [
            "Represent reusable canon as editable cards: character, organization, location, hook, relationship, style, and chapter-state cards.",
            "Card updates must be local and reviewable; do not silently rewrite unrelated bible sections when a chapter only changes one field.",
        ]
        if "structured_generation_schema" in patterns:
            hints.append("Each card type should have required fields and validation rules before AI fills or revises it.")
        if "context_reference" in patterns:
            hints.append("Cards should expose compact references that prompts can include without loading the whole project history.")
        return hints

    def _build_context_reference_hints(self, patterns: set[str]) -> list[str]:
        if "context_reference" not in patterns:
            return []
        hints = [
            "Build prompts from explicit context references: selected cards, recent chapter deltas, unresolved hooks, and relevant source-pattern notes.",
            "Context inclusion must be justified by the current chapter goal; unrelated cards stay out to reduce drift and token noise.",
        ]
        if "workflow_agent_pipeline" in patterns:
            hints.append("Persist the context reference set used by each workflow node so review can replay why a draft made a decision.")
        return hints

    def _build_scene_asset_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "scene_asset_pipeline" not in patterns:
            return []
        return [
            "Convert chapter intent into scene assets before drafting: scene goal, pressure source, cast, location, prop, reveal, and exit hook.",
            "For same-type imitation, borrow the production pipeline shape—idea, outline, scene list, beat assets, review—not the original scene content.",
            "Use scene assets as review units when chapter-level feedback is too coarse to locate pacing or continuity failures.",
        ]

    def _build_quality_score_loop_hints(self, patterns: set[str]) -> list[str]:
        if "quality_score_loop" not in patterns:
            return []
        hints = [
            "Use a modify-evaluate-keep/discard loop: draft or revise one artifact, score it, keep it only when it clears the configured threshold.",
            "Separate foundation scoring from chapter scoring so weak world/character/outline setup does not leak into every chapter.",
            "Use plateau detection to stop revision loops when scores stabilize and no major actionable issue remains.",
        ]
        if "workflow_agent_pipeline" in patterns:
            hints.append("Persist loop status per workflow node: attempt count, latest score, accepted artifact, and next retry reason.")
        return hints

    def _build_voice_fingerprint_hints(self, patterns: set[str]) -> list[str]:
        if "voice_fingerprint" not in patterns:
            return []
        hints = [
            "Keep a voice fingerprint separate from the general style card: immutable guardrails plus discovered per-book voice traits.",
            "Use voice fingerprint checks before accepting drafts and before using a chapter as future style evidence.",
        ]
        if "style_signature" in patterns:
            hints.append("Merge voice fingerprint results back into style fidelity review without copying source prose.")
        return hints

    def _build_anti_slop_audit_hints(self, patterns: set[str]) -> list[str]:
        if "anti_slop_audit" not in patterns:
            return []
        return [
            "Audit drafts for word-level AI tells, over-neat explanation, repeated sentence frames, generic wisdom dialogue, and scene-free summary.",
            "Treat anti-slop findings as concrete rewrite tasks, not as a single global quality score.",
            "Run anti-pattern checks before publication or batch merge so low-level prose drift does not accumulate across chapters.",
        ]

    def _build_publication_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "publication_pipeline" not in patterns:
            return []
        return [
            "Keep export as a downstream pipeline stage: manuscript, review report, ePub/TXT/PDF, audiobook script, and landing copy are derived artifacts.",
            "Do not let publication artifacts mutate canon; canon changes must flow through bible/state/chapter change packages first.",
        ]

    def _build_lorebook_context_hints(self, patterns: set[str]) -> list[str]:
        if "lorebook_context" not in patterns:
            return []
        hints = [
            "Store lorebook entries as compact fact cards with activation keywords, priority, insertion depth, and token budget.",
            "Use recursive activation only for directly related lore; broad always-on entries should stay short and high priority.",
            "Record inactive-but-relevant lore candidates so reviewers can see what context was omitted from a draft.",
        ]
        if "context_reference" in patterns:
            hints.append("Render activated lore as explicit context references instead of anonymous prompt stuffing.")
        return hints

    def _build_author_note_layer_hints(self, patterns: set[str]) -> list[str]:
        if "author_note_layer" not in patterns:
            return []
        return [
            "Keep author notes as a separate prompt layer for transient style, POV, pacing, or scene-temperature nudges.",
            "Author notes should have scope and expiry; remove or refresh them when the chapter goal changes.",
        ]

    def _build_world_state_tracking_hints(self, patterns: set[str]) -> list[str]:
        if "world_state_tracking" not in patterns:
            return []
        return [
            "Track story state by entity type: characters, locations, regions, factions, items, and open scene logs.",
            "After each generated scene, write only the changed entity slices and keep the review log linked to the triggering chapter.",
            "Use world-state diffs to catch impossible location jumps, missing inventory changes, and stale faction control.",
        ]

    def _build_memory_snapshot_versioning_hints(self, patterns: set[str]) -> list[str]:
        if "memory_snapshot_versioning" not in patterns:
            return []
        return [
            "Create named memory snapshots before risky rewrites, bulk bible merges, or alternate continuation branches.",
            "Treat rollback as a first-class operation: rejected drafts should revert state as well as prose.",
            "When two branches are merged, surface conflicts in canon facts, timeline, relationship state, and unresolved hooks.",
        ]

    def _build_local_first_workspace_hints(self, patterns: set[str]) -> list[str]:
        if "local_first_novel_workspace" not in patterns:
            return []
        return [
            "Scope remix analysis, continuation plans, style seeds, prompt choices, and draft state to the active novel/project workspace.",
            "Keep each project workspace independently reloadable so scratch intake, source canon, and generated continuation state do not leak across books.",
            "Record workspace metadata such as source title, genre, POV, tone, and last modified time as prompt selection signals.",
        ]

    def _build_prompt_library_hints(self, patterns: set[str]) -> list[str]:
        if "prompt_library" not in patterns:
            return []
        return [
            "Register task prompts by purpose: book decomposition, scene planning, continuation drafting, style imitation, review, and state write-back.",
            "Version prompt templates and record which template produced each accepted chapter or card update.",
            "Separate global system guidance from task-specific prompts so same-type creation and continuation do not reuse the wrong instruction layer.",
        ]

    def _build_style_guide_layering_hints(self, patterns: set[str]) -> list[str]:
        if "style_guide_layering" not in patterns:
            return []
        return [
            "Compose style context as base style guide → scene override → character voice notes.",
            "Scene overrides should be local and temporary: tense, POV, pacing, dialogue density, and emotional temperature for the current scene only.",
            "Character voice notes apply to dialogue and interiority without overriding world rules or continuation canon.",
        ]

    def _build_review_queue_staging_hints(self, patterns: set[str]) -> list[str]:
        if "review_queue_staging" not in patterns:
            return []
        return [
            "Stage AI-proposed bible, card, style, and chapter changes as pending changes before applying them to canon.",
            "Each pending change should keep proposed data, previous data, source task, batch id, and accept/edit/reject status.",
            "Batch review related AI changes together so a character card, relationship edge, and scene draft can be accepted in dependency order.",
        ]

    def _build_entity_schema_custom_fields_hints(self, patterns: set[str]) -> list[str]:
        if "entity_schema_custom_fields" not in patterns:
            return []
        return [
            "Let genre-specific entity schemas add fields beyond the base card: sect, ability, rank, taboo, technology, faction role, or item rule.",
            "Validate custom fields before they enter prompts so missing genre facts are caught during analysis instead of after drafting.",
            "Use custom fields in same-type creation to transform genre mechanics without copying source names or proprietary labels.",
        ]

    def _build_scene_level_generation_hints(self, patterns: set[str]) -> list[str]:
        if "scene_level_generation" not in patterns:
            return []
        hints = [
            "Plan chapters as ordered scene units before drafting; each scene carries goal, cast, location, pressure, reveal, and exit hook.",
            "Generate and review one scene at a time with a focused context slice, then assemble the accepted scene drafts into a chapter.",
            "Extract state changes at scene granularity so relationship shifts, location moves, and clue reveals stay attributable.",
        ]
        if "content_ref_externalization" in patterns:
            hints.append("Store large scene drafts externally and keep only lightweight refs in the continuation state.")
        return hints

    def _build_content_ref_externalization_hints(self, patterns: set[str]) -> list[str]:
        if "content_ref_externalization" not in patterns:
            return []
        return [
            "Externalize large outlines, drafts, scene lists, extraction payloads, and review reports behind content refs.",
            "Each content ref should include type, path or artifact id, size, checksum, and source chapter so replay can verify integrity.",
            "Keep prompts fed by summarized refs unless the current task requires opening the full artifact.",
        ]

    def _build_graph_healing_hints(self, patterns: set[str]) -> list[str]:
        if "graph_healing" not in patterns:
            return []
        return [
            "After extraction, detect duplicate entities, orphan lore, stale relationship edges, and provisional nodes.",
            "Treat graph healing candidates as reviewable changes; auto-merge only low-risk duplicates with clear evidence.",
            "Record graph healing history so future contradictions can be traced back to a merge, rename, or cleanup decision.",
        ]

    def _build_contradiction_detection_hints(self, patterns: set[str]) -> list[str]:
        if "contradiction_detection" not in patterns:
            return []
        return [
            "Check timeline order, location presence, relationship evolution, trait consistency, faction membership, and unresolved hook state before accepting drafts.",
            "Every contradiction should name the conflicting canon facts and the scene or chapter that introduced the drift.",
            "Revision guidance should fix concrete contradictions, then rerun extraction and validation before write-back.",
        ]

    def _build_graph_branching_atomicity_hints(self, patterns: set[str]) -> list[str]:
        if "graph_branching_atomicity" not in patterns:
            return []
        return [
            "Apply multi-step canon mutations through a branch-like workspace, then publish atomically after validation.",
            "Use snapshots before bulk bible merges or alternate continuation branches so rejected work can roll back state and prose together.",
            "Surface merge conflicts in timeline, entity fields, relationship edges, hooks, and style cards instead of silently overwriting canon.",
        ]

    def _build_query_lint_contract_hints(self, patterns: set[str]) -> list[str]:
        if "query_lint_contract" not in patterns:
            return []
        return [
            "Lint generated state mutations before applying them: required fields, allowed relationship types, nullable fields, and delete/update separation.",
            "Keep stable lint codes or categories so review UI can group recurring canon-graph failures.",
            "Fail closed when a generated update cannot prove which entity, chapter, or relationship it intends to mutate.",
        ]

    def _build_premature_ending_guard_hints(self, patterns: set[str]) -> list[str]:
        if "premature_ending_guard" not in patterns:
            return []
        return [
            "Detect false endings before acceptance: unresolved main conflict, unpaid setup, missing cost, or skipped causal bridge means the chapter is not done.",
            "Treat a calm or victory scene as a stage beat unless the plan, hooks, and story arcs prove the whole-book endpoint is allowed.",
            "When the model tries to wrap up too early, revise toward a new complication, consequence, or deferred payoff rather than adding summary closure.",
        ]

    def _build_layered_memory_model_hints(self, patterns: set[str]) -> list[str]:
        if "layered_memory_model" not in patterns:
            return []
        return [
            "Keep memory layers separate: stable story bible, current character state, and plot dependency graph should be read and updated independently.",
            "A chapter may update character state without rewriting world rules; plot dependency updates need explicit setup/payoff evidence.",
            "Prompt assembly should name which layer each fact came from so stale character state does not override stable canon.",
        ]

    def _build_plot_dependency_graph_hints(self, patterns: set[str]) -> list[str]:
        if "plot_dependency_graph" not in patterns:
            return []
        return [
            "Represent hooks, clues, promises, conflicts, and payoffs as dependency edges with source chapter and expected payoff window.",
            "A payoff must trace to an active setup edge before it can enter canon.",
            "Review dangling setup edges before long continuation batches so unresolved promises are not forgotten.",
        ]

    def _build_plotgrid_scene_matrix_hints(self, patterns: set[str]) -> list[str]:
        if "plotgrid_scene_matrix" not in patterns:
            return []
        return [
            "Track each scene as a matrix row across plotline, POV, location, emotion, status, timeline position, and linked hooks.",
            "Use the matrix to spot missing thread coverage, repeated scene function, or abrupt POV/location jumps before drafting.",
            "For same-type creation, remap matrix function and pressure, not the source scene order.",
        ]

    def _build_plotline_thread_tracking_hints(self, patterns: set[str]) -> list[str]:
        if "plotline_thread_tracking" not in patterns:
            return []
        return [
            "Keep active, paused, paid-off, and abandoned plotlines visible across scenes.",
            "Every scene should advance, complicate, reveal, or deliberately rest at least one named thread.",
            "Before accepting a chapter, check whether any high-priority thread vanished without a state change.",
        ]

    def _build_scene_status_dashboard_hints(self, patterns: set[str]) -> list[str]:
        if "scene_status_dashboard" not in patterns:
            return []
        return [
            "Mark scene units by status: planned, drafted, reviewed, accepted, blocked, or rejected.",
            "Do not let rejected or blocked scenes update bible state, hooks, or future context.",
            "Use status plus review reason to resume long batches without rereading unrelated drafts.",
        ]

    def _build_gradual_reveal_control_hints(self, patterns: set[str]) -> list[str]:
        if "gradual_reveal_control" not in patterns:
            return []
        return [
            "Use a reveal budget: visible facts can enter the chapter, hidden facts stay out unless action/dialogue exposes them.",
            "Track iceberg annotations so worldbuilding depth exists without dumping it into the next scene.",
            "Review each chapter for over-explaining lore, premature secret exposure, and missing reader-facing clues.",
        ]

    def _build_setup_payoff_tracking_hints(self, patterns: set[str]) -> list[str]:
        if "setup_payoff_tracking" not in patterns:
            return []
        return [
            "Record every setup with source chapter, promised effect, expected payoff window, and current payoff status.",
            "Payoff acceptance requires a matching setup edge and a visible consequence in character, plot, or world state.",
            "Flag repeated payoff, orphan setup, and payoff without setup as review blockers.",
        ]

    def _build_scene_type_directing_hints(self, patterns: set[str]) -> list[str]:
        if "scene_type_directing" not in patterns:
            return []
        return [
            "Declare scene type before drafting: action, emotional, dialogue, investigation, transition, or reveal.",
            "Choose pacing, sensory density, dialogue ratio, and camera distance from the scene type.",
            "Review scene type drift when a scene starts as action but resolves through summary or exposition.",
        ]

    def _build_worldpkg_export_hints(self, patterns: set[str]) -> list[str]:
        if "worldpkg_export" not in patterns:
            return []
        return [
            "Export reusable world packages as derived artifacts: events, characters, locations, items, lorebook entries, and entity state transitions.",
            "Keep WorldPkg-style exports separate from canon write-back; imports must pass review before changing bible state.",
            "Use exports for replay, what-if branches, or external inspection without granting them authority over confirmed continuation canon.",
        ]

    def _build_alternate_timeline_branching_hints(self, patterns: set[str]) -> list[str]:
        if "alternate_timeline_branching" not in patterns:
            return []
        return [
            "Store what-if and same-world divergence as alternate timeline branches, not as faithful continuation state.",
            "Each branch needs a divergence point, changed assumption, affected entities, and merge/reject decision.",
            "Never let branch-only events satisfy hooks in the main canon unless an explicit merge is accepted.",
        ]

    def _build_divergence_guidance_hints(self, patterns: set[str]) -> list[str]:
        if "divergence_guidance" not in patterns:
            return []
        return [
            "Name the choice or premise change that causes divergence before drafting a branch scene.",
            "Map each divergence to immediate consequence, delayed consequence, and canon facts that stay fixed.",
            "For same-type creation, use divergence guidance to create independent causality rather than source-order replay.",
        ]

    def _build_context_pack_preview_hints(self, patterns: set[str]) -> list[str]:
        if "context_pack_preview" not in patterns:
            return []
        return [
            "Render a context-pack preview before drafting: chapter goal, accepted memory, graph facts, retrieval hits, and inclusion reason.",
            "Keep omitted-but-relevant context visible to reviewers so missing lore can be corrected without stuffing the prompt.",
            "Reject context packs that mix source inspiration with confirmed canon or include facts without retrieval reason.",
        ]

    def _build_accepted_chapter_memory_hints(self, patterns: set[str]) -> list[str]:
        if "accepted_chapter_memory" not in patterns:
            return []
        return [
            "Drafts do not update canon; only accepted chapters extract summaries, character states, graph facts, timeline events, and memory chunks.",
            "Each accepted chapter should record what memory changed and which next-chapter context pack may reuse it.",
            "Rejected drafts must keep their prose and extracted memory outside the active bible and retrieval index.",
        ]

    def _build_critic_verifier_loop_hints(self, patterns: set[str]) -> list[str]:
        if "critic_verifier_loop" not in patterns:
            return []
        return [
            "Separate writer/reviser output from critic/verifier feedback so review findings cannot silently become canon.",
            "Critique should name plot, character, setting, dialogue, mechanics, continuity, and style issues with actionable revision tasks.",
            "Verification passes only when revised text addresses the named issues and preserves the current story state.",
        ]

    def _build_collapse_prevention_hints(self, patterns: set[str]) -> list[str]:
        if "collapse_prevention" not in patterns:
            return []
        return [
            "Detect story collapse before acceptance: invalid model output, missing chapter goal, contradictory state, or causality break blocks write-back.",
            "On model failure, retry from the last accepted state and keep the failed attempt as review evidence, not as memory.",
            "Use collapse categories so batch runs stop on repeated structural failure instead of producing more broken chapters.",
        ]

    def _build_trend_deconstruction_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "trend_deconstruction_pipeline" not in patterns:
            return []
        return [
            "For same-type writing, deconstruct trend patterns into trope, hook, payoff, emotion promise, reader expectation, and reusable module shape.",
            "Transform modules before drafting: preserve emotional function and payoff density, not source names, order, or set pieces.",
            "Keep a module library with provenance and copy-risk notes so commercial-pattern learning stays separate from canon.",
        ]

    def _build_anti_ai_tone_polish_hints(self, patterns: set[str]) -> list[str]:
        if "anti_ai_tone_polish" not in patterns:
            return []
        return [
            "Polish for natural prose after continuity passes: replace explanation with action, sensory detail, subtext, and specific dialogue.",
            "Flag over-neat summaries, template transitions, generic wisdom, symmetrical paragraphs, and emotion labels as AI-tone risks.",
            "Anti-AI-tone edits must not paraphrase distinctive source passages or erase necessary canon facts.",
        ]

    def _build_preference_memory_hints(self, patterns: set[str]) -> list[str]:
        if "preference_memory" not in patterns:
            return []
        return [
            "Store reader/user preferences as separate writing preferences: genre, POV, chapter length, pacing, polish level, and taboo content.",
            "Preference memory can choose defaults and style pressure, but it cannot override world rules, continuation canon, or safety constraints.",
        ]

    def _build_interrupted_resume_flow_hints(self, patterns: set[str]) -> list[str]:
        if "interrupted_resume_flow" not in patterns:
            return []
        return [
            "Before resuming, detect unfinished phase, target chapter, current scene, last accepted artifact, failed attempt, and pending validation.",
            "Resume from the smallest safe unit: scene if a scene is in progress, chapter if the scene boundary is unclear, plan if canon changed.",
            "Do not ask for reconfirmation during automated continuation unless the checkpoint is ambiguous or conflicting.",
        ]

    def _build_auto_validation_rewrite_hints(self, patterns: set[str]) -> list[str]:
        if "auto_validation_rewrite" not in patterns:
            return []
        return [
            "Validate each chapter for required length, continuity, style fidelity, hook presence, and state write-back completeness.",
            "Failed chapters may rewrite within a bounded retry budget; each retry must target concrete validation failures.",
            "After retries are exhausted, mark the chapter blocked with evidence instead of accepting weak text.",
        ]

    def _build_top_down_story_planning_hints(self, patterns: set[str]) -> list[str]:
        if "top_down_story_planning" not in patterns:
            return []
        return [
            "Plan top-down: topic or premise -> book spec -> act plan -> chapter plan -> scene list -> scene draft.",
            "Let users or higher-level plans intervene at any scale, but lower-level generation must inherit the active parent plan.",
            "Each scene draft should know its chapter number, scene number, plan role, and previous-scene context.",
        ]

    def _build_inspired_mapping_targets(self, patterns: set[str]) -> list[str]:
        if not self._supports_inspired_creation(patterns):
            return []
        targets = [
            "character_remap",
            "organization_remap",
            "world_rule_remap",
            "plot_thread_remap",
        ]
        if "card_workbench" in patterns:
            targets.append("card_schema_remap")
        if "structured_generation_schema" in patterns:
            targets.append("schema_field_remap")
        if "context_reference" in patterns:
            targets.append("context_reference_remap")
        if "scene_asset_pipeline" in patterns:
            targets.append("scene_asset_remap")
        if "scene_level_generation" in patterns:
            targets.append("scene_plan_remap")
        if "style_guide_layering" in patterns:
            targets.append("style_layer_remap")
        if "entity_schema_custom_fields" in patterns:
            targets.append("custom_field_remap")
        if "review_queue_staging" in patterns:
            targets.append("review_queue_gate")
        if "graph_branching_atomicity" in patterns:
            targets.append("branch_snapshot_remap")
        if "quality_score_loop" in patterns:
            targets.append("quality_gate_remap")
        if "voice_fingerprint" in patterns:
            targets.append("voice_fingerprint")
        if "anti_slop_audit" in patterns:
            targets.append("anti_slop_rules")
        if "organization_graph" in patterns:
            targets.append("relationship_graph_remap")
        if "style_signature" in patterns:
            targets.append("style_signature")
        if "emotion_arc" in patterns:
            targets.append("emotional_arc")
        if "premature_ending_guard" in patterns:
            targets.append("ending_guard_remap")
        if "plot_dependency_graph" in patterns:
            targets.append("plot_dependency_remap")
        if "plotgrid_scene_matrix" in patterns or "plotline_thread_tracking" in patterns:
            targets.append("plotline_matrix_remap")
        if "gradual_reveal_control" in patterns:
            targets.append("reveal_budget_remap")
        if "setup_payoff_tracking" in patterns:
            targets.append("setup_payoff_remap")
        if "alternate_timeline_branching" in patterns:
            targets.append("branch_divergence_remap")
        if "trend_deconstruction_pipeline" in patterns:
            targets.append("trope_module_remap")
            targets.append("reader_expectation_remap")
        if "context_pack_preview" in patterns:
            targets.append("context_pack_boundary")
        if "critic_verifier_loop" in patterns:
            targets.append("critic_gate_remap")
        if "anti_ai_tone_polish" in patterns:
            targets.append("anti_ai_tone_rules")
        if "top_down_story_planning" in patterns:
            targets.append("plan_hierarchy_remap")
        return self._dedupe_texts(targets)

    def _build_inspired_prompt_hints(self, patterns: set[str]) -> list[str]:
        if not self._supports_inspired_creation(patterns):
            return []
        hints = [
            "Use the source only as style, rhythm, POV, pacing, scene-density, and emotional-temperature guidance.",
            "Generate an independent new story with new names, organizations, event chain, core conflict, and world rules.",
        ]
        if "style_signature" in patterns:
            hints.append("Carry the style signature into drafting and review, but do not preserve source facts as canon.")
        if "chapter_generation" in patterns:
            hints.append("Draft from a fresh outline/beat sheet; do not reuse the source chapter order as the new chapter order.")
        if "card_workbench" in patterns:
            hints.append("Use card structure as the workbench shape, but create new card content for characters, factions, places, and hooks.")
        if "structured_generation_schema" in patterns:
            hints.append("Use schema constraints to force completeness and independence, especially for renamed entities and transformed conflicts.")
        if "context_reference" in patterns:
            hints.append("Keep source-pattern references separate from new-story canon references so inspiration never becomes factual canon.")
        if "scene_asset_pipeline" in patterns:
            hints.append("Transform scene assets at the level of function and pressure, not at the level of source event sequence.")
        if "quality_score_loop" in patterns:
            hints.append("Use quality scores to decide whether a transformed draft is acceptable; do not lower the threshold because it resembles a source.")
        if "voice_fingerprint" in patterns:
            hints.append("Build a new voice fingerprint for the new story instead of inheriting source-book wording or signature phrases.")
        if "anti_slop_audit" in patterns:
            hints.append("Anti-slop review should remove generic AI prose without pushing the text back toward copied source phrasing.")
        if "premature_ending_guard" in patterns:
            hints.append("Preserve anti-ending pressure: the new story should avoid early total closure even if it borrows a satisfying beat shape.")
        if "plotgrid_scene_matrix" in patterns:
            hints.append("Build a new plotline/scene matrix for the new story; do not reuse the source scene rows or payoff order.")
        if "gradual_reveal_control" in patterns:
            hints.append("Create a fresh reveal budget so genre secrets unfold independently from the source book.")
        if "trend_deconstruction_pipeline" in patterns:
            hints.append("Use trend/deconstruction notes only as module shapes for reader expectation and payoff; rebuild premise, cast, and event chain.")
        if "context_pack_preview" in patterns:
            hints.append("The new story's context pack must cite transformed canon only; source deconstruction may appear as craft notes, not facts.")
        if "critic_verifier_loop" in patterns:
            hints.append("Run critic/verifier checks for independence as well as quality before accepting a same-type draft.")
        if "anti_ai_tone_polish" in patterns:
            hints.append("Anti-AI-tone polish should make the new prose more specific, not closer to source phrasing.")
        if "top_down_story_planning" in patterns:
            hints.append("Build a fresh top-down plan hierarchy so the new story is not a chapter-by-chapter route clone.")
        return hints

    def _build_inspired_transformation_hints(self, patterns: set[str]) -> list[str]:
        if not self._supports_inspired_creation(patterns):
            return []
        hints = [
            "Rename source characters and reframe their identity, role, desire, and relationship pressure before drafting.",
            "Replace source organizations, abilities, locations, and plot triggers with transformed equivalents.",
        ]
        if "worldbuilding" in patterns:
            hints.append("Transform the world rules first, then derive new plot constraints from the transformed world.")
        if "emotion_arc" in patterns:
            hints.append("Preserve the emotional function of a relationship beat while changing who causes it and why.")
        if "card_workbench" in patterns:
            hints.append("Remap card by card: a source role can inspire a new role, but every card needs new identity, constraints, and arc.")
        if "structured_generation_schema" in patterns:
            hints.append("Check transformed fields against required schema slots so no source-only proper noun or event label survives.")
        if "scene_asset_pipeline" in patterns:
            hints.append("Rebuild each scene asset from a new premise, location, cast, pressure source, and exit hook.")
        if "quality_score_loop" in patterns:
            hints.append("Keep/discard decisions should evaluate transformed-story quality and independence together.")
        if "voice_fingerprint" in patterns:
            hints.append("Translate source voice functions into new voice guardrails, not into reused sentence templates.")
        if "plot_dependency_graph" in patterns:
            hints.append("Rebuild dependency edges from new promises and clues; a source setup can inspire a function but not a factual dependency.")
        if "setup_payoff_tracking" in patterns:
            hints.append("Transform setup/payoff pairs by changing the promise, cost, and payoff consequence.")
        if "alternate_timeline_branching" in patterns:
            hints.append("Use branch divergence as a design tool for independent causality, not as a renamed source route.")
        if "trend_deconstruction_pipeline" in patterns:
            hints.append("Transform trope modules by changing desire, obstacle, cost, payoff timing, and reader-facing promise.")
        if "top_down_story_planning" in patterns:
            hints.append("Regenerate book spec, act plan, chapter plan, and scene list from the transformed premise before drafting prose.")
        if "context_pack_preview" in patterns:
            hints.append("Build a context pack from the transformed story state; do not retrieve source events as if they were reusable canon.")
        return hints

    def _build_inspired_copy_risk_hints(self, patterns: set[str]) -> list[str]:
        if not self._supports_inspired_creation(patterns):
            return []
        hints = [
            "Reject copied source names, proper nouns, scene order, set-piece sequence, and distinctive event wording.",
            "Similarity should live in genre feel and narrative mechanics, not in source facts, labels, or paragraph-level phrasing.",
        ]
        if "self_review" in patterns:
            hints.append("Review each generated chapter for source-copy risk before accepting it.")
        if "structured_generation_schema" in patterns:
            hints.append("Run copy-risk checks on structured fields as well as prose, because copied names and set-pieces often enter through planning cards.")
        if "context_reference" in patterns:
            hints.append("Reject drafts whose cited context reference points to source material as if it were new-story canon.")
        if "voice_fingerprint" in patterns:
            hints.append("Reject voice fingerprints that preserve source catchphrases, proprietary labels, or paragraph-level phrasing.")
        if "anti_slop_audit" in patterns:
            hints.append("Do not use anti-slop cleanup as a license to paraphrase distinctive source passages.")
        if "plotgrid_scene_matrix" in patterns:
            hints.append("Reject transformed outlines that preserve the source plotline matrix row order or scene-function sequence.")
        if "setup_payoff_tracking" in patterns:
            hints.append("Reject copied setup/payoff timing when the same clue, promise, and payoff window survive under new names.")
        if "worldpkg_export" in patterns:
            hints.append("Do not import source WorldPkg facts as new-story canon; exports are analysis artifacts only.")
        if "trend_deconstruction_pipeline" in patterns:
            hints.append("Reject drafts whose trope module library preserves source plot order, named gimmicks, or signature set-piece sequence.")
        if "context_pack_preview" in patterns:
            hints.append("Reject context packs that cite source analysis artifacts as new-story facts.")
        if "top_down_story_planning" in patterns:
            hints.append("Reject plan hierarchies that mirror the source act/chapter/scene route under renamed labels.")
        return hints

    def _supports_inspired_creation(self, patterns: set[str]) -> bool:
        if "same_type_creation" in patterns:
            return True
        if patterns.intersection(
            {
                "premature_ending_guard",
                "plotgrid_scene_matrix",
                "plotline_thread_tracking",
                "gradual_reveal_control",
                "setup_payoff_tracking",
                "alternate_timeline_branching",
                "divergence_guidance",
                "trend_deconstruction_pipeline",
                "context_pack_preview",
                "critic_verifier_loop",
                "top_down_story_planning",
            }
        ) and (
            "style_signature" in patterns
            or "chapter_generation" in patterns
            or "scene_type_directing" in patterns
            or "worldpkg_export" in patterns
            or "anti_ai_tone_polish" in patterns
        ):
            return True
        if "scene_asset_pipeline" in patterns and (
            "style_signature" in patterns
            or "structured_generation_schema" in patterns
            or "card_workbench" in patterns
        ):
            return True
        if "scene_level_generation" in patterns and (
            "style_guide_layering" in patterns
            or "entity_schema_custom_fields" in patterns
            or "review_queue_staging" in patterns
            or "contradiction_detection" in patterns
        ):
            return True
        return (
            "chapter_generation" in patterns
            and "style_signature" in patterns
            and (
                "character_cards" in patterns
                or "worldbuilding" in patterns
                or "book_decomposition" in patterns
                or "card_workbench" in patterns
                or "structured_generation_schema" in patterns
                or "quality_score_loop" in patterns
                or "voice_fingerprint" in patterns
                or "anti_slop_audit" in patterns
            )
        )

    def _build_self_review_policy_hints(self, patterns: set[str]) -> list[str]:
        hints = [
            "用户层允许不限次数自评优化；工程层必须使用可验证停止条件和安全上限。",
            "停止条件至少覆盖总分、读者追读分、高危问题数量和最大有效轮次。",
        ]
        if "self_review" in patterns:
            hints.append("每轮自评都要输出可执行返工说明，并优先修复设定冲突、人物跑偏和承接断裂。")
        return hints

    def _build_self_review_gate_hints(self, patterns: set[str]) -> list[str]:
        hints = [
            "Do not stop the rewrite loop until continuity conflicts, timeline drift, and style drift are all below threshold.",
            "Every revision must explain which canon risk was fixed and which story state was preserved.",
        ]
        if "self_review" in patterns:
            hints.append("The loop may repeat many times, but it must still stop when the checks stop finding new problems.")
        return hints

    def _build_chapter_change_package_hints(self, patterns: set[str]) -> list[str]:
        hints = [
            "Each chapter should emit a change package that includes timeline_delta, character_state_changes, foreshadow_changes, plan_progress, and emotional_arc.",
            "The chapter change package is the bridge between generation, analysis, bible sync, and the next continuation pass.",
        ]
        if "chapter_generation" in patterns or "continuation" in patterns:
            hints.append("Write the chapter change package as part of the state write-back path, not as an optional afterthought.")
        return hints

    def _build_pattern_pack_safety_constraints(self, ledger: dict[str, Any]) -> list[str]:
        constraints = [
            "只使用公开元数据、公开摘要和自研模式总结；不克隆、不安装、不执行外部项目。",
            "不导入外部代码、README 长段落、脚本、Docker、MCP 服务、浏览器扩展或 native binary。",
            "发现结果默认是 pattern-only；运行时试用必须另写本地安全合同。",
        ]
        constraints.extend(_text(note) for note in _as_list((ledger or {}).get("safety_notes")) if _text(note))
        return self._dedupe_texts(constraints)

    def _dedupe_texts(self, values: Iterable[Any]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            text = _text(value)
            if not text or text in seen:
                continue
            result.append(text)
            seen.add(text)
        return result

    def _rank_and_dedupe_candidates(self, candidates: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked_candidates = sorted(
            (candidate for candidate in candidates if isinstance(candidate, dict)),
            key=self._candidate_rank_key,
            reverse=True,
        )
        deduped: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        for candidate in ranked_candidates:
            normalized_url = self._normalize_candidate_url(candidate.get("url"))
            if not normalized_url or normalized_url in seen_urls:
                continue
            seen_urls.add(normalized_url)
            deduped.append(candidate)
        return deduped

    def _candidate_rank_key(self, candidate: dict[str, Any]) -> tuple[int, int, int, int, str]:
        summary = _text(candidate.get("summary"))
        return (
            int(candidate.get("score") or 0),
            int(candidate.get("stars") or 0),
            self._candidate_detail_score(candidate),
            len(summary),
            _text(candidate.get("title")),
        )

    def _candidate_detail_score(self, candidate: dict[str, Any]) -> int:
        summary = _text(candidate.get("summary"))
        absorbed_patterns = _as_list(candidate.get("absorbed_patterns"))
        risk_flags = _as_list(candidate.get("risk_flags"))
        updated_at = _text(candidate.get("updated_at"))
        return (
            (1 if summary else 0)
            + min(len(summary), 400) // 40
            + len(absorbed_patterns) * 3
            + len(risk_flags) * 2
            + (1 if updated_at else 0)
        )

    def _normalize_candidate_url(self, value: Any) -> str:
        raw = _text(value)
        if not raw:
            return ""
        parsed = urllib.parse.urlparse(raw)
        if parsed.scheme and parsed.netloc:
            path = parsed.path.rstrip("/")
            if path.endswith(".git"):
                path = path[:-4]
            return urllib.parse.urlunparse(
                (
                    parsed.scheme.lower(),
                    parsed.netloc.lower(),
                    path,
                    "",
                    "",
                    "",
                )
            )
        normalized = raw.rstrip("/")
        if normalized.endswith(".git"):
            normalized = normalized[:-4]
        return normalized

    def _parse_github_owner_repo(self, repository_url: Any) -> tuple[str, str] | None:
        raw = _text(repository_url)
        if not raw:
            return None
        parsed = urllib.parse.urlparse(raw)
        if parsed.scheme and parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            return None
        path = parsed.path if parsed.scheme else raw
        parts = [part for part in path.strip("/").split("/") if part]
        if len(parts) < 2:
            return None
        owner, repo = parts[0], parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        if not owner or not repo:
            return None
        return owner, repo

    async def _fetch_explicit_github_static_surface(
        self,
        *,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        surface: dict[str, Any] = {}
        try:
            response = await client.get(
                GITHUB_REPO_CONTENTS_API_URL.format(owner=owner, repo=repo, path="").rstrip("/"),
                headers=headers,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            payload = []

        if isinstance(payload, list):
            root_files = [
                _text(item.get("name"))
                for item in payload
                if isinstance(item, dict) and _text(item.get("name"))
            ]
            if root_files:
                surface["root_files"] = root_files

        package_scripts = await self._fetch_github_package_scripts(
            client=client,
            owner=owner,
            repo=repo,
            headers=headers,
        )
        if package_scripts:
            surface["package_scripts"] = package_scripts
        return surface

    async def _fetch_github_package_scripts(
        self,
        *,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        try:
            response = await client.get(
                GITHUB_REPO_CONTENTS_API_URL.format(owner=owner, repo=repo, path="package.json"),
                headers=headers,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return {}
        if not isinstance(payload, dict):
            return {}

        raw_content = _text(payload.get("content"))
        if not raw_content or _text(payload.get("encoding")).lower() != "base64":
            return {}
        try:
            package_payload = json.loads(base64.b64decode(raw_content).decode("utf-8"))
        except Exception:
            return {}
        scripts = package_payload.get("scripts") if isinstance(package_payload, dict) else None
        return scripts if isinstance(scripts, dict) else {}

    def _candidate_from_github(self, repository: dict[str, Any]) -> dict[str, Any]:
        topics = _as_list(repository.get("topics"))
        license_payload = repository.get("license") if isinstance(repository.get("license"), dict) else {}
        title = _text(repository.get("full_name") or repository.get("name"))
        description = _text(repository.get("description"))
        root_files = _as_list(repository.get("root_files"))
        scripts = repository.get("package_scripts") if isinstance(repository.get("package_scripts"), dict) else {}
        static_pattern_summary = self._static_repository_pattern_summary(title)
        haystack = _lower_haystack(
            title,
            description,
            static_pattern_summary,
            " ".join(map(str, topics)),
            " ".join(map(str, root_files)),
            json.dumps(scripts, ensure_ascii=False),
        )
        trust_review = self._build_github_trust_review(repository)
        return {
            "source": "github",
            "url": _text(repository.get("html_url")),
            "title": title,
            "summary": self._merge_candidate_summary(description, static_pattern_summary),
            "stars": repository.get("stargazers_count"),
            "license": _text(license_payload.get("spdx_id") or license_payload.get("key") or repository.get("license")),
            "family": self._classify_family(haystack),
            "posture": "pattern-only",
            "posture_hint": trust_review["posture_hint"],
            "risk_flags": self._risk_flags(haystack),
            "trust_review": trust_review,
            "absorbed_patterns": self._absorbed_patterns(haystack),
            "updated_at": _text(repository.get("updated_at")),
            "score": self._score_candidate(haystack, stars=repository.get("stargazers_count")),
        }

    def _static_repository_pattern_summary(self, title: str) -> str:
        return STATIC_REPOSITORY_PATTERN_OVERRIDES.get(title.lower(), "")

    def _merge_candidate_summary(self, description: str, static_pattern_summary: str) -> str:
        description = _text(description)
        static_pattern_summary = _text(static_pattern_summary)
        if description and static_pattern_summary:
            return f"{description} Static intake note: {static_pattern_summary}"
        return description or static_pattern_summary

    def _candidate_from_forum(self, item: dict[str, Any]) -> dict[str, Any]:
        title = _text(item.get("title"))
        summary = _text(item.get("summary") or item.get("description"))
        haystack = _lower_haystack(title, summary)
        return {
            "source": _text(item.get("source")) or "linux.do",
            "url": _text(item.get("url")),
            "title": title,
            "summary": summary,
            "stars": None,
            "license": "unknown",
            "family": self._classify_family(haystack),
            "posture": "pattern-only",
            "risk_flags": self._risk_flags(haystack),
            "absorbed_patterns": self._absorbed_patterns(haystack),
            "updated_at": _text(item.get("published_at")),
            "score": self._score_candidate(haystack, stars=None),
        }

    def _is_novel_candidate(self, candidate: dict[str, Any]) -> bool:
        return bool(candidate.get("url")) and candidate.get("family") == "novel-automation"

    def _classify_family(self, haystack: str) -> str:
        if any(keyword.lower() in haystack for keyword in NOVEL_KEYWORDS):
            return "novel-automation"
        if any(keyword.lower() in haystack for keyword in NARRATIVE_PRODUCTION_KEYWORDS):
            return "novel-automation"
        return "pattern-only"

    def _absorbed_patterns(self, haystack: str) -> list[str]:
        patterns: list[str] = []
        for pattern, keywords in PATTERN_KEYWORDS:
            if any(_contains_keyword(haystack, keyword) for keyword in keywords):
                patterns.append(pattern)
        patterns = patterns or ["source_discovery"]
        return self._expand_full_writing_chain_patterns(haystack, patterns)

    def _expand_full_writing_chain_patterns(self, haystack: str, patterns: list[str]) -> list[str]:
        expanded = list(patterns)
        novel_anchor_terms = (
            'novel',
            'fiction',
            'story',
            '小说',
            '故事',
            '网文',
        )
        workflow_signal_terms = (
            'chapter generation',
            'continuation',
            'story bible',
            'style analysis',
            'worldbuilding',
            'timeline',
            'character',
            'organization',
            'emotion',
            'review',
            'rewrite',
            'schema',
            'json schema',
            'structured generation',
            'card',
            'context injection',
            'knowledge graph',
            'workflow',
            'workflow agent',
            'storyboard',
            'shot list',
            'scene plan',
            '章节生成',
            '续写',
            '故事圣经',
            '风格分析',
            '世界观',
            '时间线',
            '人物',
            '组织',
            '情感',
            '评审',
            '改写',
            '结构化生成',
            '卡片',
            '上下文注入',
            '知识图谱',
            '工作流',
            '分镜',
            '镜头',
            '场景资产',
        )
        has_novel_anchor = any(term in haystack for term in novel_anchor_terms)
        workflow_signal_count = sum(1 for term in workflow_signal_terms if term in haystack)
        if has_novel_anchor and workflow_signal_count >= 3:
            for pattern in (
                "book_decomposition",
                "worldbuilding",
                "timeline",
                "character_cards",
                "organization_graph",
                "emotion_arc",
                "self_review",
            ):
                if pattern not in expanded:
                    expanded.append(pattern)
        return expanded

    def _risk_flags(self, haystack: str) -> list[str]:
        flags: list[str] = []
        for flag, keywords in RISK_FILE_KEYWORDS:
            if any(keyword.lower() in haystack for keyword in keywords):
                flags.append(flag)
        return flags

    def _build_github_trust_review(self, repository: dict[str, Any]) -> dict[str, Any]:
        flags: list[str] = []
        stars = self._int_value(repository.get("stargazers_count"))
        forks = self._int_value(repository.get("forks_count"))
        open_issues = self._int_value(repository.get("open_issues_count"))
        license_payload = repository.get("license") if isinstance(repository.get("license"), dict) else None
        license_value = ""
        if license_payload is not None:
            license_value = _text(license_payload.get("spdx_id") or license_payload.get("key"))
        else:
            license_value = _text(repository.get("license"))

        if not license_value:
            flags.append("license:missing")
        elif license_value.upper() in {"NOASSERTION", "UNKNOWN"}:
            flags.append("license:noassertion")

        if stars >= 1000:
            if bool(repository.get("has_issues", True)) and open_issues == 0:
                flags.append("zero-issues-high-stars")
            if repository.get("has_issues") is False:
                flags.append("issues:disabled-high-stars")
            if forks > 0 and forks / max(1, stars) < 0.01:
                flags.append("low-fork-high-star-ratio")
            if repository.get("has_downloads") is True:
                flags.append("downloads:enabled-high-stars")
            owner = repository.get("owner") if isinstance(repository.get("owner"), dict) else {}
            if _text(owner.get("type")).lower() == "user":
                flags.append("owner:user-high-star-tool")

        if repository.get("archived") is True:
            flags.append("repo:archived")
        if repository.get("disabled") is True:
            flags.append("repo:disabled")

        default_branch = _text(repository.get("default_branch"))
        if default_branch and default_branch not in {"main", "master"}:
            flags.append("default-branch:nonstandard")

        created_at = _parse_datetime(repository.get("created_at"))
        updated_at = _parse_datetime(repository.get("updated_at"))
        if stars >= 1000 and created_at and updated_at:
            age_days = (updated_at - created_at).days
            if age_days >= 0 and age_days < 60:
                flags.append("very-new-high-star-repo")

        flags = self._dedupe_texts(flags)
        posture_hint = "defer-trust-review" if len(flags) >= 2 else "metadata-triage"
        return {
            "review_basis": "github_metadata_only",
            "flags": flags,
            "posture_hint": posture_hint,
        }

    def _int_value(self, value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    def _score_candidate(self, haystack: str, *, stars: Any) -> int:
        score = sum(8 for keyword in NOVEL_KEYWORDS if keyword.lower() in haystack)
        for pattern, keywords in PATTERN_KEYWORDS:
            if any(keyword.lower() in haystack for keyword in keywords):
                score += 12
        try:
            star_count = int(stars or 0)
        except (TypeError, ValueError):
            star_count = 0
        if star_count >= 1000:
            score += 20
        elif star_count >= 100:
            score += 10
        elif star_count > 0:
            score += 3
        return score


source_discovery_service = NovelSourceDiscoveryService()
