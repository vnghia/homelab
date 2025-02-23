from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import HomelabBaseModel

from ...params import DaguDagParamsModel

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepRunSubdagModel(HomelabBaseModel):
    dag: str
    params: DaguDagParamsModel = DaguDagParamsModel()

    def to_run(
        self, dagu_service: DaguService, params_: DaguDagParamsModel
    ) -> dict[str, Any]:
        dag = dagu_service.DAGS[self.dag]
        params = self.params.to_params(dag.model)

        data: dict[str, Any] = {
            "run": dag.to_container_path(dagu_service.model.container.volumes)
        }
        if params:
            data["params"] = " ".join(
                '{}="{}"'.format(key, value.replace('"', '\\"'))
                for key, value in params
            )
        return data
