from datetime import datetime, timedelta, timezone
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_smorest import Blueprint, abort
from flask import jsonify
from passlib.hash import pbkdf2_sha256

from sqlalchemy.exc import SQLAlchemyError, OperationalError

from schemas import HeaderSchema, UserLoginSchema, UserSchema

from models import AdminModel, TokenBlocklist
from db import db

blp = Blueprint("user", __name__, description="User registration")

user_schema = UserLoginSchema()
user_reg = UserSchema()


@blp.route("/user/register")
class Registration(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.response(201, UserSchema)
    def post(self, header_data):
        username = header_data.get("username")
        password = header_data.get("password")

        try:
            user = AdminModel.query.filter_by(username=username).first()
            if user:
                abort(409, message="A user with that username already exists.")

            new_user = AdminModel(
                username=username, password=pbkdf2_sha256.hash(password), role="admin"
            )

            db.session.add(new_user)
            db.session.commit()
        except OperationalError:
            abort(500, message="Error connecting to the database.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while accessing the database.")
        response = user_reg.dump(new_user)
        return jsonify(response), 201


@blp.route("/user/login")
class Login(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.response(201, UserLoginSchema)
    def get(self, header_data):
        username = header_data.get("username")
        password = header_data.get("password")

        try:
            user = AdminModel.query.filter_by(username=username).first()
            if not user:
                abort(404, message="A user with that username not found.")

            if not pbkdf2_sha256.verify(password, user.password):
                abort(401, message="Invalid credentials.")

            access_token = create_access_token(
                identity=user.id, expires_delta=timedelta(minutes=30)
            )
            response = user_schema.dump({"access_token": access_token, "user": user})
            return jsonify(response), 200
        except OperationalError:
            abort(500, message="Error connecting to the database.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while accessing the database.")


@blp.route("/user/logout")
class Logout(MethodView):
    @jwt_required()
    def get(self):
        # revoke user token
        try:
            jti = get_jwt()["jti"]
            time = datetime.now(timezone.utc)
            db.session.add(TokenBlocklist(jti=jti, revoked_at=time))
            db.session.commit()
            return jsonify(message="The user was successfully logged out."), 200
        except OperationalError:
            abort(500, message="Error connecting to the database.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while accessing the database.")


@blp.route("/user/delete")
class Delete(MethodView):
    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        try:
            user = AdminModel.query.get(user_id)
            if not user:
                abort(403, message="Access to the requested resource is forbidden.")

            db.session.delete(user)
            db.session.commit()

            return jsonify(message="The user was successfully deleted."), 200
        except OperationalError:
            abort(500, message="Error connecting to the database.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while accessing the database.")
