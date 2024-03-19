from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from models import DeviceStatus


class HeaderSchema(Schema):
    username = fields.String(data_key="username", required=True)
    password = fields.String(data_key="password", required=True)


class DeviceRegistrationSchema(Schema):
    serial_number = fields.String(required=True)


class RegistrationUpdateSchema(Schema):
    status = fields.String(required=True)
    device_id = fields.Integer(required=True)


class DeviceSchema(Schema):
    id = fields.Integer(dump_only=True)
    serial_number = fields.String(required=True)
    username = fields.String(required=True)
    password = fields.String(load_only=True)
    status = EnumField(DeviceStatus, required=True)


class DeviceTokenSchema(Schema):
    access_token = fields.String(required=True)
    device = fields.Nested(DeviceSchema)


class DataSchema(Schema):
    value = fields.Float(required=True)
    unit = fields.String(required=True)
    name = fields.String(required=True)
    time = fields.DateTime()


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(load_only=True)


class UserLoginSchema(Schema):
    access_token = fields.String(required=True)
    user = fields.Nested(UserSchema)
