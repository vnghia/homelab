from homelab_integration import S3Config
from homelab_pydantic import HomelabBaseModel
from homelab_traefik_service.config.service import TraefikServiceConfig


class NgheLastFmConfig(HomelabBaseModel):
    key: str


class NgheSpotifyConfig(HomelabBaseModel):
    id: str
    secret: str


class NgheConfig(HomelabBaseModel):
    lastfm: NgheLastFmConfig
    spotify: NgheSpotifyConfig
    s3: S3Config | None = None
    traefik: TraefikServiceConfig
