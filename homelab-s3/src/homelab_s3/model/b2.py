from homelab_pydantic import HomelabBaseModel


class B2BucketModel(HomelabBaseModel):
    capabilities: list[str] = ["listFiles", "readFiles", "writeFiles", "deleteFiles"]
