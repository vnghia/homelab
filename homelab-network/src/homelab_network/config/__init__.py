import functools
import operator

from homelab_pydantic import HomelabBaseModel

from .port import NetworkPortConfig
from .record import RecordConfig


class NetworkConfig(HomelabBaseModel):
    records: dict[str, RecordConfig]
    port: NetworkPortConfig

    @property
    def aliases(self) -> list[str]:
        return functools.reduce(
            operator.iadd, [record.aliases for record in self.records.values()], []
        )
