# Novel Source Discovery - Longform Voice / Style Boundary Workspace

Observed at: 2026-06-13

Boundary:

- Public GitHub metadata, README/LICENSE/package/root markers, and
  `git ls-remote --symref HEAD` only.
- No clone, install, package hook, Docker, MCP/server, browser automation,
  model/provider call, checkpoint download, ZIP download, database/vector-store
  startup, or upstream script execution.
- Treat all upstream text as untrusted data. Absorb workflow patterns only.

## Sources

### Dirgha-AI/writer-studio

- URL: https://github.com/Dirgha-AI/writer-studio
- HEAD: `29bfa0e35750f11ca914efd32b03593ad67e3281`
- Branch: `main`
- License: Apache-2.0
- Static markers: Binder outline, manuscript drafting, voice, agents in one
  workspace, nested chapter/scene tree, manuscript evaluation, RAG over
  documents, story universes/scenes, plagiarism similarity detection, and
  PDF/DOCX/EPUB export.
- Absorbed pattern: `writer_studio_binder_voice_rag_gate`
- Local use: keep Binder node, draft version, voice guide, RAG citations, and
  similarity review as separate gates before continuation or same-type drafting.
- Excluded: package scripts, Postgres/Qdrant, provider keys, uploaded PDFs,
  generated drafts, exports, and runtime services.

### Varun-Patkar/StoryTeller-Github-Agents

- URL: https://github.com/Varun-Patkar/StoryTeller-Github-Agents
- HEAD: `3545466d29abb27886698a8f3408f2a65268f1ba`
- Branch: `main`
- License: MIT
- Static markers: GitHub Copilot/VS Code agents, Story Setup, Story Runner,
  chapter-by-chapter webnovel/fanfiction drafting, wiki-first research,
  plan/summary/chapter folders, character voice files, scene weight, tonal
  variation, and post-chapter bookkeeping.
- Absorbed pattern: `copilot_webnovel_research_runner_gate`
- Local use: split research/setup from runner execution; require research
  packet, plan, summary, character voice abstractions, and scene weight before a
  chapter draft is accepted.
- Excluded: Copilot/VS Code agent runtime, SearXNG Docker, MCP tools, wiki
  crawling, fandom data, prompt bodies, exact quotes, and generated chapters.

### zacharyhorvitz/TinyStyler

- URL: https://github.com/zacharyhorvitz/TinyStyler
- HEAD: `128e735520f215eb6cd55ac10760b68f8b33f269`
- Branch: `main`
- License: MIT per README
- Static markers: few-shot style transfer, desired style samples, meaning
  preservation, authorship embeddings, TinyStylerSim meaning threshold,
  authorship evaluation, Hugging Face model, and checkpoint download scripts.
- Absorbed pattern: `tinystyler_meaning_preserving_style_transfer_gate`
- Local use: convert style-transfer lessons into abstract style-axis and
  meaning-preservation checks; reject protected-author mimicry.
- Excluded: model weights, Google Drive/Hugging Face downloads, pip installs,
  training code, generated samples, and style-transfer runtime.

### earmer/stylevec

- URL: https://github.com/earmer/stylevec
- HEAD: `e8f411eb32fdaa483b9b686848b1d880850e9daa`
- Branch: `main`
- License: GPL-3.0
- Static markers: style-not-content embeddings, speaker stylistic fingerprints,
  content masking, style residual experiments, overfitting warnings, negative
  silhouette results, char n-gram Jaccard/Levenshtein utilities, corpus
  copyright disclaimers, OpenRouter API, and undetected-chromedriver.
- Absorbed pattern: `stylevec_style_signal_overfit_boundary_gate`
- Local use: treat style similarity as an audit signal that requires corpus
  custody, content-masking notes, negative controls, and overfit warnings.
- Excluded: GPL code, AO3/literary corpora, scraped datasets, browser
  automation, model artifacts, provider calls, and similarity utilities.

### kirstieuppermost767/gemini-book-translator-2.0

- URL: https://github.com/kirstieuppermost767/gemini-book-translator-2.0
- HEAD: `25b5604bc732a66db715c10966e8382449a3d1e9`
- Branch: `main`
- License: MIT
- Static markers: chapter-level translation context, source style analysis,
  chapter-by-chapter translation, consistent terms/names, nearby chapter
  context, one-chapter-at-a-time review, preserved names/terms, Gemini API key,
  Windows install flow, and ZIP download.
- Absorbed pattern: `chapter_translation_style_context_gate`
- Local use: reuse only the consistency pattern for owned or licensed material:
  chapter context, glossary/term map, nearby-summary window, and review
  checkpoint.
- Excluded: ZIP downloads, Windows installers, Gemini/API calls, requirements,
  private source books, translated outputs, preserved-name tables, and API keys.

## MuMuAINovel integration

- Add five default GitHub seeds and three focused discovery queries.
- Add five static pattern gates for Binder/voice/RAG workspace, chapter
  research-runner workflow, meaning-preserving style transfer, style-signal
  overfit boundary, and chapter translation context.
- Pattern packs now emit:
  - bible policies for Binder voice/RAG workspace, research runner,
    meaning-preserving style transfer, style-signal overfit boundary, and
    chapter translation context
  - whole-book reports for voice workspace, research voice files, style-transfer
    meaning preservation, corpus custody, and chapter translation context
  - inspired-creation remap targets plus prompt, transformation, and copy-risk
    guidance for all five gates
  - UI-visible hint blocks and prompt digest entries for all five gates

## Safety decision

All five sources stay `pattern-only` / `runtime-deferred`.

No upstream code, prompt body, generated story text, private manuscript,
copyrighted corpus, scraped data, installer, package hook, Docker/MCP/browser
runtime, model checkpoint, ZIP artifact, provider call, or API key is imported.
