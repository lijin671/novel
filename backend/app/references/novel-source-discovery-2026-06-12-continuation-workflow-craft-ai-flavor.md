# Novel source discovery intake - continuation workflow, craft review, tutorial curation, AI-flavor cleanup

Date: 2026-06-12

Scope: public GitHub Search + GitHub REST metadata + `git ls-remote` HEAD + raw README/root marker static review.

No clone, install, package manager, script, provider call, browser automation, MCP server, binary, Docker stack, or local manuscript/runtime data was executed.

## Sources reviewed

- `ARMANDSnow/make-ur-Agent-writer`
  - URL: https://github.com/ARMANDSnow/make-ur-Agent-writer
  - HEAD: `e3c18f83f17f204f382781c746e57cf0a05a41be`
  - License signal: `NOASSERTION`
  - Posture: pattern-only, runtime-deferred
  - Absorbed gate: `mock_first_multi_agent_continuation_gate`
  - Static value: mock-first long-form continuation readiness, per-book workspace isolation, staged normalize/split/extract/compress/debate/plan/draft/review/lint pipeline, reviewer fail-closed behavior, token/cost trace.
  - Deferred: source novels, outputs/logs, scripts, requirements, local web UI, provider/API-key flows, workspaces.

- `qiyan233/inkos-like-novel-os`
  - URL: https://github.com/qiyan233/inkos-like-novel-os
  - HEAD: `9c83269a197802a1b51561fa8efb77cb736c1647`
  - License signal: MIT
  - Posture: pattern-only, runtime-deferred
  - Absorbed gate: `truth_file_write_next_state_update_gate`
  - Static value: truth-file source of authority, write-next work package, revise loop, extract-state/state-update split, snapshots, continuity audit, long-running workflow-skill contract.
  - Deferred: OpenClaw/skill install, scripts, example story files, generated outputs.

- `a9549521/chronicler`
  - URL: https://github.com/a9549521/chronicler
  - HEAD: `b82afa4879dd0ea26f9b46bad094a8562172f80c`
  - License signal: missing
  - Posture: pattern-only, runtime-deferred
  - Absorbed gate: `author_control_context_assembly_gate`
  - Static value: author-controlled context assembly, multi-level summaries, Facts Table, selected Lore injection, outline-range focus, human decision authority before drafting.
  - Deferred: packaged Windows binary, backend/frontend runtime, API settings, prompts/models, local manuscripts, database state.

- `wgwtest/novel-writing`
  - URL: https://github.com/wgwtest/novel-writing
  - HEAD: `5e8a9ce414b2ce4b529ecbca67da4cd474679a30`
  - License signal: MIT
  - Posture: pattern-only, runtime-deferred
  - Absorbed gate: `craft_scene_concrete_finding_revision_gate`
  - Static value: concrete craft findings, narrative-function review, style-bearing material protection, realism/access-limit checks, scene continuation without summary collapse.
  - Deferred: Codex skill install, copied skill bodies, assets, release/install workflow.

- `HZ-KMNO/web-novel-tutorial-curation-skill`
  - URL: https://github.com/HZ-KMNO/web-novel-tutorial-curation-skill
  - HEAD: `d3386a73038ff6b64b430bc6fe3048ab96b678c7`
  - License signal: MIT
  - Posture: pattern-only, runtime-deferred
  - Absorbed gate: `tutorial_case_library_curation_gate`
  - Static value: source-template detection, list-before-detail extraction, stable-id dedupe, principle summaries instead of copied tutorial bodies, excellent-case analysis dimensions, validation counts.
  - Deferred: scraping/browser/API extraction, copyrighted tutorial bodies, case prose, local documents.

- `981029l/webnovel-writer`
  - URL: https://github.com/981029l/webnovel-writer
  - HEAD: `c6f073baa807b07926970cfaaf904a08a1cbd19d`
  - License signal: missing from API/root static pass; README badge claims GPL but not treated as sufficient without root license evidence.
  - Posture: pattern-only, runtime-deferred
  - Absorbed gate: `anti_hallucination_strand_weave_review_gate`
  - Static value: anti-hallucination rules, outline-as-law, setting-as-physics, new-entity identification, Strand Weave rhythm, dual-agent architecture, five-dimensional review, RAG/recovery posture.
  - Deferred: credential-like README/env surfaces, Claude Code runtime, backend/frontend services, scripts, provider calls, local project data.

- `B1lli/remove-ai-flavor-writing-skill`
  - URL: https://github.com/B1lli/remove-ai-flavor-writing-skill
  - HEAD: `5edd9fa055292cdb854b210e806ad4fb64910bbe`
  - License signal: MIT
  - Posture: pattern-only, runtime-deferred
  - Absorbed gate: `ai_flavor_template_shell_cleanup_gate`
  - Static value: narrow AI-flavor cleanup after continuity approval, template-shell removal, signpost/paragraph-isomorphism/fake-engagement detection, preserving meaning/facts/tone/style.
  - Deferred: Codex skill install, scripts/tests, agents, prompt bodies.

## Deferred / not promoted

- `Anshler/graphify-novel`: GitHub API returned 404 in this static pass; no source value promoted.
- `sinfiny/AutoWriter`: static README says the current code only loads a Markdown workflow file and task dispatch/event append are intentionally empty; kept as deferred workflow-loop vocabulary, not a product gate.

## Integration decisions

- Add new repository seeds and GitHub queries for continuation readiness, truth-file workflow, author-controlled context assembly, concrete craft review, tutorial/case curation, anti-hallucination strand review, and AI-flavor cleanup.
- Add pattern pack targets for:
  - bible enrichment: readiness policy, truth-file state update, facts-table lore injection, concrete craft findings, case-library policy, anti-hallucination law, AI-flavor cleanup.
  - whole-book analysis: readiness preflight report, state-update report, author context selection report, craft finding report, tutorial/case manifest, strand-weave balance report, template-shell cleanup audit.
  - inspired creation: remap pipeline roles, truth files, author-selected context, craft findings, tutorial principles, strand-weave checks, AI-flavor edits.
- Add copy-risk guards:
  - no copyrighted source chunks in continuation packages
  - no source examples or snapshot names promoted into target canon
  - no hidden source lore/facts in selected context
  - no article bodies or benchmark-novel prose in tutorial/case prompts
  - no smoothing of copied spans under “AI-flavor cleanup”

## Verification target

- `backend/tests/services/test_source_discovery_service.py::test_continuation_workflow_curation_and_ai_flavor_sources_are_static_absorbed`
- `backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_inspired_pattern_pack_fields`

## 2026-06-13 projection update

The `truth_file_write_next_state_update_gate` from `qiyan233/inkos-like-novel-os`
is now projected into the real remix prompt-context path, not only the discovery
panel:

- continuation context renders a `Truth-file write-next state gate`
  requiring selected authority files, latest accepted chapter, open
  hook/payoff debt, planned beat, blocking assumptions, and `snapshot_id`
  before drafting.
- inspired/same-type context renders the same state boundary so target projects
  rebuild their own truth/state package instead of carrying source truth-file
  names or example state.
- revise and state-update remain separate: candidate drafts do not mutate
  long-term bible/timeline/character/hook/plan state until a chapter is accepted.

Verification addendum:

- `backend/tests/services/test_book_remix_context_service.py::test_build_remix_context_blocks_render_truth_file_write_next_state_gate`
