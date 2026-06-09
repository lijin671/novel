# Novel Source Discovery - 2026-06-10 Trope Boundary Independence

## Scope

This intake pass focuses on same-type creation and source-book continuation
where genre similarity is allowed but source-specific plot copying is not.

The absorbed pattern is a trope-level boundary:

- compare trope inventories as abstract genre signals
- use trope co-occurrence as expectation options, not copied plot routes
- track trope density and novelty budget before accepting a draft
- keep trope sites, scrapers, and parsers as metadata-only references by default

No repository was cloned. No package manager, installer, scraper, parser,
runtime service, browser, model provider, dataset import, or script was run.

## Source Snapshot

- `MitchSaltykov/TVTropes-correlation`
  - URL: `https://github.com/MitchSaltykov/TVTropes-correlation`
  - HEAD: `15f69de8447112db5d6f5d8f2f3863c712717097`
  - default branch: `master`
  - license: no license file observed in static root check
  - posture: `pattern-only`
  - absorbed pattern: `trope_inventory_similarity_gate`

- `jwzimmer-zz/tv-tropes`
  - URL: `https://github.com/jwzimmer-zz/tv-tropes`
  - HEAD: `44442b66286eaf2738fc5d863d175d4577da97f4`
  - default branch: `main`
  - license: MIT
  - posture: `pattern-only`
  - absorbed pattern: `trope_graph_expectation_map`

- `slowwavesleep/TvTropesMovieData`
  - URL: `https://github.com/slowwavesleep/TvTropesMovieData`
  - HEAD: `d4b330ec72bddbd61883d735cc2d62ae6f21f1e2`
  - default branch: `main`
  - license: CC-BY-SA-4.0
  - posture: `pattern-only`
  - absorbed pattern: `trope_density_novelty_budget`

- `rhgarcia/tropescraper`
  - URL: `https://github.com/rhgarcia/tropescraper`
  - HEAD: `20cf2606d348f0dc77d26b99c7f61630abc08fd3`
  - default branch: `master`
  - license: LGPL-3.0
  - posture: `pattern-only`
  - absorbed pattern: `trope_source_boundary_review`
  - runtime exclusion: no scraping or package execution

- `Sirver51/tvtropes-parser`
  - URL: `https://github.com/Sirver51/tvtropes-parser`
  - HEAD: `cbfb0cb6abafbcf56bc9ac73cedc6c805252a855`
  - default branch: `master`
  - license: no license file observed in static root check
  - posture: `pattern-only`
  - absorbed pattern: `trope_source_boundary_review`
  - runtime exclusion: no parser execution or page fetching

## Fusion Decision

These sources are not imported as tools. They are fused into MuMuAINovel as
review gates for inspired writing and continuation prompts.

New pattern pack fields:

- `trope_inventory_similarity_gate_hints`
- `trope_graph_expectation_map_hints`
- `trope_density_novelty_budget_hints`
- `trope_source_boundary_review_hints`

New continuation / inspired prompt section:

- `Trope independence audit`

## Local Adaptation

- Same-type writing may share genre-level tropes.
- A draft is blocked when the rare trope vector, trope adjacency chain, or
  trope timing mirrors one source work without new cast, setting, stakes,
  causal order, and payoff.
- Trope labels stay metadata. Source page prose, crawled text, and parser dumps
  do not enter prompts.
- Trope density is treated as a cliche pressure signal; saturated clusters need
  a local twist, inversion, shifted cost, or new consequence.

## Verification Target

- Classification maps the reviewed sources into trope independence patterns.
- Pattern pack digest exposes the four trope hint groups.
- Continuation and same-type creation context blocks render the trope audit.
- Default discovery includes the reviewed explicit GitHub sources and search
  queries.
