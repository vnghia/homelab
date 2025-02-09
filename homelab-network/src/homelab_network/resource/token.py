import pulumi_cloudflare as cloudflare
from pulumi import ComponentResource, ResourceOptions

from homelab_network.config.network import NetworkConfig


class TokenResource(ComponentResource):
    RESOURCE_NAME = "token"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions | None,
        project_prefix: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        permission_groups = cloudflare.get_api_token_permission_groups()
        self.resources = {
            "com.cloudflare.api.account.zone.{}".format(v): "*"
            for v in [config.public.zone_id, config.private.zone_id]
        }

        self.read = cloudflare.ApiToken(
            "read",
            opts=ResourceOptions.merge(
                self.child_opts, ResourceOptions(delete_before_replace=True)
            ),
            name="{}-acme-read-token".format(project_prefix),
            policies=[
                cloudflare.ApiTokenPolicyArgs(
                    permission_groups=[permission_groups.zone["Zone Read"]],
                    resources=self.resources,
                )
            ],
        )
        self.write = cloudflare.ApiToken(
            "write",
            opts=ResourceOptions.merge(
                self.child_opts, ResourceOptions(delete_before_replace=True)
            ),
            name="{}-acme-write-token".format(project_prefix),
            policies=[
                cloudflare.ApiTokenPolicyArgs(
                    permission_groups=[permission_groups.zone["DNS Write"]],
                    resources=self.resources,
                )
            ],
        )

        self.register_outputs({"read": self.read.value, "write": self.write.value})
