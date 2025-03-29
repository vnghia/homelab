import json

from homelab_barman_service import BarmanService
from homelab_dagu_config.model import DaguDagModel
from homelab_dagu_config.model.params import DaguDagParamsModel, DaguDagParamType
from homelab_dagu_config.model.step import DaguDagStepModel
from homelab_dagu_config.model.step.run import DaguDagStepRunModel
from homelab_dagu_config.model.step.run.command import (
    DaguDagStepRunCommandModel,
    DaguDagStepRunCommandParamModel,
    DaguDagStepRunCommandParamTypeModel,
)
from homelab_dagu_config.model.step.script import DaguDagStepScriptModel
from homelab_dagu_service import DaguService
from homelab_dagu_service.model import DaguDagModelBuilder
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import BackupConfig


class BackupService(ServiceWithConfigResourceBase[BackupConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[BackupConfig],
        *,
        opts: ResourceOptions | None,
        dagu_service: DaguService,
        barman_service: BarmanService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.backup_service = DaguDagModel(
            name="service",
            path="{}-service".format(self.name()),
            steps=[
                DaguDagStepModel(
                    name="extract-{}".format(barman_service.name()),
                    dir=dagu_service.get_tmp_dir(),
                    run=DaguDagStepRunModel(DaguDagStepRunCommandModel(["/bin/bash"])),
                    script=DaguDagStepScriptModel(
                        DaguDagStepRunCommandModel(
                            [
                                "echo '{}'".format(
                                    json.dumps(
                                        barman_service.service_maps, sort_keys=True
                                    )
                                ),
                                "|",
                                "jq",
                                "-r",
                                DaguDagStepRunCommandParamModel(
                                    param=DaguDagStepRunCommandParamTypeModel(
                                        type=DaguDagParamType.BACKUP
                                    ),
                                    template='".{value} | if . == null then \\"\\" else join(\\" \\") end"',
                                ),
                            ]
                        )
                    ),
                )
            ],
            tags=[self.name()],
            params=DaguDagParamsModel(types={DaguDagParamType.BACKUP: ""}),
        )

        DaguDagModelBuilder(self.backup_service).build_resource(
            self.backup_service.name,
            opts=self.child_opts,
            main_service=self,
            dagu_service=dagu_service,
        )

        self.register_outputs({})
