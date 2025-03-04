from collections import defaultdict

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import ExtraConfig


class ExtraService[T: ExtraConfig](ServiceWithConfigResourceBase[T]):
    REGISTER_OUTPUT = True

    def __init__(
        self,
        model: ServiceWithConfigModel[T],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
        options: dict[str | None, ContainerModelBuildArgs] | None,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        build_options = defaultdict(ContainerModelBuildArgs, (options or {}))
        for name, s3 in self.config.s3.root.items():
            build_options[name].envs = {**build_options[name].envs, **s3.to_envs()}

        self.build_containers(options=build_options)

        if self.REGISTER_OUTPUT:
            self.register_outputs({})
