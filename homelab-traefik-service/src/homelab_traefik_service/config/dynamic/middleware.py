from typing import Any

from homelab_docker.model.file.config import ConfigFile
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.volume import VolumeResource
from pulumi import ResourceOptions
from pydantic import BaseModel, RootModel

from ..static import TraefikStaticConfig


class TraefikDynamicMiddlewareFullConfig(BaseModel):
    name: str
    data: Any

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        volume_resource: VolumeResource,
        static_config: TraefikStaticConfig,
    ) -> FileResource:
        data = {"http": {"middlewares": {self.name: self.data}}}

        return ConfigFile(
            container_volume_path=static_config.get_dynamic_container_volume_path(
                self.name
            ),
            data=data,
            schema_url="https://json.schemastore.org/traefik-v3-file-provider.json",
        ).build_resource(resource_name, opts=opts, volume_resource=volume_resource)


class TraefikDynamicMiddlewareConfig(
    RootModel[str | TraefikDynamicMiddlewareFullConfig]
):
    @property
    def name(self) -> str:
        root = self.root
        return (
            root.name if isinstance(root, TraefikDynamicMiddlewareFullConfig) else root
        )

    @property
    def data(self) -> Any:
        root = self.root
        return (
            root.data if isinstance(root, TraefikDynamicMiddlewareFullConfig) else None
        )
