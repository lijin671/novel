# Novel Source Discovery - Human-Machine Batch Orchestration

Observed at: 2026-06-10T23:45:00+08:00

Boundary:

```text
public_github_lsremote_raw_readme_license_marker_scan_no_login_no_clone_no_runtime
```

This pass statically reviewed public GitHub metadata and raw README/LICENSE
markers for Chinese webnovel tooling around inline co-writing, hierarchical
book orchestration, batch continuation, prompt variation, and local author-data
boundaries.

No repository was cloned, installed, built, executed, or launched. No package
manager, Docker stack, desktop app, updater, local model connector, provider
call, browser automation, MCP server, binary, zip, shell script, or PowerShell
script was run.

## Source Snapshot

- `leehong0704/ai-novel`
  - HEAD: `28f94afa0f56129b12f707a7b4fe59a8a4bc4999`
  - License marker: EPL-1.0
  - Static markers: Chinese desktop AI novel tool, human-machine co-creation,
    outline/body generation, AI polishing, precise modification, local memory,
    Windows packaged zip.
  - Posture: `pattern-only`

- `wynnforthework/ai-novel-weaver`
  - HEAD: `0085184dd581a427b9193f3ed04ea3848409c1b9`
  - License marker: no root license observed in this pass.
  - Static markers: web-based AI novel platform, orchestrator-driven
    generate/validate/improve loop, hierarchical planning from volume/arc to
    chapter, memory weave, one-click book decomposition, local deployment.
  - Posture: `pattern-only / license-review-needed`

- `fuchen2020/BatchScribe`
  - HEAD: `600fde9d4ad648c4f5dfbf44f8535f7ebff5cdb3`
  - License marker: AGPL-3.0
  - Static markers: Windows-only AI novel generator, batch generation,
    continuation, story type/style controls, prompt configuration, chapter
    memory/context.
  - Posture: `pattern-only`

- `xy9144/flutter-novel-main`
  - HEAD: `a76a430f7973e764c762ac44d74b19f9c3b2aa7e`
  - License marker: MIT
  - Static markers: Flutter AI novel wrapper, outline -> volume plan -> range
    plan -> chapter plan -> chapter text, progress-based auto continuation,
    progress tracking, homogeneity-driven prompt revision, random title/topic,
    local Ollama notes.
  - Posture: `pattern-only`

- `duoyang666/ai_novel`
  - HEAD: `48fb0c3770b539a8f544acda77f7adcb3e6a124e`
  - License marker: Apache-2.0
  - Static markers: Chinese AI writing / knowledge-base app, local software
    downloads, auto-upgrade zip, Feishu tutorials, outline/chapter generation,
    continuation, batch writing, pleasure-point and rhythm hints.
  - Posture: `pattern-only / runtime-deferred`

## Absorbed Patterns

- `inline_human_machine_coauthoring_gate`
  - Generated prose is a starting point.
  - Author edits, localized polishing, precise modification, and affected spans
    must stay visible as reviewable diffs.
  - Localized repair should not regenerate the entire chapter unless the
    chapter-level plan is wrong.

- `hierarchical_orchestrator_generation_gate`
  - Long-form writing needs explicit scope: book -> volume -> arc -> chapter ->
    scene.
  - Each generate/validate/improve loop records the stage, input artifacts,
    failed checks, accepted output, and next scope.
  - New volumes or arcs remain approval-gated because they mutate structure.

- `batch_continuation_progress_queue_gate`
  - Batch continuation is a queue, not an unbounded loop.
  - Each job records the prior accepted chapter, progress cursor, retry budget,
    validation state, and next incomplete chapter pointer.
  - Failed or logic-confused chapters remain pending instead of advancing the
    queue.

- `homogeneity_prompt_variation_gate`
  - Adjacent chapter windows should be checked for repeated openings, conflict
    shape, payoff cadence, rhythm, and reaction loops.
  - Fixes must vary structural axes such as pressure source, POV distance,
    scene function, information release, and hook style.

- `local_author_data_boundary_gate`
  - Local author data, source notes, generated drafts, model endpoint settings,
    packaged apps, update channels, and backups are separate review surfaces.
  - Static intake may record download/update risk.
  - Runtime trials require a separate local safety contract.

## MuMuAINovel Adaptation

- Discovery seeds now include these five repositories as static pattern sources.
- Pattern keywords now recognize inline co-authoring, hierarchical
  orchestration, batch continuation queues, homogeneity prompt variation, and
  local author-data/update surfaces.
- Pattern packs now expose prompt-safe hints and analysis targets for:
  - localized revision spans
  - volume/arc/chapter orchestration traces
  - batch continuation jobs
  - homogeneity findings
  - local author-data manifests

## Deferred / Runtime Gates

- Do not execute packaged Windows zips, upgrade zips, desktop apps, Flutter
  apps, Python requirements, local servers, or provider/model connectors.
- Do not import forum-thread content, Feishu tutorial bodies, release packages,
  or generated prompt libraries into canon.
- Do not treat auto-continuation as approval to mutate accepted story state.
- Do not let source README workflows override local copy-risk, canon, and
  author-approval gates.
