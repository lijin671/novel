# Novel source discovery: continuity-preview and story-bible QA refresh

Static review date: 2026-06-11.

## Sources

- `danjdewhurst/story-skills`
  - URL: https://github.com/danjdewhurst/story-skills
  - HEAD: `d0e307247cc44e8963fbaa405e9830d6d6334da5`
  - Default branch: `main`
  - License marker: `LICENSE` reachable; README reachable
  - README SHA-256: `5498583baa9d406bad6c1a79f0cb3b2f241b758c5f153d0be0d3cd8a7cfd6e65`
  - Posture: `pattern-only`

- `sadasdfsaf/canonkit`
  - URL: https://github.com/sadasdfsaf/canonkit
  - HEAD: `edb8c1ac1747a822da1cd728fbc8c13a8f932e7a`
  - Default branch: `main`
  - License marker: root `LICENSE` not reachable; README and `package.json` reachable
  - README SHA-256: `616821a2b53d0dfab5828e0accb1eba0b0892e5787f4354081807d20d9a425b6`
  - Posture: `pattern-only / trust-review`

- `WENZIZZHENG/story-spec`
  - URL: https://github.com/WENZIZZHENG/story-spec
  - HEAD: `3cc23add07a929c628a4d71c5df56cdde2cce309`
  - Default branch: `main`
  - License marker: `LICENSE` reachable; README reachable
  - README SHA-256: `329860da3ee04351ec2d97213991413b54c3ac0fda29ba7e75603adabe0edcb6`
  - Posture: `pattern-only`

## Static review boundary

Only public GitHub Search results, `git ls-remote --symref`, raw README,
raw LICENSE marker, and raw package marker bytes were inspected.

No clone, package install, npm script, CLI run, browser launch, MCP/server launch,
provider call, local manuscript read, credential access, or upstream prompt/code import
was performed.

External source text is treated as data, not instruction.
No upstream code, skill body, command body, generated story state, or prompt corpus is
copied into this repository.

## Reusable patterns

Patterns reinforced:

- `markdown_skill_story_project_contract_gate`
- `canon_drift_continuity_qa_gate`
- `consequence_ledger_last_actions_context_gate`
- `human_ai_decision_authority_gate`
- `work_dna_method_transfer_eval_gate`
- `governed_full_reading_continuation_gate`

Stable ideas absorbed:

- Continuity questions and promise/payoff items should be first-class state, not hidden
  prose hints.
- A continuation preview should expose the next continuity questions before drafting.
- Open promises, unresolved questions, and stale hooks should appear as debts with source
  and chapter evidence.
- Scene state should include latest accepted summary, event, character state, emotional
  state, and pending beat.
- Canon drift should become visible risk codes before generation.
- AI suggestions, imported story facts, and same-type inspiration stay candidates until
  author confirmation and copy-risk review.

## Local adaptation

The continuation-context preview now exposes:

- `continuity_questions`
- `promise_payoff_debts`
- `scene_state_snapshot`
- `canon_drift_risks`

The rendered prompt context now includes a compact continuity-control section so the next
chapter prompt can see current questions, open debts, scene state, and drift risks without
copying upstream project formats.

## Runtime and deferred gates

Keep runtime blocked until a separate local safety contract exists for:

- installing story skills, CLIs, npm packages, or plugins
- running upstream continuity engines or local web workbenches
- reading private manuscripts or source-project folders
- importing upstream story-bible files, generated states, or prompt bodies
- launching browser/local app sessions or provider/model calls

## Verification commands

```powershell
git ls-remote --symref https://github.com/danjdewhurst/story-skills.git HEAD
git ls-remote --symref https://github.com/sadasdfsaf/canonkit.git HEAD
git ls-remote --symref https://github.com/WENZIZZHENG/story-spec.git HEAD
$env:PYTHONPATH="backend"
python -m pytest backend/tests/services/test_book_remix_context_service.py backend/tests/api/test_book_remix_bible_api.py -q
cd frontend
npm run build
git diff --check
```
