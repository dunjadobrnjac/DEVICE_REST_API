from flask.views import MethodView
from flask_smorest import Blueprint
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from schemas import DataSchema

from models import DataModel, DataType
from db import db

from datetime import datetime

blp = Blueprint("data", __name__, description="Endpoint for receiving data.")


# {"value":"11", "unit":"Celsius","name": "Temperature"}
@blp.route("/data")
class DataResource(MethodView):
    @jwt_required()
    @blp.arguments(DataSchema)
    def post(self, data_payload):
        device_id = get_jwt_identity()

        value = data_payload.get("value")
        name = data_payload.get("name")
        unit = data_payload.get("unit")
        time = data_payload.get("time")

        data_type = DataType.query.filter_by(name=name, unit=unit).first()
        if not data_type:
            data_type = DataType(name=name, unit=unit)
            db.session.add(data_type)
            db.session.commit()

        if time is None:
            time = datetime.utcnow()

        new_data = DataModel(
            generated_value=value,
            generation_time=time,
            data_type_id=data_type.id,
            device_id=device_id,
        )
        db.session.add(new_data)
        db.session.commit()

        return jsonify(message="New data added successfully"), 201
