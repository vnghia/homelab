import typing
from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_pydantic import HomelabBaseModel
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType

from ..model.record import TraefikRecordMiddlewareModel, TraefikRecordModel

if typing.TYPE_CHECKING:
    from .. import TraefikService


class TraefikRecordConfig(HomelabBaseModel):
    config: dict[str, TraefikRecordModel]
    external_middlewares: dict[
        TraefikDynamicType, list[TraefikRecordMiddlewareModel]
    ] = {}
    internal_middlewares: dict[
        TraefikDynamicType, list[TraefikRecordMiddlewareModel]
    ] = {}

    _external_middlewares: dict[TraefikDynamicType, list[str]]
    _internal_middlewares: dict[TraefikDynamicType, list[str]]

    def model_post_init(self, context: Any, /) -> None:
        self._external_middlewares = {}
        self._internal_middlewares = {}

    def build_middlewares(
        self,
        internal: bool,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
        type_: TraefikDynamicType,
    ) -> list[str]:
        # Since record middleware's name won't change, we only need to build once regardless of extractor_args

        (middlewares, _middlewares) = (
            (self.internal_middlewares, self._internal_middlewares)
            if internal
            else (self.external_middlewares, self._external_middlewares)
        )

        if type_ not in _middlewares:
            _middlewares[type_] = TraefikRecordMiddlewareModel.build_middlewares(
                middlewares.get(type_, []), traefik_service, extractor_args, type_
            )
        return _middlewares[type_]
