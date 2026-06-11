# 2026-06-12 InkAI 静态吸收记录

## Source

- URL: <https://github.com/yan2959088709/InkAI->
- Observed HEAD: `1ac9ee1cdfc8f85db43528ef73903d87c31015da`
- Default branch: `main`
- GitHub API license: `NOASSERTION`
- README badge/license claim: MIT badge present, but no root `LICENSE` file observed in API root listing
- Posture: `pattern-only`

## Public evidence used

- GitHub repository metadata and reachable default-branch HEAD.
- Public README / README_CN summary and root tree names only.
- No clone, no install, no Flask start, no model/provider call, no package manager run.

## Reusable patterns

- `big_five_character_psychology_gate`: character cards should carry an explicit
  psychology vector, desire, fear, decision triggers, relationship pressure, and
  change evidence before a chapter is accepted.
- `six_dimension_continuation_audit_retry_gate`: continuation quality should be
  audited on separate axes: character, plot logic, world coherence, style
  fidelity, reader experience, and long-term threads. Failed axes become
  targeted rewrite tasks and must be re-audited.
- `genre_tag_taxonomy_router_gate`: genre tags are routeable reader-promise
  metadata across type, theme, style, and audience; they guide writing without
  copying source events or motifs.

## Deferred/runtime gates

- Do not run `pip install`, `requirements.txt`, Flask server, start scripts, or
  web UI.
- Do not call OpenAI-compatible providers, GLM, API_KEY, BASE_URL, or any model.
- Treat license as unresolved for code adoption because public metadata and
  README badge conflict; absorb only architecture and workflow patterns.

## Project update

- Added InkAI to static GitHub discovery seeds.
- Added query coverage for Big Five / six-dimensional continuation audits.
- Added pattern recognition and prompt-pack hints for character psychology,
  genre-tag routing, and six-dimension continuation retry loops.

## Verification

- `python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_inkai_source_adds_big_five_and_six_dimension_continuation_gates -q`
- `python -m pytest backend/tests/services/test_source_discovery_service.py -q`
- `python -m pytest backend/tests/services/test_chapter_guardrails_rewrite.py backend/tests/api/test_chapter_analysis_remix_sync.py backend/tests/frontend/test_chapters_page_copy.py -q`
- `git diff --check`
