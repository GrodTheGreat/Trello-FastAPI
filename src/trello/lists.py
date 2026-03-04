from sqlmodel import Session, select

from trello.database import BoardRecord, ListRecord


class ListRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def find(self, list_id: int) -> ListRecord | None:
        statement = select(ListRecord).where(ListRecord.id == list_id).limit(1)

        return self._db.exec(statement).first()
