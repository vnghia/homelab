from pydantic import RootModel


class DaguDagParamsModel(RootModel[dict[str, str]]):
    root: dict[str, str]

    def to_key_command(self, key: str) -> str:
        self.root[key]
        return "${{{}}}".format(key)
