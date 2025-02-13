from enum import StrEnum, auto

from pydantic import BaseModel, RootModel


class Platform(StrEnum):
    ARM64 = auto()
    AMD64 = auto()


class PlatformFullString(BaseModel):
    template: str
    platform: dict[Platform, str]

    def to_str(self, platform: Platform) -> str:
        return self.template.format(platform=self.platform[platform])


class PlatformString(RootModel[str | PlatformFullString]):
    def to_str(self, platform: Platform) -> str:
        root = self.root
        if isinstance(root, PlatformFullString):
            return root.to_str(platform)
        else:
            return root
