# Novel source discovery - 2026-06-15 - Story Skills deterministic continuity projection

## Source

- GitHub: `https://github.com/danjdewhurst/story-skills`
- Reachable HEAD: `c482d48f4eb9b488f033a77a51f9fae55cc0d75f` on `refs/heads/main`
- License: MIT, from `LICENSE`
- Source family: markdown-first fiction project skills, story bible schema, and deterministic continuity maintenance.
- Posture: public static review only; pattern-only projection.
- GitHub API tree status: public API returned `403`; treated as no-bypass. Review continued only with bounded raw public files listed below.

Reviewed raw files and SHA256:

```text
6165CF9BA767438E8D149F747EF92C27C065FEAD7B45F91EFA111D617CAF8852  README.md
1C8C7A7B5BEF62874F510F603F02ADA40F5880668E8983D2FC7D1150B4318226  LICENSE
9ACE3DEC9FD2CA22E9F6A96A9CF54EA4F498EE6D4522301FD775BC87BD2511D6  skills/story-init/SKILL.md
BC21410CC846D00B766A8C465C30E48AF859083C83D2F731BD7EB415C76C578A  skills/character-management/SKILL.md
6085390C930309C1E9F3182C50C30E9D746D0F054000F2808147A80807B2B279  skills/worldbuilding/SKILL.md
54A38F07A5D0106C66E30058A7E375867F3CA1924AEF8208A4428C205D73146C  skills/plot-structure/SKILL.md
F302204D7FD1B61E99DB81BDAFF19CB45A5859635F6173404DDD2B985A1DF346  skills/chapter-writing/SKILL.md
C6A39A9C03D43EA6AC345F5FA428D11005C1E9CF430B1EDFF8B824B8B6273DA1  skills/revision-continuity/SKILL.md
C9343BE1365417B7323EAF98E97C2D9AC413D510BDA549A30CD1D2C709B8500E  skills/story-maintenance/SKILL.md
2A61450996B9C180B675C5EC1C6EDA3447132154B4D365FFB54BB016429F1265  docs/schema-v2.md
F018F4D5AA669B4315B6F0C785CCD40AEB46F4B66AA2166A62EBC5D4AA6EB95A  schemas/story.schema.json
```

## Absorbed pattern

Projected gate: `story_skills_deterministic_continuity_contract_gate`

Reusable value:

- Treat continuity as a deterministic contract, not only a prose-review checklist.
- Track character lifecycle/status and death chapter separately from later references.
- Separate present-scene cast from mentions, memories, records, and flashbacks.
- Track promise/question setup and payoff order so a resolution cannot precede introduction.
- Track durable character state, object state, and knowledge state before later chapters reuse them.

## MuMuAINovel projection

Updated source discovery so Story Skills-like sources now produce:

- pattern detection for deterministic continuity contracts
- pattern-pack hints
- bible enrichment target: `story_skills_deterministic_continuity_contract_policy`
- whole-book analysis target: `story_skills_deterministic_continuity_contract_report`
- same-type remap target: `story_skills_deterministic_continuity_contract_remap`
- prompt, transform, and copy-risk hints

Updated continuation preview/control so the gate becomes a project-native acceptance surface:

- production control axes for lifecycle, promise/question ordering, scene cast/mentions, and durable state references
- warning bucket: `story_skills_continuity_contract_warnings`
- continuation context section with no-runtime deterministic continuity rules
- same-type boundary that blocks importing upstream sample ids, CLI finding text, or demo continuity cases as target canon
- frontend type and warning display

## Boundary

No Story Skills CLI, package manager, plugin install, bundled scripts, GitHub Actions, examples, generated projects, or runtime checks were executed.

No upstream source code was transplanted. MuMuAINovel keeps a fresh implementation and uses only high-level project-contract patterns.

## Verification targets

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_state_contract_living_document_frontmatter_sources_are_static_absorbed -q
python -X utf8 -m pytest backend/tests/services/test_book_remix_context_service.py::test_story_skills_deterministic_continuity_contract_gate_projects_preview_controls -q
python -X utf8 -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py::test_continuation_context_preview_panel_surfaces_story_skills_continuity_warning_bucket -q
```
