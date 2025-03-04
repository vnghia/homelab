from collections import defaultdict

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import ExtraConfig


class ExtraService(ServiceWithConfigResourceBase[ExtraConfig]):
    REGISTER_OUTPUT = True

    def __init__(
        self,
        model: ServiceWithConfigModel[ExtraConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        options: defaultdict[str | None, ContainerModelBuildArgs] = defaultdict(
            ContainerModelBuildArgs
        )
        for name, s3 in self.config.s3.root.items():
            options[name].envs = {**options[name].envs, **s3.to_envs()}

        self.build_containers(options=options)

        if self.REGISTER_OUTPUT:
            self.register_outputs({})
