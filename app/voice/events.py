import json
from dataclasses import asdict, dataclass
from typing import Literal


@dataclass
class VoiceEvent:
    type: str

    def to_json(self) -> str:
        payload = asdict(self)
        payload.pop("type")
        return json.dumps({"type": self.type, **payload})


@dataclass
class TranscriptEvent(VoiceEvent):
    type: Literal["transcript"] = "transcript"
    text: str = ""


@dataclass
class PartialEvent(VoiceEvent):
    type: Literal["partial"] = "partial"
    text: str = ""


@dataclass
class StartOfTurnEvent(VoiceEvent):
    type: Literal["start_of_turn"] = "start_of_turn"


@dataclass
class TokenEvent(VoiceEvent):
    type: Literal["token"] = "token"
    content: str = ""


@dataclass
class ThinkingEvent(VoiceEvent):
    type: Literal["thinking"] = "thinking"
    name: str = ""


@dataclass
class AudioEvent(VoiceEvent):
    type: Literal["audio"] = "audio"
    n_bytes: int = 0


@dataclass
class ClosedEvent(VoiceEvent):
    type: Literal["closed"] = "closed"
    reason: str = ""


@dataclass
class ErrorEvent(VoiceEvent):
    type: Literal["error"] = "error"
    detail: str = ""


@dataclass
class DoneEvent(VoiceEvent):
    type: Literal["done"] = "done"
