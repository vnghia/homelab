from functools import cached_property

from ...user import UidGidModel


class ContainerUserConfig(UidGidModel):
    @cached_property
    def user(self) -> str:
        return "{}:{}".format(self.uid, self.gid)

    @property
    def is_root(self) -> bool:
        return self.uid == 0 and self.gid == 0

    @property
    def is_default(self) -> bool:
        return self.uid == self.DEFAULT_UID and self.gid == self.DEFAULT_GID
