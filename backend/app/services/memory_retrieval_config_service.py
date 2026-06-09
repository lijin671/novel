"""记忆检索配置服务。"""
import copy
import json
import time
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import get_engine
from app.logger import get_logger
from app.models.settings import Settings

logger = get_logger(__name__)

MEMORY_RETRIEVAL_VERSION = "1.0"
MEMORY_RETRIEVAL_CONFIG_KEY = "memory_retrieval"
SUPPORTED_MEMORY_TYPES = [
    "chapter_summary",
    "foreshadow",
    "hook",
    "plot_point",
    "character_event",
]
DEFAULT_MEMORY_SCENARIO_TYPES = {
    "chapter_generation": ["chapter_summary", "foreshadow", "hook", "plot_point"],
    "character_context": ["character_event", "chapter_summary", "plot_point"],
    "plot_context": ["plot_point", "hook", "foreshadow", "chapter_summary"],
}
_CACHE_TTL_SECONDS = 60
_user_config_cache: Dict[str, Dict[str, Any]] = {}


def get_default_memory_retrieval_config() -> Dict[str, Any]:
    """返回默认记忆检索配置。"""
    return {
        "version": MEMORY_RETRIEVAL_VERSION,
        "scenario_types": copy.deepcopy(DEFAULT_MEMORY_SCENARIO_TYPES),
    }


def parse_preferences_json(
    preferences: Optional[str],
    *,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """解析 settings.preferences，异常时回退为空字典。"""
    if not preferences:
        return {}

    try:
        parsed = json.loads(preferences)
    except (json.JSONDecodeError, TypeError) as exc:
        if user_id:
            logger.warning(f"解析用户 {user_id} 的 preferences 失败，回退默认记忆检索配置: {exc}")
        else:
            logger.warning(f"解析 preferences 失败，回退默认记忆检索配置: {exc}")
        return {}

    return parsed if isinstance(parsed, dict) else {}


def normalize_memory_types(memory_types: Optional[List[Any]]) -> List[str]:
    """过滤并去重记忆类型。"""
    if not isinstance(memory_types, list):
        return []

    normalized: List[str] = []
    seen = set()
    for item in memory_types:
        memory_type = str(item or "").strip()
        if not memory_type or memory_type in seen:
            continue
        if memory_type not in SUPPORTED_MEMORY_TYPES:
            continue
        seen.add(memory_type)
        normalized.append(memory_type)

    return normalized


def normalize_memory_retrieval_config(raw_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """将原始配置归一化为稳定结构。"""
    config = get_default_memory_retrieval_config()
    if not isinstance(raw_config, dict):
        return config

    scenario_types = raw_config.get("scenario_types")
    if isinstance(scenario_types, dict):
        for key, values in scenario_types.items():
            scenario = str(key or "").strip()
            if not scenario:
                continue
            config["scenario_types"][scenario] = normalize_memory_types(values)

    version = str(raw_config.get("version") or MEMORY_RETRIEVAL_VERSION).strip()
    config["version"] = version or MEMORY_RETRIEVAL_VERSION
    return config


def get_memory_retrieval_config_from_preferences(
    preferences: Optional[str],
    *,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """从 preferences 中提取记忆检索配置。"""
    prefs = parse_preferences_json(preferences, user_id=user_id)
    return normalize_memory_retrieval_config(prefs.get(MEMORY_RETRIEVAL_CONFIG_KEY))


def merge_memory_retrieval_config(
    current_config: Optional[Dict[str, Any]],
    scenario_overrides: Optional[Dict[str, Optional[List[str]]]]
) -> Dict[str, Any]:
    """将局部更新合并到现有配置中。"""
    config = normalize_memory_retrieval_config(current_config)
    if not isinstance(scenario_overrides, dict):
        return config

    for key, values in scenario_overrides.items():
        scenario = str(key or "").strip()
        if not scenario:
            continue

        if values is None:
            if scenario in DEFAULT_MEMORY_SCENARIO_TYPES:
                config["scenario_types"][scenario] = list(DEFAULT_MEMORY_SCENARIO_TYPES[scenario])
            else:
                config["scenario_types"].pop(scenario, None)
            continue

        config["scenario_types"][scenario] = normalize_memory_types(values)

    return config


def update_memory_retrieval_preferences(
    preferences: Optional[str],
    scenario_overrides: Optional[Dict[str, Optional[List[str]]]],
    *,
    user_id: Optional[str] = None
) -> tuple[str, Dict[str, Any]]:
    """更新 preferences 中的记忆检索配置。"""
    prefs = parse_preferences_json(preferences, user_id=user_id)
    merged_config = merge_memory_retrieval_config(
        prefs.get(MEMORY_RETRIEVAL_CONFIG_KEY),
        scenario_overrides,
    )
    prefs[MEMORY_RETRIEVAL_CONFIG_KEY] = merged_config
    return json.dumps(prefs, ensure_ascii=False), merged_config


def invalidate_user_memory_retrieval_config_cache(user_id: str) -> None:
    """清理指定用户的记忆检索配置缓存。"""
    _user_config_cache.pop(user_id, None)


async def _load_user_preferences(user_id: str) -> Optional[str]:
    """从数据库读取用户 preferences。"""
    engine = await get_engine(user_id)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        result = await session.execute(
            select(Settings.preferences).where(Settings.user_id == user_id)
        )
        return result.scalar_one_or_none()


async def get_user_memory_retrieval_config(
    user_id: str,
    *,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """获取用户生效中的记忆检索配置。"""
    cache_key = str(user_id or "").strip()
    if not cache_key:
        return get_default_memory_retrieval_config()

    now = time.monotonic()
    cached = _user_config_cache.get(cache_key)
    if cached and not force_refresh:
        loaded_at = float(cached.get("loaded_at", 0.0))
        if now - loaded_at < _CACHE_TTL_SECONDS:
            return copy.deepcopy(cached["config"])

    try:
        preferences = await _load_user_preferences(cache_key)
        config = get_memory_retrieval_config_from_preferences(
            preferences,
            user_id=cache_key,
        )
    except Exception as exc:
        logger.warning(f"读取用户 {cache_key} 的记忆检索配置失败，使用默认配置: {exc}")
        config = get_default_memory_retrieval_config()

    _user_config_cache[cache_key] = {
        "config": copy.deepcopy(config),
        "loaded_at": now,
    }
    return copy.deepcopy(config)
