def detect_intent(message):
    msg = message.lower()

    if "wedding" in msg:
        return "wedding"
    elif "party" in msg:
        return "party"
    elif "casual" in msg:
        return "casual"
    elif any(color in msg for color in ["red", "blue", "green", "black", "white"]):
        return "color"
    else:
        return "unknown"