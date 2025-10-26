from typing import Any, ClassVar, Self

import deepmerge
from deepmerge.merger import Merger
from pydantic import BaseModel, ConfigDict, RootModel, model_validator

OVERWRITE_TYPE_SPECIFIC_MERGE_STRATEGIES: list[tuple[type, str]] = [
    (list, "override"),
    (dict, "merge"),
    (set, "union"),
]
override_merger: Merger = Merger(
    OVERWRITE_TYPE_SPECIFIC_MERGE_STRATEGIES, ["override"], ["override"]
)


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

    def model_merge(self, other: Self, override: bool = False) -> Self:
        left_data = self.model_dump(mode="json", by_alias=True, exclude_unset=True)
        right_data = other.model_dump(mode="json", by_alias=True, exclude_unset=True)

        merged_data = (
            override_merger.merge(left_data, right_data)
            if override
            else deepmerge.always_merger.merge(left_data, right_data)
        )
        return self.__class__(**merged_data)


class HomelabRootModel[T](RootModel[T]):
    model_config = ConfigDict(
        frozen=True,
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

    def model_merge(self, other: Self, override: bool = False) -> Self:
        left_data = self.model_dump(mode="json", by_alias=True, exclude_unset=True)
        right_data = other.model_dump(mode="json", by_alias=True, exclude_unset=True)

        merged_data = (
            override_merger.merge(left_data, right_data)
            if override
            else deepmerge.always_merger.merge(left_data, right_data)
        )
        return self.__class__(**merged_data)


class HomelabServiceConfigDict[T](HomelabRootModel[dict[str | None, T]]):
    NONE_KEY: ClassVar[str | None]

    @model_validator(mode="after")
    def set_none_key(self) -> Self:
        return self.model_construct(
            root={
                None if key == self.NONE_KEY else key: model
                for key, model in self.root.items()
            }
        )

    def __bool__(self) -> bool:
        return bool(self.root)

    def __getitem__(self, key: str | None) -> T:
        return self.root[key]
