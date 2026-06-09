"""Render source-discovery pattern packs into compact prompt guidance."""

from __future__ import annotations

from typing import Any, Optional


def render_source_pattern_pack_digest(
    source_pattern_pack: Optional[dict[str, Any]],
    *,
    empty_message: str = "(no public source pattern pack; use only local project canon.)",
    include_inspired_guidance: bool = True,
) -> str:
    """Convert the latest source-discovery pattern pack into prompt-safe bullets."""
    if not source_pattern_pack:
        return empty_message

    lines: list[str] = []
    workflow_patterns = _as_dict_list(source_pattern_pack.get("workflow_patterns"))
    if workflow_patterns:
        lines.append("- workflow_patterns:")
        for pattern in workflow_patterns[:8]:
            name = str(pattern.get("name") or "").strip()
            if not name:
                continue
            count = pattern.get("candidate_count") or 0
            top_source_url = str(pattern.get("top_source_url") or "").strip()
            posture_hint = str(pattern.get("posture_hint") or "").strip()
            risk_flags = _as_note_list(pattern.get("risk_flags"))
            trust_flags = _as_note_list(pattern.get("trust_flags"))
            posture_text = f"; posture_hint: {posture_hint}" if posture_hint else ""
            risk_text = f"; risk_flags: {', '.join(risk_flags[:5])}" if risk_flags else ""
            trust_text = f"; trust_flags: {', '.join(trust_flags[:5])}" if trust_flags else ""
            source_text = f"; top_source: {top_source_url}" if top_source_url else ""
            lines.append(f"  - {name} (candidates: {count}{source_text}{posture_text}{risk_text}{trust_text})")

    bible_targets = _as_note_list(source_pattern_pack.get("bible_enrichment_targets"))
    if bible_targets:
        lines.append("- bible_enrichment_targets: " + ", ".join(bible_targets[:12]))

    whole_book_targets = _as_note_list(source_pattern_pack.get("whole_book_analysis_targets"))
    if whole_book_targets:
        lines.append("- whole_book_analysis_targets: " + ", ".join(whole_book_targets[:14]))

    continuation_hints = _as_note_list(source_pattern_pack.get("continuation_prompt_hints"))
    if continuation_hints:
        lines.append("- continuation_prompt_hints:")
        for hint in continuation_hints[:8]:
            lines.append(f"  - {hint}")

    continuation_state_hints = _as_note_list(source_pattern_pack.get("continuation_state_hints"))
    if continuation_state_hints:
        lines.append("- continuation_state_hints:")
        for hint in continuation_state_hints[:8]:
            lines.append(f"  - {hint}")

    style_hints = _as_note_list(source_pattern_pack.get("style_signature_hints"))
    if style_hints:
        lines.append("- style_signature_hints:")
        for hint in style_hints[:6]:
            lines.append(f"  - {hint}")

    style_fidelity_hints = _as_note_list(source_pattern_pack.get("style_fidelity_hints"))
    if style_fidelity_hints:
        lines.append("- style_fidelity_hints:")
        for hint in style_fidelity_hints[:6]:
            lines.append(f"  - {hint}")

    structured_generation_hints = _as_note_list(source_pattern_pack.get("structured_generation_hints"))
    if structured_generation_hints:
        lines.append("- structured_generation_hints:")
        for hint in structured_generation_hints[:6]:
            lines.append(f"  - {hint}")

    card_workbench_hints = _as_note_list(source_pattern_pack.get("card_workbench_hints"))
    if card_workbench_hints:
        lines.append("- card_workbench_hints:")
        for hint in card_workbench_hints[:6]:
            lines.append(f"  - {hint}")

    context_reference_hints = _as_note_list(source_pattern_pack.get("context_reference_hints"))
    if context_reference_hints:
        lines.append("- context_reference_hints:")
        for hint in context_reference_hints[:6]:
            lines.append(f"  - {hint}")

    scene_asset_pipeline_hints = _as_note_list(source_pattern_pack.get("scene_asset_pipeline_hints"))
    if scene_asset_pipeline_hints:
        lines.append("- scene_asset_pipeline_hints:")
        for hint in scene_asset_pipeline_hints[:6]:
            lines.append(f"  - {hint}")

    quality_score_loop_hints = _as_note_list(source_pattern_pack.get("quality_score_loop_hints"))
    if quality_score_loop_hints:
        lines.append("- quality_score_loop_hints:")
        for hint in quality_score_loop_hints[:6]:
            lines.append(f"  - {hint}")

    voice_fingerprint_hints = _as_note_list(source_pattern_pack.get("voice_fingerprint_hints"))
    if voice_fingerprint_hints:
        lines.append("- voice_fingerprint_hints:")
        for hint in voice_fingerprint_hints[:6]:
            lines.append(f"  - {hint}")

    anti_slop_audit_hints = _as_note_list(source_pattern_pack.get("anti_slop_audit_hints"))
    if anti_slop_audit_hints:
        lines.append("- anti_slop_audit_hints:")
        for hint in anti_slop_audit_hints[:6]:
            lines.append(f"  - {hint}")

    publication_pipeline_hints = _as_note_list(source_pattern_pack.get("publication_pipeline_hints"))
    if publication_pipeline_hints:
        lines.append("- publication_pipeline_hints:")
        for hint in publication_pipeline_hints[:6]:
            lines.append(f"  - {hint}")

    lorebook_context_hints = _as_note_list(source_pattern_pack.get("lorebook_context_hints"))
    if lorebook_context_hints:
        lines.append("- lorebook_context_hints:")
        for hint in lorebook_context_hints[:6]:
            lines.append(f"  - {hint}")

    author_note_layer_hints = _as_note_list(source_pattern_pack.get("author_note_layer_hints"))
    if author_note_layer_hints:
        lines.append("- author_note_layer_hints:")
        for hint in author_note_layer_hints[:6]:
            lines.append(f"  - {hint}")

    world_state_tracking_hints = _as_note_list(source_pattern_pack.get("world_state_tracking_hints"))
    if world_state_tracking_hints:
        lines.append("- world_state_tracking_hints:")
        for hint in world_state_tracking_hints[:6]:
            lines.append(f"  - {hint}")

    memory_snapshot_versioning_hints = _as_note_list(source_pattern_pack.get("memory_snapshot_versioning_hints"))
    if memory_snapshot_versioning_hints:
        lines.append("- memory_snapshot_versioning_hints:")
        for hint in memory_snapshot_versioning_hints[:6]:
            lines.append(f"  - {hint}")

    local_first_workspace_hints = _as_note_list(source_pattern_pack.get("local_first_workspace_hints"))
    if local_first_workspace_hints:
        lines.append("- local_first_workspace_hints:")
        for hint in local_first_workspace_hints[:6]:
            lines.append(f"  - {hint}")

    prompt_library_hints = _as_note_list(source_pattern_pack.get("prompt_library_hints"))
    if prompt_library_hints:
        lines.append("- prompt_library_hints:")
        for hint in prompt_library_hints[:6]:
            lines.append(f"  - {hint}")

    style_guide_layering_hints = _as_note_list(source_pattern_pack.get("style_guide_layering_hints"))
    if style_guide_layering_hints:
        lines.append("- style_guide_layering_hints:")
        for hint in style_guide_layering_hints[:6]:
            lines.append(f"  - {hint}")

    review_queue_staging_hints = _as_note_list(source_pattern_pack.get("review_queue_staging_hints"))
    if review_queue_staging_hints:
        lines.append("- review_queue_staging_hints:")
        for hint in review_queue_staging_hints[:6]:
            lines.append(f"  - {hint}")

    entity_schema_custom_fields_hints = _as_note_list(source_pattern_pack.get("entity_schema_custom_fields_hints"))
    if entity_schema_custom_fields_hints:
        lines.append("- entity_schema_custom_fields_hints:")
        for hint in entity_schema_custom_fields_hints[:6]:
            lines.append(f"  - {hint}")

    scene_level_generation_hints = _as_note_list(source_pattern_pack.get("scene_level_generation_hints"))
    if scene_level_generation_hints:
        lines.append("- scene_level_generation_hints:")
        for hint in scene_level_generation_hints[:6]:
            lines.append(f"  - {hint}")

    content_ref_externalization_hints = _as_note_list(source_pattern_pack.get("content_ref_externalization_hints"))
    if content_ref_externalization_hints:
        lines.append("- content_ref_externalization_hints:")
        for hint in content_ref_externalization_hints[:6]:
            lines.append(f"  - {hint}")

    graph_healing_hints = _as_note_list(source_pattern_pack.get("graph_healing_hints"))
    if graph_healing_hints:
        lines.append("- graph_healing_hints:")
        for hint in graph_healing_hints[:6]:
            lines.append(f"  - {hint}")

    contradiction_detection_hints = _as_note_list(source_pattern_pack.get("contradiction_detection_hints"))
    if contradiction_detection_hints:
        lines.append("- contradiction_detection_hints:")
        for hint in contradiction_detection_hints[:6]:
            lines.append(f"  - {hint}")

    graph_branching_atomicity_hints = _as_note_list(source_pattern_pack.get("graph_branching_atomicity_hints"))
    if graph_branching_atomicity_hints:
        lines.append("- graph_branching_atomicity_hints:")
        for hint in graph_branching_atomicity_hints[:6]:
            lines.append(f"  - {hint}")

    query_lint_contract_hints = _as_note_list(source_pattern_pack.get("query_lint_contract_hints"))
    if query_lint_contract_hints:
        lines.append("- query_lint_contract_hints:")
        for hint in query_lint_contract_hints[:6]:
            lines.append(f"  - {hint}")

    if include_inspired_guidance:
        inspired_mapping_targets = _as_note_list(source_pattern_pack.get("inspired_mapping_targets"))
        if inspired_mapping_targets:
            lines.append("- inspired_mapping_targets: " + ", ".join(inspired_mapping_targets[:12]))

        inspired_prompt_hints = _as_note_list(source_pattern_pack.get("inspired_prompt_hints"))
        if inspired_prompt_hints:
            lines.append("- inspired_prompt_hints:")
            for hint in inspired_prompt_hints[:6]:
                lines.append(f"  - {hint}")

        inspired_transformation_hints = _as_note_list(source_pattern_pack.get("inspired_transformation_hints"))
        if inspired_transformation_hints:
            lines.append("- inspired_transformation_hints:")
            for hint in inspired_transformation_hints[:6]:
                lines.append(f"  - {hint}")

        inspired_copy_risk_hints = _as_note_list(source_pattern_pack.get("inspired_copy_risk_hints"))
        if inspired_copy_risk_hints:
            lines.append("- inspired_copy_risk_hints:")
            for hint in inspired_copy_risk_hints[:6]:
                lines.append(f"  - {hint}")

    review_hints = _as_note_list(source_pattern_pack.get("self_review_policy_hints"))
    if review_hints:
        lines.append("- self_review_policy_hints:")
        for hint in review_hints[:6]:
            lines.append(f"  - {hint}")

    review_gate_hints = _as_note_list(source_pattern_pack.get("self_review_gate_hints"))
    if review_gate_hints:
        lines.append("- self_review_gate_hints:")
        for hint in review_gate_hints[:6]:
            lines.append(f"  - {hint}")

    chapter_change_hints = _as_note_list(source_pattern_pack.get("chapter_change_package_hints"))
    if chapter_change_hints:
        lines.append("- chapter_change_package_hints:")
        for hint in chapter_change_hints[:6]:
            lines.append(f"  - {hint}")

    safety_constraints = _as_note_list(source_pattern_pack.get("safety_constraints"))
    if safety_constraints:
        lines.append("- safety_constraints:")
        for constraint in safety_constraints[:8]:
            lines.append(f"  - {constraint}")

    source_intake_notes = _as_note_list(source_pattern_pack.get("source_intake_notes"))
    if source_intake_notes:
        lines.append("- source_intake_notes:")
        for note in source_intake_notes[:6]:
            lines.append(f"  - {note}")

    if not lines:
        return "(empty public source pattern pack; do not import external code.)"
    return "\n".join(lines)


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _as_note_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    notes: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            notes.append(text)
    return notes
