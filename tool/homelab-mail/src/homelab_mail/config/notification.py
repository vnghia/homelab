from homelab_pydantic.model import HomelabRootModel

from ..model.notification import NotificationModel


class NotificationConfig(HomelabRootModel[dict[str, NotificationModel]]):
    root: dict[str, NotificationModel] = {}

    def __getitem__(self, key: str) -> NotificationModel:
        return self.root[key]
