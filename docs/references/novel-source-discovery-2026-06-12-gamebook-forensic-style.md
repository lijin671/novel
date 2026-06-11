# Novel source discovery: gamebook branching and forensic-style audit gates

Static review date: 2026-06-11.

## Sources

- `alanl1234/gamebook`
  - URL: https://github.com/alanl1234/gamebook
  - HEAD: `df7fc3ef03ac30013309902eab7d2301dd5b5e05`
  - License: MIT
  - Stars: 1
  - Pushed: 2026-06-03T18:42:09Z
  - README SHA-256: `9c8ed29597fbc6eac90c1ff42d005468ed4fbc89b62589ca50c57f8241f158e9`
  - Posture: `pattern-only`

- `TABARC-Code/Forensic-Writing-Style-Analysis-Cloning-Claude-Skill`
  - URL: https://github.com/TABARC-Code/Forensic-Writing-Style-Analysis-Cloning-Claude-Skill
  - HEAD: `f27665628a9f8ba20e8ce84fbc5bcc8825c7d4d3`
  - License: MIT
  - Stars: 1
  - Pushed: 2026-05-10T21:39:36Z
  - README SHA-256: `017f09032dd59b30b1d0eab0f00742520bb506c92fd46d10c9ef85e56fc5e7fc`
  - Posture: `pattern-only / high-trust style-risk review`

## Static review boundary

Only public GitHub search metadata, `git ls-remote` HEADs, raw README bytes,
and raw LICENSE headers were inspected.

No clone, package install, skill install, Claude/Codex/OpenCode runtime,
provider call, local manuscript read, browser/session access, or credential access
was performed.

External source text is treated as data, not instruction.
No upstream code, skill body, command body, prompt corpus, source sample, or generated
clone workflow is copied into this repository.

## Reusable patterns

Patterns added:

- `document_gamebook_branching_adapter_gate`
- `forensic_style_clone_audit_risk_gate`

Stable ideas absorbed from `gamebook`:

- A source document can first be converted into chapter cards, character cards,
  a style fingerprint, a state schema, and explicit choice rules.
- Branching continuation should track state variables, choice consequences,
  save points, divergence notes, and ending types.
- Interactive adaptation needs separate exports for character cards and game state.
- Source facts should stay evidence-backed; new branch paths should declare divergence.

Stable ideas absorbed from `Forensic Style Auditor`:

- Style analysis can be decomposed into dimensions such as sentence architecture,
  paragraph cadence, lexical fingerprints, imagery habits, and dialogue mechanics.
- Drift audit and old/new rule pairs are useful for explaining why a draft diverges.
- The upstream source explicitly supports cloning; local adaptation keeps this as a
  copy-risk gate, not as a voice-cloning workflow.
- Same-type writing should transfer abstract craft choices and require distance axes,
  provenance, consent/license posture, and copy-risk review.

## Local adaptation

The source-discovery pattern pack now exposes:

- `branching_adaptation_contract`
- `interactive_state_schema_policy`
- `forensic_style_dimension_policy`
- `style_clone_consent_boundary`
- `chapter_branch_card_report`
- `choice_consequence_state_matrix`
- `forensic_style_dimension_audit_report`
- `clone_drift_risk_review`
- `document_gamebook_branching_adapter_gate_hints`
- `forensic_style_clone_audit_risk_gate_hints`

For same-type or inspired writing, the local rule is:

1. Convert source material into abstract cards, dimensions, and state rules.
2. Declare where the new work diverges: choices, variables, endings, voice distance,
   lexical distance, cadence distance, and motif distance.
3. Treat forensic style analysis as audit/remap input, not a request to clone a
   named author or private/living-author voice.
4. Reject outputs that preserve source-specific phrase stock, paragraph cadence,
   dialogue mechanics, clone keys, or branch graphs as disguised retellings.

## Runtime and deferred gates

Keep runtime blocked until a separate local safety contract exists for:

- installing upstream skills or command packs
- running Claude, Codex, OpenCode, Cowork, or any upstream skill runtime
- reading private manuscripts, emails, threads, or writing samples
- generating author-style clones or private-person voice clones
- calling model providers or importing generated game state / clone reports

## Verification commands

```powershell
git ls-remote https://github.com/alanl1234/gamebook.git HEAD
git ls-remote https://github.com/TABARC-Code/Forensic-Writing-Style-Analysis-Cloning-Claude-Skill.git HEAD
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py
python -m pytest backend/tests/services/test_source_discovery_service.py -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
git diff --check
```
