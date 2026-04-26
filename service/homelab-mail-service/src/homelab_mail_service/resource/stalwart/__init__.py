import typing
from collections import defaultdict

from homelab_docker.extract.global_ import GlobalExtractor
from pulumi import ComponentResource, Output, ResourceOptions

from .jmap import (
    MailStalwartAccountResource,
    MailStalwartDomainResource,
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
        mail_noreply = mail_service.mail_resource.noreply

        self.domains: dict[str, dict[str, MailStalwartDomainResource]] = defaultdict(
            dict
        )

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

        for name, account in mail_noreply.accounts.items():
            if account.hostname in self.domains[account.record]:
                domain = self.domains[account.record][account.hostname]
            else:
                domain = MailStalwartDomainResource(
                    "{}-{}".format(account.record, account.hostname),
                    self.child_opts,
                    mail_service,
                    {
                        "name": account.domain,
                        "certificateManagement": {"@type": "Manual"},
                        "allowRelaying": True,
                        "dkimManagement": {"@type": "Manual"},
                        "dnsManagement": {"@type": "Manual"},
                        "subAddressing": {"@type": "Disabled"},
                    },
                )
                self.domains[account.record][account.hostname] = domain

            MailStalwartAccountResource(
                "noreply-{}".format(name),
                self.child_opts,
                mail_service,
                {
                    "@type": "User",
                    "name": account.username,
                    "credentials": [
                        {
                            "@type": "Password",
                            "secret": account.password.bcrypt_hash,
                        }
                    ],
                    "domainId": domain.id,
                },
            )

        self.register_outputs({})
