from sqlalchemy.orm import Session

from app.models.client import Client


def find_or_create_client(db: Session, name: str) -> Client:
    """Encontra um cliente pelo nome ou cria um novo se não existir."""
    client = db.query(Client).filter(Client.name == name).first()
    if not client:
        client = Client(name=name)
        db.add(client)
        db.commit()
        db.refresh(client)
    return client


def get_client(db: Session, client_id: int) -> Client | None:
    """Obtém um cliente por ID."""
    return db.query(Client).filter(Client.id == client_id).first()


def list_clients(db: Session) -> list[Client]:
    """Lista todos os clientes."""
    return db.query(Client).all()
