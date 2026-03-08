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

from trello.ssr.auth.csrf import create_csrf, set_csrf_cookie, verify_csrf
from trello.ssr.auth.passwords import is_correct_password
from trello.ssr.auth.schemas import SignInFormData, SignUpFormData
from trello.ssr.auth.sessions import SESSION_KEY, create_session, set_session_cookie
from trello.ssr.auth.users import (
    create_user,
    get_user_by_email,
    get_user_by_session,
    get_user_by_username,
)

TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"

auth_router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def require_auth(request: Request):
    current_user = get_current_user(request)
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@dataclass
class CurrentUser:
    user_id: int


def get_current_user(request: Request) -> CurrentUser | None:
    token = request.cookies.get(SESSION_KEY)
    if token is None:
        return None
    session_hash = hashlib.sha256(token.encode()).hexdigest()
    user = get_user_by_session(session_hash)
    return CurrentUser(user_id=user.id) if user else None  # type: ignore


@auth_router.get("/sign-in")
async def get_sign_in(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "sign-in.html")


@auth_router.post("/sign-in")
async def sign_in(
    request: Request,
    response: Response,
    data: Annotated[SignInFormData, Form()],
) -> RedirectResponse:
    user = get_user_by_email(data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid email/password combination",
        )
    if not is_correct_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid email/password combination",
        )
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
async def get_sign_up(request: Request, response: Response) -> HTMLResponse:
    return templates.TemplateResponse(request, "sign-up.html")


@auth_router.post("/sign-up")
async def sign_up(
    request: Request,
    response: Response,
    data: Annotated[SignUpFormData, Form()],
) -> RedirectResponse:
    if data.password != data.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="passwords don't match",
        )
    existing_user = get_user_by_email(data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with this email already exists",
        )
    existing_user = get_user_by_username(data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with this username already exists",
        )
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
    response: Response,
    current_user: Annotated[CurrentUser | None, Depends(get_current_user)],
) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "public.html", {"current_user": current_user}
    )


@auth_router.get("/protected", dependencies=[Depends(require_auth)])
async def get_protected(request: Request, response: Response) -> HTMLResponse:
    return templates.TemplateResponse(request, "protected.html")
