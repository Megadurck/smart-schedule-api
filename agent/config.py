import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Agent configuration
AGENT_PROVIDER = os.getenv("AGENT_PROVIDER", "ollama").strip().lower()
AGENT_COMPANY_NAME = os.getenv("AGENT_COMPANY_NAME", "default-company").strip()

# Ollama configuration
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434").strip()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "dolphin-mixtral").strip()
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))

# OpenAI configuration (legacy)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if AGENT_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY nao encontrada. Defina a chave ou use AGENT_PROVIDER=ollama."
    )

if AGENT_PROVIDER not in ["ollama", "openai", "offline"]:
    raise ValueError(
        f"AGENT_PROVIDER deve ser 'ollama', 'openai' ou 'offline', recebido: {AGENT_PROVIDER}"
    )
