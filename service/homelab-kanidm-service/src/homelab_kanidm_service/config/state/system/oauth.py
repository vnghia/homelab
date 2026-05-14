from typing import Self

from homelab_pydantic import HomelabRootModel

from ....model.state.system.oauth import KanidmStateSystemOauthModel


class KanidmStateSystemOauthConfig(
    HomelabRootModel[dict[str, KanidmStateSystemOauthModel]]
):
    @classmethod
    def default(cls) -> Self:
        return cls({})
