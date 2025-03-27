from homelab_pydantic import HomelabBaseModel

from .oauth import KanidmStateSystemOauthConfig


class KanidmStateSystemConfig(HomelabBaseModel):
    oauth2: KanidmStateSystemOauthConfig = KanidmStateSystemOauthConfig()
