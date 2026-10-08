
from flask import Blueprint, request
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


@clubs_bp.get("/api/clubs/<int:club_id>")
def get_club(club_id):
    club = db.session.get(Club, club_id)

    if club is None:
        return {"error": "Club not found"}, 404

    return {
        "id": club.id,
        "name": club.name
    }


@clubs_bp.post("/api/clubs")
def create_club():
    data = request.get_json()

    club = Club(
        name=data["name"]
    )

    db.session.add(club)
    db.session.commit()

    return {
        "id": club.id,
        "name": club.name
    }, 201


@clubs_bp.put("/api/clubs/<int:club_id>")
def update_club(club_id):
    club = db.session.get(Club, club_id)

    if club is None:
        return {"error": "Club not found"}, 404

    data = request.get_json()

    club.name = data["name"]

    db.session.commit()

    return {
        "id": club.id,
        "name": club.name
    }


@clubs_bp.delete("/api/clubs/<int:club_id>")
def delete_club(club_id):
    club = db.session.get(Club, club_id)

    if club is None:
        return {"error": "Club not found"}, 404

    db.session.delete(club)
    db.session.commit()

    return {
        "message": "Club deleted",
        "id": club_id
    }