from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pulumi import Output


class DaguDagDotenvModel(HomelabBaseModel):
    s3: str | None = None
    envs: dict[str, GlobalExtract] = {}

    def to_envs(self, extractor_args: ExtractorArgs) -> dict[str, Output[str]]:
        return {
            **(
                {
                    k: Output.from_input(v)
                    for k, v in extractor_args.docker_resource_args.config.s3[self.s3]
                    .to_envs()
                    .items()
                }
                if self.s3
                else {}
            ),
            **{
                k: GlobalExtractor(v).extract_str(extractor_args)
                for k, v in self.envs.items()
            },
        }
