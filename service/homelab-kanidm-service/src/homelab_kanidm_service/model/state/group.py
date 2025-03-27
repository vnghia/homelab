from homelab_docker.extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class KanidmStateGroupModel(HomelabBaseModel):
    present: bool = True
    members: list[GlobalExtract]
