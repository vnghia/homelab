import pulumi
import pulumi_ovh as ovh
from pulumi import ComponentResource, Output, ResourceOptions
from pydantic import HttpUrl

from ..config.ovh import OvhConfig


class OvhResource(ComponentResource):
    RESOURCE_NAME = "ovh"

    def __init__(self, config: OvhConfig, *, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self, delete_before_replace=True)

        self.credentials = {}

        from ..resource import S3CredentialArgs

        for name, model in config.root.items():
            bucket = ovh.cloudproject.Storage(
                name,
                opts=self.child_opts,
                region_name=model.region,
                encryption=ovh.cloudproject.StorageEncryptionArgs(
                    sse_algorithm="AES256"
                ),
                hide_objects=True,
            )

            user = ovh.cloudproject.User(
                "s3-user-{}".format(name),
                opts=self.child_opts,
                description="s3-user-{}".format(name),
                role_name="objectstore_operator",
            )
            _ = ovh.cloudproject.S3Policy(
                "s3-policy-{}".format(name),
                self.child_opts,
                user_id=user.id,
                policy=Output.json_dumps(
                    {
                        "Statement": [
                            {
                                "Sid": "RWContainer",
                                "Effect": "Allow",
                                "Action": model.actions,
                                "Resource": [
                                    Output.format("arn:aws:s3:::{}", bucket.name),
                                    Output.format("arn:aws:s3:::{}/*", bucket.name),
                                ],
                            }
                        ]
                    }
                ),
            )
            credential = ovh.cloudproject.S3Credential(
                "s3-credential-{}".format(name), opts=self.child_opts, user_id=user.id
            )

            self.credentials[name] = S3CredentialArgs(
                key_id=credential.access_key_id,
                access_key=credential.secret_access_key,
                endpoint=HttpUrl(
                    "https://s3.{}.io.cloud.ovh.net/".format(model.region.lower())
                ),
                bucket=bucket.name,
            )

            pulumi.export("ovh.s3.{}.key_id".format(name), credential.access_key_id)
            pulumi.export(
                "ovh.s3.{}.access_key".format(name), credential.secret_access_key
            )

        self.register_outputs({})
