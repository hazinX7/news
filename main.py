from __future__ import annotations

from datetime import datetime
from pathlib import Path
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, ValidationError
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from starlette.middleware.sessions import SessionMiddleware


BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = "sqlite:///./news.db"


class Base(DeclarativeBase):
    pass


class Role:
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(16), default=Role.USER)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    news: Mapped[list[News]] = relationship(back_populates="author")
    comments: Mapped[list[Comment]] = relationship(back_populates="author")


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), index=True)
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author: Mapped[User] = relationship(back_populates="news")
    comments: Mapped[list[Comment]] = relationship(back_populates="news", cascade="all, delete-orphan")
    reactions: Mapped[list[Reaction]] = relationship(back_populates="news", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    news: Mapped[News] = relationship(back_populates="comments")
    author: Mapped[User] = relationship(back_populates="comments")


class Reaction(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("news_id", "user_id", name="uniq_news_user_reaction"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    value: Mapped[int] = mapped_column(Integer)  # 1 like, -1 dislike

    news: Mapped[News] = relationship(back_populates="reactions")


engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

app = FastAPI(title="Лента Дня")
app.add_middleware(SessionMiddleware, secret_key="change-me-in-production")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class RegisterForm(BaseModel):
    name: str
    email: EmailStr
    password: str


def sha256(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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
    if user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


def redirect(path: str) -> RedirectResponse:
    return RedirectResponse(url=path, status_code=status.HTTP_303_SEE_OTHER)


def render(request: Request, template: str, context: dict):
    context["request"] = request
    context["current_user"] = get_current_user(request, context["db"])
    return templates.TemplateResponse(request, template, context)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@lentadnya.local").first()
        if not admin:
            db.add(
                User(
                    name="Администратор",
                    email="admin@lentadnya.local",
                    password_hash=sha256("admin123"),
                    role=Role.ADMIN,
                )
            )
            db.commit()
    finally:
        db.close()


@app.get("/")
def index(request: Request, q: str = "", db: Session = Depends(get_db)):
    query = db.query(News).filter(News.is_published.is_(True))
    if q.strip():
        pattern = f"%{q.strip()}%"
        query = query.filter((News.title.ilike(pattern)) | (News.content.ilike(pattern)))
    rows = query.order_by(News.created_at.desc()).all()

    rating_subq = (
        db.query(Reaction.news_id, func.coalesce(func.sum(Reaction.value), 0).label("rating"))
        .group_by(Reaction.news_id)
        .subquery()
    )
    ratings = {
        row.news_id: row.rating
        for row in db.query(rating_subq.c.news_id, rating_subq.c.rating).all()
    }

    return render(
        request,
        "index.html",
        {"db": db, "news": rows, "q": q, "ratings": ratings},
    )


@app.get("/news/{news_id}")
def news_detail(news_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(News, news_id)
    if not item or not item.is_published:
        raise HTTPException(status_code=404)
    comments = (
        db.query(Comment)
        .filter(Comment.news_id == news_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    rating = db.query(func.coalesce(func.sum(Reaction.value), 0)).filter(Reaction.news_id == news_id).scalar()
    return render(
        request,
        "news_detail.html",
        {"db": db, "item": item, "comments": comments, "rating": int(rating or 0)},
    )


@app.post("/news/{news_id}/react")
def react(news_id: int, request: Request, value: int = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_auth(user)
    if value not in (1, -1):
        raise HTTPException(status_code=400)
    if not db.get(News, news_id):
        raise HTTPException(status_code=404)
    record = db.query(Reaction).filter(Reaction.news_id == news_id, Reaction.user_id == user.id).first()
    if record:
        record.value = value
    else:
        db.add(Reaction(news_id=news_id, user_id=user.id, value=value))
    db.commit()
    return redirect(f"/news/{news_id}")


@app.post("/news/{news_id}/comment")
def add_comment(news_id: int, request: Request, body: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_auth(user)
    text = body.strip()
    if len(text) < 2:
        raise HTTPException(status_code=400, detail="Комментарий слишком короткий")
    if not db.get(News, news_id):
        raise HTTPException(status_code=404)
    db.add(Comment(body=text, news_id=news_id, author_id=user.id))
    db.commit()
    return redirect(f"/news/{news_id}")


@app.post("/comments/{comment_id}/delete")
def delete_comment(comment_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_auth(user)
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404)
    if user.role != Role.ADMIN and comment.author_id != user.id:
        raise HTTPException(status_code=403)
    news_id = comment.news_id
    db.delete(comment)
    db.commit()
    return redirect(f"/news/{news_id}")


@app.get("/auth/register")
def register_page(request: Request, db: Session = Depends(get_db)):
    return render(request, "register.html", {"db": db, "error": None})


@app.post("/auth/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        form = RegisterForm(name=name.strip(), email=email.strip(), password=password)
    except ValidationError:
        return render(request, "register.html", {"db": db, "error": "Проверьте корректность e-mail"})

    if len(form.name) < 2 or len(password) < 6:
        return render(
            request,
            "register.html",
            {"db": db, "error": "Имя от 2 символов, пароль от 6 символов"},
        )
    if db.query(User).filter(User.email == form.email).first():
        return render(request, "register.html", {"db": db, "error": "Пользователь уже существует"})

    user = User(name=form.name, email=form.email, password_hash=sha256(password), role=Role.USER)
    db.add(user)
    db.commit()
    request.session["user_id"] = user.id
    return redirect("/")


@app.get("/auth/login")
def login_page(request: Request, db: Session = Depends(get_db)):
    return render(request, "login.html", {"db": db, "error": None})


@app.post("/auth/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or user.password_hash != sha256(password):
        return render(request, "login.html", {"db": db, "error": "Неверный логин или пароль"})
    if user.is_blocked:
        return render(request, "login.html", {"db": db, "error": "Аккаунт заблокирован"})
    request.session["user_id"] = user.id
    return redirect("/")


@app.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return redirect("/")


@app.get("/admin")
def admin_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_admin(user)
    return render(
        request,
        "admin.html",
        {
            "db": db,
            "users": db.query(User).order_by(User.created_at.desc()).all(),
            "news": db.query(News).order_by(News.created_at.desc()).all(),
            "comments": db.query(Comment).order_by(Comment.created_at.desc()).limit(50).all(),
        },
    )


@app.post("/admin/news/create")
def admin_news_create(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    is_published: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    require_admin(user)
    if len(title.strip()) < 5 or len(content.strip()) < 20:
        raise HTTPException(status_code=400, detail="Слишком короткая новость")
    db.add(
        News(
            title=title.strip(),
            content=content.strip(),
            author_id=user.id,
            is_published=bool(is_published),
        )
    )
    db.commit()
    return redirect("/admin")


@app.post("/admin/news/{news_id}/edit")
def admin_news_edit(
    news_id: int,
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    is_published: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    require_admin(user)
    item = db.get(News, news_id)
    if not item:
        raise HTTPException(status_code=404)
    item.title = title.strip()
    item.content = content.strip()
    item.is_published = bool(is_published)
    db.commit()
    return redirect("/admin")


@app.post("/admin/news/{news_id}/delete")
def admin_news_delete(news_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_admin(user)
    item = db.get(News, news_id)
    if item:
        db.delete(item)
        db.commit()
    return redirect("/admin")


@app.post("/admin/users/{user_id}/toggle-block")
def admin_toggle_block(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_admin(user)
    target = db.get(User, user_id)
    if not target or target.role == Role.ADMIN:
        return redirect("/admin")
    target.is_blocked = not target.is_blocked
    db.commit()
    return redirect("/admin")


@app.post("/admin/users/{user_id}/delete")
def admin_delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_admin(user)
    target = db.get(User, user_id)
    if target and target.role != Role.ADMIN:
        db.delete(target)
        db.commit()
    return redirect("/admin")


@app.post("/admin/comments/{comment_id}/delete")
def admin_delete_comment(comment_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_admin(user)
    comment = db.get(Comment, comment_id)
    if comment:
        db.delete(comment)
        db.commit()
    return redirect("/admin")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
