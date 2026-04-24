from homelab_pydantic.model import HomelabRootModel

from ..model.no_reply import NoReplyModel


class NoReplyConfig(HomelabRootModel[dict[str, NoReplyModel]]):
    root: dict[str, NoReplyModel] = {}

    def __getitem__(self, key: str) -> NoReplyModel:
        return self.root[key]
