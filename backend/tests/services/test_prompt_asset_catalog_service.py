from __future__ import annotations

from app.services.prompt_asset_catalog_service import prompt_asset_catalog_service


def test_prompt_asset_catalog_exposes_workflow_metadata() -> None:
    asset = prompt_asset_catalog_service.get_asset("083", include_content=False)

    assert asset is not None
    assert asset["filename"] == "083-辅助工具-整书拆解分析.md"
    assert asset["sequence"] == 83
    assert asset["library_series"] == "通用"
    assert asset["workflow_phase"] == "辅助工具"
    assert asset["workflow_lane"] == "拆书分析"
    assert asset["prompt_scope"] == "review"
    assert asset["prompt_scope_label"] == "评估"
    assert asset["topic"] == "整书拆解分析"
    assert "拆书分析" in asset["tags"]


def test_prompt_asset_catalog_searches_workflow_metadata() -> None:
    assets = prompt_asset_catalog_service.list_assets(search="拆书分析")

    assert assets
    assert any(asset["filename"] == "083-辅助工具-整书拆解分析.md" for asset in assets)
    assert all(
        "拆书" in asset["workflow_lane"] or "拆书" in " ".join(asset["tags"]) or "拆书" in asset["name"]
        for asset in assets
    )


def test_prompt_asset_catalog_keeps_high_risk_content_blocked() -> None:
    asset = prompt_asset_catalog_service.get_asset(
        "390",
        include_content=True,
    )

    assert asset is not None
    assert asset["library_series"] == "黑暗多子多福"
    assert asset["workflow_lane"] == "设定构建"
    assert asset["risk_level"] == "high"
    assert asset["prompt_content"] is None
    assert asset["content_blocked_reason"] == "高风险资产不提供接口级正文回传"
