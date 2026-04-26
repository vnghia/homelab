import typing
from typing import Any, ClassVar

import httpx
from homelab_pydantic import DictAnyAdapter, HomelabBaseModel
from pulumi import ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider

if typing.TYPE_CHECKING:
    from ... import MailService


class MailStalwartJmapProviderProps(HomelabBaseModel):
    RESOURCE_KEY: ClassVar[str] = "resource"
    SET_KEY: ClassVar[str] = "@set"

    url: str
    username: str
    password: str
    type: str
    data: dict[str, Any]

    def create(self) -> tuple[str, dict[str, Any]]:
        data = self.data
        for key, value in data.items():
            if isinstance(value, list):
                if value[0] == self.SET_KEY:
                    data[key] = dict.fromkeys(value[1:], True)
                else:
                    data[key] = {str(i): item for i, item in enumerate(value)}

        with httpx.Client(
            base_url=self.url, auth=httpx.BasicAuth(self.username, self.password)
        ) as client:
            response = (
                client.post(
                    "/jmap",
                    json={
                        "methodCalls": [
                            [
                                "x:{}/set".format(self.type),
                                {"create": {self.RESOURCE_KEY: self.data}},
                                "c1",
                            ]
                        ],
                        "using": ["urn:ietf:params:jmap:core", "urn:stalwart:jmap"],
                    },
                )
                .raise_for_status()
                .json()
            )
            try:
                resource = DictAnyAdapter.validate_python(
                    response["methodResponses"][0][1]["created"][self.RESOURCE_KEY]
                )
                id = str(resource["id"])
            except KeyError as error:
                raise RuntimeError(response) from error
            return id, resource

    def delete(self, id: str) -> None:
        with httpx.Client(
            base_url=self.url, auth=httpx.BasicAuth(self.username, self.password)
        ) as client:
            client.post(
                "/jmap",
                json={
                    "methodCalls": [
                        [
                            "x:{}/set".format(self.type),
                            {"destroy": [id]},
                            "c1",
                        ]
                    ],
                    "using": ["urn:ietf:params:jmap:core", "urn:stalwart:jmap"],
                },
            ).raise_for_status()


class MailStalwartJmapProvider(ResourceProvider):
    def create(self, props: dict[str, Any]) -> CreateResult:
        jmap_props = MailStalwartJmapProviderProps(**props)
        id, _ = jmap_props.create()
        return CreateResult(id_=id, outs=jmap_props.model_dump(mode="json"))

    def delete(self, id: str, props: dict[str, Any]) -> None:
        MailStalwartJmapProviderProps(**props).delete(id)


class MailStalwartJmapResource(Resource, module="stalwart", name="Jmap"):
    def __init__(
        self,
        type: str,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__(
            MailStalwartJmapProvider(),
            name,
            {
                "url": mail_service.stalwart_recovery_url,
                "username": mail_service.stalwart_recovery_username,
                "password": mail_service.stalwart_recovery_password,
                "type": type,
                "data": data,
            },
            opts,
        )


class MailStalwartNetworkListenerResource(
    MailStalwartJmapResource, module="stalwart", name="NetworkListener"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("NetworkListener", name, opts, mail_service, data)
