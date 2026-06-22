from app.voice.sanitize import for_tts


def test_strips_markdown():
    assert for_tts("Your **claim** is *under review*.") == "Your claim is under review."


def test_strips_emojis():
    assert for_tts("Approved! 🎉 ✅") == "Approved!"


def test_preserves_numbers_and_ids():
    assert for_tts("Claim ID: 12345, Policy: POL-001.") == "Claim ID: 12345, Policy: POL-001."


def test_empty_string():
    assert for_tts("") == ""
