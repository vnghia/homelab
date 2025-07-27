from __future__ import annotations

import base64
import re
from enum import StrEnum
from typing import Any, ClassVar

import pulumi
from docker.models.containers import Container
from homelab_docker.client import DockerClient
from homelab_docker.resource import DockerResourceArgs
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Input, Output, ResourceOptions
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    ReadResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pydantic import computed_field, field_validator, model_validator


class NtfyUserAclPermission(StrEnum):
    READ_WRITE = "read-write"
    READ_ONLY = "read-only"
    WRITE_ONLY = "write-only"


class NtfyUserAclConfig(HomelabRootModel[dict[str, NtfyUserAclPermission]]):
    ACL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^- (read-write|read-only|write-only) access to topic (.*)$"
    )

    root: dict[str, NtfyUserAclPermission] = {}


class NtfyUserProviderProps(HomelabBaseModel):
    USER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^user ([\w]+|\*) \(role: (\w+), .*$"
    )

    docker_host: str
    username: str
    password: str
    container: str
    role: str
    acl: NtfyUserAclConfig

    @field_validator("username", "password", "container", mode="before")
    @classmethod
    def ignore_pulumi_unknown(cls, data: Any) -> Any:
        if isinstance(data, pulumi.output.Unknown):
            pulumi.log.warn("Pulumi unknown output encountered: {}".format(data))
            return ""
        return data

    @model_validator(mode="before")
    @classmethod
    def ignore_authorization(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data.pop("authorization", None)
        return data

    @property
    def id_(self) -> str:
        return self.username

    @computed_field  # type: ignore[prop-decorator]
    @property
    def authorization(self) -> str:
        return "Basic {}".format(
            base64.b64encode(
                "{}:{}".format(self.username, self.password).encode()
            ).decode()
        )

    def get_container(self) -> Container:
        return DockerClient(self.docker_host).containers.get(self.container)

    def get_user(self) -> NtfyUserProviderProps | None:
        result: str = (
            self.get_container()
            .exec_run(["ntfy", "access", self.username])
            .output.decode()
        )
        result = result.strip()
        if result == "user {} does not exist".format(self.username):
            return None
        lines = result.splitlines()
        match_user = self.USER_PATTERN.match(lines[0])
        if not match_user:
            raise RuntimeError("Could not extract user information")
        if match_user[1] != self.username:
            raise RuntimeError()
        user = self.__replace__(role=match_user[2])

        acls: dict[str, str] = {}
        for line in lines[1:]:
            match_acl = NtfyUserAclConfig.ACL_PATTERN.match(line)
            if match_acl:
                acls[match_acl[2]] = match_acl[1]
        user = user.__replace__(acl=NtfyUserAclConfig.model_validate(acls))

        user.change_pass()
        return user

    def add(self) -> None:
        self.get_container().exec_run(
            ["ntfy", "user", "add", "--role", self.role, self.username],
            environment={"NTFY_PASSWORD": self.password},
        )
        self.upsert_acl()

    def upsert_acl(self) -> None:
        container = self.get_container()
        container.exec_run(["ntfy", "access", "--reset", self.username])
        for topic, permission in self.acl.root.items():
            container.exec_run(["ntfy", "access", self.username, topic, permission])

    def change_role(self) -> None:
        self.get_container().exec_run(
            ["ntfy", "user", "change-role", self.username, self.role],
        )

    def change_pass(self) -> None:
        self.get_container().exec_run(
            ["ntfy", "user", "change-pass", self.username],
            environment={"NTFY_PASSWORD": self.password},
        )

    def delete(self) -> None:
        self.get_container().exec_run(["ntfy", "user", "del", self.username])

    def upsert(self) -> None:
        user = self.get_user()
        if user:
            if user.role != self.role:
                self.change_role()
            if user.acl != self.acl:
                self.upsert_acl()
        else:
            self.add()


class NtfyUserProvider(ResourceProvider):
    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        user_props = NtfyUserProviderProps(**props)
        user_props.add()
        return CreateResult(id_=user_props.id_, outs=user_props.model_dump(mode="json"))

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        user_news = NtfyUserProviderProps(**news)
        user_olds = NtfyUserProviderProps(**olds).__replace__(
            container=user_news.container
        )
        if user_olds.username != user_olds.password:
            user_olds.delete()
        user_news.upsert()
        return UpdateResult(outs=user_news.model_dump(mode="json"))

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        user_olds = NtfyUserProviderProps(**olds)
        user_news = NtfyUserProviderProps(**news)
        return DiffResult(changes=user_olds != user_news)

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        user_props = NtfyUserProviderProps(**props)
        user_props.delete()

    def read(self, id_: str, props: dict[str, Any]) -> ReadResult:
        user_props = NtfyUserProviderProps(**props)
        user = user_props.get_user()
        if user:
            return ReadResult(id_=id_, outs=user.model_dump(mode="json"))
        return ReadResult(outs={})


class NtfyUserResource(Resource, module="ntfy", name="User"):
    authorization: Output[str]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        container: Input[str],
        username: Input[str],
        password: Input[str],
        role: Input[str],
        acl: NtfyUserAclConfig,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(
            NtfyUserProvider(),
            resource_name,
            {
                "docker-host": docker_resource_args.config.host.ssh,
                "container": container,
                "username": username,
                "password": password,
                "role": role,
                "acl": acl.model_dump(mode="python"),
                "authorization": None,
            },
            ResourceOptions.merge(
                opts, ResourceOptions(additional_secret_outputs=["authorization"])
            ),
        )
