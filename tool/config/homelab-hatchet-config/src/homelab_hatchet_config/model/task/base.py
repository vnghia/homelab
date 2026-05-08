from homelab_pydantic import HomelabBaseModel


class HatchetTaskBaseModel(HomelabBaseModel):
    workflow: bool = False
    schedules: list[str] = []

    @property
    def should_workflow(self) -> bool:
        return self.workflow or not self.schedules
