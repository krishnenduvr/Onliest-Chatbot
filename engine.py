import json
from urllib import error, request

try:
    from chatbot.config import OLLAMA_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL
    from chatbot.intents import detect_intent
    from chatbot.memory import get_context, update_context
except ModuleNotFoundError:
    from config import OLLAMA_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL
    from intents import detect_intent
    from memory import get_context, update_context


def build_messages(message, context):
    system_prompt = (
        "You are a helpful chatbot. Answer the user's question directly and clearly. "
        "Use saved context when it is relevant."
    )
    messages = [{"role": "system", "content": system_prompt}]

    if context:
        messages.append(
            {
                "role": "system",
                "content": f"Saved user context: {context}",
            }
        )

    messages.append({"role": "user", "content": message})
    return messages


def fallback_response():
    return (
        "I could not get a response from Ollama right now. "
        "Please make sure Ollama is running locally or that your cloud API settings are correct."
    )


def format_api_error(exc):
    message = str(exc)

    if "Connection refused" in message or "WinError 10061" in message:
        return (
            "Ollama connection error: if you are using local Ollama, start it first. "
            "If you are using an Ollama API key, set OLLAMA_BASE_URL=https://ollama.com "
            "and add OLLAMA_API_KEY in chatbot/.env."
        )

    if "404" in message:
        return (
            f"Ollama model error: '{OLLAMA_MODEL}' was not found. "
            f"Run 'ollama pull {OLLAMA_MODEL}' and try again."
        )

    if "401" in message or "403" in message:
        return "Ollama authentication error: check your OLLAMA_API_KEY."

    return f"Ollama error: {message}"


def llm_response(message, context):
    messages = build_messages(message, context)

    try:
        payload = json.dumps(
            {
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if OLLAMA_API_KEY:
            headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
        req = request.Request(
            f"{OLLAMA_BASE_URL}/api/chat",
            data=payload,
            headers=headers,
            method="POST",
        )
        with request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("message", {}).get("content", "").strip() or fallback_response()
    except error.HTTPError as exc:
        return format_api_error(exc)
    except error.URLError as exc:
        return format_api_error(exc)
    except Exception as exc:
        return format_api_error(exc)


def get_response(user_id, message):
    context = get_context(user_id)
    intent = detect_intent(message)

    if intent != "unknown":
        update_context(user_id, "last_intent", intent)

    if intent == "color":
        update_context(user_id, "color", message)

    if intent in {"wedding", "party", "casual"}:
        update_context(user_id, "event", intent)

    return llm_response(message, get_context(user_id))
