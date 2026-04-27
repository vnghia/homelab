import typing
from collections import defaultdict

from homelab_docker.extract.global_ import GlobalExtractor
from pulumi import ComponentResource, Output, ResourceOptions

from .jmap import (
    MailStalwartAccountResource,
    MailStalwartDomainResource,
    MailStalwartJmapProviderProps,
    MailStalwartMtaOutboundStrategyResource,
    MailStalwartMtaRouteResource,
    MailStalwartMtaStageAuthResource,
    MailStalwartMtaStageEhloResource,
    MailStalwartNetworkListenerResource,
    MailStalwartTracerResource,
)

if typing.TYPE_CHECKING:
    from ... import MailService


class MailStalwartResource(ComponentResource):
    RESOURCE_NAME = "stalwart"

    # TODO: Restrict access to all accounts/reject non FQDN/sasl to local ips after setting up ProxyProtocol
    def __init__(self, *, opts: ResourceOptions, mail_service: MailService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)
        stalwart_config = mail_service.stalwart_config

        mail_config = mail_service.mail_resource.config
        mail_notification = mail_service.mail_resource.notification

        self.domains: dict[str, dict[str, MailStalwartDomainResource]] = defaultdict(
            dict
        )
        self.relays: dict[str, MailStalwartMtaRouteResource] = {}
        self.relay_conditions: dict[str, list[str]] = defaultdict(list)

        MailStalwartTracerResource(
            "stdout",
            self.child_opts,
            mail_service,
            {"@type": "Stdout", "enable": True, "level": "trace"},
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

        for name, relay in mail_config.relay.root.items():
            credential = relay.credential
            self.relays[name] = MailStalwartMtaRouteResource(
                name,
                self.child_opts,
                mail_service,
                {
                    "@type": "Relay",
                    "name": name,
                    "address": credential.host,
                    "port": credential.port,
                    "protocol": "smtp",
                    "implicitTls": True,
                    "authUsername": credential.username,
                    "authSecret": {"@type": "Value", "secret": credential.password},
                },
            )

        for name, account in mail_notification.accounts.items():
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
                "notification-{}".format(name),
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

            if account.relay:
                self.relay_conditions[account.relay].append(
                    "sender == '{}'".format(account.address)
                )

        MailStalwartMtaStageEhloResource(
            "ehlo",
            self.child_opts,
            mail_service,
            {
                "rejectNonFqdn": {
                    "else": "false",
                    "match": [{"if": "local_port == 25", "then": "false"}],
                }
            },
        )

        MailStalwartMtaStageAuthResource(
            "auth",
            self.child_opts,
            mail_service,
            {
                "saslMechanisms": {
                    "else": "false",
                    "match": [
                        {"if": "true", "then": "[plain, login, oauthbearer, xoauth2]"},
                    ],
                },
                "require": {"else": "true"},
            },
        )

        MailStalwartMtaOutboundStrategyResource(
            "route",
            self.child_opts,
            mail_service,
            {
                "route": {
                    "else": "false",
                    "match": [
                        {"if": " || ".join(condition), "then": "'{}'".format(relay)}
                        for relay, condition in self.relay_conditions.items()
                    ],
                }
            },
        )

        self.register_outputs({})
