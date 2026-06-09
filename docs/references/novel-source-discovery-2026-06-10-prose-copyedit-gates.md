# Novel Source Discovery - 2026-06-10 Prose Copyedit Gates

## Purpose

Static intake for prose lint, grammar, spelling, and copyedit projects that can
improve MuMuAINovel's continuation and same-type creation review flow.

This pass mines workflow patterns only. It does not clone, install, run package
managers, launch language servers, start grammar servers, install browser/editor
extensions, or send manuscripts to external checking services.

## Safety boundary

- Quarantine: L1 public metadata + `git ls-remote` HEAD + raw license file read.
- GitHub REST API returned unauthenticated 403 rate-limit errors, so metadata was
  not trusted as complete.
- Raw license files were read as static text only.
- No external project code or examples were executed.

## Source snapshot

- [vale-cli/vale](https://github.com/vale-cli/vale)
  - HEAD: `c1533d196022cfd4c3b7fe37cad8aa07e03e49da`
  - default branch observed: `v3`
  - license: MIT
  - posture: pattern-only
  - absorbed pattern: configurable prose lint / house-style rule gate

- [textlint/textlint](https://github.com/textlint/textlint)
  - HEAD: `311bc33fd5649b81b36e59ff3e04c31801d551d2`
  - default branch observed: `master`
  - license: MIT
  - posture: pattern-only
  - absorbed pattern: pluggable natural-language lint profile and diagnostic queue

- [amperser/proselint](https://github.com/amperser/proselint)
  - HEAD: `79b33e728a385d6244a993c5e7f2f94c98cc881d`
  - default branch observed: `main`
  - license: BSD-style license text
  - posture: pattern-only
  - absorbed pattern: prose warning taxonomy for cliches, jargon, redundancy, and passive phrasing

- [Automattic/harper](https://github.com/Automattic/harper)
  - HEAD: `73d40fe09f9c1cec13034734a62fa4b6e678357b`
  - default branch observed: `master`
  - license: Apache-2.0
  - posture: pattern-only
  - absorbed pattern: offline grammar/spelling gate and dialogue exception boundary

- [languagetool-org/languagetool](https://github.com/languagetool-org/languagetool)
  - HEAD: `e560e2b8fd11b586a0a6ab5aa6b0c055692f6c09`
  - default branch observed: `master`
  - license: LGPL-2.1
  - posture: pattern-only / runtime-deferred
  - absorbed pattern: multilingual grammar, spelling, and style gate taxonomy

- [btford/write-good](https://github.com/btford/write-good)
  - HEAD: `6940b034c6f5a7e101c01a24d651a778fc3fe435`
  - default branch observed: `master`
  - license: MIT
  - posture: pattern-only
  - absorbed pattern: lightweight prose warnings and author-visible triage

## Reusable patterns

### prose_lint_style_rule_gate

Use lint rules as a project-local house style profile, not as universal truth.
Each warning needs chapter, speaker, scene, and deliberate-voice context. The
rule profile can improve final polish, but it must not flatten narrator or
character voice.

### grammar_spelling_copyedit_gate

Run grammar, spelling, and copyedit checks after canon/continuity review.
Grammar polish must not legitimize unsupported facts. Dialogue, dialect,
invented terms, names, and genre vocabulary need an explicit exception policy.

### copyedit_diagnostic_triage_queue

Convert lint and grammar diagnostics into review states: accept, ignore,
rewrite, or needs-author-review. Persist ignored diagnostics with reasons so
repeated warnings do not hide new copyedit defects across chapters.

## MuMuAINovel integration

Updated artifacts:

- `backend/app/services/source_discovery_service.py`
  - adds discovery queries and explicit repository URLs
  - classifies prose lint / grammar / diagnostic signals as novel automation
  - emits new pattern-pack targets and prompt hints
- `backend/app/services/source_pattern_pack_prompt.py`
  - renders new hint families into prompt digest
- `backend/app/services/book_remix_context_service.py`
  - adds `Copyedit and prose lint audit` to continuation and same-type contexts
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
  - increments source candidates to 131
  - records 171 workflow patterns
  - adds the three copyedit/prose-lint patterns

## Deferred runtime gates

A future runtime trial must define:

- exact checker and version
- local/offline vs external service boundary
- manuscript privacy scope
- allowed file paths
- generated report path
- timeout and cleanup
- no package hook / extension / server launch unless explicitly approved

Until then, these sources remain pattern-only.
