from datetime import datetime

from app import app
from models import db, Base, User, Club, Event

with app.app_context():
    try:
        engine = db.get_engine()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        
        # Create users
        admin = User(
            name="admin",
            username="admin",
            password="admin123",
            is_admin=True
        )

        alice = User(
            name="alice",
            username="alice",
            password="alice123",
            is_admin=False
        )

        bob = User(
            name="bob",
            username="bob",
            password="bob123",
            is_admin=False
        )

        # Create clubs
        chess = Club(name="Chess Club")
        robotics = Club(name="Robotics Club")

        # Add relationships
        chess.members.extend([alice, bob])
        robotics.members.extend([alice, admin])

        # Create events
        tournament = Event(
            name="Tournament",
            date=datetime(2026, 10, 15, 15, 30),
            location="Room 104",
            creator=admin,
            club=chess,
            attendees=[alice, bob]
        )

        workshop = Event(
            name="Workshop",
            date=datetime(2026, 10, 22, 15, 30),
            location="Library",
            creator=admin,
            club=chess,
            attendees=[alice]
        )

        db.session.add_all([
            admin,
            alice,
            bob,
            chess,
            robotics,
            tournament,
            workshop
        ])

        db.session.commit()
        print("Database seeded successfully!")

    except Exception as e:
        db.session.rollback()
        print("Database seed failed.")
        print(f"Error: {e}")
        raise