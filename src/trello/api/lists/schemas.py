from fastapi import HTTPException, status

from trello.api.schemas import BaseSchema
from trello.database import ListRecord


class ListSchema(BaseSchema):
    id: int
    board_id: int
    name: str
    position: float


class ListResponse(BaseSchema):
    list: ListSchema


class ListsResponse(BaseSchema):
    lists: list[ListSchema]


def list_record_to_schema(lst: ListRecord) -> ListSchema:
    if lst.id is None or lst.board_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ListSchema(
        id=lst.id,
        board_id=lst.board_id,
        name=lst.name,
        position=lst.position,
    )
