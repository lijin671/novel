# Novel Source Discovery - 2026-06-11 Chinese Text Processing

## Purpose

Static intake for Chinese NLP projects that can improve MuMuAINovel's Chinese
source deconstruction, continuation, and same-type creation review flow.

This pass mines workflow patterns only. It does not clone, install, build native
code, download NLP models, run tokenizers/correctors, launch services, or send
manuscripts to external APIs.

## Safety boundary

- Quarantine: L1 public metadata + `git ls-remote` HEAD + raw license static read.
- No package manager, installer, model download, server, browser extension, or
  native build was executed.
- Runtime adoption is deferred until a local safety contract names the exact
  checker/model, file scope, privacy boundary, output path, timeout, and cleanup.

## Source snapshot

- [fxsjy/jieba](https://github.com/fxsjy/jieba)
  - HEAD: `67fa2e36e72f69d9134b8a1037b83fbb070b9775`
  - default branch observed: `master`
  - license: MIT
  - posture: pattern-only
  - absorbed pattern: Chinese segmentation, custom dictionary, keyword extraction gate

- [messense/jieba-rs](https://github.com/messense/jieba-rs)
  - HEAD: `1e77e50d0f1d62a545c535b8e2d2e00348c39e11`
  - default branch observed: `main`
  - license: MIT
  - posture: pattern-only / runtime-deferred
  - absorbed pattern: deterministic Chinese tokenizer boundary; native build deferred

- [hankcs/HanLP](https://github.com/hankcs/HanLP)
  - HEAD: `942ce9306c953cc9f445a448c8e25584bb561453`
  - default branch observed: `master`
  - license: Apache-2.0
  - posture: pattern-only
  - absorbed pattern: Chinese NER, alias, entity consistency review

- [HIT-SCIR/ltp](https://github.com/HIT-SCIR/ltp)
  - HEAD: `1f042d48b0a785ff7875b2e63c1439ef8c78995c`
  - default branch observed: `main`
  - license: not confirmed via raw `LICENSE` in this pass
  - posture: pattern-only / license-review-needed before runtime
  - absorbed pattern: Chinese segmentation, NER, and role extraction review

- [BYVoid/OpenCC](https://github.com/BYVoid/OpenCC)
  - HEAD: `3bf661989c6980884bc52c34bda245e55ea3664f`
  - default branch observed: `master`
  - license: Apache-2.0
  - posture: pattern-only / runtime-deferred
  - absorbed pattern: Simplified/Traditional and variant normalization gate

- [shibing624/pycorrector](https://github.com/shibing624/pycorrector)
  - HEAD: `7e3caeaf03c42cdb7473ed7e966b62bdc6c69309`
  - default branch observed: `master`
  - license: Apache-2.0
  - posture: pattern-only
  - absorbed pattern: Chinese correction review queue and confusion-set exceptions

## Reusable patterns

### chinese_segmentation_keyword_gate

Use Chinese segmentation with a project dictionary before keyword, motif, style,
or retrieval analysis. Names, invented terms, sects, places, skills, and unique
objects must be dictionary entries before comparing source and new drafts.

### chinese_ner_alias_consistency_gate

Map Chinese names, aliases, locations, organizations, titles, and relationship
labels into a review ledger before chapter state write-back. Flag entity
merges/splits when aliases or labels drift across chapters.

### chinese_text_normalization_gate

Declare Simplified/Traditional, punctuation width, numeral, and variant-character
policy before deconstruction or export. Normalize for comparison/retrieval, but
keep author-approved manuscript surface unchanged unless a change is accepted.

### chinese_error_correction_review_gate

Treat Chinese typo and correction suggestions as review items, not automatic
rewrites. Protect names, invented terms, dialect, honorifics, and genre
vocabulary with explicit exceptions.

## MuMuAINovel integration

Updated artifacts:

- `backend/app/services/source_discovery_service.py`
  - adds Chinese NLP discovery queries and explicit repository URLs
  - classifies Chinese segmentation/NER/normalization/correction signals
  - emits new pattern-pack targets and hints
- `backend/app/services/source_pattern_pack_prompt.py`
  - renders the new Chinese text-processing hint families
- `backend/app/services/book_remix_context_service.py`
  - adds `Chinese text processing audit` to continuation and same-type contexts
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
  - increments source candidates to 137
  - records 175 workflow patterns

## Deferred runtime gates

Before any runtime trial:

- choose local-only checker/tokenizer/model
- record model or dictionary source and license
- declare manuscript privacy scope
- declare exact file paths and output reports
- prohibit source-book text upload unless separately approved
- set timeout and cleanup
- verify no installer, package hook, native build, or service launch occurs

## Frontend surfacing addendum - 2026-06-10

Fresh public `git ls-remote --symref HEAD` check ran on
2026-06-10 18:54 +08:00 and was stored only under
`tmp/source-intake-chinese-narrative-2026-06-10/head-manifest.json`.

Observed HEADs:

- `fxsjy/jieba`: `67fa2e36e72f69d9134b8a1037b83fbb070b9775`
- `messense/jieba-rs`: `1e77e50d0f1d62a545c535b8e2d2e00348c39e11`
- `hankcs/HanLP`: `ddb1299bddff079e447af52ec12549c50636bfa8`
  on observed default branch `doc-zh`
- `HIT-SCIR/ltp`: `1f042d48b0a785ff7875b2e63c1439ef8c78995c`
- `BYVoid/OpenCC`: `3bf661989c6980884bc52c34bda245e55ea3664f`
- `shibing624/pycorrector`: `7e3caeaf03c42cdb7473ed7e966b62bdc6c69309`

Project integration delta:

- `BookRemixSourceDiscoveryPanel.tsx` now includes these repositories in the
  default public GitHub seed list.
- The source-discovery UI now pins a `Chinese text processing gates` group for:
  segmentation/keyword review, Chinese NER/alias consistency, text
  normalization, and Chinese correction triage.
- `sourceDiscovery.ts` exposes the corresponding pattern-pack fields so the
  frontend contract matches the backend pack.

Runtime boundary is unchanged: these projects are evidence sources only. No
tokenizer, model, native build, package, or correction pipeline was executed.
