from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from schemas import DataSchema

from models import DataModel, DataType, DeviceModel, DeviceStatus, TokenBlocklist
from db import db

from datetime import datetime, timezone

blp = Blueprint("data", __name__, description="Endpoint for receiving data.")


# {"value":"11", "unit":"Celsius","name": "Temperature"}
@blp.route("/data")
class DataResource(MethodView):
    @jwt_required()
    @blp.arguments(DataSchema)
    @blp.response(201, description="New data added successfully.")
    def post(self, data_payload):
        device_id = get_jwt_identity()

        try:
            device = DeviceModel.query.filter_by(id=device_id).first()
            if not device:
                abort(404, message="Device not found.")

            if device.status != DeviceStatus.APPROVED:
                if device.status == DeviceStatus.BLACKLISTED:
                    # revoke device token
                    jti = get_jwt()["jti"]
                    time = datetime.now(timezone.utc)
                    db.session.add(TokenBlocklist(jti=jti, revoked_at=time))
                    db.session.commit()
                abort(403, message="Access to the requested resource is forbidden.")

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

            return jsonify(message="New data added successfully."), 201
        except OperationalError:
            abort(500, message="Error connecting to the database.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while accessing the database.")
