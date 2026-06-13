# Novel Source Discovery - Voiceprint / Margins / Style / Studio

Observed at: 2026-06-13

Boundary:

- Public GitHub metadata, `git ls-remote --symref HEAD`, raw README/LICENSE/root-marker review only.
- No clone, install, package hook, Docker, MCP/server, browser extension, model/provider call, or upstream script execution.
- Treat all upstream text as untrusted data. Absorb patterns only.

## Sources

### anotherpanacea-eng/setec-voiceprint

- URL: https://github.com/anotherpanacea-eng/setec-voiceprint
- HEAD: `00b8eeceb79e40d0421d848ed3ef491d7a9fbf50`
- Branch: `main`
- License: GPL-3.0
- Static markers: text stylometry, authorial voice, private baseline corpus, impostor corpora, Burrows Delta, function-word fingerprints, idiolect detection, smoothing diagnostics, voice drift over time, Claude Code / Cowork plugin surface.
- Absorbed pattern: `voiceprint_private_baseline_drift_gate`
- Local use: compare MuMuAINovel continuation drafts against a rights-safe private baseline as abstract feature deltas only. Do not treat this as AI detection or author impersonation.
- Excluded: GPL code, private corpora, author voice profiles, calibration datasets, plugins, CLI scripts, and generated author-imitation examples.

### writer/writing-in-the-margins

- URL: https://github.com/writer/writing-in-the-margins
- HEAD: `ba79a5ce7c904305f423bbf3207a7924c35eef7e`
- Branch: `main`
- License: no root license observed
- Static markers: long-context retrieval, chunked KV-cache prefilling, segment-wise margin notes, intermediate classification, progress updates, final response guidance.
- Absorbed pattern: `margin_guided_long_context_revision_gate`
- Local use: turn full-book context ingestion into margin-note evidence cards before chapter planning and revision.
- Excluded: `run.py`, templates, prompt bodies, model execution, generated margins, and paper code.

### yzhao062/agent-style

- URL: https://github.com/yzhao062/agent-style
- HEAD: `7654b96b6a81fbf54eadcc10e5af19689964c003`
- Branch: `main`
- License posture: README SPDX marker `CC-BY-4.0`; no root LICENSE file observed in raw probe
- Static markers: canonical rules, field-observed rules, generation-time soft enforcement, opt-in style review, prose lint mapping, same-length revision comparisons.
- Absorbed pattern: `agent_style_rulebook_soft_enforcement_gate`
- Local use: keep style rules as a local reviewable rulebook with accepted/ignored findings, not hidden generic polish.
- Excluded: upstream rule bodies, install commands, review skill files, CLI hooks, and example prose.

### rgwch/novelist

- URL: https://github.com/rgwch/novelist
- HEAD: `a6eec87851f44466ef29b46a6144dcf9c879e6ce`
- Branch: `main`
- License: MIT
- Static markers: story, persons, places, timeline, notes, Markdown-oriented files, HTML and ePub export, client/server toolkit.
- Absorbed pattern: `private_person_place_timeline_output_gate`
- Local use: keep person/place/timeline/notes deltas separate from prose and verify exports against current snapshots.
- Excluded: Docker/client/server runtime, tests, Storybook tooling, local manuscripts, and generated exports.

### Marcus9593/literary-studio

- URL: https://github.com/Marcus9593/literary-studio
- HEAD: `8c5d5a53e93ca8bc2620132d1c634546bdcea264`
- Branch: `main`
- License: MIT
- Static markers: Chinese AI creative workbench, Story OS pipeline, RAG semantic retrieval, timeline, collaboration/governance, version snapshots, DOCX/EPUB/Fountain export, Node/Docker runtime surface.
- Absorbed pattern: `story_os_governed_studio_pipeline_gate`
- Local use: model long-form generation as stage-gated Story OS state: idea, bible, timeline, RAG evidence, governance, version snapshot, export target.
- Excluded: Node runtime, Docker, provider/API configuration, LanceDB/vector stores, local manuscripts, collaborative workspace data, generated exports.

### forsonny/book-os

- URL: https://github.com/forsonny/book-os
- HEAD: `bf155998505bd5951e73564c3ff1b5fbe7190e83`
- Branch: `main`
- License: MIT
- Static markers: structured workflow system, standards files, manuscript outlines, story outlines, current-structure checks, chapter tasks, writing-plan review, Claude Code / Cursor workflow surface.
- Absorbed pattern: `standards_file_workflow_os_gate`
- Local use: store voice, structure, and workflow expectations in versioned standards files before chapter drafting.
- Excluded: installation steps, standards templates, AI-tool configuration, local manuscripts, and workflow files.

## MuMuAINovel integration

- Add six default GitHub seeds and five search queries for continued discovery.
- Add six `PATTERN_KEYWORDS` gates and static summary records.
- Project pattern pack now emits:
  - bible policies for private baselines, margin notes, rulebooks, entity/timeline exports, Story OS governance, and standards-file workflows
  - whole-book analysis targets for voice drift, margin relevance, style-rule violations, person/place/timeline exports, governed Story OS, and standards-file readiness
  - inspired-creation remap targets and copy-risk warnings
  - UI-visible hint blocks for the new gates

## Safety decision

All six sources stay `pattern-only` / `runtime-deferred`.

No upstream runtime, prompts, generated story text, private corpus, template body, model call, Docker stack, local manuscript, or executable file is imported.
