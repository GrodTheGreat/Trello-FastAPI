from fastapi import APIRouter

from trello.api.boards.router import boards_router
from trello.api.cards.router import cards_router
from trello.api.lists.router import lists_router

api_router = APIRouter()

api_router.include_router(boards_router, prefix="/boards")
api_router.include_router(cards_router, prefix="/cards")
api_router.include_router(lists_router, prefix="/lists")
