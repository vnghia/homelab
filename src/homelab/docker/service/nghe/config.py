from pydantic import BaseModel


class NgheLastFmConfig(BaseModel):
    key: str


class NgheSpotifyConfig(BaseModel):
    id: str
    secret: str


class NgheConfig(BaseModel):
    lastfm: NgheLastFmConfig
    spotify: NgheSpotifyConfig
