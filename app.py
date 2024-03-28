from datetime import timedelta
import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from db import db

from resources import AuthBlueprint
from resources import UserBlueprint
from resources import DataBlueprint

from models import TokenBlocklist


def create_app():
    app = Flask(__name__)
    load_dotenv()  # load contents from .env

    app.config["API_TITLE"] = "IoT REST API"
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
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=365)
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "message": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"message": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    def kill_function():
        # it will kill server after few seconds waiting for responding
        import signal
        from time import sleep

        sleep(2)
        os.kill(os.getpid(), signal.SIGINT)

    @app.route("/shutdown", methods=["GET"])
    def shutdown():
        # TODO: enable only for admin
        # TODO: enable only when debugging
        # TODO: resolve
        from threading import Thread

        print(" * Shutting down Flask app...")
        # will create and start thread that will kill the server
        thread = Thread(
            target=kill_function,
        )
        thread.start()
        return (
            jsonify({"message": "Shutting down Flask app...."}),
            200,
        )

    api.register_blueprint(AuthBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(DataBlueprint)

    return app
