from typing import Self

from homelab_pydantic import HomelabRootModel

from ...model.state.group import KanidmStateGroupModel


class KanidmStateGroupConfig(HomelabRootModel[dict[str, KanidmStateGroupModel]]):
    @classmethod
    def default(cls) -> Self:
        return cls({})
