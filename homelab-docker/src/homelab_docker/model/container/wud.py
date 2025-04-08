from typing import ClassVar

from homelab_pydantic import HomelabBaseModel


class ContainerWudConfig(HomelabBaseModel):
    SEMVER_PATTERN: ClassVar[str] = r"\d+\.\d+\.\d+"

    template: str | None = None
    include: str | None = None
    include_prefix: str = ""
    include_suffix: str = ""
    transform: bool = False

    def build_labels(
        self,
        resource_name: str | None,
    ) -> dict[str, str]:
        return (
            ({"wud.display.name": resource_name} if resource_name else {})
            | ({"wud.link.template": self.template} if self.template else {})
            | (
                {
                    "wud.tag.transform": "^"
                    + self.include_prefix
                    + "("
                    + self.SEMVER_PATTERN
                    + ")"
                    + self.include_suffix
                    + "$ => $1"
                }
                if self.transform
                else {}
            )
            | {
                "wud.tag.include": self.include
                or (
                    "^"
                    + self.include_prefix
                    + self.SEMVER_PATTERN
                    + self.include_suffix
                    + "$"
                ),
                "wud.watch": "true",
            }
        )
