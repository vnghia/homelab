from homelab_mail import MailConfig
from homelab_pydantic import HomelabBaseModel
from homelab_s3 import S3Config


class GlobalConfig(HomelabBaseModel):
    s3: S3Config = S3Config({})
    mail: MailConfig = MailConfig({})
