# Distilled Novel Toolbox platform/compliance projection

Date: 2026-06-14

## Source

- `https://github.com/dama-cyber/Distilled-Novel-Toolbox`
- Observed default branch: `main`
- Observed HEAD: `350f2bd2b23c7400509897742b22d0f2b139338d`
- Discovery channel: GitHub/static source intake
- License: not observed from root `LICENSE` or `LICENSE.md`
- Related cloud-repo packet:
  `source-intake-2026-06-14-active-goal-continuation-351-distilled-novel-toolbox-static-selective-projection-review.md`

## Posture

- pattern-only
- L1 public metadata / raw README / cloud-repo static packet review
- no clone, install, package execution, provider/model call, generation runtime,
  platform login, publishing action, prompt-body import, sample-fiction import,
  credential read, or host config mutation

## Absorbed pattern

The source contributes a Chinese web-novel toolbox shape around:

- platform/commercial fit
- compliance and sensitive-word review
- publishing analytics as planning metadata
- human polishing / de-AI wording as quality review vocabulary
- prompt and sample-fiction exclusion boundaries

Only the review-packet shape is retained. Upstream prompt templates, skill
bodies, anti-detection instructions, platform policy bodies, and generated story
examples are not imported.

## Local adaptation

`BookRemixContextService` now renders a
`Distilled Novel Toolbox platform/compliance gate` when a pattern pack includes:

- `distilled_novel_toolbox_platform_compliance_gate`
- `distilled_novel_toolbox_human_polish_boundary_gate`

Added control axes:

- `market_fit_card`
- `platform_policy_verification`
- `compliance_review_packet`
- `human_polish_boundary`
- `prompt_body_import_policy`

Added acceptance steps:

- `verify_platform_policy_current`
- `verify_compliance_review_packet`
- `verify_no_detection_evasion_or_prompt_body_import`

The gate appears in both continuation and same-type creation contexts.

## Boundary

Continuation mode may use market fit, compliance, and polish reviews only as
constraints around the target-owned manuscript. They cannot override accepted
canon or replace current authoritative platform/legal verification.

Same-type creation may transfer only the review-packet shape. It must not reuse
source platform claims, prompt templates, anti-detection instructions, sample
fiction, module text, commercial recipes, or platform policy bodies.

## Verification

- `python -m pytest backend/tests/services/test_book_remix_context_service.py::test_distilled_novel_toolbox_platform_compliance_gate_renders_context_and_audit -q`
