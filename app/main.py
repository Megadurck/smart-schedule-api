from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1 import api_router

from app.database.session import engine, Base
from app.models.client import Client
from app.models.shedule_model import Schedule
from app.models.working_hours_model import WorkingHours

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Criar tabelas do banco
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: (nada por enquanto)

app = FastAPI(title="Smart Schedule API", lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")