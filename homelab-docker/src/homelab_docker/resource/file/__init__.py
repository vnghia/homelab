from __future__ import annotations

import io
import tarfile
import tempfile
import typing
from contextlib import contextmanager
from pathlib import PosixPath
from typing import Any, Iterator

import pulumi
from docker.errors import NotFound
from docker.models.containers import Container
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import Input, Output, ResourceOptions
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    ReadResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pydantic import (
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    computed_field,
    field_validator,
    model_validator,
)

from ...client import DockerClient
from ...model.docker.container.volume_path import ContainerVolumePath
from ...model.file import FileDataModel, FileLocationModel, FilePermissionModel
from ...model.user import UidGidModel

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class FileProviderProps(HomelabBaseModel):
    docker_host: str
    location: FileLocationModel
    data: FileDataModel
    permission: FilePermissionModel = FilePermissionModel()

    @property
    def id_(self) -> str:
        return self.location.id_

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        return self.data.hash

    @field_validator("data", mode="wrap")
    @classmethod
    def ignore_pulumi_unknown(
        cls, data: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> FileDataModel:
        if isinstance(data, pulumi.output.Unknown):
            pulumi.log.warn(
                "Pulumi unknown output encountered: {}. Validated data: {}".format(
                    data, info.data
                )
            )
            return FileDataModel(content="")
        return handler(data)  # type: ignore[no-any-return]

    @model_validator(mode="before")
    @classmethod
    def ignore_hash(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data.pop("hash", None)
        return data


class FileVolumeProxy:
    WORKING_DIR = AbsolutePath(PosixPath("/mnt/volume"))

    @classmethod
    @contextmanager
    def container(cls, docker_host: str, volume: str) -> Iterator[Container]:
        container = DockerClient(docker_host).containers.create(
            image=DockerClient.UTILITY_IMAGE,
            detach=True,
            network_mode="none",
            volumes={volume: {"bind": cls.WORKING_DIR.as_posix(), "mode": "rw"}},
            working_dir=cls.WORKING_DIR.as_posix(),
        )
        try:
            yield container
        finally:
            container.remove(force=True)

    @classmethod
    def update_tarinfo_permission(
        cls, tarinfo: tarfile.TarInfo, permission: FilePermissionModel
    ) -> tarfile.TarInfo:
        return tarinfo.replace(
            mode=permission.mode,
            uid=permission.owner.uid,
            gid=permission.owner.gid,
            deep=False,
        )

    @classmethod
    def create_file(cls, props: FileProviderProps) -> None:
        def compress_tar() -> io.BytesIO:
            tar_file = io.BytesIO()
            with (
                tarfile.open(mode="w|", fileobj=tar_file) as tar,
                tempfile.NamedTemporaryFile() as file,
            ):
                file.write(props.data.content.encode())
                file.flush()
                tar.add(
                    file.name,
                    arcname=props.location.path.root,
                    filter=lambda x: cls.update_tarinfo_permission(x, props.permission),
                )
            tar_file.seek(0)
            return tar_file

        with cls.container(props.docker_host, props.location.volume) as container:
            container.put_archive(cls.WORKING_DIR.as_posix(), compress_tar())

    @classmethod
    def read_file(cls, props: FileProviderProps) -> FileProviderProps | None:
        with cls.container(props.docker_host, props.location.volume) as container:
            try:
                tar_file = io.BytesIO()
                (stream, stat) = container.get_archive(
                    (cls.WORKING_DIR / props.location.path).as_posix()
                )
                for chunk in stream:
                    tar_file.write(chunk)
                tar_file.seek(0)
                with tarfile.open(mode="r", fileobj=tar_file) as tar:
                    name = stat["name"]
                    member = tar.getmember(name)
                    file = tar.extractfile(member)
                    if not file:
                        raise KeyError("tar member {} not found".format(name))
                    return props.__replace__(
                        data=FileDataModel(content=file.read().decode()),
                        permission=FilePermissionModel(
                            mode=member.mode,
                            owner=UidGidModel(uid=member.uid, gid=member.gid),
                        ),
                    )
            except NotFound:
                return None

    @classmethod
    def delete_file(cls, props: FileProviderProps) -> None:
        DockerClient(props.docker_host).containers.run(
            image=DockerClient.UTILITY_IMAGE,
            command=["rm", "-rf", props.location.path.as_posix()],
            detach=False,
            network_mode="none",
            remove=True,
            volumes={
                props.location.volume: {
                    "bind": cls.WORKING_DIR.as_posix(),
                    "mode": "rw",
                }
            },
            working_dir=cls.WORKING_DIR.as_posix(),
        )


class FileProvider(ResourceProvider):
    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        file_props = FileProviderProps(**props)
        FileVolumeProxy.create_file(file_props)
        return CreateResult(id_=file_props.id_, outs=file_props.model_dump(mode="json"))

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        file_olds = FileProviderProps(**olds)
        file_news = FileProviderProps(**news)
        return DiffResult(changes=file_olds != file_news)

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        file_olds = FileProviderProps(**olds)
        file_news = FileProviderProps(**news)
        if file_olds.location != file_news.location:
            FileVolumeProxy.delete_file(file_olds)
        FileVolumeProxy.create_file(file_news)
        return UpdateResult(outs=file_news.model_dump(mode="json"))

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        file_props = FileProviderProps(**props)
        FileVolumeProxy.delete_file(file_props)

    def read(self, id_: str, props: dict[str, Any]) -> ReadResult:
        file_props = FileProviderProps(**props)
        read_props = FileVolumeProxy.read_file(file_props)
        if read_props:
            return ReadResult(id_=id_, outs=read_props.model_dump(mode="json"))
        return ReadResult(outs={})


class FileResource(Resource, module="docker", name="File"):
    hash: Output[str]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        volume_path: ContainerVolumePath,
        content: Input[str],
        permission: UidGidModel | FilePermissionModel,
        extractor_args: ExtractorArgs,
    ) -> None:
        self.volume_path = volume_path
        volume = extractor_args.host.docker.volume[volume_path.volume]
        super().__init__(
            FileProvider(),
            resource_name,
            {
                "docker-host": extractor_args.host_model.access.ssh,
                "location": {
                    "volume": volume.resource.name,
                    "path": volume_path.path.as_posix(),
                },
                "data": {"content": content},
                "permission": permission.model_dump()
                if isinstance(permission, FilePermissionModel)
                else {
                    "mode": FilePermissionModel.DEFAULT_MODE,
                    "owner": permission.model_dump(),
                },
                "hash": None,
            },
            ResourceOptions.merge(opts, ResourceOptions(deleted_with=volume.resource)),
        )

    def to_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.volume_path.to_path(extractor_args)
