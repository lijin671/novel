# Novel Source Discovery - 2026-06-09 Story Quality Evaluation

## Scope

This note records a static source-intake pass for MuMuAINovel story-quality evaluation, same-type creation screening, chapter variant comparison, style-axis review, and long-story event planning.

The intake focused on quality rubrics and objective comparison patterns that can improve continuation and imitation output without importing external runtime code, datasets, model weights, or benchmark tables.

## Safety Boundary

- Posture: `pattern-only`.
- Intake surface: public repository metadata, public README/root-file/LICENSE inspection, and `git ls-remote` HEAD evidence.
- Scratch files: `tmp/source-intake-2026-06-09-story-quality-eval/`.
- Not performed: install, clone for runtime, package-manager call, script execution, model/provider call, benchmark run, dataset/model-weight import, Docker/MCP/browser/desktop launch, credential read, or host configuration mutation.
- Runtime trials remain blocked until a separate local safety contract defines scope, auth, secrets, network, cleanup, rollback, and verification.

## Source Snapshot

- `lars76/story-evaluation-llm`
  - URL: https://github.com/lars76/story-evaluation-llm
  - Branch / HEAD: `main` / `0cfd38760e6bf929988c84b0b7ce3e6229d2ee3e`
  - License evidence: `LICENSE` file observed, MIT text
  - Posture: `pattern-only`
  - Reusable value: q1-q15 story-quality rubric, overall/length score, character consistency, reader interest, plot resolution, ranked weaknesses.

- `lechmazur/writing`
  - URL: https://github.com/lechmazur/writing
  - Branch / HEAD: `main` / `efa30bf6bf762765d05b83edc486f7f0398fff1a`
  - License evidence: no root license file observed in static pass
  - Posture: `pattern-only`
  - Reusable value: head-to-head story comparisons under the same creative brief, pairwise margins, evaluator agreement, order-swap bias reduction.

- `lechmazur/writing_styles`
  - URL: https://github.com/lechmazur/writing_styles
  - Branch / HEAD: `main` / `edecdd56162ec2f996ab80fc20edcfe9f9b3813d`
  - License evidence: no root license file observed in static pass
  - Posture: `pattern-only`
  - Reusable value: style fingerprints and diversity axes for voice/diction, rhythm/syntax, POV/discourse, structure/pacing, tone, imagery, dialogue, experimentation, closure, and content choices.

- `anirudhlakkaraju/cs4_benchmark`
  - URL: https://github.com/anirudhlakkaraju/cs4_benchmark
  - Branch / HEAD: `master` / `24769694d5549b879df8854a8c470e41ff1d561f`
  - License evidence: `LICENSE` file observed, MIT text
  - Posture: `pattern-only`
  - Reusable value: constraint specificity, constraint satisfaction, coherence, perplexity, and creativity balance for constrained story generation.

- `Theltn/AICreativityJudge`
  - URL: https://github.com/Theltn/AICreativityJudge
  - Branch / HEAD: `main` / `1b28b363bce6f9a22e6740d660b69c6d91502ebd`
  - License evidence: no root license file observed in static pass
  - Posture: `pattern-only`
  - Reusable value: five-dimension creativity rubric: lexical richness, syntactic complexity, novelty, imagery, and narrative dynamics.

- `clchinkc/story-bench`
  - URL: https://github.com/clchinkc/story-bench
  - Branch / HEAD: `main` / `2722769c79c7aa79a8bb7a90fa9da724974ee5e8`
  - License evidence: `LICENSE` file observed, MIT text
  - Posture: `pattern-only`
  - Reusable value: story-theory tasks, beat interpolation/revision, constrained continuation, theory conversion, weighted LLM-judge criteria, programmatic checks.

- `THU-KEG/StoryWriter`
  - URL: https://github.com/THU-KEG/StoryWriter
  - Branch / HEAD: `main` / `08c32d74ce08b46a762951c7f2235772022baa77`
  - License evidence: no root license file observed in static pass
  - Posture: `pattern-only`
  - Reusable value: Outline Agent, Planning Agent, Writing Agent, event-based outlines, chapter-wise plans, dynamic story-history compression.

- `ZJU-LLMs/OpenStory`
  - URL: https://github.com/ZJU-LLMs/OpenStory
  - Branch / HEAD: `main` / `e73b6079bc9c7ca61bae45e1e55ea5e9b3bee786`
  - License evidence: `LICENSE` file observed, Apache-2.0 text
  - Posture: `pattern-only`
  - Reusable value: multi-agent story-world simulation, dynamic agent add/remove, character behavior, social interaction, story evolution. Runtime/provider configuration stays out of scope.

## Absorbed Patterns

- `pairwise_story_comparison_ranking`
  - Generate or compare matched variants under the same creative brief.
  - Reduce position bias with order-swapped review where applicable.
  - Keep the winning rationale as revision evidence, not as canon by itself.

- `multidimensional_quality_rubric`
  - Score drafts across grammar, clarity, causal connection, scene purpose, internal consistency, character consistency, motivation, dialogue, reader interest, and resolution.
  - Convert ranked weaknesses into targeted revision tasks.

- `story_theory_beat_evaluation`
  - Check whether a beat performs its narrative function.
  - For revision, separate diagnosis, flaw fix, beat satisfaction, preservation, and minimal-change criteria.

- `constraint_specificity_creativity_benchmark`
  - Track hard constraints per prompt.
  - Review constraint satisfaction together with creativity and coherence.
  - Reject checklist prose or copied source events when constraints become specific.

- `style_axis_diversity_fingerprint`
  - Fingerprint style on visible axes: voice/diction, rhythm/syntax, POV/discourse, pacing, tone, imagery, dialogue, experimentation, closure.
  - Use style-axis evidence to avoid voice collapse across batches.

- `event_outline_history_compression`
  - Plan long stories as event outlines and chapter-wise event plans.
  - Compress prior history around the current event, while keeping omitted-history evidence inspectable.

- `agentic_story_world_simulation`
  - Treat multi-agent story-world simulation as a proposal generator for character behavior, social interaction, and world evolution.
  - Simulated outcomes require canon and author review before write-back.

## MuMuAINovel Integration Points

- `source_discovery_service.py`
  - Added default GitHub queries and repository URLs for story-quality evaluation and benchmark sources.
  - Added keyword classification, static summaries, priorities, analysis targets, prompt hints, state hints, and same-type remap/copy-risk guidance for the seven new patterns.

- `source_pattern_pack_prompt.py`
  - Added the seven hint families to pattern-pack digest rendering.

- `book_remix_context_service.py`
  - Added `Story quality evaluation audit` for continuation and same-type inspired contexts.
  - The audit surfaces pairwise variant comparison, quality rubric scoring, story-theory beat checks, constraint specificity, style-axis fingerprints, event-history compression, and simulation proposal boundaries.

- `backend/app/references/novel-source-pattern-pack-2026-06-09.json`
  - Refreshed from 67 to 75 source candidates.
  - Added story-quality evaluation pattern groups and guidance.

## Verification Targets

- `test_story_quality_eval_projects_are_classified_as_quality_patterns`
- `test_story_quality_eval_pattern_pack_exposes_variant_and_rubric_guidance`
- `test_default_discovery_sources_include_story_quality_eval_projects`
- `test_build_remix_continuation_context_block_renders_story_quality_eval_audit`
