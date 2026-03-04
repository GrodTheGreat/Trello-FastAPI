from typing import Annotated

from fastapi import APIRouter, Path, status

members_router = APIRouter()
member_router = APIRouter()

MemberIdRouteParam = Annotated[int, Path(alias="memberId", ge=1)]


@member_router.get("", status_code=status.HTTP_200_OK)
async def get_member(member_id: MemberIdRouteParam):
    pass


@member_router.get("/boards", status_code=status.HTTP_200_OK)
async def get_member_boards(member_id: MemberIdRouteParam):
    pass


@member_router.get("/organizations", status_code=status.HTTP_200_OK)
async def get_member_organizations(member_id: MemberIdRouteParam):
    pass


members_router.include_router(member_router, prefix="/{memberId:int}")
