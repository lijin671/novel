# Novel source discovery - Character knowledge timeline gate

Date: 2026-06-11

## Source

- Repository: https://github.com/v-saprykin/storygraph
- Static fetch method: `git ls-remote`, raw README, raw LICENSE
- Reachable HEAD: `1b8f5aaae5f1d047f25edd5a08d73adaddcee7e4`
- License marker: MIT
- Intake posture: `pattern-only`
- Runtime posture: no clone, no install, no Docker, no .NET build, no database,
  no provider/model call, no manuscript import.

## Static markers reviewed

The public README frames StoryGraph as a backend platform for converting
long-form fiction into a validated narrative graph. The core chain is:

```text
Manuscript text -> chapters -> scenes -> narrative events -> characters ->
relationships -> plotlines -> timelines -> analytical queries
```

Useful markers for MuMuAINovel:

- structural defects in long novels become harder to detect manually
- unresolved plotlines
- characters disappearing for too long
- facts known by each character at a given story point
- scenes that do not change story-world state
- what breaks if a key event changes
- `KnowledgeState`, `CharacterState`, `TimelineVersion`, `CausalLink`
- human review before merge
- public repo should not contain real unpublished manuscript data

## Absorbed pattern

### `character_knowledge_timeline_gate`

Add a first-class gate for tracking who knows what, when, and from which
evidence.

This strengthens拆书续写 and同类型仿写 because source graphs often preserve more
than plot order. They also preserve reveal order, secret holders, absence gaps,
and POV visibility. Those must be transformed, not renamed.

Gate rules:

1. Build a knowledge-state timeline per character.
   - event id
   - known fact
   - evidence id
   - reveal scope
   - timeline version
   - uncertainty status

2. Before a POV scene is accepted, verify visibility.
   - POV character cannot act on unknown facts
   - narration cannot leak secrets outside the current visibility window
   - reader-facing reveal timing must match the current chapter contract

3. For same-type creation, remap the source knowledge graph.
   - new secret
   - new holder
   - new reveal timing
   - changed absence gap
   - changed consequence path

## Project changes

- Added `v-saprykin/storygraph` to repository discovery seeds.
- Added a GitHub query for `knowledge states` / character fact visibility.
- Added `character_knowledge_timeline_gate` keyword detection.
- Added pattern-pack targets:
  - `character_knowledge_state_policy`
  - `pov_secret_visibility_policy`
  - `character_knowledge_timeline`
  - `secret_visibility_matrix`
  - `non_state_changing_scene_findings`
  - `missing_character_presence_report`
  - `character_knowledge_visibility_remap`
- Surfaced frontend/type/prompt digest hints.

## Deferred surfaces

StoryGraph's planned stack includes .NET, PostgreSQL, Docker Compose, workers,
OpenTelemetry, pgvector, and AI extraction workers. These stay blocked unless a
separate runtime safety contract exists.
