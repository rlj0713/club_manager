
from flask import Blueprint, request
from sqlalchemy import select
from models import db, Club, User
from routes.users import require_user

clubs_bp = Blueprint("clubs", __name__)

@clubs_bp.get("/api/clubs")
def get_clubs():
    user, error = require_user()
    if error is not None:
        return error

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
    user, error = require_user()
    if error is not None:
        return error

    club = db.session.get(Club, club_id)

    if club is None:
        return {"error": "Club not found"}, 404

    return {
        "id": club.id,
        "name": club.name,
        "members": [member.username for member in club.members],
        "events": [
            {
                "id": event.id,
                "name": event.name,
                "location": event.location,
                "date": event.date.isoformat(),
            }
            for event in club.events
        ],
    }


@clubs_bp.post("/api/clubs")
def create_club():
    user, error = require_user()
    if error is not None:
        return error
    if not user.is_admin:
        return {"error": "Admin access required"}, 403

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


@clubs_bp.post("/api/clubs/<int:club_id>/members")
def invite_member(club_id):
    user, error = require_user()
    if error is not None:
        return error
    if not user.is_admin:
        return {"error": "Admin access required"}, 403

    club = db.session.get(Club, club_id)
    if club is None:
        return {"error": "Club not found"}, 404

    data = request.get_json()
    identifier = data.get("username") or data.get("email") if isinstance(data, dict) else None
    if not isinstance(identifier, str) or not identifier.strip():
        return {"error": "Username or email is required"}, 400

    member = db.session.scalar(
        select(User).where(
            (User.username == identifier.strip())
            | (User.email == identifier.strip().lower())
        )
    )
    if member is None:
        return {"error": "User not found"}, 404
    if member in club.members:
        return {"error": "User is already a club member"}, 409

    club.members.append(member)
    db.session.commit()

    return {
        "message": "Member added",
        "club_id": club.id,
        "user_id": member.id,
        "username": member.username,
    }, 201


@clubs_bp.put("/api/clubs/<int:club_id>")
def update_club(club_id):
    user, error = require_user()
    if error is not None:
        return error
    if not user.is_admin:
        return {"error": "Admin access required"}, 403

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
    user, error = require_user()
    if error is not None:
        return error
    if not user.is_admin:
        return {"error": "Admin access required"}, 403

    club = db.session.get(Club, club_id)

    if club is None:
        return {"error": "Club not found"}, 404

    db.session.delete(club)
    db.session.commit()

    return {
        "message": "Club deleted",
        "id": club_id
    }



# Example web requests to test all functionality:

# GET
# curl http://localhost:5000/api/clubs
# OR
# curl http://localhost:5000/api/clubs/1


# CREATE (POST)
# curl -X POST http://localhost:5000/api/clubs \
#   -H "Content-Type: application/json" \
#   -d '{"name":"Drama Club"}'


# UPDATE (PUT)
# curl -X PUT http://localhost:5000/api/clubs/3 \
#   -H "Content-Type: application/json" \
#   -d '{"name":"Advanced Drama Club"}'


# DELETE
# curl -X DELETE http://localhost:5000/api/clubs/3