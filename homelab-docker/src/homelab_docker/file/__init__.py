import hashlib
import io
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path, PosixPath
from typing import Any, Iterator

import docker
from docker.errors import NotFound
from docker.models.containers import Container
from pulumi import Input, ResourceOptions
from pulumi.dynamic import (
    ConfigureRequest,
    CreateResult,
    DiffResult,
    ReadResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator

from homelab_docker.volume_path import VolumePath, VolumePathInput


class FileProviderProps(BaseModel):
    model_config = ConfigDict(strict=True)

    volume_path: VolumePath
    content: str
    mode: int = Field(strict=False)

    @field_validator("volume_path", mode="after")
    def check_path_not_empty(cls, volume_path: VolumePath) -> VolumePath:
        if not volume_path.path.name:
            raise ValueError("{} should not be empty".format(volume_path.path))
        return volume_path

    @property
    def id_(self) -> str:
        return self.volume_path.id_

    @property
    def hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()


class VolumeProxy:
    IMAGE = "busybox"
    WORKING_DIR = PosixPath("/mnt/volume/")

    @classmethod
    @contextmanager
    def container(cls, volume: str) -> Iterator[Container]:
        container = docker.from_env().containers.create(
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
        docker.from_env().images.pull(repository=cls.IMAGE)

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
                        arcname=props.volume_path.path,
                        filter=lambda x: x.replace(mode=props.mode, deep=False),
                    )
            tar_file.seek(0)
            return tar_file

        with cls.container(props.volume_path.volume) as container:
            container.put_archive(cls.WORKING_DIR.as_posix(), compress_tar())

    @classmethod
    def read_file(cls, props: FileProviderProps) -> FileProviderProps | None:
        with cls.container(props.volume_path.volume) as container:
            try:
                tar_file = io.BytesIO()
                (stream, stat) = container.get_archive(
                    (cls.WORKING_DIR / props.volume_path.path).as_posix()
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
        docker.from_env().containers.run(
            image=cls.IMAGE,
            command=["rm", "-rf", props.volume_path.path.as_posix()],
            remove=True,
            network_mode="none",
            volumes={
                props.volume_path.volume: {
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
        VolumeProxy.pull_image()

    def create(self, props: dict[str, Any]) -> CreateResult:
        file_props = FileProviderProps(**props)
        VolumeProxy.create_file(file_props)
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
        VolumeProxy.create_file(file_news)
        return UpdateResult(outs=file_news.model_dump(mode="json"))

    def delete(self, _id: str, props: dict[str, Any]) -> None:
        file_props = FileProviderProps(**props)
        VolumeProxy.delete_file(file_props)

    def read(self, id_: str, props: dict[str, Any]) -> ReadResult:
        file_props = FileProviderProps(**props)
        read_props = VolumeProxy.read_file(file_props)
        if read_props:
            return ReadResult(id_=id_, outs=read_props.model_dump(mode="json"))
        else:
            return ReadResult(outs={})


class File(Resource, module="docker", name="File"):
    def __init__(
        self,
        resource_name: str,
        volume_path: VolumePathInput,
        content: Input[str],
        mode: Input[int] = 0o444,
        opts: ResourceOptions | None = None,
    ):
        super().__init__(
            FileProvider(),
            resource_name,
            {
                "volume_path": volume_path.to_props(),
                "content": content,
                "mode": mode,
            },
            ResourceOptions.merge(
                opts,
                ResourceOptions(
                    delete_before_replace=True, deleted_with=volume_path.volume
                ),
            ),
        )
