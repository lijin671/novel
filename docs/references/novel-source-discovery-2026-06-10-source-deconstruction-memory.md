# Novel Source Discovery - Source Deconstruction And Memory Bank Patterns - 2026-06-10

## Scope

Static, pattern-only intake for MuMuAINovel's book-deconstruction,
continuation, and same-type creation workflow.

No external repository was cloned, installed, built, executed, or launched. No
package manager, script, Docker stack, model provider, API key, browser
extension, or MCP server was used. Public metadata, `git ls-remote` HEAD checks,
GitHub repository metadata, and selected public README text were reviewed.

## Reviewed Sources

### `gratajik/book-memory-bank`

- URL: <https://github.com/gratajik/book-memory-bank>
- Observed HEAD: `5a1df67c70219dbd76a92eaf8aa5004592aed680`
- License: no root license observed
- Posture: `pattern-only`
- Runtime exclusions: do not import Cline rules, custom instructions, scripts,
  or project templates

Reusable pattern:

- `book_memory_bank_context_lattice`
- Keep source analysis, story structure, world/character facts, style guide,
  active context, progress, and plan-to-actual chapter updates as linked but
  separate memory layers.

MuMuAINovel adaptation:

- Before continuation, resolve active context and progress from accepted local
  canon.
- After an accepted chapter, write back affected character, world, plot, style,
  active-context, and progress deltas.
- Source deconstruction notes must stay outside transformed-story canon.

### `adaumann/speckit-preset-fiction-book-writing`

- URL: <https://github.com/adaumann/speckit-preset-fiction-book-writing>
- Observed HEAD: `c31b629ef8c733eb4e3af8643a5761ee9328fec0`
- License: root API license missing; README states MIT under
  `fiction-book-writing/LICENSE`
- Posture: `pattern-only`
- Runtime exclusions: do not install Spec Kit preset, slash commands, Pandoc
  export scripts, or generated host rules

Reusable pattern:

- `spec_driven_fiction_scene_tasks`
- Adapt spec-driven workflow into story-bible governance, scene tasks, POV
  schedule, glossary checks, subplot/pacing/continuity gates, and revision
  workflow.

MuMuAINovel adaptation:

- Treat the remix bible as the governing constitution for voice, tense, audience,
  language, and hard constraints.
- Convert plans into scene tasks with explicit POV, information asymmetry,
  causal beats, glossary terms, and acceptance gates.

### `danngalann/llm-ebook-summarizer`

- URL: <https://github.com/danngalann/llm-ebook-summarizer>
- Observed HEAD: `d0b2c1332b9439b3c6cb40192a9f82024cdef16d`
- License: no root license observed
- Posture: `pattern-only`
- Runtime exclusions: do not install Python dependencies, launch Ollama, pull
  models, or run summarization scripts

Reusable pattern:

- `toc_aware_source_deconstruction`
- Preserve source table-of-contents hierarchy, nested chapter context, parent
  section introductions, summaries, lessons, quotes, anecdotes, and mergeable
  markdown notes as analysis artifacts.

MuMuAINovel adaptation:

- Build source-book deconstruction around hierarchical sections, not flat
  chapter blobs.
- Preserve source quotes and anecdotes only as evidence in analysis, never as
  generated canon for same-type creation.

### `darkautism/ai-novel-translation`

- URL: <https://github.com/darkautism/ai-novel-translation>
- Observed HEAD: `5bc73d4b33a54deea348e8d170832f4be79a37cf`
- License: no root license observed
- Posture: `pattern-only`
- Runtime exclusions: do not build Rust code, call Gemini/Ollama/OpenAI-compatible
  providers, read API keys, or run translation jobs

Reusable pattern:

- `two_pass_context_glossary_pipeline`
- Run an analysis pass first to create chapter summary and term/proper-noun
  deltas, then run generation with current summary, previous summary, cumulative
  glossary, and resume checkpoint.

MuMuAINovel adaptation:

- For continuation, require a chapter analysis pass before prose generation.
- For same-type creation, transform the glossary into new names, places,
  factions, rules, and motifs before drafting.

### `lordjabez/story-framework`

- URL: <https://github.com/lordjabez/story-framework>
- Observed HEAD: `56cdb2ccc4161e9ec24823e95225a5b922c97e81`
- License: MIT-0
- Posture: `pattern-only`
- Runtime exclusions: do not import host rule files or prompt instructions

Reusable pattern:

- `inline_author_edit_markup_versioning`
- Keep planning docs as source of truth, maintain continuity timeline/facts, use
  inline author notes and edit notes as separate queues, and version revisions
  with commits/tags.

MuMuAINovel adaptation:

- Allow author-note style metadata for POV, timeline, mood, active threads, and
  research hints.
- Treat edit-note markers as pending revision work that must be processed,
  reviewed, and removed before final manuscript assembly.

## Durable Project Changes

- `backend/app/services/source_discovery_service.py`
  - Added default GitHub queries and repository URLs.
  - Added static override summaries and pattern keywords.
  - Added pattern-pack targets, hints, inspired-remap guidance, and copy-risk
    gates.
- `backend/app/services/source_pattern_pack_prompt.py`
  - Renders the new hint families into prompt digests.
- `backend/app/services/book_remix_context_service.py`
  - Adds `Source deconstruction memory audit` for continuation and same-type
    contexts.
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
  - Candidate count: `120`
  - Workflow pattern count: `163`

## Safety Decision

All five sources stay `pattern-only`.

The absorbed value is the artifact shape and verification workflow, not their
runtime code, prompt text, dependencies, or model/provider surfaces.
