# Novel source discovery: copy similarity runtime guardrails

Date: 2026-06-11

## Sources

- `blingenf/copydetect`
  - Public GitHub metadata: MIT, code plagiarism detection, winnowing/document fingerprinting.
  - Static posture only. No clone, install, detector run, corpus import, or copied detector code.
- `agranya99/MOSS-winnowing-seqMatcher`
  - Public GitHub metadata: MIT, MOSS-style winnowing plus SequenceMatcher.
  - Static posture only. No script execution.
- `seomoz/simhash-py`
  - Public GitHub metadata: MIT, SimHash and near-duplicate detection.
  - Static posture only. No native build or package import.
- `1e0ng/simhash`
  - Public GitHub metadata: MIT, Python SimHash implementation.
  - Static posture only. No package import.
- `google/diff-match-patch`
  - Public GitHub metadata: Apache-2.0, plain-text diff/match/patch with semantic cleanup.
  - Static posture only. No source port import.

## Absorbed pattern

The useful pattern is not a dependency. It is a review shape:

1. Exact distinctive span match catches copied source wording.
2. Ordered short phrase overlap catches patch-like rearrangement.
3. Character-shingle fingerprint overlap catches partial copy after small edits.
4. Windowed fuzzy similarity catches renamed or lightly paraphrased spans.
5. SimHash-style near-duplicate scoring catches reordered windows that still preserve source topology.

## Project integration

Updated `backend/app/services/chapter_guardrails.py` so same-type creation drafts now emit an `inspired_source_copy` violation with the first detected signal:

- `distinctive_substring`
- `exact_normalized_excerpt`
- `ordered_phrase_overlap`
- `fingerprint_overlap:<ratio>`
- `fuzzy_window_similarity:<ratio>`
- `simhash_near_duplicate:<ratio>`

This keeps source-learning useful while blocking copied prose, route order, and scene topology from becoming accepted draft text.

Updated `backend/app/services/source_pattern_pack_prompt.py` so rewrite prompts surface copy-similarity hints together instead of burying them deep in the generic pattern pack.

## Runtime boundary

No external packages were installed.
No GitHub repositories were cloned.
No detector or native extension was executed.
No source project code was copied into the app.
