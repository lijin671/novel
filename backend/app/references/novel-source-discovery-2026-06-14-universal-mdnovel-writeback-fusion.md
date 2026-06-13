# Novel Source Discovery 2026-06-14 — universal-novel-writing × mdnovel writeback fusion

## Sources

- Local reference: `D:/project/universal-novel-writing`
- GitHub reference: `https://github.com/peter88213/mdnovel`
- Intake posture: pattern-only for both sources

## Static Evidence

`universal-novel-writing` defines the accepted-chapter progress report as a
separate write-back artifact: summary, new facts, character changes, hook/payoff
movement, continuity updates, next focus, measurable length, and risks.

`mdnovel` adds per-section narrative time, duration, weekday, character age,
status, and export-inclusion boundaries.

## Fused Pattern

When both `progress_report_continuity_writeback_gate` and
`narrative_time_age_trace_gate` are active, MuMuAINovel now treats time/status
trace fields as part of the accepted chapter write-back gate.

Required fused fields:

```text
summary
new_facts
character_changes
hook_deltas
continuity_updates
next_chapter_focus
word_count
risks
narrative_time
duration
weekday
character_age_refs
section_status
export_included
```

This closes a gap between chapter-level creative acceptance and section-level
export/canon custody. A chapter is not ready for reuse in continuation prompts
if the prose summary is present but its narrative time, age trace, section
status, or export boundary is missing.

## MuMuAINovel Integration

- `book_remix_context_service.py`
  - Adds `narrative_time_age_progress_writeback` to continuation control axes
    when both gates are active.
  - Adds `verify_narrative_time_age_writeback` to acceptance steps.
  - Extends progress-report gap detection with narrative time, duration,
    weekday, character age refs, section status, and export inclusion.
  - Renders required time-trace fields inside the continuation context block.

## Runtime Boundary

No local skill install, no upstream code import, no provider call, no browser/MCP
runtime, no Pandoc/Timeline execution, no prompt-body transplant, and no GPL code
copying was used.
