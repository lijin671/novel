# Multi-metric similarity preview projection

Date: 2026-06-15

## Source posture

This projection uses the static evidence recorded in
`novel-source-discovery-2026-06-12-originality-style-safety.md`.

Pattern-only sources:

- `CSOAI-ORG/plagiarism-checker-ai-mcp`
  - pattern: `originality_report_multimetric_gate`
- `Saarah-Saeed/AI_Plagiarism_Detector`
  - pattern: `semantic_stylometric_overlap_gate`

No clone, install, MCP/server launch, Streamlit/UI runtime, Docker, dataset
ingestion, web scraping, browser control, provider/API call, private manuscript
upload, detector execution, or generated rewrite pipeline was performed.

## Absorbed pattern

The remix preview now treats originality and similarity reports as report
vocabulary and acceptance evidence, not runtime services.

Projected gates:

1. `originality_report_multimetric_gate`
   - require report id and source overlap span manifest
   - combine n-gram overlap, sequence matches, stylometric distance,
     citation/source checks, and reviewer notes
   - require transform/hold/reject decisions for risky spans before generation

2. `semantic_stylometric_overlap_gate`
   - check semantic similarity, TF-IDF keyword skeleton, and stylometric
     resemblance
   - record threshold version, reviewer notes, and section-level risk labels
   - reject close paraphrase even when exact wording changed

## Project projection

Continuation context now exposes:

- control axes for multi-metric originality reports, source overlap span
  manifests, transform decisions, semantic/stylometric similarity reports,
  paraphrase-structure risk, and reviewer thresholds
- warning buckets:
  - `originality_report_multimetric_warnings`
  - `semantic_stylometric_overlap_warnings`
- same-type independence checks that transfer only report shape while requiring
  new source-span namespaces, transform-action namespaces, semantic function
  remaps, keyword skeleton remaps, and threshold versions

## Runtime boundary

This is static projection only. Runtime originality checking, external detector
services, source upload, web similarity lookup, scraping, and API/provider use
remain deferred until a separate local safety contract exists.
