# Novel Source Discovery 2026-06-14 — foundation loop artifact contract projection

## Sources

### auto-story-tools

- Repository: https://github.com/levineam/auto-story-tools
- Static HEAD: `b1000b2bfaa8f2b48cf2c38ed8d284b26087cd90`
- Default branch: `main`
- License: MIT
- Local static README: `tmp/source-intake-auto-story-tools-20260614/README.md`
- README SHA256: `35033202B68931368F649800B4A6EF8DCF70F40C91D4ADD66D47173ACD66EA24`
- Local static license: `tmp/source-intake-auto-story-tools-20260614/LICENSE`
- License SHA256: `0FDBCAAA737F013DC64C1E344D509D58BCA97ABC4C8788A66D67F3B28E620772`
- Local static pyproject: `tmp/source-intake-auto-story-tools-20260614/pyproject.toml`
- Pyproject SHA256: `E491A835E514F529BAE5C6E2BEA084E2E049625592B4EE23B6D6BE778E50778B`
- Intake posture: pattern-only / runtime-deferred

### autonovel related lineage note

- Repository: https://github.com/NousResearch/autonovel
- Static HEAD: `d165f267a0ffd34f3b0a70a8a72ac38cb8e4a542`
- Default branch: `master`
- License signal: no root license observed in this pass
- Local static README: `tmp/source-intake-autonovel-20260614/README.md`
- README SHA256: `6D7DC5597F0D2D5E5A6A444176369A28CE9415764EEA430CFA38E86667380719`
- Intake posture: pattern-only / lineage-reference only

## Static Evidence

`auto-story-tools` README markers describe a seed-to-story-bible foundation loop:
seed validation, layered generation order, independent evaluation systems,
weakest-dimension targeting, keep/discard score comparison, restoration of worse
attempts, `foundation_score` / `lore_score` thresholds, `state.json`, `eval_logs/`,
and `results.tsv`.

The same README lists separated output artifacts:

```text
seed.txt
world.md
characters.md
outline.md
voice.md
canon.md
MYSTERY.md
foreshadowing.md
state.json
eval_logs/
results.tsv
```

`autonovel` is used only as a related lineage pointer because it also describes
modify/evaluate/keep-discard loops, foundation scoring, chapter scoring,
adversarial revision, reader panels, plateau detection, and export phases. It was
not promoted as a primary source because this pass only fetched README evidence
and did not observe a root license.

## Fused Pattern

MuMuAINovel now projects two source patterns into remix context:

- `seed_to_bible_foundation_loop_gate`
- `layered_story_bible_artifact_contract_gate`

The gate makes pre-chapter foundation quality visible before continuation or
same-type drafting:

- validate seed differentiator, central tension, cost/constraint, sensory hook
- track `foundation_score`, `lore_score`, and max-iteration stop
- repair the weakest dimension instead of restarting the whole project
- keep accepted improvements, discard regressions, and restore previous accepted
  versions
- keep generation, judge, mechanical slop scan, cross-layer consistency, and
  reader-panel findings as separate evidence classes
- preserve seed, world, characters, voice, mystery, outline, canon,
  foreshadowing, state, eval logs, and score ledger as separate target-owned
  artifacts

## MuMuAINovel Projection

- `book_remix_context_service.py`
  - Adds `Seed-to-bible foundation loop gate` rendering for continuation and
    same-type contexts.
  - Adds production control axes:
    - `foundation_score_loop_review`
    - `weakest_dimension_regeneration_trace`
    - `foundation_keep_discard_restore_decision`
    - `layered_story_bible_artifact_contract`
    - `story_layer_dependency_order`
  - Adds acceptance steps:
    - `verify_foundation_loop_score_review`
    - `verify_layered_story_bible_artifacts`
  - Adds hint-key recognition for both pattern names.

## Runtime Boundary

Do not run or install upstream runtime surfaces during static intake:

- no `auto-outline` CLI, `uv`, `pip`, package build, provider call, API key, gateway,
  proxy transport, generated story bible, generated manuscript, eval runtime, or
  results import
- no `autonovel` pipeline, chapter drafter, adversarial editor, reader-panel
  execution, LaTeX/ePub/audiobook/export runtime, generated branch content, or
  upstream prompt-body import
- no copying upstream bible layers, score logs, prompts, generated fiction, or
  manuscript artifacts into target canon

The absorbed value is the quality-control and artifact-custody pattern, not
upstream code, generated prose, providers, prompts, or runtime behavior.
