from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions


class SecretModel(HomelabBaseModel):
    protect: bool = False

    def opts(self, opts: ResourceOptions) -> ResourceOptions:
        return ResourceOptions.merge(
            opts,
            ResourceOptions(protect=self.protect, additional_secret_outputs=["result"]),
        )
