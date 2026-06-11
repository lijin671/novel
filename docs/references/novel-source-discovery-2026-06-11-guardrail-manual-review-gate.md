# Novel Source Discovery - 2026-06-11 Guardrail Manual Review Gate

## Scope

Static source-intake pass for long-form AI novel systems related to???????????????????????

No repository was cloned, installed, or executed. Evidence was limited to public GitHub metadata/search and `git ls-remote HEAD`.

## Sources

- `ExplosiveCoderflome/AI-Novel-Writing-Assistant`
  - URL: https://github.com/ExplosiveCoderflome/AI-Novel-Writing-Assistant
  - Observed HEAD: `e88cdcd22ff02d056c9b7c7214d7e67b54a28d9e`
  - Public metadata: AI-native long-form novel system with agents, worldbuilding, RAG, structured planning, and full production workflow.
  - Posture: `pattern-only`; license is non-standard/NOASSERTION in GitHub metadata.
- `DuckTraDo/Novel`
  - URL: https://github.com/DuckTraDo/Novel
  - Observed HEAD: `cb80630cb340303d70bba42274dd7afbf892d4f8`
  - Public metadata: local-first AI novel pipeline with structured story memory, scene-level context, LoRA style adapters, and continuity checks.
  - Posture: `pattern-only`; MIT.
- `angel1411337-del/WriterOS`
  - URL: https://github.com/angel1411337-del/WriterOS
  - Observed HEAD: `22808f4b6e54d370ec8c90ffe3e50885d9f32ada`
  - Public metadata: complex-fiction writing assistant with specialized agents for worldbuilding, continuity, character arcs, plot holes, PostgreSQL/vector search, and Obsidian-compatible local-first storage.
  - Posture: `pattern-only`; license metadata `NOASSERTION`.
- `f5alcon/The-Novelists-Atelier`
  - URL: https://github.com/f5alcon/The-Novelists-Atelier
  - Observed HEAD: `e00560021c9773edad7cd745bbf5384bbdb45eab`
  - Public metadata: privacy-first browser-local writing assistant with multiple providers and series/book/chapter-level context management.
  - Posture: `pattern-only`; Apache-2.0.

## Reusable pattern

Chapter acceptance must be a separate gate from chapter text persistence.

A generated chapter may be saved for inspection, but if rewrite attempts still fail copy-risk, canon-repetition, or other high-severity guardrails, it should not be promoted as completed canon. It should be marked as review-required, and downstream analysis, memory extraction, foreshadow write-back, and continuation state write-back should wait for human review.

## Project adaptation

- `apply_chapter_guardrail_check` now emits `acceptance_status` and `manual_review_reasons`.
- Chapter generation saves unresolved guardrail failures with status `review_required` instead of `completed`.
- Batch generation raises after saving a review-required chapter so the ordered continuation batch stops before later chapters consume unsafe state.
- Generation history records a compact guardrail status note.
- The chapter list UI recognizes `review_required` and blocks later chapter generation until the user reviews the prior chapter.

## Runtime boundary

No external project code was imported. The local change only adds deterministic acceptance-state handling around existing guardrail results.
