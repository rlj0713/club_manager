# pip install flask
# pip install flask_sqlalchemy_lite

import os

from dotenv import load_dotenv
from flask import Flask
from flask import render_template
from models import db, Base
from routes.clubs import clubs_bp
from routes.events import events_bp
from routes.users import users_bp

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///db.sqlite3"}
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

db.init_app(app)

app.register_blueprint(clubs_bp)
app.register_blueprint(events_bp)
app.register_blueprint(users_bp)


@app.get("/")
def index():
    return render_template("dashboard.html")


@app.get("/login")
def login_page():
    return render_template("login.html")


@app.get("/register")
def register_page():
    return render_template("register.html")


@app.get("/users/<int:user_id>")
def profile_page(user_id):
    return render_template("profile.html")


@app.get("/clubs")
def clubs_home():
    return render_template("clubs.html")


@app.get("/clubs/<int:club_id>")
def club_page(club_id):
    return render_template("club.html")


@app.get("/events")
def events_home():
    return render_template("events.html")


@app.get("/events/<int:event_id>")
def event_page(event_id):
    return render_template("event.html")


if __name__ == "__main__":
    with app.app_context():
        engine = db.get_engine()
        Base.metadata.create_all(engine)

    app.run(debug=True)

# To launch: python3 app.py
# To access database: sqlite3 instance/db.sqlite3
#    Ex: SELECT * FROM user;