# Novel Source Discovery 2026-06-14 — mdnovel Section / Plotgrid / Time Trace

## Source

- Repository: https://github.com/peter88213/mdnovel
- Static HEAD: `6d35eee674912a2e505293a4a0adcb25b054b5da`
- Default branch: `main`
- GitHub metadata checked: 2026-06-14
- License: GPL-3.0
- State: archived public repository
- Posture: pattern-only

## Static Evidence

Static public metadata and README/root markers show a Markdown novel editor with:

- manuscript hierarchy: parts, chapters, sections
- per-section viewpoint character, status, summary, characters, locations, items
- plot lines, subplots, character arcs, plot grid, and spreadsheet-style matrices
- narrative time, duration, date, weekday, and character age by section
- unused chapters/sections excluded from document export
- JSON text-file storage and Pandoc-oriented manuscript export
- release/download surface under `dist/`, including executable archive / zip distribution
- Python/Tkinter runtime, optional Pandoc, optional Timeline integration
- structural templates such as Three Act, Hero's Journey, and Save the Cat

## Absorbed Patterns

### `narrative_time_age_trace_gate`

For拆书续写 and same-type writing, every accepted section should carry a minimal time trace:

```text
section_id
status: planned | drafted | reviewed | accepted | unused | rejected
pov_character
narrative_date_time
duration
weekday
character_age_refs
plotline_refs
export_included
source_evidence
```

The gate blocks three common failures:

1. timeline drift after long continuation batches
2. character-age and relationship-speed contradictions
3. draft/unused sections leaking into canon, prompts, or export

### Existing Pattern Reinforcement

- `section_metadata_traceability_gate`: section metadata now explicitly includes POV, status, time, and export boundary.
- `plotgrid_scene_matrix`: matrix rows should include plotline, POV, location, emotion, status, time, and linked hooks.
- `plotline_thread_tracking`: subplots and character arcs must be visible across section rows.
- `manuscript_export_formats`: exports are derived artifacts and must ignore unused/rejected sections.

## Local Adaptation

- Add `peter88213/mdnovel` to static discovery sources.
- Add a dedicated `narrative_time_age_trace_gate` so continuation context can audit section time and export state.
- Surface the gate in pattern-pack hints, prompt digest, frontend panel, and remix context blocks.
- Keep GPL source as pattern-only. Do not import code, templates, sample projects, release archives, or README prompt bodies.

## Runtime Boundary

Do not run or install:

- Python/Tkinter application
- `.pyzw` or `.zip` release archives
- setup scripts
- Pandoc conversion pipeline
- Timeline sync
- converters in linked tools
- bundled templates or samples as project defaults

This intake is static review only.
