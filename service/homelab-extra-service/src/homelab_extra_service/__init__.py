from typing import Self

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
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

    def build(self) -> Self:
        for name, key in self.config.s3.root.items():
            s3 = self.docker_resource_args.config.s3[key]
            self.options[name].envs = {**self.options[name].envs, **s3.to_envs()}

        self.build_containers()

        if self.REGISTER_OUTPUT:
            self.register_outputs({})

        return self
