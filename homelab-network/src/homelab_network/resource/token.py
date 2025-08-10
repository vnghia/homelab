from collections import defaultdict

import pulumi_cloudflare as cloudflare
from homelab_global import GlobalArgs
from pulumi import ComponentResource, ResourceOptions

from ..config import NetworkConfig


class TokenResource(ComponentResource):
    RESOURCE_NAME = "token"

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions,
        global_args: GlobalArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        permission_groups = cloudflare.get_api_token_permission_groups_list_output()

        self.amce_resources: defaultdict[str, dict[str, str]] = defaultdict(dict)
        for record in config.records.values():
            self.amce_resources[record.host][
                "com.cloudflare.api.account.zone.{}".format(record.zone_id)
            ] = "*"

        self.amce_tokens: dict[
            str, tuple[cloudflare.ApiToken, cloudflare.ApiToken]
        ] = {}
        for host, resources in self.amce_resources.items():
            amce_read = cloudflare.ApiToken(
                "{}-read".format(host),
                opts=ResourceOptions.merge(
                    self.child_opts, ResourceOptions(delete_before_replace=True)
                ),
                name="{}-{}-acme-read-token".format(global_args.project.prefix, host),
                policies=[
                    cloudflare.ApiTokenPolicyArgs(
                        effect="allow",
                        permission_groups=permission_groups.apply(
                            lambda groups: [
                                cloudflare.ApiTokenPolicyPermissionGroupArgs(
                                    id=group.id
                                )
                                for group in groups.results
                                if group.name == "Zone Read"
                            ]
                        ),
                        resources=resources,
                    )
                ],
            )
            amce_write = cloudflare.ApiToken(
                "{}-write".format(host),
                opts=ResourceOptions.merge(
                    self.child_opts, ResourceOptions(delete_before_replace=True)
                ),
                name="{}-{}-acme-write-token".format(global_args.project.prefix, host),
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
                        resources=resources,
                    )
                ],
            )
            self.amce_tokens[host] = (amce_read, amce_write)

        self.ddns_resources: defaultdict[str, dict[str, str]] = defaultdict(dict)
        for record in config.records.values():
            if record.is_ddns:
                self.ddns_resources[record.host][
                    "com.cloudflare.api.account.zone.{}".format(record.zone_id)
                ] = "*"

        self.ddns_tokens: dict[str, cloudflare.ApiToken] = {}
        for host, resources in self.ddns_resources.items():
            ddns_write = cloudflare.ApiToken(
                "{}-ddns".format(host),
                opts=ResourceOptions.merge(
                    self.child_opts, ResourceOptions(delete_before_replace=True)
                ),
                name="{}-{}-ddns-write-token".format(global_args.project.prefix, host),
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
                        resources=resources,
                    )
                ],
            )
            self.ddns_tokens[host] = ddns_write

        self.register_outputs({})
