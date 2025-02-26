from homelab_pydantic import HomelabRootModel

from ...model.service.secret import ServiceSecretModel


class ServiceSecretConfig(HomelabRootModel[dict[str, ServiceSecretModel]]):
    pass
