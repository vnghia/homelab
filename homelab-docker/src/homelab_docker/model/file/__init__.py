import hashlib
from functools import cached_property
from typing import Any, ClassVar

import pulumi
from homelab_pydantic import HomelabBaseModel, HomelabRootModel, RelativePath
from pydantic import (
    NonNegativeInt,
    PositiveInt,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)


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
    uid: NonNegativeInt = DEFAULT_UID
    gid: NonNegativeInt = DEFAULT_GID


class FilePermissionUserModel(
    HomelabRootModel[str | tuple[str, int] | FilePermissionModel]
):
    root: str | tuple[str, int] | FilePermissionModel = FilePermissionModel()

    @classmethod
    def split_id(cls, user: str) -> tuple[int, int]:
        uid, gid = user.split(":", maxsplit=1)
        return int(uid), int(gid)

    def to_permission(self) -> FilePermissionModel:
        root = self.root
        if isinstance(root, FilePermissionModel):
            return root

        if isinstance(root, str):
            user = root
            mode = FilePermissionModel.DEFAULT_MODE
        else:
            user, mode = root

        uid, gid = self.split_id(user)
        return FilePermissionModel(mode=mode, uid=uid, gid=gid)


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
