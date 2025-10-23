from homelab_dagu_config import DaguServiceConfigBase
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from homelab_s3_config import S3ServiceConfigBase
from homelab_traefik_config import TraefikServiceConfigBase


class ExtraDependOnFullConfig(HomelabBaseModel):
    host: str | None = None
    service: str


class ExtraDependOnConfig(HomelabRootModel[str | ExtraDependOnFullConfig]):
    def to_full(self) -> ExtraDependOnFullConfig:
        root = self.root
        if isinstance(root, ExtraDependOnFullConfig):
            return root
        return ExtraDependOnFullConfig(service=root)


class ExtraConfig(TraefikServiceConfigBase, S3ServiceConfigBase, DaguServiceConfigBase):
    depends_on: list[ExtraDependOnConfig] = []
