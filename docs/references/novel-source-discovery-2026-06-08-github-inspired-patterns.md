# Novel Source Discovery - 2026-06-08 GitHub Inspired Patterns

## Scope

Static GitHub source-intake for MuMuAINovel?????????????????????
No repository was cloned, installed, imported, or executed. Only public README snippets and `git ls-remote HEAD` metadata were checked.

## Source Snapshot

- [voocel/ainovel-cli](https://github.com/voocel/ainovel-cli): existing explicit seed for multi-agent AI novel generation discovery.
- [NousResearch/autonovel](https://github.com/NousResearch/autonovel): HEAD `d165f267a0ffd34f3b0a70a8a72ac38cb8e4a542`; autonomous novel pipeline from seed to manuscript/media. Absorb as pattern-only for modify/evaluate/keep-discard loops and layered fiction pipeline.
- [leenbj/novel-creator-skill](https://github.com/leenbj/novel-creator-skill): HEAD `a327428ea26962163f823ad74001243f91bc7738`; Chinese long-form novel skill. Absorb as category-local / pattern-only for long-memory, chapter gates, RAG/knowledge-graph guidance, and Chinese web-novel workflow language.
- [KazKozDev/NovelGenerator](https://github.com/KazKozDev/NovelGenerator): HEAD `abf86425f769a5e30e60a716754750b1c51eb5f6`; LLM-powered full-novel generation. Absorb as pattern-only for character knowledge, timeline coherence, emotional arcs, parallel plot threads, and autonomous chapter pipeline.
- [raestrada/storycraftr](https://github.com/raestrada/storycraftr): HEAD `73a77097d14e57070ac1a6f04b5badfbc9be91b1`; CLI book creation assistant. Absorb as index-plus-pattern for command-sized worldbuilding/outline/chapter/iteration workflow.
- [YuanShiJiLoong/author](https://github.com/YuanShiJiLoong/author): HEAD `e1f386be6a1a86bdcf9db54fd7ad3f9b254bd3cc`; AI creative writing platform. Absorb as pattern-only for local-first worldbuilding manager, AI memory, preview, and accept/reject workflow.
- [brandburner/fabula](https://github.com/brandburner/fabula): HEAD `6bc794bccba5708efc83caffff2b8ff5d19710cb`; narrative analysis to knowledge graph. Absorb as pattern-only for two-pass extraction, entity resolution, and graph-backed character/location/object/organization/event/relationship checks.

## Absorbed Project Rules

- Keep these repositories as source-discovery seeds, not runtime dependencies.
- Same-type creation needs fields separate from continuation:
  - `inspired_mapping_targets`
  - `inspired_prompt_hints`
  - `inspired_transformation_hints`
  - `inspired_copy_risk_hints`
- Inspired generation must treat source material as style and genre mechanics only.
- Copy-risk review must reject source names, proper nouns, scene order, set-piece sequence, and distinctive wording.
- Continuation and inspired creation should share style-fidelity gates, but not share canon semantics.

## Implementation Touchpoints

- `backend/app/services/source_discovery_service.py`
  - default explicit GitHub repository seeds now include the reviewed shortlist.
  - pattern pack now emits inspired-specific mapping, transformation, prompt, and copy-risk hints.
- `backend/app/services/source_pattern_pack_prompt.py`
  - prompt digest now renders inspired-specific fields.
- `backend/app/services/book_remix_context_service.py`
  - inspired mode gets a stable prompt context block from default style + source-discovery pack.
- `backend/app/api/chapters.py`
  - chapter generation can inject inspired context when no confirmed continuation lineage exists.
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
  - UI exposes the expanded GitHub seed shortlist and inspired pattern-pack fields.

## Posture

All listed sources remain `pattern-only` or `index-plus-pattern`. Runtime trial, package install, Docker use, MCP server startup, browser extension use, scripts, native binaries, and provider calls require a separate local safety contract.
