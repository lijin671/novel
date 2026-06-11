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


PROMPT_SCOPE_LABELS = {
    "macro": "宏观",
    "meso": "中观",
    "micro": "微观",
    "tool": "工具",
    "review": "评估",
}

GENRE_SERIES_HINTS = (
    "世情文",
    "玄幻小说",
    "情满四合院",
    "狗血女文",
    "知乎短篇",
    "多子多福",
    "黑暗多子多福",
    "欲念描写专家",
)

PHASE_HINTS = (
    "创意阶段",
    "设定阶段",
    "框架阶段",
    "创作阶段",
    "进阶技巧",
    "数据分析",
    "商业化",
    "辅助工具",
    "额外功能",
    "宏观",
    "设定",
    "势力",
    "中观",
    "微观",
    "辅助",
    "创作流程",
)

WORKFLOW_LANE_RULES = (
    ("拆书分析", ("拆书", "拆解", "源书", "同类型")),
    ("风格仿写", ("仿写", "文风", "风格", "文风迁移")),
    ("创意立项", ("创意", "灵感", "立项", "核心梗", "卖点")),
    ("市场定位", ("市场", "定位", "热度", "读者画像", "算法", "扫榜")),
    ("设定构建", ("设定", "世界观", "人物", "角色", "等级", "势力", "系统", "金手指")),
    ("章节创作", ("框架", "大纲", "细纲", "章节", "场景", "对话", "战斗", "日常", "创作流程")),
    ("质量评估", ("数据分析", "质量", "评分", "逻辑检查", "读者反馈", "复盘", "审校")),
    ("商业运营", ("商业化", "营销", "宣传语", "粉丝运营", "反馈迭代")),
    ("辅助工具", ("辅助", "工具", "卡文", "素材", "名称生成", "生成器")),
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


def _merge_tags(*groups: list[str] | tuple[str, ...]) -> list[str]:
    """合并标签并保持顺序，避免前端重复显示。"""
    result: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for raw_tag in group:
            tag = str(raw_tag or "").strip()
            if not tag or tag in seen:
                continue
            seen.add(tag)
            result.append(tag)
    return result


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

            if search and not self._matches_search(asset, search):
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
        metadata = self._parse_filename_metadata(filename)
        risk = self._classify_risk(filename, content)
        sync_status = self._resolve_sync_status(filename, risk["level"])
        preview = self._build_preview(content) if risk["level"] != "high" else None
        tags = _merge_tags(
            _build_local_tags(filename, content),
            (
                metadata["library_series"],
                metadata["workflow_phase"],
                metadata["workflow_lane"],
                metadata["prompt_scope_label"],
            ),
        )

        asset = {
            "id": self._build_asset_id(file_path),
            "filename": filename,
            "name": _display_name_from_filename(filename),
            "source_path": str(file_path.relative_to(PROMT_DIR.parent)).replace("\\", "/"),
            "description": _extract_description(content),
            "category": _infer_category(filename, content),
            "tags": tags,
            **metadata,
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

    def _matches_search(self, asset: dict, search: str) -> bool:
        query = search.lower().strip()
        searchable = [
            asset.get("filename", ""),
            asset.get("name", ""),
            asset.get("description", ""),
            asset.get("category", ""),
            asset.get("library_series", ""),
            asset.get("workflow_phase", ""),
            asset.get("workflow_lane", ""),
            asset.get("prompt_scope_label", ""),
            asset.get("topic", ""),
            " ".join(asset.get("tags", [])),
        ]
        return any(query in str(value).lower() for value in searchable)

    def _parse_filename_metadata(self, filename: str) -> dict:
        stem = Path(filename).stem
        number_match = re.match(r"^(?P<number>\d+)-(?P<body>.+)$", stem)
        sequence = int(number_match.group("number")) if number_match else None
        body = number_match.group("body") if number_match else stem
        parts = [part.strip() for part in body.split("-") if part.strip()]

        library_series = self._infer_library_series(parts)
        workflow_phase = self._infer_workflow_phase(parts)
        workflow_lane = self._infer_workflow_lane(parts)
        prompt_scope = self._infer_prompt_scope(parts, workflow_lane)
        topic = parts[-1] if parts else body

        return {
            "sequence": sequence,
            "library_series": library_series,
            "workflow_phase": workflow_phase,
            "workflow_lane": workflow_lane,
            "prompt_scope": prompt_scope,
            "prompt_scope_label": PROMPT_SCOPE_LABELS[prompt_scope],
            "topic": topic,
            "filename_parts": parts,
        }

    def _infer_library_series(self, parts: list[str]) -> str:
        if not parts:
            return "通用"
        first = parts[0]
        for hint in GENRE_SERIES_HINTS:
            if hint == first or hint in first:
                return first
        if first.endswith("文") or first.endswith("小说") or first.endswith("专家"):
            return first
        if "多子多福" in first:
            return first
        return "通用"

    def _infer_workflow_phase(self, parts: list[str]) -> str:
        for part in parts:
            if "阶段" in part:
                return part
        for part in parts:
            if part in PHASE_HINTS:
                return part
        return parts[1] if len(parts) > 2 else (parts[0] if parts else "未分组")

    def _infer_workflow_lane(self, parts: list[str]) -> str:
        haystack = " ".join(parts)
        for lane, keywords in WORKFLOW_LANE_RULES:
            if any(keyword in haystack for keyword in keywords):
                return lane
        return "通用资产"

    def _infer_prompt_scope(self, parts: list[str], workflow_lane: str) -> str:
        haystack = " ".join(parts)
        if workflow_lane in {"拆书分析", "质量评估"}:
            return "review"
        if workflow_lane in {"辅助工具", "商业运营"}:
            return "tool"
        if any(keyword in haystack for keyword in ("微观", "润色", "感官", "对话", "句", "词")):
            return "micro"
        if any(keyword in haystack for keyword in ("中观", "章节", "场景", "势力", "战斗", "日常")):
            return "meso"
        return "macro"

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
