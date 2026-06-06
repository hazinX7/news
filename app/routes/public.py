from datetime import datetime, time

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, require_auth
from app.models import Comment, CommentReaction, News, Reaction
from app.web import redirect, render


router = APIRouter()


def build_reaction_counts(db: Session):
    likes = func.sum(case((Reaction.value == 1, 1), else_=0)).label("likes")
    dislikes = func.sum(case((Reaction.value == -1, 1), else_=0)).label("dislikes")
    rows = db.query(Reaction.news_id, likes, dislikes).group_by(Reaction.news_id).all()
    return {row.news_id: {"likes": int(row.likes or 0), "dislikes": int(row.dislikes or 0)} for row in rows}


def build_comment_reaction_counts(db: Session, comment_ids: list[int]):
    if not comment_ids:
        return {}
    likes = func.sum(case((CommentReaction.value == 1, 1), else_=0)).label("likes")
    dislikes = func.sum(case((CommentReaction.value == -1, 1), else_=0)).label("dislikes")
    rows = (
        db.query(CommentReaction.comment_id, likes, dislikes)
        .filter(CommentReaction.comment_id.in_(comment_ids))
        .group_by(CommentReaction.comment_id)
        .all()
    )
    return {row.comment_id: {"likes": int(row.likes or 0), "dislikes": int(row.dislikes or 0)} for row in rows}


def parse_date_start(value: str | None):
    if not value:
        return None
    try:
        return datetime.combine(datetime.fromisoformat(value).date(), time.min)
    except ValueError:
        return None


def parse_date_end(value: str | None):
    if not value:
        return None
    try:
        return datetime.combine(datetime.fromisoformat(value).date(), time.max)
    except ValueError:
        return None


@router.get("/")
def index(
    request: Request,
    q: str = "",
    date_from: str = "",
    date_to: str = "",
    sort: str = "newest",
    db: Session = Depends(get_db),
):
    query = db.query(News).filter(News.is_published.is_(True))
    if q.strip():
        pattern = f"%{q.strip()}%"
        query = query.filter((News.title.ilike(pattern)) | (News.content.ilike(pattern)))
    parsed_date_from = parse_date_start(date_from)
    parsed_date_to = parse_date_end(date_to)
    if parsed_date_from:
        query = query.filter(News.created_at >= parsed_date_from)
    if parsed_date_to:
        query = query.filter(News.created_at <= parsed_date_to)
    rows = query.order_by(News.created_at.desc()).all()

    reactions = build_reaction_counts(db)
    if sort == "oldest":
        rows = sorted(rows, key=lambda item: item.created_at)
    elif sort == "likes":
        rows = sorted(rows, key=lambda item: reactions.get(item.id, {}).get("likes", 0), reverse=True)
    elif sort == "dislikes":
        rows = sorted(rows, key=lambda item: reactions.get(item.id, {}).get("dislikes", 0), reverse=True)

    filters = {
        "q": q,
        "date_from": date_from,
        "date_to": date_to,
        "sort": sort,
    }

    return render(
        request,
        "index.html",
        {"db": db, "news": rows, "q": q, "reactions": reactions, "filters": filters},
    )


@router.get("/news/{news_id}")
def news_detail(news_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.get(News, news_id)
    if not item or not item.is_published:
        raise HTTPException(status_code=404)
    comments = db.query(Comment).filter(Comment.news_id == news_id).order_by(Comment.created_at.desc()).all()
    reactions = build_reaction_counts(db).get(news_id, {"likes": 0, "dislikes": 0})
    comment_reactions = build_comment_reaction_counts(db, [c.id for c in comments])
    return render(
        request,
        "news_detail.html",
        {
            "db": db,
            "item": item,
            "comments": comments,
            "reactions": reactions,
            "comment_reactions": comment_reactions,
        },
    )


@router.patch("/news/{news_id}/react")
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


@router.post("/news/{news_id}/comment")
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


@router.patch("/comments/{comment_id}/react")
def react_comment(comment_id: int, request: Request, value: int = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_auth(user)
    if value not in (1, -1):
        raise HTTPException(status_code=400)
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404)
    record = db.query(CommentReaction).filter(CommentReaction.comment_id == comment_id, CommentReaction.user_id == user.id).first()
    if record:
        record.value = value
    else:
        db.add(CommentReaction(comment_id=comment_id, user_id=user.id, value=value))
    db.commit()
    return redirect(f"/news/{comment.news_id}")


@router.delete("/comments/{comment_id}/delete")
def delete_comment(comment_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    require_auth(user)
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404)
    if user.role != "admin" and comment.author_id != user.id:
        raise HTTPException(status_code=403)
    news_id = comment.news_id
    db.delete(comment)
    db.commit()
    return redirect(f"/news/{news_id}")
