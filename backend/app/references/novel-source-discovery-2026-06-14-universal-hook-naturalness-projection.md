# Universal Novel Writing hook / naturalness projection

Date: 2026-06-14

Source:
- `D:/project/universal-novel-writing`
- `D:/project/universal-novel-writing/SKILL.md`
- `D:/project/universal-novel-writing/references/chapter-workflow.md`
- `D:/project/universal-novel-writing/references/revision-checklists.md`

Posture:
- local static review only
- pattern-only
- license unknown
- no install, clone, script execution, provider call, browser/MCP runtime, or manuscript import

Reusable patterns:

1. `opening_ending_hook_integrity_gate`
   - Continue-chapter and same-type workflows need an explicit opening hook type.
   - Ending hooks need a named job: danger, reframed fact, forced decision, cost, collided desires, thread payoff plus larger question, or changed image.
   - Fake cliffhangers are rejected when they resolve instantly without cost, state change, or payoff movement.

2. `anti_ai_naturalness_texture_gate`
   - Naturalness review is a manuscript quality gate, not an AI-detector bypass claim.
   - Review looks for balanced essay rhythm, generic emotion labels, polished summary dialogue, repetitive transitions, and over-neat moral explanation.
   - Repair uses concrete action, uneven rhythm, sensory pressure, subtext, silence/avoidance, and character-specific diction.

Artifacts updated:
- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `frontend/src/types/sourceDiscovery.ts`
- `frontend/src/types/bookRemixBible.ts`
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
- `frontend/src/components/book-remix/BookRemixContinuationContextPreviewPanel.tsx`
- `backend/app/references/novel-source-pattern-pack-2026-06-13.json`

Deferred/runtime gates:
- Upstream prompt bodies and prose examples are not imported.
- Source opening/ending hook content is not copied.
- Same-type creation may only reuse hook pressure and review axes.
- Continuation may only use target-owned accepted state and open promise debts.

Verification:
- Added TDD coverage for source pattern absorption, continuation/same-type context rendering, production audit axes, and frontend hint surfacing.
