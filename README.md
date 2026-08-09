# Smart Schedule

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.x-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" />
  <img src="https://img.shields.io/badge/Pydantic-2.x-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/TypeScript-6.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-8.x-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-4.x-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-LLM-8B0000?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Pytest-passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/v2.0-LLM--Agent-blue?style=for-the-badge" />
</p>

> Plataforma completa de agendamentos para empresas de servicos — API REST robusta + painel web moderno + agente conversacional com LLM local (Ollama).

---

## Versao 2.0 — Agente com LLM Local

**Nova**: Agora o sistema inclui um assistente conversacional inteligente que interpreta linguagem natural em português e interage diretamente com a API de agendamentos. O agente roda localmente usando **Ollama**, sem dependência de APIs externas.

### O que mudou

| Feature | v1.0 | v2.0 |
|---|---|---|
| Interpretação de intenção | Pattern matching simples | LLM com Ollama (compreensão natural) |
| Suporte para linguagem natural | Limitado (regex) | Completo em português |
| Escalabilidade de novas ações | Manual (novos padrões) | Automática (LLM entende contexto) |
| Dependência externa | Nenhuma | Ollama local (sem internet necessária) |
| Confiança da interpretação | N/A | Métrica incluída (0-1) |

---

## Visao geral

O Smart Schedule e uma solucao full-stack para gestao de agendamentos. Cada empresa possui seu proprio espaco isolado (multi-tenant), com controle total sobre clientes, profissionais, horarios de funcionamento e agenda. O painel web consome a API diretamente e oferece uma experiencia fluida para o dia a dia operacional.

A partir da **v2.0**, um **agente conversacional com LLM local** permite que usuarios interajam com o sistema via linguagem natural, listando slots e agendando sem precisar acessar o painel web.

### Principais funcionalidades

| Modulo | Descricao |
|---|---|
| **Autenticacao** | Registro de empresa + login com JWT (access + refresh token) |
| **Multi-tenant** | Isolamento total de dados por empresa via `company_id` |
| **Clientes** | CRUD completo de clientes vinculados a empresa |
| **Profissionais** | Gestao de profissionais com valor por servico |
| **Horarios** | Configuracao de horarios de funcionamento por dia da semana |
| **Agenda** | Criacao, listagem e atualizacao de status de agendamentos |
| **Dashboard** | Indicadores operacionais: receita total, ticket medio, agendamentos por profissional e proximos compromissos |
| **Agente LLM** | Assistente conversacional local para listar slots e criar agendamentos via linguagem natural (novo em v2.0) |

---

## Stack tecnologica

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — framework web assíncrono de alta performance
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM com suporte a migrations e queries compostas
- **[Pydantic v2](https://docs.pydantic.dev/)** — validacao e serializacao de dados
- **[python-jose](https://github.com/mpdavis/python-jose)** + **passlib** — autenticacao JWT com hash PBKDF2
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — gerenciamento de variaveis de ambiente
- **[httpx](https://www.python-httpx.org/)** — cliente HTTP async/sync (integracao Ollama)
- **SQLite** — banco padrao para desenvolvimento local (facilmente substituível por PostgreSQL)

### Agente LLM (v2.0)
- **[Ollama](https://ollama.ai/)** — LLM local (sem dependência de APIs externas)
- **Modelo dolphin-mixtral** — compreensao natural em português com excelente performance
- **Prompt engineering** — extração de intenção e parâmetros em JSON estruturado
- **Interpretação de linguagem natural** — suporta variações linguísticas e contexto

### Frontend
- **[React 19](https://react.dev/)** + **[TypeScript](https://www.typescriptlang.org/)** — UI declarativa com tipagem forte
- **[Vite 8](https://vitejs.dev/)** — bundler ultrarapido com HMR
- **[Tailwind CSS v4](https://tailwindcss.com/)** — estilizacao utilitaria
- **[shadcn/ui](https://ui.shadcn.com/)** + **Radix UI** — componentes acessiveis e customizaveis
- **[React Hook Form](https://react-hook-form.com/)** + **[Zod](https://zod.dev/)** — formularios com validacao de schema
- **[Axios](https://axios-http.com/)** — cliente HTTP com interceptors
- **[React Router v7](https://reactrouter.com/)** — roteamento declarativo
- **[Lucide React](https://lucide.dev/)** — icones consistentes

### Qualidade
- **[Pytest](https://docs.pytest.org/)** — testes de integracao por modulo
- **ESLint** — linting do frontend

---

## Estrutura do projeto

```
smart-schedule-api/
│
├── app/                          # Backend FastAPI
│   ├── main.py                   # Entry point, lifespan e registro de rotas
│   ├── api/
│   │   └── v1/
│   │       └── routers/          # Um arquivo por dominio de negocio
│   │           ├── auth.py
│   │           ├── customers.py
│   │           ├── professionals.py
│   │           ├── working_hours.py
│   │           ├── schedule.py
│   │           ├── company_admin.py
│   │           ├── dashboard.py
│   │           └── health.py
│   ├── core/
│   │   ├── dependencies.py       # Injecao de dependencias (usuario autenticado, etc.)
│   │   └── security.py           # Hash de senha, criacao e validacao de JWT
│   ├── database/
│   │   └── session.py            # Engine SQLAlchemy, sessao e migracoes inline
│   ├── models/                   # Modelos ORM (tabelas do banco)
│   ├── schemas/                  # Schemas Pydantic (request/response)
│   ├── repositories/             # Camada de acesso ao banco por dominio
│   ├── services/                 # Regras de negocio por dominio
│   └── enum/                     # Enums: status de agendamento, dias da semana
│
├── agent/                        # Modulo de agente conversacional com LLM (v2.0)
│   ├── agent.py                  # Interpretacao de intencao + despacho de acoes
│   ├── llm.py                    # Cliente Ollama com suporte a JSON estruturado
│   ├── openai_client.py          # Stub para integracao OpenAI (futura)
│   ├── tools.py                  # Ferramentas: listar slots, criar agendamentos
│   ├── prompts.py                # Prompts estruturados em português
│   ├── config.py                 # Configuracao: endpoint, modelo, temperatura Ollama
│   ├── setup.py                  # Setup/diagnóstico do Ollama (verifica instalação)
│   └── main.py                   # Entry point do agente (CLI interativa)
│
├── frontend/                     # Painel web React + TypeScript
│   ├── src/
│   │   ├── App.tsx               # Rotas e layout principal
│   │   ├── pages/                # Uma pagina por modulo (Dashboard, Clientes, etc.)
│   │   ├── components/           # Componentes reutilizaveis e UI base (shadcn)
│   │   ├── contexts/             # AuthContext (estado global de autenticacao)
│   │   ├── services/
│   │   │   └── api.ts            # Configuracao do Axios e todos os servicos de API
│   │   └── lib/
│   │       └── utils.ts          # Utilitarios (cn, etc.)
│   ├── package.json
│   └── vite.config.ts
│
├── tests/                        # Testes de integracao com Pytest
│   ├── conftest.py               # Fixtures: banco em memoria, cliente de teste, tokens
│   ├── test_auth.py
│   ├── test_customers.py
│   ├── test_professionals.py
│   ├── test_working_hours.py
│   ├── test_schedule.py
│   └── test_dashboard.py
│
├── reset_db.py                   # Script para resetar o banco local
├── requirements.txt
└── .env                          # Variaveis de ambiente (nao commitado)
```

---

## Como executar localmente

### Pre-requisitos

- Python **3.11+**
- Node.js **18+** e npm
- Git

---

### 1. Clonar o repositorio

```bash
git clone https://github.com/Megadurck/smart-schedule-api.git
cd smart-schedule-api
```

---

### 2. Configurar variaveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua_chave_secreta_longa_e_aleatoria
```

> A `SECRET_KEY` e obrigatoria. A API nao sobe sem ela. Voce pode gerar uma com:
> ```powershell
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

### 3. Backend

```powershell
# Criar e ativar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Subir a API
uvicorn app.main:app --reload --port 8000
```

A API estara disponivel em:

| URL | Descricao |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger UI — documentacao interativa |
| `http://127.0.0.1:8000/redoc` | ReDoc — documentacao alternativa |
| `http://127.0.0.1:8000/api/v1/health` | Health check |

> **Banco de dados:** O SQLite e criado automaticamente em `smart_schedule.db` na primeira execucao. Para resetar: `python reset_db.py`.

---

### 4. Frontend

```powershell
cd frontend

# Instalar dependencias
npm install

# Subir em modo desenvolvimento
npm run dev
```

O painel web estara disponivel em `http://localhost:5173`.

> O frontend aponta por padrao para `http://127.0.0.1:8000`. Certifique-se de que a API esta rodando antes de acessar o painel.

---

## 5. Agente Conversacional (v2.0) — Ollama

O agente LLM permite interagir com o sistema via **linguagem natural em português**, sem precisar acessar o painel web. Roda **localmente** usando Ollama, garantindo privacidade e sem depender de APIs externas.

### Pre-requisitos

1. **Ollama instalado** — [Download](https://ollama.ai)
2. **Modelo baixado localmente** — `dolphin-mixtral` recomendado (~8 GB)

### Configurar o agente

#### 1. Instalar Ollama
Download em https://ollama.ai

#### 2. Baixar o modelo
```powershell
ollama pull dolphin-mixtral
```

Ou usar outro modelo (mais rápido):
```powershell
ollama pull mistral
ollama pull neural-chat
ollama pull llama2
```

#### 3. Iniciar o servidor Ollama
Em um terminal separado:
```powershell
ollama serve
```

Sera exibido algo como:
```
Listening on 127.0.0.1:11434
```

#### 4. Configurar `.env`
Se usando modelo diferente, edite `.env`:
```env
AGENT_PROVIDER=ollama
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=dolphin-mixtral
OLLAMA_TEMPERATURE=0.3
```

#### 5. Testar o agente
```powershell
python tests/test_ollama_agent.py
```

Voce vera algo como:
```
👤 Usuário: Quais são os horários para 03/03/2026?
INFO:httpx:HTTP Request: POST http://localhost:11434/api/generate "HTTP/1.1 200 OK"
INFO:agent.agent:Intent: list_slots (confidence: 1.00)
🤖 Agent: Não encontrei horários disponíveis no período informado.
```

### Como funciona o fluxo

```
Usuário (Linguagem natural em português)
  ↓
Agente recebe mensagem
  ↓
OllamaClient faz requisição ao LLM
  ↓
LLM (dolphin-mixtral) interpreta e retorna JSON:
  {
    "action": "list_slots" | "create_schedule" | "help",
    "date": "DD/MM/YYYY" ou null,
    "customer_name": "Nome" ou null,
    "time": "HH:MM:SS" ou null,
    "confidence": 0.0 a 1.0
  }
  ↓
Agent despacha ação
  ↓
Tools executam via repositórios/services
  ↓
Resposta formatada retorna ao usuário
```

### Exemplos de uso

```
Usuário: "Quais horários estão disponíveis para 03/03/2026?"
→ Intent: list_slots, date: 03/03/2026
→ Retorna: Lista de slots disponíveis

Usuário: "Agendar Maria Silva em 05/03/2026 às 14:00"
→ Intent: create_schedule, customer_name: Maria Silva, date: 05/03/2026, time: 14:00:00
→ Retorna: Confirmação do agendamento

Usuário: "Pode me mostrar os horários?"
→ Intent: list_slots, date: null (usa data atual)
→ Retorna: Lista de slots para os próximos 7 dias

Usuário: "Oi, como funciona?"
→ Intent: help
→ Retorna: Mensagem de ajuda com exemplos
```

### Parar o agente
Pressione `Ctrl+C` no terminal para encerrar.

---

## Arquitetura do Agente LLM

### Componentes

| Componente | Arquivo | Responsabilidade |
|---|---|---|
| **LLM Client** | `agent/llm.py` | Comunicação com Ollama, gerenciamento de prompts e parsing de JSON |
| **Agent** | `agent/agent.py` | Orquestração de intent parsing, despacho de ações e tratamento de erros |
| **Tools** | `agent/tools.py` | Interface com o `ScheduleApiClient` para listar slots e criar agendamentos |
| **API Client** | `agent/api_client.py` | Cliente HTTP (login/refresh JWT) que consome a Smart Schedule API — o agent não acessa mais o banco diretamente |
| **WhatsApp Client** | `agent/whatsapp_client.py` | Envio de mensagens de resposta via Meta WhatsApp Cloud API |
| **Config** | `agent/config.py` | Configuração: endpoint Ollama, modelo, temperatura, provider (ollama/openai/offline), credenciais da API e do WhatsApp |
| **Prompts** | `agent/prompts.py` | Prompts estruturados em português com exemplos e formatos esperados |

### Fluxo de decisão

1. **Parsing de Intent**: O LLM analisa a mensagem e retorna um JSON estruturado com `action`, parâmetros e `confidence`
2. **Validação**: Agente verifica se todos os parâmetros necessários foram extraídos
3. **Execução**: Tools chamam a Smart Schedule API via HTTP (`agent/api_client.py`), autenticando com um usuário/empresa dedicado do agent
4. **Resposta**: Resultado formatado é retornado ao usuário (ou enviado de volta via WhatsApp, quando a mensagem vem do webhook)
5. **Fallback**: Se LLM falhar (timeout, erro), agent tenta padrão simples (pattern matching)

### Configuração de provedor

- **`AGENT_PROVIDER=ollama`** (padrão): Usa Ollama local
- **`AGENT_PROVIDER=offline`**: Desativa LLM, usa apenas pattern matching simples
- **`AGENT_PROVIDER=openai`** (futuro): Stub para integração OpenAI (não implementado ainda)

### Performance

- **Primeira requisição**: ~2-5s (modelo sendo carregado em RAM pelo Ollama)
- **Requisições subsequentes**: ~0.5-1.5s (modelo já na memória)
- **Timeout**: 300s padrão (para lentidão ou carregamento do modelo)

---

## Endpoints da API

Todos os endpoints (exceto `/auth/register` e `/auth/login`) exigem o header:
```
Authorization: Bearer <access_token>
```

### Autenticacao — `/api/v1/auth`

| Metodo | Rota | Descricao |
|---|---|---|
| `POST` | `/auth/register` | Registra uma nova empresa e retorna os tokens |
| `POST` | `/auth/login` | Autentica usuario e retorna os tokens |
| `POST` | `/auth/refresh` | Renova o access token a partir do refresh token |
| `GET` | `/auth/me` | Retorna os dados do usuario autenticado |

### Clientes — `/api/v1/customers`

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/customers` | Lista todos os clientes da empresa |
| `POST` | `/customers` | Cria um novo cliente |
| `GET` | `/customers/{id}` | Busca cliente por ID |
| `PUT` | `/customers/{id}` | Atualiza dados do cliente |
| `DELETE` | `/customers/{id}` | Remove o cliente |

### Profissionais — `/api/v1/professionals`

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/professionals` | Lista todos os profissionais |
| `POST` | `/professionals` | Cria um novo profissional |
| `GET` | `/professionals/{id}` | Busca profissional por ID |
| `PUT` | `/professionals/{id}` | Atualiza dados do profissional |
| `DELETE` | `/professionals/{id}` | Remove o profissional |

### Horarios de Funcionamento — `/api/v1/working-hours`

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/working-hours` | Lista configuracoes de horario da empresa |
| `POST` | `/working-hours` | Define horario para um dia da semana |
| `PUT` | `/working-hours/{id}` | Atualiza uma configuracao de horario |
| `DELETE` | `/working-hours/{id}` | Remove uma configuracao |

### Agendamentos — `/api/v1/schedule`

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/schedule` | Lista agendamentos (filtros por data, status, profissional) |
| `POST` | `/schedule` | Cria um novo agendamento |
| `GET` | `/schedule/{id}` | Busca agendamento por ID |
| `PATCH` | `/schedule/{id}/status` | Atualiza status (pendente, concluido, cancelado) |

### Administracao — `/api/v1/company-admin`

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/company-admin` | Retorna dados da empresa autenticada |
| `PUT` | `/company-admin` | Atualiza informacoes da empresa |

### Dashboard — `/api/v1/dashboard`

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/dashboard/insights` | Retorna indicadores: total de agendamentos, receita total, ticket medio, receita por profissional e proximos compromissos. Suporta filtro por `start_date` e `end_date`. |

---

## Testes

Os testes cobrem todos os modulos de negocio com banco SQLite em memoria. Cada suite cria e destroi seu proprio estado de forma isolada.

```powershell
# Rodar todos os testes
pytest -v

# Rodar apenas um modulo
pytest tests/test_schedule.py -v

# Modo silencioso (apenas resultado final)
pytest -q
```

---

## Build de producao

### Backend

Para produção, troque o SQLite por PostgreSQL configurando a variavel `DATABASE_URL` e use um servidor ASGI como [Gunicorn](https://gunicorn.org/) com workers Uvicorn:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000
```

### Frontend

```powershell
cd frontend
npm run build
```

Os arquivos estaticos serao gerados em `frontend/dist/` e podem ser servidos por qualquer CDN ou servidor web (Nginx, Vercel, Netlify, etc.).

---

## Mudancas na v2.0

### Adicoes

- ✅ **Agente LLM com Ollama**: Interpretação de linguagem natural em português
- ✅ **Cliente Ollama**: `agent/llm.py` com suporte a requisições JSON estruturadas
- ✅ **Prompts estruturados**: `agent/prompts.py` com exemplos em português
- ✅ **Ferramentas de agente**: `agent/tools.py` com integração a repositórios existentes
- ✅ **Configuração flexível**: Suporte para Ollama, OpenAI (stub) e offline
- ✅ **Testes**: `test_ollama_agent.py` para validar fluxo completo
- ✅ **Documentação**: Guia completo de setup em `OLLAMA_AGENT_README.md`
- ✅ **Métrica de confiança**: Cada intent inclui `confidence` (0-1)

### Melhorias

- 🔧 **Tratamento de erros robusto**: Fallback automático para pattern matching se LLM falhar
- 🔧 **Respostas mais claras**: Mensagens de ajuda e exemplos mais detalhados
- 🔧 **Timeout configurável**: 300s padrão para lentidão do modelo
- 🔧 **Isolamento de tenant**: Agente respeita `AGENT_COMPANY_NAME` para isolamento multi-tenant

### Compatibilidade

- ✅ Totalmente retrocompatível com v1.0
- ✅ Não altera endpoints da API
- ✅ Não modifica modelos do banco
- ✅ Apenas adiciona novo modulo `agent/` com opção de uso

---

## 🚧 Em finalizacao — Integracao com WhatsApp (Meta Cloud API)

**Status: em andamento.** O agente esta sendo adaptado para atender clientes diretamente pelo WhatsApp, usando a **Meta WhatsApp Cloud API** (numero de teste gratuito).

### O que ja foi feito

- ✅ O agent deixou de acessar o banco/services diretamente e agora consome a propria API via HTTP (`agent/api_client.py`), com login/refresh de JWT automatico
- ✅ Novo endpoint `GET /api/v1/schedule/available-slots` para expor a listagem de horarios livres
- ✅ Webhook do WhatsApp implementado em `app/api/v1/routers/whatsapp.py`:
  - `GET /api/v1/whatsapp/webhook` — handshake de verificacao exigido pelo Meta
  - `POST /api/v1/whatsapp/webhook` — recebe mensagens, valida a assinatura HMAC (`X-Hub-Signature-256`) e responde via `agent/whatsapp_client.py`
- ✅ Validado localmente: suite de testes (77 testes), fluxo HTTP completo do agent e handshake/assinatura do webhook

### O que falta (pre-requisitos manuais)

- ⏳ Criar o app no [Meta for Developers](https://developers.meta.com) e obter o numero de teste do WhatsApp
- ⏳ Preencher no `.env`: `META_VERIFY_TOKEN`, `META_WHATSAPP_TOKEN`, `META_PHONE_NUMBER_ID`, `META_APP_SECRET`
- ⏳ Expor a API publicamente (ex.: `ngrok`) para registrar a URL do webhook no painel do Meta
- ⏳ Teste real ponta a ponta enviando mensagens pelo WhatsApp

---

## Licenca

Distribuido sob a licenca **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
