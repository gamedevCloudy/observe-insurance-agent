import re

_EMOJI_RE = re.compile(
    "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0\U000024C2-\U0001F251]+",
    flags=re.UNICODE,
)
_MD_RE = re.compile(r"([*_`#>\[\]()~]|\\[*_`#>\[\]()~])")
_WS_RE = re.compile(r"\s+")


def for_tts(text: str) -> str:
    """Strip markdown/emojis/special chars that a TTS engine would read literally."""
    if not text:
        return ""
    out = _EMOJI_RE.sub("", text)
    out = _MD_RE.sub("", out)
    out = _WS_RE.sub(" ", out).strip()
    return out
