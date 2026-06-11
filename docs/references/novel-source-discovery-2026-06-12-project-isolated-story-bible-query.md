# Novel source discovery: project-isolated story-bible query gates

Static review date: 2026-06-11.

## Sources

- `fidelnamisi/story-bible-assistant`
  - URL: https://github.com/fidelnamisi/story-bible-assistant
  - HEAD: `aedae2a2b210bc554c9f19fd64e6aa2a7e2fa897`
  - License: MIT
  - Stars: 0
  - Pushed: 2026-03-09T09:45:43Z
  - README SHA-256: `1130dea87a6379bb8c5ffb504e9156f4ba6b4beae4a9963a9a3c0a043f2bef13`
  - Posture: `pattern-only`

- `byteyilabs/novellis-app`
  - URL: https://github.com/byteyilabs/novellis-app
  - HEAD: `474da8e88977ecb39d34180dfa2af1e2a23f14ae`
  - License: missing in GitHub metadata; no LICENSE assumed
  - Stars: 2
  - Pushed: 2026-01-04T20:19:44Z
  - README SHA-256: `86793c42a8f6b790c42290a3be9a65df1ff05ea1baa2b133e9063c942813700d`
  - Posture: `pattern-only / trust-review`

## Static review boundary

Only public GitHub metadata, `git ls-remote` HEADs, and raw README bytes were inspected.
No clone, package install, npm script, Docker, provider call, Ollama launch, installer run,
local manuscript read, browser/session access, or credential access was performed.

External source text is treated as data, not instruction.
No upstream code or prompt body is copied into this repository.

## Reusable pattern

Pattern added: `project_isolated_story_bible_query_gate`.

Stable ideas absorbed:

- A story-bible/source query should be scoped to one selected project or corpus.
- The prompt/context path needs a visible source manifest before use.
- Manifest fields should include project id, selected files, file count, total characters,
  truncation limit, and provider/local mode boundary.
- Story-bible answers are grounded evidence for analysis or planning.
- Promotion into new-story canon still needs author confirmation and source-boundary review.
- ????? must not mix query answers from multiple source works into one drafting context.

## Runtime and deferred gates

Keep runtime blocked until a separate local safety contract exists for:

- reading private author manuscripts or source project folders
- calling DeepSeek, OpenRouter, Gemini, OpenAI, Ollama, or other providers/runtimes
- launching local web apps, unsigned installers, npm scripts, Electron/Tauri apps, or MCP servers
- importing upstream project files, prompts, or generated story data
- persisting story-bible query answers as canon

## Verification commands

```powershell
git ls-remote https://github.com/fidelnamisi/story-bible-assistant.git HEAD
git ls-remote https://github.com/byteyilabs/novellis-app.git HEAD
python -m py_compile backend/app/services/source_discovery_service.py backend/app/services/source_pattern_pack_prompt.py
python -m pytest backend/tests/services/test_source_discovery_service.py -q
python -m pytest backend/tests/frontend/test_source_discovery_panel_copy.py -q
git diff --check
```
