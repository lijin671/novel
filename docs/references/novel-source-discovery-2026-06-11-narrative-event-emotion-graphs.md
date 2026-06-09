# Novel Source Discovery - 2026-06-11 Narrative Event / Emotion Graphs

## Purpose

This note absorbs public GitHub projects for source-book deconstruction,
continuation, and same-type original creation.

The focus is structural evidence, not runtime import:

- literary entity/event annotation
- narrative event-chain and causal/discourse graph review
- sentiment/emotion arcs over chapters or scenes
- cross-context coreference stability
- character interaction networks

## Safety Boundary

Static intake only.

- No repository was cloned.
- No dataset, notebook, R package, Python package, Java runtime, model weight,
  graph pipeline, or visualization server was installed or executed.
- Sources with missing licenses stay pattern-only.
- Source character names, event labels, emotion-curve anchors, coreference
  clusters, and relationship topology must be transformed before same-type
  creation.

## Source Snapshot

| Source | Observed HEAD | License | Posture | Absorbed patterns |
|---|---|---|---|---|
| `dbamman/litbank` | `3e50db0ffc033d7ccbb94f4d88f6b99210328ed8` | unknown | pattern-only | `literary_event_entity_annotation_gate` |
| `eecrazy/ConstructingNEEG_IJCAI_2018` | `97b133685fbca89ce908977857e056481a9deadf` | unknown | pattern-only | `narrative_event_evolution_graph_gate` |
| `acolas1/EventNarrative` | `a6e2b06e998ac2709cce36ff25ae8ffaa3d9b425` | unknown | pattern-only | `narrative_event_evolution_graph_gate` |
| `doug919/narrative_graph_emnlp2020` | `f63a17ff7ef0d2d71630230e3c1af7a26894fdb3` | MIT | pattern-only | `narrative_event_evolution_graph_gate` |
| `mjockers/syuzhet` | `73ec7d852e1f368661069e1b75e6c8c12a9f2133` | unknown | pattern-only | `sentiment_arc_emotion_trajectory_gate` |
| `jon-chun/sentimentarcs_notebooks` | `f427bedd93b712d9574ae1d0cd60345cd3a342a9` | MIT | pattern-only | `sentiment_arc_emotion_trajectory_gate` |
| `SapienzaNLP/xcore` | `9a5713b210abaaa6ded158966b200740ea1bfbfc` | unknown | pattern-only | `cross_context_coreference_gate` |
| `anastasia-zhukova/XCoref` | `f62e9ddbe63290228cdc4cbd49f8c94105b1cf15` | Apache-2.0 | pattern-only | `cross_context_coreference_gate` |
| `hzjken/character-network` | `3f48c059b7aadc9fe9492961a54fcc0fa226b2d5` | unknown | pattern-only | `character_interaction_network_gate` |
| `devbret/character-interactions` | `68e1b8c88029a77e04007f73adc82da268fa377f` | MIT | pattern-only | `character_interaction_network_gate` |

## Reusable Patterns

### `literary_event_entity_annotation_gate`

Before source summaries or bible write-back, record:

- literary entities
- event mentions
- participant roles
- mention spans
- unresolved labels or annotation gaps

This gives 拆书 a reviewable evidence layer instead of letting raw summaries
silently become canon.

### `narrative_event_evolution_graph_gate`

Represent source events as a graph before deriving continuation or same-type
beats.

Track:

- temporal order
- causal edges
- discourse relation edges
- blocker / reversal / payoff edges
- next-event prediction uncertainty

For same-type creation, event order and causal edges must be remapped.
Renaming actors is not enough.

### `sentiment_arc_emotion_trajectory_gate`

Track source emotion as evidence:

- global sentiment arc
- character-specific emotion trajectory
- chapter or scene anchor
- turning-point reason
- model or lexicon disagreement

Emotion curves are review signals, not automatic quality scores.
For 仿写, the new book needs new triggers and payoffs.

### `cross_context_coreference_gate`

Maintain cross-chapter and cross-document mention clusters for:

- people
- places
- organizations
- events
- abstract concepts

Ambiguous clusters stay out of accepted canon until reviewed.
Same-type creation must regenerate aliases and cluster boundaries around the new
cast and event set.

### `character_interaction_network_gate`

Extract character networks as review evidence:

- co-occurrence
- dialogue interaction
- sentiment or polarity
- faction or group membership
- centrality and bridge characters
- relationship timing

For same-type creation, topology must change: centrality, alliance/conflict
polarity, timing, and bridge roles cannot mirror the source.

## Project Integration

Updated artifacts:

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/app/services/book_remix_context_service.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/services/test_book_remix_context_service.py`

Pattern pack now records:

- `source_candidate_count: 154`
- `workflow_patterns: 185`
- five new narrative event / emotion / character-network workflow patterns

## Deferred Runtime Gates

Runtime use remains blocked until a separate local safety contract exists for:

- local source corpus scope
- dataset/model/license boundaries
- no-network parser mode where possible
- output scratch path
- graph artifact checksum
- manual review before canon write-back
- explicit same-type transformation audit
