# Novel Source Discovery - Entity Redaction And Proper-Noun Leakage - 2026-06-10

## Purpose

Absorb entity-redaction and named-entity review patterns for MuMuAINovel's
source-book deconstruction, continuation, and same-type creation workflows.

The goal is not to add PII tooling to the runtime. The goal is to prevent
source-specific names, places, factions, artifacts, powers, titles, and invented
terms from leaking into new drafts after surface-level renaming.

## Static Source Snapshot

All HEADs below were refreshed with `git ls-remote <repo> HEAD` on
2026-06-10. Only public metadata, README/root files, and license files were
inspected.

- `microsoft/presidio`
  - HEAD: `83ab7eb85609c49d9b0b17c44b5c025575966876`
  - default branch: `main`
  - license: MIT via GitHub metadata and `LICENSE`
  - posture: `pattern-only`
  - absorbed patterns: `source_entity_redaction_gate`,
    `proper_noun_leakage_review`
  - runtime risk: Docker/service surface present in root files

- `LeapBeyond/scrubadub`
  - HEAD: `53772cbef417da290d25c95373031f786ab3b5c6`
  - default branch: `master`
  - license: Apache-2.0 via GitHub metadata and `LICENSE`
  - posture: `pattern-only`
  - absorbed patterns: `source_entity_redaction_gate`,
    `placeholder_alias_consistency_map`

- `urchade/GLiNER`
  - HEAD: `3ddf1689ed4ae6544f0e904c447f5dd9d2bb7ca3`
  - default branch: `main`
  - license: Apache-2.0 via GitHub metadata and `LICENSE`
  - posture: `pattern-only`
  - absorbed patterns: `custom_entity_label_inventory`,
    `proper_noun_leakage_review`

- `flairNLP/flair`
  - HEAD: `d4ea3777998ba67bfbe6b6b8359e024dcf673c3e`
  - default branch: `master`
  - license: GitHub metadata reports `NOASSERTION`; root `LICENSE` is MIT
  - posture: `pattern-only`
  - absorbed patterns: `custom_entity_label_inventory`,
    `proper_noun_leakage_review`

- `explosion/spaCy`
  - HEAD: `e67199550e365dacee28b109210c3a43e1477638`
  - default branch: `master`
  - license: MIT via GitHub metadata and `LICENSE`
  - posture: `pattern-only`
  - absorbed patterns: `custom_entity_label_inventory`,
    `proper_noun_leakage_review`

## Absorbed Workflow Patterns

- `source_entity_redaction_gate`
  - Detect and redact source-specific entities before source deconstruction
    output is allowed into same-type drafting context.
  - True continuation may keep approved canon names. Same-type creation must
    use transformed placeholders or fresh names.

- `custom_entity_label_inventory`
  - Track fiction-specific labels beyond PERSON/ORG/LOC: faction, rank,
    artifact, power, species, place type, title, invented term, and relationship
    label.
  - Store source entity inventories as analysis evidence, not as generation
    canon.

- `placeholder_alias_consistency_map`
  - Keep stable placeholder ids, aliases, nicknames, and titles across chapters.
  - Review collisions where two source entities collapse into one replacement
    or one source entity receives multiple replacements.

- `proper_noun_leakage_review`
  - Compare drafts against source blocklists and approved exception lists before
    accepting continuation or same-type prose.
  - Common genre nouns can have reviewer exceptions. Distinctive names, places,
    factions, artifacts, and powers require replacement unless explicitly
    allowed.

## Runtime Exclusions

No external repository was cloned, installed, executed, or imported.

Excluded by design:

- Presidio services, Docker compose files, analyzer/anonymizer runtime, image
  redaction, and CLI/package execution
- Scrubadub optional detector packages and runtime dependencies
- GLiNER/Flair/spaCy models, downloads, training scripts, and package runtime
- external scripts, package managers, Docker stacks, native binaries, MCP
  servers, browser extensions, or provider calls

## Artifacts Updated

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`
