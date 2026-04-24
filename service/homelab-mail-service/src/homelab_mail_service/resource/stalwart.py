import shutil
import subprocess
import tempfile
import typing
from typing import Any, ClassVar

import orjson
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider, UpdateResult

if typing.TYPE_CHECKING:
    from .. import MailService


class MailStalwartProviderProps(HomelabBaseModel):
    BINARY: ClassVar[str] = "stalwart-cli"

    url: str
    username: str
    password: str
    plan: list[Any] = []

    def provision(self) -> None:
        binary = shutil.which(self.BINARY)
        if not binary:
            raise ValueError("{} is not installed".format(self.BINARY))

        with tempfile.NamedTemporaryFile(mode="w+b") as file:
            file.write(orjson.dumps(self.plan))
            file.flush()

            subprocess.check_call(
                [binary, "apply", "--json", "--file", file.name],
                env={
                    "STALWART_URL": self.url,
                    "STALWART_USER": self.username,
                    "STALWART_PASSWORD": self.password,
                },
            )


class MailStalwartProvider(ResourceProvider):
    RESOURCE_ID = "stalwart"

    serialize_as_secret_always = True

    def create(self, props: dict[str, Any]) -> CreateResult:
        stalwart_props = MailStalwartProviderProps(**props)
        stalwart_props.provision()
        return CreateResult(
            id_=self.RESOURCE_ID, outs=stalwart_props.model_dump(mode="json")
        )

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        stalwart_props = MailStalwartProviderProps(**news)
        stalwart_props.provision()
        return UpdateResult(outs=stalwart_props.model_dump(mode="json"))


class MailStalwartResource(Resource, module="stalwart", name="Configuration"):
    def __init__(self, opts: ResourceOptions, mail_service: MailService) -> None:
        super().__init__(
            MailStalwartProvider(),
            MailStalwartProvider.RESOURCE_ID,
            {
                "url": mail_service.stalwart_recovery_url,
                "username": mail_service.stalwart_recovery_username,
                "password": mail_service.stalwart_recovery_password,
                "plan": self.compute_plan(mail_service),
            },
            opts,
        )

    def compute_plan(self, mail_service: MailService) -> list[Any]:
        return (
            self.destroy_operations()
            + self.create_listeners_operations(mail_service)
            + self.create_noreply_operations(mail_service)
        )

    def destroy_operations(self) -> list[Any]:
        return [
            {"@type": "destroy", "object": "NetworkListener"},
            {"@type": "destroy", "object": "Domain"},
            {"@type": "destroy", "object": "Account", "value": {"@type": "Group"}},
            {"@type": "destroy", "object": "Account", "value": {"@type": "User"}},
        ]

    def create_listeners_operations(self, mail_service: MailService) -> list[Any]:
        mail_config = mail_service.mail_resource.config
        return [
            {
                "@type": "create",
                "object": "NetworkListener",
                "value": {
                    "smpts": {
                        "name": "smtps",
                        "bind": {"[::]:{}".format(mail_config.address.port): True},
                        "protocol": "smtp",
                        "tlsImplicit": True,
                    }
                },
            }
        ]

    def create_noreply_operations(self, mail_service: MailService) -> list[Any]:
        mail_noreply = mail_service.mail_resource.noreply

        operations = []
        for name, account in mail_noreply.accounts.items():
            domain_key = "domain-noreply-{}".format(name)
            user_key = "user-noreply-{}".format(name)
            operations += [
                {
                    "@type": "create",
                    "object": "Domain",
                    "value": {
                        domain_key: {
                            "name": account.domain,
                            "certificateManagement": {"@type": "Manual"},
                            "allowRelaying": True,
                            "dkimManagement": {"@type": "Manual"},
                            "dnsManagement": {"@type": "Manual"},
                            "subAddressing": {"@type": "Disabled"},
                        }
                    },
                },
                {
                    "@type": "create",
                    "object": "Account",
                    "value": {
                        user_key: {
                            "@type": "User",
                            "name": account.username,
                            "credentials": {
                                "0": {
                                    "@type": "Password",
                                    "secret": account.password.bcrypt_hash,
                                }
                            },
                            "domainId": "#{}".format(domain_key),
                        }
                    },
                },
            ]

        return operations
