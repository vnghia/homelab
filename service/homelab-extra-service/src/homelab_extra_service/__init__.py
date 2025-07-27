from typing import Self

from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import ExtraConfig


class ExtraService[T: ExtraConfig](ServiceWithConfigResourceBase[T]):
    REGISTER_OUTPUT = True

    def __init__(
        self,
        model: ServiceWithConfigModel[T],
        *,
        opts: ResourceOptions,
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
                    content=GlobalExtractor(model.content).extract_str(
                        self, container_model
                    ),
                    mode=model.mode,
                    docker_resources_args=self.docker_resource_args,
                )
                for resource_name, model in config.items()
            ]

        self.build_containers()

        if self.REGISTER_OUTPUT:
            self.register_outputs({})

        return self

    @classmethod
    def extract_depends_on(
        cls, models: dict[str, ServiceWithConfigModel[ExtraConfig]], name: str
    ) -> dict[str, None]:
        results: dict[str, None] = {}
        for depend_on in models[name].config.depends_on:
            results |= cls.extract_depends_on(models, depend_on)
        return results | {name: None}

    @classmethod
    def sort_depends_on(
        cls, models: dict[str, ServiceWithConfigModel[ExtraConfig]]
    ) -> dict[str, ServiceWithConfigModel[ExtraConfig]]:
        results: dict[str, ServiceWithConfigModel[ExtraConfig]] = {}
        for name in models:
            depends_on = cls.extract_depends_on(models, name)
            for depend_on in depends_on:
                results[depend_on] = models[depend_on]
        return results
