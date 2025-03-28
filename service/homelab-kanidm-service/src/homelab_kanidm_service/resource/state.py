from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import typing
from typing import Any, ClassVar

from homelab_docker.extract import GlobalExtract
from homelab_docker.resource.file.config import JsonDefaultModel
from homelab_pydantic import HomelabBaseModel
from pulumi import Output, ResourceOptions
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pydantic import ValidationError, computed_field, model_validator
from pydantic.alias_generators import to_camel

from homelab_kanidm_service.config.state.person import KanidmStatePersonConfig

if typing.TYPE_CHECKING:
    from .. import KanidmService


class KanidmStateProviderProps(HomelabBaseModel):
    binary: ClassVar[str] = "kanidm-provision"

    url: str
    password: str
    state: JsonDefaultModel

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        return hashlib.sha256(self.state.model_dump_json().encode()).hexdigest()

    @model_validator(mode="before")
    @classmethod
    def ignore_hash(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data.pop("hash", None)
        return data

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
            (
                key
                if not isinstance(key, str)
                or key.startswith(KanidmStatePersonConfig.GROUP_PREFIX)
                else to_camel(key)
            ): cls.rename_key(value) if isinstance(value, (dict, list)) else value
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

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        kanidm_olds = KanidmStateProviderProps(**olds)
        try:
            kanidm_news = KanidmStateProviderProps(**news)
            return DiffResult(changes=kanidm_olds != kanidm_news)
        except ValidationError:
            return DiffResult(changes=True)

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        kanidm_props = KanidmStateProviderProps(**news)
        kanidm_props.provision()
        return UpdateResult(outs=kanidm_props.model_dump(mode="json"))


class KanidmStateResource(Resource, module="kanidm", name="State"):
    hash: Output[str]

    def __init__(self, opts: ResourceOptions | None, kanidm_service: KanidmService):
        state = kanidm_service.config.state.build(kanidm_service.OPENID_GROUP)

        super().__init__(
            KanidmStateProvider(),
            KanidmStateProvider.RESOURCE_ID,
            {
                "url": kanidm_service.docker_resource_args.hostnames[True][
                    kanidm_service.name()
                ].apply(lambda x: "https://{}".format(x)),
                "password": kanidm_service.idm_admin.password,
                "state": GlobalExtract.extract_recursively(
                    state.model_dump(mode="json"), kanidm_service, None
                ),
                "hash": None,
            },
            opts,
        )
