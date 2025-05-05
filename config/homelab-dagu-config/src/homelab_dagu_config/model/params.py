from __future__ import annotations

import typing
from enum import StrEnum, auto
from typing import ClassVar

from homelab_backup.config import BackupGlobalConfig
from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from ..model import DaguDagModel
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

    main: dict[str, str] = {}
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

    def to_params(self, dag: DaguDagModel) -> list[dict[str, str]] | None:
        from ..model.step.precondition import DaguDagStepPreConditionFullModel
        from ..model.step.run.command import (
            DaguDagStepRunCommandFullModel,
            DaguDagStepRunCommandModel,
            DaguDagStepRunCommandParamModel,
            DaguDagStepRunCommandParamTypeFullModel,
        )

        used_params = set()
        for step in dag.steps:
            run = step.run.root
            script = step.script
            preconditions = step.preconditions

            commands: list[DaguDagStepRunCommandFullModel] = []
            if isinstance(run, DaguDagStepRunCommandModel):
                commands += run.root
            if script and isinstance(script.root, DaguDagStepRunCommandModel):
                commands += script.root.root
            for precondition in preconditions:
                if isinstance(
                    precondition.root, DaguDagStepPreConditionFullModel
                ) and isinstance(
                    precondition.root.condition.root,
                    DaguDagStepRunCommandParamTypeFullModel,
                ):
                    commands.append(
                        DaguDagStepRunCommandFullModel(
                            DaguDagStepRunCommandParamModel(
                                param=precondition.root.condition
                            )
                        )
                    )

            for command in commands:
                root = command.root
                if isinstance(root, DaguDagStepRunCommandParamModel):
                    used_params.add(
                        root.param.root.type
                        if isinstance(
                            root.param.root, DaguDagStepRunCommandParamTypeFullModel
                        )
                        else root.param.root
                    )

        params = []
        for key_type, default_value in self.types.items():
            if key_type in used_params:
                param_value = self.PARAM_VALUE[key_type]
                params.append(
                    {
                        param_value[0]: default_value
                        if default_value is not None
                        else param_value[1]
                    }
                )
        for key_main, value in self.main.items():
            if key_main in used_params:
                params.append({key_main: value})

        return params or None
