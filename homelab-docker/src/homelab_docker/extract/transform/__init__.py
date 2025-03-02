import typing

import pulumi_random as random
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import Input, Output

from .path import ExtractTransformPath
from .secret import ExtractTransformSecret
from .string import ExtractTransformString

if typing.TYPE_CHECKING:
    from ...model.container.volume_path import ContainerVolumePath


class ExtractTransform(HomelabBaseModel):
    path: ExtractTransformPath = ExtractTransformPath()
    string: ExtractTransformString = ExtractTransformString()
    secret: ExtractTransformSecret = ExtractTransformSecret()

    def transform_string(
        self, value: Input[str] | random.RandomPassword
    ) -> Output[str]:
        if isinstance(value, random.RandomPassword):
            value_output = self.secret.transform(value)
        else:
            value_output = Output.from_input(value)
        return value_output.apply(self.string.transform)

    def transform_path(self, path: AbsolutePath) -> AbsolutePath:
        return self.path.transform(path)

    def transform_volume_path(
        self, volume_path: ContainerVolumePath
    ) -> ContainerVolumePath:
        return self.path.transform_volume_path(volume_path)
