# Novel Source Discovery 2026-06-14 — live diagnostics × visible outline import projection

## Sources

### NovelWriter

- Repository: https://github.com/akarshkashyap4-ui/NovelWriter
- Static HEAD: `e5e1fb27c1c24b5c7bbbbbeb80650fb39ccd69c3`
- Default branch: `main`
- License: MIT
- Local static packet: `tmp/source-intake-novelwriter-readme-20260614.md`
- README SHA256: `3E36BAD4A2607051DBDB99433B6908277B24FE5DBDEB50278E46235D3E0DE294`
- Intake posture: pattern-only / no runtime

### Kindling

- Repository: https://github.com/smith-and-web/kindling
- Static HEAD: `fb67c06ff6e26983e42977624b427dd889abc90d`
- Default branch: `main`
- License: MIT
- Local static packet: `tmp/source-intake-kindling-readme-20260614.md`
- README SHA256: `33D6B239BBCD9576DE82CD5538FEA16CCAE6E60AB25031DACCB2B8CC3870D061`
- Intake posture: pattern-only / no runtime

## Static Evidence

NovelWriter's README describes a writing environment with chapters, scenes,
characters, plot planning, an Agent panel, Event Line, open plot lines,
Connection Web, Story Pulse, inline scene suggestions, optional Echo Chamber
reader reactions, live mood/remarks, reading mode, and PDF export.

Kindling's README describes local-first writing software for plotters and
outliners where the outline stays visible while writing. Static markers include
scene beats as expandable prompts, imports from Scrivener, Plottr, yWriter,
Obsidian Longform and Markdown, exports to Scrivener, DOCX, EPUB, Markdown,
Longform and Treatment, local SQLite project files, smart reference detection,
custom fields/tags, beat sheet templates, reference panels, and sync/reimport
previews.

## Fused Pattern

### `live_diagnostics_outline_import_gate`

When `novelwriter_live_manuscript_analytics_gate` or
`kindling_local_outline_reference_import_gate` is active, MuMuAINovel should
surface two separate custody layers before drafting:

```text
live_diagnostic_layers
advisory_analysis_boundary
visible_outline_scaffold
import_export_custody
reference_detection_boundary
continuation_or_same_type_boundary
runtime_boundary
```

The gate prevents three common failures:

1. live diagnostics and reader simulations being treated as accepted canon
2. visible outline prompts leaking into prose without chapter acceptance
3. imported project structure or reference labels becoming target-story facts

## MuMuAINovel Projection

- `book_remix_context_service.py`
  - Adds `live_manuscript_diagnostic_layers` and
    `advisory_scene_suggestion_review` to continuation control axes for
    NovelWriter-derived live analytics.
  - Adds `visible_outline_import_export_custody` to continuation control axes
    for Kindling-derived visible outline/import-export custody.
  - Adds `verify_live_diagnostics_review_state` and
    `verify_outline_import_export_custody` acceptance steps.
  - Renders continuation and same-type context sections for diagnostic layers,
    visible scene-beat scaffolds, import/export custody, reference detection,
    target-story independence, and runtime exclusions.

## Runtime Boundary

Do not run or install upstream runtimes during static intake:

- no npm install/dev server, Tauri/Rust/Svelte build, or app launch
- no AI side panel execution, provider call, generated summary, mood art,
  reader simulation, or PDF export
- no local SQLite project access
- no parser execution, import/export action, sync/reimport action, or manuscript
  data read
- no copying upstream demo beats, reference labels, screenshots, release assets,
  or generated prose into target canon

The absorbed value is the custody model, not upstream code or runtime behavior.
