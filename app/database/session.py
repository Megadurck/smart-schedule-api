from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# URL do banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./smart_schedule.db"

# Cria o engine do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necessário apenas para SQLite
)

# Cria uma classe SessionLocal para gerenciar sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

_auth_columns_checked = False

# Função para obter uma sessão de banco de dados
def get_db():
    global _auth_columns_checked
    if not _auth_columns_checked:
        ensure_auth_columns()
        _auth_columns_checked = True

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_auth_columns():
    """Garante colunas de autenticação em bases SQLite já existentes."""
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if "clients" not in table_names:
        return

    columns = {column["name"] for column in inspector.get_columns("clients")}
    if "password_hash" in columns:
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE clients ADD COLUMN password_hash VARCHAR"))