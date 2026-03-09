from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from trello.adapters.lists.repository import ListRepository
from trello.api.dependencies import get_db
from trello.authorization import ListPolicy


def get_list_policy(db: Annotated[Session, Depends(get_db)]) -> ListPolicy:
    return ListPolicy(db)


def get_list_repo(db: Annotated[Session, Depends(get_db)]) -> ListRepository:
    return ListRepository(db)
