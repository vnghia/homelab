import typing
from typing import Any, ClassVar, Self

from homelab_docker.extract import ExtractorArgs
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType
from pydantic import NonNegativeInt

if typing.TYPE_CHECKING:
    from .. import TraefikService


class TraefikRecordMiddlewareFullModel(HomelabBaseModel):
    DEFAULT_PRIORITY: ClassVar[NonNegativeInt] = 100

    service: str | None = None
    middleware: str | None = None
    priority: NonNegativeInt = DEFAULT_PRIORITY


class TraefikRecordMiddlewareModel(
    HomelabRootModel[str | TraefikRecordMiddlewareFullModel]
):
    def to_full(self) -> TraefikRecordMiddlewareFullModel:
        from .. import TraefikService

        root = self.root
        if isinstance(root, TraefikRecordMiddlewareFullModel):
            return root
        return TraefikRecordMiddlewareFullModel(
            service=TraefikService.name(), middleware=root
        )

    @classmethod
    def build_middlewares(
        cls,
        middlewares: list[Self],
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
        type_: TraefikDynamicType,
    ) -> list[str]:
        from homelab_traefik_config.model.dynamic.middleware import (
            TraefikDynamicMiddlewareModel,
            TraefikDynamicMiddlewareUseModel,
        )

        from ..model.dynamic.middleware import (
            TraefikDynamicMiddlewareModelBuilder,
        )

        return [
            TraefikDynamicMiddlewareModelBuilder(
                TraefikDynamicMiddlewareModel(
                    TraefikDynamicMiddlewareUseModel(
                        service=middleware.service, name=middleware.middleware
                    )
                )
            ).get_name(traefik_service, extractor_args, type_)
            for middleware in sorted(
                map(TraefikRecordMiddlewareModel.to_full, middlewares),
                key=lambda x: x.priority,
            )
        ]


class TraefikRecordModel(HomelabBaseModel):
    entrypoint: str
    middlewares: dict[TraefikDynamicType, list[TraefikRecordMiddlewareModel]] = {}

    _middlewares: dict[TraefikDynamicType, list[str]]

    def model_post_init(self, context: Any, /) -> None:
        self._middlewares = {}

    def build_middlewares(
        self,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
        type_: TraefikDynamicType,
    ) -> list[str]:
        # Since record middleware's name won't change, we only need to build once regardless of extractor_args

        if type_ not in self._middlewares:
            self._middlewares[type_] = TraefikRecordMiddlewareModel.build_middlewares(
                self.middlewares.get(type_, []), traefik_service, extractor_args, type_
            )
        return self._middlewares[type_]
