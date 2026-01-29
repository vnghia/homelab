from homelab_pydantic import HomelabBaseModel
from pydantic import ConfigDict


class ContainerObservabilityInputModel(HomelabBaseModel):
    service: str | None = None
    container: str | None = None
    input: str

    @property
    def has_container(self) -> bool:
        return "container" in self.model_fields_set


class ContainerObservabilityModel(HomelabBaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    inputs: list[ContainerObservabilityInputModel] = []


class ContainerObservabilityConfig(HomelabBaseModel):
    sources: dict[str, ContainerObservabilityModel] = {}
    transforms: dict[str, ContainerObservabilityModel] = {}
    sinks: dict[str, ContainerObservabilityModel] = {}
