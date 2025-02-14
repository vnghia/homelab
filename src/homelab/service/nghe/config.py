from homelab_integration.config.s3 import S3IntegrationConfig
from pydantic import BaseModel


class NgheLastFmConfig(BaseModel):
    key: str


class NgheSpotifyConfig(BaseModel):
    id: str
    secret: str


class NgheConfig(BaseModel):
    lastfm: NgheLastFmConfig
    spotify: NgheSpotifyConfig
    s3: S3IntegrationConfig | None = None
