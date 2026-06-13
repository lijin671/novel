# Novel Source Discovery - Dramatic Corpus / Character Network Static Intake

Observed: 2026-06-13 Asia/Shanghai

Boundary:

```text
public_github_dramatic_corpus_character_network_static_lsremote_raw_marker_no_login_no_clone_no_runtime
```

This pass reviewed public GitHub metadata, `git ls-remote --symref HEAD`, and
raw README/LICENSE/package markers only. No repository was cloned. No package
manager, Docker stack, eXist DB, web frontend, API, notebook, dataset, model,
or corpus runtime was executed.

## Sources

- `dracor-org/dracor-api`
  - URL: https://github.com/dracor-org/dracor-api
  - HEAD: `e23d1761fb2a04a0bf0d2fd92875eb17e5e0013d`
  - License marker: MIT
  - Static markers: TEI drama API, characters, speakers, scenes, network
    metrics, eXist DB, metrics/triplestore services, Docker Compose.
  - Posture: `pattern-only`.

- `dracor-org/dracor-schema`
  - URL: https://github.com/dracor-org/dracor-schema
  - HEAD: `6631a52c364aaa426dce2e561f453a17eeeae34d`
  - License marker: CC-BY-4.0
  - Static markers: TEI customization, ODD, Relax NG schema, Schematron rules,
    drama encoding guidelines.
  - Posture: `pattern-only`.

- `dracor-org/dracor-frontend`
  - URL: https://github.com/dracor-org/dracor-frontend
  - HEAD: `67f62ac0aebedfaf24a77dc07cc7a2105d9c42a5`
  - License marker: MIT
  - Static markers: corpus browser, character-network UI, Vite/React,
    package runtime, local/API-backed configuration.
  - Posture: `pattern-only`.

- `L-Earthling/litnet-balance`
  - URL: https://github.com/L-Earthling/litnet-balance
  - HEAD: `88fd4ceb8ec9d45424a801bb1a154bb1e74c782b`
  - License markers: code MIT; dataset CC-BY-4.0 in README badge/description.
  - Static markers: 873 temporal signed fictional character networks,
    chapter-level positive/negative/neutral relationship polarity, structural
    balance, centrality, bridge-role analysis.
  - Posture: `pattern-only`.

Deferred weak signals:

- `roelsmeets/actual-fictions`: tiny public README, no license observed in this
  pass. Kept as weak character-network discovery signal only.
- `gaurav-sharma-22/author_style_transfer`: tiny public README, no license
  observed, direct author-style transfer framing. Kept as a negative-boundary
  reminder, not a style-transfer source.

## Absorbed Patterns

- `dracor_tei_scene_speaker_network_gate`
  - Model source scenes with speaker, cast, act/scene id, entrance/exit, and
    relationship-network evidence.
  - Use TEI-style structure as a拆书 index, not as copied dramatic text.
  - For continuation, verify dialogue ownership and speaker presence before
    accepting scene or chapter state.

- `temporal_signed_relationship_balance_gate`
  - Track positive, negative, and neutral relationship edges by chapter window.
  - Review centrality, bridge-character load, structural-balance shifts, and
    polarity reversals before accepting relationship canon.
  - For同类型仿写, change relationship balance, polarity timing, and bridge
    roles so a renamed cast does not preserve the source social graph.

## Runtime / Data Exclusions

- Do not clone, install, build, or run DraCor API/frontend/schema tooling.
- Do not run Docker Compose, eXist DB, triplestore, Vite, pnpm, schema build
  scripts, notebooks, Python requirements, or API calls.
- Do not download or import corpora, TEI texts, network datasets, thesis PDFs,
  generated graph data, or example dramatic text into drafting context.
- Do not treat public corpus/network examples as permission to copy scene order,
  cast names, dialogue, or relationship topology.

## Local Projection

Updated local artifacts:

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/tests/services/test_source_discovery_service.py`

Durable prompt-pack effect:

- Adds default discovery URLs and GitHub queries for DraCor / TEI dramatic
  corpus and temporal signed character-network sources.
- Exposes bible enrichment targets for TEI scene/speaker policies and
  relationship-balance thresholds.
- Exposes whole-book analysis reports for scene/speaker network coverage and
  temporal relationship polarity drift.
- Extends same-type copy-risk review with relationship-balance and
  scene/speaker graph leakage blockers.
