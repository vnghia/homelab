from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import HomelabBaseModel

from ...params import DaguDagParamsModel

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepRunSubdagModel(HomelabBaseModel):
    service: str
    dag: str
    params: DaguDagParamsModel = DaguDagParamsModel()

    def to_run(
        self, dagu_service: DaguService, params_: DaguDagParamsModel
    ) -> dict[str, Any]:
        dagu_config = dagu_service.config
        dagu_model = dagu_service.model[dagu_config.dags_dir.container]
        dag = dagu_service.DAGS[self.service][self.dag]
        params = self.params.to_params(dag.model)

        data: dict[str, Any] = {"run": dag.to_path(dagu_model)}
        if params:
            data["params"] = " ".join(
                '{}="{}"'.format(key, value.replace('"', '\\"'))
                for key, value in params
            )
        return data
