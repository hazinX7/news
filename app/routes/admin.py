from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, require_admin, require_editor_or_admin
from app.models import Comment, News, User
from app.web import redirect, render


router = APIRouter(prefix="/admin")


@router.get("")
def admin_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_editor_or_admin(user)
    can_manage_users = user.role == "admin"
    return render(
        request,
        "admin.html",
        {
            "db": db,
            "users": db.query(User).order_by(User.created_at.desc()).all() if can_manage_users else [],
            "news": db.query(News).order_by(News.created_at.desc()).all(),
            "comments": db.query(Comment).order_by(Comment.created_at.desc()).limit(50).all(),
            "can_manage_users": can_manage_users,
            "panel_title": "Панель контента" if user.role == "editor" else "Панель администратора",
        },
    )


@router.post("/news/create")
def admin_news_create(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    is_published: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    require_editor_or_admin(user)
    if len(title.strip()) < 5 or len(content.strip()) < 20:
        raise HTTPException(status_code=400, detail="Слишком короткая новость")
    db.add(News(title=title.strip(), content=content.strip(), author_id=user.id, is_published=bool(is_published)))
    db.commit()
    return redirect("/admin")


@router.post("/news/{news_id}/edit")
def admin_news_edit(
    news_id: int,
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    is_published: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    require_editor_or_admin(user)
    item = db.get(News, news_id)
    if not item:
        raise HTTPException(status_code=404)
    item.title = title.strip()
    item.content = content.strip()
    item.is_published = bool(is_published)
    db.commit()
    return redirect("/admin")


@router.post("/news/{news_id}/delete")
def admin_news_delete(news_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_editor_or_admin(user)
    item = db.get(News, news_id)
    if item:
        db.delete(item)
        db.commit()
    return redirect("/admin")


@router.post("/users/{user_id}/toggle-block")
def admin_toggle_block(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_admin(user)
    target = db.get(User, user_id)
    if not target or target.role == "admin":
        return redirect("/admin")
    target.is_blocked = not target.is_blocked
    db.commit()
    return redirect("/admin")


@router.post("/users/{user_id}/delete")
def admin_delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_admin(user)
    target = db.get(User, user_id)
    if target and target.role != "admin":
        db.delete(target)
        db.commit()
    return redirect("/admin")


@router.post("/comments/{comment_id}/delete")
def admin_delete_comment(comment_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_editor_or_admin(user)
    comment = db.get(Comment, comment_id)
    if comment:
        db.delete(comment)
        db.commit()
    return redirect("/admin")
