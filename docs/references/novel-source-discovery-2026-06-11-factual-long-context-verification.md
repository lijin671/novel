# Novel Source Discovery - 2026-06-11 Factual Grounding / Long-Context Verification

## Scope

Static public intake for factual grounding, hallucination review, and long-context recall checks that can improve ???? and ????? acceptance gates.

Boundary: public GitHub Search/API metadata, `git ls-remote --symref HEAD`, raw README/LICENSE marker scan, no login, no clone, no install, no package manager, no dataset download, no model/provider call, no benchmark runtime.

Scratch manifest: `tmp/source-intake-20260611-factual-long-context-static-review.json`.

## Source Snapshot

- `shmsw25/FActScore`
  - URL: `https://github.com/shmsw25/FActScore`
  - observed HEAD: `f28272deffcf` on `main`
  - license signal: `MIT`; raw license path: `LICENSE`
  - static markers: `atomic, fact, factual, long-form, precision, retrieval`
  - absorbed pattern: `atomic_fact_precision_gate`

- `potsawee/selfcheckgpt`
  - URL: `https://github.com/potsawee/selfcheckgpt`
  - observed HEAD: `19b492a2a380` on `main`
  - license signal: `MIT`; raw license path: `LICENSE`
  - static markers: `consistency, fact, factual, hallucination, qa, selfcheck`
  - absorbed pattern: `self_consistency_hallucination_gate`

- `amazon-science/RefChecker`
  - URL: `https://github.com/amazon-science/RefChecker`
  - observed HEAD: `1df1b25cee79` on `main`
  - license signal: `Apache-2.0`; raw license path: `LICENSE`
  - static markers: `benchmark, checker, claim, fact, factual, hallucination, qa, reference, retrieval, selfcheck`
  - absorbed pattern: `reference_claim_verification_gate`

- `THUDM/LongBench`
  - URL: `https://github.com/THUDM/LongBench`
  - observed HEAD: `2e00731f8d0b` on `main`
  - license signal: `Apache-2.0`; raw license path: `LICENSE`
  - static markers: `benchmark, long context, qa, retrieval`
  - absorbed pattern: `long_context_benchmark_task_suite_gate`

- `NVIDIA/RULER`
  - URL: `https://github.com/NVIDIA/RULER`
  - observed HEAD: `ab17b7853df4` on `main`
  - license signal: `Apache-2.0`; raw license path: `LICENSE`
  - static markers: `benchmark, claim, haystack, multi-hop, needle, qa, retrieval, ruler, synthetic`
  - absorbed pattern: `needle_haystack_context_recall_gate + long_context_benchmark_task_suite_gate`

- `gkamradt/LLMTest_NeedleInAHaystack`
  - URL: `https://github.com/gkamradt/LLMTest_NeedleInAHaystack`
  - observed HEAD: `021385d68d32` on `main`
  - license signal: `MIT`; raw license path: `LICENSE.txt`
  - static markers: `fact, haystack, long context, needle, reference, retrieval`
  - absorbed pattern: `needle_haystack_context_recall_gate`

- `booydar/babilong`
  - URL: `https://github.com/booydar/babilong`
  - observed HEAD: `7a6efee29f5c` on `main`
  - license signal: `Apache-2.0`; raw license path: `LICENSE`
  - static markers: `babilong, benchmark, claim, fact, haystack, long context, long-form, needle, qa, reference`
  - absorbed pattern: `distributed_fact_chain_recall_gate`

- `OpenBMB/InfiniteBench`
  - URL: `https://github.com/OpenBMB/InfiniteBench`
  - observed HEAD: `51d9b37b0f17` on `main`
  - license signal: `Apache-2.0`; raw license path: `LICENSE`
  - static markers: `benchmark, infinitebench, long context, qa, reference, retrieval, synthetic`
  - absorbed pattern: `long_context_benchmark_task_suite_gate`

- `princeton-nlp/HELMET`
  - URL: `https://github.com/princeton-nlp/HELMET`
  - observed HEAD: `af609c4d51b9` on `main`
  - license signal: `MIT`; raw license path: `LICENSE`
  - static markers: `benchmark, claim, fact, helmet, infinitebench, long context, long-form, multi-hop, qa, retrieval`
  - absorbed pattern: `long_context_benchmark_task_suite_gate`

## Reusable Patterns

- `atomic_fact_precision_gate`: split generated chapter claims into atomic facts and require support decisions before canon write-back.
- `self_consistency_hallucination_gate`: use sampled disagreement as a review signal for high-impact facts, motives, timelines, and world rules.
- `reference_claim_verification_gate`: extract claims and classify each as supported, unsupported, contradicted, or out-of-scope against a named evidence scope.
- `long_context_benchmark_task_suite_gate`: test context packs separately for retrieval, QA, summarization, and multi-hop reasoning coverage.
- `needle_haystack_context_recall_gate`: probe hidden clue/fact recall across long chapter ranges, depths, and distractor density.
- `distributed_fact_chain_recall_gate`: verify long-range payoffs that require multiple facts from different chapters before accepting prose.

## Local Fusion

- Added default GitHub seeds and search queries for factuality, claim checking, and long-context recall projects.
- Added source-discovery pattern keywords, static repository summaries, pattern-pack targets, and prompt digest keys.
- Same-type creation guidance keeps original-source facts out of transformed-story grounding evidence.

## Deferred Runtime Gates

- Do not run benchmark scripts, model calls, retrievers, datasets, or package managers during source discovery.
- Do not import upstream datasets or generated samples into project canon.
- Any future runtime trial needs a local safety contract naming data scope, model/provider boundary, timeout, cleanup, and verifier.

## Verification

- `python -m pytest backend/tests/services/test_source_discovery_service.py::test_factual_grounding_long_context_sources_map_to_verification_gates -q`
