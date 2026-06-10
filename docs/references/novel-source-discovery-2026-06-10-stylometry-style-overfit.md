# Novel Source Discovery - 2026-06-10 Stylometry / Style Overfit

## Scope

This pass statically reviewed public GitHub sources for stylometry, authorship
attribution, writing-style similarity, style-change detection, and
anti-stylometry. The goal is to improve MuMuAINovel's source-book deconstruction,
same-type creation, and copy-risk review without importing external runtime
code.

No repository was cloned. No package was installed. No scripts, notebooks,
Docker stacks, model files, local HTTP APIs, providers, or GUI/runtime tools
were executed.

## Reviewed sources

| Source | Observed HEAD | License posture | Intake posture |
|---|---:|---|---|
| <https://github.com/computationalstylistics/stylo> | `8e18eb1c4e3fc6e0356a9d160b0e87cfd3928290` | GPL-3 noted in README | pattern-only |
| <https://github.com/fastdatascience/faststylometry> | `89e2b48a674a54ffdcc717e0373ce2571eb7cc0a` | MIT | pattern-only |
| <https://github.com/Hassaan-Elahi/Writing-Styles-Classification-Using-Stylometric-Analysis> | `abf3027b75501669dc87eb22d3d289c7ecf7d1b2` | MIT | pattern-only |
| <https://github.com/michaeleby1/stylometric-analysis-project-gutenberg> | `644ddeeffd595b7971ba46e87e28ea38d3dc56ce` | no license file observed | pattern-only |
| <https://github.com/pan-webis-de/pan-code> | `c32432d0e9a161450d46d33264df950b5aa3eec0` | MIT | pattern-only |
| <https://github.com/mullerpeter/authorstyle> | `234e785d96f8345549edbdad07195243a4704599` | MIT | pattern-only |
| <https://github.com/ivannikov-lab/style-change-analysis> | `bf46b65db7fc32b14efcb08592d72e5883db8d98` | Apache-2.0 | pattern-only |
| <https://github.com/sam0jones0/pyantistylometry> | `8f08e609b98509edebc06bf62773fa758d06fa71` | no license file observed | pattern-only |
| <https://github.com/ngpepin/stylometric-transfer> | `1d8d479137516387a643a266435bd5049501b831` | PolyForm Noncommercial 1.0.0 | pattern-only / runtime-deferred |
| <https://github.com/ContextLab/llm-stylometry> | `1411b89d589198d470097e20f986e2c92b200400` | MIT | pattern-only |
| <https://github.com/llm-authorship/survey> | `a1f183dfdf5077a5df8fdc3b428bcd6fd7a1da83` | MIT | index-plus-pattern |

`jpotts18/stylo` was checked as a candidate name but `git ls-remote` returned
repository-not-found, so it was not promoted.

## Absorbed patterns

- `stylometric_author_fingerprint_gate`
  - Build an inspectable style profile from measurable features.
  - Version the profile by corpus scope, feature family, settings, and reviewer.
  - Use fingerprints as calibration/risk evidence, not as a target to copy.

- `function_word_syntax_style_gate`
  - Track function words, punctuation, sentence rhythm, readability, vocabulary
    richness, and syntactic features by window.
  - Keep dialogue/register exceptions explicit.
  - Convert source ranges into a new local house-style profile.

- `authorship_attribution_similarity_gate`
  - Use source-author similarity as a risk signal.
  - Same-type drafts should be closer to the new approved style baseline than
    to the source author/source text.
  - Record distance thresholds and false-positive notes.

- `style_overfit_regression_gate`
  - Run windowed checks after entity remap, paraphrase, humanization, and
    copyedit.
  - Regression fixtures should include renamed and polished examples because
    source voice leakage survives surface substitutions.
  - A grammar-clean chapter can still fail if it overfits source style.

- `paraphrase_independence_review_gate`
  - Separate allowed abstract voice goals from blocked author-mimicry.
  - Reject prompts that require source-specific phrase families, tics, scene
    order, or cadence.
  - Require author-visible accept/ignore/rewrite decisions before accepting
    humanized or style-transferred prose.

## MuMuAINovel projection

Updated durable artifacts:

- `backend/app/services/source_discovery_service.py`
  - added discovery queries, static source summaries, pattern classification,
    pattern-pack targets, hints, inspired remap keys, and copy-risk hints
- `backend/app/services/source_pattern_pack_prompt.py`
  - added digest exposure for the five new stylometry/style-overfit gates
- `backend/app/services/book_remix_context_service.py`
  - added continuation/inspired audit section for stylometry and overfit review
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
  - updated to `source_candidate_count: 165`
  - updated to `workflow_patterns: 190`

## Runtime exclusions

- Do not import GPL or noncommercial source code.
- Do not run notebooks, package installs, HTTP API harnesses, model training,
  GUI dashboards, or provider-backed style-transfer scripts.
- Do not store source books, author corpora, prompts, or trained style models
  inside MuMuAINovel without a separate provenance and rights review.
- Treat author-style transfer as a copy-risk surface, not a default generation
  feature.

## Verification notes

Static checks used:

- `git ls-remote --symref <repo> HEAD`
- README/LICENSE static reads through public raw GitHub content
- no clone/install/execute

Projected test coverage:

- source metadata classification for stylometry/style-overfit sources
- pattern-pack target and digest exposure
- continuation and inspired context audit rendering

## Frontend surfacing addendum - 2026-06-10

Fresh public `git ls-remote --symref HEAD` check ran on
2026-06-10 19:04 +08:00 and was stored only under
`tmp/source-intake-copy-style-trope-2026-06-10/head-manifest.json`.

Observed HEADs:

- `computationalstylistics/stylo`: `8e18eb1c4e3fc6e0356a9d160b0e87cfd3928290`
- `fastdatascience/faststylometry`: `89e2b48a674a54ffdcc717e0373ce2571eb7cc0a`
- `Hassaan-Elahi/Writing-Styles-Classification-Using-Stylometric-Analysis`:
  `abf3027b75501669dc87eb22d3d289c7ecf7d1b2`
- `michaeleby1/stylometric-analysis-project-gutenberg`:
  `644ddeeffd595b7971ba46e87e28ea38d3dc56ce`
- `pan-webis-de/pan-code`: `c32432d0e9a161450d46d33264df950b5aa3eec0`
- `mullerpeter/authorstyle`: `234e785d96f8345549edbdad07195243a4704599`
- `ivannikov-lab/style-change-analysis`: `bf46b65db7fc32b14efcb08592d72e5883db8d98`
- `sam0jones0/pyantistylometry`: `8f08e609b98509edebc06bf62773fa758d06fa71`
- `ngpepin/stylometric-transfer`: `1d8d479137516387a643a266435bd5049501b831`
- `ContextLab/llm-stylometry`: `1411b89d589198d470097e20f986e2c92b200400`
- `llm-authorship/survey`: `a1f183dfdf5077a5df8fdc3b428bcd6fd7a1da83`
- `LSYS/LexicalRichness`: `69e6b8f381d6b86ec826911c3f0bb2fb298aac25`
- `HLasse/TextDescriptives`: `0bbc6600bcdb3b6fcb3b6618375428005e12e133`

Project integration delta:

- `BookRemixSourceDiscoveryPanel.tsx` now includes these repositories in the
  default public GitHub seed list.
- The source-discovery UI now pins `Stylometry / style overfit gates` for
  style-axis diversity, stylometric author fingerprints, function-word/syntax
  style, authorship similarity, overfit regression, paraphrase independence,
  and AI-prose fingerprint clusters.
- `sourceDiscovery.ts` exposes the corresponding pattern-pack fields so
  source-book style can be used as bounded calibration rather than copied voice.

Runtime boundary is unchanged: no stylometry package, notebook, model, or
style-transfer pipeline was installed or executed.
