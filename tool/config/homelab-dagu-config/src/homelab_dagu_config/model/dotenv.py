from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_s3.model import S3Key
from pulumi import Output


class DaguDagDotenvModel(HomelabBaseModel):
    s3: S3Key | None = None
    envs: dict[str, GlobalExtract] = {}

    def to_envs(self, extractor_args: ExtractorArgs) -> dict[str, Output[str]]:
        return {
            **(
                extractor_args.global_resource.plain_args.s3[self.s3].to_envs(None)
                if self.s3
                else {}
            ),
            **{
                k: GlobalExtractor(v).extract_str(extractor_args)
                for k, v in self.envs.items()
            },
        }
