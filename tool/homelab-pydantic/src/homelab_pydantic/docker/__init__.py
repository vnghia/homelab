from pydantic import Field

from . import schema


class ContainerCreationModel(schema.ModelContainerConfig):
    host_config: schema.ModelHostConfig | None = Field(None, alias="HostConfig")
    networking_config: schema.ModelNetworkingConfig | None = Field(
        None, alias="NetworkingConfig"
    )
