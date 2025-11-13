from homelab_pydantic import HomelabBaseModel
from pulumi import ComponentResource, ResourceOptions


class SecretBaseModel(HomelabBaseModel):
    active: bool = True
    protect: bool = False

    def opts(self, opts: ResourceOptions) -> ResourceOptions:
        return ResourceOptions.merge(
            opts,
            ResourceOptions(
                protect=self.protect or opts.protect,
                additional_secret_outputs=["result"],
            ),
        )

    def child_opts(self, t: str, name: str, opts: ResourceOptions) -> ResourceOptions:
        return ResourceOptions(parent=ComponentResource(t, name, None, self.opts(opts)))
