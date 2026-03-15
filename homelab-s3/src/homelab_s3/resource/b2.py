import pulumi
import pulumi_b2 as b2
from pulumi import ComponentResource, ResourceOptions
from pydantic import HttpUrl

from ..config.b2 import B2Config


class B2Resource(ComponentResource):
    RESOURCE_NAME = "b2"

    def __init__(self, config: B2Config, *, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        # TODO: Use autonaming after https://github.com/pulumi/pulumi-terraform-provider/issues/104
        self.child_opts = ResourceOptions(parent=self, delete_before_replace=True)

        self.url = HttpUrl(b2.get_account_info().s3_api_url)
        self.credentials = {}

        from ..resource import S3CredentialArgs

        for name, model in config.root.items():
            bucket = b2.bucket.Bucket(
                resource_name=name,
                opts=self.child_opts,
                bucket_name=model.name or name,
                bucket_type="allPrivate",
                default_server_side_encryption=b2.BucketDefaultServerSideEncryptionArgs(
                    algorithm="AES256", mode="SSE-B2"
                ),
                lifecycle_rules=[
                    b2.BucketLifecycleRuleArgs(
                        file_name_prefix=lifecycle.prefix,
                        days_from_hiding_to_deleting=float(lifecycle.version),
                    )
                    for lifecycle in lifecycles
                ]
                if (lifecycles := model.lifecycles)
                else None,
            )
            key = b2.application_key.ApplicationKey(
                resource_name=name,
                opts=self.child_opts,
                capabilities=model.capabilities,
                key_name=name,
                bucket_id=bucket.id,
            )
            self.credentials[name] = S3CredentialArgs(
                key_id=key.application_key_id,
                access_key=key.application_key,
                endpoint=self.url,
                bucket=bucket.bucket_name,
            )

            pulumi.export("b2.{}.key_id".format(name), key.application_key_id)
            pulumi.export("b2.{}.access_key".format(name), key.application_key)

        self.register_outputs({})
