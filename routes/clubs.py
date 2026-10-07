
from flask import Blueprint
from sqlalchemy import select
from models import db, Club

clubs_bp = Blueprint("clubs", __name__)

@clubs_bp.get("/api/clubs")
def get_clubs():
    clubs = db.session.scalars(select(Club)).all()

    json_data = []
    
    for club in clubs:
        members = []
        for member in club.members:
            members.append(member.username)
        events = []
        for event in club.events:
            events.append(event.name)
        json_data.append(
            {
                'id': club.id,
                'name': club.name,
                'members': members,
                'events': events
            }
        )

    return json_data