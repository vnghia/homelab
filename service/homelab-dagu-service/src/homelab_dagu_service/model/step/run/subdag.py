from __future__ import annotations

import typing
from typing import Any

from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step.run.subdag import DaguDagStepRunSubdagModel
from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_pydantic.model import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepRunSubdagModelBuilder(HomelabRootModel[DaguDagStepRunSubdagModel]):
    def to_run(
        self,
        _params: DaguDagParamsModel,
        dagu_service: DaguService,
        extractor_args: ExtractorArgs,
    ) -> dict[str, Any]:
        from homelab_dagu_service.model.params import DaguDagParamsModelBuilder

        root = self.root

        dagu_config = dagu_service.config
        dag = dagu_service.dags[root.service][root.dag]
        params = DaguDagParamsModelBuilder(root.params).to_params(
            dag.model, extractor_args
        )

        data: dict[str, Any] = {
            "run": dag.to_path(
                dagu_service.extractor_args_from_self(dagu_config.dags_dir.container)
            )
        }

        if root.parallel:
            data["parallel"] = {
                "items": [
                    GlobalExtractor(item).extract_str(extractor_args)
                    for item in root.parallel.items
                ]
            } | (
                {"maxConcurrent": root.parallel.max_concurrent}
                if root.parallel.max_concurrent
                else {}
            )

        if params:
            data["params"] = Output.all(**params).apply(
                lambda extractor_args: " ".join(
                    '{}="{}"'.format(key, value.replace('"', '\\"'))
                    for key, value in extractor_args.items()
                )
            )
        return data
