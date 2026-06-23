"""
Test script for Ollama agent integration
"""
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure project root is importable when running this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.agent import handle_message

# Test cases
test_messages = [
    "Quais são os horários disponíveis para 03/03/2026?",
    "Quero agendar Maria Silva em 05/03/2026 às 14:00",
    "Pode me mostrar os horários?",
    "Agendar João em 10/03/2026 10:30",
    "Oi, como funciona?",
]

if __name__ == "__main__":
    print("=" * 60)
    print("Testando Agent com Ollama")
    print("=" * 60)

    for msg in test_messages:
        print(f"\n👤 Usuário: {msg}")
        try:
            response = handle_message(msg)
            print(f"🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Erro: {e}")
            logger.exception("Erro ao processar mensagem")

    print("\n" + "=" * 60)
