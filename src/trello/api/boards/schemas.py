from fastapi import HTTPException, status

from trello.api.schemas import BaseSchema
from trello.database import BoardRecord


class BoardSchema(BaseSchema):
    id: int
    creator_id: int
    name: str


class BoardResponse(BaseSchema):
    board: BoardSchema


class BoardsResponse(BaseSchema):
    boards: list[BoardSchema]


def board_record_to_schema(board: BoardRecord) -> BoardSchema:
    if board.id is None or board.creator_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return BoardSchema(id=board.id, creator_id=board.creator_id, name=board.name)
