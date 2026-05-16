from collections import defaultdict

from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_hatchet_config.model.scheduler import HatchetServiceSchedulerModel
from homelab_pydantic import DatabaseType
from homelab_restic.model.frequency import BackupFrequency
from homelab_restic_service import ResticService
from pulumi import ResourceOptions

from .config import BackupConfig
from .hatchet.workflow.backup import (
    Backup,
    HatchetBackupConfig,
    HatchetBackupServiceModel,
)


class BackupService(ServiceWithConfigResourceBase[BackupConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[BackupConfig],
        *,
        opts: ResourceOptions,
        restic_service: ResticService,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        # TODO: Support pre-backup hook
        self.frequency_configs: defaultdict[BackupFrequency, list[str]] = defaultdict(
            list
        )
        self.hatchet_backup_service_config: dict[str, HatchetBackupServiceModel] = {}

        for service, resource in self.extractor_args.services.items():
            service_group = restic_service.service_groups.get(service)
            service_database_group = restic_service.service_database_groups.get(service)

            if not service_group and not service_database_group:
                continue

            self.frequency_configs[resource.model.backup.frequency].append(service)

            self.hatchet_backup_service_config[service] = HatchetBackupServiceModel(
                profiles=service_group or [],
                databases={
                    service_database_group_type: {
                        service_database.backup: service_database.name
                        for service_database in service_database_group_model
                    }
                    for service_database_group_type, service_database_group_model in service_database_group.items()
                }
                if service_database_group
                else {},
            )

        self.config.hatchet.config.root = {
            HatchetBackupConfig.CONFIG_KEY: HatchetBackupConfig(
                services=self.hatchet_backup_service_config
            ).model_dump(mode="json")
        }

        self.config.hatchet.scheduler.root = {
            frequency: HatchetServiceSchedulerModel(
                workflow=Backup.BACKUP_SERVICES,
                schedules=[self.config.schedule[frequency]],
                input={"services": services},
            )
            for frequency, services in self.frequency_configs.items()
        }

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
