from homelab_pydantic import HomelabRootModel

from .run.command import DaguDagStepRunCommandModel


class DaguDagStepScriptModel(HomelabRootModel[str | DaguDagStepRunCommandModel]):
    pass
