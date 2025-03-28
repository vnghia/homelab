from typing import ClassVar

from homelab_pydantic import HomelabRootModel

from ...model.state.person import KanidmStatePersonModel


class KanidmStatePersonConfig(HomelabRootModel[dict[str, KanidmStatePersonModel]]):
    GROUP_PREFIX: ClassVar[str] = "group_person_"

    root: dict[str, KanidmStatePersonModel] = {}

    @classmethod
    def to_group_name(cls, person: str) -> str:
        return "{}{}".format(cls.GROUP_PREFIX, person)
