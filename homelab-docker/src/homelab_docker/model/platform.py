from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class Platform(StrEnum):
    ARM64 = auto()
    AMD64 = auto()


class PlatformFullString(HomelabBaseModel):
    template: str
    platform: dict[Platform, str] = {platform: platform.value for platform in Platform}

    def to_str(self, platform: Platform) -> str:
        return self.template.format(platform=self.platform[platform])


class PlatformString(HomelabRootModel[str | PlatformFullString]):
    def to_str(self, platform: Platform) -> str:
        root = self.root
        if isinstance(root, PlatformFullString):
            return root.to_str(platform)
        else:
            return root
