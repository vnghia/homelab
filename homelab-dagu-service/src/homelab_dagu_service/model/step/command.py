import typing

from pydantic import BaseModel, RootModel

if typing.TYPE_CHECKING:
    from ..params import DaguDagParamsModel


class DaguDagStepCommandParamModel(BaseModel):
    param: str


class DaguDagStepCommandModel(RootModel[DaguDagStepCommandParamModel | str]):
    def to_str(self, params: "DaguDagParamsModel") -> str:
        root = self.root
        if isinstance(root, DaguDagStepCommandParamModel):
            return params.to_key_command(root.param)
        else:
            return root
