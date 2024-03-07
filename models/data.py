from db import db
from models import DataTypeEnum


class DataModel(db.Model):
    __tablename__ = "data"

    id = db.Column(db.Integer, primary_key=True)
    generated_value = db.Column(db.Float, nullable=False)
    generation_time = db.Column(db.DateTime, nullable=False)
    data_type = db.Column(db.Enum(DataTypeEnum))

    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False)
    device = db.relationship("DeviceModel", back_populates="data")
