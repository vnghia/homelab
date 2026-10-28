from homelab_pydantic import HomelabBaseModel


class HostAccessModel(HomelabBaseModel):
    user: str
    address: str

    @property
    def ssh(self) -> str:
        return f"ssh://{self.user}@{self.address}"
