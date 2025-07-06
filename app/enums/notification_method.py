from enum import Enum

class NotificationMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"