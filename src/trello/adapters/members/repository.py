from sqlmodel import Session, select

from trello.database import BoardMemberRecord, OrganizationMemberRecord


class MemberRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def find_board_memberships(self, user_id: int) -> list[BoardMemberRecord]:
        statement = select(BoardMemberRecord).where(
            BoardMemberRecord.member_id == user_id
        )
        memberships = self._db.exec(statement).all()
        return list(memberships)

    def find_organization_memberships(
        self,
        user_id: int,
    ) -> list[OrganizationMemberRecord]:
        statement = select(OrganizationMemberRecord).where(
            OrganizationMemberRecord.member_id == user_id
        )
        memberships = self._db.exec(statement).all()
        return list(memberships)
