from homelab_integration.config.s3 import S3IntegrationConfig
from homelab_pydantic import HomelabBaseModel


class NgheLastFmConfig(HomelabBaseModel):
    key: str


class NgheSpotifyConfig(HomelabBaseModel):
    id: str
    secret: str


class NgheConfig(HomelabBaseModel):
    lastfm: NgheLastFmConfig
    spotify: NgheSpotifyConfig
    s3: S3IntegrationConfig | None = None
