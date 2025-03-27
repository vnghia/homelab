from homelab_pydantic import HomelabRootModel

from ....model.state.system.oauth import KanidmStateSystemOauthModel


class KanidmStateSystemOauthConfig(
    HomelabRootModel[dict[str, KanidmStateSystemOauthModel]]
):
    root: dict[str, KanidmStateSystemOauthModel] = {}
