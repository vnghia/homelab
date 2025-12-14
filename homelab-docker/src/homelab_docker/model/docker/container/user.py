from functools import cached_property

from ...uid import UidGidModel


class ContainerUserConfig(UidGidModel):
    @cached_property
    def user(self) -> str:
        return "{}:{}".format(self.uid, self.gid)
