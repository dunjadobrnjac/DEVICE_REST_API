from db import db
from models import DeviceStatus


class DeviceModel(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(256), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    status = db.Column(db.Enum(DeviceStatus), nullable=False)

    data = db.relationship("DataModel", back_populates="device", lazy="dynamic")
