from sqlmodel import Session, select

from trello.database import SessionRecord, UserRecord, engine
from trello.ssr.auth.passwords import hash_password


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def get(self, user_id: int) -> UserRecord | None:
        statement = select(UserRecord).where(UserRecord.id == user_id).limit(1)
        return self._db.exec(statement).first()

    def get_email(self, email: str) -> UserRecord | None:
        statement = select(UserRecord).where(UserRecord.email == email).limit(1)
        user = self._db.exec(statement).first()
        return user

    def get_by_session(self, session_hash: str) -> UserRecord | None:
        statement = (
            select(UserRecord)
            .join(SessionRecord)
            .where(SessionRecord.session_hash == session_hash)
            .limit(1)
        )
        user = self._db.exec(statement).first()
        return user

    def get_by_username(self, username: str) -> UserRecord | None:
        statement = select(UserRecord).where(UserRecord.username == username).limit(1)
        user = self._db.exec(statement).first()
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
