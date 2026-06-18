from homelab_pydantic import HomelabBaseModel


class OvhModel(HomelabBaseModel):
    region: str
    actions: list[str] = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:ListMultipartUploadParts",
        "s3:ListBucketMultipartUploads",
        "s3:AbortMultipartUpload",
        "s3:GetBucketLocation",
    ]
