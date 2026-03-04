from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from trello.adaptors.boards.repository import BoardRepository
from trello.adaptors.cards.repository import CardRepository
from trello.adaptors.lists.repository import ListRepository
from trello.api.boards.dependecies import get_board_policy, get_board_repo
from trello.api.boards.schemas import BoardResponse, board_record_to_schema
from trello.api.cards.dependecies import get_card_repo
from trello.api.cards.schemas import CardsResponse, card_record_to_schema
from trello.api.dependencies import OptionalUser, get_user
from trello.api.lists.dependecies import get_list_repo
from trello.api.lists.schemas import ListsResponse, list_record_to_schema
from trello.authorization import BoardPolicy
from trello.exceptions import NotFoundException

board_router = APIRouter()
boards_router = APIRouter()

BoardIdRouteParam = Annotated[int, Path(alias="boardId", ge=1)]


@board_router.get("")
async def get_board(
    board_id: BoardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
) -> BoardResponse:
    board = board_repo.find(board_id=board_id)
    if board is None or not board_policy.can_view(user.id, board):
        raise NotFoundException(f"board with id {board_id} not found")
    board_data = board_record_to_schema(board)

    return BoardResponse(board=board_data)


@board_router.get("/cards")
async def get_board_cards(
    board_id: BoardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
) -> CardsResponse:
    board = board_repo.find(board_id=board_id)
    if board is None or not board_policy.can_view(user.id, board):
        raise NotFoundException(f"board with id {board_id} not found")
    cards = card_repo.find_by_board(board.id)
    cards_data = [card_record_to_schema(card) for card in cards]

    return CardsResponse(cards=cards_data)


@board_router.get("/lists")
async def get_board_lists(
    board_id: BoardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> ListsResponse:
    board = board_repo.find(board_id=board_id)
    if board is None or not board_policy.can_view(user.id, board):
        raise NotFoundException(f"board with id {board_id} not found")
    lists = list_repo.find_by_board(board.id)
    lists_data = [list_record_to_schema(lst) for lst in lists]

    return ListsResponse(lists=lists_data)


boards_router.include_router(board_router, prefix="/{boardId:int}")
