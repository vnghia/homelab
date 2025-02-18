from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel, model_validator


class HomelabBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda x: x.replace("_", "-"),
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        revalidate_instances="always",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
        validation_error_cause=True,
    )

    @model_validator(mode="before")
    @classmethod
    def ignore_pulumi_provider(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data.pop("__provider", None)
        return data


class HomelabRootModel[T](RootModel[T]):
    model_config = ConfigDict(
        frozen=True,
        revalidate_instances="always",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
        validation_error_cause=True,
    )

    root: T
