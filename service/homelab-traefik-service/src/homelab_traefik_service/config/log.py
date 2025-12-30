from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

from ..resource.static.schema import TypesAccessLog


class TraefikAccessLogConfig(HomelabBaseModel):
    path: GlobalExtract | None = None
    config: TypesAccessLog | None = None


class TraefikLogConfig(HomelabBaseModel):
    access: TraefikAccessLogConfig = TraefikAccessLogConfig()
