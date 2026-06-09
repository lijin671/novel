"""公开源发现 API schema。"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SourceDiscoveryRunRequest(BaseModel):
    """运行公开源发现。"""

    model_config = ConfigDict(extra="forbid")

    github_queries: Optional[list[str]] = Field(
        default=None,
        description="GitHub Search API 查询语句；为空时使用小说自动化默认查询。",
    )
    linux_do_rss_urls: Optional[list[str]] = Field(
        default=None,
        description="Linux.do RSS URL；为空时使用默认公开 RSS。",
    )
    github_repository_urls: Optional[list[str]] = Field(
        default=None,
        description="Explicit GitHub repository URLs to fetch by metadata API, such as https://github.com/voocel/ainovel-cli.",
    )
    per_github_query: int = Field(default=10, ge=1, le=50)
    per_rss_feed: int = Field(default=20, ge=1, le=50)
    write_to_docs: bool = Field(
        default=False,
        description="是否把 ledger 写入 docs/references/novel-source-discovery-YYYY-MM-DD.md。",
    )


class SourceDiscoveryCandidateResponse(BaseModel):
    """公开源候选条目。"""

    source: str
    url: str
    title: str
    summary: str = ""
    stars: Optional[int] = None
    license: str = "unknown"
    family: str
    posture: str
    posture_hint: str = "metadata-triage"
    risk_flags: list[str] = Field(default_factory=list)
    trust_review: dict = Field(default_factory=dict)
    absorbed_patterns: list[str] = Field(default_factory=list)
    updated_at: str = ""
    score: int = 0


class SourceDiscoveryLedgerResponse(BaseModel):
    """公开源发现 ledger 响应。"""

    generated_at: str
    candidate_count: int = 0
    candidates: list[SourceDiscoveryCandidateResponse] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    fetch_errors: list[dict[str, str]] = Field(default_factory=list)
    pattern_pack: dict = Field(default_factory=dict)
    written_path: Optional[str] = None
    written_pattern_pack_path: Optional[str] = None


class SourceDiscoveryRefreshRequest(SourceDiscoveryRunRequest):
    """Refresh persisted source discovery artifacts when missing/stale or explicitly forced."""

    force: bool = Field(
        default=False,
        description="是否强制刷新来源发现产物；为 false 时仅在缺失或过期时刷新。",
    )
    max_age_hours: float = Field(default=24.0, gt=0, le=168)


class SourceDiscoveryRefreshResponse(BaseModel):
    """Source discovery refresh response."""

    refreshed: bool
    refresh_policy_before: dict = Field(default_factory=dict)
    refresh_policy_after: dict = Field(default_factory=dict)
    refresh_reason: str = ""
    candidate_count: int = 0
    candidates: list[SourceDiscoveryCandidateResponse] = Field(default_factory=list)
    fetch_errors: list[dict[str, str]] = Field(default_factory=list)
    written_path: Optional[str] = None
    written_pattern_pack_path: Optional[str] = None
    pattern_pack: dict = Field(default_factory=dict)
    ledger: dict = Field(default_factory=dict)


class SourceDiscoveryLatestArtifactResponse(BaseModel):
    """Latest persisted public source discovery artifacts."""

    pattern_pack: dict = Field(default_factory=dict)
    ledger: dict = Field(default_factory=dict)
    refresh_policy: dict = Field(default_factory=dict)
