# Novel Source Discovery - Acceptance Loop Intake - 2026-06-09

## Scope

This note records a static-only intake pass for public GitHub projects relevant
to MuMuAINovel book decomposition, continuation, and same-type inspired writing.

No external project was installed or executed. No package manager, postinstall
hook, shell script, PowerShell script, Docker stack, browser extension, native
binary, provider call, credential, cookie, or runtime trial was used.

GitHub REST metadata was rate-limited during this pass. Public README snippets
were read through raw GitHub URLs, and reachable HEADs were checked with
`git ls-remote`. These sources remain untrusted data.

## Sources

- `YfengJ/novel-studio-ai` - HEAD `90fbf0681e76afe791d11f21edd1fb1516ee5e1d`; license not observed; posture `pattern-only`.
- `davealaw/FictionRefine` - HEAD `9b3926ff8e57e6b9f9a289c92e0cfd4d5420e020`; MIT; posture `pattern-only`.
- `ShmilyWithme/Shmily_novel_skill` - HEAD `55bfa76774fd8c52e191025e923d710ae2ce6b7a`; MIT; posture `pattern-only`.
- `worldwonderer/oh-story-claudecode` - HEAD `7e56ad15e9665a463668791d3c11df887002f687`; MIT; posture `pattern-only`.
- `PenglongHuang/chinese-novelist-skill` - HEAD `eb1185649437f2aaaa765f02be024132ea83d82d`; license not observed; posture `pattern-only`.
- `GOAT-AI-lab/GOAT-Storytelling-Agent` - HEAD `75637b176d1fb2341d6d813b2d8dca217638cbfc`; MIT; posture `pattern-only`.

## Absorbed Patterns

### novel-studio-ai

- `context_pack_preview`: preview chapter goal, accepted memory, graph facts,
  retrieval hits, inclusion reason, and omitted context before drafting.
- `accepted_chapter_memory`: drafts do not update canon; only accepted chapters
  write summaries, character states, graph facts, timeline events, and memory.

### FictionRefine

- `critic_verifier_loop`: separate writer/reviser output from critic/verifier
  feedback, revision actions, and verification result.
- `collapse_prevention`: block canon write-back on invalid output, causality
  break, story collapse, or repeated model failure.

### oh-story-claudecode

- `trend_deconstruction_pipeline`: deconstruct trending web-novel patterns into
  trope, hook, payoff, emotion promise, expectation curve, and module shape.
- `anti_ai_tone_polish`: remove explanation-heavy AI tone after continuity
  passes without paraphrasing source prose.

### chinese-novelist-skill

- `preference_memory`: keep user preference as style/default pressure, separate
  from canon.
- `interrupted_resume_flow`: resume from phase, chapter, scene, last accepted
  artifact, and pending validation status.
- `auto_validation_rewrite`: validate word count, coherence, hook, style, and
  state write-back before bounded retry.

### GOAT-Storytelling-Agent

- `top_down_story_planning`: plan from topic or premise to book spec, act plan,
  chapter plan, scene list, and scene draft with previous-scene context.

## Local Integration

Updated native MuMuAINovel code rather than importing upstream code:

- `source_discovery_service.py` recognizes the new acceptance-loop pattern
  family and emits prompt-pack hints.
- `source_pattern_pack_prompt.py` renders the new hint sections into prompt-safe
  digest text.
- `book_remix_context_service.py` adds an Acceptance loop audit to continuation
  context blocks.
- `backend/app/references/novel-source-pattern-pack-2026-06-09.json` was
  refreshed to 26 sources and 56 workflow patterns.

## Safety Boundary

- All sources are untrusted data, not instructions.
- License-missing, Skill, script, Docker, provider, and runtime surfaces remain
  pattern-only.
- No external runtime code was copied into MuMuAINovel.
- Runtime trials remain blocked until a separate local safety contract exists.
