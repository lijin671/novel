# Novel Source Discovery - 2026-06-10 Writing Benchmark / Story Evaluation

## Scope

This note records a pattern-only intake pass for creative-writing benchmark and
story-evaluation sources that can improve MuMuAINovel's 拆书续写 and 同类型仿写
flows.

No repository was cloned. No package was installed. No benchmark script,
notebook, dataset, model, provider call, Docker stack, MCP server, shell script,
PowerShell script, or project runtime was executed.

GitHub REST API returned anonymous rate-limit HTTP 403 during this pass. Source
metadata below therefore uses `git ls-remote --symref HEAD`, raw README, and raw
LICENSE checks only. No credential, token, cookie, or authenticated request was
used.

## Sources

- `X-PLUG/WritingBench`
  - URL: `https://github.com/X-PLUG/WritingBench`
  - Observed default branch: `main`
  - Observed HEAD: `ae2d5176449b7b769815482641d35926f26793eb`
  - License: Apache-2.0 (`LICENSE` reachable)
  - Static surface: `README.md`, `LICENSE`
  - Public README signal: generative-writing benchmark, 1,000 real-world
    writing queries, instance-specific criteria, requirement-dimension scores,
    model-augmented query generation, human-in-the-loop refinement, material
    collection, and material pruning.

- `EQ-bench/creative-writing-bench`
  - URL: `https://github.com/EQ-bench/creative-writing-bench`
  - Observed default branch: `main`
  - Observed HEAD: `13fc250dbff26317d9367601002906e8bb096c09`
  - License: no root license file observed by raw file checks
  - Static surface: `README.md`, `requirements.txt`, `.env.example`
  - Public README signal: Creative Writing Benchmark v3, hybrid rubric,
    pairwise matchups, Elo / Glicko-2 rating, win margins, and bias mitigation
    for length, position, verbosity, and poetic incoherence.

- `EQ-bench/longform-writing-bench`
  - URL: `https://github.com/EQ-bench/longform-writing-bench`
  - Observed default branch: `main`
  - Observed HEAD: `34f60a028c3f973c19cde98dc5a9e8f9875a87e3`
  - License: no root license file observed by raw file checks
  - Static surface: `README.md`, `requirements.txt`, `.env.example`
  - Public README signal: longform creative writing benchmark with
    brainstorming, planning, critical reflection, character profiles, eight
    chapter novella writing, and narrative consistency judging.

- `dig-team/hanna-benchmark-asg`
  - URL: `https://github.com/dig-team/hanna-benchmark-asg`
  - Observed default branch: `main`
  - Observed HEAD: `282f27536a5d05ad4ce14298abcd70c45668fed2`
  - License: MIT (`LICENSE` reachable)
  - Static surface: `README.md`, `LICENSE`, `requirements.txt`
  - Public README signal: HANNA human-annotated narratives for automatic story
    generation evaluation, 1,056 stories from 96 prompts, three raters per
    story, and six reader-facing axes: relevance, coherence, empathy, surprise,
    engagement, and complexity.

## Absorbed patterns

- `instance_specific_writing_criteria_gate`
  - Attach local acceptance criteria to each continuation or same-type writing
    task.
  - Treat canon facts, requested beat, style target, format/length, and reader
    promise as separate requirement dimensions.
  - Do not let fluent prose hide a failed local requirement.

- `material_grounded_query_refinement`
  - Separate required materials from optional/noisy references before drafting.
  - Rewrite ambiguous or unrealistic local tasks before generation.
  - For 同类型仿写, keep only abstract constraints and rebuild concrete facts.

- `hybrid_rubric_pairwise_elo_judge`
  - Score candidate drafts with a rubric first.
  - Use pairwise comparison only to distinguish close variants.
  - Keep pairwise wins explainable by margin and concrete story evidence.

- `judge_bias_mitigation_check`
  - Audit length, position/order, verbosity, and ornate-but-incoherent prose
    bias before accepting a winning draft.
  - Swap candidate order in pairwise review.
  - Reject evaluations that reward padding over usable continuation canon.

- `plan_reflect_character_chapter_pipeline`
  - Persist brainstorm, plan, critique/reflection, and character profiles before
    chapter generation.
  - Link chapter sequence generation to that trace.
  - Use the trace to prevent later chapters from inventing incompatible motives.

- `human_story_metric_panel`
  - Track reader-facing story quality on separate axes: relevance, coherence,
    empathy, surprise, engagement, and complexity.
  - Convert low axes into named repairs.
  - Do not average away engagement or empathy collapse.

## MuMuAINovel adaptation

- Continuation prompts now gain a creative-writing benchmark audit section when
  the source pattern pack contains these patterns.
- Pattern-pack digest now exposes benchmark criteria, material pruning,
  pairwise/Elo judge, bias mitigation, longform planning trace, and human story
  metric hints.
- Same-type creation now gets remap targets for instance criteria, material
  grounding, hybrid judge, judge-bias checks, plan-reflect-character traces, and
  reader-facing metric axes.

## Updated artifacts

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
