# Novel Source Discovery 2026-06-14 — frame coordinate × setting document × StateDB projection

## Sources

### A Bridge in the Sky / ABITS

- Repository: https://github.com/nickcottrell/abits
- Static HEAD: `3c79c31247ec489f63a38bc8755ca646e84a01be`
- Default branch: `main`
- License signal: no root license observed in this pass
- Local static README: `tmp/source-intake-abits-readme-20260614.md`
- README SHA256: `0100CF24C910F890F9EBAD207C11BA5570EFF1201831AA11F9127BA80A3CD78B`
- Local static requirements: `tmp/source-intake-abits-requirements-20260614.txt`
- Requirements SHA256: `CF1480DE1193FC2D38EF617B4CF809DF63EA84CADFCDB91C95ABC4A2353D04CF`
- Intake posture: pattern-only / runtime-deferred

### Novel Setting Runtime Construction

- Repository: https://github.com/novemberjae-cmyk/Novel-Setting-Runtime-Construction
- Static HEAD: `35a50ad58877f1728df97c351208f71d42f44c77`
- Default branch: `main`
- License: MIT
- Local static README: `tmp/source-intake-setting-runtime-readme-20260614.md`
- README SHA256: `DB69B41BC9479C2FD063863E1DF446E28A84D54B8A44894F2ADCC515DB68995E`
- Local static license: `tmp/source-intake-setting-runtime-license-20260614.txt`
- License SHA256: `C01D81D5C7B8D6BFFC47BE75E4AE7B867BF64A263ABB86A9BB63F2BE61EA541D`
- Intake posture: pattern-only / runtime-deferred

### InkFoundry

- Repository: https://github.com/wangjiaquangithub/InkFoundry
- Static HEAD: `12b3a78cb5e5bdc7fe06036a1c9a94bb78490e03`
- Default branch: `main`
- License signal: no root license observed in this pass
- Local static README: `tmp/source-intake-inkfoundry-readme-20260614.md`
- README SHA256: `E5C0C44613F4ACF172F60CD82A42CD9749A5E8E5E80581410267A1BB32E69487`
- Local static requirements: `tmp/source-intake-inkfoundry-requirements-20260614.txt`
- Requirements SHA256: `2019C8B88A42023FCE363EDBF88C6ECF776FF40CB87663D043C8465EB2C55C57`
- Intake posture: pattern-only / runtime-deferred

## Static Evidence

ABITS README markers describe vector storytelling with VRGB frames: story beats,
tone, density, register, baseline word counts, frame configs, canonical baseline
frames, timestamped generated drafts, diff against baseline, provider access,
environment variables, and shell/Python generation scripts.

Novel Setting Runtime markers describe a multi-document fiction-setting system:
story bible, voice bible, project instructions, tracked items, opening scenario,
theory-of-mind notes, anti-patterns, document jobs, session start/resume
protocols, construction/runtime environment split, closed documents, priority
order, review before moving on, and environment-specific filesystem paths.

InkFoundry markers describe a narrative OS with StateDB as hard truth,
StateFilter blocking contradictory RAG, Navigator/Writer/Editor/RedTeam agents,
VoiceSandbox, snapshots, versioning, locks, circuit breaker, watchdog timeout,
ChromaDB vector memory, import/export with path traversal protection, provider
model settings, daemon scheduler, token tracking, and MCP/FastAPI surfaces.

## Fused Pattern

### `frame_setting_state_runtime_gate`

When any of these gates are active:

- `vector_story_frame_coordinate_gate`
- `setting_runtime_document_architecture_gate`
- `inkfoundry_state_db_redteam_voice_sandbox_gate`

MuMuAINovel now asks the remix context to surface:

```text
frame_coordinate_contract
setting_document_architecture
session_start_packet
state_over_vector_boundary
redteam_voice_sandbox_review
continuation_or_same_type_boundary
runtime_boundary
```

The gate prevents four failures:

1. asking the model to write a whole chapter without frame-level beat/tone/density/register constraints
2. loading setting documents blindly without stale/forbidden/closed document custody
3. allowing vector recall to override accepted hard state
4. treating RedTeam or VoiceSandbox findings as hidden generation authority instead of review proposals

## MuMuAINovel Projection

- `book_remix_context_service.py`
  - Adds `story_frame_coordinate_contract` for VRGB-style target-owned frame control.
  - Adds `setting_document_session_packet` for loaded/stale/forbidden document custody.
  - Adds `state_db_over_vector_review` and `redteam_voice_sandbox_findings` for hard-state and review-envelope control.
  - Adds acceptance steps:
    - `verify_frame_coordinate_contract`
    - `verify_setting_document_session_packet`
    - `verify_state_db_redteam_voice_review`
  - Renders continuation and same-type context sections with runtime exclusions.

## Runtime Boundary

Do not run or install upstream runtimes during static intake:

- no generation engine, provider/model call, OpenAI/AWS key use, environment variable read, shell script, Python build, or generated draft
- no campaign prompt body, upstream setting instruction, environment path, filesystem/MCP runtime, or user setting file access
- no InkFoundry backend/frontend, ChromaDB, StateDB runtime, daemon scheduler, MCP/FastAPI server, import/export artifact, token tracker, or generated manuscript
- no copying canonical frames, baseline prose, setting documents, RedTeam findings, VoiceSandbox profiles, or prompt bodies into MuMuAINovel canon

The absorbed value is the custody/control pattern, not upstream code, generated prose, prompt bodies, or runtime behavior.
