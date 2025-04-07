from pathlib import PosixPath
from typing import Self

from pydantic import model_validator

from .model import HomelabRootModel


class RelativePath(HomelabRootModel[PosixPath]):
    @model_validator(mode="after")
    def check_relative_path(self) -> Self:
        root = self.root
        if root.is_absolute():
            raise ValueError("{} is not a relative path".format(root))
        return self

    def __truediv__(self, other: str | Self) -> Self:
        if isinstance(other, str):
            return self / self.__class__(PosixPath(other))
        else:
            return self.__class__(self.root / other.root)

    def as_posix(self) -> str:
        return self.root.as_posix()

    def __json__(self) -> str:
        return self.as_posix()

    @property
    def suffix(self) -> str:
        return self.root.suffix

    def with_suffix(self, suffix: str) -> Self:
        return self.__class__(self.root.with_suffix(suffix))


class AbsolutePath(HomelabRootModel[PosixPath]):
    @model_validator(mode="after")
    def check_absolute_path(self) -> Self:
        root = self.root
        if not root.is_absolute():
            raise ValueError("{} is not an absolute path".format(root))
        return self

    def __truediv__(self, other: str | RelativePath) -> Self:
        if isinstance(other, str):
            return self / RelativePath(PosixPath(other))
        else:
            return self.__class__(self.root / other.root)

    def as_posix(self) -> str:
        return self.root.as_posix()

    def __json__(self) -> str:
        return self.as_posix()

    @property
    def suffix(self) -> str:
        return self.root.suffix

    def with_suffix(self, suffix: str) -> Self:
        return self.__class__(self.root.with_suffix(suffix))
