from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_pydantic import HomelabBaseModel
from pulumi import Input


class DaguDagStepJqExecutorModel(HomelabBaseModel):
    raw: bool = True

    def to_executor(
        self,
        _extractor_args: ExtractorArgs,
        _dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        return {
            "type": "jq",
            "config": None if not self.raw else {"raw": True},
        }
