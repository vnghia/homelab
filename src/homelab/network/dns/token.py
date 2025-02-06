# import pulumi_cloudflare as cloudflare
# from homelab_config import config
# from pulumi import ComponentResource, ResourceOptions


# class Token(ComponentResource):
#     RESOURCE_NAME = "dns-token"

#     def __init__(
#         self,
#         opts: ResourceOptions | None = None,
#     ) -> None:
#         self.config = config.network.dns

#         super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
#         self.child_opts = ResourceOptions(parent=self)

#         permission_groups = cloudflare.get_api_token_permission_groups()
#         self.resources = {
#             "com.cloudflare.api.account.zone.{}".format(v): "*"
#             for v in [
#                 self.config.public.zone_id,
#                 self.config.private.zone_id,
#             ]
#         }
#         self.read = cloudflare.ApiToken(
#             "read",
#             opts=ResourceOptions.merge(
#                 self.child_opts, ResourceOptions(delete_before_replace=True)
#             ),
#             name=config.get_name("acme-read-token", project=True),
#             policies=[
#                 cloudflare.ApiTokenPolicyArgs(
#                     permission_groups=[permission_groups.zone["Zone Read"]],
#                     resources=self.resources,
#                 )
#             ],
#         )
#         self.write = cloudflare.ApiToken(
#             "write",
#             opts=ResourceOptions.merge(
#                 self.child_opts, ResourceOptions(delete_before_replace=True)
#             ),
#             name=config.get_name("acme-write-token", project=True),
#             policies=[
#                 cloudflare.ApiTokenPolicyArgs(
#                     permission_groups=[permission_groups.zone["DNS Write"]],
#                     resources=self.resources,
#                 )
#             ],
#         )

#         self.register_outputs({"read": self.read.value, "write": self.write.value})
