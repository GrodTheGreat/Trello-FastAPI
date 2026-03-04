from dataclasses import dataclass
from typing import Generator

from sqlmodel import Session

from trello.database import engine


@dataclass(frozen=True)
class OptionalUser:
    id: int = 1


def get_user() -> OptionalUser:
    return OptionalUser()


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
