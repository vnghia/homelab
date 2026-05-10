from pydantic import Field

from ..model import HomelabBaseModel, HomelabServiceConfigDict
from . import schema


class ContainerCreationModel(schema.ModelContainerConfig):
    host_config: schema.ModelHostConfig | None = Field(None, alias="HostConfig")
    networking_config: schema.ModelNetworkingConfig | None = Field(
        None, alias="NetworkingConfig"
    )


class ContainerExecModel(HomelabBaseModel):
    container: str | None = None
    command: list[str]


class ContainerServiceName(HomelabServiceConfigDict[str]):
    NONE_KEY = "name"
