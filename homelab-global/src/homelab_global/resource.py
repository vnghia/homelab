import pulumi_tailscale as tailscale
from homelab_extract import GlobalExtract
from homelab_extract.plain import PlainArgs
from homelab_mail.resource import MailResource
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
        mail_resource: MailResource,
        plain_args: PlainArgs,
        project_args: ProjectArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config
        self.variables = config.variables | {
            mail_resource.config.address.variable.host: GlobalExtract.from_simple(
                mail_resource.host
            ),
            mail_resource.config.address.variable.port: GlobalExtract.from_simple(
                str(mail_resource.config.address.port)
            ),
        }
        self.plain_args = plain_args
        self.project_args = project_args

        self.secret = SecretResource(
            config.secrets,
            opts=self.child_opts,
            name=self.RESOURCE_NAME,
            plain_args=plain_args,
        )

        self.mesh_devices = tailscale.get_devices()
        self.mesh_ips = {
            device.name.split(".", maxsplit=1)[0]: list(
                map(IPvAnyAddressAdapter.validate_python, device.addresses)
            )
            for device in tailscale.get_devices().devices
        }

        self.register_outputs({})

    def get_mesh_ip(self, host: str) -> list[IPvAnyAddress]:
        return self.mesh_ips["{}-core".format(host)]
