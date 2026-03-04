from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from trello.adaptors.boards.repository import BoardRepository
from trello.adaptors.cards.repository import CardRepository
from trello.adaptors.lists.repository import ListRepository
from trello.api.boards.dependecies import get_board_repo
from trello.api.boards.schemas import BoardResponse, board_record_to_schema
from trello.api.cards.dependecies import get_card_repo
from trello.api.cards.schemas import CardsResponse, card_record_to_schema
from trello.api.dependencies import OptionalUser, get_user
from trello.api.lists.dependecies import get_list_policy, get_list_repo
from trello.api.lists.schemas import ListResponse, list_record_to_schema
from trello.authorization import ListPolicy
from trello.exceptions import NotFoundException

list_router = APIRouter()
lists_router = APIRouter()

ListIdRouteParam = Annotated[int, Path(alias="listId", ge=1)]


@list_router.get("")
async def get_list(
    list_id: ListIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    list_policy: Annotated[ListPolicy, Depends(get_list_policy)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> ListResponse:
    lst = list_repo.find(list_id=list_id)
    if lst is None or not list_policy.can_view(user.id, lst):
        raise NotFoundException(f"list with id {list_id} not found")
    list_data = list_record_to_schema(lst)

    return ListResponse(list=list_data)


@list_router.get("/board")
async def get_list_board(
    list_id: ListIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
    list_policy: Annotated[ListPolicy, Depends(get_list_policy)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> BoardResponse:
    lst = list_repo.find(list_id=list_id)
    if lst is None or not list_policy.can_view(user.id, lst):
        raise NotFoundException(f"list with id {list_id} not found")
    if lst.board_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board = board_repo.find(lst.board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board_data = board_record_to_schema(board)

    return BoardResponse(board=board_data)


@list_router.get("/cards")
async def get_list_cards(
    list_id: ListIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
    list_policy: Annotated[ListPolicy, Depends(get_list_policy)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> CardsResponse:
    lst = list_repo.find(list_id=list_id)
    if lst is None or not list_policy.can_view(user.id, lst):
        raise NotFoundException(f"list with id {list_id} not found")
    if lst.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    cards = card_repo.find_by_list(list_id=lst.id)
    cards_data = [card_record_to_schema(card) for card in cards]

    return CardsResponse(cards=cards_data)


lists_router.include_router(list_router, prefix="/{listId}")
