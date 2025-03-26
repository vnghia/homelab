from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict


class S3ServiceConfig(HomelabServiceConfigDict[str]):
    NONE_KEY = "s3"


class S3ServiceConfigBase(HomelabBaseModel):
    s3: S3ServiceConfig = S3ServiceConfig({})
