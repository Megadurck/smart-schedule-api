from sqlalchemy.orm import Session

from app.models.user import User


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_name(db: Session, name: str, company_id: int) -> User | None:
    return (
        db.query(User)
        .filter(User.name == name, User.company_id == company_id)
        .first()
    )


def create_user(
    db: Session,
    name: str,
    company_id: int,
    password_hash: str | None = None,
) -> User:
    user = User(name=name, company_id=company_id, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_user_password(db: Session, user: User, password_hash: str) -> User:
    user.password_hash = password_hash
    db.commit()
    db.refresh(user)
    return user
