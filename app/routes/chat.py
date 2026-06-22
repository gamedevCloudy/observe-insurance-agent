import json
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage

from app.agents.graph import build_agent
from app.schemas import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])

_agent = build_agent()


def _is_emergency_escalation_closed(state) -> bool:
    for msg in state.get("messages", []):
        if isinstance(msg, ToolMessage) and msg.name == "escalate":
            try:
                content = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                if content.get("chat_closed"):
                    return True
            except (json.JSONDecodeError, TypeError):
                pass
    return False


async def _stream_events(body: ChatRequest):
    thread_id = body.thread_id or str(uuid4())
    yield f"event: thread\ndata: {json.dumps({'thread_id': thread_id})}\n\n"

    config = {"configurable": {"thread_id": thread_id}}

    state = await _agent.aget_state(config)
    if _is_emergency_escalation_closed(state.values):
        yield f"event: closed\ndata: {json.dumps({'reason': 'emergency-escalation'})}\n\n"
        return

    emergency_escalated = False

    try:
        async for chunk, _metadata in _agent.astream(
            {"messages": [HumanMessage(content=body.message)]},
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield f"event: token\ndata: {json.dumps({'content': chunk.content})}\n\n"
            elif isinstance(chunk, ToolMessage) and chunk.name == "escalate":
                try:
                    content = json.loads(chunk.content) if isinstance(chunk.content, str) else chunk.content
                    if content.get("chat_closed"):
                        emergency_escalated = True
                except (json.JSONDecodeError, TypeError):
                    pass
    except Exception as exc:
        yield f"event: error\ndata: {json.dumps({'detail': str(exc)})}\n\n"
        return

    if emergency_escalated:
        yield f"event: closed\ndata: {json.dumps({'reason': 'emergency-escalation'})}\n\n"
    else:
        yield "event: done\ndata: {}\n\n"


@router.post("/")
async def chat(body: ChatRequest):
    return StreamingResponse(
        _stream_events(body),
        media_type="text/event-stream",
    )
