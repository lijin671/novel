# Novel Source Discovery - 2026-06-11 Chinese Webnovel Platform KB + Resilient Engine Gates

## Scope

Static source-intake for MuMuAINovel 拆书续写 / 同类型仿写 workflow.

No clone, install, package manager, MCP/server launch, CLI execution, provider call,
credential read, browser/desktop control, or external project code execution was
performed. Evidence came from public GitHub metadata, `git ls-remote HEAD`, and
raw README/LICENSE markers only.

Boundary marker:

```text
public_github_webnovel_platform_kb_resilient_engine_static_review_no_clone_no_runtime_20260611
```

## Sources

### `TianHengZhuang/Chinese-WebNovel-Master`

- URL: https://github.com/TianHengZhuang/Chinese-WebNovel-Master
- Observed HEAD: `bdb4ed86ef8c8022966a5c76687aed73ad5b1f67`
- Default branch: `main`
- License: no license file observed through GitHub metadata
- Stars signal: `2`
- Posture: `pattern-only / runtime-deferred`
- Static markers: multi-agent Chinese web fiction workflow, platform suitability,
  platform-specific reader preferences, market analysis, title/tag/synopsis
  generation, suspense hook systems, retention optimization, publishing package.

Absorbed patterns:

- `platform_kb_retention_strategy_gate`
- `chapter_end_hook_retention_ladder_gate`

Runtime exclusions:

- no skill load
- no provider/model call
- no platform publishing
- no upstream knowledge-base body import

### `tance-mang/chinese-webnovel-skills`

- URL: https://github.com/tance-mang/chinese-webnovel-skills
- Observed HEAD: `7d84e456b36eef3838404f95cf128072418f1147`
- Default branch: `main`
- License: `MIT`
- Stars signal: `2`
- Posture: `pattern-only / selective-local-projection later only`
- Static markers: Chinese web-novel skill toolkit, golden opening, cheat system,
  character setup, prose expansion, 爽点打脸, rhythm labeling, 追读诊断,
  de-AI polish, submission review, platform trends, fanfic compliance, export
  setup for multiple model products.

Absorbed patterns:

- `platform_kb_retention_strategy_gate`
- `chapter_end_hook_retention_ladder_gate`

Runtime exclusions:

- no plugin marketplace install
- no skill body bulk import
- no CLI/API provider connection
- no platform submission flow

### `yaopushen/webnovel-kb`

- URL: https://github.com/yaopushen/webnovel-kb
- Observed HEAD: `c2214489e78ce807c3e99dee48d9101b6b1e4748`
- Default branch: `main`
- License: no license file observed through GitHub metadata
- Stars signal: `1`
- Posture: `pattern-only / runtime-deferred`
- Static markers: Chinese webnovel knowledge-base MCP server, TXT import,
  semantic/BM25/hybrid/rerank search, plot-pattern extraction, writing-template
  extraction, style analysis, chapter outline extraction, imitation rewrite
  levels, OAuth PKCE, async tasks, OpenAI-compatible model surfaces.

Absorbed pattern:

- `webnovel_kb_mcp_runtime_boundary_gate`

Runtime exclusions:

- no MCP/server launch
- no package install
- no OAuth/provider/API key surface
- no embedding or external search call
- no novel corpus import

### `ohh-000/longform-novel-engine`

- URL: https://github.com/ohh-000/longform-novel-engine
- Observed HEAD: `ff43e2ece580643cf9dddc45c5f759e2137db25d`
- Default branch: `main`
- License: `MIT`
- Stars signal: `0`
- Posture: `pattern-only`
- Static markers: long-context multi-agent fiction workflow with Director,
  Opening Audition, Writer, Critic, Patch Reviser, Reader Simulator, Archivist,
  State Validator, strict quality gates, context packs, hidden secrets,
  foreshadowing, world rules, and long-running state validation.

Absorbed patterns:

- `long_context_role_boundary_state_validation_gate`
- `chapter_end_hook_retention_ladder_gate`

Runtime exclusions:

- no Python environment
- no tests/CLI execution
- no provider/model call
- no private story state import

### `Jackela/Novel-Engine`

- URL: https://github.com/Jackela/Novel-Engine
- Observed HEAD: `47ae06b642763482f6126515bd4587e0a2cfef22`
- Default branch: `main`
- License: `MIT`
- Stars signal: `6`
- Posture: `pattern-only`
- Static markers: local-first novel engine, chapter Markdown as source of truth,
  sidecar JSON evidence, run artifacts, raw model output, custom caching,
  duplicate-call avoidance, thread-safe concurrency, graceful degradation,
  circuit breakers, review report, manuscript export.

Absorbed pattern:

- `agent_cache_concurrency_recovery_gate`

Runtime exclusions:

- no `uv` or CLI/API/frontend runtime
- no provider/model call
- no local workspace/artifact read

## Project Fusion

### Platform-KB retention strategy

New durable rule:

- keep platform-specific knowledge as a strategy matrix
- split genre trend, platform fit, reader promise, title/tag/synopsis, and
  commercial potential into separate fields
- never treat a platform example or knowledge-base body as reusable canon

MuMuAINovel targets:

- `platform_reader_preference_matrix`
- `commercial_storytelling_strategy_policy`
- `platform_reader_preference_report`

### Chapter-end hook ladder

New durable rule:

- every chapter ending should be scored for unresolved pressure, immediate
  question, payoff delay, emotional charge, and read-next pull
- hook evidence must be generated from transformed stakes and local character
  desire, not copied source cliffhanger timing

MuMuAINovel targets:

- `chapter_end_hook_ladder`
- `read_next_intent_scorecard`
- `chapter_end_hook_ladder_report`

### Webnovel KB runtime boundary

New durable rule:

- knowledge-base retrieval must label corpus, chunk, search mode, rerank reason,
  and whether the hit is source analysis, style-only evidence, or accepted canon
- MCP, OAuth, embeddings, external search, and providers are runtime surfaces
  held behind a separate admission contract

MuMuAINovel targets:

- `webnovel_kb_runtime_boundary_policy`
- `plot_style_search_namespace_manifest`
- `webnovel_kb_boundary_report`

### Cache / concurrency / recovery gate

New durable rule:

- deduplicate generation calls by role, prompt digest, context-pack id, model
  settings, chapter id, and source-boundary mode
- concurrent agents must record run id, lock scope, retry count, circuit-breaker
  state, graceful-degradation result, and reviewer outcome

MuMuAINovel targets:

- `generation_cache_idempotency_policy`
- `concurrent_agent_recovery_policy`
- `agent_cache_idempotency_report`

### Long-context role-boundary validation

New durable rule:

- Director, Writer, Critic, Reader Simulator, Archivist, and State Validator use
  different context visibility
- Writer executes accepted blueprint; state write-back and corruption repair are
  explicit validator/reviewer actions
- long-context packs must be checked for stale canon and role-boundary leaks
  before queuing the next chapter

MuMuAINovel targets:

- `long_context_role_visibility_policy`
- `state_validator_quality_gate_policy`
- `long_context_role_boundary_report`

## Verification

Fresh local verification for this intake batch should include:

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py -q
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py
git diff --check -- backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py backend/tests/services/test_source_discovery_service.py docs/references/novel-source-discovery-2026-06-11-chinese-webnovel-resilient-engine.md
```
