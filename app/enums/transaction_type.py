from enum import Enum


class TransactionType(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"