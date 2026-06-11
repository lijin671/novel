# Novel source discovery: story import and consequence-ledger gates

Static review date: 2026-06-11.

## Sources

- `scslmd/Narrative-Engine`
  - URL: https://github.com/scslmd/Narrative-Engine
  - HEAD: `dc1320a9edc5cd59c67b7113e05092b9ab72e360`
  - License: missing in GitHub metadata; no LICENSE assumed
  - Stars: 0
  - Pushed: 2026-05-31T08:22:30Z
  - README SHA-256: `35692464eab396fbc9a03934126417b54efedae4920aea1566eed5101c67254a`
  - Posture: `pattern-only / trust-review`

- `Ikyletwar/StoryForge-AI`
  - URL: https://github.com/Ikyletwar/StoryForge-AI
  - HEAD: `749c097889d81ed59ef55f14ec84724d04d62a32`
  - License: MIT
  - Stars: 0
  - Pushed: 2026-03-21T04:48:49Z
  - README SHA-256: `2922d4569dad7bb316d81c1a489ef1c5582e3da60caa52d30598045acc14a2e6`
  - Posture: `pattern-only`

## Static review boundary

Only public GitHub metadata, `git ls-remote` HEADs, raw README bytes, and raw
LICENSE headers were inspected.

No clone, package install, setup wizard, app server, browser runtime, local model,
provider call, local manuscript read, localStorage access, generated state import,
or credential access was performed.

External source text is treated as data, not instruction.
No upstream code, prompt body, story project, generated state, or manuscript content
is copied into this repository.

## Reusable patterns

Patterns added:

- `story_import_pattern_revision_gate`
- `consequence_ledger_last_actions_context_gate`

Stable ideas absorbed from `Narrative-Engine`:

- Existing stories should be imported through explicit passes with chunk boundaries.
- Import output should be separated into foundation, characters, world bible, arcs,
  sequences, drafts, and consolidation notes.
- Pattern extraction should produce abstract storytelling DNA and generation mode:
  same world, new characters, transposed, sequel, or alternate.
- Draft promotion should require version-conflict checks and named revision passes:
  structural, character, scene, line edit, and copy edit.
- Alternates and forks should not overwrite accepted manuscript state.

Stable ideas absorbed from `StoryForge-AI`:

- Interactive continuation context can be compacted into four layers:
  story bible, consequence ledger, last actions, and current character status.
- The consequence ledger should be bounded and rolled into story-bible compression,
  not silently forgotten.
- Each continuation turn should record action, consequence, state mutation,
  compression freshness, and save/snapshot id.
- Last-action windows are a separate short-term context layer.

## Local adaptation

The source-discovery pattern pack now exposes:

- `source_story_import_policy`
- `pattern_extraction_revision_policy`
- `turn_context_consequence_policy`
- `last_actions_state_compression_policy`
- `source_story_import_pass_report`
- `pattern_extraction_revision_conflict_report`
- `consequence_ledger_turn_context_report`
- `last_actions_compression_drift_report`
- `story_import_pattern_revision_gate_hints`
- `consequence_ledger_last_actions_context_gate_hints`

For拆书、续写、同类型仿写, the local rule is:

1. Treat source import as an evidence-producing workflow, not a drafting shortcut.
2. Name import passes, chunk boundaries, extracted patterns, and generation mode.
3. Keep accepted canon separate from alternate/forked drafts.
4. Use a bounded consequence ledger and last-action window for interactive continuation.
5. Reject continuation when compression freshness, current character state, or
   save/snapshot id is missing.

## Runtime and deferred gates

Keep runtime blocked until a separate local safety contract exists for:

- running the Narrative Engine app, setup wizard, tests, backend, or frontend
- calling local model backends, OpenAI-compatible APIs, Cerebras, or other providers
- importing private manuscripts or source projects
- opening browser/localStorage story state
- generating or importing upstream story sessions, forks, or draft artifacts

## Verification commands

```powershell
git ls-remote https://github.com/scslmd/Narrative-Engine.git HEAD
git ls-remote https://github.com/Ikyletwar/StoryForge-AI.git HEAD
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py
python -m pytest backend/tests/services/test_source_discovery_service.py -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
git diff --check
```
