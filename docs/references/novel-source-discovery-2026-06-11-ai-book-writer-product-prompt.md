# Novel Source Discovery - 2026-06-11 AI Book Writer / Product Boundary / Prompt Scaffold Static Review

## Boundary

`public_github_ai_book_writer_prompt_webapp_static_head_raw_readme_license_no_login_no_clone_no_runtime_20260611`

This pass used public GitHub repository metadata, `git ls-remote --symref`,
raw README/LICENSE reads, and compact marker counts only.

It did not clone repositories, install packages, execute scripts, run web apps,
launch AutoGen, call GPT/OpenAI/302.AI/provider services, read credentials, or
import upstream prompts/code.

Static cache:

- `tmp/source-intake-20260611-ai-book-writer-prompt-webapp-static-review.json`

## Reviewed sources

### `adamwlarson/ai-book-writer`

- URL: <https://github.com/adamwlarson/ai-book-writer>
- HEAD: `9066128481b20bfbbcfca82cc791b09fdf18a6a5`
- Default branch: `main`
- License marker: no raw LICENSE observed
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - role-separated collaborative writing agents
  - Story Planner / World Builder / Memory Keeper / Writer / Editor /
    Outline Creator
  - outline and continuity review before chapter drafting
- Absorbed as: `multi_agent_outline_continuity_review_gate`
- Runtime excluded:
  - no AutoGen launch
  - no Python dependency install
  - no provider/API call
  - no upstream prompt body import

### `302ai/302_novel_writing`

- URL: <https://github.com/302ai/302_novel_writing>
- HEAD: `1c113a7735f54d57849a911090f45aa4b37c8ae9`
- Default branch: `main`
- License marker: Apache-2.0
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - manual writing and AI-assisted writing as separate action surfaces
  - AI writing sidebar
  - diverse writing styles
  - intelligent plot planning
  - real-time edit / modification flow
  - online service and self-deploy split
- Absorbed as: `hosted_ai_sidebar_product_boundary_gate`
- Runtime excluded:
  - no online service login
  - no deployment
  - no package install
  - no provider/model call
  - no local upload or cover generation runtime

### `christiandarkin/creative-writers-toolkit`

- URL: <https://github.com/christiandarkin/creative-writers-toolkit>
- HEAD: `04b21b685cd5225829484ed9b77dcf7720be46cb`
- Default branch: `main`
- License marker: no raw LICENSE observed
- Family: `novel-automation`
- Posture: `pattern-only`
- Reusable pattern:
  - character outlines
  - story synopses
  - treatments
  - plot outlines
  - scene lists
  - staged creative scaffold promotion
- Absorbed as: `creative_scaffold_prompt_sequence_gate`
- Runtime excluded:
  - no GPT-3/OpenAI key
  - no Python runtime
  - no upstream prompt/text files
  - no generated sample body import

### Deferred candidate: `mysticmars/book-writer-ai`

- URL: <https://github.com/mysticmars/book-writer-ai>
- `git ls-remote` result: repository not found
- Decision: `defer`
- Reason: no reachable HEAD or README.

## Project fusion

The promoted patterns were fused into:

- default GitHub seed URLs
- default GitHub query vocabulary
- static repository pattern summaries
- `PATTERN_KEYWORDS`
- source pattern pack hints
- bible enrichment targets
- whole-book analysis targets
- same-type/inspired remap targets
- source pattern pack prompt digest
- service regression test

## New gates

- `multi_agent_outline_continuity_review_gate`
  - separates planner, world-builder, memory-keeper, writer, editor, and
    outline roles before accepting continuation output.
- `hosted_ai_sidebar_product_boundary_gate`
  - treats AI sidebar actions, online service, self-deploy, provider, and upload
    surfaces as separate held states.
- `creative_scaffold_prompt_sequence_gate`
  - keeps character outline, synopsis, treatment, plot outline, and scene list
    as staged candidates before canon promotion.

## Verification

RED:

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_ai_book_writer_product_prompt_sources_map_to_continuation_gates -q
```

Expected failure was the missing default repository seed.

GREEN:

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_ai_book_writer_product_prompt_sources_map_to_continuation_gates -q
```

Result: `1 passed`.
