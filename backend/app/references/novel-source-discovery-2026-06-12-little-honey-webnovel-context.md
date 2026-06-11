# Little Honey AI Web Novel static intake - 2026-06-12

## Source

- Repository: `CARL-JOSEPH-LEE/little-honey-ai-web-novel`
- URL: `https://github.com/CARL-JOSEPH-LEE/little-honey-ai-web-novel`
- Observed HEAD: `75386e7c2c901bf5ad9ef173f6a15db074db9358`
- Default branch: `main`
- License: `MIT`
- Stars / forks at intake: `0 / 0`
- Observed pushed time: `2026-05-17T02:37:42Z`

## Intake posture

`pattern-only`.

Only public GitHub metadata, `git ls-remote`, root tree names, and README
markers were reviewed. No clone, package install, runtime launch, provider call,
desktop app execution, script execution, binary inspection, or secret file read
was performed.

## Static markers

The README describes a serialized web-novel production chain:

```text
concept -> story bible -> rolling chapter direction -> scene blueprint
-> chapter draft -> quality review -> rewrite -> summary
-> continuity memory -> manuscript merge
```

The reusable part is not its desktop app. The reusable part is the way it
separates rolling chapter planning, scene-level reader payoff, review/rewrite,
and continuity memory writeback.

## Absorbed patterns

### `rolling_chapter_direction_context_priority_gate`

Use rolling chapter direction instead of a brittle full-book outline.

Context should be packed in priority order:

1. stable concept and story identity
2. useful story-bible slices
3. current chapter direction
4. previous chapter summaries
5. recent-summary window
6. continuity memory
7. user directions
8. nearby upcoming pressure
9. selected full previous chapters only after protected budget remains

This improves long continuation by preventing random history dumps and by
keeping stable identity above recent prose.

### `scene_blueprint_reader_reward_gate`

Convert a vague next-chapter direction into executable scene blueprints.

Required scene contract:

- location
- characters
- goal
- obstacle
- turning point
- information gain
- reader reward
- scene-end hook

This gives prose generation a narrative skeleton without making the final prose
template-like.

### `webnovel_quality_review_rewrite_memory_gate`

Review every draft before acceptance.

Review dimensions:

- opening hook
- continuity
- conflict density
- reader reward
- mobile readability
- cliffhanger strength
- originality
- dialogue
- pacing
- voice consistency
- anti-cliche behavior

Failed dimensions feed a bounded rewrite loop. Accepted chapters write back
summary and continuity memory: key events, character changes, new facts,
foreshadowing, open hooks, next pressure, timeline, world facts, unresolved
threads, and style notes.

## Risks and blocked surfaces

Root tree markers include Windows executables, license issuer tooling, packaging
specs, scripts, `seller_private_key.json`, and model/provider key surfaces.

Blocked during intake and future default runs:

- no `.exe` execution
- no license issuer execution
- no script execution
- no package install
- no provider/model call
- no credential, token, cookie, private key, or `seller_private_key.json` read
- no upstream prompt/code import

## Project mapping

Updated artifacts:

- `NovelSourceDiscoveryService` default GitHub discovery seed
- `PATTERN_KEYWORDS`
- static repository pattern override
- source pattern pack targets and hints
- inspired same-type creation remap / prompt / transformation / copy-risk hints
- source pattern pack digest allowlist
- focused regression test

## Verification

Focused test:

```powershell
python -m pytest backend/tests/services/test_source_discovery_service.py::test_static_little_honey_source_adds_rolling_context_scene_reward_review_gates -q
```

Observed result:

```text
1 passed, 3 warnings
```
