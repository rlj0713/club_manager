from datetime import datetime
import bcrypt
from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy import String, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

db = SQLAlchemy()


# Relationships
club_membership = Table(
    'club_membership',
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("club_id", ForeignKey("club.id"), primary_key=True)
)

event_attendee = Table(
    'event_attendee',
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("event_id", ForeignKey("event.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str]
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    _password: Mapped[str] = mapped_column("password", String(60))
    is_admin: Mapped[bool]
    clubs: Mapped[list["Club"]] = relationship( secondary="club_membership", back_populates="members")
    events: Mapped[list["Event"]] = relationship(back_populates="creator")
    events_attending: Mapped[list["Event"]] = relationship(secondary="event_attendee", back_populates="attendees")

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self.set_password(value)

    def set_password(self, password: str) -> None:
        self._password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self._password.encode("utf-8")
        )

class Club(Base):
    __tablename__ = "club"

    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str]
    members: Mapped[list["User"]] = relationship(secondary="club_membership", back_populates="clubs" )
    events: Mapped[list["Event"]] = relationship(back_populates="club")

class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str]
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    location: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    creator: Mapped["User"] = relationship(back_populates="events")
    club_id: Mapped[int] = mapped_column(ForeignKey("club.id"))
    club: Mapped["Club"] = relationship(back_populates="events")
    attendees: Mapped[list["User"]] = relationship(secondary="event_attendee", back_populates="events_attending")