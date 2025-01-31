from pydantic import BaseModel, ConfigDict

from homelab_config.integration.s3 import S3


class Integration(BaseModel):
    model_config = ConfigDict(strict=True)

    s3: S3
