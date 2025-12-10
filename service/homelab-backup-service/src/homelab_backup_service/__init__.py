import operator
from collections import defaultdict
from functools import reduce

from homelab_balite_service import BaliteService
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
    DaguDagStepRunCommandFullModel,
    DaguDagStepRunCommandModel,
    DaguDagStepRunCommandParamModel,
    DaguDagStepRunCommandParamTypeFullModel,
    DaguDagStepRunCommandParamTypeModel,
)
from homelab_dagu_config.model.step.run.subdag import (
    DaguDagStepRunSubdagModel,
    DaguDagStepRunSubdagParallelModel,
)
from homelab_dagu_config.model.step.script import DaguDagStepScriptModel
from homelab_dagu_service import DaguService
from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.database.type import DatabaseType
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_extract import GlobalExtract
from homelab_extract.transform.string import (
    ExtractTransformString,
    ExtractTransformStringTemplate,
)
from homelab_restic.model.frequency import BackupFrequency
from homelab_restic_service import ResticService
from pulumi import ResourceOptions

from .config import BackupConfig
from .config.service import BackupServiceConfig
from .model.service import BackupServiceModel, BackupServiceVolumeModel


class BackupService(ServiceWithConfigResourceBase[BackupConfig]):
    DEFAULT_BACKUP_MODEL = BackupServiceModel()
    DEFAULT_VOLUME_BACKUP_MODEL = BackupServiceVolumeModel()

    PRE_BACKUP_VOLUME_DAG_KEY = "pre-backup-volume"
    BACKUP_SERVICE_DAG_KEY = "service"
    BACKUP_ALL_DAG_KEY = "all"

    BACKUP_KEY = DaguDagParamsModel.PARAM_VALUE[DaguDagParamType.BACKUP][0]
    EXTRACT_CONFIG_STEP = "extract-config"
    BACKUP_CONFIG_OUTPUT = "BACKUP_CONFIG_OUTPUT"

    BACKUP_DATABASE_SUBDAGS = {
        DatabaseType.POSTGRES: BarmanService.name(),
        DatabaseType.SQLITE: BaliteService.name(),
    }

    def __init__(
        self,
        model: ServiceWithConfigModel[BackupConfig],
        *,
        opts: ResourceOptions,
        dagu_service: DaguService,
        restic_service: ResticService,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        pre_volume_backups = []

        backup_configs = {}
        self.frequency_configs: defaultdict[BackupFrequency, list[GlobalExtract]] = (
            defaultdict(list)
        )

        for service, resource in self.extractor_args.services.items():
            service_model = None
            if service in restic_service.service_groups:
                volume_model = None
                if (
                    dagu_service_config := dagu_service.get_service_config(resource)
                ) and (
                    (self.PRE_BACKUP_VOLUME_DAG_KEY in dagu_service_config.dag.root)
                    or (
                        dagu_service_config.docker
                        and self.PRE_BACKUP_VOLUME_DAG_KEY
                        in dagu_service_config.docker.dags
                    )
                ):
                    volume_model = BackupServiceVolumeModel(pre=True)
                    pre_volume_backups.append(
                        DaguDagStepModel(
                            name=service,
                            run=DaguDagStepRunModel(
                                DaguDagStepRunSubdagModel(
                                    service=service, dag=self.PRE_BACKUP_VOLUME_DAG_KEY
                                )
                            ),
                            preconditions=[
                                DaguDagStepPreConditionModel(
                                    DaguDagStepPreConditionFullModel(
                                        condition=DaguDagStepRunCommandParamTypeModel(
                                            DaguDagStepRunCommandParamTypeFullModel(
                                                type=DaguDagParamType.BACKUP
                                            )
                                        ),
                                        expected=service,
                                    )
                                )
                            ],
                            depends=[],
                        )
                    )
                service_model = self.DEFAULT_BACKUP_MODEL.__replace__(
                    volume=volume_model or self.DEFAULT_VOLUME_BACKUP_MODEL
                )
            if service in restic_service.service_database_groups:
                service_model = (
                    service_model or self.DEFAULT_BACKUP_MODEL
                ).__replace__(
                    databases={
                        type_: " ".join(names)
                        for type_, names in restic_service.service_database_groups[
                            service
                        ].items()
                    }
                )

            if service_model:
                backup_configs[service] = service_model
                self.frequency_configs[resource.model.backup.frequency].append(
                    GlobalExtract.from_simple(service)
                )
        self.backup_configs = BackupServiceConfig(backup_configs)

        self.config.dagu.dag.root[self.PRE_BACKUP_VOLUME_DAG_KEY] = DaguDagModel(
            name=self.PRE_BACKUP_VOLUME_DAG_KEY,
            path="{}-{}".format(self.name(), self.PRE_BACKUP_VOLUME_DAG_KEY),
            steps=pre_volume_backups,
            tags=[self.name()],
            params=DaguDagParamsModel(types={DaguDagParamType.BACKUP: ""}),
        )

        self.config.dagu.dag.root[self.BACKUP_SERVICE_DAG_KEY] = DaguDagModel(
            name=self.BACKUP_SERVICE_DAG_KEY,
            path="{}-{}".format(self.name(), self.BACKUP_SERVICE_DAG_KEY),
            max_active_runs=1,
            steps=[
                DaguDagStepModel(
                    name=self.EXTRACT_CONFIG_STEP,
                    dir=dagu_service.get_tmp_dir(),
                    run=DaguDagStepRunModel(
                        DaguDagStepRunCommandModel(
                            [
                                DaguDagStepRunCommandFullModel(
                                    GlobalExtract.from_simple("/bin/bash")
                                )
                            ]
                        )
                    ),
                    script=DaguDagStepScriptModel(
                        DaguDagStepRunCommandModel(
                            [
                                DaguDagStepRunCommandFullModel(
                                    GlobalExtract.from_simple(
                                        "echo '{}'".format(
                                            self.backup_configs.model_dump_json(
                                                exclude_unset=True
                                            )
                                        )
                                    )
                                ),
                                DaguDagStepRunCommandFullModel(
                                    GlobalExtract.from_simple("|")
                                ),
                                DaguDagStepRunCommandFullModel(
                                    GlobalExtract.from_simple("jq")
                                ),
                                DaguDagStepRunCommandFullModel(
                                    GlobalExtract.from_simple("-c")
                                ),
                                DaguDagStepRunCommandFullModel(
                                    DaguDagStepRunCommandParamModel(
                                        param=DaguDagStepRunCommandParamTypeModel(
                                            DaguDagStepRunCommandParamTypeFullModel(
                                                type=DaguDagParamType.BACKUP
                                            )
                                        ),
                                        transform=ExtractTransformString(
                                            template=ExtractTransformStringTemplate(
                                                '".{value}"'
                                            )
                                        ),
                                    )
                                ),
                            ]
                        )
                    ),
                    output=self.BACKUP_CONFIG_OUTPUT,
                ),
                DaguDagStepModel(
                    name=self.PRE_BACKUP_VOLUME_DAG_KEY,
                    run=DaguDagStepRunModel(
                        DaguDagStepRunSubdagModel(
                            service=self.name(),
                            dag=self.PRE_BACKUP_VOLUME_DAG_KEY,
                            params=DaguDagParamsModel(
                                types={
                                    DaguDagParamType.BACKUP: "${{{}}}".format(
                                        self.BACKUP_KEY
                                    )
                                }
                            ),
                        )
                    ),
                    continue_on=DaguDagStepContinueOnModel(skipped=True),
                    depends=[self.EXTRACT_CONFIG_STEP],
                    preconditions=[
                        DaguDagStepPreConditionModel(
                            DaguDagStepPreConditionFullModel(
                                condition=DaguDagStepRunCommandParamTypeModel(
                                    "${{{}}}".format(self.BACKUP_CONFIG_OUTPUT)
                                ),
                                expected='re:.*"pre".*',
                            )
                        )
                    ],
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
                                        self.BACKUP_KEY
                                    )
                                }
                            ),
                        )
                    ),
                    depends=[self.PRE_BACKUP_VOLUME_DAG_KEY],
                    preconditions=[
                        DaguDagStepPreConditionModel(
                            DaguDagStepPreConditionFullModel(
                                condition=DaguDagStepRunCommandParamTypeModel(
                                    "${{{}}}".format(self.BACKUP_CONFIG_OUTPUT)
                                ),
                                expected='re:.*"volume".*',
                            )
                        )
                    ],
                ),
                *reduce(
                    operator.iadd,
                    [
                        # TODO: Remove this after precondition and output json issues are fixed
                        [
                            DaguDagStepModel(
                                name=self.get_extract_database_step(type_),
                                run=DaguDagStepRunModel(
                                    DaguDagStepRunCommandModel(
                                        [
                                            DaguDagStepRunCommandFullModel(
                                                GlobalExtract.from_simple(
                                                    ".databases.{} | select(.!=null)".format(
                                                        type_.value
                                                    )
                                                )
                                            )
                                        ]
                                    )
                                ),
                                script=DaguDagStepScriptModel(
                                    GlobalExtract.from_simple(
                                        "${{{}}}".format(self.BACKUP_CONFIG_OUTPUT)
                                    )
                                ),
                                executor=DaguDagStepExecutorModel(
                                    DaguDagStepJqExecutorModel()
                                ),
                                depends=[self.EXTRACT_CONFIG_STEP],
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
                                            condition=DaguDagStepRunCommandParamTypeModel(
                                                "${{{}}}".format(
                                                    self.get_extract_database_step_output(
                                                        type_
                                                    )
                                                )
                                            ),
                                            expected="re:.+",
                                        )
                                    )
                                ],
                            ),
                        ]
                        for type_, service in self.BACKUP_DATABASE_SUBDAGS.items()
                    ],
                ),
                DaguDagStepModel(
                    name="backup-database",
                    run=DaguDagStepRunModel(
                        DaguDagStepRunSubdagModel(
                            service=restic_service.name(),
                            dag=self.name(),
                            params=DaguDagParamsModel(
                                types={
                                    DaguDagParamType.BACKUP: "${{{}}}-database".format(
                                        self.BACKUP_KEY
                                    )
                                }
                            ),
                        )
                    ),
                    depends=[
                        self.get_backup_database_step(type_)
                        for type_ in self.BACKUP_DATABASE_SUBDAGS
                    ],
                    preconditions=[
                        DaguDagStepPreConditionModel(
                            DaguDagStepPreConditionFullModel(
                                condition=DaguDagStepRunCommandParamTypeModel(
                                    "${{{}}}".format(self.BACKUP_CONFIG_OUTPUT)
                                ),
                                expected='re:.*"databases".*',
                            )
                        )
                    ],
                ),
            ],
            tags=[self.name()],
            params=DaguDagParamsModel(types={DaguDagParamType.BACKUP: ""}),
        )

        for frequency, services in self.frequency_configs.items():
            frequency_key = "{}-{}".format(self.BACKUP_ALL_DAG_KEY, frequency)
            self.config.dagu.dag.root[frequency_key] = DaguDagModel(
                name=frequency_key,
                path="{}-{}".format(self.name(), frequency_key),
                max_active_runs=1,
                schedule=self.config.schedule[frequency],
                steps=[
                    DaguDagStepModel(
                        name="all",
                        run=DaguDagStepRunModel(
                            DaguDagStepRunSubdagModel(
                                service=self.name(),
                                dag="service",
                                parallel=DaguDagStepRunSubdagParallelModel(
                                    param=DaguDagParamType.BACKUP,
                                    items=services,
                                    max_concurrent=self.config.max_concurent,
                                ),
                            )
                        ),
                    )
                ],
                tags=[self.name()],
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
