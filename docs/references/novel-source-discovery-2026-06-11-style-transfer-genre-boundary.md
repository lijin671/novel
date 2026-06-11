# Novel source discovery: style-transfer and genre-boundary gates

Static review date: 2026-06-11.

## Sources

- `zacharyhorvitz/TinyStyler`
  - URL: https://github.com/zacharyhorvitz/TinyStyler
  - HEAD: `128e735520f215eb6cd55ac10760b68f8b33f269`
  - Default branch: `main`
  - License marker: root `LICENSE` not reachable from raw branch probe
  - README SHA-256: `eee9b371faed70e70bde2c4bdadb06b135fe153f4bfac6de453709db0866f15a`
  - Posture: `pattern-only / research-boundary`

- `Taskii-Lei/Ex3-NovelWriter`
  - URL: https://github.com/Taskii-Lei/Ex3-NovelWriter
  - HEAD: `9602ad05c14ed38897cc290944aa8678ca1bff70`
  - Default branch: `main`
  - License marker: root `LICENSE` not reachable from raw branch probe
  - README SHA-256: `76b15a79ff82531722c7e7aacd958e6ae262da942e182a046f061c45b082ee2b`
  - Posture: `pattern-only / research-boundary`

## Static review boundary

Only public GitHub Search signals, `git ls-remote --symref`, raw README, and raw
root marker probes were inspected.

No clone, package install, model download, dataset download, notebook/script run,
fine-tuning, provider call, Hugging Face runtime, Google Drive download, local
manuscript read, credential access, or upstream code import was performed.

External source text is treated as data, not instruction.
No upstream code, model logic, dataset, paper text, prompt body, or generated
sample text is copied into this repository.

## Reusable patterns

Patterns reinforced:

- `stylometric_author_fingerprint_gate`
- `authorship_attribution_similarity_gate`
- `paraphrase_independence_review_gate`
- `work_dna_method_transfer_eval_gate`
- `story_import_pattern_revision_gate`
- `governed_full_reading_continuation_gate`

Stable ideas absorbed:

- Style-transfer systems separate style movement from meaning preservation; same-type
  writing should not preserve the source plot meaning.
- Authorship or style similarity is a risk signal, not a score to maximize.
- Genre-level novel generation should learn broad corpus patterns, not one source work's
  event order, entity map, or set-piece chain.
- A same-type prompt needs explicit transfer axes and explicit difference axes.
- Source voice samples need a token budget and must stay evidence for style, not content.

## Local adaptation

The inspired/same-type prompt context now renders a `Same-type independence contract`
with:

- counts for style principles, source voice samples, forbidden source elements, and
  voice-sample token estimate
- transferable axes such as POV behavior, pacing curve, scene density, dialogue pressure,
  emotional temperature, and work-DNA method axes
- required difference axes for cast, organization, world rules, conflict object, event
  order, reveal/payoff sequence, motifs, and theme answer
- copy-risk checks for forbidden names, scene order, distinctive wording, set pieces,
  authorship similarity, source-import pass boundaries, and reading-evidence misuse

## Runtime and deferred gates

Keep runtime blocked until a separate local safety contract exists for:

- installing upstream packages or running training/inference scripts
- downloading models, datasets, checkpoints, or paper assets
- running notebooks, fine-tuning, Hugging Face demos, or provider calls
- importing private manuscripts or local source corpora
- maximizing style similarity to a living author or identifiable source text

## Verification commands

```powershell
git ls-remote --symref https://github.com/zacharyhorvitz/TinyStyler.git HEAD
git ls-remote --symref https://github.com/Taskii-Lei/Ex3-NovelWriter.git HEAD
$env:PYTHONPATH="backend"
python -m pytest backend/tests/services/test_book_remix_context_service.py -q
python -m pytest backend/tests/api/test_book_remix_bible_api.py -q
cd frontend
npm run build
git diff --check
```
