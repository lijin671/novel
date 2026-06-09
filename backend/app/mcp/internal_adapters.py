"""项目内置 MCP 适配器。

把非 MCP 协议的第三方接口包装成可供现有 MCP 门面调用的本地工具。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol
from urllib.parse import parse_qsl, urlparse, urlunparse

import httpx

from app.logger import get_logger

logger = get_logger(__name__)


class BuiltinToolAdapter(Protocol):
    """内置工具适配器协议。"""

    adapter_name: str

    async def list_tools(self) -> List[Dict[str, Any]]:
        """返回工具定义。"""

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用工具。"""

    async def health_check(self) -> Dict[str, Any]:
        """健康检查。"""

    async def aclose(self) -> None:
        """释放资源。"""


@dataclass(frozen=True)
class BuiltinAdapterContext:
    """内置适配器运行上下文。"""

    user_id: str
    plugin_name: str
    base_url: str
    headers: Dict[str, str]
    config: Dict[str, Any]
    timeout: float = 60.0


class BuiltinAdapterError(Exception):
    """内置适配器调用异常。"""


class ExaRestAdapter:
    """Exa REST 搜索适配器。"""

    adapter_name = "exa_rest"

    def __init__(self, context: BuiltinAdapterContext):
        self.context = context
        self.base_url, url_query_params = self._normalize_base_url(context.base_url)
        configured_query_params = context.config.get("query_params") or {}
        self.query_params = {
            **url_query_params,
            **configured_query_params,
        }
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **(context.headers or {}),
        }
        self.timeout = context.timeout

    @staticmethod
    def _normalize_base_url(raw_url: str) -> tuple[str, Dict[str, str]]:
        base_url = (raw_url or "").strip().rstrip("/")
        if not base_url:
            raise BuiltinAdapterError("Exa REST 适配器缺少 base_url 配置")

        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise BuiltinAdapterError("Exa REST 地址格式无效，请填写完整的 http(s) 地址")

        path = parsed.path.rstrip("/")
        for suffix in ("/search", "/answer", "/answers", "/contents"):
            if path.lower().endswith(suffix):
                path = path[: -len(suffix)]
                break

        normalized_url = urlunparse((parsed.scheme, parsed.netloc, path, "", "", "")).rstrip("/")
        if not normalized_url:
            normalized_url = f"{parsed.scheme}://{parsed.netloc}"

        query_params = {
            key: value
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key
        }
        return normalized_url, query_params

    async def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search",
                "description": (
                    "检索公开网页资料，适合核对现实人物、女团、成员名单、所属公司、出道日、"
                    "退团/毕业/解散节点与公开活动时间线。"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "检索语句，建议直接写组合名、成员名或时间线需求。",
                        },
                        "numResults": {
                            "type": "integer",
                            "description": "返回结果条数，默认 5。",
                            "minimum": 1,
                            "maximum": 25,
                        },
                        "includeDomains": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "限制检索域名列表。",
                        },
                        "excludeDomains": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "排除域名列表。",
                        },
                        "startPublishedDate": {
                            "type": "string",
                            "description": "起始发布日期，ISO-8601 格式。",
                        },
                        "endPublishedDate": {
                            "type": "string",
                            "description": "结束发布日期，ISO-8601 格式。",
                        },
                        "type": {
                            "type": "string",
                            "description": "Exa 搜索类型，如 keyword / neural / auto。",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "answer",
                "description": "对公开资料问题生成检索型回答，适合先做事实核对再补充来源线索。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "问题描述，例如某女团完整成员名单或某成员加入/退出时间。",
                        }
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "contents",
                "description": "按 Exa 结果 ID 或 URL 拉取页面内容，适合补齐成员资料与时间线细节。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Exa 搜索结果 ID 列表。",
                        },
                        "urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "网页 URL 列表。",
                        },
                    },
                },
            },
        ]

    async def health_check(self) -> Dict[str, Any]:
        result = await self._post("/search", {"query": "TWICE 成员", "numResults": 1})
        return {
            "success": True,
            "message": "Exa REST 适配器连接正常",
            "tools_count": len(await self.list_tools()),
            "result_preview": self._build_preview(result),
        }

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name == "search":
            return await self._call_search(arguments)
        if tool_name == "answer":
            return await self._call_answer(arguments)
        if tool_name == "contents":
            return await self._call_contents(arguments)
        raise BuiltinAdapterError(f"未知的 Exa REST 工具: {tool_name}")

    async def aclose(self) -> None:
        return None

    async def _call_search(self, arguments: Dict[str, Any]) -> Any:
        query = str(arguments.get("query") or "").strip()
        if not query:
            raise BuiltinAdapterError("search 工具缺少 query 参数")

        payload: Dict[str, Any] = {"query": query, "numResults": arguments.get("numResults", 5)}
        for key in (
            "includeDomains",
            "excludeDomains",
            "startPublishedDate",
            "endPublishedDate",
            "type",
            "includeText",
            "useAutoprompt",
            "category",
        ):
            value = arguments.get(key)
            if value not in (None, "", []):
                payload[key] = value

        return await self._post("/search", payload)

    async def _call_answer(self, arguments: Dict[str, Any]) -> Any:
        query = str(arguments.get("query") or "").strip()
        if not query:
            raise BuiltinAdapterError("answer 工具缺少 query 参数")

        payload = {"query": query}
        try:
            return await self._post("/answer", payload)
        except BuiltinAdapterError as exc:
            if "404" not in str(exc):
                raise
        return await self._post("/answers", payload)

    async def _call_contents(self, arguments: Dict[str, Any]) -> Any:
        ids = arguments.get("ids")
        urls = arguments.get("urls")
        if not ids and not urls:
            raise BuiltinAdapterError("contents 工具至少需要 ids 或 urls 其中一个参数")

        payload: Dict[str, Any] = {}
        if ids:
            payload["ids"] = ids
        if urls:
            payload["urls"] = urls
        return await self._post("/contents", payload)

    async def _post(self, path: str, payload: Dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    params=self.query_params or None,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            detail = self._extract_error_message(exc.response)
            raise BuiltinAdapterError(
                f"Exa REST 请求失败 ({exc.response.status_code}): {detail}"
            ) from exc
        except httpx.RequestError as exc:
            raise BuiltinAdapterError(f"Exa REST 网络请求失败: {exc}") from exc
        except ValueError as exc:
            raise BuiltinAdapterError(f"Exa REST 返回了无法解析的 JSON 响应: {exc}") from exc

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            text = response.text.strip()
            return text[:200] if text else "未知错误"

        if isinstance(payload, dict):
            for key in ("error", "message", "detail"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            return str(payload)

        return str(payload)

    @staticmethod
    def _build_preview(result: Any) -> str:
        if isinstance(result, dict):
            for key in ("answer", "summary"):
                value = result.get(key)
                if isinstance(value, str) and value.strip():
                    return value[:160]

            results = result.get("results")
            if isinstance(results, list) and results:
                first_item = results[0]
                if isinstance(first_item, dict):
                    title = str(first_item.get("title") or "").strip()
                    url = str(first_item.get("url") or "").strip()
                    preview = " / ".join(part for part in (title, url) if part)
                    if preview:
                        return preview[:160]
        return "请求成功"


def create_builtin_adapter(context: BuiltinAdapterContext) -> BuiltinToolAdapter:
    """根据配置创建内置适配器实例。"""

    adapter_name = str(context.config.get("builtin_adapter") or "").strip().lower()
    if adapter_name == ExaRestAdapter.adapter_name:
        logger.info("创建内置适配器: exa_rest")
        return ExaRestAdapter(context)

    raise BuiltinAdapterError(f"未知的内置适配器类型: {adapter_name or '未配置'}")
