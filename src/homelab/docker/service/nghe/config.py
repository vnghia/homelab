from pydantic import BaseModel


class LastFm(BaseModel):
    key: str


class Spotify(BaseModel):
    id: str
    secret: str


class Config(BaseModel):
    lastfm: LastFm
    spotify: Spotify
