from marshmallow import Schema, fields


class HeaderSchema(Schema):
    username = fields.String(data_key="username", required=True)
    password = fields.String(data_key="password", required=True)


class DeviceRegistrationSchema(Schema):
    serial_number = fields.String(required=True)


class RegistrationUpdateSchema(Schema):
    status = fields.String(required=True)
    device_id = fields.Integer(required=True)
