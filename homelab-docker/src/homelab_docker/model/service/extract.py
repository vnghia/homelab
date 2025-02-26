from typing import Any

from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pydantic import ValidationError

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

    @classmethod
    def extract_recursively(cls, data: Any, model: ServiceModel) -> Any:
        if isinstance(data, dict):
            result_dict = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    try:
                        extract = cls(**value).extract_str(model)
                    except ValidationError:
                        extract = cls.extract_recursively(value, model)
                else:
                    extract = cls.extract_recursively(value, model)
                result_dict[key] = extract
            return result_dict
        elif isinstance(data, list):
            result_list = []
            for value in data:
                if isinstance(value, dict):
                    try:
                        extract = cls(**value).extract_str(model)
                    except ValidationError:
                        extract = cls.extract_recursively(value, model)
                else:
                    extract = cls.extract_recursively(value, model)
                result_list.append(extract)
            return result_list
        else:
            return data
