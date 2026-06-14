# Novel Source Discovery 2026-06-15: Deterministic Volume Spec-Quality Orchestration

## Scope

Static intake for MuMuAINovel 拆书续写 / 同类型仿写 workflow optimization.

Sources reviewed without install or runtime execution:

- `DankerMu/novel-writer-plugin`
  - reachable HEAD: `e6f4cabd8eedf1a3418c2ef74789341969168341`
  - license observed: MIT
  - note: README tail still contains an old “license not selected” marker; treat as stale/conflicting documentation, not runtime permission
  - posture: pattern-only / static workflow projection
- `DankerMu/novel-writer-cli`
  - reachable HEAD: `d1e893d99416640baeea9aa396dbdf343b59664d`
  - license observed: MIT
  - related mirror marker: `DankerMu/cc-novel-writer.git` at the same observed HEAD
  - posture: pattern-only / static workflow projection

## Absorbed patterns

### Volume rolling spec-quality gate

Reusable structure:

- WorldBuilder / PlotArchitect / ChapterWriter / Summarizer / QualityJudge role separation
- volume plan -> daily chapter pipeline -> 5-chapter sliding check -> 10-chapter deep inventory -> volume-end audit
- L1 world rules, L2 character contracts, L3 chapter contracts, and LS storylines as separate acceptance layers
- `storylines.json` / `chapter-contracts` as inspiration for target-owned ledgers
- eight-dimension weighted scoring and five-tier quality decisions

Projection in MuMuAINovel:

- `volume_rolling_spec_quality_gate`
- `volume_rolling_spec_quality_gate_hints`
- `volume_spec_contract_quality_policy`
- `volume_rolling_spec_quality_report`
- `volume_rolling_spec_quality_remap`

Same-type boundary: reuse only the orchestration shape. Do not copy upstream agent prompt bodies, generated prose, contract examples, storyline examples, plugin hooks, shell scripts, or quality-judge wording.

### Executor-agnostic instruction checkpoint gate

Reusable structure:

- deterministic orchestration layer does not call LLM APIs directly
- orchestrator emits an instruction packet
- executor writes staging artifacts
- checkpoint state selects the next recovery cursor
- validate / advance / commit keeps state movement transactional
- audit logs and reports make replay possible

Projection in MuMuAINovel:

- `executor_agnostic_instruction_checkpoint_gate`
- `executor_agnostic_instruction_checkpoint_gate_hints`
- `instruction_packet_checkpoint_policy`
- `instruction_checkpoint_staging_audit_report`
- `instruction_checkpoint_staging_remap`

Same-type boundary: instruction packets, checkpoint schemas, staging paths, command labels, lock files, audit logs, and runtime reports are workflow evidence only. They must not become target canon, chapter prose, or hidden prompt bodies.

## Runtime exclusions

No clone, package install, `npm` / `npx` / package-script execution, shell-script execution, Claude plugin install, SessionStart hook use, provider call, Docker/MCP/browser launch, credential read, cookie read, account mutation, or host/model configuration change was authorized by this intake.

## Verification target

```powershell
python -m pytest `
  backend/tests/services/test_source_discovery_service.py::test_dankermu_deterministic_volume_spec_orchestration_sources_are_static_absorbed `
  backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_deterministic_volume_spec_gates `
  -q
```
