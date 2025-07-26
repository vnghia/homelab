import pulumi_tls as tls
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions


class SecretKeyModel(HomelabBaseModel):
    algorithm: str
    protect: bool = False

    def build_resource(
        self, resource_name: str, opts: ResourceOptions
    ) -> tls.PrivateKey:
        opts = ResourceOptions.merge(opts, ResourceOptions(protect=self.protect))
        return tls.PrivateKey(resource_name, opts=opts, algorithm=self.algorithm)
