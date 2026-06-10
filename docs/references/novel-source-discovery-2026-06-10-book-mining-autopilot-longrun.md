# Novel Source Discovery - 2026-06-10 Book Mining / Autopilot / Longrun

## Scope

Static source-intake pass for MuMuAINovel book-deconstruction, continuation, and same-type writing workflows.

No external repository was cloned, installed, executed, or imported. Review used public GitHub metadata, `git ls-remote` HEAD checks, raw README/LICENSE snippets, and GitHub tree metadata only.

## Promoted sources

### `cchheerrss/ai-novel-trilogy`

- URL: https://github.com/cchheerrss/ai-novel-trilogy
- Observed HEAD: `c5e533b36a0bf913e03a51e536322a51d0d52a02`
- License: MIT
- Family: novel automation / book-mining / genesis / continuation pipeline
- Posture: pattern-only
- Static evidence:
  - README describes a three-system lifecycle: book mining, novel genesis, then novel automation.
  - Public tree exposes `book-mining/`, `novel-genesis/`, `novel-automation/`, pattern libraries, canon-seed handoff, and automation gate files.
- Absorbed pattern:
  - `book_mining_genesis_automation_gate`
- Local adaptation:
  - Split source-book deconstruction from new-book canon.
  - Keep pattern library, concept scoring, canon seed, and automation gate decisions as separate artifacts.
  - Source mining notes stay reference-only; only accepted canon seed fields can drive chapter automation.

### `zhitongblog/novel-studio`

- URL: https://github.com/zhitongblog/novel-studio
- Observed HEAD: `df15dde3d618c2704de530e0d2654046c3ce716f`
- License: MIT
- Family: multi-book webnovel studio / autopilot orchestration
- Posture: pattern-only / runtime-deferred
- Static evidence:
  - README describes multi-book longform writing, per-book Unterm profile isolation, Codex/Claude/Gemini CLI orchestration, autopilot continuation, stop limits, and periodic full-book logic checks.
  - Public tree contains desktop/Tauri, CLI, MCP, model, and autopilot surfaces.
- Absorbed pattern:
  - `multi_book_autopilot_studio_gate`
- Local adaptation:
  - Add per-book profile boundary and context namespace checks.
  - Autopilot must have visible continue limits, stop phrases, manual stop, and periodic full-book logic review.
  - MCP, Tauri, npm, local auth-token, and CLI runtime surfaces remain excluded from intake.

### `DinhLucent/webnovel-longrun-aigen-docs`

- URL: https://github.com/DinhLucent/webnovel-longrun-aigen-docs
- Observed HEAD: `e98081c825ecd8762a0254f4d5bf4692e53fefcf`
- License: GPL-3.0
- Family: long-running webnovel memory / commit projection docs
- Posture: pattern-only
- Static evidence:
  - README describes `.story-system` as source of truth, accepted chapter commits, event/entity extraction, `.webnovel` read-model projections, RAG/query router, memory scratchpad, and read-only dashboard.
  - Public tree is docs-only except license and architecture asset.
- Absorbed pattern:
  - `longrun_commit_projection_health_gate`
- Local adaptation:
  - Accepted chapter commit is the boundary for prose, events, entities, summaries, and memory updates.
  - Source-of-truth files and read-model projections must be separated with freshness checks.
  - Dashboard/read-model surfaces are observational, not canon write surfaces.

## 2026-06-10 reader reward / tri-modal audit addendum

Static pass added two public GitHub sources for the next拆书续写 / 同类型仿写 quality loop.

### `haowjy/creative-writing-skills`

- URL: https://github.com/haowjy/creative-writing-skills
- Observed HEAD: `81fa0be02eeb985404bb3ffc361e62dcba0385e6`
- License: Apache-2.0
- Family: creative-writing skill pack / reader-response review / project knowledge maintenance
- Posture: pattern-only
- Static evidence:
  - README describes muse-led exploration, writer/critic/revision-writer loops, reader-sim feedback, continuity checking, style reference creation, and chronicler knowledge-base updates.
  - Public metadata confirms an external plugin / skill runtime surface, so no skill files, zip files, marketplace commands, or agents were installed or imported.
- Absorbed pattern:
  - `reader_reward_channel_gate`
- Local adaptation:
  - Review pivotal scenes on separate reader channels: immersion/transportation, prose aesthetics, social-simulation believability, and flow.
  - Treat reader-sim output as diagnostic evidence only; confusion or boredom becomes a bounded revision task, not an automatic rewrite.
  - For同类型仿写, require reader reward and independence evidence together.

### `jblemee/bmad-book-builder`

- URL: https://github.com/jblemee/bmad-book-builder
- Observed HEAD: `678c13f61a39f672308e920333709ade08829502`
- License: WTFPL
- Family: AI-assisted novel workflow module / chapter audit chain
- Posture: pattern-only
- Static evidence:
  - README describes 8 specialized agents, 17 workflows, Create/Edit/Validate modes, a pre-writing checklist, quantitative style metrics, automated post-chapter audits, living-bible update, character audits, theme tracking, rhythm analysis, and reality checks.
  - Public metadata confirms BMAD CLI / custom module install surface, so no CLI, npm installer, local module, workflow file, or agent runtime was installed or imported.
- Absorbed pattern:
  - `tri_modal_workflow_validation_gate`
- Local adaptation:
  - Declare workflow mode before any mutation: Create, Edit, or Validate.
  - Run pre-writing checklist before drafting.
  - After chapter acceptance, run review -> bible/state update -> character audit -> theme/rhythm audit -> next-chapter handoff.

## Deferred / duplicate sources

- `Saemer2023/webnovel-writer-opencode`: overlaps with existing `lujih/webnovel-writer-opencode`; useful as sibling evidence only. GPL/runtime installer surface keeps it pattern-only and not newly promoted.
- `SageAutoman/novel-control-station-openclaw-skill`: overlaps existing `jingtai123/Novel-Control-Station-Skill`; OpenClaw adaptation confirms one-chapter-at-a-time/writeback boundaries but does not require a new gate.
- `njacknot/novelist-skill`: useful skill-pack signal for chapter-control/professional mode, but install scripts and overlap with existing Chinese novelist skills keep it deferred for a later focused skill-pack pass.

## New workflow gates

### `book_mining_genesis_automation_gate`

Use when the system has source-book deconstruction or same-type writing inputs.

Rules:

- Mine source books into abstract pattern entries only.
- Run concept/genesis scoring before automation.
- Emit canon seed as the only handoff into chapter production.
- Keep source patterns, market notes, canon seed, and automation state in separate namespaces.

### `multi_book_autopilot_studio_gate`

Use when a writing session can run multiple books or unattended batches.

Rules:

- Bind every run to one book profile and context namespace.
- Require continue count, completion phrases, manual stop, and question-answer policy before autopilot.
- Insert periodic full-book logic checks before further unattended continuation.

### `longrun_commit_projection_health_gate`

Use when long-running continuation depends on derived state, summary, RAG, or dashboard projections.

Rules:

- Accepted chapter commit is the state mutation boundary.
- Derived projections must trace to the latest accepted commit.
- Stale projections or mixed source/new canon memory block next-chapter generation.

### `reader_reward_channel_gate`

Use when a continuation or same-type draft needs reader-facing quality feedback.

Rules:

- Score pivotal scenes on reader reward channels separately.
- Convert reader-sim issues into scoped revision tasks.
- Never let source resemblance count as reader pull in同类型仿写.

### `tri_modal_workflow_validation_gate`

Use when a workflow can create, edit, or validate bible / plan / chapter state.

Rules:

- Create, Edit, and Validate have different write permissions.
- Pre-writing checklist gates chapter drafting.
- Post-chapter audit chain gates canon/state write-back.

## Artifacts updated

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `frontend/src/types/sourceDiscovery.ts`
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/tests/frontend/test_source_discovery_panel_copy.py`
- `backend/app/references/novel-source-pattern-pack-2026-06-10.json`

## Runtime exclusions

- No clone.
- No package manager.
- No scripts or installers.
- No Tauri, MCP, CLI, browser, provider, local model, or dashboard runtime.
- No source prose, pattern library body, or prompt file copied into runtime.

## Scene promise / serial simulation review addendum - 2026-06-10

This addendum records a public GitHub metadata + raw README/static file review pass for additional fiction-writing, webnovel, simulation, and manuscript-review sources. No external project was cloned, installed, built, launched, or executed. Scratch evidence was saved under `tmp/source-intake-*` only.

### Reviewed sources

- `Deland78/Claude-Writing-Skills`
  - URL: `https://github.com/Deland78/Claude-Writing-Skills`
  - observed HEAD: `e8f2a83ccf47e279e9c980b6765d92fda7c5d55e`
  - license: no license detected from public metadata
  - static evidence: README, `docs/mob_protocol.md`, `.claude/skills/scene-architect/SKILL.md`, tree metadata
  - absorbed pattern: `scene_promise_mob_review_gate`
  - reusable lesson: chapter promise -> scene cards -> draft -> cited mob review -> accepted canon commit. Specialist comments are queued one at a time and require citations/author resolution before they may mutate bible, relationships, timeline, or chapter plan.
  - runtime exclusion: Claude hooks, shell scripts, skill files, agents, and command protocols are not imported or executed.

- `netflypsb/webnovel-mcp`
  - URL: `https://github.com/netflypsb/webnovel-mcp`
  - observed HEAD: `7fd8ce5b9a061a8f49a435a5f36d10430af3b4be`
  - license: MIT
  - static evidence: README, `webnovel-author/SKILL.md`, `style-guide.md`, tree metadata
  - absorbed pattern: `webnovel_genre_tracker_gate`
  - reusable lesson: serial fiction needs explicit project structure plus genre-specific trackers for foreshadowing, timeline, LitRPG stats/inventory/quests, romance stages, cliffhanger rotation, stale characters, and chapter gaps.
  - runtime exclusion: uvx/pip install, MCP server launch, marketplace/license-key paths, and MCP tool calls are not executed.

- `hackertaco/novel-generator`
  - URL: `https://github.com/hackertaco/novel-generator`
  - observed HEAD: `eeac60fe9e41c144004a81f4764988f573188755`
  - license: no license detected from public metadata
  - static evidence: README, `docs/novel-engine-cli-library-parity.md`, tree metadata
  - absorbed pattern: `simulation_causal_ledger_verification_gate`
  - reusable lesson: long-form generation should advance world truth, character memory, belief state, utterance history, causal ledger, chapter summaries, and run metadata together, then verify long-horizon contradictions before accepting autopilot output.
  - runtime exclusion: npm/tsx scripts, provider calls, env files, Python legacy CLI, web routes, and API wrappers are not executed.

- `eristoddle/git-write`
  - URL: `https://github.com/eristoddle/git-write`
  - observed HEAD: `adf28c6f1bdd99fd1bdd95479b2f72413c9ebc4c`
  - license: MIT
  - static evidence: README, `docs/USER_GUIDE.md`, tree metadata
  - absorbed pattern: `writer_git_exploration_review_gate`
  - reusable lesson: risky rewrites should be treated as explorations/branches with word-level review, author-controlled accept/reject/modify decisions, beta-reader annotation provenance, and replayable merge history.
  - runtime exclusion: pip/poetry/npm install, Docker/compose, deploy scripts, API server, web app, and demo credentials are not used.

### Local projection

The pattern pack now exposes these additional prompt-safe hint fields:

- `scene_promise_mob_review_gate_hints`
- `webnovel_genre_tracker_gate_hints`
- `simulation_causal_ledger_verification_gate_hints`
- `writer_git_exploration_review_gate_hints`

These fields are static source-derived gates only. They do not authorize any upstream runtime, MCP server, package installation, provider call, browser/desktop control, or external account mutation.

## Narrative QA / summary / causality addendum - 2026-06-10

This addendum records a public GitHub HEAD + raw README/LICENSE static-review pass for narrative comprehension, long-form summary alignment, story QA, why-explanation, commonsense psychology, and query-focused long-summary sources. No external project was cloned, installed, built, launched, or executed. Scratch evidence was saved under `tmp/source-intake-narrative-qa-2026-06-10` only.

### Reviewed sources

- `google-deepmind/narrativeqa`
  - URL: `https://github.com/google-deepmind/narrativeqa`
  - observed HEAD: `904246f6d1fe99a99a08a03501fe3e619af2cee5`
  - license: Apache-2.0
  - static evidence: README, LICENSE
  - absorbed pattern: `narrative_qa_comprehension_gate`
  - reusable lesson:拆书 output should include evidence-backed questions and answers across plot, motive, relationships, setting rules, and unresolved hooks before it can feed续写.
  - runtime exclusion: story downloads, `download_stories.sh`, compare scripts, and corpus files are not executed or imported.

- `salesforce/booksum`
  - URL: `https://github.com/salesforce/booksum`
  - observed HEAD: `df178bf574cba106e6b5f71b5aafdcd488452798`
  - license: BSD-3-Clause
  - static evidence: README, LICENSE.txt
  - absorbed pattern: `chapter_summary_alignment_gate`
  - reusable lesson: paragraph-, chapter-, arc-, and book-level summaries need separate validation so long-form causal and temporal dependencies are not lost during context compression.
  - runtime exclusion: GCP downloads, summary collection scripts, datasets, and model baselines are not executed.

- `uci-soe/FairytaleQAData`
  - URL: `https://github.com/uci-soe/FairytaleQAData`
  - observed HEAD: `a24ddc17364666b7c13a425b9970c87368b03417`
  - license: Apache-2.0
  - static evidence: README, LICENSE
  - absorbed pattern: `story_question_answer_validation_gate`
  - reusable lesson: scene or section QA should ground answers to exact section/chapter evidence and narrative elements instead of accepting plausible genre guesses.
  - runtime exclusion: starter scripts, notebooks, HuggingFace loaders, and story/QA data are not executed or imported.

- `StonyBrookNLP/tellmewhy`
  - URL: `https://github.com/StonyBrookNLP/tellmewhy`
  - observed HEAD: `22ee9a0804f80b22d1afe45885243e059ca5206d`
  - license: no license detected from static README/LICENSE fetch
  - static evidence: README
  - absorbed pattern: `causal_why_explanation_gate`
  - reusable lesson: major character actions need why-answers grounded in prior events, belief state, pressure, and helpful sentence/chapter evidence; unsupported motives become reveal debt or revision tasks.
  - runtime exclusion: Google Drive downloads, HuggingFace dataset loading, evaluation scripts, and model tasks are not executed.

- `uwnlp/storycommonsense`
  - URL: `https://github.com/uwnlp/storycommonsense`
  - observed HEAD: `c8cb91b75b79925949fb2f0e564b58c198da11de`
  - license: no license detected from static README/LICENSE fetch
  - static evidence: README
  - absorbed pattern: `story_commonsense_consistency_gate`
  - reusable lesson:续写 should maintain a naive-psychology ledger for motivation, emotion, belief, desire, and likely reaction so character actions do not jump without on-page cause.
  - runtime exclusion: datasets, model code, project website workflows, and external loaders are not executed.

- `nyu-mll/SQuALITY`
  - URL: `https://github.com/nyu-mll/SQuALITY`
  - observed HEAD: `dc08d4f574639d773bc64ef3ab3527043108fb4e`
  - license: mixed data terms noted in README
  - static evidence: README
  - absorbed pattern: `query_focused_long_summary_gate`
  - reusable lesson: long-context summaries should be query-focused, with separate plot, character, relationship, and world-rule summaries plus disagreement notes before compression.
  - runtime exclusion: data files, training scripts, Project Gutenberg story consumption, and model baselines are not executed.

### Local projection

The pattern pack now exposes these additional prompt-safe hint fields:

- `narrative_qa_comprehension_gate_hints`
- `chapter_summary_alignment_gate_hints`
- `story_question_answer_validation_gate_hints`
- `causal_why_explanation_gate_hints`
- `story_commonsense_consistency_gate_hints`
- `query_focused_long_summary_gate_hints`

These fields are static source-derived gates only. They do not authorize any upstream dataset download, script execution, model training/evaluation, package installation, provider call, browser/desktop control, or external account mutation.

## Rights / corpus / entity leakage addendum - 2026-06-10

This addendum records a public GitHub HEAD + raw README/LICENSE static-review pass for source rights admission, SPDX / REUSE metadata, public-domain corpus boundaries, entity redaction, custom NER labels, placeholder consistency, and proper-noun leakage review. No external project was cloned, installed, built, launched, or executed. Scratch evidence was saved under `tmp/source-intake-rights-entity-2026-06-10` only.

### Reviewed sources

- `licensee/licensee`
  - URL: `https://github.com/licensee/licensee`
  - observed HEAD: `dad4bb434b80a3d86bf9660f0db0e622a4d5d087`
  - license: MIT
  - static evidence: LICENSE metadata and public repository metadata
  - absorbed pattern: `source_license_detection_gate`
  - reusable lesson: source-book import,拆书,续写, and同类型仿写 need a license confidence record before any long source text enters prompts.
  - runtime exclusion: Ruby gems, package install, license scanner execution, and repository scan commands are not executed.

- `fsfe/reuse-tool`
  - URL: `https://github.com/fsfe/reuse-tool`
  - observed HEAD: `20e2e152790022891d67f1074c6dbce0494ad7cd`
  - license: Apache-2.0
  - static evidence: README
  - absorbed pattern: `spdx_reuse_compliance_gate`
  - reusable lesson: SPDX ids and file-level copyright/attribution fields belong in a source manifest, not inside prose-generation prompts.
  - runtime exclusion: Python package install, REUSE command execution, and repository linting are not executed.

- `spdx/license-list-data`
  - URL: `https://github.com/spdx/license-list-data`
  - observed HEAD: `421fbabbe80c94c58c12316af1bc6a2dca2362bc`
  - license: no license detected from static README/LICENSE fetch
  - static evidence: README
  - absorbed patterns: `spdx_reuse_compliance_gate`, `attribution_derivative_work_gate`
  - reusable lesson: normalize source rights to stable license ids and keep attribution / derivative-use review as an admission gate before同类型仿写.
  - runtime exclusion: generated license data tooling, build scripts, and package workflows are not executed.

- `c-w/Gutenberg`
  - URL: `https://github.com/c-w/Gutenberg`
  - observed HEAD: `123d13435b31a39f6fda3c4df2976a40f74633a1`
  - license: Apache-2.0
  - static evidence: README, LICENSE
  - absorbed pattern: `public_domain_corpus_boundary`
  - reusable lesson: public-domain metadata still needs title, author, edition/source URL, observed date, extraction format, and jurisdiction notes before it can feed拆书.
  - runtime exclusion: corpus parsing, downloads, and API/client code are not executed.

- `Imkun-on/gutenberg-corpus-cli`
  - URL: `https://github.com/Imkun-on/gutenberg-corpus-cli`
  - observed HEAD: `8bf8ca7260a0a3c1c233a30eb629771beea9639e`
  - license: MIT
  - static evidence: README, LICENSE
  - absorbed pattern: `public_domain_corpus_boundary`
  - reusable lesson: corpus downloader output is not drafting context by default; downloader use needs a separate runtime and rights review gate.
  - runtime exclusion: CLI install, text downloads, full-text search build, parallel download jobs, and corpus generation are not executed.

- `microsoft/presidio`
  - URL: `https://github.com/microsoft/presidio`
  - observed HEAD: `83ab7eb85609c49d9b0b17c44b5c025575966876`
  - license: MIT
  - static evidence: LICENSE and public repository metadata
  - absorbed patterns: `source_entity_redaction_gate`, `placeholder_alias_consistency_map`
  - reusable lesson: source-specific names, places, factions, artifacts, powers, titles, and other proper nouns should be redacted into stable placeholders before同类型仿写.
  - runtime exclusion: Docker, analyzer/anonymizer services, package install, NLP runtime, API server, and sample execution are not used.

- `LeapBeyond/scrubadub`
  - URL: `https://github.com/LeapBeyond/scrubadub`
  - observed HEAD: `53772cbef417da290d25c95373031f786ab3b5c6`
  - license: Apache-2.0
  - static evidence: README, LICENSE
  - absorbed patterns: `source_entity_redaction_gate`, `placeholder_alias_consistency_map`
  - reusable lesson: redaction needs detector output, placeholder id, replacement policy, collision review, and reviewer decision trace.
  - runtime exclusion: Python install, detectors, replacers, and text-processing runtime are not executed.

- `urchade/GLiNER`
  - URL: `https://github.com/urchade/GLiNER`
  - observed HEAD: `3ddf1689ed4ae6544f0e904c447f5dd9d2bb7ca3`
  - license: Apache-2.0
  - static evidence: README, LICENSE
  - absorbed patterns: `custom_entity_label_inventory`, `proper_noun_leakage_review`
  - reusable lesson: fiction needs custom entity labels beyond PERSON / ORG / LOC, including faction, rank, artifact, power, species, title, invented term, and relationship label.
  - runtime exclusion: model download, inference, notebook/script execution, and package install are not executed.

- `explosion/spaCy`
  - URL: `https://github.com/explosion/spaCy`
  - observed HEAD: `e67199550e365dacee28b109210c3a43e1477638`
  - license: MIT
  - static evidence: README, LICENSE
  - absorbed patterns: `custom_entity_label_inventory`, `proper_noun_leakage_review`
  - reusable lesson: proper-noun leakage review should compare drafts against source blocklists plus approved exception lists before chapter acceptance.
  - runtime exclusion: model download, pipeline execution, package install, and NLP runtime are not executed.

### Local projection

The source discovery panel now pins these prompt-safe fields instead of leaving them only in the dynamic fallback group:

- `source_license_detection_gate_hints`
- `spdx_reuse_compliance_gate_hints`
- `public_domain_corpus_boundary_hints`
- `attribution_derivative_work_gate_hints`
- `source_entity_redaction_gate_hints`
- `custom_entity_label_inventory_hints`
- `placeholder_alias_consistency_map_hints`
- `proper_noun_leakage_review_hints`

These fields are static source-derived admission gates only. They do not authorize corpus download, scanner execution, NER/model inference, package installation, Docker/service launch, provider call, browser/desktop control, external account mutation, or importing source prose into prompts.

## Source import / EPUB QA addendum - 2026-06-10

This addendum records a public GitHub HEAD + raw README/LICENSE static-review pass for ebook import, PDF layout extraction, OCR, document partitioning, provenance checksums, EPUB conformance, accessibility, front/back matter, and navigation QA. No external project was cloned, installed, built, launched, or executed. Scratch evidence was saved under `tmp/source-intake-source-import-ebook-2026-06-10` only.

### Reviewed sources

- `aerkalov/ebooklib`
  - URL: `https://github.com/aerkalov/ebooklib`
  - observed HEAD: `a50289fb9d4039224d54bf7d92698eb03cd68254`
  - static evidence: README
  - absorbed pattern: `source_format_import_manifest`
  - reusable lesson:拆书 import needs a source-format manifest with EPUB/OPF/spine/TOC/metadata evidence before chapter boundaries feed analysis.
  - runtime exclusion: Python package install, EPUB parsing, and conversion code are not executed.

- `pdfminer/pdfminer.six`
  - URL: `https://github.com/pdfminer/pdfminer.six`
  - observed HEAD: `a18de2a9c479b4c847538500017b449ddaec177e`
  - static evidence: README
  - absorbed pattern: `pdf_layout_text_extraction_gate`
  - reusable lesson: PDF拆书 should preserve page span, reading order, text block, and layout-gap findings instead of treating extracted text as already clean chapters.
  - runtime exclusion: Python package install and PDF extraction are not executed.

- `pymupdf/PyMuPDF`
  - URL: `https://github.com/pymupdf/PyMuPDF`
  - observed HEAD: `d981d87e87924962f7975dc2ed746e6c627e6cf6`
  - static evidence: README
  - absorbed pattern: `pdf_layout_text_extraction_gate`
  - reusable lesson: page-coordinate extraction can support reviewer-visible boundary evidence for source chapters, quotes, images, and missing text gaps.
  - runtime exclusion: package install, PDF/image extraction, and native bindings are not executed.

- `ocrmypdf/OCRmyPDF`
  - URL: `https://github.com/ocrmypdf/OCRmyPDF`
  - observed HEAD: `5cb5d7a682095700aa28eb592a94c0fe28e94fd0`
  - static evidence: README
  - absorbed pattern: `ocr_scanned_page_import_gate`
  - reusable lesson: scanned-source import needs OCR confidence, hOCR/text-layer evidence, manual review items, and page-level uncertainty before it can feed续写 context.
  - runtime exclusion: OCR pipeline, Tesseract calls, package install, and file mutation are not executed.

- `tesseract-ocr/tesseract`
  - URL: `https://github.com/tesseract-ocr/tesseract`
  - observed HEAD: `f4afb2cc9545f622a07812b09e1b72fc78f85a64`
  - static evidence: README
  - absorbed pattern: `ocr_scanned_page_import_gate`
  - reusable lesson: OCR text from images should be labeled as uncertain source evidence until confidence and manual review pass.
  - runtime exclusion: native build, model data download, OCR execution, and image processing are not executed.

- `Unstructured-IO/unstructured`
  - URL: `https://github.com/Unstructured-IO/unstructured`
  - observed HEAD: `dedf144192347a89bb70ddc8a896eeeaa7440be0`
  - static evidence: README
  - absorbed pattern: `document_partition_chapter_detection_gate`
  - reusable lesson: document partitioning should output element sequence, title/heading confidence, chapter candidates, and rejected boundary evidence.
  - runtime exclusion: package install, partition pipelines, model/runtime services, and external API calls are not executed.

- `jgm/pandoc`
  - URL: `https://github.com/jgm/pandoc`
  - observed HEAD: `912bfa5e2e3f5c74eb125dfc19404f67c61ca58b`
  - static evidence: README
  - absorbed pattern: `import_provenance_checksum_gate`
  - reusable lesson: format conversion should record input artifact, parser/converter version, settings, output checksum, and conversion log before source text is trusted.
  - runtime exclusion: binary execution, document conversion, package install, and filter execution are not used.

- `w3c/epubcheck`
  - URL: `https://github.com/w3c/epubcheck`
  - observed HEAD: `82b174ec319ea3e6c9d2488f84155fa4a9171fc2`
  - static evidence: README
  - absorbed patterns: `epub_structure_validation_gate`, `toc_navigation_consistency_gate`
  - reusable lesson: EPUB output should validate OPF manifest, spine, media types, navigation document, heading hierarchy, and reader navigation before release.
  - runtime exclusion: Java/runtime execution, validator execution, and build tooling are not used.

- `daisy/ace`
  - URL: `https://github.com/daisy/ace`
  - observed HEAD: `dfa87b528f598a034f98e8a3126bf4b5bf9203bf`
  - static evidence: README
  - absorbed pattern: `ebook_accessibility_audit_gate`
  - reusable lesson: exported books need accessibility metadata, alt text, landmarks, reading-order notes, and hazard review separate from prose quality.
  - runtime exclusion: npm install, accessibility checker execution, and browser/runtime tooling are not executed.

- `standardebooks/tools`
  - URL: `https://github.com/standardebooks/tools`
  - observed HEAD: `89e81b956216d3ddf49f5fd0b397847b711b0aa7`
  - static evidence: README
  - absorbed pattern: `front_back_matter_metadata_gate`
  - reusable lesson: front matter, back matter, title page, colophon, endnotes, author/source metadata, and identifiers must be regenerated from the transformed book.
  - runtime exclusion: tools install, build commands, lint commands, and publication workflows are not executed.

- `Sigil-Ebook/Sigil`
  - URL: `https://github.com/Sigil-Ebook/Sigil`
  - observed HEAD: `79ca6771be61305673b9123c8c0a0ee74bd044ee`
  - static evidence: README
  - absorbed pattern: `toc_navigation_consistency_gate`
  - reusable lesson: a reviewer-visible book browser / manifest / spine / TOC model helps catch navigation drift between chapter files and packaged ebook output.
  - runtime exclusion: desktop app, installers, native build, and EPUB editing runtime are not executed.

- `w3c/epub-tests`
  - URL: `https://github.com/w3c/epub-tests`
  - observed HEAD: `45feac979d9b12b502f124db7bc5056977628417`
  - static evidence: README
  - absorbed pattern: `epub_structure_validation_gate`
  - reusable lesson: EPUB validation should treat conformance as a separate gate from manuscript acceptance and preserve a failure category report.
  - runtime exclusion: test suite execution, package workflows, and reading-system tests are not executed.

- `daisy/epub-accessibility-tests`
  - URL: `https://github.com/daisy/epub-accessibility-tests`
  - observed HEAD: `6ecadf3393083dd93fa79d8b62e0281957a7b05e`
  - static evidence: README
  - absorbed pattern: `ebook_accessibility_audit_gate`
  - reusable lesson: accessibility fixtures should become a release checklist for metadata, semantics, navigation, and reader-facing hazards, not drafting instructions.
  - runtime exclusion: accessibility test execution, reading-system runtime, and package workflows are not executed.

### Local projection

The source discovery panel now pins these prompt-safe fields instead of leaving them only in the dynamic fallback group:

- `source_format_import_manifest_hints`
- `pdf_layout_text_extraction_gate_hints`
- `ocr_scanned_page_import_gate_hints`
- `document_partition_chapter_detection_gate_hints`
- `import_provenance_checksum_gate_hints`
- `epub_structure_validation_gate_hints`
- `ebook_accessibility_audit_gate_hints`
- `front_back_matter_metadata_gate_hints`
- `toc_navigation_consistency_gate_hints`

These fields are static source-derived import and publication gates only. They do not authorize package installation, document conversion, OCR execution, PDF/EPUB parsing, validator runs, desktop app launch, native build, external API calls, provider calls, or importing source prose into prompts without the existing rights and entity-leakage gates.

## Longform generation / benchmark / co-writing addendum - 2026-06-10

This addendum records a public GitHub HEAD + raw README static-review pass for
ultra-long writing, reward/ruler gates, creative-writing benchmarks, human story
metrics, co-writing scaffolds, recursive revision, persona/dialogue memory, and
event-to-sentence realization. No external project was cloned, installed, built,
launched, or executed. Scratch evidence was saved under
`tmp/source-intake-longform-eval-cowriting-2026-06-10` only.

### Reviewed sources

- `THUDM/LongWriter`
  - URL: `https://github.com/THUDM/LongWriter`
  - observed HEAD: `447539b356a8b09760b51eca876e19b6fc1f2dd7`
  - static evidence: README
  - absorbed patterns: `agentwrite_plan_write_pipeline`, `long_output_length_quality_ruler`
  - reusable lesson: 长篇续写 should separate planning artifacts from writing artifacts, then score length, completeness, and long-output quality before accepting a batch.
  - runtime exclusion: Python package install, model scripts, data construction, and evaluation runs are not executed.

- `THUDM/LongReward`
  - URL: `https://github.com/THUDM/LongReward`
  - observed HEAD: `c56577876cff75a963c90b3551df952f095b4c06`
  - static evidence: README
  - absorbed pattern: `long_context_reward_dimension_gate`
  - reusable lesson: long-context chapters need separate helpfulness, logicality, faithfulness, and completeness checks rather than one opaque quality score.
  - runtime exclusion: scorer runtime, package install, model loading, and benchmark execution are not used.

- `THU-KEG/LongWriter-V`
  - URL: `https://github.com/THU-KEG/LongWriter-V`
  - observed HEAD: `ea87eb2af54731375f1384c5fbb961fc1e860820`
  - static evidence: README
  - absorbed patterns: `agentwrite_plan_write_pipeline`, `long_output_length_quality_ruler`
  - reusable lesson: multimodal/long-output writing should preserve outline, chapter plan, and ruler evidence as review artifacts before prose enters续写 context.
  - runtime exclusion: VLM agents, package install, model calls, and evaluation scripts are not executed.

- `X-PLUG/WritingBench`
  - URL: `https://github.com/X-PLUG/WritingBench`
  - observed HEAD: `ae2d5176449b7b769815482641d35926f26793eb`
  - static evidence: README
  - absorbed patterns: `instance_specific_writing_criteria_gate`, `material_grounded_query_refinement`
  - reusable lesson: 仿写/续写 review should attach per-instance criteria and material-grounded requirement notes, not reuse a generic scoring rubric for every book.
  - runtime exclusion: benchmark data generation, prompt scripts, model calls, and package install are not executed.

- `EQ-bench/creative-writing-bench`
  - URL: `https://github.com/EQ-bench/creative-writing-bench`
  - observed HEAD: `13fc250dbff26317d9367601002906e8bb096c09`
  - static evidence: README
  - absorbed patterns: `hybrid_rubric_pairwise_elo_judge`, `judge_bias_mitigation_check`
  - reusable lesson: creative-writing judges need hybrid rubric plus pairwise comparison evidence, with explicit bias checks for length, order, verbosity, and incoherent flourish.
  - runtime exclusion: pairwise judge runtime, scoring scripts, package install, and model calls are not used.

- `EQ-bench/longform-writing-bench`
  - URL: `https://github.com/EQ-bench/longform-writing-bench`
  - observed HEAD: `34f60a028c3f973c19cde98dc5a9e8f9875a87e3`
  - static evidence: README
  - absorbed pattern: `plan_reflect_character_chapter_pipeline`
  - reusable lesson: longform review should preserve brainstorm, plan, reflection, character profile, chapter output, and consistency checks as one traceable pipeline.
  - runtime exclusion: benchmark execution, prompt execution, package install, and model calls are not used.

- `dig-team/hanna-benchmark-asg`
  - URL: `https://github.com/dig-team/hanna-benchmark-asg`
  - observed HEAD: `282f27536a5d05ad4ce14298abcd70c45668fed2`
  - static evidence: README
  - absorbed pattern: `human_story_metric_panel`
  - reusable lesson: generated-story review should expose relevance, coherence, empathy, surprise, engagement, and complexity as separate human-facing metrics.
  - runtime exclusion: dataset import, metric execution, package install, and model scoring are not used.

- `google-deepmind/dramatron`
  - URL: `https://github.com/google-deepmind/dramatron`
  - observed HEAD: `2e7c36afadacf8321b77a468940024371b7a8c7a`
  - static evidence: README
  - absorbed patterns: `hierarchical_cowriting_story_scaffold`, `human_coauthor_edit_boundary`
  - reusable lesson: co-writing workflows should decompose logline, characters, plot points, locations, and dialogue while keeping human edits as first-class boundary decisions.
  - runtime exclusion: Colab/runtime launch, scripts, provider calls, and package install are not used.

- `yangkevin2/emnlp22-re3-story-generation`
  - URL: `https://github.com/yangkevin2/emnlp22-re3-story-generation`
  - observed HEAD: `3a97ebde04e3333962c2825146897efe1dc87dd8`
  - static evidence: README
  - absorbed patterns: `recursive_reprompt_revision_loop`, `reranker_guided_candidate_selection`
  - reusable lesson: long-story generation benefits from plan, draft, rewrite, edit, and rerank stages, but each loop needs a replayable revision trace before replacing accepted text.
  - runtime exclusion: notebooks, scripts, dependencies, model calls, and reranker execution are not used.

- `LC1332/Chat-Haruhi-Suzumiya`
  - URL: `https://github.com/LC1332/Chat-Haruhi-Suzumiya`
  - observed HEAD: `290bf4ad22076156083804013012847a77c0646c`
  - static evidence: README
  - absorbed pattern: `character_dialogue_persona_memory`
  - reusable lesson: character voice should be represented as bounded persona/dialogue memory and evidence notes, not as direct copying of source character prose.
  - runtime exclusion: dataset import, notebooks, package install, role-play runtime, and model calls are not used.

- `rajammanabrolu/StoryRealization`
  - URL: `https://github.com/rajammanabrolu/StoryRealization`
  - observed HEAD: `c01253d42d88783ea5899c68134f442d00b65183`
  - static evidence: README
  - absorbed patterns: `event_to_sentence_realization_trace`, `entity_memory_slotfill_grounding`
  - reusable lesson: event expansion should keep event creation, slot filling, entity memory, confidence, and sentence realization evidence separate from final prose.
  - runtime exclusion: model/runtime scripts, data import, package install, and ensemble execution are not used.

### Local projection

The source discovery panel now pins these prompt-safe fields instead of leaving
them only in the dynamic fallback group:

- `agentwrite_plan_write_pipeline_hints`
- `long_output_length_quality_ruler_hints`
- `long_context_reward_dimension_gate_hints`
- `instance_specific_writing_criteria_gate_hints`
- `material_grounded_query_refinement_hints`
- `hybrid_rubric_pairwise_elo_judge_hints`
- `judge_bias_mitigation_check_hints`
- `plan_reflect_character_chapter_pipeline_hints`
- `human_story_metric_panel_hints`
- `hierarchical_cowriting_story_scaffold_hints`
- `human_coauthor_edit_boundary_hints`
- `recursive_reprompt_revision_loop_hints`
- `reranker_guided_candidate_selection_hints`
- `event_to_sentence_realization_trace_hints`
- `entity_memory_slotfill_grounding_hints`

These fields are static source-derived planning, reward, benchmark, and
co-writing gates only. They do not authorize package installation, benchmark
execution, notebook/script runs, model/provider calls, dataset import, external
runtime launch, role-play service launch, or copying source prose/persona text
into prompts.

## Source deconstruction / memory glossary addendum - 2026-06-10

This addendum records a public GitHub HEAD + raw README static-review pass for
source-book deconstruction, persistent writing memory, spec-driven fiction
tasks, TOC-aware ebook notes, cumulative glossary pipelines, and inline author
edit markup. No external project was cloned, installed, built, launched, or
executed. Scratch evidence was saved under
`tmp/source-intake-source-deconstruction-memory-2026-06-10` only.

### Reviewed sources

- `gratajik/book-memory-bank`
  - URL: `https://github.com/gratajik/book-memory-bank`
  - observed HEAD: `5a1df67c70219dbd76a92eaf8aa5004592aed680`
  - static evidence: README
  - absorbed pattern: `book_memory_bank_context_lattice`
  - reusable lesson: 拆书/续写 context should be split into project brief, story structure, world/character notes, active context, and progress instead of relying on stateless chat memory.
  - runtime exclusion: Cline automation, prompt execution, file-agent updates, and any assistant runtime are not used.

- `adaumann/speckit-preset-fiction-book-writing`
  - URL: `https://github.com/adaumann/speckit-preset-fiction-book-writing`
  - observed HEAD: `c31b629ef8c733eb4e3af8643a5761ee9328fec0`
  - static evidence: README
  - absorbed pattern: `spec_driven_fiction_scene_tasks`
  - reusable lesson: same-type writing should convert story briefs into governed scene tasks with constitution, POV, plot structure, glossary, and quality gates before drafting.
  - runtime exclusion: Spec Kit workflow runtime, template execution, package tooling, and provider calls are not used.

- `danngalann/llm-ebook-summarizer`
  - URL: `https://github.com/danngalann/llm-ebook-summarizer`
  - observed HEAD: `d0b2c1332b9439b3c6cb40192a9f82024cdef16d`
  - static evidence: README
  - absorbed pattern: `toc_aware_source_deconstruction`
  - reusable lesson: source-book notes should preserve TOC hierarchy, nested chapters, parent section introductions, quotes, anecdotes, and rejected boundaries as deconstruction evidence.
  - runtime exclusion: EPUB/PDF parsing, summarizer calls, script execution, package install, and model calls are not used.

- `darkautism/ai-novel-translation`
  - URL: `https://github.com/darkautism/ai-novel-translation`
  - observed HEAD: `5bc73d4b33a54deea348e8d170832f4be79a37cf`
  - static evidence: README
  - absorbed pattern: `two_pass_context_glossary_pipeline`
  - reusable lesson: chapter ingestion should run an analysis pass for summary and term extraction, then use previous summary plus cumulative glossary for transformed context.
  - runtime exclusion: Rust build, config execution, chapter translation, provider calls, and glossary file mutation are not used.

- `lordjabez/story-framework`
  - URL: `https://github.com/lordjabez/story-framework`
  - observed HEAD: `56cdb2ccc4161e9ec24823e95225a5b922c97e81`
  - static evidence: README
  - absorbed pattern: `inline_author_edit_markup_versioning`
  - reusable lesson: author notes, edit markers, continuity facts, timeline files, and git milestone tags should remain reviewer-visible state instead of being silently folded into final prose.
  - runtime exclusion: git tag mutation, draft processing, assistant edit-note execution, and repository workflow commands are not used.

### Local projection

The source discovery panel now pins these prompt-safe fields instead of leaving
them only in the dynamic fallback group:

- `book_memory_bank_context_lattice_hints`
- `spec_driven_fiction_scene_tasks_hints`
- `toc_aware_source_deconstruction_hints`
- `two_pass_context_glossary_pipeline_hints`
- `inline_author_edit_markup_versioning_hints`

These fields are static source-derived deconstruction, memory, glossary, and
edit-review gates only. They do not authorize package installation,
EPUB/PDF/translation execution, prompt/provider calls, assistant runtime launch,
git tag creation, external project workflow execution, or treating source
analysis notes as transformed-story canon.
