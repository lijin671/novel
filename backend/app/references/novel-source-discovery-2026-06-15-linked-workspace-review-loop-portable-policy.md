# Novel Source Discovery 2026-06-15: Linked Workspace, Review Loop, and Portable Tool Policy Projection

## Scope

Static intake for continuation / same-type writing workflow optimization in MuMuAINovel.

Sources reviewed without install or runtime execution:

- `guchendesigndog/GC-Writer-Assistant`
  - reachable HEAD: `b38f83c55dddbbd124a04bf7481d8fc97431c83c`
  - license observed: MIT
  - posture: pattern-only / static workflow projection
- `jinmawang/claude-novel-writeFlow`
  - reachable HEAD: `a559eee6b7c70063e63b93ebadb5a72c0eff3705`
  - license observed: no LICENSE marker in static pass
  - posture: pattern-only / static workflow projection
- `D:/project/universal-novel-writing`
  - local reference folder, no `.git` directory observed
  - files observed: `SKILL.md`, `references/chapter-workflow.md`, `references/genre-patterns.md`, `references/planning-templates.md`, `references/revision-checklists.md`, `references/story-bible.md`
  - license observed: not present in local reference folder
  - posture: local static review / pattern-only

## Reusable patterns

### Linked chapter workspace state

Absorbed from GC-Writer-Assistant style workflow shape:

- imported chapter list
- extracted chapter outlines
- reference display pane
- writing pane
- local output folder
- current writing cursor / state memory

Projection in MuMuAINovel:

- `linked_chapter_workspace_state_gate`
- `linked_chapter_workspace_state_gate_hints`
- `imported_chapter_manifest`
- `chapter_outline_extraction_status`
- `linked_reference_write_state`
- `current_writing_state_memory`

Same-type boundary: reuse only the workspace shape. Do not carry source chapter headings, extracted outlines, local file paths, or prose into target canon.

### Writer / style / continuity context rebuild loop

Absorbed from claude-novel-writeFlow workflow shape:

- explicit context init / rebuild before midstream adoption
- Writer, Style Reviewer, and Continuity Reviewer findings
- previous/next 2 chapter outline window
- chapter-by-chapter pause / confirmation gate

Projection in MuMuAINovel:

- `tri_reviewer_context_rebuild_gate`
- `tri_reviewer_context_rebuild_gate_hints`
- `context_rebuild_manifest`
- `writer_style_continuity_review_findings`
- `review_iteration_resolution_log`
- `chapter_pause_confirmation_status`

Same-type boundary: reviewer roles and context windows are reusable process structure only. Upstream prompt bodies, examples, provider traces, and chapter content remain excluded.

### Universal portable tool policy

Absorbed from the local `universal-novel-writing` reference:

- no specific client/runtime is mandatory
- file tools persist artifacts when present
- missing search marks facts as assumptions
- task/subagent tools support independent review passes when available
- command tools are limited to mechanical checks
- existing manuscript files are not overwritten or deleted without explicit scope
- patches, versioned files, revision notes, absolute paths, and localized filename conventions are preferred

Projection in MuMuAINovel:

- `universal_portable_tool_policy_gate`
- `universal_portable_tool_policy_gate_hints`
- `universal_portable_tool_policy`
- `universal_portable_tool_policy_report`
- `universal_portable_tool_policy_remap`
- `portable_tool_surface_policy`
- `assumption_register_for_unavailable_search`
- `nonoverwrite_versioned_revision_lane`

Same-type boundary: artifact paths, filename conventions, assumptions, and revision lanes must be rebuilt for the target project. Do not import upstream paths, local folder names, or client-specific habits as canon.

## Runtime exclusions

No clone, package install, script execution, Docker/MCP/browser launch, provider call, credential read, cookie read, account mutation, or host/model configuration change was authorized by this intake.

## Verification commands

```powershell
python -m pytest `
  backend/tests/services/test_source_discovery_service.py::test_gc_writer_and_writeflow_workspace_gates_project_to_pattern_pack `
  backend/tests/services/test_source_discovery_service.py::test_local_universal_novel_writing_skill_is_static_absorbed `
  backend/tests/services/test_book_remix_context_service.py::test_gc_writer_writeflow_workspace_and_review_gates_render_context_and_audit `
  backend/tests/services/test_book_remix_context_service.py::test_build_remix_continuation_context_block_renders_universal_novel_workflow_contract `
  backend/tests/services/test_book_remix_context_service.py::test_universal_project_memory_gate_extends_control_audit_and_warnings `
  backend/tests/frontend/test_source_discovery_panel_copy.py::test_source_discovery_panel_surfaces_universal_novel_writing_gates `
  -q
```
