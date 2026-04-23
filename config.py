import os
from pathlib import Path

from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
ENV_PATHS = [
    CURRENT_DIR / ".env",
    CURRENT_DIR / "chatbot" / ".env",
]

for env_path in ENV_PATHS:
    if env_path.exists():
        load_dotenv(env_path, override=False)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
