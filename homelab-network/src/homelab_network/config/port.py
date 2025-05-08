from typing import ClassVar

from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from ..model.port import NetworkPortModel


class NetworkPortConfig(HomelabBaseModel):
    HTTP: ClassVar[PositiveInt] = 80
    HTTPS: ClassVar[PositiveInt] = 443

    internal: NetworkPortModel
    external: NetworkPortModel
