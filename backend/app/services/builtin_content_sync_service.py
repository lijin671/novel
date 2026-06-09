"""内置内容同步服务。"""
from dataclasses import dataclass
from pathlib import Path
import re
import uuid
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import get_engine
from app.logger import get_logger
from app.models.prompt_workshop import PromptWorkshopItem
from app.models.writing_style import WritingStyle

logger = get_logger(__name__)

PROJECT_CONSISTENCY_PRESET_ID = "project_consistency"
PROJECT_CONSISTENCY_PRESET_NAME = "长篇一致性（项目版）"
PROJECT_CONSISTENCY_PRESET_DESCRIPTION = (
    "面向长篇续写、断更续写和拆书二创的项目型风格预设，"
    "强调增量衔接、角色稳定、伏笔回收与按需考据。"
)
PROJECT_CONSISTENCY_PRESET_PROMPT = """写作要求：

1. 你正在 MuMuAINovel 的项目工作台中创作，必须以当前章节大纲、上一章衔接锚点、上一章摘要、最近章节上下文、相关记忆、伏笔提醒、角色与职业信息为准。
2. 不伪造已读内容，不把信息缺口补成既成事实；如果上下文不足，优先保守续写，不强行发明隐藏剧情。
3. 默认采用增量续写，只写本章新增推进，不要把上一章换一种说法再复述一遍。
4. 先保时间线、人物关系、利益链、伤势与资源状态、伏笔状态，再追求辞藻和气氛。
5. 配角不能只是工具人。关键配角必须有目标、顾虑、筹码、误判和反应。
6. 爽点必须落到具体结果：行动成败、地位变化、利益得失、情报推进、关系变化，避免空喊口号。
7. 涉及现实资料时仅按需核验；未核验的现实细节不要装懂，不要为了联网而联网。
8. 输出正文时去掉解释腔，不写“上一章提要”“作者有话说”“本章总结”等元信息。"""

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROMT_DIR = PROJECT_ROOT / "promt"
BUILTIN_PROMPT_SOURCE = "builtin:prompt-assets"
BUILTIN_WORKSHOP_NAMESPACE = uuid.UUID("2d740346-5c3a-41ba-bc21-76878b84ce4d")

SAFE_PROMT_FILENAMES = (
    "255-多子多福-创意阶段-灵感捕捉.md",
    "256-多子多福-创意阶段-市场定位.md",
    "257-多子多福-创意阶段-核心梗设计.md",
    "258-多子多福-创意阶段-金手指设计.md",
    "259-多子多福-设定阶段-世界观设定.md",
    "260-多子多福-设定阶段-人物设定.md",
    "261-多子多福-设定阶段-等级体系设计.md",
    "262-多子多福-设定阶段-天赋系统.md",
    "263-多子多福-框架阶段-故事线.md",
    "264-多子多福-框架阶段-场景设计.md",
    "265-多子多福-框架阶段-章节纲.md",
    "266-多子多福-框架阶段-细纲.md",
    "267-多子多福-创作阶段-章节创作.md",
    "268-多子多福-创作阶段-修订润色.md",
    "269-多子多福-创作阶段-语言润色.md",
    "271-多子多福-进阶技巧-爽点设计.md",
    "272-多子多福-进阶技巧-战斗场景.md",
    "273-多子多福-进阶技巧-日常场景.md",
    "274-多子多福-进阶技巧-节奏校准.md",
    "275-多子多福-进阶技巧-金手指使用.md",
    "276-多子多福-进阶技巧-反派视角.md",
    "277-多子多福-辅助工具-灵感捕捉.md",
    "278-多子多福-辅助工具-卡文急救.md",
    "279-多子多福-辅助工具-整书拆解.md",
    "300-多子多福-辅助-情感词汇库.md",
    "340-多子多福-进阶-尺度把控.md",
    "341-多子多福-进阶-爽点节奏设计.md",
    "342-多子多福-进阶-情感高潮设计.md",
    "343-多子多福-进阶-后宫互动设计.md",
    "344-多子多福-进阶-系统平衡设计.md",
    "345-多子多福-创作流程.md",
)

HIGH_RISK_KEYWORDS = (
    "黑暗多子多福",
    "非自愿",
    "强迫",
    "强制",
    "强占",
    "乱伦",
    "凌辱",
    "窒息",
    "寄生",
    "人体实验",
    "绝对支配",
    "病态支配",
    "容器",
    "洗脑",
    "驯化",
    "调教",
)


@dataclass(frozen=True)
class BuiltinWorkshopSeed:
    """官方提示词工坊种子条目。"""

    source_key: str
    name: str
    description: str
    prompt_content: str
    category: str
    tags: tuple[str, ...]


def _stable_workshop_item_id(source_key: str) -> str:
    """基于来源键生成稳定 UUID，确保重复同步时可更新。"""
    return str(uuid.uuid5(BUILTIN_WORKSHOP_NAMESPACE, source_key))


def _normalize_tags(*groups: Iterable[str]) -> list[str]:
    """标签去重并保序。"""
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


def _display_name_from_filename(filename: str) -> str:
    """将文件名转换为更适合在工坊展示的名称。"""
    stem = re.sub(r"^\d+-", "", Path(filename).stem)
    parts = [part for part in stem.split("-") if part]
    return " · ".join(parts) if parts else Path(filename).stem


def _extract_description(content: str) -> str:
    """从 Markdown 中提取一段简短描述。"""
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("#", "|", "```", "-", "*")):
            continue
        cleaned = re.sub(r"\s+", " ", line)
        return cleaned[:110] + ("..." if len(cleaned) > 110 else "")
    return "本地提示词库同步条目"


def _infer_category(filename: str, content: str) -> str:
    """按文件名和内容推断工坊分类。"""
    haystack = f"{filename}\n{content}"
    if any(keyword in haystack for keyword in ("仙侠", "修仙", "修真", "玄幻", "老祖")):
        return "fantasy"
    if any(keyword in haystack for keyword in ("末世", "丧尸", "校园", "惊悚")):
        return "horror"
    if any(keyword in haystack for keyword in ("都市", "职场", "直播")):
        return "urban"
    return "other"


def _build_local_tags(filename: str, content: str) -> list[str]:
    """从文件名提取尽量稳定的标签。"""
    stem = re.sub(r"^\d+-", "", Path(filename).stem)
    filename_parts = [part for part in stem.split("-") if part]
    detected_tags: list[str] = []
    for keyword in (
        "多子多福",
        "创意阶段",
        "设定阶段",
        "框架阶段",
        "创作阶段",
        "进阶技巧",
        "辅助工具",
        "创作流程",
        "市场定位",
        "核心梗",
        "金手指",
        "世界观",
        "人物设定",
        "章节创作",
        "节奏",
        "系统平衡",
    ):
        if keyword in filename or keyword in content:
            detected_tags.append(keyword)

    return _normalize_tags(
        ("官方精选", "本地提示词库", "低风险"),
        filename_parts,
        detected_tags,
    )


def _is_safe_local_prompt(filename: str, content: str) -> bool:
    """过滤不适合直接接入官方工坊的高风险条目。"""
    haystack = f"{filename}\n{content}"
    return not any(keyword in haystack for keyword in HIGH_RISK_KEYWORDS)


def _build_custom_prompt_seeds() -> list[BuiltinWorkshopSeed]:
    """构建本轮新增的官方精选提示词。"""
    return [
        BuiltinWorkshopSeed(
            source_key="curated/dz001-market-positioning",
            name="DZ-001 · 长生老祖 · 市场定位与核心卖点",
            description="围绕“寿元续命 + 家族修仙 + 全族反馈”整理仙侠家族流的定位、卖点和风险约束。",
            category="fantasy",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "多子多福", "仙侠", "家族修仙", "寿元流", "低风险", "DZ-001"),
                )
            ),
            prompt_content="""# DZ-001 · 长生老祖 · 市场定位与核心卖点

## 系统角色

你是一位擅长仙侠家族流的题材策划师，负责把“寿元续命 + 家族修仙 + 全族反馈”打磨成可落地的商业化核心梗。

## 核心任务

1. 明确一句话卖点、目标读者、题材标签。
2. 设计前中后期增长曲线：续命求生 → 家族扩张 → 诸天争霸。
3. 强化“老祖威严、护短、资源掌控、家族整体成长”的爽感。
4. 输出适合继续喂给后续设定设计、章节大纲、角色矩阵的结构化结果。

## 强约束

1. 主角必须保留老祖身份的威严和掌控力，但人物关系推进必须建立在明确自愿、互利合作或长期情感积累基础上。
2. 不写强迫、羞辱、非自愿、物化式征服，不把女性角色写成纯工具。
3. 每个爽点都要落到具体结果：寿元增加、家族位阶提升、领地扩张、战力变化、势力震动。
4. 早期必须保留寿元紧迫感，中期必须转向家族经营，后期再逐步升级为横扫诸天。

## 输入插槽

- inspiration_id
- inspiration_source
- inspiration_type
- inspiration_description
- expansion_direction
- priority_score
- development_suggestion

## 输出要求

```json
{
  "market_positioning_report": {
    "one_sentence_hook": "",
    "core_selling_points": [],
    "target_audience": "",
    "growth_curve": {
      "early_stage": "",
      "middle_stage": "",
      "late_stage": ""
    },
    "commercial_highlights": []
  },
  "creation_guardrails": {
    "must_keep": [],
    "must_avoid": [],
    "balance_notes": []
  }
}
```""",
        ),
        BuiltinWorkshopSeed(
            source_key="curated/dz001-system-world",
            name="DZ-001 · 长生老祖 · 系统与世界观设计",
            description="聚焦寿元资产化、全族经验反馈、腐朽末法世界与家族奇观体系的系统设定模板。",
            category="fantasy",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "多子多福", "仙侠", "系统设计", "世界观", "低风险", "DZ-001"),
                )
            ),
            prompt_content="""# DZ-001 · 长生老祖 · 系统与世界观设计

## 系统角色

你是一位长篇仙侠系统架构师，负责搭建“长生老祖”题材可持续连载的世界观和系统机制。

## 设计重点

1. 建立“寿元资产化”主循环：寿元是生存压力，也是资源货币。
2. 建立“全族经验池”副循环：子嗣、族人、家族奇观共同反哺主角。
3. 用“腐朽末法 / 资源垄断 / 血脉品阶制”解释主角为何必须走家族路线。
4. 设计清晰的限制机制，避免第十章就彻底失控。

## 强约束

1. 成长曲线必须分层：前期求生，中期经营，后期指数扩张。
2. 系统奖励不能只围绕感情关系，必须纳入炼丹、阵法、商道、领地、族运、情报等势力模块。
3. 不把“繁衍”写成粗暴数值刷取，要给出因果代价、资源消耗、家族管理成本。
4. 不写非自愿关系绑定，不写靠羞辱或强制制造“忠诚”。

## 输入插槽

- core_concept
- protagonist_profile
- family_goal
- worldview_seed
- risk_notes

## 输出要求

```json
{
  "system_design": {
    "system_name": "",
    "core_loops": [],
    "resource_types": [],
    "limitation_rules": [],
    "family_buildings": []
  },
  "world_setting": {
    "era_background": "",
    "social_structure": "",
    "regional_map": [],
    "main_factions": [],
    "core_conflicts": []
  },
  "balance_guardrails": {
    "anti_runaway_rules": [],
    "late_game_pressure": [],
    "serialization_notes": []
  }
}
```""",
        ),
        BuiltinWorkshopSeed(
            source_key="curated/dz001-character-matrix",
            name="DZ-001 · 长生老祖 · 角色与家族矩阵",
            description="将陈远、正妻、侧室、家族骨干与子嗣管理规则整理为长篇连载可维护的人物矩阵。",
            category="fantasy",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "多子多福", "仙侠", "人物设定", "女主矩阵", "家族经营", "低风险", "DZ-001"),
                )
            ),
            prompt_content="""# DZ-001 · 长生老祖 · 角色与家族矩阵

## 系统角色

你是一位长篇群像角色设计师，负责把“老祖 + 正妻 + 侧室 + 子嗣 + 家族骨干”整理成可长期维护的人物矩阵。

## 设计重点

1. 主角要兼具威严、护短、谋略与长期目标，不写成无脑后宫工具。
2. 每位女主都必须有独立目标、技能专长、家族岗位和剧情功能。
3. 家族骨干与子嗣要形成管理链条，避免角色越写越乱。
4. 提前定义“人物出场节奏、地位晋升、情感推进、冲突协调”规则。

## 强约束

1. 禁止把女主写成纯生育工具或纯争宠机器。
2. 情感推进必须有事件支点：救助、合作、共同守家、价值认同、长期陪伴。
3. 每位关键角色必须写出目标、顾虑、筹码、误判和成长代价。
4. 输出必须方便后续转为角色卡、章节导演脚本和家族档案。

## 输入插槽

- protagonist_seed
- female_character_pool
- family_positions
- conflict_needs

## 输出要求

```json
{
  "protagonist_design": {},
  "female_character_matrix": [],
  "family_management_map": {
    "inner_court": [],
    "martial": [],
    "finance": [],
    "alchemy_and_array": []
  },
  "offspring_archive_rules": {
    "naming_rules": "",
    "growth_tracking_fields": [],
    "chapter_update_rules": []
  }
}
```""",
        ),
        BuiltinWorkshopSeed(
            source_key="curated/apocalypse-campus-safe-positioning",
            name="末世校园多子题材 · 安全化定位",
            description="将“校园末世 + 多子成长”改写为更适合商用平台的生存向、契约向、基地经营向提示词。",
            category="horror",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "末世", "校园", "多子多福", "轻黑暗", "安全改写"),
                )
            ),
            prompt_content="""# 末世校园多子题材 · 安全化定位

## 系统角色

你是一位末世生存题材策划师，负责把“封闭校园 + 丧尸狂潮 + 家族成长”改写成适合商业平台的轻黑暗多子题材。

## 核心任务

1. 提炼“安全屋 / 免疫源 / 队伍扩张 / 子嗣反哺”的主循环。
2. 把原本偏极端的支配感改写为资源契约、组织秩序、求生联盟和家族成长。
3. 让题材保留压迫感和危机感，但不踩平台高风险线。

## 强约束

1. 所有亲密关系必须建立在明确自愿、契约合作或情感升温基础上。
2. 不写强占、标记、强制净化、性暴力、活体实验、物化称呼等高风险内容。
3. 子嗣或后代设定要偏“血脉觉醒 / 萌系强战力 / 家族守护者”，不走怪物寄生路线。
4. 冲突核心放在资源、信任、组织秩序、丧尸围城和队伍升级上。

## 输入插槽

- setting_tag
- target_audience
- dark_intensity
- protagonist_seed
- campus_resource_map

## 输出要求

```json
{
  "system_overview": {
    "core_hook": "",
    "survival_loop": [],
    "team_growth_loop": []
  },
  "risk_control": {
    "allowed_darkness": [],
    "must_avoid": [],
    "platform_adaptation": []
  },
  "chapter_opening_strategy": {
    "chapter_1": "",
    "chapter_2": "",
    "chapter_3": ""
  }
}
```""",
        ),
        BuiltinWorkshopSeed(
            source_key="curated/apocalypse-campus-safe-flow",
            name="末世校园多子题材 · 安全化创作流程",
            description="将轻黑暗末世校园题材拆成可执行的创作阶段，方便在本地项目中按阶段调用。",
            category="horror",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "末世", "校园", "创作流程", "轻黑暗", "安全改写"),
                )
            ),
            prompt_content="""# 末世校园多子题材 · 安全化创作流程

## 系统角色

你是一位末世题材流程设计师，负责把“校园求生 + 家族成长 + 轻黑暗氛围”拆解为能稳定执行的写作流水线。

## 阶段建议

1. 创意阶段：确定病毒规则、校园地图、主角优势、初始生存小队。
2. 设定阶段：建立安全屋、物资循环、异能来源、后代成长机制。
3. 框架阶段：拆出“封锁求生 → 食堂争夺 → 校园清扫 → 城市扩张”的里程碑。
4. 创作阶段：每章都要有危机、选择、推进、反哺、留钩。
5. 复盘阶段：检查角色关系、物资消耗、战力平衡、感染风险、记忆回写。

## 强约束

1. 整个流程默认按轻黑暗到中黑暗执行，主打压迫感，不主打极端刺激。
2. 章节爆点优先选择救援、反杀、据点升级、关系升温、后代觉醒、队伍扩编。
3. 不写高风险血腥癖、人体实验癖、非自愿关系、未成年擦边内容。

## 输入插槽

- current_stage
- dark_intensity
- target_platform
- word_count_target
- current_problem

## 输出要求

```json
{
  "current_stage_goal": "",
  "required_inputs": [],
  "recommended_outputs": [],
  "next_step_prompts": [],
  "risk_checklist": []
}
```""",
        ),
        BuiltinWorkshopSeed(
            source_key="curated/irl-girlgroup-organization-timeline",
            name="现实女团资料构建 · 组合档案与现实时间线",
            description="按公开资料核对女团组合名、代际口径、公司、出道与活动节点、退团毕业解散时间和完整成员名单。",
            category="other",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "现实资料", "女团", "K-pop", "时间线", "组织设定", "IZ*ONE", "TWICE", "(G)I-DLE", "ITZY", "NMIXX", "低风险"),
                )
            ),
            prompt_content="""# 现实女团资料构建 · 组合档案与现实时间线

## 系统角色

你是一位专门处理现实娱乐公开资料的设定研究员，负责把女团组合档案整理成可直接用于组织卡和世界书的结构化底稿。

## 核心任务

1. 先检索公开资料，再整理组合的中英文常见写法、所属公司、出道日期、活动期和重要节点。
2. 按现实世界时间线记录改名、重组、毕业、退团、回归、解散、限定活动期等信息。
3. 尽量补齐完整成员名单，并区分现役成员、历任成员、限定企划成员和毕业成员。
4. 需要时标注常见代际口径，例如二代、三代、四代、五代、六代，但不能把有争议的口径写成绝对事实。

## 强约束

1. 如果启用了 MCP / 搜索工具，涉及现实女团、成员名单、时间线时必须先检索，不能凭印象补全。
2. 不能编造不存在的成员、出道日、退团节点、公司变更或解散信息。
3. 时间信息优先写成绝对日期或明确年月，避免只写“后来”“当时”“近年”。
4. 若不同来源存在分歧，要写出“常见口径”“另一种口径”或“待核实”，不要强行合并成单一结论。
5. 只使用公开资料，不添加私密传闻、饭圈脑补或未证实内部消息。

## 常见覆盖范围提示

- 二代常见示例：Girls' Generation、KARA、Wonder Girls、2NE1、T-ARA、Apink
- 三代常见示例：TWICE、Red Velvet、BLACKPINK、GFRIEND、MAMAMOO、OH MY GIRL、WJSN、Lovelyz
- 四代常见示例：IZ*ONE、(G)I-DLE、ITZY、aespa、STAYC、IVE、LE SSERAFIM、NMIXX、Kep1er、fromis_9
- 五代常见示例：NewJeans、tripleS、KISS OF LIFE、BABYMONSTER、ILLIT
- 六代口径争议更大，不要预设唯一清单，必须按用户指定和检索结果标注“常见归类 / 待核实”

## 输入插槽

- group_name
- alias
- focus_year_range
- known_clues
- need_member_completeness

## 输出要求

```json
{
  "group_profile": {
    "official_name": "",
    "aliases": [],
    "generation_label": "",
    "generation_note": "",
    "company": "",
    "debut_date": "",
    "activity_period": "",
    "status": "",
    "timeline_events": [
      {
        "date": "",
        "event": "",
        "evidence_note": ""
      }
    ],
    "member_roster": {
      "current_members": [],
      "former_members": [],
      "project_or_limited_members": []
    }
  },
  "verification_notes": {
    "confirmed_points": [],
    "conflicting_points": [],
    "needs_more_search": []
  }
}
```""",
        ),
        BuiltinWorkshopSeed(
            source_key="curated/irl-girlgroup-member-profile",
            name="现实女团资料构建 · 成员角色卡补全",
            description="按公开资料补齐艺名、本名、国籍、队内定位、所属组合、加入出道毕业退团时间和角色卡字段。",
            category="other",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "现实资料", "角色卡", "女团成员", "K-pop", "IZ*ONE", "TWICE", "(G)I-DLE", "ITZY", "NMIXX", "低风险"),
                )
            ),
            prompt_content="""# 现实女团资料构建 · 成员角色卡补全

## 系统角色

你是一位专门整理现实偶像公开档案的角色卡编辑，负责把成员资料压缩成可直接用于角色生成功能的干净底座。

## 核心任务

1. 先检索公开资料，再核对艺名、本名、出生年或完整生日、国籍、所属组合和队内定位。
2. 记录成员加入、出道、活动暂停、毕业、退团、解散后再出道等关键时间节点。
3. 如果成员参与过多个组合、限定团、子团、企划团，要按时间顺序整理所属关系。
4. 生成给角色系统使用的摘要字段，例如外界常见印象、公开技能标签、代表活动期和公开身份变化。

## 强约束

1. 只能写公开资料，不写住址、私生活、绯闻、未证实恋爱、私密关系或饭圈推测。
2. 涉及年龄时优先使用出生日期或出生年份，不要写易过期的“现在 XX 岁”，除非用户明确要求。
3. 队内定位若随时期变化，要注明“常见定位 / 不同时期定位差异”。
4. 不能把同名不同人、改艺名前后身份、日韩中译名混在一起。
5. 若资料不完整，要明确写“待补充检索”，不能假设填空。

## 输入插槽

- member_name
- possible_group
- target_fields
- known_aliases
- focus_time_range

## 输出要求

```json
{
  "member_profile": {
    "stage_name": "",
    "legal_or_common_name": "",
    "birth_date": "",
    "nationality": "",
    "group_affiliations": [
      {
        "group_name": "",
        "role": "",
        "started_at": "",
        "ended_at": "",
        "note": ""
      }
    ],
    "public_positions": [],
    "public_keywords": [],
    "timeline_summary": [],
    "character_card_ready_summary": ""
  },
  "verification_notes": {
    "confirmed_points": [],
    "ambiguous_points": [],
    "missing_fields": []
  }
}
```""",
        ),
        BuiltinWorkshopSeed(
            source_key="curated/irl-girlgroup-generation-coverage",
            name="现实女团资料构建 · 二到六代常见组合覆盖清单",
            description="给模型明确二到六代常见女团的检索覆盖面，并要求对代际争议保持标注而非硬判定。",
            category="other",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "现实资料", "代际划分", "女团清单", "K-pop", "检索覆盖", "低风险"),
                )
            ),
            prompt_content="""# 现实女团资料构建 · 二到六代常见组合覆盖清单

## 系统角色

你是一位负责检索规划的资料编目员，需要先扩大检索覆盖面，再按女团代际与活动期梳理优先级。

## 使用目标

1. 给模型一个“先搜哪些团、哪些代际最常被用户提到”的范围底图。
2. 避免只盯着单一组合，导致组织与成员模板覆盖不全。
3. 在用户没有写全团名时，也能根据代际和公司快速扩展候选清单。

## 常见口径示例

- 二代常见示例：Girls' Generation、KARA、Wonder Girls、2NE1、T-ARA、Apink
- 三代常见示例：TWICE、Red Velvet、BLACKPINK、GFRIEND、MAMAMOO、OH MY GIRL、WJSN、Lovelyz
- 四代常见示例：IZ*ONE、(G)I-DLE、ITZY、aespa、STAYC、IVE、LE SSERAFIM、NMIXX、Kep1er、fromis_9
- 五代常见示例：NewJeans、tripleS、KISS OF LIFE、BABYMONSTER、ILLIT
- 六代：不写死唯一答案，必须结合用户指定、当下公开口径和检索结果，标注“常见归类 / 有争议 / 待核实”

## 强约束

1. 以上仅是检索示例清单，不是唯一正确答案，不得把争议口径写成官方标准。
2. 用户点名的组合必须优先覆盖，例如 IZ*ONE、TWICE、(G)I-DLE、ITZY、NMIXX。
3. 若遇到限定团、子团、企划团，要单独标记，不与常设团混写。
4. 若用户要求“完整成员”或“现实时间线”，必须把该组合放入高优先级检索队列。

## 输入插槽

- user_named_groups
- target_generation_range
- preferred_market
- completeness_goal

## 输出要求

```json
{
  "generation_map": [
    {
      "generation": "",
      "common_examples": [],
      "coverage_priority_groups": [],
      "note": ""
    }
  ],
  "search_plan": {
    "must_cover_groups": [],
    "second_pass_groups": [],
    "project_groups_to_separate": [],
    "disputed_generation_cases": []
  }
}
```""",
        ),
        BuiltinWorkshopSeed(
            source_key="curated/irl-girlgroup-org-member-detail",
            name="现实女团资料构建 · 二到六代组织与成员细分模板",
            description="把常见女团按代际拆成更细的组织卡与成员卡生成提示，优先覆盖常见二到六代组合，并把限定团/企划团单独标记。",
            category="other",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "现实资料", "女团组织", "成员模板", "K-pop", "二代", "三代", "四代", "五代", "六代", "低风险"),
                )
            ),
            prompt_content="""# 现实女团资料构建 · 二到六代组织与成员细分模板

## 系统角色

你是一位负责把现实女团资料拆成“组织卡 + 成员卡 + 成员关系”的资料编辑，需要先扩大覆盖面，再把每个组合拆成适合小说项目使用的结构化模板。

## 使用目标

1. 当用户说“补全女团组织与成员”时，不只补组合名，还要补组织类型、成员关系、活动期和关键时间线。
2. 当用户说“按现实时间线”时，组织卡和成员卡都要优先写绝对日期或明确年份。
3. 当用户说“常见二到六代女团”时，至少先从下列示例里扩展候选，再按用户点名优先级排序。

## 常见覆盖示例

- 二代：Girls' Generation、KARA、Wonder Girls、2NE1、T-ARA、Apink、f(x)、SISTAR
- 三代：TWICE、Red Velvet、BLACKPINK、GFRIEND、MAMAMOO、OH MY GIRL、WJSN、Lovelyz、Dreamcatcher
- 四代：IZ*ONE、(G)I-DLE、ITZY、aespa、STAYC、IVE、LE SSERAFIM、NMIXX、Kep1er、fromis_9
- 五代：NewJeans、tripleS、KISS OF LIFE、BABYMONSTER、ILLIT、UNIS
- 六代：不要写成唯一标准答案；结合用户指定、公开口径和检索结果，标注“常见口径/存在争议/待核实”

## 组织卡细化要求

1. organization_type 要明确写成“现实女团 / 限定团 / 企划团 / 子团 / 公司内组合”等。
2. background 前半段必须先压缩成高密度摘要，优先包含：活动期、状态、完整成员名单、关键节点。
3. 如果是限定团或企划团，要单独说明活动区间、企划来源、活动结束节点，不要和常设团混写。
4. 如果是多公司协作、项目团、选秀团，必须在 company 或 summary 中写清楚运作背景。

## 成员卡细化要求

1. 每个成员至少拆出：艺名、常用本名、所属组合、公开定位、加入/出道、离开/毕业、公开身份摘要。
2. 如果同一成员经历多个组合、限定团或再出道，必须按现实时间线拆开写。
3. 不要把“成员定位”“舞台人设”“同人解读”混成一段，要分开表达。
4. 如果资料不足，明确写“待补充检索”，不要假设填空。

## 成员关系细化要求

1. organization_members 要尽量完整，不要只列主角或高热成员。
2. position 优先写公开定位或团内职责；没有明确定位时写“成员”。
3. status 至少区分 active / former / project_or_limited。
4. notes 用来记录公开时间线摘要，不要写未公开私生活。

## 强约束

1. 这是一份现实资料模板，不允许把代际争议写成官方定论。
2. 用户点名的组合必须优先展开，例如 IZ*ONE、TWICE、(G)I-DLE、ITZY、NMIXX。
3. 不得把未公开恋爱、站外八卦、粉圈猜测写进角色卡或成员关系。

## 输入插槽

- user_named_groups
- focus_generations
- completeness_goal
- target_mode

## 输出要求

```json
{
  "organization_templates": [
    {
      "group_name": "",
      "generation": "",
      "organization_type": "",
      "must_cover_fields": [],
      "timeline_focus": [],
      "member_bucket_rule": ""
    }
  ],
  "member_templates": [
    {
      "group_name": "",
      "member_card_fields": [],
      "relationship_fields": [],
      "special_notes": []
    }
  ],
  "coverage_plan": {
    "first_pass_groups": [],
    "second_pass_groups": [],
    "limited_or_project_groups": [],
    "generation_disputes": []
  }
}
```""",
        ),
        BuiltinWorkshopSeed(
            source_key="curated/irl-girlgroup-public-dynamics",
            name="百合向女团项目 · 公开互动氛围底座",
            description="只基于公开舞台、团综、采访和官方物料，整理可用于百合向项目的互动氛围和搭档关系底座。",
            category="romance",
            tags=tuple(
                _normalize_tags(
                    ("官方精选", "百合向", "女团", "公开互动", "舞台化学反应", "团综", "低风险"),
                )
            ),
            prompt_content="""# 百合向女团项目 · 公开互动氛围底座

## 系统角色

你是一位只处理公开舞台互动和节目物料的关系氛围整理员，负责为百合向创作项目提供安全、可核对的现实资料底座。

## 核心任务

1. 只整理公开可见的互动，例如舞台配对、团综固定搭档、采访中的互相称呼、照顾关系、默契分工和官方 unit。
2. 总结成员之间适合创作参考的互动关键词，例如“吵闹搭档”“互相照顾”“双队长张力”“室友感”“舞台化学反应”。
3. 如有明确公开来源，可以附上“来源类型”，例如舞台、团综、采访、幕后花絮、官方直播。
4. 让结果适合转成偏日常、陪伴、心动感、舞台默契感的创作提示，而不是私密关系断言。

## 强约束

1. 绝不能把真实人物写成私下恋爱既定事实，不能捏造未公开的亲密关系。
2. 不写露骨内容，不写私人性经历，不写偷拍视频或站外八卦。
3. 所有关系描述都必须基于公开物料，可用“公开氛围像”“观众常见解读”为限定语。
4. 如果缺乏公开互动证据，就写“公开材料不足”，不要强行凑 CP 设定。

## 输入插槽

- group_name
- target_members
- wanted_tone
- allowed_source_types

## 输出要求

```json
{
  "public_dynamics": [
    {
      "pair_or_group": [],
      "dynamic_keywords": [],
      "public_examples": [],
      "source_types": [],
      "safe_writing_hint": ""
    }
  ],
  "guardrails": {
    "can_use": [],
    "must_not_claim": [],
    "needs_more_search": []
  }
}
```""",
        ),
    ]


class BuiltinContentSyncService:
    """同步内置的项目级风格预设和官方提示词。"""

    async def sync(self) -> None:
        try:
            engine = await get_engine("bootstrap")
            session_factory = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            async with session_factory() as session:
                changed = await self._ensure_project_consistency_preset(session)
                changed |= await self._sync_builtin_prompt_workshop_items(session)
                if changed:
                    await session.commit()
        except Exception as exc:
            logger.warning(f"同步内置内容失败，已跳过: {exc}")

    async def _ensure_project_consistency_preset(self, session: AsyncSession) -> bool:
        result = await session.execute(
            select(WritingStyle).where(
                WritingStyle.user_id.is_(None),
                WritingStyle.preset_id == PROJECT_CONSISTENCY_PRESET_ID,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            return False

        session.add(
            WritingStyle(
                user_id=None,
                name=PROJECT_CONSISTENCY_PRESET_NAME,
                style_type="preset",
                preset_id=PROJECT_CONSISTENCY_PRESET_ID,
                description=PROJECT_CONSISTENCY_PRESET_DESCRIPTION,
                prompt_content=PROJECT_CONSISTENCY_PRESET_PROMPT,
                order_index=90,
            )
        )
        logger.info(f"已补齐内置写作风格预设: {PROJECT_CONSISTENCY_PRESET_NAME}")
        return True

    async def _sync_builtin_prompt_workshop_items(self, session: AsyncSession) -> bool:
        seeds = [
            *self._load_local_prompt_seeds(),
            *_build_custom_prompt_seeds(),
        ]
        if not seeds:
            return False

        seed_ids = [_stable_workshop_item_id(seed.source_key) for seed in seeds]
        result = await session.execute(
            select(PromptWorkshopItem).where(PromptWorkshopItem.id.in_(seed_ids))
        )
        existing_items = {item.id: item for item in result.scalars().all()}

        added_count = 0
        updated_count = 0

        for seed in seeds:
            item_id = _stable_workshop_item_id(seed.source_key)
            existing = existing_items.get(item_id)
            tags = list(seed.tags)

            if existing is None:
                session.add(
                    PromptWorkshopItem(
                        id=item_id,
                        name=seed.name,
                        description=seed.description,
                        prompt_content=seed.prompt_content,
                        category=seed.category,
                        tags=tags,
                        author_name="官方",
                        source_instance=BUILTIN_PROMPT_SOURCE,
                        is_official=True,
                        status="active",
                    )
                )
                added_count += 1
                continue

            changed = False
            for field_name, value in (
                ("name", seed.name),
                ("description", seed.description),
                ("prompt_content", seed.prompt_content),
                ("category", seed.category),
                ("tags", tags),
            ):
                if getattr(existing, field_name) != value:
                    setattr(existing, field_name, value)
                    changed = True

            if existing.author_name != "官方":
                existing.author_name = "官方"
                changed = True
            if existing.source_instance != BUILTIN_PROMPT_SOURCE:
                existing.source_instance = BUILTIN_PROMPT_SOURCE
                changed = True
            if not existing.is_official:
                existing.is_official = True
                changed = True
            if existing.status != "active":
                existing.status = "active"
                changed = True

            if changed:
                updated_count += 1

        if added_count or updated_count:
            logger.info(
                "已同步官方提示词工坊条目: 新增 %s 条，更新 %s 条",
                added_count,
                updated_count,
            )
            return True

        return False

    def _load_local_prompt_seeds(self) -> list[BuiltinWorkshopSeed]:
        seeds: list[BuiltinWorkshopSeed] = []

        for filename in SAFE_PROMT_FILENAMES:
            file_path = PROMT_DIR / filename
            if not file_path.exists():
                logger.warning(f"本地提示词文件不存在，已跳过: {filename}")
                continue

            content = file_path.read_text(encoding="utf-8").strip()
            if not content:
                logger.warning(f"本地提示词文件为空，已跳过: {filename}")
                continue

            if not _is_safe_local_prompt(filename, content):
                logger.info(f"检测到高风险提示词，未同步进官方工坊: {filename}")
                continue

            seeds.append(
                BuiltinWorkshopSeed(
                    source_key=f"promt/{filename}",
                    name=_display_name_from_filename(filename),
                    description=_extract_description(content),
                    prompt_content=content,
                    category=_infer_category(filename, content),
                    tags=tuple(_build_local_tags(filename, content)),
                )
            )

        return seeds


builtin_content_sync_service = BuiltinContentSyncService()
