from homelab_pydantic import HomelabServiceConfigDict


class S3ServiceConfig(HomelabServiceConfigDict[str]):
    NONE_KEY = "s3"
