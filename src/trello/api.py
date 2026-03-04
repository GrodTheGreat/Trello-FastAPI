from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from trello.authorization import BoardPolicy, CardPolicy, ListPolicy
from trello.boards import BoardRepository
from trello.cards import CardRepository
from trello.dependencies import (
    OptionalUser,
    get_board_policy,
    get_board_repo,
    get_card_policy,
    get_card_repo,
    get_list_policy,
    get_list_repo,
    get_user,
)
from trello.lists import ListRepository
from trello.schemas import (
    BoardResponse,
    CardResponse,
    CardsResponse,
    ListResponse,
    ListsResponse,
    board_record_to_schema,
    card_record_to_schema,
    list_record_to_schema,
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


@cards_router.get("/{cardId:int}")
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


@cards_router.get("/{cardId:int}/board")
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


@cards_router.get("/{cardId:int}/list")
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


@lists_router.get("/{listId:int}")
async def get_list(
    list_id: ListIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    list_policy: Annotated[ListPolicy, Depends(get_list_policy)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> ListResponse:
    lst = list_repo.find(list_id=list_id)
    if lst is None or not list_policy.can_view(user.id, lst):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    list_data = list_record_to_schema(lst)

    return ListResponse(list=list_data)


@lists_router.get("/{listId:int}/board")
async def get_list_board(
    list_id: ListIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)],
    list_policy: Annotated[ListPolicy, Depends(get_list_policy)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> BoardResponse:
    lst = list_repo.find(list_id=list_id)
    if lst is None or not list_policy.can_view(user.id, lst):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if lst.board_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board = board_repo.find(lst.board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    board_data = board_record_to_schema(board)

    return BoardResponse(board=board_data)


@lists_router.get("/{listId:int}/cards")
async def get_list_cards(
    list_id: ListIdRouteParam,
    user: Annotated[OptionalUser, Depends(get_user)],
    card_repo: Annotated[CardRepository, Depends(get_card_repo)],
    list_policy: Annotated[ListPolicy, Depends(get_list_policy)],
    list_repo: Annotated[ListRepository, Depends(get_list_repo)],
) -> CardsResponse:
    lst = list_repo.find(list_id=list_id)
    if lst is None or not list_policy.can_view(user.id, lst):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if lst.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    cards = card_repo.find_by_list(list_id=lst.id)
    cards_data = [card_record_to_schema(card) for card in cards]

    return CardsResponse(cards=cards_data)


api_router.include_router(boards_router, prefix="/boards")
api_router.include_router(cards_router, prefix="/cards")
api_router.include_router(lists_router, prefix="/lists")
