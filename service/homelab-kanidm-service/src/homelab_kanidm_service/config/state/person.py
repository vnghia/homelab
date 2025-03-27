from homelab_pydantic import HomelabRootModel

from ...model.state.person import KanidmStatePersonModel


class KanidmStatePersonConfig(HomelabRootModel[dict[str, KanidmStatePersonModel]]):
    root: dict[str, KanidmStatePersonModel] = {}
