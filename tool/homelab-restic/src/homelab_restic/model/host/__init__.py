from homelab_pydantic import HomelabRootModel

from .s3 import ResticS3Host
from .sftp import ResticSftpHost


class ResticHost(HomelabRootModel[ResticS3Host | ResticSftpHost]):
    pass
