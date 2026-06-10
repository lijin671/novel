# Novel Source Discovery Intake - Agent Role Profile Workflow

Date: 2026-06-11

## Source

- Repository: `ayermac/novelos`
- URL: https://github.com/ayermac/novelos
- Reachable HEAD: `6cfcff3a1c78d569151da958282e6dd85f9eb308`
- License signal: MIT via public `LICENSE`
- Intake posture: `pattern-only`

## Static evidence

Reviewed public README and `git ls-remote` evidence only. GitHub API metadata returned `403`, so the prior scratch metadata is treated as a cached discovery signal, not fresh API proof.

Public README markers show:

- local-first desktop fiction workbench backed by SQLite
- LangGraph chapter workflow
- planner, screenwriter, author, polisher, editor, memory curator, and publisher roles
- workflow timeline and run details in the author workbench
- project memory for characters, world settings, factions, outlines, plot holes, instructions, and story facts
- quality diagnosis and revision support
- run observability with node events, artifacts, LLM latency/tokens, Run Doctor attribution, retry and recovery tools, and memory backfill
- reusable LLM profiles and agent-level LLM routing
- runtime surfaces for Electron, FastAPI, LangGraph, provider credentials, local config, and Electron `safeStorage`

## Reusable pattern

`agent_role_profile_workflow_gate`

The useful pattern is not the desktop application or upstream agent code. The useful pattern is a run contract that treats every writing role as a typed profile with explicit context visibility, model route, output artifact, and canon-write authority.

For MuMuAINovel this becomes:

1. Declare the active role before the chapter step starts.
2. Attach role-specific allowed inputs and hidden/blocked context classes.
3. Record which model/profile route was selected without calling any provider during source discovery.
4. Write timeline events with role id, node id, run id, artifact ids, retry state, and token/latency counters.
5. Keep planner/screenwriter/author/editor outputs as reviewable artifacts until accepted.
6. Prevent memory-curator or publisher roles from promoting rejected drafts or source-analysis notes into future context.

## Productization in MuMuAINovel

Updated source discovery so the backend can surface:

- `agent_role_profile_policy`
- `workflow_timeline_event_policy`
- `agent_role_profile_matrix`
- `workflow_timeline_run_trace`
- `agent_llm_route_audit`
- `memory_curator_publish_boundary_findings`
- `agent_role_profile_remap`
- `agent_role_profile_workflow_gate_hints`

The frontend now pins this gate under `Causal state-machine / skill workflow gates` so role routing evidence is visible beside LangGraph state-machine guidance.

## Runtime boundary

No upstream code was cloned, installed, built, or executed.

Blocked without a separate runtime safety contract:

- `pip install -e .`, npm install, desktop build, Vite, Electron, or FastAPI launch
- LangGraph workflow execution
- provider/model calls
- credential, API-key, local config, or Electron `safeStorage` access
- upstream scripts, diagnostics, recovery tools, or memory backfill
- copying upstream agent implementation or prompt text

## Deferred follow-up

`v-saprykin/storygraph` and `10Legs/novel-template` still overlap with existing graph/counterfactual and editorial stop-authority gates. Keep them as reinforcement evidence unless a sharper gap appears.
