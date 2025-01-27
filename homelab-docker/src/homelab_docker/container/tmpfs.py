from pathlib import PosixPath

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator


class Tmpfs(BaseModel):
    model_config = ConfigDict(strict=True)

    path: PosixPath = Field(PosixPath("/tmp"), strict=False)
    size: PositiveInt | None = None

    @field_validator("path", mode="after")
    @classmethod
    def check_absolute_path(cls, path: PosixPath) -> PosixPath:
        if not path.is_absolute():
            raise ValueError("path must be absolute")
        return path
