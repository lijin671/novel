# Novel source discovery - 2026-06-14 mode-contract preview projection

## Source

- GitHub: `FURUYAN1234/story-maker`
- Public HEAD: `667f0a5f79f820b272ad046db597a8502bd50d7e`
- Default HEAD ref: `refs/heads/main`
- License: no root `LICENSE` observed from raw probe
- Intake posture: `pattern-only`

## Static evidence used

Bounded public probes only:

- `git ls-remote --symref https://github.com/FURUYAN1234/story-maker.git HEAD`
- raw `README.md` from `main`
- raw `package.json` from `main`

No clone, checkout, npm install, build, provider call, browser runtime, API key,
image input, news grounding, prompt body import, or generated output was used.

## Reusable pattern

Story Maker's stable idea is a visible multi-axis generation contract:

- selected output mode wins over incidental source-material wording
- visible axes are inspectable before generation
- axes include theme/seed, characters, genre, world/setting, audience, era,
  ending style, narrator/POV, source material, supplemental constraints, and
  optional style analysis
- short/generic output should be repaired from the same accepted axes rather
  than patched with source-specific facts or copied plot order

## MuMuAINovel projection

This pass projects the pattern into continuation context preview:

- `selected_output_mode_priority`
- `visible_creative_axis_contract`
- `under_length_rewrite_boundary`
- `mode_contract_axes`
- `mode_contract_warnings`

The prompt context now renders `Mode contract generation audit` when
`mode_contract_generation_gate` is active, making selected mode and visible-axis
gaps visible before continuation or same-type drafting.

## Safety boundary

Runtime remains blocked for clone, checkout, npm install, Vite build of the
upstream project, provider/API calls, API-key entry, browser runtime, image/news
features, prompt-body import, credential reads, host/model config mutation, and
remote push.
