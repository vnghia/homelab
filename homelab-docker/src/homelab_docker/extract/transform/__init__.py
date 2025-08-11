from __future__ import annotations

import typing
from typing import Any

import pulumi_random as random
from homelab_extract.transform import ExtractTransform
from homelab_pydantic import AbsolutePath, HomelabRootModel
from pulumi import Input, Output

from .path import ExtractPathTransformer
from .secret import ExtractSecretTransformer
from .string import ExtractStringTransformer

if typing.TYPE_CHECKING:
    from ...model.docker.container.volume_path import ContainerVolumePath


class ExtractTransformer(HomelabRootModel[ExtractTransform]):
    def transform_string(
        self,
        value: Input[str]
        | random.RandomPassword
        | dict[str, Output[str]]
        | dict[Output[str], Any],
    ) -> Output[str]:
        root = self.root
        if not isinstance(value, dict):
            if root.secret is not None:
                value_output = ExtractSecretTransformer(root.secret).transform(value)
            else:
                value_output = Output.from_input(
                    value.result if isinstance(value, random.RandomPassword) else value
                )
            return value_output.apply(
                lambda value: ExtractStringTransformer(root.string).transform(
                    value, False
                )
            )
        return Output.json_dumps(value).apply(
            lambda value: ExtractStringTransformer(root.string).transform(value, True)
        )

    def transform_path(self, path: AbsolutePath) -> AbsolutePath:
        root = self.root
        return ExtractPathTransformer(root.path).transform(path)

    def transform_volume_path(
        self, volume_path: ContainerVolumePath
    ) -> ContainerVolumePath:
        root = self.root
        return ExtractPathTransformer(root.path).transform_volume_path(volume_path)
