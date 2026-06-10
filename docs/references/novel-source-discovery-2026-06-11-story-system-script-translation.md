# Novel Source Discovery - 2026-06-11 Story System / Screenplay / Translation Static Review

## Boundary

`public_github_story_system_script_translation_static_head_raw_readme_license_no_login_no_clone_no_runtime_20260611`

This pass used public GitHub metadata, `git ls-remote --symref`, raw
README/LICENSE reads, and compact marker counts only.

It did not clone, install packages, execute scripts, launch GUIs/desktops, run
browser workbenches, call OpenAI/Gemini/other providers, read credentials, read
local novels, or import upstream prompt/code/text bodies.

Static cache:

- `tmp/source-intake-20260611-story-system-script-translation-static-review.json`

## Reviewed sources

### `bybren-llc/story-systems-template`

- URL: <https://github.com/bybren-llc/story-systems-template>
- HEAD: `e4ddd291a5d708737c2e7a97d541fd7f837d195c`
- Default branch: `main`
- License marker: MIT
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - writers' room as role-separated review structure
  - roles with stop authority
  - shared knowledge sync
  - Fountain/screenplay export as downstream held artifact
- Absorbed as: `writers_room_stop_authority_gate`
- Runtime excluded:
  - no npm/CLI runtime
  - no GUI launch
  - no provider platform call
  - no upstream sync
  - no generated screenplay artifact import

### `1want2beaQuant/ai-novel2script`

- URL: <https://github.com/1want2beaQuant/ai-novel2script>
- HEAD: `d17522da1809d41c1419afb0c693db58da08ca5f`
- Default branch: `main`
- License marker: MIT
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - 3+ chapter preflight
  - novel paragraph to act/scene/action/dialogue/transition map
  - `structure_map`
  - `story_bible`
  - `adaptation_report`
  - `coverage_report`
  - quality gates before Fountain/YAML/Markdown export
- Absorbed as: `novel_to_screenplay_structure_coverage_gate`
- Runtime excluded:
  - no Python package install
  - no web workbench launch
  - no OpenAI-compatible enhancement
  - no export runtime

### `Shirochi-stack/Glossarion`

- URL: <https://github.com/Shirochi-stack/Glossarion>
- HEAD: `224b6c07be07991bb880fd395b0b9ac8f311080f`
- Default branch: `main`
- License marker: MIT
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - contextual translation
  - glossary system
  - quality assurance suite
  - EPUB rebuild as held artifact
  - duplicate detection
  - provider and credential surfaces separated from analysis
- Absorbed as: `translation_glossary_context_qa_gate`
- Runtime excluded:
  - no PySide GUI launch
  - no provider calls
  - no credential/API-key use
  - no local LLM
  - no manga/image translation runtime
  - no EPUB rebuild runtime

### `oodadoudou/Transoria`

- URL: <https://github.com/oodadoudou/Transoria>
- HEAD: `21da5f85adf2c3ba677ea028921db21449cc8ab0`
- Default branch: `main`
- License marker: no raw LICENSE observed
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - term extraction and term review
  - translation/proofreading/task IDs
  - resume/retry
  - batch and regex replacement
  - source-residue / low-confidence / adjacent-duplicate labels
  - copyright/right-use warnings
- Absorbed as: `desktop_translation_batch_replacement_boundary_gate`
- Runtime excluded:
  - no installer
  - no desktop shell
  - no source runtime
  - no user API keys
  - no local file reads
  - no EPUB operation

## Project fusion

The promoted patterns were fused into:

- default GitHub seed URLs
- default GitHub query vocabulary
- static repository pattern summaries
- `PATTERN_KEYWORDS`
- source pattern pack hints
- bible enrichment targets
- whole-book analysis targets
- same-type/inspired remap targets
- source pattern pack prompt digest
- service regression test

## New gates

- `writers_room_stop_authority_gate`
  - makes stop-authority and role objection resolution explicit before chapter
    promotion or screenplay export.
- `novel_to_screenplay_structure_coverage_gate`
  - maps source chapters to screenplay structure and coverage reports before
    any adaptation artifact is accepted.
- `translation_glossary_context_qa_gate`
  - separates glossary, context, provider settings, QA, and EPUB rebuild notes.
- `desktop_translation_batch_replacement_boundary_gate`
  - treats batch replacement, retry/resume, low-confidence groups, and
    source-residue warnings as review gates.

## Verification

RED:

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_story_system_script_translation_sources_map_to_adaptation_gates -q
```

Expected failure was the missing default repository seed.

GREEN:

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_story_system_script_translation_sources_map_to_adaptation_gates -q
```

Result: `1 passed`.
