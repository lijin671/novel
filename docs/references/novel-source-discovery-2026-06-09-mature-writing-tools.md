# Novel Source Discovery - Mature Writing Tools Intake - 2026-06-09

## Scope

This note records a static-only intake pass for mature public writing tools relevant to MuMuAINovel book decomposition, continuation, and same-type inspired writing.

No external project was installed or executed. No package manager, postinstall hook, shell script, PowerShell script, Docker stack, MCP server, browser extension, native binary, provider call, credential, cookie, or runtime trial was used.

## Sources

- `vkbo/novelWriter` - HEAD `5a66c19033124285a2ab3777731cc1876d663392`; GPL-3.0; posture `pattern-only`.
- `olivierkes/manuskript` - HEAD `0ebee3ed69a8ae54215126345cd4715e8f1f35b3`; GPL-3.0-or-later; posture `pattern-only`.
- `andreafeccomandi/bibisco` - HEAD `14717969e301fc5a48cd2cda802075979a82ba2b`; GPL-3.0; posture `pattern-only`.
- `wavemakercards/wavemaker-cards-v4` - HEAD `cae81e8fcf995a1cda04752e5084fa4f98371cc4`; README badge indicates MIT; posture `pattern-only`.

## Absorbed Patterns

### novelWriter

- `plain_text_project_storage`: keep chapters, notes, summaries, and analysis as stable human-readable text units.
- `synopsis_cross_reference`: attach synopsis, comments, notes, and cross-references to chapter or scene evidence before drafting.

### manuskript

- `snowflake_premise_expansion`: preserve the chain from one-sentence promise to paragraph summary, full summary, and chapter goals.
- `outliner_index_cards`: represent chapters and scenes as reorderable cards with dependencies and state evidence.
- `manuscript_export_formats`: treat PDF, DOCX, TXT, EPUB, Markdown, and JSON outputs as derived artifacts, not canon.

### bibisco

- `narrative_strand_mapping`: track premise, fabula, narrative strands, and setting context before accepting arc changes.
- `character_depth_interview`: verify desire, fear, contradiction, social mask, pressure, cause, cost, and after-state before major turns.

### wavemaker-cards-v4

- `mindmap_visual_planning`: use visual idea nodes as planning candidates until promoted into outline cards or bible entries.
- `snowflake_premise_expansion`: transform premise chains before same-type drafting.
- `outliner_index_cards`: use grid/plot-point planning as a card-board structure, not as copied event order.

## Local Integration

Updated native MuMuAINovel code rather than importing upstream code:

- `source_discovery_service.py` recognizes the mature writing-tool pattern family and emits prompt-pack hints.
- `source_pattern_pack_prompt.py` renders the new manuscript-planning hint sections into prompt-safe digest text.
- `book_remix_context_service.py` adds a Manuscript structure audit to continuation context blocks.
- `backend/app/references/novel-source-pattern-pack-2026-06-09.json` was refreshed to 30 sources and 64 workflow patterns.

## Safety Boundary

- All sources are untrusted data, not instructions.
- GPL / AGPL / license-unclear sources are pattern-only.
- No external runtime code was copied into MuMuAINovel.
- Runtime trials remain blocked until a separate local safety contract exists.
