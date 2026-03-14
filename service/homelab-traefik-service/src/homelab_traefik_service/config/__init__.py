from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_traefik_config import TraefikServiceConfigBase
from pydantic import HttpUrl

from ..resource.static.schema import TypesOTLP
from .entrypoint import TraefikEntrypointConfig
from .log import TraefikLogConfig
from .record import TraefikRecordConfig


class TraefikPathConfig(HomelabBaseModel):
    static: GlobalExtract
    dynamic: GlobalExtract
    api: GlobalExtract | None = None


class TraefikAcmeConfig(HomelabBaseModel):
    server: HttpUrl
    email: str
    storage: GlobalExtract
    disable_checks: bool
    require_all_rns: bool
    disable_ans_checks: bool
    delay_before_checks: str


class TraefikMetricsConfig(HomelabBaseModel):
    endpoint: GlobalExtract
    service_name: GlobalExtract
    otlp: TypesOTLP | None = None
    headers: dict[str, GlobalExtract] = {}
    resource_attributes: dict[str, GlobalExtract] = {}


class TraefikSablierConfig(HomelabBaseModel):
    url: GlobalExtract


class TraefikPluginConfig(HomelabBaseModel):
    name: str
    version: str
    unsafe: bool = False


class TraefikConfig(TraefikServiceConfigBase, HomelabBaseModel):
    path: TraefikPathConfig
    acme: TraefikAcmeConfig
    log: TraefikLogConfig
    metrics: TraefikMetricsConfig | None
    entrypoint: TraefikEntrypointConfig
    record: TraefikRecordConfig
    sablier: TraefikSablierConfig | None = None
    plugins: dict[str, TraefikPluginConfig] = {}

    @property
    def sablier_(self) -> TraefikSablierConfig:
        if not self.sablier:
            raise ValueError("Sablier url is not configured")
        return self.sablier
