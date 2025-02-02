import homelab_config as config
import pulumi_random as random
from homelab_config.docker.service.database.postgres import Postgres as Model
from homelab_docker.container import Container
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
        self.model = model
        self.short_name = self.model.get_short_name(service_name, name)
        self.full_name = self.model.get_full_name(service_name, name)
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

        self.container = Container(
            image=self.model.image,
            tmpfs=[Tmpfs(data=self.model.PGRUN_PATH)],
            networks={self.model.network: Network()},
            volumes={self.full_name: Volume(data=self.model.PGDATA_PATH)},
            envs={
                "POSTGRES_USER": String(data=self.username),
                "POSTGRES_DB": String(data=self.database),
                "PGDATA": String(data=VolumePath(volume=self.full_name)),
            },
            labels=config.constant.PROJECT_LABELS,
        ).build_resource(
            self.full_name,
            timezone=config.docker.timezone,
            resource=resource.to_docker_resource(),
            opts=self.child_opts,
            envs={
                "POSTGRES_PASSWORD": self.password,
            },
        )

        self.register_outputs({"name": self.container.name})

    def get_url(self) -> Output[PostgresDsn]:
        return Output.format(
            "postgres://{0}:{1}@{2}:{3}/{4}?sslmode=disable",
            self.username,
            self.password,
            self.full_name,
            self.model.PORT,
            self.database,
        ).apply(PostgresDsn)
