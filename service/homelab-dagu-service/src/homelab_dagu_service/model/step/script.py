from __future__ import annotations

import typing

from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step.run.command import DaguDagStepRunCommandModel
from homelab_dagu_config.model.step.script import DaguDagStepScriptModel
from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_pydantic.model import HomelabRootModel
from pulumi import Output

from homelab_dagu_service.model.step.run.command import (
    DaguDagStepRunCommandModelBuilder,
)

if typing.TYPE_CHECKING:
    from ... import DaguService


class DaguDagStepScriptModelBuilder(HomelabRootModel[DaguDagStepScriptModel]):
    def to_script(
        self,
        params: DaguDagParamsModel,
        extractor_args: ExtractorArgs,
        dagu_service: DaguService,
    ) -> Output[str]:
        root = self.root.root
        if isinstance(root, DaguDagStepRunCommandModel):
            return DaguDagStepRunCommandModelBuilder(root).to_command(
                params, extractor_args
            )
        return GlobalExtractor(root).extract_str(extractor_args)
