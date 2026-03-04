from enum import Enum
from typing import Optional

from sqlmodel import (
    Field,
    Relationship,
    Session,
    SQLModel,
    StaticPool,
    create_engine,
)


class BoardPermissionLevel(Enum):
    ORG = "org"
    PRIVATE = "private"
    PUBLIC = "public"


class OrganizationPermissionLevel(Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class BoardMemberRecord(SQLModel, table=True):
    board_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="boardrecord.id",
    )
    member_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="userrecord.id",
    )

    board: Optional["BoardRecord"] = Relationship(back_populates="members")
    member: Optional["UserRecord"] = Relationship(back_populates="board_memberships")


class OrganizationMemberRecord(SQLModel, table=True):
    organization_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="organizationrecord.id",
    )
    member_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="userrecord.id",
    )

    organization: Optional["OrganizationRecord"] = Relationship(
        back_populates="members"
    )
    member: Optional["UserRecord"] = Relationship(
        back_populates="organization_memberships"
    )


class UserRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str

    boards: list["BoardRecord"] = Relationship(
        back_populates="creator",
        cascade_delete=True,
    )
    board_memberships: list["BoardMemberRecord"] = Relationship(back_populates="member")
    sessions: list["SessionRecord"] = Relationship(
        back_populates="user",
        cascade_delete=True,
    )
    organization_memberships: list["OrganizationMemberRecord"] = Relationship(
        back_populates="member",
    )


class BoardRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    creator_id: int | None = Field(default=None, foreign_key="userrecord.id")
    organization_id: int | None = Field(
        default=None, foreign_key="organizationrecord.id"
    )
    name: str
    permission_level: BoardPermissionLevel = Field(default=BoardPermissionLevel.ORG)

    creator: Optional["UserRecord"] = Relationship(back_populates="boards")
    lists: list["ListRecord"] = Relationship(
        back_populates="board",
        cascade_delete=True,
    )
    members: list["BoardMemberRecord"] = Relationship(back_populates="board")
    organization: Optional["OrganizationRecord"] = Relationship(back_populates="boards")


class CardRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    list_id: int | None = Field(default=None, foreign_key="listrecord.id")
    name: str
    position: float

    list: Optional["ListRecord"] = Relationship(back_populates="cards")


class ListRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    board_id: int | None = Field(default=None, foreign_key="boardrecord.id")
    name: str
    position: float

    board: Optional["BoardRecord"] = Relationship(back_populates="lists")
    cards: list["CardRecord"] = Relationship(back_populates="list", cascade_delete=True)


class OrganizationRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    permission_level: OrganizationPermissionLevel = Field(
        default=OrganizationPermissionLevel.PRIVATE
    )

    boards: list["BoardRecord"] = Relationship(back_populates="organization")
    members: list["OrganizationMemberRecord"] = Relationship(
        back_populates="organization"
    )


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
    o = OrganizationRecord(name="Organization 1")
    session.add(u1)
    session.add(u2)
    session.add(o)
    om1 = OrganizationMemberRecord(organization=o, member=u1)
    om2 = OrganizationMemberRecord(organization=o, member=u2)
    session.add(om1)
    session.add(om2)
    for i in range(1, 4):
        b = BoardRecord(
            orgnization=o,
            name=f"Board {i}",
            permissionLevel=BoardPermissionLevel.ORG,
            creator=u1 if i % 2 == 1 else u2,
        )
        session.add(b)
        bm = BoardMemberRecord(board=b, member=u1 if i % 2 == 1 else u2)
        session.add(bm)
        for j in range(1, 4):
            li = ListRecord(name=f"List {j * i}", position=1_000.0 * j, board=b)
            session.add(li)
            for k in range(1, 3):
                c = CardRecord(name=f"Card {k * k * i}", position=1_000.0 * k, list=li)
                session.add(c)
    session.commit()
