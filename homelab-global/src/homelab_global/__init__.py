import dataclasses


@dataclasses.dataclass
class ProjectArgs:
    name: str
    stack: str
    labels: dict[str, str]

    @property
    def prefix(self) -> str:
        return "{}-{}".format(self.name, self.stack)
