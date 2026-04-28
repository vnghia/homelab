import typing
from typing import Any, ClassVar

import httpx
from homelab_pydantic import DictAnyAdapter, HomelabBaseModel
from pulumi import ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider, UpdateResult
from pydantic import ConfigDict

if typing.TYPE_CHECKING:
    from ... import MailService


class MailStalwartJmapProviderProps(HomelabBaseModel):
    model_config = ConfigDict(extra="ignore")

    RESOURCE_KEY: ClassVar[str] = "resource"
    SET_KEY: ClassVar[str] = "@set"

    SINGLETON_ID: ClassVar[str] = "singleton"

    url: str
    username: str
    password: str
    type: str
    singleton: bool
    data: dict[str, Any]
    attrs: list[str] = []

    @classmethod
    def transform_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        data = data.copy()
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = cls.transform_data(data[key])
            elif isinstance(value, list):
                if value[0] == cls.SET_KEY:
                    data[key] = dict.fromkeys(value[1:], True)
                else:
                    data[key] = {
                        str(i): cls.transform_data(item)
                        if isinstance(item, dict)
                        else item
                        for i, item in enumerate(value)
                    }
            elif isinstance(value, float):
                data[key] = int(value)
        return data

    @classmethod
    def compare_data(cls, olds: dict[str, Any], news: dict[str, Any]) -> dict[str, Any]:
        diff: dict[str, Any] = {}

        for new_key, new_value in news.items():
            if new_key in {"@type", "else", "match"}:
                return news
            if old_value := olds.get(new_key):
                if type(old_value) is not type(new_value):
                    raise ValueError(
                        "old ({}) and new ({}) value must have the same type".format(
                            type(old_value), type(new_value)
                        )
                    )

                if old_value != new_value:
                    if isinstance(new_value, dict):
                        if value_diff := cls.compare_data(old_value, new_value):
                            diff[new_key] = value_diff
                    else:
                        diff[new_key] = new_value

            else:
                diff[new_key] = new_value

        for old_key, old_value in olds.items():
            if old_key not in news:
                diff[old_key] = {} if isinstance(old_value, dict) else False

        return diff

    @classmethod
    def extract_data(cls, data: dict[str, Any], attrs: list[str]) -> dict[str, Any]:
        return {attr: data[attr] for attr in attrs}

    def create(self) -> tuple[str, dict[str, Any]]:
        if self.singleton:
            return self.SINGLETON_ID, self.update(self.SINGLETON_ID, olds={})

        data = self.transform_data(self.data)
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
                                {"create": {self.RESOURCE_KEY: data}},
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
                return id, self.extract_data(resource, self.attrs)
            except KeyError as error:
                raise RuntimeError(data, response) from error

    def update(self, id: str, olds: dict[str, Any]) -> dict[str, Any]:
        olds = self.transform_data(olds)
        news = self.transform_data(self.data)
        diff = self.compare_data(olds, news)
        if not diff:
            return self.extract_data(self.data, self.attrs)

        with httpx.Client(
            base_url=self.url, auth=httpx.BasicAuth(self.username, self.password)
        ) as client:
            response = (
                client.post(
                    "/jmap",
                    json={
                        "methodCalls": [
                            ["x:{}/set".format(self.type), {"update": {id: diff}}, "c1"]
                        ],
                        "using": ["urn:ietf:params:jmap:core", "urn:stalwart:jmap"],
                    },
                )
                .raise_for_status()
                .json()
            )
            try:
                resource = response["methodResponses"][0][1]["updated"][id]
                if not resource:
                    return self.extract_data(self.data, self.attrs)
                return self.extract_data(
                    DictAnyAdapter.validate_python(resource), self.attrs
                )
            except KeyError as error:
                raise RuntimeError(diff, response) from error

    def delete(self, id: str) -> None:
        if self.singleton:
            self.__replace__(data={}).update(self.SINGLETON_ID, olds=self.data)
            return

        with httpx.Client(
            base_url=self.url, auth=httpx.BasicAuth(self.username, self.password)
        ) as client:
            client.post(
                "/jmap",
                json={
                    "methodCalls": [
                        ["x:{}/set".format(self.type), {"destroy": [id]}, "c1"]
                    ],
                    "using": ["urn:ietf:params:jmap:core", "urn:stalwart:jmap"],
                },
            ).raise_for_status()


class MailStalwartJmapProvider(ResourceProvider):
    def create(self, props: dict[str, Any]) -> CreateResult:
        jmap_props = MailStalwartJmapProviderProps(**props)
        id, _ = jmap_props.create()
        return CreateResult(id_=id, outs=jmap_props.model_dump(mode="json"))

    def update(
        self, id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        jmap_olds = MailStalwartJmapProviderProps(**olds)
        jmap_news = MailStalwartJmapProviderProps(**news)
        jmap_news.update(id, jmap_olds.data)
        return UpdateResult(outs=jmap_news.model_dump(mode="json"))

    def delete(self, id: str, props: dict[str, Any]) -> None:
        MailStalwartJmapProviderProps(**props).delete(id)


class MailStalwartJmapResource(Resource, module="stalwart", name="Jmap"):
    def __init__(
        self,
        type: str,
        singleton: bool,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
        attrs: list[str] | None = None,
        secret_attrs: list[str] | None = None,
    ) -> None:
        super().__init__(
            MailStalwartJmapProvider(),
            name,
            {
                "url": mail_service.stalwart_recovery_url
                if mail_service.stalwart_config.recovery.enabled
                else mail_service.stalwart_url,
                "username": mail_service.stalwart_recovery_username,
                "password": mail_service.stalwart_recovery_password,
                "type": type,
                "singleton": singleton,
                "data": data,
            }
            | dict.fromkeys((attrs or []) + (secret_attrs or [])),
            ResourceOptions.merge(
                opts,
                ResourceOptions(
                    delete_before_replace=True, additional_secret_outputs=secret_attrs
                ),
            ),
        )


class MailStalwartTracerResource(
    MailStalwartJmapResource, module="stalwart", name="Tracer"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("Tracer", False, name, opts, mail_service, data)


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
        super().__init__("NetworkListener", False, name, opts, mail_service, data)


class MailStalwartDirectoryResource(
    MailStalwartJmapResource, module="stalwart", name="Directory"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("Directory", False, name, opts, mail_service, data)


class MailStalwartAuthenticationResource(
    MailStalwartJmapResource, module="stalwart", name="Authentication"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("Authentication", True, name, opts, mail_service, data)


class MailStalwartDomainResource(
    MailStalwartJmapResource, module="stalwart", name="Domain"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("Domain", False, name, opts, mail_service, data)


class MailStalwartSystemSettingsResource(
    MailStalwartJmapResource, module="stalwart", name="SystemSettings"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("SystemSettings", True, name, opts, mail_service, data)


class MailStalwartMtaStageEhloResource(
    MailStalwartJmapResource, module="stalwart", name="MtaStageEhlo"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("MtaStageEhlo", True, name, opts, mail_service, data)


class MailStalwartMtaStageRcptResource(
    MailStalwartJmapResource, module="stalwart", name="MtaStageRcpt"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("MtaStageRcpt", True, name, opts, mail_service, data)


class MailStalwartMtaStageAuthResource(
    MailStalwartJmapResource, module="stalwart", name="MtaStageAuth"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("MtaStageAuth", True, name, opts, mail_service, data)


class MailStalwartMtaRouteResource(
    MailStalwartJmapResource, module="stalwart", name="MtaRoute"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("MtaRoute", False, name, opts, mail_service, data)


class MailStalwartMtaOutboundStrategyResource(
    MailStalwartJmapResource, module="stalwart", name="MtaOutboundStrategy"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("MtaOutboundStrategy", True, name, opts, mail_service, data)


class MailStalwartAccountResource(
    MailStalwartJmapResource, module="stalwart", name="Account"
):
    def __init__(
        self,
        name: str,
        opts: ResourceOptions,
        mail_service: MailService,
        data: dict[str, Any],
    ) -> None:
        super().__init__("Account", False, name, opts, mail_service, data)
