from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from trello.adapters.boards.repository import BoardRepository
from trello.api.dependencies import get_db
from trello.authorization import BoardPolicy


def get_board_policy(db: Annotated[Session, Depends(get_db)]) -> BoardPolicy:
    return BoardPolicy(db)


def get_board_repo(db: Annotated[Session, Depends(get_db)]) -> BoardRepository:
    return BoardRepository(db)
