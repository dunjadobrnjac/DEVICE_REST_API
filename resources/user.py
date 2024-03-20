from datetime import timedelta
from flask.views import MethodView
from flask_jwt_extended import create_access_token
from flask_smorest import Blueprint, abort
from flask import jsonify
from passlib.hash import pbkdf2_sha256

from sqlalchemy.exc import SQLAlchemyError

from schemas import HeaderSchema, UserLoginSchema, UserSchema

from models import UserModel
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

        user = UserModel.query.filter_by(username=username).first()
        if user:
            abort(409, message="A user with that username already exists.")

        new_user = UserModel(username=username, password=pbkdf2_sha256.hash(password))
        try:
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting new user.")

        response = user_reg.dump({"user": new_user})
        return jsonify(response), 201


@blp.route("/user/login")
class Login(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.response(201, UserLoginSchema)
    def get(self, header_data):
        username = header_data.get("username")
        password = header_data.get("password")

        user = UserModel.query.filter_by(username=username).first()
        if not user:
            abort(404, message="A user with that username not found.")

        if not pbkdf2_sha256.verify(password, user.password):
            abort(401, message="Invalid credentials.")

        access_token = create_access_token(
            identity=user.id, expires_delta=timedelta(minutes=30)
        )
        response = user_schema.dump({"access_token": access_token, "user": user})
        return jsonify(response), 200
