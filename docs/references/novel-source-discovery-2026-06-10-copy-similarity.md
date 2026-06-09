# Novel Source Discovery - 2026-06-10 Copy Similarity Gates

## Scope

Static source intake for source-copy risk, fingerprint overlap, fuzzy phrase
similarity, and diff-span review patterns that can strengthen MuMuAINovel
????? and ???? acceptance gates.

No external repository was cloned, installed, executed, or imported. No package
hook, detector runtime, shell script, native extension, provider call, credential,
cookie, or external code execution was used.

## Sources

- `blingenf/copydetect` ? HEAD `ba072818afc876db8b4b65d34ab33ac2260d3d75`; license MIT; public README/root metadata only.
- `rapidfuzz/RapidFuzz` ? HEAD `a49aa034bace992b73978e9429bab2b7372a6ff4`; license MIT; public README/root metadata only.
- `google/diff-match-patch` ? HEAD `62f2e689f498f9c92dbc588c58750addec9b1654`; license Apache-2.0; public README/root metadata only.
- `agranya99/MOSS-winnowing-seqMatcher` ? HEAD `a8579f73912592a98b11d162424df81d1196af8d`; license MIT; public README/root metadata only.

## Absorbed Patterns

### source_text_fingerprint_gate

Use source/draft fingerprint comparison as a review gate. High-overlap windows
become review items, not automatic proof. Thresholds should separate long
phrases, names, set-piece labels, and scene-order topology so false positives do
not block legitimate continuation canon.

### fuzzy_phrase_similarity_gate

Use fuzzy phrase thresholds to catch paraphrased source sentences, renamed
proper-noun strings, and near-duplicate dialogue turns. Medium-similarity spans
require human or explicit review because genre phrases and required canon labels
can be legitimate matches.

### diff_span_copy_review

Use source-vs-draft diff spans to inspect copied wording, source sentence order,
semantic-cleanup matches, and patch-like edits. Store source ref, draft ref,
match reason, decision, and rewrite action before accepting a risky same-type
chapter.

## MuMuAINovel Integration

- `source_discovery_service.py` now classifies copy-similarity sources, exposes
  fingerprint/fuzzy/diff pattern hints, and adds same-type copy-risk remap rules.
- `source_pattern_pack_prompt.py` now renders the new copy-similarity hint keys.
- `book_remix_context_service.py` now injects `Copy similarity audit` into
  continuation and same-type creation contexts when the pattern pack contains
  the relevant gates.
- `novel-source-pattern-pack-2026-06-10.json` appends four new source titles and
  three new workflow patterns to the existing pattern pack.
- Tests cover classification, default discovery sources, pattern-pack rendering,
  and same-type context audit output.

## Runtime Gates

- Pattern-only.
- No external code import.
- No repository clone or package install.
- No detector execution, package hook, shell script, native extension, or MCP
  server.
- No provider/model call.
- Similarity gates are acceptance/review patterns, not legal judgments or proof
  of infringement.
