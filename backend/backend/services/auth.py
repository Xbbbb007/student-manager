from sqlalchemy.orm import Session
from ..models.user import User
from ..core.security import hash_password, verify_password, create_access_token


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def create_user(db: Session, username: str, password: str, name: str, role: str) -> User:
    user = User(
        username=username,
        password_hash=hash_password(password),
        name=name,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def init_admin(db: Session):
    """Create default admin if not exists"""
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        create_user(db, "admin", "admin123", "系统管理员", "admin")
