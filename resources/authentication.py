from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from flask_jwt_extended import create_access_token
from passlib.hash import pbkdf2_sha256

from schemas import (
    HeaderSchema,
    DeviceRegistrationSchema,
    RegistrationUpdateSchema,
    DeviceSchema,
    DeviceLoginSchema,
)

from models import DeviceModel, DeviceStatus, UserModel
from db import db

# from datetime import datetime, timedelta

blp = Blueprint(
    "auth", __name__, description="Registration and login operations for devices."
)

device_schema = DeviceSchema()
login_schema = DeviceLoginSchema()


@blp.route("/auth/login/<int:id>")
class Login(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.response(200, DeviceLoginSchema)
    def get(self, header_data, id):
        username = header_data.get("username")
        password = header_data.get("password")

        device = DeviceModel.query.filter_by(id=id).first()
        if not device:
            abort(404, message="Device not found or invalid ID provided.")

        if device.username != username or not pbkdf2_sha256.verify(
            password, device.password
        ):
            abort(401, message="Invalid credentials.")

        if device.status != DeviceStatus.APPROVED:
            if device.status == DeviceStatus.CREATED:
                device_json = device_schema.dump(device)
                return jsonify(device_json), 200

            if device.status == DeviceStatus.BLACKLISTED:
                abort(403, message="Access to the requested resource is forbidden.")

            if device.status == DeviceStatus.DELETED:
                abort(
                    401,
                    message="The device cannot be logged in because the account has been deleted. "
                    "Please register again.",
                )

        # expires = datetime.utcnow() + timedelta(hours=256)
        access_token = create_access_token(
            identity=device.id
        )  # dodati timestamp i expires_delta=expires

        response = login_schema.dump({"access_token": access_token, "device": device})

        return jsonify(response), 200


@blp.route("/auth/register")
class Registration(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.arguments(DeviceRegistrationSchema, location="json")
    @blp.response(201, DeviceSchema)
    def post(self, header_data, payload_data):
        username = header_data.get("username")
        password = header_data.get("password")
        serial_number = payload_data.get("serial_number")

        device = DeviceModel.query.filter_by(serial_number=serial_number).first()

        if device:
            if device.status != DeviceStatus.DELETED:
                abort(
                    409,
                    message="Registration could not be completed due to a conflict. "
                    "Serial number already exist.",
                )

            if device.status == DeviceStatus.DELETED:
                device.status = DeviceStatus.CREATED
                db.session.commit()

                device_json = device_schema.dump(device)
                return jsonify(device_json), 201

        new_device = DeviceModel(
            username=username,
            password=pbkdf2_sha256.hash(password),
            serial_number=serial_number,
            status=DeviceStatus.CREATED,
        )
        db.session.add(new_device)
        db.session.commit()

        device_json = device_schema.dump(new_device)
        return jsonify(device_json), 201


@blp.route("/auth/status/<int:id>")
class RegistrationStatus(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.response(200, DeviceSchema)
    def get(self, header_data, id):
        username = header_data.get("username")
        password = header_data.get("password")

        device = DeviceModel.query.get(id)
        if not device:
            abort(404, message="Device not found or invalid ID provided.")

        # device = DeviceModel.query.get_or_404(id)

        if device.username != username or not pbkdf2_sha256.verify(
            password, device.password
        ):
            abort(401, message="Invalid credentials.")

        if device.status != DeviceStatus.APPROVED:
            if device.status == DeviceStatus.BLACKLISTED:
                abort(403, message="Access to the requested resource is forbidden.")

            device_json = device_schema.dump(device)
            return jsonify(device_json), 200

        access_token = create_access_token(identity=device.id)

        response = login_schema.dump({"access_token": access_token, "device": device})
        return jsonify(response), 200


@blp.route("/auth/update")
class RegistrationUpdate(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.arguments(RegistrationUpdateSchema, location="json")
    @blp.response(200, DeviceSchema)
    def patch(self, header_data, payload_data):
        username = header_data.get("username")
        password = header_data.get("password")
        new_status = payload_data.get("status")
        device_id = payload_data.get("device_id")

        user = UserModel.query.filter_by(username=username).first()

        if not user:
            abort(404, message="User not found or invalid username provided.")

        if not pbkdf2_sha256.verify(password, user.password):
            abort(401, message="Invalid password.")

        device = DeviceModel.query.get(device_id)
        if not device:
            abort(404, message="Device not found or invalid ID provided.")

        try:
            device.status = DeviceStatus[new_status]
            db.session.commit()
            device_json = device_schema.dump(device)
            return jsonify(device_json), 200
        except KeyError:
            abort(400, message="Invalid device status provided.")


@blp.route("/auth/delete/<int:id>")
class DeleteRegistration(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.response(200, DeviceSchema)
    def delete(self, header_data, id):
        username = header_data.get("username")
        password = header_data.get("password")

        device = DeviceModel.query.get(id)
        if not device:
            abort(404, message="Device not found or invalid ID provided.")

        if device.username != username or not pbkdf2_sha256.verify(
            password, device.password
        ):
            abort(401, message="Invalid credentials.")

        if device.status == DeviceStatus.BLACKLISTED:
            abort(403, message="Access to the requested resource is forbidden.")

        if device.status == DeviceStatus.DELETED:
            abort(403, message="Device is already deleted.")

        device.status = DeviceStatus.DELETED
        db.session.commit()

        device_json = device_schema.dump(device)
        return jsonify(device_json), 200
