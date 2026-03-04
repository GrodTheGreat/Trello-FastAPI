from fastapi import HTTPException, status

from trello.api.schemas import BaseSchema
from trello.database import CardRecord


class CardSchema(BaseSchema):
    id: int
    list_id: int
    name: str
    position: float


class CardResponse(BaseSchema):
    card: CardSchema


class CardsResponse(BaseSchema):
    cards: list[CardSchema]


def card_record_to_schema(card: CardRecord) -> CardSchema:
    if card.id is None or card.list_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return CardSchema(
        id=card.id,
        list_id=card.list_id,
        name=card.name,
        position=card.position,
    )
