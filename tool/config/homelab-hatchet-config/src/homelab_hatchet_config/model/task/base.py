from homelab_pydantic import HomelabBaseModel


class HatchetTaskBaseModel(HomelabBaseModel):
    schedules: list[str] = []
