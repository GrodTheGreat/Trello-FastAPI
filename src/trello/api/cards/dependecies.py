from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from trello.adaptors.cards.repository import CardRepository
from trello.api.dependencies import get_db
from trello.authorization import CardPolicy


def get_card_policy(db: Annotated[Session, Depends(get_db)]) -> CardPolicy:
    return CardPolicy(db)


def get_card_repo(db: Annotated[Session, Depends(get_db)]) -> CardRepository:
    return CardRepository(db)
