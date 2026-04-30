from typing import Any

from homelab_pydantic import HomelabBaseModel


class DaguDagStepContinueOnModel(HomelabBaseModel):
    failure: bool = False
    skipped: bool = False
    output: list[str] = []
    mark_success: bool = False

    def to_step(self) -> dict[str, Any]:
        return {
            "continueOn": ({"failure": self.failure} if self.failure else {})
            | ({"skipped": self.skipped} if self.skipped else {})
            | ({"output": self.output} if self.output else {})
            | ({"markSuccess": self.mark_success} if self.mark_success else {})
        }
