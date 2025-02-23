from homelab_backup.config import BackupConfig
from homelab_barman_service import BarmanService
from homelab_dagu_service import DaguService
from homelab_dagu_service.model import DaguDagModel
from homelab_dagu_service.model.step import DaguDagStepModel
from homelab_dagu_service.model.step.continue_on import DaguDagStepContinueOnModel
from homelab_dagu_service.model.step.run import DaguDagStepRunModel
from homelab_dagu_service.model.step.run.subdag import DaguDagStepRunSubdagModel
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

        self.build_containers(options={})

        self.backup_dag = DaguDagModel(
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
                            dag="{}-{}".format(barman_service.name(), self.name())
                        )
                    ),
                ),
                DaguDagStepModel(
                    name=restic_service.name(),
                    run=DaguDagStepRunModel(
                        DaguDagStepRunSubdagModel(
                            dag="{}-{}".format(restic_service.name(), self.name())
                        )
                    ),
                ),
            ],
        ).build_resource(
            self.name(),
            opts=self.child_opts,
            main_service=self,
            dagu_service=dagu_service,
            container_model_build_args=None,
            dotenvs=None,
        )

        self.register_outputs({})
