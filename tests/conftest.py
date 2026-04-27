import os

import pytest
from app.database.session import Base, engine

os.environ.setdefault("SECRET_KEY", "test-secret-key")

@pytest.fixture(scope="function", autouse=True)
def clean_database():
    # Recria schema completo em cada teste para garantir compatibilidade
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)