from __future__ import annotations

import typing
from enum import StrEnum, auto
from typing import ClassVar

from homelab_backup.config import BackupGlobalConfig
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from .step.run.command import DaguDagStepRunCommandParamTypeModel


class DaguDagParamType(StrEnum):
    BACKUP = auto()
    SNAPSHOT = auto()
    DEBUG = auto()


class DaguDagParamsModel(HomelabBaseModel):
    PARAM_VALUE: ClassVar[dict[DaguDagParamType, tuple[str, str]]] = {
        DaguDagParamType.BACKUP: (
            BackupGlobalConfig.BACKUP_KEY,
            BackupGlobalConfig.BACKUP_KEY_VALUE,
        ),
        DaguDagParamType.SNAPSHOT: (
            BackupGlobalConfig.SNAPSHOT_KEY,
            BackupGlobalConfig.SNAPSHOT_KEY_VALUE,
        ),
        DaguDagParamType.DEBUG: ("SLEEP_DURATION", "30m"),
    }

    main: dict[str, GlobalExtract] = {}
    types: dict[DaguDagParamType, str | None] = {}

    def __bool__(self) -> bool:
        return bool(self.main) or bool(self.types)

    def to_key_command_unchecked(self, key: DaguDagStepRunCommandParamTypeModel) -> str:
        from ..model.step.run.command import DaguDagStepRunCommandParamTypeFullModel

        root = key.root
        if isinstance(root, DaguDagStepRunCommandParamTypeFullModel):
            result = self.PARAM_VALUE[root.type][0]
            if not root.dollar:
                return result
            root = result
        return "${{{}}}".format(root)

    def check_key(
        self, key: DaguDagStepRunCommandParamTypeModel
    ) -> DaguDagStepRunCommandParamTypeModel:
        from ..model.step.run.command import DaguDagStepRunCommandParamTypeFullModel

        root = key.root
        if isinstance(root, DaguDagStepRunCommandParamTypeFullModel):
            self.types[root.type]
            return key
        self.main[root]
        return key

    def to_key_command(self, key: DaguDagStepRunCommandParamTypeModel) -> str:
        return self.to_key_command_unchecked(self.check_key(key))
