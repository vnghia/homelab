from typing import Self

import homelab_docker as docker
from pydantic import BaseModel, model_validator

from homelab.common import constant


class Volume(BaseModel):
    local: dict[str, docker.volume.Local]

    @model_validator(mode="after")
    def merge_pulumi_label(self) -> Self:
        self.local = {
            name: model.model_copy(
                update={"labels": model.labels | constant.PROJECT_LABELS}
            )
            for name, model in self.local.items()
        }
        return self
