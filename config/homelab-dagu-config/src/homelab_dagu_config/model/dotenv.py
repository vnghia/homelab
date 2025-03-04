from homelab_docker.extract import GlobalExtract
from homelab_docker.model.container import ContainerModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from homelab_s3_config import S3Config
from pulumi import Output


class DaguDagDotenvModel(HomelabBaseModel):
    s3: S3Config | None = None
    envs: dict[str, GlobalExtract] = {}

    def to_envs(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> dict[str, Output[str]]:
        return {
            **(
                {k: Output.from_input(v) for k, v in self.s3.to_envs().items()}
                if self.s3
                else {}
            ),
            **{k: v.extract_str(main_service, model) for k, v in self.envs.items()},
        }
