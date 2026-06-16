from __future__ import annotations

from app.schemas.book_import import BookImportChapter
from app.schemas.book_remix import BookRemixInspiredSeedProfile, BookRemixSeedMapping
from app.services.book_remix_service import BookRemixService


def _chapter(number: int, title: str, content: str, summary: str) -> BookImportChapter:
    return BookImportChapter(
        title=title,
        content=content,
        summary=summary,
        chapter_number=number,
        outline_title=title,
    )


def test_deconstruction_pack_for_continuation_surfaces_universal_contract():
    service = BookRemixService()
    chapters = [
        _chapter(
            1,
            "逃离",
            "林夏在雨夜离开公司。她握着旧徽章，没有回头。\n\n\"别跟来。\"她说。",
            "林夏离开公司，旧徽章成为后续身份线索。",
        ),
        _chapter(
            2,
            "旧站台",
            "站台的灯忽明忽暗。周砚把车票推到她面前，要求她今晚做决定。",
            "周砚要求林夏在离开和留下之间做选择。",
        ),
        _chapter(
            3,
            "未接电话",
            "电话在凌晨三点响起。屏幕上的名字让林夏停住脚步。她知道这不是结束。",
            "旧组织在凌晨联系林夏，留下新的危险和未解问题。",
        ),
    ]

    pack = service._build_deconstruction_pack(  # noqa: SLF001 - unit-level contract test
        remix_mode="continuation",
        source_filename="source.txt",
        chapters=chapters,
        total_words=sum(len(chapter.content) for chapter in chapters),
        inspired_seed_profile=None,
    ).model_dump()

    assert pack["source_scope"]["chapter_count"] == 3
    assert pack["source_scope"]["last_chapter"]["title"] == "未接电话"
    assert pack["chapter_contract"]["mode"] == "continue-chapter"
    assert pack["chapter_contract"]["opening_hook"].startswith("Continue from Ch3")
    assert pack["chapter_contract"]["main_goal"]
    assert "goal" in pack["scene_beat_sheet"][0]
    assert pack["reader_pull_checklist"] == [
        "Who is the POV character?",
        "What do they want now?",
        "What blocks them?",
        "Why does it matter?",
        "What changed by the end?",
        "What question or desire pulls me onward?",
    ]
    assert pack["hook_payoff_matrix"]["seeded_threads"]
    assert "timeline" in pack["continuity_ledger"]["required_ledgers"]
    assert "chapter_log" in pack["continuity_ledger"]["progress_writeback"]
    assert "relationship_changes" in pack["progress_report_contract"]["required_fields"]
    assert pack["progress_report_contract"]["promotion_rule"].startswith("No generated chapter")
    assert "anti_ai_naturalness" in {gate["name"] for gate in pack["revision_gates"]}
    assert pack["revision_strategy"]["ordered_passes"] == [
        "developmental",
        "character",
        "continuity",
        "scene",
        "line",
        "proof_format",
    ]
    assert "smallest_failing_artifact" in pack["revision_strategy"]["patch_policy"]
    assert "critical" in pack["revision_strategy"]["severity_scale"]
    assert "character_specific_diction" in pack["revision_strategy"]["anti_ai_naturalness_fixes"]
    assert pack["confidence"]["level"] in {"medium", "high"}


def test_deconstruction_pack_for_inspired_marks_same_type_boundaries():
    service = BookRemixService()
    chapters = [
        _chapter(
            1,
            "青铜门",
            "陆青发现青铜门背后的学院。星火公会和白塔公司都在追查钥匙。",
            "陆青进入学院，星火公会和白塔公司争夺钥匙。",
        ),
        _chapter(
            2,
            "白塔邀请",
            "白塔公司邀请陆青加入，星火公会暗中阻止，钥匙第一次失控。",
            "白塔公司和星火公会围绕钥匙发生冲突。",
        ),
    ]
    seed_profile = BookRemixInspiredSeedProfile(
        characters=[BookRemixSeedMapping(source_name="陆青", occurrence_count=4)],
        organizations=[BookRemixSeedMapping(source_name="星火公会", occurrence_count=3)],
        abilities=[BookRemixSeedMapping(source_name="钥匙", occurrence_count=3)],
        world_elements=[BookRemixSeedMapping(source_name="白塔公司", occurrence_count=2)],
        plot_threads=[BookRemixSeedMapping(source_name="青铜门", occurrence_count=1)],
    )

    pack = service._build_deconstruction_pack(  # noqa: SLF001 - unit-level contract test
        remix_mode="inspired",
        source_filename="source.txt",
        chapters=chapters,
        total_words=sum(len(chapter.content) for chapter in chapters),
        inspired_seed_profile=seed_profile,
    ).model_dump()

    boundaries = pack["same_type_boundaries"]
    must_replace = " ".join(boundaries["must_replace_elements"])
    assert pack["chapter_contract"]["mode"] == "full-project"
    assert "fresh_characters" in boundaries["required_difference_axes"]
    assert "陆青" in must_replace
    assert "星火公会" in must_replace
    assert pack["hook_payoff_matrix"]["same_type_rule"].startswith("For inspired mode")
    assert "青铜门" in " ".join(boundaries["high_risk_similarity"])
    assert "protected_expression" in boundaries["copy_risk_checks"]


def test_continuation_style_payload_includes_deconstruction_contract():
    service = BookRemixService()
    chapters = [
        _chapter(
            1,
            "雨夜离开",
            "林夏在雨夜离开公司。她握着旧徽章，没有回头。",
            "林夏带着旧徽章离开公司。",
        ),
        _chapter(
            2,
            "未接电话",
            "电话在凌晨三点响起。林夏停住脚步，知道这不是结束。",
            "旧组织在凌晨联系林夏，留下新的危险。",
        ),
    ]

    payload = service._build_continuation_style_payload(  # noqa: SLF001
        source_filename="source.txt",
        chapters=chapters,
        narrative_perspective="第三人称",
    )

    assert payload is not None
    prompt = payload["prompt_content"]
    assert "可审查拆书包" in prompt
    assert "chapter_contract.mode: continue-chapter" in prompt
    assert "reader_pull" in prompt
    assert "scene_beat_sheet" in prompt
    assert "hook_payoff_matrix" in prompt
    assert "progress_report_contract.required_fields" in prompt
    assert "revision_strategy.ordered_passes" in prompt
    assert "revision_strategy.patch_policy" in prompt
    assert "continuity_writeback" in prompt
    assert "anti_ai_naturalness" in prompt


def test_inspired_style_payload_includes_same_type_deconstruction_boundaries():
    service = BookRemixService()
    chapters = [
        _chapter(
            1,
            "青铜门",
            "陆青发现青铜门背后的学院。星火公会和白塔公司都在追查钥匙。",
            "陆青进入学院，组织围绕钥匙发生冲突。",
        )
    ]

    payload = service._build_inspired_style_payload(  # noqa: SLF001
        source_filename="source.txt",
        chapters=chapters,
        narrative_perspective="第三人称",
        source_pattern_pack=None,
    )

    assert payload is not None
    prompt = payload["prompt_content"]
    assert "可审查拆书包" in prompt
    assert "chapter_contract.mode: full-project" in prompt
    assert "same_type_boundaries.required_difference_axes" in prompt
    assert "fresh_characters" in prompt
    assert "copy_risk_checks" in prompt
