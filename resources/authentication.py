from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from schemas import (
    HeaderSchema,
    DeviceRegistrationSchema,
    RegistrationUpdateSchema,
    DeviceSchema,
    DeviceTokenSchema,
)

from models import DeviceModel, DeviceStatus, UserModel
from db import db

# from datetime import datetime, timedelta

blp = Blueprint(
    "auth", __name__, description="Registration and login operations for devices."
)

device_schema = DeviceSchema()
login_schema = DeviceTokenSchema()


@blp.route("/auth/login/<int:id>")
class Login(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.response(200, DeviceTokenSchema)
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
            if device.status == DeviceStatus.BLACKLISTED:
                abort(403, message="Access to the requested resource is forbidden.")

            if device.status == DeviceStatus.DELETED:
                abort(
                    401,
                    message="The device cannot be logged in because the account has been deleted. "
                    "Please register again.",
                )

        access_token = create_access_token(identity=device.id)

        response = login_schema.dump({"access_token": access_token, "device": device})

        return jsonify(response), 200


@blp.route("/auth/register")
class Registration(MethodView):
    @blp.arguments(HeaderSchema, location="headers")
    @blp.arguments(DeviceRegistrationSchema, location="json")
    @blp.response(201, DeviceTokenSchema)
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
                device.usermane = username
                device.password = pbkdf2_sha256.hash(password)
                try:
                    db.session.commit()
                except SQLAlchemyError:
                    abort(500, message="An error occured while updating device.")

                access_token = create_access_token(identity=device.id)

                response = login_schema.dump(
                    {"access_token": access_token, "device": device}
                )
                return jsonify(response), 201

        new_device = DeviceModel(
            username=username,
            password=pbkdf2_sha256.hash(password),
            serial_number=serial_number,
            status=DeviceStatus.CREATED,
        )
        try:
            db.session.add(new_device)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting new device.")

        access_token = create_access_token(identity=new_device.id)

        response = login_schema.dump(
            {"access_token": access_token, "device": new_device}
        )
        return jsonify(response), 201


@blp.route("/auth/status")
class RegistrationStatus(MethodView):
    @jwt_required()
    @blp.response(200, DeviceSchema)
    def get(self):
        device_id = get_jwt_identity()

        device = DeviceModel.query.get(device_id)
        if not device:
            abort(404, message="Device not found.")

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
    @jwt_required()
    @blp.arguments(RegistrationUpdateSchema, location="json")
    @blp.response(200, DeviceSchema)
    def patch(self, payload_data):
        new_status = payload_data.get("status")
        device_id = payload_data.get("device_id")

        user_id = get_jwt_identity()

        user = UserModel.query.filter_by(id=user_id).first()

        if not user:
            abort(404, message="User not found.")

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
        except SQLAlchemyError:
            abort(500, message="An error occured while updating device.")


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
        try:
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while updating device.")

        device_json = device_schema.dump(device)
        return jsonify(device_json), 200
