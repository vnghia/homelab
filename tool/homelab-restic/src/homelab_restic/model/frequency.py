from enum import StrEnum, auto


class BackupFrequency(StrEnum):
    HOURLY = auto()
    DAILY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    YEARLY = auto()
