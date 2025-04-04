import operator
from functools import reduce

from homelab_barman_service import BarmanService
from homelab_dagu_config.model import DaguDagModel
from homelab_dagu_config.model.params import DaguDagParamsModel, DaguDagParamType
from homelab_dagu_config.model.step import DaguDagStepModel
from homelab_dagu_config.model.step.continue_on import DaguDagStepContinueOnModel
from homelab_dagu_config.model.step.executor import DaguDagStepExecutorModel
from homelab_dagu_config.model.step.executor.jq import DaguDagStepJqExecutorModel
from homelab_dagu_config.model.step.precondition import (
    DaguDagStepPreConditionFullModel,
    DaguDagStepPreConditionModel,
)
from homelab_dagu_config.model.step.run import DaguDagStepRunModel
from homelab_dagu_config.model.step.run.command import (
    DaguDagStepRunCommandModel,
    DaguDagStepRunCommandParamModel,
    DaguDagStepRunCommandParamTypeModel,
)
from homelab_dagu_config.model.step.run.subdag import DaguDagStepRunSubdagModel
from homelab_dagu_config.model.step.script import DaguDagStepScriptModel
from homelab_dagu_service import DaguService
from homelab_dagu_service.model import DaguDagModelBuilder
from homelab_docker.model.database.type import DatabaseType
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_extract.transform.string import ExtractTransformString
from homelab_restic_service import ResticService
from pulumi import ResourceOptions

from .config import BackupConfig
from .config.service import BackupServiceConfig
from .model.service import BackupServiceModel


class BackupService(ServiceWithConfigResourceBase[BackupConfig]):
    BARMAN_BACKUP_KEY = "BARMAN_BACKUP_KEY"

    DEFAULT_BACKUP_MODEL = BackupServiceModel()

    BACKUP_CONFIG_OUTPUT = "BACKUP_CONFIG_OUTPUT"
    BACKUP_VOLUME_CONFIG_OUTPUT = "BACKUP_VOLUME_CONFIG_OUTPUT"

    BACKUP_DATABASE_SUBDAGS = {DatabaseType.POSTGRES: BarmanService.name()}

    def __init__(
        self,
        model: ServiceWithConfigModel[BackupConfig],
        *,
        opts: ResourceOptions | None,
        dagu_service: DaguService,
        barman_service: BarmanService,
        restic_service: ResticService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        backup_configs = {}
        for service in self.SERVICES.keys():
            service_model = self.DEFAULT_BACKUP_MODEL.model_copy()
            if service in restic_service.service_groups:
                service_model = service_model.__replace__(volume=True)
            if service in restic_service.service_database_groups:
                service_model = service_model.__replace__(
                    databases={
                        type_: " ".join(names)
                        for type_, names in restic_service.service_database_groups[
                            service
                        ].items()
                    }
                )

            if service_model != self.DEFAULT_BACKUP_MODEL:
                backup_configs[service] = service_model
        self.backup_configs = BackupServiceConfig(backup_configs)

        self.backup_service = DaguDagModel(
            name="service",
            path="{}-service".format(self.name()),
            max_active_runs=1,
            steps=[
                DaguDagStepModel(
                    name="extract-config",
                    dir=dagu_service.get_tmp_dir(),
                    run=DaguDagStepRunModel(DaguDagStepRunCommandModel(["/bin/bash"])),
                    script=DaguDagStepScriptModel(
                        DaguDagStepRunCommandModel(
                            [
                                "echo '{}'".format(
                                    self.backup_configs.model_dump_json(
                                        exclude_unset=True
                                    )
                                ),
                                "|",
                                "jq",
                                "-c",
                                DaguDagStepRunCommandParamModel(
                                    param=DaguDagStepRunCommandParamTypeModel(
                                        type=DaguDagParamType.BACKUP
                                    ),
                                    transform=ExtractTransformString(
                                        template='".{value}"'
                                    ),
                                ),
                            ]
                        )
                    ),
                    output=self.BACKUP_CONFIG_OUTPUT,
                ),
                DaguDagStepModel(
                    name="extract-volume",
                    run=DaguDagStepRunModel(DaguDagStepRunCommandModel([".volume"])),
                    script=DaguDagStepScriptModel(
                        "${{{}}}".format(self.BACKUP_CONFIG_OUTPUT)
                    ),
                    executor=DaguDagStepExecutorModel(DaguDagStepJqExecutorModel()),
                    depends=["extract-config"],
                    output=self.BACKUP_VOLUME_CONFIG_OUTPUT,
                ),
                DaguDagStepModel(
                    name="backup-volume",
                    run=DaguDagStepRunModel(
                        DaguDagStepRunSubdagModel(
                            service=restic_service.name(),
                            dag=self.name(),
                            params=DaguDagParamsModel(
                                types={
                                    DaguDagParamType.BACKUP: "${{{}}}".format(
                                        DaguDagParamsModel.PARAM_VALUE[
                                            DaguDagParamType.BACKUP
                                        ][0]
                                    )
                                }
                            ),
                        )
                    ),
                    depends=["extract-volume"],
                    preconditions=[
                        DaguDagStepPreConditionModel(
                            DaguDagStepPreConditionFullModel(
                                condition="${{{}}}".format(
                                    self.BACKUP_VOLUME_CONFIG_OUTPUT
                                ),
                                expected="true",
                            )
                        )
                    ],
                ),
            ]
            + reduce(
                operator.add,
                [
                    [
                        DaguDagStepModel(
                            name=self.get_extract_database_step(type_),
                            run=DaguDagStepRunModel(
                                DaguDagStepRunCommandModel(
                                    [
                                        ".databases.{} | select(.!=null)".format(
                                            type_.value
                                        )
                                    ]
                                )
                            ),
                            script=DaguDagStepScriptModel(
                                "${{{}}}".format(self.BACKUP_CONFIG_OUTPUT)
                            ),
                            executor=DaguDagStepExecutorModel(
                                DaguDagStepJqExecutorModel()
                            ),
                            depends=["extract-config"],
                            output=self.get_extract_database_step_output(type_),
                        ),
                        DaguDagStepModel(
                            name=self.get_backup_database_step(type_),
                            run=DaguDagStepRunModel(
                                DaguDagStepRunSubdagModel(
                                    service=service,
                                    dag=self.name(),
                                    params=DaguDagParamsModel(
                                        types={
                                            DaguDagParamType.BACKUP: "${{{}}}".format(
                                                self.get_extract_database_step_output(
                                                    type_
                                                )
                                            )
                                        }
                                    ),
                                )
                            ),
                            depends=[self.get_extract_database_step(type_)],
                            continue_on=DaguDagStepContinueOnModel(skipped=True),
                            preconditions=[
                                DaguDagStepPreConditionModel(
                                    DaguDagStepPreConditionFullModel(
                                        condition="${{{}}}".format(
                                            self.get_extract_database_step_output(type_)
                                        ),
                                        expected="re:.+",
                                    )
                                )
                            ],
                        ),
                    ]
                    for type_, service in self.BACKUP_DATABASE_SUBDAGS.items()
                ],
            )
            + [
                DaguDagStepModel(
                    name="backup-database",
                    run=DaguDagStepRunModel(
                        DaguDagStepRunSubdagModel(
                            service=restic_service.name(),
                            dag=self.name(),
                            params=DaguDagParamsModel(
                                types={
                                    DaguDagParamType.BACKUP: "${{{}}}-database".format(
                                        DaguDagParamsModel.PARAM_VALUE[
                                            DaguDagParamType.BACKUP
                                        ][0]
                                    )
                                }
                            ),
                        )
                    ),
                    depends=[
                        self.get_backup_database_step(type_)
                        for type_ in self.BACKUP_DATABASE_SUBDAGS.keys()
                    ],
                    preconditions=[
                        DaguDagStepPreConditionModel(
                            DaguDagStepPreConditionFullModel(
                                condition="${{{}}}".format(self.BACKUP_CONFIG_OUTPUT),
                                expected='re:.*"databases".*',
                            )
                        )
                    ],
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

        self.backup_all = DaguDagModel(
            name="all",
            path="{}-all".format(self.name()),
            max_active_runs=1,
            schedule=self.config.schedule,
            steps=[
                DaguDagStepModel(
                    name=service,
                    run=DaguDagStepRunModel(
                        DaguDagStepRunSubdagModel(
                            service=self.name(),
                            dag="service",
                            params=DaguDagParamsModel(
                                types={DaguDagParamType.BACKUP: service}
                            ),
                        )
                    ),
                )
                for service in self.backup_configs.root.keys()
            ],
            tags=[self.name()],
        )

        DaguDagModelBuilder(self.backup_all).build_resource(
            self.backup_all.name,
            opts=self.child_opts,
            main_service=self,
            dagu_service=dagu_service,
        )

        self.register_outputs({})

    @classmethod
    def get_extract_database_step(cls, type_: DatabaseType) -> str:
        return "extract-database-{}".format(type_.value)

    @classmethod
    def get_extract_database_step_output(cls, type_: DatabaseType) -> str:
        return "BACKUP_DATABASE_{}_CONFIG_OUTPUT".format(type_.value.upper())

    @classmethod
    def get_backup_database_step(cls, type_: DatabaseType) -> str:
        return "backup-database-{}".format(type_.value)
