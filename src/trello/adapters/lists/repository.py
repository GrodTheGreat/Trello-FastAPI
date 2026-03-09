from sqlmodel import Session, col, select

from trello.database import CardListRecord


class ListRepository:
    def __init__(self, session: Session) -> None:
        self._db: Session = session

    def find(self, list_id: int) -> CardListRecord | None:
        statement = select(CardListRecord).where(CardListRecord.id == list_id).limit(1)

        return self._db.exec(statement).first()

    def find_by_board(self, board_id: int) -> list[CardListRecord]:
        statement = (
            select(CardListRecord)
            .where(CardListRecord.board_id == board_id)
            .order_by(col(CardListRecord.position))
        )

        return list(self._db.exec(statement).all())
