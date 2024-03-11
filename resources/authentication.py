from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from flask_jwt_extended import create_access_token
from passlib.hash import pbkdf2_sha256

from schemas import HeaderSchema, DeviceRegistrationSchema, RegistrationUpdateSchema

from models import DeviceModel, DeviceStatus, UserModel
from db import db

# from datetime import datetime, timedelta

blp = Blueprint(
    "auth", __name__, description="Registration and login operations for devices."
)


@blp.route("/auth/login/<int:id>")
class Login(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    def get(self, header_data, id):
        username = header_data.get("username")
        password = header_data.get("password")

        device = DeviceModel.query.filter_by(id=id).first()
        if not device:
            return jsonify({"status": "Device not found or invalid ID provided."}), 404

        if device.username != username or not pbkdf2_sha256.verify(
            password, device.password
        ):
            return jsonify({"status": "Invalid credentials."}), 401

        if device.status != DeviceStatus.APPROVED:
            if device.status == DeviceStatus.CREATED:
                return jsonify(
                    {
                        "status": "Device is created but not approved for login.",
                        "device_status": device.status.value,
                    }
                ), 200
            if device.status == DeviceStatus.BLACKLISTED:
                return jsonify(
                    {"status": "Access to the requested resource is forbidden."}
                ), 403
            if device.status == DeviceStatus.DELETED:
                return jsonify(
                    {
                        "status": "The device cannot be logged in because the account has been deleted. "
                                  "Please register again.",
                        "device_status": device.status.value,
                    }
                ), 401

        # expires = datetime.utcnow() + timedelta(hours=256)
        access_token = create_access_token(
            identity=device.id
        )  # dodati timestamp i expires_delta=expires

        return jsonify(
            {"access_token": access_token, "device_status": device.status.value}
        ), 200


@blp.route("/auth/register")
class Registration(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.arguments(DeviceRegistrationSchema, location="json")
    def post(self, header_data, payload_data):
        username = header_data.get("username")
        password = header_data.get("password")
        serial_number = payload_data.get("serial_number")

        device = DeviceModel.query.filter_by(serial_number=serial_number).first()

        if device:
            if device.status != DeviceStatus.DELETED:
                return jsonify(
                    {
                        "status": "Registration could not be completed due to a conflict. Serial number already exist.",
                        "device_status": device.status.value,
                    }
                ), 409
            if device.status == DeviceStatus.DELETED:
                device.status = DeviceStatus.CREATED
                db.session.commit()
                return jsonify(
                    {
                        "status": "Device status updated.",
                        "id": device.id,
                        "device_status": device.status.value,
                    }
                ), 201

        new_device = DeviceModel(
            username=username,
            password=pbkdf2_sha256.hash(password),
            serial_number=serial_number,
            status=DeviceStatus.CREATED,
        )
        db.session.add(new_device)
        db.session.commit()

        return jsonify(
            {
                "status": "New device created.",
                "id": new_device.id,
                "device_status": new_device.status.value,
            }
        ), 201


@blp.route("/auth/status/<int:id>")
class RegistrationStatus(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    def get(self, header_data, id):
        username = header_data.get("username")
        password = header_data.get("password")

        device = DeviceModel.query.get(id)
        if not device:
            return jsonify({"status": "Device not found or invalid ID provided."}), 404

        # device = DeviceModel.query.get_or_404(id)

        if device.username != username or not pbkdf2_sha256.verify(
            password, device.password
        ):
            return jsonify({"status": "Invalid credentials."}), 401

        if device.status != DeviceStatus.APPROVED:
            if device.status == DeviceStatus.BLACKLISTED:
                return jsonify(
                    {"status": "Access to the requested resource is forbidden."}
                ), 403

            return jsonify({"device_status": device.status.value}), 200

        access_token = create_access_token(identity=device.id)

        return jsonify(
            {"jwt_token": access_token, "device_status": device.status.value}
        ), 200


@blp.route("/auth/update")
class RegistrationUpdate(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.arguments(RegistrationUpdateSchema, location="json")
    def patch(self, header_data, payload_data):
        username = header_data.get("username")
        password = header_data.get("password")
        new_status = payload_data.get("status")
        device_id = payload_data.get("device_id")

        user = UserModel.query.filter_by(username=username).first()

        if not user:
            return jsonify(
                {"status": "User not found or invalid username provided."}
            ), 404

        if not pbkdf2_sha256.verify(password, user.password):
            return jsonify({"status": "Invalid password."}), 401

        device = DeviceModel.query.get(device_id)
        if not device:
            return jsonify({"status": "Device not found or invalid ID provided."}), 404

        try:
            device.status = DeviceStatus[new_status]
            db.session.commit()
            return jsonify({"status": "Device status updated seccessfully."}), 200
        except KeyError:
            return jsonify({"status": "Invalid device status provided."}), 400


@blp.route("/auth/delete/<int:id>")
class DeleteRegistration(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    def delete(self, header_data, id):
        username = header_data.get("username")
        password = header_data.get("password")

        device = DeviceModel.query.get(id)
        if not device:
            return jsonify({"status": "Device not found or invalid ID provided."}), 404

        # device = DeviceModel.query.get_or_404(id)

        if device.username != username or not pbkdf2_sha256.verify(
            password, device.password
        ):
            return jsonify({"status": "Invalid credentials."}), 401

        if device.status == DeviceStatus.BLACKLISTED:
            return jsonify(
                {"status": "Access to the requested resource is forbidden."}
            ), 403

        if device.status == DeviceStatus.DELETED:
            return jsonify({"status": "Device is already deleted."}), 403

        device.status = DeviceStatus.DELETED
        db.session.commit()

        return jsonify(
            {
                "status": "Device status updated seccessfully.",
                "device_status": device.status.value,
            }
        ), 200
