from sqlmodel import Session, select

from trello.database import BoardRecord, ListRecord


class BoardRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def find(self, board_id: int) -> BoardRecord | None:
        statement = select(BoardRecord).where(BoardRecord.id == board_id).limit(1)

        return self._db.exec(statement).first()

    def find_by_list(self, list_id: int) -> BoardRecord | None:
        statement = (
            select(BoardRecord)
            .join(ListRecord)
            .where(ListRecord.id == list_id)
            .limit(1)
        )

        return self._db.exec(statement).first()
