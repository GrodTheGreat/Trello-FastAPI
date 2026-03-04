from fastapi import APIRouter

from trello.api.boards.router import boards_router
from trello.api.cards.router import cards_router
from trello.api.lists.router import lists_router
from trello.api.members.router import members_router
from trello.api.organizations.router import organizations_router

api_router = APIRouter()

api_router.include_router(boards_router, prefix="/boards")
api_router.include_router(cards_router, prefix="/cards")
api_router.include_router(lists_router, prefix="/lists")
api_router.include_router(members_router, prefix="/members")
api_router.include_router(organizations_router, prefix="/organizations")
