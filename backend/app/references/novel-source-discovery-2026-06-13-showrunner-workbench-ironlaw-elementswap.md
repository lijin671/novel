# Novel source discovery: showrunner, workbench, Iron Law, element swap

Observed at: 2026-06-13

Boundary: `public_github_metadata_lsremote_raw_readme_license_marker_no_clone_no_install_no_runtime`

This pass used public GitHub search/API metadata, `git ls-remote`, raw README/SKILL/LICENSE markers, and root-file markers only. No repository was cloned. No installer, package manager, script, Docker stack, provider, MCP server, browser, or local project runtime was executed.

## Sources reviewed

### liuyichen118-png/fiction-showrunner-skill

- Source: https://github.com/liuyichen118-png/fiction-showrunner-skill
- Observed HEAD: `4153165d843043ebc3bfe9dfe8aa09dd8f381929`
- License: MIT
- Static markers: `README.md`, `README.zh-CN.md`, `SKILL.md`, `PUBLIC_RELEASE_REVIEW.md`, `templates/`, `scripts/scan_chapter_quality.py`
- Absorbed pattern: `public_showrunner_template_release_gate`
- Reusable idea: long-form work should move through story bible, character bible, chapter brief, draft, continuity update, foreshadowing tracker, revision checklist, and quality scan. Public-release review is useful as a no-private-canon gate.
- Deferred runtime: skill installation, helper script execution, copied templates, examples, and prompt bodies.

### huahaiwujiang/novelist-workbench

- Source: https://github.com/huahaiwujiang/novelist-workbench
- Observed HEAD: `d66a2f06910c29d470ac0638cec9417b75f9eff0`
- License: MIT marker in raw `LICENSE`; GitHub API reported `NOASSERTION`
- Static markers: `README.md`, `AGENTS.md`, `.claude/skills/chinese-novelist/SKILL.md`, `references/`, `novels/`, `web-studio/`
- Absorbed pattern: `phase1_style_manual_reference_boundary_gate`
- Reusable idea: imitation writing should split Phase 1 source deconstruction from Phase 2 target creation. Read-only references produce a target-owned style manual; target chapter count is locked before outline and chapters advance serially.
- Deferred runtime: local skill execution, package scripts, web-studio runtime, reference corpus ingestion, generated novels, and prompt bodies.

### BillChen-29/novel-base

- Source: https://github.com/BillChen-29/novel-base
- Observed HEAD: `5eb40e51b3fbdbff1455a84bea7b3295ac3ceba0`
- License: no root license file observed
- Static markers: `README.md`, `SKILL.md`, `WORKFLOW.md`, `skill-definition.json`, `scripts/`, `templates/`, `references/`
- Absorbed pattern: `six_layer_iron_law_chapter_gate`
- Reusable idea: each chapter can be gated through truth files, state tracking, knowledge graph, outline anchors, retrieval context, and cross-agent review. Failed gates block the next chapter; anti-resolution rules keep non-final chapters from solving the main conflict early.
- Deferred runtime: Hermes skill runtime, scripts, slash commands, databases, provider endpoints, generated story content, and local assets.

### dama-cyber/novel-ai-system

- Source: https://github.com/dama-cyber/novel-ai-system
- Observed HEAD: `af7354324fcbd30d252b67294a78f0b8ce45d7ee`
- License: MIT
- Static markers: `README.md`, `SKILLS.md`, `PROMPTS.md`, `MODULE_INDEX.md`, `Dockerfile`, `package.json`, `novelai.ps1`, `scripts/21-combined-revision.sh`, `scripts/24-content-rewriter.sh`
- Absorbed pattern: `element_swap_deconstruction_rewrite_pipeline_gate`
- Reusable idea: 拆书续写 can be modeled as split-book analysis, element-swap design, content rewrite, cumulative chapter analysis, style engineering, and enhancement review.
- Deferred runtime: Docker, Qwen CLI/OAuth, npm scripts, shell/PowerShell/batch scripts, server runtime, provider calls, prompt bodies, and generated examples.

## MuMuAINovel adaptation

- Add four pattern-only gates to source discovery and pattern-pack generation.
- Surface their hints in the Book Remix source discovery panel.
- Keep all upstream value as abstract workflow vocabulary and verifier targets.
- Do not copy upstream code, prompts, examples, reference texts, generated prose, templates, or local project state.

