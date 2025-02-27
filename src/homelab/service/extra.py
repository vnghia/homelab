from collections import defaultdict

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_integration.s3 import S3ServiceConfig
from homelab_pydantic import HomelabBaseModel
from homelab_traefik_service import TraefikService
from homelab_traefik_service.config.service import TraefikServiceConfig
from pulumi import ResourceOptions


class ExtraConfig(HomelabBaseModel):
    traefik: TraefikServiceConfig = TraefikServiceConfig({})
    s3: S3ServiceConfig = S3ServiceConfig({})


class ExtraService(ServiceWithConfigResourceBase[ExtraConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[ExtraConfig],
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        options: defaultdict[str | None, ContainerModelBuildArgs] = defaultdict(
            ContainerModelBuildArgs
        )
        for name, s3 in self.config.s3.root.items():
            options[name].envs = {**options[name].envs, **s3.to_envs()}

        self.build_containers(options=options)

        if self.config.traefik.root:
            self.traefik = self.config.traefik.build_resources(
                opts=self.child_opts,
                main_service=self,
                traefik_service=traefik_service,
            )

        self.register_outputs({})
