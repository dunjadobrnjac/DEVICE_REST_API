import os
from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from db import db

from resources.authentication import blp as AuthBlueprint
from resources.user import blp as UserBlueprint


def create_app():
    app = Flask(__name__)
    load_dotenv()  # load contents from .env

    app.config["API_TITLE"] = "IoT REST APi"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    # database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    db.init_app(app)

    api = Api(app)
    migrate = Migrate(app, db)

    # jwt configuration
    # koristena komanda secrets.SystemRandom().getrandbits(256)
    # kljuc nece ostati ovde
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY", "secret")
    jwt = JWTManager(app)

    api.register_blueprint(AuthBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
