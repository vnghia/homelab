from homelab_docker.extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class KanidmStateSystemOauthModel(HomelabBaseModel):
    present: bool = True
    public: bool = True
    display_name: GlobalExtract
    origin_url: list[GlobalExtract]
    origin_landing: GlobalExtract
    prefer_short_username: bool = False
