import pulumi
import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions
from pydantic.alias_generators import to_snake

from homelab_docker.model.container import (
    ContainerModel,
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
)
from homelab_docker.model.service import ServiceModel


class ServiceResourceBase[T](ComponentResource):
    CONTAINERS: dict[str, docker.Container] = {}

    def __init__(
        self,
        model: ServiceModel[T],
        *,
        opts: ResourceOptions | None,
        container_model_global_args: ContainerModelGlobalArgs,
    ) -> None:
        super().__init__(self.name(), self.name(), None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.model = model
        self.container_model_global_args = container_model_global_args

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__).replace("_", "-")

    @property
    def config(self) -> T:
        return self.model.config

    def add_service_name(self, name: str | None) -> str:
        return "{}-{}".format(self.name(), name) if name else self.name()

    def build_container(
        self,
        name: str | None,
        model: ContainerModel,
        container_model_build_args: ContainerModelBuildArgs | None,
    ) -> docker.Container:
        container_model_build_args = (
            container_model_build_args or ContainerModelBuildArgs()
        )
        return model.build_resource(
            self.add_service_name(name),
            opts=self.child_opts,
            global_args=self.container_model_global_args,
            build_args=container_model_build_args,
            containers=self.CONTAINERS,
        )

    def build_containers(
        self, options: dict[str | None, ContainerModelBuildArgs]
    ) -> None:
        self.container = self.build_container(
            None, self.model.container, options.get(None)
        )
        self.containers = {
            name: self.build_container(name, model, options.get(name))
            for name, model in self.model.containers.items()
        } | {None: self.container}

        for name, container in self.containers.items():
            name = self.add_service_name(name)
            self.CONTAINERS[name] = container
            pulumi.export("container.{}".format(name), container.name)
