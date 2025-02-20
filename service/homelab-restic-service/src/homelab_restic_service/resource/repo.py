from typing import Any

from docker.errors import ContainerError
from homelab_docker.client import DockerClient
from homelab_docker.resource.image import ImageResource
from homelab_pydantic import HomelabBaseModel
from pulumi import Input, ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider

from ..config import ResticConfig
from ..config.repo import ResticRepoConfig


class ResticRepoProviderProps(HomelabBaseModel):
    image: str
    restic: ResticRepoConfig

    password: str

    @property
    def id_(self) -> str:
        return self.restic.repo

    def to_envs(self) -> dict[str, str]:
        return self.restic.to_envs(self.password)


class ResticRepo:
    @classmethod
    def exist(cls, props: ResticRepoProviderProps) -> bool:
        # https://restic.readthedocs.io/en/stable/075_scripting.html#check-if-a-repository-is-already-initialized
        client = DockerClient()
        envs = props.to_envs()
        try:
            client.containers.run(
                props.image,
                entrypoint=["/usr/bin/restic"],
                command=["cat", "config"],
                detach=False,
                environment=envs,
                remove=True,
            )
            return True
        except ContainerError as error:
            if error.exit_status == 10:
                return False
            else:
                raise error

    @classmethod
    def init(cls, props: ResticRepoProviderProps) -> None:
        client = DockerClient()
        envs = props.to_envs()
        client.containers.run(
            props.image,
            entrypoint=["/usr/bin/restic"],
            command=["init"],
            detach=False,
            environment=envs,
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
        config: ResticConfig,
        *,
        opts: ResourceOptions | None,
        password: Input[str],
        image_resource: ImageResource,
    ):
        super().__init__(
            ResticRepoProvider(),
            resource_name,
            {
                "image": image_resource.remotes[config.image].image_id,
                "restic": config.repo.model_dump(mode="json", by_alias=True),
                "password": password,
            },
            opts,
        )
