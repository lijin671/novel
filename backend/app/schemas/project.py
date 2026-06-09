"""项目相关的 Pydantic 模型"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectRealitySyncConfig(BaseModel):
    """项目级现实资料同步配置"""

    mode: Literal["auto", "force", "off"] = Field(
        default="auto",
        description="现实资料同步模式：auto=自动识别，force=强制同步，off=关闭",
    )
    preferred_groups: list[str] = Field(
        default_factory=list,
        description="优先同步的现实女团组合列表",
    )
    max_groups_per_run: int = Field(
        default=6,
        ge=1,
        le=12,
        description="单次续写前最多同步多少个组合",
    )


class ProjectBase(BaseModel):
    """项目基础模型"""

    title: str = Field(..., description="项目标题")
    description: Optional[str] = Field(None, description="项目描述")
    theme: Optional[str] = Field(None, description="主题")
    genre: Optional[str] = Field(None, description="小说类型")
    target_words: Optional[int] = Field(None, description="目标字数")
    outline_mode: Literal["one-to-one", "one-to-many"] = Field(
        default="one-to-many",
        description="大纲章节模式: one-to-one / one-to-many",
    )
    reality_sync_config: Optional[ProjectRealitySyncConfig] = Field(
        default=None,
        description="项目级现实资料同步配置",
    )


class ProjectCreate(ProjectBase):
    """创建项目请求"""


class ProjectUpdate(BaseModel):
    """更新项目请求"""

    title: Optional[str] = None
    description: Optional[str] = None
    theme: Optional[str] = None
    genre: Optional[str] = None
    target_words: Optional[int] = None
    status: Optional[str] = None
    world_time_period: Optional[str] = None
    world_location: Optional[str] = None
    world_atmosphere: Optional[str] = None
    world_rules: Optional[str] = None
    chapter_count: Optional[int] = None
    narrative_perspective: Optional[str] = None
    character_count: Optional[int] = None
    reality_sync_config: Optional[ProjectRealitySyncConfig] = None


class ProjectResponse(ProjectBase):
    """项目响应模型"""

    id: str
    status: str
    current_words: int
    wizard_status: Optional[str] = None
    wizard_step: Optional[int] = None
    world_time_period: Optional[str] = None
    world_location: Optional[str] = None
    world_atmosphere: Optional[str] = None
    world_rules: Optional[str] = None
    chapter_count: Optional[int] = None
    narrative_perspective: Optional[str] = None
    character_count: Optional[int] = None
    outline_mode: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """项目列表响应模型"""

    total: int
    items: list[ProjectResponse]


class ProjectWizardRequest(BaseModel):
    """项目创建向导请求模型"""

    title: str = Field(..., description="书名")
    theme: str = Field(..., description="主题")
    genre: Optional[str] = Field(None, description="类型")
    chapter_count: int = Field(..., ge=1, description="章节数量")
    narrative_perspective: str = Field(..., description="叙事视角")
    character_count: int = Field(5, ge=5, description="角色数量（至少5个）")
    target_words: Optional[int] = Field(None, description="目标字数")
    outline_mode: Literal["one-to-one", "one-to-many"] = Field(
        default="one-to-many",
        description="大纲章节模式",
    )


class WorldBuildingResponse(BaseModel):
    """世界构建响应模型"""

    time_period: str = Field(..., description="时间背景")
    location: str = Field(..., description="地理位置")
    atmosphere: str = Field(..., description="氛围基调")
    rules: str = Field(..., description="世界规则")
