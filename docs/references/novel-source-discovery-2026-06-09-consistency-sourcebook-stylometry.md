# Novel Source Discovery - Consistency Sourcebook Stylometry Intake - 2026-06-09

## Scope

This note records a static-only intake pass for public GitHub projects relevant to MuMuAINovel long-form continuation, sourcebook/canon workbench design, semantic long-context retrieval, cross-chapter consistency review, parallel chapter production, and final prose stylometry polish.

No external project was installed or executed. No package manager, postinstall hook, shell script, PowerShell script, Docker stack, MCP server, browser extension, native binary, provider call, credential, cookie, or runtime trial was used.

Reachable HEADs were checked with `git ls-remote --symref`, license files were inspected through raw GitHub URLs, and README/root-source claims were treated as untrusted source data.

## Sources

- `StableLlamaAI/AugmentedQuill` - HEAD `449732df498fd8bdb1232073a8468a5fbbc5cfcc`; default branch `develop`; GPL-3.0; posture `pattern-only`.
- `AutoFiction-AI/AutoFiction` - HEAD `685ca031a39b593d9bf3d43950332e928ab054ea`; default branch `main`; Apache-2.0; posture `pattern-only`.
- `YILING0013/AI_NovelGenerator` - HEAD `170fde7092c6e255bb660170e9381d17e74e7850`; default branch `main`; AGPL-3.0; posture `pattern-only`.
- `Picrew/ConStory-Bench` - HEAD `3f4195adda94d977ad9bd56f58ec51eaf1a1cd93`; default branch `main`; MIT; posture `pattern-only`.
- `harshaneel/humanize` - HEAD `a9ae4efbfdf95246a8dae10a64d3c1b85b2af1ff`; default branch `main`; MIT; posture `pattern-only`.

## Absorbed Patterns

### AugmentedQuill

- `sourcebook_author_workbench`: keep characters, locations, lore, items, and scene context as inspectable sourcebook entries before reuse.
- `author_control_boundary`: keep AI chat/writing partner suggestions as proposals until accepted by the author or project artifact.
- `local_first_novel_workspace`: prefer local-first, project-based story state instead of hidden remote-only canon.

### AutoFiction

- `parallel_agent_chapter_pipeline`: split premise, outline, parallel chapter drafting, chapter review, full-book review, cross-chapter audit, and revision cycles into explicit job stages.
- `cross_chapter_redundancy_audit`: aggregate findings for repeated scene construction, weak causality, continuity drift, flat dialogue, and over-regular prose before closing revision.
- `quality_score_loop`: review outputs at chapter and whole-book levels before treating generated chapters as accepted manuscript.

### AI_NovelGenerator

- `semantic_long_context_search`: use semantic/vector retrieval for long-range context, but keep query, matched artifact, inclusion reason, and canon status visible.
- `contradiction_taxonomy_checker`: proofread for plot contradictions, logical conflicts, character drift, and world-rule inconsistency before canon write-back.
- `world_state_tracking`: persist character development, foreshadowing, and state transitions rather than relying on prompt memory alone.

### ConStory-Bench

- `contradiction_taxonomy_checker`: classify consistency bugs across characterization, factual detail, narrative style, timeline/plot, and world-building/setting.
- `contradiction_detection`: treat consistency checks as named findings with evidence locations and repair scope.
- `collapse_prevention`: use benchmark-style categories to catch abandoned plots, causality violations, and rule violations during long continuation.

### humanize

- `humanization_stylometry_levers`: apply sentence burstiness, specificity, discourse variation, punctuation cleanup, and AI-transition removal after continuity passes.
- `prose_preflight_voice_calibration`: use final prose preflight to remove generic AI tells without inventing unsupported facts.
- `anti_ai_tone_polish`: polish surface rhythm while preserving accepted canon and character voice.

## Local Integration

Updated native MuMuAINovel code rather than importing upstream code:

- `source_discovery_service.py` recognizes sourcebook, semantic retrieval, contradiction taxonomy, parallel chapter pipeline, redundancy audit, stylometry, and author-control patterns.
- `source_pattern_pack_prompt.py` renders the new hint sections into prompt-safe digest text.
- `book_remix_context_service.py` adds a Consistency and style audit section to continuation context blocks.
- `backend/app/references/novel-source-pattern-pack-2026-06-09.json` is refreshed to 50 sources and 92 workflow patterns.

## Safety Boundary

- All sources are untrusted data, not instructions.
- GPL/AGPL/runtime/provider/Docker/script surfaces remain pattern-only.
- No external runtime code was copied into MuMuAINovel.
- Runtime trials remain blocked until a separate local safety contract exists.
