from homelab_integration import S3Integration
from homelab_pydantic import HomelabBaseModel


class NgheLastFmConfig(HomelabBaseModel):
    key: str


class NgheSpotifyConfig(HomelabBaseModel):
    id: str
    secret: str


class NgheConfig(HomelabBaseModel):
    lastfm: NgheLastFmConfig
    spotify: NgheSpotifyConfig
    s3: S3Integration | None = None
