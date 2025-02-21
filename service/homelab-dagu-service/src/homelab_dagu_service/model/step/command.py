from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ..params import DaguDagParamsModel, DaguDagParamType


class DaguDagStepCommandParamTypeModel(HomelabBaseModel):
    type: DaguDagParamType


class DaguDagStepCommandParamModel(HomelabBaseModel):
    param: DaguDagStepCommandParamTypeModel | str

    def to_key(self) -> DaguDagParamType | str:
        param = self.param
        if isinstance(param, DaguDagStepCommandParamTypeModel):
            return param.type
        else:
            return param


class DaguDagStepCommandModel(HomelabRootModel[DaguDagStepCommandParamModel | str]):
    def to_str(self, params: DaguDagParamsModel | None) -> str:
        root = self.root
        if isinstance(root, DaguDagStepCommandParamModel):
            if not params:
                raise ValueError("Dag params is None")
            return params.to_key_command(root.to_key())
        else:
            return root
