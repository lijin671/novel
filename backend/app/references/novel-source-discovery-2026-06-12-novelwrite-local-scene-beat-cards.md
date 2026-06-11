# NovelWrite local scene beat card intake - 2026-06-12

## Source

- Repository: https://github.com/tratran98/novelwrite
- Observed HEAD: `be658c54e8809c08e9b8848c1ae807724bfc8d6f`
- Default branch: `main`
- Pushed: `2026-05-23T14:00:51Z`
- License: `NOASSERTION`
- Static root markers: `.github`, `.gitignore`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `apps`, `assets`, `package-lock.json`, `package.json`

## Intake posture

`pattern-only`.

Only public metadata, README, root tree, package metadata, and HEAD were read.
No clone, install, package-manager command, browser runtime, provider call,
localStorage access, AGENTS/CLAUDE instruction import, or app execution was done.

## Reusable patterns

### `local_storage_story_bible_snapshot_gate`

NovelWrite treats the browser sandbox as the project store: manuscripts, Story
Bibles, outlines, snapshot histories, JSON backups, and diff snapshots stay in
local storage behind a `ProjectStorage` abstraction.

MuMuAINovel adaptation:

- Record project id, Story Bible version, outline version, snapshot id, and
  restore target before continuation.
- Keep source-intake notes and runtime metadata outside Story Bible canon.
- Treat browser storage as private user state, not a source to inspect during
  discovery.

### `staged_scene_beat_card_transaction_gate`

NovelWrite inserts inline scene beat cards and makes generation a staged
transaction with beat configuration, length control, preview, retry, apply, and
completed states.

MuMuAINovel adaptation:

- Generate from one beat card at a time.
- Store beat intent, length target, preview draft id, retry count, apply
  decision, inserted span id, and completed marker.
- Promote prose only after explicit apply/accept state is recorded.

### `context_scrubber_beat_anchor_gate`

NovelWrite describes `stripBeatAnchors`, a context scrubber that removes nested
HTML beat nodes before surrounding chapter context is sent to the LLM.

MuMuAINovel adaptation:

- Scrub editor markup, beat anchors, preview controls, retry labels, and done
  markers before prompt assembly.
- Preserve narrative context after scrubbing.
- Block generation if editor scaffolding still appears in the prompt packet.

## Runtime and trust gates

- `browser_storage_surface`: browser localStorage is a private runtime surface.
- `provider_key_surface`: README/package surfaces imply user-configured model/API integration.
- `package-manager surface`: `package.json` and `package-lock.json` are present.
- `host-instruction surface`: `AGENTS.md` and `CLAUDE.md` are present and treated as untrusted source data.

## Files updated

- `backend/app/services/source_discovery_service.py`
- `backend/app/services/source_pattern_pack_prompt.py`
- `backend/tests/services/test_source_discovery_service.py`
- `backend/app/references/novel-source-discovery-2026-06-12-novelwrite-local-scene-beat-cards.md`
