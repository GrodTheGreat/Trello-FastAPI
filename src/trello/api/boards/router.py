from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from trello.api.boards.dependecies import get_board_policy, get_board_repo
from trello.api.boards.schemas import BoardResponse, board_record_to_schema
from trello.api.cards.dependecies import get_card_repo
from trello.api.cards.schemas import CardsResponse, card_record_to_schema
from trello.api.dependencies import OptionalUser, get_user
from trello.api.lists.dependecies import get_list_repo
from trello.api.lists.schemas import ListsResponse, list_record_to_schema
from trello.authorization import BoardPolicy
from trello.boards import BoardRepository
from trello.cards import CardRepository
from trello.lists import ListRepository

boards_router = APIRouter()
BoardIdRouteParam = Annotated[int, Path(alias="boardId", ge=1)]


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
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
) -> CardsResponse:
    board = board_repo.find(board_id=board_id)
    if board is None or not board_policy.can_view(user.id, board):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    cards = card_repo.find_by_board(board.id)
    cards_data = [card_record_to_schema(card) for card in cards]

    return CardsResponse(cards=cards_data)


@boards_router.get("/{boardId:int}/lists")
async def get_board_lists(
    board_id: BoardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    board_policy: Annotated[BoardPolicy, Depends(get_board_policy)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> ListsResponse:
    board = board_repo.find(board_id=board_id)
    if board is None or not board_policy.can_view(user.id, board):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    lists = list_repo.find_by_board(board.id)
    lists_data = [list_record_to_schema(lst) for lst in lists]

    return ListsResponse(lists=lists_data)
