"""
Dialogue Routes - 对话 API 路由

提供对话相关的 RESTful API 和 WebSocket 支持。
"""

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/dialogue", tags=["dialogue"])


# ============== Models ==============

class Message(BaseModel):
    """对话消息"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # user, interviewer, system
    content: str
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DialogueSession(BaseModel):
    """对话会话"""
    id: str
    scene_id: str
    scene_name: str
    messages: List[Message] = Field(default_factory=list)
    status: str = "active"  # active, paused, completed
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    success: bool
    message: Message
    response: Optional[Message] = None
    session: DialogueSession


class DialogueHistoryResponse(BaseModel):
    """对话历史响应"""
    session: DialogueSession
    message_count: int


# ============== In-Memory Storage ==============

# 实际应用中应该使用数据库
SESSIONS_DB: Dict[str, DialogueSession] = {}


# ============== Helper Functions ==============

def get_session(session_id: str) -> Optional[DialogueSession]:
    """获取会话"""
    return SESSIONS_DB.get(session_id)


def create_session(scene_id: str, scene_name: str) -> DialogueSession:
    """创建新会话"""
    session = DialogueSession(
        id=str(uuid.uuid4()),
        scene_id=scene_id,
        scene_name=scene_name,
    )
    SESSIONS_DB[session.id] = session
    return session


def generate_ai_response(user_message: str, scene_id: str) -> str:
    """
    生成 AI 响应

    这里应该调用真实的 AI 模型，暂时使用预设响应。
    """
    # 简单的关键词匹配响应
    user_input_lower = user_message.lower()

    # 根据场景定制响应
    if scene_id == "tech_frontend":
        if "介绍" in user_input_lower or "自我" in user_input_lower:
            return "很好！那么请谈谈你最熟悉的前端框架，比如 React 或 Vue，" \
                   "以及你在项目中是如何使用的。"
        elif "框架" in user_input_lower or "react" in user_input_lower or "vue" in user_input_lower:
            return "不错。那么你能解释一下虚拟 DOM 的概念吗？" \
                   "它为什么能提高性能？"
        elif "dom" in user_input_lower or "性能" in user_input_lower:
            return "很好。在实际项目中，你是如何优化前端性能的？" \
                   "有哪些具体的实践？"
        else:
            return "明白了。能详细说说你的实现思路吗？"

    elif scene_id == "tech_backend":
        if "介绍" in user_input_lower or "自我" in user_input_lower:
            return "好的。请谈谈你常用的后端技术栈，" \
                   "以及你在数据库设计方面的经验。"
        elif "数据库" in user_input_lower or "设计" in user_input_lower:
            return "很好。那么请谈谈数据库索引的原理，" \
                   "以及在什么情况下索引会失效。"
        elif "索引" in user_input_lower:
            return "不错。现在考虑一个场景：如何设计一个支持高并发的 API？" \
                   "你会考虑哪些方面？"
        else:
            return "理解了。能具体说说你的技术方案吗？"

    elif scene_id == "hr_interview":
        if "介绍" in user_input_lower or "自我" in user_input_lower:
            return "很好。那么请谈谈你的职业规划，" \
                   "以及你为什么想加入我们公司。"
        elif "规划" in user_input_lower or "公司" in user_input_lower:
            return "不错。你能分享一个你在团队中遇到冲突并成功解决的经历吗？"
        elif "冲突" in user_input_lower or "团队" in user_input_lower:
            return "很好。最后，你觉得自己最大的优点和缺点是什么？"
        else:
            return "明白了。能再多说一些具体的例子吗？"

    else:
        # 通用响应
        if "你好" in user_input_lower or "hello" in user_input_lower:
            return "你好！很高兴见到你。能先简单介绍一下你自己吗？"
        elif "介绍" in user_input_lower:
            return "很好！那么请谈谈你最近参与的一个项目，" \
                   "以及你在其中扮演的角色。"
        elif "项目" in user_input_lower or "经验" in user_input_lower:
            return "听起来是个有趣的项目。" \
                   "在这个过程中，你遇到的最大挑战是什么？你是如何解决的？"
        elif "挑战" in user_input_lower or "困难" in user_input_lower:
            return "面对困难时的解决能力很重要。" \
                   "那么，你对这个职位有什么期待？"
        else:
            return "明白了。能详细说说你的想法吗？"


# ============== Routes ==============

@router.post("/sessions", response_model=DialogueSession)
async def create_dialogue_session(
    scene_id: str,
    scene_name: str,
) -> DialogueSession:
    """创建新的对话会话"""
    session = create_session(scene_id, scene_name)
    return session


@router.get("/sessions/{session_id}", response_model=DialogueSession)
async def get_dialogue_session(session_id: str) -> DialogueSession:
    """获取对话会话"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session


@router.get("/sessions/{session_id}/history", response_model=DialogueHistoryResponse)
async def get_dialogue_history(session_id: str) -> DialogueHistoryResponse:
    """获取对话历史"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return DialogueHistoryResponse(
        session=session,
        message_count=len(session.messages),
    )


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
) -> SendMessageResponse:
    """发送消息并获取响应"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    if session.status != "active":
        raise HTTPException(status_code=400, detail="会话已结束")

    # 创建用户消息
    user_message = Message(
        role="user",
        content=request.content,
        metadata=request.metadata,
    )
    session.messages.append(user_message)

    # 生成 AI 响应
    ai_content = generate_ai_response(request.content, session.scene_id)
    ai_message = Message(
        role="interviewer",
        content=ai_content,
    )
    session.messages.append(ai_message)

    # 更新会话
    session.updated_at = time.time()

    return SendMessageResponse(
        success=True,
        message=user_message,
        response=ai_message,
        session=session,
    )


@router.post("/sessions/{session_id}/complete")
async def complete_session(session_id: str) -> Dict[str, Any]:
    """完成对话会话"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session.status = "completed"
    session.updated_at = time.time()

    return {
        "success": True,
        "session_id": session_id,
        "message_count": len(session.messages),
        "duration": session.updated_at - session.created_at,
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, Any]:
    """删除对话会话"""
    if session_id not in SESSIONS_DB:
        raise HTTPException(status_code=404, detail="会话不存在")

    del SESSIONS_DB[session_id]

    return {"success": True, "message": "会话已删除"}


@router.get("/sessions")
async def list_sessions() -> Dict[str, Any]:
    """列出所有会话"""
    sessions = []
    for session in SESSIONS_DB.values():
        sessions.append({
            "id": session.id,
            "scene_name": session.scene_name,
            "status": session.status,
            "message_count": len(session.messages),
            "created_at": datetime.fromtimestamp(session.created_at).isoformat(),
        })

    return {"sessions": sessions, "total": len(sessions)}


# ============== WebSocket Support ==============

@router.websocket("/ws/{session_id}")
async def websocket_dialogue(websocket: WebSocket, session_id: str):
    """
    WebSocket 对话连接

    支持实时双向通信。
    """
    await websocket.accept()

    session = get_session(session_id)
    if not session:
        await websocket.send_json({"error": "会话不存在"})
        await websocket.close()
        return

    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            content = data.get("content", "")

            if not content:
                continue

            # 创建用户消息
            user_message = Message(
                role="user",
                content=content,
            )
            session.messages.append(user_message)

            # 发送确认
            await websocket.send_json({
                "type": "message_received",
                "message": {
                    "id": user_message.id,
                    "role": user_message.role,
                    "content": user_message.content,
                    "timestamp": user_message.timestamp,
                },
            })

            # 模拟打字延迟
            await websocket.send_json({"type": "typing_start"})
            await websocket.receive()  # 等待一小段时间

            # 生成 AI 响应
            ai_content = generate_ai_response(content, session.scene_id)
            ai_message = Message(
                role="interviewer",
                content=ai_content,
            )
            session.messages.append(ai_message)
            session.updated_at = time.time()

            # 发送 AI 响应
            await websocket.send_json({
                "type": "typing_end",
            })
            await websocket.send_json({
                "type": "message",
                "message": {
                    "id": ai_message.id,
                    "role": ai_message.role,
                    "content": ai_message.content,
                    "timestamp": ai_message.timestamp,
                },
            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
