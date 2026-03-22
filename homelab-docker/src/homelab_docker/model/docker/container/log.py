from homelab_pydantic.model import HomelabBaseModel


class ContainerLogConfig(HomelabBaseModel):
    driver: str
    opts: dict[str, str] = {}
