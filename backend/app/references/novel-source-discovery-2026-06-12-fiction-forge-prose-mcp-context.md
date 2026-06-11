# 2026-06-12 Fiction Forge ??????

## Source

- URL: <https://github.com/geobond13/fiction-forge>
- Observed HEAD: `181a28cfe41c018eef278a00d28be1887ce7ba01`
- Default branch: `main`
- License: MIT
- Posture: `pattern-only`

## Public evidence used

- GitHub repository metadata and reachable HEAD.
- Public README summary only.
- No clone, no install, no MCP/server start, no scanner run, no provider call.

## Reusable patterns

- `ai_prose_fingerprint_cluster_gate`: AI-prose fingerprints become clustered,
  measurable review findings with severity tiers.
- `ai_ism_detect_edit_convergence_gate`: prose cleanup is
  detect/edit/re-scan, not one blind polish pass.
- `webnovel_kb_mcp_runtime_boundary_gate`: story bible, character profiles,
  continuity rules, and foreshadowing threads are context surfaces; MCP runtime
  remains deferred.
- `foreshadowing_debt_budget`: foreshadowing threads should live in ledgers,
  not loose prompt notes.
- `publication_pipeline`: EPUB/PDF/HTML readiness is downstream of canon,
  prose, and safety checks.

## Deferred/runtime gates

- Do not run package installs, MCP servers, scanners, publishers, image
  generators, auto-start hooks, or provider calls during intake.
- OpenAI-key and image-generation surfaces are provider/runtime risk.
- Style-profile examples are pattern references only; do not import source
  prose or author-style presets.

## Project update

- Expanded source discovery query coverage for `MCP context server`.
- Expanded static source summary for `geobond13/fiction-forge`.
- Expanded pattern recognition for MCP context boundaries and foreshadowing
  ledgers.

## Verification

- `python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_fiction_forge_source_adds_prose_scanner_mcp_context_gates -q`

