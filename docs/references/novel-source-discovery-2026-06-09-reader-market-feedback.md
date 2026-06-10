# Novel Source Discovery - 2026-06-09 Reader / Market Feedback

## Scope

Static source intake for reader feedback, market-position, review-signal, and
chapter engagement patterns that can improve MuMuAINovel continuation and
same-type creation.

No external repository was cloned, installed, executed, or imported. No dataset,
review body, scraper, browser automation, model provider, Docker stack, or API
credential was used.

## Sources

- `zygmuntz/goodbooks-10k` ? HEAD `6dd165b555a7b47b2dd36743a425776e641ff50c`; public README/root metadata only.
- `MengtingWan/goodreads` ? HEAD `e8205dd0622fd3ba09b3ad8901f4f04fbbb75d8e`; public README/root metadata only.
- `maria-antoniak/goodreads-scraper` ? HEAD `e1b1e86595bf30bde098008b9b75b56831ec0d9c`; public README/root metadata only.
- `Ckokoski/authorclaw` ? HEAD `6573d230ee8a4ee8e78a68e1c06c3f288afd6ee1`; public README/root/tree snippets only.
- `f5alcon/The-Novelists-Atelier` ? HEAD `e00560021c9773edad7cd745bbf5384bbdb45eab`; public README/prompt/security metadata only.

## Absorbed Patterns

### reader_rating_signal_model

Use ratings, to-read markers, shelves, and tags as aggregate reader-expectation
signals. In MuMuAINovel this becomes calibration metadata for promise, subgenre,
mood, and audience expectation. It is not canon and cannot override the author or
confirmed book bible.

### review_spoiler_sentiment_corpus

Cluster review-like feedback into praise, complaints, trope requests, comp
suggestions, sentiment drift, and spoiler-sensitive issues. Store opaque ids and
aggregate labels only. Do not paste review text into prompts or marketing copy.

### beta_reader_archetype_panel

Run simulated reader perspectives as early-warning review: genre fan, casual
reader, critical reader, and sensitivity reader. Capture tension, pacing,
want-to-continue, confusion, favorite moment, stumble point, and emotions per
chapter. This supplements but does not replace real human feedback.

### comp_title_market_positioning

Use comparable titles to calibrate audience promise, tone, trope expectation,
market gap, and positioning copy constraints. For same-type creation, transform
comp signals into a new premise, cast, conflict, setting, and hook promise.

### local_reader_experience_editor

Audit micro-tension, reader curiosity, chapter hook, cliffhanger, scene
openings/endings, paragraph rhythm, Style DNA fit, and token/context breakdown
before expensive full-manuscript review.

## MuMuAINovel Integration

- `source_discovery_service.py` now discovers and packs reader/market feedback
  patterns.
- `source_pattern_pack_prompt.py` now renders the new hint keys.
- `book_remix_context_service.py` now injects `Reader market feedback audit`
  into continuation and same-type creation contexts.
- Tests cover classification, pattern-pack hint rendering, default sources, and
  prompt audit rendering.

## Runtime Gates

- Pattern-only.
- No Goodreads dataset download.
- No scraper execution.
- No review text ingestion.
- No browser automation.
- No provider/model call.
- No external runtime code import.

## Frontend surfacing addendum - 2026-06-10

Fresh public `git ls-remote --symref HEAD` check ran on
2026-06-10 19:16 +08:00 and was stored only under
`tmp/source-intake-reader-market-2026-06-10/head-manifest.json`.

Observed HEADs:

- `zygmuntz/goodbooks-10k`: `6dd165b555a7b47b2dd36743a425776e641ff50c`
- `MengtingWan/goodreads`: `e8205dd0622fd3ba09b3ad8901f4f04fbbb75d8e`
- `maria-antoniak/goodreads-scraper`:
  `e1b1e86595bf30bde098008b9b75b56831ec0d9c`
- `Ckokoski/authorclaw`: `6573d230ee8a4ee8e78a68e1c06c3f288afd6ee1`
- `f5alcon/The-Novelists-Atelier`:
  `e00560021c9773edad7cd745bbf5384bbdb45eab`

Project integration delta:

- `BookRemixSourceDiscoveryPanel.tsx` now includes these repositories in the
  default public GitHub seed list.
- The source-discovery UI now pins `Reader feedback / market positioning gates`
  for reader retention, rating/tag signals, spoiler-aware review clusters,
  beta-reader archetypes, comp-title positioning, and local reader-experience
  editing.
- `sourceDiscovery.ts` exposes the corresponding pattern-pack fields so
  same-type creation can separate market expectation from canon mutation.

Runtime boundary is unchanged: no Goodreads data download, review scraping,
browser automation, provider call, review-text ingestion, or external runtime
code import was performed.
