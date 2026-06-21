from langchain_core.tools import tool


@tool
def escalate(reason: str) -> dict:
    """Escalate the call to a human representative. reason: one of 'ask-human-support', 'out-of-knowledge', 'emergency'."""
    valid = {"ask-human-support", "out-of-knowledge", "emergency"}
    if reason not in valid:
        return {"error": f"Invalid reason '{reason}'. Must be one of: {', '.join(sorted(valid))}"}
    return {"status": "escalated", "reason": reason, "message": "I'm transferring you to a representative now. Please hold."}
