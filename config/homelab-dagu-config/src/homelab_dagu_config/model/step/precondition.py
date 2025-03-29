from typing import Any

from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class DaguDagStepPreConditionFullModel(HomelabBaseModel):
    condition: str
    expected: str

    def to_step(self) -> dict[str, Any]:
        return {"condition": self.condition, "expected": self.expected}


class DaguDagStepPreConditionModel(
    HomelabRootModel[DaguDagStepPreConditionFullModel | str]
):
    def to_step(self) -> str | dict[str, Any]:
        root = self.root
        if isinstance(root, DaguDagStepPreConditionFullModel):
            return root.to_step()
        else:
            return root
