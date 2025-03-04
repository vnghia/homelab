from homelab_backup.config import BackupConfig
from homelab_barman_service import BarmanService
from homelab_dagu_config.model import DaguDagModel
from homelab_dagu_config.model.step import DaguDagStepModel
from homelab_dagu_config.model.step.continue_on import DaguDagStepContinueOnModel
from homelab_dagu_config.model.step.run import DaguDagStepRunModel
from homelab_dagu_config.model.step.run.subdag import DaguDagStepRunSubdagModel
from homelab_dagu_service import DaguService
from homelab_dagu_service.model import DaguDagModelBuilder
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_restic_service import ResticService
from pulumi import ResourceOptions


class BackupService(ServiceWithConfigResourceBase[BackupConfig]):
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

        self.build_containers()

        self.backup_dag = DaguDagModelBuilder(
            DaguDagModel(
                name=self.name(),
                group=self.name(),
                tags=self.config.tags,
                schedule=self.config.schedule,
                max_active_runs=1,
                steps=[
                    DaguDagStepModel(
                        name=barman_service.name(),
                        continue_on=DaguDagStepContinueOnModel(failure=True),
                        run=DaguDagStepRunModel(
                            DaguDagStepRunSubdagModel(
                                service=barman_service.name(), dag=self.name()
                            )
                        ),
                    ),
                    DaguDagStepModel(
                        name=restic_service.name(),
                        run=DaguDagStepRunModel(
                            DaguDagStepRunSubdagModel(
                                service=restic_service.name(), dag=self.name()
                            )
                        ),
                    ),
                ],
            )
        ).build_resource(
            self.name(),
            opts=self.child_opts,
            main_service=self,
            dagu_service=dagu_service,
        )

        self.register_outputs({})
