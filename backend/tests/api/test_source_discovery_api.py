from __future__ import annotations

from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient

from app.api.source_discovery import router
import app.api.source_discovery as source_discovery_api_module


TEST_USER_ID = "user-source-discovery"


class StubSourceDiscoveryService:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.writes: list[dict] = []

    async def discover_public_sources(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "generated_at": "2026-05-31T09:30:00+08:00",
            "candidate_count": 1,
            "candidates": [
                {
                    "source": "github",
                    "url": "https://github.com/voocel/ainovel-cli",
                    "title": "voocel/ainovel-cli",
                    "summary": "AI novel writing CLI",
                    "stars": 1280,
                    "license": "MIT",
                    "family": "novel-automation",
                    "posture": "pattern-only",
                    "risk_flags": ["postinstall"],
                    "absorbed_patterns": ["chapter_generation", "continuation"],
                    "updated_at": "2026-05-28T12:00:00Z",
                    "score": 88,
                }
            ],
            "safety_notes": ["只采集公开元数据和公开摘要；不克隆、不安装、不执行外部项目。"],
            "fetch_errors": [],
        }

    def write_ledger(self, **kwargs):
        self.writes.append(kwargs)
        path = Path(kwargs["repo_root"]) / "docs" / "references" / "novel-source-discovery-2026-05-31.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Novel Source Discovery Ledger - 2026-05-31\n", encoding="utf-8")
        return path

    def build_pattern_pack_from_ledger(self, ledger):
        return {
            "generated_at": ledger["generated_at"],
            "source_candidate_count": ledger["candidate_count"],
            "workflow_patterns": [
                {
                    "name": "continuation",
                    "candidate_count": 1,
                    "top_source_url": "https://github.com/voocel/ainovel-cli",
                    "risk_flags": ["postinstall"],
                    "sources": [],
                }
            ],
            "bible_enrichment_targets": ["world_rules", "timeline", "character_cards"],
            "continuation_prompt_hints": ["续写前读取世界观、时间线、人物卡。"],
            "style_signature_hints": ["保留原书味道。"],
            "self_review_policy_hints": ["不限次数自评优化需要工程停止条件。"],
            "safety_constraints": ["不导入外部代码。"],
        }

    def write_pattern_pack(self, **kwargs):
        self.writes.append({"pattern_pack": kwargs})
        path = Path(kwargs["repo_root"]) / "backend" / "app" / "references" / "novel-source-pattern-pack-2026-05-31.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
        return path

    def load_latest_pattern_pack_artifact(self, *, repo_root: Path):
        return {
            "found": True,
            "path": str(repo_root / "backend" / "app" / "references" / "novel-source-pattern-pack-2026-05-31.json"),
            "generated_at": "2026-05-31T09:30:00+08:00",
            "source_candidate_count": 1,
            "workflow_pattern_count": 1,
            "source_titles": ["voocel/ainovel-cli"],
            "pattern_pack": self.build_pattern_pack_from_ledger(
                {
                    "generated_at": "2026-05-31T09:30:00+08:00",
                    "candidate_count": 1,
                }
            ),
        }

    def load_latest_ledger_artifact(self, *, repo_root: Path):
        return {
            "found": True,
            "path": str(repo_root / "docs" / "references" / "novel-source-discovery-2026-05-31.md"),
            "date_slug": "2026-05-31",
            "content": "# Novel Source Discovery Ledger - 2026-05-31\n\n- URL: https://github.com/voocel/ainovel-cli\n",
        }

    def evaluate_refresh_need(self, *, repo_root: Path):
        return {
            "refresh_needed": False,
            "reason": "pattern_pack_fresh",
            "generated_at": "2026-05-31T09:30:00+08:00",
            "age_hours": 2.5,
            "max_age_hours": 24.0,
        }

    async def refresh_pattern_pack_if_needed(self, **kwargs):
        self.calls.append({"refresh_pattern_pack_if_needed": kwargs})
        refresh_policy_before = {
            "refresh_needed": True,
            "reason": "pattern_pack_missing",
            "generated_at": None,
            "age_hours": None,
            "max_age_hours": kwargs.get("max_age_hours", 24.0),
        }
        return {
            "refreshed": True,
            "refresh_policy_before": refresh_policy_before,
            "refresh_policy_after": {
                "refresh_needed": False,
                "reason": "pattern_pack_fresh",
                "generated_at": "2026-05-31T09:30:00+08:00",
                "age_hours": 0.0,
                "max_age_hours": kwargs.get("max_age_hours", 24.0),
            },
            "refresh_reason": refresh_policy_before["reason"],
            "candidate_count": 1,
            "candidates": [
                {
                    "source": "github",
                    "url": "https://github.com/voocel/ainovel-cli",
                    "title": "voocel/ainovel-cli",
                    "summary": "AI novel writing CLI",
                    "stars": 1280,
                    "license": "MIT",
                    "family": "novel-automation",
                    "posture": "pattern-only",
                    "risk_flags": ["postinstall"],
                    "absorbed_patterns": ["chapter_generation", "continuation"],
                    "updated_at": "2026-05-28T12:00:00Z",
                    "score": 88,
                }
            ],
            "fetch_errors": [],
            "written_path": str(kwargs["repo_root"] / "docs" / "references" / "novel-source-discovery-2026-05-31.md"),
            "written_pattern_pack_path": str(kwargs["repo_root"] / "backend" / "app" / "references" / "novel-source-pattern-pack-2026-05-31.json"),
            "pattern_pack": self.load_latest_pattern_pack_artifact(repo_root=kwargs["repo_root"]),
            "ledger": self.load_latest_ledger_artifact(repo_root=kwargs["repo_root"]),
        }


@pytest_asyncio.fixture
async def api_context(monkeypatch, tmp_path: Path):
    app = FastAPI()
    app.include_router(router, prefix="/api")

    @app.middleware("http")
    async def inject_user_id(request: Request, call_next):
        request.state.user_id = TEST_USER_ID
        return await call_next(request)

    stub_service = StubSourceDiscoveryService()
    monkeypatch.setattr(source_discovery_api_module, "source_discovery_service", stub_service)
    monkeypatch.setattr(source_discovery_api_module, "PROJECT_ROOT", tmp_path)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield {
            "client": client,
            "service": stub_service,
            "repo_root": tmp_path,
        }


@pytest.mark.asyncio
async def test_run_source_discovery_returns_public_metadata_ledger(api_context):
    client: AsyncClient = api_context["client"]

    response = await client.post(
        "/api/source-discovery/ledger/run",
        json={
            "github_queries": ["ai novel writing stars:>50"],
            "github_repository_urls": ["https://github.com/voocel/ainovel-cli"],
            "linux_do_rss_urls": ["https://linux.do/tag/444-tag/444.rss"],
            "per_github_query": 3,
            "per_rss_feed": 2,
            "write_to_docs": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate_count"] == 1
    assert payload["written_path"] is None
    assert payload["written_pattern_pack_path"] is None
    assert payload["pattern_pack"]["workflow_patterns"][0]["name"] == "continuation"
    assert payload["candidates"][0]["title"] == "voocel/ainovel-cli"
    assert payload["candidates"][0]["family"] == "novel-automation"
    assert api_context["service"].calls[0]["github_queries"] == ["ai novel writing stars:>50"]
    assert api_context["service"].calls[0]["github_repository_urls"] == ["https://github.com/voocel/ainovel-cli"]
    assert api_context["service"].calls[0]["linux_do_rss_urls"] == ["https://linux.do/tag/444-tag/444.rss"]
    assert api_context["service"].writes == []


@pytest.mark.asyncio
async def test_run_source_discovery_can_write_ledger_under_docs_references(api_context):
    client: AsyncClient = api_context["client"]

    response = await client.post(
        "/api/source-discovery/ledger/run",
        json={"write_to_docs": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate_count"] == 1
    assert Path(payload["written_path"]).name == "novel-source-discovery-2026-05-31.md"
    assert Path(payload["written_path"]).parent.name == "references"
    assert Path(payload["written_path"]).parent.parent.name == "docs"
    assert api_context["service"].writes[0]["repo_root"] == api_context["repo_root"]
    assert Path(payload["written_pattern_pack_path"]).name == "novel-source-pattern-pack-2026-05-31.json"


@pytest.mark.asyncio
async def test_run_source_discovery_allows_empty_repository_url_override(api_context):
    client: AsyncClient = api_context["client"]

    response = await client.post(
        "/api/source-discovery/ledger/run",
        json={"github_repository_urls": []},
    )

    assert response.status_code == 200
    assert api_context["service"].calls[0]["github_repository_urls"] == []


@pytest.mark.asyncio
async def test_run_source_discovery_requires_login():
    app = FastAPI()
    app.include_router(router, prefix="/api")
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/api/source-discovery/ledger/run", json={})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_latest_source_discovery_artifacts_returns_pattern_pack_and_ledger(api_context):
    client: AsyncClient = api_context["client"]

    response = await client.get("/api/source-discovery/latest")

    assert response.status_code == 200
    payload = response.json()
    assert payload["pattern_pack"]["found"] is True
    assert payload["pattern_pack"]["generated_at"] == "2026-05-31T09:30:00+08:00"
    assert payload["pattern_pack"]["workflow_pattern_count"] == 1
    assert payload["pattern_pack"]["pattern_pack"]["workflow_patterns"][0]["name"] == "continuation"
    assert payload["refresh_policy"]["refresh_needed"] is False
    assert payload["refresh_policy"]["reason"] == "pattern_pack_fresh"
    assert payload["refresh_policy"]["age_hours"] == 2.5
    assert payload["ledger"]["found"] is True
    assert "voocel/ainovel-cli" in payload["ledger"]["content"]


@pytest.mark.asyncio
async def test_refresh_source_discovery_updates_missing_or_stale_artifacts(api_context):
    client: AsyncClient = api_context["client"]

    response = await client.post(
        "/api/source-discovery/refresh",
        json={
            "github_queries": ["ai novel writing stars:>50"],
            "github_repository_urls": ["https://github.com/voocel/ainovel-cli"],
            "linux_do_rss_urls": ["https://linux.do/tag/444-tag/444.rss"],
            "force": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["refreshed"] is True
    assert payload["refresh_policy_before"]["reason"] == "pattern_pack_missing"
    assert payload["refresh_policy_after"]["reason"] == "pattern_pack_fresh"
    assert payload["refresh_reason"] == "pattern_pack_missing"
    assert payload["candidate_count"] == 1
    assert Path(payload["written_pattern_pack_path"]).name == "novel-source-pattern-pack-2026-05-31.json"
    call = api_context["service"].calls[-1]["refresh_pattern_pack_if_needed"]
    assert call["github_queries"] == ["ai novel writing stars:>50"]
    assert call["github_repository_urls"] == ["https://github.com/voocel/ainovel-cli"]
    assert call["linux_do_rss_urls"] == ["https://linux.do/tag/444-tag/444.rss"]
    assert call["force"] is True


@pytest.mark.asyncio
async def test_get_latest_source_discovery_artifacts_requires_login():
    app = FastAPI()
    app.include_router(router, prefix="/api")
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/source-discovery/latest")

    assert response.status_code == 401


def test_main_app_registers_source_discovery_router():
    from app.main import app

    paths = {getattr(route, "path", "") for route in app.routes}
    assert "/api/source-discovery/ledger/run" in paths
    assert "/api/source-discovery/latest" in paths
    assert "/api/source-discovery/refresh" in paths
