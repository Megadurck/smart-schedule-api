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
  <img src="https://img.shields.io/badge/Pytest-passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

> Plataforma completa de agendamentos para empresas de servicos — API REST robusta + painel web moderno com arquitetura multi-tenant.

---

## Visao geral

O Smart Schedule e uma solucao full-stack para gestao de agendamentos. Cada empresa possui seu proprio espaco isolado (multi-tenant), com controle total sobre clientes, profissionais, horarios de funcionamento e agenda. O painel web consome a API diretamente e oferece uma experiencia fluida para o dia a dia operacional.

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
| **Agente local** | Modulo de assistente conversacional para listagem de slots e criacao de agendamentos via linguagem natural |

---

## Stack tecnologica

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — framework web assíncrono de alta performance
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM com suporte a migrations e queries compostas
- **[Pydantic v2](https://docs.pydantic.dev/)** — validacao e serializacao de dados
- **[python-jose](https://github.com/mpdavis/python-jose)** + **passlib** — autenticacao JWT com hash PBKDF2
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — gerenciamento de variaveis de ambiente
- **SQLite** — banco padrao para desenvolvimento local (facilmente substituível por PostgreSQL)

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
├── agent/                        # Modulo de agente conversacional local
│   ├── agent.py                  # Interpretacao de intencao e despacho de acoes
│   ├── tools.py                  # Ferramentas: listar slots, criar agendamentos
│   ├── config.py                 # Configuracao do provedor de LLM
│   └── main.py                   # Entry point do agente (CLI)
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

## Licenca

Distribuido sob a licenca **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
