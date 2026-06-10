# Novel Source Discovery - 2026-06-10 Book NLP / Readability / Motif Gates

## Scope

This note records a static pattern-only intake pass for BookRemix source
analysis, continuation, and same-type imitation. The target improvement is to
make book-level NLP, quote attribution, readability, lexical diversity, and
motif extraction visible in the source-discovery UI instead of leaving those
fields in the generic additional-gates bucket.

## Sources

Fresh public HEAD and GitHub metadata were recorded under
`tmp/source-intake-segmentation-rag-eval-2026-06-10/`.
No source was cloned, installed, or executed.

- `booknlp/booknlp`
  - HEAD: `3d900fc2224e55960c3363826ae28539b77b4204`
  - Metadata license: MIT
  - Absorbed as `character_quote_attribution_map` only.
- `textstat/textstat`
  - HEAD: `e398f27543389283e847fc29568b049623c0e243`
  - Metadata license: MIT
  - Absorbed as `readability_pacing_metric_gate` only.
- `boudinfl/pke`
  - HEAD: `69871ffdb720b83df23684fea53ec8776fd87e63`
  - Metadata license: GPL-3.0
  - Absorbed as `keyphrase_motif_extraction` only; runtime import remains blocked.
- `LSYS/LexicalRichness`
  - HEAD: `69e6b8f381d6b86ec826911c3f0bb2fb298aac25`
  - Metadata license: MIT
  - Absorbed as `lexical_diversity_voice_audit` only.
- `HLasse/TextDescriptives`
  - HEAD: `0bbc6600bcdb3b6fcb3b6618375428005e12e133`
  - Metadata license: Apache-2.0
  - Absorbed as readability and lexical-metric bundle evidence only.

## Absorbed patterns

- `character_quote_attribution_map`
  - Track speaker, quote span, alias, relationship pressure, and scene goal
    before using dialogue evidence in continuation context.
  - For same-type imitation, transform speaker roles and dialogue goals rather
    than copying the source speaker map.

- `readability_pacing_metric_gate`
  - Compare sentence length, paragraph length, readability, and scene density
    across source, draft, and accepted chapters.
  - Treat metric drift as review evidence. Do not auto-rewrite from a metric
    alone.

- `lexical_diversity_voice_audit`
  - Track repeated vocabulary, catchphrases, lexical diversity, and narrator or
    speaker windows before accepting style-sensitive drafts.
  - Preserve broad rhythm only; replace source-specific diction, metaphors, and
    image clusters.

- `keyphrase_motif_extraction`
  - Extract motifs and keyphrases from source, outline, and draft to reveal
    missing promises, repeated anchors, and topic drift.
  - Same-type creation must transform motif functions into new objects, places,
    taboos, and stakes.

## MuMuAINovel integration

Updated surfaces:

- `BookRemixSourceDiscoveryPanel.tsx`
  - Added missing visible default seeds for `booknlp`, `textstat`, and `pke`.
  - Added `Book NLP / readability / motif gates` as a dedicated UI group.
- `sourceDiscovery.ts`
  - Added explicit pattern-pack fields for quote attribution, readability,
    lexical diversity, and motif extraction hints.
- `test_source_discovery_panel_copy.py`
  - Added copy and default-seed assertions so the UI cannot silently hide these
    source-discovered gates again.

## Runtime gates

This is static source intake only.

- No clone.
- No install.
- No package hook.
- No external NLP, summarization, or metric runtime execution.
- No provider/model call.
- No external code, dataset, or prompt set import.

Future runtime trials require a separate local safety contract covering scope,
license compatibility, dependency graph, input text privacy, network behavior,
cleanup, rollback, and verification.
