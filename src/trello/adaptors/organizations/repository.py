from sqlmodel import Session, select

from trello.database import OrganizationRecord


class OrganizationRepository:
    def __init__(self, session: Session):
        self._db: Session = session

    def find(self, organization_id: int) -> OrganizationRecord | None:
        statement = (
            select(OrganizationRecord)
            .where(OrganizationRecord.id == organization_id)
            .limit(1)
        )
        return self._db.exec(statement).first()
