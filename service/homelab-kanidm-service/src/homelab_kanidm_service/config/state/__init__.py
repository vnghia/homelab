from homelab_pydantic import HomelabBaseModel

from .group import KanidmStateGroupConfig
from .person import KanidmStatePersonConfig
from .system import KanidmStateSystemConfig


class KanidmStateConfig(HomelabBaseModel):
    groups: KanidmStateGroupConfig = KanidmStateGroupConfig()
    persons: KanidmStatePersonConfig = KanidmStatePersonConfig()
    systems: KanidmStateSystemConfig = KanidmStateSystemConfig()
