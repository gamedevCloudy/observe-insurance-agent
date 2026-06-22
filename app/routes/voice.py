import asyncio
import contextlib
import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from app.agents.graph import build_agent
from app.core.logging import bind_session, clear_session, get_logger
from app.voice.deepgram import StreamingSTT
from app.voice.events import PartialEvent, StartOfTurnEvent, VoiceEvent
from app.voice.pipeline import agent_turn

log = get_logger("observeai.voice")

router = APIRouter(prefix="/voice", tags=["voice"])

_agent = build_agent()
_STATIC = Path(__file__).resolve().parent.parent.parent / "static" / "voice.html"


@router.get("/")
async def voice_page():
    return FileResponse(_STATIC)


async def _send_item(item, ws: WebSocket) -> None:
    if isinstance(item, (bytes, bytearray)) and item:
        await ws.send_bytes(bytes(item))
    elif isinstance(item, VoiceEvent):
        await ws.send_text(item.to_json())


@router.websocket("/ws")
async def voice_ws(websocket: WebSocket):
    await websocket.accept()
    thread_id = str(uuid4())
    bind_session(thread_id, thread_id)
    client = websocket.client.host if websocket.client else None
    log.info("session.start", client=client)
    current: asyncio.Task | None = None

    stt = StreamingSTT()
    try:
        await stt.connect()
    except Exception as exc:
        log.error("stt.connect.failed", error=str(exc))
        await websocket.close()
        clear_session()
        return
    log.info("stt.connect")

    async def cancel_current():
        nonlocal current
        if current and not current.done():
            current.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await current
        current = None

    async def run_agent(transcript: str):
        nonlocal current
        await cancel_current()
        current = asyncio.create_task(_drain_agent(transcript))

    async def _drain_agent(transcript: str):
        async for item in agent_turn(transcript, thread_id, _agent):
            await _send_item(item, ws=websocket)

    async def drain_stt():
        async for evt in stt.events():
            if evt.kind == "start_of_turn":
                await websocket.send_text(StartOfTurnEvent().to_json())
                await cancel_current()
            elif evt.kind == "partial":
                await websocket.send_text(PartialEvent(text=evt.transcript).to_json())
            elif evt.kind == "final":
                if evt.transcript.strip():
                    log.info("stt.transcript", transcript=evt.transcript[:80])
                    await run_agent(evt.transcript)

    stt_task = asyncio.create_task(drain_stt())

    reason = "client-disconnect"
    try:
        while True:
            msg = await websocket.receive()
            if msg["type"] == "websocket.disconnect":
                break
            data = msg.get("bytes")
            text = msg.get("text")
            if data:
                await stt.send_media(data)
            elif text:
                try:
                    ctrl = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if ctrl.get("type") == "stop":
                    await cancel_current()
                elif ctrl.get("type") == "text" and ctrl.get("content", "").strip():
                    log.info("text.input", text=ctrl["content"][:80])
                    await websocket.send_text(StartOfTurnEvent().to_json())
                    await run_agent(ctrl["content"].strip())
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        reason = "error"
        log.error("session.error", error=str(exc))
        raise
    finally:
        stt_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await stt_task
        await cancel_current()
        await stt.close()
        log.info("session.end", reason=reason)
        clear_session()
