import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Agent configuration
AGENT_PROVIDER = os.getenv("AGENT_PROVIDER", "ollama").strip().lower()
AGENT_COMPANY_NAME = os.getenv("AGENT_COMPANY_NAME", "default-company").strip()

# Smart Schedule API (o agent consome a API via HTTP em vez de acessar o banco direto)
AGENT_API_BASE_URL = os.getenv("AGENT_API_BASE_URL", "http://localhost:8000/api/v1").strip()
AGENT_API_USER = os.getenv("AGENT_API_USER", "agent-bot").strip()
AGENT_API_PASSWORD = os.getenv("AGENT_API_PASSWORD", "").strip()

# Ollama configuration
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434").strip()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "dolphin-mixtral").strip()
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))

# WhatsApp - Meta Cloud API (webhook de teste)
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "").strip()
META_WHATSAPP_TOKEN = os.getenv("META_WHATSAPP_TOKEN", "").strip()
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "").strip()
META_APP_SECRET = os.getenv("META_APP_SECRET", "").strip()
META_API_VERSION = os.getenv("META_API_VERSION", "v20.0").strip()

if AGENT_PROVIDER not in ["ollama", "offline"]:
    raise ValueError(
        f"AGENT_PROVIDER deve ser 'ollama' ou 'offline', recebido: {AGENT_PROVIDER}"
    )

if not AGENT_API_PASSWORD:
    raise ValueError(
        "AGENT_API_PASSWORD nao definida. Configure uma senha para o usuario do agent na API."
    )
