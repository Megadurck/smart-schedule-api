"""Script para resetar o banco de dados"""
from app.database.session import engine, Base
from sqlalchemy import text

def reset_database():
    """Drop todas as tabelas e recria com o novo schema"""
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        
        # Drop all tables
        conn.execute(text("DROP TABLE IF EXISTS schedules"))
        conn.execute(text("DROP TABLE IF EXISTS customers"))
        conn.execute(text("DROP TABLE IF EXISTS professionals"))
        conn.execute(text("DROP TABLE IF EXISTS users"))
        conn.execute(text("DROP TABLE IF EXISTS companies"))
        conn.execute(text("DROP TABLE IF EXISTS working_hours"))
        
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()
    
    # Recria as tabelas
    Base.metadata.create_all(bind=engine)
    print("✅ Banco resetado com sucesso!")

if __name__ == "__main__":
    reset_database()
