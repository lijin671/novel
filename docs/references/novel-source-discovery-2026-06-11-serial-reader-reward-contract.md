# Novel Source Discovery - Serial Reader Reward Contract (2026-06-11)

## Scope

Static source-intake pass for commercial serialization, reader reward, opening-hook, paid-conversion, and platform-packaging patterns that can improve the book-remix / continuation workbench.

No upstream project was cloned, installed, executed, or imported as runtime code. Scratch evidence is under `tmp/source-intake-20260611-serial-reader-reward/`.

## Sources

### `ansrhkddns-web/k-webnovel-architect`

- URL: https://github.com/ansrhkddns-web/k-webnovel-architect
- Observed HEAD: `7744c0472257f6487f3067ff5f929fbc6a5cd1e5`
- License: MIT
- Family: webnovel commercial-serialization planning skill
- Posture: pattern-only

Reusable patterns:

- Treat genre grammar as a reader contract, not just a trope list.
- Track target reader persona, promised reward, opening hook, episode roadmap, chapter production brief, paid-conversion point, platform packaging, and retention risk as separate artifacts.
- Use paid-conversion planning as a trust check: the reader must have received enough concrete reward before the free-to-paid turn.
- Platform package outputs are market artifacts; they should not mutate canon unless the author approves the story impact.

Deferred/runtime gates:

- Do not import upstream skill text, agents, references, prompts, or install assumptions.
- Do not run any Codex/agent workflow from the source project.

### `0503xqy/novel-writer`

- URL: https://github.com/0503xqy/novel-writer
- Observed HEAD: `9a3c008ba7b071fabc34ea020c3c5a957217f3ed`
- License: no license observed
- Family: commercial webnovel project scaffold / skill
- Posture: pattern-only

Reusable patterns:

- Make each chapter carry a visible commercial contract: opening hook, chapter promise, pressure, reward, state change, ending hook, and retention risk.
- Keep canon, character relationships, power system, rhythm, commercial chapter contract, and retention audit as separate project folders/artifacts.
- Treat retention audit as a repeatable gate before accepting a long-serial chapter.

Deferred/runtime gates:

- No-license posture blocks code/prompt import.
- `SKILL.md`, agents, references, scripts, and prompt bodies are not imported or executed.

## Project Adaptation

Added `serial_reader_reward_contract_gate` to source discovery and pattern-pack generation.

The gate surfaces:

- `serial_reader_reward_contract_gate_hints`
- `serial_reader_reward_contract`
- `platform_packaging_boundary_policy`
- `reader_reward_map`
- `opening_hook_contract`
- `free_to_paid_turning_points`
- `platform_packaging_fit_report`
- `serial_reward_contract_remap`

Continuation prompt impact:

- Before drafting a serial chapter, name the target reader, promised reward, opening hook, delivered scene reward, retention risk, and next-payment trust signal.

Same-type / inspired-writing boundary:

- Rebuild the reader-reward contract from the transformed premise.
- Reject drafts that reuse source title formulas, reward order, paid-turn timing, platform package, or reader-promise wording.

## Verification Targets

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `frontend/src/types/sourceDiscovery.ts`
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/frontend/test_source_discovery_panel_copy.py`
