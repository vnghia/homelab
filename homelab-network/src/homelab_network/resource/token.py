import dataclasses
import urllib.parse
from collections import defaultdict
from typing import ClassVar, Self

import pulumi_cloudflare as cloudflare
from homelab_global import ProjectArgs
from pulumi import ComponentResource, Output, ResourceOptions

from ..config import NetworkConfig


@dataclasses.dataclass
class PermissionGroups:
    READ_NAME: ClassVar[str] = urllib.parse.quote_plus("Zone Read")
    WRITE_NAME: ClassVar[str] = urllib.parse.quote_plus("DNS Write")

    SCOPE: ClassVar[str] = urllib.parse.quote_plus("com.cloudflare.api.account.zone")

    read: Output[list[cloudflare.ApiTokenPolicyPermissionGroupArgs]]
    write: Output[list[cloudflare.ApiTokenPolicyPermissionGroupArgs]]

    @classmethod
    def to_args(
        cls, groups: cloudflare.GetApiTokenPermissionGroupsListResult
    ) -> list[cloudflare.ApiTokenPolicyPermissionGroupArgs]:
        return [
            cloudflare.ApiTokenPolicyPermissionGroupArgs(id=group.id)
            for group in groups.results
        ]

    @classmethod
    def get_group(
        cls, name: str, scope: str
    ) -> Output[list[cloudflare.ApiTokenPolicyPermissionGroupArgs]]:
        return cloudflare.get_api_token_permission_groups_list_output(
            name=name, scope=scope
        ).apply(cls.to_args)

    @classmethod
    def get(cls) -> Self:
        return cls(
            read=cls.get_group(cls.READ_NAME, cls.SCOPE),
            write=cls.get_group(cls.WRITE_NAME, cls.SCOPE),
        )


class TokenResource(ComponentResource):
    RESOURCE_NAME = "token"

    PERMISSION_GROUPS: PermissionGroups = PermissionGroups.get()

    def __init__(
        self,
        config: NetworkConfig,
        *,
        opts: ResourceOptions,
        project_args: ProjectArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.amce_resources: defaultdict[str, dict[str, str]] = defaultdict(dict)
        for record in config.records.values():
            self.amce_resources[record.host][
                "com.cloudflare.api.account.zone.{}".format(record.zone_id)
            ] = "*"

        self.acme_tokens: dict[str, cloudflare.ApiToken] = {}

        for host, resources in self.amce_resources.items():
            acme_token = cloudflare.ApiToken(
                "{}-acme".format(host),
                opts=ResourceOptions.merge(
                    self.child_opts, ResourceOptions(delete_before_replace=True)
                ),
                name="{}-{}-acme-token".format(project_args.prefix, host),
                policies=[
                    cloudflare.ApiTokenPolicyArgs(
                        effect="allow",
                        permission_groups=Output.all(
                            read=self.PERMISSION_GROUPS.read,
                            write=self.PERMISSION_GROUPS.write,
                        ).apply(lambda kwargs: kwargs["read"] + kwargs["write"]),
                        resources=resources,
                    )
                ],
            )
            self.acme_tokens[host] = acme_token

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
                name="{}-{}-ddns-write-token".format(project_args.prefix, host),
                policies=[
                    cloudflare.ApiTokenPolicyArgs(
                        effect="allow",
                        permission_groups=self.PERMISSION_GROUPS.write,
                        resources=resources,
                    )
                ],
            )
            self.ddns_tokens[host] = ddns_write

        self.register_outputs({})
