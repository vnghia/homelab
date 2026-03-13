import pulumi_tailscale as tailscale
from homelab_extract.plain import PlainArgs
from homelab_pydantic import IPvAnyAddressAdapter
from homelab_secret.resource import SecretResource
from pulumi import ComponentResource, ResourceOptions
from pydantic import IPvAnyAddress

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

        self.mesh_ips: dict[str, list[IPvAnyAddress]] = {}

        self.register_outputs({})

    def get_mesh_ip(self, host: str) -> list[IPvAnyAddress]:
        if host not in self.mesh_ips:
            self.mesh_ips[host] = list(
                map(
                    IPvAnyAddressAdapter.validate_python,
                    tailscale.get_device("{}-core".format(host)).addresses,
                )
            )
        return self.mesh_ips[host]
