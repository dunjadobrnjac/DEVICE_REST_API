from flask.views import MethodView
from flask_smorest import Blueprint
from flask import jsonify

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

        new_user = UserModel(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify(
            {
                "status": "New user created.",
                "id": new_user.id,
                "username": new_user.username,
                "password": new_user.password,
            }
        ), 201
