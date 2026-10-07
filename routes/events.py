
from flask import Blueprint
from sqlalchemy import select
from models import db, Event

events_bp = Blueprint("events", __name__)

@events_bp.get("/api/events")
def get_events():
    events = db.session.scalars(select(Event)).all()

    return [
        {
            "id": event.id,
            "name": event.name,
            "location": event.location
        }
        for event in events
    ]