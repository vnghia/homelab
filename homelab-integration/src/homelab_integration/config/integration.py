from homelab_pydantic import HomelabBaseModel

from .s3 import S3IntegrationConfig


class IntegrationConfig(HomelabBaseModel):
    s3: S3IntegrationConfig
