# Universal Novel Writing intake/export/rollback projection

Date: 2026-06-14

## Source

- `D:/project/universal-novel-writing`
- `D:/project/universal-novel-writing/SKILL.md`
- `D:/project/universal-novel-writing/references/planning-templates.md`
- `D:/project/universal-novel-writing/references/chapter-workflow.md`
- `D:/project/universal-novel-writing/references/revision-checklists.md`

## Posture

- local static review only
- pattern-only
- license unknown
- no install, package execution, provider call, prompt-body import, source prose import, or manuscript import

## Absorbed pattern

The portable workflow adds three reusable controls for拆书续写 and同类型仿写:

- five-question intake: ask at most five setup questions, then produce logline, reader promise, protagonist arc, opposition, world rules, ending direction, and a 5-15 beat package;
- clean export: export mode packages only accepted chapters into a clean manuscript or structured export plan;
- minimal rollback: when a gate fails, repair the smallest failing artifact instead of restarting or overwriting the whole project.

## Related public metadata pulse

A bounded web search on 2026-06-14 found adjacent public GitHub patterns without cloning, installing, or executing:

- `DoktorDaveJoos/manuscript`: local-first manuscript app with story-bible/wiki reference and chapter operations.
- `john-paul-ruf/novel-engine`: phase-gated editorial production pipeline with author authority and release notes emphasizing revision queue and book dashboard.
- `worldwonderer/oh-story-claudecode`: continuation-bible extraction with story architecture, character, narrative, and consistency roles.
- `Anshler/graphify-novel`: premise-to-story-bible scaffolding and contradiction/unresolved-setup tracking.

These were kept as weak discovery signals only. No external code, prompts, assets, release artifacts, or runtime behavior were imported.

## Local adaptation

`BookRemixContextService` now recognizes these source-pattern gates:

- `five_question_intake_story_promise_gate`
- `universal_export_clean_manuscript_gate`
- `minimal_rollback_repair_scope_gate`

Continuation mode projects them into prompt context as an intake/export/rollback gate. It also adds audit axes for intake packet, clean manuscript export scope, and minimal rollback repair scope.

Same-type mode keeps the upstream workflow as craft discipline only. The target project must rebuild its own premise, beats, export manifest, and repair notes. Source questions, source answers, source chapter order, and source repair notes do not become target canon.

`NovelSourceDiscoveryService` now detects these gates from the local static reference and exposes corresponding pattern-pack hints, whole-book analysis targets, bible enrichment policies, and same-type remap targets.

The source-discovery panel now surfaces these hints next to the other Universal Novel Writing gates.

## Boundary

Export manifests are derived artifacts. They do not write back into canon unless a separate accepted chapter or continuity patch is reviewed.

Rollback repair scope must name the failing gate, repaired artifact, and verifier. Broad regeneration or accepted manuscript overwrite is not authorized by this projection.

## Verification

- `python -m py_compile backend/app/services/book_remix_context_service.py backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py`
- `python -m pytest backend/tests/services/test_source_discovery_service.py::test_local_universal_novel_writing_skill_is_static_absorbed backend/tests/services/test_book_remix_context_service.py::test_universal_intake_export_rollback_gates_render_context_and_audit backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_universal_novel_writing_gates -q`
