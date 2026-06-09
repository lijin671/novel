# Novel Source Discovery - Dedup / Semantic Similarity Gates - 2026-06-10

## Scope

This pass improves MuMuAINovel's book-deconstruction, continuation, and
same-type/inspired-writing safeguards with static lessons from public GitHub
deduplication and similarity projects.

No repository was cloned, installed, imported, or executed. No package manager,
model, native extension, Docker stack, script, browser extension, MCP server, or
credential was used. All absorption is pattern-only.

## Static Source Snapshot

- [ChenghaoMou/text-dedup](https://github.com/ChenghaoMou/text-dedup)
  - HEAD: `7538f3ec6a28e72a86de5978e58655175b46a11e`
  - License: Apache-2.0
  - Use: all-in-one dedup taxonomy across exact, MinHash, SimHash, and semantic
    dedup checks.
- [google-research/deduplicate-text-datasets](https://github.com/google-research/deduplicate-text-datasets)
  - HEAD: `4e9888ac3f95dc4f6169867a04c4c19df02dafe3`
  - License: Apache-2.0
  - Archived: true
  - Use: repeated-sequence and corpus-leakage review; do not run Rust/Python
    tooling or download datasets.
- [ekzhu/datasketch](https://github.com/ekzhu/datasketch)
  - HEAD: `f84c431ba6f463302a7f42f48b494b4d3e2287b3`
  - License: MIT
  - Use: MinHash/LSH and Jaccard-style near-duplicate threshold design.
- [seomoz/simhash-py](https://github.com/seomoz/simhash-py)
  - HEAD: `cb966253b5ad7a056b3bc9a5d24a4c9ca8153fb8`
  - License: MIT
  - Use: SimHash/Hamming near-duplicate review; native extension not built.
- [1e0ng/simhash](https://github.com/1e0ng/simhash)
  - HEAD: `78f3b8d5b810d93443269b6e227cae7b95e67316`
  - License: MIT
  - Use: lightweight SimHash threshold vocabulary.
- [MinishLab/semhash](https://github.com/MinishLab/semhash)
  - HEAD: `986e782990a4913a4b6f854af342c7ee03dea634`
  - License: MIT
  - Use: semantic duplicate clustering and filtering gates.
- [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers)
  - HEAD: `4df4e7ecc611fec614ffb9108ef8aefb4d951f54`
  - License: Apache-2.0
  - Use: embedding-neighbor similarity as review evidence, not a runtime
    dependency.
- [facebookresearch/faiss](https://github.com/facebookresearch/faiss)
  - HEAD: `1cdc3709c656eea41ce3725024070f2516e3b30b`
  - License: MIT
  - Use: dense-vector nearest-neighbor and clustering review patterns.
- [facebookresearch/SemDeDup](https://github.com/facebookresearch/SemDeDup)
  - HEAD: `6b4194511202c29b0e1ac8c730996777449ea2a4`
  - License: NOASSERTION
  - Archived: true
  - Use: semantic duplicate cluster and dataset-leakage caution; conda/runtime
    pipeline remains blocked.

## Absorbed Patterns

- `minhash_lsh_near_duplicate_gate`
  - Compare source and draft shingles.
  - Review high-Jaccard near-duplicate windows before acceptance.
  - Keep threshold, shingle size, and accepted/rewritten decisions visible.
- `simhash_hamming_similarity_gate`
  - Catch lightly edited, reordered, translated, or polished source windows.
  - Keep separate Hamming thresholds for dialogue, prose, and outline windows.
- `semantic_duplicate_cluster_gate`
  - Cluster source/draft windows to catch paraphrased duplicate scenes.
  - Treat source-neighbor clusters as review evidence, not automatic rejection.
- `embedding_similarity_independence_gate`
  - Require key draft passages to be closer to transformed canon or the new
    brief than to source excerpts.
  - Store nearest-neighbor evidence and thresholds for review.
- `corpus_leakage_dedup_review_gate`
  - Keep source corpus, deconstruction notes, transformed canon, and generated
    draft manifests separate.
  - Reject repeated long sequences and source-route clusters unless they are
    explicit continuation canon.

## MuMuAINovel Projection

Updated artifacts:

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`

Runtime boundary:

- No external dedup/similarity library was added as a dependency.
- No model download or vector index runtime was introduced.
- The new behavior is prompt/context guidance and pattern-pack metadata only.
