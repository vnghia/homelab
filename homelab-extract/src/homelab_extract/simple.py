from homelab_pydantic import HomelabRootModel
from pydantic import NonNegativeInt


class GlobalExtractSimpleSource(HomelabRootModel[NonNegativeInt | bool | str]):
    pass
