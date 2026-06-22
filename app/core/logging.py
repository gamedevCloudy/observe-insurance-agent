import logging
import uuid
from contextvars import ContextVar

import structlog

session_id_var: ContextVar[str | None] = ContextVar("session_id", default=None)
thread_id_var: ContextVar[str | None] = ContextVar("thread_id", default=None)
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

_NOISY = ("httpx", "httpcore", "openai", "urllib3")


def _add_contextvars(_logger, _method_name, event_dict):
    for name, var in (
        ("session_id", session_id_var),
        ("thread_id", thread_id_var),
        ("request_id", request_id_var),
    ):
        val = var.get()
        if val is not None:
            event_dict.setdefault(name, val)
    return event_dict


def get_logger(name: str):
    return structlog.get_logger(name)


def bind_session(session_id: str, thread_id: str) -> None:
    session_id_var.set(session_id)
    thread_id_var.set(thread_id)


def clear_session() -> None:
    session_id_var.set(None)
    thread_id_var.set(None)


def configure_logging(level: str = "INFO") -> None:
    processors = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level)),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _add_contextvars,
        ],
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers[:] = []
        lg.propagate = True

    for name in _NOISY:
        logging.getLogger(name).setLevel(logging.WARNING)


class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers") or [])
        rid = (headers.get(b"x-request-id") or b"").decode() or uuid.uuid4().hex[:8]
        token = request_id_var.set(rid)

        async def send_with_header(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"].append((b"x-request-id", rid.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
        finally:
            request_id_var.reset(token)