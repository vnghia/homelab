from typing import Any, ClassVar

from docker.errors import ContainerError
from homelab_backup_service.config.restic import ResticConfig
from homelab_docker.client import DockerClient
from homelab_docker.resource.image import ImageResource
from homelab_integration.config.s3 import S3IntegrationConfig
from pulumi import Input, ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider
from pydantic import BaseModel


class ResticRepoProviderProps(BaseModel):
    RESTIC_IMAGE_KEY: ClassVar[str] = "restic"

    image: str
    restic: ResticConfig
    s3: S3IntegrationConfig

    password: str

    @property
    def id_(self) -> str:
        return self.restic.build_repo_url(self.s3)

    def to_envs(self) -> dict[str, str]:
        return self.s3.to_envs(use_default_region=True) | {
            "RESTIC_REPOSITORY": self.id_,
            "RESTIC_PASSWORD": self.password,
        }


class ResticRepo:
    @classmethod
    def exist(cls, props: ResticRepoProviderProps) -> bool:
        # https://restic.readthedocs.io/en/stable/075_scripting.html#check-if-a-repository-is-already-initialized
        client = DockerClient()
        envs = props.to_envs()
        try:
            client.containers.run(
                props.image,
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
            props.image, command=["init"], detach=False, environment=envs, remove=True
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
        s3_integration_config: S3IntegrationConfig,
        image_resource: ImageResource,
    ):
        super().__init__(
            ResticRepoProvider(),
            resource_name,
            {
                "image": image_resource.remotes[
                    ResticRepoProviderProps.RESTIC_IMAGE_KEY
                ].image_id,
                "restic": config.model_dump(mode="json"),
                "s3": s3_integration_config.model_dump(mode="json", by_alias=True),
                "password": password,
            },
            opts,
        )
