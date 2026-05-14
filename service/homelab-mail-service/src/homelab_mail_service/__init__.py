from typing import ClassVar

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
from homelab_kanidm_service import KanidmService
from homelab_mail.resource import MailResource
from pulumi import Output, ResourceOptions

from .config import MailConfig
from .resource.stalwart import MailStalwartResource


class MailService(ExtraService[MailConfig]):
    STALWART_CONTAINER: ClassVar[str | None] = None

    def __init__(
        self,
        model: ServiceWithConfigModel[MailConfig],
        *,
        opts: ResourceOptions,
        mail_resource: MailResource,
        kanidm_service: KanidmService,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.mail_resource = mail_resource
        self.stalwart_config = self.config.stalwart

        self.http_port_source = self.stalwart_config.listener.root["http"].port
        self.http_port = GlobalExtractor(self.http_port_source).extract_str(
            self.extractor_args
        )

        self.stalwart_url = "https://{}".format(
            self.extractor_args.hostnames[self.stalwart_config.system.record][
                self.stalwart_config.system.hostname
            ].value
        )
        self.stalwart_recovery_url = Output.format(
            "http://{}:{}",
            GlobalExtractor(self.stalwart_config.recovery.address).extract_str(
                self.extractor_args
            ),
            self.http_port,
        )
        self.stalwart_recovery_username = GlobalExtractor(
            self.stalwart_config.recovery.username
        ).extract_str(self.extractor_args)
        self.stalwart_recovery_password = GlobalExtractor(
            self.stalwart_config.recovery.password
        ).extract_str(self.extractor_args)

        if self.stalwart_config.recovery.enabled or self.stalwart_config.recovery.admin:
            self.options[self.STALWART_CONTAINER].envs = {
                "STALWART_RECOVERY_ADMIN": Output.concat(
                    self.stalwart_recovery_username,
                    ":",
                    self.stalwart_recovery_password,
                )
            }
        if self.stalwart_config.recovery.enabled:
            self.options[self.STALWART_CONTAINER].add_envs(
                {
                    "STALWART_RECOVERY_MODE": "1",
                    "STALWART_RECOVERY_MODE_PORT": self.http_port,
                }
            )
            self.options[self.STALWART_CONTAINER].add_network(
                ContainerNetworkModelBuildArgs(
                    ports=ContainerPortsConfig(
                        {
                            "recovery": ContainerPortRangeConfig(
                                internal=self.http_port_source,
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
            opts=self.child_opts, mail_service=self, kanidm_service=kanidm_service
        )
