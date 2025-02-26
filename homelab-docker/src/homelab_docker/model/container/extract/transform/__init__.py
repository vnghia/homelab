import pulumi_random as random
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import Input, Output

from ...volume_path import ContainerVolumePath
from .path import ContainerExtractTransformPath
from .secret import ContainerExtractTransformSecret
from .string import ContainerExtractTransformString


class ContainerExtractTransform(HomelabBaseModel):
    string: ContainerExtractTransformString = ContainerExtractTransformString()
    path: ContainerExtractTransformPath = ContainerExtractTransformPath()
    secret: ContainerExtractTransformSecret = ContainerExtractTransformSecret()

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
