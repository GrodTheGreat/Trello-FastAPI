from sqlmodel import Session, select

from trello.database import BoardRecord, ListRecord


class ListRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def find(self, list_id: int, requested_by: int) -> ListRecord | None:
        statement = (
            select(ListRecord)
            .join(BoardRecord)
            .where(ListRecord.id == list_id, BoardRecord.creator_id == requested_by)
            .limit(1)
        )
        return self._db.exec(statement).first()
