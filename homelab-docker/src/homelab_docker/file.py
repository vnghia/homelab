import hashlib
import io
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path, PosixPath
from typing import Iterator

import docker
import pulumi_docker
from docker.errors import NotFound
from docker.models.containers import Container
from pulumi import Input, Output, ResourceOptions
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    ReadResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pydantic import BaseModel, ConfigDict, Field

from homelab_docker.pydantic.path import RelativePath


class FileProviderProps(BaseModel):
    model_config = ConfigDict(strict=True)

    volume: str
    path: RelativePath
    content: str
    mode: int = Field(strict=False)

    @property
    def id_(self) -> str:
        return f"{self.volume}:{self.path.as_posix()}"

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
    def pull_image(cls):
        docker.from_env().images.pull(repository=cls.IMAGE)

    @classmethod
    def create_file(cls, props: FileProviderProps):
        def compress_tar():
            tar_file = io.BytesIO()
            with tarfile.open(mode="w", fileobj=tar_file) as tar:
                with tempfile.NamedTemporaryFile() as file:
                    file.write(props.content.encode())
                    file.flush()
                    tar.add(
                        file.name,
                        arcname=props.path,
                        filter=lambda x: x.replace(mode=props.mode, deep=False),
                    )
            tar_file.seek(0)
            return tar_file

        with cls.container(props.volume) as container:
            container.put_archive(cls.WORKING_DIR.as_posix(), compress_tar())

    @classmethod
    def read_file(cls, props: FileProviderProps) -> FileProviderProps | None:
        with cls.container(props.volume) as container:
            try:
                tar_file = io.BytesIO()
                (stream, stat) = container.get_archive(
                    (cls.WORKING_DIR / props.path).as_posix()
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
    def delete_file(cls, props: FileProviderProps):
        docker.from_env().containers.run(
            image=cls.IMAGE,
            command=["rm", "-rf", props.path.as_posix()],
            remove=True,
            network_mode="none",
            volumes={props.volume: {"bind": cls.WORKING_DIR.as_posix(), "mode": "rw"}},
            working_dir=cls.WORKING_DIR.as_posix(),
            detach=True,
        )


class FileProvider(ResourceProvider):
    serialize_as_secret_always = False

    def configure(self, req) -> None:
        VolumeProxy.pull_image()

    def create(self, props) -> CreateResult:
        props = FileProviderProps(**props)
        VolumeProxy.create_file(props)
        return CreateResult(id_=props.id_, outs=props.model_dump(mode="json"))

    def diff(self, _id: str, olds, news) -> DiffResult:
        olds = FileProviderProps(**olds)
        news = FileProviderProps(**news)
        return DiffResult(
            changes=olds != news,
            stables=["volume", "path"],
        )

    def update(self, _id: str, _olds, news) -> UpdateResult:
        news = FileProviderProps(**news)
        VolumeProxy.create_file(news)
        return UpdateResult(outs=news.model_dump(mode="json"))

    def delete(self, _id: str, props):
        props = FileProviderProps(**props)
        VolumeProxy.delete_file(props)

    def read(self, id_: str, props) -> ReadResult:
        props = FileProviderProps(**props)
        props = VolumeProxy.read_file(props)
        if props:
            return ReadResult(id_=id_, outs=props.model_dump(mode="json"))
        else:
            return ReadResult(outs={})


class File(Resource, module="docker", name="File"):
    def __init__(
        self,
        resource_name: str,
        volume: pulumi_docker.Volume,
        path: Input[RelativePath],
        content: Input[str],
        mode: Input[int] = 0o444,
        opts: ResourceOptions | None = None,
    ):
        super().__init__(
            FileProvider(),
            resource_name,
            {
                "volume": volume.name,
                "path": Output.from_input(path).apply(lambda x: x.as_posix()),
                "content": content,
                "mode": mode,
            },
            ResourceOptions.merge(
                opts, ResourceOptions(delete_before_replace=True, deleted_with=volume)
            ),
        )
