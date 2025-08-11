import dataclasses

import pulumi_docker as docker
from pulumi import Output

from ...model.docker.container import ContainerModel


@dataclasses.dataclass
class ContainerResource:
    model: ContainerModel
    resource: docker.Container

    @property
    def id(self) -> Output[str]:
        return self.resource.id

    @property
    def name(self) -> Output[str]:
        return self.resource.name
