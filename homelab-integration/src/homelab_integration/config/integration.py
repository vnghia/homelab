from pydantic import BaseModel

from .s3 import S3IntegrationConfig


class IntegrationConfig(BaseModel):
    s3: S3IntegrationConfig
