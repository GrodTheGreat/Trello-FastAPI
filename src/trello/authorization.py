from sqlmodel import Session, select

from trello.database import (
    BoardMemberRecord,
    BoardPermissionLevel,
    BoardRecord,
)


class BoardPolicy:
    def __init__(self, session: Session):
        self._db: Session = session

    def can_view(self, user_id: int, board: BoardRecord) -> bool:
        if board.permissionLevel == BoardPermissionLevel.PUBLIC:
            return True
        elif user_id == board.creator_id:
            return True
        statement = select(BoardMemberRecord).where(
            BoardMemberRecord.board_id == board.id,
            BoardMemberRecord.member_id == user_id,
        )
        member = self._db.exec(statement).first()

        return member is not None
