from __future__ import annotations

from typing import Self

from homelab_extract import GlobalExtract
from homelab_extract.transform.string import ExtractTransformString
from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ...params import DaguDagParamType


class DaguDagStepRunCommandParamTypeModel(HomelabBaseModel):
    type: DaguDagParamType
    dollar: bool = True


class DaguDagStepRunCommandParamModel(HomelabBaseModel):
    param: DaguDagStepRunCommandParamTypeModel | str
    transform: ExtractTransformString = ExtractTransformString()


class DaguDagStepRunCommandFullModel(
    HomelabRootModel[DaguDagStepRunCommandParamModel | GlobalExtract]
):
    pass


class DaguDagStepRunCommandModel(
    HomelabRootModel[list[DaguDagStepRunCommandFullModel]]
):
    def __add__(self, other: Self) -> Self:
        return self.__class__(self.root + other.root)
