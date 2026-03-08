from sqlmodel import Session, col, select

from trello.database import CardListRecord, CardRecord


class CardRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def find(self, card_id: int) -> CardRecord | None:
        statement = select(CardRecord).where(CardRecord.id == card_id).limit(1)

        return self._db.exec(statement).first()

    def find_by_board(self, board_id: int) -> list[CardRecord]:
        statement = (
            select(CardRecord)
            .join(CardListRecord)
            .where(CardListRecord.board_id == board_id)
            .order_by(col(CardListRecord.position), col(CardRecord.position))
        )
        return list(self._db.exec(statement).all())

    def find_by_list(self, list_id: int) -> list[CardRecord]:
        statement = (
            select(CardRecord)
            .where(CardRecord.list_id == list_id)
            .order_by(col(CardRecord.position))
        )
        return list(self._db.exec(statement).all())
