# Novel Source Discovery 2026-06-13 - Disassembly / Style / Truth / Collaboration / SDD

## Scope

Static source intake for MuMuAINovel book-remix, continuation, and same-type creation flows.

No upstream repository was cloned. No package manager, installer, script, Docker stack, MCP server,
browser extension, provider call, database, or model runtime was executed.

## Sources absorbed

### novel-writer-pro/novel_disassembly_agent_mini

- URL: https://github.com/novel-writer-pro/novel_disassembly_agent_mini
- Reachable HEAD: `83d3f8c5da09cd1461f38ddfe77028233e3d4b0e`
- Default ref observed by `git ls-remote --symref`: `v0.1.1`
- License: no root license file observed in this static pass
- Static markers reviewed: README, docs entry table, app/API/Web role split
- Absorbed pattern: `chapter_progressive_disassembly_checkpoint_gate`
- Reusable idea: source-book disassembly should advance through normalized chapters, job/checkpoint state,
  raw-output custody, JSON-first analysis, Markdown reports, and QA citation jumps before reuse.
- Runtime posture: pattern-only / runtime-deferred.

### lsg1103275794/novel-writer-style-cn

- URL: https://github.com/lsg1103275794/novel-writer-style-cn
- Reachable HEAD: `5190ac2e29ccd76d7392d03471ec668d0d502b8c`
- Default branch: `main`
- License: MIT
- Static markers reviewed: README, LICENSE
- Absorbed pattern: `quantified_style_learning_confidence_gate`
- Reusable idea: style learning needs measurable axes, confidence scoring, style validation, and source-rights
  boundary before any same-type style profile can guide drafting.
- Runtime posture: pattern-only / runtime-deferred.

### lgz-star/novel-pro

- URL: https://github.com/lgz-star/novel-pro
- Reachable HEAD: `5f56f95087f81dd74a74e4b7e83d5b108650bfbe`
- Default branch: `main`
- License: AGPL-3.0
- Static markers reviewed: README, LICENSE
- Absorbed pattern: `truth_system_chapter_settlement_gate`
- Reusable idea: long-novel takeover and continuation should settle chapters into a truth ledger and snapshot
  view; pending-sync chapters block the next draft.
- Runtime posture: pattern-only / no AGPL code import.

### blueraina/astrbot_plugin_novel

- URL: https://github.com/blueraina/astrbot_plugin_novel
- Reachable HEAD: `c2d8e4e01db8e9d62e95f7c23381a389953c8ca7`
- Default branch: `main`
- License: MIT
- Static markers reviewed: README, LICENSE
- Absorbed pattern: `group_collaboration_conflict_vote_memory_gate`
- Reusable idea: collaborative story input should pass through idea scoring, conflict detection, vote decision,
  contributor policy, group isolation, bounded memory recall, and plot checking.
- Runtime posture: pattern-only / runtime-deferred; no chat logs, user identities, or plugin data imported.

### t59688/arboris-novel

- URL: https://github.com/t59688/arboris-novel
- Reachable HEAD: `dd80c69bc30a80d68b375bd504c6bc308164ff9e`
- Default branch: `main`
- License: README badge says MIT; no root license file observed in this static pass
- Static markers reviewed: README
- Absorbed pattern: `arboris_story_direction_workspace_gate`
- Reusable idea: author-facing workspaces should keep character, outline, setting, next-direction options,
  selected option rationale, and rejected alternatives visible before generation.
- Runtime posture: pattern-only / runtime-deferred.

### wordflowlab/novel-writer

- URL: https://github.com/wordflowlab/novel-writer
- Reachable HEAD: `e4190d407e736affa42ba55a70d91961c6ce3932`
- Default branch: `main`
- License: MIT
- Static markers reviewed: README, LICENSE
- Absorbed pattern: `sdd_seven_step_cross_platform_skill_gate`
- Reusable idea: route novel creation through a phase ladder with artifact and exit gates:
  constitution, specification, clarification, plan, tasks, write, and analyze.
- Runtime posture: pattern-only / runtime-deferred.

## Deferred / rejected

- `Anshler/graphify-novel`: public search result existed, but `git ls-remote` returned repository not found.
- `visibl-ai/visibl-audiobooks`: reachable and related to fiction-to-visual adaptation, but this pass targets
  writing-state, disassembly, style, continuation, and same-type creation. Visual/audiobook pipeline remains deferred.

## MuMuAINovel integration

New static pattern gates were added to:

- `source_discovery_service.py`
- `source_pattern_pack_prompt.py`
- `sourceDiscovery.ts`
- `BookRemixSourceDiscoveryPanel.tsx`
- `test_source_discovery_service.py`

## Safety boundary

The absorbed value is limited to workflow vocabulary and acceptance gates.

Blocked by default:

- upstream code, prompt bodies, generated prose, templates, examples, and sample corpora
- provider/model calls
- npm/pip/package scripts
- PostgreSQL/Alembic/LangGraph/SkillKit/AstrBot runtimes
- QQ/group chat data, user identities, screenshots, local projects, databases, exports
- author-style corpora unless user-owned or explicitly rights-cleared
