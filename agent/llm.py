"""
LLM integration for Ollama-based agent
"""
import json
import logging
from typing import Optional

import httpx

from agent.config import OLLAMA_ENDPOINT, OLLAMA_MODEL, OLLAMA_TEMPERATURE

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(
        self,
        endpoint: str = OLLAMA_ENDPOINT,
        model: str = OLLAMA_MODEL,
        temperature: float = OLLAMA_TEMPERATURE,
    ):
        self.endpoint = endpoint
        self.model = model
        self.temperature = temperature
        self.client = httpx.Client(timeout=300.0)  # 5 minutos para carregamento do modelo

    def generate(self, prompt: str, system: str = "", json_mode: bool = False) -> str:
        """Generate response from Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": self.temperature,
                "stream": False,
            }

            if system:
                payload["system"] = system

            response = self.client.post(
                f"{self.endpoint}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except httpx.ConnectError:
            logger.error(
                f"Falha ao conectar ao Ollama em {self.endpoint}. "
                "Verifique se o Ollama está rodando: ollama serve"
            )
            raise
        except Exception as e:
            logger.error(f"Erro ao comunicar com Ollama: {e}")
            raise

    def extract_json(self, prompt: str, system: str = "") -> dict:
        """Generate response and parse as JSON"""
        response = self.generate(prompt, system)
        try:
            # Tenta extrair JSON da resposta
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning(f"Falha ao parsear JSON: {response}")
        return {}

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
