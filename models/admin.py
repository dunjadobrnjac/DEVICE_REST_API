from db import db
from models.user import UserModel


class AdminModel(UserModel):
    __tablename__ = "admins"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }
