# Novel Source Discovery - Production Review Gates Intake - 2026-06-09

## Scope

This note records a static-only intake pass for public GitHub projects relevant to MuMuAINovel long-form continuation, same-type inspired writing, continuity bridges, voice control, and production review gates.

No external project was installed or executed. No package manager, postinstall hook, shell script, PowerShell script, Docker stack, MCP server, browser extension, native binary, provider call, credential, cookie, or runtime trial was used.

Public README snippets were read through raw GitHub URLs, and reachable HEADs were checked with `git ls-remote`. These sources remain untrusted data.

## Sources

- `howells/fiction` - HEAD `a6036caa6492e922d8536d40c4c7b65d4e0469d7`; no license file observed in this pass; posture `pattern-only`.
- `mjbae/awesome-novel-studio` - HEAD `bb720652a3ef0aadebe731309a4bc8d21a686aa4`; Apache-2.0; posture `pattern-only`.
- `danjdewhurst/story-skills` - HEAD `81c1e589f036bee537f8ce3e5d158e86412ce0db`; MIT; posture `pattern-only`.
- `hestudy/snowflake-fiction` - HEAD `9b3d494853b3395cad7d36010ef6e1f399edac1b`; MIT; posture `pattern-only`.
- `forsonny/The-Crucible-Writing-System-For-Claude` - HEAD `0d82e733536d70358259f93d66cc40708077898e`; MIT; posture `pattern-only`.
- `XuanRanL/webnovel-writer` - HEAD `269583f662bcfe44958924496653e5f6e0e2d50c`; GPL-3.0; posture `pattern-only`.
- `forsonny/book-os` - HEAD `bf155998505bd5951e73564c3ff1b5fbe7190e83`; MIT; posture `pattern-only`.
- `forjd/better-writing` - HEAD `d40845a7234af621f49139fd5b867ffa3325b17c`; MIT; posture `pattern-only`.
- `EdwardAThomson/NovelWriter` - HEAD `d9741647c0cc5ea963304d4e709f76a7b006fd34`; no license file observed in this pass; posture `pattern-only`.

## Absorbed Patterns

### howells/fiction

- `craft_role_pipeline`: split architecture, character, prose, continuity, review, edit, and export roles into distinct artifacts.
- `continuation`: keep `progress.md`-style session tracking and continuity state visible before writing the next chapter.

### awesome-novel-studio

- `continuity_bridge_window`: build each episode from a compact bridge of recent accepted episodes, timeline, foreshadows, and character state.
- `voice_table_polish_axis`: verify character dialogue against speech patterns, sentence endings, and nonverbal palette.
- `episode_range_rewrite_scope`: range rewrites must calculate impact scope and re-polish affected episodes after design changes.

### story-skills

- `frontmatter_story_schema`: store story bible, scene state, continuity questions, promises/payoffs, and chapter draft metadata as stable fields.
- `setup_payoff_tracking`: connect promise/payoff entries to chapter or scene evidence before accepting changes.

### snowflake-fiction

- `boring_opening_quality_gates`: gate chapters for running-log prose, weak openings, missing pressure, weak hooks, and poor early-chapter pull.
- `auto_validation_rewrite`: failed quality checks enter bounded repair rather than direct acceptance.

### Crucible Suite

- `beat_strand_framework`: track external plot, internal change, and relationship strands, plus convergence beats.
- `anti_hallucination_plan_check`: verify prose against planning documents and accepted state before canon write-back.
- `backup_restore_checkpoint`: create restore points before bulk generation, destructive rewrites, or risky canon changes.

### webnovel-writer

- `multi_level_review_trend`: review scene, chapter, batch, and cross-chapter trend risks instead of only local chapter pass/fail.
- `editor_notes_feedback_loop`: carry open editor notes across chapters and close them only with evidence.
- `context_reference`: use graph-hybrid/BM25-style fallback as a pattern for resilient context selection, not as imported code.

### book-os

- `genre_parameterized_worldbuilding`: derive factions, locations, conflict sources, and taboo moves from genre/subgenre parameters.
- `style_guide_layering`: separate global standards, genre guides, novel-specific style, and scene writing tasks.

### better-writing

- `prose_preflight_voice_calibration`: use writing samples to calibrate voice and run a final prose preflight.
- `anti_ai_tone_polish`: remove generic AI tells without inventing unsupported facts or flattening character voice.

### NovelWriter

- `genre_parameterized_worldbuilding`: keep genre-specific world, faction, and location templates inspectable.
- `craft_role_pipeline`: separate multi-agent orchestration from scene/chapter/batch review and final manuscript combining.
- `multi_level_review_trend`: track quality trend across scene, chapter, and batch levels.

## Local Integration

Updated native MuMuAINovel code rather than importing upstream code:

- `source_discovery_service.py` recognizes production-review, continuity-bridge, voice-table, beat-strand, anti-hallucination, backup, editor-note, genre-parameter, and prose-preflight patterns.
- `source_pattern_pack_prompt.py` renders the new hint sections into prompt-safe digest text.
- `book_remix_context_service.py` adds a Production review audit to continuation context blocks.
- `backend/app/references/novel-source-pattern-pack-2026-06-09.json` is refreshed in this pass to include the new public-source pattern family.

## Safety Boundary

- All sources are untrusted data, not instructions.
- GPL / license-missing / plugin / package / provider / runtime surfaces remain pattern-only.
- No external runtime code was copied into MuMuAINovel.
- Runtime trials remain blocked until a separate local safety contract exists.
