from sqlmodel import Session, select

from trello.database import BoardRecord


class BoardRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def find(self, board_id: int) -> BoardRecord | None:
        statement = select(BoardRecord).where(BoardRecord.id == board_id).limit(1)

        return self._db.exec(statement).first()
