from homelab_pydantic import AbsolutePath, HomelabBaseModel

from .continue_on import DaguDagStepContinueOnModel
from .executor import DaguDagStepExecutorModel
from .precondition import DaguDagStepPreConditionModel
from .run import DaguDagStepRunModel
from .script import DaguDagStepScriptModel


class DaguDagStepModel(HomelabBaseModel):
    name: str
    dir: AbsolutePath | None = None
    run: DaguDagStepRunModel
    script: DaguDagStepScriptModel | None = None
    continue_on: DaguDagStepContinueOnModel | None = None
    executor: DaguDagStepExecutorModel | None = None
    output: str | None = None
    depends: list[str] | None = None
    preconditions: list[DaguDagStepPreConditionModel] = []
