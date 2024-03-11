from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from passlib.hash import pbkdf2_sha256

from schemas import HeaderSchema

from models import UserModel
from db import db

blp = Blueprint("user", __name__, description="User registration")


@blp.route("/user/register")
class Registration(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    def post(self, header_data):
        username = header_data.get("username")
        password = header_data.get("password")

        user = UserModel.query.filter_by(username=username).first()
        if user:
            abort(409, message="A user with that username already exists.")

        new_user = UserModel(username=username, password=pbkdf2_sha256.hash(password))
        db.session.add(new_user)
        db.session.commit()

        return jsonify(
            {
                "status": "User created successfully.",
                "id": new_user.id,
                "username": new_user.username,
            }
        ), 201
