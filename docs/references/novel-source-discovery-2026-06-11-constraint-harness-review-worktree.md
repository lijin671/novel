# Novel source discovery: constraint harness review worktree

Date: 2026-06-11

## Source

- Repository: `justinjorgensen/writeassist`
- URL: `https://github.com/justinjorgensen/writeassist`
- Static posture: `pattern-only`
- License observed: MIT
- Reachable HEAD: `fe07dd4be9dc8173107e8d8217984b2e98bb47d3`
- Default branch observed by `git ls-remote`: `main`

## Static evidence

Reviewed without clone, install, runtime launch, provider call, hook execution,
or credential access.

- `README.md`
  - `sha256=12a16095de5005fd62a5e4bc2e30302e5dd307ad08183bf424c9664f8da6dacd`
  - Public markers: constraint-driven writing framework, harness-level
    enforcement, PreToolUse guard, final scanner, least-privilege reviewers,
    isolated git-worktree revision branches, seven named critics, four-tier
    rubric, existing-draft import conflict ledger.
- `LICENSE`
  - `sha256=833a4a48b2e70f0f2f930017bc373fdedfe650159630cfebd7c40cbd77ec534b`
  - MIT text observed.
- `CLAUDE.md`
  - `sha256=a9a25c4260adb9f202cf43f1447b8a955783741773c68fe5feef0424583096ea`
  - Public markers: framework config boundary, Claude Code runtime
    requirements, parallel critic execution, reviewer/creator role split,
    import-book conflict ledger.
- `package.json`: 404
- `AGENTS.md`: 404

GitHub API metadata was rate-limited anonymously during this pass, so durable
freshness proof is `git ls-remote` plus raw-file hash evidence.

## Reusable patterns

- Hard writing rules should become deterministic gates.
  Prompt wording is not enough for constraints like banned tokens, mandatory
  style rules, source-boundary policy, or author-specific no-go lists.
- Reviewers should be least-privilege.
  Critic roles score, cite evidence, and open issues; creator/reviser roles
  own manuscript mutation.
- Revision attempts should be isolated and auditable.
  A risky rewrite needs a branch/worktree id, diff summary, rollback note,
  rubric result, and acceptance decision before becoming canon.
- Existing-draft import should surface conflicts.
  The system should reverse-engineer scaffold, character, timeline, and rule
  evidence, then keep unresolved contradictions in a conflict ledger.

## MuMuAINovel projection

Added pattern gate:

- `constraint_harness_review_worktree_gate`

Mapped targets:

- Bible enrichment:
  - `author_constraint_harness_policy`
  - `least_privilege_reviewer_role_policy`
  - `isolated_revision_worktree_policy`
- Whole-book analysis:
  - `constraint_gate_violation_report`
  - `least_privilege_reviewer_role_report`
  - `isolated_revision_worktree_trace`
  - `parallel_critic_panel_report`
  - `import_conflict_ledger_report`
- Same-type creation:
  - `constraint_rubric_remap`
  - `reviewer_role_boundary_remap`
  - `isolated_revision_branch_remap`

## Deferred/runtime gates

Do not import or run upstream:

- Claude Code hooks
- `.claude/scripts/*.sh`
- slash commands
- workflow runtimes
- git worktree/branch/commit automation
- upstream agent/config files

Only the abstract gate structure is absorbed.
