import dataclasses
from typing import Any, Mapping

from pulumi import Input

from ..container.volume_path import ContainerVolumePath


@dataclasses.dataclass
class ConfigFileModel:
    container_volume_path: ContainerVolumePath
    data: Mapping[str, Input[Any]]
