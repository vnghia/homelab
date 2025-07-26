from typing import Any

from docker.errors import ContainerError
from homelab_docker.client import DockerClient
from homelab_pydantic import HomelabBaseModel
from pulumi import Output, ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider


class ResticRepoProviderProps(HomelabBaseModel):
    image: str
    envs: dict[str, str]

    @property
    def id_(self) -> str:
        return self.envs["RESTIC_REPOSITORY"]


class ResticRepo:
    NOT_INITIALIZED_YET = 10

    @classmethod
    def exist(cls, props: ResticRepoProviderProps) -> bool:
        # https://restic.readthedocs.io/en/stable/075_scripting.html#check-if-a-repository-is-already-initialized
        client = DockerClient()
        try:
            client.containers.run(
                props.image,
                entrypoint=["/usr/bin/restic"],
                command=["cat", "config"],
                detach=False,
                environment=props.envs,
                remove=True,
            )
            return True
        except ContainerError as error:
            if error.exit_status == cls.NOT_INITIALIZED_YET:
                return False
            raise error

    @classmethod
    def init(cls, props: ResticRepoProviderProps) -> None:
        client = DockerClient()
        client.containers.run(
            props.image,
            entrypoint=["/usr/bin/restic"],
            command=["init"],
            detach=False,
            environment=props.envs,
            remove=True,
        )


class ResticRepoProvider(ResourceProvider):
    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        restic_props = ResticRepoProviderProps(**props)
        if not ResticRepo.exist(restic_props):
            ResticRepo.init(restic_props)
        return CreateResult(
            id_=restic_props.id_, outs=restic_props.model_dump(mode="json")
        )


class ResticRepoResource(Resource, module="restic", name="Repo"):
    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        image: Output[str],
        envs: dict[str, Output[str]],
    ) -> None:
        super().__init__(
            ResticRepoProvider(), resource_name, {"image": image, "envs": envs}, opts
        )
