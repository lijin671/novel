# Novel Source Discovery - 2026-06-10 Voice / Timeline / Skill Catalog Gates

## Scope

Static source-intake pass for character voice control, rolling anti-repetition,
series timeline continuity, relationship mapping, and creative-skill catalog
triage relevant to MuMuAINovel 拆书续写 and 同类型创作.

Boundary:

```text
public_metadata_static_review_no_clone_no_install_no_execute
```

No external source was cloned, installed, executed, used as a plugin, launched
as an agent, or allowed to call a provider. Evidence was limited to public
GitHub pages, `git ls-remote` HEAD checks, and selected public raw root files
such as README / LICENSE / AGENTS.md / package manifests.

## Source snapshots

- `rhavekost/author-toolkit`
  - URL: `https://github.com/rhavekost/author-toolkit`
  - HEAD: `5faebfac5fddb59149798b8108a2c379d9b2465c`
  - License: no root license file observed in this static pass.
  - Static signal: public README describes Claude Code writing skills for
    fiction and narrative authors, a fiction workshop, Character Consultant,
    Continuity Tracker, timeline/world-fact consistency, and genre-specific
    worldbuilding checks.
  - Posture: `pattern-only`; license/trust review deferred before any runtime
    trial.

- `mike-cramblett/novel-novel-generator`
  - URL: `https://github.com/mike-cramblett/novel-novel-generator`
  - HEAD: `a658c9bbd24f2ab00799c295768608f91388b198`
  - License: no root license file observed in this static pass.
  - Static signal: public README/package metadata describe a whole-novel
    pipeline with story-bible generation, character voice fingerprinting,
    chapter outline planning, drafting with prior context, continuity editor
    audit, rolling summary, rolling pre-banned phrases, state JSON, and PDF
    export.
  - Posture: `pattern-only`; Node runtime and providers are excluded.

- `denmurray10/Story-Timeline-Builder`
  - URL: `https://github.com/denmurray10/Story-Timeline-Builder`
  - HEAD: `89297a658b3f2ff7ea6d62baf5202ece6eebb7b7`
  - License: no root license file observed in this static pass.
  - Static signal: public README describes a fiction-author digital story bible
    for complex multi-book series, chronological events versus narrative
    sequence, dynamic relationship mapping, character arcs, worldbuilding rules,
    and continuity-error prevention.
  - Posture: `pattern-only`; Django app, hosted service, database, and AI
    runtime are excluded.

- `jwynia/agent-skills`
  - URL: `https://github.com/jwynia/agent-skills`
  - HEAD: `e02ec7e226a6e4f8419fd3b88a1d8e472d421b32`
  - License: no root license file observed in this static pass.
  - Static signal: public README/AGENTS.md describe a large agent-skill catalog
    with creative/narrative categories and context-network workflow notes.
  - Posture: `index-only`; skill packs and prompt bodies are not installed or
    imported wholesale.

## Reusable patterns

- `voice_fingerprint`
  - Separate character voice evidence from generic prose style.
  - Use voice checks before accepting generated chapters as future style input.

- `anti_repetition_prompt_rules`
  - Maintain rolling banned phrase / repeated beat ledgers across chapter
    batches.
  - Repair failing spans or repeated beat chains instead of flattening voice.

- `rolling_summary_context_trim`
  - Update running summaries only after accepted chapters.
  - Record which context was omitted and why it is safe to drop.

- `temporal_canon_context_graph`
  - Compare chronological event order against narrative reveal order before
    accepting continuation or same-type planning changes.
  - Treat source chronology as analysis evidence, not transformed-story canon.

- `character_interaction_network_gate`
  - Track relationship polarity, frequency, bridge characters, and arc deltas
    across long series.
  - For same-type creation, rebuild relationship topology instead of renaming
    source relationships.

- `source_discovery`
  - Large creative/narrative skill catalogs stay `index-only`.
  - Promote one bounded pattern only after original-source confirmation,
    posture review, and safety notes.

## Local adaptation

Updated durable project surfaces:

- `backend/app/services/source_discovery_service.py`
  - adds four static-review seeds
  - adds compact summaries for voice, timeline, relationship, and skill-catalog
    intake
  - adds a static posture override so large skill catalogs can stay `index-only`
    rather than being treated as runtime candidates

- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
  - raises source candidate count to 228
  - adds the new sources to current pattern evidence and source titles
  - refreshes hints for voice, anti-repetition, temporal graph, relationship,
    rolling-summary, and source-discovery catalog gates

- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
  - adds the four sources to the editable default seed list
  - exposes `Voice / timeline continuity gates` in the source discovery panel

- `frontend/src/types/sourceDiscovery.ts`
  - adds explicit fields for the new surfaced gate groups

## Deferred/runtime gates

Still not authorized by this intake:

- cloning or installing repositories
- running Claude Code / Node / Django / provider-backed workflows
- importing skill bodies, prompt bodies, AGENTS.md content, README prose, or
  generated fiction
- launching apps, databases, MCP/server runtimes, browser/desktop automation, or
  hosted services
- using API keys, cookies, tokens, private repos, or account state

Runtime trial requires a separate local safety contract covering scope, auth,
secrets, network, cleanup, rollback, and verification.

## Verification targets

- Source discovery service tests should prove the new seeds, posture override,
  and mapped patterns.
- Frontend copy tests should prove the new seed URLs and visible gate group.
- `git diff --check`, backend tests, and frontend build should pass.
