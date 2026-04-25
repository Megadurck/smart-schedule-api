# Smart Schedule API

<p align="center">
  API REST para gestão de agenda com autenticação JWT, validação de expediente e ambiente preparado para agente de atendimento.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.13+-blue.svg">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.129.2-009688.svg">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0.47-D71F00.svg">
  <img alt="Pytest" src="https://img.shields.io/badge/tests-pytest%209.0.2-0A9EDC.svg">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green.svg">
</p>

## Sumário

- [Visão Geral](#visão-geral)
- [Principais Funcionalidades](#principais-funcionalidades)
- [Regras de Negócio Implementadas](#regras-de-negócio-implementadas)
- [Arquitetura](#arquitetura)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Stack e Dependências](#stack-e-dependências)
- [Como Rodar o Projeto](#como-rodar-o-projeto)
- [Documentação Interativa](#documentação-interativa)
- [Autenticação JWT](#autenticação-jwt)
- [API Endpoints](#api-endpoints)
- [Exemplos de Uso](#exemplos-de-uso)
- [Testes](#testes)
- [Banco de Dados](#banco-de-dados)
- [Roadmap de Melhorias](#roadmap-de-melhorias)
- [Licença](#licença)

---

## Visão Geral

O Smart Schedule API é uma API REST construída com FastAPI para controle de agendamentos.

O projeto implementa:

- cadastro e consulta de horários de funcionamento por dia da semana;
- criação, atualização, leitura e remoção de agendamentos;
- validações de conflito de horário;
- validações de horário de expediente e intervalo de almoço;
- cálculo de slots de atendimento disponíveis por dia;
- sugestão de horários recorrentes com base no histórico do cliente;
- autenticação JWT com access token (10 minutos) e refresh token;
- ambiente configurado para receber um agente de IA para interpretar mensagens de clientes e agendar horários automaticamente.

Além da API principal, o projeto já inclui um módulo de agente local em `agent/`, preparado para evoluir de um fluxo offline de testes para um fluxo integrado com provedor de IA.

A persistência é feita em SQLite via SQLAlchemy ORM.

---

## Principais Funcionalidades

### 1) Gestão de Agendamentos

- Criar agendamento com nome do cliente, data e hora.
- Listar todos os agendamentos.
- Buscar agendamento por ID.
- Atualizar agendamento existente.
- Deletar agendamento.

### 2) Gestão de Horário de Funcionamento

- Configurar expediente por dia da semana.
- Configurar duração de slot de atendimento (em minutos).
- Configurar intervalo de almoço opcional.
- Listar horários configurados.
- Calcular total de slots disponíveis em um dia.

### 3) Sugestão de Horários Recorrentes

- Aprende padrões do cliente com base em agendamentos anteriores.
- Prioriza combinações recorrentes de dia da semana + horário.
- Valida disponibilidade real (expediente ativo e sem conflito).
- Faz fallback para próximos horários livres quando não houver histórico suficiente.

### 4) Saúde da API

- Endpoint de health check para monitoramento.

### 5) Autenticação e Segurança

- Login por cliente + senha.
- Access token JWT com expiração de 10 minutos.
- Refresh token para renovação sem novo login.
- Rotas de escrita protegidas por Bearer Token.

### 6) Agente de Atendimento (Preparado para IA)

- Módulo local de agente em `agent/` para testes incrementais.
- Interpretação de intenção por mensagem (consultar horários e agendar).
- Execução das regras reais de negócio da agenda (conflito e almoço).
- Modo offline para validação funcional sem dependência de provedor externo.
- Ambiente pronto para plugar provedor de IA quando desejado.

---

## Regras de Negócio Implementadas

### Agendamento

- Data deve estar no formato `DD/MM/YYYY`.
- Hora deve estar no formato `HH:MM:SS`.
- Não permite conflito de data/hora entre agendamentos.
- Não permite agendar fora do horário de funcionamento ativo do dia.
- Se o horário estiver no intervalo de almoço, o agendamento é rejeitado.

### Sugestão de Horários

- Usa histórico por cliente para aprender recorrência de `weekday + time`.
- Ordena preferências por frequência e recência.
- Retorna somente sugestões válidas no expediente ativo.
- Nunca sugere horário já ocupado.
- Se não houver histórico, retorna próximos slots livres por ordem cronológica.

### Horário de Funcionamento

- `start_time` deve ser menor que `end_time`.
- Se almoço for informado:
  - `lunch_start` deve ser menor que `lunch_end`.
  - almoço deve estar completamente dentro do expediente.
- `slot_duration_minutes` deve ser maior que zero.
- `weekday` deve estar entre `0` e `6` (segunda a domingo).

### Mapeamento de weekday

- `0` = SEGUNDA
- `1` = TERÇA
- `2` = QUARTA
- `3` = QUINTA
- `4` = SEXTA
- `5` = SÁBADO
- `6` = DOMINGO

---

## Arquitetura

O projeto segue uma separação por camadas:

- **Routers (API)**: entrada HTTP, validação inicial de payload e códigos de resposta.
- **Services (Negócio)**: regras de domínio e orquestração.
- **Repositories (Dados)**: queries e persistência com SQLAlchemy.
- **Models (ORM)**: entidades do banco de dados.
- **Database**: configuração do engine, session e base declarativa.
- **Agent**: camada local de interação por mensagem, preparada para receber um provedor de IA no futuro.

Fluxo principal:

1. Requisição chega no router.
2. Router chama service.
3. Service aplica regras (conflito, expediente, parsing, etc.).
4. Service usa repository para acessar/persistir dados.
5. Repository interage com models via Session.

Fluxo atual do agente local:

1. Usuário envia uma mensagem no terminal.
2. O módulo `agent/agent.py` identifica a intenção da mensagem.
3. O módulo `agent/tools.py` reutiliza as regras e serviços já existentes da API.
4. O agente responde com horários disponíveis ou com o resultado do agendamento.

---

## Estrutura de Pastas

```text
smart-schedule-api/
├── agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   ├── main.py
│   └── tools.py
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routers/
│   │           ├── auth.py
│   │           ├── health.py
│   │           ├── schedule.py
│   │           └── working_hours.py
│   ├── core/
│   │   ├── dependencies.py
│   │   ├── security.py
│   │   └── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py
│   ├── enum/
│   │   └── weekday.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── schedule_model.py
│   │   └── working_hours_model.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── client_repository.py
│   │   └── schedule_repository.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── schedule.py
│   │   └── working_hours.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── schedule_service.py
│   │   └── working_hours_service.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_schedule.py
│   └── test_working_hours.py
├── .env.example
├── reset_db.py
├── smart_schedule.db
├── requirements.txt
├── LICENSE
└── .gitignore
```

---

## Stack e Dependências

Dependências principais:

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- Pytest
- HTTPX (suporte aos testes e cliente HTTP)
- Passlib (hash de senha com pbkdf2_sha256)
- Python-JOSE (JWT)
- Python-Dotenv (carregamento de variáveis de ambiente)

Arquivo de dependências: `requirements.txt`

---

## Como Rodar o Projeto

### Pré-requisitos

- Python 3.13+
- Pip

### 1) Clonar o repositório

```bash
git clone https://github.com/Megadurck/smart-schedule-api.git
cd smart-schedule-api
```

### 2) Criar e ativar ambiente virtual

#### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Instalar dependências

```bash
pip install -r requirements.txt
```

### 4) Configurar variáveis de ambiente

`SECRET_KEY` é obrigatória para geração/validação de JWT.

Você pode usar `.env.example` como base.

#### Windows (PowerShell)

```powershell
$env:SECRET_KEY="troque-por-uma-chave-forte"
$env:AGENT_PROVIDER="offline"
```

#### Linux/macOS

```bash
export SECRET_KEY="troque-por-uma-chave-forte"
export AGENT_PROVIDER="offline"
```

Variáveis opcionais do agente:

- `AGENT_PROVIDER=offline` para o modo local de testes.
- `OPENAI_API_KEY=...` para preparar integração com provedor online no futuro.

### 5) Rodar a API em desenvolvimento

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

- http://127.0.0.1:8000 (redireciona automaticamente para o Swagger)

### 6) Executar o agente local (modo offline)

```bash
python -m agent.agent
```

Exemplos de mensagens para testar no terminal:

- `horarios para 03/03/2026`
- `agendar nome Maria em 03/03/2026 09:00:00`
- `agendar nome Joao em 03/03/2026 12:30:00`

Para preparar integração com provedor de IA, configure as variáveis de ambiente:

- `AGENT_PROVIDER=offline` (padrão)
- `OPENAI_API_KEY=...` (opcional, para provider online)

---

## Documentação Interativa

Com a aplicação rodando, acesse:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Ao abrir a raiz `/`, o browser é redirecionado automaticamente para o Swagger.

---

## Autenticação JWT

Fluxo recomendado:

1. Registrar credencial de cliente em `POST /auth/register`.
2. Fazer login em `POST /auth/login`.
3. Usar `access_token` no header `Authorization: Bearer <token>`.
4. Ao expirar access token (10 min), usar `POST /auth/refresh`.
5. Se refresh token expirar, fazer login novamente.

Mensagens de expiração:

- Access token expirado: orientar refresh ou novo login.
- Refresh token expirado: orientar novo login.

Obs.: requisição sem token em rota protegida retorna `401 Unauthorized`.

---

## API Endpoints

Base path: `/api/v1`

### Health

- `GET /health`

### Schedule

- `GET /schedule/` -> lista todos
- `GET /schedule/{id}` -> busca por ID
- `POST /schedule/` -> cria (protegido)
- `PUT /schedule/{id}` -> atualiza (protegido)
- `DELETE /schedule/{id}` -> remove (protegido)
- `POST /schedule/suggestions` -> sugere horários recorrentes por cliente (protegido)

### Working Hours

- `GET /working-hours/` -> lista configurações
- `POST /working-hours/` -> cria/atualiza configuração do dia (protegido)
- `GET /working-hours/slots/{weekday}` -> calcula slots disponíveis

### Auth

- `POST /auth/register` -> cria credencial para cliente e devolve tokens
- `POST /auth/login` -> autentica cliente e devolve tokens
- `POST /auth/refresh` -> renova access token
- `GET /auth/me` -> retorna cliente autenticado

---

## Exemplos de Uso

### Registrar credencial

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "joao",
    "password": "senha123"
  }'
```

### Login

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "joao",
    "password": "senha123"
  }'
```

### Definir expediente (segunda)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/working-hours/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -d '{
    "weekday": 0,
    "start_time": "08:00:00",
    "end_time": "18:00:00",
    "slot_duration_minutes": 30,
    "lunch_start": "12:00:00",
    "lunch_end": "14:00:00"
  }'
```

### Criar agendamento

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/schedule/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -d '{
    "client_name": "João Silva",
    "date": "03/03/2026",
    "time": "10:00:00"
  }'
```

### Consultar slots do dia

```bash
curl "http://127.0.0.1:8000/api/v1/working-hours/slots/0"
```

### Sugerir horários para cliente

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/schedule/suggestions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -d '{
    "client_name": "João Silva",
    "start_date": "11/03/2026",
    "limit": 3,
    "search_days": 30
  }'
```

### Testar agente local em modo offline

```bash
python -m agent.agent
```

Exemplo de sessão:

```text
> horarios para 03/03/2026
Horarios disponiveis: 03/03/2026 08:00:00, 03/03/2026 08:30:00, ...

> agendar nome Maria em 03/03/2026 09:00:00
Agendamento confirmado para Maria em 03/03/2026 as 09:00:00.
```

---

## Testes

A suíte utiliza Pytest e está organizada em:

- `tests/test_schedule.py`
- `tests/test_working_hours.py`
- `tests/test_auth.py`
- `tests/conftest.py`

O módulo `agent/` também foi validado manualmente em cenários de:

- listagem de horários disponíveis;
- bloqueio de conflito no mesmo horário;
- bloqueio de agendamento durante o intervalo de almoço.

Execução dos testes:

```bash
pytest -q
```

Resultado atual da suíte:

- 51 testes passando

---

## Banco de Dados

- Banco local: SQLite
- Arquivo: `smart_schedule.db`
- URL configurada em `app/database/session.py`:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./smart_schedule.db"
```

As tabelas são criadas automaticamente no startup da aplicação (lifespan do FastAPI).

### Resetar banco

```bash
python reset_db.py
```

---

## Roadmap de Melhorias

Sugestões para evolução do projeto:

- adicionar migrations com Alembic;
- separar `requirements` de produção e desenvolvimento;
- mover configurações para um módulo central (`app/core/config.py`);
- incluir autorização por papéis (roles/permissões);
- implementar multi-tenant (owner por usuário/empresa);
- expor o agente local por endpoint HTTP ou webhook;
- conectar o agente a um provedor de IA para interpretação avançada de mensagens;
- criar endpoint para confirmação automática de agendamento a partir de sugestão;
- adicionar CI com lint, type-check e testes automatizados.

---

## Licença

Este projeto está sob licença MIT.

Veja o arquivo [LICENSE](LICENSE).
