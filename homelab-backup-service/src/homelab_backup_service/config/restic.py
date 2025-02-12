import urllib.parse
from pathlib import PosixPath

from homelab_docker.pydantic import RelativePath
from homelab_integration.config.s3 import S3IntegrationConfig
from pydantic import BaseModel


class ResticConfig(BaseModel):
    bucket: str
    prefix: RelativePath

    def build_repo_url(self, s3_integration_config: S3IntegrationConfig) -> str:
        return "s3:{}".format(
            urllib.parse.urljoin(
                str(s3_integration_config.endpoint) or "s3.us-east-1.amazonaws.com",
                (PosixPath(self.bucket) / self.prefix).as_posix(),
            )
        )
