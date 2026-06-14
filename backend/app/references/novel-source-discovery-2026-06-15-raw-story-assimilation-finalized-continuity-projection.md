# Novel Source Discovery 2026-06-15: Raw Story Assimilation and Six-Layer Canon Gates

## Scope

Static projection for MuMuAINovel book-remix continuation and same-type writing.

Sources reviewed or reused as prior static intake evidence:

- `D:/project/universal-novel-writing`
  - files read: `SKILL.md`, `references/story-bible.md`, `references/planning-templates.md`, `references/chapter-workflow.md`, `references/revision-checklists.md`, `references/genre-patterns.md`
  - posture: local static reference / pattern-only
  - license: not asserted by this pass
- `HKStudio011/Open-Novel-Skills`
  - existing project intake gate: `raw_story_assimilation_workflow_gate`
  - posture: pattern-only / static workflow projection
- `BillChen-29/novel-base`
  - existing project intake gate: `six_layer_iron_law_chapter_gate`
  - posture: pattern-only / no root license file observed in earlier intake

## Absorbed projection

### Raw story assimilation gate

Reusable structure:

- imported raw story or legacy notes are evidence, not canon;
- raw inputs must be recorded in a `raw_story_manifest`-style surface;
- source facts must first become proposed target `Bible` and `Outline` deltas;
- review remains diagnosis-only before drafting or rewriting;
- continuity writeback happens only after the target chapter is finalized / accepted.

Projection in MuMuAINovel:

- continuation context renders `Raw story assimilation gate`;
- production audit adds:
  - `raw_story_import_manifest`
  - `proposed_bible_outline_delta`
  - `diagnosis_only_assimilation_review`
  - `finalized_chapter_continuity_writeback`
- missing evidence emits `raw_story_assimilation_warnings`;
- same-type independence audit treats raw-story assimilation as a transferable workflow only.

Same-type boundary: raw source order cannot become the target outline. Source plot facts require approved target-owned Bible / Outline deltas before use.

### Six-layer Iron Law consistency gate

Reusable structure:

- truth file / canonical fact surface;
- state tracking for character, world, timeline, and known facts;
- knowledge graph or equivalent fact relation surface;
- outline anchors that gate chapter sequence;
- reverse-brake / anti-premature-resolution policy;
- failed gate blocks chapter acceptance and triggers current-chapter repair.

Projection in MuMuAINovel:

- continuation context renders `Six-layer Iron Law consistency gate`;
- production audit adds:
  - `six_layer_truth_state_graph`
  - `outline_anchor_reverse_brake`
  - `failed_gate_chapter_acceptance_block`
- missing evidence emits `six_layer_iron_law_warnings`;
- same-type independence audit requires new truth-file facts, outline anchor order, graph ids, and brake labels.

Same-type boundary: reuse only the consistency review shape. Do not copy source truth files, anchor order, labels, example facts, generated prose, skill files, scripts, or runtime assets.

## Runtime exclusions

This pass does not authorize clone, install, package/script execution, Docker, MCP/browser/runtime launch, provider/model call, upstream prompt body import, upstream skill-file import, generated prose import, database use, credential/session access, or host/model configuration mutation.

## Verification target

```powershell
python -X utf8 -m pytest backend/tests/services/test_book_remix_context_service.py -q -k "raw_story_assimilation_gate_projects or six_layer_iron_law_gate_projects" --disable-warnings
python -X utf8 -m pytest backend/tests/services/test_book_remix_context_service.py -q --disable-warnings
```
