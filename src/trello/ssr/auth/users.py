from sqlmodel import Session, select

from trello.database import SessionRecord, UserRecord, engine
from trello.ssr.auth.passwords import hash_password


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
