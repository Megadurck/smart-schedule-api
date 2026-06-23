## Ollama Agent Integration

O agent foi migrado para usar Ollama (LLM local) em vez de pattern matching simples. Isso fornece:

✅ **Melhorias:**
- Compreensão natural de linguagem em português
- Maior flexibilidade em interpretação de intenções
- Melhor tratamento de variações linguísticas
- Integração com modelo `dolphin-mixtral` executando localmente

### Pré-requisitos

1. **Ollama instalado**: https://ollama.ai
2. **Modelo dolphin-mixtral carregado**:
   ```bash
   ollama pull dolphin-mixtral
   ```
3. **Ollama rodando** na porta padrão:
   ```bash
   ollama serve
   ```

### Configuração

O arquivo `.env` foi atualizado com:
```env
AGENT_PROVIDER=ollama
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=dolphin-mixtral
OLLAMA_TEMPERATURE=0.3
```

### Testando o Agent

1. **Garantir que Ollama está rodando**:
   ```bash
   # Em outro terminal
   ollama serve
   ```

2. **Executar teste**:
   ```bash
   python tests/test_ollama_agent.py
   ```

3. **Modo interativo**:
   ```bash
   python -m agent.agent
   ```

### Como funciona

1. Usuário envia mensagem
2. LLM (Ollama) analisa e extrai estrutura JSON com:
   - `action`: "list_slots", "create_schedule" ou "help"
   - `date`: Data em DD/MM/YYYY (se aplicável)
   - `customer_name`: Nome do cliente (se aplicável)
   - `time`: Hora em HH:MM:SS (se aplicável)
   - `confidence`: Confiança da interpretação (0-1)
3. Agent executa a ação
4. Resposta formatada é retornada

### Exemplos de uso

```
Usuário: "Quais horários estão disponíveis para 03/03/2026?"
→ Retorna lista de slots disponíveis

Usuário: "Agendar Maria Silva em 05/03/2026 às 14:00"
→ Cria agendamento confirmado

Usuário: "Pode me ajudar?"
→ Retorna mensagem de ajuda
```

### Fallback

Se o Ollama não estiver disponível, o agent tenta:
1. Modo simples (pattern matching)
2. AGENT_PROVIDER=offline (desativa LLM)

### Solução de problemas

**Erro: "Falha ao conectar ao Ollama"**
- Verifique se Ollama está rodando: `ollama serve`
- Verifique endpoint em `.env` (padrão: http://localhost:11434)

**Resposta vazia do LLM**
- Verifique se o modelo `dolphin-mixtral` está carregado: `ollama list`
- Tente usar outro modelo: `ollama pull mistral`, depois atualize `.env`

**Resposta lenta**
- Normal para primeira execução (modelo sendo carregado em RAM)
- Modelos maiores são mais lentos, considere usar `mistral` ou `neural-chat` se necessário
