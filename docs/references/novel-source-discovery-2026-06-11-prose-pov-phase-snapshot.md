# Novel Source Discovery - Prose POV Phase Snapshot Review

Observed at: 2026-06-11T02:20:00+08:00

Boundary:

```text
public_github_lsremote_raw_readme_license_marker_scan_no_login_no_clone_no_runtime
```

This pass used public `git ls-remote` HEAD checks plus raw README/LICENSE/root
marker reads. It was static intake only.

No repository was cloned, installed, built, executed, or launched. No package
manager, PyPI install, CLI run, web app, pretrained model, notebook, terminal
binary, Bund script, provider call, API key, token, cookie, browser storage,
local manuscript, or ebook corpus was used.

Cache:

- `tmp/source-intake-20260611-prose-pov-style-static-review.json`

## Source Snapshot

- `prosegrinder/python-prosegrinder`
  - HEAD: `c30f221e031eac2e25d1aed7b985f950659d92dd`
  - Default branch: `main`
  - License marker: GPL-3.0.
  - Static markers: prose text counter, word/sentence/paragraph/syllable
    counts, point-of-view, dialogue, narrative, readability scores, JSON output
    with file hash.
  - Posture: `pattern-only / PyPI-and-CLI-runtime-deferred`

- `oxinabox/NovelPerspective`
  - HEAD: `f65807441d82bef17ba939b15581158f807b9606`
  - Default branch: `master`
  - License marker: MIT.
  - Static markers: ebook chapter POV-character identification, character
    story-line include/exclude transform, copyright-sensitive evaluation data
    omission, web app and pretrained model surface.
  - Posture: `pattern-only / ebook-webapp-model-runtime-deferred`

- `d-wwei/great-writer`
  - HEAD: `266bfd6ec26e5dedd23cd4b569e034b50b58d463`
  - Default branch: `main`
  - License marker: MIT.
  - Static markers: bilingual AI-agent writing system, six-phase pipeline,
    nine writing modes, fifteen writing principles, four-pass polish, AI-trace
    removal.
  - Posture: `pattern-only / upstream-prompt-runtime-deferred`

- `vulogov/blackInkhaven`
  - HEAD: `c6203062b8d3780796b0a428c18b5f8ba1e51c1e`
  - Default branch: `main`
  - License marker: Unlicense / public-domain dedication.
  - Static markers: terminal book-writing app, hierarchical Typst text nodes,
    local DuckDB metadata, full-text/semantic index, versioned snapshots,
    backups, lexicon books for characters/places/artefacts, Bund scripts, LLM
    provider routing.
  - Posture: `pattern-only / binary-script-provider-runtime-deferred`

Reviewed but not promoted in this slice:

- `mshumer/gpt-author`
  - Useful as a single-run novel generator reference, but the README surface is
    dominated by provider calls, notebooks, Stable Diffusion, EPUB generation,
    and API-key setup. Existing generation/export gates already cover the safe
    portions.
- `chapelR/serious`
  - Public HEAD and license were reachable, but no root README was available in
    this pass. It stays unpromoted until there is clearer original-source
    evidence.

## Absorbed Patterns

- `prose_metric_pov_dialogue_gate`
  - Treat POV, dialogue, narrative, sentence, paragraph, and readability
    metrics as review evidence for拆书、续写 and same-type writing.
  - Metrics are baselines and outlier signals, not source-copy targets.

- `pov_character_thread_filter_gate`
  - Map chapters to active POV characters and character threads before trimming
    source context.
  - POV filters may help analysis, but cannot delete canon required for
    faithful continuation.

- `agent_writing_phase_polish_gate`
  - Separate thinking, drafting, and polish passes.
  - AI-trace removal happens after canon, causality, and source-boundary gates.

- `hierarchical_semantic_snapshot_workspace_gate`
  - Model long manuscripts as stable book/chapter/subchapter/paragraph nodes.
  - Retrieval and rewrite prompts must cite node id, snapshot id, boundary label,
    and inclusion reason.

## MuMuAINovel Adaptation

- Discovery defaults now include the four promoted repositories and focused
  GitHub searches for:
  - POV/dialogue/narrative prose metrics
  - POV-character thread filtering
  - phase/polish writing systems
  - hierarchical semantic indexes and versioned snapshots
- Pattern packs now expose:
  - `prose_metric_pov_dialogue_gate_hints`
  - `pov_character_thread_filter_gate_hints`
  - `agent_writing_phase_polish_gate_hints`
  - `hierarchical_semantic_snapshot_workspace_gate_hints`
- Bible enrichment now includes prose metric baseline policy, POV-thread maps,
  phase/polish mode policy, and hierarchical text-node snapshot policy.
- Whole-book analysis now includes POV/dialogue/narrative metric reports,
  POV-thread filter reports, phase-polish AI-trace reports, and hierarchical
  snapshot reports.
- Same-type creation now remaps POV/dialogue metric ranges, POV thread filters,
  phase/polish modes, and snapshot namespaces before drafting.

## Deferred / Runtime Gates

- Do not install Prosegrinder from PyPI or run its CLI during source intake.
- Do not launch NovelPerspective web app, ebook transforms, pretrained models,
  or corpus preprocessing.
- Do not import Great Writer prompt bodies or run upstream agents.
- Do not launch Inkhaven, run Bund scripts, invoke provider routing, read local
  manuscripts, or touch semantic indexes outside this project.
- Do not use any upstream generated prose, ebook content, prompt body, model
  output, or local manuscript data as MuMuAINovel canon.

## Verification

- RED:
  `python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_prose_pov_phase_snapshot_sources_map_to_source_study_gates -q`
  failed before defaults and gates existed.
- GREEN:
  `python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_prose_pov_phase_snapshot_sources_map_to_source_study_gates -q`
  passed after implementation.
