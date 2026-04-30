from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class ServiceDependOnFullConfig(HomelabBaseModel):
    host: str | None = None
    service: str


class ServiceDependOnConfig(HomelabRootModel[str | ServiceDependOnFullConfig]):
    def to_full(self) -> ServiceDependOnFullConfig:
        root = self.root
        if isinstance(root, ServiceDependOnFullConfig):
            return root
        return ServiceDependOnFullConfig(service=root)
