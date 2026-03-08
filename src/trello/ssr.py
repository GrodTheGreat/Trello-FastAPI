import hashlib
import hmac
import os
import pathlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Annotated

from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import Session, select

from trello.database import SessionRecord, UserRecord, engine
from trello.passwords import hash_password, is_correct_password

load_dotenv()

ssr_router = APIRouter()

env = os.getenv("ENVIRONMENT", "development")

BASE_DIR = pathlib.Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
IS_PROD = env == "production"
MAX_AGE = 60 * 5  # 5 min for testing
CSRF_NBYTES = 32
CSRF_KEY = "Trello-CSRF-Token"
SESSION_KEY = "Trello-Session"
SESSION_NBYTES = 64
SEPARATOR = "."
SIGNING_SECRET = "super-secret-key"
X_CSRF_KEY = "Request-Trello-CSRF-Token"

templates = Jinja2Templates(directory=TEMPLATES_DIR)


class SignInFormData(BaseModel):
    email: str
    password: str


class SignUpFormData(BaseModel):
    email: str
    username: str
    password: str
    confirm: str


def verify_csrf(
    cookie: Annotated[str, Cookie(alias=CSRF_KEY)],
    header: Annotated[str, Header(alias=X_CSRF_KEY)],
):
    if cookie is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if header is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if cookie != header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    if not is_valid_csrf(cookie):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


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


@ssr_router.get("/sign-in")
async def get_sign_in(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "sign-in.html")


@ssr_router.post("/sign-in")
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


@ssr_router.post("/sign-out", dependencies=[Depends(verify_csrf)])
async def sign_out(request: Request, response: Response):
    raise NotImplementedError()


@ssr_router.get("/sign-up")
async def get_sign_up(request: Request, response: Response) -> HTMLResponse:
    return templates.TemplateResponse(request, "sign-up.html")


@ssr_router.post("/sign-up")
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


@ssr_router.get("/public")
async def get_public(
    request: Request,
    response: Response,
    current_user: Annotated[CurrentUser | None, Depends(get_current_user)],
) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "public.html", {"current_user": current_user}
    )


@ssr_router.get("/protected", dependencies=[Depends(require_auth)])
async def get_protected(request: Request, response: Response) -> HTMLResponse:
    return templates.TemplateResponse(request, "protected.html")


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_KEY,
        value=token,
        max_age=MAX_AGE,
        secure=IS_PROD,
        httponly=True,
    )


def set_csrf_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=CSRF_KEY,
        value=token,
        max_age=MAX_AGE,
        secure=IS_PROD,
        httponly=False,
    )


def get_user(user_id: int) -> UserRecord | None:
    with Session(engine) as db:
        statement = select(UserRecord).where(UserRecord.id == user_id).limit(1)
        user = db.exec(statement).first()
    return user


def get_user_by_email(email: str) -> UserRecord | None:
    with Session(engine) as db:
        statement = select(UserRecord).where(UserRecord.email == email).limit(1)
        user = db.exec(statement).first()
    return user


def get_user_by_username(username: str) -> UserRecord | None:
    with Session(engine) as db:
        statement = select(UserRecord).where(UserRecord.username == username).limit(1)
        user = db.exec(statement).first()
    return user


def get_user_by_session(session_hash: str) -> UserRecord | None:
    with Session(engine) as db:
        statement = (
            select(UserRecord)
            .join(SessionRecord)
            .where(SessionRecord.session_hash == session_hash)
            .limit(1)
        )
        user = db.exec(statement).first()
    return user


def create_user(email: str, username: str, password: str) -> UserRecord:
    user = UserRecord(
        email=email,
        username=username,
        password_hash=hash_password(password),
    )
    with Session(engine) as db:
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(SESSION_NBYTES)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expiry = datetime.now(timezone.utc) + timedelta(seconds=MAX_AGE)
    session = SessionRecord(session_hash=token_hash, user_id=user_id, expires_at=expiry)
    with Session(engine) as db:
        db.add(session)
        db.commit()
    return token


def create_csrf() -> str:
    token = secrets.token_urlsafe(CSRF_NBYTES)
    signature = sign_csrf(token)
    return token + SEPARATOR + signature


def sign_csrf(token: str) -> str:
    return hmac.new(
        SIGNING_SECRET.encode(),
        token.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()


def is_valid_csrf(signed: str) -> bool:
    try:
        token, signature = signed.rsplit(SEPARATOR, maxsplit=1)
    except ValueError:
        return False
    expected = sign_csrf(token)
    return signature == expected
