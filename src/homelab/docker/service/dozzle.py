from pulumi import ResourceOptions

from homelab import common
from homelab.docker.image import Image
from homelab.docker.network import Network
from homelab.docker.service.base import Base, BuildOption
from homelab.docker.volume import Volume


class Dozzle(Base):
    def __init__(
        self,
        network: Network,
        image: Image,
        volume: Volume,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(
            network=network,
            image=image,
            volume=volume,
            opts=opts,
        )

        self.hostname = common.get_name(name=None, project=True, stack=True)
        self.build_containers(
            options={
                None: BuildOption(
                    opts=ResourceOptions(delete_before_replace=True),
                    envs={
                        "DOZZLE_BASE": "/log",
                        "DOZZLE_FILTER": f"label=pulumi.stack={common.constant.PROJECT_STACK}",
                        "DOZZLE_ENABLE_ACTIONS": "true",
                    },
                )
            }
        )
