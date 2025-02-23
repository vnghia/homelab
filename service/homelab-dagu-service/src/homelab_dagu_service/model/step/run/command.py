from __future__ import annotations

import typing
from typing import Any, Self

from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ...params import DaguDagParamsModel, DaguDagParamType

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepRunCommandParamTypeModel(HomelabBaseModel):
    type: DaguDagParamType


class DaguDagStepRunCommandParamModel(HomelabBaseModel):
    param: DaguDagStepRunCommandParamTypeModel | str

    def to_key(self) -> DaguDagParamType | str:
        param = self.param
        if isinstance(param, DaguDagStepRunCommandParamTypeModel):
            return param.type
        else:
            return param


class DaguDagStepRunCommandModel(
    HomelabRootModel[list[DaguDagStepRunCommandParamModel | str]]
):
    def __add__(self, other: Self) -> Self:
        return self.__class__(self.root + other.root)

    @classmethod
    def command_to_str(
        cls, command: DaguDagStepRunCommandParamModel | str, params: DaguDagParamsModel
    ) -> str:
        if isinstance(command, DaguDagStepRunCommandParamModel):
            return params.to_key_command(command.to_key())
        else:
            return command

    def to_run(
        self,
        dagu_service_: DaguService,
        params: DaguDagParamsModel,
    ) -> dict[str, Any]:
        return {
            "command": " ".join(
                self.command_to_str(command, params) for command in self.root
            )
        }
