from homelab_pydantic import HomelabBaseModel


class B2Model(HomelabBaseModel):
    name: str | None = None
    capabilities: list[str] = [
        "deleteFiles",
        "listBuckets",
        "listFiles",
        "readBucketEncryption",
        "readBucketLifecycleRules",
        "readBucketLogging",
        "readBucketNotifications",
        "readBucketReplications",
        "readBuckets",
        "readFiles",
        "shareFiles",
        "writeBucketEncryption",
        "writeBucketLifecycleRules",
        "writeBucketLogging",
        "writeBucketNotifications",
        "writeBucketReplications",
        "writeBuckets",
        "writeFiles",
    ]
