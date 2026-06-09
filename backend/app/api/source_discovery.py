"""公开小说项目发现 API。"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from app.schemas.source_discovery import (
    SourceDiscoveryLatestArtifactResponse,
    SourceDiscoveryLedgerResponse,
    SourceDiscoveryRefreshRequest,
    SourceDiscoveryRefreshResponse,
    SourceDiscoveryRunRequest,
)
from app.services.source_discovery_service import (
    DEFAULT_GITHUB_QUERIES,
    DEFAULT_GITHUB_REPOSITORY_URLS,
    DEFAULT_LINUX_DO_RSS_URLS,
    source_discovery_service,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

router = APIRouter(prefix="/source-discovery", tags=["公开源发现"])


def _require_user_id(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    return str(user_id)


@router.post(
    "/ledger/run",
    response_model=SourceDiscoveryLedgerResponse,
    summary="从 GitHub 和 Linux.do 采集小说自动化公开源候选",
)
async def run_source_discovery_ledger(
    payload: SourceDiscoveryRunRequest,
    request: Request,
):
    """采集公开元数据并可选写入 docs/references ledger。"""
    _require_user_id(request)

    result = await source_discovery_service.discover_public_sources(
        github_queries=payload.github_queries or DEFAULT_GITHUB_QUERIES,
        github_repository_urls=(
            DEFAULT_GITHUB_REPOSITORY_URLS
            if payload.github_repository_urls is None
            else payload.github_repository_urls
        ),
        linux_do_rss_urls=payload.linux_do_rss_urls or DEFAULT_LINUX_DO_RSS_URLS,
        github_token=os.environ.get("GITHUB_TOKEN"),
        per_github_query=payload.per_github_query,
        per_rss_feed=payload.per_rss_feed,
    )

    pattern_pack = source_discovery_service.build_pattern_pack_from_ledger(result)

    written_path = None
    written_pattern_pack_path = None
    if payload.write_to_docs:
        written_path = str(
            source_discovery_service.write_ledger(
                repo_root=PROJECT_ROOT,
                result=result,
            )
        )
        written_pattern_pack_path = str(
            source_discovery_service.write_pattern_pack(
                repo_root=PROJECT_ROOT,
                pattern_pack=pattern_pack,
            )
        )

    return {
        **result,
        "pattern_pack": pattern_pack,
        "written_path": written_path,
        "written_pattern_pack_path": written_pattern_pack_path,
    }


@router.post(
    "/refresh",
    response_model=SourceDiscoveryRefreshResponse,
    summary="按新鲜度刷新来源发现产物",
)
async def refresh_source_discovery_artifacts(
    payload: SourceDiscoveryRefreshRequest,
    request: Request,
):
    """Refresh persisted source discovery artifacts when they are missing, stale, or forced."""
    _require_user_id(request)

    return await source_discovery_service.refresh_pattern_pack_if_needed(
        repo_root=PROJECT_ROOT,
        github_queries=payload.github_queries or DEFAULT_GITHUB_QUERIES,
        github_repository_urls=(
            DEFAULT_GITHUB_REPOSITORY_URLS
            if payload.github_repository_urls is None
            else payload.github_repository_urls
        ),
        linux_do_rss_urls=payload.linux_do_rss_urls or DEFAULT_LINUX_DO_RSS_URLS,
        github_token=os.environ.get("GITHUB_TOKEN"),
        per_github_query=payload.per_github_query,
        per_rss_feed=payload.per_rss_feed,
        max_age_hours=payload.max_age_hours,
        force=payload.force,
    )


@router.get(
    "/latest",
    response_model=SourceDiscoveryLatestArtifactResponse,
    summary="读取最近一次公开源发现沉淀结果",
)
async def get_latest_source_discovery_artifacts(request: Request):
    """Return latest persisted ledger and pattern pack for UI/workflow visibility."""
    _require_user_id(request)
    return {
        "pattern_pack": source_discovery_service.load_latest_pattern_pack_artifact(
            repo_root=PROJECT_ROOT,
        ),
        "ledger": source_discovery_service.load_latest_ledger_artifact(
            repo_root=PROJECT_ROOT,
        ),
        "refresh_policy": source_discovery_service.evaluate_refresh_need(
            repo_root=PROJECT_ROOT,
        ),
    }
