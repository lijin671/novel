# Novel source discovery - canon / sparks / Codex parity / API-free cataloging / rights-safe memory / desktop agents

Date: 2026-06-12
Scope: pattern-only static intake for MuMuAINovel book remix, long-form continuation, source digestion, and same-type writing safety.

## Boundary

Reviewed repositories were treated as untrusted upstream data. Intake used public GitHub Search metadata, GitHub repository metadata, `git ls-remote`, root marker names, and README snippets only. No clone, checkout, install, package manager, Docker, MCP server, desktop app, browser automation, Obsidian vault import, database startup, provider call, login, credential read, manuscript import, release asset execution, hook registration, or generated-output import was performed.

GitHub Search hit unauthenticated API rate limits during later exploratory queries. The six promoted candidates below all have direct source URLs and reachable HEAD evidence.

## Sources

- `mindattic/StreetSamurai`
  - Source: https://github.com/mindattic/StreetSamurai
  - Observed HEAD: `e953178d73605d63f0792741104f4539aefcc8d8`
  - License: no license observed in GitHub metadata
  - Family: C#/.NET Blazor long-form fiction engine
  - Absorbed pattern: `strand_beat_quorum_canon_gate`
  - Reusable idea: model long-form structure as Strand/Beat records linked to SQL/vector canon and a directional entity graph; keep multi-provider Quorum review and contradiction sweeps as review evidence, not automatic canon mutation.
  - Deferred runtime: Azure deployment, SQL Server, vector DB/embeddings, providers, MCP, scripts, local worldbuilding data, and generated manuscripts.

- `F-S-Neal/substrate-method`
  - Source: https://github.com/F-S-Neal/substrate-method
  - Observed HEAD: `4e93412bd02544eee9810785e25227d654815f49`
  - License: MIT
  - Family: Obsidian+AI fiction/worldbuilding vault workflow
  - Absorbed pattern: `substrate_spark_canon_promotion_gate`
  - Reusable idea: capture messy ideas as tagged sparks, review and choose them, assemble topic reports, then promote only selected report evidence into canon while keeping rejected ideas separate.
  - Deferred runtime: Obsidian vault zip, external AI prompts, local author notes, vault imports, and provider calls.

- `MrMO0802/Webnovel-Writer-Codex`
  - Source: https://github.com/MrMO0802/Webnovel-Writer-Codex
  - Observed HEAD: `3e5137dc21fa8792b3071505bcc08849c8949fc5`
  - License: GPL-3.0
  - Family: Codex-native derivative webnovel writing skill/plugin pack
  - Absorbed pattern: `codex_webnovel_plugin_parity_gate`
  - Reusable idea: derivative Claude/Codex skill packs need explicit parity evidence across plugin metadata, agents, skills, hooks, evals, references, templates, and adapter support before their workflow assumptions are trusted.
  - Deferred runtime: plugin install, hook registration, dashboard runtime, skill/agent body import, upstream prompt bodies, and generated project content.

- `teangtang1122/NovelWritingAgent`
  - Source: https://github.com/teangtang1122/NovelWritingAgent
  - Observed HEAD: `adb968674d6987e39ab35110daff9e036e8087e6`
  - License: no license observed
  - Family: local Chinese long-form novel workspace / external-agent API-free workflow
  - Absorbed pattern: `external_agent_api_free_cataloging_gate`
  - Reusable idea: default external agents to API-free project/cataloging tools; separate internal model quota tools; allow parallel fact extraction, but serialize candidate generation by chapter order; keep draft save, quality review, chapter creation, and story updates as separate id-bearing steps.
  - Deferred runtime: packaged Windows launcher, backend/frontend startup, MCP tools, internal model quota, providers, database state, and scripts.

- `TommyShalby/longform-novel-drafting-toolkit`
  - Source: https://github.com/TommyShalby/longform-novel-drafting-toolkit
  - Observed HEAD: `672834266bb2b85f90fe8ea10458cbbb5ae640bd`
  - License: MIT
  - Family: compact Python source-to-memory long-form drafting pipeline
  - Absorbed pattern: `rights_safe_source_to_memory_pipeline_gate`
  - Reusable idea: require rights status and source provenance before extracting PDF/TXT, chunking, rolling summaries, global memory, chapter plans, original chapter drafting, generated-chapter summaries, and final combine.
  - Deferred runtime: requirements install, file extraction, provider calls, API keys, service-account files, private notes, and generated manuscripts.

- `simple-calcate/writerAgent`
  - Source: https://github.com/simple-calcate/writerAgent
  - Observed HEAD: `4560752e10a824fdf9f15b0d07c19a3517eab2b2`
  - License: AGPL-3.0
  - Family: Electron desktop webnovel writing assistant
  - Absorbed pattern: `desktop_agent_planning_reflection_gate`
  - Reusable idea: expose desktop-agent assistance as plan -> tool -> memory -> draft -> reflection -> author acceptance, with semantic search and foreshadowing checks as cited evidence rather than hidden rewrite authority.
  - Deferred runtime: Electron app, releases, package scripts, local files, web search, API keys, and desktop packaging.

## Durable integration

Updated the source-discovery pipeline to surface these gates in:

- default GitHub query and repository seeds
- static repository pattern overrides
- pattern keyword detection
- absorbed-pattern scoring
- bible enrichment targets
- whole-book analysis targets
- continuation prompt hints
- inspired mapping targets
- inspired transformation and copy-risk hints
- pattern-pack prompt digest allowlist
- frontend pattern-pack payload types and panel copy
- backend and frontend tests

## Runtime gates

These sources remain pattern-only. Promotion to executable support requires:

1. exact project/source-material scope and rights status
2. tool/server/database/provider allowlists and denylist
3. credential/API-key/session exclusion
4. storage and generated-output custody
5. rollback and cleanup steps
6. non-provider default verifier
7. explicit user confirmation for any runtime trial
