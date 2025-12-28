from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from .run.command import DaguDagStepRunCommandParamTypeModel

if typing.TYPE_CHECKING:
    from ..params import DaguDagParamsModel


class DaguDagStepPreConditionFullModel(HomelabBaseModel):
    condition: DaguDagStepRunCommandParamTypeModel
    expected: str
    negate: bool | None = None

    def to_step(self, params: DaguDagParamsModel) -> dict[str, Any]:
        return {
            "condition": self.condition.root
            if isinstance(self.condition.root, str)
            else params.to_key_command(self.condition),
            "expected": self.expected,
        } | ({"negate": self.negate} if self.negate else {})


class DaguDagStepPreConditionModel(
    HomelabRootModel[DaguDagStepPreConditionFullModel | str]
):
    def to_step(self, params: DaguDagParamsModel) -> str | dict[str, Any]:
        root = self.root
        if isinstance(root, DaguDagStepPreConditionFullModel):
            return root.to_step(params)
        return root
