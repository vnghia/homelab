from pydantic import BaseModel

from homelab_docker.model.build.context import BuildContextModel


class BuildModel(BaseModel):
    context: BuildContextModel
