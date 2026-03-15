import pulumi
import pulumi_b2 as b2
from pulumi import ComponentResource, ResourceOptions

from ..config.b2 import B2Config


class B2Resource(ComponentResource):
    RESOURCE_NAME = "b2"

    def __init__(self, config: B2Config, *, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        for name, model in config.root.items():
            bucket = b2.bucket.Bucket(
                resource_name=name,
                opts=self.child_opts,
                bucket_name=model.name or name,
                bucket_type="allPrivate",
                default_server_side_encryption=b2.BucketDefaultServerSideEncryptionArgs(
                    algorithm="AES256", mode="SSE-B2"
                ),
            )
            key = b2.application_key.ApplicationKey(
                resource_name=name,
                opts=self.child_opts,
                capabilities=model.capabilities,
                key_name=name,
                bucket_ids=[bucket.id],
            )
            pulumi.export("b2.{}.key_id".format(name), key.application_key_id)
            pulumi.export("b2.{}.access_key".format(name), key.application_key)
