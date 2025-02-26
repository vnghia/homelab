from homelab_integration import S3Integration
from homelab_pydantic import HomelabBaseModel
from homelab_traefik_service.config.dynamic.http import TraefikDynamicHttpConfig


class NgheLastFmConfig(HomelabBaseModel):
    key: str


class NgheSpotifyConfig(HomelabBaseModel):
    id: str
    secret: str


class NgheConfig(HomelabBaseModel):
    lastfm: NgheLastFmConfig
    spotify: NgheSpotifyConfig
    s3: S3Integration | None = None
    traefik: TraefikDynamicHttpConfig
