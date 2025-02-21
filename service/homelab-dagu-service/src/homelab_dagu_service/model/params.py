from __future__ import annotations

import typing
from enum import StrEnum, auto
from typing import ClassVar

from homelab_backup.config import BackupConfig
from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from ..model import DaguDagModel


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

    def to_params(self, dag: DaguDagModel) -> list[dict[str, str]] | None:
        from ..model.step.command import (
            DaguDagStepCommandParamModel,
            DaguDagStepCommandParamTypeModel,
        )

        used_params = {
            (
                command.root.param.type
                if isinstance(command.root.param, DaguDagStepCommandParamTypeModel)
                else command.root.param
            )
            for step in dag.steps
            for command in step.command
            if isinstance(command.root, DaguDagStepCommandParamModel)
        }

        params = []
        for key, value in self.main.items():
            if key in used_params:
                params.append({key: value})
        for key, default_value in self.types.items():
            if key in used_params:
                param_value = self.PARAM_VALUE[key]
                params.append({param_value[0]: default_value or param_value[1]})

        return params or None
