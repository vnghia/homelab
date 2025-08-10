import dataclasses

from homelab_mail import MailConfig
from homelab_s3 import S3Config


@dataclasses.dataclass
class ProjectArgs:
    name: str
    stack: str
    labels: dict[str, str]

    @property
    def prefix(self) -> str:
        return "{}-{}".format(self.name, self.stack)


@dataclasses.dataclass
class GlobalArgs:
    project: ProjectArgs
    s3: S3Config
    mail: MailConfig
