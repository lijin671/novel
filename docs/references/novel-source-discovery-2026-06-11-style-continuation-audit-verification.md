# Novel Source Discovery - Style Continuation Audit Verification

Observed at: 2026-06-11T00:45:00+08:00

Boundary:

```text
public_github_lsremote_raw_readme_license_marker_scan_no_login_no_clone_no_runtime
```

This pass statically reviewed public GitHub metadata, reachable HEAD markers,
raw README/LICENSE markers, and root-file hints for style continuation,
serial-audit, multi-agent rewrite, story-bible context packets, and
memory-augmented verification projects.

No repository was cloned, installed, built, executed, or launched. No package
manager, Docker stack, MCP server, browser extension, native binary, provider
call, API key, token, cookie, browser storage, account state, or private
manuscript was used.

## Source Snapshot

- `Boundless-Fang/StyleSync-Novel`
  - HEAD: `2afa0a7da34b9bd8f347b1c3f11ee88f1e36f0ed`
  - Default branch: `main`
  - Static markers: style analysis, vocabulary library, worldbuilding
    extraction, character-card extraction, setting completion, chapter outline
    generation, body generation, chapter-local modification.
  - Risk markers: `DEEPSEEK_API_KEY`, `SILICONFLOW_API_KEY`.
  - Posture: `pattern-only / runtime-deferred`

- `eluckydog/DreamQuill`
  - HEAD: `2b8a5964472e1710026b3010960e4e86cb7e2d90`
  - Default branch: `main`
  - License marker: MIT.
  - Static markers: pure-prompt novel agent, continuity guard, setting cards,
    ten-chapter stress test, 5000-6000 character wrap-up mode, prompt-only
    decay ceiling.
  - Posture: `pattern-only / no-runtime`

- `304769384-png/fanqie-novel-skill`
  - HEAD: `7d874e032d2de3dace74ae585cd2dbfbac2cde69`
  - Default branch: `main`
  - Static markers: serial webnovel skill, AI de-flavoring, progress tracking,
    minimum audit set, battle-scene audit, dialogue-ratio monitor, cycle
    detection every five chapters, full audit every ten chapters.
  - Posture: `pattern-only / upstream-skill-body-not-imported`

- `leistung/novel-write`
  - HEAD: `d9681fd01a919015e03d8b630f7f18514547f8c7`
  - Default branch: `main`
  - Static markers: LangChain/LangGraph, Architect / Writer / Consistency /
    Author agents, continuation, rewrite from chapter n, outline-impact
    review, reject/retry up to three times, score below 80 returns to planning.
  - Risk markers: `.env.example`, provider-key surface.
  - Posture: `pattern-only / runtime-deferred`

- `VerifiedOrganic/spindle`
  - HEAD: `f03b2d562ee73b3d2e8bfe56f40eeb4ab923732a`
  - Default branch: `main`
  - License marker: MIT.
  - Static markers: local-first story bible, context packet, recent summaries,
    narrative promises, branch/savepoints, restore, continuity checks,
    dual-persona editorial review, canonical fact extraction, MCP server.
  - Posture: `pattern-only / MCP-runtime-deferred`

- `daveremy/edword`
  - HEAD: `324fe9235bace4c395f6cf72b8f5cdb6b79c7388`
  - Default branch: `main`
  - Static markers: memory-augmented extraction, chapter-by-chapter index,
    deterministic accumulation, knowledge graph, Chain-of-Verification,
    targeted questions, continuity checking, incremental processing.
  - Posture: `pattern-only / CLI-MCP-provider-runtime-deferred`

- `adameya2004-oss/CraftEngine`
  - HEAD: `5ec78905a5e3bf1f65b005551bab83fe49165ec6`
  - Default branch: `master`
  - Static markers: 22-book statistical style analysis, style presets, quality
    analyzer, smart rewriter, imported style learning, character voice
    profiles, rhythm/sensory/repetition/ending metrics, SillyTavern extension.
  - Posture: `pattern-only / browser-extension-runtime-deferred`

## Absorbed Patterns

- `style_vocab_world_card_extraction_gate`
  - Extract style vocabulary, world cards, character cards, and local rewrite
    scopes as separate reviewed artifacts.
  - Same-type creation remaps vocabulary into abstract style levers and creates
    new world cards.

- `prompt_only_decay_ceiling_gate`
  - Prompt-only drafting gets a chapter-count ceiling, stress-test report, and
    wrap-up-mode trigger.
  - Context refresh is mandatory when decay appears.

- `serial_platform_minimum_audit_gate`
  - Serial continuation needs a minimum audit set for hook, dialogue ratio,
    loop detection, battle logic, chapter summary, and AI-tone cleanup.

- `multi_agent_reject_retry_review_gate`
  - Multi-agent drafting records role, score, reject reason, retry count, and
    return-to-planning decisions.

- `story_bible_context_packet_branch_gate`
  - Context packets include story bible, recent summaries, promises, branch id,
    savepoint, and restore target.

- `memory_augmented_delta_verification_gate`
  - Current-chapter facts are staged as deltas and verified with targeted
    questions before deterministic accumulation into the fact index.

- `statistical_style_benchmark_rewrite_gate`
  - Statistical style presets are abstract thresholds for rhythm, sensory
    density, dialogue, repetition, slop, ending quality, and voice drift.

## MuMuAINovel Adaptation

- Discovery defaults now include the seven reviewed repositories and focused
  searches for style vocabulary/world cards, pure-prompt wrap-up mode,
  delta extraction/Chain-of-Verification, and 22-book style presets.
- Pattern packs now expose seven new hint groups for style continuation,
  serial audits, agent retry review, context-packet branching, delta
  verification, and statistical rewrite benchmarks.
- Bible enrichment now includes style vocabulary libraries, minimum chapter
  audit sets, delta fact indexes, story-bible context packets, and statistical
  style benchmark policy.
- Whole-book analysis now includes prompt-only decay reports, multi-agent retry
  traces, delta extraction verification reports, and style benchmark rewrite
  reports.
- Same-type creation now remaps style vocabulary and statistical benchmark
  policies before drafting.

## Deferred / Runtime Gates

- Do not execute upstream installers, package managers, shell scripts, MCP
  servers, browser extensions, SillyTavern extensions, native binaries,
  provider SDKs, Docker stacks, or CLI runtimes during intake.
- Do not read `.env`, API keys, provider tokens, OAuth material, cookies,
  browser storage, local manuscripts, or account state.
- Do not import upstream prompt bodies, prose examples, generated chapters,
  README text, benchmark examples, or extension code into creative canon.
- Runtime trials require a separate local safety contract and explicit user
  approval.

## Verification

- Targeted RED was observed for the missing default repositories and pattern
  gates:
  `python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_style_continuation_sources_map_to_audit_and_verification_gates -q`
- Targeted GREEN after implementation:
  `python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_style_continuation_sources_map_to_audit_and_verification_gates -q`
