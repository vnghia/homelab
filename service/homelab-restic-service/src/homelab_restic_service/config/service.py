from homelab_pydantic import HomelabRootModel

from ..model.service import ResticServiceModel


class ResticServiceConfig(HomelabRootModel[dict[str, ResticServiceModel]]):
    pass
