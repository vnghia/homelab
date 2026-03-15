from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class B2LifecycleModel(HomelabBaseModel):
    prefix: str = ""
    version: PositiveInt


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
    lifecycles: list[B2LifecycleModel] = []
