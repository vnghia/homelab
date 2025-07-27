from pathlib import Path
from typing import Any, ClassVar, Self, Type

import deepmerge
import pulumi
import yaml
from homelab_docker.config import DockerConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_network.config import NetworkConfig
from homelab_pydantic import HomelabBaseModel

from .constant import PROJECT_LABELS, PROJECT_NAME, PROJECT_STACK


class DockerConfigs[TSun: ServiceConfigBase](HomelabBaseModel):
    sun: DockerConfig[TSun]


class Config[TSun: ServiceConfigBase](HomelabBaseModel):
    PROJECT_NAME: ClassVar[str] = PROJECT_NAME
    PROJECT_STACK: ClassVar[str] = PROJECT_STACK
    PROJECT_LABELS: ClassVar[dict[str, str]] = PROJECT_LABELS

    dockers: DockerConfigs[TSun]
    network: NetworkConfig

    @classmethod
    def get_key(cls, key: str) -> Any:
        data = pulumi.Config().get_object(key, {})

        for path in (
            (Path(__file__).parent.parent.parent.parent / "config" / key)
            .resolve(True)
            .glob("*.yaml")
        ):
            with open(path) as file:
                data = deepmerge.always_merger.merge(data, yaml.full_load(file))

        return deepmerge.always_merger.merge(
            data, pulumi.Config().get_object("stack-{}".format(key), {})
        )

    @classmethod
    def get_docker_configs(
        cls, docker_type: Type[DockerConfigs[TSun]]
    ) -> DockerConfigs[TSun]:
        key = "docker"

        config_data = {}
        config_dir = (
            Path(__file__).parent.parent.parent.parent / "config" / key
        ).resolve(True)

        for host in DockerConfigs.model_fields:
            host_data: dict[str, Any] = {}
            host_dir = config_dir / "hosts" / host

            for host_service_path in host_dir.glob("*.yaml"):
                service_path = config_dir / host_service_path.name
                with (
                    open(service_path) as service_file,
                    open(host_service_path) as host_service_file,
                ):
                    service_data = yaml.full_load(service_file)
                    host_service_data = yaml.full_load(host_service_file)
                    if host_service_data:
                        final_data = deepmerge.always_merger.merge(
                            service_data, host_service_data
                        )
                    else:
                        final_data = service_data
                    host_data = deepmerge.always_merger.merge(host_data, final_data)

            config_data[host] = host_data

        return docker_type.model_validate(
            deepmerge.always_merger.merge(
                config_data, pulumi.Config().get_object("stack-{}".format(key), {})
            )
        )

    @classmethod
    def get_name(
        cls, name: str | None, project: bool = False, stack: bool = True
    ) -> str:
        return "-".join(
            ([cls.PROJECT_NAME] if project or not name else [])
            + ([name] if name else [])
            + ([cls.PROJECT_STACK] if stack else [])
        )

    @classmethod
    def build(cls, docker_type: Type[DockerConfigs[TSun]]) -> Self:
        return cls(
            dockers=cls.get_docker_configs(docker_type),
            network=NetworkConfig.model_validate(cls.get_key("network")),
        )
