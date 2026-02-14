from homelab_pydantic.model import HomelabBaseModel
from pydantic import PositiveInt


class ContainerMemoryConfig(HomelabBaseModel):
    limit: PositiveInt | None = None
    reservation: PositiveInt | None = None
