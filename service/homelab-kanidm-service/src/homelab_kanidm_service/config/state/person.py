from typing import ClassVar, Self

from homelab_pydantic import HomelabRootModel

from ...model.state.person import KanidmStatePersonModel


class KanidmStatePersonConfig(HomelabRootModel[dict[str, KanidmStatePersonModel]]):
    GROUP_PREFIX: ClassVar[str] = "group_person_"

    @classmethod
    def default(cls) -> Self:
        return cls({})

    @classmethod
    def to_group_name(cls, person: str) -> str:
        return "{}{}".format(cls.GROUP_PREFIX, person)
