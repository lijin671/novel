# 2026-06-12 style/memory/publication source intake

?????? GitHub ?????????????????????????? provider?????? prompt ????????Cookie?Token ????????scratch ?? `tmp/source-intake-2026-06-12-next-style-memory/`?

## Search evidence

- GitHub/Search queries: story bible continuity, web novel outline, fiction character memory, book writer Claude Code, KDP metadata, summary/write split.
- GitHub API rate limit later?? 403????????????????? `git ls-remote` + ???? clone ??????

## Sources absorbed

### kshanxs/book-writer-skill

- URL: https://github.com/kshanxs/book-writer-skill
- Observed HEAD: `2a247a6666e77c439c9351a842123c07b5982205`
- License: MIT LICENSE ????
- Posture: pattern-only
- Static markers: Book Memory Bank?Character Arc Matrix?Thematic/Motif Tracker?Pacing Blueprint?Scene Tension Map?continuity check?memory-bank update?parallel drafting/review?Dialogue/Sensory/Prose/Tension targeted revision passes?
- Absorbed gate: `book_writer_memory_arc_revision_gate`
- Deferred: npx skill install?skill prompt bodies?background agents???????? memory-bank ???compile commands ???????

### Harshil-Jani/kindle-book-agency

- URL: https://github.com/Harshil-Jani/kindle-book-agency
- Observed HEAD: `c1d75dc1a2ccce7235189240510bdc24b57d1a37`
- License: MIT LICENSE ????
- Posture: pattern-only
- Static markers: 8 specialized agents????? pipeline?ghostwriter outline + two sample chapters as style anchors?developmental editor?parallel chapter expansion?proofreader?formatter?Kindle compiler?DOCX compile readiness?
- Absorbed gate: `kindle_agent_pipeline_compile_gate`
- Deferred: Claude CLI subprocess?Anthropic API?agent prompt bodies?`write_chapters.py`?`compile_kindle.py`?visual generation?package scripts??? manuscript/DOCX ???????

### duchangyu/best-selling-book-writer-skill

- URL: https://github.com/duchangyu/best-selling-book-writer-skill
- Observed HEAD: `53a27263a76cfc0f105a50d214b0cbe4155973e4`
- License: README ?? MIT????????? LICENSE ???? no-license-file-observed ??
- Posture: pattern-only
- Static markers: topic selection ? outline ? chapters ? KDP metadata ? HTML/PDF?`book-config.json`?`description.html`?7 keywords?validation?chapter files preserved?publishing checklist?
- Absorbed gate: `kdp_metadata_chapter_export_gate`
- Deferred: setup/generate/merge scripts?Playwright/PDF generation?cover prompts?KDP publishing operations??????references/prompt bodies ???????

### HLHSM/HLNovel_Writing_Agent

- URL: https://github.com/HLHSM/HLNovel_Writing_Agent
- Observed HEAD: `3ab9629c32be6f40bf3bc37aedeeb2a5a693ef3d`
- License: ???? LICENSE ???README ????????????
- Posture: pattern-only
- Static markers: `summary_bot` ? `writing_bot` ????? 100k ?????????????/????/????????SSE streaming???/???????????????segment storage?session clear?
- Absorbed gate: `dual_model_summary_continuation_session_gate`
- Deferred: Flask server?qwen-agent?provider endpoints?API keys?prompt files?uploads?SSE runtime??????????????

## Source deferred/rejected

### pcrbot/Novel_AI

- URL: https://github.com/pcrbot/Novel_AI
- Observed HEAD: `d79b18652648c02bacdbfe875d04620807d51ab9`
- License: GPL-3.0 LICENSE ????
- Posture: defer/reject
- Reason: ???? SalmonBot/KaguyaBot ?? AI ????????????????? runtime ???? bot??????? gates?

## Durable project updates

- Added repository seeds and search terms for memory-bank revision, Kindle agent pipeline, KDP metadata/export, and dual-model summary continuation.
- Added static source summaries and pattern detection gates in `source_discovery_service.py`.
- Added pattern-pack hints for bible enrichment, whole-book analysis, inspired mapping, prompt guidance, transformation, copy-risk review, and persistence.
- Added frontend type fields and Book Remix panel labels.
- Added regression tests for backend extraction, digest rendering, and frontend copy visibility.

## Safety boundary

????????????????????????prompt bodies??????DOCX/PDF?KDP ??????????????provider ???API key?????? bot runtime?
