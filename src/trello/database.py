from typing import Generator, Optional

from sqlmodel import (
    Field,
    Relationship,
    SQLModel,
    Session,
    StaticPool,
    create_engine,
)


class UserRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str

    boards: list["BoardRecord"] = Relationship(
        back_populates="creator",
        cascade_delete=True,
    )
    sessions: list["SessionRecord"] = Relationship(
        back_populates="user",
        cascade_delete=True,
    )


class BoardRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    creator_id: int | None = Field(default=None, foreign_key="userrecord.id")
    name: str

    creator: Optional["UserRecord"] = Relationship(back_populates="boards")
    lists: list["ListRecord"] = Relationship(
        back_populates="board",
        cascade_delete=True,
    )


class ListRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    board_id: int | None = Field(default=None, foreign_key="boardrecord.id")
    name: str
    position: float

    board: Optional["BoardRecord"] = Relationship(back_populates="lists")
    cards: list["CardRecord"] = Relationship(back_populates="list", cascade_delete=True)


class CardRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    list_id: int | None = Field(default=None, foreign_key="listrecord.id")
    name: str
    position: float

    list: Optional["ListRecord"] = Relationship(back_populates="cards")


class SessionRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_hash: str
    user_id: int | None = Field(default=None, foreign_key="userrecord.id")

    user: Optional["UserRecord"] = Relationship(back_populates="sessions")


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    u1 = UserRecord(email="user1@email.com", password_hash="password")
    u2 = UserRecord(email="user2@email.com", password_hash="password")
    for i in range(1, 4):
        b = BoardRecord(name=f"Board {i}", creator=u1 if i % 2 == 1 else u2)
        session.add(b)
        for j in range(1, 4):
            li = ListRecord(name=f"List {j * i}", position=1_000.0 * j, board=b)
            session.add(li)
            for k in range(1, 3):
                c = CardRecord(name=f"Card {k * k * i}", position=1_000.0 * k, list=li)
                session.add(c)
    session.commit()


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
