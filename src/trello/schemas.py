from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from trello.database import BoardRecord, CardRecord, ListRecord


class BaseSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class BoardSchema(BaseSchema):
    id: int
    creator_id: int
    name: str


class BoardResponse(BaseSchema):
    board: BoardSchema


class ListSchema(BaseSchema):
    id: int
    board_id: int
    name: str
    position: float


class ListResponse(BaseSchema):
    list: ListSchema


class ListsResponse(BaseSchema):
    lists: list[ListSchema]


class CardSchema(BaseSchema):
    id: int
    list_id: int
    name: str
    position: float


class CardResponse(BaseSchema):
    card: CardSchema


class CardsResponse(BaseSchema):
    cards: list[CardSchema]


def board_record_to_schema(board: BoardRecord) -> BoardSchema:
    if board.id is None or board.creator_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return BoardSchema(id=board.id, creator_id=board.creator_id, name=board.name)


def card_record_to_schema(card: CardRecord) -> CardSchema:
    if card.id is None or card.list_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return CardSchema(
        id=card.id,
        list_id=card.list_id,
        name=card.name,
        position=card.position,
    )


def list_record_to_schema(lst: ListRecord) -> ListSchema:
    if lst.id is None or lst.board_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ListSchema(
        id=lst.id,
        board_id=lst.board_id,
        name=lst.name,
        position=lst.position,
    )
