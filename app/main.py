from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from app.api.v1 import api_router

from app.database.session import engine, Base, ensure_auth_columns
from app.models.client import Client
from app.models.shedule_model import Schedule
from app.models.working_hours_model import WorkingHours

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Criar tabelas do banco
    Base.metadata.create_all(bind=engine)
    ensure_auth_columns()
    yield
    # Shutdown: (nada por enquanto)

app = FastAPI(title="Smart Schedule API", lifespan=lifespan)

# Redireciona a raiz "/" para a documentação automática do Swagger
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

app.include_router(api_router, prefix="/api/v1")