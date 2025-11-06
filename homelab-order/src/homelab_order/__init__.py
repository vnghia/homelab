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


class HomelabOrderProviderProps(HomelabBaseModel):
    model_config = ConfigDict(frozen=False)

    id: str
    names: set[str]
    orders: dict[str, NonNegativeInt] = {}

    def fill(self) -> None:
        current = 0
        current_orders = bidict(self.orders)
        self.orders = {}
        for name in self.names:
            if name in current_orders:
                self.orders[name] = current_orders[name]
            else:
                while (
                    current in current_orders.inverse
                    and current_orders.inverse[current] in self.names
                ):
                    current += 1
                self.orders[name] = current
                current += 1


class HomelabOrderProvider(ResourceProvider):
    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        order_props = HomelabOrderProviderProps(**props)
        order_props.fill()
        return CreateResult(
            id_=order_props.id, outs=order_props.model_dump(mode="json")
        )

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        order_olds = HomelabOrderProviderProps(**olds)
        order_news = HomelabOrderProviderProps(**news)
        return DiffResult(changes=order_olds.names != order_news.names)

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        order_olds = HomelabOrderProviderProps(**olds)
        news["orders"] = order_olds.orders
        order_news = HomelabOrderProviderProps(**news)
        order_news.fill()
        return UpdateResult(outs=order_news.model_dump(mode="json"))


class HomelabOrderResource(Resource, module="homelab", name="Order"):
    orders: Output[dict[str, NonNegativeInt]]

    def __init__(
        self, resource_name: str, *, opts: ResourceOptions, names: list[str]
    ) -> None:
        super().__init__(
            HomelabOrderProvider(),
            resource_name,
            {"id": resource_name, "names": names, "orders": None},
            opts,
        )
