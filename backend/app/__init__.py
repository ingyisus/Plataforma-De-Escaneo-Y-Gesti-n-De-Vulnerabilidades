from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

db = SQLAlchemy()
login = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    login.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes import main
    app.register_blueprint(main)
    return app
