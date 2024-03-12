from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from passlib.hash import pbkdf2_sha256

from schemas import HeaderSchema, UserRegistrationSchema

from models import UserModel
from db import db

blp = Blueprint("user", __name__, description="User registration")

user_schema = UserRegistrationSchema()


@blp.route("/user/register")
class Registration(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.response(201, UserRegistrationSchema)
    def post(self, header_data):
        username = header_data.get("username")
        password = header_data.get("password")

        user = UserModel.query.filter_by(username=username).first()
        if user:
            abort(409, message="A user with that username already exists.")

        new_user = UserModel(username=username, password=pbkdf2_sha256.hash(password))
        db.session.add(new_user)
        db.session.commit()

        new_user_json = user_schema.dump(new_user)

        return jsonify(new_user_json), 201
