import time
import uuid
from dataclasses import dataclass
from typing import Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from sqlmodel import Session

from trello.adapters.users.repository import UserRepository
from trello.api.router import api_router
from trello.database import engine
from trello.exceptions import NotFoundException
from trello.ssr.auth.exceptions import (
    EmailConflictException,
    LoginFailureException,
    PasswordMismatchException,
    UsernameConflictException,
)
from trello.ssr.auth.sessions import SESSION_KEY, hash_session
from trello.ssr.router import ssr_router

app = FastAPI()


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(_: Request, exc: NotFoundException):
    return JSONResponse(
        content={"message": exc.message},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.exception_handler(PasswordMismatchException)
async def password_mismatch_exception_handler(
    _: Request, exc: PasswordMismatchException
):
    return JSONResponse(
        content={"message": "passwords don't match"},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.exception_handler(EmailConflictException)
async def email_conflict_exception_handler(
    _: Request, exc: EmailConflictException
) -> JSONResponse:
    return JSONResponse(
        content={"message": "user with this email already exists"},
        status_code=status.HTTP_409_CONFLICT,
    )


@app.exception_handler(LoginFailureException)
async def login_failure_exception_handler(
    _: Request, exc: LoginFailureException
) -> JSONResponse:
    return JSONResponse(
        content={"message": "invalid email/password combination"},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.exception_handler(UsernameConflictException)
async def username_conflict_exception_handler(
    _: Request, exc: UsernameConflictException
) -> JSONResponse:
    return JSONResponse(
        content={"message": "user with this username already exists"},
        status_code=status.HTTP_409_CONFLICT,
    )


@app.exception_handler(Exception)
async def internal_server_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        content={"message": "an unexpected error occurred"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@dataclass
class CurrentUser:
    user_id: int


@app.middleware("http")
async def get_current_user_middleware(request: Request, call_next: Callable):
    current_user = None
    session = request.cookies.get(SESSION_KEY)
    if session is not None:
        session_hash = hash_session(session)
        with Session(engine) as db:
            user_repo = UserRepository(db)
            user = user_repo.get_by_session(session_hash)
            if user is not None:
                current_user = CurrentUser(user_id=user.id)  # type: ignore
    request.state.user = current_user
    return await call_next(request)


@app.middleware("http")
async def time_request_middleware(request: Request, call_next: Callable):
    start_time = time.perf_counter()
    response: Response = await call_next(request)
    time_taken = time.perf_counter() - start_time
    response.headers["Trello-Process-Time"] = str(time_taken)
    return response


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next: Callable):
    request_id = uuid.uuid4()
    request.state.request_id = request_id
    response: Response = await call_next(request)
    response.headers["Trello-Request-Id"] = str(request_id)
    return response


app.include_router(ssr_router, prefix="")
app.include_router(api_router, prefix="/api")
