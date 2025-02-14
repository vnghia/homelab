from pathlib import PosixPath
from typing import Mapping

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.file.config import ConfigFileModel
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.config import ConfigFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_traefik_service import TraefikService
from homelab_traefik_service.config.dynamic.http import TraefikHttpDynamicConfig
from homelab_traefik_service.config.dynamic.service import TraefikDynamicServiceConfig
from pulumi import Input, ResourceOptions


class DaguService(ServiceResourceBase[None]):
    DAGS_DIR_ENV = "DAGU_DAGS_DIR"

    def __init__(
        self,
        model: ServiceModel[None],
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.build_containers(
            options={
                None: ContainerModelBuildArgs(
                    envs={"DAGU_TZ": str(self.docker_resource_args.timezone)}
                )
            }
        )

        self.traefik = TraefikHttpDynamicConfig(
            name=self.name(),
            public=False,
            service=TraefikDynamicServiceConfig(
                int(self.model.container.envs["DAGU_PORT"].to_str())
            ),
        ).build_resource(None, opts=self.child_opts, traefik_service=traefik_service)

        self.register_outputs({})

    def get_config_container_volume_path(self) -> ContainerVolumePath:
        return self.model.container.envs[self.DAGS_DIR_ENV].as_container_volume_path()

    def get_env_container_volume_path(self, name: str) -> ContainerVolumePath:
        return self.get_config_container_volume_path().join(PosixPath(name), ".env")

    def build_env_file(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        name: str,
        envs: Mapping[str, Input[str]],
    ) -> ConfigFileResource:
        return ConfigFileModel(
            container_volume_path=self.get_env_container_volume_path(name), data=envs
        ).build_resource(
            resource_name,
            opts=opts,
            volume_resource=self.docker_resource_args.volume,
        )
