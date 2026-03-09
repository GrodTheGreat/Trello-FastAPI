from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from trello.adapters.organizations.repository import OrganizationRepository
from trello.api.dependencies import get_db
from trello.authorization import OrganizationPolicy


def get_organization_policy(session: Session = Depends(get_db)) -> OrganizationPolicy:
    return OrganizationPolicy(session)


def get_organization_repo(
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationRepository:
    return OrganizationRepository(db)
