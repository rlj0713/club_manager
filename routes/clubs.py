
from flask import Blueprint
from sqlalchemy import select
from models import db, Club

clubs_bp = Blueprint("clubs", __name__)

@clubs_bp.get("/api/clubs")
def get_clubs():
    clubs = db.session.scalars(select(Club)).all()

    return [
        {
            "id": club.id,
            "name": club.name
        }
        for club in clubs
    ]