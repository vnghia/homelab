from homelab_pydantic import HomelabBaseModel


class HostAccessModel(HomelabBaseModel):
    user: str
    address: str

    @property
    def ssh(self) -> str:
        return "ssh://{}@{}".format(self.user, self.address)
