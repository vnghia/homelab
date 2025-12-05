from homelab_pydantic import HomelabRootModel

from .s3 import ResticS3Host


class ResticHost(HomelabRootModel[ResticS3Host]):
    pass
