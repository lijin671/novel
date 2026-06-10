# Novel Source Discovery - 2026-06-10 Local RAG / Canon QA / Patch Replay

## Intake boundary

本轮只做公开 GitHub 元数据与 README/root-file 静态吸收。

未 clone、未安装、未执行 package manager、Docker、脚本、MCP、插件、模型调用、浏览器或桌面控制。
所有候选默认是 `pattern-only`；任何 runtime trial 都需要单独安全合同。

## Reviewed sources

- `datacrystals/AIStoryWriter`
  - HEAD: `161b712400cd825f2d0a933cb0d9c362a48ea30b`
  - license: AGPL-3.0
  - posture: `pattern-only`
  - absorbed: staged outline / chapter writing / revision / evaluation separation.
- `sadasdfsaf/canonkit`
  - HEAD: `edb8c1ac1747a822da1cd728fbc8c13a8f932e7a`
  - license: no GitHub license detected
  - posture: `pattern-only`
  - absorbed: local-first story bible, canon drift QA, scene context pack.
- `heider-x/vela`
  - HEAD: `854a0c0acc57b8f99904b96b4470df355e0918c9`
  - license: GPL-3.0
  - posture: `pattern-only`
  - absorbed: local-first writing IDE, BYOK/local RAG, review/rewrite/refine loop.
- `pulpgen-dev/pulpgen`
  - HEAD: `91c77b4877cb90a0fffba1b4593bb176909c88ff`
  - license: MIT
  - posture: `pattern-only`
  - absorbed: outline.xml, patch-NN replay, final.xml/final.html, version snapshots.
- `jim60105/HeartReverie`
  - HEAD: `c79fc28bdaee1a10e5cf0f3f96735fad2f414b18`
  - license: AGPL-3.0
  - posture: `pattern-only`
  - absorbed: markdown story/lore files, reader-writer loop, plugin manifest boundaries.
- `wzxsph/Novel-Claude`
  - HEAD: `dfe59c1e99677638b33d9974b3a79acd4364acb4`
  - license: GPL-3.0
  - posture: `pattern-only`
  - absorbed: microkernel/plugin architecture, EventBus, PluginManager, context isolation.
- `liaoma1993/aiAIfiction`
  - HEAD: `5c86b56a898895adec00889d70e328fa25195ab3`
  - license: no GitHub license detected
  - posture: `pattern-only`
  - absorbed: abstract style learning Skill, representative sampling, quality audit, repair dashboard.
- `vishnu0120754/ReNovel-AI`
  - HEAD: `2afcbf730e5b586e82ef9076117918a124e4f17a`
  - license: GPL-3.0
  - posture: `pattern-only`
  - absorbed: memory-backed revision workspace and card-based editing boundary.
- `worldwonderer/zenstory`
  - HEAD: `7006d11e7fc45ec0ccc9f2c676a0fe266de92824`
  - license: MIT
  - posture: `pattern-only`
  - absorbed: agent-operated writing files, reference deconstruction, hybrid RAG, quality reviewer.

`Anshler/graphify-novel` was still not promoted because the GitHub repository API returned 404 during this pass.

## New patterns

- `local_rag_writing_ide_gate`
  - Keep accepted canon, author notes, and source-deconstruction material in separated retrieval scopes.
  - Preview retrieved chunks before drafting so reference material cannot masquerade as canon.
- `canon_drift_continuity_qa_gate`
  - Treat story-bible continuity QA as a blocking gate before chapter acceptance.
  - Scene context packs should contain only the facts needed for the current scene/revision.
- `patch_replay_manuscript_state_gate`
  - Store generation and edits as ordered patches.
  - The current manuscript must be reconstructable from outline plus accepted patches.
- `microkernel_skill_plugin_isolation_gate`
  - Treat skills/plugins as isolated stages with contracts, validation, and failure containment.
  - Generated or third-party skills remain pattern-only during source intake.
- `interactive_reader_writer_loop_gate`
  - Separate reader guidance, author edits, assistant suggestions, and accepted chapter files.
  - User-guided plot turns become state deltas before canon write-back.
- `abstract_style_learning_skill_gate`
  - Extract abstract craft axes from style samples: pacing, sentence rhythm, scene construction, dialogue function, emotion landing, repair rules.
  - Do not persist source prose, names, plot facts, or distinctive expressions in reusable style profiles.

## Local adaptation

本项目的拆书续写和同类型仿写链路需要新增一组 gate：

1. 拆书材料进入 RAG 前标记为 `source_analysis`、`accepted_canon` 或 `style_only`。
2. 续写前运行 canon drift QA；失败项进入硬约束，不作为普通润色建议。
3. 章节生成/修订写入 patch replay 记录，避免直接覆盖已验收正文。
4. 外部 skill/plugin 只吸收 stage contract，不导入提示词正文或安装脚本。
5. 同类型仿写只继承抽象技法，不继承源书事实、专名、事件顺序或句段表达。

## Verification target

- `backend/app/services/source_discovery_service.py` exposes six new workflow patterns and hint builders.
- `backend/app/services/source_pattern_pack_prompt.py` includes the six new hint groups in digest rendering.
- `frontend/src/components/book-remix/BookRemixSourceDiscoveryPanel.tsx` pins the new local RAG / canon QA / patch replay group.
- Tests cover default seeds, metadata-to-pattern mapping, digest exposure, and UI copy.
