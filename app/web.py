from fastapi import Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.deps import get_current_user


templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def redirect(path: str) -> RedirectResponse:
    return RedirectResponse(url=path, status_code=status.HTTP_303_SEE_OTHER)


def render(request: Request, template: str, context: dict):
    context["request"] = request
    context["current_user"] = get_current_user(request, context["db"])
    return templates.TemplateResponse(request, template, context)

