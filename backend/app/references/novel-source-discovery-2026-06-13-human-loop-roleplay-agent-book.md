# Novel source discovery - human loop / roleplay / agent book patterns

Date: 2026-06-13

Scope: static public GitHub intake for拆书续写、同类型仿写、长篇小说工作流。

No repository was cloned, installed, built, or executed. No provider call, browser
runtime, MCP runtime, private chat state, cookie, token, API key, or generated
upstream manuscript artifact was imported.

## Sources

- `jbpayton/robot-writers-room`
  - URL: `https://github.com/jbpayton/robot-writers-room`
  - Observed HEAD: `8a18e902b37eb8c864c1d2d68602d44eccadf00b`
  - Branch: `master`
  - License: MIT
  - Posture: pattern-only
  - Static markers: human final say, Brainstormer, Researcher, Refiner, Scribe,
    Outliner, Worldbuilder, Character Designer, Chapter Outliner, accept/reject/
    modify flow, typed idea cards, LangChain web research tools.

- `WASasquatch/TheSpire_Roleplay`
  - URL: `https://github.com/WASasquatch/TheSpire_Roleplay`
  - Observed HEAD: `0003275ee900e3b17979c8dd6a688bc84d9dc0e2`
  - Branch: `main`
  - License: AGPL-3.0
  - Posture: pattern-only
  - Static markers: roleplay-focused chat, characters as first-class entities,
    OOC/IC separation, rich bios, stats, portraits, in-character journal,
    relationship titles, in-app wiki, private DM/friends surface, chapters and
    reviews.

- `SimonWaldherr/AI-Book-Generator`
  - URL: `https://github.com/SimonWaldherr/AI-Book-Generator`
  - Observed HEAD: `59567997d6bebbe0f3b91c947f74e8d9605fe6d9`
  - Branch: `main`
  - License posture: conflict observed. LICENSE is GPL-3.0; package metadata
    reports MIT.
  - Posture: pattern-only
  - Static markers: Agent Mode, Generate Complete Book, title suggestions,
    concept, outline, sequential chapter generation, live log/cancel, cover
    generation, localStorage, provider API keys, TXT/HTML/MD/JSON/PDF export.

- `kwaroran/RisuAI`
  - URL: `https://github.com/kwaroran/RisuAI`
  - Observed HEAD: `6765daa2d9503e453fcd7ee121cbf8766e3ffb24`
  - Branch: `main`
  - License: GPL-3.0
  - Posture: pattern-only
  - Static markers: multi-provider roleplay/chat, assets and emotion images,
    group chats, plugins, regex output modification, translators, lorebook/world
    infos/memory book, prompting order, impersonation prompts, variables,
    conditions, Tauri/Electron/localforage/WebLLM/updater surfaces.

## Absorbed patterns

- `robot_writers_room_human_card_flow_gate`
  - Use human final-say as the promotion gate.
  - Keep idea cards typed as World / Character / Plot / Theme candidates.
  - Researcher web-search/runtime tools remain excluded.

- `spire_roleplay_character_privacy_fiction_surface_gate`
  - Separate OOC, IC journal, wiki, profile, private DM/friend context, and
    publishable chapter/review state.
  - Treat character privacy/visibility as a first-class gate before reuse.

- `ai_book_generator_agent_mode_local_key_export_gate`
  - Treat complete-book generation as staged state: title, concept, outline,
    chapter sequence, export readiness, cancel state, acceptance id.
  - Keep localStorage, API keys, provider calls, cover generation, and export
    artifacts outside source intake.

- `risuai_lorebook_prompt_order_regex_gate`
  - Make lorebook activation, prompt insertion order, impersonation boundary,
    variables, conditions, and regex output modification reviewable.
  - Keep plugins, providers, local storage, updaters, and chat content outside
    source intake.

## Runtime exclusions

Blocked for this intake:

- clone, checkout, install, build, package-manager scripts, postinstall hooks
- Python/Node/Tauri/Electron/browser/runtime launch
- MCP/server/database/chat/private-message runtime
- provider/model/API calls and API-key handling
- localStorage/browser storage import
- upstream generated books, prompts, logs, character cards, chat state, or prose
- AGPL/GPL/license-conflicted code reuse
- deploy scripts, updaters, plugin activation, cover/export generation

## Local adaptation

MuMuAINovel uses these sources only as abstract workflow vocabulary:

- human-card ideation policy/report/remap
- roleplay character privacy and fiction-surface policy/report/remap
- staged agent-mode book generation with local-key/export boundaries
- lorebook prompt-order regex review gates

The implementation is repo-native and test-covered through
`test_human_in_loop_roleplay_agent_book_sources_are_static_absorbed`.
