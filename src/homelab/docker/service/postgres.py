import homelab_config as config
import pulumi_docker as docker
import pulumi_random as random
from homelab_config.docker.service.database.postgres import Postgres as Model
from homelab_docker.container import Container
from homelab_docker.container.healthcheck import Healthcheck
from homelab_docker.container.network import Network
from homelab_docker.container.string import String
from homelab_docker.container.tmpfs import Tmpfs
from homelab_docker.container.volume import Volume
from homelab_docker.volume_path import VolumePath
from pulumi import ComponentResource, Output, ResourceOptions
from pydantic import PostgresDsn

from homelab.docker.resource import Resource


class Postgres(ComponentResource):
    def __init__(
        self,
        service_name: str,
        name: str,
        model: Model,
        resource: Resource,
        opts: ResourceOptions | None,
    ) -> None:
        self.service_name = service_name
        self.name = name

        self.model = model
        self.resource = resource

        super().__init__(self.model.DATABASE_TYPE, self.short_name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.username = self.model.user or self.service_name
        self.database = self.model.database or self.service_name
        self.password = random.RandomPassword(
            self.short_name,
            opts=self.child_opts,
            length=self.model.PASSWORD_LENGTH,
            special=False,
        ).result

        self.containers: dict[int, docker.Container] = {}
        for version in self.model.versions:
            full_name_version = self.get_full_name_version(version)
            self.containers[version] = Container(
                image=self.model.get_image(version),
                healthcheck=Healthcheck(
                    tests=["CMD", "pg_isready", "-U", self.database],
                    interval="5s",
                    timeout="5s",
                    retries=5,
                ),
                tmpfs=[Tmpfs(data=self.model.PGRUN_PATH)],
                networks={self.model.network: Network()},
                volumes={full_name_version: Volume(data=self.model.PGDATA_PATH)},
                envs={
                    "POSTGRES_USER": String(data=self.username),
                    "POSTGRES_DB": String(data=self.database),
                    "PGDATA": String(data=VolumePath(volume=full_name_version)),
                },
                labels=config.constant.PROJECT_LABELS,
            ).build_resource(
                full_name_version,
                timezone=config.docker.timezone,
                resource=resource.to_docker_resource(),
                opts=self.child_opts,
                envs={
                    "POSTGRES_PASSWORD": self.password,
                },
            )

        self.register_outputs({})

    @property
    def short_name(self) -> str:
        return self.model.get_short_name(self.name)

    def get_short_name_version(self, version: int) -> str:
        return self.model.get_short_name_version(self.name, version)

    def get_full_name_version(self, version: int) -> str:
        return self.model.get_full_name_version(self.service_name, self.name, version)

    @property
    def container(self) -> docker.Container:
        return self.containers[self.model.versions[0]]

    def get_url(self) -> Output[PostgresDsn]:
        return Output.format(
            "postgres://{0}:{1}@{2}:{3}/{4}?sslmode=disable",
            self.username,
            self.password,
            self.get_full_name_version(self.model.versions[0]),
            self.model.PORT,
            self.database,
        ).apply(PostgresDsn)
