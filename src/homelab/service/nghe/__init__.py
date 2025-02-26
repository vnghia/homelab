import binascii

import pulumi_random as random
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_traefik_service import TraefikService
from pulumi import ResourceOptions

from .config import NgheConfig


class NgheService(ServiceWithConfigResourceBase[NgheConfig]):
    KEY_LENGTH = 16

    def __init__(
        self,
        model: ServiceWithConfigModel[NgheConfig],
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        s3_envs: dict[str, str] = {}
        if self.config.s3:
            s3_envs = {k: v for k, v in self.config.s3.to_envs().items()}

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
                        "NGHE_INTEGRATION__SPOTIFY__ID": self.config.spotify.id,
                        "NGHE_INTEGRATION__SPOTIFY__SECRET": self.config.spotify.secret,
                        "NGHE_INTEGRATION__LASTFM__KEY": self.config.lastfm.key,
                        **s3_envs,
                    }
                )
            }
        )

        self.traefik = self.config.traefik.build_resources(
            opts=self.child_opts,
            main_service=self,
            traefik_service=traefik_service,
        )

        self.register_outputs({})
