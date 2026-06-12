# Novel Source Discovery - Originality and Style Safety

Static intake only. No clone, install, provider call, MCP/server launch, Docker
launch, web scraping, browser control, text upload, or script execution was
performed.

## Sources checked

- `CSOAI-ORG/plagiarism-checker-ai-mcp`
  - HEAD: `03c27c27f918a008974fa9763b1e577c3bac3d71`
  - Pattern: `originality_report_multimetric_gate`
- `Saarah-Saeed/AI_Plagiarism_Detector`
  - HEAD: `4aabd72eb23b70304127079f20a0f38c257508a1`
  - Pattern: `semantic_stylometric_overlap_gate`
- `ShreyaKaushikdev/slopguard`
  - HEAD: `cd49b0799de1b850a54715d6ed70e23edc91b3dd`
  - Pattern: `human_oversight_quality_signal_gate`
- `amaezey/human-eyes`
  - HEAD: `3fb0eb33f90846499c358b2259a11256b79e6bbe`
  - Pattern: `ai_tell_pattern_review_gate`
- `ksanyok/TextHumanize`
  - HEAD: `c536af4626866e8766fde93b36da456a8f371c5c`
  - Pattern: `naturalization_detector_disclaimer_gate`
- `Daksh1092/PLAGIASCAN`
  - HEAD: `9a3a918276a8a7b1771224fde7f311101b1667bf`
  - Pattern: `web_similarity_scrape_boundary_gate`

## Absorbed rules

- 同类型仿写不能只看单一相似度分数；需要 n-gram、序列匹配、语义重叠、关键词骨架与文体距离的组合报告。
- “AI 味”检查只作为确定性模式审阅，不作为“真人写作”证明。
- 质量审阅要看作者选择、取舍、修改理由与具体化证据，而不是只判断是否 AI 生成。
- 文本自然化只能服务于清晰度、语气、节奏与具体性；不得承诺或追求绕过 AI 检测。
- 联网相似度、搜索 API、网页抓取、MCP 原创性检查都需要单独的运行时安全合同。
- 默认不上传私有稿件；相似度报告必须记录来源 URL、匹配段、分数、变换决策和审阅结果。

## Runtime boundary

All six sources stay `pattern-only`. MCP/server packages, pip/npx installers,
Claude/Codex skill installs, release ZIPs, Docker demos, Streamlit/UI runtimes,
datasets/corpora, web scraping, Google/Search APIs, private manuscript upload,
detector testing, and generated rewrite pipelines are deferred until a separate
local safety contract exists.
