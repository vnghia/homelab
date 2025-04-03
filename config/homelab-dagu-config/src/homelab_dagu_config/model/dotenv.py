from homelab_docker.extract import GlobalExtractor
from homelab_docker.model.container import ContainerModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pulumi import Output


class DaguDagDotenvModel(HomelabBaseModel):
    s3: str | None = None
    envs: dict[str, GlobalExtract] = {}

    def to_envs(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> dict[str, Output[str]]:
        return {
            **(
                {
                    k: Output.from_input(v)
                    for k, v in main_service.docker_resource_args.config.s3[self.s3]
                    .to_envs()
                    .items()
                }
                if self.s3
                else {}
            ),
            **{
                k: GlobalExtractor(v).extract_str(main_service, model)
                for k, v in self.envs.items()
            },
        }
