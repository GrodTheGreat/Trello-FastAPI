from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from trello.adaptors.organizations.repository import OrganizationRepository
from trello.api.dependencies import get_db


def get_organization_repo(
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationRepository:
    return OrganizationRepository(db)
