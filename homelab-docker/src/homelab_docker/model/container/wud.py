from typing import ClassVar

from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class ContainerWudConfig(HomelabBaseModel):
    SEMVER_PATTERN: ClassVar[list[str]] = [r"\d+"]

    template: str | None = None
    include: str | None = None
    include_prefix: str = ""
    include_suffix: str = ""
    exclude: str | None = None
    transform: bool = False
    semver_count: PositiveInt = 3

    def build_labels(
        self,
        resource_name: str | None,
    ) -> dict[str, str]:
        semver_pattern = r"\.".join(self.SEMVER_PATTERN * self.semver_count)
        return (
            ({"wud.display.name": resource_name} if resource_name else {})
            | ({"wud.link.template": self.template} if self.template else {})
            | (
                {
                    "wud.tag.transform": "^"
                    + self.include_prefix
                    + "("
                    + semver_pattern
                    + ")"
                    + self.include_suffix
                    + "$ => $1"
                }
                if self.transform
                else {}
            )
            | ({"wud.tag.exclude": self.exclude} if self.exclude else {})
            | {
                "wud.tag.include": self.include
                or (
                    "^"
                    + self.include_prefix
                    + semver_pattern
                    + self.include_suffix
                    + "$"
                ),
                "wud.watch": "true",
            }
        )
