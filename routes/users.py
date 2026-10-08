from flask import Blueprint, request, session
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from models import Event, User, db

users_bp = Blueprint("users", __name__)


def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id is not None else None


def require_user():
    user = current_user()
    return (user, None) if user is not None else (None, ({"error": "Authentication required"}, 401))


def user_response(user):
    return {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
    }


def get_credentials():
    data = request.get_json()

    if not isinstance(data, dict):
        return None, ({"error": "A JSON request body is required"}, 400)

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        return None, ({"error": "Username is required"}, 400)

    if not isinstance(password, str) or not password:
        return None, ({"error": "Password is required"}, 400)

    return (username.strip(), password), None


@users_bp.post("/api/users")
def create_user():
    data = request.get_json()
    credentials, error = get_credentials()

    if error is not None:
        return error

    name = data.get("name")
    email = data.get("email")
    username, password = credentials

    if not isinstance(name, str) or not name.strip():
        return {"error": "Name is required"}, 400

    if not isinstance(email, str) or not email.strip():
        return {"error": "Email is required"}, 400

    if len(username) > 50:
        return {"error": "Username must be 50 characters or fewer"}, 400

    if len(email.strip()) > 255:
        return {"error": "Email must be 255 characters or fewer"}, 400

    if len(password.encode("utf-8")) > 72:
        return {"error": "Password must be 72 bytes or fewer"}, 400

    user = User(
        name=name.strip(),
        username=username,
        email=email.strip().lower(),
        password=password,
        is_admin=False,
    )

    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Username or email is already in use"}, 409

    session.clear()
    session["user_id"] = user.id

    return user_response(user), 201


@users_bp.post("/api/login")
def login():
    credentials, error = get_credentials()

    if error is not None:
        return error

    username, password = credentials
    user = db.session.scalar(select(User).where(User.username == username))

    if user is None or not user.check_password(password):
        return {"error": "Invalid username or password"}, 401

    session.clear()
    session["user_id"] = user.id

    return user_response(user)


@users_bp.get("/api/users/<int:user_id>")
def get_user(user_id):
    user, error = require_user()

    if error is not None:
        return error

    if user.id != user_id:
        return {"error": "You can only view your own account"}, 403

    return user_response(user)


@users_bp.get("/api/me")
def get_current_user():
    user, error = require_user()

    if error is not None:
        return error

    return user_response(user)


@users_bp.put("/api/users/<int:user_id>")
def update_user(user_id):
    user, error = require_user()

    if error is not None:
        return error

    if user.id != user_id:
        return {"error": "You can only edit your own account"}, 403

    data = request.get_json()

    if not isinstance(data, dict):
        return {"error": "A JSON request body is required"}, 400

    if "username" in data:
        if not isinstance(data["username"], str) or not data["username"].strip():
            return {"error": "Username is required"}, 400
        if len(data["username"].strip()) > 50:
            return {"error": "Username must be 50 characters or fewer"}, 400
        user.username = data["username"].strip()

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return {"error": "Name is required"}, 400
        user.name = data["name"].strip()

    if "email" in data:
        if not isinstance(data["email"], str) or not data["email"].strip():
            return {"error": "Email is required"}, 400
        if len(data["email"].strip()) > 255:
            return {"error": "Email must be 255 characters or fewer"}, 400
        user.email = data["email"].strip().lower()

    if "password" in data:
        if not isinstance(data["password"], str) or not data["password"]:
            return {"error": "Password is required"}, 400
        if len(data["password"].encode("utf-8")) > 72:
            return {"error": "Password must be 72 bytes or fewer"}, 400
        user.password = data["password"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Username or email is already in use"}, 409

    return user_response(user)


@users_bp.post("/api/logout")
def logout():
    session.clear()
    return "", 204


@users_bp.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    current_user_id = session.get("user_id")

    if current_user_id is None:
        return {"error": "Authentication required"}, 401

    if current_user_id != user_id:
        return {"error": "You can only delete your own account"}, 403

    user = db.session.get(User, current_user_id)

    if user is None:
        session.clear()
        return {"error": "Authentication required"}, 401

    created_event_count = db.session.scalar(
        select(func.count()).select_from(Event).where(Event.creator_id == user.id)
    )

    if created_event_count:
        return {
            "error": "Delete or reassign events you created before deleting your account"
        }, 409

    db.session.delete(user)
    db.session.commit()
    session.clear()

    return {
        "message": "User deleted",
        "id": user_id,
    }
