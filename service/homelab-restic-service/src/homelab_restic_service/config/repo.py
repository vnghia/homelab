import urllib.parse
from pathlib import PosixPath

from homelab_pydantic import HomelabBaseModel, RelativePath
from homelab_s3_config import S3Config


class ResticRepoConfig(HomelabBaseModel):
    bucket: str
    prefix: RelativePath
    s3: S3Config

    @property
    def repo(self) -> str:
        return "s3:{}".format(
            urllib.parse.urljoin(
                str(self.s3.endpoint) or "s3.us-east-1.amazonaws.com",
                (RelativePath(PosixPath(self.bucket)) / self.prefix).as_posix(),
            )
        )

    def to_envs[T](self, password: T) -> dict[str, str | T]:
        s3_envs: dict[str, str | T] = {k: v for k, v in self.s3.to_envs().items()}
        return s3_envs | {
            "RESTIC_REPOSITORY": self.repo,
            "RESTIC_PASSWORD": password,
        }
