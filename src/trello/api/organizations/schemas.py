from trello.api.schemas import BaseSchema
from trello.database import OrganizationRecord


class OrganizationSchema(BaseSchema):
    id: int
    name: str


class OrganizationResponse(BaseSchema):
    organization: OrganizationSchema


def organization_record_to_schema(
    organization: OrganizationRecord,
) -> OrganizationSchema:
    return OrganizationSchema(id=organization.id, name=organization.name)
