from __future__ import annotations

import typing
from typing import Protocol, TypeVar

from homelab_pydantic import AbsolutePath
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..model.container.volume_path import ContainerVolumePath
    from ..resource.service import ServiceResourceBase

T = TypeVar("T")


class ExtractorBase(Protocol[T]):
    root: T

    def __init__(self, root: T) -> None:
        self.root = root

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def ensure_valid_model(self, model: ContainerModel | None) -> ContainerModel:
        if not model:
            raise ValueError("Container model is required for {}".format(self.name))
        return model

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str] | dict[str, Output[str]]:
        raise TypeError("Could not extract str from {}".format(self.name))

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        raise TypeError("Could not extract path from {}".format(self.name))

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        raise TypeError("Could not extract volume path from {}".format(self.name))
