import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from app.api.v1 import api_router

from app.database.session import (
    engine,
    Base,
    ensure_company_admin_columns,
    ensure_schedule_constraints,
)
from agent.whatsapp_client import start_neonize_listener, stop_neonize_listener
from app.models.company import Company
from app.models.customer import Customer
from app.models.professional import Professional
from app.models.schedule_model import Schedule
from app.models.user import User
from app.models.working_hours_model import WorkingHours

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Criar tabelas do banco
    Base.metadata.create_all(bind=engine)
    ensure_company_admin_columns()
    ensure_schedule_constraints()

    if os.getenv("WHATSAPP_PROVIDER", "neonize").strip().lower() == "neonize":
        start_neonize_listener()

    yield

    if os.getenv("WHATSAPP_PROVIDER", "neonize").strip().lower() == "neonize":
        stop_neonize_listener()

app = FastAPI(title="Smart Schedule API", lifespan=lifespan)

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redireciona a raiz "/" para a documentação automática do Swagger
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

app.include_router(api_router, prefix="/api/v1")