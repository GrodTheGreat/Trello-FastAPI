import hashlib
import pathlib
from dataclasses import dataclass
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from trello.adaptors.users.repository import UserRepository, create_user
from trello.database import get_db

from .csrf import create_csrf, set_csrf_cookie, verify_csrf
from .exceptions import (
    EmailConflictException,
    LoginFailureException,
    PasswordMismatchException,
    UsernameConflictException,
)
from .passwords import is_correct_password
from .schemas import SignInFormData, SignUpFormData
from .sessions import SESSION_KEY, create_session, set_session_cookie

TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"

auth_router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@dataclass
class CurrentUser:
    user_id: int


def get_user_repo(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_current_user(
    request: Request,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> CurrentUser | None:
    token = request.cookies.get(SESSION_KEY)
    if token is None:
        return None
    session_hash = hashlib.sha256(token.encode()).hexdigest()
    user = user_repo.get_by_session(session_hash)
    return CurrentUser(user_id=user.id) if user else None  # type: ignore


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


@auth_router.post("/sign-out", dependencies=[Depends(verify_csrf)])
async def sign_out(request: Request, response: Response):
    raise NotImplementedError()


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
        request, "public.html", {"current_user": current_user}
    )


@auth_router.get("/protected", dependencies=[Depends(require_auth)])
async def get_protected(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "protected.html")
