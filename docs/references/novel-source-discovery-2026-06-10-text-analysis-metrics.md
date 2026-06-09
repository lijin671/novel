# Novel Source Discovery - 2026-06-10 Text Analysis Metrics

## Scope

Static source intake for book-length text analysis patterns that can strengthen
MuMuAINovel continuation and same-type creation review gates.

No external repository was cloned, installed, executed, or imported. No package
hook, model download, NLP runtime, shell script, native extension, provider call,
credential, cookie, or external code execution was used.

## Sources

- `booknlp/booknlp` - HEAD `3d900fc2224e55960c3363826ae28539b77b4204`; license MIT; public metadata/root files only.
- `textstat/textstat` - HEAD `e398f27543389283e847fc29568b049623c0e243`; license MIT; public metadata/root files only.
- `LSYS/LexicalRichness` - HEAD `69e6b8f381d6b86ec826911c3f0bb2fb298aac25`; license MIT; public metadata/root files only.
- `HLasse/TextDescriptives` - HEAD `0bbc6600bcdb3b6fcb3b6618375428005e12e133`; license Apache-2.0; public metadata/root files only.
- `boudinfl/pke` - HEAD `69871ffdb720b83df23684fea53ec8776fd87e63`; license GPL-3.0; public metadata/root files only.

## Absorbed Patterns

### character_quote_attribution_map

Use book-length character mention, alias, speaker, and quote-attribution mapping
before judging voice consistency. Continuation can verify that dialogue belongs
to the right current speaker state. Same-type creation can preserve only quote
function and pressure while rebuilding cast, aliases, and dialogue content.

### readability_pacing_metric_gate

Use readability, sentence-length, paragraph-density, and scene-density curves as
pacing review signals. The metric is not a rewrite command by itself; it surfaces
where chapters became too flat, too dense, or source-route-shaped.

### lexical_diversity_voice_audit

Use lexical richness/diversity signals to detect repeated vocabulary clusters,
voice drift, sudden narrator changes, and copied diction. Same-type creation may
borrow broad diversity range, but not source catchphrases, metaphor clusters, or
signature word families.

### keyphrase_motif_extraction

Extract keyphrases and motif terms from source, outline, and draft to find topic
drift, missing promises, repeated thematic anchors, and copied source-specific
objects or symbols. GPL source remains pattern-only; no code is imported.

## MuMuAINovel Integration

- `source_discovery_service.py` now classifies text-analysis repositories,
  exposes four pattern-pack hint families, and adds same-type remap/copy-risk
  rules.
- `source_pattern_pack_prompt.py` now renders the new text-analysis hint keys.
- `book_remix_context_service.py` now injects `Text analysis audit` into
  continuation and same-type creation contexts.
- `novel-source-pattern-pack-2026-06-10.json` now includes 93 source candidates
  and 136 workflow patterns, including the five text-analysis sources above.
- Tests cover classification, default discovery sources, pattern-pack rendering,
  digest rendering, and continuation/same-type context audit output.

## Runtime Gates

- Pattern-only.
- No external code import.
- No repository clone or package install.
- No model download, package hook, shell script, native extension, Docker stack,
  MCP server, or provider/model call.
- Metrics are review signals, not legal judgments and not automatic quality
  proof.
