# Novel Source Discovery - 2026-06-10 LongWriter / LongReward

## Scope

This note records a pattern-only intake pass for long-output generation and
long-context evaluation sources that can improve MuMuAINovel's 拆书续写 and
同类型仿写 flows.

No repository was cloned. No package was installed. No model, dataset, provider,
Docker stack, MCP server, shell script, or project runtime was executed.

## Sources

- `THUDM/LongWriter`
  - URL: `https://github.com/THUDM/LongWriter`
  - Observed HEAD: `447539b356a8b09760b51eca876e19b6fc1f2dd7`
  - License: Apache-2.0
  - Public metadata: 1865 stars, pushed `2025-06-24`, updated `2026-06-09`
  - Static surface: `agentwrite/plan.py`, `agentwrite/write.py`,
    `agentwrite/prompts/plan.txt`, `agentwrite/prompts/write.txt`,
    `evaluation/eval_length.py`, `evaluation/eval_quality.py`,
    `evaluation/longbench_write*.jsonl`, `evaluation/longwrite_ruler.jsonl`

- `THUDM/LongReward`
  - URL: `https://github.com/THUDM/LongReward`
  - Observed HEAD: `c56577876cff75a963c90b3551df952f095b4c06`
  - License: Apache-2.0
  - Public metadata: 62 stars, pushed `2024-10-29`, updated `2025-12-29`
  - Static surface: `long_reward/auto_scorer.py`,
    `long_reward/prompts/*_few_shot.txt`, `evaluation/LongBench*`

- `THU-KEG/LongWriter-V`
  - URL: `https://github.com/THU-KEG/LongWriter-V`
  - Observed HEAD: `ea87eb2af54731375f1384c5fbb961fc1e860820`
  - License: MIT
  - Public metadata: 22 stars, pushed `2025-03-29`, updated `2026-04-11`
  - Static surface: `agentwrite/outline_vlm.py`,
    `agentwrite/prompts/plan.txt`, `agentwrite/prompts/write.txt`,
    `eval/mmlongbench_write.py`, `eval/longwrite_v_ruler.py`

## Absorbed patterns

- `agentwrite_plan_write_pipeline`
  - Split ultra-long generation into a planning artifact and a writing artifact.
  - Validate the plan before prose expansion.
  - Link each writing stage back to its plan segment, target length, accepted
    context, and post-write change package.

- `long_output_length_quality_ruler`
  - Measure output length and output quality together.
  - Reject long chapters that hit word count through repetition, truncation,
    premature summary closure, canon drift, or style collapse.
  - Add stress-test style checks for long continuation batches.

- `long_context_reward_dimension_gate`
  - Score long-context outputs on separate dimensions:
    helpfulness, logicality, faithfulness, and completeness.
  - Do not average away a faithfulness or logicality failure.
  - Convert low dimensions into named fix tasks before canon write-back.

## MuMuAINovel adaptation

- Continuation prompts should carry long-output gates:
  - plan artifact present
  - write stage mapped to plan segment
  - target length vs actual length
  - truncation and repetition checks
  - canon/style/coherence checks
  - helpfulness/logicality/faithfulness/completeness review

- 同类型仿写 prompts should remap long-output structure:
  - rebuild plan-write stage boundaries
  - avoid source outline order
  - use transformed-story evidence for reward dimensions
  - reject source-like section pacing even when the text is long and fluent

## Updated artifacts

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
