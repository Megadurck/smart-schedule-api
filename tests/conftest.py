import os

import pytest
from sqlalchemy import text
from app.database.session import engine

os.environ.setdefault("SECRET_KEY", "test-secret-key")

@pytest.fixture(scope="function", autouse=True)
def clean_database():
    # Limpar tabelas antes de cada teste
    with engine.connect() as conn:
        # Desabilitar foreign keys para SQLite
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        # Deletar em ordem reversa de dependências
        conn.execute(text("DELETE FROM schedules"))
        conn.execute(text("DELETE FROM clients"))
        conn.execute(text("DELETE FROM working_hours"))
        # Reabilitar
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()