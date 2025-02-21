from homelab_pydantic import HomelabBaseModel

from homelab_dagu_service.model.step.command import DaguDagStepCommandModel


class DaguDagStepCommandConfig(HomelabBaseModel):
    prefix: list[DaguDagStepCommandModel] = []
    suffix: list[DaguDagStepCommandModel] = []
