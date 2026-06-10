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
    '("plain text" OR "synopsis" OR "cross-referencing") ("novel" OR "manuscript" OR "fiction") in:name,description,readme',
    '("snowflake method" OR "index cards" OR "outliner") ("novel" OR "writing" OR "manuscript") in:name,description,readme',
    '("narrative strands" OR "fabula" OR "character interview") ("novel" OR "writing") in:name,description,readme',
    '("mind mapping" OR "timeline planning" OR "grid planner") ("creative writing" OR "novel" OR "story") in:name,description,readme',
    '("human review of synopsis" OR "chapter summaries" OR "synopsis gate") ("novel" OR "story" OR "fiction") in:name,description,readme',
    '("retrieve relevant" OR "related text snippets" OR "sync update outline") ("long novel" OR "novel agent" OR "RAG") in:name,description,readme',
    '("intent.md" OR "context.json" OR "rule-stack.yaml" OR "trace.json") ("story" OR "novel" OR "writing") in:name,description,readme',
    '("recursive planning" OR "dynamic adaptation" OR "heterogeneous integration") ("fiction writing" OR "long-form writing" OR "story") in:name,description,readme',
    '("json schema" OR "schema-first" OR "structured generation") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("card" OR "cards" OR "context injection" OR "knowledge graph") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("workflow agent" OR "workflow studio" OR "progress recovery") ("novel" OR "fiction" OR "story") in:name,description,readme',
    '("continuity bridge" OR "voice table" OR "episode rewrite") ("web novel" OR "novel studio") in:name,description,readme',
    '("YAML frontmatter" OR "promise/payoff" OR "continuity questions") ("fiction" OR "story bible") in:name,description,readme',
    '("anti-hallucination" OR "bi-chapter review" OR "automatic backups") ("novel" OR "fiction") in:name,description,readme',
    '("boring detection" OR "opening check" OR "golden three chapters") ("web novel" OR "novel") in:name,description,readme',
    '("multi-level review" OR "trend tracking" OR "batch-level quality") ("novel" OR "fiction") in:name,description,readme',
    '("voice calibration" OR "final pre-flight" OR "generic AI tells") ("writing" OR "prose") in:name,description,readme',
    '("scene-by-scene objectives" OR "genre guides" OR "writing tasks") ("novel" OR "fiction") in:name,description,readme',
    '("sourcebook" OR "source book" OR "writing partner") ("novel" OR "AI writing") in:name,description,readme',
    '("long story consistency" OR "narrative consistency" OR "ConStory") ("LLM" OR "story generation") in:name,description,readme',
    '("cross-chapter redundancy" OR "full-book review" OR "parallel chapter drafting") ("novel" OR "fiction") in:name,description,readme',
    '("semantic search" OR "vector-based long-term context" OR "plot contradictions") ("novel" OR "chapter") in:name,description,readme',
    '("perplexity" OR "burstiness" OR "stylometry") ("humanize" OR "AI text") in:name,description,readme',
    '("story generation taxonomy" OR "LLM story generation" OR "story generation survey") ("novel" OR "script") in:name,description,readme',
    '("story bible" OR "plot threads" OR "continuity checker") ("writer" OR "editor" OR "chapter outlines") in:name,description,readme',
    '("narrative arc" OR "author style" OR "scenario blueprint") ("story mode" OR "fiction") in:name,description,readme',
    '("prompt recipes" OR "sampling grid" OR "append-only log") ("writing" OR "story") in:name,description,readme',
    '("hero journey" OR "Freytag" OR "Wikiquote" OR "story structure RAG") ("novel" OR "fiction") in:name,description,readme',
    '("novel to video" OR "script to scene" OR "character reference") ("AI" OR "film production") in:name,description,readme',
    '("NRD" OR "task tree" OR "revision passes") ("novel" OR "writing") in:name,description,readme',
    '("scene" OR "shot" OR "idea to production" OR "storyboard") ("AI" OR "Claude Code") in:name,description,readme',
    '("story contract" OR "chapter commit" OR "fact snapshot") ("webnovel" OR "novel" OR "long-form") in:name,description,readme',
    '("fact write-back" OR "state write-back" OR "generation gates") ("web novel" OR "novel writing") in:name,description,readme',
    '("foreshadowing debt" OR "follow-up rate" OR "reader retention") ("webnovel" OR "novel") in:name,description,readme',
    '("Draft A" OR "Draft B" OR "Draft C" OR "chapter blueprint") ("web novel" OR "fiction writing") in:name,description,readme',
    '("rolling summary" OR "character state tracking" OR "context trimming") ("long-form" OR "novel") in:name,description,readme',
    '("head-to-head story" OR "pairwise margins" OR "evaluator agreement") ("creative writing" OR "fiction") in:name,description,readme',
    '("q1" OR "q15" OR "ranked weaknesses" OR "overall score") ("story evaluation" OR "creative writing") in:name,description,readme',
    '("story theory" OR "beat interpolation" OR "beat revision" OR "Save the Cat") ("LLM" OR "story generation") in:name,description,readme',
    '("constraint specificity" OR "constraint satisfaction" OR "CS4") ("story generation" OR "creativity") in:name,description,readme',
    '("style fingerprints" OR "within-model diversity" OR "style axes") ("flash fiction" OR "creative writing") in:name,description,readme',
    '("goodreads" OR "ratings" OR "shelves" OR "to read") ("book" OR "reader" OR "recommendation") in:name,description,readme',
    '("spoiler detection" OR "book reviews" OR "reader reviews" OR "review corpus") ("goodreads" OR "fiction") in:name,description,readme',
    '("beta reader" OR "reader feedback" OR "want to continue" OR "stumble point") ("novel" OR "manuscript" OR "author") in:name,description,readme',
    '("comp title" OR "market positioning" OR "genre trends" OR "reader expectations") ("author" OR "novel" OR "book") in:name,description,readme',
    '("micro-tension" OR "reader curiosity" OR "chapter hook" OR "cliffhanger audit") ("novel" OR "manuscript") in:name,description,readme',
    '("docx" OR "markdown export" OR "table of contents" OR "title page") ("book" OR "manuscript" OR "novel") in:name,description,readme',
    '("KDP" OR "cover specs" OR "cover design" OR "page numbers") ("book" OR "manuscript" OR "novel") in:name,description,readme',
    '("interactive narrative" OR "branching story" OR "choice graph") ("fiction" OR "story" OR "narrative") in:name,description,readme',
    '("dialogue" OR "options" OR "commands" OR "variables") ("interactive fiction" OR "narrative") in:name,description,readme',
    '("passages" OR "links" OR "nonlinear stories" OR "multiple-choice games") ("fiction" OR "story") in:name,description,readme',
    '("winnowing" OR "document fingerprinting" OR "plagiarism detection") ("text" OR "source" OR "similarity") in:name,description,readme',
    '("fuzzy string matching" OR "Levenshtein" OR "string metrics") ("text" OR "similarity" OR "copy") in:name,description,readme',
    '("diff match patch" OR "semantic cleanup" OR "copied spans") ("text" OR "copy" OR "similarity") in:name,description,readme',
    '("MinHash" OR "LSH" OR "near duplicate") ("text dedup" OR "deduplication" OR "Jaccard") in:name,description,readme',
    '("SimHash" OR "Hamming distance" OR "near duplicate") ("text" OR "document" OR "similarity") in:name,description,readme',
    '("semantic deduplication" OR "embedding similarity" OR "semantic duplicates" OR "FAISS") ("text" OR "dataset" OR "corpus") in:name,description,readme',
    '("quote attribution" OR "character coreference" OR "speaker attribution") ("book" OR "novel" OR "fiction") in:name,description,readme',
    '("readability" OR "sentence length" OR "lexical diversity" OR "lexical richness") ("novel" OR "fiction" OR "text analysis") in:name,description,readme',
    '("prose lint" OR "prose linter" OR "style linter" OR "copyedit") ("novel" OR "fiction" OR "manuscript" OR "markdown") in:name,description,readme',
    '("grammar checker" OR "spell checker" OR "spelling and grammar" OR "proofreading") ("markdown" OR "manuscript" OR "fiction") in:name,description,readme',
    '("natural language linter" OR "text linter" OR "write-good" OR "proselint") ("prose" OR "writing" OR "markdown") in:name,description,readme',
    '("lint diagnostics" OR "style diagnostics" OR "copyedit suggestions" OR "accepted ignored") ("writing" OR "prose" OR "manuscript") in:name,description,readme',
    '("Chinese word segmentation" OR "jieba" OR "HanLP" OR "LTP") ("novel" OR "fiction" OR "text analysis") in:name,description,readme',
    '("Chinese NER" OR "named entity recognition" OR "alias" OR "entity linking") ("novel" OR "fiction" OR "Chinese text") in:name,description,readme',
    '("OpenCC" OR "Simplified Chinese" OR "Traditional Chinese" OR "Chinese conversion") ("novel" OR "manuscript" OR "text normalization") in:name,description,readme',
    '("Chinese spelling correction" OR "Chinese text correction" OR "pycorrector" OR "confusion set") ("novel" OR "manuscript" OR "proofreading") in:name,description,readme',
    '("EPUB" OR "ebook" OR "table of contents" OR "spine") ("novel" OR "manuscript" OR "chapter extraction") in:name,description,readme',
    '("PDF text extraction" OR "layout analysis" OR "text blocks" OR "page coordinates") ("book" OR "novel" OR "manuscript") in:name,description,readme',
    '("OCR" OR "scanned PDF" OR "hOCR" OR "Tesseract") ("book" OR "novel" OR "manuscript") in:name,description,readme',
    '("document partition" OR "partition_pdf" OR "partition_epub" OR "document elements") ("book" OR "chapter" OR "manuscript") in:name,description,readme',
    '("MarkItDown" OR "Docling" OR "MinerU" OR "marker") ("PDF" OR "DOCX" OR "Markdown" OR "LLM-ready") in:name,description,readme',
    '("pdf to markdown" OR "pdf-to-json" OR "document parser" OR "document conversion") ("book" OR "manuscript" OR "chapter import") in:name,description,readme',
    '("Pandoc" OR "format conversion" OR "metadata" OR "checksum") ("manuscript" OR "book" OR "chapter import") in:name,description,readme',
    '("Chinese Literature NER" OR "discourse-level NER" OR "relation extraction") ("literature" OR "novel" OR "fiction") in:name,description,readme',
    '("LitBank" OR "literary event detection" OR "literary entities") ("fiction" OR "literature" OR "novel") in:name,description,readme',
    '("narrative event evolutionary graph" OR "narrative event chain" OR "script event prediction") ("story" OR "event graph") in:name,description,readme',
    '("sentiment arcs" OR "sentiment-based plot arcs" OR "emotion in text over time") ("fiction" OR "novel" OR "text") in:name,description,readme',
    '("cross-context coreference" OR "cross-document coreference" OR "XCoref") ("entity" OR "event" OR "literature") in:name,description,readme',
    '("character network" OR "fictional character network" OR "character interactions") ("novel" OR "literary" OR "fiction") in:name,description,readme',
    '("stylometry" OR "computational stylistics" OR "Burrows Delta") ("authorship attribution" OR "author style" OR "fiction") in:name,description,readme',
    '("text reuse" OR "Burrow\'s delta" OR "pydelta") ("source similarity" OR "author style" OR "manuscript") in:name,description,readme',
    '("function words" OR "syntactic features" OR "lexical richness") ("authorship attribution" OR "writing style" OR "stylometry") in:name,description,readme',
    '("style change detection" OR "style breach detection" OR "intrinsic plagiarism") ("stylometry" OR "PAN") in:name,description,readme',
    '("stylometric transfer" OR "author-style transfer" OR "style fingerprint") ("LLM" OR "writing" OR "text") in:name,description,readme',
    '("anti-stylometry" OR "style anonymization" OR "paraphrase independence") ("text" OR "writing") in:name,description,readme',
    '("keyphrase extraction" OR "keyword extraction" OR "motif extraction") ("novel" OR "fiction" OR "narrative") in:name,description,readme',
    '("semantic chunk" OR "text splitter" OR "recursive character splitter") ("novel" OR "chapter" OR "long text") in:name,description,readme',
    '("summarization" OR "extractive summarizer" OR "chapter summary") ("novel" OR "book" OR "long text") in:name,description,readme',
    '("topic modeling" OR "dynamic topic" OR "topic drift") ("novel" OR "chapter" OR "narrative") in:name,description,readme',
    '("faithfulness" OR "context precision" OR "context recall" OR "groundedness") ("RAG" OR "LLM evaluation") in:name,description,readme',
    '("observability" OR "trace" OR "tracing" OR "retrieval traces") ("LLM" OR "RAG" OR "evals") in:name,description,readme',
    '("prompt tests" OR "golden dataset" OR "regression suite" OR "custom evals") ("LLM" OR "prompt") in:name,description,readme',
    '("AgentWrite" OR "LongWriter" OR "LongBench-Write" OR "LongWrite-Ruler") ("long-form" OR "long output" OR "story") in:name,description,readme',
    '("helpfulness" OR "logicality" OR "faithfulness" OR "completeness") ("long-context" OR "long output" OR "writing") in:name,description,readme',
    '("ultra-long" OR "10000+ words" OR "long output quality") ("writing" OR "generation" OR "story") in:name,description,readme',
    '("WritingBench" OR "instance-specific criteria" OR "requirement-dimension scores") ("writing" OR "generative writing") in:name,description,readme',
    '("creative writing benchmark" OR "hybrid rubric" OR "Glicko-2" OR "Elo") ("creative writing" OR "story") in:name,description,readme',
    '("longform creative writing benchmark" OR "critical reflection" OR "character profiles") ("longform" OR "story") in:name,description,readme',
    '("HANNA" OR "human-annotated narratives" OR "story evaluation") ("story generation" OR "automatic metrics") in:name,description,readme',
    '("Dramatron" OR "log line" OR "character descriptions" OR "plot points") ("hierarchical story generation" OR "co-writing") in:name,description,readme',
    '("recursive reprompting" OR "recursive reprompting and revision" OR "Plan Draft Rewrite Edit" OR "relevance reranker" OR "coherence reranker") ("long story" OR "story generation") in:name,description,readme',
    '("Chat-Haruhi" OR "character imitation" OR "novel character extraction") ("role-playing" OR "character dialogue") in:name,description,readme',
    '("event-to-sentence" OR "plot events into sentences" OR "slot filling" OR "memory graph") ("story realization" OR "story generation") in:name,description,readme',
    '("book memory bank" OR "stateless AI" OR "activeContext.md" OR "progress.md") ("book writing" OR "novel") in:name,description,readme',
    '("Spec Kit" OR "constitution.md" OR "scene-by-scene writing tasks" OR "story bible governance") ("fiction" OR "novel") in:name,description,readme',
    '("nested chapters" OR "parent section introductions" OR "table of contents") ("ebook summarizer" OR "chapter summaries" OR "book summary") in:name,description,readme',
    '("two-pass translation" OR "cumulative glossary" OR "previous chapter summary") ("novel translation" OR "serialized novels") in:name,description,readme',
    '("author notes" OR "edit notes" OR "source of truth") ("markdown files" OR "story framework" OR "fiction") in:name,description,readme',
    '("temporal knowledge graph" OR "temporal context graph" OR "provenance") ("AI agents" OR "agent memory") in:name,description,readme',
    '("multi-level memory" OR "long-term memory" OR "session state") ("AI agents" OR "personalized AI") in:name,description,readme',
    '("GraphRAG" OR "community summaries" OR "extract structured data from unstructured text") ("knowledge graph" OR "RAG") in:name,description,readme',
    '("dual-level architecture" OR "knowledge graphs" OR "vector embeddings") ("LightRAG" OR "RAG") in:name,description,readme',
    '("extract nodes" OR "relationships and properties" OR "custom schema") ("LLM graph builder" OR "knowledge graph") in:name,description,readme',
    '("novel2graph" OR "novel to graph" OR "character relationship graph") ("novel" OR "book" OR "literary text") in:name,description,readme',
    '("relationship graph" OR "event graph" OR "natural language search") ("novel" OR "fiction" OR "story bible") in:name,description,readme',
    '("TV Tropes" OR "tvtropes" OR "trope correlation") ("story" OR "fiction" OR "narrative") in:name,description,readme',
    '("trope graph" OR "trope network" OR "trope similarity") ("fiction" OR "story" OR "narrative") in:name,description,readme',
    '("character tropes" OR "trope dataset" OR "movie tropes") ("story" OR "fiction" OR "narrative") in:name,description,readme',
    '("license detection" OR "SPDX" OR "REUSE") ("source text" OR "corpus" OR "book") in:name,description,readme',
    '("Project Gutenberg" OR "public domain") ("metadata" OR "corpus" OR "book") in:name,description,readme',
    '("copyright" OR "license metadata" OR "attribution") ("ebook" OR "source text" OR "corpus") in:name,description,readme',
    '("PII" OR "de-identification" OR "anonymization" OR "redaction") ("named entity" OR "source text") in:name,description,readme',
    '("zero-shot NER" OR "custom entity types" OR "named entity recognition") ("fiction" OR "novel" OR "character") in:name,description,readme',
    '("proper noun" OR "entity redaction" OR "anonymize text") ("story" OR "fiction" OR "source text") in:name,description,readme',
    '("EPUBCheck" OR "EPUB conformance" OR "OPF manifest" OR "spine validation") ("ebook" OR "publication") in:name,description,readme',
    '("Ace by DAISY" OR "EPUB accessibility" OR "accessibility metadata" OR "WCAG") ("ebook" OR "reading system") in:name,description,readme',
    '("front matter" OR "back matter" OR "colophon" OR "titlepage") ("ebook" OR "EPUB" OR "manuscript") in:name,description,readme',
    '("EPUB tests" OR "navigation document" OR "nav toc" OR "spine order") ("ebook" OR "EPUB") in:name,description,readme',
    '("multi-agent framework" OR "seven specialized AI agents" OR "editorial pipeline") ("novel" OR "book" OR "fiction") in:name,description,readme',
    '("candidate is not canon" OR "preview confirm apply" OR "confirmed true") ("novel" OR "story" OR "creative writing") in:name,description,readme',
    '("spoiler filtering" OR "future chapter" OR "six-stage" OR "anti-rushing") ("novel" OR "chapter generation") in:name,description,readme',
    '("chapter control card" OR "control-cards" OR "dynamic state") ("Chinese long-form fiction" OR "webnovel" OR "novel") in:name,description,readme',
    '("trace replay" OR "chapter workbench" OR "Memory Browser") ("novel" OR "long-form writing") in:name,description,readme',
    '("global find replace" OR "Graphviz" OR "relationship graph") ("novel" OR "character" OR "writing") in:name,description,readme',
    '("permanent bible" OR "chapter-NN" OR "state/current" OR "chapter state") ("novel" OR "fiction" OR "Claude Code") in:name,description,readme',
    '("section metadata" OR "characters locations items" OR "pacing visualization" OR "plot points") ("novel" OR "writing" OR "manuscript") in:name,description,readme',
    '("AI writing fingerprints" OR "prose pattern scanner" OR "voice drift" OR "cluster detection") ("novel" OR "fiction" OR "manuscript") in:name,description,readme',
    '("BookRun" OR "Judge/Repair" OR "export audit" OR "real LLM smoke") ("novel" OR "story" OR "long-form writing") in:name,description,readme',
    '("provider budget" OR "LLM profile routing" OR "cost tracking" OR "smoke gate") ("novel" OR "writing" OR "agent") in:name,description,readme',
    '("Python sidecar" OR "graph/vector memory" OR "deployment profiles") ("novel" OR "long-form fiction" OR "writing workbench") in:name,description,readme',
    '("outline checkpoint" OR "narrative milestones" OR "Story Bible truth source") ("novel" OR "AI-assisted writing") in:name,description,readme',
    '("language style guide" OR "localized writing rules" OR "Vietnamese writing patterns") ("webnovel" OR "novel writing") in:name,description,readme',
    '("progressive disclosure" OR "intent-based command routing" OR "protocol files") ("novel" OR "Claude Skill" OR "long-form writing") in:name,description,readme',
    '("no-slop" OR "banned vocabulary" OR "AI writing patterns" OR "prose linter") ("writing" OR "prose" OR "novel") in:name,description,readme',
    '("project modifiers" OR "AI-driven initial planning" OR "chapter review") ("novel" OR "long-form writing" OR "creative dashboard") in:name,description,readme',
    '("canon governance" OR "portable skill runtime" OR "SQLite state") ("novel" OR "long-form fiction" OR "agent workflow") in:name,description,readme',
    '("sliding-window memory" OR "CJK-aware counter" OR "chapter range refinement") ("novel" OR "story generator" OR "continuity") in:name,description,readme',
    '("story bible wiki" OR "canon lint" OR "relationship graph") ("novel" OR "worldbuilding" OR "continuity") in:name,description,readme',
    '("Plan Draft Log Verify" OR "foreshadowing checklist" OR "living documents") ("longform" OR "novel" OR "manuscript") in:name,description,readme',
    '("metadata-first analysis" OR "safe scene revision" OR "git history") ("novel" OR "long-form fiction" OR "MCP") in:name,description,readme',
    '("Verbalized Sampling" OR "mode collapse" OR "writer wiki") ("creative writing" OR "story" OR "novel") in:name,description,readme',
    '("Dramatica" OR "causal chain" OR "foreshadowing tracking") ("AI novel" OR "novel-writing" OR "story generation") in:name,description,readme',
    '("Capture" OR "Distillation" OR "Production") ("agentic platform" OR "novel" OR "story foundry") in:name,description,readme',
    '("OpenClaw" OR "agent skill") ("Chinese novel" OR "novel-writing" OR "web novel") in:name,description,readme',
    '("LangGraph" OR "story state" OR "story-writing") ("fiction" OR "novel" OR "agent") in:name,description,readme',
    '("local-first" OR "privacy-first" OR "local RAG") ("novel" OR "web fiction" OR "creative writing") in:name,description,readme',
    '("story bible" OR "canon drift" OR "continuity checker") ("fiction" OR "novel" OR "long-form") in:name,description,readme',
    '("patch-NN" OR "outline.xml" OR "final.xml") ("AI novel" OR "drafting agent" OR "manuscript") in:name,description,readme',
    '("microkernel" OR "plugin architecture" OR "EventBus") ("AI novel" OR "web novel" OR "agentic novel") in:name,description,readme',
    '("style learning" OR "writing style Skill" OR "technique spectrum") ("novel" OR "webnovel" OR "fiction") in:name,description,readme',
    '("improvised writing" OR "open_threads" OR "single-chapter blueprint") ("novel" OR "web novel" OR "continuation") in:name,description,readme',
    '("inspiration bank" OR "style mimicry" OR "offline creative writing") ("novel" OR "long-form" OR "local RAG") in:name,description,readme',
    '("novel atelier" OR "beat planner" OR "hook auditor" OR "infinite-serial") ("Claude Code" OR "multi-agent novel") in:name,description,readme',
    '("book-mining" OR "novel-genesis" OR "canon-seed") ("novel-automation" OR "webnovel") in:name,description,readme',
    '("multi-book" OR "autopilot" OR "full-book logic check") ("novel studio" OR "webnovel") in:name,description,readme',
    '("CHAPTER_COMMIT" OR ".story-system" OR "read-model") ("webnovel" OR "longrun" OR "novel") in:name,description,readme',
    '("nine-agent pipeline" OR "Continuity Detective" OR "Foreshadowing Tracker") ("novel" OR "story" OR "fiction") in:name,description,readme',
    '("fresh context" OR "no memory fatigue" OR "next incomplete chapter" OR "progress.txt") ("fiction" OR "story bible" OR "chapter") in:name,description,readme',
    '("four reward channels" OR "reader-sim" OR "style-creator" OR "chronicler") ("creative writing" OR "novel") in:name,description,readme',
    '("tri-modal" OR "pre-writing checklist" OR "automated audit chain") ("novel" OR "story bible" OR "chapter") in:name,description,readme',
    '("chapter promise" OR "scene architect" OR "mob review" OR "character truth") ("fiction writing" OR "novel") in:name,description,readme',
    '("foreshadowing tracker" OR "LitRPG stats" OR "romance arc tracker") ("webnovel" OR "serial fiction") in:name,description,readme',
    '("simulation-first" OR "causal ledger" OR "belief state" OR "utterance history") ("novel generator" OR "long-form fiction") in:name,description,readme',
    '("writer-friendly git" OR "beta reader annotations" OR "word-by-word comparison") ("manuscript" OR "novel") in:name,description,readme',
    '("mode contract" OR "output mode" OR "visible creative axes" OR "style analyzer") ("story generator" OR "creative writing") in:name,description,readme',
    '("master study" OR "masterWorks" OR "chapter beats" OR "style metrics") ("novel" OR "writing workbench") in:name,description,readme',
    '("world model" OR "story rules" OR "style consistent") ("AI novel" OR "story writing") in:name,description,readme',
    '("AI-Fic-IDE" OR "Android native" OR "history snapshots" OR "AI memory") ("web novel" OR "AI writing") in:name,description,readme',
    '("human-machine co-creation" OR "inline edit" OR "precise modification" OR "AI polishing") ("AI novel" OR "web novel") in:name,description,readme',
    '("orchestrator" OR "hierarchical planning" OR "volume" OR "arc" OR "memory weave") ("AI novel" OR "long-form writing") in:name,description,readme',
    '("batch generation" OR "progress tracking" OR "auto continuation" OR "homogeneity") ("AI novel" OR "web novel") in:name,description,readme',
    '("本地数据" OR "自动升级" OR "批量生成" OR "进度追踪") ("AI小说" OR "网文") in:name,description,readme',
    '("prompt preset" OR "prompt variables" OR "提示词库" OR "预设管理") ("AI小说" OR "novel writing") in:name,description,readme',
    '("导入小说" OR "txt import" OR "chapter outline" OR "智能解析目录") ("AI小说" OR "web novel") in:name,description,readme',
    '("文笔DNA" OR "style DNA" OR "reference library" OR "风格模仿") ("AI novel" OR "小说") in:name,description,readme',
    '("draft vs confirmed" OR "rewrite candidates" OR "metadata-only index" OR "offline-first") ("novel" OR "writing workbench") in:name,description,readme',
    '("chapter descriptions" OR "previous chapters" OR "real-time streaming") ("book writing" OR "novel") in:name,description,readme',
    '("AI beta reader" OR "contextual feedback" OR "previous chapter summaries") ("novel" OR "manuscript") in:name,description,readme',
    '("citation styles" OR "AI research engine" OR "web search integration") ("research" OR "book writing" OR "manuscript") in:name,description,readme',
    '("style vocabulary" OR "vocabulary library") ("world cards" OR "worldbuilding extraction" OR "character cards") ("novel" OR "AI writing") in:name,description,readme',
    '("pure-prompt" OR "prompt-only") ("wrap-up mode" OR "continuity guard" OR "stress test") ("novel" OR "fiction") in:name,description,readme',
    '("delta extraction" OR "memory-augmented extraction") ("chain-of-verification" OR "deterministic accumulation") ("manuscript" OR "novel") in:name,description,readme',
    '("22-book" OR "22 published novels") ("style preset" OR "style presets" OR "smart rewriter") ("writing quality" OR "novel") in:name,description,readme',
    '("NarrativeQA" OR "reading comprehension challenge" OR "questions and answers") ("narrative" OR "story") in:name,description,readme',
    '("BookSum" OR "chapter-level" OR "book-level" OR "long-form narrative summarization") ("book" OR "novel") in:name,description,readme',
    '("FairytaleQA" OR "narrative comprehension" OR "question-answer pairs") ("story" OR "fairytale") in:name,description,readme',
    '("TellMeWhy" OR "why-questions" OR "helpful sentences") ("narratives" OR "story") in:name,description,readme',
    '("Story Commonsense" OR "naive psychology" OR "character motivations") ("story" OR "narrative") in:name,description,readme',
    '("SQuALITY" OR "question-focused" OR "multi-reference summarization") ("long-document" OR "story") in:name,description,readme',
    '("AI is off by default" OR "workspace level" OR "line-level diff") ("novel" OR "fiction") in:name,description,readme',
    '("canon-aware" OR "chapter contracts" OR "drafts/reviews/research") ("novel" OR "long-form fiction") in:name,description,readme',
    '("state-sync memory" OR "golden-three-chapters" OR "anti-AI-pattern") ("web novel" OR "long-form fiction") in:name,description,readme',
    '("AI-agent handbook" OR "integrated drafting beta review revision") ("Chinese webnovel" OR "webnovel") in:name,description,readme',
    '("PSYKE Story Bible" OR "Narrative Engine" OR "Story Grid") ("creative writing" OR "novel") in:name,description,readme',
    '("Story Engine v2" OR "1000-chapter" OR "prompt cache") ("webnovel" OR "story factory") in:name,description,readme',
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
    "https://github.com/vkbo/novelWriter",
    "https://github.com/olivierkes/manuskript",
    "https://github.com/andreafeccomandi/bibisco",
    "https://github.com/wavemakercards/wavemaker-cards-v4",
    "https://github.com/Narcooo/inkos",
    "https://github.com/MaoXiaoYuZ/Long-Novel-GPT",
    "https://github.com/dylanhogg/gptauthor",
    "https://github.com/kevboh/longform",
    "https://github.com/principia-ai/WriteHERE",
    "https://github.com/iLearn-Lab/NovelClaw",
    "https://github.com/howells/fiction",
    "https://github.com/mjbae/awesome-novel-studio",
    "https://github.com/danjdewhurst/story-skills",
    "https://github.com/hestudy/snowflake-fiction",
    "https://github.com/forsonny/The-Crucible-Writing-System-For-Claude",
    "https://github.com/XuanRanL/webnovel-writer",
    "https://github.com/forsonny/book-os",
    "https://github.com/forjd/better-writing",
    "https://github.com/EdwardAThomson/NovelWriter",
    "https://github.com/StableLlamaAI/AugmentedQuill",
    "https://github.com/AutoFiction-AI/AutoFiction",
    "https://github.com/YILING0013/AI_NovelGenerator",
    "https://github.com/Picrew/ConStory-Bench",
    "https://github.com/harshaneel/humanize",
    "https://github.com/Picrew/awesome-llm-story-generation",
    "https://github.com/Anning01/novelvids",
    "https://github.com/MemeCalculate/moyin-creator",
    "https://github.com/jncchds/abook",
    "https://github.com/Prompt-And-Circumstance/StoryMode",
    "https://github.com/brianlmerritt/explore_writing",
    "https://github.com/forsonny/novel-master-ai",
    "https://github.com/arian-emami/NovelDreamer",
    "https://github.com/lingfengQAQ/webnovel-writer",
    "https://github.com/zy-zmc/tianming-novel-ai-writer",
    "https://github.com/lujih/webnovel-writer-opencode",
    "https://github.com/starMagic/webnovel-writer-hermes",
    "https://github.com/HZ-KMNO/web-novel-writing-guidance-skill",
    "https://github.com/jinmawang/claude-novel-writeFlow",
    "https://github.com/DuckTraDo/Novel",
    "https://github.com/makieali/longform-ai",
    "https://github.com/guchendesigndog/GC-Writer-Assistant",
    "https://github.com/lars76/story-evaluation-llm",
    "https://github.com/lechmazur/writing",
    "https://github.com/lechmazur/writing_styles",
    "https://github.com/anirudhlakkaraju/cs4_benchmark",
    "https://github.com/Theltn/AICreativityJudge",
    "https://github.com/clchinkc/story-bench",
    "https://github.com/THU-KEG/StoryWriter",
    "https://github.com/ZJU-LLMs/OpenStory",
    "https://github.com/zygmuntz/goodbooks-10k",
    "https://github.com/MengtingWan/goodreads",
    "https://github.com/maria-antoniak/goodreads-scraper",
    "https://github.com/Ckokoski/authorclaw",
    "https://github.com/f5alcon/The-Novelists-Atelier",
    "https://github.com/arupmaity1/book-writer-mcp",
    "https://github.com/inkle/ink",
    "https://github.com/YarnSpinnerTool/YarnSpinner",
    "https://github.com/klembot/twinejs",
    "https://github.com/dfabulich/choicescript",
    "https://github.com/blingenf/copydetect",
    "https://github.com/ropensci/textreuse",
    "https://github.com/rapidfuzz/RapidFuzz",
    "https://github.com/google/diff-match-patch",
    "https://github.com/agranya99/MOSS-winnowing-seqMatcher",
    "https://github.com/ChenghaoMou/text-dedup",
    "https://github.com/google-research/deduplicate-text-datasets",
    "https://github.com/ekzhu/datasketch",
    "https://github.com/seomoz/simhash-py",
    "https://github.com/1e0ng/simhash",
    "https://github.com/MinishLab/semhash",
    "https://github.com/UKPLab/sentence-transformers",
    "https://github.com/facebookresearch/faiss",
    "https://github.com/facebookresearch/SemDeDup",
    "https://github.com/booknlp/booknlp",
    "https://github.com/textstat/textstat",
    "https://github.com/vale-cli/vale",
    "https://github.com/textlint/textlint",
    "https://github.com/amperser/proselint",
    "https://github.com/Automattic/harper",
    "https://github.com/languagetool-org/languagetool",
    "https://github.com/btford/write-good",
    "https://github.com/fxsjy/jieba",
    "https://github.com/messense/jieba-rs",
    "https://github.com/hankcs/HanLP",
    "https://github.com/HIT-SCIR/ltp",
    "https://github.com/BYVoid/OpenCC",
    "https://github.com/shibing624/pycorrector",
    "https://github.com/aerkalov/ebooklib",
    "https://github.com/pdfminer/pdfminer.six",
    "https://github.com/pymupdf/PyMuPDF",
    "https://github.com/ocrmypdf/OCRmyPDF",
    "https://github.com/tesseract-ocr/tesseract",
    "https://github.com/Unstructured-IO/unstructured",
    "https://github.com/microsoft/markitdown",
    "https://github.com/docling-project/docling",
    "https://github.com/opendatalab/MinerU",
    "https://github.com/datalab-to/marker",
    "https://github.com/jgm/pandoc",
    "https://github.com/google-deepmind/narrativeqa",
    "https://github.com/salesforce/booksum",
    "https://github.com/uci-soe/FairytaleQAData",
    "https://github.com/StonyBrookNLP/tellmewhy",
    "https://github.com/uwnlp/storycommonsense",
    "https://github.com/nyu-mll/SQuALITY",
    "https://github.com/lancopku/Chinese-Literature-NER-RE-Dataset",
    "https://github.com/dbamman/litbank",
    "https://github.com/eecrazy/ConstructingNEEG_IJCAI_2018",
    "https://github.com/acolas1/EventNarrative",
    "https://github.com/doug919/narrative_graph_emnlp2020",
    "https://github.com/mjockers/syuzhet",
    "https://github.com/jon-chun/sentimentarcs_notebooks",
    "https://github.com/SapienzaNLP/xcore",
    "https://github.com/anastasia-zhukova/XCoref",
    "https://github.com/hzjken/character-network",
    "https://github.com/devbret/character-interactions",
    "https://github.com/computationalstylistics/stylo",
    "https://github.com/fastdatascience/faststylometry",
    "https://github.com/cophi-wue/pydelta",
    "https://github.com/Hassaan-Elahi/Writing-Styles-Classification-Using-Stylometric-Analysis",
    "https://github.com/michaeleby1/stylometric-analysis-project-gutenberg",
    "https://github.com/pan-webis-de/pan-code",
    "https://github.com/mullerpeter/authorstyle",
    "https://github.com/ivannikov-lab/style-change-analysis",
    "https://github.com/sam0jones0/pyantistylometry",
    "https://github.com/ngpepin/stylometric-transfer",
    "https://github.com/ContextLab/llm-stylometry",
    "https://github.com/llm-authorship/survey",
    "https://github.com/LSYS/LexicalRichness",
    "https://github.com/HLasse/TextDescriptives",
    "https://github.com/boudinfl/pke",
    "https://github.com/benbrandt/text-splitter",
    "https://github.com/langchain-ai/langchain",
    "https://github.com/miso-belica/sumy",
    "https://github.com/dmmiller612/bert-extractive-summarizer",
    "https://github.com/MaartenGr/BERTopic",
    "https://github.com/explodinggradients/ragas",
    "https://github.com/confident-ai/deepeval",
    "https://github.com/truera/trulens",
    "https://github.com/Arize-ai/phoenix",
    "https://github.com/promptfoo/promptfoo",
    "https://github.com/openai/evals",
    "https://github.com/THUDM/LongWriter",
    "https://github.com/THUDM/LongReward",
    "https://github.com/THU-KEG/LongWriter-V",
    "https://github.com/X-PLUG/WritingBench",
    "https://github.com/EQ-bench/creative-writing-bench",
    "https://github.com/EQ-bench/longform-writing-bench",
    "https://github.com/dig-team/hanna-benchmark-asg",
    "https://github.com/google-deepmind/dramatron",
    "https://github.com/yangkevin2/emnlp22-re3-story-generation",
    "https://github.com/LC1332/Chat-Haruhi-Suzumiya",
    "https://github.com/rajammanabrolu/StoryRealization",
    "https://github.com/gratajik/book-memory-bank",
    "https://github.com/adaumann/speckit-preset-fiction-book-writing",
    "https://github.com/danngalann/llm-ebook-summarizer",
    "https://github.com/darkautism/ai-novel-translation",
    "https://github.com/lordjabez/story-framework",
    "https://github.com/getzep/graphiti",
    "https://github.com/mem0ai/mem0",
    "https://github.com/microsoft/graphrag",
    "https://github.com/HKUDS/LightRAG",
    "https://github.com/neo4j-labs/llm-graph-builder",
    "https://github.com/IDSIA/novel2graph",
    "https://github.com/Drwei3155/story-graph",
    "https://github.com/MitchSaltykov/TVTropes-correlation",
    "https://github.com/jwzimmer-zz/tv-tropes",
    "https://github.com/slowwavesleep/TvTropesMovieData",
    "https://github.com/rhgarcia/tropescraper",
    "https://github.com/Sirver51/tvtropes-parser",
    "https://github.com/licensee/licensee",
    "https://github.com/fsfe/reuse-tool",
    "https://github.com/spdx/license-list-data",
    "https://github.com/c-w/Gutenberg",
    "https://github.com/Imkun-on/gutenberg-corpus-cli",
    "https://github.com/microsoft/presidio",
    "https://github.com/LeapBeyond/scrubadub",
    "https://github.com/urchade/GLiNER",
    "https://github.com/flairNLP/flair",
    "https://github.com/explosion/spaCy",
    "https://github.com/w3c/epubcheck",
    "https://github.com/daisy/ace",
    "https://github.com/standardebooks/tools",
    "https://github.com/Sigil-Ebook/Sigil",
    "https://github.com/w3c/epub-tests",
    "https://github.com/daisy/epub-accessibility-tests",
    "https://github.com/john-paul-ruf/novel-engine",
    "https://github.com/ThomasHoussin/Claude-Book",
    "https://github.com/DoktorDaveJoos/Manuscript",
    "https://github.com/geobond13/fiction-forge",
    "https://github.com/shenminglinyi/PlotPilot",
    "https://github.com/peter88213/novelibre",
    "https://github.com/WENZIZZHENG/story-spec",
    "https://github.com/KKKenChow/ai-novel-writer",
    "https://github.com/papysans/Morpheus",
    "https://github.com/jingtai123/Novel-Control-Station-Skill",
    "https://github.com/xindoo/sumeru",
    "https://github.com/AI-Practical-Lab/ai-novel",
    "https://github.com/XZZKANY/StoryForge",
    "https://github.com/spiritLHLS/novelbuilder",
    "https://github.com/qiuxinyuan321/novel-writer-master",
    "https://github.com/Byk3y/no-slop",
    "https://github.com/nntrivi2001/wordsmith",
    "https://github.com/zy-zmc/tianming-skill",
    "https://github.com/para-droid-ai/NovelizeAI",
    "https://github.com/Moosphan/novel-orchestrator",
    "https://github.com/kirinonakar/Novelgen",
    "https://github.com/abrahamp47/storyforge-wiki",
    "https://github.com/third-order-labs/longform-plugin",
    "https://github.com/hannasdev/mcp-writing",
    "https://github.com/xbraindance/Creative-writing-skill",
    "https://github.com/tiny-flowlab/novel-studio-copilot-cli",
    "https://github.com/guerra2fernando/libriscribe",
    "https://github.com/muckelverk/pulpgen",
    "https://github.com/bhed/sentiers-open-source",
    "https://github.com/rhavekost/author-toolkit",
    "https://github.com/mike-cramblett/novel-novel-generator",
    "https://github.com/denmurray10/Story-Timeline-Builder",
    "https://github.com/jwynia/agent-skills",
    "https://github.com/ydsgangge-ux/dramatica-flow",
    "https://github.com/mmunro3318/story-foundry",
    "https://github.com/Shine8592/novel-writer-skills",
    "https://github.com/modoojunko/awesome-novel-skill",
    "https://github.com/langchain-ai/story-writing",
    "https://github.com/EdwardAThomson/StoryDaemon",
    "https://github.com/datacrystals/AIStoryWriter",
    "https://github.com/sadasdfsaf/canonkit",
    "https://github.com/heider-x/vela",
    "https://github.com/pulpgen-dev/pulpgen",
    "https://github.com/jim60105/HeartReverie",
    "https://github.com/wzxsph/Novel-Claude",
    "https://github.com/liaoma1993/aiAIfiction",
    "https://github.com/vishnu0120754/ReNovel-AI",
    "https://github.com/worldwonderer/zenstory",
    "https://github.com/tuxiangxianzhe/NovelWriter_public",
    "https://github.com/MA-Bihani/Novelia_public",
    "https://github.com/huodebing-alt/Claude-Code-Novel-Agents",
    "https://github.com/cchheerrss/ai-novel-trilogy",
    "https://github.com/zhitongblog/novel-studio",
    "https://github.com/DinhLucent/webnovel-longrun-aigen-docs",
    "https://github.com/dorakingx/novelpilot",
    "https://github.com/heaversm/ralph-storywriter",
    "https://github.com/haowjy/creative-writing-skills",
    "https://github.com/jblemee/bmad-book-builder",
    "https://github.com/Deland78/Claude-Writing-Skills",
    "https://github.com/netflypsb/webnovel-mcp",
    "https://github.com/hackertaco/novel-generator",
    "https://github.com/eristoddle/git-write",
    "https://github.com/fopearcano/storyplanner",
    "https://github.com/giapnguyen74/xnovelist",
    "https://github.com/waylean/plotrail",
    "https://github.com/XINGANLIU/web-novel-writing-skill",
    "https://github.com/miserylee/webnovel-handbook",
    "https://github.com/ungden/truyencity2",
    "https://github.com/FURUYAN1234/story-maker",
    "https://github.com/yuanbw2025/storyforge",
    "https://github.com/dedyrio/novelwriter",
    "https://github.com/qq1375828505/AI-Fic-IDE",
    "https://github.com/leehong0704/ai-novel",
    "https://github.com/wynnforthework/ai-novel-weaver",
    "https://github.com/fuchen2020/BatchScribe",
    "https://github.com/xy9144/flutter-novel-main",
    "https://github.com/duoyang666/ai_novel",
    "https://github.com/Deng-m1/MaliangAINovalWriter",
    "https://github.com/ponysb/91Writing",
    "https://github.com/hezhengtao/MortalAINovel-AIWritingSystem-ai-",
    "https://github.com/linnnn89/novel-agent-workbench",
    "https://github.com/qnbs/StoryCraft-Studio",
    "https://github.com/dlintin/sidekickwriter",
    "https://github.com/gennitdev/ai-beta-reader-frontend",
    "https://github.com/gennitdev/ai-beta-reader-backend",
    "https://github.com/wesleyscholl/book-generator",
    "https://github.com/Boundless-Fang/StyleSync-Novel",
    "https://github.com/eluckydog/DreamQuill",
    "https://github.com/304769384-png/fanqie-novel-skill",
    "https://github.com/leistung/novel-write",
    "https://github.com/VerifiedOrganic/spindle",
    "https://github.com/daveremy/edword",
    "https://github.com/adameya2004-oss/CraftEngine",
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
    "interactive narrative",
    "interactive fiction",
    "branching story",
    "nonlinear story",
    "dialogue",
    "choice",
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
    ("chapter_generation", ("chapter generation", "chapter-writing", "chapter writer", "chapter writing", "multi-chapter stories", "iterative chapter writing", "autonomous novel pipeline", "novel pipeline", "seed concept to print-ready", "章节生成", "生成章节", "章节创作", "小说生成", "创作平台", "写作平台")),
    ("continuation", ("continuation", "continue", "续写", "断更续写", "继续写")),
    ("same_type_creation", ("同类型", "same type creation", "same-type creation", "inspired", "remix", "二创", "同人", "同类创作", "风格复刻")),
    ("worldbuilding", ("worldbuilding", "世界观", "设定", "world rules")),
    ("timeline", ("timeline", "时间线", "chronology")),
    ("character_cards", ("character", "人物", "角色", "人物卡")),
    ("organization_graph", ("organization", "faction", "组织", "势力")),
    ("emotion_arc", ("emotion", "情感", "relationship", "关系")),
    ("style_signature", ("style", "voice", "风格", "文风", "味道")),
    ("self_review", ("review", "critique", "评审", "自评", "自我评审", "优化", "rewrite")),
    ("card_workbench", ("card", "cards", "card-based", "card workbench", "卡片", "卡片式", "卡片创作")),
    ("structured_generation_schema", ("schema", "json schema", "schema-first", "structured generation", "结构化", "结构化生成", "动态输出模型", "输出模型")),
    ("context_reference", ("context injection", "context reference", "context-aware", "@dsl", "knowledge graph", "vector retrieval", "vector storage", "retrieved automatically", "retrieval", "retrieve relevant", "rag", "injection viewer", "上下文注入", "上下文引用", "知识图谱", "引用")),
    ("workflow_agent_pipeline", ("workflow agent", "workflow studio", "workflow system", "persistent workflow", "progress recovery", "multi-agent", "editorial pipeline", "agent handoff", "工作流", "工作流系统", "中断恢复", "触发器")),
    ("scene_asset_pipeline", ("idea to production", "filmmaking", "film production", "screenplay", "storyboard", "shot", "shot list", "scene asset", "scene plan", "镜头", "分镜", "场景资产")),
    ("quality_score_loop", ("modify-evaluate-keep", "keep/discard", "foundation_score", "quality score", "chapter quality", "score >", "plateau detection", "reader panel", "llm judge", "dual-persona review", "质量评分", "读者面板", "平台期检测")),
    ("voice_fingerprint", ("voice fingerprint", "voice analysis", "voice discovery", "voice.md", "声纹", "文风指纹", "语气指纹", "声音发现")),
    ("anti_slop_audit", ("anti-slop", "anti-pattern", "slop scorer", "ai tell", "mechanical slop", "anti-pattern rules", "反 AI", "反套路", "AI 味", "机械感")),
    ("publication_pipeline", ("print-ready", "epub", "audiobook", "landing page", "typeset", "latex", "export", "publish", "publication", "有声书", "排版", "出版", "交付流水线")),
    ("lorebook_context", ("world info", "worldinfo", "lorebook", "memory book", "keyword activation", "recursive scan", "scan depth", "insertion order", "context budget", "世界信息", "设定集", "关键词激活", "递归扫描")),
    ("author_note_layer", ("author's note", "authors note", "author note", "insertion frequency", "in-chat", "chat memory", "作者注释", "作者备注", "提示词层")),
    ("world_state_tracking", ("solo tabletop game master", "players, locations, regions, and items", "world state", "story state", "story world", "world model", "story rules", "clear world model", "characters relationships", "persistent state", "central state", "state parser", "event memory", "event memories", "fact memory", "fact memories", "emotional memory", "emotional memories", "relationship memory", "relationship memories", "scene log", "review logs", "structured prompts", "世界状态", "实体状态", "场景日志")),
    ("memory_snapshot_versioning", ("git for ai agent memory", "snapshot", "branch", "merge", "rollback", "memory versioning", "memory branch", "compaction", "consolidation", "memory rollup", "memory rollups", "multi-tier memory", "记忆快照", "记忆分支", "回滚")),
    ("local_first_novel_workspace", ("local-first", "local first", "privacy-first", "offline access", "indexeddb", "multi-novel", "active novel", "workspace", "local data persistence", "novel workspace", "own every word", "no subscription", "your prose stays on your device", "local model", "本地优先", "离线访问", "多小说工作区")),
    ("prompt_library", ("prompt manager", "prompt library", "task-specific prompt", "task prompts", "system prompt", "reset prompts", "prompt template", "prompttemplates", "prompt workflows", "visible, editable, and savable", "visible editable savable", "system/user/parameters", "saveTarget", "提示词库", "提示词管理", "任务提示词")),
    ("scene_level_generation", ("scene-level generation", "scene level generation", "scene-by-scene", "scene drafts", "plan scenes", "draft scene", "scene text writing", "generate prose for each scene", "场景级生成", "逐场景生成")),
    ("review_queue_staging", ("review queue", "pendingchange", "pending change", "staging area", "diff view", "line-level diff", "automatic snapshots", "draft awaiting your review", "accept edit reject", "accept all", "staged not applied", "审查队列", "暂存区", "待审核变更")),
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
    ("setup_payoff_tracking", ("setup/payoff", "setup payoff", "foreshadowing tracking", "foreshadowing tracker", "planned payoffs", "payoff", "setup chapter", "expected payoff", "伏笔回收", "埋设回收")),
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
    ("plain_text_project_storage", ("plain text", "human readable text files", "many smaller text documents", "version control", "file synchronisation", "minimal formatting syntax", "robustness", "纯文本", "可读文本", "版本控制")),
    ("synopsis_cross_reference", ("synopsis", "comments", "cross-referencing", "cross reference", "metadata syntax", "notes", "comment", "摘要", "交叉引用")),
    ("snowflake_premise_expansion", ("snowflake method", "snowflake", "one sentence", "to a paragraph", "full summary", "step-by-step story development", "premise expansion", "premise from one sentence", "雪花法", "一句话", "完整梗概")),
    ("outliner_index_cards", ("outliner", "outline mode", "index cards", "grid planner", "plot point management", "plot points", "reorderable nestable scenes", "reorderable, nestable list", "reorderable scenes", "nestable scenes", "re-organize chapters and scenes", "edit and re-organize", "chapter and scene management", "大纲模式", "索引卡", "章节重排")),
    ("narrative_strand_mapping", ("narrative strands", "narrative engine", "story grid", "multi-plot", "act/beat analysis", "fabula", "premise", "settings: geographic, temporal and social context", "geographic, temporal and social context", "story line", "叙事线", "故事线", "社会背景")),
    ("character_depth_interview", ("know everything about your characters", "believable characters", "human nature", "character complexity", "character interview", "人物访谈", "人物深描", "可信人物")),
    ("mindmap_visual_planning", ("mind mapping", "mind map", "interactive visual story planning", "visual story planning", "drag-and-drop node", "visual links", "visualization tools", "脑图", "思维导图")),
    ("manuscript_export_formats", ("export novel in pdf, docx, or txt", "export formats", "import/export formats", "import and export", "import and export document formats", "document formats", "html, epub, opendocument, docx", "pdf, docx, txt", "markdown export", "markdown and html export", "html export", "json exports", "导出", "文档格式")),
    ("human_synopsis_gate", ("human review of synopsis", "review the synopsis", "generate another before proceeding", "chapter summaries", "synopsis gate", "人工审阅梗概", "章节摘要审核")),
    ("retrieval_guided_span_rewrite", ("retrieve relevant body snippets", "retrieve relevant text snippets", "related text snippets", "related body snippets", "related plot outline", "modify text snippets", "sync update outline", "同步更新剧情纲要", "相关正文片段", "检索相关正文片段", "修改正文片段")),
    ("runtime_artifact_trace", ("intent.md", "context.json", "rule-stack.yaml", "trace.json", "runtime artifacts", "actual selected context", "rule stack", "inspectable run", "可检查运行", "追踪文件")),
    ("schema_validated_state_delta", ("zod schema", "json delta", "state delta", "validate runtime state", "validateruntimestate", "immutable update", "structure validation", "bad data rejected", "状态增量", "结构校验")),
    ("recursive_adaptive_planning", ("recursive planning", "recursive task decomposition", "heterogeneous integration", "dynamic adaptation", "adaptive planning", "retrieval, reasoning, and composition", "递归规划", "动态规划", "自适应规划")),
    ("workflow_manuscript_compilation", ("workflow-based compilation", "compile manuscripts", "compilation tool", "ordered manuscript", "ordered series of scenes", "manuscript compilation", "编译手稿", "场景编译")),
    ("writing_session_goal_tracking", ("writing session goals", "daily writing session goals", "word counts", "scene/draft/project word counts", "writing goals", "字数目标", "写作目标")),
    ("inspectable_run_workspace", ("inspectable writing workspace", "inspectable runs", "sessions, storyboards, manuscript surfaces", "editable memory banks", "storyboards", "manuscript surfaces", "memory-aware writing control", "可检查工作区", "运行会话")),
    ("craft_role_pipeline", ("specialized agents", "architecture, characters, prose, review, editing, continuity", "agent roles", "review agents", "multi-agent orchestration", "tool selection", "craft-aware feedback", "production system", "specialist agents", "nine-agent pipeline", "premise architect", "character director", "world builder", "plot strategist", "chapter architect", "prose writer", "style editor", "publisher agent")),
    ("frontmatter_story_schema", ("yaml frontmatter", "frontmatter", "shared project format", "story bible", "character files", "scene state", "continuity questions", "plain markdown with yaml")),
    ("continuity_bridge_window", ("continuity bridge", "previous 2 episodes", "previous two episodes", "collects timeline", "feeds it to the creation agent", "progress.md", "continuity state")),
    ("episode_range_rewrite_scope", ("episode range", "ep001-ep010", "range arguments", "impact scope", "rewrite episodes", "auto-calculates impact scope", "after design changes")),
    ("voice_table_polish_axis", ("voice table", "speech patterns", "sentence endings", "non-verbal palette", "voice consistency", "voice checker", "voice axis", "polish axes")),
    ("boring_opening_quality_gates", ("boring detect", "boring-detect", "running-log", "opening check", "opening-check", "golden three chapters", "golden-three-chapters", "quality check", "hook", "reader experience")),
    ("beat_strand_framework", ("36-beat", "36 beat", "three interwoven strands", "quest", "fire", "constellation", "forge points", "apex", "mercy engine", "narrative framework")),
    ("anti_hallucination_plan_check", ("anti-hallucination", "strict verification against planning documents", "verification against planning documents", "hallucination", "forgetting", "reduce forgetting", "memory and hallucination guard")),
    ("backup_restore_checkpoint", ("automatic backups", "restore from backup", "crucible-restore", "git backup", "backup", "restore", "never lose your work")),
    ("multi_level_review_trend", ("multi-level review", "scene, chapter, and batch-level", "batch-level quality", "trend tracking", "quality analysis", "7 layers", "70 checks", "audit gate")),
    ("editor_notes_feedback_loop", ("editor_notes", "editor notes", "cross-chapter feedback", "feedback loop", "cross-chapter closure", "review notes", "revision pass")),
    ("genre_parameterized_worldbuilding", ("genre-specific", "genre guides", "genre conventions", "dynamic faction", "location systems", "faction generation", "any genre", "subgenre", "genre-specific world-building")),
    ("prose_preflight_voice_calibration", ("voice calibration", "writing sample", "generic ai tells", "final pre-flight", "pre-flight check", "specificity does not turn into invention", "clear, specific, and human")),
    ("sourcebook_author_workbench", ("sourcebook", "source book", "sourcebook entries", "writing partner", "author in the driver seat", "story structure + chatbot", "project-based story authoring", "multi-book structure")),
    ("semantic_long_context_search", ("semantic search engine", "semantic search", "vector-based long-term context", "vectorstore", "local vector db", "long-term context consistency", "knowledge base integration", "local document references")),
    ("contradiction_taxonomy_checker", ("narrative consistency", "consistency bugs", "contradiction detection", "consistency errors", "characterization", "factual detail", "timeline & plot", "world-building & setting", "causality violations", "abandoned plots", "plot contradictions", "logical conflicts")),
    ("parallel_agent_chapter_pipeline", ("parallel chapter drafting", "premise -> outline -> parallel chapter drafting", "frontier ai coding agent", "agentic jobs", "full-book review", "cross-chapter audit", "aggregate findings", "review-and-revision cycles")),
    ("cross_chapter_redundancy_audit", ("cross-chapter redundancy", "repetitive scene construction", "weak causality", "continuity drift", "flat dialogue", "over-regular prose", "grep to count prose patterns")),
    ("humanization_stylometry_levers", ("perplexity", "burstiness", "stylometry", "discourse", "watermarking", "nine humanization levers", "specificity insertion", "ai-transition removal", "rlhf voice strip")),
    ("author_control_boundary", ("author in the driver seat", "creative partner", "supports your voice and choices", "your story is your story", "human readers respond", "clearly labeled as ai-generated", "ethics.md")),
    ("research_taxonomy_story_map", ("story generation taxonomy", "llm story generation", "curated list of story/novel/script generation research", "planning / decomposition", "agent collaboration", "sandbox / world simulation", "multimodal story generation", "evaluation / benchmark", "method categories")),
    ("novel_to_multimodal_pipeline", ("novel to short drama", "novel-to-short-drama", "novel to video", "script to scene", "script to film", "storyboard", "video synthesis", "film production tool", "剧本到成片", "小说转短剧")),
    ("entity_to_visual_asset_pipeline", ("entity extraction", "character reference", "reference image", "reference images", "visual asset", "scene asset", "storyboard asset", "角色参考图", "实体提取")),
    ("agentic_book_planner_pipeline", ("story bible", "plot threads", "chapter outlines", "writer", "editor", "continuity checker", "7 agents", "agentic book planner", "book creation assistant", "worldbuilding, book structure, chapters")),
    ("rag_synopsis_spine", ("rag context retrieval", "full synopsis spine", "synopsis spine", "chapter summaries", "retrieved context", "local embeddings", "book structure", "context retrieval")),
    ("anti_repetition_prompt_rules", ("anti-repetition", "anti repetition", "avoid repetition", "repetition rules", "anti-repetition rules", "repeated phrases", "repeated scene", "token stats")),
    ("prompt_recipe_experiment_grid", ("prompt recipes", "prompt recipe", "sampling grid", "temperature grid", "experiment harness", "write/review/top_writing", "top_writing")),
    ("append_only_generation_review_log", ("append-only", "append only", "resumable tsv", "append-only/resumable", "review log", "generation log", "experiment log")),
    ("narrative_arc_template_control", ("narrative arc", "scenario blueprint", "43 genres", "story style", "author style", "mix-and-match", "genre list", "arc template")),
    ("nrd_task_tree_pipeline", ("nrd", "arcs/chapters/scenes", "revision passes", "tagged workflow", "continuity reporting", "task tree", "novel master")),
    ("sampling_parameter_quality_sweep", ("sampling grid", "temperature", "top_p", "top-k", "sampling parameter", "quality sweep", "parameter sweep")),
    ("story_structure_rag_planning", ("wikiquote", "hero's journey", "freytag", "story structure rag", "style/thematic samples", "acts/chapters pre-planning", "thematic samples")),
    ("story_contract_commit_chain", ("story contract", "story contracts", "chapter contract", "chapter contracts", "chapter_commit", "chapter commit", "approved chapter contract", "合同", "提交链", "故事合同", "唯一的事实源头", "主链", "accepted chapter_commit")),
    ("fact_snapshot_delta_gate", ("fact snapshot", "事实快照", "15维事实快照", "12类变更声明", "state write-back", "fact write-back", "状态回写", "事实回写", "变更声明", "generation gates", "生成门禁", "统一校验")),
    ("projection_sync_observability", ("projection_log", "projection log", "state/index/summary/memory/vector", "投影", "派生视图", "只读视图", "dashboard", "doctor", "preflight", "项目体检", "可视化面板")),
    ("foreshadowing_debt_budget", ("foreshadowing debt", "foreshadowing tracking", "伏笔债务", "debttracker", "token 预留", "budget allocation", "上下文预算", "未回收伏笔", "伏笔追踪")),
    ("reader_retention_review_gate", ("reader retention", "follow-up rate", "追读力", "爽点", "ooc", "节奏", "6 维", "six-dimensional", "reader promise", "读者承诺")),
    ("draft_stage_revision_ladder", ("draft a", "draft b", "draft c", "chapter blueprint", "key-information file", "chapter task card", "初稿", "定向修改", "去ai", "连续性记录", "drafting, revision, and final polish")),
    ("rolling_summary_context_trim", ("rolling summary", "compressed plot summary", "context trimmed", "token budget", "character state tracking", "timeline events", "relevant passages", "session progress", "context trimming", "chapter_summaries", "chapter summaries", "events.jsonl", "timeline.jsonl", "relationship graph", "memory update after each chapter")),
    ("multidimensional_quality_rubric", ("q1-q15", "q1 to q15", "q1", "q15", "15 quality metrics", "overall score", "ranked weaknesses", "character consistency", "reader interest", "plot resolution", "quality metrics", "quality evaluations")),
    ("pairwise_story_comparison_ranking", ("head-to-head story", "head to head story", "pairwise judgments", "paired story judgments", "visible story order", "story order swaps", "pairwise margins", "evaluator agreement", "matched creative briefs", "direct story comparisons")),
    ("style_axis_diversity_fingerprint", ("style fingerprints", "style fingerprint", "within-model diversity", "diversity per model", "style axes", "voice and diction", "rhythm and syntax", "pov and discourse", "structure and pacing", "closure axes")),
    ("constraint_specificity_creativity_benchmark", ("constraint specificity", "constraint satisfaction", "cs4", "prompts of varying specificity", "specific prompts", "creativity benchmark", "coherence and perplexity", "synthesized constraint specificity")),
    ("story_theory_beat_evaluation", ("story theory", "hero's journey", "save the cat", "beat interpolation", "beat revision", "multi-beat synthesis", "theory conversion", "constrained continuation", "beat execution", "narrative criteria")),
    ("event_outline_history_compression", ("outline agent", "planning agent", "writing agent", "event-based outlines", "chapter-wise plans", "dynamically compresses the story history", "story history", "current event", "inter-event relationships")),
    ("agentic_story_world_simulation", ("story-world simulation", "story world simulation", "multi-agent inference", "multi-agent simulation", "dynamic agents", "dynamically adding and removing agents", "character behavior", "social interaction", "story evolution")),
    ("reader_rating_signal_model", ("goodbooks", "goodreads", "six million ratings", "ratings.csv", "to_read.csv", "average rating", "rating distribution", "tags/shelves/genres", "book recommendation", "recommender system", "reader preference", "reader ratings", "book shelves", "to-read intent")),
    ("review_spoiler_sentiment_corpus", ("book reviews", "reader reviews", "review corpus", "fine-grained spoiler detection", "spoiler detection", "sentiment timeline", "review datasets", "amateur criticism", "reviews analyzed", "review corpus", "spoiler-aware feedback", "sentiment drift")),
    ("beta_reader_archetype_panel", ("beta reader", "simulated reader", "reader perspectives", "genre fan", "casual reader", "critical reader", "sensitivity reader", "wanttocontinue", "want to continue", "stumble point", "favorite moment", "confusion flags", "ai beta readers", "beta reader panel", "reader trial feedback")),
    ("comp_title_market_positioning", ("comp title", "comparable titles", "market positioning", "genre trends", "reader expectations", "bestseller patterns", "trope requested", "common complaints", "if you liked", "blurb", "amazon description", "keywords", "comp title", "market position", "reader expectation")),
    ("local_reader_experience_editor", ("micro-tension", "reader curiosity tracker", "chapter hook", "cliffhanger audit", "tension & engagement", "scene openings", "scene endings", "white space", "paragraph rhythm", "style dna", "token breakdown", "smart context auto-toggling", "reader experience", "reader curiosity", "chapter hook")),
    ("delivery_manuscript_assembly", ("assembled from many smaller text", "compile manuscript", "compiles your manuscript", "manuscript-wide statistics", "book_chapter_list", "chapter order", "chapter reorder", "chapter header", "chapter headings", "final manuscript", "accepted chapters", "manuscript assembly", "manuscript surface", "ordered manuscript")),
    ("export_format_fidelity_audit", ("markdown/docx export", "markdown export", "docx export", "pdf, docx, or txt", "export novel in pdf", "formatted .docx", "title page", "page numbers", "configurable fonts", "export format", "clean markdown", "derived manuscript artifacts")),
    ("preview_toc_packaging", ("html preview", "built-in html preview", "preview server", "table of contents", "toc", "book typography", "auto-refreshes", "drop caps", "ornamental dividers")),
    ("cover_kdp_metadata_boundary", ("kdp", "cover specs", "kdp-compliant", "cover design", "cover metadata", "cover prompt", "color palettes", "typography", "book launch copy")),
    ("branching_choice_graph", ("interactive narrative", "branching story", "highly branching stories", "choice graph", "choices", "knots", "stitches", "diverts", "weave structure", "nonlinear stories", "multiple-choice games", "choice-driven", "branch edges")),
    ("node_dialogue_state_machine", ("dialogue system", "interactive conversations", "dialogue tool", "lines", "options", "commands", "dialogue scripts", "nodes", "node-based", "entry state", "exit deltas")),
    ("passage_link_navigation_map", ("passages", "links", "passage links", "story formats", "nonlinear stories", "reachable path", "dead-end", "navigation map", "twine")),
    ("choice_stats_consequence_gate", ("stats", "variables", "choice stats", "stat mutation", "achievements", "commands", "visible consequence", "delayed consequence", "choice consequences")),
    ("source_text_fingerprint_gate", ("winnowing", "document fingerprinting", "fingerprinting", "plagiarism detection", "copied slices", "moss", "source fingerprint", "text fingerprint", "fingerprint overlap", "textreuse", "text reuse", "document similarity", "text alignment")),
    ("fuzzy_phrase_similarity_gate", ("fuzzy string matching", "levenshtein", "string metrics", "sequence matcher", "sequencematcher", "fuzzy phrase", "phrase similarity")),
    ("diff_span_copy_review", ("diff match patch", "diff, match and patch", "semantic cleanup", "copied spans", "diff spans", "patch library", "diff_span")),
    ("minhash_lsh_near_duplicate_gate", ("minhash", "lsh", "locality sensitive hashing", "jaccard similarity", "near duplicate", "near-duplicate", "text dedup", "deduplication", "text-dedup", "datasketch")),
    ("simhash_hamming_similarity_gate", ("simhash", "hamming distance", "hamming", "similar hashes", "near-duplicate documents", "near duplicate documents", "simhash-py")),
    ("semantic_duplicate_cluster_gate", ("semantic deduplication", "semantic dedup", "semantic duplicates", "semhash", "semdedup", "embedding clusters", "cluster semantic duplicates")),
    ("embedding_similarity_independence_gate", ("sentence-transformers", "sentence transformers", "embedding similarity", "dense vectors", "similarity search", "nearest neighbor", "nearest neighbours", "faiss", "vector similarity", "cosine similarity")),
    ("corpus_leakage_dedup_review_gate", ("deduplicating training data", "exactsubstr", "neardup", "dataset deduplication", "deduplicate language model datasets", "corpus leakage", "training data dedup", "repeated sequences")),
    ("character_quote_attribution_map", ("booknlp", "book-length documents", "character coreference", "character mentions", "quote attribution", "speaker attribution", "entity tokens", "quote speaker", "speaker map")),
    ("readability_pacing_metric_gate", ("readability", "readability statistics", "sentence length", "paragraph length", "flesch", "gunning fog", "smog index", "text statistics")),
    ("prose_lint_style_rule_gate", ("prose lint", "prose linter", "style linter", "natural language linter", "text linter", "vale", "textlint", "proselint", "write-good", "write good", "weasel words", "passive voice", "cliches", "style guide rules", "house style", "lint prose", "\u6587\u7a3f\u6821\u5bf9", "\u98ce\u683c\u89c4\u5219", "\u6563\u6587\u68c0\u67e5")),
    ("grammar_spelling_copyedit_gate", ("grammar checker", "spelling and grammar", "spell checker", "spellcheck", "spelling", "languagetool", "harper", "proofreading", "copyedit", "copyediting", "grammar engine", "offline grammar", "\u8bed\u6cd5\u68c0\u67e5", "\u62fc\u5199\u68c0\u67e5", "\u6821\u5bf9")),
    ("copyedit_diagnostic_triage_queue", ("lint diagnostics", "style diagnostics", "copyedit suggestions", "diagnostics", "suggestions", "rule violations", "ignore rules", "suppression", "accepted ignored", "triage", "diagnostic queue", "revision queue", "\u6821\u5bf9\u961f\u5217", "\u8bca\u65ad\u961f\u5217", "\u91c7\u7eb3\u5ffd\u7565")),
    ("lexical_diversity_voice_audit", ("lexical richness", "lexical diversity", "mtld", "hd-d", "hdd", "type-token", "type token ratio", "vocabulary diversity")),
    ("stylometric_author_fingerprint_gate", ("stylometry", "computational stylistics", "stylometric analyses", "stylometric analysis", "style fingerprint", "stylometric profile", "author fingerprint", "author-style transfer", "stylometric transfer", "authorship attribution", "burrows delta", "burrow's delta", "pydelta", "distance metrics", "style model")),
    ("function_word_syntax_style_gate", ("function words", "most frequent words", "mfw", "sentence length", "word length", "punctuation frequency", "pos tags", "syntactic features", "readability scores", "vocabulary richness", "style metrics", "stylometric features", "character n-grams")),
    ("authorship_attribution_similarity_gate", ("authorship attribution", "author identification", "author verification", "author profiling", "style similarity", "cosine similarity between titles", "pan corpora", "pan shared tasks", "burrows delta", "cross-entropy", "llm stylometry")),
    ("style_overfit_regression_gate", ("style change detection", "style breach detection", "intrinsic plagiarism", "style change", "style breach", "detecting exact indices", "neighboring paragraphs", "cluster change", "style differences", "overfit", "overfitting", "style leakage")),
    ("paraphrase_independence_review_gate", ("anti-stylometry", "style anonymization", "stylometric transfer", "author-style transfer", "humanization", "similarity methods", "style constraints", "style transfer", "paraphrase", "paraphrase independence", "copy-risk", "author voice mimicry")),
    ("keyphrase_motif_extraction", ("keyphrase extraction", "keyword extraction", "keyphrase candidates", "candidate weighting", "motif extraction", "motif drift", "topic salience")),
    ("chinese_segmentation_keyword_gate", ("chinese word segmentation", "jieba", "hanlp", "ltp", "tokenization", "tokenizer", "segmentation", "word segment", "keyword extraction", "tf-idf", "textrank", "custom dictionary", "user dictionary", "\u4e2d\u6587\u5206\u8bcd", "\u5173\u952e\u8bcd\u63d0\u53d6", "\u81ea\u5b9a\u4e49\u8bcd\u5178")),
    ("chinese_ner_alias_consistency_gate", ("chinese ner", "named entity recognition", "ner", "hanlp", "ltp", "chinese-literature-ner-re-dataset", "discourse-level named entity", "literature text", "relation extraction", "entity recognition", "person name", "location name", "organization name", "alias", "coreference", "entity linking", "\u5b9e\u4f53\u8bc6\u522b", "\u4eba\u540d", "\u5730\u540d", "\u7ec4\u7ec7\u540d", "\u522b\u540d")),
    ("chinese_text_normalization_gate", ("opencc", "simplified chinese", "traditional chinese", "chinese conversion", "text normalization", "normalization", "punctuation normalization", "fullwidth", "halfwidth", "variant characters", "\u7b80\u7e41\u8f6c\u6362", "\u6587\u672c\u89c4\u8303\u5316", "\u5168\u89d2", "\u534a\u89d2")),
    ("chinese_error_correction_review_gate", ("chinese spelling correction", "chinese text correction", "pycorrector", "confusion set", "error correction", "spelling correction", "grammar correction", "proofreading", "bert correction", "\u4e2d\u6587\u7ea0\u9519", "\u9519\u522b\u5b57", "\u6df7\u6dc6\u96c6")),
    ("source_format_import_manifest", ("epub", "ebook", "ebooklib", "pandoc", "markitdown", "docling", "mineru", "marker", "format conversion", "document conversion", "office documents", "llm-ready markdown", "llm-ready markdown/json", "pdf to markdown", "pdf-to-markdown", "mobi", "azw3", "docx", "opf", "spine", "table of contents", "toc", "metadata", "chapter import", "source import", "\u7535\u5b50\u4e66", "\u76ee\u5f55", "\u7ae0\u8282\u5bfc\u5165")),
    ("pdf_layout_text_extraction_gate", ("pdfminer", "pymupdf", "docling", "mineru", "marker", "pdf text extraction", "layout analysis", "document analysis", "layout model", "pdf parser", "pdf converter", "pdf extractor", "pdf-to-json", "pdf-to-text", "text blocks", "page coordinates", "reading order", "page spans", "pdf pages", "\u7248\u9762", "\u9875\u7801", "\u6587\u672c\u5757")),
    ("ocr_scanned_page_import_gate", ("ocr", "ocrmypdf", "tesseract", "mineru", "marker", "scanned pdf", "scanned page", "hocr", "ocr confidence", "deskew", "page image", "image text", "\u626b\u63cf", "\u56fe\u50cf\u8bc6\u522b", "\u8bc6\u522b\u7f6e\u4fe1\u5ea6")),
    ("document_partition_chapter_detection_gate", ("unstructured", "docling", "mineru", "marker", "document parser", "document parsing", "document partition", "partition_pdf", "partition_epub", "document elements", "title element", "heading detection", "section detection", "chapter detection", "layout element", "\u7ae0\u8282\u68c0\u6d4b", "\u6807\u9898\u8bc6\u522b")),
    ("import_provenance_checksum_gate", ("checksum", "hash", "source file", "file provenance", "import manifest", "page range", "extraction settings", "parser version", "input artifact", "conversion log", "\u6821\u9a8c\u548c", "\u6765\u6e90\u8ffd\u6eaf", "\u5bfc\u5165\u6e05\u5355")),
    ("epub_structure_validation_gate", ("epubcheck", "epub conformance", "epub validation", "opf manifest", "package document", "container.xml", "spine validation", "media-type validation", "validation report", "epub tests", "\u7535\u5b50\u4e66\u6821\u9a8c", "\u51fa\u7248\u6821\u9a8c")),
    ("ebook_accessibility_audit_gate", ("ace by daisy", "epub accessibility", "accessibility checker", "accessibility metadata", "wcag", "screen reader", "reading system accessibility", "alt text", "landmarks", "hazards", "\u53ef\u8bbf\u95ee\u6027", "\u9605\u8bfb\u7cfb\u7edf")),
    ("front_back_matter_metadata_gate", ("standard ebooks", "front matter", "back matter", "titlepage", "title page", "colophon", "endnotes", "copyright page", "publication metadata", "dc:title", "dc:creator", "\u524d\u8a00", "\u540e\u8bb0", "\u51fa\u7248\u5143\u6570\u636e")),
    ("toc_navigation_consistency_gate", ("sigil", "nav toc", "navigation document", "ncx", "spine order", "toc navigation", "table of contents", "heading hierarchy", "reader navigation", "landmarks", "\u76ee\u5f55\u5bfc\u822a", "\u9605\u8bfb\u5bfc\u822a")),
    ("agentic_editorial_pipeline_gate", ("multi-agent framework", "seven specialized ai agents", "editorial production pipeline", "editorial pipeline", "professional editorial team", "book-building system", "planner writer reviewer", "copy-edit", "compile your manuscript", "claude book framework", "\u591a\u667a\u80fd\u4f53", "\u7f16\u8f91\u6d41\u6c34\u7ebf")),
    ("chapter_state_archive_ladder", ("permanent bible", "transient state", "versioned per chapter", "chapter-nn", "archived states", "state/current", "state file templates", "timeline/history", "chapter state", "current symlink", "\u7ae0\u8282\u72b6\u6001", "\u72b6\u6001\u5f52\u6863")),
    ("section_metadata_traceability_gate", ("section metadata", "characters, locations, and items", "characters locations items", "plot lines", "plot points", "pacing visualization", "structural analysis", "acts", "beats", "chapter metadata", "narrative dag", "knowledge graph", "\u77e5\u8bc6\u56fe\u8c31", "\u7ae0\u8282\u5143\u6570\u636e")),
    ("ai_prose_fingerprint_cluster_gate", ("ai writing fingerprints", "prose pattern scanner", "overused patterns", "em-dashes", "show-then-tell", "hedging language", "voice drift", "severity scoring", "cluster detection", "defingerprint", "prose scanner", "\u673a\u5473", "\u98ce\u683c\u6f02\u79fb")),
    ("author_candidate_canon_confirmation_gate", ("candidate is not canon", "candidates are not canon", "candidate-not-canon", "preview confirm apply", "preview / confirm / apply", "preview/confirm/apply", "propose-then-confirm", "safe propose-then-confirm", "ai is off by default", "ai levels", "workspace level", "level 0 to 5", "single dial", "ai prose, in a slot you defined", "confirmed true", "source: user-explicit", "ai-suggested", "clarification rollback", "candidate outline", "canon review", "候选不入正典", "预览确认应用", "候选大纲", "作者确认", "回滚")),
    ("progressive_spoiler_context_window_gate", ("spoiler filtering", "spoiler filter", "future chapter", "future chapters", "future-chapter", "six-stage", "six stage", "stage-aware", "progressive pacing", "strict moderate minimal none", "range validation", "context window", "context-window", "anti-rushing", "\u5267\u900f\u8fc7\u6ee4", "\u672a\u6765\u7ae0\u8282", "\u9636\u6bb5\u611f\u77e5", "\u4e0a\u4e0b\u6587\u7a97\u53e3", "rag\u8303\u56f4", "\u9632\u62a2\u8dd1")),
    ("chapter_control_card_writeback_gate", ("chapter control card", "chapter control cards", "control-card", "control card", "control-cards", "dynamic state file", "dynamic state management", "state write-back", "write back", "chapter title control", "chapter handoff pressure", "\u7ae0\u8282\u63a7\u5236\u5361", "\u52a8\u6001\u72b6\u6001", "\u5199\u56de", "\u6807\u9898\u63a7\u5236", "\u7ed3\u5c3e\u94a9\u5b50")),
    ("trace_replay_revision_workspace_gate", ("trace replay", "decision trace", "chapter workbench", "memory browser", "quality dashboard", "reviewable and traceable", "trajectory replay", "rebuild this chapter", "\u8f68\u8ff9\u56de\u653e", "\u51b3\u7b56\u8ffd\u8e2a", "\u7ae0\u8282\u5de5\u4f5c\u53f0", "\u91cd\u5199\u5f71\u54cd")),
    ("relationship_graph_global_replace_gate", ("global find replace", "global search replace", "find and replace", "one-click replace", "graphviz", "relationship graph", "character relationship graph", "upstream change", "conflict warning", "\u5168\u5c40\u67e5\u627e\u66ff\u6362", "\u5173\u7cfb\u56fe", "\u4eba\u7269\u5173\u7cfb\u56fe", "\u4e00\u952e\u66ff\u6362", "\u51b2\u7a81\u9884\u8b66")),
    ("bookrun_audit_trail_gate", ("bookrun", "book run", "blueprint", "judge/repair", "judge repair", "export audit", "audit_report.json", "book.md", "checkpoint resume", "real llm smoke", "core verification", "e2e run")),
    ("provider_budget_smoke_gate", ("provider budget", "llm profile", "llm profile routing", "token budget", "time budget", "cost tracking", "prompt cache", "cache hit", "cost per 1000-chapter", "provider fallback", "provider smoke", "real llm smoke", "smoke gate", "budget controls")),
    ("sidecar_memory_profile_boundary", ("python sidecar", "go api gateway", "graph/vector memory", "graph memory", "vector memory", "deployment profiles", "sqlite-only", "no-graph-vector", "qdrant", "neo4j", "redis", "sidecar")),
    ("outline_checkpoint_milestone_gate", ("outline checkpoint", "chapter milestone", "narrative milestone", "narrative milestones", "story bible truth source", "story bible as truth source", "checkpoint constraints", "layered outline", "blueprint milestone", "chapter sequence")),
    ("language_localization_style_profile_gate", ("vietnamese writing patterns", "style_guide_vn", "style guide vn", "localized writing rules", "language style guide", "language-specific style", "units:", "proper nouns/terms", "cumulative glossary", "\u6587\u98ce\u6837\u672c", "\u672c\u5730\u5316")),
    ("progressive_disclosure_skill_protocol_gate", ("progressive disclosure", "intent-based command routing", "protocol files", "protocols/", "codex/", "entry light", "protocol heavy", "knowledge base", "agent workflow handbook", "agent should not put the entire repo", "docs/00-index.md", "command routing", "渐进式披露", "指令路由", "运行协议")),
    ("anti_slop_rulepack_triage_gate", ("no-slop", "banned vocabulary", "ai writing patterns", "anti-ai-pattern", "anti ai pattern", "prose linter", "simple copulas", "marketing language", "vague attribution", "slop", "rulepack", "triage", "反 ai 痕迹")),
    ("user_modifier_project_blueprint_gate", ("project modifiers", "target novel length", "target chapter word count", "ai-driven initial planning", "initial plan", "idea spark", "dashboard", "live timings", "system log", "project state", "export json")),
    ("portable_canon_skill_runtime_gate", ("canon governance", "canon layer", "portable skill runtime", "story/*.md", "markdown frontmatter", "sqlite state", "canon-sync", "artifact index", "project config", "skill runtime")),
    ("staged_outline_chunk_window_gate", ("sliding-window memory", "focused plot context", "adjacent parts", "cjk-aware counter", "start chapter", "end chapter", "chapter range refinement", "batch start", "resume interrupted generation", "plot token usage")),
    ("wiki_canon_graph_lint_gate", ("story bible wiki", "worldbuilding wiki", "canon lint", "wiki-query", "wiki-graph", "relationship graph", "continuity warnings", "timeline contradictions", "unresolved setup/payoff", "lore clusters")),
    ("plan_draft_log_verify_loop_gate", ("plan \u2192 draft \u2192 log \u2192 verify", "plan -> draft -> log -> verify", "plan draft log verify", "living documents", "thread tracking", "foreshadowing checklists", "scene logs", "wrap", "documents are current")),
    ("mcp_scene_index_revision_boundary", ("metadata-first analysis", "sqlite-canonical", "scene files", "safe scene revision", "ai-assisted prose editing with confirmation", "git history", "review bundles", "scrivener direct extraction", "targeted scene reading", "sync dir")),
    ("verbalized_sampling_diversity_wiki_gate", ("verbalized sampling", "mode collapse", "distribution of responses", "probability score", "writer's wiki", "auto-files", "automatic character and setting detection", "diverse outlines", "brainstorm", "critic")),
    ("mode_contract_generation_gate", ("mode contract", "mode-specific contract", "public mode contract", "selected-mode priority", "selected-mode-first", "selected mode", "output mode", "output modes", "visible axes", "creative axes", "axis tags", "audience", "ending style", "narrator", "point of view", "under-length", "rewrite handling", "draft length", "structured generation contract")),
    ("source_study_method_bank_isolation_gate", ("master study", "masterworks", "masterchunkanalysis", "masterchapterbeats", "masterstylemetrics", "masterinsights", "methodology library", "method bank", "source study", "independent data table", "does not pollute creative data", "not pollute creative data")),
    ("inline_human_machine_coauthoring_gate", ("human-machine co-creation", "human machine co creation", "precise modification", "inline edit", "micro adjustment", "ai polishing", "生成即起点", "微调见真章", "人机共创", "精细化", "局部修改", "润色")),
    ("hierarchical_orchestrator_generation_gate", ("orchestrator-driven", "orchestrator driven", "orchestrator", "hierarchical planning", "volume and arc", "new volume", "new arc", "memory weave", "生成 → 验证 → 改进", "分层规划", "编排器", "卷和情节弧线", "作品发布")),
    ("batch_continuation_progress_queue_gate", ("batch generation", "batch generate", "batch scribe", "batchscribe", "批量生成", "批量创作", "批量续写", "progress tracking", "auto continuation", "自动判定进度续写", "进度追踪", "自动续写")),
    ("homogeneity_prompt_variation_gate", ("homogeneity", "samey", "同质化", "random title", "random topic", "随机生成书名", "随机生成题材", "prompt variation", "prompt revision", "修改了提示词")),
    ("local_author_data_boundary_gate", ("local data management", "local data", "offline data", "本地数据", "本地ollama", "local ollama", "local desktop", "windows packaged", "windows 打包版", "automatic update", "自动升级", "upgrade.zip")),
    ("prompt_preset_variable_library_gate", ("prompt preset", "prompt presets", "prompt variable", "prompt variables", "prompt template", "prompt-template", "variable system", "template import", "usage stats", "提示词库", "提示词管理", "预设管理", "系统提示词", "用户提示词", "变量系统", "动态变量", "template library", "模板导入", "提示词效果追踪")),
    ("imported_manuscript_migration_outline_gate", ("imported manuscript", "manuscript import", "txt import", "txt 导入", "导入小说", "智能解析目录", "generate each chapter outline", "每章大纲", "quickly migrate existing work", "迁移现有作品", "选择性导入")),
    ("style_dna_reference_library_gate", ("style dna", "writing dna", "writing-dna", "文笔dna", "narrative dna", "拆书知识库", "reference library", "参考库", "学习和模仿", "风格模仿", "风格学习")),
    ("draft_candidate_promotion_gate", ("draft vs confirmed", "confirmed chapters", "rewrite candidates", "candidate comparison", "草稿不会自动覆盖正文", "草稿候选", "确认稿", "重写候选", "人工确认稿", "promoting only approved drafts")),
    ("privacy_preserving_local_index_gate", ("privacy-preserving index", "metadata-only", "metadata only", "never manuscript", "all data stays local", "all data is saved", "offline-first", "本地保存", "本地化数据", "数据优先保存在本机", "草稿不会自动覆盖正文")),
    ("chapter_description_continuity_bridge_gate", ("chapter descriptions", "chapter-by-chapter outline", "previous chapters for continuity", "awareness of all previous chapters", "previous chapters as context", "structured book", "guided mode", "pro mode")),
    ("selective_streaming_regeneration_gate", ("real-time streaming", "streaming text", "generate the entire book", "individual chapters", "regenerate specific chapters", "without losing the rest", "inline editing", "save instantly")),
    ("research_citation_boundary_gate", ("ai research engine", "web search integration", "academic databases", "citation styles", "citations are woven", "quality & plagiarism checks", "plagiarism checks", "source content")),
    ("beta_reader_summary_context_gate", ("ai beta reader", "contextual ai reviews", "structured summaries", "summaries of previous chapters", "previous chapter summaries", "plot points, characters", "multiple review styles", "fan style")),
    ("style_vocab_world_card_extraction_gate", ("style vocabulary", "vocabulary library", "world cards", "worldbuilding extraction", "worldview extraction", "setting completion", "character card extraction", "chapter-local modification")),
    ("prompt_only_decay_ceiling_gate", ("pure-prompt", "prompt-only", "prompt only", "no install and no api key", "comfort zone decay", "wrap-up mode", "10 chapter stress test", "5000-6000 character")),
    ("serial_platform_minimum_audit_gate", ("minimum audit set", "battle scene audit", "dialogue ratio monitor", "cycle pattern detection", "full audit every 10 chapters", "every 5 chapters", "ai de-flavoring", "chapter checks")),
    ("multi_agent_reject_retry_review_gate", ("reject retry", "reject retry up to 3 times", "score below 80", "returning to planning", "consistency checker", "outline change impact analysis", "architect, writer", "langchain and langgraph")),
    ("story_bible_context_packet_branch_gate", ("context packet assembly", "context packet", "recent chapter summaries", "branch and save points", "save points", "restore earlier scene versions", "dual-persona editorial reviews", "canonical fact extraction")),
    ("memory_augmented_delta_verification_gate", ("memory-augmented extraction", "chain-of-verification", "deterministic accumulation", "delta extraction", "structured facts from current chapter", "targeted questions", "incremental processing", "codex validation")),
    ("statistical_style_benchmark_rewrite_gate", ("22-book", "22 published novels", "22-book statistical analysis", "style presets", "smart rewriter", "quality analyzer", "character voice profiles", "sensory density")),
    ("literary_event_entity_annotation_gate", ("litbank", "literary entities", "literary entity", "literary event detection", "literary events", "annotated dataset of fiction", "coreference in english literature", "entity annotation", "event annotation", "\u6587\u5b66\u5b9e\u4f53", "\u6587\u5b66\u4e8b\u4ef6")),
    ("narrative_event_evolution_graph_gate", ("narrative event evolutionary graph", "narrative event chain", "narrative event chains", "script event prediction", "event-centric dataset", "event narrative", "event embedding", "discourse relations", "event graph", "event evolution", "\u4e8b\u4ef6\u94fe", "\u53d9\u4e8b\u4e8b\u4ef6")),
    ("sentiment_arc_emotion_trajectory_gate", ("syuzhet", "sentiment arcs", "sentimentarcs", "sentiment-based plot arcs", "sentiment based plot arcs", "emotion in text over time", "literary emotion dynamics", "emotion trajectory", "emotion timeline", "\u60c5\u7eea\u5f27", "\u60c5\u611f\u8d70\u5411")),
    ("cross_context_coreference_gate", ("cross-context coreference", "cross context coreference", "cross-document coreference", "cross document coreference", "xcore", "xcoref", "entity, event, and abstract concepts", "multiple contexts", "multiple documents", "mention cluster", "\u8de8\u6587\u6863\u5171\u6307", "\u5171\u6307\u6d88\u89e3")),
    ("character_interaction_network_gate", ("character network", "character-network", "character networks", "fictional characters", "social networks of fictional characters", "character interactions", "relationship network", "temporal signed character networks", "character social relationship", "\u4eba\u7269\u5173\u7cfb\u7f51", "\u89d2\u8272\u4e92\u52a8")),
    ("semantic_chunk_boundary_map", ("semantic text splitter", "semantic chunk", "semantic chunking", "text splitter", "text splitting", "recursive character text splitter", "recursive character splitter", "chunk capacity", "chunk boundary", "boundary preservation")),
    ("chapter_summary_anchor_gate", ("automatic text summarizer", "extractive summarizer", "extractive summarization", "summarization chains", "lsa", "lexrank", "textrank", "representative sentences", "chapter summary", "summary anchor")),
    ("topic_drift_map", ("topic modeling", "bertopic", "dynamic topic modeling", "dynamic topics", "topic representation", "c-tf-idf", "topic drift", "topic clusters")),
    ("context_faithfulness_eval_gate", ("faithfulness", "answer relevancy", "answer relevance", "context precision", "context recall", "groundedness", "context relevance", "hallucination metrics", "rag evaluation")),
    ("retrieval_trace_observability_gate", ("llm app observability", "ai observability", "observability", "tracing", "traces", "retrieval traces", "llm spans", "feedback functions")),
    ("prompt_regression_eval_suite", ("prompt tests", "golden datasets", "golden dataset", "regression suites", "regression suite", "regression tests", "ci evaluation", "custom evals", "graders")),
    ("agentwrite_plan_write_pipeline", ("agentwrite", "plan.py", "write.py", "plan.txt", "write.txt", "outline_vlm", "automated ultra-long output data construction", "plan and then write")),
    ("long_output_length_quality_ruler", ("longwriter", "longbench-write", "longwrite-ruler", "mmlongbench-write", "ultra-long text generation", "ultra-long output", "10000+ words", "maximum output length", "output length", "long output quality", "length stress test")),
    ("long_context_reward_dimension_gate", ("longreward", "long-context scenarios", "helpfulness", "logicality", "faithfulness", "completeness", "final reward", "reward score", "auto_scorer")),
    ("instance_specific_writing_criteria_gate", ("writingbench", "instance-specific criteria", "requirement-dimension scores", "requirement dimension scores", "5 instance-specific criteria", "five instance-specific criteria")),
    ("material_grounded_query_refinement", ("model-augmented query generation", "human-in-the-loop refinement", "query diversification", "query refinement guidance pool", "material collection", "material pruning")),
    ("hybrid_rubric_pairwise_elo_judge", ("creative writing benchmark v3", "hybrid rubric", "pairwise matchups", "elo scoring", "glicko-2", "win margin", "final elo")),
    ("judge_bias_mitigation_check", ("bias mitigation", "judge biases", "length bias", "position bias", "verbosity", "poetic incoherence", "length, position, verbosity")),
    ("plan_reflect_character_chapter_pipeline", ("longform creative writing benchmark", "brainstorming & planning", "critical reflection", "character profiles", "8 chapters", "complete novella", "narrative construction")),
    ("human_story_metric_panel", ("hanna", "human-annotated narratives", "relevance, coherence", "empathy, surprise", "engagement and complexity", "automatic story evaluation", "human annotated narratives")),
    ("hierarchical_cowriting_story_scaffold", ("dramatron", "hierarchical story generation", "log line", "character descriptions", "plot points", "location descriptions", "dialogue", "co-writing")),
    ("human_coauthor_edit_boundary", ("human authors", "compilation, editing, and rewriting", "human editing", "plagiarism", "toxicity scores", "formulaic", "co-writer")),
    ("recursive_reprompt_revision_loop", ("re3", "recursive reprompting", "recursive reprompting and revision", "plan, draft, rewrite, edit", "plan-draft-rewrite", "outline reload", "setup-only")),
    ("reranker_guided_candidate_selection", ("relevance reranker", "coherence reranker", "reranker", "max-candidates", "max-beam-size", "continuation-threshold", "dynamic continuation")),
    ("character_dialogue_persona_memory", ("chat-haruhi", "character imitation", "approximate tone", "personality and plot chat", "extracting characters from novels", "novel_collecting", "role datasets")),
    ("event_to_sentence_realization_trace", ("story realization", "plot events into sentences", "event-to-sentence", "event creation", "eventify", "ensemble thresholds", "confidence scores")),
    ("entity_memory_slotfill_grounding", ("slot filling", "slotfilling", "memory graph", "getagentturn", "entities", "entity tracking")),
    ("book_memory_bank_context_lattice", ("book memory bank", "stateless ai", "memory resets", "projectbrief.md", "story_structure.md", "world_and_characters.md", "activecontext.md", "progress.md", "comprehensive memory bank updating")),
    ("spec_driven_fiction_scene_tasks", ("spec kit fiction", "story bible governance", "constitution.md", "scene-by-scene writing tasks", "quality gates instead of ci", "pov schedule", "information asymmetry map", "glossary audit", "subplot health dashboard")),
    ("toc_aware_source_deconstruction", ("llm ebook summarizer", "epub files", "pdf files", "table of contents", "nested chapters", "parent section introductions", "structured markdown notes", "quotes and anecdotes", "merge utility")),
    ("two_pass_context_glossary_pipeline", ("two-pass translation", "pass 1 (analysis)", "pass 2 (translation)", "previous chapter summary", "cumulative glossary", "proper nouns/terms", "resume support", "prompt templates")),
    ("inline_author_edit_markup_versioning", ("story framework", "markdown files and git", "source of truth", "continuity/timeline.md", "continuity/facts.md", "process edit notes", "[[pov", "{{fix", "git tag")),
    ("causal_dramatica_agent_pipeline", ("dramatica", "causal-driven", "causal driven", "causal chain", "causal-chain management", "5-layer agent", "five-layer agent", "multi-line narration", "deep narrative logic", "因果链", "多线叙事", "伏笔追踪")),
    ("capture_distillation_production_gate", ("capture -> distillation -> production", "capture distillation production", "capture stage", "distillation stage", "production stages", "story foundry", "agent-template", "agentic platform to assist an author")),
    ("skill_orchestrated_chinese_novel_workflow", ("openclaw skill", "agent-skill", "awesome novel skill", "web novel writing skill", "chinese novel writing", "chinese-novel", "web-novel", "10-stage pipeline", "7 expert roles", "4-layer anti-hallucination", "state-sync memory", "golden-three-chapters", "worldbuilding to character shaping", "章节规划", "正文写作", "小说创作搭档")),
    ("langgraph_story_state_machine", ("langgraph", "langchain", "story state flow", "story-writing sample", "langgraph.json", "agent.py", "stateful planning", "story state machine")),
    ("story_daemon_evolution_loop", ("storydaemon", "autonomous agent", "plans, writes, and evolves stories", "evolves stories organically", "organic planning", "long-form fiction through an autonomous agent")),
    ("local_rag_writing_ide_gate", ("local rag", "hybrid rag", "local-first", "privacy-first", "byok", "million-word local rag", "vector search", "local vector", "local-only", "knowledge base", "semantic vector retrieval")),
    ("canon_drift_continuity_qa_gate", ("canon drift", "continuity checker", "continuity detective", "continuity qa", "story bible and continuity", "contradictions before", "canon qa", "continuity engine", "scene context", "fact mismatch")),
    ("patch_replay_manuscript_state_gate", ("patch-nn", "patch-01", "outline.xml", "final.xml", "version-nn", "replays these patches", "reconstruct the story's current state", "sequential dispatch logs", "latest.html")),
    ("microkernel_skill_plugin_isolation_gate", ("microkernel", "plugin architecture", "eventbus", "pluginmanager", "hot-reload", "skill builder agent", "plugin.json", "plugin hook", "stage plugin", "skill isolation")),
    ("interactive_reader_writer_loop_gate", ("interactive ai-assisted editing", "interactive menu", "reader", "writer", "guide the plot", "story into chapter files", "three-way collaboration", "card-based editing", "reader-writer", "chapter files")),
    ("abstract_style_learning_skill_gate", ("writing style skill", "style learning", "technique spectrum", "representative sampling", "style sample", "style profile", "character voice matrix", "retention model", "do not copy source prose")),
    ("impromptu_thread_pool_chapter_gate", ("improvised writing", "即兴写作", "open_threads", "伏笔池", "single-chapter blueprint", "单章蓝图", "chapter intent", "口述意图", "finalize", "已埋未收", "已收未结", "待开发")),
    ("offline_inspiration_bank_style_gate", ("inspiration bank", "100% offline", "offline & private", "offline creative writing", "style mimicry", "dynamic style engine", "local ollama", "local rag pipeline", "lancedb", "inspiration", "rewrite", "continue")),
    ("atelier_phase_pipeline_gate", ("novel atelier", "50 agents", "70 skills", "6-phase pipeline", "beat planner", "hook auditor", "infinite-serial", "human control", "manual mode", "semi mode", "full mode", "developmental editor", "continuity reader")),
    ("book_mining_genesis_automation_gate", ("book-mining", "book mining", "novel-genesis", "novel automation", "novel-automation", "canon-seed", "canon seed", "pattern assembly", "market scan", "scoring gate", "pattern-aware quality gates", "library/index.yaml")),
    ("multi_book_autopilot_studio_gate", ("multi-book", "multi book", "autopilot", "full-book logic check", "full book logic check", "fullcheckevery", "maxautocontinue", "unterm profile", "bookshelf", "book shelf", "multi-interface", "多本长篇", "全文逻辑自检")),
    ("longrun_commit_projection_health_gate", (".story-system", ".webnovel", "chapter_commit", "CHAPTER_COMMIT", "read-model", "read model", "projection writers", "memory_scratchpad", "state.json", "index.db", "longrun aigen", "context agent", "data agent", "read-only dashboard")),
    ("fresh_context_chapter_iteration_gate", ("fresh context", "no memory fatigue", "next incomplete chapter", "find next incomplete chapter", "progress.txt", "prd.json", "story_bible", "plan write review revise", "plan → write → review → revise", "skill ensemble", "loop until all chapters complete")),
    ("reader_reward_channel_gate", ("four reward channels", "reader reward", "reader-sim", "reader sim", "transportation", "aesthetic", "social simulation", "flow", "simulated reader reactions", "moment-by-moment")),
    ("tri_modal_workflow_validation_gate", ("tri-modal", "tri modal", "create/edit/validate", "create + edit + validate", "pre-writing checklist", "automated audit chain", "living bible update", "character-specific audits", "rhythm analysis")),
    ("scene_promise_mob_review_gate", ("chapter promise", "scene architect", "character truth", "mob session", "comment queue", "lead editor", "citation enforcement", "five commandments", "value shift")),
    ("webnovel_genre_tracker_gate", ("webnovel-mcp", "story engine v2", "story factory", "1000-chapter", "foreshadowing tracker", "timeline tracker", "volume", "climax ladder", "cast database", "power-system canon", "plot twists", "litrpg stats", "litrpg stat blocks", "romance arc tracker", "stale characters", "chapter gaps", "xianxia", "progression fantasy")),
    ("simulation_causal_ledger_verification_gate", ("simulation-first", "world truth", "belief state", "utterance history", "causal ledger", "verify-long-form", "canonical validation", "300-episode", "long-form verification")),
    ("writer_git_exploration_review_gate", ("gitwrite", "writer-friendly git", "explorations", "word-by-word comparison", "beta reader annotations", "author control", "selective integration", "cherry-pick individual changes")),
    ("narrative_qa_comprehension_gate", ("narrativeqa", "reading comprehension challenge", "questions and answers", "qaps.csv", "document_id", "wikipedia summaries", "full stories")),
    ("chapter_summary_alignment_gate", ("booksum", "long-form narrative summarization", "chapter-level", "book-level", "paragraph-level", "human written summaries", "causal and temporal dependencies")),
    ("story_question_answer_validation_gate", ("fairytaleqa", "narrative comprehension", "question-answer pairs", "qa-pairs", "cor_section", "story_section", "education experts", "7 narrative elements")),
    ("causal_why_explanation_gate", ("tellmewhy", "why-questions", "why questions", "why characters", "free-form answers", "helpful_sentences", "validity human judgments", "plausible answer")),
    ("story_commonsense_consistency_gate", ("storycommonsense", "story commonsense", "naive psychology", "character motivations", "character emotions", "mental states", "simple commonsense stories")),
    ("query_focused_long_summary_gate", ("squality", "question-focused", "long-document", "multi-reference summarization", "what is the plot of the story", "four reference summaries", "project gutenberg story")),
    ("temporal_canon_context_graph", ("graphiti", "temporal knowledge graph", "temporal context", "episodes", "bi-temporal", "valid_at", "invalid_at", "hybrid search", "provenance tracking")),
    ("long_term_author_preference_memory", ("mem0", "memory layer", "long-term memory", "user preferences", "session memory", "adaptive personalization", "multi-level memory", "episodic memory")),
    ("community_graph_source_deconstruction", ("graphrag", "community summaries", "community reports", "extract structured data from unstructured text", "entity extraction", "graph-based indexing", "global search", "local search")),
    ("dual_level_graph_vector_retrieval", ("lightrag", "dual-level", "dual level", "knowledge graphs", "vector embeddings", "naive", "local", "global", "hybrid", "kg+vector")),
    ("schema_guided_graph_extraction", ("llm graph builder", "extract nodes", "relationships and properties", "custom schema", "node labels", "relationship types", "source metadata", "neo4j graph")),
    ("trope_inventory_similarity_gate", ("tvtropes", "tv tropes", "trope correlation", "tropes they use", "trope similarity", "trope vector", "two works", "terms of the tropes")),
    ("trope_graph_expectation_map", ("trope graph", "trope network", "network of tropes", "trope co-occurrence", "trope adjacency", "categories and related tropes")),
    ("trope_density_novelty_budget", ("trope dataset", "movie tropes", "movies and their tropes", "trope inventory", "trope frequency", "trope density")),
    ("trope_source_boundary_review", ("tropescraper", "trope scraper", "tvtropes-parser", "not intended for mass scraping", "page parser for tv tropes", "scrape tv tropes")),
    ("source_license_detection_gate", ("licensee", "license detection", "detect licenses", "license detector", "license metadata", "license matcher")),
    ("spdx_reuse_compliance_gate", ("spdx", "reuse", "spdx-license-identifier", "spdx filecopyrighttext", "reuse recommendations", "license list data")),
    ("public_domain_corpus_boundary", ("project gutenberg", "public domain", "public-domain book corpora", "body of public domain texts", "gutenberg corpus", "gutenberg scraper")),
    ("attribution_derivative_work_gate", ("attribution", "derivative", "cc-by", "cc-by-sa", "license terms", "copyright", "reuse compliance")),
    ("source_entity_redaction_gate", ("presidio", "pii de-identification", "sensitive data", "redacting", "redaction", "anonymizing", "anonymization", "scrubadub", "personally identifiable information")),
    ("custom_entity_label_inventory", ("gliner", "extract any entity types", "custom entity types", "custom pii recognizers", "customizable pipelines", "pretrained pipelines", "named entity recognition", "ner models")),
    ("placeholder_alias_consistency_map", ("anonymous ids", "anonymized", "placeholder", "masking", "surrogate", "replacers", "detectors and postprocessors", "anonymize text")),
    ("proper_noun_leakage_review", ("proper noun", "names, locations", "person names", "locations", "organizations", "entity recognizer", "entity types", "rule based logic", "named entities")),
)
RISK_FILE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("postinstall", ("postinstall",)),
    ("docker", ("dockerfile", "docker-compose", "compose.yaml", "compose.yml")),
    ("shell_script", (".sh", "install.sh", "setup.sh")),
    ("powershell_script", (".ps1", "install.ps1", "setup.ps1")),
    ("native_binary", (".exe", ".dll", ".so", ".dylib")),
    ("binary_distribution", (".zip", "release/", "windows packaged", "windows 打包版", "安装包", "客户端")),
    ("auto_update", ("auto upgrade", "automatic update", "自动升级", "upgrade.zip", "在线升级")),
    ("windows_script", (".bat", ".cmd", "build_", "setup_env", "start_")),
    ("provider_key_surface", ("api key", "api keys", "api_key", "openai_api_key", "private api key", "private user api", "encrypted api key", "encrypted api keys", "user-configured api", "user configured api", "私有api key", "用户可配置私有api key", "用户自行配置", "api密钥", "密钥")),
    ("cloud_sync_oauth_surface", ("oauth", "oauth 2.0", "google drive", "cloud sync", "auth0", "jwt token", "pkce", "database_url", "postgres", "neon")),
    ("browser_storage_surface", ("indexeddb", "service worker", "pwa", "webllm", "tauri")),
    ("browser_extension", ("manifest.json", "chrome-extension", "extension")),
    ("mcp_server", ("mcp", "server.py", "server.ts")),
    ("device_control", ("adb", "root", "accessibility", "plugin marketplace")),
    ("network_scraper", ("scraper", "scrape", "crawler", "tropescraper", "tv tropes url")),
    ("corpus_downloader", ("download texts", "parallel downloads", "gutenberg scraper", "build public-domain book corpora", "full-text search")),
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
    "vkbo/novelwriter": (
        "Plain-text novel editor for manuscripts assembled from many smaller text documents. Public README describes human-readable file storage, minimal formatting, "
        "metadata syntax for comments, synopsis, and cross-referencing, and project format suited for version control and file synchronization."
    ),
    "olivierkes/manuskript": (
        "Open-source writer tool. Public README describes premise growth from one sentence to paragraph to full summary, characters, plots, outlines, index cards, worldbuilding, "
        "item tracking, chapter/scene reorganization, story line view, templates, writing modes, frequency analyzer, and import/export formats."
    ),
    "andreafeccomandi/bibisco": (
        "Open-source novel writing app. Public README describes chapter and scene organization, revisions, premise, fabula, narrative strands, geographic/temporal/social setting, "
        "and deep character understanding for believable characters."
    ),
    "wavemakercards/wavemaker-cards-v4": (
        "Creative writing and planning suite. Public README describes distraction-free writing, mind mapping, timeline planning, grid planner, character tracking across scenes, "
        "plot point management, and Snowflake Method step-by-step story development."
    ),
    "narcooo/inkos": (
        "Story creation AI agent for long/short fiction, screenplays, fan fiction, continuations, same-type writing, and interactive worlds. Public README describes review list/approve-all, "
        "continuity auditor dimensions, bounded revise-audit loops, plan/compose runtime artifacts intent.md/context.json/rule-stack.yaml/trace.json, Zod schema validated state deltas, "
        "author intent/current focus controls, SQLite temporal memory, and human-readable state projections."
    ),
    "maoxiaoyuz/long-novel-gpt": (
        "Long-novel agent using LLM and RAG. Public README describes importing an existing novel, book decomposition into plot/character relationship outline, user change requests, "
        "retrieving relevant body text snippets and plot outline, rewriting those snippets, and synchronously updating the plot outline."
    ),
    "dylanhogg/gptauthor": (
        "CLI for long-form multi-chapter stories. Public README describes human-written story prompt, AI-generated synopsis with chapter summaries, human review/edit/regeneration of synopsis, "
        "then iterative chapter writing from the common synopsis and previous chapter, exporting Markdown and HTML outputs."
    ),
    "kevboh/longform": (
        "Obsidian plugin for novels, screenplays, and long projects. Public README describes organizing notes/scenes into an ordered manuscript, reorderable/nestable scene list, "
        "scene/draft/project word counts, daily writing session goals, and workflow-based compilation into manuscripts."
    ),
    "principia-ai/writehere": (
        "Open-source long-form writing framework based on heterogeneous recursive planning. Public README describes recursive task decomposition, integration of retrieval/reasoning/composition, "
        "and dynamic adaptation during fiction and report writing."
    ),
    "ilearn-lab/novelclaw": (
        "Long-form fiction workspace centered on chapter drafting, inspectable runs, manuscript review, and memory-aware writing control. Public README describes sessions, storyboards, "
        "manuscript surfaces, character/world views, editable memory banks, chapter control, and GitHub-safe release posture."
    ),
    "howells/fiction": (
        "Claude Code fiction writing plugin. Public README describes a complete novel workflow with specialized agents for architecture, characters, prose, review, editing, "
        "continuity, and publishing prep; progress.md session tracking; chapter/scene breakdown; and chapter-by-chapter craft review."
    ),
    "mjbae/awesome-novel-studio": (
        "Claude Code web-novel production harness. Public README describes propose/design/create/polish/rewrite pipeline, 18 specialist agents, 16-axis polish, "
        "voice table, continuity bridge from the previous two episodes, range rewrite commands, and design-change impact scope."
    ),
    "danjdewhurst/story-skills": (
        "Agent Skills project format for fiction. Public README describes markdown files with YAML frontmatter for story bible, character files, worldbuilding notes, "
        "factions, artifacts, plot arcs, scene state, continuity questions, promises/payoffs, timelines, and chapter drafts."
    ),
    "hestudy/snowflake-fiction": (
        "Chinese Claude Code novel-writing plugin. Public README describes Snowflake method orchestration, concept validation, character design, scene planning with partial rerun, "
        "chapter writing, novel review, humanizing, quality checks, boring-detect, opening checks, and export."
    ),
    "forsonny/the-crucible-writing-system-for-claude": (
        "Claude Code epic-fantasy writing system. Public README describes a 36-beat framework, three interwoven strands, Forge Points and Apex, Mercy Engine, "
        "scene-by-scene drafting, bi-chapter reviews, anti-hallucination checks against planning documents, and automatic backups/restore."
    ),
    "xuanranl/webnovel-writer": (
        "Claude Code long web-novel system. Public README describes reducing forgetting and hallucination, RAG configuration, graph-hybrid/BM25 fallback, agent settings, "
        "7-layer audit gates, about 70 checks, audit-agent, chapter_audit CLI, and editor_notes cross-chapter feedback."
    ),
    "forsonny/book-os": (
        "Novel-OS structured workflow system. Public README describes AI-tool-agnostic writing context, genre guides, story outlines, scene-by-scene writing tasks, "
        "global standards, novel-specific style, and writing tasks that keep voice and context inspectable."
    ),
    "forjd/better-writing": (
        "Agent skill for human prose quality. Public README describes removing generic AI tells, slop structures, voice calibration from writing samples, "
        "factual guardrails so specificity does not become invention, and final pre-flight checks before delivery."
    ),
    "edwardathomson/novelwriter": (
        "Python LLM novel-writing application. Public README describes genre-specific worldbuilding, dynamic factions and locations, agentic multi-agent orchestration, "
        "scene/chapter/batch-level review, trend tracking, automated chapter writing, flexible outputs, and chapter manuscript combining."
    ),
    "stablellamaai/augmentedquill": (
        "Local-first AI writing assistant with project-based story authoring, multi-chapter and multi-book structure, Writing Partner chat, sourcebook entries for characters/scenes/lore/items, "
        "story.json configuration, image prompt support, and an explicit author-in-the-driver-seat boundary. GPL-3.0 and setup/runtime surfaces keep it pattern-only."
    ),
    "autofiction-ai/autofiction": (
        "Research pipeline for long-form AI novel generation and revision. Public README describes premise development, outlining, parallel chapter drafting, chapter review, "
        "full-book review, cross-chapter auditing, aggregate findings, revision cycles, structured artifacts, tests, expensive agent-job accounting, and AI-generated labeling/ethics."
    ),
    "yiling0013/ai_novelgenerator": (
        "Automatic novel generation tool. Public README describes setting workshop, intelligent multi-stage chapter generation, state tracking for character development and foreshadowing, "
        "semantic search, vector long-term context consistency, knowledge-base integration, automatic proofreading for plot contradictions/logical conflicts, and visual workbench."
    ),
    "picrew/constory-bench": (
        "Long-story consistency benchmark and ConStory-Checker. Public README describes narrative consistency errors across characterization, factual detail, narrative style, timeline/plot, "
        "world-building/setting, plus 19 subtypes such as forgotten abilities, nomenclature confusions, causality violations, abandoned plots, and rule violations."
    ),
    "harshaneel/humanize": (
        "LLM-agnostic static AI text humanization/detection skill. Public README describes perplexity, burstiness, stylometry, discourse, watermarking, nine humanization levers, "
        "rule-based audit-revise loop, limits against learned classifiers, and factual guardrails for specificity."
    ),
    "picrew/awesome-llm-story-generation": (
        "Curated LLM story/novel/script generation index. Public README describes 232 verified entries, 10 method categories, planning/decomposition, "
        "agent collaboration, sandbox/world simulation, multimodal story generation, memory/long-context, and evaluation/benchmark groupings. "
        "Absorb as index-only taxonomy; do not import catalog content into runtime prompts."
    ),
    "anning01/novelvids": (
        "Chinese novel-to-short-drama production platform. Public README describes a full AI-driven pipeline that transforms novels into video content through "
        "chapter/script processing, entity extraction, reference imagery, storyboards, and video synthesis. High runtime/API surface keeps it pattern-only."
    ),
    "memecalculate/moyin-creator": (
        "AI film production tool with script-to-film batch workflow. Public README describes a production chain from script to characters, scenes, director decisions, "
        "shot/storyboard planning, and final video. AGPL/Electron/runtime surface keeps it pattern-only."
    ),
    "jncchds/abook": (
        "Agentic book-writing workspace. Public README describes seven agents across Story Bible, Characters, Plot Threads, Chapter Outlines, Writer, Editor, and Continuity Checker; "
        "RAG context retrieval, full synopsis spine, anti-repetition prompt rules, token stats, and export surfaces. Docker/MCP/runtime surface keeps it pattern-only."
    ),
    "dorakingx/novelpilot": (
        "NovelPilot is a Gemma-powered AI writing agent with a nine-agent pipeline from Premise Architect through Publisher Agent. Public README describes typed JSON outputs, "
        "Story Bible, Foreshadowing Tracker, Continuity Detective, completed novel reader, Markdown export, and optional live provider mode. Treat provider/runtime surfaces as pattern-only."
    ),
    "heaversm/ralph-storywriter": (
        "Ralph Story Writer is a Claude Code loop for fiction and dissertation projects. Public README describes fresh context per iteration, no memory fatigue, prd.json chapter manifests, "
        "STORY_BIBLE.md, progress.txt, Plan -> Write -> Review -> Revise skill ensemble, chapter save/update loops, and shell scripts. Treat scripts/provider auth as non-executable pattern evidence."
    ),
    "prompt-and-circumstance/storymode": (
        "SillyTavern story-mode extension. Public README describes 43 genres, story style and author style controls, mix-and-match story settings, narrative arc controls, "
        "and scenario blueprint schema. Browser/extension/runtime surface keeps it pattern-only."
    ),
    "brianlmerritt/explore_writing": (
        "Writing experiment harness. Public README describes prompt recipes, sampling/temperature grids, write/review/top_writing phases, rubric review, "
        "append-only resumable TSV logs, and parameter comparison loops."
    ),
    "forsonny/novel-master-ai": (
        "Novel Master AI workflow. Public README describes NRD-driven task tree from arcs to chapters to scenes, tagged workflow steps, revision passes, "
        "continuity reporting, CLI/MCP surfaces, and structured manuscript planning. Runtime/MCP surface keeps it pattern-only."
    ),
    "arian-emami/noveldreamer": (
        "Research novel generator using style/thematic retrieval. Public README describes RAG from Wikiquote samples, Hero's Journey and Freytag structure, "
        "and act/chapter pre-planning before generation."
    ),
    "lingfengqaq/webnovel-writer": (
        "Chinese long-form webnovel writing system for Claude Code with eight skill commands, Story System contracts as the single source of truth, "
        "accepted CHAPTER_COMMIT write-back, state/index/summary/memory/vector projections, projection logs, read-only dashboard, doctor/preflight checks, "
        "context/reviewer/data/deconstruction agents, RAG, anti-AI final checks, and review dimensions for consistency, OOC, pacing, and reader retention."
    ),
    "zy-zmc/tianming-novel-ai-writer": (
        "AI novel writing system centered on 15-dimensional fact snapshots, 12 change declaration classes, six generation gates, closed-loop chapter writing, "
        "long-distance recall, unified validation, local semantic search, and per-chapter state write-back for thousands of chapters."
    ),
    "lujih/webnovel-writer-opencode": (
        "OpenCode adaptation of webnovel-writer with long-form serialized writing flow, context preparation, review, anti-AI polish, fact extraction, "
        "and accepted chapter commit projection patterns. Treat as sibling pattern evidence, not a separate runtime dependency."
    ),
    "starmagic/webnovel-writer-hermes": (
        "Hermes Agent adaptation of the webnovel writer flow with story contracts, layered RAG, three-tier memory, foreshadowing DebtTracker, "
        "dynamic context-budget reservation, entity-graph RAG, time-sliced character-state queries, six-dimensional parallel review, "
        "context/reviewer/data/deconstruction agents, health self-check, graceful fallback, and read-only dashboard."
    ),
    "hz-kmno/web-novel-writing-guidance-skill": (
        "Web novel writing guidance skill that turns ideas into story-engine design, chapter blueprints, key-information files, chapter task cards, "
        "Draft A/B/C revision ladder, de-AI final pass, continuity records, next-chapter handoff, independent character goals, information boundaries, "
        "mistaken beliefs, and foreshadowing tracking."
    ),
    "jinmawang/claude-novel-writeflow": (
        "Claude Code novel workflow plugin with style definition before outline, four-way brainstorm, structured chapter outlines, Writer Agent, "
        "Style Reviewer, Continuity Reviewer, ±2 chapter context window, bounded review loops, context extraction for existing chapters, "
        "plain-text outline/context/chapter storage, and safe single-chapter rewrites."
    ),
    "ducktrado/novel": (
        "Local-first AI novel writing pipeline with memory/story_bible.yaml, characters.yaml, foreshadowing.yaml, style_bank.jsonl, "
        "events/timeline/chapter_summaries ledgers, relationship graph, consistency checks, memory update after each chapter, "
        "chapter reset boundaries, desktop memory workbench, and LoRA style adapter posture."
    ),
    "makieali/longform-ai": (
        "LongForm AI long-form generation engine for novels, docs, courses, and screenplays with provider roles, interactive sessions, book outline and chapter schemas, "
        "chapter status, edit-cycle records, automatic retry/expand/edit/rewrite/continuity loop, rolling summary, character state, timeline events, world state, "
        "relevant-passage retrieval, token-budget context trimming, cost tracking, and session restore."
    ),
    "guchendesigndog/gc-writer-assistant": (
        "Chinese web-novel local writing assistant for chapter management, outline extraction, AI polishing, continuation, themed workspaces, and user-facing AI interface setup. "
        "Pattern-only value is lightweight chapter/outline workspace integration rather than runtime scripts."
    ),
    "lars76/story-evaluation-llm": (
        "Story evaluation dataset and benchmark for LLM short-story quality. Public README describes q1-q15 quality metrics, length score, overall score, "
        "character consistency, reader interest, plot resolution, ranked weaknesses, and averaging across evaluator models."
    ),
    "lechmazur/writing": (
        "LLM creative story-writing benchmark with constrained creative briefs, head-to-head matched story comparisons, paired judgments, visible story-order swaps, "
        "evaluator agreement, pairwise margins, and comparison-graph ranking rather than single absolute scores."
    ),
    "lechmazur/writing_styles": (
        "Flash-fiction style and diversity benchmark. Public README describes style fingerprints and axes for voice/diction, rhythm/syntax, POV/discourse, "
        "structure/pacing, tone, imagery, dialogue, experimentation, closure, and content choices."
    ),
    "anirudhlakkaraju/cs4_benchmark": (
        "CS4 benchmark for evaluating LLM creativity in story generation under varying constraint specificity. Public README describes prompt constraints, "
        "constraint satisfaction, narrative coherence, perplexity, and creativity under increasingly specific briefs."
    ),
    "theltn/aicreativityjudge": (
        "Creative-writing evaluator using a five-dimension rubric: lexical richness, syntactic complexity, novelty, imagery, and narrative dynamics. "
        "Pattern-only value is rubric decomposition; model training/runtime UI are not imported."
    ),
    "clchinkc/story-bench": (
        "Story Theory Benchmark using objective story-theory frameworks, programmatic checks, LLM judge ensemble, beat interpolation, beat revision, "
        "multi-beat synthesis, constrained continuation, theory conversion, and weighted narrative criteria."
    ),
    "thu-keg/storywriter": (
        "Multi-agent long-story generation framework with Outline Agent, Planning Agent, and Writing Agent. Public README describes event-based outlines, "
        "chapter-wise plans, dynamic compression of story history, discourse coherence, narrative complexity, and human/automatic evaluation."
    ),
    "zju-llms/openstory": (
        "OpenStory multi-agent story-world simulation framework. Public README describes dynamic agent addition/removal, character behavior, social interaction, "
        "story evolution, and Dream of the Red Chamber simulation. Runtime requires provider/config setup and remains out of scope."
    ),
    "zygmuntz/goodbooks-10k": (
        "Goodbooks-10k book dataset with ten thousand popular books, six million ratings, to-read signals, metadata, and user tags/shelves/genres. "
        "Pattern-only value is aggregate reader preference modeling, market-adjacent rating signals, and shelf/tag expectation maps; dataset import is not performed."
    ),
    "mengtingwan/goodreads": (
        "Goodreads dataset code samples for academic-use review and interaction data, including recommendation behavior chains, review statistics, "
        "fine-grained spoiler detection, and exploration notebooks. Pattern-only value is review-signal and spoiler-aware feedback design; no dataset download is performed."
    ),
    "maria-antoniak/goodreads-scraper": (
        "Goodreads classics scraper project and computational reader-review study. Public README describes review/metadata fields, rating distribution, top shelves, lists, "
        "full review collection, Selenium/browser dependency, and a 2025 unmaintained/broken warning. Absorb only review metadata schema and safety warnings."
    ),
    "ckokoski/authorclaw": (
        "AuthorClaw autonomous author agent with pipeline planning, deep revision, AI beta readers, market research, comp titles, reader intelligence, book launch copy, "
        "reader archetype feedback, tension/pacing/want-to-continue/confusion/favorite-moment/stumble-point reports, and review-cluster safety rails. Runtime is not imported."
    ),
    "f5alcon/the-novelists-atelier": (
        "The Novelist's Atelier local-browser writing assistant with series/book/chapter context, developmental editing, tension and engagement prompts, reader curiosity tracker, "
        "chapter hook and cliffhanger audits, style DNA, smart context auto-toggling, local text analysis, token breakdown, local storage, backups, and security notes."
    ),
    "leehong0704/ai-novel": (
        "AI Novel Tool is a Chinese desktop webnovel assistant. Public README describes human-machine co-creation, outline/body generation, "
        "AI polishing, precise modification, local memory/history, and a Windows packaged zip. Pattern-only value is inline author-controlled revision "
        "with explicit diff review; packaged binaries and runtime are not used."
    ),
    "wynnforthework/ai-novel-weaver": (
        "AI Novel Weaver is a web-based long-novel platform. Public README describes an orchestrator-driven generation/validation/improvement loop, "
        "hierarchical planning from volumes and arcs to chapters, memory weave, one-click book decomposition, local deployment, and prompt/agent coordination. "
        "Pattern-only value is hierarchical orchestration and book-decomposition gates; local server/runtime are not launched."
    ),
    "fuchen2020/batchscribe": (
        "BatchScribe is a Windows-only AI novel generator under AGPL-3.0. Public README describes batch generation, continuation, story type/style controls, "
        "prompt configuration, memory-like context, chapter generation, and user review. Pattern-only value is batch continuation queue governance; Windows runtime is not used."
    ),
    "xy9144/flutter-novel-main": (
        "Flutter Novel Generator is a cross-platform AI novel wrapper inspired by a public 52pojie thread. Public README describes outline -> volume plan -> range plan -> "
        "chapter plan -> chapter text, automatic progress-based continuation, progress tracking, prompt revisions after homogeneous multi-chapter output, and local Ollama interface notes. "
        "Pattern-only value is progress queue and homogeneity prompt variation; forum source and app runtime are not imported."
    ),
    "duoyang666/ai_novel": (
        "duoyang666/ai_novel is a Chinese AI writing and knowledge-base app with public README markers for local software downloads, auto-upgrade zip, Feishu tutorials, "
        "webnovel features such as outline, chapter generation, continuation, batch writing, and pleasure-point/rhythm support. Pattern-only value is local author-data boundary and update-surface risk review; downloads and auto-updaters are not executed."
    ),
    "deng-m1/maliangainovalwriter": (
        "Maliang AI writer is a Flutter/Spring Boot AI novel platform. Public README describes hierarchical work management, txt import with chapter-outline generation, "
        "system and user prompt presets, template and preset management, private user API keys, public model pool, model validation, LLM observability, token/cost traces, and knowledge-extraction review. "
        "Pattern-only value is prompt preset governance, imported-manuscript migration, and provider trace boundaries; Docker/runtime/admin services are not launched."
    ),
    "ponysb/91writing": (
        "91Writing is a Vue-based Chinese AI novel writing tool. Public README describes user-configured APIs, local data posture, smart continuation with custom direction and word-count range, "
        "content preview, prompt-template categories, variable system, template import, usage statistics, token cost management, type configuration, and selective import/export. "
        "Pattern-only value is continuation direction contracts, prompt-variable libraries, and local data import/export boundaries; front-end runtime and Docker assets are not executed."
    ),
    "hezhengtao/mortalainovel-aiwritingsystem-ai-": (
        "MortalWrite is a local desktop AI writing assistant. Public README describes local workspace selection, book/volume/chapter/section management, continuation, polishing, style imitation, "
        "character cards, AI relationship graph generation, inspiration brainstorming, and a book-decomposition knowledge base that analyzes imported snippets into writing DNA. "
        "Pattern-only value is style-DNA reference-library abstraction and local author-data boundaries; exe/package/runtime paths are not executed."
    ),
    "linnnn89/novel-agent-workbench": (
        "Novel Agent Workbench is an AGPL local AI novel workbench. Public README describes local-first project storage, Memory Bank, world/character settings, draft generation, AI review, "
        "revision requests, rewrite candidates, candidate comparison, confirmed-chapter promotion, provider gates, audit metadata, mock provider, and Windows build scripts. "
        "Pattern-only value is draft/review/rewrite/confirmed state separation and explicit provider-call boundaries; AGPL code and scripts are not imported or executed."
    ),
    "qnbs/storycraft-studio": (
        "StoryCraft Studio is an MIT offline-first writing studio. Public README describes IndexedDB local storage, PWA/desktop modes, story planning, character/world building, revision snapshots, "
        "template remixing, privacy-first local AI/WebLLM/ONNX/Transformers fallbacks, encrypted API keys, and cross-project search that stores lightweight metadata rather than manuscript plaintext. "
        "Pattern-only value is privacy-preserving local indexing and offline-first prompt/context boundaries; Node/Tauri/PWA/runtime assets are not installed or launched."
    ),
    "arupmaity1/book-writer-mcp": (
        "Book Writer MCP for AI-assisted manuscript work. Public README describes story bible, style guide, continuity checker, chapter create/read/update/list/reorder, "
        "manuscript-wide statistics, HTML preview, clean Markdown and formatted DOCX export with title page, table of contents, page numbers, fonts/spacing, cover design, and KDP cover specs. "
        "Absorb delivery packaging and export-audit patterns only; MCP runtime is not started."
    ),
    "inkle/ink": (
        "Inkle ink is an MIT interactive narrative scripting language. Public README describes highly branching stories, choices, knots, stitches, diverts, variables, and weave structure. "
        "Absorb branch graph and passage navigation patterns only; compiler/editor/runtime is not executed."
    ),
    "yarnspinnertool/yarnspinner": (
        "Yarn Spinner is an MIT dialogue tool. Public README describes interactive conversations with dialogue lines, player options, commands, variables, and node-based scripts. "
        "Absorb dialogue state machine and choice consequence patterns only; engine packages are not installed."
    ),
    "klembot/twinejs": (
        "Twine is a GPL-3.0 tool for interactive nonlinear stories. Public metadata describes passages, links, variables, story formats, and nonlinear story navigation. "
        "Absorb passage-link navigation and branch-map patterns only; app/runtime code is not imported."
    ),
    "dfabulich/choicescript": (
        "ChoiceScript is a language for multiple-choice games. Public metadata describes choices, stats, variables, achievements, and consequence-driven story state. "
        "Absorb choice-stat consequence gates only; no runtime code or license-unclear files are imported."
    ),
    "blingenf/copydetect": (
        "Copydetect is an MIT code plagiarism detection tool based on winnowing document fingerprinting and copied-slice reports. "
        "Absorb fingerprint overlap and source-copy review patterns only; no package install or detector runtime is executed."
    ),
    "ropensci/textreuse": (
        "textreuse detects text reuse and document similarity, with public README markers for pairwise comparisons, MinHashing, locality-sensitive hashing, and text alignment. "
        "Absorb reuse-alignment and near-duplicate gates only; R package runtime and example corpora are not executed."
    ),
    "rapidfuzz/rapidfuzz": (
        "RapidFuzz is an MIT fuzzy string matching library using Levenshtein distance and string metrics. "
        "Absorb fuzzy phrase similarity threshold patterns only; native/package runtime is not imported."
    ),
    "google/diff-match-patch": (
        "Diff Match Patch is an Apache-2.0 diff, match, and patch library with semantic cleanup and tests. "
        "Absorb copied-span diff review patterns only; source ports are not imported."
    ),
    "agranya99/moss-winnowing-seqmatcher": (
        "MOSS-winnowing-seqMatcher is an MIT educational plagiarism checker using winnowing and SequenceMatcher. "
        "Absorb fingerprint and fuzzy phrase review patterns only; scripts are not executed."
    ),
    "chenghaomou/text-dedup": (
        "text-dedup is an Apache-2.0 all-in-one text deduplication project. "
        "Absorb exact, MinHash, SimHash, and semantic dedup gate patterns only; package/runtime code is not installed."
    ),
    "google-research/deduplicate-text-datasets": (
        "Deduplicating Training Data Makes Language Models Better releases ExactSubstr deduplication and NearDup cluster artifacts for dataset cleaning. "
        "Absorb corpus leakage and repeated-sequence review gates only; Rust/Python scripts and datasets are not executed or downloaded."
    ),
    "ekzhu/datasketch": (
        "datasketch provides MinHash, MinHash LSH, LSH Forest, Weighted MinHash, HyperLogLog, and related probabilistic structures. "
        "Absorb Jaccard/LSH near-duplicate threshold patterns only; package runtime is not imported."
    ),
    "seomoz/simhash-py": (
        "simhash-py identifies near-duplicate documents by comparing similar hashes and Hamming distance. "
        "Absorb SimHash/Hamming review gates only; C++ extension/runtime is not built."
    ),
    "1e0ng/simhash": (
        "simhash is a Python implementation of the SimHash algorithm for text similarity. "
        "Absorb lightweight SimHash near-duplicate review patterns only; package runtime is not imported."
    ),
    "minishlab/semhash": (
        "SemHash is a MIT fast multimodal semantic deduplication and filtering project. "
        "Absorb semantic duplicate clustering and filtering gates only; models/packages are not installed."
    ),
    "ukplab/sentence-transformers": (
        "Sentence Transformers provides embeddings, retrieval, and reranking for semantic similarity. "
        "Absorb embedding-similarity independence review gates only; models and runtime dependencies are not downloaded."
    ),
    "huggingface/sentence-transformers": (
        "Sentence Transformers provides embeddings, retrieval, and reranking for semantic similarity. "
        "Absorb embedding-similarity independence review gates only; models and runtime dependencies are not downloaded."
    ),
    "facebookresearch/faiss": (
        "Faiss is a MIT library for efficient similarity search and clustering of dense vectors. "
        "Absorb vector-nearest-neighbor review and threshold patterns only; native/GPU runtime is not imported."
    ),
    "facebookresearch/semdedup": (
        "SemDeDup identifies and removes semantic duplicates in web-scale datasets using embedding clusters. "
        "Absorb semantic duplicate cluster gates and corpus leakage warnings only; archived code, conda env, and data pipeline are not executed."
    ),
    "booknlp/booknlp": (
        "BookNLP is an MIT NLP pipeline for book-length documents. Public README and metadata describe character coreference, "
        "quote attribution, entity tokens, speaker/mention outputs, and book-oriented processing. Absorb character-quote attribution maps only; runtime models are not installed."
    ),
    "textstat/textstat": (
        "Textstat is an MIT Python library for readability statistics over text, paragraphs, and sentences. "
        "Absorb readability and sentence/paragraph pacing metric gates only; package runtime is not imported."
    ),
    "vale-cli/vale": (
        "Vale is a prose linter with configurable style rules and syntax-aware checks for markup such as Markdown. "
        "Absorb project-local house-style rule gates and diagnostic reporting only; the CLI is not installed or executed."
    ),
    "textlint/textlint": (
        "Textlint is a pluggable natural language linter for Markdown and text with configurable rule packages. "
        "Absorb manuscript lint profile, exception, and rule-pack layering patterns only; Node packages are not installed."
    ),
    "amperser/proselint": (
        "Proselint checks prose for style issues such as cliches, jargon, redundancy, and passive phrasing. "
        "Absorb copyedit warning categories as optional review diagnostics, not automatic rewrites."
    ),
    "automattic/harper": (
        "Harper is an offline grammar checker and language server for developers writing prose. "
        "Absorb local-first grammar/spelling review and dialect exception boundaries only; browser/editor integrations are not installed."
    ),
    "languagetool-org/languagetool": (
        "LanguageTool is a multilingual grammar, style, and spell checker with server/client surfaces. "
        "Absorb grammar/spelling/copyedit gate taxonomy only; no server, extension, or external checking service is launched."
    ),
    "btford/write-good": (
        "Write-good is a MIT prose style checker that flags passive voice, weasel words, adverbs, cliches, and hard-to-read text. "
        "Absorb lightweight prose-warning categories and author-review triage patterns only; package runtime is not imported."
    ),
    "fxsjy/jieba": (
        "Jieba is a MIT Chinese word segmentation toolkit with dictionary-based segmentation and keyword extraction. "
        "Absorb custom-dictionary segmentation and keyword gates for Chinese manuscript analysis only; package runtime is not imported."
    ),
    "messense/jieba-rs": (
        "Jieba-rs is a MIT Rust implementation of Jieba-style Chinese tokenization. "
        "Absorb tokenizer runtime-boundary and deterministic segmentation ideas only; native/runtime code is not built."
    ),
    "hankcs/hanlp": (
        "HanLP is an Apache-2.0 multilingual NLP toolkit with Chinese tokenization, NER, dependency parsing, and semantic analysis surfaces. "
        "Absorb entity/alias consistency and Chinese text analysis gates only; models are not downloaded."
    ),
    "hit-scir/ltp": (
        "LTP is a Chinese NLP toolkit from HIT-SCIR with segmentation, POS, NER, dependency, and semantic role capabilities. "
        "Absorb Chinese entity/role extraction review patterns only; license was not confirmed via raw LICENSE in this static pass."
    ),
    "byvoid/opencc": (
        "OpenCC converts between Simplified and Traditional Chinese variants. "
        "Absorb explicit text-normalization gates for source/deck/manuscript consistency only; conversion runtime is not installed."
    ),
    "shibing624/pycorrector": (
        "PyCorrector is an Apache-2.0 Chinese text error correction toolkit with confusion-set and model-based correction modes. "
        "Absorb Chinese typo/confusion review queues only; models and package runtime are not imported."
    ),
    "aerkalov/ebooklib": (
        "EbookLib handles EPUB reading/writing with OPF metadata, spine, and table-of-contents surfaces. "
        "Absorb EPUB source-import manifest and chapter-spine mapping patterns only; AGPL runtime code is not imported."
    ),
    "w3c/epubcheck": (
        "EPUBCheck is the W3C EPUB conformance checker for EPUB publications with package, OPF, manifest, spine, navigation, "
        "media-type, and validation-report surfaces. Absorb EPUB structure validation gates only; Java/library/runtime code is not executed."
    ),
    "daisy/ace": (
        "Ace by DAISY is an EPUB accessibility checking tool. Public README/package materials describe accessibility reports for EPUB publications. "
        "Absorb ebook accessibility audit gates only; npm/runtime checks are not launched."
    ),
    "standardebooks/tools": (
        "Standard Ebooks tools support producing ebooks with setup, text processing, build, metadata, titlepage, endnotes, colophon, and release checks. "
        "Absorb front/back matter and publication metadata gates only; GPL tools and command-line workflows are not installed."
    ),
    "sigil-ebook/sigil": (
        "Sigil is an open-source EPUB editor for EPUB 2 and EPUB 3 with book browser, manifest, spine, metadata, and table-of-contents editing surfaces. "
        "Absorb TOC/navigation consistency review patterns only; Qt/native application code is not built or launched."
    ),
    "w3c/epub-tests": (
        "W3C EPUB tests validate implementability of EPUB 3 specifications with focused EPUB fixtures and documentation. "
        "Absorb EPUB structure and navigation regression fixture patterns only; test EPUBs and generators are not imported."
    ),
    "daisy/epub-accessibility-tests": (
        "DAISY EPUB accessibility tests provide EPUB fixtures for reading-system accessibility behavior. "
        "Absorb accessibility fixture and reader-navigation audit patterns only; test books are not downloaded or executed."
    ),
    "john-paul-ruf/novel-engine": (
        "Novel Engine is an AGPL desktop book-building system with a human-author creative boundary and seven specialized AI editorial agents for pitch, scaffold, draft, analysis, revision, copy-edit, and export. "
        "Absorb agentic editorial pipeline gates only; Electron/Claude/Pandoc runtimes are not installed or launched."
    ),
    "thomashoussin/claude-book": (
        "Claude Book is a MIT Claude Code multi-agent framework for novel writing with reusable skills, agents, permanent bible files, transient per-chapter state, timeline history, and chapter archives. "
        "Absorb role handoff and chapter-state archive patterns only; no Claude Code agents or generation providers are run."
    ),
    "doktordavejoos/manuscript": (
        "Manuscript is a local-first desktop app for novelists with structural analysis, pacing visualization, prose refinement, AI-assisted review, local SQLite storage, acts, beats, and chapter models. "
        "Absorb offline structural/pacing workbench patterns only; app code, AI providers, queues, and dependencies are not executed."
    ),
    "geobond13/fiction-forge": (
        "Fiction Forge is a MIT prose pattern scanner and MCP context-server toolkit for AI-assisted novels, detecting AI writing fingerprints, voice drift, severity clusters, story-bible access, and publishing outputs. "
        "Absorb prose fingerprint cluster gates only; MCP server, scanners, publisher, and image-generation tools are not run."
    ),
    "shenminglinyi/plotpilot": (
        "PlotPilot is a narrative-engine kernel for long-form AI creation with persistent memory, knowledge graph, DAG workflows, and creator review surfaces. "
        "Absorb section metadata and narrative traceability patterns only; services, models, and workflows are not launched."
    ),
    "peter88213/novelibre": (
        "novelibre is a GPL novel organizer that keeps section metadata associated with manuscript chapters, relates characters, locations, items, plot lines, and plot points, and supports large-novel planning. "
        "Absorb section metadata traceability patterns only; LibreOffice/OpenOffice add-ons and runtime files are not executed."
    ),
    "wenzizzheng/story-spec": (
        "StorySpec is a MIT Chinese long-form fiction co-creation workbench. Public README describes preserving author ideas, offering consequence-bearing candidates, preview/confirm/apply flows, candidate-not-canon status, rollback, story specs, plans, drafts, tracking files, and agent guides. "
        "Absorb author-candidate canon confirmation gates only; npm package, app server, workers, and agent integrations are not installed or run."
    ),
    "kkkenchow/ai-novel-writer": (
        "AI Novel Writer is a MIT Chinese full-chain local RAG novel tool. Public README describes local ChromaDB memory, staged world/character/outline/chapter workflow, six-stage progressive pacing, four-level spoiler filtering, future-chapter range validation, global find/replace, consistency checks, Graphviz relationship graphs, and Markdown export. "
        "Absorb progressive spoiler context windows, relationship graph, and propagation gates only; Streamlit/API/vector runtimes and providers are not launched."
    ),
    "papysans/morpheus": (
        "Morpheus is a Chinese multi-agent long-form writing workbench. Public README describes project setup, batch generation, chapter workbench rewrites, L1/L2/L3 memory, open threads, context packs, knowledge graph, trace replay, dashboard metrics, review/consistency subsystems, and import/export. "
        "Absorb trace replay and revision workspace gates only; backend, frontend, LanceDB, providers, and services are not started."
    ),
    "jingtai123/novel-control-station-skill": (
        "Novel Control Station is a MIT Chinese long-form fiction control skill. Public README describes opening interviews, complete outlines and character files, multi-line structure control, document-driven truth layer, chapter control cards, dynamic state write-back after each chapter, graph recall views, title/hook control, style module scheduling, anti-AI revision, and marathon continuation scripts. "
        "Absorb chapter-control-card and write-back gates only; skill runtime and marathon scripts are not executed."
    ),
    "xindoo/sumeru": (
        "Sumeru Writing is a Chinese webnovel AI Agent skill collection. Public README describes topic selection, outline design, chapter writing, continuation/rewrite, batch parallel creation, logic review, polishing, final validation, stage skipping, interrupted resume, and .sumeru intermediate state. "
        "Absorb Chinese webnovel control-card, batch-review, and resume patterns only; skill pack and install paths are not imported."
    ),
    "ai-practical-lab/ai-novel": (
        "AI Novel Assistant is a MIT AI-driven novel creation assistant. Public README describes streaming writing, smart context from setting collections, outlines and previous chapters, structured world/character/outline/chapter management, immersive editor, and local data management. "
        "Absorb structured Chinese novel workflow and context-window lessons only; package scripts, frontend/backend, and provider surfaces are not run."
    ),
    "xzzkany/storyforge": (
        "StoryForge is a Chinese long-form novel production pipeline. Public README and package metadata describe BookRun, Blueprint, Judge/Repair, checkpoint resume, Story Memory, export audit reports, real LLM smoke gates, and core verification workflows. "
        "Absorb BookRun audit-trail and provider smoke-budget gates only; pnpm, uv, scripts, Docker, workflows, providers, and app runtimes are not executed."
    ),
    "spiritlhls/novelbuilder": (
        "NovelBuilder is an AI long-form fiction workbench with Vue UI, Go API gateway, Python sidecar, task queues, LLM profile routing, optional graph/vector memory via Neo4j/Qdrant, and deployment profiles from SQLite-only to Docker stacks. "
        "Absorb sidecar memory-profile boundary and provider admission gates only; GPL code, Docker profiles, sidecars, databases, queues, and providers are not launched."
    ),
    "qiuxinyuan321/novel-writer-master": (
        "Novel Writer Master is an AI-assisted novel writing tool with an anti-AI-rate engine, layered outline, checkpoint constraints, narrative milestones, Story Bible truth-source framing, and provider-backed writing surfaces. "
        "Absorb outline checkpoint and anti-slop review gates only; Streamlit/FastAPI/provider runtimes, vector stores, and package dependencies are not executed."
    ),
    "byk3y/no-slop": (
        "no-slop is a MIT prose linter skill/rulepack that flags AI writing patterns using banned vocabulary, copula substitutions, marketing phrasing, vague attribution, and structural tells. "
        "Absorb prose rulepack triage gates only; no rule files are copied wholesale and no external skill runtime is installed."
    ),
    "nntrivi2001/wordsmith": (
        "Wordsmith is a GPL-3.0 long-form webnovel system for Claude Code with eight writing skills, seven agents, local RAG, dashboard/resume/learn workflows, and Vietnamese writing style rules. "
        "Absorb language-localization style-profile and skill workflow boundary patterns only; GPL code, RAG index, dashboard, agents, and plugin paths are not imported."
    ),
    "zy-zmc/tianming-skill": (
        "TianMing Skill is a CC BY-NC-SA long-form novel collaboration skill split from a monolithic prompt into 30+ protocol files with progressive disclosure, intent-based command routing, codex/protocol/knowledge-base layers, and consistency enforcement. "
        "Absorb progressive-disclosure protocol gates and localization/style profile boundaries only; prompt files are not copied and the skill is not installed or treated as runtime authority."
    ),
    "para-droid-ai/novelizeai": (
        "Novelize AI is a web application for turning a seed idea into a multi-chapter novel through project modifiers, AI-driven initial planning, chapter plans, prose, self-review, revisions, dashboard progress, live timing logs, and full project-state export. "
        "Absorb project-blueprint modifier and timing/export audit gates only; Gemini/provider surfaces, browser local storage, example outputs, and app runtime are not imported or executed."
    ),
    "moosphan/novel-orchestrator": (
        "Novel Orchestrator is a PolyForm Noncommercial long-form writing engine with story/*.md assets, YAML frontmatter, a Canon layer, portable Agent Skill runtime, workflow orchestration, SQLite state, artifacts, checkpoints, inspect/audit/export commands, and canon-sync. "
        "Absorb portable canon skill-runtime and artifact trace gates only; Python package, model scanning, providers, and CLI runtime are not installed or run."
    ),
    "kirinonakar/novelgen": (
        "NovelGen AI is a MIT Tauri/Rust desktop story generator with seed-to-plot automation, multilingual generation, staged long-outline planning for 13+ chapters, sliding-window chapter context, CJK-aware token counting, interrupted resume, batch jobs, and chapter-range refinement. "
        "Absorb staged outline chunk windows and chapter-range revision gates only; Tauri, Rust, Node, LM Studio, Gemini, Credential Manager, and app binaries are not launched."
    ),
    "abrahamp47/storyforge-wiki": (
        "Storyforge Wiki is a MIT Claude Code-first story bible and worldbuilding wiki for novels with raw document ingestion, wiki health checks, canon lint, continuity queries, relationship graphs, timeline contradiction detection, and unresolved setup/payoff review. "
        "Absorb wiki canon-graph lint and continuity-query gates only; slash commands, Quartz publishing, and Claude Code runtime are not run."
    ),
    "third-order-labs/longform-plugin": (
        "Longform is a MIT Claude/Cowork writing workflow plugin for novel-length fiction using a Plan -> Draft -> Log -> Verify -> Repeat loop, living documents, scene logs, continuity records, glossary, thread tracking, foreshadowing checklists, review, and wrap commands. "
        "Absorb living-document freshness and plan-draft-log-verify gates only; plugin installation and Claude/Cowork runtime are not used."
    ),
    "hannasdev/mcp-writing": (
        "mcp-writing is an AGPL-3.0 MCP service for long-form fiction that builds a metadata-first scene index, SQLite-canonical structural and relationship metadata, compatibility sidecars, targeted scene reading, safe scene revision with human confirmation, git history, review bundles, and Scrivener extraction. "
        "Absorb scene-index and safe-revision boundary patterns only; MCP server, npm package, Docker, Node runtime, databases, and sync directories are not started or read."
    ),
    "xbraindance/creative-writing-skill": (
        "Creative Writing with Verbalized Sampling is a MIT creative-writing skill that uses verbalized sampling to avoid mode collapse, generate probability-scored diverse ideas/outlines/drafts, and auto-file drafts, characters, settings, and critique outputs into a persistent writer wiki. "
        "Absorb diversity-sampling and writer-wiki filing gates only; the skill is not installed and prompt files are not copied into runtime context."
    ),
    "tiny-flowlab/novel-studio-copilot-cli": (
        "Novel Studio for Copilot CLI is a MIT multi-agent novel creation system. Public README/AGENTS.md describe 13 specialized agents, AGENTS.md auto-loading, "
        "@agent invocation, planning, writing, editing, continuity, and quality-control orchestration. Absorb agentic editorial pipeline and craft-role routing gates only; "
        "Copilot CLI, agents, hooks, prompts, and runtime command files are not installed, invoked, or copied into runtime context."
    ),
    "guerra2fernando/libriscribe": (
        "LibriScribe is a multi-agent book writing assistant. Public README describes multi-agent orchestration, specialized agent roles, a project manager, outliner, writer/editor roles, worldbuilding, draft generation, "
        "interactive editing, prompt files, and execution-cost logging. Absorb craft-role handoff, budget visibility, and editable-review-loop patterns only; provider calls, "
        "agent prompts, CLI runtime, and generated sample content are not imported."
    ),
    "muckelverk/pulpgen": (
        "pulpgen is a MIT AI novel drafting agent. Public README and project files describe idea-to-outline, chapter writing, interactive editing, XML state files, "
        "project folders, final.html manuscript output, export format boundaries, and derived manuscript artifacts. Absorb outline/state-file and manuscript assembly gates only; Gemini/provider calls, Python runtime, "
        "dependencies, and generated manuscript examples are not executed or imported."
    ),
    "bhed/sentiers-open-source": (
        "Sentiers is a MIT Claude Code-based agentic novel-writing system centered on author agency. Public README describes interactive branch choices, author-selected "
        "narrative paths, choice consequences, agent quality support, and state snapshots for returning to earlier branches. Absorb author-choice branch graph, consequence, and snapshot gates only; "
        "Claude Code commands, derived Claude Book code, prompts, and runtime agents are not launched or copied."
    ),
    "rhavekost/author-toolkit": (
        "Author Toolkit is a Claude Code writing-skill plugin for fiction and narrative authors. Public README describes a fiction workshop with editorial personas, "
        "agent roles such as Character Consultant and Continuity Tracker, voice fingerprint consistency, motivation and arc review, timeline, world facts, internal consistency, "
        "and genre-specific worldbuilding checks. Absorb editorial-persona and continuity-gate patterns only; plugin installation examples and skill prompts are not imported."
    ),
    "mike-cramblett/novel-novel-generator": (
        "Novel Novel Generator is a whole-novel pipeline with IP intake, Story Bible generation, Stylistic Compression Induction for character voice fingerprints, "
        "chapter-by-chapter outline planning, drafting from prior-chapter context, continuity editor audits, rolling summaries, repeated phrases and anti-repetition rules, "
        "state JSON, and PDF manuscript export. Absorb voice-fingerprint, rolling-summary, anti-repetition, and export-audit patterns only; Node runtime and provider calls are not run."
    ),
    "denmurray10/story-timeline-builder": (
        "Story Timeline Builder is a fiction-author digital story bible for complex multi-book series. Public README describes chronological events versus narrative sequence, "
        "dynamic relationship network mapping, character arcs, worldbuilding rules, continuity errors, timeline management, temporal context, and AI continuity-engine support. "
        "Absorb timeline/relationship-network and temporal-canon context gates only; Django app, hosted service, database, and provider surfaces are not launched."
    ),
    "jwynia/agent-skills": (
        "Agent Skills Collection is a large reusable skills catalog with a creative/narrative fiction and story skills category. Public README/AGENTS.md describe browsing skills by category, "
        "npx installation examples, context-network source-of-truth workflow, and documentation-first progress checks. Keep it index-only as a discovery catalog; do not install skills wholesale or import prompt bodies."
    ),
    "pdfminer/pdfminer.six": (
        "Pdfminer.six extracts text and layout information from PDF files. "
        "Absorb page/span/layout extraction gates for source deconstruction only; package runtime is not imported."
    ),
    "pymupdf/pymupdf": (
        "PyMuPDF exposes PDF page text blocks, coordinates, images, and metadata. "
        "Absorb layout-aware PDF import checks only; AGPL/commercial runtime is not imported."
    ),
    "ocrmypdf/ocrmypdf": (
        "OCRmyPDF adds OCR text layers to scanned PDFs and records OCR pipeline behavior. "
        "Absorb scanned-page OCR admission and confidence review patterns only; no OCR runtime or external binary is launched."
    ),
    "tesseract-ocr/tesseract": (
        "Tesseract is an OCR engine for image text recognition. "
        "Absorb language/confidence/page-image review gates only; native OCR runtime and language data are not downloaded."
    ),
    "unstructured-io/unstructured": (
        "Unstructured partitions PDFs, EPUBs, HTML, DOCX, and other documents into typed elements. "
        "Absorb document-element partition and chapter-heading detection patterns only; package runtime is not imported."
    ),
    "microsoft/markitdown": (
        "MarkItDown is a MIT Microsoft Python tool for converting files and Office documents to Markdown. "
        "Static README/root markers mention command-line use, optional dependencies, Dockerfile, PDF, EPUB, DOCX, OCR, and JSON-related surfaces. "
        "Absorb LLM-ready Markdown import-manifest and format-conversion gates only; package, optional converters, Docker, and provider integrations are not run."
    ),
    "docling-project/docling": (
        "Docling is a MIT document parser/converter for GenAI-ready documents. "
        "Static metadata/root markers show PDF/DOCX/HTML/PPTX/XLSX, markdown/json, OCR/layout/table extraction, Dockerfile, and agent prompt files. "
        "Absorb document partition, layout, and chapter-heading validation gates only; AGENTS/CLAUDE files, scripts, Docker, and runtime models are not imported."
    ),
    "opendatalab/mineru": (
        "MinerU transforms complex PDFs and Office docs into LLM-ready Markdown/JSON with layout-analysis, OCR, PDF parser/extractor, and document-analysis surfaces. "
        "Absorb PDF layout/OCR/import-manifest gates only; NOASSERTION license status, demos, Docker, model/runtime assets, and online services stay runtime-deferred."
    ),
    "datalab-to/marker": (
        "Marker converts PDF to Markdown and JSON and exposes chunk conversion, extraction app/server files, OCR, layout, and PDF/DOCX/EPUB marker surfaces. "
        "Absorb high-accuracy PDF-to-Markdown review and chunk boundary patterns only; GPL runtime, apps, servers, model dependencies, and commercial-service paths are not imported."
    ),
    "jgm/pandoc": (
        "Pandoc converts between document formats and preserves metadata boundaries across manuscript formats. "
        "Absorb format conversion provenance patterns only; GPL runtime is not installed."
    ),
    "lancopku/chinese-literature-ner-re-dataset": (
        "Chinese-Literature-NER-RE-Dataset is a discourse-level Chinese literary NER and relation-extraction dataset with entity, relation, and annotation-format docs. "
        "Absorb Chinese literary alias/entity/relation review vocabulary only; dataset files are not imported and no model training/runtime is run."
    ),
    "dbamman/litbank": (
        "LitBank is an annotated dataset of 100 works of fiction covering literary entities, literary events, and coreference in English literature. "
        "Absorb entity/event/coreference annotation gates only; dataset files and models are not imported."
    ),
    "eecrazy/constructingneeg_ijcai_2018": (
        "ConstructingNEEG studies narrative event evolutionary graphs for script event prediction. "
        "Absorb event-chain/evolution graph review patterns only; external data, PyTorch runtime, and old dependencies are not executed."
    ),
    "acolas1/eventnarrative": (
        "EventNarrative is an event-centric knowledge-graph-to-text dataset and resource. "
        "Absorb event graph linearization and provenance separation patterns only; dataset/runtime assets are not downloaded."
    ),
    "doug919/narrative_graph_emnlp2020": (
        "Narrative graph EMNLP 2020 models contextualized event embeddings for discourse relations. "
        "Absorb discourse/event relation evidence patterns only; trained models and Java/Python runtime are not executed."
    ),
    "mjockers/syuzhet": (
        "Syuzhet extracts sentiment and sentiment-based plot arcs from text. "
        "Absorb emotion-arc review and pacing-trajectory patterns only; R package runtime is not installed."
    ),
    "jon-chun/sentimentarcs_notebooks": (
        "SentimentArcs notebooks compare many sentiment models to analyze emotion in text over time. "
        "Absorb ensemble emotion-arc audit patterns only; notebooks and model dependencies are not executed."
    ),
    "sapienzanlp/xcore": (
        "xCoRe is an all-in-one cross-context coreference model for short, long, and multiple contexts. "
        "Absorb cross-context mention-cluster stability gates only; model weights and runtime are not downloaded."
    ),
    "anastasia-zhukova/xcoref": (
        "XCoref resolves cross-document entity, event, and abstract-concept coreference through staged sieves. "
        "Absorb cross-document entity/event identity review patterns only; pipeline runtime is not executed."
    ),
    "hzjken/character-network": (
        "Character-network analyzes relationships among novel characters with graph, entity-recognition, and sentiment techniques. "
        "Absorb character interaction network gates only; example corpus and notebooks are not executed."
    ),
    "devbret/character-interactions": (
        "Character-interactions extracts characters, infers relationships, and visualizes literary interaction networks. "
        "Absorb character relationship evidence and network review patterns only; web/D3 runtime is not launched."
    ),
    "computationalstylistics/stylo": (
        "Stylo is an R package for computational stylistics and authorship attribution with distance and classification style analyses. "
        "Absorb author fingerprint and function-word style gates only; GPL code and GUI/runtime are not imported."
    ),
    "fastdatascience/faststylometry": (
        "FastStylometry is a Python NLP library for fast stylometric authorship and style-similarity analysis. "
        "Absorb Burrows-Delta/style-distance review gates only; package runtime is not installed."
    ),
    "cophi-wue/pydelta": (
        "pydelta is an experimental Python implementation of Burrow's Delta for computational stylistics. "
        "Absorb author-style distance and source-voice overfit review vocabulary only; notebooks/package runtime are not executed."
    ),
    "hassaan-elahi/writing-styles-classification-using-stylometric-analysis": (
        "This stylometric analysis project classifies style shifts inside one document using sentence length, readability, vocabulary richness, and frequencies. "
        "Absorb style-change and overfit-regression gates only; examples and notebooks are not executed."
    ),
    "michaeleby1/stylometric-analysis-project-gutenberg": (
        "Project Gutenberg stylometric analysis builds numerical style metrics, cosine-similarity recommendations, and style clusters for books. "
        "Absorb book-level style similarity baselines only; Gutenberg scraping code and data are not run."
    ),
    "pan-webis-de/pan-code": (
        "PAN code contains shared-task baselines and evaluation code for authorship attribution, style change, and related text forensics tasks. "
        "Absorb attribution/evaluation-gate patterns only; task data and runtime baselines are not imported."
    ),
    "mullerpeter/authorstyle": (
        "Authorstyle handles PAN corpora and extracts stylometric features from text documents. "
        "Absorb explicit feature-ledger patterns for authorship similarity only; package runtime is not installed."
    ),
    "ivannikov-lab/style-change-analysis": (
        "Style-change-analysis studies PAN-style style change and style breach detection with paragraph windows, clustering, and statistical comparison. "
        "Absorb style-overfit regression and windowed style drift gates only; datasets/models are not executed."
    ),
    "sam0jones0/pyantistylometry": (
        "PyAntiStylometry records anti-stylometry research for changing identifiable writing-style signals. "
        "Absorb paraphrase-independence risk checks only; no code or automation is imported."
    ),
    "ngpepin/stylometric-transfer": (
        "Stylometric-transfer builds explicit JSON style fingerprints and applies controllable author-style transfer with similarity checks. "
        "Absorb inspectable style-profile and overfit-risk gates only; PolyForm Noncommercial code, HTTP API, prompts, and scripts are not imported or run."
    ),
    "contextlab/llm-stylometry": (
        "LLM-stylometry studies author-trained language models and stylometric signals, including cross-entropy style comparisons. "
        "Absorb LLM-era style similarity and author-fingerprint risk gates only; models and scripts are not downloaded or run."
    ),
    "llm-authorship/survey": (
        "Authorship Attribution in the Era of LLMs is a paper list covering human author attribution, LLM detection, model attribution, and human-LLM coauthoring. "
        "Absorb taxonomy and independence-review gates only; survey index content stays pattern-only."
    ),
    "lsys/lexicalrichness": (
        "LexicalRichness is an MIT module for lexical richness and diversity metrics such as MTLD, HD-D, and type-token variants. "
        "Absorb lexical diversity voice-audit patterns only; no dependency is installed."
    ),
    "hlasse/textdescriptives": (
        "TextDescriptives is an Apache-2.0 text-metrics library covering descriptive, readability, coherence, dependency, and quality signals. "
        "Absorb metric-bundle audit patterns only; spaCy/runtime dependencies are not installed."
    ),
    "boudinfl/pke": (
        "PKE is a GPL-3.0 keyphrase extraction module with candidate extraction and weighting. "
        "Absorb keyphrase/motif extraction patterns only; GPL code and runtime are not imported."
    ),
    "benbrandt/text-splitter": (
        "Text Splitter provides semantic text splitting for Markdown, plain text, and code with chunk capacities and boundary preservation. "
        "Absorb semantic chunk boundary patterns only; Rust/Python/JS packages are not installed."
    ),
    "langchain-ai/langchain": (
        "LangChain includes recursive character text splitters, semantic chunking, document transformers, and summarization chains. "
        "Absorb chunking and summary-chain patterns only; framework runtime and providers are not imported."
    ),
    "miso-belica/sumy": (
        "Sumy is an Apache-2.0 automatic text summarization library with LSA, LexRank, TextRank, Edmundson, and Luhn summarizers. "
        "Absorb chapter summary anchor patterns only; package runtime is not imported."
    ),
    "dmmiller612/bert-extractive-summarizer": (
        "BERT Extractive Summarizer selects representative sentences from embeddings for extractive summaries. "
        "Absorb representative-sentence summary anchor patterns only; model/runtime dependencies are not installed."
    ),
    "maartengr/bertopic": (
        "BERTopic is a topic-modeling framework using transformer embeddings, c-TF-IDF, topic representations, and dynamic topic modeling. "
        "Absorb topic drift and topic-cluster audit patterns only; model/runtime dependencies are not installed."
    ),
    "explodinggradients/ragas": (
        "Ragas is an Apache-2.0 RAG evaluation framework with faithfulness, answer relevancy, context precision, context recall, and testset generation. "
        "Absorb context faithfulness and grounding-eval gates only; runtime and provider integrations are not imported."
    ),
    "confident-ai/deepeval": (
        "DeepEval is an Apache-2.0 LLM evaluation framework with hallucination, answer relevancy, faithfulness, datasets, GEval, and regression tests. "
        "Absorb faithfulness and prompt-regression patterns only; test runner/runtime is not installed."
    ),
    "truera/trulens": (
        "TruLens is an MIT LLM app observability and evaluation framework with feedback functions, groundedness, context relevance, answer relevance, and traces. "
        "Absorb retrieval trace and groundedness review patterns only; runtime instrumentation is not imported."
    ),
    "arize-ai/phoenix": (
        "Phoenix is an AI observability and evaluation platform with tracing, LLM spans, retrieval traces, datasets, experiments, and evals. "
        "Absorb trace observability patterns only; Docker/runtime services are not launched."
    ),
    "promptfoo/promptfoo": (
        "Promptfoo is an MIT prompt testing and eval framework with assertions, golden datasets, regression suites, red-team checks, and CI evaluation. "
        "Absorb prompt-regression suite patterns only; node runtime and scanners are not installed."
    ),
    "openai/evals": (
        "OpenAI Evals is an MIT framework for building custom evals with datasets, samples, graders, and regression cases. "
        "Absorb custom eval and golden-case regression patterns only; eval runtime and provider calls are not used."
    ),
    "thudm/longwriter": (
        "LongWriter is an Apache-2.0 long-output generation project. Public README describes AgentWrite under agentwrite/ with plan.py then write.py, "
        "prompt files plan.txt/write.txt, LongBench-Write for long output quality, and LongWrite-Ruler for maximum output length stress tests. "
        "Absorb plan-write decomposition, length-quality ruler, and long-output evaluation patterns only; model/runtime/provider code is not imported."
    ),
    "thudm/longreward": (
        "LongReward is an Apache-2.0 long-context AI-feedback project. Public README describes auto_scorer scoring long-context responses across helpfulness, "
        "logicality, faithfulness, and completeness, then averaging them into a reward score. Absorb multi-dimension long-output acceptance gates only; "
        "reward models, datasets, and provider calls are not used."
    ),
    "thu-keg/longwriter-v": (
        "LongWriter-V is an MIT ultra-long multimodal generation project. Public README describes LongWriter-Agent-V under agentwrite/, outline_vlm.py, "
        "MMLongBench-Write for long output quality, and LongWrite-V-Ruler for length stress tests. Absorb outline-first long-output and ruler evaluation patterns only; "
        "vision-language model/runtime/API surfaces are not used."
    ),
    "x-plug/writingbench": (
        "WritingBench is an Apache-2.0 generative-writing benchmark. Public README describes 1,000 real-world writing queries, "
        "5 instance-specific criteria per query, requirement-dimension scores, model-augmented query generation, human-in-the-loop refinement, "
        "and material pruning. Absorb local acceptance-criteria and material-grounding gates only; critic models, datasets, and provider calls are not used."
    ),
    "eq-bench/creative-writing-bench": (
        "Creative Writing Benchmark v3 evaluates creative writing with isolated rubric scoring, sparse and comprehensive pairwise matchups, "
        "Elo/Glicko-2 stabilization, win margins, and bias-mitigation notes for length, position, verbosity, and poetic incoherence. "
        "Absorb judge-design patterns only; runtime benchmark scripts, dependencies, API keys, and provider calls are not used."
    ),
    "eq-bench/longform-writing-bench": (
        "Longform Creative Writing Benchmark evaluates brainstorming, planning, critical reflection, character profiles, and eight-chapter novella writing "
        "with narrative consistency and prose-quality judging. Absorb the plan-reflect-character-chapter production trace only; scripts, endpoints, and judge calls are not used."
    ),
    "dig-team/hanna-benchmark-asg": (
        "HANNA is an MIT human-annotated narrative evaluation dataset for automatic story generation. Public README describes 1,056 stories from 96 prompts, "
        "three human raters per story, six criteria (relevance, coherence, empathy, surprise, engagement, complexity), automatic metrics, and LLM explanations. "
        "Absorb reader-facing metric axes only; datasets, notebooks, and metrics code are not imported."
    ),
    "google-deepmind/dramatron": (
        "Dramatron is an Apache-2.0/CC-BY co-writing system for scripts. Public README describes hierarchical generation from log line to character descriptions, "
        "plot points, location descriptions, and dialogue, with human compilation, editing, and rewriting plus plagiarism/toxicity cautions. "
        "Absorb the layered co-writing scaffold and human edit boundary only; Colab/model interfaces are not used."
    ),
    "yangkevin2/emnlp22-re3-story-generation": (
        "Re3 is an MIT long-story generation research codebase. Public README describes recursive reprompting and revision, Plan/Draft/Rewrite/Edit ablations, "
        "outline save/load, relevance and coherence rerankers, candidate limits, beam search, and continuation thresholds. "
        "Absorb recursive revision and reranker-guided candidate-selection patterns only; GPT/API calls, downloads, checkpoints, and training scripts are not used."
    ),
    "lc1332/chat-haruhi-suzumiya": (
        "Chat-Haruhi is an Apache-2.0 character-roleplay project with CC BY-NC data. Public README describes imitating character tone, personality, and plot chat, "
        "extracting characters from novels, role datasets, and personality research. Absorb persona-memory and dialogue-evidence patterns only; models, datasets, demos, and role IP are not imported."
    ),
    "rajammanabrolu/storyrealization": (
        "StoryRealization expands plot events into sentences. Public README describes event creation, slot filling, a memory graph for entities, ensemble thresholds, "
        "confidence scores, and a stale runtime stack. Absorb event-to-sentence trace and entity grounding patterns only; servers, Docker, parsers, datasets, and code are not used."
    ),
    "gratajik/book-memory-bank": (
        "Book Memory Bank is a no-license-observed structured documentation system for AI-assisted book writing. Public README describes a persistently updated knowledge base "
        "for stateless AI, core files for project brief, story structure, world/characters, active context, progress, style guide, master outline, chapter outlines, "
        "plan-to-actual comparison, and comprehensive memory updates after chapter completion. Absorb the context-lattice and update-checklist pattern only; Cline rules and scripts are not imported."
    ),
    "adaumann/speckit-preset-fiction-book-writing": (
        "Spec Kit Fiction Book Writing Preset exposes a fiction adaptation of Spec-Driven Development. Public README describes story-bible governance through constitution.md, "
        "story briefs, plans, scene-by-scene writing tasks, POV architecture, information asymmetry maps, quality gates, glossary checks, subplot health, pacing/statistics/sensitivity gates, "
        "and submission/export workflow. Absorb spec-driven scene tasks and story-bible gates only; installable presets, slash commands, scripts, and Pandoc export are not run."
    ),
    "danngalann/llm-ebook-summarizer": (
        "LLM Ebook Summarizer is a no-license-observed tool for extracting and summarizing EPUB/PDF chapters. Public README describes table-of-contents processing, nested chapters, "
        "parent section introduction preservation, structured markdown notes with summaries, lessons, quotes, anecdotes, 200-word content filters, translation, and merge-to-book output. "
        "Absorb TOC-aware source deconstruction only; Ollama/model runtime, package setup, and scripts are not executed."
    ),
    "darkautism/ai-novel-translation": (
        "AI Novel Translation is a no-license-observed Rust tool for serialized novel translation. Public README describes a two-pass workflow: analysis creates chapter summary and extracts terms, "
        "translation uses the current summary plus cumulative glossary, previous chapter summary, resume detection, configurable prompts, and manual glossary edits. "
        "Absorb context/glossary consistency and resume patterns only; Rust build, providers, API keys, and translation runtime are not used."
    ),
    "lordjabez/story-framework": (
        "Story Framework is an MIT-0 markdown-and-git fiction workspace. Public README describes planning docs as story source of truth, Continuity/timeline.md, Continuity/facts.md, "
        "Plot/threads.md, one draft file per chapter, git commits/tags, inline author notes [[...]], edit notes {{...}}, and process-edit-notes revision flow. "
        "Absorb inline note queues and revision-versioning patterns only; prompt files and host rules are not imported."
    ),
    "getzep/graphiti": (
        "Graphiti is a temporal knowledge-graph memory system for AI agents, useful as a pattern source for novel canon memory. Public project materials describe temporally-aware episodes, entity/relationship extraction, "
        "hybrid semantic/keyword/graph search, provenance, and context assembly for dynamic agent memory. Absorb temporal canon graph and provenance patterns only; "
        "database services, server runtime, dependencies, and API surfaces are not used."
    ),
    "mem0ai/mem0": (
        "Mem0 is a long-term memory layer for AI agents and assistants, useful as a pattern source for author preference and novel project memory. Public materials describe user/session memories, adaptive personalization, memory search, "
        "and multi-level memory workflows. Absorb author preference, project memory, and session-state layering patterns only; hosted service, SDKs, telemetry, and provider calls are not used."
    ),
    "microsoft/graphrag": (
        "GraphRAG is a graph-based retrieval approach for extracting structured data from unstructured text and producing entity/community summaries for global and local search, useful for source-book and novel canon deconstruction. "
        "Absorb source-book graph deconstruction and community-summary patterns only; indexing pipelines, model calls, storage backends, and CLI runtime are not used."
    ),
    "hkuds/lightrag": (
        "LightRAG is a graph/vector retrieval project that emphasizes dual-level retrieval over knowledge graphs and vector embeddings with local, global, hybrid, and naive query modes for long-form story context. "
        "Absorb dual-level graph-vector context selection patterns only; dependencies, servers, model calls, and storage/runtime code are not imported."
    ),
    "neo4j-labs/llm-graph-builder": (
        "Neo4j LLM Graph Builder extracts nodes, relationships, and properties from unstructured documents into a graph using schema guidance and source metadata, useful for novel source/canon extraction. "
        "Absorb schema-guided canon/source graph extraction patterns only; Neo4j services, UI, Docker/runtime pieces, and provider calls are not used."
    ),
    "idsia/novel2graph": (
        "NOVEL2GRAPH is a literary-text knowledge-graph workflow. Public README describes receiving a book as input, discovering main characters, main relations, "
        "knowledge graph material, static and dynamic embeddings, relation reports, character occurrence clusters, character network views, character interactions, chapter slices, and an interface for monitoring results. "
        "Absorb full-book source decomposition, character relationship graph, narrative event graph, and schema-guided graph extraction patterns: extract nodes, relationships and properties with source metadata. Stanford NLP downloads, Python scripts, GUI runtime, scraping, and datasets are not executed."
    ),
    "drwei3155/story-graph": (
        "Story Graph is a Chinese novel relationship-graph workbench. Public README describes entering a novel name, AI-generated visual character relationship network, "
        "natural-language graph search, relationship-path explanation, multi-book comparison, event timeline, manual graph edits, statistics, and PNG export. "
        "Absorb relationship-graph review, event-timeline deconstruction, source comparison, and editable graph-audit UI patterns only; Node server, DeepSeek/API keys, browser sessionStorage, provider calls, and hosted app are not used."
    ),
    "mitchsaltykov/tvtropes-correlation": (
        "TVTropes-correlation compares two works by their trope sets. Static README describes entering media URLs and measuring similarity by shared tropes. "
        "Absorb trope-vector similarity and same-type independence review patterns only; the Heroku app, scraping flow, and source site access are not executed."
    ),
    "jwzimmer-zz/tv-tropes": (
        "tv-tropes is a final-project repository for building a network of tropes from TV Tropes wiki material. "
        "Absorb trope graph / co-occurrence expectation-map patterns only; no wiki crawl, dataset import, or notebook/runtime execution is performed."
    ),
    "slowwavesleep/tvtropesmoviedata": (
        "TvTropesMovieData exposes a CC-BY-SA movie-to-trope dataset. "
        "Absorb trope inventory, density, and novelty-budget patterns only; dataset rows and downstream training material are not imported into drafting context."
    ),
    "rhgarcia/tropescraper": (
        "Tropescraper is an LGPL Python package for scraping trope metadata. "
        "Absorb only the admission boundary: public trope sources require no runtime scrape by default, no mass mirroring, and no scraped text in prompts."
    ),
    "sirver51/tvtropes-parser": (
        "tvtropes-parser parses TV Tropes pages into sections and states it is not intended for mass scraping. "
        "Absorb section-boundary and no-mass-scrape review patterns only; parser code, Kotlin runtime, and page fetching are not executed."
    ),
    "licensee/licensee": (
        "Licensee detects repository licenses and is used by GitHub-style license matching. "
        "Absorb license-detection review patterns only; Ruby runtime, gem execution, and source-code import are not used."
    ),
    "fsfe/reuse-tool": (
        "REUSE is a tool and recommendation set for copyright and licensing metadata using SPDX identifiers, file copyright text, and reusable compliance checks. "
        "Absorb SPDX/REUSE manifest patterns only; the CLI and package runtime are not executed."
    ),
    "spdx/license-list-data": (
        "SPDX License List Data publishes generated license metadata and machine-readable license list formats. "
        "Absorb license-id normalization and allowed-license taxonomy patterns only; generated data is not copied into runtime context."
    ),
    "c-w/gutenberg": (
        "Gutenberg is an Apache-2.0 Python project for working with the Project Gutenberg body of public-domain texts, including metadata and text cleaning. "
        "Absorb public-domain source-boundary and metadata-cleaning review patterns only; downloads and cleaning scripts are not executed."
    ),
    "imkun-on/gutenberg-corpus-cli": (
        "Gutenberg Corpus CLI browses Project Gutenberg metadata and builds public-domain corpora with downloads, local SQLite catalog, and full-text search. "
        "Absorb public-domain corpus admission and downloader-boundary patterns only; scraper, download, database, and corpus-building runtime are not executed."
    ),
    "microsoft/presidio": (
        "Presidio detects, redacts, masks, and anonymizes sensitive data with NLP, pattern matching, custom recognizers, and anonymizer operators. "
        "Absorb source-entity redaction and proper-noun leakage review patterns only; Docker, services, image redaction, and package runtime are not executed."
    ),
    "leapbeyond/scrubadub": (
        "Scrubadub removes personally identifiable information from text with detectors, postprocessors, replacers, and anonymous ids. "
        "Absorb placeholder and alias-consistency redaction patterns only; optional detector packages and runtime dependencies are not installed."
    ),
    "urchade/gliner": (
        "GLiNER is a generalist lightweight named entity recognition project for extracting arbitrary entity types from text. "
        "Absorb custom entity-label inventory patterns for fictional names, places, factions, artifacts, and powers only; models and package runtime are not downloaded."
    ),
    "flairnlp/flair": (
        "Flair provides NLP sequence labeling and named entity recognition models across languages. "
        "Absorb multilingual proper-noun inventory and leakage-review patterns only; trained models and framework runtime are not imported."
    ),
    "explosion/spacy": (
        "spaCy provides industrial NLP pipelines with tokenization, named entity recognition, text classification, and custom pipeline components. "
        "Absorb pipeline-shaped entity review and custom fiction-entity labeling patterns only; models, packages, and runtime pipelines are not installed."
    ),
    "ydsgangge-ux/dramatica-flow": (
        "Causal-driven AI novel engine based on Dramatica theory with a five-layer Agent writing pipeline, "
        "causal-chain management, multi-line narration, foreshadowing tracking, FastAPI/CLI surfaces, and install scripts. "
        "Pattern-only adaptation for causal dramaturgy gates, foreshadowing debt, and agent-layer handoff checks."
    ),
    "mmunro3318/story-foundry": (
        "Agentic authoring platform for ideation and novel writing with Claude Code / VS Code collaboration, "
        "agent templates, workflow folder, and Capture -> Distillation -> Production style stages. "
        "Pattern-only adaptation for staged source capture, distilled story packets, and production gate handoffs."
    ),
    "shine8592/novel-writer-skills": (
        "OpenClaw skill pack for zero-cost Chinese novel writing with multiple skills, Chinese web-novel focus, "
        "chapter generation, style constraints, and provider-budget positioning. "
        "Pattern-only adaptation for skill-orchestrated Chinese novel workflows, budget smoke gates, and localization-style checks."
    ),
    "modoojunko/awesome-novel-skill": (
        "Chinese novel-writing skill system for AI agents. Public metadata describes worldbuilding, character shaping, "
        "chapter planning, prose writing, SKILL.md, agents, memory, templates, tools, and install scripts under GPL-3.0. "
        "Pattern-only adaptation for skill-orchestrated Chinese novel workflows; no installer or bulk skill import."
    ),
    "langchain-ai/story-writing": (
        "LangGraph / LangChain story-writing sample with agent.py, langgraph.json, app pages, requirements, tests, and story state flow. "
        "Pattern-only adaptation for graph/state-machine writing loops and stateful planning checkpoints; no package runtime import."
    ),
    "edwardathomson/storydaemon": (
        "Autonomous long-form fiction agent that plans, writes, and evolves stories organically with work directories, docs, scripts, and tests. "
        "Pattern-only adaptation for story-daemon evolution loops, organic planning checkpoints, and autonomous-agent review boundaries."
    ),
    "datacrystals/aistorywriter": (
        "AIStoryWriter is an AGPL LLM story generator with outline, chapter-outline, chapter-writing, revision, evaluation, and local/Ollama model selection surfaces. "
        "Pattern-only adaptation for staged long-output generation and quality model separation; requirements, provider calls, prompt files, and scripts are not executed or imported."
    ),
    "sadasdfsaf/canonkit": (
        "CanonKit is a local-first story bible and continuity checker for fiction teams and solo authors, focused on canon drift, structured characters, locations, rules, scenes, JSON import/export, and context packs. "
        "Pattern-only adaptation for canon-drift QA, continuity checks, and scene-focused context pack gates; no browser app, npm install, or sample project import."
    ),
    "heider-x/vela": (
        "Vela is a GPL AI novel-writing IDE with local-first privacy posture, BYOK model calls, worldbuilding, auto outline, chapter drafting, review/rewrite/refine loops, and local RAG knowledge base. "
        "Pattern-only adaptation for local RAG writing IDE boundaries and retrieval-backed continuity; Electron/Vite app, package hooks, and model calls are not launched."
    ),
    "pulpgen-dev/pulpgen": (
        "pulpgen-dev/pulpgen is a MIT AI novel drafting agent that turns an idea into outline.xml, patch-NN.xml dispatch logs, final.xml/final.html, and versioned HTML snapshots with interactive editing. "
        "Pattern-only adaptation for patch replay manuscript state, version snapshots, and idea-to-draft assembly gates; Gemini calls, uv/Python runtime, and exporters are not executed."
    ),
    "jim60105/heartreverie": (
        "HeartReverie is an AGPL AI interactive novel engine using markdown story/prompt/lore files, Git-friendly editing, a plugin.json ecosystem, hooks, prompt fragments, reader progress, and writer surfaces. "
        "Pattern-only adaptation for file-backed reader-writer loops and plugin boundary gates; Deno, containers, Helm, plugins, scripts, and Agent Skill install commands are not executed."
    ),
    "wzxsph/novel-claude": (
        "Novel-Claude is a GPL agentic long-form web-novel generation framework with microkernel/plugin architecture, EventBus, PluginManager, NovelContext, world_builder, volume_planner, scene_writer, editor agent, RAG memory skill, and skill builder agent. "
        "Pattern-only adaptation for plugin isolation, context isolation, event-bus stage boundaries, and scene-task gates; Python runtime, prompts, skills, provider calls, and generated plugin code are not imported."
    ),
    "liaoma1993/aiaifiction": (
        "AI Fiction Studio is a Chinese long-form web-novel workbench for project planning, worldbuilding, roles/factions, volume/chapter outlines, style learning Skill, chapter writing, quality audit, repair, memory center, and story graph. "
        "Pattern-only adaptation for abstract style-skill learning, memory-center QA, and long-form repair dashboards; Docker, backend/frontend services, scripts, uploads, and model configuration are not run."
    ),
    "vishnu0120754/renovel-ai": (
        "ReNovel-AI is a GPL novel revision workspace with long-term memory, three-way collaboration, card-based editing, import, automated revisions, and narrative expansion. "
        "Pattern-only adaptation for interactive revision loops and memory-backed edit cards; installers, batch files, requirements, and app runtime are not executed."
    ),
    "worldwonderer/zenstory": (
        "ZenStory is a MIT AI-powered novel workbench where agents operate creative files for character cards, reference deconstruction, outline planning, chapter writing, quality review, material library, hybrid RAG retrieval, and context compression. "
        "Pattern-only adaptation for reference-material deconstruction, local file workspace, hybrid retrieval, and multi-agent writing QA; Docker, apps, scripts, and agent runtime are not launched."
    ),
    "tuxiangxianzhe/novelwriter_public": (
        "NovelWriter_public is an AGPL Vue/FastAPI AI novel platform with outline and improvised-writing modes, open_threads foreshadowing pool, single-chapter blueprints, scene-segmented generation, context-injected revision, backups, narrative DNA, style imitation, continuation expansion, and AI-tone removal. "
        "Pattern-only adaptation for impromptu continuation gates, scene-density drafting, and thread-pool settlement; Docker, frontend/backend services, scripts, providers, and prompts are not executed or imported."
    ),
    "ma-bihani/novelia_public": (
        "Novelia_public is a local-first Electron/React creative-writing environment described as offline/private with Ollama local RAG, an Inspiration bank for PDF/DOCX lore and notes, Continue/Rewrite modes, dynamic style engine, and filesystem book/chapter storage. "
        "Pattern-only adaptation for offline inspiration-bank boundaries and style-mimicry isolation; Electron app, LangChain/LanceDB pipeline, local model calls, and document ingestion are not launched."
    ),
    "huodebing-alt/claude-code-novel-agents": (
        "Claude-Code-Novel-Agents is a MIT Claude Code novel atelier with many specialized agents, skills, a six-phase pipeline, detailed beat planner, hook auditor, outline reviewer, PDF compositor, and infinite-serial mode. "
        "Pattern-only adaptation for phase manifests, beat-tree handoffs, hook audits, and human-control modes; agent definitions, skills, and install/runtime instructions are not imported or executed."
    ),
    "cchheerrss/ai-novel-trilogy": (
        "AI Novel Trilogy is a MIT three-system Chinese webnovel pipeline: book-mining extracts reusable patterns, novel-genesis validates concepts and emits canon seed YAML, and novel-automation applies pattern-aware chapter gates. "
        "Pattern-only adaptation for deconstruction-to-genesis handoff, canon seed separation, scoring gates, and automation boundaries; PowerShell tools, Claude/Codex runtime manifests, and source texts are not executed or imported."
    ),
    "zhitongblog/novel-studio": (
        "Novel Studio is a MIT multi-book webnovel studio that orchestrates Unterm profiles with Codex, Claude Code, and Gemini CLI, exposing desktop/TUI/CLI/MCP surfaces, autopilot continuation, periodic full-book logic checks, and per-book context files. "
        "Pattern-only adaptation for multi-book session isolation, autopilot stop conditions, periodic continuity audits, and human-visible studio control; npm/Tauri/MCP/runtime surfaces and auth tokens are not launched or read."
    ),
    "dinhlucent/webnovel-longrun-aigen-docs": (
        "Webnovel Longrun AIGen docs describe a long-running webnovel system with .story-system as the source of truth, accepted chapter commits, event extraction, .webnovel read-model projections, RAG/query routing, memory scratchpad, and read-only dashboard. "
        "Pattern-only adaptation for commit-to-projection health gates and longrun memory hygiene; GPL docs are not copied, and Python/runtime components are not installed."
    ),
    "haowjy/creative-writing-skills": (
        "Creative Writing Skills is an Apache-2.0 Claude/Cowork/Meridian skill pack for novels, short stories, and serial fiction. Public README describes muse-led brainstorming, "
        "writer/critic/revision loops, reader-sim feedback across four reward channels, continuity checks, style-creator voice references, and chronicler knowledge-base updates. "
        "Pattern-only adaptation for reader-reward review, style/reference boundaries, and accepted-fact sync; plugin installs, agents, zips, and runtime commands are not imported or executed."
    ),
    "jblemee/bmad-book-builder": (
        "BMad Book Builder is a WTFPL BMAD module for AI-assisted novels with 8 specialized agents, 17 workflows, Create/Edit/Validate modes, pre-writing checklist, quantitative style metrics, "
        "automated post-chapter audit chain, living-bible updates, per-character contradiction audits, theme tracking, rhythm analysis, and reality checks. "
        "Pattern-only adaptation for tri-modal workflow gates and post-chapter audit chains; BMAD CLI, npm installers, custom modules, agents, and workflow files are not installed or copied."
    ),
    "deland78/claude-writing-skills": (
        "Claude-Writing-Skills is a fiction co-author skill system for Claude Code with story bible files, chapter promise, scene architect, scene draft, character truth pass, "
        "voice anchor, tension curve, AI-filter humanize, and a mob-session protocol where a lead editor queues specialist comments with citations before committing canon changes. "
        "Pattern-only adaptation for promise-to-scene cards and cited human-in-the-loop review; Claude hooks, shell scripts, skills, agents, and runtime commands are not imported or executed."
    ),
    "netflypsb/webnovel-mcp": (
        "webnovel-mcp is a MIT MCP server and webnovel author skill for serial fiction projects. Public README/SKILL describe project scaffolding, character/chapter/world/style resources, "
        "foreshadowing reports, continuity checks, timeline tracking, LitRPG stat blocks, romance arc tracking, and style-guide rules for cliffhangers and power progression. "
        "Pattern-only adaptation for serial-genre trackers and project-structure admission; uvx/pip install, MCP server launch, license-key paths, and tool calls are not executed."
    ),
    "hackertaco/novel-generator": (
        "Kakao Novel Generator is a simulation-first long-form novel engine with explicit world truth, character memory, belief state, utterance history, causal ledgers, chapter summaries, "
        "shared CLI/library workflow contracts, and long-form verification over a deterministic 300-episode scenario. "
        "Pattern-only adaptation for causal-ledger verification and surface-parity artifacts; npm/tsx scripts, provider calls, env files, legacy Python CLI, and web/API surfaces are not executed."
    ),
    "eristoddle/git-write": (
        "GitWrite is a MIT writer-friendly abstraction over Git for writers, editors, and beta readers. Public README/User Guide describe save/history, explorations as branches, "
        "word-by-word diff, author-controlled review, selective integration, beta-reader annotations as commits, and export/version checkpoints. "
        "Pattern-only adaptation for manuscript branch review and annotation provenance; pip/poetry/npm install, Docker/compose, deploy scripts, API server, and demo credentials are not used."
    ),
    "google-deepmind/narrativeqa": (
        "NarrativeQA is an Apache-2.0 reading-comprehension dataset for books and movie scripts with document metadata, Wikipedia summaries, links to full stories, and question/answer pairs. "
        "Pattern-only adaptation for拆书 QA coverage and continuation comprehension checks; download_stories.sh, story downloads, and corpus files are not executed or imported."
    ),
    "salesforce/booksum": (
        "BookSum is a BSD-3-Clause collection for long-form narrative summarization over novels, plays, and stories, with human summaries at paragraph, chapter, and book granularity. "
        "Pattern-only adaptation for chapter/book summary alignment, causal/temporal dependency coverage, and abstract summary review; GCP downloads and data-collection scripts are not executed."
    ),
    "uci-soe/fairytaleqadata": (
        "FairytaleQAData is an Apache-2.0 narrative-comprehension dataset with children story sections, sentence files, and expert-authored question-answer pairs linked to story sections and narrative-element categories. "
        "Pattern-only adaptation for section-grounded QA validation and story-element coverage; starter scripts, notebooks, dataset loaders, and full text are not executed or imported."
    ),
    "stonybrooknlp/tellmewhy": (
        "TellMeWhy is a narrative why-question dataset with free-form answers, helpful-sentence annotations, answerability judgments, and grammaticality/validity human evaluation for why characters act. "
        "Pattern-only adaptation for causal why-explanation gates; Google Drive downloads, HuggingFace loaders, scripts, and evaluation runtime are not executed."
    ),
    "uwnlp/storycommonsense": (
        "Story Commonsense Knowledge accompanies ACL 2018 work on naive psychology of characters in simple commonsense stories. "
        "Pattern-only adaptation for character motivation, emotion, and mental-state consistency checks; dataset downloads, model code, and external website workflows are not executed."
    ),
    "nyu-mll/squality": (
        "SQuALITY is a question-focused long-document multi-reference summarization dataset over Project Gutenberg short stories, with plot questions and multiple human reference summaries. "
        "Pattern-only adaptation for query-focused summary and plot-question review; training scripts, data files, and dataset consumption code are not executed or imported."
    ),
    "fopearcano/storyplanner": (
        "Storyplanner is a local-first creative writing tool with narrative engines for novel, screenplay, stage script, and graphic novel structures, "
        "a PSYKE Story Bible, story grid, multi-plot, timeline, motif/causality/continuity graph, and safe propose-then-confirm assistant actions. "
        "Pattern-only adaptation for engine-aware decomposition, story-bible graph context, and author-confirmed AI actions; scripts and local API runtime are not executed."
    ),
    "giapnguyen74/xnovelist": (
        "xnovelist is an MIT local-first novel editor where prose stays on the device, AI is off by default, and a workspace level from 0 to 5 caps AI authority. "
        "Public README describes Story Bible entities, voice/continuity capture, automatic snapshots, line-level diff, and drafts awaiting review. "
        "Pattern-only adaptation for author-controlled AI levels, local manuscript ownership, and staged review; Next.js/package scripts are not installed or run."
    ),
    "waylean/plotrail": (
        "PlotRail is an MIT canon-aware reusable SKILL.md workflow for long-form fiction. Public README describes canon files, approved chapter contracts, "
        "drafts/reviews/research folders, memory ledgers, story bible before drafting, and continuity review for every chapter. "
        "Pattern-only adaptation for chapter contract rails and continuity QA; external skill files are not installed or copied."
    ),
    "xinganliu/web-novel-writing-skill": (
        "Web Novel Writing Skill is an MIT Chinese web-novel agentic workflow with a 10-stage pipeline, 7 expert roles, 4-layer anti-hallucination, "
        "state-sync memory, golden-three-chapters strategy, and anti-AI-pattern quality gates. "
        "Pattern-only adaptation for Chinese web-novel workflow routing and anti-slop gates; AGENTS/CLAUDE/plugin skill surfaces are not installed or imported."
    ),
    "miserylee/webnovel-handbook": (
        "webnovel-handbook is an MIT AI-agent handbook for Chinese webnovel workflows. Public README says agents should not load the whole repo; they route through README, AGENTS, docs/00-index, "
        "then task-specific docs such as integrated drafting, beta-reader feedback, review, and revision workflows. "
        "Pattern-only adaptation for progressive handbook routing and reader-review loops; scripts and skill packs are not executed or copied."
    ),
    "ungden/truyencity2": (
        "TruyenCity2 is an Apache-2.0 AI webnovel platform with Story Engine v2 for long serials. Public README describes 5-layer canon/plan/state/memory/quality/context/pipeline architecture, "
        "1000-chapter Story Factory workflow, foreshadowing, timeline, cast database, power-system canon, plot-twist tables, batch writing, autopilot, and prompt-cache cost controls. "
        "Pattern-only adaptation for serial genre state trackers, longrun autopilot gates, and provider-budget smoke boundaries; app, Supabase, edge functions, and scripts are not run."
    ),
    "furuyan1234/story-maker": (
        "Story Maker is a static creative-text web app that builds generation from visible axes: output mode, theme, genre, worldview, audience, era, ending style, narrator, characters, source material, image material, and optional style analysis. "
        "Public README describes selected-mode-first contracts, mode-specific output shapes, under-length draft rewrite handling, axis tags, provider key safety, and explicit legal/publication caveats. "
        "Pattern-only adaptation for mode-contract generation gates and anti-generic prose checks; Vite app, GitHub Pages deployment, provider calls, keys, and browser runtime are not used."
    ),
    "yuanbw2025/storyforge": (
        "StoryForge is a Chinese privacy-first offline browser writing studio. Public README describes visible/editable/savable prompt templates, prompt workflows, IndexedDB storage, 11 BYOK providers, chain workflows, chunked million-word import, three-layer memory, consistency checks, and master-study tables. "
        "Pattern-only adaptation for transparent prompt workflow libraries and source-study method-bank isolation; npm app, provider calls, private prompts, local data, and docs/CLAUDE startup instructions are not imported or run."
    ),
    "dedyrio/novelwriter": (
        "novelwriter is an AGPL-3.0 AI story tool whose public README says it imports existing stories, extracts characters and relationships, maintains a world model, applies story rules, and preserves style consistency. "
        "Pattern-only adaptation for world-model rule gates and style-consistent continuation; Windows installer downloads, Docker instructions, ZIP/EXE artifacts, provider keys, and app runtime are not downloaded or executed."
    ),
    "qq1375828505/ai-fic-ide": (
        "AI-Fic-IDE is an Android-native Chinese web-novel writing IDE forked from Operit AI. Public README describes character cards, setting cards, foreshadowing states, AI memory, cross-chapter search/replace, autosave, history snapshots, local models, multi-model providers, MCP plugin market, ADB/root/accessibility surfaces, and APK releases. "
        "Pattern-only adaptation for mobile/offline writing workspace cards and snapshot boundaries; APKs, Android runtime, ADB/root/accessibility, MCP plugins, provider keys, and native binaries are not installed or launched."
    ),
    "dlintin/sidekickwriter": (
        "SidekickWriter is an AI-powered book writing platform. Public README describes guided/pro modes, writing style selection, character development, chapter-by-chapter outline generation, chapter descriptions aware of previous chapters for continuity, full-book or per-chapter generation, real-time streaming, inline editing, specific-chapter regeneration, research sources, and citation styles. "
        "Pattern-only adaptation for chapter-description context bridges, selective regeneration, and research citation boundaries; provider calls and hosted platform use are not performed."
    ),
    "gennitdev/ai-beta-reader-frontend": (
        "AI Beta Reader frontend manages books and chapters, markdown editing, smart chapter summaries that track plot points, characters, and key events, contextual AI reviews using previous chapter summaries, multiple review styles, sql.js/local storage, Google Drive OAuth sync, and OpenAI-backed reviews. "
        "Pattern-only adaptation for beta-reader summary context review and storage/oauth boundaries; OAuth, Google Drive, local browser storage, and provider calls are not used."
    ),
    "gennitdev/ai-beta-reader-backend": (
        "AI Beta Reader backend is an Express REST API for AI-generated chapter feedback with previous-chapter-summary context, Auth0 JWT, PostgreSQL/Neon, OpenAI Responses API, OPENAI_API_KEY, and DATABASE_URL configuration. "
        "Pattern-only adaptation for summary-context beta review and credential/database boundaries; API server, database, Auth0, and provider calls are not launched."
    ),
    "wesleyscholl/book-generator": (
        "AI Book Generator is an autonomous book creation pipeline. Public README describes shell-script helpers for topic/title selection, detailed outlines, chapter generation/extension/editing, optional quality and plagiarism checks, full manuscript assembly with title pages, table of contents, copyright pages, appendices, acknowledgements, and EPUB/PDF/KDP-style export. "
        "Pattern-only adaptation for research citation boundaries and publication assembly gates; shell scripts, providers, ImageMagick, Pandoc, TeX, and KDP workflows are not run."
    ),
    "boundless-fang/stylesync-novel": (
        "StyleSync-Novel is a Chinese AI novel prototype. Public README markers describe style analysis, style vocabulary libraries, worldbuilding extraction, character-card extraction, setting completion, chapter outline generation, body generation, and chapter-local modification. "
        "Pattern-only adaptation for style-vocabulary/world-card extraction and scoped rewrite gates; DeepSeek/SiliconFlow provider keys, scripts, and runtime are not used."
    ),
    "eluckydog/dreamquill": (
        "DreamQuill is a MIT pure-prompt novel writing agent. Public README markers describe prompt-only operation, continuity guards, setting cards, ten-chapter stress testing, 5000-6000 character wrap-up mode, and prompt-only capability decay. "
        "Pattern-only adaptation for prompt-only decay ceilings and continuation stress reports; no prompts are bulk-imported or executed."
    ),
    "304769384-png/fanqie-novel-skill": (
        "fanqie-novel-skill is a Chinese serial-webnovel skill pack. Public README markers describe AI de-flavoring, progress tracking, minimum audit sets, battle-scene audit, dialogue-ratio monitoring, loop/cycle detection every five chapters, and full audit every ten chapters. "
        "Pattern-only adaptation for serial platform audit gates; upstream skill bodies, prompts, and runtime commands are not imported."
    ),
    "leistung/novel-write": (
        "novel-write is a LangChain/LangGraph multi-agent novel-writing assistant. Public README markers describe Architect, Writer, Consistency Checker, and Author agents, next-chapter continuation, rewrite-from-chapter-n, outline-impact analysis, reject/retry loops, and score-below-80 return-to-planning behavior. "
        "Pattern-only adaptation for multi-agent reject/retry review gates; provider keys, .env configuration, and runtime graph execution are not used."
    ),
    "verifiedorganic/spindle": (
        "spindle is a MIT local-first fiction planning companion. Public README markers describe story bible, context-packet assembly, recent summaries, narrative promises, branch/save points, restoreable scene versions, continuity checks, dual-persona editorial review, canonical fact extraction, EPUB export, and MCP server surfaces. "
        "Pattern-only adaptation for story-bible context packets and branch checkpoints; MCP server, Rust binary/runtime, and exports are not launched."
    ),
    "daveremy/edword": (
        "edword is an editorial-analysis project for book manuscripts. Public README markers describe memory-augmented extraction, chapter-by-chapter indexing, structured fact extraction from the current chapter, deterministic accumulation into a knowledge graph, Chain-of-Verification, targeted questions, continuity checking, and incremental processing. "
        "Pattern-only adaptation for delta fact indexing and verification reports; CLI, MCP, provider calls, and manuscript runtime analysis are not executed."
    ),
    "adameya2004-oss/craftengine": (
        "CraftEngine is a SillyTavern extension. Public README markers describe writing-quality analysis from 22 published novels, 22-book style presets, smart rewriting below thresholds, imported book style learning, character voice profiles, rhythm/sensory-density metrics, slop detection, dialogue checks, repetition checks, and ending-quality metrics. "
        "Pattern-only adaptation for statistical style benchmark rewrite gates; browser extension and SillyTavern runtime are not installed or launched."
    ),
}

STATIC_REPOSITORY_POSTURE_OVERRIDES: dict[str, tuple[str, str]] = {
    "jwynia/agent-skills": ("index-only", "catalog-index-only"),
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
            "mode_contract_generation_gate_hints": self._build_mode_contract_generation_gate_hints(available_patterns),
            "source_study_method_bank_isolation_gate_hints": self._build_source_study_method_bank_isolation_gate_hints(available_patterns),
            "inline_human_machine_coauthoring_gate_hints": self._build_inline_human_machine_coauthoring_gate_hints(available_patterns),
            "hierarchical_orchestrator_generation_gate_hints": self._build_hierarchical_orchestrator_generation_gate_hints(available_patterns),
            "batch_continuation_progress_queue_gate_hints": self._build_batch_continuation_progress_queue_gate_hints(available_patterns),
            "homogeneity_prompt_variation_gate_hints": self._build_homogeneity_prompt_variation_gate_hints(available_patterns),
            "local_author_data_boundary_gate_hints": self._build_local_author_data_boundary_gate_hints(available_patterns),
            "prompt_preset_variable_library_gate_hints": self._build_prompt_preset_variable_library_gate_hints(available_patterns),
            "imported_manuscript_migration_outline_gate_hints": self._build_imported_manuscript_migration_outline_gate_hints(available_patterns),
            "style_dna_reference_library_gate_hints": self._build_style_dna_reference_library_gate_hints(available_patterns),
            "draft_candidate_promotion_gate_hints": self._build_draft_candidate_promotion_gate_hints(available_patterns),
            "privacy_preserving_local_index_gate_hints": self._build_privacy_preserving_local_index_gate_hints(available_patterns),
            "chapter_description_continuity_bridge_gate_hints": self._build_chapter_description_continuity_bridge_gate_hints(available_patterns),
            "selective_streaming_regeneration_gate_hints": self._build_selective_streaming_regeneration_gate_hints(available_patterns),
            "research_citation_boundary_gate_hints": self._build_research_citation_boundary_gate_hints(available_patterns),
            "beta_reader_summary_context_gate_hints": self._build_beta_reader_summary_context_gate_hints(available_patterns),
            "style_vocab_world_card_extraction_gate_hints": self._build_style_vocab_world_card_extraction_gate_hints(available_patterns),
            "prompt_only_decay_ceiling_gate_hints": self._build_prompt_only_decay_ceiling_gate_hints(available_patterns),
            "serial_platform_minimum_audit_gate_hints": self._build_serial_platform_minimum_audit_gate_hints(available_patterns),
            "multi_agent_reject_retry_review_gate_hints": self._build_multi_agent_reject_retry_review_gate_hints(available_patterns),
            "story_bible_context_packet_branch_gate_hints": self._build_story_bible_context_packet_branch_gate_hints(available_patterns),
            "memory_augmented_delta_verification_gate_hints": self._build_memory_augmented_delta_verification_gate_hints(available_patterns),
            "statistical_style_benchmark_rewrite_gate_hints": self._build_statistical_style_benchmark_rewrite_gate_hints(available_patterns),
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
            "plain_text_project_storage_hints": self._build_plain_text_project_storage_hints(available_patterns),
            "synopsis_cross_reference_hints": self._build_synopsis_cross_reference_hints(available_patterns),
            "snowflake_premise_expansion_hints": self._build_snowflake_premise_expansion_hints(available_patterns),
            "outliner_index_cards_hints": self._build_outliner_index_cards_hints(available_patterns),
            "narrative_strand_mapping_hints": self._build_narrative_strand_mapping_hints(available_patterns),
            "character_depth_interview_hints": self._build_character_depth_interview_hints(available_patterns),
            "mindmap_visual_planning_hints": self._build_mindmap_visual_planning_hints(available_patterns),
            "manuscript_export_formats_hints": self._build_manuscript_export_formats_hints(available_patterns),
            "human_synopsis_gate_hints": self._build_human_synopsis_gate_hints(available_patterns),
            "retrieval_guided_span_rewrite_hints": self._build_retrieval_guided_span_rewrite_hints(available_patterns),
            "runtime_artifact_trace_hints": self._build_runtime_artifact_trace_hints(available_patterns),
            "schema_validated_state_delta_hints": self._build_schema_validated_state_delta_hints(available_patterns),
            "recursive_adaptive_planning_hints": self._build_recursive_adaptive_planning_hints(available_patterns),
            "workflow_manuscript_compilation_hints": self._build_workflow_manuscript_compilation_hints(available_patterns),
            "writing_session_goal_tracking_hints": self._build_writing_session_goal_tracking_hints(available_patterns),
            "inspectable_run_workspace_hints": self._build_inspectable_run_workspace_hints(available_patterns),
            "craft_role_pipeline_hints": self._build_craft_role_pipeline_hints(available_patterns),
            "frontmatter_story_schema_hints": self._build_frontmatter_story_schema_hints(available_patterns),
            "continuity_bridge_window_hints": self._build_continuity_bridge_window_hints(available_patterns),
            "episode_range_rewrite_scope_hints": self._build_episode_range_rewrite_scope_hints(available_patterns),
            "voice_table_polish_axis_hints": self._build_voice_table_polish_axis_hints(available_patterns),
            "boring_opening_quality_gates_hints": self._build_boring_opening_quality_gates_hints(available_patterns),
            "beat_strand_framework_hints": self._build_beat_strand_framework_hints(available_patterns),
            "anti_hallucination_plan_check_hints": self._build_anti_hallucination_plan_check_hints(available_patterns),
            "backup_restore_checkpoint_hints": self._build_backup_restore_checkpoint_hints(available_patterns),
            "multi_level_review_trend_hints": self._build_multi_level_review_trend_hints(available_patterns),
            "editor_notes_feedback_loop_hints": self._build_editor_notes_feedback_loop_hints(available_patterns),
            "genre_parameterized_worldbuilding_hints": self._build_genre_parameterized_worldbuilding_hints(available_patterns),
            "prose_preflight_voice_calibration_hints": self._build_prose_preflight_voice_calibration_hints(available_patterns),
            "sourcebook_author_workbench_hints": self._build_sourcebook_author_workbench_hints(available_patterns),
            "semantic_long_context_search_hints": self._build_semantic_long_context_search_hints(available_patterns),
            "contradiction_taxonomy_checker_hints": self._build_contradiction_taxonomy_checker_hints(available_patterns),
            "parallel_agent_chapter_pipeline_hints": self._build_parallel_agent_chapter_pipeline_hints(available_patterns),
            "cross_chapter_redundancy_audit_hints": self._build_cross_chapter_redundancy_audit_hints(available_patterns),
            "humanization_stylometry_levers_hints": self._build_humanization_stylometry_levers_hints(available_patterns),
            "author_control_boundary_hints": self._build_author_control_boundary_hints(available_patterns),
            "research_taxonomy_story_map_hints": self._build_research_taxonomy_story_map_hints(available_patterns),
            "novel_to_multimodal_pipeline_hints": self._build_novel_to_multimodal_pipeline_hints(available_patterns),
            "entity_to_visual_asset_pipeline_hints": self._build_entity_to_visual_asset_pipeline_hints(available_patterns),
            "agentic_book_planner_pipeline_hints": self._build_agentic_book_planner_pipeline_hints(available_patterns),
            "rag_synopsis_spine_hints": self._build_rag_synopsis_spine_hints(available_patterns),
            "anti_repetition_prompt_rules_hints": self._build_anti_repetition_prompt_rules_hints(available_patterns),
            "prompt_recipe_experiment_grid_hints": self._build_prompt_recipe_experiment_grid_hints(available_patterns),
            "append_only_generation_review_log_hints": self._build_append_only_generation_review_log_hints(available_patterns),
            "narrative_arc_template_control_hints": self._build_narrative_arc_template_control_hints(available_patterns),
            "nrd_task_tree_pipeline_hints": self._build_nrd_task_tree_pipeline_hints(available_patterns),
            "sampling_parameter_quality_sweep_hints": self._build_sampling_parameter_quality_sweep_hints(available_patterns),
            "story_structure_rag_planning_hints": self._build_story_structure_rag_planning_hints(available_patterns),
            "story_contract_commit_chain_hints": self._build_story_contract_commit_chain_hints(available_patterns),
            "fact_snapshot_delta_gate_hints": self._build_fact_snapshot_delta_gate_hints(available_patterns),
            "projection_sync_observability_hints": self._build_projection_sync_observability_hints(available_patterns),
            "foreshadowing_debt_budget_hints": self._build_foreshadowing_debt_budget_hints(available_patterns),
            "reader_retention_review_gate_hints": self._build_reader_retention_review_gate_hints(available_patterns),
            "draft_stage_revision_ladder_hints": self._build_draft_stage_revision_ladder_hints(available_patterns),
            "rolling_summary_context_trim_hints": self._build_rolling_summary_context_trim_hints(available_patterns),
            "pairwise_story_comparison_ranking_hints": self._build_pairwise_story_comparison_ranking_hints(available_patterns),
            "multidimensional_quality_rubric_hints": self._build_multidimensional_quality_rubric_hints(available_patterns),
            "story_theory_beat_evaluation_hints": self._build_story_theory_beat_evaluation_hints(available_patterns),
            "constraint_specificity_creativity_benchmark_hints": self._build_constraint_specificity_creativity_benchmark_hints(available_patterns),
            "style_axis_diversity_fingerprint_hints": self._build_style_axis_diversity_fingerprint_hints(available_patterns),
            "event_outline_history_compression_hints": self._build_event_outline_history_compression_hints(available_patterns),
            "agentic_story_world_simulation_hints": self._build_agentic_story_world_simulation_hints(available_patterns),
            "reader_rating_signal_model_hints": self._build_reader_rating_signal_model_hints(available_patterns),
            "review_spoiler_sentiment_corpus_hints": self._build_review_spoiler_sentiment_corpus_hints(available_patterns),
            "beta_reader_archetype_panel_hints": self._build_beta_reader_archetype_panel_hints(available_patterns),
            "comp_title_market_positioning_hints": self._build_comp_title_market_positioning_hints(available_patterns),
            "local_reader_experience_editor_hints": self._build_local_reader_experience_editor_hints(available_patterns),
            "delivery_manuscript_assembly_hints": self._build_delivery_manuscript_assembly_hints(available_patterns),
            "export_format_fidelity_audit_hints": self._build_export_format_fidelity_audit_hints(available_patterns),
            "preview_toc_packaging_hints": self._build_preview_toc_packaging_hints(available_patterns),
            "cover_kdp_metadata_boundary_hints": self._build_cover_kdp_metadata_boundary_hints(available_patterns),
            "branching_choice_graph_hints": self._build_branching_choice_graph_hints(available_patterns),
            "node_dialogue_state_machine_hints": self._build_node_dialogue_state_machine_hints(available_patterns),
            "passage_link_navigation_map_hints": self._build_passage_link_navigation_map_hints(available_patterns),
            "choice_stats_consequence_gate_hints": self._build_choice_stats_consequence_gate_hints(available_patterns),
            "source_text_fingerprint_gate_hints": self._build_source_text_fingerprint_gate_hints(available_patterns),
            "fuzzy_phrase_similarity_gate_hints": self._build_fuzzy_phrase_similarity_gate_hints(available_patterns),
            "diff_span_copy_review_hints": self._build_diff_span_copy_review_hints(available_patterns),
            "minhash_lsh_near_duplicate_gate_hints": self._build_minhash_lsh_near_duplicate_gate_hints(available_patterns),
            "simhash_hamming_similarity_gate_hints": self._build_simhash_hamming_similarity_gate_hints(available_patterns),
            "semantic_duplicate_cluster_gate_hints": self._build_semantic_duplicate_cluster_gate_hints(available_patterns),
            "embedding_similarity_independence_gate_hints": self._build_embedding_similarity_independence_gate_hints(available_patterns),
            "corpus_leakage_dedup_review_gate_hints": self._build_corpus_leakage_dedup_review_gate_hints(available_patterns),
            "character_quote_attribution_map_hints": self._build_character_quote_attribution_map_hints(available_patterns),
            "readability_pacing_metric_gate_hints": self._build_readability_pacing_metric_gate_hints(available_patterns),
            "prose_lint_style_rule_gate_hints": self._build_prose_lint_style_rule_gate_hints(available_patterns),
            "grammar_spelling_copyedit_gate_hints": self._build_grammar_spelling_copyedit_gate_hints(available_patterns),
            "copyedit_diagnostic_triage_queue_hints": self._build_copyedit_diagnostic_triage_queue_hints(available_patterns),
            "lexical_diversity_voice_audit_hints": self._build_lexical_diversity_voice_audit_hints(available_patterns),
            "stylometric_author_fingerprint_gate_hints": self._build_stylometric_author_fingerprint_gate_hints(available_patterns),
            "function_word_syntax_style_gate_hints": self._build_function_word_syntax_style_gate_hints(available_patterns),
            "authorship_attribution_similarity_gate_hints": self._build_authorship_attribution_similarity_gate_hints(available_patterns),
            "style_overfit_regression_gate_hints": self._build_style_overfit_regression_gate_hints(available_patterns),
            "paraphrase_independence_review_gate_hints": self._build_paraphrase_independence_review_gate_hints(available_patterns),
            "keyphrase_motif_extraction_hints": self._build_keyphrase_motif_extraction_hints(available_patterns),
            "chinese_segmentation_keyword_gate_hints": self._build_chinese_segmentation_keyword_gate_hints(available_patterns),
            "chinese_ner_alias_consistency_gate_hints": self._build_chinese_ner_alias_consistency_gate_hints(available_patterns),
            "chinese_text_normalization_gate_hints": self._build_chinese_text_normalization_gate_hints(available_patterns),
            "chinese_error_correction_review_gate_hints": self._build_chinese_error_correction_review_gate_hints(available_patterns),
            "source_format_import_manifest_hints": self._build_source_format_import_manifest_hints(available_patterns),
            "pdf_layout_text_extraction_gate_hints": self._build_pdf_layout_text_extraction_gate_hints(available_patterns),
            "ocr_scanned_page_import_gate_hints": self._build_ocr_scanned_page_import_gate_hints(available_patterns),
            "document_partition_chapter_detection_gate_hints": self._build_document_partition_chapter_detection_gate_hints(available_patterns),
            "import_provenance_checksum_gate_hints": self._build_import_provenance_checksum_gate_hints(available_patterns),
            "epub_structure_validation_gate_hints": self._build_epub_structure_validation_gate_hints(available_patterns),
            "ebook_accessibility_audit_gate_hints": self._build_ebook_accessibility_audit_gate_hints(available_patterns),
            "front_back_matter_metadata_gate_hints": self._build_front_back_matter_metadata_gate_hints(available_patterns),
            "toc_navigation_consistency_gate_hints": self._build_toc_navigation_consistency_gate_hints(available_patterns),
            "agentic_editorial_pipeline_gate_hints": self._build_agentic_editorial_pipeline_gate_hints(available_patterns),
            "chapter_state_archive_ladder_hints": self._build_chapter_state_archive_ladder_hints(available_patterns),
            "section_metadata_traceability_gate_hints": self._build_section_metadata_traceability_gate_hints(available_patterns),
            "ai_prose_fingerprint_cluster_gate_hints": self._build_ai_prose_fingerprint_cluster_gate_hints(available_patterns),
            "author_candidate_canon_confirmation_gate_hints": self._build_author_candidate_canon_confirmation_gate_hints(available_patterns),
            "progressive_spoiler_context_window_gate_hints": self._build_progressive_spoiler_context_window_gate_hints(available_patterns),
            "chapter_control_card_writeback_gate_hints": self._build_chapter_control_card_writeback_gate_hints(available_patterns),
            "trace_replay_revision_workspace_gate_hints": self._build_trace_replay_revision_workspace_gate_hints(available_patterns),
            "relationship_graph_global_replace_gate_hints": self._build_relationship_graph_global_replace_gate_hints(available_patterns),
            "bookrun_audit_trail_gate_hints": self._build_bookrun_audit_trail_gate_hints(available_patterns),
            "provider_budget_smoke_gate_hints": self._build_provider_budget_smoke_gate_hints(available_patterns),
            "sidecar_memory_profile_boundary_hints": self._build_sidecar_memory_profile_boundary_hints(available_patterns),
            "outline_checkpoint_milestone_gate_hints": self._build_outline_checkpoint_milestone_gate_hints(available_patterns),
            "language_localization_style_profile_gate_hints": self._build_language_localization_style_profile_gate_hints(available_patterns),
            "progressive_disclosure_skill_protocol_gate_hints": self._build_progressive_disclosure_skill_protocol_gate_hints(available_patterns),
            "anti_slop_rulepack_triage_gate_hints": self._build_anti_slop_rulepack_triage_gate_hints(available_patterns),
            "user_modifier_project_blueprint_gate_hints": self._build_user_modifier_project_blueprint_gate_hints(available_patterns),
            "portable_canon_skill_runtime_gate_hints": self._build_portable_canon_skill_runtime_gate_hints(available_patterns),
            "staged_outline_chunk_window_gate_hints": self._build_staged_outline_chunk_window_gate_hints(available_patterns),
            "wiki_canon_graph_lint_gate_hints": self._build_wiki_canon_graph_lint_gate_hints(available_patterns),
            "plan_draft_log_verify_loop_gate_hints": self._build_plan_draft_log_verify_loop_gate_hints(available_patterns),
            "mcp_scene_index_revision_boundary_hints": self._build_mcp_scene_index_revision_boundary_hints(available_patterns),
            "verbalized_sampling_diversity_wiki_gate_hints": self._build_verbalized_sampling_diversity_wiki_gate_hints(available_patterns),
            "literary_event_entity_annotation_gate_hints": self._build_literary_event_entity_annotation_gate_hints(available_patterns),
            "narrative_event_evolution_graph_gate_hints": self._build_narrative_event_evolution_graph_gate_hints(available_patterns),
            "sentiment_arc_emotion_trajectory_gate_hints": self._build_sentiment_arc_emotion_trajectory_gate_hints(available_patterns),
            "cross_context_coreference_gate_hints": self._build_cross_context_coreference_gate_hints(available_patterns),
            "character_interaction_network_gate_hints": self._build_character_interaction_network_gate_hints(available_patterns),
            "semantic_chunk_boundary_map_hints": self._build_semantic_chunk_boundary_map_hints(available_patterns),
            "chapter_summary_anchor_gate_hints": self._build_chapter_summary_anchor_gate_hints(available_patterns),
            "topic_drift_map_hints": self._build_topic_drift_map_hints(available_patterns),
            "context_faithfulness_eval_gate_hints": self._build_context_faithfulness_eval_gate_hints(available_patterns),
            "retrieval_trace_observability_gate_hints": self._build_retrieval_trace_observability_gate_hints(available_patterns),
            "prompt_regression_eval_suite_hints": self._build_prompt_regression_eval_suite_hints(available_patterns),
            "agentwrite_plan_write_pipeline_hints": self._build_agentwrite_plan_write_pipeline_hints(available_patterns),
            "long_output_length_quality_ruler_hints": self._build_long_output_length_quality_ruler_hints(available_patterns),
            "long_context_reward_dimension_gate_hints": self._build_long_context_reward_dimension_gate_hints(available_patterns),
            "instance_specific_writing_criteria_gate_hints": self._build_instance_specific_writing_criteria_gate_hints(available_patterns),
            "material_grounded_query_refinement_hints": self._build_material_grounded_query_refinement_hints(available_patterns),
            "hybrid_rubric_pairwise_elo_judge_hints": self._build_hybrid_rubric_pairwise_elo_judge_hints(available_patterns),
            "judge_bias_mitigation_check_hints": self._build_judge_bias_mitigation_check_hints(available_patterns),
            "plan_reflect_character_chapter_pipeline_hints": self._build_plan_reflect_character_chapter_pipeline_hints(available_patterns),
            "human_story_metric_panel_hints": self._build_human_story_metric_panel_hints(available_patterns),
            "hierarchical_cowriting_story_scaffold_hints": self._build_hierarchical_cowriting_story_scaffold_hints(available_patterns),
            "human_coauthor_edit_boundary_hints": self._build_human_coauthor_edit_boundary_hints(available_patterns),
            "recursive_reprompt_revision_loop_hints": self._build_recursive_reprompt_revision_loop_hints(available_patterns),
            "reranker_guided_candidate_selection_hints": self._build_reranker_guided_candidate_selection_hints(available_patterns),
            "character_dialogue_persona_memory_hints": self._build_character_dialogue_persona_memory_hints(available_patterns),
            "event_to_sentence_realization_trace_hints": self._build_event_to_sentence_realization_trace_hints(available_patterns),
            "entity_memory_slotfill_grounding_hints": self._build_entity_memory_slotfill_grounding_hints(available_patterns),
            "book_memory_bank_context_lattice_hints": self._build_book_memory_bank_context_lattice_hints(available_patterns),
            "spec_driven_fiction_scene_tasks_hints": self._build_spec_driven_fiction_scene_tasks_hints(available_patterns),
            "toc_aware_source_deconstruction_hints": self._build_toc_aware_source_deconstruction_hints(available_patterns),
            "two_pass_context_glossary_pipeline_hints": self._build_two_pass_context_glossary_pipeline_hints(available_patterns),
            "inline_author_edit_markup_versioning_hints": self._build_inline_author_edit_markup_versioning_hints(available_patterns),
            "causal_dramatica_agent_pipeline_hints": self._build_causal_dramatica_agent_pipeline_hints(available_patterns),
            "capture_distillation_production_gate_hints": self._build_capture_distillation_production_gate_hints(available_patterns),
            "skill_orchestrated_chinese_novel_workflow_hints": self._build_skill_orchestrated_chinese_novel_workflow_hints(available_patterns),
            "langgraph_story_state_machine_hints": self._build_langgraph_story_state_machine_hints(available_patterns),
            "story_daemon_evolution_loop_hints": self._build_story_daemon_evolution_loop_hints(available_patterns),
            "local_rag_writing_ide_gate_hints": self._build_local_rag_writing_ide_gate_hints(available_patterns),
            "canon_drift_continuity_qa_gate_hints": self._build_canon_drift_continuity_qa_gate_hints(available_patterns),
            "patch_replay_manuscript_state_gate_hints": self._build_patch_replay_manuscript_state_gate_hints(available_patterns),
            "microkernel_skill_plugin_isolation_gate_hints": self._build_microkernel_skill_plugin_isolation_gate_hints(available_patterns),
            "interactive_reader_writer_loop_gate_hints": self._build_interactive_reader_writer_loop_gate_hints(available_patterns),
            "abstract_style_learning_skill_gate_hints": self._build_abstract_style_learning_skill_gate_hints(available_patterns),
            "impromptu_thread_pool_chapter_gate_hints": self._build_impromptu_thread_pool_chapter_gate_hints(available_patterns),
            "offline_inspiration_bank_style_gate_hints": self._build_offline_inspiration_bank_style_gate_hints(available_patterns),
            "atelier_phase_pipeline_gate_hints": self._build_atelier_phase_pipeline_gate_hints(available_patterns),
            "book_mining_genesis_automation_gate_hints": self._build_book_mining_genesis_automation_gate_hints(available_patterns),
            "multi_book_autopilot_studio_gate_hints": self._build_multi_book_autopilot_studio_gate_hints(available_patterns),
            "longrun_commit_projection_health_gate_hints": self._build_longrun_commit_projection_health_gate_hints(available_patterns),
            "fresh_context_chapter_iteration_gate_hints": self._build_fresh_context_chapter_iteration_gate_hints(available_patterns),
            "reader_reward_channel_gate_hints": self._build_reader_reward_channel_gate_hints(available_patterns),
            "tri_modal_workflow_validation_gate_hints": self._build_tri_modal_workflow_validation_gate_hints(available_patterns),
            "scene_promise_mob_review_gate_hints": self._build_scene_promise_mob_review_gate_hints(available_patterns),
            "webnovel_genre_tracker_gate_hints": self._build_webnovel_genre_tracker_gate_hints(available_patterns),
            "simulation_causal_ledger_verification_gate_hints": self._build_simulation_causal_ledger_verification_gate_hints(available_patterns),
            "writer_git_exploration_review_gate_hints": self._build_writer_git_exploration_review_gate_hints(available_patterns),
            "narrative_qa_comprehension_gate_hints": self._build_narrative_qa_comprehension_gate_hints(available_patterns),
            "chapter_summary_alignment_gate_hints": self._build_chapter_summary_alignment_gate_hints(available_patterns),
            "story_question_answer_validation_gate_hints": self._build_story_question_answer_validation_gate_hints(available_patterns),
            "causal_why_explanation_gate_hints": self._build_causal_why_explanation_gate_hints(available_patterns),
            "story_commonsense_consistency_gate_hints": self._build_story_commonsense_consistency_gate_hints(available_patterns),
            "query_focused_long_summary_gate_hints": self._build_query_focused_long_summary_gate_hints(available_patterns),
            "temporal_canon_context_graph_hints": self._build_temporal_canon_context_graph_hints(available_patterns),
            "long_term_author_preference_memory_hints": self._build_long_term_author_preference_memory_hints(available_patterns),
            "community_graph_source_deconstruction_hints": self._build_community_graph_source_deconstruction_hints(available_patterns),
            "dual_level_graph_vector_retrieval_hints": self._build_dual_level_graph_vector_retrieval_hints(available_patterns),
            "schema_guided_graph_extraction_hints": self._build_schema_guided_graph_extraction_hints(available_patterns),
            "trope_inventory_similarity_gate_hints": self._build_trope_inventory_similarity_gate_hints(available_patterns),
            "trope_graph_expectation_map_hints": self._build_trope_graph_expectation_map_hints(available_patterns),
            "trope_density_novelty_budget_hints": self._build_trope_density_novelty_budget_hints(available_patterns),
            "trope_source_boundary_review_hints": self._build_trope_source_boundary_review_hints(available_patterns),
            "source_license_detection_gate_hints": self._build_source_license_detection_gate_hints(available_patterns),
            "spdx_reuse_compliance_gate_hints": self._build_spdx_reuse_compliance_gate_hints(available_patterns),
            "public_domain_corpus_boundary_hints": self._build_public_domain_corpus_boundary_hints(available_patterns),
            "attribution_derivative_work_gate_hints": self._build_attribution_derivative_work_gate_hints(available_patterns),
            "source_entity_redaction_gate_hints": self._build_source_entity_redaction_gate_hints(available_patterns),
            "custom_entity_label_inventory_hints": self._build_custom_entity_label_inventory_hints(available_patterns),
            "placeholder_alias_consistency_map_hints": self._build_placeholder_alias_consistency_map_hints(available_patterns),
            "proper_noun_leakage_review_hints": self._build_proper_noun_leakage_review_hints(available_patterns),
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
            "plain_text_project_storage": 36,
            "synopsis_cross_reference": 38,
            "snowflake_premise_expansion": 54,
            "outliner_index_cards": 53,
            "narrative_strand_mapping": 52,
            "character_depth_interview": 58,
            "mindmap_visual_planning": 37,
            "manuscript_export_formats": 24,
            "human_synopsis_gate": 62,
            "retrieval_guided_span_rewrite": 61,
            "runtime_artifact_trace": 55,
            "schema_validated_state_delta": 57,
            "recursive_adaptive_planning": 56,
            "workflow_manuscript_compilation": 34,
            "writing_session_goal_tracking": 23,
            "inspectable_run_workspace": 40,
            "craft_role_pipeline": 58,
            "frontmatter_story_schema": 50,
            "continuity_bridge_window": 66,
            "episode_range_rewrite_scope": 47,
            "voice_table_polish_axis": 59,
            "boring_opening_quality_gates": 57,
            "beat_strand_framework": 56,
            "anti_hallucination_plan_check": 65,
            "backup_restore_checkpoint": 46,
            "multi_level_review_trend": 60,
            "editor_notes_feedback_loop": 55,
            "genre_parameterized_worldbuilding": 54,
            "prose_preflight_voice_calibration": 52,
            "sourcebook_author_workbench": 49,
            "semantic_long_context_search": 61,
            "contradiction_taxonomy_checker": 67,
            "parallel_agent_chapter_pipeline": 62,
            "cross_chapter_redundancy_audit": 64,
            "humanization_stylometry_levers": 43,
            "author_control_boundary": 41,
            "research_taxonomy_story_map": 30,
            "novel_to_multimodal_pipeline": 36,
            "entity_to_visual_asset_pipeline": 44,
            "agentic_book_planner_pipeline": 60,
            "rag_synopsis_spine": 63,
            "anti_repetition_prompt_rules": 58,
            "prompt_recipe_experiment_grid": 39,
            "append_only_generation_review_log": 42,
            "narrative_arc_template_control": 53,
            "nrd_task_tree_pipeline": 59,
            "sampling_parameter_quality_sweep": 37,
            "story_structure_rag_planning": 52,
            "story_contract_commit_chain": 68,
            "fact_snapshot_delta_gate": 67,
            "projection_sync_observability": 60,
            "foreshadowing_debt_budget": 62,
            "reader_retention_review_gate": 61,
            "draft_stage_revision_ladder": 56,
            "rolling_summary_context_trim": 59,
            "pairwise_story_comparison_ranking": 58,
            "multidimensional_quality_rubric": 57,
            "story_theory_beat_evaluation": 56,
            "constraint_specificity_creativity_benchmark": 54,
            "style_axis_diversity_fingerprint": 55,
            "event_outline_history_compression": 60,
            "agentic_story_world_simulation": 49,
            "reader_rating_signal_model": 58,
            "review_spoiler_sentiment_corpus": 57,
            "beta_reader_archetype_panel": 62,
            "comp_title_market_positioning": 54,
            "local_reader_experience_editor": 59,
            "delivery_manuscript_assembly": 61,
            "export_format_fidelity_audit": 55,
            "preview_toc_packaging": 48,
            "cover_kdp_metadata_boundary": 34,
            "branching_choice_graph": 57,
            "node_dialogue_state_machine": 56,
            "passage_link_navigation_map": 49,
            "choice_stats_consequence_gate": 58,
            "source_text_fingerprint_gate": 63,
            "fuzzy_phrase_similarity_gate": 62,
            "diff_span_copy_review": 61,
            "minhash_lsh_near_duplicate_gate": 65,
            "simhash_hamming_similarity_gate": 64,
            "semantic_duplicate_cluster_gate": 66,
            "embedding_similarity_independence_gate": 66,
            "corpus_leakage_dedup_review_gate": 65,
            "character_quote_attribution_map": 66,
            "readability_pacing_metric_gate": 60,
            "prose_lint_style_rule_gate": 61,
            "grammar_spelling_copyedit_gate": 60,
            "copyedit_diagnostic_triage_queue": 59,
            "lexical_diversity_voice_audit": 59,
            "stylometric_author_fingerprint_gate": 66,
            "function_word_syntax_style_gate": 64,
            "authorship_attribution_similarity_gate": 66,
            "style_overfit_regression_gate": 67,
            "paraphrase_independence_review_gate": 67,
            "keyphrase_motif_extraction": 58,
            "chinese_segmentation_keyword_gate": 62,
            "chinese_ner_alias_consistency_gate": 63,
            "chinese_text_normalization_gate": 58,
            "chinese_error_correction_review_gate": 60,
            "source_format_import_manifest": 64,
            "pdf_layout_text_extraction_gate": 63,
            "ocr_scanned_page_import_gate": 61,
            "document_partition_chapter_detection_gate": 64,
            "import_provenance_checksum_gate": 62,
            "epub_structure_validation_gate": 64,
            "ebook_accessibility_audit_gate": 63,
            "front_back_matter_metadata_gate": 62,
            "toc_navigation_consistency_gate": 64,
            "agentic_editorial_pipeline_gate": 65,
            "chapter_state_archive_ladder": 66,
            "section_metadata_traceability_gate": 64,
            "ai_prose_fingerprint_cluster_gate": 65,
            "author_candidate_canon_confirmation_gate": 67,
            "progressive_spoiler_context_window_gate": 66,
            "chapter_control_card_writeback_gate": 67,
            "trace_replay_revision_workspace_gate": 64,
            "relationship_graph_global_replace_gate": 64,
            "bookrun_audit_trail_gate": 68,
            "provider_budget_smoke_gate": 65,
            "sidecar_memory_profile_boundary": 64,
            "outline_checkpoint_milestone_gate": 67,
            "language_localization_style_profile_gate": 62,
            "progressive_disclosure_skill_protocol_gate": 66,
            "anti_slop_rulepack_triage_gate": 63,
            "user_modifier_project_blueprint_gate": 59,
            "portable_canon_skill_runtime_gate": 66,
            "staged_outline_chunk_window_gate": 67,
            "wiki_canon_graph_lint_gate": 64,
            "plan_draft_log_verify_loop_gate": 65,
            "mcp_scene_index_revision_boundary": 63,
            "verbalized_sampling_diversity_wiki_gate": 58,
            "literary_event_entity_annotation_gate": 66,
            "narrative_event_evolution_graph_gate": 65,
            "sentiment_arc_emotion_trajectory_gate": 62,
            "cross_context_coreference_gate": 64,
            "character_interaction_network_gate": 63,
            "semantic_chunk_boundary_map": 62,
            "chapter_summary_anchor_gate": 61,
            "topic_drift_map": 60,
            "context_faithfulness_eval_gate": 64,
            "retrieval_trace_observability_gate": 63,
            "prompt_regression_eval_suite": 62,
            "agentwrite_plan_write_pipeline": 65,
            "long_output_length_quality_ruler": 64,
            "long_context_reward_dimension_gate": 63,
            "instance_specific_writing_criteria_gate": 66,
            "material_grounded_query_refinement": 64,
            "hybrid_rubric_pairwise_elo_judge": 65,
            "judge_bias_mitigation_check": 63,
            "plan_reflect_character_chapter_pipeline": 66,
            "human_story_metric_panel": 64,
            "hierarchical_cowriting_story_scaffold": 67,
            "human_coauthor_edit_boundary": 64,
            "recursive_reprompt_revision_loop": 67,
            "reranker_guided_candidate_selection": 64,
            "character_dialogue_persona_memory": 66,
            "event_to_sentence_realization_trace": 65,
            "entity_memory_slotfill_grounding": 64,
            "book_memory_bank_context_lattice": 67,
            "spec_driven_fiction_scene_tasks": 66,
            "toc_aware_source_deconstruction": 65,
            "two_pass_context_glossary_pipeline": 64,
            "inline_author_edit_markup_versioning": 63,
            "inline_human_machine_coauthoring_gate": 66,
            "hierarchical_orchestrator_generation_gate": 68,
            "batch_continuation_progress_queue_gate": 66,
            "homogeneity_prompt_variation_gate": 65,
            "local_author_data_boundary_gate": 67,
            "prompt_preset_variable_library_gate": 63,
            "imported_manuscript_migration_outline_gate": 66,
            "style_dna_reference_library_gate": 67,
            "draft_candidate_promotion_gate": 69,
            "privacy_preserving_local_index_gate": 64,
            "chapter_description_continuity_bridge_gate": 67,
            "selective_streaming_regeneration_gate": 65,
            "research_citation_boundary_gate": 66,
            "beta_reader_summary_context_gate": 68,
            "style_vocab_world_card_extraction_gate": 69,
            "prompt_only_decay_ceiling_gate": 64,
            "serial_platform_minimum_audit_gate": 67,
            "multi_agent_reject_retry_review_gate": 69,
            "story_bible_context_packet_branch_gate": 69,
            "memory_augmented_delta_verification_gate": 70,
            "statistical_style_benchmark_rewrite_gate": 68,
            "causal_dramatica_agent_pipeline": 68,
            "capture_distillation_production_gate": 66,
            "skill_orchestrated_chinese_novel_workflow": 67,
            "langgraph_story_state_machine": 65,
            "story_daemon_evolution_loop": 65,
            "local_rag_writing_ide_gate": 68,
            "canon_drift_continuity_qa_gate": 70,
            "patch_replay_manuscript_state_gate": 66,
            "microkernel_skill_plugin_isolation_gate": 65,
            "interactive_reader_writer_loop_gate": 64,
            "abstract_style_learning_skill_gate": 69,
            "impromptu_thread_pool_chapter_gate": 68,
            "offline_inspiration_bank_style_gate": 67,
            "atelier_phase_pipeline_gate": 66,
            "book_mining_genesis_automation_gate": 70,
            "multi_book_autopilot_studio_gate": 66,
            "longrun_commit_projection_health_gate": 68,
            "fresh_context_chapter_iteration_gate": 67,
            "reader_reward_channel_gate": 65,
            "tri_modal_workflow_validation_gate": 67,
            "scene_promise_mob_review_gate": 67,
            "webnovel_genre_tracker_gate": 66,
            "simulation_causal_ledger_verification_gate": 69,
            "writer_git_exploration_review_gate": 64,
            "narrative_qa_comprehension_gate": 70,
            "chapter_summary_alignment_gate": 69,
            "story_question_answer_validation_gate": 68,
            "causal_why_explanation_gate": 70,
            "story_commonsense_consistency_gate": 67,
            "query_focused_long_summary_gate": 67,
            "temporal_canon_context_graph": 68,
            "long_term_author_preference_memory": 64,
            "community_graph_source_deconstruction": 66,
            "dual_level_graph_vector_retrieval": 65,
            "schema_guided_graph_extraction": 66,
            "trope_inventory_similarity_gate": 66,
            "trope_graph_expectation_map": 63,
            "trope_density_novelty_budget": 62,
            "trope_source_boundary_review": 65,
            "source_license_detection_gate": 68,
            "spdx_reuse_compliance_gate": 67,
            "public_domain_corpus_boundary": 66,
            "attribution_derivative_work_gate": 66,
            "source_entity_redaction_gate": 67,
            "custom_entity_label_inventory": 66,
            "placeholder_alias_consistency_map": 65,
            "proper_noun_leakage_review": 67,
            "mode_contract_generation_gate": 66,
            "source_study_method_bank_isolation_gate": 66,
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
        if "mode_contract_generation_gate" in patterns:
            targets.append("generation_mode_contracts")
            targets.append("mode_axis_validation_rules")
        if "source_study_method_bank_isolation_gate" in patterns:
            targets.append("source_study_method_bank")
            targets.append("source_study_contamination_policy")
        if "inline_human_machine_coauthoring_gate" in patterns:
            targets.append("inline_revision_policy")
            targets.append("author_acceptance_diff_rules")
        if "hierarchical_orchestrator_generation_gate" in patterns:
            targets.append("hierarchical_generation_plan")
            targets.append("orchestrator_stage_contracts")
        if "batch_continuation_progress_queue_gate" in patterns:
            targets.append("batch_continuation_queue")
            targets.append("progress_tracking_policy")
        if "homogeneity_prompt_variation_gate" in patterns:
            targets.append("homogeneity_variation_policy")
            targets.append("prompt_variation_axes")
        if "local_author_data_boundary_gate" in patterns:
            targets.append("local_author_data_boundary")
            targets.append("update_surface_review_policy")
        if "prompt_preset_variable_library_gate" in patterns:
            targets.append("prompt_preset_registry")
            targets.append("prompt_variable_schema")
        if "imported_manuscript_migration_outline_gate" in patterns:
            targets.append("imported_manuscript_manifest")
            targets.append("migration_outline_policy")
        if "style_dna_reference_library_gate" in patterns:
            targets.append("style_dna_reference_library")
            targets.append("style_abstraction_policy")
        if "draft_candidate_promotion_gate" in patterns:
            targets.append("draft_candidate_state_policy")
            targets.append("confirmed_chapter_promotion_rules")
        if "privacy_preserving_local_index_gate" in patterns:
            targets.append("local_index_privacy_policy")
            targets.append("metadata_only_search_scope")
        if "chapter_description_continuity_bridge_gate" in patterns:
            targets.append("chapter_description_contracts")
            targets.append("previous_chapter_summary_policy")
        if "selective_streaming_regeneration_gate" in patterns:
            targets.append("selective_regeneration_policy")
            targets.append("streaming_checkpoint_policy")
        if "research_citation_boundary_gate" in patterns:
            targets.append("research_citation_policy")
            targets.append("source_evidence_manifest")
        if "beta_reader_summary_context_gate" in patterns:
            targets.append("beta_reader_feedback_styles")
            targets.append("summary_context_review_policy")
        if "style_vocab_world_card_extraction_gate" in patterns:
            targets.append("style_vocabulary_library")
            targets.append("world_card_extraction_policy")
        if "prompt_only_decay_ceiling_gate" in patterns:
            targets.append("prompt_only_decay_policy")
            targets.append("wrap_up_mode_boundary")
        if "serial_platform_minimum_audit_gate" in patterns:
            targets.append("minimum_chapter_audit_set")
            targets.append("serial_platform_audit_cadence")
        if "multi_agent_reject_retry_review_gate" in patterns:
            targets.append("multi_agent_retry_review_policy")
            targets.append("reject_retry_budget")
        if "story_bible_context_packet_branch_gate" in patterns:
            targets.append("story_bible_context_packet")
            targets.append("branch_savepoint_policy")
        if "memory_augmented_delta_verification_gate" in patterns:
            targets.append("delta_fact_index")
            targets.append("chain_of_verification_policy")
        if "statistical_style_benchmark_rewrite_gate" in patterns:
            targets.append("statistical_style_benchmark_policy")
            targets.append("style_benchmark_thresholds")
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
        if "trope_inventory_similarity_gate" in patterns:
            targets.append("trope_inventory_baseline")
            targets.append("trope_similarity_thresholds")
        if "trope_graph_expectation_map" in patterns:
            targets.append("trope_graph_expectation_map")
        if "trope_density_novelty_budget" in patterns:
            targets.append("trope_density_novelty_budget")
        if "trope_source_boundary_review" in patterns:
            targets.append("trope_source_boundary_policy")
        if "source_license_detection_gate" in patterns:
            targets.append("source_license_manifest")
            targets.append("license_detection_review_policy")
        if "spdx_reuse_compliance_gate" in patterns:
            targets.append("spdx_reuse_manifest")
            targets.append("file_copyright_attribution_ledger")
        if "public_domain_corpus_boundary" in patterns:
            targets.append("public_domain_source_manifest")
            targets.append("source_jurisdiction_review_policy")
        if "attribution_derivative_work_gate" in patterns:
            targets.append("attribution_derivative_policy")
            targets.append("licensed_source_usage_boundary")
        if "source_entity_redaction_gate" in patterns:
            targets.append("source_entity_redaction_manifest")
            targets.append("entity_leakage_review_policy")
        if "custom_entity_label_inventory" in patterns:
            targets.append("custom_fiction_entity_label_set")
            targets.append("source_entity_inventory")
        if "placeholder_alias_consistency_map" in patterns:
            targets.append("placeholder_alias_map")
            targets.append("replacement_consistency_policy")
        if "proper_noun_leakage_review" in patterns:
            targets.append("proper_noun_blocklist")
            targets.append("proper_noun_allowlist")
        if "canon_drift_continuity_qa_gate" in patterns:
            targets.append("canon_drift_rulebook")
            targets.append("continuity_qa_checklist")
        if "local_rag_writing_ide_gate" in patterns:
            targets.append("local_rag_material_scope")
            targets.append("retrieval_context_boundary")
        if "patch_replay_manuscript_state_gate" in patterns:
            targets.append("patch_replay_manifest")
            targets.append("manuscript_version_snapshot_rules")
        if "microkernel_skill_plugin_isolation_gate" in patterns:
            targets.append("plugin_isolation_policy")
            targets.append("skill_event_bus_contract")
        if "interactive_reader_writer_loop_gate" in patterns:
            targets.append("reader_writer_interaction_log")
            targets.append("chapter_file_acceptance_state")
        if "abstract_style_learning_skill_gate" in patterns:
            targets.append("abstract_style_skill_profile")
            targets.append("style_sample_boundary_rules")
        if "impromptu_thread_pool_chapter_gate" in patterns:
            targets.append("open_thread_pool_schema")
            targets.append("single_chapter_blueprint_rules")
        if "offline_inspiration_bank_style_gate" in patterns:
            targets.append("inspiration_bank_scope_policy")
            targets.append("offline_style_mimicry_boundary_rules")
        if "atelier_phase_pipeline_gate" in patterns:
            targets.append("atelier_phase_manifest")
            targets.append("beat_tree_hook_audit_rules")
        if "book_mining_genesis_automation_gate" in patterns:
            targets.append("book_mining_pattern_library_manifest")
            targets.append("canon_seed_handoff_schema")
        if "multi_book_autopilot_studio_gate" in patterns:
            targets.append("multi_book_profile_boundary")
            targets.append("autopilot_stop_condition_policy")
        if "longrun_commit_projection_health_gate" in patterns:
            targets.append("chapter_commit_projection_manifest")
            targets.append("read_model_health_policy")
        if "fresh_context_chapter_iteration_gate" in patterns:
            targets.append("fresh_context_iteration_manifest")
            targets.append("chapter_progress_log_policy")
        if "narrative_qa_comprehension_gate" in patterns:
            targets.append("narrative_question_answer_ledger")
            targets.append("source_summary_question_coverage_policy")
        if "chapter_summary_alignment_gate" in patterns:
            targets.append("chapter_summary_alignment_policy")
            targets.append("book_level_summary_drift_rules")
        if "story_question_answer_validation_gate" in patterns:
            targets.append("story_element_qa_schema")
            targets.append("section_grounding_evidence_policy")
        if "causal_why_explanation_gate" in patterns:
            targets.append("causal_why_answer_ledger")
            targets.append("helpful_sentence_grounding_policy")
        if "story_commonsense_consistency_gate" in patterns:
            targets.append("character_psychology_consistency_policy")
            targets.append("motivation_emotion_state_ledger")
        if "query_focused_long_summary_gate" in patterns:
            targets.append("query_focused_summary_policy")
            targets.append("multi_reference_summary_review_rules")
        if "epub_structure_validation_gate" in patterns:
            targets.append("epub_validation_policy")
            targets.append("opf_manifest_spine_policy")
        if "ebook_accessibility_audit_gate" in patterns:
            targets.append("ebook_accessibility_policy")
            targets.append("accessibility_metadata_policy")
        if "front_back_matter_metadata_gate" in patterns:
            targets.append("front_back_matter_manifest")
            targets.append("publication_metadata_policy")
        if "toc_navigation_consistency_gate" in patterns:
            targets.append("toc_navigation_policy")
            targets.append("spine_nav_heading_policy")
        if "agentic_editorial_pipeline_gate" in patterns:
            targets.append("editorial_role_manifest")
            targets.append("author_decision_boundary_policy")
        if "chapter_state_archive_ladder" in patterns:
            targets.append("chapter_state_archive_policy")
            targets.append("permanent_bible_transient_state_boundary")
        if "section_metadata_traceability_gate" in patterns:
            targets.append("section_metadata_schema")
            targets.append("cast_location_item_section_index")
        if "ai_prose_fingerprint_cluster_gate" in patterns:
            targets.append("ai_prose_fingerprint_scan_policy")
            targets.append("fingerprint_exception_ledger")
        if "author_candidate_canon_confirmation_gate" in patterns:
            targets.append("candidate_canon_confirmation_policy")
            targets.append("preview_confirm_apply_review_log")
        if "progressive_spoiler_context_window_gate" in patterns:
            targets.append("spoiler_context_window_policy")
            targets.append("stage_aware_future_context_limits")
        if "chapter_control_card_writeback_gate" in patterns:
            targets.append("chapter_control_card_schema")
            targets.append("dynamic_state_writeback_policy")
        if "trace_replay_revision_workspace_gate" in patterns:
            targets.append("trace_replay_review_policy")
            targets.append("chapter_revision_workspace_policy")
        if "relationship_graph_global_replace_gate" in patterns:
            targets.append("relationship_graph_update_policy")
            targets.append("global_replace_consistency_policy")
        if "bookrun_audit_trail_gate" in patterns:
            targets.append("bookrun_audit_trail_policy")
            targets.append("judge_repair_acceptance_policy")
        if "provider_budget_smoke_gate" in patterns:
            targets.append("provider_budget_smoke_policy")
            targets.append("llm_profile_budget_limits")
        if "sidecar_memory_profile_boundary" in patterns:
            targets.append("sidecar_memory_boundary_policy")
            targets.append("graph_vector_profile_manifest")
        if "outline_checkpoint_milestone_gate" in patterns:
            targets.append("outline_checkpoint_milestone_policy")
            targets.append("story_bible_truth_source_policy")
        if "language_localization_style_profile_gate" in patterns:
            targets.append("language_style_profile")
            targets.append("localization_rulepack")
        if "progressive_disclosure_skill_protocol_gate" in patterns:
            targets.append("skill_protocol_route_manifest")
            targets.append("progressive_disclosure_loading_policy")
        if "anti_slop_rulepack_triage_gate" in patterns:
            targets.append("anti_slop_rulepack")
            targets.append("prose_rule_triage_policy")
        if "user_modifier_project_blueprint_gate" in patterns:
            targets.append("user_modifier_blueprint_policy")
            targets.append("project_modifier_schema")
        if "portable_canon_skill_runtime_gate" in patterns:
            targets.append("portable_canon_runtime_policy")
            targets.append("canon_asset_frontmatter_contract")
        if "staged_outline_chunk_window_gate" in patterns:
            targets.append("staged_outline_chunk_policy")
            targets.append("sliding_window_memory_policy")
        if "wiki_canon_graph_lint_gate" in patterns:
            targets.append("wiki_canon_lint_policy")
            targets.append("relationship_graph_lint_manifest")
        if "plan_draft_log_verify_loop_gate" in patterns:
            targets.append("plan_draft_log_verify_policy")
            targets.append("living_document_update_policy")
        if "mcp_scene_index_revision_boundary" in patterns:
            targets.append("scene_index_revision_boundary_policy")
            targets.append("revision_confirmation_git_history_policy")
        if "verbalized_sampling_diversity_wiki_gate" in patterns:
            targets.append("verbalized_sampling_diversity_policy")
            targets.append("writer_wiki_autofile_policy")
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
        if "reader_rating_signal_model" in patterns:
            targets.append("reader_rating_signal_map")
            targets.append("shelf_tag_expectation_profile")
        if "review_spoiler_sentiment_corpus" in patterns:
            targets.append("spoiler_sensitive_review_signals")
            targets.append("review_sentiment_clusters")
        if "beta_reader_archetype_panel" in patterns:
            targets.append("beta_reader_archetypes")
            targets.append("want_to_continue_thresholds")
        if "comp_title_market_positioning" in patterns:
            targets.append("comp_title_positioning")
            targets.append("market_gap_statement")
        if "local_reader_experience_editor" in patterns:
            targets.append("reader_experience_prompts")
            targets.append("micro_tension_hook_rules")
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
        if "plain_text_project_storage" in patterns:
            targets.append("manuscript_text_units")
        if "synopsis_cross_reference" in patterns:
            targets.append("synopsis_cross_refs")
        if "snowflake_premise_expansion" in patterns:
            targets.append("snowflake_premise_chain")
        if "outliner_index_cards" in patterns:
            targets.append("index_card_board")
        if "narrative_strand_mapping" in patterns:
            targets.append("narrative_strands")
        if "character_depth_interview" in patterns:
            targets.append("character_depth_questions")
        if "mindmap_visual_planning" in patterns:
            targets.append("mindmap_nodes")
        if "manuscript_export_formats" in patterns:
            targets.append("export_format_targets")
        if "delivery_manuscript_assembly" in patterns:
            targets.append("final_manuscript_assembly_rules")
            targets.append("chapter_header_normalization")
        if "export_format_fidelity_audit" in patterns:
            targets.append("export_fidelity_checks")
        if "preview_toc_packaging" in patterns:
            targets.append("preview_toc_rules")
        if "cover_kdp_metadata_boundary" in patterns:
            targets.append("cover_kdp_metadata")
        if "branching_choice_graph" in patterns:
            targets.append("choice_branch_graph")
            targets.append("branch_decision_points")
        if "node_dialogue_state_machine" in patterns:
            targets.append("dialogue_node_state_machine")
            targets.append("dialogue_entry_exit_deltas")
        if "passage_link_navigation_map" in patterns:
            targets.append("passage_link_navigation_map")
        if "choice_stats_consequence_gate" in patterns:
            targets.append("choice_stats_consequence_ledger")
        if "source_text_fingerprint_gate" in patterns:
            targets.append("source_fingerprint_baseline")
            targets.append("fingerprint_overlap_thresholds")
        if "fuzzy_phrase_similarity_gate" in patterns:
            targets.append("fuzzy_phrase_thresholds")
            targets.append("phrase_similarity_review_rules")
        if "diff_span_copy_review" in patterns:
            targets.append("diff_span_review_rules")
            targets.append("copied_span_rewrite_policy")
        if "minhash_lsh_near_duplicate_gate" in patterns:
            targets.append("minhash_lsh_thresholds")
            targets.append("shingle_window_policy")
        if "simhash_hamming_similarity_gate" in patterns:
            targets.append("simhash_hamming_thresholds")
            targets.append("near_duplicate_window_policy")
        if "semantic_duplicate_cluster_gate" in patterns:
            targets.append("semantic_duplicate_cluster_thresholds")
            targets.append("cluster_false_positive_review_rules")
        if "embedding_similarity_independence_gate" in patterns:
            targets.append("embedding_similarity_independence_thresholds")
            targets.append("nearest_neighbor_review_policy")
        if "corpus_leakage_dedup_review_gate" in patterns:
            targets.append("corpus_leakage_review_policy")
            targets.append("source_corpus_boundary_manifest")
        if "character_quote_attribution_map" in patterns:
            targets.append("character_quote_speaker_map")
            targets.append("alias_mention_index")
        if "readability_pacing_metric_gate" in patterns:
            targets.append("readability_pacing_thresholds")
            targets.append("sentence_paragraph_curve")
        if "prose_lint_style_rule_gate" in patterns:
            targets.append("prose_lint_rule_profile")
            targets.append("house_style_rule_exceptions")
        if "grammar_spelling_copyedit_gate" in patterns:
            targets.append("grammar_spelling_boundary_rules")
            targets.append("dialogue_dialect_exception_policy")
        if "copyedit_diagnostic_triage_queue" in patterns:
            targets.append("copyedit_diagnostic_queue")
            targets.append("accepted_ignored_diagnostic_ledger")
        if "lexical_diversity_voice_audit" in patterns:
            targets.append("lexical_diversity_voice_baseline")
            targets.append("vocabulary_drift_rules")
        if "stylometric_author_fingerprint_gate" in patterns:
            targets.append("stylometric_author_fingerprint_baseline")
            targets.append("style_profile_version_manifest")
        if "function_word_syntax_style_gate" in patterns:
            targets.append("function_word_syntax_style_baseline")
            targets.append("punctuation_sentence_rhythm_rules")
        if "authorship_attribution_similarity_gate" in patterns:
            targets.append("authorship_similarity_thresholds")
            targets.append("source_author_distance_policy")
        if "style_overfit_regression_gate" in patterns:
            targets.append("style_overfit_regression_cases")
            targets.append("style_drift_window_thresholds")
        if "paraphrase_independence_review_gate" in patterns:
            targets.append("paraphrase_independence_review_policy")
            targets.append("style_transfer_boundary_rules")
        if "keyphrase_motif_extraction" in patterns:
            targets.append("keyphrase_motif_ledger")
            targets.append("motif_topic_drift_rules")
        if "chinese_segmentation_keyword_gate" in patterns:
            targets.append("chinese_segmentation_dictionary")
            targets.append("keyword_motif_extraction_profile")
        if "chinese_ner_alias_consistency_gate" in patterns:
            targets.append("chinese_entity_alias_ledger")
            targets.append("character_location_org_name_rules")
        if "chinese_text_normalization_gate" in patterns:
            targets.append("chinese_text_normalization_policy")
            targets.append("simplified_traditional_variant_map")
        if "chinese_error_correction_review_gate" in patterns:
            targets.append("chinese_correction_review_queue")
            targets.append("confusion_set_exception_policy")
        if "source_format_import_manifest" in patterns:
            targets.append("source_import_manifest")
            targets.append("source_toc_spine_map")
        if "pdf_layout_text_extraction_gate" in patterns:
            targets.append("pdf_page_span_map")
            targets.append("layout_reading_order_rules")
        if "ocr_scanned_page_import_gate" in patterns:
            targets.append("ocr_page_confidence_report")
            targets.append("scanned_page_review_queue")
        if "document_partition_chapter_detection_gate" in patterns:
            targets.append("document_element_partition_map")
            targets.append("chapter_heading_detection_rules")
        if "import_provenance_checksum_gate" in patterns:
            targets.append("source_file_checksum_manifest")
            targets.append("import_parser_version_ledger")
        if "literary_event_entity_annotation_gate" in patterns:
            targets.append("literary_entity_event_annotation_schema")
            targets.append("event_participant_role_ledger")
        if "narrative_event_evolution_graph_gate" in patterns:
            targets.append("narrative_event_chain_graph")
            targets.append("event_causality_discourse_edges")
        if "sentiment_arc_emotion_trajectory_gate" in patterns:
            targets.append("sentiment_arc_baseline")
            targets.append("character_emotion_trajectory")
        if "cross_context_coreference_gate" in patterns:
            targets.append("cross_context_coreference_ledger")
            targets.append("mention_cluster_boundary_rules")
        if "character_interaction_network_gate" in patterns:
            targets.append("character_interaction_network")
            targets.append("relationship_polarity_timeline")
        if "semantic_chunk_boundary_map" in patterns:
            targets.append("semantic_chunk_boundary_manifest")
            targets.append("chunk_inclusion_rules")
        if "chapter_summary_anchor_gate" in patterns:
            targets.append("chapter_summary_anchor_index")
            targets.append("representative_sentence_refs")
        if "topic_drift_map" in patterns:
            targets.append("topic_cluster_map")
            targets.append("topic_drift_thresholds")
        if "context_faithfulness_eval_gate" in patterns:
            targets.append("faithfulness_eval_thresholds")
            targets.append("context_grounding_rules")
        if "retrieval_trace_observability_gate" in patterns:
            targets.append("retrieval_trace_schema")
            targets.append("context_selection_reason_rules")
        if "prompt_regression_eval_suite" in patterns:
            targets.append("prompt_regression_suite")
            targets.append("golden_case_dataset")
        if "agentwrite_plan_write_pipeline" in patterns:
            targets.append("agentwrite_plan_artifacts")
            targets.append("agentwrite_write_artifacts")
        if "long_output_length_quality_ruler" in patterns:
            targets.append("long_output_length_targets")
            targets.append("length_quality_ruler_thresholds")
        if "long_context_reward_dimension_gate" in patterns:
            targets.append("long_context_reward_dimensions")
            targets.append("helpfulness_logicality_faithfulness_completeness_scores")
        if "instance_specific_writing_criteria_gate" in patterns:
            targets.append("instance_specific_writing_criteria")
            targets.append("requirement_dimension_coverage_rules")
        if "material_grounded_query_refinement" in patterns:
            targets.append("material_requirement_notes")
            targets.append("material_pruning_rules")
        if "hybrid_rubric_pairwise_elo_judge" in patterns:
            targets.append("creative_judge_rubric")
            targets.append("pairwise_comparison_policy")
        if "judge_bias_mitigation_check" in patterns:
            targets.append("judge_bias_mitigation_rules")
        if "plan_reflect_character_chapter_pipeline" in patterns:
            targets.append("plan_reflection_gate")
            targets.append("character_profile_requirements")
        if "human_story_metric_panel" in patterns:
            targets.append("human_story_metric_axes")
        if "hierarchical_cowriting_story_scaffold" in patterns:
            targets.append("logline_character_plot_location_dialogue_scaffold")
            targets.append("hierarchical_story_layer_rules")
        if "human_coauthor_edit_boundary" in patterns:
            targets.append("human_coauthor_edit_policy")
        if "recursive_reprompt_revision_loop" in patterns:
            targets.append("recursive_reprompt_revision_policy")
            targets.append("plan_draft_rewrite_edit_stage_rules")
        if "reranker_guided_candidate_selection" in patterns:
            targets.append("reranker_candidate_selection_rules")
        if "character_dialogue_persona_memory" in patterns:
            targets.append("character_persona_dialogue_evidence")
            targets.append("tone_personality_plot_chat_boundaries")
        if "event_to_sentence_realization_trace" in patterns:
            targets.append("event_to_sentence_realization_schema")
        if "entity_memory_slotfill_grounding" in patterns:
            targets.append("entity_memory_slotfill_rules")
        if "book_memory_bank_context_lattice" in patterns:
            targets.append("book_memory_bank_manifest")
            targets.append("active_context_progress_rules")
        if "spec_driven_fiction_scene_tasks" in patterns:
            targets.append("fiction_constitution")
            targets.append("scene_task_backlog")
            targets.append("pov_information_asymmetry_map")
        if "toc_aware_source_deconstruction" in patterns:
            targets.append("source_toc_deconstruction_index")
            targets.append("chapter_summary_evidence_schema")
        if "two_pass_context_glossary_pipeline" in patterns:
            targets.append("cumulative_glossary")
            targets.append("previous_chapter_summary_bridge")
        if "inline_author_edit_markup_versioning" in patterns:
            targets.append("inline_author_edit_markup_policy")
            targets.append("revision_version_milestones")
        if "causal_dramatica_agent_pipeline" in patterns:
            targets.append("causal_dramatica_thread_map")
            targets.append("agent_layer_handoff_policy")
        if "capture_distillation_production_gate" in patterns:
            targets.append("capture_distillation_production_packet")
            targets.append("source_to_production_promotion_rules")
        if "skill_orchestrated_chinese_novel_workflow" in patterns:
            targets.append("skill_orchestrated_chinese_workflow_manifest")
            targets.append("webnovel_stage_skill_boundaries")
        if "langgraph_story_state_machine" in patterns:
            targets.append("story_state_machine_schema")
            targets.append("checkpoint_transition_rules")
        if "story_daemon_evolution_loop" in patterns:
            targets.append("story_evolution_loop_policy")
            targets.append("autonomous_agent_acceptance_boundary")
        if "local_rag_writing_ide_gate" in patterns:
            targets.append("local_rag_context_pack_policy")
            targets.append("source_material_retrieval_boundary")
        if "canon_drift_continuity_qa_gate" in patterns:
            targets.append("canon_drift_qa_report")
            targets.append("scene_continuity_context_pack")
        if "patch_replay_manuscript_state_gate" in patterns:
            targets.append("patch_replay_state_log")
            targets.append("version_snapshot_chain")
        if "microkernel_skill_plugin_isolation_gate" in patterns:
            targets.append("plugin_event_stage_map")
            targets.append("plugin_failure_isolation_rules")
        if "interactive_reader_writer_loop_gate" in patterns:
            targets.append("reader_input_to_chapter_trace")
            targets.append("interactive_revision_acceptance_log")
        if "abstract_style_learning_skill_gate" in patterns:
            targets.append("style_abstraction_evidence")
            targets.append("style_overfit_boundary_report")
        if "impromptu_thread_pool_chapter_gate" in patterns:
            targets.append("impromptu_chapter_intent_trace")
            targets.append("open_thread_settlement_report")
        if "offline_inspiration_bank_style_gate" in patterns:
            targets.append("inspiration_bank_retrieval_scope")
            targets.append("style_mimicry_boundary_report")
        if "atelier_phase_pipeline_gate" in patterns:
            targets.append("atelier_phase_handoff_trace")
            targets.append("beat_tree_hook_audit_report")
        if "book_mining_genesis_automation_gate" in patterns:
            targets.append("book_mining_pattern_index")
            targets.append("genesis_scoring_gate_report")
        if "multi_book_autopilot_studio_gate" in patterns:
            targets.append("multi_book_autopilot_session_audit")
            targets.append("periodic_full_book_logic_check_report")
        if "longrun_commit_projection_health_gate" in patterns:
            targets.append("chapter_commit_projection_health_report")
            targets.append("read_model_memory_drift_audit")
        if "fresh_context_chapter_iteration_gate" in patterns:
            targets.append("fresh_context_chapter_loop_audit")
            targets.append("next_incomplete_chapter_manifest")
        if "temporal_canon_context_graph" in patterns:
            targets.append("temporal_canon_graph_schema")
            targets.append("episode_provenance_rules")
        if "long_term_author_preference_memory" in patterns:
            targets.append("author_preference_memory_layers")
            targets.append("session_memory_scope_rules")
        if "community_graph_source_deconstruction" in patterns:
            targets.append("source_entity_community_graph")
            targets.append("community_summary_index")
        if "dual_level_graph_vector_retrieval" in patterns:
            targets.append("graph_vector_retrieval_policy")
            targets.append("local_global_hybrid_query_modes")
        if "schema_guided_graph_extraction" in patterns:
            targets.append("canon_graph_extraction_schema")
            targets.append("source_metadata_link_rules")
        if "human_synopsis_gate" in patterns:
            targets.append("synopsis_review_gate")
        if "retrieval_guided_span_rewrite" in patterns:
            targets.append("retrieval_guided_rewrite_scope")
        if "runtime_artifact_trace" in patterns:
            targets.append("runtime_trace_artifacts")
        if "schema_validated_state_delta" in patterns:
            targets.append("validated_state_delta_schema")
        if "recursive_adaptive_planning" in patterns:
            targets.append("adaptive_planning_tasks")
        if "workflow_manuscript_compilation" in patterns:
            targets.append("manuscript_compilation_workflow")
        if "writing_session_goal_tracking" in patterns:
            targets.append("writing_session_goals")
        if "inspectable_run_workspace" in patterns:
            targets.append("inspectable_run_workspace")
        if "craft_role_pipeline" in patterns:
            targets.append("craft_role_assignments")
        if "frontmatter_story_schema" in patterns:
            targets.append("frontmatter_story_schema")
            targets.append("continuity_question_ledger")
        if "continuity_bridge_window" in patterns:
            targets.append("continuity_bridge_window")
        if "voice_table_polish_axis" in patterns:
            targets.append("voice_table")
        if "beat_strand_framework" in patterns:
            targets.append("beat_strand_map")
        if "anti_hallucination_plan_check" in patterns:
            targets.append("plan_verification_rules")
        if "genre_parameterized_worldbuilding" in patterns:
            targets.append("genre_parameterized_world_rules")
        if "prose_preflight_voice_calibration" in patterns:
            targets.append("voice_calibration_samples")
        if "sourcebook_author_workbench" in patterns:
            targets.append("sourcebook_entries")
            targets.append("author_control_rules")
        if "semantic_long_context_search" in patterns:
            targets.append("semantic_context_index")
        if "contradiction_taxonomy_checker" in patterns:
            targets.append("consistency_bug_taxonomy")
        if "parallel_agent_chapter_pipeline" in patterns:
            targets.append("agent_stage_contracts")
        if "humanization_stylometry_levers" in patterns:
            targets.append("stylometry_polish_rules")
        if "author_control_boundary" in patterns:
            targets.append("human_authority_boundary")
        if "research_taxonomy_story_map" in patterns:
            targets.append("research_taxonomy_map")
        if "novel_to_multimodal_pipeline" in patterns:
            targets.append("multimodal_adaptation_plan")
        if "entity_to_visual_asset_pipeline" in patterns:
            targets.append("entity_visual_asset_refs")
        if "agentic_book_planner_pipeline" in patterns:
            targets.append("agentic_planning_roles")
        if "rag_synopsis_spine" in patterns:
            targets.append("synopsis_spine")
        if "anti_repetition_prompt_rules" in patterns:
            targets.append("anti_repetition_rules")
        if "prompt_recipe_experiment_grid" in patterns:
            targets.append("prompt_recipe_catalog")
        if "append_only_generation_review_log" in patterns:
            targets.append("generation_review_log")
        if "narrative_arc_template_control" in patterns:
            targets.append("narrative_arc_templates")
        if "nrd_task_tree_pipeline" in patterns:
            targets.append("nrd_task_tree")
        if "sampling_parameter_quality_sweep" in patterns:
            targets.append("sampling_quality_grid")
        if "story_structure_rag_planning" in patterns:
            targets.append("story_structure_refs")
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
        if "mode_contract_generation_gate" in patterns:
            targets.extend(["mode_contract_matrix", "axis_tag_validation_report", "under_length_rewrite_trace"])
        if "source_study_method_bank_isolation_gate" in patterns:
            targets.extend(["source_study_method_bank_report", "master_study_contamination_audit", "method_insight_promotion_findings"])
        if "chapter_description_continuity_bridge_gate" in patterns:
            targets.extend(["chapter_description_context_bridge", "previous_chapter_summary_trace", "description_to_draft_continuity_checks"])
        if "selective_streaming_regeneration_gate" in patterns:
            targets.extend(["selective_regeneration_report", "specific_chapter_rewrite_scope", "streaming_checkpoint_recovery"])
        if "research_citation_boundary_gate" in patterns:
            targets.extend(["research_citation_manifest", "evidence_source_scope", "fiction_fact_boundary_findings"])
        if "beta_reader_summary_context_gate" in patterns:
            targets.extend(["previous_summary_review_context", "beta_reader_feedback_trace", "review_style_effect_findings"])
        if "style_vocab_world_card_extraction_gate" in patterns:
            targets.extend(["style_vocabulary_extraction_report", "world_card_extraction_report", "chapter_local_style_patch_scope"])
        if "prompt_only_decay_ceiling_gate" in patterns:
            targets.extend(["pure_prompt_decay_report", "prompt_only_stress_test_findings", "wrap_up_mode_boundary_findings"])
        if "serial_platform_minimum_audit_gate" in patterns:
            targets.extend(["minimum_audit_cadence_report", "dialogue_ratio_loop_findings", "battle_scene_audit_findings"])
        if "multi_agent_reject_retry_review_gate" in patterns:
            targets.extend(["multi_agent_retry_trace", "reject_reason_report", "score_below_threshold_planning_return"])
        if "story_bible_context_packet_branch_gate" in patterns:
            targets.extend(["story_bible_context_packet_report", "branch_savepoint_trace", "dual_persona_editorial_findings"])
        if "memory_augmented_delta_verification_gate" in patterns:
            targets.extend(["delta_extraction_verification_report", "deterministic_accumulation_trace", "targeted_question_findings"])
        if "statistical_style_benchmark_rewrite_gate" in patterns:
            targets.extend(["style_benchmark_rewrite_report", "style_preset_threshold_findings", "voice_profile_metric_report"])
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
        if "plain_text_project_storage" in patterns:
            targets.extend(["manuscript_text_units", "note_text_units", "human_readable_storage_refs"])
        if "synopsis_cross_reference" in patterns:
            targets.extend(["synopsis_cross_refs", "comment_refs", "note_backlinks"])
        if "snowflake_premise_expansion" in patterns:
            targets.extend(["snowflake_premise_chain", "one_sentence_premise", "paragraph_summary", "full_summary"])
        if "outliner_index_cards" in patterns:
            targets.extend(["index_card_board", "chapter_scene_cards", "reorder_operations"])
        if "narrative_strand_mapping" in patterns:
            targets.extend(["narrative_strands", "fabula_map", "setting_context_layers"])
        if "character_depth_interview" in patterns:
            targets.extend(["character_depth_interviews", "belief_desire_fear_map", "character_contradictions"])
        if "mindmap_visual_planning" in patterns:
            targets.extend(["mindmap_nodes", "visual_link_edges", "idea_to_outline_promotions"])
        if "manuscript_export_formats" in patterns:
            targets.extend(["export_format_targets", "derived_manuscript_artifacts"])
        if "delivery_manuscript_assembly" in patterns:
            targets.extend(["final_manuscript_assembly_plan", "chapter_header_normalization_report", "chapter_order_gap_duplicate_audit"])
        if "export_format_fidelity_audit" in patterns:
            targets.extend(["export_format_fidelity_report", "markdown_docx_txt_parity", "derived_export_manifest"])
        if "preview_toc_packaging" in patterns:
            targets.extend(["toc_preview_heading_map", "html_preview_checks", "reader_navigation_audit"])
        if "cover_kdp_metadata_boundary" in patterns:
            targets.extend(["cover_kdp_metadata_spec", "cover_asset_prompt_boundary", "publication_metadata_review"])
        if "branching_choice_graph" in patterns:
            targets.extend(["choice_branch_graph", "branch_decision_points", "branch_merge_reject_notes"])
        if "node_dialogue_state_machine" in patterns:
            targets.extend(["dialogue_node_state_machine", "dialogue_entry_conditions", "dialogue_exit_state_deltas"])
        if "passage_link_navigation_map" in patterns:
            targets.extend(["passage_link_navigation_map", "dead_end_passage_findings", "reachable_path_checks"])
        if "choice_stats_consequence_gate" in patterns:
            targets.extend(["choice_stats_consequence_ledger", "visible_delayed_consequence_checks"])
        if "source_text_fingerprint_gate" in patterns:
            targets.extend(["source_fingerprint_overlap_report", "fingerprint_false_positive_notes", "fingerprint_threshold_decisions"])
        if "fuzzy_phrase_similarity_gate" in patterns:
            targets.extend(["fuzzy_phrase_similarity_report", "paraphrase_similarity_findings", "phrase_threshold_decisions"])
        if "diff_span_copy_review" in patterns:
            targets.extend(["diff_span_copy_risk_report", "copied_span_review_notes", "semantic_cleanup_review_findings"])
        if "minhash_lsh_near_duplicate_gate" in patterns:
            targets.extend(["minhash_lsh_overlap_report", "jaccard_near_duplicate_windows", "shingle_false_positive_notes"])
        if "simhash_hamming_similarity_gate" in patterns:
            targets.extend(["simhash_hamming_report", "near_duplicate_hash_windows", "hamming_threshold_decisions"])
        if "semantic_duplicate_cluster_gate" in patterns:
            targets.extend(["semantic_duplicate_cluster_report", "embedding_cluster_neighbors", "semantic_dedup_false_positive_notes"])
        if "embedding_similarity_independence_gate" in patterns:
            targets.extend(["embedding_similarity_independence_report", "nearest_neighbor_source_hits", "source_distance_acceptance_decisions"])
        if "corpus_leakage_dedup_review_gate" in patterns:
            targets.extend(["corpus_leakage_dedup_report", "repeated_sequence_findings", "source_corpus_boundary_findings"])
        if "character_quote_attribution_map" in patterns:
            targets.extend(["character_quote_attribution_report", "speaker_alias_map", "quote_voice_distribution"])
        if "readability_pacing_metric_gate" in patterns:
            targets.extend(["readability_pacing_curve", "sentence_length_variance_report", "paragraph_density_report"])
        if "prose_lint_style_rule_gate" in patterns:
            targets.extend(["prose_lint_report", "house_style_violation_map", "rule_exception_notes"])
        if "grammar_spelling_copyedit_gate" in patterns:
            targets.extend(["grammar_spelling_report", "copyedit_blocker_findings", "dialogue_exception_findings"])
        if "copyedit_diagnostic_triage_queue" in patterns:
            targets.extend(["copyedit_diagnostic_triage_report", "accepted_ignored_lint_ledger", "revision_task_queue"])
        if "lexical_diversity_voice_audit" in patterns:
            targets.extend(["lexical_diversity_voice_report", "mtld_hdd_voice_baseline", "repeated_vocabulary_findings"])
        if "stylometric_author_fingerprint_gate" in patterns:
            targets.extend(["stylometric_author_fingerprint_report", "style_profile_distance_matrix", "voice_fingerprint_version_diff"])
        if "function_word_syntax_style_gate" in patterns:
            targets.extend(["function_word_syntax_report", "punctuation_sentence_rhythm_curve", "style_feature_outlier_windows"])
        if "authorship_attribution_similarity_gate" in patterns:
            targets.extend(["authorship_similarity_report", "source_author_distance_findings", "same_type_similarity_threshold_decisions"])
        if "style_overfit_regression_gate" in patterns:
            targets.extend(["style_overfit_regression_report", "style_change_window_findings", "source_voice_leakage_failures"])
        if "paraphrase_independence_review_gate" in patterns:
            targets.extend(["paraphrase_independence_report", "style_transfer_boundary_findings", "author_voice_mimicry_risk_notes"])
        if "keyphrase_motif_extraction" in patterns:
            targets.extend(["keyphrase_motif_map", "motif_drift_findings", "topic_keyword_salience"])
        if "chinese_segmentation_keyword_gate" in patterns:
            targets.extend(["chinese_segmentation_report", "custom_dictionary_hits", "keyword_motif_salience"])
        if "chinese_ner_alias_consistency_gate" in patterns:
            targets.extend(["chinese_entity_alias_report", "character_location_org_consistency", "alias_conflict_findings"])
        if "chinese_text_normalization_gate" in patterns:
            targets.extend(["chinese_text_normalization_report", "simplified_traditional_variant_findings", "punctuation_width_findings"])
        if "chinese_error_correction_review_gate" in patterns:
            targets.extend(["chinese_error_correction_report", "confusion_set_review_findings", "accepted_ignored_correction_ledger"])
        if "source_format_import_manifest" in patterns:
            targets.extend(["source_import_manifest_report", "toc_spine_chapter_map", "source_metadata_findings"])
        if "pdf_layout_text_extraction_gate" in patterns:
            targets.extend(["pdf_layout_extraction_report", "page_span_reading_order", "pdf_text_gap_findings"])
        if "ocr_scanned_page_import_gate" in patterns:
            targets.extend(["ocr_confidence_report", "scanned_page_text_gap_findings", "ocr_manual_review_items"])
        if "document_partition_chapter_detection_gate" in patterns:
            targets.extend(["document_partition_report", "chapter_heading_detection_report", "element_type_sequence"])
        if "import_provenance_checksum_gate" in patterns:
            targets.extend(["import_checksum_report", "parser_setting_manifest", "source_artifact_provenance"])
        if "epub_structure_validation_gate" in patterns:
            targets.extend(["epub_validation_report", "opf_spine_manifest_findings", "media_type_container_findings"])
        if "ebook_accessibility_audit_gate" in patterns:
            targets.extend(["ebook_accessibility_report", "alt_text_landmark_findings", "accessibility_metadata_findings"])
        if "front_back_matter_metadata_gate" in patterns:
            targets.extend(["front_back_matter_report", "title_colophon_copyright_gaps", "publication_metadata_findings"])
        if "toc_navigation_consistency_gate" in patterns:
            targets.extend(["toc_navigation_consistency_report", "nav_spine_heading_mismatches", "reader_navigation_findings"])
        if "agentic_editorial_pipeline_gate" in patterns:
            targets.extend(["editorial_pipeline_report", "agent_role_handoff_findings", "author_decision_boundary_findings"])
        if "chapter_state_archive_ladder" in patterns:
            targets.extend(["chapter_state_archive_diff_report", "permanent_bible_state_drift_findings", "current_state_pointer_findings"])
        if "section_metadata_traceability_gate" in patterns:
            targets.extend(["section_metadata_coverage_report", "cast_location_item_section_gaps", "plotline_section_trace_findings"])
        if "ai_prose_fingerprint_cluster_gate" in patterns:
            targets.extend(["ai_prose_fingerprint_cluster_report", "voice_drift_cluster_findings", "accepted_exception_pattern_ledger"])
        if "author_candidate_canon_confirmation_gate" in patterns:
            targets.extend(["candidate_canon_confirmation_report", "unconfirmed_ai_candidate_findings", "preview_apply_decision_log"])
        if "progressive_spoiler_context_window_gate" in patterns:
            targets.extend(["spoiler_context_window_report", "future_chapter_leakage_findings", "stage_context_range_validation"])
        if "chapter_control_card_writeback_gate" in patterns:
            targets.extend(["chapter_control_card_coverage_report", "dynamic_state_writeback_findings", "next_chapter_handoff_pressure_log"])
        if "trace_replay_revision_workspace_gate" in patterns:
            targets.extend(["trace_replay_review_report", "chapter_rewrite_impact_findings", "revision_decision_trace_log"])
        if "relationship_graph_global_replace_gate" in patterns:
            targets.extend(["relationship_graph_consistency_report", "global_replace_propagation_findings", "upstream_change_conflict_warnings"])
        if "bookrun_audit_trail_gate" in patterns:
            targets.extend(["bookrun_audit_trail_report", "judge_repair_acceptance_log", "export_audit_artifact_manifest"])
        if "provider_budget_smoke_gate" in patterns:
            targets.extend(["provider_budget_smoke_report", "llm_profile_cost_trace", "provider_runtime_admission_findings"])
        if "sidecar_memory_profile_boundary" in patterns:
            targets.extend(["sidecar_memory_profile_report", "graph_vector_boundary_findings", "deployment_profile_runtime_exclusions"])
        if "outline_checkpoint_milestone_gate" in patterns:
            targets.extend(["outline_checkpoint_milestone_report", "story_bible_truth_source_drift_findings", "narrative_milestone_coverage"])
        if "language_localization_style_profile_gate" in patterns:
            targets.extend(["language_style_profile_report", "localized_rule_exception_ledger", "glossary_unit_register_findings"])
        if "progressive_disclosure_skill_protocol_gate" in patterns:
            targets.extend(["skill_protocol_route_report", "progressive_disclosure_load_trace", "knowledge_base_binding_findings"])
        if "anti_slop_rulepack_triage_gate" in patterns:
            targets.extend(["anti_slop_rulepack_triage_report", "banned_vocabulary_exception_ledger", "ai_prose_tell_findings"])
        if "user_modifier_project_blueprint_gate" in patterns:
            targets.extend(["project_modifier_blueprint_report", "dashboard_timing_export_audit", "project_state_export_findings"])
        if "portable_canon_skill_runtime_gate" in patterns:
            targets.extend(["portable_canon_runtime_report", "sqlite_checkpoint_artifact_trace", "canon_sync_frontmatter_findings"])
        if "staged_outline_chunk_window_gate" in patterns:
            targets.extend(["staged_outline_chunk_window_report", "chapter_range_refinement_findings", "sliding_window_context_trace"])
        if "wiki_canon_graph_lint_gate" in patterns:
            targets.extend(["wiki_canon_graph_lint_report", "continuity_query_conflict_findings", "relationship_graph_quality_findings"])
        if "plan_draft_log_verify_loop_gate" in patterns:
            targets.extend(["plan_draft_log_verify_report", "living_document_freshness_findings", "foreshadowing_thread_update_findings"])
        if "mcp_scene_index_revision_boundary" in patterns:
            targets.extend(["scene_index_revision_boundary_report", "safe_scene_revision_confirmation_log", "metadata_sync_git_history_findings"])
        if "verbalized_sampling_diversity_wiki_gate" in patterns:
            targets.extend(["verbalized_sampling_diversity_report", "writer_wiki_autofile_findings", "mode_collapse_variety_findings"])
        if "literary_event_entity_annotation_gate" in patterns:
            targets.extend(["literary_entity_event_annotation_report", "event_participant_role_conflicts", "source_event_annotation_gaps"])
        if "narrative_event_evolution_graph_gate" in patterns:
            targets.extend(["narrative_event_chain_report", "causal_discourse_edge_findings", "event_order_dependency_gaps"])
        if "sentiment_arc_emotion_trajectory_gate" in patterns:
            targets.extend(["sentiment_arc_emotion_report", "character_emotion_trajectory_report", "emotion_turning_point_findings"])
        if "cross_context_coreference_gate" in patterns:
            targets.extend(["cross_context_coreference_report", "mention_cluster_conflicts", "entity_event_identity_gaps"])
        if "character_interaction_network_gate" in patterns:
            targets.extend(["character_interaction_network_report", "relationship_polarity_drift", "centrality_role_shift_findings"])
        if "semantic_chunk_boundary_map" in patterns:
            targets.extend(["semantic_chunk_boundary_report", "chunk_overlap_manifest", "context_boundary_findings"])
        if "chapter_summary_anchor_gate" in patterns:
            targets.extend(["chapter_summary_anchor_report", "representative_sentence_refs", "summary_anchor_drift_findings"])
        if "narrative_qa_comprehension_gate" in patterns:
            targets.extend(["narrative_qa_coverage_report", "question_answer_evidence_map", "source_summary_comprehension_gaps"])
        if "chapter_summary_alignment_gate" in patterns:
            targets.extend(["chapter_summary_alignment_report", "book_chapter_summary_consistency", "causal_temporal_summary_gap_findings"])
        if "story_question_answer_validation_gate" in patterns:
            targets.extend(["story_element_qa_report", "section_grounded_answer_gaps", "narrative_element_coverage_findings"])
        if "causal_why_explanation_gate" in patterns:
            targets.extend(["causal_why_explanation_report", "helpful_sentence_grounding_findings", "plausible_answer_validity_notes"])
        if "story_commonsense_consistency_gate" in patterns:
            targets.extend(["story_commonsense_report", "character_motivation_emotion_conflicts", "mental_state_continuity_findings"])
        if "query_focused_long_summary_gate" in patterns:
            targets.extend(["query_focused_summary_report", "plot_question_response_alignment", "multi_reference_summary_disagreement"])
        if "trope_inventory_similarity_gate" in patterns:
            targets.extend(["trope_similarity_report", "shared_trope_vector", "source_trope_overlap_decisions"])
        if "trope_graph_expectation_map" in patterns:
            targets.extend(["trope_graph_expectation_report", "trope_cooccurrence_map", "genre_expectation_edges"])
        if "trope_density_novelty_budget" in patterns:
            targets.extend(["trope_density_report", "novelty_budget_findings", "cliche_saturation_notes"])
        if "trope_source_boundary_review" in patterns:
            targets.extend(["trope_source_boundary_report", "scrape_runtime_rejection_notes", "source_text_exclusion_checks"])
        if "source_license_detection_gate" in patterns:
            targets.extend(["source_license_review_report", "license_detection_confidence", "unknown_license_blockers"])
        if "spdx_reuse_compliance_gate" in patterns:
            targets.extend(["spdx_reuse_compliance_report", "copyright_attribution_gaps", "license_id_normalization_findings"])
        if "public_domain_corpus_boundary" in patterns:
            targets.extend(["public_domain_source_report", "gutenberg_metadata_findings", "public_domain_scope_notes"])
        if "attribution_derivative_work_gate" in patterns:
            targets.extend(["attribution_derivative_review", "allowed_use_boundary_findings", "licensed_source_exclusion_notes"])
        if "source_entity_redaction_gate" in patterns:
            targets.extend(["source_entity_redaction_report", "unredacted_source_entity_findings", "redaction_review_decisions"])
        if "custom_entity_label_inventory" in patterns:
            targets.extend(["custom_entity_label_inventory", "fiction_entity_type_coverage", "unmapped_entity_findings"])
        if "placeholder_alias_consistency_map" in patterns:
            targets.extend(["placeholder_alias_consistency_report", "replacement_collision_findings", "alias_namespace_drift_notes"])
        if "proper_noun_leakage_review" in patterns:
            targets.extend(["proper_noun_leakage_report", "source_name_carryover_findings", "allowed_name_exception_notes"])
        if "canon_drift_continuity_qa_gate" in patterns:
            targets.extend(["canon_drift_qa_report", "continuity_context_pack_findings", "scene_fact_mismatch_notes"])
        if "local_rag_writing_ide_gate" in patterns:
            targets.extend(["local_rag_context_boundary_report", "source_material_retrieval_trace", "retrieved_context_scope_findings"])
        if "patch_replay_manuscript_state_gate" in patterns:
            targets.extend(["patch_replay_state_report", "version_snapshot_diff_trace", "latest_state_reconstruction_findings"])
        if "microkernel_skill_plugin_isolation_gate" in patterns:
            targets.extend(["plugin_isolation_report", "event_bus_stage_trace", "skill_failure_containment_findings"])
        if "interactive_reader_writer_loop_gate" in patterns:
            targets.extend(["interactive_reader_writer_trace", "chapter_file_writeback_audit", "revision_acceptance_findings"])
        if "abstract_style_learning_skill_gate" in patterns:
            targets.extend(["style_skill_abstraction_report", "source_sample_boundary_findings", "style_copy_leakage_notes"])
        if "impromptu_thread_pool_chapter_gate" in patterns:
            targets.extend(["impromptu_chapter_intent_trace", "open_thread_pool_findings", "finalize_thread_settlement_notes"])
        if "offline_inspiration_bank_style_gate" in patterns:
            targets.extend(["inspiration_bank_scope_report", "offline_style_mimicry_findings", "local_reference_boundary_notes"])
        if "atelier_phase_pipeline_gate" in patterns:
            targets.extend(["atelier_phase_handoff_trace", "beat_tree_audit_findings", "hook_auditor_notes"])
        if "book_mining_genesis_automation_gate" in patterns:
            targets.extend(["book_mining_pattern_review", "genesis_scoring_findings", "canon_seed_handoff_findings"])
        if "multi_book_autopilot_studio_gate" in patterns:
            targets.extend(["multi_book_profile_audit", "autopilot_stop_condition_findings", "full_book_logic_check_notes"])
        if "longrun_commit_projection_health_gate" in patterns:
            targets.extend(["chapter_commit_projection_health", "read_model_staleness_findings", "memory_scratchpad_scope_notes"])
        if "fresh_context_chapter_iteration_gate" in patterns:
            targets.extend(["fresh_context_iteration_report", "chapter_manifest_progress_findings", "memory_fatigue_reset_notes"])
        if "topic_drift_map" in patterns:
            targets.extend(["topic_drift_map", "topic_cluster_timeline", "off_arc_topic_findings"])
        if "context_faithfulness_eval_gate" in patterns:
            targets.extend(["context_faithfulness_eval_report", "groundedness_findings", "context_precision_recall_scores"])
        if "retrieval_trace_observability_gate" in patterns:
            targets.extend(["retrieval_trace_eval_report", "selected_omitted_context_trace", "context_relevance_findings"])
        if "prompt_regression_eval_suite" in patterns:
            targets.extend(["prompt_regression_suite", "golden_case_eval_results", "eval_failure_diffs"])
        if "agentwrite_plan_write_pipeline" in patterns:
            targets.extend(["agentwrite_plan_artifact", "agentwrite_write_artifact", "plan_write_stage_trace"])
        if "long_output_length_quality_ruler" in patterns:
            targets.extend(["long_output_length_report", "long_output_quality_report", "length_stress_test_results"])
        if "long_context_reward_dimension_gate" in patterns:
            targets.extend(["long_context_reward_scores", "helpfulness_logicality_faithfulness_completeness_report", "reward_dimension_fix_tasks"])
        if "instance_specific_writing_criteria_gate" in patterns:
            targets.extend(["instance_specific_criteria_report", "requirement_dimension_coverage", "chapter_acceptance_criteria_failures"])
        if "material_grounded_query_refinement" in patterns:
            targets.extend(["material_grounding_pruning_report", "query_requirement_fit_findings", "irrelevant_material_rejections"])
        if "hybrid_rubric_pairwise_elo_judge" in patterns:
            targets.extend(["hybrid_rubric_pairwise_elo_report", "pairwise_neighbor_comparisons", "elo_stability_notes"])
        if "judge_bias_mitigation_check" in patterns:
            targets.extend(["judge_bias_mitigation_report", "length_position_verbosity_bias_findings", "poetic_incoherence_findings"])
        if "plan_reflect_character_chapter_pipeline" in patterns:
            targets.extend(["plan_reflection_character_profile_trace", "chapter_sequence_generation_trace", "narrative_consistency_judge_notes"])
        if "human_story_metric_panel" in patterns:
            targets.extend(["human_story_metric_scores", "relevance_coherence_empathy_surprise_engagement_complexity_report", "reader_axis_fix_tasks"])
        if "hierarchical_cowriting_story_scaffold" in patterns:
            targets.extend(["hierarchical_story_scaffold_report", "logline_character_plot_location_dialogue_trace", "layer_consistency_findings"])
        if "human_coauthor_edit_boundary" in patterns:
            targets.extend(["human_coauthor_edit_report", "plagiarism_toxicity_formulaic_risk_notes", "author_rewrite_decisions"])
        if "recursive_reprompt_revision_loop" in patterns:
            targets.extend(["recursive_reprompt_revision_trace", "plan_draft_rewrite_edit_report", "outline_reload_checkpoint"])
        if "reranker_guided_candidate_selection" in patterns:
            targets.extend(["reranker_candidate_scores", "relevance_coherence_selection_report", "beam_candidate_decision_log"])
        if "character_dialogue_persona_memory" in patterns:
            targets.extend(["character_persona_dialogue_report", "tone_personality_plot_chat_evidence", "role_voice_drift_findings"])
        if "event_to_sentence_realization_trace" in patterns:
            targets.extend(["event_to_sentence_trace", "plot_event_realization_report", "ensemble_confidence_notes"])
        if "entity_memory_slotfill_grounding" in patterns:
            targets.extend(["entity_memory_slotfill_report", "entity_tracking_findings", "slot_grounding_failures"])
        if "book_memory_bank_context_lattice" in patterns:
            targets.extend(["memory_bank_completeness_report", "plan_to_actual_comparison", "active_context_progress_report"])
        if "spec_driven_fiction_scene_tasks" in patterns:
            targets.extend(["story_bible_quality_gate_report", "scene_task_coverage_report", "pov_schedule_information_asymmetry_report"])
        if "toc_aware_source_deconstruction" in patterns:
            targets.extend(["toc_hierarchy_summary_report", "nested_section_context_report", "source_quote_anecdote_evidence"])
        if "two_pass_context_glossary_pipeline" in patterns:
            targets.extend(["two_pass_glossary_consistency_report", "proper_noun_term_drift_findings", "resume_checkpoint_suggestion"])
        if "inline_author_edit_markup_versioning" in patterns:
            targets.extend(["inline_edit_note_queue", "author_note_context_map", "revision_diff_milestones"])
        if "causal_dramatica_agent_pipeline" in patterns:
            targets.extend(["causal_dramatica_thread_report", "agent_layer_handoff_trace", "foreshadowing_causality_findings"])
        if "capture_distillation_production_gate" in patterns:
            targets.extend(["capture_distillation_production_report", "distilled_story_packet_findings", "production_promotion_decisions"])
        if "skill_orchestrated_chinese_novel_workflow" in patterns:
            targets.extend(["skill_orchestrated_chinese_workflow_report", "webnovel_stage_boundary_findings", "skill_runtime_exclusion_notes"])
        if "langgraph_story_state_machine" in patterns:
            targets.extend(["story_state_machine_report", "checkpoint_transition_trace", "stateful_planning_findings"])
        if "story_daemon_evolution_loop" in patterns:
            targets.extend(["story_daemon_evolution_report", "organic_plan_write_review_trace", "agent_autonomy_boundary_findings"])
        if "local_rag_writing_ide_gate" in patterns:
            targets.extend(["local_rag_context_boundary_report", "source_material_retrieval_trace", "retrieved_context_scope_findings"])
        if "canon_drift_continuity_qa_gate" in patterns:
            targets.extend(["canon_drift_qa_report", "continuity_context_pack_findings", "scene_fact_mismatch_notes"])
        if "patch_replay_manuscript_state_gate" in patterns:
            targets.extend(["patch_replay_state_log", "version_snapshot_diff_trace", "latest_state_reconstruction_findings"])
        if "microkernel_skill_plugin_isolation_gate" in patterns:
            targets.extend(["plugin_isolation_report", "event_bus_stage_trace", "skill_failure_containment_findings"])
        if "interactive_reader_writer_loop_gate" in patterns:
            targets.extend(["interactive_reader_writer_trace", "chapter_file_writeback_audit", "revision_acceptance_findings"])
        if "abstract_style_learning_skill_gate" in patterns:
            targets.extend(["style_skill_abstraction_report", "source_sample_boundary_findings", "style_copy_leakage_notes"])
        if "impromptu_thread_pool_chapter_gate" in patterns:
            targets.extend(["impromptu_chapter_intent_trace", "open_thread_pool_findings", "finalize_thread_settlement_notes"])
        if "offline_inspiration_bank_style_gate" in patterns:
            targets.extend(["inspiration_bank_scope_report", "offline_style_mimicry_findings", "local_reference_boundary_notes"])
        if "atelier_phase_pipeline_gate" in patterns:
            targets.extend(["atelier_phase_handoff_trace", "beat_tree_audit_findings", "hook_auditor_notes"])
        if "book_mining_genesis_automation_gate" in patterns:
            targets.extend(["book_mining_pattern_review", "genesis_scoring_findings", "canon_seed_handoff_findings"])
        if "multi_book_autopilot_studio_gate" in patterns:
            targets.extend(["multi_book_profile_audit", "autopilot_stop_condition_findings", "full_book_logic_check_notes"])
        if "longrun_commit_projection_health_gate" in patterns:
            targets.extend(["chapter_commit_projection_health", "read_model_staleness_findings", "memory_scratchpad_scope_notes"])
        if "fresh_context_chapter_iteration_gate" in patterns:
            targets.extend(["fresh_context_iteration_report", "next_incomplete_chapter_detection", "progress_log_update_findings"])
        if "temporal_canon_context_graph" in patterns:
            targets.extend(["temporal_canon_graph_report", "episode_provenance_trace", "validity_window_conflicts"])
        if "long_term_author_preference_memory" in patterns:
            targets.extend(["author_preference_memory_report", "session_memory_drift_findings", "project_memory_scope_audit"])
        if "community_graph_source_deconstruction" in patterns:
            targets.extend(["source_community_summary_report", "entity_community_overlap_findings", "global_local_question_coverage"])
        if "dual_level_graph_vector_retrieval" in patterns:
            targets.extend(["graph_vector_retrieval_report", "local_global_hybrid_context_selection", "retrieval_mode_failure_notes"])
        if "schema_guided_graph_extraction" in patterns:
            targets.extend(["schema_guided_extraction_report", "node_relationship_property_coverage", "source_metadata_grounding_report"])
        if "human_synopsis_gate" in patterns:
            targets.extend(["synopsis_review_gate", "chapter_summary_review_status", "synopsis_regeneration_options"])
        if "retrieval_guided_span_rewrite" in patterns:
            targets.extend(["retrieved_text_spans", "span_rewrite_scope", "outline_sync_delta"])
        if "runtime_artifact_trace" in patterns:
            targets.extend(["runtime_intent_artifact", "selected_context_artifact", "rule_stack_artifact", "trace_artifact"])
        if "schema_validated_state_delta" in patterns:
            targets.extend(["validated_state_delta_schema", "state_delta_rejections", "immutable_state_updates"])
        if "recursive_adaptive_planning" in patterns:
            targets.extend(["adaptive_task_tree", "retrieval_reasoning_composition_steps", "dynamic_replan_points"])
        if "workflow_manuscript_compilation" in patterns:
            targets.extend(["manuscript_compile_steps", "ordered_scene_sources", "compile_output_manifest"])
        if "writing_session_goal_tracking" in patterns:
            targets.extend(["writing_session_goal", "scene_draft_word_counts", "daily_progress_targets"])
        if "inspectable_run_workspace" in patterns:
            targets.extend(["inspectable_run_sessions", "storyboard_surfaces", "editable_memory_bank_refs"])
        if "craft_role_pipeline" in patterns:
            targets.extend(["craft_role_assignments", "role_output_boundaries", "review_agent_findings"])
        if "frontmatter_story_schema" in patterns:
            targets.extend(["frontmatter_story_schema", "scene_state_frontmatter", "continuity_questions", "promise_payoff_refs"])
        if "continuity_bridge_window" in patterns:
            targets.extend(["continuity_bridge_window", "recent_episode_state", "bridge_input_sources"])
        if "episode_range_rewrite_scope" in patterns:
            targets.extend(["rewrite_impact_scope", "episode_range_change_plan"])
        if "voice_table_polish_axis" in patterns:
            targets.extend(["voice_table", "dialogue_consistency_axes", "nonverbal_palette"])
        if "boring_opening_quality_gates" in patterns:
            targets.extend(["boring_scene_findings", "opening_hook_checks", "reader_experience_findings"])
        if "beat_strand_framework" in patterns:
            targets.extend(["beat_framework_map", "interwoven_strands", "convergence_points"])
        if "anti_hallucination_plan_check" in patterns:
            targets.extend(["plan_verification_results", "hallucination_risk_findings", "forgotten_state_findings"])
        if "backup_restore_checkpoint" in patterns:
            targets.extend(["backup_restore_points", "restore_manifest"])
        if "multi_level_review_trend" in patterns:
            targets.extend(["scene_chapter_batch_reviews", "quality_trend_report", "audit_layer_results"])
        if "editor_notes_feedback_loop" in patterns:
            targets.extend(["editor_notes", "cross_chapter_feedback_items"])
        if "genre_parameterized_worldbuilding" in patterns:
            targets.extend(["genre_worldbuilding_parameters", "faction_location_templates", "genre_guide_refs"])
        if "prose_preflight_voice_calibration" in patterns:
            targets.extend(["voice_calibration_samples", "prose_preflight_findings", "specificity_guardrails"])
        if "sourcebook_author_workbench" in patterns:
            targets.extend(["sourcebook_entries", "writing_partner_actions", "author_control_decisions"])
        if "semantic_long_context_search" in patterns:
            targets.extend(["semantic_context_hits", "vector_context_reason", "knowledge_base_refs"])
        if "contradiction_taxonomy_checker" in patterns:
            targets.extend(["consistency_bug_taxonomy", "characterization_conflicts", "timeline_plot_conflicts", "world_rule_conflicts"])
        if "parallel_agent_chapter_pipeline" in patterns:
            targets.extend(["agent_stage_contracts", "parallel_chapter_jobs", "aggregate_revision_findings"])
        if "cross_chapter_redundancy_audit" in patterns:
            targets.extend(["cross_chapter_redundancy_findings", "repetitive_scene_patterns", "over_regular_prose_findings"])
        if "humanization_stylometry_levers" in patterns:
            targets.extend(["stylometry_findings", "burstiness_findings", "perplexity_risk_notes", "ai_transition_removals"])
        if "author_control_boundary" in patterns:
            targets.extend(["author_control_decisions", "ai_generated_labeling", "ethical_disclosure_notes"])
        if "research_taxonomy_story_map" in patterns:
            targets.extend(["story_generation_taxonomy", "method_category_map", "benchmark_candidate_refs"])
        if "novel_to_multimodal_pipeline" in patterns:
            targets.extend(["multimodal_adaptation_chain", "script_scene_storyboard_outputs", "video_asset_boundaries"])
        if "entity_to_visual_asset_pipeline" in patterns:
            targets.extend(["entity_extraction_results", "character_reference_assets", "scene_visual_asset_manifest"])
        if "agentic_book_planner_pipeline" in patterns:
            targets.extend(["story_bible_agent_outputs", "plot_thread_agent_outputs", "chapter_outline_agent_outputs", "continuity_checker_outputs"])
        if "rag_synopsis_spine" in patterns:
            targets.extend(["full_synopsis_spine", "rag_context_retrieval_log", "chapter_summary_spine"])
        if "anti_repetition_prompt_rules" in patterns:
            targets.extend(["anti_repetition_rule_hits", "token_stats", "repeated_phrase_scene_shape_report"])
        if "prompt_recipe_experiment_grid" in patterns:
            targets.extend(["prompt_recipe_grid", "writing_experiment_runs", "rubric_review_scores"])
        if "append_only_generation_review_log" in patterns:
            targets.extend(["append_only_run_log", "resumable_review_records", "experiment_resume_state"])
        if "narrative_arc_template_control" in patterns:
            targets.extend(["narrative_arc_templates", "genre_style_matrix", "scenario_blueprint_fields"])
        if "nrd_task_tree_pipeline" in patterns:
            targets.extend(["nrd_task_tree", "arc_chapter_scene_nodes", "revision_pass_records"])
        if "sampling_parameter_quality_sweep" in patterns:
            targets.extend(["sampling_parameter_grid", "quality_sweep_results", "temperature_top_p_findings"])
        if "story_structure_rag_planning" in patterns:
            targets.extend(["hero_journey_beats", "freytag_structure_points", "style_thematic_rag_samples"])
        if "story_contract_commit_chain" in patterns:
            targets.extend(["story_contracts", "accepted_chapter_commits", "canon_commit_chain"])
        if "fact_snapshot_delta_gate" in patterns:
            targets.extend(["fact_snapshot_dimensions", "change_declaration_types", "generation_gate_results", "state_writeback_log"])
        if "projection_sync_observability" in patterns:
            targets.extend(["projection_views", "projection_sync_log", "doctor_preflight_results", "dashboard_read_model"])
        if "foreshadowing_debt_budget" in patterns:
            targets.extend(["foreshadowing_debt_items", "context_budget_reservations", "unresolved_hook_pressure"])
        if "reader_retention_review_gate" in patterns:
            targets.extend(["reader_retention_score", "pleasure_point_checks", "ooc_rhythm_review", "chapter_hook_strength"])
        if "draft_stage_revision_ladder" in patterns:
            targets.extend(["chapter_blueprint", "key_information_file", "draft_stage_status", "next_chapter_handoff"])
        if "rolling_summary_context_trim" in patterns:
            targets.extend(["rolling_summary", "character_state_snapshot", "timeline_event_log", "context_trim_manifest"])
        if "pairwise_story_comparison_ranking" in patterns:
            targets.extend(["pairwise_story_comparisons", "matched_variant_briefs", "evaluator_agreement_report"])
        if "multidimensional_quality_rubric" in patterns:
            targets.extend(["story_quality_rubric_scores", "ranked_weaknesses", "reader_interest_resolution_scores"])
        if "story_theory_beat_evaluation" in patterns:
            targets.extend(["story_theory_task_results", "beat_execution_checks", "constrained_continuation_criteria"])
        if "constraint_specificity_creativity_benchmark" in patterns:
            targets.extend(["constraint_specificity_level", "constraint_satisfaction_results", "coherence_creativity_balance"])
        if "style_axis_diversity_fingerprint" in patterns:
            targets.extend(["style_axis_fingerprint", "style_diversity_score", "voice_rhythm_pov_axes"])
        if "event_outline_history_compression" in patterns:
            targets.extend(["event_outline_graph", "chapter_plan_events", "compressed_history_for_current_event"])
        if "agentic_story_world_simulation" in patterns:
            targets.extend(["simulated_agent_interactions", "character_behavior_state", "story_world_evolution_log"])
        if "reader_rating_signal_model" in patterns:
            targets.extend(["reader_rating_matrix", "to_read_intent_signals", "shelf_tag_expectation_map", "aggregate_preference_notes"])
        if "review_spoiler_sentiment_corpus" in patterns:
            targets.extend(["review_signal_clusters", "spoiler_risk_flags", "sentiment_timeline", "common_praise_complaint_map"])
        if "beta_reader_archetype_panel" in patterns:
            targets.extend(["beta_reader_archetypes", "chapter_want_to_continue_scores", "confusion_flags", "favorite_moments", "stumble_points"])
        if "comp_title_market_positioning" in patterns:
            targets.extend(["comp_title_matrix", "reader_expectation_profile", "genre_gap_statement", "positioning_copy_constraints"])
        if "local_reader_experience_editor" in patterns:
            targets.extend(["micro_tension_findings", "reader_curiosity_threads", "chapter_hook_cliffhanger_audit", "style_dna_context_fit", "token_breakdown_notes"])
        if "inline_human_machine_coauthoring_gate" in patterns:
            targets.extend(["inline_revision_spans", "author_edit_acceptance_log", "localized_diff_review"])
        if "hierarchical_orchestrator_generation_gate" in patterns:
            targets.extend(["volume_arc_chapter_plan", "orchestrator_loop_trace", "generation_validation_improvement_cycles"])
        if "batch_continuation_progress_queue_gate" in patterns:
            targets.extend(["batch_continuation_jobs", "auto_continuation_progress_state", "queue_retry_boundaries"])
        if "homogeneity_prompt_variation_gate" in patterns:
            targets.extend(["homogeneity_findings", "prompt_variation_report", "random_topic_title_seed_log"])
        if "local_author_data_boundary_gate" in patterns:
            targets.extend(["local_author_data_manifest", "download_update_surface_risk_review", "runtime_trial_blockers"])
        if "prompt_preset_variable_library_gate" in patterns:
            targets.extend(["prompt_preset_matrix", "prompt_variable_usage", "prompt_effect_tracking_notes"])
        if "imported_manuscript_migration_outline_gate" in patterns:
            targets.extend(["imported_chapter_map", "migration_generated_outlines", "source_import_boundary_review"])
        if "style_dna_reference_library_gate" in patterns:
            targets.extend(["style_dna_abstractions", "reference_library_items", "style_copy_risk_notes"])
        if "draft_candidate_promotion_gate" in patterns:
            targets.extend(["draft_review_rewrite_candidates", "candidate_comparison_log", "confirmed_chapter_acceptance_log"])
        if "privacy_preserving_local_index_gate" in patterns:
            targets.extend(["local_metadata_index_manifest", "privacy_search_fields", "plaintext_exclusion_checks"])
        if "chapter_description_continuity_bridge_gate" in patterns:
            targets.extend(["chapter_description_context_bridge", "previous_chapter_summary_trace", "description_to_draft_continuity_checks"])
        if "selective_streaming_regeneration_gate" in patterns:
            targets.extend(["selective_regeneration_report", "specific_chapter_rewrite_scope", "streaming_checkpoint_recovery"])
        if "research_citation_boundary_gate" in patterns:
            targets.extend(["research_citation_manifest", "evidence_source_scope", "fiction_fact_boundary_findings"])
        if "beta_reader_summary_context_gate" in patterns:
            targets.extend(["previous_summary_review_context", "beta_reader_feedback_trace", "review_style_effect_findings"])
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
        if "continuity_bridge_window" in patterns:
            hints.append("Before writing the next episode, build a continuity bridge from the last accepted chapters, active timeline, foreshadows, character state, and editor notes.")
        if "voice_table_polish_axis" in patterns:
            hints.append("Check dialogue against a voice table: sentence endings, diction, nonverbal palette, and motivation must stay distinct by character.")
        if "anti_hallucination_plan_check" in patterns:
            hints.append("Drafting cannot invent facts outside the accepted bible, plan, or chapter-change packages; mark missing facts as review questions instead.")
        if "multi_level_review_trend" in patterns:
            hints.append("Review at scene, chapter, and batch levels so local fixes do not hide cross-chapter drift or repeated weak beats.")
        if "editor_notes_feedback_loop" in patterns:
            hints.append("Carry unresolved editor notes into the next chapter context and close each note only with chapter evidence.")
        if "reader_rating_signal_model" in patterns:
            hints.append("Use rating/shelf/to-read signals only as aggregate reader-expectation hints; they must not override accepted canon or author direction.")
        if "review_spoiler_sentiment_corpus" in patterns:
            hints.append("When using review-like feedback, separate spoiler-sensitive complaints, praise clusters, and sentiment drift from canon facts.")
        if "beta_reader_archetype_panel" in patterns:
            hints.append("Run a beta-reader panel on important chapters: genre fan, casual reader, critical reader, and sensitivity reader each produce confusion and turn-page notes.")
        if "comp_title_market_positioning" in patterns:
            hints.append("Use comp titles to calibrate promise, tone, trope expectation, and market gap; do not copy their premise, cast, title language, or review wording.")
        if "local_reader_experience_editor" in patterns:
            hints.append("Before acceptance, audit micro-tension, reader curiosity, chapter hook, cliffhanger, paragraph rhythm, and scene opening/ending strength.")
        if "semantic_long_context_search" in patterns:
            hints.append("Use semantic long-context search for chapter-specific recall, but cite the selected sourcebook or knowledge-base refs instead of silently injecting them.")
        if "contradiction_taxonomy_checker" in patterns:
            hints.append("Run a contradiction taxonomy check before accepting a chapter: characterization, factual detail, narrative style, timeline/plot, and world rules.")
        if "cross_chapter_redundancy_audit" in patterns:
            hints.append("Audit cross-chapter redundancy, repeated scene construction, weak causality, flat dialogue, and over-regular prose before revision closes.")
        if "author_control_boundary" in patterns:
            hints.append("Keep the author in control: AI may propose, draft, and review, but canon changes require accepted project artifacts or explicit user direction.")
        if "research_taxonomy_story_map" in patterns:
            hints.append("Use the research taxonomy as a checklist for method coverage: planning, agents, simulation, multimodal adaptation, memory, and benchmark gates.")
        if "agentic_book_planner_pipeline" in patterns:
            hints.append("Separate Story Bible, Characters, Plot Threads, Chapter Outlines, Writer, Editor, and Continuity Checker outputs before drafting.")
        if "rag_synopsis_spine" in patterns:
            hints.append("Keep a full synopsis spine and retrieve only the chapter-summary/context slices relevant to the next beat.")
        if "anti_repetition_prompt_rules" in patterns:
            hints.append("Apply anti-repetition rules before acceptance: reject repeated phrases, repeated scene shapes, and redundant causal bridges.")
        if "narrative_arc_template_control" in patterns:
            hints.append("Select narrative arc and genre/style controls explicitly so continuation follows the intended arc instead of drifting by local scene taste.")
        if "nrd_task_tree_pipeline" in patterns:
            hints.append("Drive continuation from an NRD-style task tree: arcs -> chapters -> scenes -> revision passes, with continuity reporting after each level.")
        if "story_structure_rag_planning" in patterns:
            hints.append("Use story-structure references as planning scaffolds only; map Hero's Journey/Freytag beats to this book's accepted facts before prose.")
        if "story_contract_commit_chain" in patterns:
            hints.append("续写必须从故事合同和 accepted CHAPTER_COMMIT 主链取事实；草稿未提交前不能进入可复用状态。")
        if "fact_snapshot_delta_gate" in patterns:
            hints.append("写前组装事实快照，写后提交类型化变更声明；只有通过生成门禁的状态回写才能成为新事实。")
        if "projection_sync_observability" in patterns:
            hints.append("每次承接前检查 state/index/summary/memory/vector 等派生视图是否已同步到最新 accepted commit。")
        if "foreshadowing_debt_budget" in patterns:
            hints.append("优先召回高债务伏笔，预留上下文预算，并在揭示前标明铺垫、回收窗口和当前状态。")
        if "reader_retention_review_gate" in patterns:
            hints.append("章节验收同时检查一致性、OOC、节奏、爽点兑现和下一章拉力；流畅但无追读压力不能接受。")
        if "draft_stage_revision_ladder" in patterns:
            hints.append("按章节蓝图、关键信息、任务卡到 Draft A/B/C 逐级修订；Draft C 只做去 AI 味和语言收束，不改事实。")
        if "rolling_summary_context_trim" in patterns:
            hints.append("用 rolling summary、人物状态、时间线事件和裁剪清单控制长上下文，只注入与当前章节有关的片段。")
        if "pairwise_story_comparison_ranking" in patterns:
            hints.append("关键章节可生成同约束变体并做成对比较；验收依据是相同创意简报下的优劣证据，不是单稿直觉。")
        if "multidimensional_quality_rubric" in patterns:
            hints.append("章节评审拆成多维指标：语法清晰、因果连接、场景目的、内部一致性、人物动机、对白、读者兴趣和收束。")
        if "story_theory_beat_evaluation" in patterns:
            hints.append("用故事理论检查当前节拍是否完成叙事功能；补桥、修节拍和受限续写都要保留前后连续性。")
        if "constraint_specificity_creativity_benchmark" in patterns:
            hints.append("记录每章硬约束数量和满足情况；在约束更具体时仍需保留新意、连贯性和可读性。")
        if "style_axis_diversity_fingerprint" in patterns:
            hints.append("用风格轴检查输出：声线、句法节奏、视角距离、结构节奏、情绪、意象、对白和收束方式。")
        if "event_outline_history_compression" in patterns:
            hints.append("把长篇历史压缩到当前事件相关的事件大纲和章节计划，避免上下文过载导致当前行动失焦。")
        if "agentic_story_world_simulation" in patterns:
            hints.append("多角色推演只作为因果候选；角色行为、社交互动和世界演化必须经过作者验收后才写入正史。")
        if "top_down_story_planning" in patterns:
            hints.append("长篇规划从 book spec 到卷/章/场景逐级展开，当前场景写作必须承接上一场景文本状态。")
        if "plain_text_project_storage" in patterns:
            hints.append("把章节、笔记、摘要和分析切成稳定文本单元，便于 diff、回滚和人工审阅。")
        if "synopsis_cross_reference" in patterns:
            hints.append("生成前核对本章 synopsis、评论、注释和交叉引用，避免遗漏已标记线索。")
        if "snowflake_premise_expansion" in patterns:
            hints.append("从一句话前提扩展到段落摘要、完整梗概和章节目标，防止续写偏离核心承诺。")
        if "outliner_index_cards" in patterns:
            hints.append("把章节和场景作为可重排卡片处理，重排时同步保留人物、伏笔和状态证据。")
        if "narrative_strand_mapping" in patterns:
            hints.append("按叙事线、fabula、地理/时间/社会背景检查章节承接，不只看单章爽点。")
        if "character_depth_interview" in patterns:
            hints.append("重大人物转折前先核对欲望、恐惧、矛盾、社会面具和压力来源。")
        if "mindmap_visual_planning" in patterns:
            hints.append("脑图节点只作为创意候选；进入正史前必须提升为大纲、卡片或圣经字段。")
        if "human_synopsis_gate" in patterns:
            hints.append("章节梗概进入正文前必须先过人工/显式验收；不满意时重新生成或修改梗概，而不是带病扩写。")
        if "retrieval_guided_span_rewrite" in patterns:
            hints.append("改写已有长篇时先检索相关正文片段和剧情纲要，只改命中的片段，并同步写出纲要增量。")
        if "runtime_artifact_trace" in patterns:
            hints.append("生成前保存意图、选入上下文、规则栈和追踪信息，便于复盘为什么本章这样写。")
        if "schema_validated_state_delta" in patterns:
            hints.append("LLM 产出的状态增量必须过 schema 校验；坏数据拒绝写入，避免连续性错误滚雪球。")
        if "recursive_adaptive_planning" in patterns:
            hints.append("复杂写作任务按递归规划拆成检索、推理、构思和成文子任务，并允许根据上下文动态重规划。")
        if "canon_drift_continuity_qa_gate" in patterns:
            hints.append("Before continuation, produce a scene-focused context pack and turn canon-drift QA failures into hard constraints.")
        if "local_rag_writing_ide_gate" in patterns:
            hints.append("Local RAG may recall canon and approved notes, but source-deconstruction material cannot be merged directly into continuation canon.")
        if "patch_replay_manuscript_state_gate" in patterns:
            hints.append("Every continuation or revision should write a replayable patch/state record so the latest manuscript can be rebuilt from outline plus patches.")
        if "impromptu_thread_pool_chapter_gate" in patterns:
            hints.append("For ad-hoc continuation, convert the user's chapter intent into a single-chapter blueprint before drafting, then settle open threads after finalize.")
        if "offline_inspiration_bank_style_gate" in patterns:
            hints.append("Inspiration-bank retrieval can guide tone or lore, but continuation prompts must label whether each item is accepted canon, note, or style-only reference.")
        if "atelier_phase_pipeline_gate" in patterns:
            hints.append("Choose the atelier control mode up front: full automation, assisted phase handoff, or manual approval before any agent stage writes canon.")
        if "book_mining_genesis_automation_gate" in patterns:
            hints.append("Before same-type continuation, separate source-book mining patterns from new canon seeds; only scored and accepted canon-seed fields may drive automation.")
        if "multi_book_autopilot_studio_gate" in patterns:
            hints.append("For multi-book runs, bind each continuation to one book profile, visible session, continue limit, and periodic full-book logic check.")
        if "longrun_commit_projection_health_gate" in patterns:
            hints.append("Before drafting, confirm the latest accepted chapter commit has updated state, summaries, memory, and read-model projections.")
        if "fresh_context_chapter_iteration_gate" in patterns:
            hints.append("Start each chapter pass from fresh context: story bible, manifest, progress log, and the next incomplete chapter, not from chat-memory residue.")
        if "inline_human_machine_coauthoring_gate" in patterns:
            hints.append("Use inline human-machine edits for localized continuation repair; preserve accepted chapter context and rerun review on only the changed spans.")
        if "hierarchical_orchestrator_generation_gate" in patterns:
            hints.append("Select the continuation scope explicitly: new volume, new arc, next chapter, or scene repair; do not let an orchestrator guess the hierarchy silently.")
        if "batch_continuation_progress_queue_gate" in patterns:
            hints.append("For batch continuation, consume the next queued chapter only after its prior chapter is accepted and progress state is current.")
        if "homogeneity_prompt_variation_gate" in patterns:
            hints.append("Before continuing multiple chapters, vary pressure source, POV distance, scene function, and payoff style to prevent samey chapter templates.")
        if "local_author_data_boundary_gate" in patterns:
            hints.append("Treat local packaged apps, upgrade links, and model endpoint settings as runtime surfaces; use only static pattern notes in drafting prompts.")
        if "prompt_preset_variable_library_gate" in patterns:
            hints.append("Select prompt presets by task, mode, and context budget; resolve variables explicitly before drafting so hidden defaults do not steer continuation.")
        if "imported_manuscript_migration_outline_gate" in patterns:
            hints.append("When continuing an imported manuscript, draft from the parsed chapter map and generated outline, not from unbounded raw imported text.")
        if "style_dna_reference_library_gate" in patterns:
            hints.append("Use style-DNA references as abstract craft constraints only; never inject reference prose or distinctive source turns into continuation prompts.")
        if "draft_candidate_promotion_gate" in patterns:
            hints.append("Generate continuation as a draft candidate first; review, compare, and promote only after the author or acceptance gate confirms it.")
        if "privacy_preserving_local_index_gate" in patterns:
            hints.append("Retrieve local search context through metadata-scoped manifests; prompts should name included fields and exclude plaintext that was not explicitly selected.")
        if "chapter_description_continuity_bridge_gate" in patterns:
            hints.append("章节描述只能承接已接受的前文摘要、章节变化包和当前大纲，不用未验收草稿补连续性。")
        if "selective_streaming_regeneration_gate" in patterns:
            hints.append("局部重生必须锁定 specific chapter、影响段落和邻近冻结章节，不能覆盖未点名章节或整书状态。")
        if "research_citation_boundary_gate" in patterns:
            hints.append("研究引用只作为证据、素材和事实边界；虚构正文采用前要经过作者验收，不能把外部事实直接写成正史。")
        if "beta_reader_summary_context_gate" in patterns:
            hints.append("Beta reader 评审提示词必须绑定 previous chapter summaries、当前章节 id 和反馈风格，读者反应不得改写 canon。")
        if "style_vocab_world_card_extraction_gate" in patterns:
            hints.append("Build the continuation prompt from reviewed style vocabulary, world cards, character cards, and chapter-local patch scope; keep each layer visible.")
        if "prompt_only_decay_ceiling_gate" in patterns:
            hints.append("If using prompt-only continuation, state the chapter-count ceiling, decay risks, and wrap-up mode trigger before drafting.")
        if "serial_platform_minimum_audit_gate" in patterns:
            hints.append("Include the minimum serial audit checklist in the prompt so the draft targets hook, dialogue ratio, anti-loop, battle logic, and AI-tone cleanup.")
        if "multi_agent_reject_retry_review_gate" in patterns:
            hints.append("Ask each agent pass to return score, reject reason, retry count, and planning-return decision instead of only revised prose.")
        if "story_bible_context_packet_branch_gate" in patterns:
            hints.append("Name the story-bible context packet, branch id, recent summaries, promises, and savepoint before any continuation or rewrite.")
        if "memory_augmented_delta_verification_gate" in patterns:
            hints.append("Request chapter deltas separately from prose and verify them with targeted questions before they can seed the next prompt.")
        if "statistical_style_benchmark_rewrite_gate" in patterns:
            hints.append("Use statistical style benchmarks as threshold labels for rhythm, sensory density, dialogue, repetition, and voice drift; never paste benchmark prose.")
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
        if "continuity_bridge_window" in patterns:
            hints.append("Persist the bridge input set for each episode: recent chapters used, state slices selected, omitted risks, and why they were enough.")
        if "episode_range_rewrite_scope" in patterns:
            hints.append("When rewriting a chapter range, store the impact scope and all downstream chapters that must be re-polished or rechecked.")
        if "backup_restore_checkpoint" in patterns:
            hints.append("Create a restore checkpoint before range rewrites, bulk polishing, or schema migrations so rejected changes can roll back cleanly.")
        if "editor_notes_feedback_loop" in patterns:
            hints.append("Keep editor notes as open/closed state across chapters instead of burying them in review prose.")
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
        if "reader_rating_signal_model" in patterns:
            hints.append("Persist aggregate reader signals as external calibration metadata: rating bucket, shelf/tag expectation, to-read intent, and source/date.")
        if "review_spoiler_sentiment_corpus" in patterns:
            hints.append("Store review clusters by opaque ids and aggregate labels; never keep reviewer identity or verbatim review text in drafting context.")
        if "beta_reader_archetype_panel" in patterns:
            hints.append("Attach beta-reader reports to chapter state with archetype, tension, pacing, want-to-continue, confusion, favorite moment, and stumble point.")
        if "comp_title_market_positioning" in patterns:
            hints.append("Keep comp-title matrices as market-position artifacts, not canon; expire them when genre target, audience, or premise changes.")
        if "local_reader_experience_editor" in patterns:
            hints.append("Persist reader-experience findings as review tasks tied to chapter ids so hook, curiosity, and rhythm fixes can be verified after rewrite.")
        if "sourcebook_author_workbench" in patterns:
            hints.append("Persist sourcebook entries as author-owned state; Writing Partner suggestions remain proposals until accepted.")
        if "semantic_long_context_search" in patterns:
            hints.append("Store semantic search results with query, matched artifact, inclusion reason, and whether each hit became canon evidence.")
        if "parallel_agent_chapter_pipeline" in patterns:
            hints.append("Record each agent stage job, input artifact set, output path, validation status, and aggregate revision finding for replayable long runs.")
        if "cross_chapter_redundancy_audit" in patterns:
            hints.append("Persist redundancy findings across chapters so repeated weak patterns can be fixed in batch revision rather than forgotten.")
        if "research_taxonomy_story_map" in patterns:
            hints.append("Persist the chosen method taxonomy category for each writing run so later reviews know whether it was planning, agentic, RAG, multimodal, or benchmark-driven.")
        if "agentic_book_planner_pipeline" in patterns:
            hints.append("Store agent role outputs separately; Writer drafts should cite Story Bible, Plot Thread, Chapter Outline, Editor, and Continuity Checker artifact ids.")
        if "rag_synopsis_spine" in patterns:
            hints.append("Keep the full synopsis spine, chapter summaries, retrieval query, included context, and omitted context together for resumable continuation.")
        if "anti_repetition_prompt_rules" in patterns:
            hints.append("Persist anti-repetition rule hits and token/repeated-pattern stats across chapters so batch repair can target recurring prose habits.")
        if "prompt_recipe_experiment_grid" in patterns:
            hints.append("Persist prompt recipe, sampling parameters, review rubric, and keep/discard decision for every experiment run.")
        if "append_only_generation_review_log" in patterns:
            hints.append("Use append-only generation/review logs for experiment runs so interrupted sweeps resume without rewriting prior evidence.")
        if "nrd_task_tree_pipeline" in patterns:
            hints.append("Track NRD task-tree nodes, tags, revision pass status, and continuity-report outcomes across arcs, chapters, and scenes.")
        if "top_down_story_planning" in patterns:
            hints.append("Persist the hierarchy from book spec to act, chapter, scene, and previous-scene context so partial generation can resume at the right scale.")
        if "plain_text_project_storage" in patterns:
            hints.append("Keep stable ids for manuscript text units so generated changes can be diffed and reverted without losing notes.")
        if "synopsis_cross_reference" in patterns:
            hints.append("Persist synopsis and cross-reference links beside chapter state so prompts can cite why a note is relevant.")
        if "outliner_index_cards" in patterns:
            hints.append("When outline cards are reordered, record previous order, new order, and affected dependencies.")
        if "narrative_strand_mapping" in patterns:
            hints.append("Track narrative strand membership per scene so a strand does not disappear during long continuation.")
        if "character_depth_interview" in patterns:
            hints.append("Store character-depth answers separately from transient scene mood; update them only from accepted evidence.")
        if "human_synopsis_gate" in patterns:
            hints.append("Record whether synopsis and chapter summaries were accepted, edited, or regenerated before drafting prose.")
        if "retrieval_guided_span_rewrite" in patterns:
            hints.append("Persist retrieved span ids, rewrite decision, and outline sync delta so localized edits do not drift the whole book.")
        if "runtime_artifact_trace" in patterns:
            hints.append("Store intent, selected context, rule stack, and trace artifacts beside each chapter run for replay.")
        if "schema_validated_state_delta" in patterns:
            hints.append("Persist accepted and rejected state deltas with validation errors before mutating canon state.")
        if "recursive_adaptive_planning" in patterns:
            hints.append("Track adaptive task-tree nodes and replan reasons so long runs can resume at the right subtask.")
        if "workflow_manuscript_compilation" in patterns:
            hints.append("Keep compilation manifests separate from canon; compiled manuscripts derive from ordered accepted scenes.")
        if "writing_session_goal_tracking" in patterns:
            hints.append("Record session word-count goals and actual accepted-word counts without letting numeric goals override continuity.")
        if "inspectable_run_workspace" in patterns:
            hints.append("Expose session, storyboard, manuscript surface, and memory-bank refs so reviewers can inspect a run without hidden state.")
        if "story_contract_commit_chain" in patterns:
            hints.append("Persist story contracts and accepted chapter commits as the canonical chain; every derived state should trace back to a commit id.")
        if "fact_snapshot_delta_gate" in patterns:
            hints.append("Store before-state, proposed delta, validation result, and after-state for every accepted chapter fact update.")
        if "projection_sync_observability" in patterns:
            hints.append("Keep projection logs for state/index/summary/memory/vector updates so stale read models are visible before the next prompt.")
        if "foreshadowing_debt_budget" in patterns:
            hints.append("Track foreshadowing debt with status, expected payoff window, context-budget reservation, and last chapter touched.")
        if "draft_stage_revision_ladder" in patterns:
            hints.append("Persist Draft A/B/C status and the next-chapter handoff separately from the final accepted prose.")
        if "rolling_summary_context_trim" in patterns:
            hints.append("Store rolling summaries, context trim manifests, and selected relevant passages beside the chapter run for restore and review.")
        if "pairwise_story_comparison_ranking" in patterns:
            hints.append("Store matched variant ids, shared brief, evaluator notes, order-swap result, and keep/discard decision for every pairwise comparison.")
        if "multidimensional_quality_rubric" in patterns:
            hints.append("Persist rubric scores and top ranked weaknesses so later revisions target the largest quality gaps first.")
        if "story_theory_beat_evaluation" in patterns:
            hints.append("Record beat task type, required narrative function, preservation requirements, and pass/fail criteria before accepting a revision.")
        if "constraint_specificity_creativity_benchmark" in patterns:
            hints.append("Store each required constraint, satisfaction evidence, and coherence tradeoff so highly specific prompts remain auditable.")
        if "style_axis_diversity_fingerprint" in patterns:
            hints.append("Persist style-axis fingerprints per chapter to detect voice narrowing, rhythm drift, or unplanned POV changes across batches.")
        if "event_outline_history_compression" in patterns:
            hints.append("Keep compressed history tied to the current event and chapter plan so omitted history can be inspected when continuity breaks.")
        if "agentic_story_world_simulation" in patterns:
            hints.append("Record simulated agent choices as proposals with source state and acceptance status; do not merge simulated outcomes into canon automatically.")
        if "trope_inventory_similarity_gate" in patterns:
            hints.append("Track source and draft trope inventories as abstract genre signals; shared trope count is allowed only when concrete events, names, and order are independent.")
        if "trope_graph_expectation_map" in patterns:
            hints.append("Persist trope graph expectation edges separately from canon facts so genre conventions do not become copied plot obligations.")
        if "trope_density_novelty_budget" in patterns:
            hints.append("Record trope density, repeated archetype load, and novelty budget per arc before accepting same-type continuation plans.")
        if "trope_source_boundary_review" in patterns:
            hints.append("Store trope-source provenance as metadata only; never keep scraped page prose or live-site fetch output in generation context by default.")
        if "source_license_detection_gate" in patterns:
            hints.append("Persist source license status, detector confidence, reviewer decision, and blocked/allowed usage before any source text enters analysis or drafting context.")
        if "spdx_reuse_compliance_gate" in patterns:
            hints.append("Store SPDX ids, copyright holders, attribution notes, and file/source-level provenance separately from story canon.")
        if "public_domain_corpus_boundary" in patterns:
            hints.append("Record public-domain source, observed metadata, jurisdiction caveat, and extraction settings before using public-domain text for deconstruction.")
        if "canon_drift_continuity_qa_gate" in patterns:
            hints.append("Keep continuity QA findings as state, not prose advice: failed facts block drafting until resolved or explicitly waived.")
        if "interactive_reader_writer_loop_gate" in patterns:
            hints.append("Treat reader/user guidance as a new state delta with acceptance status before it changes chapter files or canon memory.")
        if "microkernel_skill_plugin_isolation_gate" in patterns:
            hints.append("Plugin or skill outputs must publish through explicit stage events and cannot mutate canon when their validation or isolation gate fails.")
        if "abstract_style_learning_skill_gate" in patterns:
            hints.append("Store style-learning output as abstract craft axes and banned carryover items, never as reusable source phrases or source-specific facts.")
        if "impromptu_thread_pool_chapter_gate" in patterns:
            hints.append("Treat open_threads as state buckets: unresolved, partially paid, and development-needed items must be updated only after accepted chapter finalize.")
        if "offline_inspiration_bank_style_gate" in patterns:
            hints.append("Keep inspiration-bank files outside canon memory until the author accepts a fact; style mimicry output stays in a separate style-boundary record.")
        if "atelier_phase_pipeline_gate" in patterns:
            hints.append("Persist each atelier phase handoff as beat tree, hook audit, owner, acceptance decision, and next phase input.")
        if "book_mining_genesis_automation_gate" in patterns:
            hints.append("Store book-mining pattern ids, genesis scores, accepted canon seed, and automation gate decisions as separate state layers.")
        if "multi_book_autopilot_studio_gate" in patterns:
            hints.append("Persist per-book profile, session owner, autopilot counters, stop phrases, and full-book check cadence before continuing unattended batches.")
        if "longrun_commit_projection_health_gate" in patterns:
            hints.append("Treat .story-system artifacts as source of truth and .webnovel projections as derived read models with freshness checks.")
        if "fresh_context_chapter_iteration_gate" in patterns:
            hints.append("Store the chapter manifest, last completed chapter, review result, and progress.txt update before scheduling the next fresh-context pass.")
        if "inline_human_machine_coauthoring_gate" in patterns:
            hints.append("Persist localized revision spans with author decision, reason, and downstream state impact instead of flattening them into an untraceable new chapter.")
        if "hierarchical_orchestrator_generation_gate" in patterns:
            hints.append("Persist hierarchy state for volume, arc, chapter, and scene scopes so a continuation run can resume at the right level.")
        if "batch_continuation_progress_queue_gate" in patterns:
            hints.append("Persist queue cursor, completed chapter ids, failed attempts, retry limits, and skipped chapters before any batch continuation advances.")
        if "homogeneity_prompt_variation_gate" in patterns:
            hints.append("Store homogeneity findings across chapter windows so repeated rhythm, hook, and payoff shapes can be fixed before they propagate.")
        if "local_author_data_boundary_gate" in patterns:
            hints.append("Keep local author data, external source metadata, generated drafts, and update/download evidence in separate manifests.")
        if "prompt_preset_variable_library_gate" in patterns:
            hints.append("Persist preset id, variable values, model parameters, and prompt version with each chapter attempt for reproducible repairs.")
        if "imported_manuscript_migration_outline_gate" in patterns:
            hints.append("Persist imported file checksum, chapter parser result, generated outline ids, and which imported chapters were accepted as canon.")
        if "style_dna_reference_library_gate" in patterns:
            hints.append("Store style-DNA entries as source-boundary metadata with abstraction level, allowed use, and copy-risk reviewer notes.")
        if "draft_candidate_promotion_gate" in patterns:
            hints.append("Keep draft, review, rewrite candidate, rejected, and confirmed chapter states separate so rejected prose cannot update memory.")
        if "privacy_preserving_local_index_gate" in patterns:
            hints.append("Local indexes should store metadata, hashes, labels, and retrieval reasons; manuscript plaintext stays in explicit project artifacts.")
        if "chapter_description_continuity_bridge_gate" in patterns:
            hints.append("Persist chapter-description contracts with accepted prior-summary ids, outline slot, continuity assumptions, and reviewer decision.")
        if "selective_streaming_regeneration_gate" in patterns:
            hints.append("Persist regeneration scope as specific chapter id, protected neighboring chapters, changed spans, checkpoint id, and rollback target.")
        if "research_citation_boundary_gate" in patterns:
            hints.append("Persist research citations in a source-evidence manifest with provenance, allowed-use label, fiction-fact boundary, and canon promotion status.")
        if "beta_reader_summary_context_gate" in patterns:
            hints.append("Attach beta-reader feedback to previous chapter summaries, review style, current chapter id, and accepted/rejected revision tasks.")
        if "style_vocab_world_card_extraction_gate" in patterns:
            hints.append("Persist style vocabulary, world cards, character cards, and local rewrite spans as separate state records with reviewer provenance.")
        if "prompt_only_decay_ceiling_gate" in patterns:
            hints.append("Persist prompt-only run length, decay findings, wrap-up mode entry, and the point where refreshed context becomes mandatory.")
        if "serial_platform_minimum_audit_gate" in patterns:
            hints.append("Persist audit cadence results: per-chapter minimum checks, five-chapter loop checks, and ten-chapter full audit decisions.")
        if "multi_agent_reject_retry_review_gate" in patterns:
            hints.append("Persist multi-agent retry trace with role, score, reject reason, retry budget, and return-to-planning marker.")
        if "story_bible_context_packet_branch_gate" in patterns:
            hints.append("Persist context packet lineage, branch/savepoint ids, restore targets, recent summaries, promises, and fact-extraction decisions.")
        if "memory_augmented_delta_verification_gate" in patterns:
            hints.append("Persist every extracted delta with chapter id, previous value, proposed value, deterministic accumulation order, and verification result.")
        if "statistical_style_benchmark_rewrite_gate" in patterns:
            hints.append("Persist style benchmark policy, failed metric, style preset, rewrite span, and overfit/copy-risk decision for every rewrite.")
        if "attribution_derivative_work_gate" in patterns:
            hints.append("Persist attribution and derivative-work review as source-boundary metadata; it must not mutate characters, plot, or style as canon facts.")
        if "source_entity_redaction_gate" in patterns:
            hints.append("Persist source-entity redaction decisions before analysis or drafting so copied names, places, factions, artifacts, and powers cannot silently enter canon.")
        if "custom_entity_label_inventory" in patterns:
            hints.append("Store fiction-specific entity labels separately from ordinary NER output: character, faction, location, artifact, title, ability, rank, and invented term.")
        if "placeholder_alias_consistency_map" in patterns:
            hints.append("Keep a stable placeholder and alias map for redacted sources, and review replacement collisions before any remapped context is reused.")
        if "proper_noun_leakage_review" in patterns:
            hints.append("Record source proper-noun blocklists and approved exceptions as review metadata before accepting continuation or same-type drafts.")
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

    def _build_mode_contract_generation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "mode_contract_generation_gate" not in patterns:
            return []
        return [
            "Before generation, choose a visible mode contract: output shape, genre, audience, POV/narrator, ending style, source-material role, and minimum completeness threshold.",
            "Selected mode wins over incidental words in the prompt; mode, axis tags, and rewrite reason should be recorded with each generated draft.",
            "Reject under-length or generic drafts by asking for a bounded rewrite from the same accepted inputs, not by adding source-specific people, places, or plot facts.",
        ]

    def _build_source_study_method_bank_isolation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "source_study_method_bank_isolation_gate" not in patterns:
            return []
        return [
            "Keep source-study outputs in a separate method bank: chunk analysis, chapter beats, style metrics, and extracted techniques do not directly mutate creative canon.",
            "Promote only abstract methods into planning: beat function, pacing device, reveal technique, reader promise, and craft rule; raw source facts stay out.",
            "For same-type creation, cite method-bank ids in prompts so reviewers can verify inspiration without loading source passages as context.",
        ]

    def _build_inline_human_machine_coauthoring_gate_hints(self, patterns: set[str]) -> list[str]:
        if "inline_human_machine_coauthoring_gate" not in patterns:
            return []
        return [
            "Treat generated prose as a starting point: author edits, localized polishing, and precise modifications must stay visible as reviewable spans.",
            "Inline revision should record before/after text, edit intent, affected canon fields, and whether the author accepted or rejected the change.",
            "Do not regenerate a whole chapter when only one paragraph, hook, or dialogue beat needs repair; localize the edit and rerun copy-risk review on the changed span.",
        ]

    def _build_hierarchical_orchestrator_generation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "hierarchical_orchestrator_generation_gate" not in patterns:
            return []
        return [
            "Drive long-form writing from hierarchy: book premise -> volume -> arc -> chapter plan -> scene/draft, with a trace for every orchestrator decision.",
            "Each generate/validate/improve loop should name its stage, input artifacts, failed checks, accepted output, and next planned scope.",
            "Do not let a high-level orchestrator silently skip author approval when it creates a new volume, arc, or canon-changing chapter branch.",
        ]

    def _build_batch_continuation_progress_queue_gate_hints(self, patterns: set[str]) -> list[str]:
        if "batch_continuation_progress_queue_gate" not in patterns:
            return []
        return [
            "Represent batch continuation as a queue of chapter jobs with source state, retry budget, validation status, and next incomplete chapter pointer.",
            "Auto-continuation may advance only from accepted progress state; failed or logic-confused chapters stay pending until reviewed.",
            "Batch jobs should preserve user prompt, outline slice, chapter plan, and generated artifact id so interrupted runs can resume without guessing.",
        ]

    def _build_homogeneity_prompt_variation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "homogeneity_prompt_variation_gate" not in patterns:
            return []
        return [
            "Track samey outputs across adjacent chapters: repeated openings, conflict shape, sentence rhythm, payoff cadence, and character reaction loops.",
            "Variation fixes should change prompt axes such as topic seed, pressure source, POV distance, scene type, or information release—not just synonyms.",
            "For same-type creation, novelty budget must be checked before batch generation so copied genre beats do not harden into a repeated template.",
        ]

    def _build_local_author_data_boundary_gate_hints(self, patterns: set[str]) -> list[str]:
        if "local_author_data_boundary_gate" not in patterns:
            return []
        return [
            "Keep local author data boundaries explicit: project files, prompts, model endpoints, packaged binaries, update channels, and backups are separate review surfaces.",
            "Static intake can record download/update risks, but it must not execute packaged apps, auto-updaters, or local model connectors without a runtime contract.",
            "Before any source material enters drafting, record whether it is accepted canon, author-owned note, public metadata, or blocked external text.",
        ]

    def _build_prompt_preset_variable_library_gate_hints(self, patterns: set[str]) -> list[str]:
        if "prompt_preset_variable_library_gate" not in patterns:
            return []
        return [
            "Prompt presets should declare task, mode, required variables, context sources, model parameters, and reviewer-visible defaults.",
            "Variable substitution must be resolved before a prompt is sent or saved so hidden template state cannot alter a continuation silently.",
            "Track prompt usage and outcome notes by preset version; do not let one successful preset become a global default for every chapter mode.",
        ]

    def _build_imported_manuscript_migration_outline_gate_hints(self, patterns: set[str]) -> list[str]:
        if "imported_manuscript_migration_outline_gate" not in patterns:
            return []
        return [
            "Treat imported manuscripts as migration inputs: record checksum, parser result, chapter map, generated summaries, and acceptance status before drafting.",
            "Generate or review per-chapter outlines after import so continuation can target a known chapter slot rather than raw unbounded source text.",
            "Selective import/export should keep prompt libraries, API settings, manuscript text, and derived outlines in separate boundary classes.",
        ]

    def _build_style_dna_reference_library_gate_hints(self, patterns: set[str]) -> list[str]:
        if "style_dna_reference_library_gate" not in patterns:
            return []
        return [
            "A style-DNA library stores abstract craft features such as rhythm, scene density, dialogue pressure, and payoff shape, not source paragraphs.",
            "Each reference-library item needs provenance, license/posture, allowed-use label, abstraction summary, and copy-risk review before it informs same-type creation.",
            "For imitation-like work, cite style-DNA ids and novelty requirements; never ask the model to reproduce a named author or source passage.",
        ]

    def _build_draft_candidate_promotion_gate_hints(self, patterns: set[str]) -> list[str]:
        if "draft_candidate_promotion_gate" not in patterns:
            return []
        return [
            "AI output starts as a draft candidate. Review, rewrite candidates, and manual edits must stay separate from confirmed chapter text.",
            "Promotion to confirmed chapter requires an explicit acceptance event with source candidate id, reviewer, reason, and downstream memory update list.",
            "Rejected or smoke-test drafts can remain as evidence but must not seed Memory Bank, context packs, or accepted chapter summaries.",
        ]

    def _build_privacy_preserving_local_index_gate_hints(self, patterns: set[str]) -> list[str]:
        if "privacy_preserving_local_index_gate" not in patterns:
            return []
        return [
            "Local search indexes should default to metadata-only fields such as title, logline, labels, word count, character names, hashes, and retrieval reasons.",
            "Offline-first or browser-local storage is still a privacy surface: record encryption, export, backup, deletion, and provider-call boundaries.",
            "Before prompt assembly, prove which local plaintext snippets were selected by the user or gate; metadata hits alone should not leak manuscript plaintext.",
        ]

    def _build_chapter_description_continuity_bridge_gate_hints(self, patterns: set[str]) -> list[str]:
        if "chapter_description_continuity_bridge_gate" not in patterns:
            return []
        return [
            "Treat chapter descriptions as continuity contracts: each description cites accepted previous chapter summaries, outline slot, active character state, and unresolved hooks.",
            "A generated chapter may elaborate the chapter description, but it must not invent bridge facts missing from accepted summaries or approved chapter-change packages.",
            "For same-type or拆书续写, remap source chapter functions into new description contracts before drafting, rather than copying source chapter order or labels.",
        ]

    def _build_selective_streaming_regeneration_gate_hints(self, patterns: set[str]) -> list[str]:
        if "selective_streaming_regeneration_gate" not in patterns:
            return []
        return [
            "Regeneration scope must name the specific chapter, protected neighboring chapters, affected spans, retry budget, and rollback checkpoint before text starts streaming.",
            "Streaming output remains a draft candidate until accepted; partial stream failures must not update the rest of the manuscript or derived memory.",
            "A specific chapter repair may refresh its local summary and change package, but it cannot overwrite other chapters or whole-book canon without a separate review gate.",
        ]

    def _build_research_citation_boundary_gate_hints(self, patterns: set[str]) -> list[str]:
        if "research_citation_boundary_gate" not in patterns:
            return []
        return [
            "Research sources and citation styles belong in a source-evidence manifest, not in fiction canon by default.",
            "Use cited material as factual boundary, atmosphere, or craft evidence; promote it into story state only through an accepted decision with provenance and license/posture notes.",
            "Quality, plagiarism, and citation checks should review source leakage before publication export or same-type drafting acceptance.",
        ]

    def _build_beta_reader_summary_context_gate_hints(self, patterns: set[str]) -> list[str]:
        if "beta_reader_summary_context_gate" not in patterns:
            return []
        return [
            "Beta-reader review must bind feedback to previous chapter summaries, current chapter id, spoiler window, and selected review style.",
            "Separate fan, editorial, and line-note feedback from canon: feedback creates revision tasks, not automatic story facts.",
            "If previous chapter summaries are stale, regenerate or review the summaries before asking for contextual feedback on the next chapter.",
        ]

    def _build_style_vocab_world_card_extraction_gate_hints(self, patterns: set[str]) -> list[str]:
        if "style_vocab_world_card_extraction_gate" not in patterns:
            return []
        return [
            "Extract style vocabulary, world cards, character cards, and chapter-local modification scopes into separate reviewed artifacts before drafting.",
            "A style vocabulary library may guide diction and rhythm, but worldbuilding facts must enter canon only through reviewed world-card updates.",
            "For same-type creation, remap source style vocabulary into abstract levers and create new world cards instead of carrying source proper nouns or facts.",
        ]

    def _build_prompt_only_decay_ceiling_gate_hints(self, patterns: set[str]) -> list[str]:
        if "prompt_only_decay_ceiling_gate" not in patterns:
            return []
        return [
            "Track prompt-only continuation as a bounded mode: record chapter count, context loss, comfort-zone decay, and wrap-up mode triggers.",
            "Prompt-only runs need an explicit ceiling; after the stress-test window, require refreshed bible/context packets rather than relying on chat residue.",
            "Use wrap-up mode only as a controlled recovery path, not as proof that a prompt-only workflow can sustain long-form canon.",
        ]

    def _build_serial_platform_minimum_audit_gate_hints(self, patterns: set[str]) -> list[str]:
        if "serial_platform_minimum_audit_gate" not in patterns:
            return []
        return [
            "Define a minimum chapter audit set before serial continuation: AI-tone cleanup, battle logic, dialogue ratio, loop pattern, hook, and chapter summary.",
            "Run lightweight cadence checks every few chapters and a full audit window every ten chapters before updating long-run plans.",
            "Platform-flavored de-AI rewriting should emit findings and diffs; it must not silently flatten voice or overwrite accepted canon.",
        ]

    def _build_multi_agent_reject_retry_review_gate_hints(self, patterns: set[str]) -> list[str]:
        if "multi_agent_reject_retry_review_gate" not in patterns:
            return []
        return [
            "Multi-agent drafting needs a reject/retry trace: actor, score, failed criterion, retry count, and whether the work returns to planning.",
            "Cap rewrite retries and require a planning handoff when consistency or author review remains below threshold after the budget is spent.",
            "Architect, writer, consistency checker, and author roles should exchange structured findings, not mutate bible or chapter text out of order.",
        ]

    def _build_story_bible_context_packet_branch_gate_hints(self, patterns: set[str]) -> list[str]:
        if "story_bible_context_packet_branch_gate" not in patterns:
            return []
        return [
            "Assemble each drafting context packet from story bible, recent summaries, active promises, branch id, savepoint, and allowed restore target.",
            "Branch and savepoint metadata must travel with context packets so rejected rewrites can roll back prose, bible deltas, and summaries together.",
            "Dual-persona editorial review can propose fact extraction, but canonical fact write-back requires accepted evidence and branch lineage.",
        ]

    def _build_memory_augmented_delta_verification_gate_hints(self, patterns: set[str]) -> list[str]:
        if "memory_augmented_delta_verification_gate" not in patterns:
            return []
        return [
            "Use memory-augmented delta extraction chapter by chapter: extract current-chapter facts, stage deltas, then verify with targeted questions.",
            "Deterministic accumulation into a delta fact index must keep source chapter id, previous value, proposed value, verification result, and rejection reason.",
            "Chain-of-Verification findings should gate continuity acceptance before deltas can update the knowledge graph or next-chapter context.",
        ]

    def _build_statistical_style_benchmark_rewrite_gate_hints(self, patterns: set[str]) -> list[str]:
        if "statistical_style_benchmark_rewrite_gate" not in patterns:
            return []
        return [
            "Use 22-book or similar statistical benchmarks as abstract style thresholds, not as copied prose, scene inventory, or source-specific voice.",
            "A smart rewriter should record which metric failed, the target style preset, the rewritten span, and whether the rewrite improved or overfit.",
            "Style benchmark gates should cover rhythm, sensory density, dialogue, repetition, slop, ending quality, and character voice profile drift.",
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

    def _build_plain_text_project_storage_hints(self, patterns: set[str]) -> list[str]:
        if "plain_text_project_storage" not in patterns:
            return []
        return [
            "Keep chapters, notes, summaries, and analysis as stable human-readable text units with durable ids.",
            "Prefer diffable manuscript units for long-form state so reviewers can compare, revert, and synchronize changes.",
            "Generated edits should target a named text unit rather than rewriting an opaque whole-project blob.",
        ]

    def _build_synopsis_cross_reference_hints(self, patterns: set[str]) -> list[str]:
        if "synopsis_cross_reference" not in patterns:
            return []
        return [
            "Attach synopsis, comments, notes, and cross-references to the chapter or scene they explain.",
            "Before drafting, list which synopsis notes and refs are active for this chapter and why.",
            "Cross-references should point to canon artifacts, not to source-intake inspiration as story fact.",
        ]

    def _build_snowflake_premise_expansion_hints(self, patterns: set[str]) -> list[str]:
        if "snowflake_premise_expansion" not in patterns:
            return []
        return [
            "Preserve a premise chain: one-sentence promise -> paragraph summary -> full summary -> chapter goals.",
            "Review new outlines against the premise chain so expanded detail does not contradict the core story promise.",
            "For same-type creation, transform the premise chain before generating scenes; do not expand the source premise under new names.",
        ]

    def _build_outliner_index_cards_hints(self, patterns: set[str]) -> list[str]:
        if "outliner_index_cards" not in patterns:
            return []
        return [
            "Represent chapters and scenes as reorderable outline/index cards with goal, conflict, hook, status, and dependencies.",
            "When a card moves, re-check timeline, setup/payoff, character state, and narrative strand dependencies.",
            "Use cards to stage structural changes before updating bible state or accepted chapter memory.",
        ]

    def _build_narrative_strand_mapping_hints(self, patterns: set[str]) -> list[str]:
        if "narrative_strand_mapping" not in patterns:
            return []
        return [
            "Map premise, fabula, narrative strands, and geographic/temporal/social setting context before accepting arc changes.",
            "Every scene should declare which narrative strand it advances, complicates, rests, or resolves.",
            "Same-type writing may borrow strand function, but must rebuild the concrete fabula and setting context.",
        ]

    def _build_character_depth_interview_hints(self, patterns: set[str]) -> list[str]:
        if "character_depth_interview" not in patterns:
            return []
        return [
            "Use character-depth questions before major turns: desire, fear, contradiction, wound, social mask, and pressure source.",
            "Believable character changes require visible cause, cost, and after-state, not just a new trait label.",
            "Store depth answers as character-card evidence only after accepted scenes prove them.",
        ]

    def _build_mindmap_visual_planning_hints(self, patterns: set[str]) -> list[str]:
        if "mindmap_visual_planning" not in patterns:
            return []
        return [
            "Use mindmap nodes for early idea exploration, then promote selected nodes into outline cards, bible entries, or scene tasks.",
            "Visual links should remain planning evidence until accepted into canon through review.",
            "Do not inject the whole mindmap into drafting; select the nodes directly relevant to the current chapter goal.",
        ]

    def _build_manuscript_export_formats_hints(self, patterns: set[str]) -> list[str]:
        if "manuscript_export_formats" not in patterns:
            return []
        return [
            "Treat PDF, DOCX, TXT, EPUB, Markdown, and JSON exports as derived artifacts, never as automatic canon mutations.",
            "Exports should include source state version, accepted chapter range, and generation timestamp for replay.",
        ]

    def _build_human_synopsis_gate_hints(self, patterns: set[str]) -> list[str]:
        if "human_synopsis_gate" not in patterns:
            return []
        return [
            "Generate or update the synopsis and chapter summaries before prose, then require explicit accept/edit/regenerate status.",
            "Do not draft from an unreviewed synopsis when the user is doing source-book continuation or same-type imitation.",
            "If synopsis review fails, regenerate or patch the synopsis before expanding chapters.",
        ]

    def _build_retrieval_guided_span_rewrite_hints(self, patterns: set[str]) -> list[str]:
        if "retrieval_guided_span_rewrite" not in patterns:
            return []
        return [
            "For existing-novel rewrites, retrieve the relevant body spans and outline nodes before editing.",
            "Constrain rewrite scope to named spans, then emit an outline sync delta that explains what changed.",
            "Do not rewrite unrelated chapters because a global instruction matched one local plot issue.",
        ]

    def _build_runtime_artifact_trace_hints(self, patterns: set[str]) -> list[str]:
        if "runtime_artifact_trace" not in patterns:
            return []
        return [
            "Persist run artifacts for each chapter task: intent, selected context, rule stack, and trace.",
            "Use trace artifacts to debug prompt assembly and continuity decisions instead of relying on chat memory.",
            "A context trace should explain both included context and important omitted context.",
        ]

    def _build_schema_validated_state_delta_hints(self, patterns: set[str]) -> list[str]:
        if "schema_validated_state_delta" not in patterns:
            return []
        return [
            "Represent canon mutations as typed state deltas and validate them before applying them.",
            "Reject malformed or out-of-range deltas rather than normalizing them into canon silently.",
            "Apply accepted deltas immutably so review can compare before-state, delta, and after-state.",
        ]

    def _build_recursive_adaptive_planning_hints(self, patterns: set[str]) -> list[str]:
        if "recursive_adaptive_planning" not in patterns:
            return []
        return [
            "Break long-form tasks recursively into retrieval, reasoning, planning, composition, and review subtasks.",
            "Allow replanning when retrieved context or review findings contradict the current plan.",
            "Keep the adaptive task tree inspectable so later runs know why a branch was expanded or abandoned.",
        ]

    def _build_workflow_manuscript_compilation_hints(self, patterns: set[str]) -> list[str]:
        if "workflow_manuscript_compilation" not in patterns:
            return []
        return [
            "Compile manuscripts from ordered accepted scenes through an explicit workflow, not by concatenating draft buffers.",
            "Compilation should record source scene order, filters/transforms, output path, and source state version.",
            "Keep compilation outputs derived; they must not write back into canon without review.",
        ]

    def _build_writing_session_goal_tracking_hints(self, patterns: set[str]) -> list[str]:
        if "writing_session_goal_tracking" not in patterns:
            return []
        return [
            "Track session-level word-count goals, accepted word counts, and progress status separately from quality gates.",
            "A word-count goal can guide scope, but it cannot override continuity, copy-risk, or synopsis gates.",
        ]

    def _build_inspectable_run_workspace_hints(self, patterns: set[str]) -> list[str]:
        if "inspectable_run_workspace" not in patterns:
            return []
        return [
            "Expose writing sessions, storyboard surfaces, manuscript surfaces, character/world views, and editable memory-bank refs.",
            "Each inspectable run should show current phase, selected context, accepted artifacts, pending review, and next action.",
            "Reviewers should be able to inspect the run state without reading hidden provider prompts or external project code.",
        ]

    def _build_craft_role_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "craft_role_pipeline" not in patterns:
            return []
        return [
            "Separate craft roles: architecture, character, prose, continuity, review, editing, and export should produce distinct artifacts.",
            "A review role may request changes, but canon write-back stays with the owning generation or state-sync step.",
        ]

    def _build_frontmatter_story_schema_hints(self, patterns: set[str]) -> list[str]:
        if "frontmatter_story_schema" not in patterns:
            return []
        return [
            "Use stable frontmatter-like fields for story bible, scene state, continuity questions, promises/payoffs, and chapter drafts.",
            "Keep prose bodies separate from metadata so checks can diff state without parsing the whole manuscript.",
        ]

    def _build_continuity_bridge_window_hints(self, patterns: set[str]) -> list[str]:
        if "continuity_bridge_window" not in patterns:
            return []
        return [
            "Build a compact continuity bridge from the last accepted chapters, active timeline, open hooks, character state, and editor notes.",
            "The bridge should record which recent chapters were included and why older material was omitted.",
        ]

    def _build_episode_range_rewrite_scope_hints(self, patterns: set[str]) -> list[str]:
        if "episode_range_rewrite_scope" not in patterns:
            return []
        return [
            "Range rewrites must calculate downstream impact before editing: affected chapters, polish axes, state deltas, and acceptance gates.",
            "Do not silently rewrite outside the requested range; emit a separate impact proposal for dependent chapters.",
        ]

    def _build_voice_table_polish_axis_hints(self, patterns: set[str]) -> list[str]:
        if "voice_table_polish_axis" not in patterns:
            return []
        return [
            "Create a voice table with diction, sentence endings, rhythm, nonverbal palette, taboo phrases, and motivation pressure per character.",
            "Polish dialogue against the table after continuity checks, not by flattening every character into one narrative voice.",
        ]

    def _build_boring_opening_quality_gates_hints(self, patterns: set[str]) -> list[str]:
        if "boring_opening_quality_gates" not in patterns:
            return []
        return [
            "Gate chapters for boringness, weak opening hook, flat scene purpose, missing pressure, and weak end hook before acceptance.",
            "Opening checks should protect the first scene and early chapters from exposition-only starts.",
        ]

    def _build_beat_strand_framework_hints(self, patterns: set[str]) -> list[str]:
        if "beat_strand_framework" not in patterns:
            return []
        return [
            "Map external plot, internal change, and relationship strands separately, then mark convergence beats where they collide.",
            "A beat framework is a pressure map, not a license to force every chapter into the same template.",
        ]

    def _build_anti_hallucination_plan_check_hints(self, patterns: set[str]) -> list[str]:
        if "anti_hallucination_plan_check" not in patterns:
            return []
        return [
            "Before accepting prose, verify new facts against planning documents, bible state, retrieval evidence, and accepted chapter changes.",
            "If evidence is missing, emit a continuity question or review note instead of inventing a bridge.",
        ]

    def _build_backup_restore_checkpoint_hints(self, patterns: set[str]) -> list[str]:
        if "backup_restore_checkpoint" not in patterns:
            return []
        return [
            "Create restore checkpoints before bulk generation, range rewrite, schema migration, or destructive canon merge.",
            "A restore point must name the changed artifacts so prose, plan, bible, and review state roll back together.",
        ]

    def _build_multi_level_review_trend_hints(self, patterns: set[str]) -> list[str]:
        if "multi_level_review_trend" not in patterns:
            return []
        return [
            "Review at scene, chapter, batch, and cross-chapter trend levels; local pass status cannot hide repeated drift.",
            "Track trend findings such as repeated weak hooks, voice collapse, unresolved editor notes, and pacing flatlines.",
        ]

    def _build_editor_notes_feedback_loop_hints(self, patterns: set[str]) -> list[str]:
        if "editor_notes_feedback_loop" not in patterns:
            return []
        return [
            "Persist editor notes as open, deferred, or closed items with the chapter evidence that resolves them.",
            "Next-chapter prompts should include only active notes relevant to the current beat or risk.",
        ]

    def _build_genre_parameterized_worldbuilding_hints(self, patterns: set[str]) -> list[str]:
        if "genre_parameterized_worldbuilding" not in patterns:
            return []
        return [
            "Parameterize factions, locations, conflict sources, genre promises, and taboo moves by genre/subgenre before outlining.",
            "Same-type creation should transform genre modules instead of copying source organizations, settings, or gimmicks.",
        ]

    def _build_prose_preflight_voice_calibration_hints(self, patterns: set[str]) -> list[str]:
        if "prose_preflight_voice_calibration" not in patterns:
            return []
        return [
            "Use voice samples to calibrate specificity, rhythm, warmth, and density before polishing prose.",
            "The final prose preflight removes generic AI tells while preserving factual guardrails and character voice.",
        ]

    def _build_sourcebook_author_workbench_hints(self, patterns: set[str]) -> list[str]:
        if "sourcebook_author_workbench" not in patterns:
            return []
        return [
            "Keep sourcebook entries for characters, locations, lore, items, and scene context as author-owned planning state.",
            "Writing-partner actions should propose additions or edits; accepted sourcebook entries become the only reusable canon layer.",
        ]

    def _build_semantic_long_context_search_hints(self, patterns: set[str]) -> list[str]:
        if "semantic_long_context_search" not in patterns:
            return []
        return [
            "Use semantic search to retrieve long-range context, but require an inclusion reason and source artifact id for every injected hit.",
            "Fallback retrieval should prefer accepted chapters, sourcebook entries, and knowledge-base refs over raw draft buffers.",
        ]

    def _build_contradiction_taxonomy_checker_hints(self, patterns: set[str]) -> list[str]:
        if "contradiction_taxonomy_checker" not in patterns:
            return []
        return [
            "Check long-story consistency by taxonomy: characterization, factual detail, narrative style, timeline/plot, and world rules.",
            "Each contradiction finding should name the conflicting facts, evidence locations, subtype, severity, and required repair scope.",
        ]

    def _build_parallel_agent_chapter_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "parallel_agent_chapter_pipeline" not in patterns:
            return []
        return [
            "Parallel chapter jobs need isolated workspaces, explicit input artifacts, and validation before aggregate revision.",
            "Aggregate findings from chapter reviews, full-book review, and cross-chapter audit before starting revision cycles.",
        ]

    def _build_cross_chapter_redundancy_audit_hints(self, patterns: set[str]) -> list[str]:
        if "cross_chapter_redundancy_audit" not in patterns:
            return []
        return [
            "Count repeated scene structures, weak causality bridges, flat dialogue patterns, and over-regular prose across the whole manuscript.",
            "Batch revision should fix recurring cross-chapter patterns without disturbing accepted continuity state.",
        ]

    def _build_humanization_stylometry_levers_hints(self, patterns: set[str]) -> list[str]:
        if "humanization_stylometry_levers" not in patterns:
            return []
        return [
            "Use stylometry levers only after continuity passes: sentence burstiness, specificity, discourse variation, and AI-transition removal.",
            "Humanization cannot justify copying source phrasing or inventing unsupported facts; keep factual guardrails active.",
        ]

    def _build_author_control_boundary_hints(self, patterns: set[str]) -> list[str]:
        if "author_control_boundary" not in patterns:
            return []
        return [
            "Separate AI proposals from accepted canon and keep user/author decisions visible in the run state.",
            "When output is AI-generated or synthetic, label it in artifacts instead of presenting it as human-authored final prose.",
        ]

    def _build_research_taxonomy_story_map_hints(self, patterns: set[str]) -> list[str]:
        if "research_taxonomy_story_map" not in patterns:
            return []
        return [
            "Use the story-generation taxonomy as an index-only coverage map: planning/decomposition, agent collaboration, simulation, multimodal, memory, and evaluation.",
            "Do not inject a large awesome-list into prompts; cite only the method category that explains the current writing choice.",
        ]

    def _build_novel_to_multimodal_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "novel_to_multimodal_pipeline" not in patterns:
            return []
        return [
            "When planning adaptation, split novel text into chapter summary, script scene, storyboard/shot list, asset manifest, and derived media output.",
            "Multimodal outputs are derived artifacts; they must not mutate novel canon unless an accepted script/scene change package says so.",
        ]

    def _build_entity_to_visual_asset_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "entity_to_visual_asset_pipeline" not in patterns:
            return []
        return [
            "Extract characters, locations, props, costumes, and scene mood into visual-asset refs before storyboard or image/video prompting.",
            "Reference images and visual prompts must cite the source entity/card version so later prose changes can invalidate stale assets.",
        ]

    def _build_agentic_book_planner_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "agentic_book_planner_pipeline" not in patterns:
            return []
        return [
            "Keep book-planning roles separate: Story Bible, Characters, Plot Threads, Chapter Outlines, Writer, Editor, and Continuity Checker.",
            "Writer output should cite the accepted planning artifacts it used, and Editor/Continuity findings should remain review records until accepted.",
        ]

    def _build_rag_synopsis_spine_hints(self, patterns: set[str]) -> list[str]:
        if "rag_synopsis_spine" not in patterns:
            return []
        return [
            "Maintain a full synopsis spine with chapter summaries and retrieve against that spine before pulling larger chapter text.",
            "Every RAG hit needs query, matched synopsis/chapter id, inclusion reason, and canon status before prompt injection.",
        ]

    def _build_anti_repetition_prompt_rules_hints(self, patterns: set[str]) -> list[str]:
        if "anti_repetition_prompt_rules" not in patterns:
            return []
        return [
            "Add anti-repetition rules to prompt and review: repeated phrase, repeated scene shape, repeated causal bridge, and repeated emotional beat.",
            "Use token/repetition stats as evidence for batch repair, not as a reason to flatten the prose voice.",
        ]

    def _build_prompt_recipe_experiment_grid_hints(self, patterns: set[str]) -> list[str]:
        if "prompt_recipe_experiment_grid" not in patterns:
            return []
        return [
            "Run prompt recipes as bounded experiments with fixed inputs, rubric review, and keep/discard decisions before promoting a recipe.",
            "Compare recipes by story quality, continuity risk, style fidelity, novelty, and copy-risk instead of by one sample's surface fluency.",
        ]

    def _build_append_only_generation_review_log_hints(self, patterns: set[str]) -> list[str]:
        if "append_only_generation_review_log" not in patterns:
            return []
        return [
            "Record generation experiments in an append-only log with recipe id, parameter set, output id, review score, and decision.",
            "Interrupted sweeps should resume by appending new rows, not by rewriting prior review evidence.",
        ]

    def _build_narrative_arc_template_control_hints(self, patterns: set[str]) -> list[str]:
        if "narrative_arc_template_control" not in patterns:
            return []
        return [
            "Select genre, story style, author-style target, narrative arc, and scenario blueprint before same-type drafting.",
            "Arc templates guide pressure and payoff timing; they must be transformed into new cast, setting, conflict, and event chain.",
        ]

    def _build_nrd_task_tree_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "nrd_task_tree_pipeline" not in patterns:
            return []
        return [
            "Represent long-form planning as an NRD task tree from arcs to chapters to scenes and revision passes.",
            "Each task node needs tag/status, accepted input artifacts, generated output, review finding, and continuity-report result.",
        ]

    def _build_sampling_parameter_quality_sweep_hints(self, patterns: set[str]) -> list[str]:
        if "sampling_parameter_quality_sweep" not in patterns:
            return []
        return [
            "Sweep sampling parameters only under fixed story inputs and a shared review rubric so quality changes are comparable.",
            "Promote parameter defaults only when they improve continuity, voice, pacing, and copy-risk together.",
        ]

    def _build_story_structure_rag_planning_hints(self, patterns: set[str]) -> list[str]:
        if "story_structure_rag_planning" not in patterns:
            return []
        return [
            "Use retrieved style/thematic samples plus Hero's Journey or Freytag beats as planning scaffolds before act/chapter drafting.",
            "Structure references are not canon; map each beat to accepted story facts before prose generation.",
        ]



    def _build_story_contract_commit_chain_hints(self, patterns: set[str]) -> list[str]:
        if "story_contract_commit_chain" not in patterns:
            return []
        return [
            "Treat story contracts as the single source of truth for serialized continuation; drafts become canon only through accepted chapter commits.",
            "Each chapter commit should record input contract version, accepted prose id, extracted facts, review status, and projection targets.",
        ]

    def _build_fact_snapshot_delta_gate_hints(self, patterns: set[str]) -> list[str]:
        if "fact_snapshot_delta_gate" not in patterns:
            return []
        return [
            "Before prose, assemble fact snapshots; after prose, emit typed change declarations and validate them through generation gates.",
            "Reject chapter state write-back when snapshot fields are missing, deltas conflict, or validation cannot explain the after-state.",
        ]

    def _build_projection_sync_observability_hints(self, patterns: set[str]) -> list[str]:
        if "projection_sync_observability" not in patterns:
            return []
        return [
            "Keep read models such as state, index, summaries, memory, vectors, and dashboard views derived from accepted commits.",
            "Projection logs should name which derived view synced, failed, or went stale so the next chapter does not read inconsistent state.",
        ]

    def _build_foreshadowing_debt_budget_hints(self, patterns: set[str]) -> list[str]:
        if "foreshadowing_debt_budget" not in patterns:
            return []
        return [
            "Score open foreshadowing as debt and reserve context budget for high-debt hooks before drafting related chapters.",
            "A payoff attempt must cite its setup, expected payoff window, current debt status, and whether the hook remains open or resolved.",
        ]

    def _build_reader_retention_review_gate_hints(self, patterns: set[str]) -> list[str]:
        if "reader_retention_review_gate" not in patterns:
            return []
        hints = [
            "Review each chapter for consistency, continuity, OOC, pleasure-point delivery, rhythm, and reader-retention hook before acceptance.",
            "Retention findings should become concrete revision tasks; do not accept a fluent chapter that has no pressure, payoff, or next-chapter pull.",
        ]
        if "beta_reader_archetype_panel" in patterns:
            hints.append("Fold beta-reader confusion and want-to-continue findings into retention revision tasks before acceptance.")
        if "local_reader_experience_editor" in patterns:
            hints.append("Treat micro-tension, curiosity, hook, and cliffhanger findings as reader-retention evidence, not optional polish.")
        return hints

    def _build_draft_stage_revision_ladder_hints(self, patterns: set[str]) -> list[str]:
        if "draft_stage_revision_ladder" not in patterns:
            return []
        return [
            "Use a staged ladder: chapter blueprint -> key-information file -> task card -> Draft A -> Draft B -> Draft C -> continuity handoff.",
            "Draft B preserves approved parts while applying directed changes; Draft C removes AI tone without changing canon or source-copy boundaries.",
        ]

    def _build_rolling_summary_context_trim_hints(self, patterns: set[str]) -> list[str]:
        if "rolling_summary_context_trim" not in patterns:
            return []
        return [
            "Maintain a rolling summary plus character states, timeline events, world state, and relevant passages for each chapter.",
            "When context is trimmed, record dropped items and keep enough evidence to explain why the selected context supports the next beat.",
        ]

    def _build_pairwise_story_comparison_ranking_hints(self, patterns: set[str]) -> list[str]:
        if "pairwise_story_comparison_ranking" not in patterns:
            return []
        return [
            "Compare matched chapter variants against the same brief before accepting a high-impact continuation or same-type draft.",
            "Use order-swapped pairwise notes to reduce position bias; keep the winning rationale as revision evidence, not canon.",
        ]

    def _build_multidimensional_quality_rubric_hints(self, patterns: set[str]) -> list[str]:
        if "multidimensional_quality_rubric" not in patterns:
            return []
        return [
            "Score drafts across grammar, clarity, causal connection, scene purpose, internal consistency, character consistency, dialogue, reader interest, and resolution.",
            "Rank the top weaknesses and convert them into targeted revision tasks instead of relying on a single overall score.",
        ]

    def _build_story_theory_beat_evaluation_hints(self, patterns: set[str]) -> list[str]:
        if "story_theory_beat_evaluation" not in patterns:
            return []
        return [
            "Evaluate whether the current beat performs its narrative function and preserves required context before moving to prose polish.",
            "For beat revision, separate diagnosis, flaw fix, beat satisfaction, preservation, and minimal-change criteria.",
        ]

    def _build_constraint_specificity_creativity_benchmark_hints(self, patterns: set[str]) -> list[str]:
        if "constraint_specificity_creativity_benchmark" not in patterns:
            return []
        return [
            "Track constraint specificity for each prompt so creativity is judged together with constraint satisfaction and coherence.",
            "Highly specific briefs should not push the draft into copied source events, checklist prose, or incoherent causal shortcuts.",
        ]

    def _build_style_axis_diversity_fingerprint_hints(self, patterns: set[str]) -> list[str]:
        if "style_axis_diversity_fingerprint" not in patterns:
            return []
        return [
            "Fingerprint style on visible axes: voice/diction, rhythm/syntax, POV/discourse, structure/pacing, tone, imagery, dialogue, experimentation, and closure.",
            "Use diversity evidence to avoid style collapse across chapters while preserving the target book's accepted voice boundaries.",
        ]

    def _build_event_outline_history_compression_hints(self, patterns: set[str]) -> list[str]:
        if "event_outline_history_compression" not in patterns:
            return []
        return [
            "Plan long stories as event outlines and chapter-wise event plans before writing the current chapter.",
            "Compress story history around the current event, keeping the omitted-history list available for continuity review.",
        ]

    def _build_agentic_story_world_simulation_hints(self, patterns: set[str]) -> list[str]:
        if "agentic_story_world_simulation" not in patterns:
            return []
        return [
            "Use multi-agent story-world simulation as a proposal generator for character behavior, social interaction, and world evolution.",
            "Simulated outcomes must be reviewed against canon and author direction before they become continuation facts.",
        ]

    def _build_reader_rating_signal_model_hints(self, patterns: set[str]) -> list[str]:
        if "reader_rating_signal_model" not in patterns:
            return []
        return [
            "Treat ratings, to-read markers, shelves, and tags as aggregate reader-expectation signals, not as creative truth or canon.",
            "Use shelf/tag clusters to infer promise, subgenre, mood, and audience expectation before same-type planning or chapter acceptance.",
            "Keep popularity calibration separate from prose quality so a niche-but-canon chapter is not rejected only for low market similarity.",
        ]

    def _build_review_spoiler_sentiment_corpus_hints(self, patterns: set[str]) -> list[str]:
        if "review_spoiler_sentiment_corpus" not in patterns:
            return []
        return [
            "Cluster review-like feedback into praise, complaint, trope request, comp suggestion, and spoiler-sensitive issue before turning it into revisions.",
            "Never paste verbatim review text into prompts or marketing copy; cite opaque ids and aggregate labels only.",
            "Separate spoiler risk from ordinary sentiment so late-book revelations are not spoiled inside early-chapter planning context.",
        ]

    def _build_beta_reader_archetype_panel_hints(self, patterns: set[str]) -> list[str]:
        if "beta_reader_archetype_panel" not in patterns:
            return []
        return [
            "Simulate distinct beta-reader archetypes: genre fan, casual reader, critical reader, and sensitivity reader; each reports hook, confusion, pull, and stop point.",
            "Record tension, pacing, want-to-continue percentage, favorite moment, stumble point, and emotions per chapter before accepting high-impact drafts.",
            "Use simulated beta readers as early warning only; final publication-facing claims still need real human judgment or author approval.",
        ]

    def _build_comp_title_market_positioning_hints(self, patterns: set[str]) -> list[str]:
        if "comp_title_market_positioning" not in patterns:
            return []
        return [
            "Build a comp-title matrix by genre, subgenre, tone, protagonist promise, market proof, freshness, and reader expectation gap.",
            "For same-type creation, transform comp signals into a new premise, cast, setting, conflict, and hook promise instead of copying comp plot routes.",
            "Marketing outputs such as blurbs, descriptions, keywords, and social copy are derived artifacts; they must not mutate story canon.",
        ]

    def _build_local_reader_experience_editor_hints(self, patterns: set[str]) -> list[str]:
        if "local_reader_experience_editor" not in patterns:
            return []
        return [
            "Run reader-experience edits at chapter and scene level: micro-tension, curiosity thread, hook, cliffhanger, opening, ending, paragraph rhythm, and clarity.",
            "Use series/book/chapter context scopes so broad context does not drown the current reader-experience question.",
            "Expose token/context breakdown and local analysis notes before expensive full-manuscript review passes.",
        ]

    def _build_delivery_manuscript_assembly_hints(self, patterns: set[str]) -> list[str]:
        if "delivery_manuscript_assembly" not in patterns:
            return []
        return [
            "Assemble final manuscripts only from accepted chapter artifacts, not from draft buffers, previews, or reviewer notes.",
            "Normalize chapter headings during assembly and verify chapter count, order, gaps, duplicates, and empty titles after merge.",
            "Write a delivery manifest with source range, generated range, accepted chapter count, output path, byte size, and SHA256.",
        ]

    def _build_export_format_fidelity_audit_hints(self, patterns: set[str]) -> list[str]:
        if "export_format_fidelity_audit" not in patterns:
            return []
        return [
            "Treat TXT, Markdown, DOCX, PDF, and EPUB exports as derived artifacts; canon remains the accepted bible, plan, and chapter commits.",
            "Verify each export preserves chapter order, headings, title page metadata, table of contents, page numbering, and paragraph boundaries.",
            "Do not let typography, font, spacing, or format conversion edits mutate story facts, chapter text, or continuity state.",
        ]

    def _build_preview_toc_packaging_hints(self, patterns: set[str]) -> list[str]:
        if "preview_toc_packaging" not in patterns:
            return []
        return [
            "Generate a preview and table-of-contents map from the same accepted chapter list used by final export.",
            "Use preview checks to catch broken headings, duplicate titles, navigation drift, markdown residue, and missing chapter names before delivery.",
        ]

    def _build_cover_kdp_metadata_boundary_hints(self, patterns: set[str]) -> list[str]:
        if "cover_kdp_metadata_boundary" not in patterns:
            return []
        return [
            "Keep cover prompts, KDP cover specs, blurbs, keywords, and launch copy as publication metadata; they must not write back into canon.",
            "Review cover and metadata for genre promise, title consistency, spoiler safety, and asset provenance before export packaging.",
        ]

    def _build_branching_choice_graph_hints(self, patterns: set[str]) -> list[str]:
        if "branching_choice_graph" not in patterns:
            return []
        return [
            "Model choices as explicit branch edges with source node, selected option, consequence scope, and merge/reject decision.",
            "Faithful continuation keeps optional branches outside main canon unless a branch edge is explicitly accepted.",
            "For same-type creation, rebuild branch pressure and option intent without copying source option text or branch order.",
        ]

    def _build_node_dialogue_state_machine_hints(self, patterns: set[str]) -> list[str]:
        if "node_dialogue_state_machine" not in patterns:
            return []
        return [
            "Represent dialogue as nodes with entry conditions, active speaker state, available options, command hooks, and exit state deltas.",
            "Continuation prompts should cite which dialogue node is active and which state changes are allowed before drafting dialogue.",
            "For same-type creation, remap conversation pressure and state transitions while replacing source lines, option labels, and command names.",
        ]

    def _build_passage_link_navigation_map_hints(self, patterns: set[str]) -> list[str]:
        if "passage_link_navigation_map" not in patterns:
            return []
        return [
            "Track passages as reachable nodes with visible links, hidden link conditions, dead-end checks, and intentional merge points.",
            "Before accepting a branching chapter, verify every promoted route has a reachable path and no accidental duplicate hidden route.",
            "For same-type creation, rebuild passage navigation from the new premise instead of preserving source passage order or link labels.",
        ]

    def _build_choice_stats_consequence_gate_hints(self, patterns: set[str]) -> list[str]:
        if "choice_stats_consequence_gate" not in patterns:
            return []
        return [
            "Every choice-stat mutation needs a visible immediate or delayed consequence, plus a ledger entry naming trigger, stat delta, and payoff window.",
            "Reject hidden variable drift: no branch may change canon, relationship, or world state without an explicit consequence record.",
            "For same-type creation, transform stat categories and consequence timing so source achievements, variables, and thresholds do not copy across.",
        ]

    def _build_source_text_fingerprint_gate_hints(self, patterns: set[str]) -> list[str]:
        if "source_text_fingerprint_gate" not in patterns:
            return []
        return [
            "Compare source and draft fingerprints before accepting same-type prose; high-overlap windows become review items, not automatic proof.",
            "Keep fingerprint thresholds separate for names, set-piece labels, long phrases, and structural scene order to reduce false positives.",
            "For continuation, fingerprint checks protect source fidelity boundaries; for same-type creation, they block copied route, wording, and scene topology.",
        ]

    def _build_fuzzy_phrase_similarity_gate_hints(self, patterns: set[str]) -> list[str]:
        if "fuzzy_phrase_similarity_gate" not in patterns:
            return []
        return [
            "Apply fuzzy phrase thresholds to catch paraphrased source sentences, renamed proper-noun strings, and near-duplicate dialogue turns.",
            "Review medium-similarity spans manually because genre terms, stock phrases, and required canon names can be legitimate matches.",
            "Same-type creation should lower similarity by changing sentence order, image clusters, objects, stakes, and causal wording.",
        ]

    def _build_diff_span_copy_review_hints(self, patterns: set[str]) -> list[str]:
        if "diff_span_copy_review" not in patterns:
            return []
        return [
            "Inspect diff spans between source exemplars and draft output; copied spans, sentence order, and semantic-cleanup matches require rewrite.",
            "Store span-level review notes with source ref, draft ref, match reason, decision, and rewrite action before accepting a risky chapter.",
            "Use diff review as a copy-risk gate only; it must not import source text or train prompts to imitate protected wording.",
        ]

    def _build_minhash_lsh_near_duplicate_gate_hints(self, patterns: set[str]) -> list[str]:
        if "minhash_lsh_near_duplicate_gate" not in patterns:
            return []
        return [
            "Use shingled MinHash/LSH-style checks to catch near-duplicate source windows before same-type drafts become accepted chapters.",
            "Review high-Jaccard clusters manually because genre formulas, required names, and boilerplate can be legitimate false positives.",
            "Record shingle size, threshold, and accepted/rewritten decisions so future prompt changes can be regression-tested.",
        ]

    def _build_simhash_hamming_similarity_gate_hints(self, patterns: set[str]) -> list[str]:
        if "simhash_hamming_similarity_gate" not in patterns:
            return []
        return [
            "Use SimHash/Hamming-style fingerprints for lightly edited or reordered passages that may evade exact fingerprint checks.",
            "Flag near-duplicate hash windows after entity renaming, translation, or copyedit polishing because those passes can preserve source topology.",
            "Keep Hamming thresholds separate for short dialogue, long prose windows, and outline beats to avoid over-blocking stock genre language.",
        ]

    def _build_semantic_duplicate_cluster_gate_hints(self, patterns: set[str]) -> list[str]:
        if "semantic_duplicate_cluster_gate" not in patterns:
            return []
        return [
            "Cluster source and draft windows by semantic similarity so paraphrased duplicate scenes are found even when wording changes.",
            "Treat same-cluster source neighbors as review evidence: rewrite concrete actor, object, obstacle, cost, and payoff until the draft stands alone.",
            "Store false-positive notes for shared tropes so semantic dedup does not reject genre resemblance by itself.",
        ]

    def _build_embedding_similarity_independence_gate_hints(self, patterns: set[str]) -> list[str]:
        if "embedding_similarity_independence_gate" not in patterns:
            return []
        return [
            "Run embedding-nearest-neighbor style checks against source excerpts and transformed canon before accepting same-type prose.",
            "A draft should be closest to its own transformed brief, accepted canon, or local outline, not to the source text or source author baseline.",
            "Use vector similarity as a triage signal with cited neighbors and thresholds; do not let opaque similarity scores silently rewrite prose.",
        ]

    def _build_corpus_leakage_dedup_review_gate_hints(self, patterns: set[str]) -> list[str]:
        if "corpus_leakage_dedup_review_gate" not in patterns:
            return []
        return [
            "Keep source corpora, deconstruction notes, transformed canon, and generated drafts in separate manifests so training-like leakage can be audited.",
            "Scan for repeated long sequences or chapter-route clusters that indicate the draft imported source material instead of transformed story state.",
            "Do not accept same-type output until leakage findings are resolved or explicitly marked as allowed continuation canon.",
        ]

    def _build_character_quote_attribution_map_hints(self, patterns: set[str]) -> list[str]:
        if "character_quote_attribution_map" not in patterns:
            return []
        return [
            "Build a character mention, alias, speaker, and quote-attribution map before judging voice consistency or relationship pressure.",
            "For continuation, verify new dialogue belongs to the current speaker state and does not swap aliases, titles, or pronouns across characters.",
            "For same-type creation, preserve only quote-distribution function and conflict pressure; rebuild speakers, aliases, and dialogue content.",
        ]

    def _build_readability_pacing_metric_gate_hints(self, patterns: set[str]) -> list[str]:
        if "readability_pacing_metric_gate" not in patterns:
            return []
        return [
            "Track readability, sentence length, paragraph length, and scene-density curves across source, draft, and accepted chapters.",
            "Use metric drift as a pacing review signal, not as a command to flatten prose into uniform easy text.",
            "For same-type creation, match broad reading rhythm while changing scene order, objects, stakes, and source wording.",
        ]

    def _build_prose_lint_style_rule_gate_hints(self, patterns: set[str]) -> list[str]:
        if "prose_lint_style_rule_gate" not in patterns:
            return []
        return [
            "Treat prose lint rules as project-local house style, not universal truth; every warning needs chapter, speaker, and scene context.",
            "Separate blocking violations from optional style nudges so lint output cannot flatten a deliberate narrator or character voice.",
            "For same-type creation, rebuild rule profiles around the new book's voice instead of copying the source style sheet.",
        ]

    def _build_grammar_spelling_copyedit_gate_hints(self, patterns: set[str]) -> list[str]:
        if "grammar_spelling_copyedit_gate" not in patterns:
            return []
        return [
            "Run grammar, spelling, and copyedit checks after canon/continuity review, because grammatical polish must not legitimize unsupported facts.",
            "Keep dialogue, dialect, invented terms, names, and genre vocabulary in an explicit exception policy before accepting grammar fixes.",
            "Prefer local/offline review surfaces unless a future runtime safety contract explicitly allows external grammar services.",
        ]

    def _build_copyedit_diagnostic_triage_queue_hints(self, patterns: set[str]) -> list[str]:
        if "copyedit_diagnostic_triage_queue" not in patterns:
            return []
        return [
            "Convert lint and grammar diagnostics into a triage queue with accept, ignore, rewrite, and needs-author-review states.",
            "Persist ignored diagnostics with reasons so repeated warnings do not hide new copyedit defects across chapters.",
            "Batch diagnostics by chapter and rule id before final manuscript assembly or same-type draft acceptance.",
        ]

    def _build_lexical_diversity_voice_audit_hints(self, patterns: set[str]) -> list[str]:
        if "lexical_diversity_voice_audit" not in patterns:
            return []
        return [
            "Measure lexical diversity and repeated-vocabulary drift by chapter, narrator, and major speaker before accepting style-sensitive drafts.",
            "Low diversity, sudden MTLD/HD-D jumps, or repeated word clusters should become targeted voice-review notes.",
            "Same-type creation may borrow diversity range but must replace source catchphrases, metaphor clusters, and signature diction.",
        ]

    def _build_stylometric_author_fingerprint_gate_hints(self, patterns: set[str]) -> list[str]:
        if "stylometric_author_fingerprint_gate" not in patterns:
            return []
        return [
            "Build an inspectable author/style fingerprint from stable metrics before using source style as guidance.",
            "Version each fingerprint with source scope, feature family, extraction settings, and human approval status.",
            "Same-type creation may borrow broad fingerprint targets but must not preserve source catchphrases, named imagery, or paragraph-level cadence.",
        ]

    def _build_function_word_syntax_style_gate_hints(self, patterns: set[str]) -> list[str]:
        if "function_word_syntax_style_gate" not in patterns:
            return []
        return [
            "Track function words, punctuation, sentence length, word length, readability, and syntax feature windows as style evidence.",
            "Treat feature outliers as review tasks instead of automatic rewrites, especially for dialogue, dialect, and deliberate register shifts.",
            "For same-type creation, transform feature ranges into a new house style and speaker-specific exceptions.",
        ]

    def _build_authorship_attribution_similarity_gate_hints(self, patterns: set[str]) -> list[str]:
        if "authorship_attribution_similarity_gate" not in patterns:
            return []
        return [
            "Use authorship-style similarity as a risk and calibration signal, not as a goal to maximize.",
            "Record source-vs-draft distance thresholds, false-positive notes, and reviewer decisions before accepting same-type prose.",
            "If the transformed draft becomes closer to the source author than to its own approved style baseline, route it to rewrite review.",
        ]

    def _build_style_overfit_regression_gate_hints(self, patterns: set[str]) -> list[str]:
        if "style_overfit_regression_gate" not in patterns:
            return []
        return [
            "Run windowed style-change checks across source, outline, draft, and revised prose to catch source-voice leakage.",
            "Regression cases should include paraphrased, renamed, and polished drafts because overfit often survives surface substitutions.",
            "Do not accept a draft that passes grammar/copyedit gates while failing style-overfit or source-distance gates.",
        ]

    def _build_paraphrase_independence_review_gate_hints(self, patterns: set[str]) -> list[str]:
        if "paraphrase_independence_review_gate" not in patterns:
            return []
        return [
            "Review same-type drafts for paraphrase independence after entity remap, style polish, and humanization passes.",
            "Separate allowed voice targets from blocked author-mimicry: no source-specific phrase families, scene order, or stylistic tics as required constraints.",
            "Humanization or style-transfer prompts must include copy-risk rejection, provenance, and author-visible accept/ignore decisions.",
        ]

    def _build_keyphrase_motif_extraction_hints(self, patterns: set[str]) -> list[str]:
        if "keyphrase_motif_extraction" not in patterns:
            return []
        return [
            "Extract keyphrases and motif keywords from source, outline, and draft to reveal topic drift, missing promises, and repeated thematic anchors.",
            "Continuation review should compare keyphrase salience against active arcs, foreshadows, and chapter goals before canon write-back.",
            "Same-type creation should transform motif functions into new objects, places, taboos, and stakes rather than reusing source keywords.",
        ]

    def _build_chinese_segmentation_keyword_gate_hints(self, patterns: set[str]) -> list[str]:
        if "chinese_segmentation_keyword_gate" not in patterns:
            return []
        return [
            "Use Chinese segmentation with a project dictionary before keyword, motif, and style analysis; names and invented terms must be dictionary entries.",
            "Record segmentation mode, custom terms, and keyword extraction method before comparing source, continuation, or same-type drafts.",
            "Do not let tokenizer output rewrite prose; it is evidence for review and context packing only.",
        ]

    def _build_chinese_ner_alias_consistency_gate_hints(self, patterns: set[str]) -> list[str]:
        if "chinese_ner_alias_consistency_gate" not in patterns:
            return []
        return [
            "Map Chinese names, aliases, locations, organizations, and titles into a review ledger before accepting chapter state updates.",
            "Flag entity merges/splits when a character alias, sect name, place name, or translated label changes across chapters.",
            "For same-type creation, source entity clusters are transformation evidence only and cannot become new-story canon names.",
        ]

    def _build_chinese_text_normalization_gate_hints(self, patterns: set[str]) -> list[str]:
        if "chinese_text_normalization_gate" not in patterns:
            return []
        return [
            "Declare Simplified/Traditional, punctuation-width, numeral, and variant-character policy before source deconstruction or final export.",
            "Normalize for comparison and retrieval, but keep the author-approved manuscript surface unchanged unless a change is accepted.",
            "Store normalization differences as review findings so same-type drafts do not inherit source-specific orthography by accident.",
        ]

    def _build_chinese_error_correction_review_gate_hints(self, patterns: set[str]) -> list[str]:
        if "chinese_error_correction_review_gate" not in patterns:
            return []
        return [
            "Treat Chinese typo/correction suggestions as review queue items with accept, ignore, or author-review status.",
            "Protect character names, invented terms, dialect, honorifics, and genre vocabulary with explicit correction exceptions.",
            "Run correction review after canon checks so a fluent correction cannot hide a continuity or source-copy problem.",
        ]

    def _build_source_format_import_manifest_hints(self, patterns: set[str]) -> list[str]:
        if "source_format_import_manifest" not in patterns:
            return []
        return [
            "Record source format, metadata, TOC, spine/order, detected chapter ids, and skipped sections before source deconstruction.",
            "Treat EPUB/PDF/DOCX/conversion output as imported evidence, not canon, until chapters are reviewed and accepted.",
            "For same-type creation, never reuse source TOC/spine order as the new outline without a transformation step.",
        ]

    def _build_pdf_layout_text_extraction_gate_hints(self, patterns: set[str]) -> list[str]:
        if "pdf_layout_text_extraction_gate" not in patterns:
            return []
        return [
            "Store page number, text span, block order, coordinates when available, and extraction gaps for every PDF-derived chapter segment.",
            "Flag headers, footers, page numbers, footnotes, two-column order, and missing text before summaries or style analysis use PDF text.",
            "Do not accept PDF extraction as faithful source text without a reading-order and gap review.",
        ]

    def _build_ocr_scanned_page_import_gate_hints(self, patterns: set[str]) -> list[str]:
        if "ocr_scanned_page_import_gate" not in patterns:
            return []
        return [
            "For scanned pages, record OCR engine/language, confidence, page image range, and low-confidence spans before deconstruction.",
            "Route low-confidence OCR text to manual review instead of feeding it directly into canon, glossary, or style extraction.",
            "OCR is a deferred runtime lane; source intake may record the gate but must not launch OCR binaries or download language data.",
        ]

    def _build_document_partition_chapter_detection_gate_hints(self, patterns: set[str]) -> list[str]:
        if "document_partition_chapter_detection_gate" not in patterns:
            return []
        return [
            "Partition imported documents into typed elements before chapter detection: title, narrative text, list, table, image, note, and footer.",
            "Detect chapter headings with evidence: element type, normalized heading text, page/span, TOC match, and neighboring section boundaries.",
            "Keep uncertain headings as review candidates so bad partitioning cannot corrupt chapter order or source summaries.",
        ]

    def _build_import_provenance_checksum_gate_hints(self, patterns: set[str]) -> list[str]:
        if "import_provenance_checksum_gate" not in patterns:
            return []
        return [
            "Attach checksum, file size, source path, parser/version, settings, and import timestamp to every source-text extraction artifact.",
            "When a parser or setting changes, invalidate derived summaries, glossary entries, and style fingerprints until re-reviewed.",
            "Keep original, extracted, normalized, and accepted text as separate artifacts with explicit lineage.",
        ]

    def _build_epub_structure_validation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "epub_structure_validation_gate" not in patterns:
            return []
        return [
            "Before final EPUB delivery, validate container, package document, OPF manifest, spine, nav document, media types, and validation errors as one report.",
            "Treat EPUB validation as a packaging gate over accepted chapters; it must not mutate canon text or silently reorder chapter content.",
            "For same-type creation, EPUB structure may inspire a delivery checklist, but source TOC, spine, and metadata order must be rebuilt for the new manuscript.",
        ]

    def _build_ebook_accessibility_audit_gate_hints(self, patterns: set[str]) -> list[str]:
        if "ebook_accessibility_audit_gate" not in patterns:
            return []
        return [
            "Audit ebook accessibility metadata, landmarks, heading levels, reading order, alt text, language declarations, and hazard notes before publication export.",
            "Accessibility findings become author-review tasks; do not auto-rewrite prose or inject external checker output into story canon.",
            "For same-type creation, keep accessibility and reader-navigation standards while changing source-specific illustrations, captions, and front/back matter text.",
        ]

    def _build_front_back_matter_metadata_gate_hints(self, patterns: set[str]) -> list[str]:
        if "front_back_matter_metadata_gate" not in patterns:
            return []
        return [
            "Keep title page, copyright, dedication, foreword, endnotes, afterword, colophon, identifiers, and publication metadata in a separate delivery manifest.",
            "Front/back matter can reference accepted canon and attribution policy, but must not become hidden prompt context for chapter continuation.",
            "For same-type creation, regenerate title, subtitle, blurb-adjacent metadata, and colophon from the transformed book rather than source packaging.",
        ]

    def _build_toc_navigation_consistency_gate_hints(self, patterns: set[str]) -> list[str]:
        if "toc_navigation_consistency_gate" not in patterns:
            return []
        return [
            "Compare visible chapter headings, nav TOC, NCX when present, spine order, landmarks, and preview navigation before accepting an ebook export.",
            "Flag missing, duplicate, empty, or reordered navigation entries separately from prose-quality findings.",
            "For same-type creation, rebuild navigation from the transformed outline so source chapter titles or section hierarchy cannot leak into delivery.",
        ]

    def _build_agentic_editorial_pipeline_gate_hints(self, patterns: set[str]) -> list[str]:
        if "agentic_editorial_pipeline_gate" not in patterns:
            return []
        return [
            "Treat planner, architect, writer, reviewer, copy-editor, and compiler roles as separate review stages with explicit handoff artifacts.",
            "The human author remains the creative authority; automated roles may propose changes, but accepted canon changes require an author/reviewer decision boundary.",
            "For same-type creation, rebuild the role pipeline around the transformed premise rather than replaying source analysis outputs as draft instructions.",
        ]

    def _build_chapter_state_archive_ladder_hints(self, patterns: set[str]) -> list[str]:
        if "chapter_state_archive_ladder" not in patterns:
            return []
        return [
            "Keep permanent bible files separate from transient per-chapter state; archive the state snapshot after each accepted chapter.",
            "A current-state pointer can speed prompting, but it must be reproducible from the chapter archive and must not overwrite historical states.",
            "For same-type creation, create a fresh state ladder for the new story; source chapter state can inform structure only after entity and plot remap.",
        ]

    def _build_section_metadata_traceability_gate_hints(self, patterns: set[str]) -> list[str]:
        if "section_metadata_traceability_gate" not in patterns:
            return []
        return [
            "Attach section/chapter metadata for cast, locations, items, plotlines, beats, pacing, status, and source evidence before generation or review.",
            "Flag sections whose metadata lacks a matching accepted chapter, timeline event, or character/location/item reference.",
            "For same-type creation, remap section metadata into new cast, places, objects, and plotline ids before drafting prose.",
        ]

    def _build_ai_prose_fingerprint_cluster_gate_hints(self, patterns: set[str]) -> list[str]:
        if "ai_prose_fingerprint_cluster_gate" not in patterns:
            return []
        return [
            "Scan accepted and candidate chapters for repeated AI-prose fingerprints, severity clusters, voice drift, hedging, overused punctuation, and show-then-tell patterns.",
            "Fingerprint findings become targeted revision tasks with accepted/ignored exceptions; they must not auto-rewrite author voice or invented terms.",
            "For same-type creation, reduce machine-prose fingerprints while preserving independence from source phrasing and source cadence.",
        ]

    def _build_author_candidate_canon_confirmation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "author_candidate_canon_confirmation_gate" not in patterns:
            return []
        return [
            "Treat AI suggestions, candidate outlines, scene cards, and style alternatives as non-canon until previewed, confirmed, and applied by the author/reviewer boundary.",
            "Persist candidate id, source, confirmation status, decision reason, and rollback path so unconfirmed ideas cannot silently enter bible, plan, or chapter prompts.",
            "For same-type creation, source-derived candidates remain craft options only; accepted transformed canon must have new names, stakes, and evidence.",
        ]

    def _build_progressive_spoiler_context_window_gate_hints(self, patterns: set[str]) -> list[str]:
        if "progressive_spoiler_context_window_gate" not in patterns:
            return []
        return [
            "Select outline, RAG, and previous-chapter context by the current story stage; early chapters should not see late spoilers, ending facts, or future payoff wording.",
            "Record the allowed chapter range, spoiler level, future-context count, and range-validation findings for each generated chapter.",
            "For same-type creation, stage windows should protect the transformed story from copying the source chapter order, reveal timing, or ending route.",
        ]

    def _build_chapter_control_card_writeback_gate_hints(self, patterns: set[str]) -> list[str]:
        if "chapter_control_card_writeback_gate" not in patterns:
            return []
        return [
            "Before drafting, create a chapter control card that states what must change, which line advances, which debt returns, the conflict, title intent, and ending hook.",
            "After acceptance, write back event, character, relationship, plotline, foreshadow, world-rule, emotional-debt, and next-chapter pressure deltas.",
            "For same-type creation, rebuild chapter cards from transformed goals and hooks; source control cards cannot become new-story tasks.",
        ]

    def _build_trace_replay_revision_workspace_gate_hints(self, patterns: set[str]) -> list[str]:
        if "trace_replay_revision_workspace_gate" not in patterns:
            return []
        return [
            "Keep chapter workbench decisions traceable: selected context, blueprint, conflict warnings, rewrite direction, reviewer findings, and final accepted text version.",
            "When redoing a chapter after later chapters exist, record impact scope and require downstream consistency review before canon write-back.",
            "For same-type creation, trace replay may explain craft choices but source traces must not be replayed as transformed-story decisions.",
        ]

    def _build_relationship_graph_global_replace_gate_hints(self, patterns: set[str]) -> list[str]:
        if "relationship_graph_global_replace_gate" not in patterns:
            return []
        return [
            "Track character relationship graphs as derived review surfaces tied to current setting, outline, and accepted chapters; regenerate after upstream edits.",
            "Global find/replace must preview every affected bible, outline, chapter, vector-memory, and graph entry, then run consistency checks before acceptance.",
            "For same-type creation, relationship graphs and replacement maps must use transformed ids so renamed source entities do not leak back through edges or aliases.",
        ]

    def _build_bookrun_audit_trail_gate_hints(self, patterns: set[str]) -> list[str]:
        if "bookrun_audit_trail_gate" not in patterns:
            return []
        return [
            "Treat each long-form generation run as a BookRun-style audit unit with blueprint, chapter plan, judge findings, repair attempts, accepted output, and export manifest.",
            "A Judge/Repair pass can only mark a chapter accepted when the failure list, repair diff, retry count, and final validation status are recorded.",
            "For same-type creation, BookRun traces prove process quality only; source run decisions must not become transformed-story canon or chapter order.",
        ]

    def _build_provider_budget_smoke_gate_hints(self, patterns: set[str]) -> list[str]:
        if "provider_budget_smoke_gate" not in patterns:
            return []
        return [
            "Separate provider/runtime admission from prompt planning: record provider profile, token/time/cost budget, smoke-scope, and no-provider dry-run status before any real generation.",
            "Real LLM smoke gates should be tiny, explicit, and reversible; failing smoke evidence blocks unattended long-run generation.",
            "For same-type creation, provider budgets constrain experiments only and never justify copying source prose to reduce retries.",
        ]

    def _build_sidecar_memory_profile_boundary_hints(self, patterns: set[str]) -> list[str]:
        if "sidecar_memory_profile_boundary" not in patterns:
            return []
        return [
            "Keep UI/API orchestration, sidecar analysis, graph memory, vector memory, queues, and provider routing as separate profiles with explicit runtime exclusions.",
            "A graph/vector sidecar profile must declare what it may read, write, cache, index, and forget before its outputs can enter continuation context.",
            "For same-type creation, source sidecar memory remains analysis evidence; transformed canon must use a new profile, namespace, and retrieval boundary.",
        ]

    def _build_outline_checkpoint_milestone_gate_hints(self, patterns: set[str]) -> list[str]:
        if "outline_checkpoint_milestone_gate" not in patterns:
            return []
        return [
            "Anchor layered outlines to checkpoints and narrative milestones so chapter drafting cannot skip unresolved setup, relationship pressure, or Story Bible constraints.",
            "Before each chapter batch, verify milestone coverage, chapter sequence, accepted-bible version, and checkpoint rollback target.",
            "For same-type creation, rebuild milestones from the transformed promise and conflict; do not reuse the source milestone order.",
        ]

    def _build_language_localization_style_profile_gate_hints(self, patterns: set[str]) -> list[str]:
        if "language_localization_style_profile_gate" not in patterns:
            return []
        return [
            "Attach a language/localization style profile to the bible: units, address terms, punctuation, honorifics, dialect limits, glossary, and forbidden cross-language artifacts.",
            "Localized style rules are review gates, not prose to copy; every exception should be logged with language, scene, speaker, and reason.",
            "For same-type creation, rebuild localized voice and glossary for the new setting so source language habits do not leak as renamed texture.",
        ]

    def _build_progressive_disclosure_skill_protocol_gate_hints(self, patterns: set[str]) -> list[str]:
        if "progressive_disclosure_skill_protocol_gate" not in patterns:
            return []
        return [
            "Use a light entry protocol that routes to only the needed planning, drafting, review, archive, or dashboard procedure for the current request.",
            "Every protocol load should bind required knowledge-base files, validate missing references, and emit the next command or stop reason.",
            "For same-type creation, protocol routing governs workflow only; external skill prompts and codex files are not copied into the new book.",
        ]

    def _build_anti_slop_rulepack_triage_gate_hints(self, patterns: set[str]) -> list[str]:
        if "anti_slop_rulepack_triage_gate" not in patterns:
            return []
        return [
            "Run AI-prose rulepack triage separately from copy-risk review: banned vocabulary, inflated copulas, vague attribution, marketing cadence, and repeated structure become revision tasks.",
            "Each prose-lint finding needs accept/ignore/rewrite status so cleanup does not flatten character voice or genre texture.",
            "For same-type creation, anti-slop cleanup must increase local specificity without paraphrasing source sentences or restoring source cadence.",
        ]

    def _build_user_modifier_project_blueprint_gate_hints(self, patterns: set[str]) -> list[str]:
        if "user_modifier_project_blueprint_gate" not in patterns:
            return []
        return [
            "Capture project modifiers before planning: genre, target length, chapter word count, POV, tone, themes, setting, pacing, prose complexity, and character count.",
            "Initial plans, chapter plans, prose, review, revision, timing logs, and project-state export should share one blueprint id so dashboard evidence is replayable.",
            "For same-type creation, modifiers are a transformed design surface; source modifiers and example outputs cannot become copied plot, cast, or prose.",
        ]

    def _build_portable_canon_skill_runtime_gate_hints(self, patterns: set[str]) -> list[str]:
        if "portable_canon_skill_runtime_gate" not in patterns:
            return []
        return [
            "Separate story assets, canon JSON/frontmatter, skill rules, workflow state, artifact index, and exports so each layer can be audited and resumed.",
            "Canon-sync must record source asset, accepted delta, SQLite/checkpoint id, artifact path, and reviewer result before generated changes become stable context.",
            "For same-type creation, portable skills and canon layers govern process only; transformed canon needs new ids, frontmatter, and runtime state.",
        ]

    def _build_staged_outline_chunk_window_gate_hints(self, patterns: set[str]) -> list[str]:
        if "staged_outline_chunk_window_gate" not in patterns:
            return []
        return [
            "For long outlines, generate and review setup plus chapter/part chunks instead of asking one prompt to hold the entire book.",
            "Drafting context should keep current and adjacent plot chunks detailed while distant chapters stay compressed to title, summary, and constraints.",
            "Chapter-range refinement must state start/end chapter, adjacent context window, CJK/token budget, resume point, and exact improvement targets.",
        ]

    def _build_wiki_canon_graph_lint_gate_hints(self, patterns: set[str]) -> list[str]:
        if "wiki_canon_graph_lint_gate" not in patterns:
            return []
        return [
            "Maintain a story-bible wiki with health, ingest, lint, query, and relationship-graph checks before adding new continuity-sensitive material.",
            "Canon lint should surface timeline contradictions, character state mismatches, disconnected lore clusters, unresolved setup/payoff, and graph quality gaps.",
            "For same-type creation, wiki pages and relationship graphs must be rebuilt from transformed facts rather than copied source pages.",
        ]

    def _build_plan_draft_log_verify_loop_gate_hints(self, patterns: set[str]) -> list[str]:
        if "plan_draft_log_verify_loop_gate" not in patterns:
            return []
        return [
            "Use a Plan -> Draft -> Log -> Verify loop for every chapter so scene logs, continuity records, glossary, threads, and foreshadowing debt stay current.",
            "Session wrap must verify living documents are updated, preview next work, and leave an explicit stop/resume state.",
            "For same-type creation, the loop verifies the transformed manuscript; source plan/log cadence is not a template to preserve.",
        ]

    def _build_mcp_scene_index_revision_boundary_hints(self, patterns: set[str]) -> list[str]:
        if "mcp_scene_index_revision_boundary" not in patterns:
            return []
        return [
            "Build metadata-first scene indexes before prose edits: scenes, beats, loglines, characters, places, threads, and relationship metadata are query targets.",
            "Safe scene revision needs selected scene ids, requested edit scope, human confirmation, reversible diff, git/history evidence, and review bundle output.",
            "For same-type creation, source scene indexes are analysis-only; transformed drafts require their own scene ids and revision ledger.",
        ]

    def _build_verbalized_sampling_diversity_wiki_gate_hints(self, patterns: set[str]) -> list[str]:
        if "verbalized_sampling_diversity_wiki_gate" not in patterns:
            return []
        return [
            "Use diversity sampling as an ideation/review gate: request multiple probability-scored alternatives, then choose or merge with recorded reasons.",
            "Auto-file brainstorms, outlines, sketches, drafts, critique, characters, and settings into the project wiki so promising variants stay recoverable.",
            "For same-type creation, diversity sampling should push away from source mode collapse; reject variants that cluster around source scenes or names.",
        ]

    def _build_literary_event_entity_annotation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "literary_event_entity_annotation_gate" not in patterns:
            return []
        return [
            "Separate source-book literary entities, events, participant roles, and mention spans before turning them into canon cards or summaries.",
            "Treat event/entity annotations as review evidence; unresolved event labels or participant slots stay out of continuation context.",
            "For same-type creation, remap roles and event functions before any source annotation can influence the new outline.",
        ]

    def _build_narrative_event_evolution_graph_gate_hints(self, patterns: set[str]) -> list[str]:
        if "narrative_event_evolution_graph_gate" not in patterns:
            return []
        return [
            "Build event-chain graphs with explicit temporal, causal, discourse, blocker, and payoff edges before deconstruction conclusions.",
            "Do not treat next-event predictions or script-like event chains as canon unless a reviewer accepts the event dependency.",
            "For same-type creation, change causal edges and event order instead of preserving source narrative evolution under renamed actors.",
        ]

    def _build_sentiment_arc_emotion_trajectory_gate_hints(self, patterns: set[str]) -> list[str]:
        if "sentiment_arc_emotion_trajectory_gate" not in patterns:
            return []
        return [
            "Track global sentiment arcs and character-specific emotion trajectories with chapter/scene anchors and turning-point reasons.",
            "Use sentiment and emotion curves as review signals, not automatic quality scores, because model/lexicon disagreement needs triage.",
            "For same-type creation, rebuild triggers and payoffs so the new book does not clone the source emotional curve.",
        ]

    def _build_cross_context_coreference_gate_hints(self, patterns: set[str]) -> list[str]:
        if "cross_context_coreference_gate" not in patterns:
            return []
        return [
            "Maintain cross-chapter and cross-document mention clusters for people, places, events, and abstract concepts before context reuse.",
            "Flag ambiguous or drifting clusters instead of writing them back into canon, especially across imported source and generated chapters.",
            "For same-type creation, regenerate aliases and cluster boundaries around the transformed cast and event set.",
        ]

    def _build_character_interaction_network_gate_hints(self, patterns: set[str]) -> list[str]:
        if "character_interaction_network_gate" not in patterns:
            return []
        return [
            "Extract character interaction networks with evidence for co-occurrence, dialogue, sentiment/polarity, faction, and time window.",
            "Review centrality, bridge characters, alliance/conflict polarity, and relationship timing before accepting relationship canon.",
            "For same-type creation, alter graph topology and relationship timing so renamed characters do not preserve the source network.",
        ]

    def _build_semantic_chunk_boundary_map_hints(self, patterns: set[str]) -> list[str]:
        if "semantic_chunk_boundary_map" not in patterns:
            return []
        return [
            "Split source and generated chapters at semantic boundaries before context packing, retrieval, or summary compression.",
            "Each chunk needs source chapter id, boundary reason, overlap policy, token/character size, and inclusion purpose.",
            "For same-type creation, remap chunk order and boundary function instead of preserving the source chapter segmentation route.",
        ]

    def _build_chapter_summary_anchor_gate_hints(self, patterns: set[str]) -> list[str]:
        if "chapter_summary_anchor_gate" not in patterns:
            return []
        return [
            "Anchor summaries to accepted chapter ids, representative sentences, source refs, and canon status before using them as prompt context.",
            "Reject summaries that hide unresolved hooks, merge separate events, or promote draft-only facts into continuation state.",
            "For same-type creation, rebuild summary anchors around transformed events so source chapter-summary order cannot leak in.",
        ]

    def _build_topic_drift_map_hints(self, patterns: set[str]) -> list[str]:
        if "topic_drift_map" not in patterns:
            return []
        return [
            "Map topic clusters across chapters and compare drift against active arcs, promises, motifs, and chapter goals before acceptance.",
            "Topic drift is a review signal: distinguish intentional subplot shift from accidental off-arc wandering or source-topic copying.",
            "For same-type creation, transform topic sequence and salience so the new story does not follow the source's topic timeline.",
        ]

    def _build_context_faithfulness_eval_gate_hints(self, patterns: set[str]) -> list[str]:
        if "context_faithfulness_eval_gate" not in patterns:
            return []
        return [
            "Evaluate whether generated facts are supported by accepted chapter memory, bible state, retrieved context, and summary anchors before canon write-back.",
            "Track faithfulness, groundedness, context precision, and context recall as review evidence; low scores create fix tasks, not automatic acceptance or rejection.",
            "For same-type creation, measure grounding against transformed-story canon only so source inspiration cannot masquerade as faithful context.",
        ]

    def _build_retrieval_trace_observability_gate_hints(self, patterns: set[str]) -> list[str]:
        if "retrieval_trace_observability_gate" not in patterns:
            return []
        return [
            "Store retrieval traces with query, selected chunks, omitted candidates, context relevance reason, and generation span that used each item.",
            "Trace review should explain why each context item entered the prompt and which important candidates were omitted.",
            "For same-type creation, separate source-analysis traces from transformed-canon traces so reviewer can detect accidental source-canon mixing.",
        ]

    def _build_prompt_regression_eval_suite_hints(self, patterns: set[str]) -> list[str]:
        if "prompt_regression_eval_suite" not in patterns:
            return []
        return [
            "Keep golden continuation and same-type cases for prompt changes: input state, expected guardrail findings, accepted outputs, and failure diffs.",
            "Run prompt regression checks before accepting prompt-pack changes that affect context selection, copy-risk gates, or canon write-back.",
            "Regression cases should include adversarial source-like inputs to prove the prompt rejects copied route, wording, and source-canon leakage.",
        ]

    def _build_agentwrite_plan_write_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "agentwrite_plan_write_pipeline" not in patterns:
            return []
        return [
            "Split ultra-long generation into a planning artifact and a writing artifact; validate the plan before prose expansion starts.",
            "Each write stage should cite the plan segment, target section length, accepted context, and post-write change package.",
            "For same-type creation, transform the plan-write stage boundaries so the new book does not follow the source outline order.",
        ]

    def _build_long_output_length_quality_ruler_hints(self, patterns: set[str]) -> list[str]:
        if "long_output_length_quality_ruler" not in patterns:
            return []
        return [
            "Track long-output quality and output length together; a chapter or batch is not acceptable when it hits word count but loses coherence, canon, or style.",
            "Use length stress tests for long continuation batches: target range, actual length, truncation risk, repeated-section risk, and ending pressure.",
            "For same-type creation, length targets must serve the transformed outline, not force source chapter pacing or section boundaries.",
        ]

    def _build_long_context_reward_dimension_gate_hints(self, patterns: set[str]) -> list[str]:
        if "long_context_reward_dimension_gate" not in patterns:
            return []
        return [
            "Evaluate long-context outputs on separate dimensions: helpfulness to the current writing goal, logicality, faithfulness, and completeness.",
            "Low reward dimensions become named fix tasks; do not average away a faithfulness or logicality failure in a long chapter.",
            "For same-type creation, completeness means all transformed-story requirements are covered without importing source-only facts.",
        ]

    def _build_instance_specific_writing_criteria_gate_hints(self, patterns: set[str]) -> list[str]:
        if "instance_specific_writing_criteria_gate" not in patterns:
            return []
        return [
            "Attach local acceptance criteria to every continuation or same-type writing task instead of relying on one global prose-quality score.",
            "Criteria should be instance-specific: canon facts, requested beat, style target, length/format, and reader promise for this chapter.",
            "Treat requirement-dimension failures as blocking fix tasks even when the prose is fluent or long enough.",
        ]

    def _build_material_grounded_query_refinement_hints(self, patterns: set[str]) -> list[str]:
        if "material_grounded_query_refinement" not in patterns:
            return []
        return [
            "Before drafting, separate required materials from optional or noisy reference notes; prune irrelevant evidence from the context pack.",
            "When a user request is ambiguous or unrealistic, rewrite the local task brief before generation rather than repairing only after failure.",
            "For same-type creation, keep material requirements as abstract constraints and rebuild concrete people, places, objects, and facts.",
        ]

    def _build_hybrid_rubric_pairwise_elo_judge_hints(self, patterns: set[str]) -> list[str]:
        if "hybrid_rubric_pairwise_elo_judge" not in patterns:
            return []
        return [
            "Use rubric scores first, then compare close candidate drafts pairwise; pairwise wins should explain margin, not just choose a favorite.",
            "Keep pairwise comparisons against neighboring drafts or variants so the judge discriminates real chapter improvements.",
            "Do not promote a draft from pairwise ranking alone when the local rubric shows canon, logic, or style failure.",
        ]

    def _build_judge_bias_mitigation_check_hints(self, patterns: set[str]) -> list[str]:
        if "judge_bias_mitigation_check" not in patterns:
            return []
        return [
            "Audit judge decisions for length, position/order, verbosity, and ornate-but-incoherent prose bias before accepting a winning draft.",
            "Swap draft order in pairwise review and require concrete evidence for wins on plot, character, style, and continuity.",
            "Reject evaluations that reward padding or poetic vagueness over usable continuation canon.",
        ]

    def _build_plan_reflect_character_chapter_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "plan_reflect_character_chapter_pipeline" not in patterns:
            return []
        return [
            "Treat longform drafting as a chain: brainstorm, plan, critique the plan, update character profiles, then write chapter sequence.",
            "Persist reflection and character-profile changes before chapter generation so later chapters do not invent incompatible motivations.",
            "For same-type creation, rebuild the plan-reflection-character trace around the new premise rather than preserving the source sequence.",
        ]

    def _build_human_story_metric_panel_hints(self, patterns: set[str]) -> list[str]:
        if "human_story_metric_panel" not in patterns:
            return []
        return [
            "Score reader-facing story quality on separate axes: relevance, coherence, empathy, surprise, engagement, and complexity.",
            "Turn low reader-axis scores into named repairs, such as empathy gap, surprise collapse, engagement drop, or complexity overload.",
            "For continuation, relevance is local to accepted canon and current chapter intent; for same-type creation, relevance is local to transformed-story promises.",
        ]

    def _build_hierarchical_cowriting_story_scaffold_hints(self, patterns: set[str]) -> list[str]:
        if "hierarchical_cowriting_story_scaffold" not in patterns:
            return []
        return [
            "Keep logline, character, plot-point, location, and dialogue layers separate; validate upper layers before expanding lower layers.",
            "Use the scaffold as author-editable material for compilation, editing, and rewriting, not as autonomous final prose.",
            "For same-type creation, rebuild every layer around the new premise before drafting dialogue or chapter scenes.",
        ]

    def _build_human_coauthor_edit_boundary_hints(self, patterns: set[str]) -> list[str]:
        if "human_coauthor_edit_boundary" not in patterns:
            return []
        return [
            "Mark AI output as co-writing material that requires human or review-gate compilation, editing, and rewriting before acceptance.",
            "Check plagiarism, toxicity/offense risk, stereotype drift, and formulaic scene output before writing accepted canon.",
            "For same-type creation, do not treat source-like inspiration as permission to keep recognizable names, set pieces, or dialogue.",
        ]

    def _build_recursive_reprompt_revision_loop_hints(self, patterns: set[str]) -> list[str]:
        if "recursive_reprompt_revision_loop" not in patterns:
            return []
        return [
            "Run long chapters as explicit stages: plan, draft, rewrite candidates, edit against state, then accept only the verified result.",
            "Save and reload outline checkpoints so an interrupted continuation resumes from a known plan rather than regenerating hidden context.",
            "Use dynamic continuation thresholds to decide when to move to the next outline item instead of forcing fixed-length padding.",
        ]

    def _build_reranker_guided_candidate_selection_hints(self, patterns: set[str]) -> list[str]:
        if "reranker_guided_candidate_selection" not in patterns:
            return []
        return [
            "Generate multiple candidate passages only when review budget allows; score them for relevance to plan and coherence with accepted context.",
            "Keep candidate-selection logs with rejected reasons, not just the winning prose.",
            "Do not let reranking optimize local fluency while losing canon, character motive, or source-copy safety.",
        ]

    def _build_character_dialogue_persona_memory_hints(self, patterns: set[str]) -> list[str]:
        if "character_dialogue_persona_memory" not in patterns:
            return []
        return [
            "Store character voice as evidence-backed tone, personality, relationship pressure, and plot-chat boundaries.",
            "Use dialogue evidence to preserve voice and role behavior without copying source lines or protected role IP.",
            "For same-type creation, transform persona memory into new characters with distinct names, facts, relationships, and verbal signatures.",
        ]

    def _build_event_to_sentence_realization_trace_hints(self, patterns: set[str]) -> list[str]:
        if "event_to_sentence_realization_trace" not in patterns:
            return []
        return [
            "Represent chapter prose expansion as event-to-sentence trace: plot event, chosen realization, confidence, and rejected alternatives.",
            "Use realization confidence to find thin or over-literal sentences that need scene-level rewrite.",
            "For same-type creation, transform plot events before realization so sentence expansion cannot preserve source event order.",
        ]

    def _build_entity_memory_slotfill_grounding_hints(self, patterns: set[str]) -> list[str]:
        if "entity_memory_slotfill_grounding" not in patterns:
            return []
        return [
            "Ground slot filling against entity memory so names, roles, locations, and objects stay consistent across realized events.",
            "Track entity substitutions explicitly when a chapter changes speaker, target, location, or carried object.",
            "Reject realized prose when slot filling imports source entities or leaves unresolved aliases.",
        ]

    def _build_book_memory_bank_context_lattice_hints(self, patterns: set[str]) -> list[str]:
        if "book_memory_bank_context_lattice" not in patterns:
            return []
        return [
            "Treat source deconstruction, story structure, world/characters, style guide, active context, and progress as separate but linked memory-bank files.",
            "Before continuation, read the current active context and progress snapshot; after accepted chapter output, update every affected memory-bank layer.",
            "Compare each completed chapter against its planned outline so drift becomes an explicit decision instead of hidden context loss.",
        ]

    def _build_spec_driven_fiction_scene_tasks_hints(self, patterns: set[str]) -> list[str]:
        if "spec_driven_fiction_scene_tasks" not in patterns:
            return []
        return [
            "Use the fiction constitution/story bible as the governing authority for voice, tense, prose profile, audience, language, and hard style rules.",
            "Translate the book plan into scene-by-scene tasks with status, POV, information asymmetry, causal beats, and quality gates before drafting.",
            "Run glossary, subplot, pacing, continuity, and sensitivity-style gates as read-only checks before accepting a chapter or same-type draft.",
        ]

    def _build_toc_aware_source_deconstruction_hints(self, patterns: set[str]) -> list[str]:
        if "toc_aware_source_deconstruction" not in patterns:
            return []
        return [
            "When deconstructing a source book, preserve table-of-contents hierarchy so parts, chapters, and sections remain traceable.",
            "Carry parent-section introductions into the first child summary only; avoid duplicating parent context across sibling sections.",
            "Separate source summaries, lessons, quotes, anecdotes, and key points so same-type drafting can use abstract craft notes without importing canon.",
        ]

    def _build_two_pass_context_glossary_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "two_pass_context_glossary_pipeline" not in patterns:
            return []
        return [
            "Run each chapter through an analysis pass before generation: summary, new terms, proper nouns, unresolved context, and glossary deltas.",
            "Use the current chapter summary, previous chapter summary, and cumulative glossary as inputs to the generation or translation pass.",
            "Support interrupted jobs by locating the last completed output/glossary pair and resuming from the next stable chapter number.",
        ]

    def _build_inline_author_edit_markup_versioning_hints(self, patterns: set[str]) -> list[str]:
        if "inline_author_edit_markup_versioning" not in patterns:
            return []
        return [
            "Allow inline author notes for POV, timeline, mood, active threads, and research context while keeping edit notes as a separate revision queue.",
            "Process edit-note markers into concrete changes, then remove or resolve them before final manuscript assembly.",
            "Tag major draft milestones and keep revision diffs inspectable so same-type rewrites and continuation repairs remain reversible.",
        ]

    def _build_causal_dramatica_agent_pipeline_hints(self, patterns: set[str]) -> list[str]:
        if "causal_dramatica_agent_pipeline" not in patterns:
            return []
        return [
            "Before drafting, map each major thread as cause -> pressure -> choice -> consequence rather than a loose sequence of cool events.",
            "Separate agent layers for premise, causality, scene plan, prose, and review; each layer must cite the accepted artifact it received.",
            "Foreshadowing tracking should record setup owner, expected payoff window, causal dependency, and unresolved-debt status.",
        ]

    def _build_capture_distillation_production_gate_hints(self, patterns: set[str]) -> list[str]:
        if "capture_distillation_production_gate" not in patterns:
            return []
        return [
            "Split author intake into capture, distillation, and production packets so raw ideas and source notes never flow directly into prose.",
            "Distillation must convert source/reference material into abstract story functions, constraints, and risks before any chapter task is opened.",
            "Production can draft only from accepted distilled packets plus local canon; rejected or undecided captures stay out of generation context.",
        ]

    def _build_skill_orchestrated_chinese_novel_workflow_hints(self, patterns: set[str]) -> list[str]:
        if "skill_orchestrated_chinese_novel_workflow" not in patterns:
            return []
        return [
            "Route Chinese web-novel work by stage: worldbuilding, character shaping, outline, chapter task, prose, polish, and continuity review.",
            "Skill packs are pattern sources only: do not bulk-import commands, install scripts, provider settings, or hidden runtime assumptions.",
            "Each stage should emit a small artifact and handoff checklist so long-form continuation survives session breaks and tool changes.",
        ]

    def _build_langgraph_story_state_machine_hints(self, patterns: set[str]) -> list[str]:
        if "langgraph_story_state_machine" not in patterns:
            return []
        return [
            "Model the writing loop as explicit state transitions: plan, retrieve, draft, review, repair, accept, and checkpoint.",
            "Every transition should validate required state fields before moving forward and preserve the rejected branch for debugging.",
            "For same-type creation, keep source-analysis state separate from transformed-story state so graph checkpoints cannot mix canon layers.",
        ]

    def _build_story_daemon_evolution_loop_hints(self, patterns: set[str]) -> list[str]:
        if "story_daemon_evolution_loop" not in patterns:
            return []
        return [
            "Autonomous story evolution must remain bounded by author goals, accepted canon, review gates, and a replayable work directory.",
            "Organic planning can propose turns, but acceptance requires evidence: plan delta, prose delta, state delta, and reviewer decision.",
            "Do not let background evolution close arcs, add irreversible lore, or rewrite prior chapters without a named acceptance boundary.",
        ]

    def _build_local_rag_writing_ide_gate_hints(self, patterns: set[str]) -> list[str]:
        if "local_rag_writing_ide_gate" not in patterns:
            return []
        return [
            "Keep local RAG as a scoped context layer: accepted canon, author notes, and source-deconstruction material must remain separately labeled.",
            "Before drafting, preview which retrieved chunks are canon, reference material, or style-only evidence; reject mixed-source context packs.",
            "BYOK/local-first posture is a runtime boundary, not permission to import external app code, model calls, or private user material.",
        ]

    def _build_canon_drift_continuity_qa_gate_hints(self, patterns: set[str]) -> list[str]:
        if "canon_drift_continuity_qa_gate" not in patterns:
            return []
        return [
            "Run canon-drift QA before chapter acceptance: characters, locations, rules, timeline, and scene facts must match the story bible or emit an explicit waiver.",
            "Build scene-focused context packs from the story bible so prompts receive only the facts needed for the current scene or revision.",
            "Treat continuity findings as blocking QA evidence; do not hide contradictions inside prose polish or style-review notes.",
        ]

    def _build_patch_replay_manuscript_state_gate_hints(self, patterns: set[str]) -> list[str]:
        if "patch_replay_manuscript_state_gate" not in patterns:
            return []
        return [
            "Record every generation and edit as an ordered patch with chapter range, source state, accepted delta, and derived preview artifact.",
            "The current manuscript must be reconstructable from outline, accepted patches, and version snapshots; direct overwrites need repair evidence.",
            "Use patch replay to compare continuation branches without merging failed drafts into canon or final manuscript exports.",
        ]

    def _build_microkernel_skill_plugin_isolation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "microkernel_skill_plugin_isolation_gate" not in patterns:
            return []
        return [
            "Model novel skills as isolated stage plugins with input/output contracts, validation, failure containment, and no implicit canon mutation.",
            "Event-bus or plugin hooks can propose worldbuilding, RAG memory, review, or scene-writing changes only through explicit accept/apply gates.",
            "Generated or third-party skills stay pattern-only until reviewed; plugin hot reload or install examples are never a source-intake default.",
        ]

    def _build_interactive_reader_writer_loop_gate_hints(self, patterns: set[str]) -> list[str]:
        if "interactive_reader_writer_loop_gate" not in patterns:
            return []
        return [
            "Separate reader guidance, author edits, assistant suggestions, and accepted chapter files so interactive continuation remains auditable.",
            "Every user-guided plot turn should produce a state delta and acceptance decision before the chapter file or lore codex is updated.",
            "Interactive revision tools may create candidates, but accepted prose must pass continuity, copy-risk, and patch-replay checks first.",
        ]

    def _build_abstract_style_learning_skill_gate_hints(self, patterns: set[str]) -> list[str]:
        if "abstract_style_learning_skill_gate" not in patterns:
            return []
        return [
            "Style-learning skills should extract abstract technique axes: pacing, sentence rhythm, scene construction, dialogue function, emotion landing, and repair rules.",
            "Keep sampled source text, distinctive names, plot facts, and proprietary expressions out of reusable style profiles and prompts.",
            "For same-type creation, require evidence that the learned style profile changes craft behavior without preserving source entities, order, or phrasing.",
        ]

    def _build_impromptu_thread_pool_chapter_gate_hints(self, patterns: set[str]) -> list[str]:
        if "impromptu_thread_pool_chapter_gate" not in patterns:
            return []
        return [
            "Support impromptu continuation by turning the current author instruction into a single-chapter blueprint before prose drafting.",
            "Maintain an open-thread pool with unresolved, partially paid, and development-needed buckets; finalize moves only accepted deltas.",
            "Scene or outline revisions should preserve untouched blueprint fields and record why any thread was opened, advanced, or resolved.",
        ]

    def _build_offline_inspiration_bank_style_gate_hints(self, patterns: set[str]) -> list[str]:
        if "offline_inspiration_bank_style_gate" not in patterns:
            return []
        return [
            "Separate local inspiration-bank materials from accepted canon, author notes, and style-only references before any Continue or Rewrite action.",
            "Style mimicry should compile an abstract boundary profile and banned carryover list, not inject source passages or proprietary phrasing.",
            "Offline/local-first posture protects privacy but does not relax license, provenance, copy-risk, or source-material labeling gates.",
        ]

    def _build_atelier_phase_pipeline_gate_hints(self, patterns: set[str]) -> list[str]:
        if "atelier_phase_pipeline_gate" not in patterns:
            return []
        return [
            "Model the novel atelier as explicit phases with named role outputs, beat-tree revisions, hook-audit findings, and author acceptance points.",
            "Human control mode is part of state: full, assisted, or manual approval changes which agent outputs may advance to canon.",
            "Hook auditors and continuity readers can block a beat or chapter, but they should emit review findings rather than silently rewriting prose.",
        ]

    def _build_book_mining_genesis_automation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "book_mining_genesis_automation_gate" not in patterns:
            return []
        return [
            "拆书产物先进入 pattern library：只保留爽点、引擎、结构、人物技法等抽象条目，不让原书设定直接进新书正典。",
            "立项阶段必须把 pattern assembly、市场/题材判断、评分门禁和 canon seed 分开，低分概念不能进入自动写作。",
            "自动续写只能读取已验收 canon seed、伏笔账本、人物不变量和复杂度预算；source mining 笔记保持只读参考。",
        ]

    def _build_multi_book_autopilot_studio_gate_hints(self, patterns: set[str]) -> list[str]:
        if "multi_book_autopilot_studio_gate" not in patterns:
            return []
        return [
            "多书并行时，每本书必须绑定独立 profile、项目目录、上下文文件和运行窗口，避免串书、串设定、串状态。",
            "Autopilot 只负责推进已授权批次：继续次数、完成短语、人工停止和模型提问应答都要有可见边界。",
            "每隔固定批次插入一次全书逻辑检查，先修时间线、人设、伏笔和设定硬伤，再进入下一轮连续写作。",
        ]

    def _build_longrun_commit_projection_health_gate_hints(self, patterns: set[str]) -> list[str]:
        if "longrun_commit_projection_health_gate" not in patterns:
            return []
        return [
            "长跑连载用 chapter commit 作为验收边界：正文、事件、实体、摘要和记忆更新必须从同一 accepted commit 派生。",
            "将 source-of-truth 文件和 read-model 投影分离；state、index、summary、memory 过期时禁止生成下一章。",
            "只读 dashboard 展示投影健康、最近事件、记忆覆盖和漂移风险，不应成为修改正典的写入口。",
        ]

    def _build_fresh_context_chapter_iteration_gate_hints(self, patterns: set[str]) -> list[str]:
        if "fresh_context_chapter_iteration_gate" not in patterns:
            return []
        return [
            "Run each chapter iteration from a fresh context packet: story bible, chapter manifest, progress log, previous accepted chapter, and explicit next-chapter brief.",
            "Detect the next incomplete chapter from the manifest before writing; never rely on chat memory or an agent's last answer as the completion source.",
            "After review/revise, update the progress log and chapter status only for accepted text; failed drafts remain outside canon and outside the next fresh-context packet.",
        ]

    def _build_reader_reward_channel_gate_hints(self, patterns: set[str]) -> list[str]:
        if "reader_reward_channel_gate" not in patterns:
            return []
        return [
            "Review each high-impact scene on separate reader channels: immersion/transportation, prose aesthetics, social-simulation believability, and flow.",
            "Reader-sim output is a diagnostic signal, not canon: convert confusion, boredom, pull, or emotional miss into bounded revision tasks before accepting prose.",
            "For same-type creation, score transformed chapters for reader reward and independence together; source resemblance must not count as reader pull.",
        ]

    def _build_tri_modal_workflow_validation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "tri_modal_workflow_validation_gate" not in patterns:
            return []
        return [
            "Declare workflow mode before mutation: Create may add bible/plan/chapter facts, Edit may patch scoped fields, and Validate may only emit findings unless explicitly applied.",
            "Run a pre-writing checklist before chapter drafting: canon inputs, voice baseline, continuity risks, character states, theme intent, rhythm target, and copy-risk boundary.",
            "After each accepted chapter, run the audit chain in order: review, bible/state update, per-character contradiction audit, theme progression, rhythm/pacing check, then next-chapter handoff.",
        ]

    def _build_scene_promise_mob_review_gate_hints(self, patterns: set[str]) -> list[str]:
        if "scene_promise_mob_review_gate" not in patterns:
            return []
        return [
            "Turn each chapter promise into 3-7 scene cards with POV, location, time, goal, obstacle, tactic, crisis, value shift, cost, exit emotion, and next hook.",
            "Before canon mutation, run a cited review queue: plot, character, theme, continuity, and prose each raise one focused comment for accept/reject/revise/park.",
            "Only accepted, citation-backed mob-review decisions may update the bible, relationships, timeline, or chapter plan; chat-only advice stays scratch.",
        ]

    def _build_webnovel_genre_tracker_gate_hints(self, patterns: set[str]) -> list[str]:
        if "webnovel_genre_tracker_gate" not in patterns:
            return []
        return [
            "Before serial chapter drafting, confirm project structure exists: novel config, chapter folder, character sheets, world entries, style guide, and editable outline.",
            "Track genre-specific state separately: foreshadowing seeds/payoffs, timeline events, LitRPG stats/inventory/quests, and romance-stage beats.",
            "Continuity checks should flag overdue foreshadowing, stale characters, chapter gaps, unresolved power milestones, and cliffhanger-type repetition before accepting the chapter.",
        ]

    def _build_simulation_causal_ledger_verification_gate_hints(self, patterns: set[str]) -> list[str]:
        if "simulation_causal_ledger_verification_gate" not in patterns:
            return []
        return [
            "Model long-form continuation as simulation state: world truth, character memory, belief state, utterance history, causal ledger, and chapter summaries must advance together.",
            "Every generation surface should emit replayable artifacts such as result.json, chapter text, chapter summary, causal-ledger.json, and run metadata.",
            "Run a long-horizon verification gate before trusting autopilot: canonical validation failures, causal contradictions, and foreshadow quality failures block acceptance.",
        ]

    def _build_writer_git_exploration_review_gate_hints(self, patterns: set[str]) -> list[str]:
        if "writer_git_exploration_review_gate" not in patterns:
            return []
        return [
            "Treat risky rewrite directions as explorations/branches, not direct overwrites of the accepted manuscript or source-derived canon.",
            "Review chapter changes at word or paragraph level with author-controlled accept/reject/modify decisions before merging into the main manuscript.",
            "Beta-reader annotations, editor notes, and alternate endings should carry provenance as review commits or change packages so accepted changes remain replayable.",
        ]

    def _build_narrative_qa_comprehension_gate_hints(self, patterns: set[str]) -> list[str]:
        if "narrative_qa_comprehension_gate" not in patterns:
            return []
        return [
            "After拆书, generate or import reviewer questions across plot, motive, relationship, setting rule, and unresolved hook; each answer must cite a summary or chapter evidence id.",
            "Continuation prompts should include only answered, evidence-backed facts; unanswered QA items become continuity questions instead of invented bridges.",
            "For同类型仿写, rebuild the QA set around transformed canon so source-book answers cannot satisfy new-story comprehension checks.",
        ]

    def _build_chapter_summary_alignment_gate_hints(self, patterns: set[str]) -> list[str]:
        if "chapter_summary_alignment_gate" not in patterns:
            return []
        return [
            "Maintain paragraph, chapter, arc, and book-level summaries as separate granularities; chapter acceptance requires local summary and book-level direction to agree.",
            "Check summaries for causal and temporal dependency loss: who caused the change, when it happened, what state changed, and what future obligation remains.",
            "When续写 changes a plot line, update derived summaries only after the chapter commit; stale summaries cannot feed the next prompt.",
        ]

    def _build_story_question_answer_validation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "story_question_answer_validation_gate" not in patterns:
            return []
        return [
            "Validate each important scene with section-grounded QA: setting, character, goal, action, outcome, feeling, and theme questions should point to exact section or chapter ids.",
            "Do not accept answers that are plausible genre guesses but unsupported by the current story section, bible state, or accepted chapter memory.",
            "Use missing QA coverage to repair拆书 notes before writing, especially around hidden motives, relationships, and scene consequences.",
        ]

    def _build_causal_why_explanation_gate_hints(self, patterns: set[str]) -> list[str]:
        if "causal_why_explanation_gate" not in patterns:
            return []
        return [
            "For every major character action, ask why it happened and require a plausible answer grounded in prior events, belief state, pressure, and helpful sentence/chapter evidence.",
            "Mark why-answers as explicit, implicit, or unavailable; unavailable motives must become reveal debt or revision tasks, not hallucinated continuity.",
            "Reject续写 drafts when character actions are only convenient for plot and cannot pass a motive-validity review.",
        ]

    def _build_story_commonsense_consistency_gate_hints(self, patterns: set[str]) -> list[str]:
        if "story_commonsense_consistency_gate" not in patterns:
            return []
        return [
            "Track naive psychology state for each key character: motivation, emotion, belief, desire, social relation, and likely reaction after every accepted beat.",
            "Before accepting a continuation, compare new actions against current mental-state ledger and flag sudden emotion, belief, or desire jumps without on-page cause.",
            "For同类型仿写, preserve only abstract psychology functions; source-specific motives, wounds, and relationship triggers must be transformed.",
        ]

    def _build_query_focused_long_summary_gate_hints(self, patterns: set[str]) -> list[str]:
        if "query_focused_long_summary_gate" not in patterns:
            return []
        return [
            "Use query-focused summaries for long context: plot question, character question, relationship question, and world-rule question should produce different context slices.",
            "Compare multiple summary candidates and record disagreements before compressing long chapters into prompt context.",
            "A query-focused summary may guide retrieval or review, but it must not replace the accepted chapter text or bible state as the truth source.",
        ]

    def _build_temporal_canon_context_graph_hints(self, patterns: set[str]) -> list[str]:
        if "temporal_canon_context_graph" not in patterns:
            return []
        return [
            "Store canon facts as temporal graph episodes with source chapter, observed_at, valid_from, invalid_after, and provenance notes.",
            "Retrieve context through a hybrid of semantic match, entity-neighborhood traversal, chronology window, and explicit relationship edges.",
            "When a continuation changes facts, add a new episode or validity window instead of overwriting earlier canon evidence.",
        ]

    def _build_long_term_author_preference_memory_hints(self, patterns: set[str]) -> list[str]:
        if "long_term_author_preference_memory" not in patterns:
            return []
        return [
            "Separate author preferences, project-level style decisions, session goals, and transient drafting notes into different memory scopes.",
            "Promote a preference into long-term memory only after it is confirmed or repeatedly used, not from one draft failure.",
            "During same-type creation, keep user/author preference memory separate from source-book deconstruction notes.",
        ]

    def _build_community_graph_source_deconstruction_hints(self, patterns: set[str]) -> list[str]:
        if "community_graph_source_deconstruction" not in patterns:
            return []
        return [
            "Deconstruct a source book into entity communities, relationship clusters, and community summaries before extracting reusable story mechanics.",
            "Use global graph summaries for whole-book structure questions and local graph neighborhoods for chapter-level continuation context.",
            "Keep source community reports as analysis evidence; transformed canon needs its own graph and summaries.",
        ]

    def _build_dual_level_graph_vector_retrieval_hints(self, patterns: set[str]) -> list[str]:
        if "dual_level_graph_vector_retrieval" not in patterns:
            return []
        return [
            "Select continuation context with dual-level retrieval: vector similarity for related passages and graph traversal for canon-critical entities.",
            "Choose query mode explicitly: local for character/state facts, global for theme or arc summaries, hybrid for chapter planning, naive only for fallback.",
            "Log which retrieval mode supplied each context item so weak graph or vector coverage can be repaired.",
        ]

    def _build_schema_guided_graph_extraction_hints(self, patterns: set[str]) -> list[str]:
        if "schema_guided_graph_extraction" not in patterns:
            return []
        return [
            "Extract canon/source graphs with a bounded schema: node labels, relationship types, required properties, source location, and confidence.",
            "Attach source metadata to every extracted node and edge so reviewers can trace it back to chapter, paragraph, or source-note evidence.",
            "Reject graph mutations that introduce unlabeled nodes, unsupported relationships, or facts without source metadata.",
        ]

    def _build_trope_inventory_similarity_gate_hints(self, patterns: set[str]) -> list[str]:
        if "trope_inventory_similarity_gate" not in patterns:
            return []
        return [
            "Build a compact trope inventory for source and draft; shared genre-level tropes are allowed, but rare source-specific combinations require rewrite.",
            "For same-type creation, require independent cast, setting, stakes, causal order, and payoff evidence before accepting a high trope-overlap draft.",
        ]

    def _build_trope_graph_expectation_map_hints(self, patterns: set[str]) -> list[str]:
        if "trope_graph_expectation_map" not in patterns:
            return []
        return [
            "Use trope co-occurrence as an expectation map, not a plot route; genre-adjacent trope edges should create options rather than mandatory beats.",
            "Flag rare trope adjacency chains that mirror the source work so the outline can swap relation, timing, or consequence before prose drafting.",
        ]

    def _build_trope_density_novelty_budget_hints(self, patterns: set[str]) -> list[str]:
        if "trope_density_novelty_budget" not in patterns:
            return []
        return [
            "Track trope density per arc and reserve a novelty budget for inversions, shifted costs, new symbols, or unexpected payoffs.",
            "Do not fix cliche saturation by paraphrasing source beats; change the conflict pressure or outcome function.",
        ]

    def _build_trope_source_boundary_review_hints(self, patterns: set[str]) -> list[str]:
        if "trope_source_boundary_review" not in patterns:
            return []
        return [
            "Treat trope sites and parsers as metadata-only references by default: no live scraping, no copied page prose, no mass mirroring, and no runtime parser execution.",
            "If trope labels are used, store source URL, observed date, license/terms uncertainty, and the reason the label helps review rather than generation.",
        ]

    def _build_source_license_detection_gate_hints(self, patterns: set[str]) -> list[str]:
        if "source_license_detection_gate" not in patterns:
            return []
        return [
            "Detect and record the source license before source-book import, deconstruction, continuation, or same-type imitation uses any long text.",
            "Unknown, missing, or low-confidence license status blocks copying source passages into prompts; keep only bibliographic metadata until reviewed.",
        ]

    def _build_spdx_reuse_compliance_gate_hints(self, patterns: set[str]) -> list[str]:
        if "spdx_reuse_compliance_gate" not in patterns:
            return []
        return [
            "Normalize source rights to SPDX ids and keep copyright/attribution metadata at source-file or source-artifact granularity.",
            "Treat REUSE-style metadata as a provenance checklist for imported text, not as permission to execute external tooling or import upstream code.",
        ]

    def _build_public_domain_corpus_boundary_hints(self, patterns: set[str]) -> list[str]:
        if "public_domain_corpus_boundary" not in patterns:
            return []
        return [
            "Public-domain sources still need a source manifest: title, author, edition/source URL, observed date, extraction format, and jurisdiction caveat.",
            "Project Gutenberg or other corpus downloaders remain runtime-deferred; metadata can guide admission, but downloader output is not drafting context by default.",
        ]

    def _build_attribution_derivative_work_gate_hints(self, patterns: set[str]) -> list[str]:
        if "attribution_derivative_work_gate" not in patterns:
            return []
        return [
            "Before same-type creation, decide whether the source is inspiration, quotation, adaptation, translation, or derivative-risk material.",
            "Attribution requirements and derivative-use boundaries must be satisfied outside prose generation; do not bury them inside style prompts.",
        ]

    def _build_source_entity_redaction_gate_hints(self, patterns: set[str]) -> list[str]:
        if "source_entity_redaction_gate" not in patterns:
            return []
        return [
            "Before source deconstruction or same-type drafting, detect and redact source-specific names, locations, factions, artifacts, powers, titles, and other proper nouns into review placeholders.",
            "Treat entity redaction as an admission gate: unredacted source entities may be used only when they are approved canon for a true continuation.",
        ]

    def _build_custom_entity_label_inventory_hints(self, patterns: set[str]) -> list[str]:
        if "custom_entity_label_inventory" not in patterns:
            return []
        return [
            "Use custom fiction entity labels beyond PERSON/ORG/LOC: faction, rank, artifact, power, species, place-type, title, invented term, and relationship label.",
            "Keep the source entity inventory as analysis evidence; same-type creation must rebuild an independent inventory before outlining.",
        ]

    def _build_placeholder_alias_consistency_map_hints(self, patterns: set[str]) -> list[str]:
        if "placeholder_alias_consistency_map" not in patterns:
            return []
        return [
            "Maintain stable placeholders and replacement ids across chapters so source aliases, nicknames, and titles do not drift back into prompts under partial redaction.",
            "Review placeholder collisions when two source entities collapse into one replacement or one source entity receives multiple replacements.",
        ]

    def _build_proper_noun_leakage_review_hints(self, patterns: set[str]) -> list[str]:
        if "proper_noun_leakage_review" not in patterns:
            return []
        return [
            "Run a proper-noun leakage review on drafts against source blocklists and approved exception lists before accepting chapters.",
            "Names that are common genre terms need reviewer notes; distinctive names, titles, places, factions, and artifacts require replacement unless explicitly allowed.",
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
        if "snowflake_premise_expansion" in patterns:
            targets.append("premise_chain_remap")
        if "outliner_index_cards" in patterns:
            targets.append("outline_card_remap")
        if "narrative_strand_mapping" in patterns:
            targets.append("narrative_strand_remap")
        if "character_depth_interview" in patterns:
            targets.append("character_depth_remap")
        if "mindmap_visual_planning" in patterns:
            targets.append("idea_node_remap")
        if "human_synopsis_gate" in patterns:
            targets.append("synopsis_gate_remap")
        if "retrieval_guided_span_rewrite" in patterns:
            targets.append("retrieval_span_remap")
        if "runtime_artifact_trace" in patterns:
            targets.append("trace_artifact_remap")
        if "schema_validated_state_delta" in patterns:
            targets.append("state_delta_remap")
        if "recursive_adaptive_planning" in patterns:
            targets.append("adaptive_task_tree_remap")
        if "frontmatter_story_schema" in patterns:
            targets.append("frontmatter_schema_remap")
        if "continuity_bridge_window" in patterns:
            targets.append("continuity_bridge_remap")
        if "voice_table_polish_axis" in patterns:
            targets.append("voice_table_remap")
        if "beat_strand_framework" in patterns:
            targets.append("beat_strand_remap")
        if "genre_parameterized_worldbuilding" in patterns:
            targets.append("genre_module_remap")
        if "prose_preflight_voice_calibration" in patterns:
            targets.append("voice_calibration_remap")
        if "sourcebook_author_workbench" in patterns:
            targets.append("sourcebook_remap")
        if "semantic_long_context_search" in patterns:
            targets.append("semantic_context_remap")
        if "contradiction_taxonomy_checker" in patterns:
            targets.append("consistency_taxonomy_remap")
        if "cross_chapter_redundancy_audit" in patterns:
            targets.append("redundancy_pattern_remap")
        if "humanization_stylometry_levers" in patterns:
            targets.append("stylometry_rule_remap")
        if "research_taxonomy_story_map" in patterns:
            targets.append("method_taxonomy_remap")
        if "novel_to_multimodal_pipeline" in patterns:
            targets.append("multimodal_pipeline_remap")
        if "entity_to_visual_asset_pipeline" in patterns:
            targets.append("visual_asset_remap")
        if "agentic_book_planner_pipeline" in patterns:
            targets.append("book_planner_role_remap")
        if "rag_synopsis_spine" in patterns:
            targets.append("synopsis_spine_remap")
        if "anti_repetition_prompt_rules" in patterns:
            targets.append("anti_repetition_rule_remap")
        if "prompt_recipe_experiment_grid" in patterns:
            targets.append("prompt_recipe_remap")
        if "append_only_generation_review_log" in patterns:
            targets.append("experiment_log_remap")
        if "narrative_arc_template_control" in patterns:
            targets.append("narrative_arc_remap")
        if "mode_contract_generation_gate" in patterns:
            targets.append("mode_contract_axis_remap")
        if "source_study_method_bank_isolation_gate" in patterns:
            targets.append("method_bank_remap")
        if "nrd_task_tree_pipeline" in patterns:
            targets.append("nrd_task_tree_remap")
        if "sampling_parameter_quality_sweep" in patterns:
            targets.append("sampling_quality_remap")
        if "story_structure_rag_planning" in patterns:
            targets.append("structure_scaffold_remap")
        if "story_contract_commit_chain" in patterns:
            targets.append("commit_chain_remap")
        if "fact_snapshot_delta_gate" in patterns:
            targets.append("fact_delta_remap")
        if "foreshadowing_debt_budget" in patterns:
            targets.append("foreshadowing_debt_remap")
        if "reader_retention_review_gate" in patterns:
            targets.append("retention_hook_remap")
        if "reader_rating_signal_model" in patterns:
            targets.append("reader_signal_remap")
            targets.append("shelf_tag_expectation_remap")
        if "review_spoiler_sentiment_corpus" in patterns:
            targets.append("review_cluster_remap")
            targets.append("spoiler_boundary_remap")
        if "beta_reader_archetype_panel" in patterns:
            targets.append("beta_reader_panel_remap")
        if "comp_title_market_positioning" in patterns:
            targets.append("comp_title_positioning_remap")
        if "local_reader_experience_editor" in patterns:
            targets.append("reader_experience_hook_remap")
        if "draft_stage_revision_ladder" in patterns:
            targets.append("draft_stage_remap")
        if "rolling_summary_context_trim" in patterns:
            targets.append("rolling_context_remap")
        if "pairwise_story_comparison_ranking" in patterns:
            targets.append("pairwise_variant_remap")
        if "multidimensional_quality_rubric" in patterns:
            targets.append("quality_rubric_remap")
        if "story_theory_beat_evaluation" in patterns:
            targets.append("story_theory_beat_remap")
        if "constraint_specificity_creativity_benchmark" in patterns:
            targets.append("constraint_specificity_remap")
        if "style_axis_diversity_fingerprint" in patterns:
            targets.append("style_axis_remap")
        if "event_outline_history_compression" in patterns:
            targets.append("event_outline_remap")
        if "agentic_story_world_simulation" in patterns:
            targets.append("agent_world_simulation_remap")
        if "delivery_manuscript_assembly" in patterns:
            targets.append("delivery_packaging_remap")
        if "export_format_fidelity_audit" in patterns:
            targets.append("export_fidelity_remap")
        if "preview_toc_packaging" in patterns:
            targets.append("preview_toc_remap")
        if "cover_kdp_metadata_boundary" in patterns:
            targets.append("publication_metadata_remap")
        if "branching_choice_graph" in patterns:
            targets.append("choice_branch_remap")
        if "node_dialogue_state_machine" in patterns:
            targets.append("dialogue_node_remap")
        if "passage_link_navigation_map" in patterns:
            targets.append("passage_navigation_remap")
        if "choice_stats_consequence_gate" in patterns:
            targets.append("choice_stat_consequence_remap")
        if "source_text_fingerprint_gate" in patterns:
            targets.append("fingerprint_baseline_remap")
        if "fuzzy_phrase_similarity_gate" in patterns:
            targets.append("fuzzy_phrase_threshold_remap")
        if "diff_span_copy_review" in patterns:
            targets.append("diff_span_review_remap")
        if "minhash_lsh_near_duplicate_gate" in patterns:
            targets.append("minhash_lsh_threshold_remap")
        if "simhash_hamming_similarity_gate" in patterns:
            targets.append("simhash_hamming_threshold_remap")
        if "semantic_duplicate_cluster_gate" in patterns:
            targets.append("semantic_cluster_independence_remap")
        if "embedding_similarity_independence_gate" in patterns:
            targets.append("embedding_neighbor_independence_remap")
        if "corpus_leakage_dedup_review_gate" in patterns:
            targets.append("corpus_leakage_boundary_remap")
        if "character_quote_attribution_map" in patterns:
            targets.append("quote_speaker_remap")
        if "readability_pacing_metric_gate" in patterns:
            targets.append("readability_curve_remap")
        if "prose_lint_style_rule_gate" in patterns:
            targets.append("prose_lint_rule_remap")
        if "grammar_spelling_copyedit_gate" in patterns:
            targets.append("grammar_copyedit_exception_remap")
        if "copyedit_diagnostic_triage_queue" in patterns:
            targets.append("copyedit_triage_policy_remap")
        if "lexical_diversity_voice_audit" in patterns:
            targets.append("lexical_diversity_remap")
        if "stylometric_author_fingerprint_gate" in patterns:
            targets.append("stylometric_fingerprint_remap")
        if "function_word_syntax_style_gate" in patterns:
            targets.append("function_word_syntax_remap")
        if "authorship_attribution_similarity_gate" in patterns:
            targets.append("authorship_similarity_threshold_remap")
        if "style_overfit_regression_gate" in patterns:
            targets.append("style_overfit_regression_remap")
        if "paraphrase_independence_review_gate" in patterns:
            targets.append("paraphrase_independence_policy_remap")
        if "keyphrase_motif_extraction" in patterns:
            targets.append("keyphrase_motif_remap")
        if "chinese_segmentation_keyword_gate" in patterns:
            targets.append("chinese_segmentation_dictionary_remap")
        if "chinese_ner_alias_consistency_gate" in patterns:
            targets.append("chinese_entity_alias_remap")
        if "source_entity_redaction_gate" in patterns:
            targets.append("source_entity_redaction_remap")
        if "custom_entity_label_inventory" in patterns:
            targets.append("custom_entity_label_remap")
        if "placeholder_alias_consistency_map" in patterns:
            targets.append("placeholder_alias_namespace_remap")
        if "proper_noun_leakage_review" in patterns:
            targets.append("proper_noun_blocklist_remap")
        if "chinese_text_normalization_gate" in patterns:
            targets.append("chinese_normalization_policy_remap")
        if "chinese_error_correction_review_gate" in patterns:
            targets.append("chinese_correction_exception_remap")
        if "source_format_import_manifest" in patterns:
            targets.append("source_import_structure_remap")
        if "pdf_layout_text_extraction_gate" in patterns:
            targets.append("pdf_layout_evidence_remap")
        if "ocr_scanned_page_import_gate" in patterns:
            targets.append("ocr_uncertainty_review_remap")
        if "document_partition_chapter_detection_gate" in patterns:
            targets.append("chapter_partition_structure_remap")
        if "import_provenance_checksum_gate" in patterns:
            targets.append("import_provenance_lineage_remap")
        if "epub_structure_validation_gate" in patterns:
            targets.append("epub_validation_delivery_remap")
        if "ebook_accessibility_audit_gate" in patterns:
            targets.append("ebook_accessibility_remap")
        if "front_back_matter_metadata_gate" in patterns:
            targets.append("front_back_matter_metadata_remap")
        if "toc_navigation_consistency_gate" in patterns:
            targets.append("toc_navigation_remap")
        if "agentic_editorial_pipeline_gate" in patterns:
            targets.append("editorial_role_boundary_remap")
        if "chapter_state_archive_ladder" in patterns:
            targets.append("chapter_state_ladder_remap")
        if "section_metadata_traceability_gate" in patterns:
            targets.append("section_metadata_traceability_remap")
        if "ai_prose_fingerprint_cluster_gate" in patterns:
            targets.append("prose_fingerprint_threshold_remap")
        if "author_candidate_canon_confirmation_gate" in patterns:
            targets.append("candidate_canon_decision_remap")
        if "progressive_spoiler_context_window_gate" in patterns:
            targets.append("spoiler_context_window_remap")
        if "chapter_control_card_writeback_gate" in patterns:
            targets.append("chapter_control_card_remap")
        if "trace_replay_revision_workspace_gate" in patterns:
            targets.append("trace_replay_decision_remap")
        if "relationship_graph_global_replace_gate" in patterns:
            targets.append("relationship_graph_replace_remap")
        if "bookrun_audit_trail_gate" in patterns:
            targets.append("bookrun_audit_trail_remap")
        if "provider_budget_smoke_gate" in patterns:
            targets.append("provider_budget_profile_remap")
        if "sidecar_memory_profile_boundary" in patterns:
            targets.append("sidecar_memory_profile_remap")
        if "outline_checkpoint_milestone_gate" in patterns:
            targets.append("outline_milestone_remap")
        if "language_localization_style_profile_gate" in patterns:
            targets.append("language_style_profile_remap")
        if "progressive_disclosure_skill_protocol_gate" in patterns:
            targets.append("skill_protocol_route_remap")
        if "anti_slop_rulepack_triage_gate" in patterns:
            targets.append("anti_slop_rulepack_remap")
        if "user_modifier_project_blueprint_gate" in patterns:
            targets.append("project_blueprint_modifier_remap")
        if "portable_canon_skill_runtime_gate" in patterns:
            targets.append("portable_canon_runtime_remap")
        if "staged_outline_chunk_window_gate" in patterns:
            targets.append("staged_outline_window_remap")
        if "wiki_canon_graph_lint_gate" in patterns:
            targets.append("wiki_canon_graph_remap")
        if "plan_draft_log_verify_loop_gate" in patterns:
            targets.append("plan_draft_log_verify_remap")
        if "mcp_scene_index_revision_boundary" in patterns:
            targets.append("scene_index_revision_boundary_remap")
        if "verbalized_sampling_diversity_wiki_gate" in patterns:
            targets.append("verbalized_sampling_diversity_remap")
        if "literary_event_entity_annotation_gate" in patterns:
            targets.append("literary_annotation_role_remap")
        if "narrative_event_evolution_graph_gate" in patterns:
            targets.append("event_chain_causality_remap")
        if "sentiment_arc_emotion_trajectory_gate" in patterns:
            targets.append("sentiment_arc_emotion_remap")
        if "cross_context_coreference_gate" in patterns:
            targets.append("cross_context_coreference_remap")
        if "character_interaction_network_gate" in patterns:
            targets.append("character_network_relationship_remap")
        if "semantic_chunk_boundary_map" in patterns:
            targets.append("chunk_boundary_remap")
        if "chapter_summary_anchor_gate" in patterns:
            targets.append("summary_anchor_remap")
        if "topic_drift_map" in patterns:
            targets.append("topic_drift_remap")
        if "context_faithfulness_eval_gate" in patterns:
            targets.append("faithfulness_eval_remap")
        if "retrieval_trace_observability_gate" in patterns:
            targets.append("retrieval_trace_remap")
        if "prompt_regression_eval_suite" in patterns:
            targets.append("prompt_regression_remap")
        if "agentwrite_plan_write_pipeline" in patterns:
            targets.append("plan_write_stage_remap")
        if "long_output_length_quality_ruler" in patterns:
            targets.append("long_output_ruler_remap")
        if "long_context_reward_dimension_gate" in patterns:
            targets.append("reward_dimension_remap")
        if "instance_specific_writing_criteria_gate" in patterns:
            targets.append("instance_criteria_remap")
        if "material_grounded_query_refinement" in patterns:
            targets.append("material_grounding_remap")
        if "hybrid_rubric_pairwise_elo_judge" in patterns:
            targets.append("hybrid_elo_judge_remap")
        if "judge_bias_mitigation_check" in patterns:
            targets.append("judge_bias_mitigation_remap")
        if "plan_reflect_character_chapter_pipeline" in patterns:
            targets.append("plan_reflect_character_trace_remap")
        if "human_story_metric_panel" in patterns:
            targets.append("human_story_metric_axis_remap")
        if "hierarchical_cowriting_story_scaffold" in patterns:
            targets.append("hierarchical_story_scaffold_remap")
        if "human_coauthor_edit_boundary" in patterns:
            targets.append("coauthor_edit_boundary_remap")
        if "recursive_reprompt_revision_loop" in patterns:
            targets.append("recursive_revision_loop_remap")
        if "reranker_guided_candidate_selection" in patterns:
            targets.append("reranker_candidate_selection_remap")
        if "character_dialogue_persona_memory" in patterns:
            targets.append("character_persona_memory_remap")
        if "event_to_sentence_realization_trace" in patterns:
            targets.append("event_realization_trace_remap")
        if "entity_memory_slotfill_grounding" in patterns:
            targets.append("entity_slotfill_grounding_remap")
        if "book_memory_bank_context_lattice" in patterns:
            targets.append("memory_bank_context_remap")
        if "spec_driven_fiction_scene_tasks" in patterns:
            targets.append("spec_scene_task_remap")
        if "toc_aware_source_deconstruction" in patterns:
            targets.append("source_toc_summary_remap")
        if "two_pass_context_glossary_pipeline" in patterns:
            targets.append("glossary_context_remap")
        if "inline_author_edit_markup_versioning" in patterns:
            targets.append("inline_markup_revision_remap")
        if "causal_dramatica_agent_pipeline" in patterns:
            targets.append("causal_thread_remap")
        if "capture_distillation_production_gate" in patterns:
            targets.append("distilled_packet_remap")
        if "skill_orchestrated_chinese_novel_workflow" in patterns:
            targets.append("chinese_webnovel_skill_stage_remap")
        if "langgraph_story_state_machine" in patterns:
            targets.append("story_state_machine_remap")
        if "story_daemon_evolution_loop" in patterns:
            targets.append("story_evolution_loop_remap")
        if "local_rag_writing_ide_gate" in patterns:
            targets.append("rag_context_scope_remap")
        if "canon_drift_continuity_qa_gate" in patterns:
            targets.append("canon_drift_rule_remap")
        if "patch_replay_manuscript_state_gate" in patterns:
            targets.append("patch_replay_branch_remap")
        if "microkernel_skill_plugin_isolation_gate" in patterns:
            targets.append("skill_plugin_stage_remap")
        if "interactive_reader_writer_loop_gate" in patterns:
            targets.append("interactive_choice_delta_remap")
        if "abstract_style_learning_skill_gate" in patterns:
            targets.append("abstract_style_profile_remap")
        if "impromptu_thread_pool_chapter_gate" in patterns:
            targets.append("impromptu_thread_pool_remap")
        if "offline_inspiration_bank_style_gate" in patterns:
            targets.append("inspiration_bank_style_boundary_remap")
        if "atelier_phase_pipeline_gate" in patterns:
            targets.append("atelier_phase_beat_tree_remap")
        if "book_mining_genesis_automation_gate" in patterns:
            targets.append("book_mined_pattern_to_canon_seed_remap")
        if "multi_book_autopilot_studio_gate" in patterns:
            targets.append("multi_book_profile_boundary_remap")
        if "longrun_commit_projection_health_gate" in patterns:
            targets.append("chapter_commit_projection_remap")
        if "fresh_context_chapter_iteration_gate" in patterns:
            targets.append("fresh_context_loop_remap")
        if "inline_human_machine_coauthoring_gate" in patterns:
            targets.append("inline_revision_span_remap")
        if "hierarchical_orchestrator_generation_gate" in patterns:
            targets.append("volume_arc_chapter_hierarchy_remap")
        if "batch_continuation_progress_queue_gate" in patterns:
            targets.append("batch_queue_progress_remap")
        if "homogeneity_prompt_variation_gate" in patterns:
            targets.append("variation_axis_remap")
        if "local_author_data_boundary_gate" in patterns:
            targets.append("author_data_boundary_remap")
        if "prompt_preset_variable_library_gate" in patterns:
            targets.append("prompt_preset_variable_remap")
        if "imported_manuscript_migration_outline_gate" in patterns:
            targets.append("imported_outline_boundary_remap")
        if "style_dna_reference_library_gate" in patterns:
            targets.append("style_dna_abstraction_remap")
        if "draft_candidate_promotion_gate" in patterns:
            targets.append("draft_candidate_promotion_remap")
        if "privacy_preserving_local_index_gate" in patterns:
            targets.append("metadata_index_privacy_remap")
        if "chapter_description_continuity_bridge_gate" in patterns:
            targets.append("chapter_description_continuity_remap")
        if "selective_streaming_regeneration_gate" in patterns:
            targets.append("selective_regeneration_scope_remap")
        if "research_citation_boundary_gate" in patterns:
            targets.append("research_source_citation_remap")
        if "beta_reader_summary_context_gate" in patterns:
            targets.append("beta_reader_feedback_context_remap")
        if "style_vocab_world_card_extraction_gate" in patterns:
            targets.append("style_vocabulary_remap")
            targets.append("world_card_boundary_remap")
        if "prompt_only_decay_ceiling_gate" in patterns:
            targets.append("prompt_only_ceiling_remap")
        if "serial_platform_minimum_audit_gate" in patterns:
            targets.append("serial_audit_cadence_remap")
        if "multi_agent_reject_retry_review_gate" in patterns:
            targets.append("multi_agent_retry_trace_remap")
        if "story_bible_context_packet_branch_gate" in patterns:
            targets.append("context_packet_branch_remap")
        if "memory_augmented_delta_verification_gate" in patterns:
            targets.append("delta_fact_index_remap")
        if "statistical_style_benchmark_rewrite_gate" in patterns:
            targets.append("statistical_style_benchmark_remap")
        if "temporal_canon_context_graph" in patterns:
            targets.append("temporal_graph_context_remap")
        if "long_term_author_preference_memory" in patterns:
            targets.append("author_preference_memory_remap")
        if "community_graph_source_deconstruction" in patterns:
            targets.append("source_community_graph_remap")
        if "dual_level_graph_vector_retrieval" in patterns:
            targets.append("graph_vector_retrieval_remap")
        if "schema_guided_graph_extraction" in patterns:
            targets.append("schema_guided_graph_remap")
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
        if "mode_contract_generation_gate" in patterns:
            hints.append("Use mode contracts as visible output-shape constraints, then fill them with transformed characters, conflicts, and setting rather than source specifics.")
        if "source_study_method_bank_isolation_gate" in patterns:
            hints.append("Load source-study insights as method ids and craft pressure only; do not load raw study chunks or source facts into the generation prompt.")
        if "inline_human_machine_coauthoring_gate" in patterns:
            hints.append("Ask for localized revision candidates with span ids and author decision points instead of whole-chapter regeneration when only one beat fails.")
        if "hierarchical_orchestrator_generation_gate" in patterns:
            hints.append("State whether the prompt is operating at volume, arc, chapter, or scene scope, and include only artifacts from that scope plus required parent context.")
        if "batch_continuation_progress_queue_gate" in patterns:
            hints.append("For batch runs, include queue cursor and previous accepted chapter id so each prompt knows exactly what it may continue from.")
        if "homogeneity_prompt_variation_gate" in patterns:
            hints.append("Include variation axes in the prompt—pressure source, scene function, POV distance, rhythm, and payoff style—before generating adjacent chapters.")
        if "local_author_data_boundary_gate" in patterns:
            hints.append("Label all local files, source notes, and generated drafts by boundary class before they enter the prompt: canon, author note, pattern metadata, or blocked runtime surface.")
        if "prompt_preset_variable_library_gate" in patterns:
            hints.append("Use prompt presets as visible contracts; same-type drafts must show variable values and source-boundary labels instead of hidden template defaults.")
        if "imported_manuscript_migration_outline_gate" in patterns:
            hints.append("Transform imported chapter maps into a new outline spine before drafting; do not preserve original chapter order unless the task is faithful continuation.")
        if "style_dna_reference_library_gate" in patterns:
            hints.append("Use style-DNA ids as abstract craft guidance only; generate new premise, cast, conflicts, and phrasing for same-type work.")
        if "draft_candidate_promotion_gate" in patterns:
            hints.append("For same-type creation, create draft candidates and require copy-risk review before any candidate can become confirmed text.")
        if "privacy_preserving_local_index_gate" in patterns:
            hints.append("Use metadata-only local search to find relevant project artifacts, then explicitly choose which new-story snippets may enter the prompt.")
        if "chapter_description_continuity_bridge_gate" in patterns:
            hints.append("Build transformed chapter descriptions from accepted new-story summaries; source descriptions can supply function, not facts or sequence.")
        if "selective_streaming_regeneration_gate" in patterns:
            hints.append("For same-type repairs, regenerate only the named new-story chapter or span; do not pull source-neighbor chapters into the protected manuscript state.")
        if "research_citation_boundary_gate" in patterns:
            hints.append("Cited research may guide plausibility and factual boundaries, but the prompt must label it as evidence metadata rather than canon or source prose.")
        if "beta_reader_summary_context_gate" in patterns:
            hints.append("Run beta-reader feedback on the transformed chapter using transformed previous summaries and a declared review style.")
        if "style_vocab_world_card_extraction_gate" in patterns:
            hints.append("Prompt from abstracted style vocabulary and newly created world cards; source world facts and proper nouns remain outside the new-story canon.")
        if "prompt_only_decay_ceiling_gate" in patterns:
            hints.append("For same-type prompts, declare the prompt-only ceiling and require refreshed transformed context before the draft drifts into source-like shortcuts.")
        if "serial_platform_minimum_audit_gate" in patterns:
            hints.append("Ask for serial-platform audit evidence on the transformed draft: loop risk, dialogue ratio, battle logic, AI-tone cleanup, and chapter-hook pressure.")
        if "multi_agent_reject_retry_review_gate" in patterns:
            hints.append("Route transformed drafts through role-separated review so reject/retry evidence is about the new story rather than source resemblance.")
        if "story_bible_context_packet_branch_gate" in patterns:
            hints.append("Build a new-story context packet and branch savepoint before drafting; source packets can inform shape only, not facts.")
        if "memory_augmented_delta_verification_gate" in patterns:
            hints.append("Ask for transformed fact deltas and targeted verification questions before any delta can update the new story bible.")
        if "statistical_style_benchmark_rewrite_gate" in patterns:
            hints.append("Use statistical style presets as quality thresholds while requiring independence checks against copied phrasing and source-scene rhythm.")
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
        if "reader_rating_signal_model" in patterns:
            hints.append("Reader rating and shelf signals can calibrate market feel, but the new story needs independent promise, stakes, cast, and causality.")
        if "review_spoiler_sentiment_corpus" in patterns:
            hints.append("Use review clusters as abstract reader desire and complaint signals; do not reuse review wording or spoiler examples as story facts.")
        if "beta_reader_archetype_panel" in patterns:
            hints.append("Run the transformed draft through beta-reader archetypes for hook, confusion, and turn-page pull after copy-risk checks.")
        if "comp_title_market_positioning" in patterns:
            hints.append("Comp titles guide positioning and audience promise only; rebuild premise, scene order, and hook language from scratch.")
        if "local_reader_experience_editor" in patterns:
            hints.append("Optimize micro-tension and curiosity in the transformed story without copying a source chapter's cliffhanger shape or ending cadence.")
        if "context_pack_preview" in patterns:
            hints.append("The new story's context pack must cite transformed canon only; source deconstruction may appear as craft notes, not facts.")
        if "critic_verifier_loop" in patterns:
            hints.append("Run critic/verifier checks for independence as well as quality before accepting a same-type draft.")
        if "anti_ai_tone_polish" in patterns:
            hints.append("Anti-AI-tone polish should make the new prose more specific, not closer to source phrasing.")
        if "top_down_story_planning" in patterns:
            hints.append("Build a fresh top-down plan hierarchy so the new story is not a chapter-by-chapter route clone.")
        if "snowflake_premise_expansion" in patterns:
            hints.append("Create a new premise chain before outlining; do not reuse the source promise or summary structure as canon.")
        if "outliner_index_cards" in patterns:
            hints.append("Rebuild outline cards around new goals, conflicts, hooks, and dependency order.")
        if "narrative_strand_mapping" in patterns:
            hints.append("Borrow strand function only after replacing fabula, social context, and concrete causality.")
        if "character_depth_interview" in patterns:
            hints.append("Use character-depth interviews to create new internal contradictions, not renamed source psychology.")
        if "human_synopsis_gate" in patterns:
            hints.append("Review the transformed synopsis before prose so same-type writing does not inherit the source chapter-summary route.")
        if "retrieval_guided_span_rewrite" in patterns:
            hints.append("Use retrieval to compare functions and pressure points, then rewrite only transformed spans in the new story state.")
        if "recursive_adaptive_planning" in patterns:
            hints.append("Let adaptive planning revise the new story's task tree instead of following the source workflow order.")
        if "voice_table_polish_axis" in patterns:
            hints.append("Build a new voice table for the transformed cast; source voice axes can guide separation, not wording.")
        if "genre_parameterized_worldbuilding" in patterns:
            hints.append("Transform genre parameters into new factions, locations, stakes, and taboo moves before drafting.")
        if "prose_preflight_voice_calibration" in patterns:
            hints.append("Use voice calibration to make the new prose specific and human without preserving source phrases.")
        if "sourcebook_author_workbench" in patterns:
            hints.append("Build a new sourcebook for the transformed story; sourcebook entries from the reference remain craft notes, not canon.")
        if "contradiction_taxonomy_checker" in patterns:
            hints.append("Run independence checks under the same consistency taxonomy so transformed facts do not drift back toward source facts.")
        if "research_taxonomy_story_map" in patterns:
            hints.append("Use taxonomy categories to choose a method for the new story, not to inherit another project's source list or paper structure.")
        if "agentic_book_planner_pipeline" in patterns:
            hints.append("Recreate planner-role outputs for the transformed story; source Story Bible, plot threads, and chapter outlines are reference evidence only.")
        if "rag_synopsis_spine" in patterns:
            hints.append("Build a transformed synopsis spine first, then retrieve from that new spine instead of from source-book summaries.")
        if "anti_repetition_prompt_rules" in patterns:
            hints.append("Anti-repetition checks should reject both generic loops and source-like repeated beat sequences.")
        if "prompt_recipe_experiment_grid" in patterns:
            hints.append("Evaluate same-type prompt recipes against independence, continuity, and voice before accepting the best candidate.")
        if "narrative_arc_template_control" in patterns:
            hints.append("Select a narrative arc template, then change premise, cast, cause, cost, and payoff so the arc is independent.")
        if "delivery_manuscript_assembly" in patterns:
            hints.append("For same-type creation, rebuild delivery packaging from the transformed chapter list; never reuse source chapter headings or order.")
        if "export_format_fidelity_audit" in patterns:
            hints.append("Export checks should prove transformed outputs remain independent while preserving their own chapter order and headings.")
        if "preview_toc_packaging" in patterns:
            hints.append("Preview and table-of-contents maps should be generated from transformed chapters only, not from source navigation.")
        if "cover_kdp_metadata_boundary" in patterns:
            hints.append("Publication metadata can borrow market promise shape, but titles, cover concepts, blurbs, and keywords must be newly written.")
        if "branching_choice_graph" in patterns:
            hints.append("Carry over interactive choice pressure only as abstract branch design; create new options, consequences, and merge/reject decisions.")
        if "node_dialogue_state_machine" in patterns:
            hints.append("Use node-based dialogue planning for the new cast, with fresh entry conditions, option wording, command hooks, and exit deltas.")
        if "passage_link_navigation_map" in patterns:
            hints.append("Build a new passage/link map from the transformed premise; source passage order and link labels remain analysis evidence only.")
        if "choice_stats_consequence_gate" in patterns:
            hints.append("Define new stat categories and consequence gates so choice mechanics support the new story rather than copying source variables.")
        if "source_text_fingerprint_gate" in patterns:
            hints.append("Run fingerprint overlap checks against source excerpts and rewrite high-overlap windows before accepting same-type prose.")
        if "fuzzy_phrase_similarity_gate" in patterns:
            hints.append("Use fuzzy phrase checks to catch near-copy paraphrases after names and surface labels have been changed.")
        if "diff_span_copy_review" in patterns:
            hints.append("Review source-vs-draft diff spans so semantic cleanup does not hide copied sentence order or set-piece wording.")
        if "minhash_lsh_near_duplicate_gate" in patterns:
            hints.append("Run near-duplicate shingle checks before accepting same-type prose; high-overlap windows need visible rewrite or exception notes.")
        if "simhash_hamming_similarity_gate" in patterns:
            hints.append("Use SimHash/Hamming checks after entity remap and polish so lightly edited source passages cannot pass as new prose.")
        if "semantic_duplicate_cluster_gate" in patterns:
            hints.append("Check whether draft windows cluster with source scenes; if they do, change actor pressure, object, obstacle, and payoff.")
        if "embedding_similarity_independence_gate" in patterns:
            hints.append("The nearest semantic neighbor for a draft should be transformed canon or its own brief, not the source excerpt.")
        if "corpus_leakage_dedup_review_gate" in patterns:
            hints.append("Keep source corpus notes outside generated canon and reject repeated long sequences that suggest source leakage.")
        if "character_quote_attribution_map" in patterns:
            hints.append("Map source quote distribution into new speaker functions, then rewrite aliases, speakers, and dialogue content for the transformed cast.")
        if "readability_pacing_metric_gate" in patterns:
            hints.append("Use readability and sentence-length curves as rhythm guidance while rebuilding chapter events and scene exits.")
        if "lexical_diversity_voice_audit" in patterns:
            hints.append("Carry over only broad lexical diversity range; replace source catchphrases, image clusters, and signature diction.")
        if "stylometric_author_fingerprint_gate" in patterns:
            hints.append("Use stylometric fingerprints as bounded calibration, then verify the new story has its own approved voice profile.")
        if "function_word_syntax_style_gate" in patterns:
            hints.append("Translate function-word and syntax ranges into new narrator/speaker style rules instead of copying the source author's exact rhythm.")
        if "authorship_attribution_similarity_gate" in patterns:
            hints.append("Treat high source-author similarity as a failure signal for same-type drafts, even when the prose sounds fluent.")
        if "style_overfit_regression_gate" in patterns:
            hints.append("Run style-overfit regression after paraphrase and polish passes so source voice leakage cannot survive renamed entities.")
        if "paraphrase_independence_review_gate" in patterns:
            hints.append("Require paraphrase-independence evidence before accepting inspired prose, not only surface renaming or grammar cleanup.")
        if "keyphrase_motif_extraction" in patterns:
            hints.append("Extract source motifs as abstract pressure points, then replace motif keywords with new-story objects, places, and stakes.")
        if "chinese_segmentation_keyword_gate" in patterns:
            hints.append("Rebuild custom dictionaries and keyword profiles for the transformed story so source names and invented terms are not carried over.")
        if "chinese_ner_alias_consistency_gate" in patterns:
            hints.append("Transform Chinese entity clusters by replacing names, aliases, sects, places, and relationship labels before context reuse.")
        if "source_entity_redaction_gate" in patterns:
            hints.append("Redact source-specific entities before same-type drafting; only transformed placeholders or approved continuation names may enter prompts.")
        if "custom_entity_label_inventory" in patterns:
            hints.append("Build custom fiction entity labels for the new story before generation so source factions, artifacts, ranks, powers, and titles are not reused.")
        if "placeholder_alias_consistency_map" in patterns:
            hints.append("Use a stable placeholder map during transformation and resolve replacements into a new alias namespace before prose drafting.")
        if "proper_noun_leakage_review" in patterns:
            hints.append("Run a proper-noun leak check against source blocklists after entity remap and before final same-type acceptance.")
        if "chinese_text_normalization_gate" in patterns:
            hints.append("Normalize only for comparison; regenerate visible orthography and punctuation policy for the new manuscript.")
        if "chinese_error_correction_review_gate" in patterns:
            hints.append("Treat Chinese correction suggestions as local review tasks, not automatic rewrites toward source diction.")
        if "source_format_import_manifest" in patterns:
            hints.append("Transform imported TOC/spine evidence into a new outline structure instead of preserving source chapter order.")
        if "pdf_layout_text_extraction_gate" in patterns:
            hints.append("Use PDF page/layout evidence to understand source pacing, then rebuild section boundaries for the new story.")
        if "ocr_scanned_page_import_gate" in patterns:
            hints.append("Keep OCR uncertainty out of new-story canon; only reviewed source evidence may influence transformation choices.")
        if "document_partition_chapter_detection_gate" in patterns:
            hints.append("Transform source element partitions into new scene/section functions, not copied headings or section boundaries.")
        if "import_provenance_checksum_gate" in patterns:
            hints.append("Carry import provenance as evidence only; transformed drafts need their own lineage and accepted-text artifacts.")
        if "epub_structure_validation_gate" in patterns:
            hints.append("Use EPUB validation as a delivery checklist for the transformed manuscript, not as permission to copy source package structure.")
        if "ebook_accessibility_audit_gate" in patterns:
            hints.append("Keep accessibility requirements stable while regenerating captions, alt text, landmarks, and reading-order notes for the new book.")
        if "front_back_matter_metadata_gate" in patterns:
            hints.append("Rebuild front/back matter and metadata from the transformed book; source titlepage, colophon, and identifiers remain reference evidence only.")
        if "toc_navigation_consistency_gate" in patterns:
            hints.append("Generate TOC and navigation from the transformed outline after independence checks, not from the source EPUB hierarchy.")
        if "agentic_editorial_pipeline_gate" in patterns:
            hints.append("Use editorial roles to separate planning, drafting, review, copy-edit, and compile decisions; do not let a source-analysis role write canon directly.")
        if "chapter_state_archive_ladder" in patterns:
            hints.append("Use a fresh chapter-state archive for the new story and keep source-state snapshots as reference evidence only.")
        if "section_metadata_traceability_gate" in patterns:
            hints.append("Regenerate section metadata for new cast, locations, items, plotlines, beats, and pacing before same-type drafting.")
        if "ai_prose_fingerprint_cluster_gate" in patterns:
            hints.append("Clean AI-prose fingerprints through local revision while preserving transformed-story identity and avoiding source-like cadence.")
        if "author_candidate_canon_confirmation_gate" in patterns:
            hints.append("Keep AI suggestions and source-derived ideas as candidates until the transformed story records preview, confirmation, apply status, and rollback path.")
        if "progressive_spoiler_context_window_gate" in patterns:
            hints.append("Choose context by transformed chapter stage so source late-book spoilers, ending routes, and payoff timing cannot steer early chapters.")
        if "chapter_control_card_writeback_gate" in patterns:
            hints.append("Create chapter control cards from transformed goals, line pressure, debt return, conflict, title intent, and hook before drafting.")
        if "trace_replay_revision_workspace_gate" in patterns:
            hints.append("Keep source-analysis traces separate from transformed-story workbench decisions, selected context, reviewer findings, and accepted revision evidence.")
        if "relationship_graph_global_replace_gate" in patterns:
            hints.append("Regenerate relationship graphs and global replacement previews from transformed ids before any same-type chapter accepts graph-derived context.")
        if "bookrun_audit_trail_gate" in patterns:
            hints.append("Use BookRun-style audit trails for process replay, but rebuild blueprint, judge criteria, repair decisions, and export manifest for the transformed story.")
        if "provider_budget_smoke_gate" in patterns:
            hints.append("Set a transformed-story provider budget and smoke scope before experiments; do not spend retries on source-like drafts.")
        if "sidecar_memory_profile_boundary" in patterns:
            hints.append("Create a new sidecar/vector/graph namespace for transformed canon; source memory profiles remain read-only analysis evidence.")
        if "outline_checkpoint_milestone_gate" in patterns:
            hints.append("Create new outline checkpoints and milestones from transformed stakes, relationship pressure, and payoff route before drafting.")
        if "language_localization_style_profile_gate" in patterns:
            hints.append("Build localized style profiles for the new cast and setting; source language rules may guide review categories, not voice cloning.")
        if "progressive_disclosure_skill_protocol_gate" in patterns:
            hints.append("Use progressive protocol loading to keep prompts small while ensuring transformed-story knowledge files are bound before generation.")
        if "anti_slop_rulepack_triage_gate" in patterns:
            hints.append("Run anti-slop rulepack triage as local prose cleanup after independence checks so specificity rises without copying source cadence.")
        if "user_modifier_project_blueprint_gate" in patterns:
            hints.append("Define a new modifier blueprint for the transformed project before planning; source dashboards and examples are process references only.")
        if "portable_canon_skill_runtime_gate" in patterns:
            hints.append("Create fresh story assets, frontmatter, canon ids, workflow state, and artifact indexes for the transformed book.")
        if "staged_outline_chunk_window_gate" in patterns:
            hints.append("Plan the transformed outline in stage/chapter chunks and keep only current plus adjacent context detailed during drafting.")
        if "wiki_canon_graph_lint_gate" in patterns:
            hints.append("Build a new story-bible wiki and relationship graph from transformed facts before using wiki queries in drafting.")
        if "plan_draft_log_verify_loop_gate" in patterns:
            hints.append("Apply Plan -> Draft -> Log -> Verify to transformed chapters, not to replay the source chapter workflow.")
        if "mcp_scene_index_revision_boundary" in patterns:
            hints.append("Use scene-index revision boundaries on transformed scene ids with explicit confirmation and reversible diff evidence.")
        if "verbalized_sampling_diversity_wiki_gate" in patterns:
            hints.append("Use diversity sampling to escape source-like first ideas; auto-file accepted variants into the transformed writer wiki.")
        if "literary_event_entity_annotation_gate" in patterns:
            hints.append("Transform literary entity/event annotations into new roles, event functions, and participant slots before drafting.")
        if "narrative_event_evolution_graph_gate" in patterns:
            hints.append("Remap event chains by changing causes, blockers, decision points, and payoff edges instead of preserving source chronology.")
        if "sentiment_arc_emotion_trajectory_gate" in patterns:
            hints.append("Use emotion arcs as pressure-shape evidence only; rebuild turning points, valence shifts, and character triggers for the new story.")
        if "cross_context_coreference_gate" in patterns:
            hints.append("Rebuild mention clusters around the transformed cast so source entities and events cannot leak across context packs.")
        if "character_interaction_network_gate" in patterns:
            hints.append("Transform character networks by changing centrality, alliance, conflict polarity, and relationship timing before prose expansion.")
        if "semantic_chunk_boundary_map" in patterns:
            hints.append("Use source chunk boundaries as analysis evidence only; rebuild transformed chapter chunks around the new event chain.")
        if "chapter_summary_anchor_gate" in patterns:
            hints.append("Build new summary anchors from transformed accepted chapters before using summaries as drafting context.")
        if "topic_drift_map" in patterns:
            hints.append("Use topic drift maps to check new-story focus, but change source topic order, salience, and payoff sequence.")
        if "context_faithfulness_eval_gate" in patterns:
            hints.append("Score same-type drafts for faithfulness against transformed canon only; source-analysis notes cannot count as supporting evidence.")
        if "retrieval_trace_observability_gate" in patterns:
            hints.append("Keep retrieval traces inspectable so reviewers can see whether the prompt used transformed canon or source-analysis material.")
        if "prompt_regression_eval_suite" in patterns:
            hints.append("Use golden prompt cases to test context packing, copy-risk rejection, and canon write-back before changing same-type prompts.")
        if "nrd_task_tree_pipeline" in patterns:
            hints.append("Use the NRD task tree to regenerate arcs, chapters, scenes, and revision passes for the transformed premise.")
        if "story_structure_rag_planning" in patterns:
            hints.append("Use structure scaffolds like Hero's Journey or Freytag as abstract pressure maps, not as source event order.")
        if "story_contract_commit_chain" in patterns:
            hints.append("For same-type creation, create a new contract and commit chain; source contracts may guide artifact shape only.")
        if "fact_snapshot_delta_gate" in patterns:
            hints.append("Transform fact snapshot dimensions and delta gates into new-story state fields before drafting.")
        if "foreshadowing_debt_budget" in patterns:
            hints.append("Rebuild foreshadowing debt from new hooks and payoff windows instead of copying source mysteries.")
        if "reader_retention_review_gate" in patterns:
            hints.append("Map reader-retention pressure to new hooks, pleasure points, rhythm, and cliffhangers; do not reuse source set pieces.")
        if "draft_stage_revision_ladder" in patterns:
            hints.append("Use Draft A/B/C stages to improve transformed prose while preserving independence and canon boundaries.")
        if "rolling_summary_context_trim" in patterns:
            hints.append("Build rolling summaries from transformed accepted chapters only; source summaries remain craft references.")
        if "pairwise_story_comparison_ranking" in patterns:
            hints.append("Compare transformed variants against the same new-story brief; do not choose a variant because it is closer to the source.")
        if "multidimensional_quality_rubric" in patterns:
            hints.append("Apply the quality rubric to transformed-story prose and require independence evidence alongside quality improvements.")
        if "story_theory_beat_evaluation" in patterns:
            hints.append("Map source beat functions to new beat functions, then change characters, causes, costs, and outcomes.")
        if "constraint_specificity_creativity_benchmark" in patterns:
            hints.append("Use specific constraints for the new story's premise, not for recreating source event details.")
        if "style_axis_diversity_fingerprint" in patterns:
            hints.append("Transform style axes into new voice, rhythm, POV, pacing, imagery, and closure targets without copying phrases.")
        if "event_outline_history_compression" in patterns:
            hints.append("Build a fresh event outline and compressed history for the transformed premise before drafting.")
        if "agentic_story_world_simulation" in patterns:
            hints.append("Simulate transformed character choices inside the new world state; source character behavior is only abstract craft evidence.")
        if "book_memory_bank_context_lattice" in patterns:
            hints.append("Convert source deconstruction into separate memory-bank notes: craft observations, transformed canon, active context, and progress are never mixed.")
        if "spec_driven_fiction_scene_tasks" in patterns:
            hints.append("Create transformed scene tasks from the new constitution/story bible; source scene tasks may guide format only, not content or order.")
        if "toc_aware_source_deconstruction" in patterns:
            hints.append("Use TOC-aware source summaries as analysis artifacts, then rebuild the new story's chapter hierarchy around new promises and payoffs.")
        if "two_pass_context_glossary_pipeline" in patterns:
            hints.append("Run an analysis pass that extracts source term functions, then create a new glossary for transformed names, places, rules, and motifs.")
        if "inline_author_edit_markup_versioning" in patterns:
            hints.append("Use inline author notes to control new POV, timeline, mood, and active threads; edit notes should resolve into independent prose.")
        if "causal_dramatica_agent_pipeline" in patterns:
            hints.append("Rebuild causal threads for the transformed story; source Dramatica-style roles may guide pressure only, not event order.")
        if "capture_distillation_production_gate" in patterns:
            hints.append("Convert source captures into distilled craft packets first; production prompts should never ingest raw source notes as canon.")
        if "skill_orchestrated_chinese_novel_workflow" in patterns:
            hints.append("Use Chinese web-novel stage skills as workflow shape only; generate new world rules, character arcs, and chapter hooks.")
        if "langgraph_story_state_machine" in patterns:
            hints.append("Create a separate transformed-story state machine so source-analysis states cannot be resumed as new-story canon.")
        if "story_daemon_evolution_loop" in patterns:
            hints.append("Let autonomous evolution propose alternatives, but accept only changes that pass transformed-canon and copy-risk gates.")
        if "local_rag_writing_ide_gate" in patterns:
            hints.append("Use RAG retrieval to select abstract reference evidence and new-story canon separately; never let source chunks masquerade as transformed canon.")
        if "canon_drift_continuity_qa_gate" in patterns:
            hints.append("Run canon-drift QA on the transformed story itself so copied source consistency is not mistaken for valid new-story continuity.")
        if "patch_replay_manuscript_state_gate" in patterns:
            hints.append("Record same-type transformations as patches against the new outline so source-analysis edits cannot be replayed into the new manuscript.")
        if "microkernel_skill_plugin_isolation_gate" in patterns:
            hints.append("Let skills/plugins contribute stage outputs only after replacing source entities, causality, and glossary with new-story equivalents.")
        if "interactive_reader_writer_loop_gate" in patterns:
            hints.append("Treat interactive reader choices as new-story author inputs, not as permission to preserve source scene route or event order.")
        if "abstract_style_learning_skill_gate" in patterns:
            hints.append("Use style learning for technique axes only; same-type prompts must exclude source sample phrasing, proper nouns, and plot facts.")
        if "impromptu_thread_pool_chapter_gate" in patterns:
            hints.append("For same-type drafting, rebuild the open-thread pool from the transformed story's own hooks instead of carrying source thread statuses.")
        if "offline_inspiration_bank_style_gate" in patterns:
            hints.append("Use inspiration-bank items as labeled craft references only; same-type prompts must not treat local source files as canon or reusable prose.")
        if "atelier_phase_pipeline_gate" in patterns:
            hints.append("Use the atelier phase order as process scaffolding while rebuilding beat tree, hook targets, and role briefs for the new story.")
        if "book_mining_genesis_automation_gate" in patterns:
            hints.append("Use book-mined patterns only after converting them into new canon-seed fields with new cast, engine, stakes, and payoff owners.")
        if "multi_book_autopilot_studio_gate" in patterns:
            hints.append("Treat a same-type project as a new book profile; never reuse the source book's session state, autopilot counters, or context files.")
        if "longrun_commit_projection_health_gate" in patterns:
            hints.append("Build new chapter commits and read-model projections for the transformed story instead of replaying source commit state.")
        if "fresh_context_chapter_iteration_gate" in patterns:
            hints.append("Create a new manifest and progress log for the transformed book before any fresh-context chapter loop runs.")
        if "inline_human_machine_coauthoring_gate" in patterns:
            hints.append("Create transformed inline revision spans with new-story text and author decision points; do not reuse source edit spans as draft material.")
        if "hierarchical_orchestrator_generation_gate" in patterns:
            hints.append("Transform the hierarchy first: new volume goals, arc pressure, chapter slots, and scene tasks must exist before prose generation.")
        if "batch_continuation_progress_queue_gate" in patterns:
            hints.append("Transform batch queues into new chapter jobs with fresh progress state instead of copying source job order or retry history.")
        if "homogeneity_prompt_variation_gate" in patterns:
            hints.append("Transform adjacent chapters by changing variation axes, not by paraphrasing the same source-like chapter template.")
        if "local_author_data_boundary_gate" in patterns:
            hints.append("Transform local source files into boundary-labeled metadata or author-approved notes before any same-type prompt can cite them.")
        if "temporal_canon_context_graph" in patterns:
            hints.append("Build a new temporal graph for the transformed story; source graph episodes may guide abstraction only.")
        if "long_term_author_preference_memory" in patterns:
            hints.append("Use author preference memory to preserve the user's desired feel while keeping source analysis outside project memory.")
        if "community_graph_source_deconstruction" in patterns:
            hints.append("Transform source entity communities into new cast, faction, theme, and conflict communities before drafting.")
        if "dual_level_graph_vector_retrieval" in patterns:
            hints.append("Retrieve source-like craft references and transformed canon through separate graph/vector contexts so they cannot merge.")
        if "schema_guided_graph_extraction" in patterns:
            hints.append("Create a transformed graph schema before extraction so source node labels and relationship names do not become new canon.")
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
        if "mode_contract_generation_gate" in patterns:
            hints.append("Transform each output mode by changing mode inputs first: audience, POV, ending target, conflict source, and minimum completeness threshold.")
        if "source_study_method_bank_isolation_gate" in patterns:
            hints.append("Transform source-study findings into a new method bank entry before any chapter plan can cite them.")
        if "plot_dependency_graph" in patterns:
            hints.append("Rebuild dependency edges from new promises and clues; a source setup can inspire a function but not a factual dependency.")
        if "setup_payoff_tracking" in patterns:
            hints.append("Transform setup/payoff pairs by changing the promise, cost, and payoff consequence.")
        if "alternate_timeline_branching" in patterns:
            hints.append("Use branch divergence as a design tool for independent causality, not as a renamed source route.")
        if "trend_deconstruction_pipeline" in patterns:
            hints.append("Transform trope modules by changing desire, obstacle, cost, payoff timing, and reader-facing promise.")
        if "reader_rating_signal_model" in patterns:
            hints.append("Convert shelf/tag signals into a new expectation profile before building characters, setting, and conflict.")
        if "review_spoiler_sentiment_corpus" in patterns:
            hints.append("Rewrite review-derived complaints into abstract revision goals; keep spoilers and quoted review text out of draft context.")
        if "beta_reader_archetype_panel" in patterns:
            hints.append("Transform beta-reader objections into chapter-specific fixes rather than importing the reader persona's preferred plot solution.")
        if "comp_title_market_positioning" in patterns:
            hints.append("Map each comp-title similarity to a transformed difference: new protagonist pressure, new obstacle, new setting, and new payoff cost.")
        if "local_reader_experience_editor" in patterns:
            hints.append("Rebuild hooks and cliffhangers from the new chapter's active conflict, not from source set-piece timing.")
        if "top_down_story_planning" in patterns:
            hints.append("Regenerate book spec, act plan, chapter plan, and scene list from the transformed premise before drafting prose.")
        if "context_pack_preview" in patterns:
            hints.append("Build a context pack from the transformed story state; do not retrieve source events as if they were reusable canon.")
        if "snowflake_premise_expansion" in patterns:
            hints.append("Transform from the top of the premise chain downward so lower-level scenes inherit a new core promise.")
        if "character_depth_interview" in patterns:
            hints.append("Re-answer depth questions for each transformed character before mapping any relationship beat.")
        if "human_synopsis_gate" in patterns:
            hints.append("Transform synopsis and chapter summaries first, then draft from accepted transformed summaries only.")
        if "retrieval_guided_span_rewrite" in patterns:
            hints.append("When borrowing a local scene function, identify the new-story span and update its outline delta instead of rewriting source-like neighbors.")
        if "schema_validated_state_delta" in patterns:
            hints.append("Validate transformed state deltas so copied source event labels cannot enter canon through structured fields.")
        if "beat_strand_framework" in patterns:
            hints.append("Transform strand functions and convergence pressure; do not preserve the source beat labels or sequence.")
        if "frontmatter_story_schema" in patterns:
            hints.append("Create new frontmatter/story-schema values instead of carrying source promises, questions, or scene state forward.")
        if "semantic_long_context_search" in patterns:
            hints.append("Semantic hits from source works must be converted into abstract craft pressure before any new-story context pack is built.")
        if "humanization_stylometry_levers" in patterns:
            hints.append("Stylometry polish should change surface rhythm, not preserve distinctive source phrasing or scene wording.")
        if "novel_to_multimodal_pipeline" in patterns:
            hints.append("Transform adaptation outputs at script/scene/storyboard function level; do not preserve source shot or set-piece order.")
        if "entity_to_visual_asset_pipeline" in patterns:
            hints.append("Regenerate visual-asset refs from transformed entities so source character designs, props, and locations do not leak into the new canon.")
        if "agentic_book_planner_pipeline" in patterns:
            hints.append("Transform Story Bible, character, plot-thread, and chapter-outline artifacts before any Writer role drafts prose.")
        if "rag_synopsis_spine" in patterns:
            hints.append("Rewrite the synopsis spine around the new premise and only then use it for retrieval-guided same-type drafting.")
        if "narrative_arc_template_control" in patterns:
            hints.append("Transform arc controls into new scene pressure, reveal timing, and payoff cost instead of retaining source beat order.")
        if "nrd_task_tree_pipeline" in patterns:
            hints.append("Rebuild the NRD task tree from new arcs to scenes so revision passes repair the new story, not the source workflow.")
        if "story_structure_rag_planning" in patterns:
            hints.append("Map structure-RAG samples to abstract beat purpose, then replace character, setting, event, and language before drafting.")
        if "story_contract_commit_chain" in patterns:
            hints.append("Transform the commit chain by changing the contract premise, accepted-fact categories, and chapter-causality ledger.")
        if "fact_snapshot_delta_gate" in patterns:
            hints.append("Define new fact snapshots and change declarations so transformed canon cannot inherit source labels through state fields.")
        if "foreshadowing_debt_budget" in patterns:
            hints.append("Create new foreshadowing debts with different clues, promises, costs, and payoff timing.")
        if "reader_retention_review_gate" in patterns:
            hints.append("Transform retention mechanics into new chapter-end pull, emotional pressure, and reader promise.")
        if "draft_stage_revision_ladder" in patterns:
            hints.append("Run staged revision on the transformed chapter, not on source text or source-like paraphrase.")
        if "rolling_summary_context_trim" in patterns:
            hints.append("Rewrite rolling summaries around the transformed story's accepted events before using them for continuation.")
        if "pairwise_story_comparison_ranking" in patterns:
            hints.append("Create candidate variants from the transformed brief and keep the winner for new-story reasons, not source similarity.")
        if "multidimensional_quality_rubric" in patterns:
            hints.append("Transform rubric failures into revision tasks that preserve new-story facts and reject copied source dependencies.")
        if "story_theory_beat_evaluation" in patterns:
            hints.append("Rebuild beat tasks around the transformed arc so minimal-change repair does not restore source causality.")
        if "constraint_specificity_creativity_benchmark" in patterns:
            hints.append("Raise constraint specificity with new names, settings, objects, costs, and ending targets rather than source details.")
        if "style_axis_diversity_fingerprint" in patterns:
            hints.append("Use style-axis fingerprints to shape surface craft while changing concrete motifs, metaphors, and dialogue tics.")
        if "event_outline_history_compression" in patterns:
            hints.append("Compress only the transformed event history; source event outlines remain comparison material, not context.")
        if "agentic_story_world_simulation" in patterns:
            hints.append("Transform the agent world by changing roles, social graph, environment rules, and conflict incentives before simulation.")
        if "agentic_editorial_pipeline_gate" in patterns:
            hints.append("Transform editorial handoffs by requiring each role to operate on new-story artifacts and accepted reviewer decisions.")
        if "chapter_state_archive_ladder" in patterns:
            hints.append("Transform chapter state by creating a new bible/state/archive ladder before generating or revising chapters.")
        if "section_metadata_traceability_gate" in patterns:
            hints.append("Transform section metadata into new cast, location, item, plotline, beat, pacing, and status fields.")
        if "ai_prose_fingerprint_cluster_gate" in patterns:
            hints.append("Transform prose-fingerprint findings into local revision targets instead of copying source sentence rhythm.")
        if "author_candidate_canon_confirmation_gate" in patterns:
            hints.append("Transform candidate canon decisions by assigning new-story candidate ids, reviewer decisions, and rollback notes before updating bible, plan, or chapter state.")
        if "progressive_spoiler_context_window_gate" in patterns:
            hints.append("Transform spoiler windows by changing reveal range, future-context budget, and payoff route for the new story before retrieval is allowed.")
        if "chapter_control_card_writeback_gate" in patterns:
            hints.append("Transform chapter control cards by rewriting must-change beats, line pressure, emotional debt, title intent, and next-chapter handoff for the new outline.")
        if "trace_replay_revision_workspace_gate" in patterns:
            hints.append("Transform revision traces into new-story evidence: blueprint, selected context, rewrite direction, reviewer findings, impact scope, and accepted text version.")
        if "relationship_graph_global_replace_gate" in patterns:
            hints.append("Transform relationship graphs and replacement maps by changing ids, aliases, edge labels, centrality, timing, and affected canon surfaces.")
        if "bookrun_audit_trail_gate" in patterns:
            hints.append("Transform BookRun artifacts by regenerating blueprint, judge rubric, repair log, acceptance manifest, and export audit for the new story.")
        if "provider_budget_smoke_gate" in patterns:
            hints.append("Transform provider profiles into budgeted experiment lanes with explicit dry-run, smoke, and real-generation boundaries.")
        if "sidecar_memory_profile_boundary" in patterns:
            hints.append("Transform memory architecture by assigning new graph/vector namespaces, sidecar permissions, and profile-specific read/write limits.")
        if "outline_checkpoint_milestone_gate" in patterns:
            hints.append("Transform milestones by changing checkpoint goals, chapter dependencies, causal order, and rollback points.")
        if "language_localization_style_profile_gate" in patterns:
            hints.append("Transform localization rules into new glossary, unit, honorific, punctuation, and speaker-register decisions.")
        if "progressive_disclosure_skill_protocol_gate" in patterns:
            hints.append("Transform protocol routing into project-local steps; external skill files remain reference patterns, not imported prompts.")
        if "anti_slop_rulepack_triage_gate" in patterns:
            hints.append("Transform prose lint findings into revision tasks that preserve character voice and reject generic AI phrasing.")
        if "user_modifier_project_blueprint_gate" in patterns:
            hints.append("Transform project modifiers into a fresh blueprint with new genre mix, scope, POV, setting, tone, and chapter targets.")
        if "portable_canon_skill_runtime_gate" in patterns:
            hints.append("Transform canon runtime by assigning new story asset paths, frontmatter ids, canon JSON keys, workflow state, and artifact lineage.")
        if "staged_outline_chunk_window_gate" in patterns:
            hints.append("Transform staged outlines by changing setup chunks, adjacent-window policy, chapter-range revision scope, and resume checkpoints.")
        if "wiki_canon_graph_lint_gate" in patterns:
            hints.append("Transform wiki/graph material by rebuilding pages, graph nodes, lint rules, and continuity queries around new facts.")
        if "plan_draft_log_verify_loop_gate" in patterns:
            hints.append("Transform the chapter loop by creating new plan logs, scene logs, thread updates, glossary deltas, and verify criteria.")
        if "mcp_scene_index_revision_boundary" in patterns:
            hints.append("Transform scene indexes by creating new scene ids, metadata envelopes, edit confirmations, diff records, and review bundles.")
        if "verbalized_sampling_diversity_wiki_gate" in patterns:
            hints.append("Transform diversity samples by selecting variants that depart from source premise, cast, scene order, and voice before wiki filing.")
        if "delivery_manuscript_assembly" in patterns:
            hints.append("Transform final packaging by rebuilding chapter titles, sequence, acceptance manifest, and output metadata from the new story.")
        if "export_format_fidelity_audit" in patterns:
            hints.append("Verify export fidelity against the transformed manuscript rather than matching the source layout or chapter title cadence.")
        if "preview_toc_packaging" in patterns:
            hints.append("Regenerate preview navigation and table of contents from the transformed outline after copy-risk checks.")
        if "cover_kdp_metadata_boundary" in patterns:
            hints.append("Create publication metadata from the transformed market position; source cover or KDP specs remain format examples only.")
        if "branching_choice_graph" in patterns:
            hints.append("Transform branch edges by changing decision cause, option intent, consequence scope, and merge policy before drafting.")
        if "node_dialogue_state_machine" in patterns:
            hints.append("Transform dialogue nodes around new speaker states and new exit deltas; do not preserve source line/order scaffolds.")
        if "passage_link_navigation_map" in patterns:
            hints.append("Transform navigation by rebuilding reachable paths, hidden gates, and dead-end checks around the new story topology.")
        if "choice_stats_consequence_gate" in patterns:
            hints.append("Transform stat consequences by changing the tracked values, trigger thresholds, delayed payoff, and achievement labels.")
        if "source_text_fingerprint_gate" in patterns:
            hints.append("Transform or discard any draft window whose fingerprint overlap remains close to source text after entity remapping.")
        if "fuzzy_phrase_similarity_gate" in patterns:
            hints.append("Change image clusters, objects, stakes, and causal wording until fuzzy phrase similarity drops below the review threshold.")
        if "diff_span_copy_review" in patterns:
            hints.append("Use copied-span review to drive targeted rewrites while preserving only abstract craft function.")
        if "minhash_lsh_near_duplicate_gate" in patterns:
            hints.append("Transform shingles by changing event order, object set, scene exits, and causal phrasing before prose expansion.")
        if "simhash_hamming_similarity_gate" in patterns:
            hints.append("Transform lightly similar hash windows by changing structure as well as wording; name replacement alone is insufficient.")
        if "semantic_duplicate_cluster_gate" in patterns:
            hints.append("Transform semantic clusters into new scene functions, then verify source scenes are no longer the closest cluster center.")
        if "embedding_similarity_independence_gate" in patterns:
            hints.append("Transform embedding-neighbor evidence into concrete deltas: new protagonist goal, blocker, cost, clue, and consequence.")
        if "corpus_leakage_dedup_review_gate" in patterns:
            hints.append("Transform source corpus examples into separate craft constraints so no raw source sequence enters draft context.")
        if "character_quote_attribution_map" in patterns:
            hints.append("Transform quote attribution by assigning new speakers, aliases, relationship pressure, and dialogue goals before drafting.")
        if "readability_pacing_metric_gate" in patterns:
            hints.append("Transform pacing metrics into a new readability curve for the new chapter sequence, not a source chapter-order clone.")
        if "prose_lint_style_rule_gate" in patterns:
            hints.append("Transform source prose-rule findings into new-book house style rules; do not inherit source lint exceptions, catchphrases, or cadence.")
        if "grammar_spelling_copyedit_gate" in patterns:
            hints.append("Rebuild grammar and copyedit exceptions around the new cast, invented terms, dialogue register, and genre vocabulary.")
        if "copyedit_diagnostic_triage_queue" in patterns:
            hints.append("Triage copyedit diagnostics as local revision tasks; source-derived diagnostics are evidence, not final wording.")
        if "lexical_diversity_voice_audit" in patterns:
            hints.append("Transform lexical voice baselines into new narrator and speaker vocabularies before prose expansion.")
        if "stylometric_author_fingerprint_gate" in patterns:
            hints.append("Transform style fingerprints by creating a new profile id, feature ranges, and approved exceptions for the new narrator and cast.")
        if "function_word_syntax_style_gate" in patterns:
            hints.append("Transform function-word, punctuation, and syntax features into local house-style ranges before drafting.")
        if "authorship_attribution_similarity_gate" in patterns:
            hints.append("Transform attribution checks into distance thresholds that prefer the new style baseline over the source author baseline.")
        if "style_overfit_regression_gate" in patterns:
            hints.append("Transform style-change test windows into regression fixtures that catch source voice leakage after every major prompt change.")
        if "paraphrase_independence_review_gate" in patterns:
            hints.append("Transform style-transfer prompts by separating allowed abstract voice goals from blocked phrase families, tics, and scene-order cues.")
        if "keyphrase_motif_extraction" in patterns:
            hints.append("Transform extracted motifs by changing the concrete keywords, symbolic objects, and payoff stakes.")
        if "chinese_segmentation_keyword_gate" in patterns:
            hints.append("Transform segmentation dictionaries before generating or retrieving context, especially names, skills, sects, places, and invented compounds.")
        if "chinese_ner_alias_consistency_gate" in patterns:
            hints.append("Transform entity aliases and title systems before any same-type draft becomes canon.")
        if "source_entity_redaction_gate" in patterns:
            hints.append("Transform source entity detections into placeholders first, then create fresh names, places, factions, artifacts, powers, and titles.")
        if "custom_entity_label_inventory" in patterns:
            hints.append("Transform custom entity labels into a new inventory and require every copied source label to be replaced or explicitly allowed.")
        if "placeholder_alias_consistency_map" in patterns:
            hints.append("Transform placeholder ids into a consistent new alias namespace; do not leave mixed source aliases and new aliases in one context pack.")
        if "proper_noun_leakage_review" in patterns:
            hints.append("Transform proper-noun review findings into concrete renames, allowlist notes, or blocked draft sections.")
        if "chinese_text_normalization_gate" in patterns:
            hints.append("Transform normalization policy into a new manuscript style guide instead of using source orthography as default.")
        if "chinese_error_correction_review_gate" in patterns:
            hints.append("Transform correction exceptions around the new cast, dialect, invented terms, and genre vocabulary.")
        if "source_format_import_manifest" in patterns:
            hints.append("Transform source import manifests by changing TOC hierarchy, chapter grouping, metadata use, and skipped-section policy.")
        if "pdf_layout_text_extraction_gate" in patterns:
            hints.append("Transform layout-derived pacing into new scene density; source page spans are not outline anchors.")
        if "ocr_scanned_page_import_gate" in patterns:
            hints.append("Transform OCR-derived uncertainty into review tasks, not generation context.")
        if "document_partition_chapter_detection_gate" in patterns:
            hints.append("Transform document element sequences into new chapter functions before drafting.")
        if "import_provenance_checksum_gate" in patterns:
            hints.append("Transform provenance links so source artifacts never masquerade as accepted new-story chapters.")
        if "epub_structure_validation_gate" in patterns:
            hints.append("Transform EPUB structure expectations into new validation criteria tied to the transformed chapter list and export target.")
        if "ebook_accessibility_audit_gate" in patterns:
            hints.append("Transform accessibility notes into reader-facing fixes for the new manuscript, with source-specific media and captions replaced.")
        if "front_back_matter_metadata_gate" in patterns:
            hints.append("Transform publication metadata and front/back matter at the book level before final packaging, not during prose generation.")
        if "toc_navigation_consistency_gate" in patterns:
            hints.append("Transform navigation by aligning the new outline, accepted headings, spine order, and preview links.")
        if "literary_event_entity_annotation_gate" in patterns:
            hints.append("Transform annotation schemas by replacing source event labels, participant roles, and mention evidence with new-story equivalents.")
        if "narrative_event_evolution_graph_gate" in patterns:
            hints.append("Transform event-evolution graphs by altering edge type, event order, actor intent, and consequence scope.")
        if "sentiment_arc_emotion_trajectory_gate" in patterns:
            hints.append("Transform emotion trajectories by changing who feels the shift, why it turns, and which scene pays it off.")
        if "cross_context_coreference_gate" in patterns:
            hints.append("Transform coreference ledgers so old source aliases and event mentions never resolve to new-story entities.")
        if "character_interaction_network_gate" in patterns:
            hints.append("Transform relationship graphs by changing interaction frequency, polarity, faction membership, and bridge characters.")
        if "semantic_chunk_boundary_map" in patterns:
            hints.append("Transform chunk boundaries by changing chapter segmentation, included evidence, and transition logic.")
        if "chapter_summary_anchor_gate" in patterns:
            hints.append("Transform summary anchors by selecting new representative events and sentences from the new story state.")
        if "topic_drift_map" in patterns:
            hints.append("Transform topic drift by changing topic sequence, cluster labels, and subplot emphasis before drafting.")
        if "context_faithfulness_eval_gate" in patterns:
            hints.append("Transform faithfulness checks by changing the supporting canon evidence set and expected grounded facts.")
        if "retrieval_trace_observability_gate" in patterns:
            hints.append("Transform retrieval traces by changing selected evidence, omission reasons, and generation spans for the new story.")
        if "prompt_regression_eval_suite" in patterns:
            hints.append("Transform prompt regression cases by using new-story fixtures and expected independence failures.")
        if "agentwrite_plan_write_pipeline" in patterns:
            hints.append("Transform plan-write stages by rebuilding the plan segments, section goals, and write-stage context around the new story.")
        if "long_output_length_quality_ruler" in patterns:
            hints.append("Transform long-output length targets around the new outline's rhythm instead of matching source chapter or section lengths.")
        if "long_context_reward_dimension_gate" in patterns:
            hints.append("Transform reward checks so helpfulness, logicality, faithfulness, and completeness judge only new-story requirements.")
        if "instance_specific_writing_criteria_gate" in patterns:
            hints.append("Transform instance-specific criteria into new-story requirements before drafting; do not reuse source facts as criteria.")
        if "material_grounded_query_refinement" in patterns:
            hints.append("Transform material requirements by pruning source-only evidence and rebuilding the useful constraint set for the new story.")
        if "hybrid_rubric_pairwise_elo_judge" in patterns:
            hints.append("Transform pairwise judging into comparisons among new-story draft variants, not source resemblance versus transformed prose.")
        if "judge_bias_mitigation_check" in patterns:
            hints.append("Transform judge-bias checks so length, position, verbosity, and ornate prose cannot mask source-copy or canon failures.")
        if "plan_reflect_character_chapter_pipeline" in patterns:
            hints.append("Transform the brainstorm-plan-reflect-character-chapter chain around the new premise and new cast before chapter writing.")
        if "human_story_metric_panel" in patterns:
            hints.append("Transform reader-facing metric axes into new-story targets for relevance, coherence, empathy, surprise, engagement, and complexity.")
        if "hierarchical_cowriting_story_scaffold" in patterns:
            hints.append("Transform the logline, character, plot-point, location, and dialogue layers before drafting any new prose.")
        if "human_coauthor_edit_boundary" in patterns:
            hints.append("Transform co-writing output through explicit edit decisions instead of accepting source-like generated material as final.")
        if "recursive_reprompt_revision_loop" in patterns:
            hints.append("Transform recursive revision stages so plan, draft, rewrite, and edit all operate on new-story canon and goals.")
        if "reranker_guided_candidate_selection" in patterns:
            hints.append("Transform candidate selection by scoring relevance and coherence against the new plan rather than closeness to source passages.")
        if "character_dialogue_persona_memory" in patterns:
            hints.append("Transform persona memory into new dialogue evidence, role pressures, and voice boundaries before writing lines.")
        if "event_to_sentence_realization_trace" in patterns:
            hints.append("Transform plot events before event-to-sentence expansion so realized sentences do not follow source event order.")
        if "entity_memory_slotfill_grounding" in patterns:
            hints.append("Transform entity-memory slots by replacing source entities with new-story names, roles, locations, and objects.")
        if "book_memory_bank_context_lattice" in patterns:
            hints.append("Transform source memory-bank fields into new-story project brief, structure, characters, style, active context, and progress files.")
        if "spec_driven_fiction_scene_tasks" in patterns:
            hints.append("Transform story-bible constitution, scene tasks, POV schedule, glossary, and quality gates before prose generation.")
        if "toc_aware_source_deconstruction" in patterns:
            hints.append("Transform TOC-derived summaries into new chapter functions, not a reused source section hierarchy.")
        if "two_pass_context_glossary_pipeline" in patterns:
            hints.append("Transform proper-noun and term glossaries into new names, labels, rules, and motifs before generation uses them.")
        if "inline_author_edit_markup_versioning" in patterns:
            hints.append("Transform inline notes into new-story POV/timeline/revision tasks; remove edit markers once the independent revision is accepted.")
        if "causal_dramatica_agent_pipeline" in patterns:
            hints.append("Transform causal chains by changing drive, conflict source, decision pressure, consequence, and payoff owner.")
        if "capture_distillation_production_gate" in patterns:
            hints.append("Transform captured source notes into distilled function cards before any production draft can use them.")
        if "skill_orchestrated_chinese_novel_workflow" in patterns:
            hints.append("Transform skill-stage outputs into new web-novel artifacts with independent names, sects, abilities, hooks, and arc pressure.")
        if "langgraph_story_state_machine" in patterns:
            hints.append("Transform state-machine nodes and transitions so resumed checkpoints belong to the new story, not the source analysis.")
        if "story_daemon_evolution_loop" in patterns:
            hints.append("Transform autonomous evolution proposals into explicit author-review deltas before canon write-back.")
        if "local_rag_writing_ide_gate" in patterns:
            hints.append("Transform retrieval contexts by separating source-material chunks from new canon and by rewriting retrieved inspiration into independent scene constraints.")
        if "canon_drift_continuity_qa_gate" in patterns:
            hints.append("Transform source continuity rules into a new story bible before QA; copied canon facts are failures unless this is true continuation.")
        if "patch_replay_manuscript_state_gate" in patterns:
            hints.append("Transform patch chains by creating new outline and patch ids; do not replay source manuscript patches under renamed files.")
        if "microkernel_skill_plugin_isolation_gate" in patterns:
            hints.append("Transform plugin stage contracts so source skills provide format only while new-story plugins own all names, facts, and event transitions.")
        if "interactive_reader_writer_loop_gate" in patterns:
            hints.append("Transform interactive choices into new plot deltas with new stakes, scene goals, and consequences before chapter write-back.")
        if "abstract_style_learning_skill_gate" in patterns:
            hints.append("Transform style profiles into measurable craft constraints, then verify that the draft no longer depends on source wording or scene order.")
        if "impromptu_thread_pool_chapter_gate" in patterns:
            hints.append("Transform source thread pools by changing each promise, partial payoff, and development path before opening the new chapter blueprint.")
        if "offline_inspiration_bank_style_gate" in patterns:
            hints.append("Transform inspiration-bank references into fresh style constraints and local lore tasks; source documents stay outside accepted canon until reviewed.")
        if "atelier_phase_pipeline_gate" in patterns:
            hints.append("Transform atelier handoffs by assigning new phase artifacts, beat ids, hook owners, and reviewer criteria for the independent project.")
        if "book_mining_genesis_automation_gate" in patterns:
            hints.append("Transform mining categories into abstract functions first, then create a distinct canon seed before any chapter automation runs.")
        if "multi_book_autopilot_studio_gate" in patterns:
            hints.append("Transform the studio scaffold by assigning a fresh book profile, stop conditions, continuity-check cadence, and per-book context namespace.")
        if "longrun_commit_projection_health_gate" in patterns:
            hints.append("Transform the commit chain by starting a new accepted-commit lineage and derived projections for the independent story.")
        if "fresh_context_chapter_iteration_gate" in patterns:
            hints.append("Transform fresh-context loops by building a new chapter manifest, progress log, and acceptance criteria instead of replaying the source run loop.")
        if "inline_human_machine_coauthoring_gate" in patterns:
            hints.append("Transform inline coauthor edits into new localized spans, then require author acceptance and copy-risk checks before merging.")
        if "hierarchical_orchestrator_generation_gate" in patterns:
            hints.append("Transform orchestrator stages by changing volume/arc/chapter ownership, parent context, and acceptance gates for the new book.")
        if "batch_continuation_progress_queue_gate" in patterns:
            hints.append("Transform continuation queues by resetting progress cursor, chapter ids, retry budget, and accepted-state lineage for the new project.")
        if "homogeneity_prompt_variation_gate" in patterns:
            hints.append("Transform samey output repairs by changing the structural axis—scene purpose, conflict entry, rhythm, and payoff—not just wording.")
        if "local_author_data_boundary_gate" in patterns:
            hints.append("Transform local-data notes through explicit boundary labels so packaged-app artifacts or updater evidence cannot become story canon.")
        if "prompt_preset_variable_library_gate" in patterns:
            hints.append("Transform prompt presets by changing variables, audience, scene function, and constraints for the new project instead of reusing a source preset verbatim.")
        if "imported_manuscript_migration_outline_gate" in patterns:
            hints.append("Transform imported outlines into independent chapter slots with new causes, costs, relationships, and payoff owners.")
        if "style_dna_reference_library_gate" in patterns:
            hints.append("Transform style-DNA notes into new voice guardrails; source examples may define an axis but not sentence templates.")
        if "draft_candidate_promotion_gate" in patterns:
            hints.append("Transform candidate workflows by resetting candidate ids, reviewer decisions, and memory writebacks for the new story lineage.")
        if "privacy_preserving_local_index_gate" in patterns:
            hints.append("Transform local-index hits into metadata citations first; only author-approved new-story text can become prompt context or canon.")
        if "chapter_description_continuity_bridge_gate" in patterns:
            hints.append("Transform each source chapter description into a new continuity bridge with different actors, causes, stakes, and unresolved hooks.")
        if "selective_streaming_regeneration_gate" in patterns:
            hints.append("Transform regeneration decisions as scoped patch plans: new chapter id, new affected spans, and protected accepted chapters.")
        if "research_citation_boundary_gate" in patterns:
            hints.append("Transform citations into source-evidence constraints and bibliography tasks, not into copied explanatory paragraphs or source narrative facts.")
        if "beta_reader_summary_context_gate" in patterns:
            hints.append("Transform beta-reader objections into local revision tasks tied to the new story's prior summaries and review tone.")
        if "style_vocab_world_card_extraction_gate" in patterns:
            hints.append("Transform source vocabulary into abstract style levers, then build new world cards, character cards, and local rewrite scopes from new-story facts.")
        if "prompt_only_decay_ceiling_gate" in patterns:
            hints.append("Transform prompt-only lessons into a ceiling policy: when context decays, refresh the new-story bible instead of borrowing source shortcuts.")
        if "serial_platform_minimum_audit_gate" in patterns:
            hints.append("Transform serial audit cadence into new-story acceptance gates with different hooks, battles, dialogue beats, and loop-risk evidence.")
        if "multi_agent_reject_retry_review_gate" in patterns:
            hints.append("Transform agent roles and retry budgets, but reset all scores, reject reasons, and planning decisions for the new-story lineage.")
        if "story_bible_context_packet_branch_gate" in patterns:
            hints.append("Transform context-packet assembly by creating new branch ids, savepoints, promises, and recent summaries before generation.")
        if "memory_augmented_delta_verification_gate" in patterns:
            hints.append("Transform extracted deltas into new fact candidates and verify each one before it can enter the new-story delta index.")
        if "statistical_style_benchmark_rewrite_gate" in patterns:
            hints.append("Transform style benchmark presets into target metric ranges; do not preserve source example text, scene order, or signature voice artifacts.")
        if "temporal_canon_context_graph" in patterns:
            hints.append("Transform graph episodes by changing entities, time windows, relationship causes, and provenance links before context retrieval.")
        if "long_term_author_preference_memory" in patterns:
            hints.append("Transform author preferences into project-local style decisions without recording source-book facts as preferences.")
        if "community_graph_source_deconstruction" in patterns:
            hints.append("Transform source communities into new-story communities with different members, labels, causal pressures, and cross-community edges.")
        if "dual_level_graph_vector_retrieval" in patterns:
            hints.append("Transform retrieval plans by using vector matches for craft texture and graph traversal for new-story canon only.")
        if "schema_guided_graph_extraction" in patterns:
            hints.append("Transform graph extraction schemas by replacing source labels, relationship types, and required properties with new-story equivalents.")
        if "trope_inventory_similarity_gate" in patterns:
            hints.append("Transform trope overlap by preserving only broad genre expectations; change the concrete cause, cast role, prop, setting, and payoff order.")
        if "trope_graph_expectation_map" in patterns:
            hints.append("Transform trope-graph neighbors into new combinations rather than copying the source work's trope adjacency pattern.")
        if "trope_density_novelty_budget" in patterns:
            hints.append("Transform overused trope clusters by adding a local twist, swapped power relation, altered cost, or delayed consequence.")
        if "trope_source_boundary_review" in patterns:
            hints.append("Transform trope references from metadata only; do not fetch, paste, or paraphrase live trope-page prose into a same-type draft.")
        if "source_license_detection_gate" in patterns:
            hints.append("Transform source material only after license status is known; unknown-rights text may provide metadata labels, not plot, prose, or style exemplars.")
        if "spdx_reuse_compliance_gate" in patterns:
            hints.append("Transform SPDX/REUSE findings into source admission notes and attribution tasks rather than generation content.")
        if "public_domain_corpus_boundary" in patterns:
            hints.append("Transform public-domain texts through a source manifest and originality gates; public domain is not a reason to clone chapter order or set pieces.")
        if "attribution_derivative_work_gate" in patterns:
            hints.append("Transform adaptation-risk material by separating allowed reference, required attribution, and blocked derivative similarity before drafting.")
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
        if "mode_contract_generation_gate" in patterns:
            hints.append("Reject mode-contract outputs when mode tags are satisfied by reusing source set pieces, ending cadence, or character-function order.")
        if "source_study_method_bank_isolation_gate" in patterns:
            hints.append("Reject prompts that paste source-study chunks, original beat text, or raw style metrics as drafting context instead of citing abstract method ids.")
        if "inline_human_machine_coauthoring_gate" in patterns:
            hints.append("Reject inline edits that hide source-like replacement spans inside accepted prose without author decision and copied-span review.")
        if "hierarchical_orchestrator_generation_gate" in patterns:
            hints.append("Reject orchestrator outputs that preserve source volume/arc/chapter order while only renaming stage labels.")
        if "batch_continuation_progress_queue_gate" in patterns:
            hints.append("Reject batch continuation that advances from rejected, failed, or source-derived progress state.")
        if "homogeneity_prompt_variation_gate" in patterns:
            hints.append("Reject adjacent chapters with repeated scene openings, conflict cadence, hook shape, or payoff rhythm unless a variation decision explains it.")
        if "local_author_data_boundary_gate" in patterns:
            hints.append("Reject context packs that mix packaged-app files, updater/download notes, source metadata, and accepted canon without boundary labels.")
        if "prompt_preset_variable_library_gate" in patterns:
            hints.append("Reject prompts whose template variables hide source text, source names, or author-style commands behind neutral preset labels.")
        if "imported_manuscript_migration_outline_gate" in patterns:
            hints.append("Reject same-type drafts that preserve imported chapter order, chapter titles, parser fragments, or outline wording from the source manuscript.")
        if "style_dna_reference_library_gate" in patterns:
            hints.append("Reject style-DNA use that reproduces source phrasing, named set pieces, catchphrases, or a living author's signature sentence pattern.")
        if "draft_candidate_promotion_gate" in patterns:
            hints.append("Reject candidate promotion when copy-risk, author decision, or memory-writeback evidence is missing.")
        if "privacy_preserving_local_index_gate" in patterns:
            hints.append("Reject context packs where metadata-only search results silently pull manuscript plaintext into prompts.")
        if "chapter_description_continuity_bridge_gate" in patterns:
            hints.append("Reject chapter descriptions that preserve source chapter order, distinctive labels, or bridge facts under renamed characters.")
        if "selective_streaming_regeneration_gate" in patterns:
            hints.append("Reject specific-chapter regeneration that overwrites unrelated chapters, accepted summaries, or memory state without an explicit scope review.")
        if "research_citation_boundary_gate" in patterns:
            hints.append("Reject drafts that treat research snippets, citations, or plagiarism-check notes as reusable prose or unreviewed fiction facts.")
        if "beta_reader_summary_context_gate" in patterns:
            hints.append("Reject beta-reader fixes that cite stale previous chapter summaries or convert reader preference into canon without an author decision.")
        if "style_vocab_world_card_extraction_gate" in patterns:
            hints.append("Reject style-vocabulary or world-card extraction that carries source proper nouns, unique setting rules, or chapter-local source facts into new canon.")
        if "prompt_only_decay_ceiling_gate" in patterns:
            hints.append("Reject prompt-only continuation when decay causes recycled source beats, premature wrap-up, or unsupported canon guesses.")
        if "serial_platform_minimum_audit_gate" in patterns:
            hints.append("Reject drafts that pass surface de-AI cleanup while failing loop detection, dialogue-ratio, battle-logic, or chapter-hook audit evidence.")
        if "multi_agent_reject_retry_review_gate" in patterns:
            hints.append("Reject multi-agent outputs where retry logs are missing, scores are below threshold, or rejected drafts update bible/context state.")
        if "story_bible_context_packet_branch_gate" in patterns:
            hints.append("Reject context packets without branch lineage, savepoint, restore target, and separation between source pattern notes and new-story canon.")
        if "memory_augmented_delta_verification_gate" in patterns:
            hints.append("Reject extracted deltas that skip targeted verification or merge into the knowledge graph without deterministic accumulation trace.")
        if "statistical_style_benchmark_rewrite_gate" in patterns:
            hints.append("Reject style-benchmark rewrites that overfit to 22-book presets, reproduce benchmark examples, or improve metrics by flattening character voice.")
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
        if "reader_rating_signal_model" in patterns:
            hints.append("Reject plans that treat high-rated books, shelves, or tags as permission to copy their premise, cast, or event chain.")
        if "review_spoiler_sentiment_corpus" in patterns:
            hints.append("Reject prompts or copy that paste verbatim reader reviews, reviewer identities, spoiler examples, or quoted complaint language.")
        if "beta_reader_archetype_panel" in patterns:
            hints.append("Reject beta-reader fixes that force the new story back toward a comp/source plot route instead of solving the local issue.")
        if "comp_title_market_positioning" in patterns:
            hints.append("Reject comp-title positioning that reuses title phrasing, blurb beats, named tropes as labels, or recognizable hook sequence.")
        if "local_reader_experience_editor" in patterns:
            hints.append("Reject hook/cliffhanger repairs that mirror a source chapter ending or preserve distinctive source payoff cadence.")
        if "context_pack_preview" in patterns:
            hints.append("Reject context packs that cite source analysis artifacts as new-story facts.")
        if "top_down_story_planning" in patterns:
            hints.append("Reject plan hierarchies that mirror the source act/chapter/scene route under renamed labels.")
        if "trope_inventory_similarity_gate" in patterns:
            hints.append("Reject drafts whose trope vector is near-identical to one source work without enough new cast, setting, stakes, and sequence changes.")
        if "trope_graph_expectation_map" in patterns:
            hints.append("Reject outlines that keep the same rare trope pairings and adjacency order as the source under different names.")
        if "trope_density_novelty_budget" in patterns:
            hints.append("Reject drafts that overload copied trope clusters while adding no local twist, inversion, or new consequence.")
        if "trope_source_boundary_review" in patterns:
            hints.append("Reject any trope-source text copied from crawled pages, live site output, or parser dumps; keep only compact metadata labels.")
        if "source_license_detection_gate" in patterns:
            hints.append("Reject drafts or context packs that include long source text from unknown, missing, or low-confidence license sources.")
        if "spdx_reuse_compliance_gate" in patterns:
            hints.append("Reject imports that lack source-level SPDX id, copyright holder, attribution status, or reviewer decision.")
        if "public_domain_corpus_boundary" in patterns:
            hints.append("Reject public-domain corpus use without title/author/source URL/date/extraction-format provenance and jurisdiction caveat.")
        if "attribution_derivative_work_gate" in patterns:
            hints.append("Reject same-type drafts that rely on attribution as a substitute for independent plot, character, setting, and phrasing.")
        if "source_entity_redaction_gate" in patterns:
            hints.append("Reject prompts, plans, or drafts that carry unredacted source-specific names, places, factions, artifacts, powers, or titles without continuation approval.")
        if "custom_entity_label_inventory" in patterns:
            hints.append("Reject entity inventories that only rename PERSON/ORG/LOC while leaving source-specific faction, artifact, rank, ability, or invented-term labels intact.")
        if "placeholder_alias_consistency_map" in patterns:
            hints.append("Reject partially redacted context where placeholders, aliases, nicknames, and titles map inconsistently across chapters.")
        if "proper_noun_leakage_review" in patterns:
            hints.append("Reject final drafts with distinctive source proper nouns unless each name appears in an approved exception list.")
        if "outliner_index_cards" in patterns:
            hints.append("Reject outline-card boards whose card order, scene function, and hook sequence mirror the source.")
        if "narrative_strand_mapping" in patterns:
            hints.append("Reject narrative strands that preserve source fabula and setting pressure under surface substitutions.")
        if "human_synopsis_gate" in patterns:
            hints.append("Reject accepted synopses that preserve the source chapter-summary sequence under renamed entities.")
        if "retrieval_guided_span_rewrite" in patterns:
            hints.append("Reject rewrites that retrieve source spans as canon instead of using them as transformation evidence.")
        if "runtime_artifact_trace" in patterns:
            hints.append("Reject traces whose selected context mixes source inspiration with accepted new-story canon.")
        if "continuity_bridge_window" in patterns:
            hints.append("Reject bridge packets that import source continuity as if it were accepted new-story history.")
        if "voice_table_polish_axis" in patterns:
            hints.append("Reject voice tables that keep source catchphrases, signature sentence endings, or named verbal tics.")
        if "beat_strand_framework" in patterns:
            hints.append("Reject beat maps that preserve the source convergence order under different names.")
        if "sourcebook_author_workbench" in patterns:
            hints.append("Reject transformed sourcebooks that carry source names, unique locations, lore labels, item names, or scene lists.")
        if "semantic_long_context_search" in patterns:
            hints.append("Reject semantic context packs that retrieve source passages as new-story canon.")
        if "research_taxonomy_story_map" in patterns:
            hints.append("Reject prompts that paste large index/catalog entries into same-type drafting context.")
        if "novel_to_multimodal_pipeline" in patterns:
            hints.append("Reject adaptation plans that preserve source shot order, scene order, or recognizable set-piece staging.")
        if "entity_to_visual_asset_pipeline" in patterns:
            hints.append("Reject visual-asset manifests that keep source character designs, unique props, location names, or costume signatures.")
        if "agentic_book_planner_pipeline" in patterns:
            hints.append("Reject planner-role outputs that mirror source Story Bible facts, plot-thread labels, or chapter-outline sequence.")
        if "rag_synopsis_spine" in patterns:
            hints.append("Reject synopsis spines that preserve source chapter-summary order under renamed entities.")
        if "anti_repetition_prompt_rules" in patterns:
            hints.append("Reject drafts that pass local prose checks but repeat the source's scene-function rhythm across chapters.")
        if "prompt_recipe_experiment_grid" in patterns:
            hints.append("Reject experiment winners whose quality score comes from closeness to source facts or wording.")
        if "narrative_arc_template_control" in patterns:
            hints.append("Reject arc templates that preserve source scenario blueprint fields, named gimmicks, or payoff order.")
        if "nrd_task_tree_pipeline" in patterns:
            hints.append("Reject NRD task trees whose arc/chapter/scene hierarchy mirrors the source route.")
        if "story_structure_rag_planning" in patterns:
            hints.append("Reject structure scaffolds that smuggle source quotes, named examples, or event ordering into canon.")
        if "story_contract_commit_chain" in patterns:
            hints.append("Reject transformed drafts whose contract or commit chain preserves source chapter-causality order under renamed labels.")
        if "fact_snapshot_delta_gate" in patterns:
            hints.append("Reject state deltas that keep source proper nouns, unique facts, abilities, clues, or relationship labels.")
        if "foreshadowing_debt_budget" in patterns:
            hints.append("Reject payoff plans that preserve the same clue, debt, and reveal window from the source work.")
        if "reader_retention_review_gate" in patterns:
            hints.append("Reject chapters whose retention score depends on recognizable source set pieces or hook sequence.")
        if "draft_stage_revision_ladder" in patterns:
            hints.append("Reject Draft B/C polish that merely paraphrases source wording or restores source scene order.")
        if "rolling_summary_context_trim" in patterns:
            hints.append("Reject context packs that use source rolling summaries as new-story canon.")
        if "pairwise_story_comparison_ranking" in patterns:
            hints.append("Reject pairwise winners whose advantage is source resemblance rather than transformed-story quality.")
        if "multidimensional_quality_rubric" in patterns:
            hints.append("Reject high rubric scores when copied source names, event order, or relationship dynamics remain in structured fields or prose.")
        if "story_theory_beat_evaluation" in patterns:
            hints.append("Reject beat conversions that preserve source beat order, named examples, or distinctive set-piece functions.")
        if "constraint_specificity_creativity_benchmark" in patterns:
            hints.append("Reject constraint sets that encode source-specific clues, objects, locations, or payoff windows.")
        if "style_axis_diversity_fingerprint" in patterns:
            hints.append("Reject style fingerprints that preserve source catchphrases, metaphor clusters, or recognizable closure cadence.")
        if "event_outline_history_compression" in patterns:
            hints.append("Reject compressed histories that import source events as if they happened in the transformed story.")
        if "agentic_story_world_simulation" in patterns:
            hints.append("Reject simulated outcomes that reproduce source character decisions or social graph under renamed labels.")
        if "delivery_manuscript_assembly" in patterns:
            hints.append("Reject final manuscripts whose chapter headings, title cadence, or chapter order mirror the source under renamed content.")
        if "export_format_fidelity_audit" in patterns:
            hints.append("Reject export polish that changes text toward source phrasing or treats source exports as canonical chapter text.")
        if "preview_toc_packaging" in patterns:
            hints.append("Reject TOC or preview navigation that preserves source chapter-name sequence or source section hierarchy.")
        if "cover_kdp_metadata_boundary" in patterns:
            hints.append("Reject cover, blurb, keyword, or KDP metadata that reuses source title phrasing, tagline, or recognizable hook language.")
        if "branching_choice_graph" in patterns:
            hints.append("Reject copied choice text, option order, branch topology, or consequence labels that make the new route recognizable as the source.")
        if "node_dialogue_state_machine" in patterns:
            hints.append("Reject dialogue nodes that preserve source lines, option labels, command names, or speaker-state order under renamed characters.")
        if "passage_link_navigation_map" in patterns:
            hints.append("Reject passage maps whose visible links, hidden routes, dead ends, or merge sequence mirror the source navigation.")
        if "choice_stats_consequence_gate" in patterns:
            hints.append("Reject stat ledgers that keep source variable names, achievement labels, thresholds, or delayed consequence cadence.")
        if "source_text_fingerprint_gate" in patterns:
            hints.append("Reject drafts with high fingerprint overlap in long phrases, scene order, or set-piece labels unless the span is explicit continuation canon.")
        if "fuzzy_phrase_similarity_gate" in patterns:
            hints.append("Reject paraphrases that survive fuzzy matching after names, titles, and surface nouns are changed.")
        if "diff_span_copy_review" in patterns:
            hints.append("Reject chapters whose copied-span review shows source sentence order, semantic-cleanup matches, or patch-like edits.")
        if "minhash_lsh_near_duplicate_gate" in patterns:
            hints.append("Reject high-Jaccard source overlaps unless they are reviewed stock phrases or explicit continuation canon.")
        if "simhash_hamming_similarity_gate" in patterns:
            hints.append("Reject low-Hamming-distance prose windows that survive entity remap, translation, or copyedit polish.")
        if "semantic_duplicate_cluster_gate" in patterns:
            hints.append("Reject drafts whose scene windows cluster with source scenes after concrete entities and wording have changed.")
        if "embedding_similarity_independence_gate" in patterns:
            hints.append("Reject same-type drafts when source excerpts remain the nearest semantic neighbors for key passages.")
        if "corpus_leakage_dedup_review_gate" in patterns:
            hints.append("Reject outputs that reuse long source sequences, duplicated chapter routes, or mixed source/deconstruction material as canon.")
        if "character_quote_attribution_map" in patterns:
            hints.append("Reject copied speaker quote distribution, alias clusters, or dialogue-turn ownership that makes the new cast trace back to the source.")
        if "readability_pacing_metric_gate" in patterns:
            hints.append("Reject transformed chapters that match source readability curves because they also preserve source scene order or payoff cadence.")
        if "prose_lint_style_rule_gate" in patterns:
            hints.append("Reject lint-clean drafts when the rule fixes preserve source paragraph rhythm, catchphrases, or signature sentence closures.")
        if "grammar_spelling_copyedit_gate" in patterns:
            hints.append("Reject copyedit fixes that normalize the new voice toward source diction or remove deliberate dialogue/register differences.")
        if "copyedit_diagnostic_triage_queue" in patterns:
            hints.append("Reject accepted diagnostic batches that silently apply source-like rewrites without author-visible triage reasons.")
        if "lexical_diversity_voice_audit" in patterns:
            hints.append("Reject voice audits that keep source catchphrases, repeated vocabulary clusters, or signature metaphor families.")
        if "stylometric_author_fingerprint_gate" in patterns:
            hints.append("Reject fingerprints that make the transformed draft intentionally attributable to the source author or source corpus.")
        if "function_word_syntax_style_gate" in patterns:
            hints.append("Reject drafts whose function-word, punctuation, or sentence-rhythm windows recreate source-author signatures too closely.")
        if "authorship_attribution_similarity_gate" in patterns:
            hints.append("Reject same-type drafts when attribution/similarity checks rank the source author or source text as the nearest neighbor.")
        if "style_overfit_regression_gate" in patterns:
            hints.append("Reject prompt or polish changes that improve style resemblance while increasing source-voice leakage in regression windows.")
        if "paraphrase_independence_review_gate" in patterns:
            hints.append("Reject paraphrases that pass surface-copy checks but keep source phrase families, cadence, or author-mimicry constraints.")
        if "keyphrase_motif_extraction" in patterns:
            hints.append("Reject drafts whose top motif keywords, symbolic objects, or topic salience map back to source-specific set pieces.")
        if "chinese_segmentation_keyword_gate" in patterns:
            hints.append("Reject drafts whose segmented keyword list keeps source-specific names, terms, or motif compounds under surface changes.")
        if "chinese_ner_alias_consistency_gate" in patterns:
            hints.append("Reject transformed entity ledgers that keep source aliases, sect/place names, title systems, or relationship labels as canon.")
        if "chinese_text_normalization_gate" in patterns:
            hints.append("Reject normalization diffs that hide copied source phrasing behind Simplified/Traditional or punctuation-only changes.")
        if "chinese_error_correction_review_gate" in patterns:
            hints.append("Reject correction batches that normalize character voice toward source diction or silently rewrite invented terms.")
        if "source_format_import_manifest" in patterns:
            hints.append("Reject transformed outlines that preserve source TOC, spine order, metadata titles, or chapter grouping under new labels.")
        if "pdf_layout_text_extraction_gate" in patterns:
            hints.append("Reject drafts that copy source page-span rhythm, header/footer artifacts, or layout-driven section order.")
        if "ocr_scanned_page_import_gate" in patterns:
            hints.append("Reject generations based on unreviewed low-confidence OCR spans or hallucinated fixes to unreadable pages.")
        if "document_partition_chapter_detection_gate" in patterns:
            hints.append("Reject chapter maps that keep source heading text, partition sequence, or section boundary cadence.")
        if "import_provenance_checksum_gate" in patterns:
            hints.append("Reject context packs that mix original, extracted, normalized, and accepted text without explicit lineage.")
        if "epub_structure_validation_gate" in patterns:
            hints.append("Reject EPUB exports whose package, OPF manifest, spine, or container metadata no longer matches the accepted transformed chapters.")
        if "ebook_accessibility_audit_gate" in patterns:
            hints.append("Reject accessibility fixes that copy source captions, alt text, landmark labels, or front/back matter wording.")
        if "agentic_editorial_pipeline_gate" in patterns:
            hints.append("Reject agent-role outputs that skip author/reviewer acceptance or paste source-analysis conclusions as new-story canon.")
        if "chapter_state_archive_ladder" in patterns:
            hints.append("Reject context packs where permanent bible, transient state, source state snapshots, and current chapter deltas are mixed without lineage.")
        if "section_metadata_traceability_gate" in patterns:
            hints.append("Reject section metadata that keeps source cast, location, item, plotline, beat, or pacing ids under renamed prose.")
        if "ai_prose_fingerprint_cluster_gate" in patterns:
            hints.append("Reject fingerprint cleanup that merely paraphrases source passages or preserves a source-like chapter cadence under smoother prose.")
        if "author_candidate_canon_confirmation_gate" in patterns:
            hints.append("Reject drafts that treat unconfirmed source candidates, AI suggestions, or preview-only material as transformed canon.")
        if "progressive_spoiler_context_window_gate" in patterns:
            hints.append("Reject chapters that reveal future facts, ending routes, or payoff timing because the source work revealed them in that order.")
        if "chapter_control_card_writeback_gate" in patterns:
            hints.append("Reject chapter cards whose must-change beat, line pressure, debt return, title hook, or handoff mirrors the source card sequence.")
        if "trace_replay_revision_workspace_gate" in patterns:
            hints.append("Reject trace logs that cannot separate source analysis traces from transformed-story decision evidence.")
        if "relationship_graph_global_replace_gate" in patterns:
            hints.append("Reject relationship graphs or global replacements that preserve source aliases, edge labels, centrality, or relationship timing under new names.")
        if "bookrun_audit_trail_gate" in patterns:
            hints.append("Reject BookRun traces that replay source blueprint decisions, judge rationales, or repair diffs as transformed-story authority.")
        if "provider_budget_smoke_gate" in patterns:
            hints.append("Reject provider smoke results that hide cost, token, model, profile, or real-vs-dry-run status.")
        if "sidecar_memory_profile_boundary" in patterns:
            hints.append("Reject context packs that mix source sidecar memory, transformed canon graph, vector cache, or provider profile without namespace evidence.")
        if "outline_checkpoint_milestone_gate" in patterns:
            hints.append("Reject outlines whose checkpoint sequence, milestone names, or Story Bible deltas mirror the source structure under renamed labels.")
        if "language_localization_style_profile_gate" in patterns:
            hints.append("Reject localized prose that carries source language artifacts, glossary entries, address terms, or unit conventions into an unrelated setting.")
        if "progressive_disclosure_skill_protocol_gate" in patterns:
            hints.append("Reject prompts that paste external skill protocols wholesale instead of loading compact project-native steps.")
        if "anti_slop_rulepack_triage_gate" in patterns:
            hints.append("Reject anti-slop rewrites that smooth text into generic prose or paraphrase distinctive source sentences.")
        if "user_modifier_project_blueprint_gate" in patterns:
            hints.append("Reject blueprints whose modifier set encodes source-specific cast, setting, title cadence, or chapter route.")
        if "portable_canon_skill_runtime_gate" in patterns:
            hints.append("Reject canon imports that preserve source asset paths, frontmatter ids, skill files, or artifact names as transformed-story authority.")
        if "staged_outline_chunk_window_gate" in patterns:
            hints.append("Reject staged outlines whose setup/chunk sequence, adjacent-window summaries, or range-refinement targets match the source route.")
        if "wiki_canon_graph_lint_gate" in patterns:
            hints.append("Reject wiki pages or relationship graphs that keep source node names, edge labels, timeline warnings, or setup/payoff ids.")
        if "plan_draft_log_verify_loop_gate" in patterns:
            hints.append("Reject chapter logs that reproduce source scene order, glossary entries, thread labels, or foreshadowing checklist cadence.")
        if "mcp_scene_index_revision_boundary" in patterns:
            hints.append("Reject scene revision bundles that cannot distinguish source scene ids, transformed scene ids, selected context, and accepted diffs.")
        if "verbalized_sampling_diversity_wiki_gate" in patterns:
            hints.append("Reject diversity samples when their probability set still clusters around source premise, names, sequence, or set pieces.")
        if "front_back_matter_metadata_gate" in patterns:
            hints.append("Reject packaging that preserves source titlepage, colophon, copyright text, identifiers, or publication metadata under new labels.")
        if "toc_navigation_consistency_gate" in patterns:
            hints.append("Reject TOC/navigation maps whose chapter titles, order, hierarchy, or reader links mirror the source EPUB instead of the new outline.")
        if "literary_event_entity_annotation_gate" in patterns:
            hints.append("Reject drafts whose event/entity annotation ledger preserves source participant roles, event labels, or mention order under renamed surface text.")
        if "narrative_event_evolution_graph_gate" in patterns:
            hints.append("Reject transformed outlines whose causal/event graph keeps source event order, dependency edges, or script-like next-event predictions.")
        if "sentiment_arc_emotion_trajectory_gate" in patterns:
            hints.append("Reject emotion arcs that mirror source turning-point sequence, valence curve, or character-trigger mapping too closely.")
        if "cross_context_coreference_gate" in patterns:
            hints.append("Reject coreference ledgers that allow source aliases, events, or abstract concepts to resolve into transformed canon.")
        if "character_interaction_network_gate" in patterns:
            hints.append("Reject relationship networks that preserve source central characters, alliance/conflict polarity, or interaction timing under new names.")
        if "semantic_chunk_boundary_map" in patterns:
            hints.append("Reject transformed context packs that preserve source chunk order, boundary labels, or inclusion sequence under new names.")
        if "chapter_summary_anchor_gate" in patterns:
            hints.append("Reject summaries that preserve source chapter-summary order, representative sentence function, or unresolved-hook sequence.")
        if "topic_drift_map" in patterns:
            hints.append("Reject topic maps whose cluster sequence, salience curve, or off-arc detours match the source route.")
        if "context_faithfulness_eval_gate" in patterns:
            hints.append("Reject faithfulness scores that treat source-analysis notes or source summaries as transformed-story evidence.")
        if "retrieval_trace_observability_gate" in patterns:
            hints.append("Reject traces that cannot explain why source-like context was selected, omitted, or separated from transformed canon.")
        if "prompt_regression_eval_suite" in patterns:
            hints.append("Reject prompt changes that pass quality checks but fail golden copy-risk, grounding, or source-canon leakage cases.")
        if "agentwrite_plan_write_pipeline" in patterns:
            hints.append("Reject plan-write pipelines whose plan segments, section order, or write-stage prompts mirror the source route.")
        if "long_output_length_quality_ruler" in patterns:
            hints.append("Reject long outputs that satisfy word count by padding, repeating, prematurely summarizing, or tracking source pacing too closely.")
        if "long_context_reward_dimension_gate" in patterns:
            hints.append("Reject averaged reward scores when faithfulness, logicality, or completeness fails on transformed-story evidence.")
        if "instance_specific_writing_criteria_gate" in patterns:
            hints.append("Reject criteria sets that encode source-specific clues, locations, objects, relationship labels, or payoff windows.")
        if "material_grounded_query_refinement" in patterns:
            hints.append("Reject context packs whose material grounding still treats source examples or source summaries as new-story facts.")
        if "hybrid_rubric_pairwise_elo_judge" in patterns:
            hints.append("Reject pairwise winners whose margin comes from source familiarity, extra length, or judge preference rather than transformed-story quality.")
        if "judge_bias_mitigation_check" in patterns:
            hints.append("Reject judge reports that reward verbose, longer, or later-positioned drafts without concrete story evidence.")
        if "plan_reflect_character_chapter_pipeline" in patterns:
            hints.append("Reject plan-reflect-character traces that keep source act order, cast functions, or chapter sequence under new names.")
        if "human_story_metric_panel" in patterns:
            hints.append("Reject reader-metric fixes that improve engagement by restoring recognizable source hooks or set pieces.")
        if "hierarchical_cowriting_story_scaffold" in patterns:
            hints.append("Reject hierarchical scaffolds whose logline, character function, plot-point order, or location/dialogue sequence mirrors the source.")
        if "human_coauthor_edit_boundary" in patterns:
            hints.append("Reject co-writing outputs that skip plagiarism, toxicity, stereotype, or formulaic-output review before canon acceptance.")
        if "recursive_reprompt_revision_loop" in patterns:
            hints.append("Reject recursive revisions that repeatedly reprompt source-like outlines instead of changing the underlying plan.")
        if "reranker_guided_candidate_selection" in patterns:
            hints.append("Reject reranker winners whose relevance or coherence comes from source resemblance rather than accepted new-story state.")
        if "character_dialogue_persona_memory" in patterns:
            hints.append("Reject persona memories that copy source lines, catchphrases, protected character names, or relationship labels.")
        if "event_to_sentence_realization_trace" in patterns:
            hints.append("Reject realized sentences when the event trace preserves source event order, unique props, or set-piece causality.")
        if "entity_memory_slotfill_grounding" in patterns:
            hints.append("Reject slot-filled prose that imports source entities, aliases, locations, or objects into transformed-story canon.")
        if "book_memory_bank_context_lattice" in patterns:
            hints.append("Reject memory-bank updates that mix source analysis notes into transformed canon, active context, or progress state.")
        if "spec_driven_fiction_scene_tasks" in patterns:
            hints.append("Reject scene tasks whose IDs, sequence, POV reveals, glossary terms, or quality gates recreate the source route.")
        if "toc_aware_source_deconstruction" in patterns:
            hints.append("Reject transformed outlines that preserve source TOC order, heading cadence, quotes, anecdotes, or section hierarchy.")
        if "two_pass_context_glossary_pipeline" in patterns:
            hints.append("Reject generated chapters whose glossary keeps source names, terms, locations, titles, or term-introduction order.")
        if "inline_author_edit_markup_versioning" in patterns:
            hints.append("Reject inline notes or edit queues that smuggle source scene instructions into final independent prose.")
        if "causal_dramatica_agent_pipeline" in patterns:
            hints.append("Reject causal maps that keep source event chain, dilemma order, payoff owner, or foreshadowing debt under new labels.")
        if "capture_distillation_production_gate" in patterns:
            hints.append("Reject production packets that include raw source captures, pasted source notes, or undecided distillation findings.")
        if "skill_orchestrated_chinese_novel_workflow" in patterns:
            hints.append("Reject skill-stage outputs that bulk-import external skill text, installer assumptions, or source-like Chinese web-novel proper nouns.")
        if "langgraph_story_state_machine" in patterns:
            hints.append("Reject state checkpoints that merge source-analysis state with transformed-story canon or skip transition validation.")
        if "story_daemon_evolution_loop" in patterns:
            hints.append("Reject autonomous evolution outputs that rewrite accepted canon, close arcs, or add lore without replayable review evidence.")
        if "local_rag_writing_ide_gate" in patterns:
            hints.append("Reject context packs that mix source chunks, new-story canon, and style guidance without labels, provenance, and copy-risk review.")
        if "canon_drift_continuity_qa_gate" in patterns:
            hints.append("Reject same-type drafts that pass continuity only because they preserve source canon, relationship timing, or scene facts.")
        if "patch_replay_manuscript_state_gate" in patterns:
            hints.append("Reject patch chains that cannot replay from a new outline or that silently overwrite accepted transformed chapters.")
        if "microkernel_skill_plugin_isolation_gate" in patterns:
            hints.append("Reject plugin/skill outputs that bypass stage contracts, mutate canon directly, or import third-party prompt bodies into the project.")
        if "interactive_reader_writer_loop_gate" in patterns:
            hints.append("Reject reader-writer loop outputs when the accepted choice, chapter file delta, and continuity/copy-risk checks are not traceable.")
        if "abstract_style_learning_skill_gate" in patterns:
            hints.append("Reject style profiles or drafts that retain source phrases, proper nouns, distinctive set pieces, or plot order under the label of style learning.")
        if "impromptu_thread_pool_chapter_gate" in patterns:
            hints.append("Reject same-type drafts whose open-thread statuses, payoff windows, or chapter intent route still mirror the source work.")
        if "offline_inspiration_bank_style_gate" in patterns:
            hints.append("Reject inspiration-bank prompts that blend source passages, local canon, and style goals without source labels and copy-risk review.")
        if "atelier_phase_pipeline_gate" in patterns:
            hints.append("Reject atelier outputs that preserve source beat tree order, hook language, phase artifacts, or reviewer decisions under new labels.")
        if "book_mining_genesis_automation_gate" in patterns:
            hints.append("Reject canon seeds that preserve source pattern ids as facts, reuse source payoff order, or skip scoring before automation.")
        if "multi_book_autopilot_studio_gate" in patterns:
            hints.append("Reject unattended same-type drafts when the book profile, stop limits, full-book check cadence, or context namespace is missing.")
        if "longrun_commit_projection_health_gate" in patterns:
            hints.append("Reject drafts whose read-model projections are stale, whose chapter commit lineage is unclear, or whose memory scratchpad mixes source and transformed canon.")
        if "fresh_context_chapter_iteration_gate" in patterns:
            hints.append("Reject same-type chapter loops that reuse the source prd.json, progress log, story bible, or completed-chapter status as transformed-story authority.")
        if "narrative_qa_comprehension_gate" in patterns:
            hints.append("Reject same-type QA packs where source-book questions or answers can still pass under renamed entities.")
        if "chapter_summary_alignment_gate" in patterns:
            hints.append("Reject transformed summaries that keep source chapter/book summary order, causal phrasing, or temporal dependency chain.")
        if "story_question_answer_validation_gate" in patterns:
            hints.append("Reject QA validation that treats source story sections, narrative-element labels, or answer spans as evidence for new-story canon.")
        if "causal_why_explanation_gate" in patterns:
            hints.append("Reject why-explanations that preserve source motives, helpful sentences, or action rationales under new names.")
        if "story_commonsense_consistency_gate" in patterns:
            hints.append("Reject psychology ledgers that carry over source wounds, desires, emotion triggers, or relationship expectations into transformed canon.")
        if "query_focused_long_summary_gate" in patterns:
            hints.append("Reject query-focused summaries whose plot answer is a compressed paraphrase of the source story route.")
        if "temporal_canon_context_graph" in patterns:
            hints.append("Reject temporal graphs that preserve source event chronology, relationship validity windows, or provenance as transformed canon.")
        if "long_term_author_preference_memory" in patterns:
            hints.append("Reject preference memories that store source-specific names, tropes, set pieces, or copied wording as user preferences.")
        if "community_graph_source_deconstruction" in patterns:
            hints.append("Reject community graphs whose cluster labels, membership, or inter-community conflict order reveal the source work.")
        if "dual_level_graph_vector_retrieval" in patterns:
            hints.append("Reject context packs where source vector hits or graph neighborhoods are indistinguishable from accepted transformed canon.")
        if "schema_guided_graph_extraction" in patterns:
            hints.append("Reject graph extractions that keep source node labels, relationship names, property values, or source metadata inside new-story canon.")
        return hints

    def _supports_inspired_creation(self, patterns: set[str]) -> bool:
        if "same_type_creation" in patterns:
            return True
        if patterns.intersection(
            {
                "branching_choice_graph",
                "node_dialogue_state_machine",
                "passage_link_navigation_map",
                "choice_stats_consequence_gate",
                "source_text_fingerprint_gate",
                "fuzzy_phrase_similarity_gate",
                "diff_span_copy_review",
                "minhash_lsh_near_duplicate_gate",
                "simhash_hamming_similarity_gate",
                "semantic_duplicate_cluster_gate",
                "embedding_similarity_independence_gate",
                "corpus_leakage_dedup_review_gate",
                "character_quote_attribution_map",
                "readability_pacing_metric_gate",
                "prose_lint_style_rule_gate",
                "grammar_spelling_copyedit_gate",
                "copyedit_diagnostic_triage_queue",
                "lexical_diversity_voice_audit",
                "stylometric_author_fingerprint_gate",
                "function_word_syntax_style_gate",
                "authorship_attribution_similarity_gate",
                "style_overfit_regression_gate",
                "paraphrase_independence_review_gate",
                "keyphrase_motif_extraction",
                "chinese_segmentation_keyword_gate",
                "chinese_ner_alias_consistency_gate",
                "chinese_text_normalization_gate",
                "chinese_error_correction_review_gate",
                "source_format_import_manifest",
                "pdf_layout_text_extraction_gate",
                "ocr_scanned_page_import_gate",
                "document_partition_chapter_detection_gate",
                "import_provenance_checksum_gate",
                "epub_structure_validation_gate",
                "ebook_accessibility_audit_gate",
                "front_back_matter_metadata_gate",
                "toc_navigation_consistency_gate",
                "agentic_editorial_pipeline_gate",
                "chapter_state_archive_ladder",
                "section_metadata_traceability_gate",
                "ai_prose_fingerprint_cluster_gate",
                "author_candidate_canon_confirmation_gate",
                "progressive_spoiler_context_window_gate",
                "chapter_control_card_writeback_gate",
                "trace_replay_revision_workspace_gate",
                "relationship_graph_global_replace_gate",
                "bookrun_audit_trail_gate",
                "provider_budget_smoke_gate",
                "sidecar_memory_profile_boundary",
                "outline_checkpoint_milestone_gate",
                "language_localization_style_profile_gate",
                "progressive_disclosure_skill_protocol_gate",
                "anti_slop_rulepack_triage_gate",
                "user_modifier_project_blueprint_gate",
                "portable_canon_skill_runtime_gate",
                "staged_outline_chunk_window_gate",
                "wiki_canon_graph_lint_gate",
                "plan_draft_log_verify_loop_gate",
                "mcp_scene_index_revision_boundary",
                "verbalized_sampling_diversity_wiki_gate",
                "literary_event_entity_annotation_gate",
                "narrative_event_evolution_graph_gate",
                "sentiment_arc_emotion_trajectory_gate",
                "cross_context_coreference_gate",
                "character_interaction_network_gate",
                "semantic_chunk_boundary_map",
                "chapter_summary_anchor_gate",
                "topic_drift_map",
                "context_faithfulness_eval_gate",
                "retrieval_trace_observability_gate",
                "prompt_regression_eval_suite",
                "agentwrite_plan_write_pipeline",
                "long_output_length_quality_ruler",
                "long_context_reward_dimension_gate",
                "instance_specific_writing_criteria_gate",
                "material_grounded_query_refinement",
                "hybrid_rubric_pairwise_elo_judge",
                "judge_bias_mitigation_check",
                "plan_reflect_character_chapter_pipeline",
                "human_story_metric_panel",
                "hierarchical_cowriting_story_scaffold",
                "human_coauthor_edit_boundary",
                "recursive_reprompt_revision_loop",
                "reranker_guided_candidate_selection",
                "character_dialogue_persona_memory",
                "event_to_sentence_realization_trace",
                "entity_memory_slotfill_grounding",
                "book_memory_bank_context_lattice",
                "spec_driven_fiction_scene_tasks",
                "toc_aware_source_deconstruction",
                "two_pass_context_glossary_pipeline",
                "inline_author_edit_markup_versioning",
                "causal_dramatica_agent_pipeline",
                "capture_distillation_production_gate",
                "skill_orchestrated_chinese_novel_workflow",
                "langgraph_story_state_machine",
                "story_daemon_evolution_loop",
                "local_rag_writing_ide_gate",
                "canon_drift_continuity_qa_gate",
                "patch_replay_manuscript_state_gate",
                "microkernel_skill_plugin_isolation_gate",
                "interactive_reader_writer_loop_gate",
                "abstract_style_learning_skill_gate",
                "impromptu_thread_pool_chapter_gate",
                "offline_inspiration_bank_style_gate",
                "atelier_phase_pipeline_gate",
                "book_mining_genesis_automation_gate",
                "multi_book_autopilot_studio_gate",
                "longrun_commit_projection_health_gate",
                "fresh_context_chapter_iteration_gate",
                "mode_contract_generation_gate",
                "source_study_method_bank_isolation_gate",
                "inline_human_machine_coauthoring_gate",
                "hierarchical_orchestrator_generation_gate",
                "batch_continuation_progress_queue_gate",
                "homogeneity_prompt_variation_gate",
                "local_author_data_boundary_gate",
                "prompt_preset_variable_library_gate",
                "imported_manuscript_migration_outline_gate",
                "style_dna_reference_library_gate",
                "draft_candidate_promotion_gate",
                "privacy_preserving_local_index_gate",
                "chapter_description_continuity_bridge_gate",
                "selective_streaming_regeneration_gate",
                "research_citation_boundary_gate",
                "beta_reader_summary_context_gate",
                "style_vocab_world_card_extraction_gate",
                "prompt_only_decay_ceiling_gate",
                "serial_platform_minimum_audit_gate",
                "multi_agent_reject_retry_review_gate",
                "story_bible_context_packet_branch_gate",
                "memory_augmented_delta_verification_gate",
                "statistical_style_benchmark_rewrite_gate",
                "narrative_qa_comprehension_gate",
                "chapter_summary_alignment_gate",
                "story_question_answer_validation_gate",
                "causal_why_explanation_gate",
                "story_commonsense_consistency_gate",
                "query_focused_long_summary_gate",
                "temporal_canon_context_graph",
                "long_term_author_preference_memory",
                "community_graph_source_deconstruction",
                "dual_level_graph_vector_retrieval",
                "schema_guided_graph_extraction",
                "mode_contract_generation_gate",
                "source_study_method_bank_isolation_gate",
            }
        ):
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
                "snowflake_premise_expansion",
                "outliner_index_cards",
                "narrative_strand_mapping",
                "character_depth_interview",
                "mindmap_visual_planning",
                "human_synopsis_gate",
                "retrieval_guided_span_rewrite",
                "runtime_artifact_trace",
                "schema_validated_state_delta",
                "recursive_adaptive_planning",
                "frontmatter_story_schema",
                "continuity_bridge_window",
                "voice_table_polish_axis",
                "beat_strand_framework",
                "genre_parameterized_worldbuilding",
                "prose_preflight_voice_calibration",
                "sourcebook_author_workbench",
                "semantic_long_context_search",
                "contradiction_taxonomy_checker",
                "cross_chapter_redundancy_audit",
                "humanization_stylometry_levers",
                "research_taxonomy_story_map",
                "novel_to_multimodal_pipeline",
                "entity_to_visual_asset_pipeline",
                "agentic_book_planner_pipeline",
                "rag_synopsis_spine",
                "anti_repetition_prompt_rules",
                "prompt_recipe_experiment_grid",
                "append_only_generation_review_log",
                "narrative_arc_template_control",
                "nrd_task_tree_pipeline",
                "sampling_parameter_quality_sweep",
                "story_structure_rag_planning",
                "story_contract_commit_chain",
                "fact_snapshot_delta_gate",
                "projection_sync_observability",
                "foreshadowing_debt_budget",
                "reader_retention_review_gate",
                "draft_stage_revision_ladder",
                "rolling_summary_context_trim",
                "pairwise_story_comparison_ranking",
                "multidimensional_quality_rubric",
                "story_theory_beat_evaluation",
                "constraint_specificity_creativity_benchmark",
                "style_axis_diversity_fingerprint",
                "event_outline_history_compression",
                "agentic_story_world_simulation",
                "reader_rating_signal_model",
                "review_spoiler_sentiment_corpus",
                "beta_reader_archetype_panel",
                "comp_title_market_positioning",
                "local_reader_experience_editor",
                "delivery_manuscript_assembly",
                "export_format_fidelity_audit",
                "preview_toc_packaging",
                "cover_kdp_metadata_boundary",
                "source_text_fingerprint_gate",
                "fuzzy_phrase_similarity_gate",
                "diff_span_copy_review",
                "minhash_lsh_near_duplicate_gate",
                "simhash_hamming_similarity_gate",
                "semantic_duplicate_cluster_gate",
                "embedding_similarity_independence_gate",
                "corpus_leakage_dedup_review_gate",
                "prose_lint_style_rule_gate",
                "grammar_spelling_copyedit_gate",
                "copyedit_diagnostic_triage_queue",
            }
        ) and (
            "style_signature" in patterns
            or "chapter_generation" in patterns
            or "scene_type_directing" in patterns
            or "worldpkg_export" in patterns
            or "anti_ai_tone_polish" in patterns
            or "manuscript_export_formats" in patterns
            or "plain_text_project_storage" in patterns
        ):
            return True
        if patterns.intersection(
            {
                "snowflake_premise_expansion",
                "outliner_index_cards",
                "narrative_strand_mapping",
                "character_depth_interview",
                "mindmap_visual_planning",
                "human_synopsis_gate",
                "retrieval_guided_span_rewrite",
                "recursive_adaptive_planning",
            }
        ) and (
            "narrative_strand_mapping" in patterns
            or "character_depth_interview" in patterns
            or "outliner_index_cards" in patterns
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
                or "reader_rating_signal_model" in patterns
                or "review_spoiler_sentiment_corpus" in patterns
                or "beta_reader_archetype_panel" in patterns
                or "comp_title_market_positioning" in patterns
                or "local_reader_experience_editor" in patterns
                or "delivery_manuscript_assembly" in patterns
                or "export_format_fidelity_audit" in patterns
                or "preview_toc_packaging" in patterns
                or "branching_choice_graph" in patterns
                or "node_dialogue_state_machine" in patterns
                or "passage_link_navigation_map" in patterns
                or "choice_stats_consequence_gate" in patterns
                or "source_text_fingerprint_gate" in patterns
                or "fuzzy_phrase_similarity_gate" in patterns
                or "diff_span_copy_review" in patterns
                or "minhash_lsh_near_duplicate_gate" in patterns
                or "simhash_hamming_similarity_gate" in patterns
                or "semantic_duplicate_cluster_gate" in patterns
                or "embedding_similarity_independence_gate" in patterns
                or "corpus_leakage_dedup_review_gate" in patterns
                or "prose_lint_style_rule_gate" in patterns
                or "grammar_spelling_copyedit_gate" in patterns
                or "copyedit_diagnostic_triage_queue" in patterns
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
        posture, posture_hint = self._static_repository_posture(title, trust_review["posture_hint"])
        absorbed_patterns = self._absorbed_patterns(haystack)
        if posture == "index-only" and posture_hint == "catalog-index-only":
            absorbed_patterns = ["source_discovery"]
        return {
            "source": "github",
            "url": _text(repository.get("html_url")),
            "title": title,
            "summary": self._merge_candidate_summary(description, static_pattern_summary),
            "stars": repository.get("stargazers_count"),
            "license": _text(license_payload.get("spdx_id") or license_payload.get("key") or repository.get("license")),
            "family": self._classify_family(haystack),
            "posture": posture,
            "posture_hint": posture_hint,
            "risk_flags": self._risk_flags(haystack),
            "trust_review": trust_review,
            "absorbed_patterns": absorbed_patterns,
            "updated_at": _text(repository.get("updated_at")),
            "score": self._score_candidate(haystack, stars=repository.get("stargazers_count")),
        }

    def _static_repository_pattern_summary(self, title: str) -> str:
        return STATIC_REPOSITORY_PATTERN_OVERRIDES.get(title.lower(), "")

    def _static_repository_posture(self, title: str, fallback_hint: str) -> tuple[str, str]:
        override = STATIC_REPOSITORY_POSTURE_OVERRIDES.get(title.lower())
        if override:
            return override
        return "pattern-only", fallback_hint

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
        if self._has_copy_similarity_signal(haystack):
            return "novel-automation"
        if self._has_text_analysis_signal(haystack):
            return "novel-automation"
        if self._has_stylometry_signal(haystack):
            return "novel-automation"
        if self._has_prose_quality_signal(haystack):
            return "novel-automation"
        if self._has_chinese_text_processing_signal(haystack):
            return "novel-automation"
        if self._has_source_import_signal(haystack):
            return "novel-automation"
        if self._has_literary_structure_signal(haystack):
            return "novel-automation"
        if self._has_segmentation_summary_topic_signal(haystack):
            return "novel-automation"
        if self._has_eval_observability_signal(haystack):
            return "novel-automation"
        if self._has_long_output_generation_signal(haystack):
            return "novel-automation"
        if self._has_trope_signal(haystack):
            return "novel-automation"
        if self._has_source_rights_signal(haystack):
            return "novel-automation"
        if self._has_entity_redaction_signal(haystack):
            return "novel-automation"
        return "pattern-only"

    def _has_copy_similarity_signal(self, haystack: str) -> bool:
        copy_terms = (
            "plagiarism",
            "winnowing",
            "document fingerprint",
            "fingerprinting",
            "fuzzy string matching",
            "levenshtein",
            "string metrics",
            "sequence matcher",
            "sequencematcher",
            "diff match patch",
            "semantic cleanup",
            "copied slices",
            "minhash",
            "lsh",
            "locality sensitive hashing",
            "jaccard similarity",
            "text dedup",
            "deduplication",
            "simhash",
            "hamming distance",
            "semantic deduplication",
            "semantic duplicates",
            "textreuse",
            "text reuse",
            "document similarity",
            "text alignment",
            "sentence-transformers",
            "embedding similarity",
            "similarity search",
            "faiss",
            "exactsubstr",
            "neardup",
            "corpus leakage",
        )
        return any(term in haystack for term in copy_terms)

    def _has_text_analysis_signal(self, haystack: str) -> bool:
        text_analysis_terms = (
            "booknlp",
            "book-length document",
            "character coreference",
            "quote attribution",
            "speaker attribution",
            "readability",
            "readability statistics",
            "sentence length",
            "lexical richness",
            "lexical diversity",
            "mtld",
            "hd-d",
            "keyphrase extraction",
            "keyword extraction",
            "motif extraction",
        )
        return any(term in haystack for term in text_analysis_terms)

    def _has_stylometry_signal(self, haystack: str) -> bool:
        terms = (
            "stylometry",
            "stylometric",
            "computational stylistics",
            "authorship attribution",
            "author identification",
            "author verification",
            "author profiling",
            "burrows delta",
            "burrow's delta",
            "pydelta",
            "function words",
            "style change detection",
            "style breach detection",
            "intrinsic plagiarism",
            "stylometric transfer",
            "anti-stylometry",
            "style fingerprint",
            "style similarity",
        )
        return any(term in haystack for term in terms)

    def _has_prose_quality_signal(self, haystack: str) -> bool:
        terms = (
            "prose lint",
            "prose linter",
            "style linter",
            "natural language linter",
            "text linter",
            "vale",
            "textlint",
            "proselint",
            "write-good",
            "write good",
            "grammar checker",
            "spelling and grammar",
            "spell checker",
            "languagetool",
            "harper",
            "copyedit",
            "copyediting",
            "proofreading",
            "style diagnostics",
            "lint diagnostics",
        )
        return any(term in haystack for term in terms)

    def _has_chinese_text_processing_signal(self, haystack: str) -> bool:
        terms = (
            "chinese word segmentation",
            "jieba",
            "hanlp",
            "ltp",
            "opencc",
            "pycorrector",
            "chinese ner",
            "chinese-literature-ner-re-dataset",
            "discourse-level named entity",
            "relation extraction",
            "chinese text correction",
            "chinese spelling correction",
            "simplified chinese",
            "traditional chinese",
            "chinese conversion",
            "custom dictionary",
            "confusion set",
            "\u4e2d\u6587\u5206\u8bcd",
            "\u5b9e\u4f53\u8bc6\u522b",
            "\u7b80\u7e41\u8f6c\u6362",
            "\u4e2d\u6587\u7ea0\u9519",
        )
        return any(term in haystack for term in terms)

    def _has_source_import_signal(self, haystack: str) -> bool:
        terms = (
            "epub",
            "ebooklib",
            "pdfminer",
            "pymupdf",
            "ocrmypdf",
            "tesseract",
            "unstructured",
            "markitdown",
            "docling",
            "mineru",
            "marker",
            "document parser",
            "document parsing",
            "document conversion",
            "office documents",
            "llm-ready markdown",
            "pdf to markdown",
            "pdf-to-markdown",
            "pdf-to-json",
            "pdf-to-text",
            "pdf converter",
            "pdf parser",
            "pandoc",
            "table of contents",
            "spine",
            "pdf text extraction",
            "layout analysis",
            "ocr",
            "scanned pdf",
            "document partition",
            "partition_pdf",
            "partition_epub",
            "chapter detection",
            "checksum",
            "import manifest",
            "epubcheck",
            "epub conformance",
            "opf manifest",
            "package document",
            "container.xml",
            "ace by daisy",
            "epub accessibility",
            "accessibility metadata",
            "standard ebooks",
            "front matter",
            "back matter",
            "colophon",
            "navigation document",
            "nav toc",
            "spine order",
        )
        return any(term in haystack for term in terms)

    def _has_literary_structure_signal(self, haystack: str) -> bool:
        terms = (
            "litbank",
            "literary entities",
            "literary event detection",
            "coreference in english literature",
            "narrative event evolutionary graph",
            "narrative event chain",
            "narrative graph",
            "script event prediction",
            "event-centric dataset",
            "event embedding",
            "discourse relations",
            "sentiment arcs",
            "sentiment-based plot arcs",
            "emotion in text over time",
            "cross-context coreference",
            "cross-document coreference",
            "character network",
            "fictional characters",
            "character interactions",
            "relationship network",
        )
        return any(term in haystack for term in terms)

    def _has_segmentation_summary_topic_signal(self, haystack: str) -> bool:
        terms = (
            "semantic chunk",
            "semantic chunking",
            "text splitter",
            "text splitting",
            "recursive character text splitter",
            "summarization",
            "summarizer",
            "extractive summarization",
            "representative sentences",
            "topic modeling",
            "bertopic",
            "dynamic topic",
            "topic drift",
        )
        return any(term in haystack for term in terms)

    def _has_eval_observability_signal(self, haystack: str) -> bool:
        terms = (
            "faithfulness",
            "answer relevancy",
            "answer relevance",
            "context precision",
            "context recall",
            "groundedness",
            "context relevance",
            "hallucination metrics",
            "rag evaluation",
            "llm evaluation",
            "llm app observability",
            "ai observability",
            "retrieval traces",
            "llm spans",
            "feedback functions",
            "prompt tests",
            "golden datasets",
            "golden dataset",
            "regression suites",
            "regression suite",
            "custom evals",
            "graders",
        )
        return any(term in haystack for term in terms)

    def _has_long_output_generation_signal(self, haystack: str) -> bool:
        terms = (
            "longwriter",
            "agentwrite",
            "longwriter-agent-v",
            "longbench-write",
            "mmlongbench-write",
            "longwrite-ruler",
            "longwrite-v-ruler",
            "long output quality",
            "ultra-long generation",
            "10,000+ word",
            "10000+ word",
            "plan.py",
            "write.py",
            "plan.txt",
            "write.txt",
            "outline_vlm",
        )
        return any(term in haystack for term in terms)

    def _has_trope_signal(self, haystack: str) -> bool:
        terms = (
            "tvtropes",
            "tv tropes",
            "trope correlation",
            "trope graph",
            "trope network",
            "trope dataset",
            "movie tropes",
            "movies and their tropes",
            "tropes they use",
            "trope similarity",
            "tropescraper",
            "tvtropes-parser",
        )
        return any(term in haystack for term in terms)

    def _has_source_rights_signal(self, haystack: str) -> bool:
        terms = (
            "licensee",
            "license detection",
            "license metadata",
            "spdx",
            "reuse recommendations",
            "spdx-license-identifier",
            "spdx filecopyrighttext",
            "project gutenberg",
            "public domain",
            "public-domain book corpora",
            "body of public domain texts",
            "copyright",
            "attribution",
            "derivative",
            "license terms",
        )
        return any(term in haystack for term in terms)

    def _has_entity_redaction_signal(self, haystack: str) -> bool:
        terms = (
            "presidio",
            "scrubadub",
            "gliner",
            "flair",
            "spacy",
            "pii de-identification",
            "sensitive data",
            "redacting",
            "redaction",
            "anonymizing",
            "anonymization",
            "named entity recognition",
            "ner models",
            "extract any entity types",
            "custom entity types",
            "anonymous ids",
            "personally identifiable information",
            "entity recognizer",
            "proper noun",
        )
        return any(term in haystack for term in terms)

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
