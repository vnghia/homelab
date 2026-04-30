from homelab_pydantic import HomelabServiceConfigDict

from ...model.service.file import ServiceFileModel


class ServiceFileConfig(HomelabServiceConfigDict[ServiceFileModel]):
    NONE_KEY = None
