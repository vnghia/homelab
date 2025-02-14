import binascii

import pulumi_random as random
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from homelab_integration.config.s3 import S3IntegrationConfig
from homelab_traefik_service.config.dynamic.http import TraefikHttpDynamicConfig
from homelab_traefik_service.config.dynamic.service import TraefikDynamicServiceConfig
from homelab_traefik_service.config.static import TraefikStaticConfig
from pulumi import ResourceOptions

from .config import NgheConfig


class NgheService(ServiceResourceBase[NgheConfig]):
    KEY_LENGTH = 16

    def __init__(
        self,
        model: ServiceModel[NgheConfig],
        *,
        opts: ResourceOptions | None,
        s3_integration_config: S3IntegrationConfig,
        docker_resource_args: DockerResourceArgs,
        traefik_static_config: TraefikStaticConfig,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.key = random.RandomPassword(
            "key", opts=self.child_opts, length=self.KEY_LENGTH, special=False
        ).result
        self.build_containers(
            options={
                None: ContainerModelBuildArgs(
                    envs={
                        "NGHE_DATABASE__KEY": self.key.apply(
                            lambda x: binascii.hexlify(x.encode()).decode("ascii")
                        ),
                        "NGHE_INTEGRATION__SPOTIFY__ID": self.model.config.spotify.id,
                        "NGHE_INTEGRATION__SPOTIFY__SECRET": self.model.config.spotify.secret,
                        "NGHE_INTEGRATION__LASTFM__KEY": self.model.config.lastfm.key,
                        **s3_integration_config.to_envs(use_default_region=False),
                    },
                )
            }
        )

        self.traefik = TraefikHttpDynamicConfig(
            name=self.name(),
            public=True,
            service=TraefikDynamicServiceConfig(
                int(self.model.container.envs["NGHE_SERVER__PORT"].to_str())
            ),
        ).build_resource(
            "traefik",
            opts=self.child_opts,
            volume_resource=self.docker_resource_args.volume,
            containers=self.CONTAINERS,
            static_config=traefik_static_config,
        )

        self.register_outputs({})
