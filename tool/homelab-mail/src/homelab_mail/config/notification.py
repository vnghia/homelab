from typing import Self

from homelab_pydantic.model import HomelabRootModel

from ..model.notification import NotificationModel


class NotificationConfig(HomelabRootModel[dict[str, NotificationModel]]):
    @classmethod
    def default(cls) -> Self:
        return cls({})

    def __getitem__(self, key: str) -> NotificationModel:
        return self.root[key]
