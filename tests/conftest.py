import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("SECRET_KEY", "test-secret-key")

# Engine in-memory compartilhado por todas as conexões (incluindo threads do ASGI)
_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def pytest_configure(config):
    """Registra o override de get_db assim que o pytest inicializa."""
    from app.database.session import Base, get_db
    from app.main import app

    Base.metadata.create_all(bind=_test_engine)
    app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """Recria o schema antes de cada teste."""
    from app.database.session import Base

    Base.metadata.drop_all(bind=_test_engine)
    Base.metadata.create_all(bind=_test_engine)