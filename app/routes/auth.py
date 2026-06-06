from fastapi import APIRouter, Depends, Form, Request
from pydantic import ValidationError
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import User
from app.schemas import RegisterForm
from app.security import sha256
from app.web import redirect, render


router = APIRouter(prefix="/auth")


def contains_cyrillic(value: str) -> bool:
    return any("а" <= char.lower() <= "я" or char.lower() == "ё" for char in value)


@router.get("/register")
def register_page(request: Request, db: Session = Depends(get_db)):
    return render(request, "register.html", {"db": db, "error": None})


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    clean_name = name.strip()
    clean_email = email.strip().lower()

    if contains_cyrillic(clean_name):
        return render(request, "register.html", {"db": db, "error": "Имя пользователя не должно содержать русские символы"})
    if contains_cyrillic(clean_email):
        return render(request, "register.html", {"db": db, "error": "E-mail не должен содержать русские символы"})

    if clean_email and db.query(User).filter(func.lower(User.email) == clean_email).first():
        return render(request, "register.html", {"db": db, "error": "Пользователь с таким email уже существует в системе"})
    if clean_name and db.query(User).filter(func.lower(User.name) == clean_name.lower()).first():
        return render(request, "register.html", {"db": db, "error": "Пользователь с таким username уже существует в системе"})

    if len(clean_name) < 2:
        return render(request, "register.html", {"db": db, "error": "Имя пользователя должно быть от 2 символов"})
    if len(password) < 6:
        return render(request, "register.html", {"db": db, "error": "Пароль должен быть от 6 символов"})

    try:
        form = RegisterForm(name=clean_name, email=clean_email, password=password)
    except ValidationError:
        return render(request, "register.html", {"db": db, "error": "Проверьте корректность e-mail"})

    user = User(name=form.name, email=form.email, password_hash=sha256(password), role="user")
    db.add(user)
    db.commit()
    request.session["user_id"] = user.id
    return redirect("/")


@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db)):
    return render(request, "login.html", {"db": db, "error": None})


@router.post("/login")
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


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return redirect("/")
