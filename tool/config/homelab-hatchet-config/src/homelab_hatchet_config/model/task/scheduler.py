import dataclasses

from homelab_pydantic import Json


@dataclasses.dataclass
class HatchetTaskWorkflowInputArgs:
    workflow: str
    input: Json | None
