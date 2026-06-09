"""本地提示词资产目录服务。"""
from pathlib import Path
import re
from typing import Optional

from app.services.builtin_content_sync_service import (
    HIGH_RISK_KEYWORDS,
    PROMT_DIR,
    SAFE_PROMT_FILENAMES,
    _build_local_tags,
    _display_name_from_filename,
    _extract_description,
    _infer_category,
)


MEDIUM_RISK_KEYWORDS = (
    "黑暗",
    "压迫",
    "支配",
    "欲念",
    "尺度",
    "寄生",
    "惊悚",
    "末世",
)


class PromptAssetCatalogService:
    """扫描本地 promt 目录，输出资产元数据与风险标签。"""

    def get_asset(
        self,
        asset_id: str,
        *,
        include_content: bool = False,
    ) -> Optional[dict]:
        """按资产 ID 获取单个本地提示词。"""
        if not PROMT_DIR.exists():
            return None

        normalized_asset_id = (asset_id or "").strip().lower()
        if not normalized_asset_id:
            return None

        for file_path in sorted(PROMT_DIR.glob("*.md")):
            if self._build_asset_id(file_path) != normalized_asset_id:
                continue

            content = file_path.read_text(encoding="utf-8").strip()
            if not content:
                return None

            return self._build_asset(file_path, content, include_content=include_content)

        return None

    def list_assets(
        self,
        *,
        include_content: bool = False,
        search: Optional[str] = None,
        risk_level: Optional[str] = None,
        category: Optional[str] = None,
        sync_status: Optional[str] = None,
    ) -> list[dict]:
        assets: list[dict] = []

        if not PROMT_DIR.exists():
            return assets

        for file_path in sorted(PROMT_DIR.glob("*.md")):
            content = file_path.read_text(encoding="utf-8").strip()
            if not content:
                continue

            asset = self._build_asset(file_path, content, include_content=include_content)

            if search and search.lower() not in asset["filename"].lower() and search.lower() not in asset["name"].lower():
                continue
            if risk_level and asset["risk_level"] != risk_level:
                continue
            if category and asset["category"] != category:
                continue
            if sync_status and asset["sync_status"] != sync_status:
                continue

            assets.append(asset)

        return assets

    def _build_asset(self, file_path: Path, content: str, *, include_content: bool) -> dict:
        filename = file_path.name
        risk = self._classify_risk(filename, content)
        sync_status = self._resolve_sync_status(filename, risk["level"])
        preview = self._build_preview(content) if risk["level"] != "high" else None

        asset = {
            "id": self._build_asset_id(file_path),
            "filename": filename,
            "name": _display_name_from_filename(filename),
            "source_path": str(file_path.relative_to(PROMT_DIR.parent)).replace("\\", "/"),
            "description": _extract_description(content),
            "category": _infer_category(filename, content),
            "tags": _build_local_tags(filename, content),
            "risk_level": risk["level"],
            "risk_reasons": risk["reasons"],
            "sync_status": sync_status,
            "can_sync_to_workshop": sync_status == "eligible",
            "content_preview": preview,
            "content_length": len(content),
        }

        if include_content and risk["level"] != "high":
            asset["prompt_content"] = content
        elif include_content:
            asset["prompt_content"] = None
            asset["content_blocked_reason"] = "高风险资产不提供接口级正文回传"

        return asset

    def _build_asset_id(self, file_path: Path) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "-", file_path.stem.lower()).strip("-")

    def _classify_risk(self, filename: str, content: str) -> dict:
        haystack = f"{filename}\n{content}"
        high_hits = [keyword for keyword in HIGH_RISK_KEYWORDS if keyword in haystack]
        if high_hits:
            return {
                "level": "high",
                "reasons": [f"命中高风险关键词: {', '.join(high_hits[:5])}"],
            }

        medium_hits = [keyword for keyword in MEDIUM_RISK_KEYWORDS if keyword in haystack]
        if medium_hits:
            return {
                "level": "medium",
                "reasons": [f"命中需人工复核关键词: {', '.join(medium_hits[:5])}"],
            }

        return {
            "level": "low",
            "reasons": ["未命中高风险关键词"],
        }

    def _resolve_sync_status(self, filename: str, risk_level: str) -> str:
        if risk_level == "high":
            return "blocked_high_risk"
        if filename in SAFE_PROMT_FILENAMES:
            return "eligible"
        return "catalog_only"

    def _build_preview(self, content: str, max_length: int = 600) -> str:
        plain = re.sub(r"\s+", " ", content).strip()
        if len(plain) <= max_length:
            return plain
        return plain[:max_length].rstrip("，。；、 ") + "..."


prompt_asset_catalog_service = PromptAssetCatalogService()
