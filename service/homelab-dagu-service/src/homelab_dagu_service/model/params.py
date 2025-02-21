from enum import StrEnum, auto
from typing import ClassVar

from homelab_backup.config import BackupConfig
from homelab_pydantic import HomelabBaseModel


class DaguDagParamType(StrEnum):
    BACKUP = auto()
    DEBUG = auto()


class DaguDagParamsModel(HomelabBaseModel):
    PARAM_VALUE: ClassVar[dict[DaguDagParamType, tuple[str, str]]] = {
        DaguDagParamType.BACKUP: (
            BackupConfig.BACKUP_KEY,
            BackupConfig.BACKUP_KEY_VALUE,
        ),
        DaguDagParamType.DEBUG: ("SLEEP_DURATION", "30m"),
    }

    main: dict[str, str] = {}
    types: dict[DaguDagParamType, str | None] = {}

    def __bool__(self) -> bool:
        return bool(self.main) or bool(self.types)

    def to_key_command_unchecked(self, key: str) -> str:
        return "${{{}}}".format(key)

    def to_key_command(self, key: DaguDagParamType | str) -> str:
        if isinstance(key, DaguDagParamType):
            self.types[key]
            return self.to_key_command_unchecked(self.PARAM_VALUE[key][0])

        else:
            self.main[key]
            return self.to_key_command_unchecked(key)

    def to_params(self) -> list[dict[str, str]]:
        return [{key: value} for key, value in self.main.items()] + [
            {self.PARAM_VALUE[key][0]: value or self.PARAM_VALUE[key][1]}
            for key, value in self.types.items()
        ]
