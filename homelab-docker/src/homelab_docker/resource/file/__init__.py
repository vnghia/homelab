import io
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path, PosixPath
from typing import Any, Iterator

import pulumi
from docker.errors import NotFound
from docker.models.containers import Container
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import Input, Output, ResourceOptions
from pulumi.dynamic import (
    ConfigureRequest,
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

from homelab_docker.client import DockerClient

from ...model.container.volume import ContainerVolumesConfig
from ...model.container.volume_path import ContainerVolumePath
from ...model.file import FileDataModel, FileLocationModel
from ..volume import VolumeResource


class FileProviderProps(HomelabBaseModel):
    location: FileLocationModel
    data: FileDataModel

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
            return FileDataModel(content="", mode=0o444)
        else:
            return handler(data)  # type: ignore[no-any-return]

    @model_validator(mode="before")
    @classmethod
    def ignore_hash(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data.pop("hash", None)
        return data


class FileVolumeProxy:
    IMAGE = "busybox"
    WORKING_DIR = AbsolutePath(PosixPath("/mnt/volume"))

    @classmethod
    @contextmanager
    def container(cls, volume: str) -> Iterator[Container]:
        container = DockerClient().containers.create(
            image=cls.IMAGE,
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
    def pull_image(cls) -> None:
        DockerClient().images.pull(repository=cls.IMAGE)

    @classmethod
    def create_file(cls, props: FileProviderProps) -> None:
        def compress_tar() -> io.BytesIO:
            tar_file = io.BytesIO()
            with tarfile.open(mode="w|", fileobj=tar_file) as tar:
                with tempfile.NamedTemporaryFile() as file:
                    file.write(props.data.content.encode())
                    file.flush()
                    tar.add(
                        file.name,
                        arcname=props.location.path.root,
                        filter=lambda x: x.replace(mode=props.data.mode, deep=False),
                    )
            tar_file.seek(0)
            return tar_file

        with cls.container(props.location.volume) as container:
            container.put_archive(cls.WORKING_DIR.as_posix(), compress_tar())

    @classmethod
    def read_file(cls, props: FileProviderProps) -> FileProviderProps | None:
        with cls.container(props.location.volume) as container:
            try:
                tar_file = io.BytesIO()
                (stream, stat) = container.get_archive(
                    (cls.WORKING_DIR / props.location.path).as_posix()
                )
                for chunk in stream:
                    tar_file.write(chunk)
                tar_file.seek(0)
                with tarfile.open(mode="r", fileobj=tar_file) as tar:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        name = stat["name"]
                        tar.extract(name, path=tmpdir, set_attrs=False)
                        return props.__replace__(
                            data=FileDataModel(
                                content=open(Path(tmpdir) / name).read(),
                                mode=stat["mode"],
                            )
                        )
            except NotFound:
                return None

    @classmethod
    def delete_file(cls, props: FileProviderProps) -> None:
        DockerClient().containers.run(
            image=cls.IMAGE,
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

    def configure(self, req: ConfigureRequest) -> None:
        FileVolumeProxy.pull_image()

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
        else:
            return ReadResult(outs={})


class FileResource(Resource, module="docker", name="File"):
    hash: Output[str]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        container_volume_path: ContainerVolumePath,
        content: Input[str],
        mode: int,
        volume_resource: VolumeResource,
    ):
        self.container_volume_path = container_volume_path
        volume = volume_resource[container_volume_path.volume]
        super().__init__(
            FileProvider(),
            resource_name,
            {
                "location": {
                    "volume": volume.name,
                    "path": container_volume_path.path.as_posix(),
                },
                "data": {"content": content, "mode": mode},
                "hash": None,
            },
            ResourceOptions.merge(opts, ResourceOptions(deleted_with=volume)),
        )

    def to_container_path(
        self, container_volumes_config: ContainerVolumesConfig
    ) -> AbsolutePath:
        return self.container_volume_path.to_container_path(container_volumes_config)
