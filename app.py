# Old Python way of doing things
# admin = User("Mr. Jackson", "123", True)
# student_1 = User("Bob", 123, False)
# student_2 = User("Alice", 123, False)
# club_1 = Club("Chess", members=[student_1, student_2])
# event_1 = Event("2026-10-25", "Room 104", admin)

# pip install flask
# pip install flask_sqlalchemy_lite

from flask import Flask
from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///db.sqlite3"}

class Base(DeclarativeBase):
    pass

db = SQLAlchemy()
db.init_app(app)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key = True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str]
    is_admin: Mapped[bool]
    clubs: Mapped[list["Club"]] = relationship( secondary="club_membership", back_populates="members")
    events: Mapped[list["Event"]] = relationship(back_populates="creator")
    events_attending: Mapped[list["Event"]] = relationship(secondary="event_attendee", back_populates="attendees")


class Club(Base):
    __tablename__ = "club"

    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str]
    members: Mapped[list["User"]] = relationship(secondary="club_membership", back_populates="clubs" )
    events: Mapped[list["Event"]] = relationship(back_populates="club")


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key = True)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    location: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    creator: Mapped["User"] = relationship(back_populates="events")
    club_id: Mapped[int] = mapped_column(ForeignKey("club.id"))
    club: Mapped["Club"] = relationship(back_populates="events")
    attendees: Mapped[list["User"]] = relationship(secondary="event_attendee", back_populates="events_attending")



class ClubMembership(Base):
    __tablename__ = "club_membership"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("club.id"), primary_key=True)

class EventAttendee(Base):
    __tablename__ = "event_attendee"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), primary_key=True)


if __name__ == "__main__":
    with app.app_context():
        engine = db.get_engine()
        Base.metadata.create_all(engine)

        admin = User( username="admin", password="admin123", is_admin=True)

    app.run(debug=True)