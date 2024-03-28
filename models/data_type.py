from db import db


class DataType(db.Model):
    __tablename__ = "data_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    unit = db.Column(db.String(80), nullable=False)
