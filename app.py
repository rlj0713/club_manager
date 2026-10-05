# pip install flask
# pip install flask_sqlalchemy_lite

from flask import Flask
from models import db, Base
from routes.clubs import clubs_bp

app = Flask(__name__)
app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///db.sqlite3"}

db.init_app(app)

app.register_blueprint(clubs_bp)


if __name__ == "__main__":
    with app.app_context():
        engine = db.get_engine()
        Base.metadata.create_all(engine)

    app.run(debug=True)

# To launch: python3 app.py
# To access database: sqlite3 instance/db.sqlite3
#    Ex: SELECT * FROM user;