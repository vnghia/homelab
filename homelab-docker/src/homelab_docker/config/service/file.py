from homelab_pydantic import HomelabServiceConfigDict

from ...model.service.file import ServiceFileModel


class ServiceFileConfig(HomelabServiceConfigDict[dict[str, ServiceFileModel]]):
    NONE_KEY = "file"
