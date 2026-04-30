from enum import StrEnum, auto

from homelab_extract.transform.string import ExtractTransformString
from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class Platform(StrEnum):
    ARM64 = auto()
    AMD64 = auto()


class PlatformFullString(HomelabBaseModel):
    transform: ExtractTransformString = ExtractTransformString()
    platform: dict[Platform, str] = {platform: platform.value for platform in Platform}

    def to_str(self, platform: Platform) -> str:
        return self.transform.transform(self.platform[platform], False)


class PlatformString(HomelabRootModel[str | PlatformFullString]):
    def to_str(self, platform: Platform) -> str:
        root = self.root
        if isinstance(root, PlatformFullString):
            return root.to_str(platform)
        return root
