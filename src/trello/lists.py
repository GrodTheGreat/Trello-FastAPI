from sqlmodel import Session, col, select

from trello.database import BoardRecord, ListRecord


class ListRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def find(self, list_id: int) -> ListRecord | None:
        statement = select(ListRecord).where(ListRecord.id == list_id).limit(1)

        return self._db.exec(statement).first()
    def find_by_board(self,board_id:int)->list[ListRecord]:
        statement = (
            select(ListRecord)
            .where(ListRecord.board_id == board_id)
            .order_by(col(ListRecord.position))
        )

        return list(self._db.exec(statement).all())
