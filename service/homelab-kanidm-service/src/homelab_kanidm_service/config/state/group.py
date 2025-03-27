from homelab_pydantic import HomelabRootModel

from ...model.state.group import KanidmStateGroupModel


class KanidmStateGroupConfig(HomelabRootModel[dict[str, KanidmStateGroupModel]]):
    root: dict[str, KanidmStateGroupModel] = {}
