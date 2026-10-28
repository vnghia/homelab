import dataclasses


@dataclasses.dataclass
class ProjectArgs:
    name: str
    stack: str
    labels: dict[str, str]

    @property
    def prefix(self) -> str:
        return f"{self.name}-{self.stack}"
