import hashlib
import io
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path, PosixPath
from typing import Any, Iterator

import pulumi
from docker.errors import NotFound
from docker.models.containers import Container
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
    BaseModel,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    computed_field,
    field_validator,
)

from homelab_docker.client import DockerClient
from homelab_docker.model.container.volume_path import (
    ContainerVolumePath,
    ContainerVolumeResourcePath,
)


class FileProviderProps(BaseModel):
    container_volume_path: ContainerVolumePath
    content: str
    mode: int

    @field_validator("container_volume_path", mode="after")
    def check_path_not_empty(
        cls, container_volume_path: ContainerVolumePath
    ) -> ContainerVolumePath:
        if not container_volume_path.path.name:
            raise ValueError("Container volume path should not be empty")
        return container_volume_path

    @field_validator("content", mode="wrap")
    @classmethod
    def ignore_non_string_input(
        cls, data: Any, _: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> str:
        if isinstance(data, str):
            return data
        else:
            pulumi.log.warn(
                "Non string data encountered: {}. Validated data: {}".format(
                    data, info.data
                )
            )
            return "Unknown"

    @property
    def id_(self) -> str:
        return self.container_volume_path.id_

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()


class FileVolumeProxy:
    IMAGE = "busybox"
    WORKING_DIR = PosixPath("/mnt/volume/")

    @classmethod
    @contextmanager
    def container(cls, volume: str) -> Iterator[Container]:
        container = DockerClient().containers.create(
            image=cls.IMAGE,
            network_mode="none",
            volumes={volume: {"bind": cls.WORKING_DIR.as_posix(), "mode": "rw"}},
            working_dir=cls.WORKING_DIR.as_posix(),
            detach=True,
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
            with tarfile.open(mode="w", fileobj=tar_file) as tar:
                with tempfile.NamedTemporaryFile() as file:
                    file.write(props.content.encode())
                    file.flush()
                    tar.add(
                        file.name,
                        arcname=props.container_volume_path.path,
                        filter=lambda x: x.replace(mode=props.mode, deep=False),
                    )
            tar_file.seek(0)
            return tar_file

        with cls.container(props.container_volume_path.volume) as container:
            container.put_archive(cls.WORKING_DIR.as_posix(), compress_tar())

    @classmethod
    def read_file(cls, props: FileProviderProps) -> FileProviderProps | None:
        with cls.container(props.container_volume_path.volume) as container:
            try:
                tar_file = io.BytesIO()
                (stream, stat) = container.get_archive(
                    (cls.WORKING_DIR / props.container_volume_path.path).as_posix()
                )
                for chunk in stream:
                    tar_file.write(chunk)
                tar_file.seek(0)
                with tarfile.open(mode="r", fileobj=tar_file) as tar:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        name = stat["name"]
                        tar.extract(name, path=tmpdir, set_attrs=False)
                        return props.model_copy(
                            update={
                                "content": open(Path(tmpdir) / name).read(),
                                "mode": stat["mode"],
                            }
                        )
            except NotFound:
                return None

    @classmethod
    def delete_file(cls, props: FileProviderProps) -> None:
        DockerClient().containers.run(
            image=cls.IMAGE,
            command=["rm", "-rf", props.container_volume_path.path.as_posix()],
            remove=True,
            network_mode="none",
            volumes={
                props.container_volume_path.volume: {
                    "bind": cls.WORKING_DIR.as_posix(),
                    "mode": "rw",
                }
            },
            working_dir=cls.WORKING_DIR.as_posix(),
            detach=True,
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
        return DiffResult(
            changes=file_olds != file_news,
            stables=["volume", "path"],
        )

    def update(
        self, _id: str, _olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        file_news = FileProviderProps(**news)
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
        container_volume_resource_path: ContainerVolumeResourcePath,
        content: Input[str],
        mode: int = 0o444,
    ):
        super().__init__(
            FileProvider(),
            resource_name,
            {
                "container_volume_path": container_volume_resource_path.to_props(),
                "content": content,
                "mode": mode,
                "hash": None,
            },
            ResourceOptions.merge(
                opts,
                ResourceOptions(
                    delete_before_replace=True,
                    deleted_with=container_volume_resource_path.volume,
                ),
            ),
        )
