# Novel Source Discovery 2026-06-14 — universal deep planning / revision projection

## Source

- Local path: `D:\project\universal-novel-writing`
- Family: portable fiction workflow / planning templates / chapter scene engine / revision triage
- Intake posture: `pattern-only`

## Static evidence

Read-only local review:

```text
820E8643F352CA13A5CC200BA7CF66646EA8052CDC811186EAB65A5FE3B06AB7  SKILL.md
EDA357C06A86070D0B043BF718E37F2A20E418ADAF5C909D7EAFD8D71AB5573D  references/chapter-workflow.md
A3466E86CD70FB59B11DCEB2114B4FB1DC24C68241CBE81A3684725FA9DED735  references/genre-patterns.md
702038C09620725070AD713E2A5A398DEC8CCF0CD79208E7A7C9AC1B14968A7D  references/planning-templates.md
FDDC6EF1B189CB00657C2273C4AD1B762E191FE1A64691B4DED0C38958F39689  references/revision-checklists.md
FC12A7DD8CDF7188E53AABA29B4C6C14B8A7CC100D11B9F7BE7DE000AA8FCA4B  references/story-bible.md
```

No install, package execution, provider call, browser runtime, MCP runtime,
credential read, prompt-body transplant, or manuscript import was used.

## Deep fused patterns

This pass deepens the previous universal-novel-writing projection beyond mode,
project memory, chapter contract, progress write-back, and reader-pull gates.

New projected gates:

- `premise_structure_hook_payoff_gate`
  - Requires premise / logline, protagonist want, opposition, stakes, ending
    direction, and structure choice before long drafting.
  - Requires a hook/payoff matrix with thread, seeded-in point, reader
    expectation, planned payoff, maximum delay, and status.
- `scene_goal_obstacle_cost_exit_gate`
  - Requires every scene beat to carry goal, obstacle, tactic, turn, cost, and
    changed exit state.
  - Rejects activity-only scenes that do not change plot, knowledge,
    relationship, risk, moral pressure, emotion, or world-rule understanding.
- `revision_finding_patch_strategy_gate`
  - Requires revision reports to lead with Critical / High / Medium / Low
    findings.
  - Requires least-destructive patch scope before broad rewrite.

## MuMuAINovel projection

- `source_discovery_service.py`
  - Detects the three new pattern gates from local static metadata.
  - Emits pattern-pack hints, bible enrichment targets, whole-book analysis
    targets, and same-type remap targets.
- `source_pattern_pack_prompt.py`
  - Renders the new hints into compact source-pattern digest output.
- `BookRemixSourceDiscoveryPanel.tsx`
  - Surfaces the three new universal deep-planning / revision gates.
- `book_remix_context_service.py`
  - Adds continuation / same-type context section:
    `Universal deep planning and revision gate`.
  - Adds production control axes:
    - `premise_structure_stress_test`
    - `hook_payoff_matrix_review`
    - `scene_goal_obstacle_cost_exit_state`
    - `revision_finding_severity_triage`
    - `least_destructive_patch_scope`
  - Adds acceptance steps:
    - `verify_premise_structure_hook_payoff`
    - `verify_scene_goal_obstacle_cost_exit`
    - `verify_revision_findings_patch_scope`
  - Extends same-type independence audit with new required difference axes for
    premise/logline, hook/payoff ids, scene-goal sequence, obstacle tactics,
    cost pattern, exit-state route, and patch-scope ids.

## Failure modes prevented

1. Drafting many chapters from a vague promise without a premise stress test.
2. Copying a source book's hook/payoff matrix into a same-type project.
3. Accepting scenes that are fluent but have no goal, obstacle, cost, or changed
   exit state.
4. Polishing sentences before structural, character, continuity, or scene
   findings are resolved.
5. Rewriting too broadly when a paragraph, scene, ledger field, or chapter
   contract patch would be sufficient.

## Runtime boundary

Runtime remains blocked for installing or activating the local skill, executing
scripts, calling model providers, launching browser/MCP/desktop tools, reading
credentials or unrelated manuscript folders, copying prompt bodies, importing
source project files as target canon, or mutating manuscript/canon files without
an accepted patch scope.

## Verification targets

```powershell
python -m pytest backend/tests/services/test_book_remix_context_service.py::test_universal_deep_planning_revision_gates_render_context_and_audit -q
python -m pytest backend/tests/services/test_source_discovery_service.py::test_local_universal_novel_writing_skill_is_static_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_universal_novel_writing_gates -q
```
