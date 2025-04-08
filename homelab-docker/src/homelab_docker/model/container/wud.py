from homelab_pydantic import HomelabBaseModel


class ContainerWudConfig(HomelabBaseModel):
    template: str | None = None
    include: str | None = None
    include_prefix: str = ""
    include_suffix: str = ""

    def build_labels(
        self,
        resource_name: str | None,
    ) -> dict[str, str]:
        return (
            ({"wud.display.name": resource_name} if resource_name else {})
            | ({"wud.link.template": self.template} if self.template else {})
            | {
                "wud.tag.include": self.include
                or (
                    "^"
                    + self.include_prefix
                    + r"\d+\.\d+\.\d+"
                    + self.include_suffix
                    + "$"
                ),
                "wud.watch": "true",
            }
        )
