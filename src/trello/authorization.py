from sqlmodel import Session, select

from trello.database import (
    BoardMemberRecord,
    BoardPermissionLevel,
    BoardRecord,
    CardListRecord,
    CardRecord,
    OrganizationMemberRecord,
    OrganizationPermissionLevel,
    OrganizationRecord,
)


class BoardPolicy:
    def __init__(self, session: Session):
        self._db: Session = session

    def can_view(self, user_id: int, board: BoardRecord) -> bool:
        if board.permission_level == BoardPermissionLevel.PUBLIC:
            return True
        elif user_id == board.creator_id:
            return True
        statement = select(BoardMemberRecord).where(
            BoardMemberRecord.board_id == board.id,
            BoardMemberRecord.member_id == user_id,
        )
        member = self._db.exec(statement).first()

        return member is not None


class CardPolicy:
    def __init__(self, session: Session):
        self._db: Session = session

    def can_view(self, user_id: int, card: CardRecord) -> bool:
        statement = (
            select(BoardRecord)
            .join(CardListRecord)
            .where(CardListRecord.id == card.list_id)
            .limit(1)
        )
        board = self._db.exec(statement).first()
        if board is None:
            # This shouldn't be possible
            raise Exception()
        if board.permission_level == BoardPermissionLevel.PUBLIC:
            return True
        elif user_id == board.creator_id:
            return True
        statement = select(BoardMemberRecord).where(
            BoardMemberRecord.board_id == board.id,
            BoardMemberRecord.member_id == user_id,
        )
        member = self._db.exec(statement).first()

        return member is not None


class ListPolicy:
    def __init__(self, session: Session):
        self._db: Session = session

    def can_view(self, user_id: int, list: CardListRecord) -> bool:
        statement = select(BoardRecord).where(BoardRecord.id == list.board_id).limit(1)
        board = self._db.exec(statement).first()
        if board is None:
            # This shouldn't be possible
            raise Exception()
        if board.permission_level == BoardPermissionLevel.PUBLIC:
            return True
        elif user_id == board.creator_id:
            return True
        statement = select(BoardMemberRecord).where(
            BoardMemberRecord.board_id == board.id,
            BoardMemberRecord.member_id == user_id,
        )
        member = self._db.exec(statement).first()

        return member is not None


class OrganizationPolicy:
    def __init__(self, session: Session):
        self._db: Session = session

    def can_view(self, user_id: int, organization: OrganizationRecord) -> bool:
        if organization.permission_level == OrganizationPermissionLevel.PUBLIC:
            return True
        statement = (
            select(OrganizationMemberRecord)
            .where(
                OrganizationMemberRecord.organization_id == organization.id,
                OrganizationMemberRecord.member_id == user_id,
            )
            .limit(1)
        )
        member = self._db.exec(statement).first()

        return member is not None
