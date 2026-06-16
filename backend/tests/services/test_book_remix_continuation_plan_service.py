from __future__ import annotations

import pytest

from app.services.book_remix_continuation_plan_service import BookRemixContinuationPlanService
import app.services.book_remix_continuation_plan_service as plan_service_module


class StubAIService:
    def __init__(self, payload):
        self.payload = payload
        self.calls: list[dict] = []

    async def call_with_json_retry(self, **kwargs):
        self.calls.append(kwargs)
        return self.payload


@pytest.mark.asyncio
async def test_build_plan_payload_from_confirmed_bible_and_user_direction():
    stub_ai_service = StubAIService(
        {
            "summary": "Resolve old ledger hook first, then escalate round two conflict.",
            "stage_goals": [{"goal": "Recover old ledger thread"}],
            "beats": [{"beat": "Reconnect the dropped ledger line"}],
            "priority_hooks": [{"hook": "Old rival returns"}],
            "guardrails": [{"rule": "No sudden new power systems"}],
        }
    )
    service = BookRemixContinuationPlanService(ai_service=stub_ai_service)  # type: ignore[arg-type]

    bible = {
        "generation_status": "confirmed",
        "character_cards": [{"name": "Inspector Lin", "trait": "never trusts easy alibis"}],
        "timeline": [{"event": "Warehouse fire", "impact": "destroyed the original ledger"}],
        "story_arcs": [{"name": "Ledger arc", "status": "open"}],
        "foreshadows": [{"hook": "Old rival", "status": "open"}],
        "hard_constraints": [{"rule": "Do not abruptly flip protagonist alignment"}],
    }

    plan = await service.build_plan_payload(
        project_title="Continuation Desk",
        bible=bible,
        user_direction="Connect directly from original ending",
    )

    assert plan["summary"].startswith("Resolve old")
    assert plan["guardrails"][0]["rule"] == "No sudden new power systems"

    assert len(stub_ai_service.calls) == 1
    call = stub_ai_service.calls[0]
    assert call["max_retries"] == 3
    assert call["expected_type"] == "object"
    assert call["auto_mcp"] is False
    assert "Connect directly from original ending" in call["prompt"]
    assert "priority_hooks" in call["prompt"]
    assert "character_cards" in call["prompt"]
    assert "timeline" in call["prompt"]
    assert "Inspector Lin" in call["prompt"]
    assert "Warehouse fire" in call["prompt"]


@pytest.mark.asyncio
async def test_build_plan_payload_requires_confirmed_bible():
    service = BookRemixContinuationPlanService(ai_service=StubAIService({}))  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="confirmed"):
        await service.build_plan_payload(
            project_title="Continuation Desk",
            bible={"generation_status": "generated"},
            user_direction="",
        )


@pytest.mark.asyncio
async def test_build_plan_payload_normalizes_string_arrays_into_structured_items():
    stub_ai_service = StubAIService(
        {
            "summary": "Continue from the ending without dropping timeline continuity.",
            "stage_goals": [
                "Stabilize the immediate aftermath of the secret promise",
            ],
            "beats": [
                "Show the first awkward public interaction after the stairwell scene",
            ],
            "priority_hooks": [
                "Yena has probably noticed something last night",
            ],
            "guardrails": [
                "Do not reset the chapter 200 ending",
            ],
        }
    )
    service = BookRemixContinuationPlanService(ai_service=stub_ai_service)  # type: ignore[arg-type]

    bible = {
        "generation_status": "confirmed",
        "character_cards": [{"name": "Yang Cui", "trait": "guarded"}],
        "timeline": [{"event": "Stairwell promise", "chapter": 200}],
        "story_arcs": [{"name": "Secret relationship arc", "status": "hot"}],
        "foreshadows": [{"hook": "Yena noticed something", "status": "open"}],
        "hard_constraints": [{"rule": "Keep the idol work environment in play"}],
    }

    plan = await service.build_plan_payload(
        project_title="Continuation Desk",
        bible=bible,
        user_direction="",
    )

    assert plan["stage_goals"] == [{"goal": "Stabilize the immediate aftermath of the secret promise"}]
    assert plan["beats"] == [{"beat": "Show the first awkward public interaction after the stairwell scene"}]
    assert plan["priority_hooks"] == [{"hook": "Yena has probably noticed something last night"}]
    assert plan["guardrails"] == [{"rule": "Do not reset the chapter 200 ending"}]


@pytest.mark.asyncio
async def test_build_plan_payload_backfills_when_ai_returns_summary_only():
    stub_ai_service = StubAIService(
        {
            "summary": "Continue directly from the ending and keep the fallout in play.",
            "stage_goals": [],
            "beats": [],
            "priority_hooks": [],
            "guardrails": [],
        }
    )
    service = BookRemixContinuationPlanService(ai_service=stub_ai_service)  # type: ignore[arg-type]

    bible = {
        "generation_status": "confirmed",
        "character_cards": [{"name": "Yang Cui", "core_conflict": "identity conflict under idol pressure"}],
        "timeline": [{"chapter": 200, "event": "The stairwell promise has already happened"}],
        "story_arcs": [{"name": "Secret relationship arc", "status": "hot"}],
        "foreshadows": [{"hook": "Yena has noticed something", "status": "open"}],
        "hard_constraints": [{"rule": "Do not erase the chapter 200 ending"}],
    }

    plan = await service.build_plan_payload(
        project_title="Continuation Desk",
        bible=bible,
        user_direction="",
    )

    assert plan["summary"] == "Continue directly from the ending and keep the fallout in play."
    assert plan["stage_goals"]
    assert plan["beats"]
    assert plan["priority_hooks"]
    assert plan["guardrails"]


@pytest.mark.asyncio
async def test_build_plan_payload_backfills_universal_scene_contract_fields():
    stub_ai_service = StubAIService(
        {
            "summary": "Keep the public archive fallout onstage.",
            "stage_goals": [],
            "beats": [],
            "priority_hooks": [],
            "guardrails": [],
        }
    )
    service = BookRemixContinuationPlanService(ai_service=stub_ai_service)  # type: ignore[arg-type]

    bible = {
        "generation_status": "confirmed",
        "style_signature": {
            "pov": "close third",
            "reader_promise": "public mystery pressure with earned testimony",
            "word_count_target": "10000 Chinese characters",
        },
        "character_cards": [
            {
                "name": "Lin",
                "external_want": "protect the archive witness",
                "internal_need": "trust allies under pressure",
                "cost": "public reputation can collapse",
                "voice_fingerprint": "short guarded answers",
            }
        ],
        "timeline": [
            {
                "chapter_number": 12,
                "event": "The archive seal failed in public",
                "consequence": "the crowd now doubts Lin",
            }
        ],
        "conflicts": [
            {
                "conflict": "Council pressure isolates Lin from the witness",
                "stakes": "if the witness stays silent, Lin becomes the scapegoat",
            }
        ],
        "foreshadows": [{"hook": "The witness knows who broke the seal", "status": "open"}],
        "hard_constraints": [{"rule": "Do not resolve the witness hook off-screen"}],
    }

    plan = await service.build_plan_payload(
        project_title="Universal Scene Contract Desk",
        bible=bible,
        user_direction="Continue with reader-pull and state writeback intact",
    )

    first_beat = plan["beats"][0]
    assert first_beat["status"] == "pending"
    assert first_beat["pov"] == "close third"
    assert first_beat["opening_hook_type"] == "prior-choice consequence"
    assert first_beat["reader_promise"] == "public mystery pressure with earned testimony"
    assert first_beat["goal"] == "protect the archive witness"
    assert first_beat["obstacle"] == "Council pressure isolates Lin from the witness"
    assert first_beat["stakes"] == "if the witness stays silent, Lin becomes the scapegoat"
    assert first_beat["tactic"] == "force the unresolved hook to create an on-page choice"
    assert first_beat["turn"] == "the next decision changes public trust, relationship state, or story knowledge"
    assert first_beat["cost"] == "public reputation can collapse"
    assert first_beat["exit_state"] == "canon state changes and must be written back after acceptance"
    assert first_beat["ending_hook_job"] == "pay off or complicate a carried hook with visible consequence"
    assert first_beat["micro_payoff"] == "change plot, knowledge, relationship, risk, or emotional position"
    assert first_beat["word_count_target"] == "10000 Chinese characters"
    assert first_beat["required_payoff"] == "The witness knows who broke the seal"
    assert first_beat["continuity_fact"] == "The archive seal failed in public"
    assert first_beat["progress_report_delta_required"] == [
        "summary",
        "new_facts",
        "character_changes",
        "hook_deltas",
        "continuity_updates",
        "next_chapter_focus",
        "risks",
    ]


@pytest.mark.asyncio
async def test_build_plan_payload_prompt_requests_universal_chapter_contract_shape():
    stub_ai_service = StubAIService(
        {
            "summary": "Continue from the latest state.",
            "stage_goals": [{"goal": "Keep the latest consequence active"}],
            "beats": [{"beat": "Open on the cost of the previous choice"}],
            "priority_hooks": [{"hook": "The witness knows the culprit"}],
            "guardrails": [{"rule": "No off-screen payoff"}],
        }
    )
    service = BookRemixContinuationPlanService(ai_service=stub_ai_service)  # type: ignore[arg-type]

    await service.build_plan_payload(
        project_title="Prompt Contract Desk",
        bible={
            "generation_status": "confirmed",
            "style_signature": {"reader_promise": "mystery pressure"},
            "timeline": [{"event": "The seal failed in public"}],
            "character_cards": [{"name": "Lin", "goal": "protect the witness"}],
        },
        source_pattern_pack={
            "chapter_contract_scene_beat_gate_hints": ["Chapter contract needs opening hook, obstacle, cost, and exit state."],
            "reader_pull_fresh_reader_gate_hints": ["Fresh reader must identify POV, want, obstacle, stakes, changed exit state, next pull."],
            "progress_report_continuity_writeback_gate_hints": ["Accepted chapters must write back summary, facts, hooks, and risks."],
        },
    )

    prompt = stub_ai_service.calls[0]["prompt"]
    assert "Universal beat contract requirements" in prompt
    assert "opening_hook_type" in prompt
    assert "reader_promise" in prompt
    assert "goal / obstacle / tactic / turn / cost / exit_state" in prompt
    assert "ending_hook_job" in prompt
    assert "micro_payoff" in prompt
    assert "progress_report_delta_required" in prompt


@pytest.mark.asyncio
async def test_build_plan_payload_injects_source_pattern_pack_into_plan_prompt():
    stub_ai_service = StubAIService(
        {
            "summary": "Continue from the latest state with source-style continuity.",
            "stage_goals": [],
            "beats": [],
            "priority_hooks": [],
            "guardrails": [],
        }
    )
    service = BookRemixContinuationPlanService(ai_service=stub_ai_service)  # type: ignore[arg-type]

    bible = {
        "generation_status": "confirmed",
        "character_cards": [{"name": "Yang Cui", "core_conflict": "idol pressure"}],
        "timeline": [{"chapter": 200, "event": "The promise has already happened"}],
        "story_arcs": [{"name": "Secret relationship arc", "status": "hot"}],
        "foreshadows": [{"hook": "Yena noticed something", "status": "open"}],
        "hard_constraints": [{"rule": "Do not erase the chapter 200 ending"}],
    }
    source_pattern_pack = {
        "workflow_patterns": [
            {
                "name": "continuation",
                "candidate_count": 1,
                "top_source_url": "https://github.com/voocel/ainovel-cli",
                "risk_flags": [],
            }
        ],
        "continuation_prompt_hints": ["续写前先读取世界观、时间线、人物卡、组织、情感线。"],
        "style_signature_hints": ["保留原书味道，并把风格签名作为硬约束。"],
        "self_review_policy_hints": ["不限次数自评优化必须有停止条件。"],
        "safety_constraints": ["不克隆、不安装、不执行外部项目。"],
    }

    await service.build_plan_payload(
        project_title="Continuation Desk",
        bible=bible,
        user_direction="Keep the original taste",
        source_pattern_pack=source_pattern_pack,
    )

    prompt = stub_ai_service.calls[0]["prompt"]
    assert "Public source pattern pack" in prompt
    assert "voocel/ainovel-cli" in prompt
    assert "续写前先读取世界观" in prompt
    assert "保留原书味道" in prompt
    assert "不限次数自评优化" in prompt
    assert "不克隆、不安装、不执行外部项目" in prompt


@pytest.mark.asyncio
async def test_build_plan_payload_refreshes_stale_pattern_pack_before_prompt(monkeypatch):
    stub_ai_service = StubAIService(
        {
            "summary": "Continue from latest state.",
            "stage_goals": [],
            "beats": [],
            "priority_hooks": [],
            "guardrails": [],
        }
    )
    service = BookRemixContinuationPlanService(ai_service=stub_ai_service)  # type: ignore[arg-type]
    refresh_calls: list[dict] = []
    load_calls: list[dict] = []

    async def fake_refresh(**kwargs):
        refresh_calls.append(kwargs)
        return {
            "refreshed": True,
            "pattern_pack": {
                "pattern_pack": {
                    "continuation_prompt_hints": ["fresh continuation plan hint"],
                    "self_review_policy_hints": ["fresh unlimited review stop rule"],
                }
            },
        }

    def fake_load_latest(**kwargs):
        load_calls.append(kwargs)
        return {"continuation_prompt_hints": ["stale plan hint that should not be used"]}

    monkeypatch.setattr(
        plan_service_module.source_discovery_service,
        "evaluate_refresh_need",
        lambda **kwargs: {"refresh_needed": True, "reason": "pattern_pack_stale"},
    )
    monkeypatch.setattr(
        plan_service_module.source_discovery_service,
        "refresh_pattern_pack_if_needed",
        fake_refresh,
    )
    monkeypatch.setattr(
        plan_service_module.source_discovery_service,
        "load_latest_pattern_pack",
        fake_load_latest,
    )

    await service.build_plan_payload(
        project_title="Continuation Desk",
        bible={
            "generation_status": "confirmed",
            "timeline": [{"event": "The promise has already happened"}],
            "character_cards": [{"name": "Yang Cui"}],
        },
    )

    assert refresh_calls
    assert refresh_calls[0]["repo_root"] == plan_service_module.PROJECT_ROOT
    assert refresh_calls[0]["force"] is False
    assert load_calls == []
    prompt = stub_ai_service.calls[0]["prompt"]
    assert "fresh continuation plan hint" in prompt
    assert "fresh unlimited review stop rule" in prompt
    assert "stale plan hint that should not be used" not in prompt


@pytest.mark.asyncio
async def test_build_plan_payload_loads_latest_pattern_pack_when_not_provided(monkeypatch):
    stub_ai_service = StubAIService(
        {
            "summary": "Continue from latest state.",
            "stage_goals": [],
            "beats": [],
            "priority_hooks": [],
            "guardrails": [],
        }
    )
    service = BookRemixContinuationPlanService(ai_service=stub_ai_service)  # type: ignore[arg-type]
    resolve_calls: list[dict] = []

    async def fake_resolve(**kwargs):
        resolve_calls.append(kwargs)
        return {
            "continuation_prompt_hints": ["default fresh pattern pack continuation hint"],
            "style_signature_hints": ["default preserve original flavor hint"],
        }

    monkeypatch.setattr(
        plan_service_module.source_discovery_service,
        "resolve_fresh_pattern_pack",
        fake_resolve,
    )

    await service.build_plan_payload(
        project_title="Continuation Desk",
        bible={
            "generation_status": "confirmed",
            "timeline": [{"event": "The promise has already happened"}],
            "character_cards": [{"name": "Yang Cui"}],
        },
    )

    assert resolve_calls
    assert resolve_calls[0]["repo_root"] == plan_service_module.PROJECT_ROOT
    assert "default fresh pattern pack continuation hint" in stub_ai_service.calls[0]["prompt"]
    assert "default preserve original flavor hint" in stub_ai_service.calls[0]["prompt"]
