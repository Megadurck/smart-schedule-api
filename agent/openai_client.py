"""
OpenAI integration for agent (future implementation)
"""
import logging

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI client for LLM-based agent (not yet implemented)"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.3,
    ):
        """Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4)
            temperature: Temperature setting (0-1)
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        # TODO: Initialize OpenAI client
        raise NotImplementedError("OpenAI integration not yet implemented. Use AGENT_PROVIDER=ollama")

    def generate(self, prompt: str, system: str = "") -> str:
        """Generate response from OpenAI"""
        raise NotImplementedError("OpenAI integration not yet implemented")

    def extract_json(self, prompt: str, system: str = "") -> dict:
        """Generate response and parse as JSON"""
        raise NotImplementedError("OpenAI integration not yet implemented")

    def close(self):
        """Close client connection"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
