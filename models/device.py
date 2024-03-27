from db import db
from models import DeviceStatus
from models.user import UserModel


class DeviceModel(UserModel):
    __tablename__ = "devices"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    serial_number = db.Column(db.String(256), unique=True, nullable=False)
    status = db.Column(db.Enum(DeviceStatus), nullable=False)

    data = db.relationship("DataModel", back_populates="device", lazy="dynamic")

    __mapper_args__ = {
        "polymorphic_identity": "device",
    }
