# Novel Source Discovery - 2026-06-10 Eval / Observability / Prompt Regression Patterns

## Scope

This note records a static pattern-only intake for MuMuAINovel book remix work.
The target improvement is safer book-decomposition continuation and same-type imitation:
context faithfulness review, retrieval trace observability, and prompt regression gates.

## Sources

- `explodinggradients/ragas`
  - HEAD: `298b68274234c060deacab3cf5fb52aa3a20e885`
  - License posture: Apache-2.0 from metadata used in tests/reference pack.
  - Absorbed as `context_faithfulness_eval_gate` only.
- `confident-ai/deepeval`
  - HEAD: `6e87116385dc76a0c276c14c96c826e5de5d0eb6`
  - License posture: Apache-2.0 from metadata used in tests/reference pack.
  - Absorbed as faithfulness and prompt-regression evidence only.
- `truera/trulens`
  - HEAD: `3fb807eea0ddf25cac5e65b1418a5af33f719586`
  - License posture: MIT from metadata used in tests/reference pack.
  - Absorbed as groundedness and retrieval-trace evidence only.
- `Arize-ai/phoenix`
  - HEAD: `15912cb5787c9fa11ba7e35ade1ea40868139290`
  - License posture: Elastic-2.0 from metadata used in tests/reference pack.
  - Absorbed as `retrieval_trace_observability_gate` only.
- `promptfoo/promptfoo`
  - HEAD: `aba48e4cdef5b37fd7816ff7dd4ac42a442e1238`
  - License posture: MIT from metadata used in tests/reference pack.
  - Absorbed as `prompt_regression_eval_suite` only.
- `openai/evals`
  - HEAD: `8eac7a7de5215c907fbddc30efdaf316913eccdd`
  - License posture: MIT from metadata used in tests/reference pack.
  - Absorbed as custom eval and golden-case regression evidence only.

Reachability was confirmed with `git ls-remote ... HEAD`.
No repository was cloned.

## Absorbed patterns

- `context_faithfulness_eval_gate`
  - Check whether generated facts are supported by accepted chapter memory,
    bible state, retrieved context, and summary anchors before canon write-back.
  - Track faithfulness, groundedness, context precision, and context recall as
    review evidence, not as automatic acceptance.
  - For same-type imitation, score against transformed-story canon only.

- `retrieval_trace_observability_gate`
  - Persist query, selected chunks, omitted candidates, context relevance reason,
    and generation spans that used the context.
  - Keep source-analysis traces separate from transformed-canon traces.

- `prompt_regression_eval_suite`
  - Keep golden continuation and same-type fixtures for prompt changes.
  - Regression cases should cover context packing, copy-risk rejection,
    canon write-back, and source-canon leakage.

## MuMuAINovel integration

Updated surfaces:

- `source_discovery_service.py`
  - Added default GitHub queries and repository URLs.
  - Added pattern keywords, static source overrides, family detection,
    pattern-pack hints, bible targets, whole-book targets, and inspired-copy gates.
- `source_pattern_pack_prompt.py`
  - Added digest rendering for the three new hint groups.
- `book_remix_context_service.py`
  - Added continuation and inspired context audit section for evaluation,
    retrieval traces, and prompt regression.
- `novel-source-pattern-pack-2026-06-10.json`
  - Added 6 source titles.
  - Updated source candidate count from 98 to 104.
  - Updated workflow patterns from 139 to 142.

## Runtime gates

This is static source intake only.

- No clone.
- No install.
- No package hook.
- No external eval execution.
- No provider/model call.
- No tracing service, Docker stack, red-team scanner, native binary, or script launch.
- No external code, dataset, prompt set, or eval runner imported into MuMuAINovel runtime.

Future runtime trial requires a separate local safety contract covering scope,
license, dependency graph, provider/auth surface, network behavior, cleanup,
rollback, and verification.
