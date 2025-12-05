from homelab_extract.plain import PlainArgs
from homelab_restic.resource import ResticResource
from homelab_secret.resource import SecretResource
from pulumi import ComponentResource, ResourceOptions

from homelab_global import ProjectArgs
from homelab_global.config import GlobalConfig


class GlobalResource(ComponentResource):
    RESOURCE_NAME = "global"

    def __init__(
        self,
        config: GlobalConfig,
        *,
        opts: ResourceOptions | None,
        plain_args: PlainArgs,
        project_args: ProjectArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config
        self.plain_args = plain_args
        self.project_args = project_args

        self.secret = SecretResource(
            config.secrets,
            opts=self.child_opts,
            name=self.RESOURCE_NAME,
            plain_args=plain_args,
        )

        self.restic = ResticResource(
            config.restic,
            opts=self.child_opts,
            secret_resource=self.secret,
            plain_args=plain_args,
        )

        self.register_outputs({})
