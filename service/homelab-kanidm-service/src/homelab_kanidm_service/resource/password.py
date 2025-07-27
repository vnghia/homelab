import re
from typing import Any, ClassVar

from homelab_docker.client import DockerClient
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import Input, Output, ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider, UpdateResult


class KanidmPasswordProviderProps(HomelabBaseModel):
    PASSWORD_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r'.*new_password: "([\d\w]+)".*'
    )

    docker_host: str
    container: str
    account: str
    config_path: str

    def recover_account(self) -> str:
        result: str = (
            DockerClient(self.docker_host)
            .containers.get(self.container)
            .exec_run(
                ["kanidmd", "recover-account", "-c", self.config_path, self.account]
            )
            .output.decode()
        )
        result = result.replace("\n", " ")
        match = self.PASSWORD_PATTERN.match(result)
        if not match:
            raise ValueError("Could not extract password from log: {}".format(result))
        return match[1]


class KanidmPasswordProvider(ResourceProvider):
    serialize_as_secret_always = True

    def create(self, props: dict[str, Any]) -> CreateResult:
        kanidm_props = KanidmPasswordProviderProps(**props)
        password = kanidm_props.recover_account()
        return CreateResult(
            id_=kanidm_props.account,
            outs=kanidm_props.model_dump(mode="json") | {"password": password},
        )

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        password = olds.pop("password")
        kanidm_news = KanidmPasswordProviderProps(**news)
        return UpdateResult(
            outs=kanidm_news.model_dump(mode="json") | {"password": password},
        )


class KanidmPasswordResource(Resource, module="kanidm", name="Password"):
    password: Output[str]

    def __init__(
        self,
        *,
        opts: ResourceOptions,
        container: Input[str],
        account: str,
        config_path: AbsolutePath,
    ) -> None:
        super().__init__(
            KanidmPasswordProvider(),
            account,
            {
                "container": container,
                "account": account,
                "config_path": config_path.as_posix(),
                "password": None,
            },
            ResourceOptions.merge(
                opts, ResourceOptions(additional_secret_outputs=["password"])
            ),
        )
