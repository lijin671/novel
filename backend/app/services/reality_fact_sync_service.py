from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import get_logger
from app.mcp import mcp_client
from app.models.chapter import Chapter
from app.models.character import Character
from app.models.mcp_plugin import MCPPlugin
from app.models.outline import Outline
from app.models.project import Project
from app.models.relationship import Organization, OrganizationMember
from app.services.ai_service import AIService

logger = get_logger(__name__)

MANAGED_BLOCK_START = "【现实资料同步】"
MANAGED_BLOCK_END = "【/现实资料同步】"

REALITY_REFERENCE_KEYWORDS = (
    "现实世界",
    "真实人物",
    "真实成员",
    "偶像",
    "女团",
    "女子组合",
    "成员",
    "经纪公司",
    "出道",
    "回归",
    "退团",
    "毕业",
    "解散",
    "活动期",
    "公开履历",
    "时间线",
    "韩团",
    "k-pop",
    "kpop",
)

COMMON_GROUP_SPECS: tuple[dict[str, Any], ...] = (
    {"canonical": "Girls' Generation", "aliases": ("少女时代", "SNSD", "Girls Generation"), "generation": "二代"},
    {"canonical": "KARA", "aliases": ("카라",), "generation": "二代"},
    {"canonical": "Wonder Girls", "aliases": ("WG",), "generation": "二代"},
    {"canonical": "2NE1", "aliases": tuple(), "generation": "二代"},
    {"canonical": "T-ARA", "aliases": ("TARA", "皇冠团"), "generation": "二代"},
    {"canonical": "Apink", "aliases": ("에이핑크",), "generation": "二代"},
    {"canonical": "f(x)", "aliases": ("fx",), "generation": "二代"},
    {"canonical": "SISTAR", "aliases": tuple(), "generation": "二代"},
    {"canonical": "TWICE", "aliases": ("兔瓦斯",), "generation": "三代"},
    {"canonical": "Red Velvet", "aliases": ("RV", "红贝贝"), "generation": "三代"},
    {"canonical": "BLACKPINK", "aliases": ("BP", "粉墨"), "generation": "三代"},
    {"canonical": "GFRIEND", "aliases": ("女朋友",), "generation": "三代"},
    {"canonical": "MAMAMOO", "aliases": ("麻木",), "generation": "三代"},
    {"canonical": "OH MY GIRL", "aliases": ("OMG",), "generation": "三代"},
    {"canonical": "WJSN", "aliases": ("宇宙少女", "Cosmic Girls"), "generation": "三代"},
    {"canonical": "Lovelyz", "aliases": tuple(), "generation": "三代"},
    {"canonical": "Dreamcatcher", "aliases": ("追梦人",), "generation": "三代"},
    {"canonical": "IZ*ONE", "aliases": ("아이즈원", "矮子王", "IZONE"), "generation": "四代"},
    {"canonical": "(G)I-DLE", "aliases": ("GIDLE", "I-DLE", "IDLE", "娃", "女娃"), "generation": "四代"},
    {"canonical": "ITZY", "aliases": ("있지",), "generation": "四代"},
    {"canonical": "aespa", "aliases": ("吒",), "generation": "四代"},
    {"canonical": "STAYC", "aliases": tuple(), "generation": "四代"},
    {"canonical": "fromis_9", "aliases": ("fromis9", "芙妹"), "generation": "四代"},
    {"canonical": "IVE", "aliases": ("아이브",), "generation": "四代"},
    {"canonical": "LE SSERAFIM", "aliases": ("LSF", "르세라핌"), "generation": "四代"},
    {"canonical": "NMIXX", "aliases": ("엔믹스",), "generation": "四代"},
    {"canonical": "Kep1er", "aliases": ("开普勒",), "generation": "四代"},
    {"canonical": "NewJeans", "aliases": ("뉴진스",), "generation": "五代"},
    {"canonical": "tripleS", "aliases": tuple(), "generation": "五代"},
    {"canonical": "KISS OF LIFE", "aliases": ("KIOF",), "generation": "五代"},
    {"canonical": "BABYMONSTER", "aliases": ("Baemon", "贝蒙"), "generation": "五代"},
    {"canonical": "ILLIT", "aliases": ("아일릿",), "generation": "五代"},
    {"canonical": "UNIS", "aliases": tuple(), "generation": "五代"},
    {"canonical": "MEOVV", "aliases": tuple(), "generation": "六代（常见口径，存在争议）"},
    {"canonical": "izna", "aliases": ("IZNA",), "generation": "六代（常见口径，存在争议）"},
)

GROUP_ALIAS_MAP: dict[str, str] = {}
for _spec in COMMON_GROUP_SPECS:
    GROUP_ALIAS_MAP[_spec["canonical"]] = _spec["canonical"]
    for _alias in _spec["aliases"]:
        GROUP_ALIAS_MAP[_alias] = _spec["canonical"]


@dataclass
class RealityFactSyncResult:
    attempted: bool = False
    skipped_reason: Optional[str] = None
    synced_groups: list[str] = field(default_factory=list)
    created_characters: int = 0
    updated_characters: int = 0
    linked_memberships: int = 0
    logs: list[str] = field(default_factory=list)


@dataclass
class ProjectRealitySyncConfig:
    mode: str = "auto"
    preferred_groups: list[str] = field(default_factory=list)
    max_groups_per_run: int = 6


def _normalize_name(value: Optional[str]) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    return re.sub(r"[^0-9a-z\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+", "", text)


def _dedupe_names(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = str(value or "").strip()
        normalized = _normalize_name(cleaned)
        if not cleaned or not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(cleaned)
    return result


def _is_reality_reference(*texts: Optional[str]) -> bool:
    combined = " ".join(str(text or "") for text in texts).strip().lower()
    if not combined:
        return False
    if any(keyword.lower() in combined for keyword in REALITY_REFERENCE_KEYWORDS):
        return True
    normalized = _normalize_name(combined)
    return any(_normalize_name(alias) in normalized for alias in GROUP_ALIAS_MAP)


def _clean_text(value: Any, max_length: int = 1200) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_length]


def _build_managed_block(summary_lines: list[str]) -> str:
    body = "\n".join(line for line in summary_lines if line)
    return f"{MANAGED_BLOCK_START}\n{body}\n{MANAGED_BLOCK_END}"


def _merge_managed_block(existing_text: Optional[str], summary_lines: list[str]) -> str:
    new_block = _build_managed_block(summary_lines)
    old_text = str(existing_text or "").strip()
    pattern = re.compile(
        rf"{re.escape(MANAGED_BLOCK_START)}.*?{re.escape(MANAGED_BLOCK_END)}",
        re.S,
    )
    if not old_text:
        return new_block
    if pattern.search(old_text):
        merged = pattern.sub(new_block, old_text)
    else:
        merged = f"{old_text}\n\n{new_block}"
    return merged.strip()


def _extract_timeline_lines(events: list[dict[str, Any]], max_items: int = 4) -> list[str]:
    lines: list[str] = []
    for event in events[:max_items]:
        date = str(event.get("date") or "").strip()
        content = str(event.get("event") or "").strip()
        if not content:
            continue
        lines.append(f"- {date} {content}".strip())
    return lines


def _extract_roster_entries(items: Any) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not isinstance(items, list):
        return entries
    for item in items:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            if name:
                entries.append(item)
        elif isinstance(item, str) and item.strip():
            entries.append({"name": item.strip()})
    return entries


class RealityFactSyncService:
    MAX_GROUPS_PER_RUN = 6
    MAX_SEARCH_RESULTS = 4
    MAX_CONTENT_URLS = 3
    MAX_CONFIGURED_GROUPS = 12

    def _get_project_sync_config(self, project: Project) -> ProjectRealitySyncConfig:
        raw_config = getattr(project, "reality_sync_config", None)
        if not isinstance(raw_config, dict):
            raw_config = {}

        mode = str(raw_config.get("mode") or "auto").strip().lower()
        if mode not in {"auto", "force", "off"}:
            mode = "auto"

        preferred_groups: list[str] = []
        for value in raw_config.get("preferred_groups") or []:
            canonical = self._canonicalize_group_name(value)
            if canonical:
                preferred_groups.append(canonical)

        max_groups_per_run = raw_config.get("max_groups_per_run", self.MAX_GROUPS_PER_RUN)
        try:
            max_groups_per_run = int(max_groups_per_run)
        except (TypeError, ValueError):
            max_groups_per_run = self.MAX_GROUPS_PER_RUN

        max_groups_per_run = max(1, min(max_groups_per_run, self.MAX_CONFIGURED_GROUPS))

        return ProjectRealitySyncConfig(
            mode=mode,
            preferred_groups=_dedupe_names(preferred_groups),
            max_groups_per_run=max_groups_per_run,
        )

    async def sync_for_chapter(
        self,
        *,
        project: Project,
        chapter: Chapter,
        outline: Optional[Outline],
        user_id: str,
        db: AsyncSession,
        ai_service: AIService,
        enable_mcp: bool = True,
    ) -> RealityFactSyncResult:
        result = RealityFactSyncResult()
        sync_config = self._get_project_sync_config(project)

        if sync_config.mode == "off":
            result.skipped_reason = "项目已关闭现实资料同步"
            return result

        text_bundle = await self._build_text_bundle(
            project=project,
            chapter=chapter,
            outline=outline,
            db=db,
        )
        if sync_config.mode != "force" and not _is_reality_reference(text_bundle):
            result.skipped_reason = "未命中现实女团/公开资料信号"
            return result

        if not enable_mcp:
            result.skipped_reason = "当前续写未启用 MCP"
            return result

        plugin = await self._load_exa_plugin(user_id=user_id, db=db)
        if plugin is None:
            result.skipped_reason = "未找到可用的 exa_rest 插件"
            return result

        candidate_groups = await self._extract_candidate_groups(
            text_bundle=text_bundle,
            ai_service=ai_service,
            preferred_groups=sync_config.preferred_groups,
            force_mode=sync_config.mode == "force",
        )
        if not candidate_groups:
            result.skipped_reason = "未识别到需要同步的现实女团组合"
            return result

        result.attempted = True
        if sync_config.preferred_groups:
            result.logs.append(
                f"项目现实资料同步模式={sync_config.mode}，优先组合={', '.join(sync_config.preferred_groups)}"
            )
        existing_characters = (
            await db.execute(select(Character).where(Character.project_id == project.id))
        ).scalars().all()
        existing_organizations = (
            await db.execute(select(Organization).where(Organization.project_id == project.id))
        ).scalars().all()

        for group_name in candidate_groups[: sync_config.max_groups_per_run]:
            try:
                raw_evidence = await self._collect_group_evidence(
                    user_id=user_id,
                    plugin=plugin,
                    group_name=group_name,
                )
                if not raw_evidence:
                    result.logs.append(f"{group_name}: 未拿到公开资料")
                    continue

                structured = await self._parse_group_evidence(
                    group_name=group_name,
                    raw_evidence=raw_evidence,
                    ai_service=ai_service,
                )
                if not structured:
                    result.logs.append(f"{group_name}: 结构化解析失败")
                    continue

                sync_stats = await self._upsert_group_payload(
                    project=project,
                    group_name=group_name,
                    payload=structured,
                    existing_characters=existing_characters,
                    existing_organizations=existing_organizations,
                    db=db,
                )
                result.synced_groups.append(group_name)
                result.created_characters += sync_stats["created_characters"]
                result.updated_characters += sync_stats["updated_characters"]
                result.linked_memberships += sync_stats["linked_memberships"]
                result.logs.append(
                    f"{group_name}: 已同步，角色+{sync_stats['created_characters']}，更新{sync_stats['updated_characters']}，成员关系+{sync_stats['linked_memberships']}"
                )
            except Exception as exc:
                logger.warning(f"现实资料同步失败: group={group_name}, error={exc}")
                result.logs.append(f"{group_name}: 同步失败 {exc}")

        await db.flush()
        return result

    async def _build_text_bundle(
        self,
        *,
        project: Project,
        chapter: Chapter,
        outline: Optional[Outline],
        db: AsyncSession,
    ) -> str:
        existing_names = (
            await db.execute(
                select(Character.name).where(Character.project_id == project.id).order_by(Character.name)
            )
        ).scalars().all()
        parts = [
            f"项目标题: {project.title}",
            f"项目简介: {project.description or ''}",
            f"项目题材: {project.genre or ''}",
            f"项目主题: {project.theme or ''}",
            f"世界时间: {project.world_time_period or ''}",
            f"当前章节标题: {chapter.title}",
            f"当前章节摘要: {chapter.summary or ''}",
            f"当前章节扩写计划: {chapter.expansion_plan or ''}",
            f"章节大纲: {outline.content if outline else ''}",
            f"章节结构: {outline.structure if outline else ''}",
            f"项目已有角色与组织: {', '.join(existing_names[:80])}",
        ]
        return "\n".join(part for part in parts if part).strip()

    async def _extract_candidate_groups(
        self,
        *,
        text_bundle: str,
        ai_service: AIService,
        preferred_groups: Optional[list[str]] = None,
        force_mode: bool = False,
    ) -> list[str]:
        candidate_groups = _dedupe_names(list(preferred_groups or []))
        alias_hits: list[str] = []
        normalized_bundle = _normalize_name(text_bundle)
        for raw_alias, canonical in GROUP_ALIAS_MAP.items():
            normalized_alias = _normalize_name(raw_alias)
            if normalized_alias and normalized_alias in normalized_bundle:
                alias_hits.append(canonical)

        candidate_groups.extend(alias_hits)
        candidate_groups = _dedupe_names(candidate_groups)
        if candidate_groups and (alias_hits or force_mode):
            return candidate_groups

        prompt = f"""
你是现实女团实体识别器。请根据下面文本，只提取“当前续写前需要补公开资料”的现实女子组合与成员。

只返回 JSON 对象，不要 markdown：
{{
  "groups": [
    {{
      "name": "组合常见公开写法",
      "evidence": "证据短语"
    }}
  ],
  "members": [
    {{
      "name": "成员常见公开写法",
      "likely_groups": ["可能所属组合"],
      "evidence": "证据短语"
    }}
  ]
}}

规则：
1. 只提取现实世界公开艺名/组合名，不提取原创角色。
2. 如果文本更像 K-pop 女团语境，优先还原为常见公开写法，例如 IZ*ONE、TWICE、(G)I-DLE、ITZY、NMIXX。
3. 不确定就留空，不要编造。

文本：
{text_bundle[:5000]}
""".strip()

        try:
            extracted = await ai_service.call_with_json_retry(
                prompt=prompt,
                max_retries=2,
                temperature=0.1,
                max_tokens=1200,
                expected_type="object",
                auto_mcp=False,
            )
        except Exception as exc:
            logger.info(f"现实女团候选提取回退到本地别名命中: {exc}")
            return candidate_groups

        groups = extracted.get("groups") if isinstance(extracted, dict) else []
        members = extracted.get("members") if isinstance(extracted, dict) else []

        for item in groups or []:
            name = self._canonicalize_group_name(item.get("name"))
            if name:
                candidate_groups.append(name)

        for item in members or []:
            likely_groups = item.get("likely_groups") or []
            if isinstance(likely_groups, list):
                for group_name in likely_groups:
                    name = self._canonicalize_group_name(group_name)
                    if name:
                        candidate_groups.append(name)

        return _dedupe_names(candidate_groups)

    def _canonicalize_group_name(self, raw_name: Any) -> Optional[str]:
        cleaned = str(raw_name or "").strip()
        if not cleaned:
            return None
        normalized = _normalize_name(cleaned)
        for alias, canonical in GROUP_ALIAS_MAP.items():
            if _normalize_name(alias) == normalized:
                return canonical
        return cleaned

    async def _load_exa_plugin(
        self,
        *,
        user_id: str,
        db: AsyncSession,
    ) -> Optional[MCPPlugin]:
        plugin = (
            await db.execute(
                select(MCPPlugin).where(
                    MCPPlugin.user_id == user_id,
                    MCPPlugin.enabled == True,
                    MCPPlugin.plugin_name == "exa_rest",
                )
            )
        ).scalar_one_or_none()
        if plugin is None:
            return None

        plugin_type = plugin.plugin_type or "builtin"
        if plugin_type == "http":
            plugin_type = "streamable_http"

        registered = await mcp_client.ensure_registered(
            user_id=user_id,
            plugin_name=plugin.plugin_name,
            url=plugin.server_url or "",
            plugin_type=plugin_type,
            headers=plugin.headers,
            config=plugin.config,
        )
        if not registered:
            logger.warning("exa_rest 注册失败，当前跳过现实资料同步")
            return None
        return plugin

    async def _collect_group_evidence(
        self,
        *,
        user_id: str,
        plugin: MCPPlugin,
        group_name: str,
    ) -> str:
        answer_query = (
            f"{group_name} 女团/女子组合公开资料：完整成员名单、现役与前成员、所属公司、"
            "出道时间、活动时间线、毕业/退团/解散或活动结束节点"
        )
        search_query = (
            f"{group_name} girl group members company debut timeline former members public profile"
        )

        answer_result = await mcp_client.call_tool(
            user_id,
            plugin.plugin_name,
            "answer",
            {"query": answer_query},
        )
        search_result = await mcp_client.call_tool(
            user_id,
            plugin.plugin_name,
            "search",
            {"query": search_query, "numResults": self.MAX_SEARCH_RESULTS},
        )

        urls = self._extract_search_urls(search_result)[: self.MAX_CONTENT_URLS]
        contents_result: Any = None
        if urls:
            try:
                contents_result = await mcp_client.call_tool(
                    user_id,
                    plugin.plugin_name,
                    "contents",
                    {"urls": urls},
                )
            except Exception as exc:
                logger.info(f"Exa contents 拉取失败，继续使用 answer/search: {exc}")

        parts = [
            f"目标组合: {group_name}",
            self._summarize_answer_result(answer_result),
            self._summarize_search_result(search_result),
            self._summarize_contents_result(contents_result),
        ]
        merged = "\n\n".join(part for part in parts if part).strip()
        return merged[:12000]

    def _extract_search_urls(self, search_result: Any) -> list[str]:
        if not isinstance(search_result, dict):
            return []
        results = search_result.get("results") or []
        urls: list[str] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url") or "").strip()
            if url:
                urls.append(url)
        return _dedupe_names(urls)

    def _summarize_answer_result(self, answer_result: Any) -> str:
        if not isinstance(answer_result, dict):
            return ""
        answer = _clean_text(
            answer_result.get("answer")
            or answer_result.get("summary")
            or answer_result.get("text")
            or answer_result,
            max_length=2200,
        )
        if not answer:
            return ""
        return f"【Exa Answer】\n{answer}"

    def _summarize_search_result(self, search_result: Any) -> str:
        if not isinstance(search_result, dict):
            return ""
        rows = search_result.get("results") or []
        if not isinstance(rows, list) or not rows:
            return ""
        lines = ["【Exa Search】"]
        for item in rows[: self.MAX_SEARCH_RESULTS]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            url = str(item.get("url") or "").strip()
            published = str(item.get("publishedDate") or item.get("published_date") or "").strip()
            snippet = _clean_text(item.get("text") or item.get("snippet") or "", max_length=320)
            meta = " | ".join(part for part in (title, published, url) if part)
            if meta:
                lines.append(f"- {meta}")
            if snippet:
                lines.append(f"  摘要: {snippet}")
        return "\n".join(lines)

    def _summarize_contents_result(self, contents_result: Any) -> str:
        if not isinstance(contents_result, dict):
            return ""
        rows = (
            contents_result.get("results")
            or contents_result.get("contents")
            or contents_result.get("data")
            or []
        )
        if not isinstance(rows, list) or not rows:
            return ""
        lines = ["【Exa Contents】"]
        for item in rows[: self.MAX_CONTENT_URLS]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            url = str(item.get("url") or "").strip()
            text = _clean_text(
                item.get("text")
                or item.get("content")
                or item.get("excerpt")
                or item.get("highlights")
                or "",
                max_length=900,
            )
            meta = " | ".join(part for part in (title, url) if part)
            if meta:
                lines.append(f"- {meta}")
            if text:
                lines.append(f"  正文摘录: {text}")
        return "\n".join(lines)

    async def _parse_group_evidence(
        self,
        *,
        group_name: str,
        raw_evidence: str,
        ai_service: AIService,
    ) -> Optional[dict[str, Any]]:
        prompt = f"""
你是现实女团公开资料整理器。请严格根据证据，把目标组合整理成可写入数据库的 JSON。

只返回 JSON 对象，不要 markdown，不要解释。

输出格式：
{{
  "group_profile": {{
    "official_name": "",
    "display_name": "",
    "aliases": [],
    "generation_label": "",
    "generation_note": "",
    "company": "",
    "debut_date": "",
    "activity_period": "",
    "status": "",
    "location": "",
    "summary": "",
    "timeline_events": [
      {{
        "date": "",
        "event": "",
        "evidence_note": ""
      }}
    ],
    "member_roster": {{
      "current_members": [
        {{
          "name": "",
          "positions": [],
          "joined_at": "",
          "left_at": "",
          "note": ""
        }}
      ],
      "former_members": [],
      "project_or_limited_members": []
    }}
  }},
  "member_profiles": [
    {{
      "stage_name": "",
      "full_name": "",
      "aliases": [],
      "birth_date": "",
      "nationality": "",
      "positions": [],
      "group_status": "",
      "joined_at": "",
      "left_at": "",
      "member_status": "",
      "timeline_summary": "",
      "public_identity_summary": "",
      "evidence_note": ""
    }}
  ],
  "verification_notes": {{
    "confirmed_points": [],
    "conflicting_points": [],
    "needs_more_search": []
  }}
}}

规则：
1. 只写证据中明确支持的公开资料，不要脑补。
2. 如果代际存在争议，把争议写进 generation_note，不要写成唯一标准答案。
3. 成员名单要尽量完整；证据不足时宁可留空字段，也不要编造。
4. 时间尽量写绝对日期或明确年份，避免“最近”“后来”。
5. target group: {group_name}

证据：
{raw_evidence}
""".strip()

        try:
            data = await ai_service.call_with_json_retry(
                prompt=prompt,
                max_retries=3,
                temperature=0.1,
                max_tokens=3500,
                expected_type="object",
                auto_mcp=False,
            )
        except Exception as exc:
            logger.warning(f"现实资料结构化失败: group={group_name}, error={exc}")
            return None

        if not isinstance(data, dict) or not isinstance(data.get("group_profile"), dict):
            return None
        return data

    async def _upsert_group_payload(
        self,
        *,
        project: Project,
        group_name: str,
        payload: dict[str, Any],
        existing_characters: list[Character],
        existing_organizations: list[Organization],
        db: AsyncSession,
    ) -> dict[str, int]:
        stats = {
            "created_characters": 0,
            "updated_characters": 0,
            "linked_memberships": 0,
        }

        group_profile = payload.get("group_profile") or {}
        member_profiles = payload.get("member_profiles") or []
        verification_notes = payload.get("verification_notes") or {}

        group_aliases = _dedupe_names(
            [
                group_name,
                str(group_profile.get("display_name") or "").strip(),
                str(group_profile.get("official_name") or "").strip(),
                *[str(alias).strip() for alias in group_profile.get("aliases") or []],
            ]
        )

        group_character = self._find_character(
            existing_characters=existing_characters,
            candidate_names=group_aliases,
            is_organization=True,
        )
        if group_character is None:
            group_character = Character(
                project_id=project.id,
                name=group_aliases[0] if group_aliases else group_name,
                is_organization=True,
                role_type="supporting",
            )
            db.add(group_character)
            existing_characters.append(group_character)
            await db.flush()
            stats["created_characters"] += 1
        else:
            stats["updated_characters"] += 1

        roster = group_profile.get("member_roster") or {}
        current_members = _extract_roster_entries(roster.get("current_members"))
        former_members = _extract_roster_entries(roster.get("former_members"))
        project_members = _extract_roster_entries(roster.get("project_or_limited_members"))

        member_summary_names = _dedupe_names(
            [
                *(entry.get("name") for entry in current_members),
                *(entry.get("name") for entry in former_members),
                *(entry.get("name") for entry in project_members),
            ]
        )
        summary_head = (
            f"现实资料摘要：{group_aliases[0] if group_aliases else group_name}"
            f"；活动期{group_profile.get('activity_period') or '待核实'}"
            f"；状态{group_profile.get('status') or '待核实'}"
            f"；成员{('、'.join(member_summary_names[:12])) or '待补全'}"
        )
        group_background_lines = [
            summary_head[:180],
            f"同步时间: {datetime.now().date().isoformat()}",
            f"组合名: {group_profile.get('display_name') or group_profile.get('official_name') or group_name}",
            f"别名: {'、'.join(group_aliases[1:6]) or '无'}",
            f"代际: {group_profile.get('generation_label') or '待核实'}",
            f"代际备注: {group_profile.get('generation_note') or '无'}",
            f"公司: {group_profile.get('company') or '待核实'}",
            f"出道: {group_profile.get('debut_date') or '待核实'}",
            f"活动期: {group_profile.get('activity_period') or '待核实'}",
            f"状态: {group_profile.get('status') or '待核实'}",
            f"简介: {_clean_text(group_profile.get('summary') or '', max_length=220)}",
            "关键时间线:",
            *_extract_timeline_lines(group_profile.get("timeline_events") or []),
            f"现役/活动期成员: {'、'.join(entry.get('name') for entry in current_members) or '无'}",
            f"前成员: {'、'.join(entry.get('name') for entry in former_members) or '无'}",
            f"限定/企划成员: {'、'.join(entry.get('name') for entry in project_members) or '无'}",
            f"核验补记: {'；'.join(str(item) for item in verification_notes.get('needs_more_search') or []) or '无'}",
        ]

        group_character.name = group_aliases[0] if group_aliases else group_character.name
        group_character.role_type = "supporting"
        group_character.personality = _clean_text(
            "；".join(
                part
                for part in [
                    "现实女团组织卡",
                    group_profile.get("generation_label") or "",
                    group_profile.get("company") or "",
                    group_profile.get("status") or "",
                ]
                if part
            ),
            max_length=120,
        )
        group_character.background = _merge_managed_block(
            group_character.background,
            group_background_lines,
        )
        group_character.organization_type = "现实女团"
        group_character.organization_purpose = _clean_text(
            group_profile.get("summary") or "根据公开资料维护的现实女团组织档案",
            max_length=180,
        )
        group_character.organization_members = json.dumps(
            member_summary_names,
            ensure_ascii=False,
        ) if member_summary_names else None

        organization = next(
            (item for item in existing_organizations if item.character_id == group_character.id),
            None,
        )
        if organization is None:
            organization = Organization(
                character_id=group_character.id,
                project_id=project.id,
            )
            db.add(organization)
            existing_organizations.append(organization)
            await db.flush()

        organization.member_count = len(member_summary_names)
        organization.location = _clean_text(group_profile.get("location") or "", max_length=150) or None
        organization.motto = _clean_text(group_profile.get("generation_note") or "", max_length=120) or None
        organization.color = None

        normalized_member_map: dict[str, dict[str, Any]] = {}
        for member_profile in member_profiles:
            if not isinstance(member_profile, dict):
                continue
            keys = _dedupe_names(
                [
                    str(member_profile.get("stage_name") or "").strip(),
                    str(member_profile.get("full_name") or "").strip(),
                    *[str(alias).strip() for alias in member_profile.get("aliases") or []],
                ]
            )
            for key in keys:
                normalized_member_map[_normalize_name(key)] = member_profile

        roster_status_map = [
            ("active", current_members),
            ("former", former_members),
            ("project", project_members),
        ]
        existing_memberships = (
            await db.execute(
                select(OrganizationMember).where(
                    OrganizationMember.organization_id == organization.id
                )
            )
        ).scalars().all()

        for roster_status, roster_entries in roster_status_map:
            for entry in roster_entries:
                member_name = str(entry.get("name") or "").strip()
                if not member_name:
                    continue

                member_profile = normalized_member_map.get(_normalize_name(member_name)) or {}
                candidate_names = _dedupe_names(
                    [
                        member_name,
                        str(member_profile.get("stage_name") or "").strip(),
                        str(member_profile.get("full_name") or "").strip(),
                        *[str(alias).strip() for alias in member_profile.get("aliases") or []],
                    ]
                )
                member_character = self._find_character(
                    existing_characters=existing_characters,
                    candidate_names=candidate_names,
                    is_organization=False,
                )
                if member_character is None:
                    member_character = Character(
                        project_id=project.id,
                        name=candidate_names[0] if candidate_names else member_name,
                        is_organization=False,
                        role_type="supporting",
                    )
                    db.add(member_character)
                    existing_characters.append(member_character)
                    await db.flush()
                    stats["created_characters"] += 1
                else:
                    stats["updated_characters"] += 1

                positions = _dedupe_names(
                    [
                        *(entry.get("positions") or []),
                        *(member_profile.get("positions") or []),
                    ]
                )
                member_head = (
                    f"现实资料摘要：{member_character.name}"
                    f"；所属{group_aliases[0] if group_aliases else group_name}"
                    f"；状态{member_profile.get('group_status') or roster_status}"
                    f"；定位{('、'.join(positions)) or '待核实'}"
                )
                member_background_lines = [
                    member_head[:180],
                    f"同步时间: {datetime.now().date().isoformat()}",
                    f"艺名: {member_profile.get('stage_name') or member_character.name}",
                    f"本名/常用名: {member_profile.get('full_name') or '待核实'}",
                    f"所属组合: {group_aliases[0] if group_aliases else group_name}",
                    f"国籍: {member_profile.get('nationality') or '待核实'}",
                    f"出生: {member_profile.get('birth_date') or '待核实'}",
                    f"公开定位: {'、'.join(positions) or '待核实'}",
                    f"团内状态: {member_profile.get('group_status') or roster_status}",
                    f"加入: {member_profile.get('joined_at') or entry.get('joined_at') or '待核实'}",
                    f"离开: {member_profile.get('left_at') or entry.get('left_at') or '无'}",
                    f"公开摘要: {_clean_text(member_profile.get('public_identity_summary') or entry.get('note') or '', max_length=220)}",
                    f"时间线摘要: {_clean_text(member_profile.get('timeline_summary') or '', max_length=220)}",
                    f"证据备注: {_clean_text(member_profile.get('evidence_note') or '', max_length=180)}",
                ]

                member_character.name = candidate_names[0] if candidate_names else member_character.name
                member_character.role_type = "supporting"
                member_character.personality = _clean_text(
                    "；".join(
                        part
                        for part in [
                            f"{group_aliases[0] if group_aliases else group_name}成员",
                            member_profile.get("nationality") or "",
                            "、".join(positions),
                        ]
                        if part
                    ),
                    max_length=120,
                )
                member_character.background = _merge_managed_block(
                    member_character.background,
                    member_background_lines,
                )

                membership = next(
                    (
                        item
                        for item in existing_memberships
                        if item.character_id == member_character.id
                    ),
                    None,
                )
                if membership is None:
                    membership = OrganizationMember(
                        organization_id=organization.id,
                        character_id=member_character.id,
                        position=positions[0] if positions else "成员",
                        source="reality_sync",
                    )
                    db.add(membership)
                    existing_memberships.append(membership)
                    stats["linked_memberships"] += 1

                membership.position = positions[0] if positions else membership.position or "成员"
                membership.status = self._map_membership_status(roster_status, member_profile)
                membership.joined_at = (
                    str(member_profile.get("joined_at") or entry.get("joined_at") or "").strip() or None
                )
                membership.left_at = (
                    str(member_profile.get("left_at") or entry.get("left_at") or "").strip() or None
                )
                membership.notes = _clean_text(
                    "；".join(
                        part
                        for part in [
                            member_profile.get("timeline_summary") or "",
                            member_profile.get("public_identity_summary") or "",
                            entry.get("note") or "",
                        ]
                        if part
                    ),
                    max_length=500,
                ) or None

        return stats

    def _find_character(
        self,
        *,
        existing_characters: list[Character],
        candidate_names: list[str],
        is_organization: bool,
    ) -> Optional[Character]:
        normalized_candidates = {
            _normalize_name(name)
            for name in candidate_names
            if _normalize_name(name)
        }
        if not normalized_candidates:
            return None
        for character in existing_characters:
            if bool(character.is_organization) != is_organization:
                continue
            if _normalize_name(character.name) in normalized_candidates:
                return character
        return None

    def _map_membership_status(
        self,
        roster_status: str,
        member_profile: dict[str, Any],
    ) -> str:
        explicit_status = str(member_profile.get("member_status") or "").strip().lower()
        if explicit_status in {"active", "retired", "expelled", "deceased"}:
            return explicit_status
        if roster_status == "former":
            return "retired"
        return "active"


reality_fact_sync_service = RealityFactSyncService()
