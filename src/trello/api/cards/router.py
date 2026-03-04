from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from trello.api.boards.dependecies import get_board_repo
from trello.api.boards.schemas import BoardResponse, board_record_to_schema
from trello.api.cards.dependecies import get_card_policy, get_card_repo
from trello.api.cards.schemas import CardResponse, card_record_to_schema
from trello.api.dependencies import OptionalUser, get_user
from trello.api.lists.dependecies import get_list_repo
from trello.api.lists.schemas import ListResponse, list_record_to_schema
from trello.authorization import CardPolicy
from trello.boards import BoardRepository
from trello.cards import CardRepository
from trello.lists import ListRepository

card_router = APIRouter()
cards_router = APIRouter()
cards_router.include_router(card_router, prefix="/{cardId:int}")

CardIdRouteParam = Annotated[int, Path(alias="cardId", ge=1)]


@card_router.get("")
async def get_card(
    card_id: CardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    card_policy: Annotated[CardPolicy, Depends(get_card_policy)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
) -> CardResponse:
    card = card_repo.find(card_id=card_id)
    if card is None or not card_policy.can_view(user.id, card):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    card_data = card_record_to_schema(card)

    return CardResponse(card=card_data)


@card_router.get("/board")
async def get_card_board(
    card_id: CardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
    card_policy: Annotated[CardPolicy, Depends(get_card_policy)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
) -> BoardResponse:
    card = card_repo.find(card_id=card_id)
    if card is None or not card_policy.can_view(user.id, card):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    board = board_repo.find_by_list(card.list_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board_data = board_record_to_schema(board)

    return BoardResponse(board=board_data)


@card_router.get("/list")
async def get_card_list(
    card_id: CardIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    card_policy: Annotated[CardPolicy, Depends(get_card_policy)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> ListResponse:
    card = card_repo.find(card_id=card_id)
    if card is None or not card_policy.can_view(user.id, card):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    lst = list_repo.find(list_id=card.list_id)
    if lst is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    list_data = list_record_to_schema(lst)

    return ListResponse(list=list_data)
