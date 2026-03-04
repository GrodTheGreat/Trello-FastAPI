from sqlmodel import Session, col, select

from trello.database import BoardRecord, CardRecord, ListRecord


class CardRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def find(self, card_id: int, requested_by: int) -> CardRecord | None:
        statement = (
            select(CardRecord)
            .join(ListRecord)
            .join(BoardRecord)
            .where(CardRecord.id == card_id, BoardRecord.creator_id == requested_by)
            .limit(1)
        )
        return self._db.exec(statement).first()

    def find_by_list(self, list_id: int) -> list[CardRecord]:
        statement = (
            select(CardRecord)
            .where(CardRecord.list_id == list_id)
            .order_by(col(CardRecord.position))
        )
        return list(self._db.exec(statement).all())
