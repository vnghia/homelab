from typing import Any

from homelab_pydantic import HomelabBaseModel


class DaguDagStepContinueOnModel(HomelabBaseModel):
    failure: bool = False
    skipped: bool = False

    def to_step(self) -> dict[str, Any]:
        return {"continueOn": {"failure": self.failure, "skipped": self.skipped}}
