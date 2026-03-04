from dataclasses import dataclass
from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import Session

from trello.authorization import BoardPolicy, CardPolicy, ListPolicy
from trello.boards import BoardRepository
from trello.cards import CardRepository
from trello.database import engine
from trello.lists import ListRepository


@dataclass(frozen=True)
class OptionalUser:
    id: int = 1


def get_user() -> OptionalUser:
    return OptionalUser()


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_board_policy(db: Annotated[Session, Depends(get_db)]) -> BoardPolicy:
    return BoardPolicy(db)


def get_board_repo(db: Annotated[Session, Depends(get_db)]) -> BoardRepository:
    return BoardRepository(db)


def get_card_policy(db: Annotated[Session, Depends(get_db)]) -> CardPolicy:
    return CardPolicy(db)


def get_card_repo(db: Annotated[Session, Depends(get_db)]) -> CardRepository:
    return CardRepository(db)


def get_list_policy(db: Annotated[Session, Depends(get_db)]) -> ListPolicy:
    return ListPolicy(db)


def get_list_repo(db: Annotated[Session, Depends(get_db)]) -> ListRepository:
    return ListRepository(db)
