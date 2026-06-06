from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import BASE_DIR, SESSION_SECRET
from app.db import Base, SessionLocal, engine
from app.models import User
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.public import router as public_router
from app.security import sha256


app = FastAPI(title="Лента Дня")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(public_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@lentadnya.local").first()
        if not admin:
            admin = User(email="admin@lentadnya.local")
            db.add(admin)
        admin.name = "admin"
        admin.password_hash = sha256("admin123")
        admin.role = "admin"

        editor = db.query(User).filter(User.email == "editor@lentadnya.local").first()
        if not editor:
            editor = User(email="editor@lentadnya.local")
            db.add(editor)
        editor.name = "editor"
        editor.password_hash = sha256("editor123")
        editor.role = "editor"

        db.commit()
    finally:
        db.close()
