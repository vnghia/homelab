from typing import Self

from homelab_docker.extract import GlobalExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import Output, ResourceOptions

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

        for name, config in self.config.files.root.items():
            container_model = self.model[name]
            self.options[name].files = [
                FileResource(
                    resource_name,
                    opts=self.child_opts,
                    volume_path=GlobalExtractor(model.path).extract_volume_path(
                        self, container_model
                    ),
                    content=Output.format(
                        model.content,
                        **{
                            key: GlobalExtractor(value).extract_str(
                                self, container_model
                            )
                            for key, value in model.values.items()
                        },
                    ),
                    mode=model.mode,
                    volume_resource=self.docker_resource_args.volume,
                )
                for resource_name, model in config.items()
            ]

        self.build_containers()

        if self.REGISTER_OUTPUT:
            self.register_outputs({})

        return self
