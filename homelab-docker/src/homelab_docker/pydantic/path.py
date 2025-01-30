from pathlib import PosixPath
from typing import Annotated

from pydantic import AfterValidator, Field


def __check_absolute_path(path: PosixPath) -> PosixPath:
    if not path.is_absolute():
        raise ValueError("{} is not an absolute path".format(path))
    return path


def __check_relative_path(path: PosixPath) -> PosixPath:
    if path.is_absolute():
        raise ValueError("{} is not a relative path".format(path))
    return path


AbsolutePath = Annotated[
    PosixPath, Field(strict=False), AfterValidator(__check_absolute_path)
]
RelativePath = Annotated[
    PosixPath, Field(strict=False), AfterValidator(__check_relative_path)
]
