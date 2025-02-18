from homelab_pydantic import HomelabRootModel


class DaguDagParamsModel(HomelabRootModel[dict[str, str]]):
    root: dict[str, str]

    def to_key_command(self, key: str) -> str:
        self.root[key]
        return "${{{}}}".format(key)
