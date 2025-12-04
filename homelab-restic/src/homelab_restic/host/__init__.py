from homelab_pydantic.model import HomelabRootModel

from .s3 import ResticS3Host


class ResticHostArgs:
    pass


class ResticHost(HomelabRootModel[ResticS3Host]):
    @property
    def repository(self) -> str:
        return self.root.repository
