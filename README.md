# Smart Schedule API

<p align="center">
  API REST multi-tenant para gestão de agendas com autenticação JWT, controle de expediente, clientes finais, profissionais e agente local preparado para canais conversacionais.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.13+-blue.svg">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.129.2-009688.svg">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0.47-D71F00.svg">
  <img alt="Pytest" src="https://img.shields.io/badge/tests-59%20passed-0A9EDC.svg">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green.svg">
</p>

## Visão Geral

O Smart Schedule API evoluiu de uma agenda simples para uma base SaaS multi-tenant. Hoje cada empresa possui seu próprio conjunto de usuários internos, clientes finais, profissionais, horários de trabalho e agendamentos, todos isolados por `company_id`.

O sistema foi modelado para um fluxo onde:

- a empresa configura expediente e slots de atendimento;
- usuários internos autenticados operam a conta da empresa;
- clientes finais são cadastrados e vinculados aos agendamentos;
- profissionais podem ser associados opcionalmente a cada atendimento;
- um agente local reutiliza as mesmas regras da API para consultar disponibilidade e criar agendamentos.

A persistência é feita com SQLite e SQLAlchemy ORM. A aplicação expõe uma API FastAPI com documentação automática em Swagger e já possui suíte de testes cobrindo autenticação, agendamentos, expediente, customers e professionals.

## O Que Mudou

A principal reformulação do projeto foi a troca do antigo modelo centrado em `client` por um domínio separado por responsabilidade:

- `Company`: tenant raiz da plataforma.
- `User`: usuário interno autenticado da empresa.
- `Customer`: cliente final atendido pela empresa.
- `Professional`: prestador, atendente ou profissional opcional ligado ao atendimento.
- `Schedule`: agendamento isolado por empresa, cliente final e profissional opcional.
- `WorkingHours`: expediente da empresa por dia da semana.

Além disso:

- o JWT agora carrega `company_id` e `sub = user.id`;
- autenticação passou a usar `company_name` + `user_name`;
- rotas de agenda e expediente exigem autenticação;
- foram adicionados CRUDs de customers e professionals;
- o agente local passou a resolver tenant por `AGENT_COMPANY_NAME`.

## Principais Funcionalidades

### Multi-tenant

- Isolamento completo de dados por empresa.
- Mesmo `user_name` pode existir em empresas diferentes.
- Agendamentos no mesmo dia e hora são permitidos em empresas distintas.

### Autenticação

- Registro e login por empresa e usuário interno.
- Access token JWT com validade curta.
- Refresh token para renovação de sessão.
- Endpoint `/auth/me` para resolver o usuário autenticado.

### Gestão de Customers

- Criar, listar, consultar, atualizar e remover clientes finais.
- Nomes únicos por empresa.
- Reuso automático do customer em novos agendamentos quando o nome já existe.

### Gestão de Professionals

- Criar, listar, consultar, atualizar e remover profissionais.
- Campo `is_active` para operação futura e filtragens.
- Associação opcional em cada agendamento.

### Gestão de Agendamentos

- CRUD completo de agendamentos.
- Associação por `customer_name` e `professional_id` opcional.
- Sugestão de horários recorrentes com base no histórico do customer.
- Bloqueio de conflito de horário dentro da mesma empresa.

### Gestão de Expediente

- Configuração por dia da semana.
- Duração customizável de slot.
- Intervalo de almoço opcional.
- Cálculo de slots disponíveis por weekday.

### Agente Local

- Opera em modo offline para testes rápidos.
- Reaproveita os mesmos services da API.
- Resolve tenant por `AGENT_COMPANY_NAME`.
- Pode ser evoluído para WhatsApp, chatbot ou outro provider depois.

## Regras de Negócio

### Agendamentos

- `date` deve estar no formato `DD/MM/YYYY`.
- `time` deve estar no formato `HH:MM:SS`.
- Não pode haver conflito de data e hora dentro da mesma empresa.
- O horário deve estar dentro do expediente ativo do dia.
- Horários dentro do almoço são rejeitados.
- `professional_id`, quando informado, precisa pertencer à mesma empresa do usuário autenticado.

### Sugestões

- O histórico é calculado por customer dentro da empresa atual.
- Preferências consideram recorrência de `weekday + time`.
- Horários sugeridos só aparecem se estiverem livres e dentro do expediente.
- Sem histórico suficiente, a API retorna os próximos slots livres.

### Working Hours

- `weekday` vai de `0` a `6`.
- `start_time` deve ser anterior a `end_time`.
- `slot_duration_minutes` deve ser maior que zero.
- Se almoço for informado, ele deve estar inteiramente dentro do expediente.

### Weekday

- `0` = segunda
- `1` = terça
- `2` = quarta
- `3` = quinta
- `4` = sexta
- `5` = sábado
- `6` = domingo

## Arquitetura

O projeto segue separação por camadas:

- `app/api`: entrada HTTP e contratos de resposta.
- `app/services`: regras de negócio e orquestração.
- `app/repositories`: acesso e persistência dos dados.
- `app/models`: entidades ORM.
- `app/schemas`: payloads e responses Pydantic.
- `agent`: interface conversacional local sobre o mesmo domínio.

Fluxo principal:

1. A requisição entra por um router.
2. O router resolve o usuário autenticado.
3. O service aplica validações e regras de negócio.
4. Os repositories persistem ou consultam dados filtrados por empresa.
5. A resposta volta serializada pelos schemas.

Fluxo do agente:

1. O usuário envia uma mensagem no terminal.
2. `agent/agent.py` interpreta a intenção.
3. `agent/tools.py` resolve a empresa pelo nome configurado.
4. O agente consulta slots ou cria o agendamento usando os mesmos services da API.

## Estrutura de Pastas

```text
smart-schedule-api/
├── agent/
│   ├── agent.py
│   ├── config.py
│   ├── main.py
│   └── tools.py
├── app/
│   ├── api/v1/routers/
│   │   ├── auth.py
│   │   ├── customers.py
│   │   ├── health.py
│   │   ├── professionals.py
│   │   ├── schedule.py
│   │   └── working_hours.py
│   ├── core/
│   ├── database/
│   ├── enum/
│   ├── models/
│   │   ├── company.py
│   │   ├── customer.py
│   │   ├── professional.py
│   │   ├── schedule_model.py
│   │   ├── user.py
│   │   └── working_hours_model.py
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_customers.py
│   ├── test_professionals.py
│   ├── test_schedule.py
│   └── test_working_hours.py
├── reset_db.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Stack

Principais componentes da aplicação:

- Python 3.13+
- FastAPI
- SQLAlchemy 2.x
- Pydantic
- python-jose
- passlib
- python-dotenv
- pytest
- httpx
- uvicorn

## Como Rodar

### Pré-requisitos

- Python 3.13+
- Ambiente virtual recomendado

### 1. Clonar o repositório

```bash
git clone https://github.com/Megadurck/smart-schedule-api.git
cd smart-schedule-api
```

### 2. Criar e ativar o ambiente virtual

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Variáveis mínimas:

- `SECRET_KEY`: chave usada para assinar os JWTs.
- `AGENT_PROVIDER`: provider do agente, hoje normalmente `offline`.
- `AGENT_COMPANY_NAME`: empresa que o agente local vai operar.

Exemplo PowerShell:

```powershell
$env:SECRET_KEY="troque-por-uma-chave-forte"
$env:AGENT_PROVIDER="offline"
$env:AGENT_COMPANY_NAME="empresa_demo"
```

Exemplo Linux ou macOS:

```bash
export SECRET_KEY="troque-por-uma-chave-forte"
export AGENT_PROVIDER="offline"
export AGENT_COMPANY_NAME="empresa_demo"
```

Variáveis opcionais:

- `OPENAI_API_KEY`: reservada para integração futura com provider online.

### 5. Subir a API

```bash
uvicorn app.main:app --reload
```

A raiz `/` redireciona para `/docs`.

### 6. Resetar o banco local

```bash
python reset_db.py
```

### 7. Rodar o agente local

```bash
python -m agent.agent
```

Exemplos de mensagens:

- `horarios para 03/03/2026`
- `agendar nome Maria em 03/03/2026 09:00:00`

## Documentação Interativa

Com a API rodando:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Autenticação JWT

Fluxo recomendado:

1. Registrar usuário interno em `POST /api/v1/auth/register`.
2. Fazer login em `POST /api/v1/auth/login`.
3. Enviar `Authorization: Bearer <access_token>` nas rotas protegidas.
4. Renovar sessão em `POST /api/v1/auth/refresh`.
5. Consultar usuário logado em `GET /api/v1/auth/me`.

Payload de registro e login:

```json
{
  "company_name": "empresa_demo",
  "user_name": "admin",
  "password": "senha123"
}
```

O token devolvido inclui o tenant da sessão e é usado para filtrar todos os recursos protegidos.

## Endpoints

Base path: `/api/v1`

### Health

- `GET /health`

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`

### Working Hours

- `GET /working-hours/`
- `POST /working-hours/`
- `GET /working-hours/slots/{weekday}`

### Schedule

- `GET /schedule/`
- `GET /schedule/{id}`
- `POST /schedule/`
- `PUT /schedule/{id}`
- `DELETE /schedule/{id}`
- `POST /schedule/suggestions`

### Customers

- `GET /customers/`
- `GET /customers/{customer_id}`
- `POST /customers/`
- `PUT /customers/{customer_id}`
- `DELETE /customers/{customer_id}`

### Professionals

- `GET /professionals/`
- `GET /professionals/{professional_id}`
- `POST /professionals/`
- `PUT /professionals/{professional_id}`
- `DELETE /professionals/{professional_id}`

## Exemplos de Payload

### Registrar usuário interno

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "barbearia_centro",
    "user_name": "admin",
    "password": "senha123"
  }'
```

### Configurar expediente

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

### Criar customer

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/customers/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -d '{
    "name": "Maria Souza"
  }'
```

### Criar professional

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/professionals/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -d '{
    "name": "Dra. Ana",
    "is_active": true
  }'
```

### Criar agendamento

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/schedule/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -d '{
    "customer_name": "Maria Souza",
    "date": "03/03/2026",
    "time": "09:00:00",
    "professional_id": 1
  }'
```

### Sugerir horários

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/schedule/suggestions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -d '{
    "customer_name": "Maria Souza",
    "start_date": "11/03/2026",
    "limit": 3,
    "search_days": 30
  }'
```

## Testes

A suíte usa pytest e cobre os principais fluxos do domínio atual:

- autenticação multi-tenant;
- isolamento de agendamentos por empresa;
- regras de expediente e slots;
- CRUD de customers;
- CRUD de professionals;
- associação opcional de professional em schedules.

Execução:

```bash
pytest -q
```

Resultado validado nesta versão: `59 passed`.

## Banco de Dados

O banco local padrão é SQLite. Em desenvolvimento, o schema é criado automaticamente na subida da aplicação. Quando houver mudança estrutural relevante, o fluxo recomendado é resetar o banco local com:

```bash
python reset_db.py
```

## Próximos Passos

- integrar o agente a um canal real, como WhatsApp;
- incluir migrations formais para ambientes persistentes;
- adicionar autorização por papéis de usuário interno;
- expandir disponibilidade por profissional, não apenas por empresa.

## Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para detalhes.

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
