import shutil
import subprocess
import typing
from typing import Any, ClassVar

from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)

if typing.TYPE_CHECKING:
    from .. import MailService


class MailStalwartProviderProps(HomelabBaseModel):
    BINARY: ClassVar[str] = "stalwart-cli"

    url: str
    username: str
    password: str

    def provision(self) -> None:
        binary = shutil.which(self.BINARY)
        if not binary:
            raise ValueError("{} is not installed".format(self.BINARY))

        subprocess.check_call(
            [binary, "describe"],
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


class MailStalwartResource(Resource, module="stalwart", name="Configuration"):
    def __init__(self, opts: ResourceOptions, mail_service: MailService) -> None:
        super().__init__(
            MailStalwartProvider(),
            MailStalwartProvider.RESOURCE_ID,
            {
                "url": mail_service.stalwart_recovery_url,
                "username": mail_service.stalwart_recovery_username,
                "password": mail_service.stalwart_recovery_password,
            },
            opts,
        )
