from pathlib import Path
from typing import Any, Self, Type

import deepmerge
import pulumi
import yaml
from homelab_docker.config.host import HostServiceModelConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.host import HostModel
from homelab_global import ProjectArgs
from homelab_global.config import GlobalConfig
from homelab_network.config import NetworkConfig
from homelab_pydantic import HomelabBaseModel

from homelab_config.constant import PROJECT_LABELS, PROJECT_NAME, PROJECT_STACK


class HostConfig[TSun: ServiceConfigBase, TEarth: ServiceConfigBase](HomelabBaseModel):
    sun: HostModel[TSun]
    earth: HostModel[TEarth]

    _service_model: HostServiceModelConfig

    def model_post_init(self, context: Any, /) -> None:
        self._service_model = HostServiceModelConfig(
            {
                "sun": self.sun.service_model("sun"),
                "earth": self.earth.service_model("earth"),
            }
        )

    @property
    def service_model(self) -> HostServiceModelConfig:
        return self._service_model


class Config[TSun: ServiceConfigBase, TEarth: ServiceConfigBase](HomelabBaseModel):
    host: HostConfig[TSun, TEarth]
    network: NetworkConfig
    global_: GlobalConfig

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
    def get_host_config(
        cls, docker_type: Type[HostConfig[TSun, TEarth]]
    ) -> HostConfig[TSun, TEarth]:
        key = "host"

        config_data = {}
        config_dir = (
            Path(__file__).parent.parent.parent.parent / "config" / key
        ).resolve(True)

        for host in HostConfig.model_fields:
            host_data: dict[str, Any] = {}
            host_dir = config_dir / host

            for host_service_path in host_dir.glob("*.yaml"):
                service_path = config_dir / key / host_service_path.name
                with (
                    open(service_path) as service_file,
                    open(host_service_path) as host_service_file,
                ):
                    service_data = yaml.full_load(service_file)
                    if host_service_data := yaml.full_load(host_service_file):
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
    def build(cls, host_type: Type[HostConfig[TSun, TEarth]]) -> Self:
        return cls(
            host=cls.get_host_config(host_type),
            network=NetworkConfig.model_validate(cls.get_key("network")),
            global_=GlobalConfig.model_validate(cls.get_key("global")),
        )

    @property
    def project_args(self) -> ProjectArgs:
        return ProjectArgs(
            name=PROJECT_NAME, stack=PROJECT_STACK, labels=PROJECT_LABELS
        )
