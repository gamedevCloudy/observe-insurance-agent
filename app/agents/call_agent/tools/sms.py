from langchain_core.tools import tool


@tool
def send_sms(sms_type: str) -> dict:
    """Send an SMS to the customer. sms_type: 'claim-docs' sends instructions for submitting claim documentation."""
    valid = {"claim-docs"}
    if sms_type not in valid:
        return {"error": f"Invalid sms_type '{sms_type}'. Must be one of: {', '.join(sorted(valid))}"}
    return {
        "status": "simulated",
        "sms_type": sms_type,
        "message": "SMS sent: Please submit your claim documentation via email to claims@observeinsurance.com or upload at observeinsurance.com/claims/upload.",
    }
