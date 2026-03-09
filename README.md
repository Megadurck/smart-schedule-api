# Smart Schedule API

<p align="center">
  API REST para gestão de agenda com validação de horário de funcionamento.
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
- cálculo de slots de atendimento disponíveis por dia.

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

### 3) Saúde da API

- Endpoint de health check para monitoramento.

---

## Regras de Negócio Implementadas

### Agendamento

- Data deve estar no formato `DD/MM/YYYY`.
- Hora deve estar no formato `HH:MM:SS`.
- Não permite conflito de data/hora entre agendamentos.
- Não permite agendar fora do horário de funcionamento ativo do dia.
- Se o horário estiver no intervalo de almoço, o agendamento é rejeitado.

### Horário de Funcionamento

- `start_time` deve ser menor que `end_time`.
- Se almoço for informado:
  - `lunch_start` deve ser menor que `lunch_end`.
  - almoço deve estar completamente dentro do expediente.
- `slot_duration_minutes` deve ser maior que zero.
- `weekday` deve estar entre `0` e `6` (segunda a domingo).

### Mapeamento de weekday

- `0` = SEGUNDA
- `1` = TERCA
- `2` = QUARTA
- `3` = QUINTA
- `4` = SEXTA
- `5` = SABADO
- `6` = DOMINGO

---

## Arquitetura

O projeto segue uma separação por camadas:

- **Routers (API)**: entrada HTTP, validação inicial de payload e códigos de resposta.
- **Services (Negócio)**: regras de domínio e orquestração.
- **Repositories (Dados)**: queries e persistência com SQLAlchemy.
- **Models (ORM)**: entidades do banco de dados.
- **Database**: configuração do engine, session e base declarativa.

Fluxo principal:

1. Requisição chega no router.
2. Router chama service.
3. Service aplica regras (conflito, expediente, parsing, etc.).
4. Service usa repository para acessar/persistir dados.
5. Repository interage com models via Session.

---

## Estrutura de Pastas

```text
smart-schedule-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routers/
│   │           ├── health.py
│   │           ├── schedule.py
│   │           └── working_hours.py
│   ├── core/
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py
│   ├── enum/
│   │   └── weekday.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── shedule_model.py
│   │   └── working_hours_model.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── client_repository.py
│   │   └── schedule_repository.py
│   ├── schemas/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── schedule_service.py
│   │   └── working_hours_service.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_schedule.py
│   └── test_working_hours.py
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

Arquivo de dependências: `requirements.txt`

---

## Como Rodar o Projeto

### Pré-requisitos

- Python 3.13+
- Pip

### 1) Clonar o repositório

```bash
git clone https://github.com/Megadurck/smart-schedule-api.git
cd smart-shedule-api
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

### 4) Rodar a API em desenvolvimento

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

- http://127.0.0.1:8000

---

## Documentação Interativa

Com a aplicação rodando, acesse:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## API Endpoints

Base path: `/api/v1`

### Health

- `GET /health`

### Schedule

- `GET /schedule/` -> lista todos
- `GET /schedule/{id}` -> busca por ID
- `POST /schedule/` -> cria
- `PUT /schedule/{id}` -> atualiza
- `DELETE /schedule/{id}` -> remove

### Working Hours

- `GET /working-hours/` -> lista configurações
- `POST /working-hours/` -> cria/atualiza configuração do dia
- `GET /working-hours/slots/{weekday}` -> calcula slots disponíveis

---

## Exemplos de Uso

### Definir expediente (segunda)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/working-hours/" \
  -H "Content-Type: application/json" \
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

---

## Testes

A suíte utiliza Pytest e está organizada em:

- `tests/test_schedule.py`
- `tests/test_working_hours.py`
- `tests/conftest.py`

Execução dos testes:

```bash
pytest -q
```

Resultado atual da suíte:

- 39 testes passando

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

- padronizar respostas de erro com códigos HTTP mais semânticos (ex.: conflito 409);
- adicionar migrations com Alembic;
- separar `requirements` de produção e desenvolvimento;
- incluir autenticação/autorização;
- adicionar CI com lint, type-check e testes automatizados.

---

## Licença

Este projeto está sob licença MIT.

Veja o arquivo [LICENSE](LICENSE).
