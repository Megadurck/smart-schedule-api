import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

AGENT_PROVIDER = os.getenv("AGENT_PROVIDER", "offline").strip().lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if AGENT_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY nao encontrada. Defina a chave ou use AGENT_PROVIDER=offline."
    )
