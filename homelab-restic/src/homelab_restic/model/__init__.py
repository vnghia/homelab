from homelab_extract.plain import PlainArgs
from homelab_pydantic import HomelabBaseModel
from homelab_secret.model.password import SecretPasswordModel
from pydantic import PositiveInt

from .host import ResticHost
from .keep import ResticKeepConfig


class ResticRepositoryModel(HomelabBaseModel):
    host: ResticHost
    password: SecretPasswordModel
    keep: ResticKeepConfig
    compression: str | None = None
    pack_size: PositiveInt | None = None

    def build_repository(self, plain_args: PlainArgs) -> str:
        return self.host.root.build_repository(plain_args)

    def build_envs(self, plain_args: PlainArgs) -> dict[str, str]:
        return self.host.root.build_envs(plain_args)
