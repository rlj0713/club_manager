
from datetime import datetime

from flask import Blueprint, request
from sqlalchemy import select
from models import db, Event
from routes.users import require_user

events_bp = Blueprint("events", __name__)


def can_view_event(user, event):
    return user.is_admin or user in event.club.members


def parse_event_date(value):
    if not isinstance(value, str) or not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@events_bp.get("/api/events")
def get_events():
    user, error = require_user()
    if error is not None:
        return error

    events = db.session.scalars(select(Event)).all()

    return [
        {
            "id": event.id,
            "name": event.name,
            "location": event.location,
            "date": event.date.isoformat(),
            "club_id": event.club_id,
            "creator_id": event.creator_id,
        }
        for event in events
        if can_view_event(user, event)
    ]


@events_bp.get("/api/events/<int:event_id>")
def get_event(event_id):
    user, error = require_user()
    if error is not None:
        return error

    event = db.session.get(Event, event_id)

    if event is None:
        return {"error": "Event not found"}, 404
    if not can_view_event(user, event):
        return {"error": "You must belong to the event's club"}, 403

    return {
        "id": event.id,
        "name": event.name,
        "location": event.location,
        "date": event.date.isoformat(),
        "club_id": event.club_id,
        "creator_id": event.creator_id,
    }


@events_bp.post("/api/events")
def create_event():
    user, error = require_user()
    if error is not None:
        return error
    if not user.is_admin:
        return {"error": "Admin access required"}, 403

    data = request.get_json()
    event_date = parse_event_date(data.get("date"))
    if event_date is None:
        return {"error": "A valid event date is required"}, 400

    event = Event(
        name=data["name"],
        date=event_date,
        location=data["location"],
        creator_id=user.id,
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
    user, error = require_user()
    if error is not None:
        return error

    event = db.session.get(Event, event_id)

    if event is None:
        return {"error": "Event not found"}, 404
    if not user.is_admin:
        return {"error": "Admin access required"}, 403

    data = request.get_json()
    event_date = parse_event_date(data.get("date"))
    if event_date is None:
        return {"error": "A valid event date is required"}, 400

    event.name = data["name"]
    event.date = event_date
    event.location = data["location"]

    db.session.commit()

    return {
        "id": event.id,
        "name": event.name,
        "location": event.location
    }


@events_bp.delete("/api/events/<int:event_id>")
def delete_event(event_id):
    user, error = require_user()
    if error is not None:
        return error

    event = db.session.get(Event, event_id)

    if event is None:
        return {"error": "Event not found"}, 404
    if not user.is_admin:
        return {"error": "Admin access required"}, 403

    db.session.delete(event)
    db.session.commit()

    return {
        "message": "Event deleted",
        "id": event_id
    }