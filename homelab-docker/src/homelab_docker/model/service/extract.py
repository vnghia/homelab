from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import Output
from pydantic import ValidationError

from ...model.container.extract import ContainerExtract
from ...model.container.volume_path import ContainerVolumePath

if typing.TYPE_CHECKING:
    from ...resource.service import ServiceResourceBase


class ServiceExtract(HomelabBaseModel):
    service: str | None = None
    extract: ContainerExtract

    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        return self.extract.extract_str(main_service.model[self.service], main_service)

    def extract_path(self, main_service: ServiceResourceBase) -> AbsolutePath:
        return self.extract.extract_path(main_service.model[self.service], main_service)

    def extract_volume_path(
        self, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.extract.extract_volume_path(
            main_service.model[self.service], main_service
        )

    @classmethod
    def extract_recursively(cls, data: Any, main_service: ServiceResourceBase) -> Any:
        if isinstance(data, dict):
            result_dict = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    try:
                        extract = cls(**value).extract_str(main_service)
                    except ValidationError:
                        extract = cls.extract_recursively(value, main_service)
                else:
                    extract = cls.extract_recursively(value, main_service)
                result_dict[key] = extract
            return result_dict
        elif isinstance(data, list):
            result_list = []
            for value in data:
                if isinstance(value, dict):
                    try:
                        extract = cls(**value).extract_str(main_service)
                    except ValidationError:
                        extract = cls.extract_recursively(value, main_service)
                else:
                    extract = cls.extract_recursively(value, main_service)
                result_list.append(extract)
            return result_list
        else:
            return data
