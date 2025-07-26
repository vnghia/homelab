import pulumi_cloudflare as cloudflare
from pulumi import ComponentResource, ResourceOptions

from ..config import NetworkConfig


class TokenResource(ComponentResource):
    RESOURCE_NAME = "token"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions,
        project_prefix: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        permission_groups = cloudflare.get_api_token_permission_groups_list_output()
        amce_resources = {
            "com.cloudflare.api.account.zone.{}".format(v.zone_id): "*"
            for v in config.records.values()
        }

        self.amce_read = cloudflare.ApiToken(
            "read",
            opts=ResourceOptions.merge(
                self.child_opts, ResourceOptions(delete_before_replace=True)
            ),
            name="{}-acme-read-token".format(project_prefix),
            policies=[
                cloudflare.ApiTokenPolicyArgs(
                    effect="allow",
                    permission_groups=permission_groups.apply(
                        lambda groups: [
                            cloudflare.ApiTokenPolicyPermissionGroupArgs(id=group.id)
                            for group in groups.results
                            if group.name == "Zone Read"
                        ]
                    ),
                    resources=amce_resources,
                )
            ],
        )
        self.amce_write = cloudflare.ApiToken(
            "write",
            opts=ResourceOptions.merge(
                self.child_opts, ResourceOptions(delete_before_replace=True)
            ),
            name="{}-acme-write-token".format(project_prefix),
            policies=[
                cloudflare.ApiTokenPolicyArgs(
                    effect="allow",
                    permission_groups=permission_groups.apply(
                        lambda groups: [
                            cloudflare.ApiTokenPolicyPermissionGroupArgs(id=group.id)
                            for group in groups.results
                            if group.name == "DNS Write"
                        ]
                    ),
                    resources=amce_resources,
                )
            ],
        )

        ddns_resource = {
            "com.cloudflare.api.account.zone.{}".format(v.zone_id): "*"
            for v in config.records.values()
            if v.is_ddns
        }
        self._ddns_write = None
        if ddns_resource:
            self._ddns_write = cloudflare.ApiToken(
                "ddns",
                opts=ResourceOptions.merge(
                    self.child_opts, ResourceOptions(delete_before_replace=True)
                ),
                name="{}-ddns-write-token".format(project_prefix),
                policies=[
                    cloudflare.ApiTokenPolicyArgs(
                        effect="allow",
                        permission_groups=permission_groups.apply(
                            lambda groups: [
                                cloudflare.ApiTokenPolicyPermissionGroupArgs(
                                    id=group.id
                                )
                                for group in groups.results
                                if group.name == "DNS Write"
                            ]
                        ),
                        resources=ddns_resource,
                    )
                ],
            )

        self.register_outputs(
            {"amce-read": self.amce_read.value, "acme-write": self.amce_write.value}
            | ({"ddns-write": self._ddns_write} if self._ddns_write else {})
        )

    @property
    def ddns_write(self) -> cloudflare.ApiToken:
        if not self._ddns_write:
            raise ValueError("DDNS token is None")
        return self._ddns_write
