from typing import Any

from bidict import bidict
from homelab_pydantic import HomelabBaseModel
from pulumi import Output, ResourceOptions
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pydantic import ConfigDict, NonNegativeInt


class HomelabSequenceProviderProps(HomelabBaseModel):
    model_config = ConfigDict(frozen=False)

    id: str
    names: set[str]
    sequence: dict[str, NonNegativeInt] = {}

    def fill(self) -> None:
        current = 0
        current_sequence = bidict(self.sequence)
        self.sequence = {}
        for name in self.names:
            if name in current_sequence:
                self.sequence[name] = current_sequence[name]
            else:
                while (
                    current in current_sequence.inverse
                    and current_sequence.inverse[current] in self.names
                ):
                    current += 1
                self.sequence[name] = current
                current += 1


class HomelabSequenceProvider(ResourceProvider):
    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        order_props = HomelabSequenceProviderProps(**props)
        order_props.fill()
        return CreateResult(
            id_=order_props.id, outs=order_props.model_dump(mode="json")
        )

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        order_olds = HomelabSequenceProviderProps(**olds)
        order_news = HomelabSequenceProviderProps(**news)
        return DiffResult(changes=order_olds.names != order_news.names)

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        order_olds = HomelabSequenceProviderProps(**olds)
        news["sequence"] = order_olds.sequence
        order_news = HomelabSequenceProviderProps(**news)
        order_news.fill()
        return UpdateResult(outs=order_news.model_dump(mode="json"))


class HomelabSequenceResource(Resource, module="homelab", name="Order"):
    sequence: Output[dict[str, NonNegativeInt]]

    def __init__(
        self, resource_name: str, *, opts: ResourceOptions, names: list[str]
    ) -> None:
        super().__init__(
            HomelabSequenceProvider(),
            resource_name,
            {"id": resource_name, "names": names, "sequence": None},
            opts,
        )

    def __getitem__(self, key: str) -> Output[NonNegativeInt]:
        return self.sequence.apply(lambda x: x[key])
