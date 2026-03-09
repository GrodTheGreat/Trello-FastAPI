import pathlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Annotated

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from trello.adapters.users.repository import UserRepository, create_user
from trello.api.dependencies import get_db
from trello.database import SessionRecord, engine

from .csrf import CSRF_KEY, create_csrf, set_csrf_cookie, verify_csrf
from .exceptions import (
    EmailConflictException,
    LoginFailureException,
    PasswordMismatchException,
    UsernameConflictException,
)
from .passwords import is_correct_password
from .schemas import SignInFormData, SignUpFormData
from .sessions import SESSION_KEY, create_session, hash_session, set_session_cookie

TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"

auth_router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def get_user_repo(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


@dataclass
class CurrentUser:
    user_id: int


def get_current_user(request: Request) -> CurrentUser | None:
    return request.state.user


def require_auth(
    current_user: Annotated[CurrentUser | None, Depends(get_current_user)],
):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@auth_router.get("/sign-in")
async def get_sign_in(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "sign-in.html")


@auth_router.post("/sign-in")
async def sign_in(
    data: Annotated[SignInFormData, Form()],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> RedirectResponse:
    user = user_repo.get_email(data.email)
    if user is None or not is_correct_password(data.password, user.password_hash):
        raise LoginFailureException()
    session = create_session(user.id)  # type: ignore
    csrf = create_csrf()
    redirect = RedirectResponse(url="/protected", status_code=status.HTTP_303_SEE_OTHER)
    set_session_cookie(redirect, session)
    set_csrf_cookie(redirect, csrf)
    return redirect


@auth_router.get("/sign-out", dependencies=[Depends(require_auth)])
async def get_sign_out(request: Request, response: Response) -> HTMLResponse:
    return templates.TemplateResponse(request, "sign-out.html")


@auth_router.post(
    "/sign-out", dependencies=[Depends(verify_csrf), Depends(require_auth)]
)
async def sign_out(
    request: Request,
    response: Response,
    token: Annotated[str, Cookie(alias=SESSION_KEY)],
):
    session_hash = hash_session(token)
    now = datetime.now(timezone.utc)
    with Session(engine) as db:
        statement = (
            select(SessionRecord)
            .where(
                SessionRecord.session_hash == session_hash,
                SessionRecord.expires_at > now,
                SessionRecord.revoked_at == None,  # noqa: E711
            )
            .limit(1)
        )
        session = db.exec(statement).first()
        if session:
            session.revoked_at = now
            db.commit()
    redirect = RedirectResponse(url="/public", status_code=status.HTTP_303_SEE_OTHER)
    redirect.delete_cookie(SESSION_KEY, httponly=True)
    redirect.delete_cookie(CSRF_KEY, httponly=False)
    return redirect


@auth_router.get("/sign-up")
async def get_sign_up(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "sign-up.html")


@auth_router.post("/sign-up")
async def sign_up(
    data: Annotated[SignUpFormData, Form()],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> RedirectResponse:
    if data.password != data.confirm:
        raise PasswordMismatchException()
    existing_user = user_repo.get_email(data.email)
    if existing_user:
        raise EmailConflictException()
    existing_user = user_repo.get_by_username(data.username)
    if existing_user:
        raise UsernameConflictException()
    user = create_user(data.email, data.username, data.password)
    session = create_session(user.id)  # type: ignore
    csrf = create_csrf()
    redirect = RedirectResponse(url="/protected", status_code=status.HTTP_303_SEE_OTHER)
    set_session_cookie(redirect, session)
    set_csrf_cookie(redirect, csrf)
    return redirect


@auth_router.get("/public")
async def get_public(
    request: Request,
    current_user: Annotated[CurrentUser | None, Depends(get_current_user)],
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "public.html",
        {"current_user": current_user},
    )


@auth_router.get("/protected", dependencies=[Depends(require_auth)])
async def get_protected(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "protected.html")
