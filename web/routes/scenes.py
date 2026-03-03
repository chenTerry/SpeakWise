"""
Scenes Routes - 场景 API 路由

提供场景相关的 RESTful API。
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/scenes", tags=["scenes"])


# ============== Models ==============

class SceneInfo(BaseModel):
    """场景信息"""
    id: str
    name: str
    description: str
    difficulty: int = Field(ge=1, le=5)
    domain: str
    style: str
    estimated_duration: int = 30  # minutes
    tags: List[str] = Field(default_factory=list)


class SceneConfig(BaseModel):
    """场景配置"""
    scene_id: str
    style: Optional[str] = None
    difficulty: Optional[int] = None
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class SceneListResponse(BaseModel):
    """场景列表响应"""
    scenes: List[SceneInfo]
    total: int


class SceneDetailResponse(BaseModel):
    """场景详情响应"""
    scene: SceneInfo
    config: Optional[SceneConfig] = None


# ============== Mock Data ==============

SCENES_DB: List[SceneInfo] = [
    SceneInfo(
        id="tech_frontend",
        name="技术面试 - 前端开发",
        description="模拟前端工程师技术面试，涵盖 HTML/CSS/JavaScript/框架等知识点",
        difficulty=3,
        domain="frontend",
        style="friendly",
        estimated_duration=30,
        tags=["前端", "JavaScript", "React", "Vue"],
    ),
    SceneInfo(
        id="tech_backend",
        name="技术面试 - 后端开发",
        description="模拟后端工程师技术面试，涵盖系统设计、数据库、API 开发等",
        difficulty=4,
        domain="backend",
        style="strict",
        estimated_duration=45,
        tags=["后端", "Python", "数据库", "系统设计"],
    ),
    SceneInfo(
        id="tech_system_design",
        name="技术面试 - 系统设计",
        description="模拟系统架构师面试，考察大规模系统设计能力",
        difficulty=5,
        domain="system_design",
        style="pressure",
        estimated_duration=60,
        tags=["系统设计", "架构", "分布式"],
    ),
    SceneInfo(
        id="hr_interview",
        name="HR 面试",
        description="模拟人力资源面试，考察软技能和企业文化匹配度",
        difficulty=2,
        domain="hr",
        style="friendly",
        estimated_duration=20,
        tags=["HR", "软技能", "文化匹配"],
    ),
    SceneInfo(
        id="general_interview",
        name="综合面试",
        description="综合技术能力和软技能的全面面试",
        difficulty=3,
        domain="general",
        style="friendly",
        estimated_duration=40,
        tags=["综合", "技术", "软技能"],
    ),
    SceneInfo(
        id="behavioral",
        name="行为面试",
        description="基于行为的面谈，了解过往经历和行为模式",
        difficulty=2,
        domain="behavioral",
        style="friendly",
        estimated_duration=30,
        tags=["行为", "经历", "STAR"],
    ),
]


# ============== Routes ==============

@router.get("", response_model=SceneListResponse)
async def list_scenes(
    domain: Optional[str] = Query(None, description="按领域筛选"),
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="按难度筛选"),
    style: Optional[str] = Query(None, description="按风格筛选"),
    tag: Optional[str] = Query(None, description="按标签筛选"),
) -> SceneListResponse:
    """
    获取场景列表

    支持按领域、难度、风格和标签筛选。
    """
    scenes = SCENES_DB.copy()

    # 筛选
    if domain:
        scenes = [s for s in scenes if s.domain == domain]
    if difficulty:
        scenes = [s for s in scenes if s.difficulty == difficulty]
    if style:
        scenes = [s for s in scenes if s.style == style]
    if tag:
        scenes = [s for s in scenes if tag in s.tags]

    return SceneListResponse(scenes=scenes, total=len(scenes))


@router.get("/domains")
async def list_domains() -> Dict[str, List[str]]:
    """获取所有可用领域"""
    domains = list(set(s.domain for s in SCENES_DB))
    return {"domains": domains}


@router.get("/styles")
async def list_styles() -> Dict[str, List[str]]:
    """获取所有可用风格"""
    styles = list(set(s.style for s in SCENES_DB))
    return {"styles": styles}


@router.get("/{scene_id}", response_model=SceneDetailResponse)
async def get_scene(scene_id: str) -> SceneDetailResponse:
    """获取场景详情"""
    for scene in SCENES_DB:
        if scene.id == scene_id:
            return SceneDetailResponse(scene=scene)

    raise HTTPException(status_code=404, detail=f"场景 {scene_id} 不存在")


@router.post("/{scene_id}/start")
async def start_scene(
    scene_id: str,
    config: Optional[SceneConfig] = None,
) -> Dict[str, Any]:
    """
    开始场景

    初始化场景并返回开场白。
    """
    # 验证场景存在
    scene = None
    for s in SCENES_DB:
        if s.id == scene_id:
            scene = s
            break

    if not scene:
        raise HTTPException(status_code=404, detail=f"场景 {scene_id} 不存在")

    # 生成开场白
    opening_messages = {
        "tech_frontend": "你好！欢迎参加前端开发技术面试。我是今天的面试官。"
                        "首先，能简单介绍一下你自己和你最熟悉的前端技术栈吗？",
        "tech_backend": "你好！欢迎参加后端开发技术面试。"
                       "让我们开始吧，请先谈谈你对后端开发的理解和你常用的技术栈。",
        "tech_system_design": "你好！今天是系统设计面试。"
                             "我会给你一个设计问题，希望你能展示你的架构思维。"
                             "准备好了吗？",
        "hr_interview": "你好！很高兴见到你。我是 HR 部门的面试官。"
                       "今天主要是想了解一下你的职业规划和个人特点。"
                       "先请做个自我介绍吧。",
        "general_interview": "你好！欢迎参加今天的综合面试。"
                            "我们会从技术和软技能两个方面进行交流。"
                            "放松一点，先介绍一下自己吧。",
        "behavioral": "你好！今天是行为面试，我会问你一些关于过往经历的问题。"
                     "请用 STAR 方法（情境、任务、行动、结果）来回答。"
                     "让我们开始吧。",
    }

    opening = opening_messages.get(
        scene_id,
        f"你好！欢迎参加{scene.name}。让我们开始吧！"
    )

    return {
        "success": True,
        "scene_id": scene_id,
        "scene_name": scene.name,
        "opening": opening,
        "estimated_duration": scene.estimated_duration,
    }


@router.get("/config/{scene_id}")
async def get_scene_config(scene_id: str) -> Dict[str, Any]:
    """获取场景配置选项"""
    scene = None
    for s in SCENES_DB:
        if s.id == scene_id:
            scene = s
            break

    if not scene:
        raise HTTPException(status_code=404, detail=f"场景 {scene_id} 不存在")

    return {
        "scene_id": scene_id,
        "available_styles": ["friendly", "strict", "pressure"],
        "available_difficulties": list(range(1, 6)),
        "default_style": scene.style,
        "default_difficulty": scene.difficulty,
    }
