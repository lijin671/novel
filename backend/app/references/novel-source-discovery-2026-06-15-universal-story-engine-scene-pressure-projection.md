# Novel source discovery - 2026-06-15 - universal story engine scene-pressure projection

## Source

- Local path: `D:/project/universal-novel-writing`
- Source family: portable novel-writing skill and static craft references.
- Posture: static review only; no install, no script execution, no provider call, no browser/MCP/runtime launch.
- License posture: local reference path only; license not detected in reviewed files, so this projection keeps pattern-only absorption.

Reviewed files and SHA256:

```text
820E8643F352CA13A5CC200BA7CF66646EA8052CDC811186EAB65A5FE3B06AB7  SKILL.md
FC12A7DD8CDF7188E53AABA29B4C6C14B8A7CC100D11B9F7BE7DE000AA8FCA4B  references/story-bible.md
702038C09620725070AD713E2A5A398DEC8CCF0CD79208E7A7C9AC1B14968A7D  references/planning-templates.md
EDA357C06A86070D0B043BF718E37F2A20E418ADAF5C909D7EAFD8D71AB5573D  references/chapter-workflow.md
FDDC6EF1B189CB00657C2273C4AD1B762E191FE1A64691B4DED0C38958F39689  references/revision-checklists.md
A3466E86CD70FB59B11DCEB2114B4FB1DC24C68241CBE81A3684725FA9DED735  references/genre-patterns.md
```

## Absorbed pattern

The reusable value is a story-engine pressure gate, not an upstream prompt body or prose style transplant.

Projected gate: `universal_story_engine_scene_pressure_gate`

Acceptance axes:

- `want_need_wound_cost`: protagonist or POV carrier must expose external want, internal need/wound/flaw, and a cost, limit, risk, or pressure.
- `active_opposition_stakes`: each chapter/scene needs active opposition or obstacle plus concrete stakes if the character fails.
- `choice_cost_irreversible_change`: scene beats must turn on a choice, tactic, dilemma, or action that changes plot, knowledge, relationship, risk, moral pressure, emotion, or world-rule understanding.
- `show_tell_pressure_boundary`: turning points, conflict, emotions, and choices should be dramatized; low-value transitions and repeated logistics may be summarized.
- `voice_specific_dialogue_review`: dialogue should carry character-specific diction, avoidance, goal pressure, and subtext rather than polished synopsis.

## MuMuAINovel projection

Updated the source discovery and pattern pack path so static intake can detect and surface this gate from local universal novel-writing references:

- pattern detection keyword family
- pattern-pack hint builder
- bible enrichment target: `universal_story_engine_scene_pressure_policy`
- whole-book analysis target: `story_engine_scene_pressure_report`
- same-type remap target: `story_engine_scene_pressure_remap`
- prompt, transformation, and copy-risk hints

Updated continuation and same-type context generation so the gate becomes an actual production control:

- continuation control axes and acceptance steps include story-engine pressure review
- preview audit exposes `story_engine_scene_pressure_warnings`
- continuation prompt context renders the gate and warning bucket
- same-type prompt context renders a source-boundary note so only pressure structure transfers
- independence audit adds required difference axes for target-owned desire, wound, cost, opposition, consequence, and dialogue voice

Updated frontend types and copy so preview/source-discovery panels can display the new warning and hint surface.

## Safety boundary

This intake did not copy upstream prompt bodies, agent definitions, prose examples, manuscript content, source chunks, dependency code, or runtime scripts.

Same-type仿写 may only reuse high-level craft pressure. It must rebuild all concrete story content for the target project: desire, wound, opposition, cost, scene choices, consequences, and dialogue rhythm.

Continuation may only extend accepted canon, current character state, and unresolved promise debts. It must not invent a parallel motivation system outside the confirmed bible and plan.

## Verification

Targeted tests added or extended:

```powershell
python -X utf8 -m pytest backend/tests/services/test_book_remix_context_service.py::test_universal_story_engine_scene_pressure_gate_projects_core_story_controls -q
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_local_universal_novel_writing_skill_is_static_absorbed backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_universal_novel_writing_gates backend/tests/frontend/test_source_discovery_panel_copy.py::test_continuation_context_preview_panel_surfaces_story_engine_warning_bucket -q
python -X utf8 -m pytest backend/tests/api/test_book_remix_bible_api.py backend/tests/services/test_book_remix_context_service.py backend/tests/services/test_source_discovery_service.py backend/tests/frontend/test_source_discovery_panel_copy.py -q --disable-warnings
```
