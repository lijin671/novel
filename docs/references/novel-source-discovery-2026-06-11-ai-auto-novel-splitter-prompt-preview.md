# Novel source discovery - AI automatically generates novels splitter/prompt preview

Date: 2026-06-11

## Source

- Repository: `wfcz10086/AI-automatically-generates-novels`
- URL: <https://github.com/wfcz10086/AI-automatically-generates-novels>
- Observed HEAD: `5975df2232b8a4d78114af41e267d5b2d2efeb88`
- License: Apache-2.0
- Stars at static review: 881
- Posture: `pattern-only`

Static review only. No clone checkout, install, provider call, hosted demo use,
web runtime launch, requirements install, model connector run, or account/key
inspection was performed.

## Static evidence

- GitHub metadata and `git ls-remote` confirmed the public HEAD above.
- Public README describes:
  - 智能拆书
  - 书名/简介生成
  - 正文润色
  - `shift+L` 快捷词条
  - 多套小说提示词库管理
  - `/gen` and `/gen2` model endpoints
  - API 密钥 configuration surface
- `static/book-splitter.js` static review shows:
  - chapter title regex splitting
  - encoding selection (`UTF-8`, `GBK`, `GB2312`, `BIG5`)
  - per-chapter processing state
  - chapter analysis prompt sections for summary, characters,
    relationship changes, key scenes, turns, theme, foreshadowing, and craft
  - JSON export of split/deconstruction data
- `static/prompt-editor.js` and `templates/index.html` static review show:
  - operation type display
  - selected text display
  - prompt template display
  - editable final prompt before sending
  - variable replacement before generation
  - right-click selected-span revision preview and merge

## Absorbed patterns

### `chapter_split_deconstruction_export_gate`

Use imported source text as a reviewed拆书 artifact:

- record encoding, title regex, chapter id, original span, status, retry count,
  prompt version, and export checksum
- separate summary, characters, relationship changes, key scenes, turns,
  themes, foreshadowing, and writing-technique notes
- keep exported拆书 JSON as analysis evidence, not direct canon

### `final_prompt_preview_span_revision_gate`

Before model calls or selected-span rewrites:

- show operation type, selected span, prompt template, resolved variables, and
  editable final prompt
- record the final prompt text and author edit/approval decision
- merge generated text only into the named span
- treat shortcut entries as named snippet ids with provenance and scope

## Runtime boundaries

- Provider/model endpoint code is not imported.
- API key or hosted demo surfaces are not used.
- `requirements.txt`, web app runtime, and scripts are not executed.
- The source contributes prompt-preview, span-revision, and chapter-split
  workflow gates only.
