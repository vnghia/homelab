from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container import ContainerNetworkModelBuildArgs
from homelab_docker.model.docker.container.network import (
    ContainerBridgeNetworkArgs,
    ContainerBridgeNetworkConfig,
)
from homelab_docker.model.docker.container.port import ContainerPortProtocol
from homelab_docker.model.docker.container.ports import (
    ContainerPortRangeConfig,
    ContainerPortsConfig,
)
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_extra_service import ExtraService
from pulumi import Output, ResourceOptions

from .config import MailConfig
from .resource.stalwart import MailStalwartResource


class MailService(ExtraService[MailConfig]):
    STALWART_CONTAINER = None

    def __init__(
        self,
        model: ServiceWithConfigModel[MailConfig],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.stalwart_config = self.config.stalwart

        self.stalwart_recovery_url = Output.format(
            "http://{}:{}",
            GlobalExtractor(self.stalwart_config.recovery.address).extract_str(
                self.extractor_args
            ),
            self.stalwart_config.recovery.port,
        )
        self.stalwart_recovery_username = GlobalExtractor(
            self.stalwart_config.recovery.username
        ).extract_str(self.extractor_args)
        self.stalwart_recovery_password = GlobalExtractor(
            self.stalwart_config.recovery.password
        ).extract_str(self.extractor_args)

        if self.stalwart_config.recovery.enabled:
            self.options[self.STALWART_CONTAINER].envs = {
                "STALWART_RECOVERY_MODE": "1",
                "STALWART_RECOVERY_MODE_PORT": str(self.stalwart_config.recovery.port),
                "STALWART_RECOVERY_ADMIN": Output.concat(
                    self.stalwart_recovery_username,
                    ":",
                    self.stalwart_recovery_password,
                ),
                "STALWART_HEALTHCHECK_URL": "http://localhost:{}/healthz/live".format(
                    self.stalwart_config.recovery.port
                ),
            }
            self.options[self.STALWART_CONTAINER].add_network(
                ContainerNetworkModelBuildArgs(
                    ports=ContainerPortsConfig(
                        {
                            "recovery": ContainerPortRangeConfig(
                                internal=self.stalwart_config.recovery.port,
                                protocol=ContainerPortProtocol.TCP,
                            )
                        }
                    ),
                    bridges={
                        "direct": ContainerBridgeNetworkArgs(
                            config=ContainerBridgeNetworkConfig()
                        )
                    },
                )
            )

        self.build(None)

        self.stalwart_resource = MailStalwartResource(
            opts=self.child_opts, mail_service=self
        )
