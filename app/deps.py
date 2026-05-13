from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)


def require_auth(user: User | None):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт заблокирован")


def require_admin(user: User | None):
    require_auth(user)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


def require_editor_or_admin(user: User | None):
    require_auth(user)
    if user.role not in ("editor", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
