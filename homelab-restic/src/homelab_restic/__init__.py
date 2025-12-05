from homelab_extract.plain import PlainArgs
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from homelab_secret.model.password import SecretPasswordModel

from .host import ResticHost


class ResticRepositoryModel(HomelabBaseModel):
    host: ResticHost
    password: SecretPasswordModel

    def build_repository(self, plain_args: PlainArgs) -> str:
        return self.host.root.build_repository(plain_args)

    def build_envs(self, plain_args: PlainArgs) -> dict[str, str]:
        return self.host.root.build_envs(plain_args)


class ResticConfig(HomelabRootModel[dict[str, ResticRepositoryModel]]):
    root: dict[str, ResticRepositoryModel] = {}

    def __getitem__(self, key: str) -> ResticRepositoryModel:
        return self.root[key]
