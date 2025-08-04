from typing import ClassVar

from homelab_dagu_config import DaguServiceConfig
from homelab_dagu_config.model import DaguDagModel
from homelab_dagu_config.model.params import DaguDagParamsModel, DaguDagParamType
from homelab_dagu_config.model.step import DaguDagStepModel
from homelab_dagu_config.model.step.executor import DaguDagStepExecutorModel
from homelab_dagu_config.model.step.executor.docker import (
    DaguDagStepDockerExecutorModel,
)
from homelab_dagu_config.model.step.run import DaguDagStepRunModel
from homelab_dagu_config.model.step.run.command import (
    DaguDagStepRunCommandFullModel,
    DaguDagStepRunCommandModel,
    DaguDagStepRunCommandParamModel,
    DaguDagStepRunCommandParamTypeFullModel,
    DaguDagStepRunCommandParamTypeModel,
)
from homelab_docker.extract import ExtractorArgs
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from .. import DaguService
from ..model import DaguDagModelBuilder
from ..model.dotenv import DaguDagDotenvModelBuilder
from ..resource import DaguDagResource


class DaguServiceConfigBuilder(HomelabRootModel[DaguServiceConfig]):
    DEBUG_DAG_NAME: ClassVar[str] = "debug"

    def build_resources(
        self,
        *,
        opts: ResourceOptions,
        dagu_service: DaguService,
        extractor_args: ExtractorArgs,
    ) -> dict[str | None, DaguDagResource]:
        root = self.root

        for name, dotenv in root.dotenvs.root.items():
            DaguDagDotenvModelBuilder(dotenv).build_resource(
                name,
                opts=opts,
                extractor_args=extractor_args,
                dagu_service=dagu_service,
            )

        self.build_docker_group_dags(
            opts=opts, extractor_args=extractor_args, dagu_service=dagu_service
        )

        {
            name: DaguDagModelBuilder(model).build_resource(
                name,
                opts=opts,
                extractor_args=extractor_args,
                dagu_service=dagu_service,
            )
            for name, model in root.dag.root.items()
        }

        return dagu_service.dags[extractor_args.service.name()]

    def build_docker_group_dags(
        self,
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
        dagu_service: DaguService,
    ) -> dict[str, DaguDagResource]:
        root = self.root

        if root.docker:
            executor_config = root.docker.executor
            if executor_config.debug:
                DaguDagModelBuilder(
                    DaguDagModel(
                        dotenvs=root.docker.dag.dotenvs,
                        name=self.DEBUG_DAG_NAME,
                        path="{}-{}".format(
                            extractor_args.service.name(), self.DEBUG_DAG_NAME
                        ),
                        tags=[self.DEBUG_DAG_NAME],
                        params=DaguDagParamsModel(types={DaguDagParamType.DEBUG: None}),
                        steps=[
                            DaguDagStepModel(
                                name=self.DEBUG_DAG_NAME,
                                run=DaguDagStepRunModel(
                                    DaguDagStepRunCommandModel(
                                        [
                                            DaguDagStepRunCommandFullModel(
                                                GlobalExtract.from_simple("sleep")
                                            ),
                                            DaguDagStepRunCommandFullModel(
                                                DaguDagStepRunCommandParamModel(
                                                    param=DaguDagStepRunCommandParamTypeModel(
                                                        DaguDagStepRunCommandParamTypeFullModel(
                                                            type=DaguDagParamType.DEBUG
                                                        )
                                                    )
                                                )
                                            ),
                                        ]
                                    )
                                ),
                                executor=DaguDagStepExecutorModel(
                                    DaguDagStepDockerExecutorModel(
                                        executor_config.run_executor.__replace__(
                                            entrypoint=[]
                                        )
                                    )
                                ),
                            )
                        ],
                    )
                ).build_resource(
                    self.DEBUG_DAG_NAME,
                    opts=opts,
                    extractor_args=extractor_args,
                    dagu_service=dagu_service,
                )

            return {
                name: DaguDagModelBuilder(model).build_resource(
                    name,
                    opts=opts,
                    extractor_args=extractor_args,
                    dagu_service=dagu_service,
                )
                for name, model in root.docker.build_models(
                    extractor_args=extractor_args
                ).items()
            }
        return {}
