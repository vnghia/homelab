import shutil
import subprocess
from typing import Any, ClassVar

from homelab_pydantic import HomelabBaseModel
from pulumi import Output, ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider
from pydantic import PositiveInt


class ResticRepositoryProviderProps(HomelabBaseModel):
    BINARY: ClassVar[str] = "restic"
    NOT_INITIALIZED_YET: ClassVar[PositiveInt] = 10

    envs: dict[str, str]

    @property
    def id_(self) -> str:
        return self.envs["RESTIC_REPOSITORY"]

    @property
    def binary(self) -> str:
        binary = shutil.which(self.BINARY)
        if not binary:
            raise ValueError("{} is not installed".format(self.BINARY))
        return binary

    def run(self, command: list[str]) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run([self.binary, *command], check=False, env=self.envs)

    def exist(self) -> bool:
        # https://restic.readthedocs.io/en/stable/075_scripting.html#check-if-a-repository-is-already-initialized
        return self.run(["cat", "config"]).returncode == self.NOT_INITIALIZED_YET

    def init(self) -> None:
        self.run(["init"])


class ResticRepositoryProvider(ResourceProvider):
    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        restic_props = ResticRepositoryProviderProps(**props)
        if not restic_props.exist():
            restic_props.init()
        return CreateResult(
            id_=restic_props.id_, outs=restic_props.model_dump(mode="json")
        )


class ResticRepositoryResource(Resource, module="restic", name="Repository"):
    def __init__(
        self, resource_name: str, *, opts: ResourceOptions, envs: dict[str, Output[str]]
    ) -> None:
        super().__init__(
            ResticRepositoryProvider(), resource_name, {"envs": envs}, opts
        )
