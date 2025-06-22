from __future__ import annotations

import operator
import typing
from functools import reduce
from typing import Any

from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step.run.subdag import DaguDagStepRunSubdagModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic.model import HomelabRootModel

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepRunSubdagModelBuilder(HomelabRootModel[DaguDagStepRunSubdagModel]):
    def to_run(
        self,
        params_: DaguDagParamsModel,
        dagu_service: DaguService,
        main_service: ServiceResourceBase,
    ) -> dict[str, Any]:
        root = self.root

        dagu_config = dagu_service.config
        dagu_model = dagu_service.model[dagu_config.dags_dir.container]
        dag = dagu_service.dags[root.service][root.dag]
        params = root.params.to_params(dag.model)

        data: dict[str, Any] = {"run": dag.to_path(dagu_service, dagu_model)}
        if params:
            data["params"] = " ".join(
                '{}="{}"'.format(key, value.replace('"', '\\"'))
                for key, value in params.items()
            )
        return data
