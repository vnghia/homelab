import hashlib
from functools import cached_property
from typing import Any, ClassVar

import pulumi
from homelab_pydantic import HomelabBaseModel, RelativePath
from pydantic import (
    NonNegativeInt,
    PositiveInt,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)

from ..user import UidGidModel


class FileLocationModel(HomelabBaseModel):
    volume: str
    path: RelativePath

    @property
    def id_(self) -> str:
        return "{}:{}".format(self.volume, self.path.as_posix())


class FilePermissionModel(HomelabBaseModel):
    DEFAULT_MODE: ClassVar[PositiveInt] = 0o444
    EXECUTABLE_MODE: ClassVar[PositiveInt] = 0o744

    DEFAULT_UID: ClassVar[NonNegativeInt] = 1000
    DEFAULT_GID: ClassVar[NonNegativeInt] = 1000

    mode: PositiveInt = DEFAULT_MODE
    owner: UidGidModel = UidGidModel()


class FileDataModel(HomelabBaseModel):
    content: str

    @cached_property
    def hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()

    @field_validator("content", mode="wrap")
    @classmethod
    def ignore_pulumi_unknown(
        cls, data: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> str:
        if isinstance(data, pulumi.output.Unknown):
            pulumi.log.warn(
                "Pulumi unknown output encountered: {}. Validated data: {}".format(
                    data, info.data
                )
            )
            return ""
        return handler(data)  # type: ignore[no-any-return]
