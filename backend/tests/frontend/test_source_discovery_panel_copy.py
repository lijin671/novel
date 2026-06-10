import json
import re
from pathlib import Path


def test_source_discovery_panel_surfaces_inspired_pattern_pack_fields():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    types = repo_root / "frontend" / "src" / "types" / "sourceDiscovery.ts"

    panel_text = panel.read_text(encoding="utf-8")
    types_text = types.read_text(encoding="utf-8")

    for field in (
        "continuation_prompt_hints",
        "style_signature_hints",
        "structured_generation_hints",
        "card_workbench_hints",
        "context_reference_hints",
        "scene_asset_pipeline_hints",
        "publication_pipeline_hints",
        "self_review_policy_hints",
        "inspired_mapping_targets",
        "inspired_prompt_hints",
        "inspired_transformation_hints",
        "inspired_copy_risk_hints",
        "lorebook_context_hints",
        "author_note_layer_hints",
        "world_state_tracking_hints",
        "memory_snapshot_versioning_hints",
        "quality_score_loop_hints",
        "voice_fingerprint_hints",
        "anti_slop_audit_hints",
        "bookrun_audit_trail_gate_hints",
        "provider_budget_smoke_gate_hints",
        "sidecar_memory_profile_boundary_hints",
        "outline_checkpoint_milestone_gate_hints",
        "language_localization_style_profile_gate_hints",
        "progressive_disclosure_skill_protocol_gate_hints",
        "anti_slop_rulepack_triage_gate_hints",
        "user_modifier_project_blueprint_gate_hints",
        "portable_canon_skill_runtime_gate_hints",
        "staged_outline_chunk_window_gate_hints",
        "wiki_canon_graph_lint_gate_hints",
        "plan_draft_log_verify_loop_gate_hints",
        "mcp_scene_index_revision_boundary_hints",
        "verbalized_sampling_diversity_wiki_gate_hints",
        "agentic_editorial_pipeline_gate_hints",
        "craft_role_pipeline_hints",
        "branching_choice_graph_hints",
        "choice_stats_consequence_gate_hints",
        "delivery_manuscript_assembly_hints",
        "export_format_fidelity_audit_hints",
        "character_dialogue_persona_memory_hints",
        "anti_repetition_prompt_rules_hints",
        "temporal_canon_context_graph_hints",
        "plotline_thread_tracking_hints",
        "rolling_summary_context_trim_hints",
        "local_first_workspace_hints",
        "prompt_library_hints",
        "scene_level_generation_hints",
        "review_queue_staging_hints",
        "style_guide_layering_hints",
        "entity_schema_custom_fields_hints",
        "content_ref_externalization_hints",
        "graph_healing_hints",
        "contradiction_detection_hints",
        "graph_branching_atomicity_hints",
        "query_lint_contract_hints",
        "premature_ending_guard_hints",
        "layered_memory_model_hints",
        "plot_dependency_graph_hints",
        "plotgrid_scene_matrix_hints",
        "scene_status_dashboard_hints",
        "gradual_reveal_control_hints",
        "setup_payoff_tracking_hints",
        "scene_type_directing_hints",
        "worldpkg_export_hints",
        "alternate_timeline_branching_hints",
        "divergence_guidance_hints",
        "plain_text_project_storage_hints",
        "synopsis_cross_reference_hints",
        "snowflake_premise_expansion_hints",
        "outliner_index_cards_hints",
        "narrative_strand_mapping_hints",
        "character_depth_interview_hints",
        "mindmap_visual_planning_hints",
        "manuscript_export_formats_hints",
        "causal_dramatica_agent_pipeline_hints",
        "capture_distillation_production_gate_hints",
        "skill_orchestrated_chinese_novel_workflow_hints",
        "langgraph_story_state_machine_hints",
        "story_daemon_evolution_loop_hints",
        "local_rag_writing_ide_gate_hints",
        "canon_drift_continuity_qa_gate_hints",
        "patch_replay_manuscript_state_gate_hints",
        "microkernel_skill_plugin_isolation_gate_hints",
        "interactive_reader_writer_loop_gate_hints",
        "abstract_style_learning_skill_gate_hints",
        "impromptu_thread_pool_chapter_gate_hints",
        "offline_inspiration_bank_style_gate_hints",
        "atelier_phase_pipeline_gate_hints",
            "book_mining_genesis_automation_gate_hints",
            "multi_book_autopilot_studio_gate_hints",
            "longrun_commit_projection_health_gate_hints",
            "fresh_context_chapter_iteration_gate_hints",
            "agentwrite_plan_write_pipeline_hints",
            "long_output_length_quality_ruler_hints",
            "long_context_reward_dimension_gate_hints",
            "instance_specific_writing_criteria_gate_hints",
            "material_grounded_query_refinement_hints",
            "hybrid_rubric_pairwise_elo_judge_hints",
            "judge_bias_mitigation_check_hints",
            "plan_reflect_character_chapter_pipeline_hints",
            "human_story_metric_panel_hints",
            "hierarchical_cowriting_story_scaffold_hints",
            "human_coauthor_edit_boundary_hints",
            "recursive_reprompt_revision_loop_hints",
            "reranker_guided_candidate_selection_hints",
            "event_to_sentence_realization_trace_hints",
            "entity_memory_slotfill_grounding_hints",
            "book_memory_bank_context_lattice_hints",
            "spec_driven_fiction_scene_tasks_hints",
            "toc_aware_source_deconstruction_hints",
            "two_pass_context_glossary_pipeline_hints",
            "inline_author_edit_markup_versioning_hints",
            "long_term_author_preference_memory_hints",
            "community_graph_source_deconstruction_hints",
            "dual_level_graph_vector_retrieval_hints",
            "schema_guided_graph_extraction_hints",
            "counterfactual_story_graph_rag_gate_hints",
            "character_knowledge_timeline_gate_hints",
            "living_codex_editorial_workbench_gate_hints",
            "agent_role_profile_workflow_gate_hints",
            "chinese_segmentation_keyword_gate_hints",
            "chinese_ner_alias_consistency_gate_hints",
            "chinese_text_normalization_gate_hints",
            "chinese_error_correction_review_gate_hints",
            "literary_event_entity_annotation_gate_hints",
            "narrative_event_evolution_graph_gate_hints",
            "sentiment_arc_emotion_trajectory_gate_hints",
            "cross_context_coreference_gate_hints",
            "character_interaction_network_gate_hints",
            "character_quote_attribution_map_hints",
            "readability_pacing_metric_gate_hints",
            "lexical_diversity_voice_audit_hints",
            "keyphrase_motif_extraction_hints",
            "semantic_chunk_boundary_map_hints",
            "chapter_summary_anchor_gate_hints",
            "topic_drift_map_hints",
            "context_faithfulness_eval_gate_hints",
            "retrieval_trace_observability_gate_hints",
            "prompt_regression_eval_suite_hints",
            "source_text_fingerprint_gate_hints",
            "fuzzy_phrase_similarity_gate_hints",
            "diff_span_copy_review_hints",
            "minhash_lsh_near_duplicate_gate_hints",
            "simhash_hamming_similarity_gate_hints",
            "semantic_duplicate_cluster_gate_hints",
            "embedding_similarity_independence_gate_hints",
            "style_axis_diversity_fingerprint_hints",
            "stylometric_author_fingerprint_gate_hints",
            "function_word_syntax_style_gate_hints",
            "authorship_attribution_similarity_gate_hints",
            "style_overfit_regression_gate_hints",
            "paraphrase_independence_review_gate_hints",
            "ai_prose_fingerprint_cluster_gate_hints",
            "trope_inventory_similarity_gate_hints",
            "trope_graph_expectation_map_hints",
            "trope_density_novelty_budget_hints",
            "trope_source_boundary_review_hints",
            "reader_retention_review_gate_hints",
            "serial_reader_reward_contract_gate_hints",
            "reader_rating_signal_model_hints",
            "review_spoiler_sentiment_corpus_hints",
            "beta_reader_archetype_panel_hints",
            "comp_title_market_positioning_hints",
            "local_reader_experience_editor_hints",
            "prose_lint_style_rule_gate_hints",
            "grammar_spelling_copyedit_gate_hints",
            "copyedit_diagnostic_triage_queue_hints",
            "reader_reward_channel_gate_hints",
            "tri_modal_workflow_validation_gate_hints",
            "scene_promise_mob_review_gate_hints",
            "webnovel_genre_tracker_gate_hints",
            "simulation_causal_ledger_verification_gate_hints",
            "writer_git_exploration_review_gate_hints",
            "narrative_qa_comprehension_gate_hints",
            "chapter_summary_alignment_gate_hints",
            "story_question_answer_validation_gate_hints",
            "causal_why_explanation_gate_hints",
            "story_commonsense_consistency_gate_hints",
            "query_focused_long_summary_gate_hints",
            "source_license_detection_gate_hints",
            "spdx_reuse_compliance_gate_hints",
            "public_domain_corpus_boundary_hints",
            "attribution_derivative_work_gate_hints",
            "source_entity_redaction_gate_hints",
            "custom_entity_label_inventory_hints",
            "placeholder_alias_consistency_map_hints",
            "proper_noun_leakage_review_hints",
            "source_format_import_manifest_hints",
            "pdf_layout_text_extraction_gate_hints",
            "ocr_scanned_page_import_gate_hints",
            "document_partition_chapter_detection_gate_hints",
            "import_provenance_checksum_gate_hints",
            "epub_structure_validation_gate_hints",
            "ebook_accessibility_audit_gate_hints",
            "front_back_matter_metadata_gate_hints",
            "toc_navigation_consistency_gate_hints",
        ):
        assert field in types_text
        assert field in panel_text

    assert "Core remix kernel gates" in panel_text
    assert "default_github_queries" in types_text
    assert "default_github_queries" in panel_text
    assert "default_github_repository_urls" in types_text
    assert "default_github_repository_urls" in panel_text
    assert "default_linux_do_rss_urls" in types_text
    assert "default_linux_do_rss_urls" in panel_text
    assert "repositorySeedsEdited" in panel_text
    assert "githubQueriesEdited" in panel_text
    assert "linuxDoRssUrlsEdited" in panel_text
    assert "后端默认 seed" in panel_text
    assert "GitHub Search 查询" in panel_text
    assert "Community RSS 来源" in panel_text
    assert "只按换行拆分" in panel_text
    assert "Continuation prompt hints" in panel_text
    assert "Style signature hints" in panel_text
    assert "Structured generation hints" in panel_text
    assert "Card workbench hints" in panel_text
    assert "Context reference hints" in panel_text
    assert "Scene asset pipeline hints" in panel_text
    assert "Publication pipeline hints" in panel_text
    assert "Self-review policy hints" in panel_text
    assert "Inspired mapping targets" in panel_text
    assert "Inspired copy-risk hints" in panel_text
    assert "Lorebook context hints" in panel_text
    assert "Memory snapshot versioning hints" in panel_text
    assert "BookRun / skill protocol gates" in panel_text
    assert "Project workbench / memory diversity gates" in panel_text
    assert "Provider budget smoke gates" in panel_text
    assert "Wiki canon graph lint gates" in panel_text
    assert "Authorial agents / interactive delivery gates" in panel_text
    assert "Agentic editorial pipeline gates" in panel_text
    assert "Branching choice graph gates" in panel_text
    assert "Export format fidelity audit gates" in panel_text
    assert "Voice / timeline continuity gates" in panel_text
    assert "Character dialogue persona memory gates" in panel_text
    assert "Anti-repetition prompt rule gates" in panel_text
    assert "Temporal canon context graph gates" in panel_text
    assert "Workspace / scene planning gates" in panel_text
    assert "Local-first workspace gates" in panel_text
    assert "Prompt library gates" in panel_text
    assert "Scene-level generation gates" in panel_text
    assert "Review queue staging gates" in panel_text
    assert "Style guide layering gates" in panel_text
    assert "Entity schema custom field gates" in panel_text
    assert "ContentRef externalization gates" in panel_text
    assert "Graph healing gates" in panel_text
    assert "Contradiction detection gates" in panel_text
    assert "Graph branching atomicity gates" in panel_text
    assert "Query lint contract gates" in panel_text
    assert "Plotgrid / reveal / branch gates" in panel_text
    assert "Premature ending guards" in panel_text
    assert "Layered memory model gates" in panel_text
    assert "Plot dependency graph gates" in panel_text
    assert "Plotgrid scene matrix gates" in panel_text
    assert "Scene status dashboard gates" in panel_text
    assert "Gradual reveal control gates" in panel_text
    assert "Setup / payoff tracking gates" in panel_text
    assert "Scene type directing gates" in panel_text
    assert "WorldPkg export gates" in panel_text
    assert "Alternate timeline branching gates" in panel_text
    assert "Divergence guidance gates" in panel_text
    assert "Mature manuscript planning gates" in panel_text
    assert "Plain text project storage gates" in panel_text
    assert "Synopsis cross-reference gates" in panel_text
    assert "Snowflake premise expansion gates" in panel_text
    assert "Outliner index-card gates" in panel_text
    assert "Narrative strand mapping gates" in panel_text
    assert "Character depth interview gates" in panel_text
    assert "Mindmap visual planning gates" in panel_text
    assert "Manuscript export format gates" in panel_text
    assert "Causal state-machine / skill workflow gates" in panel_text
    assert "Causal Dramatica agent pipeline gates" in panel_text
    assert "Capture distillation production gates" in panel_text
    assert "Skill-orchestrated Chinese novel workflow gates" in panel_text
    assert "LangGraph story state machine gates" in panel_text
    assert "Agent role profile workflow gates" in panel_text
    assert "Story daemon evolution loop gates" in panel_text
    assert "Local RAG / canon QA / patch replay gates" in panel_text
    assert "Local RAG writing IDE gates" in panel_text
    assert "Canon drift continuity QA gates" in panel_text
    assert "Patch replay manuscript state gates" in panel_text
    assert "Microkernel skill plugin isolation gates" in panel_text
    assert "Interactive reader-writer loop gates" in panel_text
    assert "Abstract style learning skill gates" in panel_text
    assert "Impromptu / offline / atelier gates" in panel_text
    assert "Impromptu thread-pool chapter gates" in panel_text
    assert "Offline inspiration-bank style gates" in panel_text
    assert "Atelier phase pipeline gates" in panel_text
    assert "Book-mining / autopilot / longrun gates" in panel_text
    assert "Book mining genesis automation gates" in panel_text
    assert "Multi-book autopilot studio gates" in panel_text
    assert "Longrun commit projection health gates" in panel_text
    assert "Fresh-context chapter iteration gates" in panel_text
    assert "Long-output planning / reward gates" in panel_text
    assert "AgentWrite plan-write pipeline gates" in panel_text
    assert "Long-output length quality ruler gates" in panel_text
    assert "Long-context reward dimension gates" in panel_text
    assert "Writing benchmark / judge gates" in panel_text
    assert "Instance-specific writing criteria gates" in panel_text
    assert "Material-grounded query refinement gates" in panel_text
    assert "Hybrid rubric pairwise Elo judge gates" in panel_text
    assert "Judge bias mitigation checks" in panel_text
    assert "Plan-reflect character chapter pipeline gates" in panel_text
    assert "Human story metric panel gates" in panel_text
    assert "Co-writing / recursive revision gates" in panel_text
    assert "Hierarchical co-writing story scaffold gates" in panel_text
    assert "Human coauthor edit boundaries" in panel_text
    assert "Recursive reprompt revision loop gates" in panel_text
    assert "Reranker-guided candidate selection gates" in panel_text
    assert "Event-to-sentence realization trace gates" in panel_text
    assert "Entity memory slotfill grounding gates" in panel_text
    assert "Source deconstruction / memory glossary gates" in panel_text
    assert "Book memory-bank context lattice gates" in panel_text
    assert "Spec-driven fiction scene task gates" in panel_text
    assert "TOC-aware source deconstruction gates" in panel_text
    assert "Two-pass context glossary pipeline gates" in panel_text
    assert "Inline author edit markup versioning gates" in panel_text
    assert "Graph memory / retrieval grounding gates" in panel_text
    assert "Long-term author preference memory gates" in panel_text
    assert "Community graph source deconstruction gates" in panel_text
    assert "Dual-level graph vector retrieval gates" in panel_text
    assert "Schema-guided graph extraction gates" in panel_text
    assert "Counterfactual story Graph-RAG gates" in panel_text
    assert "Living codex editorial workbench gates" in panel_text
    assert "Relationship graph global replace gates" in panel_text
    assert "Chinese text processing gates" in panel_text
    assert "Chinese segmentation / keyword gates" in panel_text
    assert "Chinese NER / alias consistency gates" in panel_text
    assert "Chinese text normalization gates" in panel_text
    assert "Chinese correction review gates" in panel_text
    assert "Narrative event / emotion graph gates" in panel_text
    assert "Literary event/entity annotation gates" in panel_text
    assert "Narrative event evolution graph gates" in panel_text
    assert "Sentiment arc / emotion trajectory gates" in panel_text
    assert "Cross-context coreference gates" in panel_text
    assert "Character interaction network gates" in panel_text
    assert "Book NLP / readability / motif gates" in panel_text
    assert "Character quote attribution maps" in panel_text
    assert "Readability pacing metric gates" in panel_text
    assert "Lexical diversity voice audits" in panel_text
    assert "Keyphrase motif extraction gates" in panel_text
    assert "Segmentation / summary / RAG eval gates" in panel_text
    assert "Semantic chunk boundary maps" in panel_text
    assert "Chapter summary anchor gates" in panel_text
    assert "Topic drift maps" in panel_text
    assert "Context faithfulness eval gates" in panel_text
    assert "Retrieval trace observability gates" in panel_text
    assert "Prompt regression eval suites" in panel_text
    assert "Copy similarity / near-duplicate gates" in panel_text
    assert "Source text fingerprint gates" in panel_text
    assert "Fuzzy phrase similarity gates" in panel_text
    assert "Diff-span copy review gates" in panel_text
    assert "MinHash / LSH near-duplicate gates" in panel_text
    assert "SimHash / Hamming similarity gates" in panel_text
    assert "Semantic duplicate cluster gates" in panel_text
    assert "Embedding similarity independence gates" in panel_text
    assert "Stylometry / style overfit gates" in panel_text
    assert "Style-axis diversity fingerprint gates" in panel_text
    assert "Stylometric author fingerprint gates" in panel_text
    assert "Function-word / syntax style gates" in panel_text
    assert "Authorship attribution similarity gates" in panel_text
    assert "Style-overfit regression gates" in panel_text
    assert "Paraphrase independence review gates" in panel_text
    assert "AI-prose fingerprint cluster gates" in panel_text
    assert "Trope / genre independence gates" in panel_text
    assert "Trope inventory similarity gates" in panel_text
    assert "Trope graph expectation map gates" in panel_text
    assert "Trope density novelty-budget gates" in panel_text
    assert "Trope source boundary review gates" in panel_text
    assert "Reader feedback / market positioning gates" in panel_text
    assert "Reader retention review gates" in panel_text
    assert "Serial reader-reward contract gates" in panel_text
    assert "Reader rating signal model gates" in panel_text
    assert "Review spoiler / sentiment corpus gates" in panel_text
    assert "Beta-reader archetype panel gates" in panel_text
    assert "Comp-title market positioning gates" in panel_text
    assert "Local reader-experience editor gates" in panel_text
    assert "Prose lint / grammar copyedit gates" in panel_text
    assert "Prose lint style rule gates" in panel_text
    assert "Grammar spelling copyedit gates" in panel_text
    assert "Copyedit diagnostic triage queue gates" in panel_text
    assert "Reader reward / tri-modal audit gates" in panel_text
    assert "Reader reward channel gates" in panel_text
    assert "Tri-modal workflow validation gates" in panel_text
    assert "Scene promise / serial simulation review gates" in panel_text
    assert "Scene promise mob-review gates" in panel_text
    assert "Webnovel genre tracker gates" in panel_text
    assert "Simulation causal-ledger verification gates" in panel_text
    assert "Writer Git exploration review gates" in panel_text
    assert "Narrative QA / summary / causality gates" in panel_text
    assert "Narrative QA comprehension gates" in panel_text
    assert "Chapter summary alignment gates" in panel_text
    assert "Story question-answer validation gates" in panel_text
    assert "Causal why-explanation gates" in panel_text
    assert "Story commonsense consistency gates" in panel_text
    assert "Query-focused long-summary gates" in panel_text
    assert "Rights / corpus admission gates" in panel_text
    assert "Source license detection gates" in panel_text
    assert "SPDX / REUSE compliance gates" in panel_text
    assert "Public-domain corpus boundaries" in panel_text
    assert "Attribution / derivative-work gates" in panel_text
    assert "Entity redaction / leakage gates" in panel_text
    assert "Source entity redaction gates" in panel_text
    assert "Custom fiction entity label inventories" in panel_text
    assert "Placeholder alias consistency maps" in panel_text
    assert "Proper-noun leakage reviews" in panel_text
    assert "Source import / chapter extraction gates" in panel_text
    assert "Source format import manifests" in panel_text
    assert "PDF layout text extraction gates" in panel_text
    assert "OCR scanned-page import gates" in panel_text
    assert "Document partition chapter detection gates" in panel_text
    assert "Import provenance checksum gates" in panel_text
    assert "EPUB structure / publication QA gates" in panel_text
    assert "EPUB structure validation gates" in panel_text
    assert "Ebook accessibility audit gates" in panel_text
    assert "Front/back matter metadata gates" in panel_text
    assert "TOC navigation consistency gates" in panel_text


def test_source_discovery_panel_uses_compact_seed_fallback_and_backend_registry_hydration():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    panel_text = panel.read_text(encoding="utf-8")

    panel_block = panel_text.split("const DEFAULT_GITHUB_REPOSITORY_SEEDS = [", 1)[1].split("\n];", 1)[0]
    fallback_urls = re.findall(r"'(https://github.com/[^']+)'", panel_block)

    assert fallback_urls == [
        "https://github.com/voocel/ainovel-cli",
        "https://github.com/NousResearch/autonovel",
        "https://github.com/MangoLion/plotbunni",
        "https://github.com/zlx362211854/novelforge-agent",
        "https://github.com/MissingDanial/StyleMuse",
        "https://github.com/mert-ozdemirr/sherlock-counterfactual-modular-graph-rag",
        "https://github.com/booknlp/booknlp",
        "https://github.com/google-deepmind/narrativeqa",
    ]
    assert len(fallback_urls) <= 8
    assert "default_github_repository_urls" in panel_text
    assert "default_github_queries" in panel_text
    assert "default_linux_do_rss_urls" in panel_text
    assert "!repositorySeedsEdited && result.default_github_repository_urls?.length" in panel_text
    assert "!githubQueriesEdited && result.default_github_queries?.length" in panel_text
    assert "!linuxDoRssUrlsEdited && result.default_linux_do_rss_urls?.length" in panel_text
    assert "result.default_github_repository_urls.join('\\n')" in panel_text
    assert "result.default_github_queries.join('\\n')" in panel_text
    assert "result.default_linux_do_rss_urls.join('\\n')" in panel_text
    assert "parseLineItems(githubQueries)" in panel_text
    assert "GitHub Search" in panel_text
    assert "Community RSS" in panel_text


def test_source_discovery_panel_has_dynamic_fallback_for_unpinned_hint_groups():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    pattern_pack = repo_root / "backend" / "app" / "references" / "novel-source-pattern-pack-2026-06-10.json"

    panel_text = panel.read_text(encoding="utf-8")
    pack = json.loads(pattern_pack.read_text(encoding="utf-8"))
    explicitly_rendered_fields = set(re.findall(r"patternPackPayload\?\.([a-zA-Z0-9_]+)", panel_text))
    dynamic_hint_fields = [
        key
        for key, value in pack.items()
        if key.endswith("_hints")
        and isinstance(value, list)
        and value
        and key not in explicitly_rendered_fields
    ]

    assert len(dynamic_hint_fields) > 60
    assert "Additional source-discovered gates" in panel_text
    assert "collectAdditionalHintBlocks" in panel_text
    assert "key.endsWith('_hints')" in panel_text
    assert "!PINNED_HINT_KEYS.has(key)" in panel_text


def test_source_discovery_panel_surfaces_workflow_pattern_evidence():
    repo_root = Path(__file__).resolve().parents[3]
    panel = repo_root / "frontend" / "src" / "components" / "book-remix" / "BookRemixSourceDiscoveryPanel.tsx"
    panel_text = panel.read_text(encoding="utf-8")

    assert "Workflow pattern evidence" in panel_text
    assert "collectWorkflowPatternEvidence" in panel_text
    assert "renderWorkflowPatternEvidence" in panel_text
    assert "WORKFLOW_PATTERN_EVIDENCE_LIMIT" in panel_text
    assert "WORKFLOW_PATTERN_SOURCE_LIMIT" in panel_text
    assert "pattern.top_source_url" in panel_text
    assert "pattern.sources" in panel_text
    assert "source.posture" in panel_text
    assert "pattern-only 静态吸收" in panel_text
    assert "不 clone、不安装、不执行" in panel_text
