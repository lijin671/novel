# Novel Source Discovery - 2026-06-11 Memory / Tribunal / Checkpoint Governance

## Scope

Static source-intake pass for long-form novel continuation, 拆书续写, and 同类型仿写 workflow patterns.

Boundary:

```text
public_git_lsremote_raw_readme_license_marker_scan_no_login_no_clone_no_runtime_2026_06_11_memory_tribunal_checkpoint
```

No source was cloned, installed, imported, or executed.

## Reviewed Sources

- `Mochocyang/QMAI`
  - HEAD: `23a683d8c60579795467a802a1036027d1c2001e`
  - Default branch: `master`
  - License signal: GitHub metadata `NOASSERTION`; README badge says MIT
  - Posture: `pattern-only`
  - Absorbed pattern: chapter ingestion, context package, token budget, hybrid retrieval, chapter summary, ending hook, relationship changes, foreshadowing, graph nodes/edges, and human confirmation before final draft acceptance.

- `knoai/knowrite`
  - HEAD: `5f3506fd029797978849d502b242a9f6ae5dab0e`
  - Default branch: `main`
  - License signal: `AGPL-3.0`
  - Posture: `pattern-only`; no code import
  - Absorbed pattern: Temporal Truth Database, Author Fingerprint, RAG Memory, five-dimensional Fitness dashboard, Automated Prompt Evolution, Trace debugger, and SQLite/local-file dual-write.

- `AxolDad/novelist`
  - HEAD: `e8a73582117e111a7fec1d233fcba846175619f8`
  - Default branch: `main`
  - License signal: GitHub metadata `NOASSERTION`; README badge says MIT
  - Posture: `pattern-only`
  - Absorbed pattern: SQLite memory core, world state/arcs/characters, Parallel Critic Tribunal, Best of 3, prose/redundancy/arc critic voting, Beads issue tracking, and dashboard review.

- `Nicholas-Yu/InkPilot`
  - HEAD: `d1656fd3448069af75f7fc094dcca30f1e039655`
  - Default branch: `main`
  - License signal: `MIT`
  - Posture: `pattern-only`
  - Absorbed pattern: AI as amplifier not voice, AI 80% + Human 20%, planning/writing/review/iteration phase split, consistency checking, AI-taste detection, cost transparency, and foreshadowing tracking.

- `guohei/fanqie-plus`
  - HEAD: `5cca5ab0a183e5f1862924fd79c964c42c85ca36`
  - Default branch: `main`
  - License signal: GitHub metadata `NOASSERTION`
  - Posture: `pattern-only`
  - Absorbed pattern: Fanqie/Tomato reader profile, platform strategy, golden three chapters, 8w/10w/15w checkpoints, ten-chapter consistency audits, pacing ledger, optional reader simulator diagnostics, and Fanqie-ready plain text export.

- `armchairfuturist-code/novel-writer-harness`
  - HEAD: `8af0fa908c909a29aeddad33a2c5105274191414`
  - Default branch: `master`
  - License signal: GitHub metadata `NOASSERTION`
  - Posture: `pattern-only`
  - Absorbed pattern: outline structural validator, character coverage, foreshadowing completeness, emotional arc progression, beat density, information boundaries, structured `---CHANGES---` JSON, twelve state-transition categories, debate court, and style engine.

## Local Projection

Project-native gates added to source-discovery pattern packs:

- `chapter_memory_ingestion_context_budget_gate`
- `human_ai_decision_authority_gate`
- `parallel_critic_tribunal_issue_gate`
- `prompt_evolution_fitness_governance_gate`
- `fanqie_checkpoint_compliance_audit_gate`
- `outline_validator_change_declaration_gate`

These gates enrich:

- bible targets
- whole-book analysis targets
- continuation / same-type prompt hints
- inspired mapping targets
- copy-risk checks
- compact digest rendering

## Runtime Exclusions

Blocked by default:

- clone checkout
- package manager install
- Streamlit / Node / Express / Docker launch
- Obsidian plugin install
- desktop app / release execution
- MCP/server launch
- provider/model/API-key calls
- platform publishing/upload
- local manuscript/vault/database reads
- upstream prompt-body import
- AGPL code import

Runtime trials require a separate local safety contract.
