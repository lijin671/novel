# Novel Source Discovery - System/World/Fate Simulation Gate

Date: 2026-06-11

## Source

- Repository: https://github.com/jasonyu0100/meridians
- Observed HEAD: `d023a2c011a76aa8e601aebc12c58e54f1cd47bd`
- Default branch: `main`
- License: MIT
- Stars/forks at review: 1 / 0
- Last pushed: 2026-06-10T04:55:42Z

Static evidence hashes:

- `README.md`: `87e54b3457f044f4e83b1d7b68874d7433d011e500158e06933d496e27f6b374`
- `LICENSE`: `7c2c869ce5cba41d4ed0475b60ebf218b51c1460bedc1b4c15895104fbd00a15`
- `package.json`: `240339ad014f00813f23ea3101d4de61ce72183a150b67d1dd7fe567ad5144e0`

Review posture: `pattern-only`, `runtime-deferred`.

No clone, npm install, browser launch, provider call, embeddings, image generation,
hosted demo use, or credential read was performed.

## Absorbed gate

`system_world_fate_simulation_gate`

Reusable pattern:

- Convert long-form source or accepted canon into a typed story graph.
- Track actors, locations, artifacts, threads, and system rules separately.
- Split simulation pressure into three fields:
  - `System`: rules, structures, constraints.
  - `World`: actor/world state and mutable positions.
  - `Fate`: open questions, unresolved tensions, bearing of the work.
- Convert LLM-extracted deltas into deterministic score/formula evidence before
  letting them steer the next scene.
- Preserve the pipeline boundary:
  - phase graph
  - causal reasoning graph
  - scene structures
  - beat plans
  - prose

## Local adaptation

For 拆书续写:

- Source analysis now has a dedicated force-field report target.
- Continuation prompts can request a System/World/Fate snapshot before drafting.
- State hints persist typed graph nodes, force scores, formula inputs, phase graph,
  causal reasoning graph, scene structure, and beat-plan ids.

For 同类型仿写:

- Transfer only the abstract pressure topology.
- Rebuild actors, locations, artifacts, threads, open questions, and deltas.
- Reject drafts that preserve the source force-field graph, phase order, or beat
  plan sequence under renamed labels.

## Runtime boundaries

Detected runtime-sensitive surfaces:

- Next.js / React browser runtime.
- IndexedDB/localStorage state.
- OpenRouter key surface.
- OpenAI embeddings key surface.
- Replicate token/image-generation surface.
- Hosted demo surface.

All remain disabled during source discovery.

## Updated artifacts

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `frontend/src/types/sourceDiscovery.ts`
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/frontend/test_source_discovery_panel_copy.py`
