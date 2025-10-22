from typing import Self

from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import ExtraConfig


class ExtraService[T: ExtraConfig](ServiceWithConfigResourceBase[T]):
    REGISTER_OUTPUT = True

    def __init__(
        self,
        model: ServiceWithConfigModel[T],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

    def build(self) -> Self:
        for name, key in self.config.s3.root.items():
            s3 = self.extractor_args.global_args.s3[key]
            self.options[name].envs = {**self.options[name].envs, **s3.to_envs()}

        self.build_containers()

        if self.REGISTER_OUTPUT:
            self.register_outputs({})

        return self

    @classmethod
    def extract_depends_on(
        cls, models: dict[str, ServiceWithConfigModel[ExtraConfig]], name: str
    ) -> dict[str, None]:
        results: dict[str, None] = {}
        for depend_on in models[name].config.depends_on:
            results |= cls.extract_depends_on(models, depend_on)
        return results | {name: None}

    @classmethod
    def sort_depends_on(
        cls, models: dict[str, ServiceWithConfigModel[ExtraConfig]]
    ) -> dict[str, ServiceWithConfigModel[ExtraConfig]]:
        results: dict[str, ServiceWithConfigModel[ExtraConfig]] = {}
        for name in models:
            depends_on = cls.extract_depends_on(models, name)
            for depend_on in depends_on:
                results[depend_on] = models[depend_on]
        return results
