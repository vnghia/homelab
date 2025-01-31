from typing import Self

import homelab_docker as docker
from pydantic import BaseModel, model_validator

from homelab_config.common import constant


class Network(BaseModel):
    bridge: dict[str, docker.network.Bridge]

    @model_validator(mode="after")
    def merge_pulumi_label(self) -> Self:
        self.bridge = {
            name: network.model_copy(
                update={"labels": network.labels | constant.PROJECT_LABELS}
            )
            for name, network in self.bridge.items()
        }
        return self
