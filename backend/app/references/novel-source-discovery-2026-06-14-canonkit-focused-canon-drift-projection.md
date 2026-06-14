# CanonKit focused canon-drift context-pack projection

Date: 2026-06-14

## Source

- `https://github.com/sadasdfsaf/canonkit`
- Observed HEAD: `edb8c1ac1747a822da1cd728fbc8c13a8f932e7a`
- Static markers: public `git ls-remote`, public README, `package.json`
- GitHub API metadata was rate-limited/blocked with HTTP 403 during this pass

## Posture

- public metadata and raw README/package marker review only
- pattern-only selective projection
- license unknown in static marker pass; no LICENSE body was found through raw root probes
- no clone, checkout, npm install, browser demo, build, test, provider call, JSON import/export, local storage access, prompt-body import, or manuscript import

## Absorbed pattern

CanonKit positions itself as a local-first story bible and continuity checker. The useful pattern for MuMuAINovel is not its UI or TypeScript implementation. The portable pattern is a pre-draft canon-drift gate plus a focused-scene context pack.

Reusable detector categories:

- missing core character setup;
- age/year mismatch;
- references to entities absent from accepted cards/rules/locations/items;
- scene state conflicts;
- asymmetric relationship records;
- focused-scene context packs built only from accepted canon.

## Local adaptation

`BookRemixContextService` now recognizes `canonkit_local_canon_drift_context_pack_gate` and projects it into continuation and same-type contexts.

Continuation control axes added:

- `local_first_canon_drift_check`
- `focused_scene_context_pack`
- `character_age_year_consistency`
- `missing_entity_reference_review`
- `relationship_symmetry_review`
- `scene_state_conflict_review`

The production audit now exposes `canonkit_context_pack_warnings` for missing or contradictory state before drafting.

Same-type mode transfers only the detector categories. Target stories must rebuild their own character cards, scene records, JSON/context packs, and canon facts independently.

## Boundary

CanonKit source content remains untrusted reference data. This pass did not import runtime code, UI text, sample project state, or JSON storage formats.

Static intake does not authorize CanonKit browser persistence, demo access, npm scripts, local project storage, or JSON import/export.

## Verification

- `backend/tests/services/test_book_remix_context_service.py`
- `python -m pytest backend/tests/services/test_book_remix_context_service.py -q`
