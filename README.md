# Smart Schedule

Smart Schedule e uma plataforma de agendamentos para empresas de servicos, com API REST e painel web.

## Visao publica

O projeto oferece:
- Cadastro e autenticacao de empresas e usuarios internos
- Gestao de clientes e profissionais
- Gestao de agenda e horarios de funcionamento
- Dashboard com indicadores operacionais e de faturamento
- Arquitetura multi-tenant com isolamento por empresa

## Stack

- Backend: FastAPI, SQLAlchemy, Pydantic
- Frontend: React, TypeScript, Vite
- Banco: SQLite (padrao local)
- Testes: Pytest

## Estrutura (resumo)

- app/: backend e regras de negocio
- frontend/: painel web
- tests/: testes automatizados
- agent/: modulo de assistente local

## Executando localmente

### 1) Backend

1. Criar e ativar ambiente virtual
2. Instalar dependencias com requirements.txt
3. Subir API

Comandos (Windows PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Documentacao interativa da API:
- http://127.0.0.1:8000/docs

### 2) Frontend

Comandos:

```powershell
cd frontend
npm install
npm run dev
```

Aplicacao web:
- http://localhost:5173

## Endpoints principais (alto nivel)

- /api/v1/auth
- /api/v1/customers
- /api/v1/professionals
- /api/v1/working-hours
- /api/v1/schedule
- /api/v1/company-admin
- /api/v1/dashboard/insights

## Qualidade

Rodar testes:

```powershell
pytest -q
```

Build do frontend:

```powershell
cd frontend
npm run build
```

## Licenca

MIT
