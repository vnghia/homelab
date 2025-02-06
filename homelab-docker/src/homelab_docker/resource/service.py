import dataclasses

import pulumi
import pulumi_docker as docker
from pulumi import ComponentResource, Input, ResourceOptions
from pydantic.alias_generators import to_snake
from pydantic_extra_types.timezone_name import TimeZoneName

from homelab_docker.file import File
from homelab_docker.model.container import Model as ContainerModel
from homelab_docker.model.service import Model as ServiceModel
from homelab_docker.resource.global_ import Global as GlobalResource


@dataclasses.dataclass
class BuildOption:
    opts: ResourceOptions | None = None
    envs: dict[str, Input[str]] = dataclasses.field(default_factory=dict)
    files: list[File] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Args:
    timezone: TimeZoneName
    global_resource: GlobalResource
    opts: ResourceOptions | None
    project_labels: dict[str, str]


class Base[T](ComponentResource):
    CONTAINERS: dict[str, docker.Container] = {}

    def __init__(
        self,
        model: ServiceModel[T],
        *,
        args: Args,
    ) -> None:
        super().__init__(self.name(), self.name(), None, args.opts)
        self.child_opts = ResourceOptions(parent=self)

        self.model = model
        self.args = args

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__).replace("_", "-")

    @property
    def config(self) -> T:
        return self.model.config

    def add_service_name(self, name: str | None) -> str:
        return "{}-{}".format(self.name(), name) if name else self.name()

    def build_container(
        self, name: str | None, model: ContainerModel, option: BuildOption | None = None
    ) -> docker.Container:
        option = option or BuildOption()
        return model.build_resource(
            self.add_service_name(name),
            opts=ResourceOptions.merge(self.child_opts, option.opts),
            timezone=self.args.timezone,
            global_resource=self.args.global_resource,
            containers=self.CONTAINERS,
            envs=option.envs,
            files=option.files,
            project_labels=self.args.project_labels,
        )

    def build_containers(self, options: dict[str | None, BuildOption] = {}) -> None:
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
