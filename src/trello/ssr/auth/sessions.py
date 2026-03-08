import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Response
from sqlmodel import Session

from trello.database import SessionRecord, engine

load_dotenv()


env = os.getenv("ENVIRONMENT", "development")
IS_PROD = env == "production"
MAX_AGE = 60 * 5  # 5 min for testing
SESSION_KEY = "Trello-Session"
SESSION_NBYTES = 64


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_KEY,
        value=token,
        max_age=MAX_AGE,
        secure=IS_PROD,
        httponly=True,
    )


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(SESSION_NBYTES)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expiry = datetime.now(timezone.utc) + timedelta(seconds=MAX_AGE)
    session = SessionRecord(session_hash=token_hash, user_id=user_id, expires_at=expiry)
    with Session(engine) as db:
        db.add(session)
        db.commit()
    return token
