# Novel Source Discovery - 2026-06-10 Story Generation Pipeline / Persona Memory

## Scope

This note records a pattern-only intake pass for long-story generation,
co-writing, character persona memory, and event-to-sentence realization sources
that can improve MuMuAINovel's ???? and ????? flows.

No repository was cloned. No package was installed. No dataset was downloaded.
No Colab/notebook, benchmark, provider call, model runtime, Docker stack,
server, shell script, PowerShell script, MCP server, browser extension, or native
binary was executed.

Source checks used `git ls-remote --symref HEAD` plus raw README/LICENSE reads.
GitHub REST API authentication, cookies, tokens, and personal account state were
not used.

## Sources

- `google-deepmind/dramatron`
  - URL: `https://github.com/google-deepmind/dramatron`
  - Observed default branch: `main`
  - Observed HEAD: `2e7c36afadacf8321b77a468940024371b7a8c7a`
  - License: Apache-2.0 for software; README also states CC-BY for other
    materials
  - Static surface: `README.md`, `LICENSE`, `colab/`
  - Public README signal: hierarchical co-writing from log line to character
    descriptions, plot points, location descriptions, and dialogue; output is
    material for compilation, editing, and rewriting; README calls out
    plagiarism, toxicity/offense, bias/stereotype, and formulaic-output risks.

- `yangkevin2/emnlp22-re3-story-generation`
  - URL: `https://github.com/yangkevin2/emnlp22-re3-story-generation`
  - Observed default branch: `main`
  - Observed HEAD: `3a97ebde04e3333962c2825146897efe1dc87dd8`
  - License: MIT
  - Static surface: `README.md`, `LICENSE`, `scripts/`, `notebooks/`,
    `requirements.txt`
  - Public README signal: Re3 long-story generation, recursive reprompting and
    revision, Plan / Draft / Rewrite / Edit ablations, outline save/load,
    relevance and coherence rerankers, candidate count, beam size, and dynamic
    continuation thresholds.

- `LC1332/Chat-Haruhi-Suzumiya`
  - URL: `https://github.com/LC1332/Chat-Haruhi-Suzumiya`
  - Observed default branch: `main`
  - Observed HEAD: `290bf4ad22076156083804013012847a77c0646c`
  - License: Apache-2.0 for code; README badge states CC BY-NC 4.0 for data
  - Static surface: `README.md`, `LICENSE`, `characters/`, `research/`,
    `notebook/`
  - Public README signal: character imitation from approximate tone,
    personality, and plot chat; links to extracting characters from novels,
    personality research, and role datasets.

- `rajammanabrolu/StoryRealization`
  - URL: `https://github.com/rajammanabrolu/StoryRealization`
  - Observed default branch: `master`
  - Observed HEAD: `c01253d42d88783ea5899c68134f442d00b65183`
  - License: no root license file observed by raw file probes
  - Static surface: `README.md`, `EventCreation/`, `E2S-Ensemble/`,
    `Slotfilling/`
  - Public README signal: expanding plot events into sentences, event creation,
    slot filling, memory graph entity tracking, ensemble thresholds, confidence
    scores, and stale runtime/server instructions.

## Absorbed patterns

- `hierarchical_cowriting_story_scaffold`
  - Keep logline, character, plot-point, location, and dialogue layers separate.
  - Validate upper layers before lower-layer prose expansion.
  - Treat the scaffold as editable author material, not final autonomous prose.

- `human_coauthor_edit_boundary`
  - Human/review-gate compilation, editing, and rewriting stays mandatory.
  - Plagiarism, toxicity/offense, stereotype drift, and formulaic output are
    explicit acceptance risks.

- `recursive_reprompt_revision_loop`
  - Run plan, draft, rewrite, and edit as separate stages.
  - Persist outline checkpoints so interrupted work resumes from known state.
  - Use dynamic continuation thresholds instead of fixed-length padding.

- `reranker_guided_candidate_selection`
  - Generate multiple candidates only when review budget allows.
  - Score candidates for relevance to plan and coherence with accepted canon.
  - Store rejected candidate reasons, not just the winner.

- `character_dialogue_persona_memory`
  - Store character voice as evidence-backed tone, personality, relationship
    pressure, and plot-chat boundaries.
  - Use dialogue evidence to preserve role behavior without copying source
    lines or protected role IP.

- `event_to_sentence_realization_trace`
  - Represent prose expansion as plot event ? realized sentence ? confidence ?
    rejected alternatives.
  - Use confidence and alternatives to find thin, literal, or stale sentences.

- `entity_memory_slotfill_grounding`
  - Ground slot filling against entity memory for names, roles, locations, and
    objects.
  - Reject realized prose that imports source entities or leaves unresolved
    aliases.

## MuMuAINovel adaptation

- Continuation prompts now gain a story-generation pipeline audit section when
  the source pattern pack contains these patterns.
- Pattern-pack digest now exposes hierarchical scaffold, human co-author edit,
  recursive revision, reranker selection, persona memory, event realization, and
  slot-fill grounding hints.
- Same-type creation now gets remap targets for hierarchical story layers,
  recursive revision loops, candidate selection, persona memory, event
  realization traces, and entity slot grounding.

## Updated artifacts

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
