from db import db


class DataModel(db.Model):
    __tablename__ = "data"

    id = db.Column(db.Integer, primary_key=True)
    generated_value = db.Column(db.Float, nullable=False)
    generation_time = db.Column(db.DateTime, nullable=False)

    data_type_id = db.Column(db.Integer, db.ForeignKey("data_type.id"), nullable=False)
    data_type = db.relationship("DataType", backref="data")

    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False)
    device = db.relationship("DeviceModel", back_populates="data")
