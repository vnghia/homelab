import typing

from homelab_docker.extract.global_ import GlobalExtractor
from pulumi import ComponentResource, Output, ResourceOptions

from .jmap import (
    MailStalwartJmapProviderProps,
    MailStalwartNetworkListenerResource,
    MailStalwartTracerResource,
)

if typing.TYPE_CHECKING:
    from ... import MailService


class MailStalwartResource(ComponentResource):
    RESOURCE_NAME = "stalwart"

    def __init__(self, *, opts: ResourceOptions, mail_service: MailService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)
        stalwart_config = mail_service.stalwart_config

        MailStalwartTracerResource(
            "stdout",
            self.child_opts,
            mail_service,
            {"@type": "Stdout", "enable": True, "level": "info"},
        )

        for name, model in stalwart_config.listener.root.items():
            MailStalwartNetworkListenerResource(
                name,
                self.child_opts,
                mail_service,
                {
                    "name": name,
                    "bind": [
                        MailStalwartJmapProviderProps.SET_KEY,
                        Output.concat(
                            "[::]:",
                            GlobalExtractor(model.port).extract_str(
                                mail_service.extractor_args
                            ),
                        ),
                    ],
                    "protocol": model.protocol,
                    "useTls": model.use_tls,
                    "tlsImplicit": model.tls_implicit if model.use_tls else False,
                },
            )

        self.register_outputs({})
