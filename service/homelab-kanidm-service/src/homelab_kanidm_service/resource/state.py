from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import typing
from typing import Any, ClassVar

from homelab_docker.extract import GlobalExtract
from homelab_docker.resource.file.config import JsonDefaultModel
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider, UpdateResult
from pydantic.alias_generators import to_camel

if typing.TYPE_CHECKING:
    from .. import KanidmService


class KanidmStateProviderProps(HomelabBaseModel):
    binary: ClassVar[str] = "kanidm-provision"

    url: str
    password: str
    state: JsonDefaultModel

    def provision(self) -> None:
        binary = shutil.which(self.binary)
        if not binary:
            raise ValueError("{} is not installed".format(self.binary))

        with tempfile.NamedTemporaryFile(mode="w") as file:
            json.dump(self.rename_key(self.state.model_dump(mode="json")), file)
            file.flush()

            subprocess.check_call(
                [binary, "--url", self.url, "--state", file.name],
                env={"KANIDM_PROVISION_IDM_ADMIN_TOKEN": self.password},
            )

    @classmethod
    def rename_key(cls, data: dict[Any, Any] | list[Any]) -> dict[Any, Any] | list[Any]:
        if isinstance(data, list):
            return [
                cls.rename_key(item) if isinstance(item, (dict, list)) else item
                for item in data
            ]
        return {
            to_camel(key): cls.rename_key(value)
            if isinstance(value, (dict, list))
            else value
            for key, value in data.items()
        }


class KanidmStateProvider(ResourceProvider):
    RESOURCE_ID = "kanidm"

    serialize_as_secret_always = True

    def create(self, props: dict[str, Any]) -> CreateResult:
        kanidm_props = KanidmStateProviderProps(**props)
        kanidm_props.provision()
        return CreateResult(
            id_=self.RESOURCE_ID, outs=kanidm_props.model_dump(mode="json")
        )

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        kanidm_props = KanidmStateProviderProps(**news)
        kanidm_props.provision()
        return UpdateResult(outs=kanidm_props.model_dump(mode="json"))


class KanidmStateResource(Resource, module="kanidm", name="State"):
    def __init__(self, opts: ResourceOptions | None, kanidm_service: KanidmService):
        super().__init__(
            KanidmStateProvider(),
            KanidmStateProvider.RESOURCE_ID,
            {
                "url": kanidm_service.docker_resource_args.hostnames[True][
                    kanidm_service.name()
                ].apply(lambda x: "https://{}".format(x)),
                "password": kanidm_service.idm_admin.password,
                "state": GlobalExtract.extract_recursively(
                    kanidm_service.config.state.model_dump(mode="json"),
                    kanidm_service,
                    None,
                ),
            },
            opts,
        )
