# Novel Source Discovery 2026-06-13 - Agent Loop / Desktop RAG / Novel Harness

## Scope

Static source intake for MuMuAINovel book-remix, continuation, same-type creation, and long-form Chinese webnovel production flows.

No upstream repository was cloned. No package manager, installer, script, GUI app, MCP server, RAG index,
provider call, local project, database, or model runtime was executed.

## Sources absorbed

### xiaoxiaoxiaotao/novel-ai-agent-Chinese

- URL: https://github.com/xiaoxiaoxiaotao/novel-ai-agent-Chinese
- Reachable HEAD: `7aa790ed8b3424eb173d7677d6f33e8c8c426a03`
- Default branch: `HEAD` resolved by public `git ls-remote`
- License: MIT
- Static markers reviewed: README.md, LICENSE, pyproject.toml, requirements.txt
- Absorbed pattern: `filesystem_memory_agent_loop_gate`
- Reusable idea: long-form generation should be a visible loop over filesystem-backed state:
  smart-question seed, world settings, persona/soul, global memory, chapter memory,
  accepted draft, and post-chapter memory update.
- Runtime posture: pattern-only / runtime-deferred.

### bbhzyq-dotcom/auto_novel_writer

- URL: https://github.com/bbhzyq-dotcom/auto_novel_writer
- Reachable HEAD: `aa5e09d54b81a844fafca449833af47b4e1dbfb4`
- Default branch: `HEAD` resolved by public `git ls-remote`
- License: no root license file observed in this static pass
- Static markers reviewed: README.md
- Absorbed pattern: `desktop_review_rag_retry_gate`
- Reusable idea: desktop long-novel production should make the write ? review score ? retry/accept ? memory update loop auditable,
  with score components, retry cap, local RAG hits, version snapshots, and export status captured separately.
- Runtime posture: pattern-only / runtime-deferred.

### manhai934/novel-harness

- URL: https://github.com/manhai934/novel-harness
- Reachable HEAD: `d923b7f3d182783c5f171e876aef425484e1d956`
- Default branch: `HEAD` resolved by public `git ls-remote`
- License: CC-BY-NC-SA-4.0
- Static markers reviewed: README.md, LICENSE, AGENTS.md
- Absorbed pattern: `novel_core_knowledge_pack_rag_gate`
- Reusable idea: writing tasks benefit from a chief-editor route that selects planning/writing/review/context agents,
  then attaches only rights-safe knowledge-pack and RAG references with explicit install, MCP, and index boundaries.
- Runtime posture: pattern-only / runtime-deferred.

## MuMuAINovel integration

New static pattern gates were added to:

- `source_discovery_service.py`
- `source_pattern_pack_prompt.py`
- `sourceDiscovery.ts`
- `BookRemixSourceDiscoveryPanel.tsx`
- `test_source_discovery_service.py`
- `test_source_discovery_panel_copy.py`

## Safety boundary

The absorbed value is limited to workflow vocabulary, state gates, local-memory boundaries, and acceptance checks.

Blocked by default:

- upstream code, AGENTS instructions, prompt bodies, agent files, skill bodies, generated prose, workspace state, and local project files
- uv/pip/package installation, CLI/runtime entrypoints, GUI launch, PyInstaller packaging, MCP server launch, RAG index build, and provider/model calls
- `.env`, API keys, OpenAI-compatible settings, Ollama endpoints, SQLite databases, version snapshots, exported novels, and logs
- knowledge-pack downloads, remote package installs, included/remote knowledge-pack bodies, and any source-reference corpus without user-owned or rights-cleared custody
