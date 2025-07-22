from __future__ import annotations

from homelab_dagu_config.model import DaguDagModel
from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step.precondition import (
    DaguDagStepPreConditionFullModel,
)
from homelab_dagu_config.model.step.run.command import (
    DaguDagStepRunCommandFullModel,
    DaguDagStepRunCommandModel,
    DaguDagStepRunCommandParamModel,
    DaguDagStepRunCommandParamTypeFullModel,
)
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic.model import HomelabRootModel
from pulumi import Output


class DaguDagParamsModelBuilder(HomelabRootModel[DaguDagParamsModel]):
    def to_params(
        self, dag: DaguDagModel, main_service: ServiceResourceBase
    ) -> dict[str, Output[str]] | None:
        model = self.root

        used_params = set()
        for step in dag.steps:
            run = step.run.root
            script = step.script
            preconditions = step.preconditions

            commands: list[DaguDagStepRunCommandFullModel] = []
            if isinstance(run, DaguDagStepRunCommandModel):
                commands += run.root
            if script and isinstance(script.root, DaguDagStepRunCommandModel):
                commands += script.root.root
            for precondition in preconditions:
                if isinstance(
                    precondition.root, DaguDagStepPreConditionFullModel
                ) and isinstance(
                    precondition.root.condition.root,
                    DaguDagStepRunCommandParamTypeFullModel,
                ):
                    commands.append(
                        DaguDagStepRunCommandFullModel(
                            DaguDagStepRunCommandParamModel(
                                param=precondition.root.condition
                            )
                        )
                    )

            for command in commands:
                root = command.root
                if isinstance(root, DaguDagStepRunCommandParamModel):
                    used_params.add(
                        root.param.root.type
                        if isinstance(
                            root.param.root, DaguDagStepRunCommandParamTypeFullModel
                        )
                        else root.param.root
                    )

        params = {
            model.PARAM_VALUE[key_type][0]: Output.from_input(
                default_value
                if default_value is not None
                else model.PARAM_VALUE[key_type][1]
            )
            for key_type, default_value in model.types.items()
            if key_type in used_params
        } | {
            key_main: GlobalExtractor(value).extract_str(main_service, None)
            for key_main, value in model.main.items()
            if key_main in used_params
        }

        return params or None
