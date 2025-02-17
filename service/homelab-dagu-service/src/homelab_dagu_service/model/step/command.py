import typing

from homelab_pydantic import HomelabBaseModel
from pydantic import RootModel

if typing.TYPE_CHECKING:
    from ..params import DaguDagParamsModel


class DaguDagStepCommandParamModel(HomelabBaseModel):
    param: str


class DaguDagStepCommandModel(RootModel[DaguDagStepCommandParamModel | str]):
    def to_str(self, params: "DaguDagParamsModel | None") -> str:
        root = self.root
        if isinstance(root, DaguDagStepCommandParamModel):
            if not params:
                raise ValueError("Dag params is None")
            return params.to_key_command(root.param)
        else:
            return root
