# Static intake: dual entry, live analytics, simulation tree - 2026-06-13

## Boundary

This intake used public GitHub Search, public `git ls-remote`, and small public
README/LICENSE marker probes.

No upstream repository was cloned, installed, built, executed, imported, indexed,
or used as a runtime dependency. Node tools, CLI commands, doctor checks, browser
apps, AI side panels, provider calls, prompt bodies, generated prose, local
knowledge bases, localStorage projects, JSON backups, and user manuscript data
remain excluded.

## Sources

### qcx1919788736-collab/craft-companion

- URL: https://github.com/qcx1919788736-collab/craft-companion
- HEAD: `3969902b7a67f40265240f213bfe408ea457e206`
- License: MIT.
- Static markers reviewed: README, LICENSE.
- Posture: pattern-only.
- Absorbed gate: `craft_companion_dual_entry_arbitration_gate`.

Reusable pattern:

- Split onboarding into two explicit routes: new novel and existing-manuscript
  import.
- Require knowledge-base readiness before formal drafting.
- Separate Writer execution, Evaluator review, Arbiter dispute resolution, final
  confirmation, checkpoint, and knowledge-base update.
- Track review findings as `confirmed`, `disputed`, or `dismissed` rather than
  collapsing all comments into one rewrite instruction.

Blocked surface:

- Node init, CLI commands, doctor runtime, project templates, prompt bodies,
  generated prose, and local knowledge bases.

### akarshkashyap4-ui/NovelWriter

- URL: https://github.com/akarshkashyap4-ui/NovelWriter
- HEAD: `e5e1fb27c1c24b5c7bbbbbeb80650fb39ccd69c3`
- License: MIT.
- Static markers reviewed: README, LICENSE.
- Posture: pattern-only.
- Absorbed gate: `novelwriter_live_manuscript_analytics_gate`.

Reusable pattern:

- Treat Event Line, open plot lines, Connection Web, and Story Pulse as live
  manuscript diagnostics.
- Keep reader-reaction simulation and live mood/remarks advisory until the
  author accepts a change.
- Store inline scene suggestions as review items, not automatic edits.

Blocked surface:

- npm install/dev runtime, AI side panel execution, provider calls, mood art,
  generated summaries, reader simulations, PDF export, and manuscript data.

### FrankS-IntelLab/LuminTree-Intel

- URL: https://github.com/FrankS-IntelLab/LuminTree-Intel
- HEAD: `e9f3c0c902aa8655f27881a033bf3de549e881ef`
- License: MIT.
- Static markers reviewed: README, LICENSE.
- Posture: pattern-only.
- Absorbed gate: `lumintree_simulation_tree_category_gate`.

Reusable pattern:

- Organize creative state as a six-category tree:
  Core Concept, Worldview Setting, Plot Framework, Character Profiles, Chapter
  Structure, and Writing Materials.
- Bind AI help to the active category so world rules, plot logic, character
  constraints, chapter plans, and style directives do not bleed together.
- Preserve AI history per node and per chapter for auditability.
- Keep full JSON export/import as a custody and backup boundary.

Blocked surface:

- Browser runtime, API endpoint configuration, voice input, provider calls,
  AI import classification, generated drafts, localStorage data, and JSON
  project backups.

## Project changes

- Added seed URLs and GitHub queries for dual-entry arbitration, live manuscript
  analytics, and six-category simulation trees.
- Added pattern-pack hint fields so拆书、续写、同类型仿写 can use these workflows as
  target-side review and memory structures.
- Added front-end labels so the source discovery panel exposes the new gates.

## Verification commands

```powershell
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_dual_entry_live_analytics_simulation_tree_sources_are_absorbed -q
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_graph_diff_layered_replay_sources_are_absorbed -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
npm --prefix frontend run build
git diff --check
```
