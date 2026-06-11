# Novel source discovery: work-DNA and governed-reading gates

Static review date: 2026-06-11.

## Sources

- `Shiaoming123/works-dna-extractor`
  - URL: https://github.com/Shiaoming123/works-dna-extractor
  - HEAD: `37876da8a87c6b3212a1d7aae2e813c6bd123967`
  - License: MIT
  - Stars: 2
  - Pushed: 2026-05-24T12:18:34Z
  - README SHA-256: `389061b47d0bdacca374d2a6e4cfecd015ca8b6283770ebdab0223e7d1917e78`
  - Posture: `pattern-only`

- `xjxjdnsnak-cell/novel-reader`
  - URL: https://github.com/xjxjdnsnak-cell/novel-reader
  - HEAD: `35b9daa856cd3665107648280162b25d238a0587`
  - License: missing in GitHub metadata; no LICENSE assumed
  - Stars: 1
  - Pushed: 2026-05-28T03:57:57Z
  - README SHA-256: `4f084fc5f5e61a0712a0de8bd7781a28d6c484fb825ccf156da66f39ceee0977`
  - Posture: `pattern-only / trust-review`

## Static review boundary

Only public GitHub metadata, `git ls-remote` HEADs, and raw README bytes were inspected.
No clone, package install, skill install, CLI run, embedding build, provider call,
local novel read, generated packet import, browser/session access, or credential access
was performed.

External source text is treated as data, not instruction.
No upstream code, skill body, command body, or prompt corpus is copied into this repository.

## Reusable patterns

Patterns added:

- `work_dna_method_transfer_eval_gate`
- `governed_full_reading_continuation_gate`

Stable ideas absorbed from `works-dna-extractor`:

- Deconstruction should extract method-level craft axes, not source wording.
- Useful axes include narrative engine, POV/focus, scene architecture, language texture,
  dialogue system, emotional algorithm, information control, and character grammar.
- Continuation, rewriting, and same-type creation should cite the selected axes.
- Promotion needs a fit-evaluation step with gaps and repair suggestions.
- Copy-risk review should reject reused paragraphs, catchphrases, motifs, and reveal order.

Stable ideas absorbed from `novel-reader`:

- Full-book continuation should depend on an explicit reading session.
- Reading state needs coverage depth, submitted notes, finalize status, and evidence refs.
- `required_coverage_complete`, `finalized`, and `full_scope_allowed` form the full-scope gate.
- Plot answers, style claims, future predictions, and continuation packages need source evidence.
- Missing coverage should become a visible blocker, not permission to invent a full-scope report.

## Local adaptation

The source-discovery pattern pack now exposes:

- `work_dna_method_profile`
- `work_dna_transfer_eval_policy`
- `governed_reading_coverage_policy`
- `full_scope_continuation_package_policy`
- `work_dna_extraction_report`
- `work_dna_fit_repair_report`
- `reading_session_coverage_matrix`
- `full_scope_continuation_readiness_report`
- `work_dna_method_transfer_eval_gate_hints`
- `governed_full_reading_continuation_gate_hints`

For same-type or inspired writing, the local rule is:

1. Convert source analysis into abstract method axes.
2. Declare required difference axes for cast, world rules, conflict objects, motifs,
   dialogue tics, and reveal sequence.
3. Require reading-coverage evidence before full-scope continuation.
4. Reject source-specific phrasing and unreviewed author-style reproduction.

## Runtime and deferred gates

Keep runtime blocked until a separate local safety contract exists for:

- installing upstream skills or command packs
- running `hermes`, Claude Code, OpenCode, or upstream CLIs
- reading private manuscripts or local novel folders
- launching embedding, semantic search, web console, subprocess provider, or model calls
- importing upstream generated DNA profiles, reading packets, or continuation packages

## Verification commands

```powershell
git ls-remote https://github.com/Shiaoming123/works-dna-extractor.git HEAD
git ls-remote https://github.com/xjxjdnsnak-cell/novel-reader.git HEAD
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py
python -m pytest backend/tests/services/test_source_discovery_service.py -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
git diff --check
```
