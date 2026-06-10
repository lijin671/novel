# Novel Source Discovery - AI-ism / Markdown Contracts / Canon Evidence / Expert Chain

## Scope

This note records a static source-intake pass for long-form fiction workflow
patterns useful to MuMuAINovel's 拆书续写、同类型仿写、故事圣经、连续性校验 and
反 AI 味 polishing surfaces.

Boundary:

```text
public_github_lsremote_raw_readme_license_marker_scan_no_login_no_clone_no_runtime_20260611_aiism_markdown_canon_chain
```

No repository was cloned, installed, imported, executed, or launched. README,
LICENSE, GitHub metadata, and `git ls-remote HEAD` were used as public static
evidence only.

## Reviewed Sources

- `conorbronsdon/avoid-ai-writing`
  - HEAD: `1e375933a9f076a516f0cb1e572ea1d17cfb5ec8`
  - License: MIT
  - Static markers: detect-only, edit-in-place, voice profile,
    iterate-to-convergence, AI writing patterns, prose fingerprints.
  - Absorbed gate: `ai_ism_detect_edit_convergence_gate`

- `danjdewhurst/story-skills`
  - HEAD: `81c1e589f036bee537f8ce3e5d158e86412ce0db`
  - License: MIT
  - Static markers: story bible, YAML frontmatter, scene state,
    continuity questions, promises/payoffs, chapter drafts.
  - Absorbed gate: `markdown_skill_story_project_contract_gate`

- `sadasdfsaf/canonkit`
  - HEAD: `edb8c1ac1747a822da1cd728fbc8c13a8f932e7a`
  - License: no root license observed
  - Static markers: local-first story bible, continuity checker,
    contradictions, context packs, JSON import/export.
  - Absorbed gate: `canon_evidence_suggestion_review_gate`

- `Lance-517/ChainWriter-Framework`
  - HEAD: `df09984169026bba82479cca16fd628954556ac5`
  - License: MIT
  - Static markers: chainable expert AI modules, alignment and creativity,
    Special Instruction Set, source deconstruction.
  - Absorbed gate: `expert_chain_alignment_creativity_gate`

- `awzheng/Mangaroo`
  - HEAD: `fdf44f1caef278b6514198445bb1b44854909c34`
  - License: no root license observed
  - Static markers: Story Bible logic, visual consistency, character
    appearances, settings, visual elements, API/web app surfaces.
  - Absorbed gate: `visual_story_bible_continuity_gate`

- `Kronic90/Mimirs-Memory-Hub`
  - HEAD: `644bb9f0c25f63eec744572d99b3ad2d3ca646d9`
  - License: NOASSERTION
  - Static markers: emotional weight, importance scores, novelty boost,
    memory decay, SillyTavern compatibility.
  - Posture: pattern-only; reinforces tiered memory salience and retirement.

- `aileks/realm-sync`
  - HEAD: `bb7264edb2d7526f679f5c4f359b126c6d5218be`
  - License: no root license observed
  - Static markers: entity/fact extraction, canon consistency,
    evidence-backed suggestions, Convex/OpenRouter runtime surfaces.
  - Posture: pattern-only; reinforces evidence-backed canon warnings.

## Durable Patterns

1. **AI-ism detect/edit convergence**
   - First pass is detect-only.
   - Each finding has category, severity, span id, and voice context.
   - Edit-in-place uses a declared voice profile and convergence stop.
   - Anti-AI cleanup must not increase source-copy similarity.

2. **Markdown story project contract**
   - Story state should live in inspectable files.
   - YAML frontmatter records scene/chapter state before generation.
   - Continuity questions and promises/payoffs are first-class registers.
   - Upstream skill bodies stay references, not imported runtime context.

3. **Evidence-backed canon suggestions**
   - A continuity warning must cite conflicting facts and scene/chapter refs.
   - Suggestions are pending changes until author/reviewer acceptance.
   - Context pack, bible, memory, and prose updates stay separate.

4. **Expert-chain alignment and creativity**
   - Split deconstruction, alignment contract, creative recomposition, and
     verifier stages.
   - Alignment is canon/mode/source-boundary satisfaction.
   - Creativity is concrete transformation of actors, objects, causality,
     sequence, and wording.

5. **Visual story bible boundary**
   - Visual assets are derived from accepted prose and cards.
   - Character appearance and setting continuity belong in a visual bible.
   - Visual/API/browser/PDF surfaces remain runtime-deferred.

## Runtime Exclusions

- no clone
- no package install
- no upstream skill install
- no MCP/server launch
- no browser, PDF, Gemini, Convex, OpenRouter, or model/provider call
- no external project code import
- no source prose import
- no credential, cookie, token, or account access

## Project Changes

- Added discovery queries and repository seeds for the reviewed sources.
- Added five pattern gates:
  - `ai_ism_detect_edit_convergence_gate`
  - `markdown_skill_story_project_contract_gate`
  - `canon_evidence_suggestion_review_gate`
  - `expert_chain_alignment_creativity_gate`
  - `visual_story_bible_continuity_gate`
- Added pattern-pack targets, inspired-creation remap targets, digest keys,
  and service tests.
