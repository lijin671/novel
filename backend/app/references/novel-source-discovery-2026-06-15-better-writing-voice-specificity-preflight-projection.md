# Novel source discovery - 2026-06-15 - Better Writing voice specificity preflight projection

## Source

- GitHub: `https://github.com/forjd/better-writing`
- Reachable HEAD: `0d7c441ab5b5b3da56fb92da022a51829500f385` on `refs/heads/main`
- License: MIT, from `LICENSE`
- Source family: prose-quality agent skill, voice calibration, anti-slop review, and pre-delivery scoring.
- Posture: public static review only; pattern-only projection.
- Scratch path: `tmp/source-intake-2026-06-15-better-writing`

Reviewed static files and SHA256:

```text
FA4D8C87EFB4ADD9F2312E0135A9F4DC3768BC885207EB0A3301868B61C86BE1  CHANGELOG.md
9D86A706C95E69FDCFE776DC458EB17A414A571F396FED021C7BC8741DFF3906  evals__README.md
9D7CA7E0934E84CD6D5BA3DB51E43D5AED04B93A153EF2BA81E84B44C2F554B9  LICENSE
DAE50A74E2F37AAC4D2A9B753DD68DF11C50C2481CC9B2CCE684B648C39CAECD  README.md
4F8B0EAC968C44E7E1F3C1BC788BB48BC98A41C4BA6C0321B0FE0F46C753F195  references__ai-writing-patterns.md
6947C32FE419009154BC94C7C6DABFE389D47B4BD4DFCD85BD698B615B3D5B7A  references__preflight.md
D5875A2CA740E3923EB7B5BFC491FA0505D79F5CE75B74B0B4F28484EF1E6DD0  references__sources.md
5E862E30DF929D45015C61267B19BA92FFAFFC9E24DCC75434EA13D60512B8C2  references__structures-and-phrases.md
6870AE30CA2013DC1FC57EFA77DBCA050DE68F841E5FBB43A1E6EA278383374F  references__voice-and-context.md
F3E3657B5FD17AA5C0BF1EF272A42ECA09856FAB604C74CC18B025F24D42C089  SKILL.md
51E5CBA874C5A2CE71C3ADF50602ABEC67BD6E4231D0C666D98EB27A219AF837  skills__better-writing__SKILL.md
```

## Absorbed pattern

Projected gate: `better_writing_voice_specificity_preflight_gate`

Reusable value:

- Treat target voice sample or accepted style signature as the prose source of truth.
- Select context dials before polish: genre, audience, tone, directness, warmth, personality, density, evidence, and polish.
- Add specificity only from canon or evidence; missing facts become placeholders or questions.
- Review AI tells as clusters and preserve defensible human quirks instead of flattening style.
- Score Directness, Specificity, Rhythm, Voice fit, and Density before public or accepted prose promotion.

## MuMuAINovel projection

Updated source discovery so Better Writing-like sources now produce:

- pattern detection for voice/specificity preflight
- pattern-pack hints
- bible enrichment target: `better_writing_voice_specificity_preflight_policy`
- whole-book analysis target: `better_writing_voice_specificity_preflight_report`
- same-type remap target: `better_writing_voice_specificity_preflight_remap`
- prompt, transformation, and copy-risk hints

Updated continuation preview/control so the gate becomes a project-native acceptance surface:

- production control axes for target voice source, context dials, specificity-without-invention, clustered AI-tell review, and preflight scoring
- warning bucket: `better_writing_voice_preflight_warnings`
- continuation context section that blocks invented details during polish
- same-type boundary that blocks importing source voice samples, examples, phrase lists, or upstream skill wording
- frontend type and warning display

## Boundary

No Better Writing skill, package manager, eval runner, upstream examples, or provider workflow was executed.

No upstream source code, skill body, examples, or reference phrase lists were transplanted. MuMuAINovel keeps a fresh implementation and uses only high-level voice-calibration and preflight-review patterns.

## Verification targets

```powershell
python -X utf8 -m pytest backend/tests/services/test_source_discovery_service.py::test_better_writing_voice_specificity_preflight_source_is_static_absorbed -q
python -X utf8 -m pytest backend/tests/services/test_book_remix_context_service.py::test_better_writing_voice_specificity_preflight_gate_projects_preview_controls -q
python -X utf8 -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py::test_continuation_context_preview_panel_surfaces_better_writing_warning_bucket -q
```
