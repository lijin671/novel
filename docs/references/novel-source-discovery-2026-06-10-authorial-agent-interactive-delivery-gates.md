# Novel Source Discovery - 2026-06-10 Authorial Agent / Interactive Delivery Gates

## Scope

Static source-intake pass for authorial agency, multi-agent editorial routing,
interactive branch choice, and manuscript delivery patterns relevant to the
MuMuAINovel book-remix / 拆书续写 / 同类型创作 workflow.

Boundary:

```text
public_metadata_static_review_no_clone_no_install_no_execute
```

No external repository was cloned, installed, executed, launched as an agent,
used as an MCP/server, or allowed to call a provider. Static evidence was limited
to GitHub public pages, `git ls-remote` HEAD checks, and selected public raw root
files such as README / LICENSE / AGENTS.md / pyproject metadata.

## Source snapshots

- `tiny-flowlab/novel-studio-copilot-cli`
  - URL: `https://github.com/tiny-flowlab/novel-studio-copilot-cli`
  - HEAD: `4dce6fce69282a7b13fcf726791a77e015ed009b`
  - License: MIT observed from root `LICENSE`.
  - Static signal: public README/AGENTS.md describe a Copilot CLI novel studio
    with 13 specialized agents, AGENTS.md auto-loading, `@agent` invocation,
    planning, writing, editing, continuity, and quality-control orchestration.
  - Posture: `pattern-only`.

- `guerra2fernando/libriscribe`
  - URL: `https://github.com/guerra2fernando/libriscribe`
  - HEAD: `1d781d373432abe2df1e477eeab083edb86ebe84`
  - License: no root license file observed in this static pass.
  - Static signal: public README describes a multi-agent book writing assistant
    with project manager, outliner, writer/editor roles, worldbuilding, draft
    generation, interactive editing, prompt files, and execution-cost logging.
  - Posture: `pattern-only`; license/trust review deferred before any runtime
    trial.

- `muckelverk/pulpgen`
  - URL: `https://github.com/muckelverk/pulpgen`
  - HEAD: `91c77b4877cb90a0fffba1b4593bb176909c88ff`
  - License: MIT observed from root `LICENSE`.
  - Static signal: public README/pyproject describe an AI novel drafting agent
    with idea-to-outline, chapter writing, interactive editing, XML state files,
    project folders, and `final.html` manuscript output.
  - Posture: `pattern-only`; provider/runtime calls are excluded.

- `bhed/sentiers-open-source`
  - URL: `https://github.com/bhed/sentiers-open-source`
  - HEAD: `9b1b1ba49347f8c4fe35c5a1fa50668d5c709c1f`
  - License: MIT observed from root `LICENSE` with derived-code attribution
    note.
  - Static signal: public README describes an agentic writing system where the
    author chooses narrative branches while agents maintain literary quality,
    with state snapshots for returning to earlier branches.
  - Posture: `pattern-only`; Claude Code commands/agents/prompts are not run or
    imported.

## Reusable patterns

- `agentic_editorial_pipeline_gate`
  - Split planning, drafting, editing, continuity, and quality-control roles.
  - Treat role output as proposals until accepted into project canon.
  - Do not let source-analysis roles write new-story canon directly.

- `craft_role_pipeline`
  - Surface the role chain in the workbench so users can see which artifact each
    role is allowed to touch.
  - Keep prompts/skills as external references; import only the routing idea.

- `branching_choice_graph`
  - For same-type creation, rebuild branch edges around the new premise rather
    than copying the source route.
  - Store rejected branches as alternatives, not as hidden canon.

- `choice_stats_consequence_gate`
  - Every interactive branch should declare changed state, delayed consequence,
    and merge/reject decision.
  - Same-type drafts must rename and redesign variables, thresholds, and payoff
    cadence.

- `delivery_manuscript_assembly`
  - Treat generated chapter files, state files, and final manuscript output as
    separately auditable artifacts.
  - Final assembly should use accepted chapter order and metadata, not source
    table-of-contents order.

- `export_format_fidelity_audit`
  - Export artifacts are derived outputs. They need format, metadata, chapter
    heading, and source-independence checks before being shown as deliverables.

## Local adaptation

Updated durable project surfaces:

- `backend/app/services/source_discovery_service.py`
  - adds the four GitHub repositories to default static review seeds
  - adds compact static pattern summaries and runtime exclusions

- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
  - adds the repositories to editable default source seeds
  - exposes an `Authorial agents / interactive delivery gates` group
  - labels workflow evidence as pattern-only static absorption

- `frontend/src/types/sourceDiscovery.ts`
  - adds explicit type fields for the newly surfaced gate groups

## Deferred/runtime gates

Still not authorized by this intake:

- cloning or installing any source repository
- running Copilot CLI / Claude Code commands / external agents
- importing prompt bodies, AGENTS.md content, or generated sample fiction
- launching MCP/server/browser/desktop runtimes
- calling Gemini, OpenAI, Claude, Copilot, or other providers
- copying external prose, README bodies, prompt files, or generated chapters

Runtime trial requires a separate local safety contract with scope, auth,
secrets, network, cleanup, rollback, and verification boundaries.

## Verification targets

- Source discovery service tests should prove the new seeds are present and map
  to the intended workflow gates from static summaries.
- Frontend copy tests should prove the new seed URLs, gate labels, and
  pattern-only evidence boundary are visible.
- `git diff --check` should stay clean.
