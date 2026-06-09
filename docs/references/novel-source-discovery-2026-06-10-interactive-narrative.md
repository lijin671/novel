# Novel Source Discovery - 2026-06-10 Interactive Narrative

## Scope

Static source intake for interactive narrative, branching story, dialogue-node,
passage-link, and choice-stat consequence patterns that can improve MuMuAINovel
???? and ?????.

No external repository was cloned, installed, executed, or imported. No package
hook, browser extension, MCP server, Docker stack, native binary, shell script,
provider call, credential, cookie, or external runtime was used.

## Sources

- `inkle/ink` ? HEAD `35c63e52f1d36060930dc7ed3cfba38ea224b528`; license MIT; public README/root metadata only.
- `YarnSpinnerTool/YarnSpinner` ? HEAD `3a5b7343f715e4e9a3705fa4224e7fa510b92f1c`; license MIT; public README/root metadata only.
- `klembot/twinejs` ? HEAD `5f2a69d5c475f9b1c0e266780dadc9e1b7507cec`; license GPL-3.0; public metadata only.
- `dfabulich/choicescript` ? HEAD `60a6c3ee7393c9ee7e42650b8e1642ae38e3cb6a`; license missing/NOASSERTION; public metadata only.

## Absorbed Patterns

### branching_choice_graph

Model reader/player choices as explicit branch edges: source node, option intent,
consequence scope, and merge/reject decision. Faithful continuation keeps
optional branches outside main canon until a branch edge is accepted. Same-type
creation keeps choice pressure while replacing option text, order, consequences,
and branch topology.

### node_dialogue_state_machine

Represent dialogue as nodes with entry conditions, speaker state, available
options, command hooks, and exit state deltas. Continuation prompts should name
the active dialogue state before drafting. Same-type creation remaps conversation
pressure and state transitions without copying lines, option labels, or command
names.

### passage_link_navigation_map

Track passages as reachable nodes with visible links, hidden link conditions,
intentional merge points, and dead-end checks. Branching chapters need reachable
path validation before acceptance. Same-type creation rebuilds passage navigation
from the transformed premise instead of preserving source passage order or link
labels.

### choice_stats_consequence_gate

Every choice-stat mutation needs a visible immediate or delayed consequence, a
trigger record, stat delta, and payoff window. Hidden variable drift is rejected:
no branch may change canon, relationship, or world state without an explicit
consequence record.

## MuMuAINovel Integration

- `source_discovery_service.py` now classifies interactive narrative sources,
  exposes new pattern-pack hints, enriches analysis targets, and adds same-type
  remap/copy-risk rules.
- `source_pattern_pack_prompt.py` now renders the new interactive narrative hint
  keys.
- `book_remix_context_service.py` now injects `Interactive narrative audit` into
  continuation and same-type creation contexts.
- `novel-source-pattern-pack-2026-06-10.json` appends the four new public sources
  and four new workflow patterns to the existing pattern pack.
- Tests cover classification, default discovery sources, pattern-pack rendering,
  and continuation/same-type prompt audit output.

## Runtime Gates

- Pattern-only.
- No external code import.
- No repository clone or package install.
- No package hook, Docker, MCP server, browser extension, or native binary.
- No provider/model call.
- License notes stay provenance metadata; GPL/unknown sources are not imported
  into runtime code.
