from enum import Enum


class DeviceStatus(Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    DELETED = "DELETED"
    BLACKLISTED = "BLACKLISTED"
