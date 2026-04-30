from homelab_extract.plain import PlainArgs
from homelab_restic.resource import ResticResource
from homelab_secret.resource import SecretResource
from pulumi import ComponentResource, ResourceOptions

from .config import BackupConfig


class BackupResource(ComponentResource):
    RESOURCE_NAME = "backup"

    def __init__(
        self,
        config: BackupConfig,
        *,
        opts: ResourceOptions | None,
        secret_resource: SecretResource,
        plain_args: PlainArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.restic = ResticResource(
            config.restic,
            opts=self.child_opts,
            secret_resource=secret_resource,
            plain_args=plain_args,
        )
