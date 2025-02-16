import hashlib

from pydantic import BaseModel

from homelab_docker.pydantic.path import RelativePath


class FileLocationModel(BaseModel):
    volume: str
    path: RelativePath

    @property
    def id_(self) -> str:
        return "{}:{}".format(self.volume, self.path.as_posix())


class FileDataModel(BaseModel):
    content: str
    mode: int

    @property
    def hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()
