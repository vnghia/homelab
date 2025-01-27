from pathlib import PosixPath

from pydantic import BaseModel, ConfigDict, field_validator


class Volume(BaseModel):
    model_config = ConfigDict(strict=True)

    path: PosixPath
    read_only: bool = False

    @field_validator("path", mode="after")
    @classmethod
    def check_absolute_path(cls, path: PosixPath) -> PosixPath:
        if path.is_absolute():
            raise ValueError("path must be absolute")
        return path
