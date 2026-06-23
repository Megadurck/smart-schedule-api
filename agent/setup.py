"""
Setup helper for Ollama agent
"""
import subprocess
import sys
import time
import httpx


def check_ollama_running(endpoint: str = "http://localhost:11434", timeout: int = 2) -> bool:
    """Check if Ollama is running and accessible"""
    try:
        response = httpx.get(f"{endpoint}/api/tags", timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def check_model_available(model: str, endpoint: str = "http://localhost:11434") -> bool:
    """Check if a specific model is available"""
    try:
        client = httpx.Client(timeout=5)
        response = client.get(f"{endpoint}/api/tags")
        response.raise_for_status()
        data = response.json()
        models = [m["name"].split(":")[0] for m in data.get("models", [])]
        return model in models or any(model in m for m in models)
    except Exception:
        return False


def print_setup_instructions():
    """Print setup instructions for Ollama"""
    print("\n" + "=" * 70)
    print("🚀 SETUP DO AGENT COM OLLAMA")
    print("=" * 70)

    print("\n1️⃣  Instalar Ollama (se não tiver):")
    print("   📥 https://ollama.ai")
    print("   Ou no Windows: https://ollama.ai/download/windows")

    print("\n2️⃣  Em um terminal separado, iniciar Ollama:")
    print("   $ ollama serve")

    print("\n3️⃣  Em outro terminal, baixar o modelo:")
    print("   $ ollama pull dolphin-mixtral")
    print("   (ou outro modelo: mistral, neural-chat, llama2)")

    print("\n4️⃣  Voltar a este terminal e executar:")
    print("   $ python tests/test_ollama_agent.py")

    print("\n⚙️  Para trocar de modelo, edite .env:")
    print("   OLLAMA_MODEL=mistral (ou outro)")

    print("\n" + "=" * 70)


def main():
    """Check setup and provide instructions"""
    print("Verificando configuração do Agent Ollama...")
    print()

    if not check_ollama_running():
        print("❌ Ollama não está rodando em http://localhost:11434")
        print_setup_instructions()
        sys.exit(1)

    print("✅ Ollama está acessível")

    if not check_model_available("dolphin-mixtral"):
        print("⚠️  Modelo 'dolphin-mixtral' não encontrado")
        print("\n   Para instalá-lo, execute em um terminal:")
        print("   $ ollama pull dolphin-mixtral")
        print()

    print("✅ Configuração aparentemente OK!")
    print("\n   Para testar, execute:")
    print("   $ python tests/test_ollama_agent.py")


if __name__ == "__main__":
    main()
