try:
    from chatbot.engine import get_response
except ModuleNotFoundError:
    from chatbot.engine import get_response

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ModuleNotFoundError:
    FastAPI = None
    BaseModel = object

app = FastAPI() if FastAPI is not None else None

if FastAPI is not None:
    class ChatRequest(BaseModel):
        user_id: str
        message: str

    @app.get("/")
    def home():
        return {"message": "Chatbot running"}

    @app.post("/chat")
    def chat(req: ChatRequest):
        reply = get_response(req.user_id, req.message)
        return {"response": reply}


def run_cli_chat():
    user_id = "default_user"
    print("Ollama Chatbot is ready. Type 'exit' to quit.")

    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAssistant: Goodbye!")
            break

        if not message:
            continue
        if message.lower() in {"exit", "quit"}:
            print("Assistant: Goodbye!")
            break

        try:
            reply = get_response(user_id, message)
            print(f"Assistant: {reply}")
        except Exception as exc:
            print(f"Assistant: Unexpected error: {exc}")


if __name__ == "__main__":
    run_cli_chat()
