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


def get_client_by_name(db: Session, name: str) -> Client | None:
    """Obtém um cliente pelo nome."""
    return db.query(Client).filter(Client.name == name).first()


def create_client(db: Session, name: str, password_hash: str | None = None) -> Client:
    """Cria um cliente com senha opcional."""
    client = Client(name=name, password_hash=password_hash)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def set_client_password(db: Session, client: Client, password_hash: str) -> Client:
    """Define/atualiza a senha de um cliente existente."""
    client.password_hash = password_hash
    db.commit()
    db.refresh(client)
    return client
