from homelab_pydantic import HomelabBaseModel

from ...model.step.run.command import DaguDagStepRunCommandModel


class DaguDagStepRunCommandsConfig(HomelabBaseModel):
    prefix: DaguDagStepRunCommandModel = DaguDagStepRunCommandModel([])
    suffix: DaguDagStepRunCommandModel = DaguDagStepRunCommandModel([])
