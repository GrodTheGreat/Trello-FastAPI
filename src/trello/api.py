from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import Session, col, select

from trello.authorization import BoardPolicy
from trello.boards import BoardRepository
from trello.cards import CardRepository
from trello.database import BoardRecord, CardRecord, ListRecord, get_db
from trello.lists import ListRepository


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


@dataclass(frozen=True)
class OptionalUser:
    id: int = 1


def get_user() -> OptionalUser:
    return OptionalUser()


def get_board_repo(db: Annotated[Session, Depends(get_db)]) -> BoardRepository:
    return BoardRepository(db)


def get_board_policy(db: Annotated[Session, Depends(get_db)]) -> BoardPolicy:
    return BoardPolicy(db)


def get_card_repo(db: Annotated[Session, Depends(get_db)]) -> CardRepository:
    return CardRepository(db)


def get_list_repo(db: Annotated[Session, Depends(get_db)]) -> ListRepository:
    return ListRepository(db)


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


api_router = APIRouter()
boards_router = APIRouter()
cards_router = APIRouter()
lists_router = APIRouter()

BoardIdRouteParam = Annotated[int, Path(alias="boardId", ge=1)]
CardIdRouteParam = Annotated[int, Path(alias="cardId", ge=1)]
ListIdRouteParam = Annotated[int, Path(alias="listId", ge=1)]


@boards_router.get("/{boardId:int}")
async def get_board(
    board_id: BoardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
) -> BoardResponse:
    board = board_repo.find(board_id=board_id)
    if board is None or not board_policy.can_view(user.id, board):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    board_data = board_record_to_schema(board)

    return BoardResponse(board=board_data)


@boards_router.get("/{boardId:int}/cards")
async def get_board_cards(
    board_id: BoardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
) -> CardsResponse:
    board = board_repo.find(board_id=board_id)
    if board is None or not board_policy.can_view(user.id, board):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    statement = (
        select(CardRecord)
        .join(ListRecord)
        .where(ListRecord.board_id == board.id)
        .order_by(col(ListRecord.position), col(CardRecord.position))
    )
    cards = db.exec(statement).all()
    cards_data = []
    for card in cards:
        cards_data.append(card_record_to_schema(card))

    return CardsResponse(cards=cards_data)


@boards_router.get("/{boardId:int}/lists")
async def get_board_lists(
    board_id: BoardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
) -> ListsResponse:
    board = board_repo.find(board_id=board_id)
    if board is None or not board_policy.can_view(user.id, board):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    statement = (
        select(ListRecord)
        .where(ListRecord.board_id == board.id)
        .order_by(col(ListRecord.position))
    )
    lists = db.exec(statement).all()
    lists_data = []
    for lst in lists:
        lists_data.append(list_record_to_schema(lst))

    return ListsResponse(lists=lists_data)


@cards_router.get("/{cardId:int}")
async def get_card(
    card_id: CardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
) -> CardResponse:
    card = card_repo.find(card_id=card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    card_data = card_record_to_schema(card)

    return CardResponse(card=card_data)


@cards_router.get("/{cardId:int}/board")
async def get_card_board(
    card_id: CardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
) -> BoardResponse:
    card = card_repo.find(card_id=card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    statement = (
        select(BoardRecord)
        .join(ListRecord)
        .where(ListRecord.id == card.list_id)
        .limit(1)
    )
    board = db.exec(statement).first()
    if board is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not board_policy.can_view(user.id, board):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    board_data = board_record_to_schema(board)

    return BoardResponse(board=board_data)


@cards_router.get("/{cardId:int}/list")
async def get_card_list(
    card_id: CardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    db: Annotated[Session, Depends(get_db)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
) -> ListResponse:
    card = card_repo.find(card_id=card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    statement = select(ListRecord).where(ListRecord.id == card.list_id).limit(1)
    lst = db.exec(statement).first()
    if lst is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    list_data = list_record_to_schema(lst)

    return ListResponse(list=list_data)


@lists_router.get("/{listId:int}")
async def get_list(
    list_id: ListIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> ListResponse:
    lst = list_repo.find(list_id=list_id)
    if lst is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    list_data = list_record_to_schema(lst)

    return ListResponse(list=list_data)


@lists_router.get("/{listId:int}/board")
async def get_list_board(
    list_id: ListIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> BoardResponse:
    lst = list_repo.find(list_id=list_id)
    if lst is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if lst.board_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board = board_repo.find(lst.board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not board_policy.can_view(user.id, board):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    board_data = board_record_to_schema(board)

    return BoardResponse(board=board_data)


@lists_router.get("/{listId:int}/cards")
async def get_list_cards(
    list_id: ListIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> CardsResponse:
    lst = list_repo.find(list_id=list_id)
    if lst is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if lst.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    cards = card_repo.find_by_list(list_id=lst.id)
    cards_data = []
    for card in cards:
        cards_data.append(card_record_to_schema(card))

    return CardsResponse(cards=cards_data)


api_router.include_router(boards_router, prefix="/boards")
api_router.include_router(cards_router, prefix="/cards")
api_router.include_router(lists_router, prefix="/lists")
