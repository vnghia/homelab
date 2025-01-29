import tarfile
import tempfile

import docker
import pulumi_docker
from pulumi import Input, Output, ResourceOptions
from pulumi.dynamic import CreateResult, Resource, ResourceProvider
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

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


class VolumeProxy:
    IMAGE = "busybox"
    WORKING_DIR = "/mnt/volume/"

    @classmethod
    def pull_image(cls):
        docker.from_env().images.pull(repository=cls.IMAGE)

    @classmethod
    def create_file(cls, props: FileProviderProps):
        def compress_tar():
            tar_file = tempfile.NamedTemporaryFile()
            with tarfile.open(mode="w", fileobj=tar_file) as tar:
                with tempfile.NamedTemporaryFile() as f:
                    f.write(props.content.encode())
                    f.flush()
                    tar.add(
                        f.name,
                        arcname=props.path,
                        filter=lambda x: x.replace(mode=props.mode, deep=False),
                    )
            tar_file.seek(0)
            return tar_file

        container = docker.from_env().containers.create(
            image=cls.IMAGE,
            network_mode="none",
            volumes={props.volume: {"bind": cls.WORKING_DIR, "mode": "rw"}},
            working_dir=cls.WORKING_DIR,
            detach=True,
        )
        container.put_archive(cls.WORKING_DIR, compress_tar())
        container.remove(force=True)

    @classmethod
    def delete_file(cls, id_: str):
        volume, raw_path = id_.split(":", maxsplit=1)
        path = TypeAdapter(RelativePath).validate_python(raw_path)

        docker.from_env().containers.run(
            image=cls.IMAGE,
            command=["rm", "-rf", path.as_posix()],
            remove=True,
            network_mode="none",
            volumes={volume: {"bind": cls.WORKING_DIR, "mode": "rw"}},
            working_dir=cls.WORKING_DIR,
            detach=True,
        )


class FileProvider(ResourceProvider):
    serialize_as_secret_always = False

    def configure(self, req) -> None:
        VolumeProxy.pull_image()

    def create(self, props) -> CreateResult:
        props = FileProviderProps(**props)
        VolumeProxy.create_file(props)
        return CreateResult(id_=props.id_, outs={})

    def delete(self, id_: str, _props):
        VolumeProxy.delete_file(id_)


class File(Resource, module="docker", name="File"):
    def __init__(
        self,
        resource_name: str,
        volume: Input[pulumi_docker.Volume],
        path: Input[RelativePath],
        content: Input[str],
        mode: Input[int] = 0o444,
        opts: ResourceOptions | None = None,
    ):
        super().__init__(
            FileProvider(),
            resource_name,
            {
                "volume": Output.from_input(volume).apply(lambda x: x.name),
                "path": Output.from_input(path).apply(lambda x: x.as_posix()),
                "content": content,
                "mode": mode,
            },
            opts,
        )
