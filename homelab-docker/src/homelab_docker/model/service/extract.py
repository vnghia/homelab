from homelab_pydantic import AbsolutePath, HomelabBaseModel

from ...model.container.extract import ContainerExtract
from ...model.container.volume_path import ContainerVolumePath
from ...model.service import ServiceModel


class ServiceExtract(HomelabBaseModel):
    service: str | None = None
    extract: ContainerExtract

    def extract_str(self, model: ServiceModel) -> str:
        return self.extract.extract_str(model[self.service])

    def extract_path(self, model: ServiceModel) -> AbsolutePath:
        return self.extract.extract_path(model[self.service])

    def extract_volume_path(self, model: ServiceModel) -> ContainerVolumePath:
        return self.extract.extract_volume_path(model[self.service])
