# Novel Source Discovery - 2026-06-13 Phase Acceptance / Local Continuation / Verification

## Scope

This note records a public, static GitHub source-intake pass for MuMuAINovel.
The lane is long-form novel automation, with emphasis on拆书续写, same-type
inspired writing, acceptance gates, local continuation memory, multi-agent
review, sensory continuation, and character/backstory verification.

Boundary:

```text
public_github_novel_phase_acceptance_continuation_verification_static_lsremote_raw_marker_no_login_no_clone_no_runtime_2026_06_13
```

No repository was cloned, installed, built, imported, or executed. No package
manager, Docker stack, MCP server, browser extension, model/provider call,
Ollama pull, vector server, CLI command, script, EPUB build, or credential read
was run. Review used only public GitHub Search metadata when available,
`git ls-remote --symref HEAD`, raw README marker scans, and raw root-file marker
checks.

## Promoted pattern-only sources

### tobyilee/book-writer

- Source: https://github.com/tobyilee/book-writer
- Observed HEAD: `13a35a72c02e1eaba913333d5a6610b252fd7a20`
- Default branch: `main`
- Search signal: 70 stars, MIT license
- Static markers: `README.md`, `LICENSE`, `CLAUDE.md`
- Posture: `pattern-only`
- Absorbed pattern: `phase_acceptance_epub_delivery_gate`

Reusable pattern:

- Treat book production as a phase-gated harness.
- Keep `book_manifest.json`, `story_bible.md`, append-only `style_log.md`,
  review logs, acceptance verdicts, and delivery validators tied to one book
  version.
- Separate creative state from export/build state.
- EPUB/DOCX/Markdown delivery consumes accepted chapters only.

Runtime exclusions:

- Claude Code agents/skills, `CLAUDE.md` instruction bodies, scripts,
  pandoc/epubcheck execution, cover generation, generated books, and manuscript
  outputs are not imported or executed.

### kino-6/novelcraft-agent

- Source: https://github.com/kino-6/novelcraft-agent
- Observed HEAD: `d40557b1f5f4fec8e9700736bd1c0219966863b4`
- Default branch: `main`
- Search signal: 0 stars, Apache-2.0 license
- Static markers: `README.md`, `LICENSE`, `pyproject.toml`
- Posture: `pattern-only`
- Absorbed pattern: `local_continuation_memory_export_gate`

Reusable pattern:

- Treat local novel continuation as a pass pipeline: Analyzer, Director,
  skill-selection, Writer, and light Polish.
- Save a compact `story_memory.json` alongside every run.
- Keep continuation-only output separate from source-plus-continuation output.
- Preserve source checksum and preview/mock state for replayable admission.

Runtime exclusions:

- uv/Python setup, Ollama model pulls, CLI execution, generated continuation
  files, `story_memory.json` runtime state, and local source novels are not
  imported or executed.

### xiehuanyi/NovelForge

- Source: https://github.com/xiehuanyi/NovelForge
- Observed HEAD: `df4cb9887eb7cbac639eb62196618540f56864ed`
- Default branch: `main`
- Search signal: 1 star, no license file observed in this pass
- Static markers: `README.md`, `requirements.txt`
- Posture: `pattern-only`
- Absorbed pattern: `six_agent_memory_debate_consistency_gate`

Reusable pattern:

- Use a six-role split for long-form generation: world, character, outline,
  writer, editor, and memory manager.
- Make Writer-Editor debate produce a score, revision reason, and acceptance
  decision before memory is updated.
- Keep working, episodic, and semantic memory as separate state lanes.
- Consistency checks become acceptance evidence, not decorative review text.

Runtime exclusions:

- requirements installs, TUI/headless runtime, provider/API keys, vector/RAG
  stores, generated examples, scripts, prompt bodies, and runtime state are not
  imported or executed.

### DeadMark70/Novel_Continuation_Studio

- Source: https://github.com/DeadMark70/Novel_Continuation_Studio
- Observed HEAD: `d465e6158f022f11f3a86cfbdcc3f246bb58fd11`
- Default branch: `master`
- Search signal: 0 stars, Apache-2.0 license
- Static markers: `README.md`, `LICENSE`, `package.json`, `AGENTS.md`
- Posture: `pattern-only`
- Absorbed pattern: `multi_phase_sensory_continuation_gate`

Reusable pattern:

- Gate continuation through Compression, Analysis, Outline, Breakdown, and
  Drafting.
- Treat sensory anchors as late-bound scene hints with cooldown memory and
  explicit manual override.
- Maintain character timelines and a foreshadow ledger across chapters.
- Distinguish manual, full-auto, and range modes before batch generation.

Runtime exclusions:

- npm/package scripts, `AGENTS.md` instructions, provider keys, generated
  chapters, UI state, local corpora, and runtime exports are not imported or
  executed.

### parijat1222q/Agentic-Verification-Pipeline

- Source: https://github.com/parijat1222q/Agentic-Verification-Pipeline
- Observed HEAD: `5e297ec3754edca78423dfca232a634fd143c49e`
- Default branch: `main`
- Search signal: 0 stars, no license file observed in this pass
- Static markers: `README.md`, `requirements.txt`, `Dockerfile`
- Posture: `pattern-only`
- Absorbed pattern: `agentic_backstory_verification_rag_gate`

Reusable pattern:

- Verify imported or generated backstory as claims.
- Split the verifier into claim extraction, investigation, and judging.
- Store retrieved evidence ids, reranker notes, reasoning trace, and unresolved
  gaps before promoting facts to canon.
- Use verification reports to block contradictory character history.

Runtime exclusions:

- Docker, vector server, Gemini/API-key runtime, datasets, requirements installs,
  generated `results.csv`, and source novel contents are not imported or
  executed.

## Deferred source

### LAY-lgtm/novel-writing-framework

- Source: https://github.com/LAY-lgtm/novel-writing-framework
- Observed HEAD: `76291596ae91047743fc620b9647971f034acf7a`
- Default branch: `master`
- Search signal: 84 stars, MIT license
- Decision: defer

Reason:

- Public raw markers were too sparse for a new durable pattern beyond existing
  Chinese novel-skill framework coverage.
- Keep as a future candidate if a later pass finds clearer architecture,
  artifact, or verifier boundaries.

## Local projection

Updated MuMuAINovel source discovery so the new patterns can appear in:

- default GitHub direct-source seeds
- default GitHub search queries
- static repository summaries
- pattern keyword detection
- pattern-pack hints
- same-type inspired remapping guidance
- frontend type surface and discovery panel display
- service and frontend coverage tests

The projection remains pattern-only. It does not grant runtime permission.
