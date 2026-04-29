from sqlalchemy import create_engine
from sqlalchemy import text
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

# Função para obter uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_auth_columns():
    """Mantido por compatibilidade com o bootstrap atual."""
    return None


def ensure_company_admin_columns():
    """Garante colunas administrativas da tabela companies em bases legadas."""
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(companies)")).fetchall()
        existing_columns = {row[1] for row in rows}

        if "display_name" not in existing_columns:
            conn.execute(text("ALTER TABLE companies ADD COLUMN display_name VARCHAR"))
        if "cancellation_policy" not in existing_columns:
            conn.execute(text("ALTER TABLE companies ADD COLUMN cancellation_policy TEXT"))
        if "default_timezone" not in existing_columns:
            conn.execute(
                text(
                    "ALTER TABLE companies ADD COLUMN default_timezone VARCHAR NOT NULL DEFAULT 'America/Sao_Paulo'"
                )
            )
        if "reminder_lead_minutes" not in existing_columns:
            conn.execute(
                text(
                    "ALTER TABLE companies ADD COLUMN reminder_lead_minutes INTEGER NOT NULL DEFAULT 120"
                )
            )