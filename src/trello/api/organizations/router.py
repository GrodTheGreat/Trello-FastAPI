from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from fastapi.params import Depends

from trello.adaptors.organizations.repository import OrganizationRepository
from trello.api.organizations.dependencies import get_organization_repo
from trello.api.organizations.schemas import (
    OrganizationResponse,
    organization_record_to_schema,
)
from trello.exceptions import NotFoundException

organizations_router = APIRouter()
organization_router = APIRouter()

OrganizationIdRouteParam = Annotated[int, Path(alias="organizationId", ge=1)]


@organization_router.get("", status_code=status.HTTP_200_OK)
async def get_organization(
    organization_id: OrganizationIdRouteParam,
    organization_repo: Annotated[
        OrganizationRepository, Depends(get_organization_repo)
    ],
) -> OrganizationResponse:
    organization = organization_repo.find(organization_id)
    if organization is None:
        raise NotFoundException(f"organization with id {organization_id} not found")
    organization_data = organization_record_to_schema(organization)

    return OrganizationResponse(organization=organization_data)


organizations_router.include_router(organization_router, prefix="/{organizationId:int}")
