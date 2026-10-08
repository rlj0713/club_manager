
from flask import Blueprint, request
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


@events_bp.get("/api/events/<int:event_id>")
def get_event(event_id):
    event = db.session.get(Event, event_id)

    if event is None:
        return {"error": "Event not found"}, 404

    return {
        "id": event.id,
        "name": event.name,
        "location": event.location
    }


@events_bp.post("/api/events")
def create_event():
    data = request.get_json()

    event = Event(
        name=data["name"],
        location=data["location"],
        creator_id=data["creator_id"],
        club_id=data["club_id"]
    )

    db.session.add(event)
    db.session.commit()

    return {
        "id": event.id,
        "name": event.name,
        "location": event.location
    }, 201


@events_bp.put("/api/events/<int:event_id>")
def update_event(event_id):
    event = db.session.get(Event, event_id)

    if event is None:
        return {"error": "Event not found"}, 404

    data = request.get_json()

    event.name = data["name"]
    event.location = data["location"]

    db.session.commit()

    return {
        "id": event.id,
        "name": event.name,
        "location": event.location
    }


@events_bp.delete("/api/events/<int:event_id>")
def delete_event(event_id):
    event = db.session.get(Event, event_id)

    if event is None:
        return {"error": "Event not found"}, 404

    db.session.delete(event)
    db.session.commit()

    return {
        "message": "Event deleted",
        "id": event_id
    }