import hashlib
import hmac
import os
import secrets
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Cookie, Header, HTTPException, Response, status

load_dotenv()


env = os.getenv("ENVIRONMENT", "development")

CSRF_NBYTES = 32
CSRF_KEY = "Trello-CSRF-Token"
IS_PROD = env == "production"
MAX_AGE = 60 * 5  # 5 min for testing
REQUEST_CSRF_KEY = "Request-Trello-CSRF-Token"
SEPARATOR = "."
SIGNING_SECRET = "super-secret-key"


def verify_csrf(
    cookie: Annotated[str, Cookie(alias=CSRF_KEY)],
    header: Annotated[str, Header(alias=REQUEST_CSRF_KEY)],
):
    if cookie is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if header is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if cookie != header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    if not is_valid_csrf(cookie):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


def set_csrf_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=CSRF_KEY,
        value=token,
        max_age=MAX_AGE,
        secure=IS_PROD,
        httponly=False,
    )


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
