from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabRootModel

from .run.command import DaguDagStepRunCommandModel


class DaguDagStepScriptModel(
    HomelabRootModel[GlobalExtract | DaguDagStepRunCommandModel]
):
    pass
