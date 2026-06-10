# Novel Source Discovery - 2026-06-10 Segmentation / Summary / Topic Patterns

## Scope

This note records a static pattern-only intake for MuMuAINovel book remix work.
The target improvement is book-decomposition continuation and same-type imitation context control:
semantic long-text chunking, accepted-chapter summary anchors, and topic-drift review.

## Sources

- `benbrandt/text-splitter`
  - HEAD: `c8d7ffd2d1e8024aa112f13b9a861b9b1a0be9cf`
  - License posture: MIT from metadata used in tests/reference pack.
  - Absorbed as `semantic_chunk_boundary_map` only.
- `langchain-ai/langchain`
  - HEAD: `7e9c916c7ec98e1930731060bd9cd36c9719c354`
  - License posture: MIT from metadata used in tests/reference pack.
  - Absorbed as chunk-boundary and summary-chain pattern evidence only.
- `miso-belica/sumy`
  - HEAD: `bbc540476970903b707309c28aa316be9a9c3511`
  - License posture: Apache-2.0 from metadata used in tests/reference pack.
  - Absorbed as `chapter_summary_anchor_gate` only.
- `dmmiller612/bert-extractive-summarizer`
  - HEAD: `84f27333aef33629444589c24933b76448777d4f`
  - License posture: MIT from metadata used in tests/reference pack.
  - Absorbed as representative-sentence summary-anchor evidence only.
- `MaartenGr/BERTopic`
  - HEAD: `f9697602d57fc6acb8ac304026ac3c9aecd8a031`
  - License posture: MIT from metadata used in tests/reference pack.
  - Absorbed as `topic_drift_map` only.

GitHub API metadata was not used in this pass because the API returned 403 in the prior run.
Reachability was confirmed with `git ls-remote ... HEAD`.
No repository was cloned.

## Absorbed patterns

- `semantic_chunk_boundary_map`
  - Store chunk id, source chapter id, boundary reason, overlap policy,
    size, and inclusion purpose before context packing.
  - For same-type creation, transform chunk order and boundary function;
    do not keep source segmentation route under new names.

- `chapter_summary_anchor_gate`
  - Every summary must point to accepted chapter ids, representative sentences,
    source refs, canon status, and unresolved-hook evidence.
  - Reject summaries that hide unresolved hooks or promote draft facts into canon.

- `topic_drift_map`
  - Map topic clusters across chapters and compare drift against active arcs,
    promises, motifs, and chapter goals.
  - Treat topic drift as review evidence, not as an automatic rewrite command.
  - For same-type imitation, change topic order, salience, cluster labels,
    and payoff sequence.

## MuMuAINovel integration

Updated surfaces:

- `source_discovery_service.py`
  - Added default GitHub queries and repository URLs.
  - Added pattern keywords, static source overrides, family detection,
    pattern-pack hints, bible targets, whole-book targets, and inspired-copy gates.
- `source_pattern_pack_prompt.py`
  - Added digest rendering for the three new hint groups.
- `book_remix_context_service.py`
  - Added continuation and inspired context audit section for segmentation,
    summary, and topic gates.
- `novel-source-pattern-pack-2026-06-10.json`
  - Added 5 source titles.
  - Updated source candidate count from 93 to 98.
  - Updated workflow patterns from 136 to 139.

## Runtime gates

This is static source intake only.

- No clone.
- No install.
- No package hook.
- No external project execution.
- No provider/model call.
- No MCP server, browser extension, Docker stack, native binary, or script launch.
- No external code import into MuMuAINovel runtime.

Future runtime trial requires a separate local safety contract covering scope,
license, dependency graph, secrets/auth surface, network behavior, cleanup,
rollback, and verification.

## Frontend surfacing addendum - 2026-06-10

A fresh public HEAD refresh was recorded under
`tmp/source-intake-segmentation-rag-eval-2026-06-10/head-manifest.json`.
No repository was cloned, installed, or executed.

Current reachable HEADs used for the UI surfacing pass:

- `benbrandt/text-splitter`: `822f059123e716476d141b64b85b99e36ac85afc`
- `langchain-ai/langchain`: `bee470cc29fec53216891f71e47217ee4eec3694`
- `miso-belica/sumy`: `bbc540476970903b707309c28aa316be9a9c3511`
- `dmmiller612/bert-extractive-summarizer`: `84f27333aef33629444589c24933b76448777d4f`
- `MaartenGr/BERTopic`: `f9697602d57fc6acb8ac304026ac3c9aecd8a031`

Frontend integration delta:

- Added the above segmentation / summary / topic projects to the visible
  BookRemix source-discovery seed list when they were missing from the UI.
- Pinned the corresponding pattern-pack keys so they no longer fall into the
  generic additional-gates bucket.
- Added an explicit `Segmentation / summary / RAG eval gates` group for
  semantic chunk boundaries, chapter summary anchors, topic drift maps,
  context faithfulness checks, retrieval traces, and prompt regression suites.

Runtime boundary remains unchanged: this pass is metadata/static-pattern intake
only. It does not authorize dependency installation, external eval execution,
provider/model calls, tracing services, scripts, Docker stacks, or code import.
