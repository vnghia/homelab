from typing import Self

import deepmerge
import homelab_docker as docker
from pydantic import BaseModel, model_validator

from homelab.common import constant


class Volume(BaseModel):
    locals: dict[str, dict[str, docker.volume.Local]]

    @model_validator(mode="after")
    def merge_pulumi_label(self) -> Self:
        self.locals = {
            namespace: {
                name: model.model_copy(
                    update={
                        "labels": deepmerge.always_merger.merge(
                            model.labels, constant.PROJECT_LABELS
                        )
                    }
                )
                for name, model in local.items()
            }
            for namespace, local in self.locals.items()
        }
        return self
