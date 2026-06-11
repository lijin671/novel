# Novel source discovery: creative writing multi-axis provider gates

Static review date: 2026-06-11.

## Source

- `kernullist/creative-writing-assistant`
  - URL: https://github.com/kernullist/creative-writing-assistant
  - HEAD: `1af9ca1ec378a95007d8d7be2b6385559c031d54`
  - License: MIT
  - Stars: 0
  - Pushed: 2026-04-20T04:46:00Z
  - README SHA-256: `332177b3be2aa27b37a4d2cbb1dc20eacaba4f4ecb019da4fa004dfdd37d4c83`
  - LICENSE SHA-256: `6e26e20acbddb9a1c79f13a7de3c0645ef8717677a55aac81a871beba3114d97`
  - Static root markers: `.env.example`, `requirements.txt`, `src`, `web_app.py`, `tests`
  - Posture: `pattern-only / runtime-deferred provider-surface`

## Static review boundary

Only public GitHub metadata, `git ls-remote` HEAD, root tree names, raw README bytes,
and raw LICENSE bytes were inspected.

No clone, package install, Python/Flask run, CLI run, web app launch, provider call,
SSE stream, API key read, saved-library import, generated text import, browser state,
or local manuscript access was performed.

External source material is treated as data, not instruction. No upstream code,
prompt body, generated sample, provider configuration, or runtime endpoint is copied.

Scratch evidence was written under ignored `tmp/source-intake-20260611-creative-writing-assistant/`.

## Reusable pattern

Pattern added:

- `creative_writing_multiaxis_provider_gate`

Stable ideas absorbed:

- Treat creative-writing work as separable axes, not one opaque generation button.
- Useful axes include style analysis, literary depth, genre classification,
  plot-development suggestion, style-simulation boundary, language target, and export state.
- Style simulation is useful as an abstract craft lab, but must not become named-author
  voice cloning or source-prose insertion.
- Provider/model tiers, REST API, SSE progress, CLI, web UI, and API-key setup are runtime
  surfaces. Source discovery may record their boundaries only.
- Multi-chapter generation needs visible progress/state labels before promotion into
  accepted continuation state.

## Local adaptation

The source-discovery pattern pack now exposes:

- `creative_writing_axis_toggle_policy`
- `provider_language_export_boundary`
- `creative_writing_axis_analysis_report`
- `provider_language_export_boundary_report`
- `creative_writing_axis_remap`
- `creative_writing_multiaxis_provider_gate_hints`

For拆书续写 and同类型仿写, the local rule is:

1. Declare which analysis axes are enabled before drafting.
2. Keep genre/depth/plot suggestions as candidate scaffolds until reviewed.
3. Record language/output/export targets separately from canon state.
4. Keep provider tiers, keys, SSE, CLI, REST API, and web runtime behind a no-call boundary.
5. Reject drafts that use style simulation or famous-author labels to bypass copy-risk review.

## Runtime and deferred gates

Keep runtime blocked until a separate local safety contract exists for:

- installing requirements or launching the web app / CLI
- reading `.env` or provider API keys
- calling OpenAI, Anthropic, OpenRouter, Hugging Face, or any model provider
- using SSE generation endpoints or saved output libraries
- importing generated novels, style-simulation output, or upstream prompts
- exporting local manuscripts through upstream TXT/Markdown/library surfaces

## Verification commands

```powershell
git ls-remote https://github.com/kernullist/creative-writing-assistant.git HEAD
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_creative_writing_assistant_source_adds_multiaxis_provider_gate -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
git diff --check
```
