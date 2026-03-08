from fastapi import APIRouter

from trello.ssr.auth.router import auth_router

ssr_router = APIRouter()

ssr_router.include_router(auth_router, prefix="")
